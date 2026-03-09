import hashlib
import json
import ssl
import threading
import time
from datetime import timedelta

import mysql.connector
import paho.mqtt.client as mqtt
from flask import flash, jsonify, redirect, request, session, url_for

from db_pool import db_pool
from nutrition_logic import PetNutritionManager

# Memori cache untuk mencegah pesan ganda (Anti-Duplikasi)
mqtt_cache = {}
CACHE_EXPIRY = 5  # seconds - window untuk detect duplicate messages



def get_db_connection(app):
    return db_pool.get_connection()


def trigger_sync(app, mqtt_client, device_id_pk):
    """Mengirim jadwal terbaru ke ESP32 melalui MQTT sync."""
    conn = None
    try:
        conn = get_db_connection(app)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT device_sn FROM devices WHERE id = %s", (device_id_pk,))
        device = cursor.fetchone()
        if not device:
            return

        cursor.execute(
            "SELECT waktu, porsi_gram FROM feeding_schedules WHERE device_id = %s AND is_active = 1",
            (device_id_pk,),
        )
        schedules = cursor.fetchall()

        formatted_sched = []
        for s in schedules:
            t = s["waktu"]
            if isinstance(t, timedelta):
                hours, remainder = divmod(t.seconds, 3600)
                minutes = remainder // 60
                time_str = f"{hours:02d}:{minutes:02d}"
            else:
                time_str = str(t)[:5]
            formatted_sched.append({"t": time_str, "p": s["porsi_gram"]})

        payload = json.dumps({"action": "sync", "schedules": formatted_sched})
        mqtt_client.publish(f"petfeed/{device['device_sn']}/perintah", payload, qos=1)
        print(f"[SYNC] Berhasil kirim {len(formatted_sched)} jadwal ke {device['device_sn']}")
    except Exception as e:
        print(f"[SYNC ERROR] {e}")
    finally:
        if conn:
            conn.close()


def generate_default_schedules(cursor, device_id, category, target_grams):
    """Menerapkan jadwal otomatis berdasarkan kategori FEDIAF."""
    cursor.execute("DELETE FROM feeding_schedules WHERE device_id = %s", (device_id,))
    # kitten/junior = 5x sehari; dewasa/senior = 3x sehari
    if category in ("kitten", "junior"):
        times = ["06:00:00", "10:00:00", "14:00:00", "18:00:00", "22:00:00"]
        porsi = round(target_grams / 5)
    else:
        times = ["07:00:00", "13:00:00", "19:00:00"]
        porsi = round(target_grams / 3)
    for t in times:
        cursor.execute(
            "INSERT INTO feeding_schedules (device_id, waktu, porsi_gram, mode, is_active) VALUES (%s, %s, %s, 'system', 1)",
            (device_id, t, porsi),
        )


def init_api(app, bcrypt):
    import os
    import uuid

    MQTT_BROKER = app.config.get("MQTT_BROKER", "broker.hivemq.com")
    MQTT_PORT = int(app.config.get("MQTT_PORT", 1883))
    MQTT_KEEPALIVE = int(os.getenv("MQTT_KEEPALIVE", 60))

    # Generate unique client ID to support multiple instances
    client_id = f"petfeeder-backend-{uuid.uuid4().hex[:8]}"
    client = mqtt.Client(client_id=client_id)

    def on_message(client, userdata, msg):
        """
        Callback for incoming MQTT messages
        Handles status reports from ESP32 devices
        """
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())

            print(f"[MQTT] Message received - Topic: {topic}")
            print(f"[MQTT] Payload: {payload}")

            # Parse topic: petfeed/{DEVICE_ID}/status
            parts = topic.split("/")
            if len(parts) == 3 and parts[2] == "status":
                device_id = parts[1]
                handle_device_status(app, device_id, payload)
            else:
                print(f"[MQTT] Unknown topic format: {topic}")

        except json.JSONDecodeError as e:
            print(f"[MQTT] JSON decode error: {e}")
        except Exception as e:
            print(f"[MQTT] Message processing error: {e}")

    def handle_device_status(app, device_id, data):
        """
        Handle status messages from ESP32 devices
        Updates feeding_logs and current_stock in database

        Args:
            app: Flask app instance
            device_id: Device serial number (e.g., "PET-A4CF12EFCDAB5678")
            data: JSON payload with porsi and metode
        """
        conn = None
        cursor = None
        try:
            porsi = data.get("porsi", 0)
            metode = data.get("metode", "manual")

            # DEDUPLICATION: Generate hash based on message content ONLY (no timestamp!)
            # This ensures duplicate messages have the SAME hash
            msg_content = f"{device_id}:{porsi}:{metode}"
            msg_hash = hashlib.md5(msg_content.encode()).hexdigest()
            current_time = time.time()

            # Check if this exact message was processed recently (within 2 seconds)
            if msg_hash in mqtt_cache:
                last_time = mqtt_cache[msg_hash]
                time_diff = current_time - last_time
                if time_diff < 2.0:  # 2 second window for duplicates
                    print(
                        f"[DEDUP] Skipping duplicate: {device_id} {porsi}g ({metode}) "
                        f"- last seen {time_diff:.2f}s ago"
                    )
                    return

            # Record message in cache
            mqtt_cache[msg_hash] = current_time

            # Clean old cache entries (keep last 50 items)
            if len(mqtt_cache) > 50:
                # Remove entries older than 10 seconds
                mqtt_cache_copy = mqtt_cache.copy()
                for hash_key, timestamp in mqtt_cache_copy.items():
                    if current_time - timestamp > 10:
                        mqtt_cache.pop(hash_key, None)

            print(f"[DEVICE] {device_id} fed {porsi}g ({metode})")

            # Get database connection
            conn = get_db_connection(app)
            cursor = conn.cursor(dictionary=True)

            # Find device in database by device_sn
            cursor.execute(
                "SELECT id, current_stock, nickname FROM devices WHERE device_sn = %s", (device_id,)
            )
            device = cursor.fetchone()

            if not device:
                print(f"[DB] Device {device_id} not found in database (not registered)")
                return

            # Insert feeding log (device_id is FK integer to devices.id)
            cursor.execute(
                """INSERT INTO feeding_logs (device_id, grams_out, method)
                   VALUES (%s, %s, %s)""",
                (device["id"], porsi, metode),
            )

            # Update current stock (prevent negative)
            new_stock = max(0, device["current_stock"] - porsi)
            cursor.execute(
                "UPDATE devices SET current_stock = %s WHERE device_sn = %s", (new_stock, device_id)
            )

            conn.commit()

            device_name = device.get("nickname") or device_id
            print(
                f"[DB] Updated {device_name}: -{porsi}g, "
                f"stock: {device['current_stock']}g -> {new_stock}g"
            )

            # Warn if stock is low
            if new_stock < 100:
                print(f"[ALERT] {device_name} stock LOW: {new_stock}g remaining!")

        except mysql.connector.Error as e:
            print(f"[DB] Database error handling device status: {e}")
            if conn:
                conn.rollback()
        except Exception as e:
            print(f"[ERROR] Unexpected error in handle_device_status: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def on_connect(client, userdata, flags, reason_code):
        """Callback when MQTT broker connection is established"""
        if reason_code == 0:
            print(f"[MQTT] Connected to {MQTT_BROKER} successfully")
            # Subscribe to device status messages (ESP32 -> Backend)
            client.subscribe("petfeed/+/status")
            print("[MQTT] Subscribed to petfeed/+/status (device reports)")
        else:
            print(f"[MQTT] Connection failed with code {reason_code}")
            # Connection error codes:
            # 1: Connection refused - incorrect protocol version
            # 2: Connection refused - invalid client identifier
            # 3: Connection refused - server unavailable
            # 4: Connection refused - bad username or password
            # 5: Connection refused - not authorized

    client.on_connect = on_connect
    client.on_message = on_message

    # TLS hanya untuk broker eksternal (port 8883)
    # Internal mosquitto Docker pakai plain 1883 — tidak butuh TLS
    if MQTT_PORT == 8883:
        client.tls_set(cert_reqs=ssl.CERT_NONE)
        client.tls_insecure_set(True)

    # Non-fatal MQTT connect: jalankan di background thread dengan retry
    # App tetap serve HTTP meskipun broker belum ready
    _MAX_MQTT_RETRIES = 10
    _MQTT_RETRY_DELAY = 5  # detik

    def _mqtt_connect_with_retry():
        for attempt in range(1, _MAX_MQTT_RETRIES + 1):
            try:
                client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE)
                client.loop_start()
                print(f"[MQTT] Connected to {MQTT_BROKER}:{MQTT_PORT} (attempt {attempt})")
                return
            except Exception as exc:
                print(f"[MQTT] Attempt {attempt}/{_MAX_MQTT_RETRIES} failed: {exc}")
                if attempt < _MAX_MQTT_RETRIES:
                    time.sleep(_MQTT_RETRY_DELAY)
        print(f"[MQTT] All {_MAX_MQTT_RETRIES} attempts failed — MQTT features unavailable.")

    threading.Thread(target=_mqtt_connect_with_retry, daemon=True).start()

    # --- ROUTES API ---

    @app.route("/api/pair_device")
    def pair_device():
        sn = request.args.get("device_id")
        pet = session.get("temp_pet_data")
        if not pet:
            return redirect(url_for("setup_pet"))

        # Kapasitas dari Config (600 gram)
        default_cap = app.config.get("DEFAULT_MAX_CAPACITY", 600)
        target = PetNutritionManager.calculate_daily_grams(
            pet["species"], pet["category"], pet["weight"], pet["kcal"]
        )

        conn = get_db_connection(app)
        cursor = conn.cursor(dictionary=True)
        try:
            # 1. Insert/update device — owner adalah user yang login
            cursor.execute(
                """
                INSERT INTO devices (device_sn, owner_id, current_stock, max_capacity)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE owner_id = %s, current_stock = %s, max_capacity = %s
                """,
                (
                    sn,
                    session["user_id"],
                    default_cap,
                    default_cap,
                    session["user_id"],
                    default_cap,
                    default_cap,
                ),
            )

            # 2. Ambil id device (PK integer)
            cursor.execute("SELECT id FROM devices WHERE device_sn = %s", (sn,))
            row = cursor.fetchone()
            if not row:
                flash("Gagal menemukan perangkat setelah registrasi.", "danger")
                return redirect(url_for("setup_pet"))
            db_id = row["id"]

            # 3. Insert/update pet (relasi device_id FK ke devices.id)
            cursor.execute("DELETE FROM pets WHERE device_id = %s", (db_id,))
            cursor.execute(
                "INSERT INTO pets (device_id, name, species, category, weight_kg, kcal_per_kg, daily_target_grams) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (
                    db_id,
                    pet["name"],
                    pet["species"],
                    pet["category"],
                    pet["weight"],
                    pet["kcal"],
                    target,
                ),
            )

            # 4. Generate jadwal default
            generate_default_schedules(cursor, db_id, pet["category"], target)
            conn.commit()

            # 5. Kirim jadwal ke ESP32 via MQTT
            trigger_sync(app, client, db_id)
            session.pop("temp_pet_data", None)
            flash(f"Alat terhubung! Stok disetel ke {default_cap}g (100%).", "success")
        finally:
            conn.close()
        return redirect(url_for("dashboard"))

    @app.route("/api/add_schedule", methods=["POST"])
    def add_schedule():
        d_id = request.form.get("device_id")
        t, g = request.form.get("time"), request.form.get("grams")
        conn = get_db_connection(app)
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM feeding_schedules WHERE device_id = %s AND mode = 'system'", (d_id,)
        )
        cursor.execute(
            "INSERT INTO feeding_schedules (device_id, waktu, porsi_gram, mode, is_active) VALUES (%s, %s, %s, 'manual', 1)",
            (d_id, t, g),
        )
        conn.commit()
        conn.close()
        trigger_sync(app, client, d_id)
        return redirect(url_for("schedules"))

    @app.route("/api/edit_schedule", methods=["POST"])
    def edit_schedule():
        s_id = request.form.get("schedule_id")
        t, g = request.form.get("time"), request.form.get("grams")
        conn = get_db_connection(app)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT device_id, mode FROM feeding_schedules WHERE id = %s", (s_id,))
        s = cursor.fetchone()
        if s:
            if s["mode"] == "system":
                cursor.execute("UPDATE feeding_schedules SET waktu = %s WHERE id = %s", (t, s_id))
            else:
                cursor.execute(
                    "UPDATE feeding_schedules SET waktu = %s, porsi_gram = %s WHERE id = %s",
                    (t, g, s_id),
                )
            conn.commit()
            trigger_sync(app, client, s["device_id"])
        conn.close()
        return redirect(url_for("schedules"))

    @app.route("/api/delete_schedule/<int:id>")
    def delete_schedule(id):
        conn = get_db_connection(app)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT device_id FROM feeding_schedules WHERE id = %s", (id,))
        s = cursor.fetchone()
        if s:
            d_id = s["device_id"]
            cursor.execute("DELETE FROM feeding_schedules WHERE id = %s", (id,))
            conn.commit()
            trigger_sync(app, client, d_id)
        conn.close()
        return redirect(url_for("schedules"))

    @app.route("/api/apply_recommendation", methods=["POST"])
    def apply_recommendation():
        d_id = request.form.get("device_id")
        conn = get_db_connection(app)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT category, daily_target_grams FROM pets WHERE device_id = %s", (d_id,)
        )
        p = cursor.fetchone()
        if p:
            generate_default_schedules(cursor, d_id, p["category"], p["daily_target_grams"])
            conn.commit()
            trigger_sync(app, client, d_id)
        conn.close()
        return redirect(url_for("schedules"))

    @app.route("/api/update_pet", methods=["POST"])
    def update_pet():
        d_id = request.form.get("device_id")
        name, weight = request.form.get("nama_kucing"), float(request.form.get("berat"))
        species, category = request.form.get("jenis"), request.form.get("kategori")
        kcal = int(request.form.get("kcal", 4000))
        target = PetNutritionManager.calculate_daily_grams(species, category, weight, kcal)
        conn = get_db_connection(app)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE pets SET name=%s, species=%s, category=%s, weight_kg=%s, kcal_per_kg=%s, daily_target_grams=%s WHERE device_id=%s",
            (name, species, category, weight, kcal, target, d_id),
        )
        generate_default_schedules(cursor, d_id, category, target)
        conn.commit()
        conn.close()
        trigger_sync(app, client, d_id)
        return redirect(url_for("profile"))

    @app.route("/api/feed_now", methods=["POST"])
    def feed_now():
        sn, porsi = request.json.get("device_id"), int(request.json.get("porsi", 15))
        client.publish(
            f"petfeed/{sn}/perintah",
            json.dumps({"action": "feed", "porsi": porsi, "metode": "manual"}),
            qos=1,
        )
        return jsonify({"status": "success"})

    @app.route("/api/refill", methods=["POST"])
    def refill():
        d_id, amt = request.form.get("device_id"), request.form.get("amount")
        conn = get_db_connection(app)
        cursor = conn.cursor()
        # Mencegah stok melebihi max_capacity (600g)
        cursor.execute(
            "UPDATE devices SET current_stock = LEAST(max_capacity, current_stock + %s) WHERE id = %s",
            (amt, d_id),
        )
        cursor.execute(
            "INSERT INTO pantry_refills (device_id, grams_added) VALUES (%s, %s)", (d_id, amt)
        )
        conn.commit()
        conn.close()
        flash("Stok Pantry diperbarui.", "success")
        return redirect(url_for("dashboard"))

    @app.route("/api/reset_password", methods=["POST"])
    def reset_password():
        new_pw = request.form.get("new_password")
        if new_pw:
            pw_h = bcrypt.generate_password_hash(new_pw).decode("utf-8")
            conn = get_db_connection(app)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET password_hash = %s WHERE user_id = %s", (pw_h, session["user_id"])
            )
            conn.commit()
            conn.close()
            flash("Password diubah!", "success")
        return redirect(url_for("profile"))

    @app.route("/api/reset_device")
    def reset_device():
        """Memperbaiki error reset alat dengan urutan delete yang benar."""
        user_id = session.get("user_id")
        conn = get_db_connection(app)
        cursor = conn.cursor(dictionary=True)

        # Ambil info alat sebelum dihapus
        cursor.execute("SELECT id, device_sn FROM devices WHERE owner_id = %s", (user_id,))
        data = cursor.fetchone()

        if data:
            d_pk = data["id"]  # ID integer (PK)

            try:
                # 1. Hapus Feeding Logs (FK integer ke devices.id)
                cursor.execute("DELETE FROM feeding_logs WHERE device_id = %s", (d_pk,))
                # 2. Hapus Pantry Refills (menggunakan device_id FK)
                cursor.execute("DELETE FROM pantry_refills WHERE device_id = %s", (d_pk,))
                # 3. Hapus Feeding Schedules (menggunakan device_id FK)
                cursor.execute("DELETE FROM feeding_schedules WHERE device_id = %s", (d_pk,))
                # 4. Hapus Profil Hewan
                cursor.execute("DELETE FROM pets WHERE device_id = %s", (d_pk,))
                # 5. Terakhir, hapus alat dari tabel devices
                cursor.execute("DELETE FROM devices WHERE id = %s", (d_pk,))

                conn.commit()
                flash("Alat berhasil di-reset dan dilepaskan.", "info")
            except Exception as e:
                conn.rollback()
                print(f"[RESET ERROR] {e}")
                flash("Gagal mereset alat. Silakan coba lagi.", "danger")

        conn.close()
        return redirect(url_for("onboarding_choice"))
