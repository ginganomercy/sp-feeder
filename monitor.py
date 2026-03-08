import csv
import json
import os
from datetime import datetime

import paho.mqtt.client as mqtt

# ==========================================
# KONFIGURASI (SINKRON DENGAN APP.PY)
# ==========================================
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
# Mendengarkan status dari SEMUA alat (wildcard +)
MQTT_TOPIC_STATUS = "petfeed/+/status"
CSV_FILE = "riwayat_pakan_lokal.csv"


def log_to_csv(data):
    """
    Mencatat data ke file CSV sebagai cadangan lokal.
    """
    file_exists = os.path.isfile(CSV_FILE)
    try:
        with open(CSV_FILE, mode="a", newline="") as file:
            writer = csv.writer(file)
            if not file_exists:
                # Header file CSV
                writer.writerow(["Waktu_Server", "Device_ID", "Porsi_Gram", "Metode", "Pesan"])

            writer.writerow(
                [
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    data.get("device_id", "Unknown"),
                    data.get("porsi", 0),
                    data.get("metode", "n/a"),
                    data.get("message", "Sukses"),
                ]
            )
        print(f"[CSV] Berhasil mencatat log untuk {data.get('device_id')}")
    except Exception as e:
        print(f"[ERROR CSV] {e}")


# ==========================================
# MQTT CALLBACKS
# ==========================================
def on_connect(client, userdata, flags, rc, properties):
    if rc == 0:
        print(f"[*] Monitor Aktif. Mendengarkan di: {MQTT_TOPIC_STATUS}")
        client.subscribe(MQTT_TOPIC_STATUS)
    else:
        print(f"[!] Gagal terkoneksi ke broker, kode: {rc}")


def on_message(client, userdata, msg):
    """
    Dijalankan setiap kali ada alat yang melapor (Feeding Success).
    """
    try:
        payload = json.loads(msg.payload.decode())
        dev_id = payload.get("device_id", "Unknown")

        print(f"\n[LAPORAN MASUK - {datetime.now().strftime('%H:%M:%S')}]")
        print(f"ID Alat : {dev_id}")
        print(f"Porsi   : {payload.get('porsi')}g")
        print(f"Metode  : {payload.get('metode')}")

        # Simpan ke CSV
        log_to_csv(payload)

    except Exception as e:
        print(f"[!] Gagal memproses pesan MQTT: {e}")


# ==========================================
# MAIN LOOP
# ==========================================
if __name__ == "__main__":
    # Menggunakan MQTT Client API v2
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message

    print(f"[*] Menghubungkan ke Broker: {MQTT_BROKER}...")
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n[*] Monitor dihentikan oleh pengguna.")
    except Exception as e:
        print(f"[!] Kesalahan sistem: {e}")
