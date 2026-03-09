import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Konfigurasi untuk Flask Smart Pet Feeder.
    Menggunakan environment variables untuk keamanan yang lebih baik.
    """

    # Security - CRITICAL: Gunakan SECRET_KEY yang kuat di production
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key-only-change-in-production")

    # Database MySQL Configuration
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DB = os.getenv("MYSQL_DB", "smart_pet_feeder")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))

    # MQTT Broker Configuration
    MQTT_BROKER = os.getenv("MQTT_BROKER", "broker.hivemq.com")
    MQTT_PORT = int(os.getenv("MQTT_PORT", 8883))

    # Hardware Configuration (Dalam Gram)
    DEFAULT_MAX_CAPACITY = int(os.getenv("DEFAULT_MAX_CAPACITY", 600))

    # Flask Configuration
    DEBUG = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")

    # Domain & HTTPS Configuration
    # Digunakan untuk url_for() dengan _external=True dan secure cookies
    APP_DOMAIN = os.getenv("APP_DOMAIN", "localhost")
    PREFERRED_URL_SCHEME = os.getenv("PREFERRED_URL_SCHEME", "http")

    # Session security — aktifkan di production (HTTPS)
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "False").lower() in ("true", "1", "yes")
    SESSION_COOKIE_HTTPONLY = True   # Selalu: cegah akses cookie via JavaScript
    SESSION_COOKIE_SAMESITE = "Lax" # Proteksi CSRF dasar
