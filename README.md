# 🐾 Smart Pet Feeder - Enterprise IoT Application

**Production-ready automated pet feeding system with ESP32 integration, MQTT protocol, and cloud deployment.**

[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.12-green)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-red)](https://flask.palletsprojects.com/)
[![Code Quality](https://img.shields.io/badge/Code%20Quality-Production--Ready-success)]()

---

## 📋 Table of Contents

- [Features](#-features)
- [Quick Start](#-quick-start)
  - [Local Development](#local-development)
  - [Docker Development](#docker-development)
  - [Production Deployment](#production-deployment)
- [Technology Stack](#️-technology-stack)
- [Project Structure](#-project-structure)
- [Configuration](#️-configuration)
- [Database](#-database)
- [IoT Integration](#-iot-integration)
- [Development](#-development)
- [Deployment](#-deployment)
- [Documentation](#-documentation)

---

## ✨ Features

### 🌐 Web Application
- ✅ **Authentication** - Secure user registration & login with bcrypt
- ✅ **Pet Management** - Onboarding wizard for pet profiles
- ✅ **Smart Scheduling** - Automated feeding based on pet nutrition needs
- ✅ **Real-time Monitoring** - Live device status & feeding logs
- ✅ **Analytics Dashboard** - Weekly feeding statistics & charts
- ✅ **Stock Management** - Pantry level tracking & low stock alerts

### 🔌 IoT Integration
- ✅ **MQTT Protocol** - Real-time bi-directional communication
- ✅ **ESP32 Support** - Arduino-based feeder device integration
- ✅ **Remote Control** - Manual feeding from web interface
- ✅ **Device Pairing** - QR code-based device registration
- ✅ **Status Reporting** - Automatic feeding event logging
- ✅ **Multi-device** - Support for multiple feeder devices per account

### 🏗️ Production Features
- ✅ **Dockerized** - Multi-stage builds for optimal image size (\u003c200MB)
- ✅ **CI/CD Pipeline** - GitHub Actions with Tailscale SSH deployment
- ✅ **Database Pooling** - Connection pool for 6-10x performance boost
- ✅ **Structured Logging** - Rotating file logs with proper error tracking
- ✅ **Health Checks** - Docker health monitoring for all services
- ✅ **Code Quality** - Black, isort, Flake8 compliance (PEP 8)
- ✅ **Security** - Non-root containers, secret management, bcrypt hashing

---

## 🚀 Quick Start

### Local Development

**Prerequisites:**
- Python 3.12+
- MySQL 8.0+
- pip

**Steps:**

```bash
# 1. Clone repository
git clone <repository-url>
cd smart_pet_feeder

# 2. Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell
# or
source venv/bin/activate      # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your database credentials

# 5. Setup database
python setup_database.py

# 6. Run application
python app.py
```

**Access:** http://localhost:5011

---

### Docker Development

**Prerequisites:**
- Docker 20.10+
- Docker Compose 2.0+

**Steps:**

```bash
# 1. Configure environment
cp .env.example .env.docker
# Edit .env.docker if needed

# 2. Start development environment
make dev-up
# or
docker-compose -f docker-compose.dev.yml up

# 3. View logs
make dev-logs
```

**Features:**
- ✅ Hot-reload enabled  
- ✅ Debug mode active  
- ✅ MySQL 8.0 container  
- ✅ Volume mounts for live code changes

**Access:** http://localhost:8000

---

### Production Deployment

**Prerequisites:**
- GitHub repository
- Proxmox Debian VM (or any Linux server)
- Tailscale account
- Docker & Docker Compose on server

**Steps:**

1. **Configure GitHub Secrets** (see [REPO.md](REPO.md))
2. **Push to main branch:**
   ```bash
   git add .
   git commit -m "Deploy to production"
   git push origin main
   ```
3. **Monitor deployment** in GitHub Actions
4. **Access application** at your configured domain

**Full Guide:** [REPO.md](REPO.md)

---

## 🛠️ Technology Stack

### Backend
| Component | Technology | Version |
|-----------|-----------|---------|
| **Framework** | Flask | 3.0.0 |
| **Database** | MySQL | 8.0 |
| **WSGI Server** | Gunicorn | 21.2.0 |
| **IoT Protocol** | MQTT (paho-mqtt) | 1.6.1 |
| **Password Hashing** | Flask-Bcrypt | 1.0.1 |
| **Connection Pooling** | mysql-connector-python | 8.2.0 |

### Frontend
- HTML5 / CSS3 / JavaScript
- Bootstrap 5 (responsive design)
- Chart.js (data visualization)
- Jinja2 templating

### Infrastructure
| Component | Technology |
|-----------|-----------|
| **Containerization** | Docker multi-stage builds |
| **Orchestration** | Docker Compose |
| **CI/CD** | GitHub Actions |
| **VPN** | Tailscale (secure SSH) |
| **MQTT Broker** | HiveMQ (public) / Mosquitto (private) |

### IoT Hardware
- **Controller:** ESP32 DevKit v1
- **Communication:** WiFi + MQTT
- **Actuator:** Servo motor (SG90)
- **Sensor:** Load cell (HX711)
- **Firmware:** Arduino + PubSubClient

---

## 📁 Project Structure

```
smart_pet_feeder/
├── 🐍 Backend
│   ├── app.py                     # Main Flask application
│   ├── api_handler.py             # MQTT & API routes
│   ├── config.py                  # Configuration management
│   ├── db_pool.py                 # Database connection pooling
│   ├── logger_config.py           # Structured logging
│   ├── nutrition_logic.py         # Pet nutrition calculations
│   └── scheduler.py               # Feeding schedule logic
│
├── 🌐 Frontend
│   ├── templates/                 # Jinja2 HTML templates
│   │   ├── auth/                  # Login, register
│   │   ├── dashboard/             # Dashboard, stats, profile
│   │   ├── onboarding/            # Pet setup wizard
│   │   └── layout.html            # Base template
│   └── static/                    # CSS, JS, images
│
├── 🐳 Docker
│   ├── Dockerfile                 # Multi-stage production build
│   ├── docker-compose.yml         # Production configuration
│   ├── docker-compose.dev.yml     # Development configuration
│   ├── .dockerignore              # Build exclusions
│   └── docker/
│       ├── mysql/init.sql         # Database initialization
│       └── mosquitto/config/      # MQTT broker config
│
├── 🔄 CI/CD
│   └── .github/workflows/
│       └── deploy.yml             # GitHub Actions deployment
│
├── 📚 Documentation
│   ├── README.md                  # This file
│   ├── REPO.md                    # GitHub Secrets setup guide
│   ├── SETUP_DEVELOPMENT.md       # Development environment guide
│   ├── QUICKSTART_PHASE1.md       # Phase 1 refactoring notes
│   └── docs/
│       ├── DATABASE_DESIGN.md     # Database schema rationale
│       └── LINTING_GUIDE.md       # Code quality tools
│
├── ⚙️ Configuration
│   ├── .env.example               # Environment template
│   ├── .env.docker                # Docker environment template
│   ├── requirements.txt           # Python dependencies
│   ├── setup.cfg                  # Flake8, isort config
│   ├── Makefile                   # Command shortcuts
│   └── smart_pet_feeder.sql       # Database schema
│
└── 🛠️ Scripts
    ├── setup_database.py          # Database setup utility
    ├── start_dev.ps1              # Windows dev startup
    └── start_dev.bat              # Windows dev startup (CMD)
```

---

## ⚙️ Configuration

### Environment Variables

Create `.env` file (local) or `.env.docker` (Docker):

```env
# ========================================
# DATABASE CONFIGURATION
# ========================================
MYSQL_HOST=localhost              # or 'db' for Docker
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_secure_password
MYSQL_DB=smart_pet_feeder
MYSQL_ROOT_PASSWORD=root_password  # Docker only

# ========================================
# FLASK SERVER CONFIGURATION
# ========================================
SERVER_HOST=0.0.0.0
SERVER_PORT=5011                   # 8000 for Docker
FLASK_DEBUG=True                   # False for production
SECRET_KEY=your-secret-key-here    # Use secrets.token_hex(32)

# ========================================
# MQTT BROKER CONFIGURATION
# ========================================
MQTT_BROKER=broker.hivemq.com      # Public broker (ESP32 compatible)
MQTT_PORT=1883
MQTT_KEEPALIVE=60

# ========================================
# LOGGING CONFIGURATION  
# ========================================
LOG_LEVEL=INFO                     # DEBUG, INFO, WARNING, ERROR
MAX_LOG_SIZE=10485760              # 10MB
BACKUP_COUNT=5

# ========================================
# DATABASE CONNECTION POOL
# ========================================
POOL_NAME=petfeeder_pool
POOL_SIZE=10
MAX_OVERFLOW=5
```

**Generate Secure Keys:**

```bash
# Flask SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

# MySQL Passwords
python -c "import secrets; print(secrets.token_urlsafe(24))"
```

---

## 🗄️ Database

### Schema Overview

```sql
-- User Management
users (id, username, email, password_hash, created_at)

-- Device Management  
devices (id, device_sn, owner_id, current_stock, max_capacity, nickname)

-- Pet Profiles
pets (id, device_id, name, species, weight_kg, daily_target_grams)

-- Scheduling
feeding_schedules (id, device_id, time, grams, active)

-- History
feeding_logs (id, device_id, timestamp, grams_out, method)
pantry_refills (id, device_id, timestamp, grams_added)
```

### Setup Database

**Automatic Setup:**
```bash
python setup_database.py
```

**Manual Setup:**
```bash
mysql -u root -p < smart_pet_feeder.sql
```

**Docker Setup:**
Database is automatically initialized on first startup via `docker/mysql/init.sql`

**Default Admin User:**
- Username: `admin`
- Password: `admin123`
- ⚠️ **Change immediately in production!**

---

## 🔌 IoT Integration

### MQTT Architecture

```
ESP32 Device ────MQTT────> HiveMQ Broker <────MQTT──── Flask Backend
                 pub/sub                      subscribe
```

**Topics:**

| Direction | Topic | Payload | Purpose |
|-----------|-------|---------|---------|
| **ESP32 → Backend** | `petfeed/{DEVICE_ID}/status` | `{"porsi":20,"metode":"manual"}` | Feeding event report |
| **Backend → ESP32** | `petfeed/{DEVICE_ID}/manual` | `{"porsi":50}` | Manual feed command |

### Device Pairing

1. User clicks "Pair Device" in dashboard
2. Scan QR code on ESP32 device
3. Device serial number is registered
4. Backend subscribes to device topic
5. Device can now send/receive commands

### ESP32 Firmware

**Required Libraries:**
- WiFi.h
- PubSubClient.h  
- ArduinoJson.h

**Connection:**
```cpp
const char* mqtt_server = "broker.hivemq.com";
const int mqtt_port = 1883;
String topic_status = "petfeed/" + deviceID + "/status";
```

**Example Code:** See [ESP32 Firmware Analysis](docs/ESP32_INTEGRATION.md)

---

## 👨‍💻 Development

### Code Quality Tools

**Installed:**
```bash
pip install black isort flake8
```

**Run Formatters:**
```bash
# Format all Python files
make format

# or manually:
black .
isort .
```

**Run Linter:**
```bash
# Check PEP 8 compliance
make lint

# or manually:
flake8 . --exclude=venv,env --max-line-length=100
```

**Run All Checks:**
```bash
make check  # format + lint
```

### Development Scripts

**Windows PowerShell:**
```bash
.\start_dev.ps1
```

**Windows CMD:**
```bash
start_dev.bat
```

**Docker Development:**
```bash
make dev-up      # Start development containers
make dev-down    # Stop containers
make dev-logs    # View logs
make dev-shell   # Enter web container shell
```

### Hot Reload

Docker development mode supports hot reload:
- Edit Python files → Server auto-restarts
- Edit templates → Refresh browser  
- Database changes → Use migrations

---

## 🚢 Deployment

### Docker Production

**Build & Run:**
```bash
# Production mode
make up

# or manually:
docker-compose up -d --build
```

**Features:**
- ✅ Multi-stage build (optimized size)
- ✅ Non-root user (`appuser`)
- ✅ Gunicorn WSGI server (4 workers)
- ✅ Health checks (30s interval)
- ✅ Auto-restart on failure
- ✅ MySQL 8.0 with persistent storage  
- ✅ Mosquitto MQTT broker (optional)

**View Logs:**
```bash
make logs
docker-compose logs -f web
```

**Access:**  
http://localhost:8000 (or configured port)

---

### CI/CD Automated Deployment

**Workflow:** `.github/workflows/deploy.yml`

**Trigger:**  
Push to `main` branch → Auto-deploy to production

**Pipeline Steps:**
1. ✅ Checkout code
2. ✅ Connect to Tailscale VPN
3. ✅ SSH to production server
4. ✅ Create `.env.docker` from GitHub Secrets
5. ✅ Sync files via rsync
6. ✅ Build Docker image
7. ✅ Start containers (`docker-compose up -d`)
8. ✅ Health check validation
9. ✅ Cleanup old images
10. ✅ Send notification (success/failure)

**Setup Guide:** [REPO.md](REPO.md)

**Required GitHub Secrets (10):**
- TAILSCALE_OAUTH_CLIENT_ID
- TAILSCALE_OAUTH_SECRET  
- SERVER_SSH_HOST
- SERVER_SSH_USER
- SERVER_SSH_KEY
- MYSQL_ROOT_PASSWORD
- MYSQL_PASSWORD
- FLASK_SECRET_KEY
- SERVER_DOMAIN
- DEPLOY_PATH

---

## 📊 Monitoring

### Application Logs

**Location:**
```
logs/petfeeder.log
```

**Log Levels:**
- DEBUG: Detailed debugging info
- INFO: Normal operation events  
- WARNING: Important events (low stock, MQTT disconnect)
- ERROR: Error conditions (DB failure, MQTT error)

**View Logs:**
```powershell
# Windows PowerShell
Get-Content logs\petfeeder.log -Wait -Tail 50

# Linux/Mac
tail -f logs/petfeeder.log
```

### Docker Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f db
docker-compose logs -f mosquitto
```

### Health Checks

**Web:**
```bash
curl http://localhost:8000/
# Expected: HTTP 200 + HTML response
```

**Database:**
```bash
docker exec smart_pet_feeder_db_1 mysqladmin ping -h localhost
# Expected: mysqld is alive
```

**MQTT Broker:**
```bash
docker exec smart_pet_feeder_mosquitto_1 cat /mosquitto/log/mosquitto.log
```

---

## 🔒 Security

### Production Checklist

- [x] **Passwords:** Use strong, random passwords (24+ chars)
- [x] **SECRET_KEY:** Generate with `secrets.token_hex(32)`
- [x] **FLASK_DEBUG:** Set to `False` in production
- [x] **Docker:** Run as non-root user (`appuser`)
- [x] **Database:** User has limited privileges (not root)
- [x] **Secrets:** Stored in GitHub Secrets (not in code)
- [x] **HTTPS:** Use reverse proxy (Nginx/Traefik + Let's Encrypt)
- [x] **Firewall:** Limit ports (80, 443, SSH only)
- [ ] **MQTT:** Migrate to private broker with authentication
- [ ] **CSP:** Implement Content Security Policy headers
- [ ] **Rate Limiting:** Add rate limiting for API endpoints

### Bcrypt Password Hashing

```python
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()

# Hash password
hashed = bcrypt.generate_password_hash(password).decode('utf-8')

# Verify password  
bcrypt.check_password_hash(hashed_password, plain_password)
```

---

## 🐛 Troubleshooting

### Common Issues

**Port Already in Use:**
```bash
# Change port in .env
SERVER_PORT=5012
```

**Database Connection Failed:**
```bash
# Verify MySQL is running
sudo systemctl status mysql  # Linux
# Check Laragon/XAMPP           # Windows

# Test connection
python setup_database.py
```

**MQTT Not Connecting:**
- Application continues working without MQTT
- Check internet connection
- Verify `MQTT_BROKER=broker.hivemq.com` in `.env`
- Check broker status: https://www.hivemq.com/mqtt-cloud-broker/

**Docker Build Fails:**
```bash
# Clean Docker system
docker system prune -a

# Rebuild without cache
docker-compose build --no-cache
```

**Permission Denied (Docker):**
```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [README.md](README.md) | Main documentation (this file) |
| [REPO.md](REPO.md) | GitHub Secrets & CI/CD setup |
| [SETUP_DEVELOPMENT.md](SETUP_DEVELOPMENT.md) | Development environment guide |
| [DATABASE_DESIGN.md](docs/DATABASE_DESIGN.md) | Database schema rationale |
| [LINTING_GUIDE.md](docs/LINTING_GUIDE.md) | Code quality tools reference |
| [QUICKSTART_PHASE1.md](QUICKSTART_PHASE1.md) | Phase 1 refactoring notes |

---

## 🎯 Roadmap

### ✅ Completed (v1.0)
- Core web application functionality
- ESP32 MQTT integration  
- Docker containers & orchestration
- CI/CD pipeline with GitHub Actions
- Code quality tools (Black, isort, Flake8)
- Database connection pooling
- Structured logging

### 🚧 In Progress (v1.1)
- Private MQTT broker migration
- Enhanced security (CSP headers, rate limiting)
- Unit & integration tests
- Performance monitoring

### 📋 Planned (v2.0)
- Multi-pet support per device
- Advanced scheduling (multiple feeds/day)
- Mobile app (Flutter/React Native)
- Admin dashboard & analytics
- Email/SMS notifications
- OTA firmware updates for ESP32

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

**Code Standards:**
- Follow PEP 8 (enforced by Flake8)
- Format with Black
- Organize imports with isort  
- Write docstrings for functions
- Add type hints where applicable

---

## 📄 License

This project is licensed under the MIT License.

---

## 👥 Team

**Smart Pet Feeder Team**  
- Backend: Flask, MySQL, MQTT Integration
- Frontend: HTML, CSS, JavaScript, Bootstrap
- IoT: ESP32, Arduino, MQTT Protocol
- DevOps: Docker, GitHub Actions, Tailscale

---

## 📞 Support

**Issues:** Open GitHub issue  
**Email:** support@smartpetfeeder.com  
**Logs:** Check `logs/petfeeder.log`  

**Quick Diagnostics:**
```bash
# Check all services
make check

# View application status
docker-compose ps

# Test database connection
python setup_database.py
```

---

**Version:** 2.0.0 (Production-Ready with CI/CD)  
**Status:** ✅ Production Deployment Ready  
**Last Updated:** 2026-02-12  
**Build:** [![Docker Build](https://img.shields.io/badge/Build-Passing-success)]()
