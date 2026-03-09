from datetime import datetime, timedelta

import mysql.connector
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_bcrypt import Bcrypt
from werkzeug.middleware.proxy_fix import ProxyFix

import api_handler  # Mengimpor logika API, MQTT
from config import Config
from db_pool import db_pool

# Import new infrastructure modules
from logger_config import get_logger, setup_logging

app = Flask(__name__)
app.config.from_object(Config)

# ProxyFix: percaya header X-Forwarded-Proto dari Cloudflare Tunnel/Nginx
# x_for=1: trust 1 proxy (Nginx), x_proto=1: trust X-Forwarded-Proto (https dari CF)
# Tanpa ini: SESSION_COOKIE_SECURE tidak bekerja & url_for() generate http:// bukan https://
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

bcrypt = Bcrypt(app)

# Initialize logging
setup_logging(app)
logger = get_logger(__name__)

# Initialize database connection pool
try:
    db_pool.initialize(app.config)
    logger.info("[OK] Database connection pool initialized successfully")
except mysql.connector.Error as err:
    logger.error(f"[FAIL] Failed to initialize database pool: {err}")
    logger.warning(
        "[WARNING] Application will use direct connections (performance may be degraded)"
    )

# Menghubungkan seluruh logika backend IOT & API ke app utama
api_handler.init_api(app, bcrypt)


# ==========================================
# DATABASE HELPER
# ==========================================
def get_db_connection():
    """
    Get MySQL database connection from pool or direct connection as fallback.

    Returns:
        mysql.connector.connection.MySQLConnection or None: Database connection if successful
    """
    # Try to get connection from pool first
    try:
        return db_pool.get_connection()
    except Exception as pool_err:
        logger.debug(f"Pool connection failed, falling back to direct: {pool_err}")

        # Fallback to direct connection
        try:
            return mysql.connector.connect(
                host=app.config["MYSQL_HOST"],
                user=app.config["MYSQL_USER"],
                password=app.config["MYSQL_PASSWORD"],
                database=app.config["MYSQL_DB"],
            )
        except mysql.connector.Error as err:
            # Log specific MySQL errors
            if err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
                logger.error("Database access denied: Invalid username or password")
            elif err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                logger.error(f"Database '{app.config['MYSQL_DB']}' does not exist")
            else:
                logger.error(f"Database connection failed: {err}")
            return None


def get_user_device_data(user_id):
    conn = get_db_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT d.id as device_id, d.device_sn, d.current_stock, d.max_capacity,
                   p.name, p.species, p.category, p.weight_kg, p.kcal_per_kg, p.daily_target_grams
            FROM devices d LEFT JOIN pets p ON d.id = p.device_id
            WHERE d.owner_id = %s LIMIT 1
        """,
            (user_id,),
        )
        return cursor.fetchone()
    finally:
        if conn and conn.is_connected():
            conn.close()



# ==========================================
# ROUTES: AUTHENTICATION
# ==========================================
@app.route("/")
def index():
    return redirect(url_for("dashboard")) if "user_id" in session else redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        un, pw = request.form.get("username"), request.form.get("password")
        conn = get_db_connection()
        if not conn:
            flash("Koneksi database gagal!", "danger")
            return render_template("auth/login.html")

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (un,))
        user = cursor.fetchone()

        if user and bcrypt.check_password_hash(user["password_hash"], pw):
            session.update({"user_id": user["user_id"], "username": user["username"]})
            return redirect(url_for("dashboard"))

        flash("Username atau password salah!", "danger")
        cursor.close()
        conn.close()
    return render_template("auth/login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        un, em, pw = request.form["username"], request.form["email"], request.form["password"]
        pw_hash = bcrypt.generate_password_hash(pw).decode("utf-8")

        conn = get_db_connection()
        if not conn:
            flash("Koneksi database gagal!", "danger")
            return render_template("auth/register.html")

        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                (un, em, pw_hash),
            )
            conn.commit()
            flash("Registrasi berhasil!", "success")
            return redirect(url_for("login"))
        except mysql.connector.IntegrityError:
            # Duplicate username or email
            flash("Username/Email sudah ada.", "danger")
        except mysql.connector.Error as err:
            print(f"[ERROR] Registration failed: {err}")
            flash("Registrasi gagal. Silakan coba lagi.", "danger")
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

    return render_template("auth/register.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ==========================================
# ROUTES: DASHBOARD & STATS
# ==========================================
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    data = get_user_device_data(session["user_id"])
    if not data or not data["name"]:
        return redirect(url_for("onboarding_choice"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM feeding_logs WHERE device_id = %s ORDER BY timestamp DESC LIMIT 10",
        (data["device_sn"],),
    )
    logs = cursor.fetchall()

    pantry = (
        round((data["current_stock"] / data["max_capacity"]) * 100)
        if data["max_capacity"] > 0
        else 0
    )
    is_owner = data["owner_id"] == session["user_id"]

    cursor.close()
    conn.close()
    data["id"] = data["device_id"]
    return render_template(
        "dashboard/index.html", data=data, logs=logs, pantry=pantry, is_owner=is_owner
    )


@app.route("/stats")
def stats():
    if "user_id" not in session:
        return redirect(url_for("login"))
    data = get_user_device_data(session["user_id"])
    if not data:
        return redirect(url_for("onboarding_choice"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 1. Ambil data 7 hari terakhir dari DB
    # Gunakan DATE_FORMAT agar string tanggal konsisten dengan Python
    cursor.execute(
        """
        SELECT DATE_FORMAT(timestamp, '%Y-%m-%d') as feed_date, SUM(grams_out) as total
        FROM feeding_logs
        WHERE device_id = %s AND timestamp >= DATE_SUB(CURDATE(), INTERVAL 6 DAY)
        GROUP BY feed_date
    """,
        (data["device_sn"],),
    )

    db_results = {row["feed_date"]: row["total"] for row in cursor.fetchall()}

    # 2. Bangun dataset 7 hari (isi 0 jika hari tersebut tidak ada di DB)
    weekly_data = []
    today = datetime.now().date()
    today_total = 0

    for i in range(6, -1, -1):
        target_date = today - timedelta(days=i)
        date_str = target_date.strftime("%Y-%m-%d")  # Pastikan format YYYY-MM-DD
        total_grams = db_results.get(date_str, 0)

        label = target_date.strftime("%d %b") if i != 0 else "Hari Ini"
        weekly_data.append({"label": label, "total": float(total_grams)})

        if i == 0:
            today_total = float(total_grams)

    cursor.close()
    conn.close()
    return render_template(
        "dashboard/stats.html", data=data, weekly_data=weekly_data, today_total=today_total
    )


# ... (Route schedules, profile, onboarding tetap sama) ...


@app.route("/schedules")
def schedules():
    if "user_id" not in session:
        return redirect(url_for("login"))
    data = get_user_device_data(session["user_id"])
    if not data:
        return redirect(url_for("onboarding_choice"))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, waktu AS time, porsi_gram AS grams, mode FROM feeding_schedules WHERE device_id = %s ORDER BY waktu ASC",
        (data["device_id"],),
    )
    scheds = cursor.fetchall()
    for s in scheds:
        if isinstance(s["time"], timedelta):
            s["time"] = (datetime.min + s["time"]).time()
    is_owner = data["owner_id"] == session["user_id"]
    cursor.close()
    conn.close()
    return render_template(
        "dashboard/schedules.html",
        data=data,
        schedules=scheds,
        has_system=any(s["mode"] == "system" for s in scheds),
        is_owner=is_owner,
    )


@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))
    data = get_user_device_data(session["user_id"])
    if not data:
        return redirect(url_for("onboarding_choice"))
    is_owner = data["owner_id"] == session["user_id"]
    return render_template("dashboard/profile.html", data=data, is_owner=is_owner)


@app.route("/onboarding/choice")
def onboarding_choice():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("onboarding/choice.html")


@app.route("/onboarding/setup_pet", methods=["GET", "POST"])
def setup_pet():
    if "user_id" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        session["temp_pet_data"] = {
            "name": request.form["nama_kucing"],
            "species": request.form["jenis"],
            "category": request.form["kategori"],
            "weight": float(request.form["berat"]),
            "kcal": int(request.form["kcal"]),
        }
        return redirect(url_for("scan_device"))
    return render_template("onboarding/setup_pet.html")


@app.route("/onboarding/scan")
def scan_device():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("onboarding/scan_device.html")


if __name__ == "__main__":
    import os

    # Load configuration from environment variables
    debug = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")
    port = int(os.getenv("SERVER_PORT", 5000))
    host = os.getenv("SERVER_HOST", "0.0.0.0")

    # CRITICAL FIX: Disable reloader to prevent duplicate MQTT clients
    # Flask reloader spawns 2 processes (parent + child) which creates 2 MQTT subscriptions
    # This causes every MQTT message to be received twice, leading to duplicate database entries
    # Trade-off: Manual restart needed for code changes, but prevents data duplication
    app.run(debug=debug, host=host, port=port, use_reloader=False)
