"""
Database Setup & Test Script
Membantu setup database dan test koneksi untuk Smart Pet Feeder
"""

import os

import mysql.connector

from config import Config


def test_connection():
    """Test koneksi ke MySQL server"""
    print("🔍 Testing MySQL connection...")
    try:
        conn = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            port=Config.MYSQL_PORT,
        )
        print("✅ MySQL server connection successful!")
        print(f"   Host: {Config.MYSQL_HOST}:{Config.MYSQL_PORT}")
        print(f"   User: {Config.MYSQL_USER}")
        conn.close()
        return True
    except mysql.connector.Error as err:
        print(f"❌ MySQL connection failed: {err}")
        print("\n💡 Tips:")
        print("   1. Pastikan MySQL server running (check Laragon/XAMPP)")
        print("   2. Cek credentials di file .env")
        print("   3. Cek port MySQL (default: 3306)")
        return False


def check_database_exists():
    """Cek apakah database sudah dibuat"""
    print(f"\n🔍 Checking database '{Config.MYSQL_DB}'...")
    try:
        conn = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            port=Config.MYSQL_PORT,
        )
        cursor = conn.cursor()
        cursor.execute(f"SHOW DATABASES LIKE '{Config.MYSQL_DB}'")
        result = cursor.fetchone()
        conn.close()

        if result:
            print(f"✅ Database '{Config.MYSQL_DB}' exists!")
            return True
        else:
            print(f"⚠️  Database '{Config.MYSQL_DB}' not found")
            return False
    except mysql.connector.Error as err:
        print(f"❌ Error checking database: {err}")
        return False


def test_database_tables():
    """Test koneksi ke database dan cek tabel"""
    print("\n🔍 Testing database tables...")
    try:
        conn = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            port=Config.MYSQL_PORT,
        )
        cursor = conn.cursor()

        # Check tables
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]

        expected_tables = [
            "users",
            "devices",
            "pets",
            "feeding_schedules",
            "feeding_logs",
            "pantry_refills",
        ]

        print(f"\n📋 Found {len(tables)} tables:")
        for table in tables:
            status = "✅" if table in expected_tables else "⚠️ "
            print(f"   {status} {table}")

        missing_tables = set(expected_tables) - set(tables)
        if missing_tables:
            print(f"\n⚠️  Missing tables: {', '.join(missing_tables)}")
            print(
                f"   Run: mysql -u {Config.MYSQL_USER} -p {Config.MYSQL_DB} < smart_pet_feeder.sql"
            )
        else:
            print("\n✅ All required tables exist!")

        # Check sample data
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print("\n📊 Database stats:")
        print(f"   Users: {user_count}")

        conn.close()
        return True

    except mysql.connector.Error as err:
        print(f"❌ Database test failed: {err}")
        return False


def import_schema():
    """Import schema SQL file"""
    sql_file = "smart_pet_feeder.sql"

    if not os.path.exists(sql_file):
        print(f"❌ File {sql_file} not found!")
        return False

    print(f"\n📥 Importing schema from {sql_file}...")
    try:
        conn = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            port=Config.MYSQL_PORT,
        )
        cursor = conn.cursor()

        # Create database if not exists
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.MYSQL_DB}")
        cursor.execute(f"USE {Config.MYSQL_DB}")

        # Read and execute SQL file
        with open(sql_file, "r", encoding="utf-8") as f:
            sql_script = f.read()

        # Split by statement and execute
        for statement in sql_script.split(";"):
            if statement.strip():
                try:
                    cursor.execute(statement)
                except mysql.connector.Error as err:
                    # Skip errors for existing objects
                    if "already exists" not in str(err).lower():
                        print(f"⚠️  Warning: {err}")

        conn.commit()
        conn.close()
        print("✅ Schema imported successfully!")
        return True

    except mysql.connector.Error as err:
        print(f"❌ Import failed: {err}")
        return False


def main():
    """Main setup wizard"""
    print("=" * 60)
    print("🐾 SMART PET FEEDER - Database Setup Wizard")
    print("=" * 60)

    # Step 1: Test MySQL connection
    if not test_connection():
        print("\n❌ Setup cannot continue. Fix MySQL connection first.")
        return

    # Step 2: Check if database exists
    db_exists = check_database_exists()

    if not db_exists:
        print("\n📋 Database needs to be created.")
        response = input(f"\n❓ Create database '{Config.MYSQL_DB}' and import schema? (y/n): ")

        if response.lower() == "y":
            if import_schema():
                print("\n🎉 Database setup complete!")
            else:
                print("\n❌ Database setup failed!")
                return
        else:
            print("\n⚠️  You need to manually create the database:")
            print(f"   mysql -u {Config.MYSQL_USER} -p < smart_pet_feeder.sql")
            return

    # Step 3: Test tables
    test_database_tables()

    print("\n" + "=" * 60)
    print("✅ Setup verification complete!")
    print("=" * 60)
    print("\n📝 Next steps:")
    print("   1. Jalankan aplikasi: python app.py")
    print("   2. Buka browser: http://localhost:5011")
    print("   3. Register user baru untuk mulai menggunakan")
    print()


if __name__ == "__main__":
    main()
