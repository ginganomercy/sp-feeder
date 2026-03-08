# 🔐 Repository Setup Guide - Smart Pet Feeder

**Panduan Setup Repository GitHub untuk CI/CD Deployment**

---

## 📋 Table of Contents

1. [GitHub Repository Secrets](#github-repository-secrets)
2. [SSH Deploy Keys](#ssh-deploy-keys)
3. [Tailscale OAuth Setup](#tailscale-oauth-setup)
4. [Server Preparation](#server-preparation)
5. [Testing Deployment](#testing-deployment)

---

## 🔑 GitHub Repository Secrets

### Required Secrets (10 Total)

Berikut adalah daftar lengkap secrets yang diperlukan untuk GitHub Actions workflow:

| Secret Name | Type | Description | Example |
|-------------|------|-------------|---------|
| `TAILSCALE_OAUTH_CLIENT_ID` | String | Tailscale OAuth Client ID | `kxxxxxxxxxxxxxx` |
| `TAILSCALE_OAUTH_SECRET` | String | Tailscale OAuth Secret | `tskey-client-kxxx...` |
| `SERVER_SSH_HOST` | String | Tailscale IP server | `100.64.1.2` |
| `SERVER_SSH_USER` | String | SSH username | `deployer` |
| `SERVER_SSH_KEY` | Multi-line | SSH Private Key | `-----BEGIN OPENSSH...` |
| `MYSQL_ROOT_PASSWORD` | String | MySQL root password | `SecureRootPass123!` |
| `MYSQL_PASSWORD` | String | MySQL app password | `AppUserPass456!` |
| `FLASK_SECRET_KEY` | String | Flask session secret | Random 64-char string |
| `SERVER_DOMAIN` | String | Domain/IP untuk akses | `petfeeder.example.com` |
| `DEPLOY_PATH` | String | Path deployment | `/opt/smart-pet-feeder` |

---

## 🛠️ Setup Instructions

### 1. GitHub Repository Secrets

#### Step 1.1: Buka Repository Settings

1. Buka repository GitHub Anda: `https://github.com/username/smart_pet_feeder`
2. Klik tab **Settings**
3. Di sidebar kiri, pilih **Secrets and variables** → **Actions**
4. Klik tombol **New repository secret**

#### Step 1.2: Tambahkan Secrets Satu Per Satu

##### 1️⃣ TAILSCALE_OAUTH_CLIENT_ID

**Cara Generate:**
1. Buka [Tailscale Admin Console](https://login.tailscale.com/admin/settings/oauth)
2. Klik **Generate OAuth Client**
3. **Description:** `GitHub Actions CI/CD`
4. **Tags:** `tag:ci`
5. **Scopes:** Pilih `devices:write`
6. Copy **Client ID**

**Menambahkan ke GitHub:**
```
Name: TAILSCALE_OAUTH_CLIENT_ID
Value: kxxxxxxxxxxxxxx
```

##### 2️⃣ TAILSCALE_OAUTH_SECRET

**Dari halaman yang sama saat generate OAuth Client:**
1. Copy **Client Secret** (hanya ditampilkan sekali!)
2. Simpan di tempat aman jika perlu backup

**Menambahkan ke GitHub:**
```
Name: TAILSCALE_OAUTH_SECRET
Value: tskey-client-kxxxxxxxxxxxxx-xxxxxxxxxxxxxxx
```

##### 3️⃣ SERVER_SSH_HOST

**Cara Mendapatkan Tailscale IP:**
```bash
# Di server Proxmox Debian Anda
tailscale ip -4
# Output: 100.64.1.2 (contoh)
```

**Menambahkan ke GitHub:**
```
Name: SERVER_SSH_HOST
Value: 100.64.1.2
```

##### 4️⃣ SERVER_SSH_USER

**Recommended:** Buat user khusus untuk deployment (bukan root)

```bash
# Di server
sudo adduser deployer
sudo usermod -aG docker deployer
```

**Menambahkan ke GitHub:**
```
Name: SERVER_SSH_USER
Value: deployer
```

##### 5️⃣ SERVER_SSH_KEY

**Cara Generate SSH Key Pair:**

```bash
# Di komputer lokal Anda (Windows PowerShell atau Git Bash)
ssh-keygen -t ed25519 -C "github-actions-ci" -f ~/.ssh/petfeeder_deploy

# Output:
# - Private key: ~/.ssh/petfeeder_deploy
# - Public key: ~/.ssh/petfeeder_deploy.pub
```

**Copy Private Key:**
```bash
# Windows PowerShell
Get-Content ~/.ssh/petfeeder_deploy | clip

# Linux/Mac
cat ~/.ssh/petfeeder_deploy | pbcopy
# atau
cat ~/.ssh/petfeeder_deploy
```

**Menambahkan ke GitHub:**
```
Name: SERVER_SSH_KEY
Value: -----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
[... paste entire private key ...]
-----END OPENSSH PRIVATE KEY-----
```

**⚠️ IMPORTANT:** Jangan tambahkan newline atau spasi ekstra!

##### 6️⃣ MYSQL_ROOT_PASSWORD

**Generate Strong Password:**
```bash
# Linux/Mac
openssl rand -base64 32

# Windows PowerShell
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 24 | % {[char]$_})
```

**Menambahkan ke GitHub:**
```
Name: MYSQL_ROOT_PASSWORD
Value: xK9mP2nQ7wR5tY8uI3oP1aS4dF6gH0j
```

##### 7️⃣ MYSQL_PASSWORD

**Generate password lain untuk app user:**

**Menambahkan ke GitHub:**
```
Name: MYSQL_PASSWORD
Value: zL3nM8kJ2vT6yW9sC4eB7rX1aQ5fN0p
```

##### 8️⃣ FLASK_SECRET_KEY

**Generate Secure Random String:**
```bash
# Linux/Mac
python3 -c "import secrets; print(secrets.token_hex(32))"

# Windows PowerShell
python -c "import secrets; print(secrets.token_hex(32))"

# Output contoh:
# 7f8e9d0c1b2a3f4e5d6c7b8a9f0e1d2c3b4a5f6e7d8c9b0a1f2e3d4c5b6a7f8e
```

**Menambahkan ke GitHub:**
```
Name: FLASK_SECRET_KEY
Value: 7f8e9d0c1b2a3f4e5d6c7b8a9f0e1d2c3b4a5f6e7d8c9b0a1f2e3d4c5b6a7f8e
```

##### 9️⃣ SERVER_DOMAIN

**Pilih salah satu:**
- Domain custom: `petfeeder.yourdomain.com`
- Tailscale hostname: `100.64.1.2`
- Public IP: `203.0.113.10` (jika ada)

**Menambahkan ke GitHub:**
```
Name: SERVER_DOMAIN
Value: petfeeder.yourdomain.com
```

##### 🔟 DEPLOY_PATH

**Recommended path:**
```
/opt/smart-pet-feeder
```

**Menambahkan ke GitHub:**
```
Name: DEPLOY_PATH
Value: /opt/smart-pet-feeder
```

---

### 2. SSH Deploy Keys Setup

#### Step 2.1: Add Public Key ke Server

**Copy Public Key:**
```bash
# Windows PowerShell
Get-Content ~/.ssh/petfeeder_deploy.pub

# Linux/Mac
cat ~/.ssh/petfeeder_deploy.pub
```

**Tambahkan ke Server:**
```bash
# SSH ke server sebagai user deployer
ssh deployer@100.64.1.2

# Buat .ssh directory jika belum ada
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Tambahkan public key
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAA... github-actions-ci" >> ~/.ssh/authorized_keys

# Set permissions
chmod 600 ~/.ssh/authorized_keys
```

#### Step 2.2: Test SSH Connection

```bash
# Dari komputer lokal
ssh -i ~/.ssh/petfeeder_deploy deployer@100.64.1.2

# Jika berhasil, Anda akan login tanpa password!
```

---

### 3. Tailscale OAuth Setup (Detail)

#### Step 3.1: Login ke Tailscale Admin

1. Buka: [https://login.tailscale.com/admin](https://login.tailscale.com/admin)
2. Login dengan akun Tailscale Anda

#### Step 3.2: Generate OAuth Client

1. Navigasi ke: **Settings** → **OAuth clients**
2. Klik **Generate OAuth client**
3. Form settings:

```yaml
Description: GitHub Actions CI/CD for Smart Pet Feeder
Tags: tag:ci
Scopes:
  ✅ devices:write
  ✅ devices:read (optional, untuk monitoring)
```

4. Klik **Generate**
5. **IMPORTANT:** Copy kedua nilai ini segera (tidak akan ditampilkan lagi):
   - Client ID
   - Client Secret

#### Step 3.3: ACL Configuration (Optional)

Jika Anda ingin membatasi akses, edit ACL di Tailscale:

```json
{
  "tagOwners": {
    "tag:ci": ["autogroup:admin"]
  },
  "acls": [
    {
      "action": "accept",
      "src": ["tag:ci"],
      "dst": ["tag:server:*"]
    }
  ]
}
```

---

### 4. Server Preparation

#### Step 4.1: Install Dependencies

```bash
# SSH ke server
ssh deployer@100.64.1.2

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker deployer

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify
docker --version
docker-compose --version
```

#### Step 4.2: Install Tailscale

```bash
# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# Connect to network
sudo tailscale up

# Verify IP
tailscale ip -4
```

#### Step 4.3: Create Deploy Directory

```bash
# Create directory
sudo mkdir -p /opt/smart-pet-feeder
sudo chown deployer:deployer /opt/smart-pet-feeder

# Verify
ls -la /opt/smart-pet-feeder
```

#### Step 4.4: Firewall Configuration (Optional)

```bash
# Install UFW
sudo apt install ufw -y

# Allow SSH (important!)
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow Flask app port (if direct access needed)
sudo ufw allow 8000/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

---

### 5. Testing Deployment

#### Step 5.1: Trigger Manual Deployment

1. Buka repository GitHub
2. Klik tab **Actions**
3. Pilih workflow **Deploy to Production**
4. Klik **Run workflow**
5. Pilih branch `main`
6. Klik **Run workflow**

#### Step 5.2: Monitor Logs

Perhatikan log di GitHub Actions:

```
✅ Connect to Tailscale
✅ Setup SSH
✅ Create .env.docker on server
✅ Sync files to server
✅ Build Docker image
✅ Start services
✅ Health check
✅ Cleanup
```

#### Step 5.3: Verify Deployment

**Check Docker containers:**
```bash
# SSH ke server
ssh deployer@100.64.1.2

# List containers
docker ps

# Expected output:
# CONTAINER ID   IMAGE                    STATUS
# abc123...      smart-pet-feeder_web     Up 2 minutes (healthy)
# def456...      mysql:8.0                Up 2 minutes (healthy)
```

**Check application logs:**
```bash
# Web app logs
docker logs smart_pet_feeder_web_1

# Database logs
docker logs smart_pet_feeder_db_1
```

**Test access:**
```bash
# From server
curl http://localhost:8000

# From Tailscale network
curl http://100.64.1.2:8000

# Expected: HTML response from Flask app
```

---

## 🔍 Troubleshooting

### Issue 1: SSH Connection Refused

**Error:**
```
ssh: connect to host 100.64.1.2 port 22: Connection refused
```

**Solution:**
```bash
# Check if Tailscale is running on server
sudo tailscale status

# Restart Tailscale if needed
sudo systemctl restart tailscaled
```

### Issue 2: Permission Denied (publickey)

**Error:**
```
Permission denied (publickey)
```

**Solution:**
```bash
# Verify public key is in authorized_keys
cat ~/.ssh/authorized_keys

# Check permissions
ls -la ~/.ssh/
# Should be: drwx------ (700) for .ssh
# Should be: -rw------- (600) for authorized_keys
```

### Issue 3: Tailscale Authentication Failed

**Error:**
```
Failed to authenticate with Tailscale
```

**Solution:**
1. Regenerate OAuth client di Tailscale Admin
2. Update secrets `TAILSCALE_OAUTH_CLIENT_ID` dan `TAILSCALE_OAUTH_SECRET`
3. Re-run workflow

### Issue 4: Docker Build Failed

**Error:**
```
error building image: ...
```

**Solution:**
```bash
# SSH to server and check disk space
df -h

# Clean up old images
docker system prune -a

# Check Docker service
sudo systemctl status docker
```

---

## 📚 Quick Reference

### All Secrets Checklist

```
☐ TAILSCALE_OAUTH_CLIENT_ID
☐ TAILSCALE_OAUTH_SECRET
☐ SERVER_SSH_HOST
☐ SERVER_SSH_USER
☐ SERVER_SSH_KEY
☐ MYSQL_ROOT_PASSWORD
☐ MYSQL_PASSWORD
☐ FLASK_SECRET_KEY
☐ SERVER_DOMAIN
☐ DEPLOY_PATH
```

### Command Cheat Sheet

```bash
# SSH to server
ssh deployer@$(tailscale ip -4)

# View logs
docker-compose -f /opt/smart-pet-feeder/docker-compose.yml logs -f

# Restart services
docker-compose -f /opt/smart-pet-feeder/docker-compose.yml restart

# Stop all
docker-compose -f /opt/smart-pet-feeder/docker-compose.yml down

# Start all
docker-compose -f /opt/smart-pet-feeder/docker-compose.yml up -d

# Check status
docker-compose -f /opt/smart-pet-feeder/docker-compose.yml ps
```

---

## 🔒 Security Best Practices

1. **Never commit secrets** to repository
2. **Rotate secrets** setiap 90 hari
3. **Use strong passwords** (minimum 24 characters)
4. **Enable 2FA** on GitHub account
5. **Restrict SSH access** dengan firewall
6. **Monitor logs** untuk suspicious activity
7. **Backup `.env.docker`** di tempat aman
8. **Use Tailscale ACLs** untuk membatasi akses

---

## 📞 Support

Jika menemui masalah:

1. Check GitHub Actions logs
2. Check server logs: `docker-compose logs`
3. Verify secrets are correctly set
4. Test SSH connection manually
5. Verify Tailscale is running

**Common Issues:**
- [Deployment Guide](./docs/DEPLOYMENT.md)
- [Docker Setup](./docker-compose.yml)
- [GitHub Actions Workflow](./.github/workflows/deploy.yml)

---

**Last Updated:** 2026-02-12  
**Version:** 1.0.0  
**Maintainer:** Smart Pet Feeder Team
