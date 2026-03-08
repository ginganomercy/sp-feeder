# Smart Pet Feeder - Setup Guide

Panduan singkat untuk setup dan running aplikasi Smart Pet Feeder.

---

## 📋 Requirements

- Python 3.10+
- MySQL/MariaDB
- Internet connection (untuk MQTT)

---

## 🚀 Setup (5 Menit)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Konfigurasi Database

Edit file `.env`:
```env
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DB=smart_pet_feeder
```

### 3. Setup Database
```bash
python setup_database.py
```

### 4. Run Application
```bash
# Activate venv
.\venv\Scripts\Activate.ps1

# Run
python app.py
```

**Buka:** http://localhost:5011

---

## 🎯 Default Configuration

| Setting | Default Value | Keterangan |
|---------|---------------|------------|
| Server Port | 5011 | Ubah di `.env` jika perlu |
| MQTT Broker | broker.hivemq.com | Public HiveMQ broker |
| Debug Mode | True | Development mode |
| DB Pool Size | 10 connections | Auto-managed |
| Log Location | `logs/petfeeder.log` | Rotating logs |

---

## 📝 First Time Use

1. **Register user baru** di http://localhost:5011/register
   - Username: `admin`
   - Email: `admin@test.com`
   - Password: `admin123`

2. **Setup pet** - Ikuti onboarding wizard

3. **Pair device** - Masukkan device serial number dari ESP32

4. **Set schedule** - Configure automatic feeding

---

## 🔧 Troubleshooting

### Error: Database not found
```bash
python setup_database.py
```

### Error: Port already in use
Edit `.env`:
```env
SERVER_PORT=5012
```

### MQTT tidak connect
- Cek internet connection
- Aplikasi tetap berjalan tanpa MQTT
- MQTT hanya untuk real-time features

---

## 📚 Files Penting

- `.env` - Configuration
- `logs/petfeeder.log` - Application logs
- `README.md` - Documentation
- `docs/DATABASE_DESIGN.md` - Database schema

---

## ⚡ Quick Commands

```bash
# Start development server
python app.py

# View logs
Get-Content logs\petfeeder.log -Wait

# Setup database
python setup_database.py

# Check database tables
mysql -u root -p smart_pet_feeder -e "SHOW TABLES"
```

---

**Updated:** 2026-02-12  
**Version:** 1.1.0
