"""
MQTT Monitor & Diagnostic Tool for Smart Pet Feeder
Monitors all MQTT traffic and tests schedule sync

Usage:
    python mqtt_diagnostics.py

Features:
    1. Monitors all petfeed/# topics
    2. Manual schedule sync trigger
    3. Connection status checker
"""

import json
import os
import sys
import time
from datetime import timedelta

import mysql.connector
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MQTT Configuration
MQTT_BROKER = os.getenv("MQTT_BROKER", "broker.hivemq.com")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_KEEPALIVE = 60

# Database Configuration
DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", "admin19"),
    "database": os.getenv("MYSQL_DB", "smart_pet_feeder"),
}


def get_db_connection():
    """Get database connection"""
    return mysql.connector.connect(**DB_CONFIG)


def on_connect(client, userdata, flags, rc):
    """MQTT Connection callback"""
    if rc == 0:
        print(f"\n✅ [MQTT] Connected to {MQTT_BROKER}")
        # Subscribe to ALL petfeed topics
        client.subscribe("petfeed/#")
        print("📡 [MQTT] Subscribed to petfeed/# (all topics)\n")
    else:
        print(f"❌ [MQTT] Connection failed with code {rc}")


def on_message(client, userdata, msg):
    """MQTT Message callback - Monitor all traffic"""
    try:
        topic = msg.topic
        payload = msg.payload.decode()

        print(f"\n📨 [MQTT MESSAGE RECEIVED]")
        print(f"   Topic: {topic}")
        print(f"   Payload: {payload}")

        # Try to parse JSON
        try:
            data = json.loads(payload)
            print(f"   Parsed: {json.dumps(data, indent=6)}")
        except json.JSONDecodeError:
            print(f"   (Not JSON format)")

        print("-" * 60)

    except Exception as e:
        print(f"❌ [ERROR] Processing message: {e}")


def get_device_info(device_id):
    """Get device serial number from database"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT device_sn FROM devices WHERE id = %s", (device_id,))
    device = cursor.fetchone()

    conn.close()
    return device


def get_schedules(device_id):
    """Get active schedules for device"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """SELECT waktu, porsi_gram 
           FROM feeding_schedules 
           WHERE device_id = %s AND is_active = 1
           ORDER BY waktu""",
        (device_id,),
    )
    schedules = cursor.fetchall()

    conn.close()
    return schedules


def format_schedule(waktu):
    """Format time for ESP32"""
    if isinstance(waktu, timedelta):
        hours, remainder = divmod(waktu.seconds, 3600)
        minutes = remainder // 60
        return f"{hours:02d}:{minutes:02d}"
    else:
        return str(waktu)[:5]


def trigger_manual_sync(client, device_id):
    """Manually trigger schedule sync to ESP32"""
    print(f"\n🔄 [SYNC] Triggering manual sync for device ID {device_id}...")

    # Get device info
    device = get_device_info(device_id)
    if not device:
        print(f"❌ [ERROR] Device ID {device_id} not found in database")
        return

    device_sn = device["device_sn"]
    print(f"   Device SN: {device_sn}")

    # Get schedules
    schedules = get_schedules(device_id)
    print(f"   Active Schedules: {len(schedules)}")

    if not schedules:
        print("   ⚠️  No active schedules found!")
        return

    # Format schedules
    formatted_schedules = []
    for s in schedules:
        time_str = format_schedule(s["waktu"])
        formatted_schedules.append({"t": time_str, "p": s["porsi_gram"]})
        print(f"      - {time_str} → {s['porsi_gram']}g")

    # Build payload
    payload = json.dumps({"action": "sync", "schedules": formatted_schedules})

    # Publish to MQTT
    topic = f"petfeed/{device_sn}/perintah"
    print(f"\n📤 [PUBLISHING]")
    print(f"   Topic: {topic}")
    print(f"   Payload: {payload}")

    result = client.publish(topic, payload, qos=1)

    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        print(f"✅ [SUCCESS] Schedule sync sent to ESP32!")
        print(f"\n⏳ Waiting for ESP32 response...")
        print(f"   (ESP32 should publish to petfeed/{device_sn}/status)")
    else:
        print(f"❌ [ERROR] Failed to publish (error code: {result.rc})")


def test_manual_feed(client, device_sn, porsi=10):
    """Test manual feed command"""
    print(f"\n🧪 [TEST] Sending manual feed command...")
    print(f"   Device: {device_sn}")
    print(f"   Amount: {porsi}g")

    payload = json.dumps({"action": "feed", "porsi": porsi, "metode": "manual"})
    topic = f"petfeed/{device_sn}/perintah"

    print(f"\n📤 [PUBLISHING]")
    print(f"   Topic: {topic}")
    print(f"   Payload: {payload}")

    result = client.publish(topic, payload, qos=1)

    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        print(f"✅ [SUCCESS] Manual feed command sent!")
        print(f"⏳ ESP32 should execute and publish status...")
    else:
        print(f"❌ [ERROR] Failed to publish")


def main():
    """Main diagnostic loop"""
    print("=" * 60)
    print("  🔧 MQTT DIAGNOSTIC TOOL - Smart Pet Feeder")
    print("=" * 60)

    # Create MQTT client
    client_id = f"diagnostic-tool-{int(time.time())}"
    client = mqtt.Client(client_id=client_id)

    client.on_connect = on_connect
    client.on_message = on_message

    print(f"\n🔌 Connecting to {MQTT_BROKER}:{MQTT_PORT}...")

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE)
        client.loop_start()

        print("\n" + "=" * 60)
        print("  📋 DIAGNOSTIC MENU")
        print("=" * 60)
        print("  1. Monitor MQTT traffic (current)")
        print("  2. Trigger schedule sync")
        print("  3. Send test manual feed")
        print("  4. Show device info")
        print("  0. Exit")
        print("=" * 60)

        while True:
            cmd = input("\n➤ Enter command (1-4, 0=exit): ").strip()

            if cmd == "0":
                print("\n👋 Exiting...")
                break

            elif cmd == "1":
                print("\n👀 Monitoring MQTT traffic...")
                print("   (Press Ctrl+C to show menu again)")
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\n\n📋 Showing menu...")

            elif cmd == "2":
                device_id = input("   Device ID (default=4): ").strip() or "4"
                trigger_manual_sync(client, int(device_id))

            elif cmd == "3":
                device_sn = (
                    input("   Device SN (default=PET-A0DFC8D8CBB0): ").strip()
                    or "PET-A0DFC8D8CBB0"
                )
                porsi = input("   Portion (default=10): ").strip() or "10"
                test_manual_feed(client, device_sn, int(porsi))

            elif cmd == "4":
                conn = get_db_connection()
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT id, device_sn FROM devices")
                devices = cursor.fetchall()
                conn.close()

                print("\n📱 Devices in Database:")
                for d in devices:
                    print(f"   ID: {d['id']} → SN: {d['device_sn']}")

            else:
                print("❌ Invalid command")

    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")
    except Exception as e:
        print(f"\n❌ [ERROR] {e}")
    finally:
        client.loop_stop()
        client.disconnect()
        print("🔌 Disconnected from MQTT broker")


if __name__ == "__main__":
    main()
