# 🚀 Production Deployment Guide - Smart Pet Feeder

**Quick reference for deploying to production via CI/CD**

---

## 📋 Prerequisites Checklist

- [  ] GitHub repository created
- [  ] Proxmox Debian VM (or Linux server) ready
- [  ] Tailscale account created
- [  ] Docker & Docker Compose installed on server
- [  ] Domain/IP for access (optional)

---

## ⚡ Quick Start (5 Minutes)

### 1️⃣ Configure GitHub Secrets (2 min)

Go to **Repository → Settings → Secrets and variables → Actions**

Add these **10 secrets:**

| Secret Name | How to Get | Example |
|-------------|-----------|---------|
| `TAILSCALE_OAUTH_CLIENT_ID` | [Tailscale Admin](https://login.tailscale.com/admin/settings/oauth) | `kxxxxxx` |
| `TAILSCALE_OAUTH_SECRET` | Same page as above | `tskey-client-xxx` |
| `SERVER_SSH_HOST` | `tailscale ip -4` on server | `100.64.1.2` |
| `SERVER_SSH_USER` | Create user: `sudo adduser deployer` | `deployer` |
| `SERVER_SSH_KEY` | `ssh-keygen -t ed25519 -f ~/.ssh/petfeeder` | Private key content |
| `MYSQL_ROOT_PASSWORD` | `openssl rand -base64 24` | Random 24+ chars |
| `MYSQL_PASSWORD` | `openssl rand -base64 24` | Random 24+ chars (different) |
| `FLASK_SECRET_KEY` | `python -c "import secrets; print(secrets.token_hex(32))"` | 64-char hex |
| `SERVER_DOMAIN` | Your domain or Tailscale IP | `petfeeder.example.com` |
| `DEPLOY_PATH` | Deployment directory on server | `/opt/smart-pet-feeder` |

**Detailed Guide:** [REPO.md](REPO.md)

---

### 2️⃣ Prepare Server (2 min)

```bash
# SSH to server
ssh your-user@your-server-ip

# Install Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker deployer

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up

# Create deployment directory
sudo mkdir -p /opt/smart-pet-feeder
sudo chown deployer:deployer /opt/smart-pet-feeder

# Add SSH public key to authorized_keys
mkdir -p ~/.ssh
echo "YOUR_PUBLIC_KEY_HERE" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

---

### 3️⃣ Deploy (1 min)

```bash
# Push to main branch
git add .
git commit -m "Deploy to production"
git push origin main
```

**GitHub Actions will automatically:**
1. Connect to Tailscale VPN
2. SSH to your server
3. Sync files
4. Build Docker image
5. Start containers
6. Run health checks

**Monitor:** Go to **Actions** tab in GitHub repository

---

## 🔍 Verify Deployment

### Check Containers

```bash
# SSH to server
ssh deployer@$(tailscale ip -4)

# List running containers
docker ps

# Expected output:
# CONTAINER ID   IMAGE                  STATUS
# abc123...      smart-pet-feeder_web   Up 2 minutes (healthy)
# def456...      mysql:8.0              Up 2 minutes (healthy)
```

### Test Application

```bash
# From server
curl http://localhost:8000

# From Tailscale network
curl http://100.64.1.2:8000

# Expected: HTML response from index page
```

### View Logs

```bash
# Application logs
docker logs smart_pet_feeder_web_1 -f

# Database logs
docker logs smart_pet_feeder_db_1

# All services
docker-compose -f /opt/smart-pet-feeder/docker-compose.yml logs -f
```

---

## 🛠️ Common Operations

### Update Application

```bash
# Just push to main
git push origin main
# CI/CD will auto-deploy
```

### Restart Services

```bash
ssh deployer@$(tailscale ip -4)
cd /opt/smart-pet-feeder
docker-compose restart
```

### View Database

```bash
docker exec -it smart_pet_feeder_db_1 mysql -u root -p
# Enter MYSQL_ROOT_PASSWORD
> USE smart_pet_feeder;
> SHOW TABLES;
```

### Backup Database

```bash
docker exec smart_pet_feeder_db_1 mysqldump -u root -p smart_pet_feeder > backup_$(date +%Y%m%d).sql
```

### Stop Application

```bash
cd /opt/smart-pet-feeder
docker-compose down
```

### Start Application

```bash
cd /opt/smart-pet-feeder
docker-compose up -d
```

---

## 🐛 Troubleshooting

### Deployment Failed

**Check GitHub Actions logs:**
1. Go to repository → **Actions** tab
2. Click on failed workflow run
3. Expand failed step to see error

**Common issues:**
- ❌ **Tailscale auth failed** → Regenerate OAuth credentials
- ❌ **SSH connection refused** → Check Tailscale running on server
- ❌ **Permission denied** → Add SSH public key to `authorized_keys`
- ❌ **Docker build failed** → Check disk space with `df -h`

### Application Won't Start

```bash
# Check container logs
docker logs smart_pet_feeder_web_1

# Common issues:
# - Database not ready: Wait 30s, it has health checks
# - Port in use: Change port in .env.docker
# - Permission denied: Check file ownership
```

### Database Connection Failed

```bash
# Check database container
docker ps | grep db
docker logs smart_pet_feeder_db_1

# Verify credentials match
cat /opt/smart-pet-feeder/.env.docker | grep MYSQL
```

### MQTT Not Working

MQTT is optional - application works without it:
- Check `MQTT_BROKER=broker.hivemq.com` in `.env.docker`
- Verify internet connectivity
- MQTT errors won't prevent application from running

---

## 🔒 Security Hardening

### SSL/TLS (Recommended)

**Install Nginx + Let's Encrypt:**

```bash
# Install Nginx
sudo apt install nginx -y

# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Configure Nginx reverse proxy
sudo nano /etc/nginx/sites-available/petfeeder

# Add:
server {
    listen 80;
    server_name petfeeder.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Enable site
sudo ln -s /etc/nginx/sites-available/petfeeder /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Get SSL certificate
sudo certbot --nginx -d petfeeder.yourdomain.com
```

### Firewall Configuration

```bash
sudo apt install ufw -y

# Allow SSH (IMPORTANT - do this first!)
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
sudo ufw status
```

### Change Default Admin Password

1. Access application at http://your-domain
2. Login with `admin` / `admin123`
3. Go to **Profile** → **Change Password**
4. Set strong password

---

## 📊 Monitoring

### View Application Status

```bash
# Container status
docker-compose -f /opt/smart-pet-feeder/docker-compose.yml ps

# Resource usage
docker stats
```

### Log Rotation

Logs are automatically rotated by Docker:
```bash
# Configure in docker-compose.yml (already set)
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

### Health Checks

```bash
# Manual health check
curl http://localhost:8000
# Expected: HTTP 200

# Database health
docker exec smart_pet_feeder_db_1 mysqladmin ping -h localhost
# Expected: mysqld is alive
```

---

## 📚 Documentation

- [README.md](README.md) - Complete project documentation
- [REPO.md](REPO.md) - GitHub Secrets detailed setup
- [DATABASE_DESIGN.md](docs/DATABASE_DESIGN.md) - Database schema

---

## 🆘 Get Help

**Diagnostic Commands:**

```bash
# Check all Docker containers
docker ps -a

# View recent logs
docker-compose logs --tail=50

# Test database connection
docker exec smart_pet_feeder_db_1 mysql -u root -pYOUR_PASSWORD -e "SELECT 1"

# Check disk space
df -h

# Check memory
free -h
```

**Support:**
- GitHub Issues: Report bugs
- Logs: `/opt/smart-pet-feeder/logs/`
- Email: support@smartpetfeeder.com

---

**Last Updated:** 2026-02-12  
**Version:** 2.0.0  
**Status:** Production Ready ✅
