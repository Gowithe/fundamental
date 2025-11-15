# 🚀 Stock Analyzer - Deployment Guide

Complete guide for deploying Stock Analyzer on various platforms.

---

## 📋 Table of Contents

1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Render Deployment](#render-deployment)
4. [Heroku Deployment](#heroku-deployment)
5. [AWS EC2 Deployment](#aws-ec2-deployment)
6. [DigitalOcean Deployment](#digitalocean-deployment)

---

## 🏠 Local Development

### macOS/Linux

```bash
# Make run script executable
chmod +x run.sh

# Run the application
./run.sh
```

### Windows

```bash
# Double-click run.bat
# Or open Command Prompt and run:
run.bat
```

### Manual Setup (All Platforms)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run Flask app
python app.py

# Open browser: http://localhost:5000
```

---

## 🐳 Docker Deployment

### Prerequisites
- Docker and Docker Compose installed
- https://www.docker.com/products/docker-desktop

### Option 1: Using Docker Compose (Recommended)

```bash
# Build and run
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop
docker-compose down
```

App will be at: `http://localhost:5000`

### Option 2: Using Docker CLI

```bash
# Build image
docker build -t stock-analyzer:latest .

# Run container
docker run -d \
  -p 5000:5000 \
  -e FINNHUB_API_KEY="your_key" \
  -e ALPHA_VANTAGE_API_KEY="your_key" \
  --name stock-analyzer \
  stock-analyzer:latest

# Check status
docker ps

# Stop container
docker stop stock-analyzer
```

### Docker Troubleshooting

```bash
# View logs
docker logs stock-analyzer

# Access shell
docker exec -it stock-analyzer bash

# Remove container
docker rm stock-analyzer

# Remove image
docker rmi stock-analyzer:latest
```

---

## 🔵 Render Deployment

### Step 1: Prepare Repository

```bash
# Initialize git repo
git init

# Add all files
git add .

# Initial commit
git commit -m "Initial commit: Stock Analyzer"

# Rename branch to main
git branch -M main
```

### Step 2: Push to GitHub

```bash
# Add remote
git remote add origin https://github.com/YOUR_USERNAME/stock-analyzer.git

# Push to GitHub
git push -u origin main
```

### Step 3: Deploy on Render

1. Go to https://render.com
2. Sign up/Login
3. Click "New +" button
4. Select "Web Service"
5. Connect your GitHub account
6. Select `stock-analyzer` repository
7. Configure:
   - **Name:** `stock-analyzer`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Plan:** Free tier (or paid)
8. Click "Create Web Service"
9. Wait for deployment (~3-5 minutes)

### Step 4: Set Environment Variables (Optional)

1. In Render dashboard, go to your service
2. Click "Environment"
3. Add variables:
   - `FINNHUB_API_KEY=your_key`
   - `ALPHA_VANTAGE_API_KEY=your_key`
4. Service will redeploy automatically

### Access Your App

Your app will be available at:
```
https://stock-analyzer-XXXX.onrender.com
```

---

## 🟣 Heroku Deployment

### Prerequisites
- Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli

### Step 1: Install Heroku CLI

```bash
# macOS
brew tap heroku/brew && brew install heroku

# Windows
# Download from: https://cli-assets.heroku.com/heroku-x64.exe

# Linux
curl https://cli-assets.heroku.com/install-ubuntu.sh | sh
```

### Step 2: Login to Heroku

```bash
heroku login
```

### Step 3: Create Heroku App

```bash
# Create app
heroku create stock-analyzer-YOUR-NAME

# Or if you have existing git repo
heroku create -a stock-analyzer-YOUR-NAME
```

### Step 4: Set Environment Variables

```bash
heroku config:set FINNHUB_API_KEY="your_key" -a stock-analyzer-YOUR-NAME
heroku config:set ALPHA_VANTAGE_API_KEY="your_key" -a stock-analyzer-YOUR-NAME
```

### Step 5: Deploy

```bash
# If not already a git repo
git init

# Add Heroku remote
heroku git:remote -a stock-analyzer-YOUR-NAME

# Deploy
git add .
git commit -m "Deploy Stock Analyzer"
git push heroku main
```

### Step 6: View Application

```bash
heroku open
```

### Monitor Logs

```bash
heroku logs --tail
```

---

## ☁️ AWS EC2 Deployment

### Prerequisites
- AWS Account
- EC2 instance (Ubuntu 20.04 recommended)
- SSH key pair

### Step 1: Connect to EC2 Instance

```bash
ssh -i your-key.pem ubuntu@your-instance-ip
```

### Step 2: Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3-pip python3-venv -y

# Install Nginx
sudo apt install nginx -y

# Install Supervisor
sudo apt install supervisor -y
```

### Step 3: Clone Repository

```bash
cd /home/ubuntu
git clone https://github.com/YOUR_USERNAME/stock-analyzer.git
cd stock-analyzer
```

### Step 4: Setup Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 5: Configure Gunicorn

```bash
# Install gunicorn
pip install gunicorn

# Test
gunicorn app:app
```

### Step 6: Configure Supervisor

```bash
sudo nano /etc/supervisor/conf.d/stock-analyzer.conf
```

Add:
```ini
[program:stock-analyzer]
directory=/home/ubuntu/stock-analyzer
command=/home/ubuntu/stock-analyzer/venv/bin/gunicorn app:app -w 4 -b 127.0.0.1:5000
user=ubuntu
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/stock-analyzer.log
environment=PYTHONUNBUFFERED=1
```

### Step 7: Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/stock-analyzer
```

Add:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static/ {
        alias /home/ubuntu/stock-analyzer/static/;
    }
}
```

### Step 8: Enable and Start Services

```bash
# Enable Nginx site
sudo ln -s /etc/nginx/sites-available/stock-analyzer /etc/nginx/sites-enabled/

# Test Nginx config
sudo nginx -t

# Start Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Start Supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start stock-analyzer
```

### Step 9: Setup SSL (Optional but Recommended)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

---

## 🌊 DigitalOcean Deployment

### Using DigitalOcean App Platform (Easiest)

### Step 1: Connect GitHub

1. Go to https://cloud.digitalocean.com
2. Click "Apps" in sidebar
3. Click "Create Apps"
4. Select GitHub as source
5. Authorize and select `stock-analyzer` repository

### Step 2: Configure

1. Set runtime to Python
2. Set build command: `pip install -r requirements.txt`
3. Set run command: `gunicorn app:app`
4. Set port to 5000

### Step 3: Environment Variables

Add:
```
FINNHUB_API_KEY=your_key
ALPHA_VANTAGE_API_KEY=your_key
```

### Step 4: Deploy

Click "Deploy" and wait for completion.

---

## 🔧 Configuration Checklist

- [ ] API keys configured
- [ ] Environment variables set
- [ ] CORS enabled (for frontend)
- [ ] Static files serving correctly
- [ ] Error handling working
- [ ] Database connection (if applicable)
- [ ] SSL/HTTPS enabled (production)
- [ ] Logging configured
- [ ] Rate limiting implemented (optional)
- [ ] Monitoring setup (optional)

---

## 📊 Comparison: Deployment Platforms

| Platform | Cost | Ease | Support | Best For |
|----------|------|------|---------|----------|
| **Local** | Free | ⭐⭐⭐⭐⭐ | N/A | Development |
| **Docker** | Free | ⭐⭐⭐⭐ | N/A | Local/CI/CD |
| **Render** | Free/Paid | ⭐⭐⭐⭐⭐ | Excellent | Quick Deploy |
| **Heroku** | Free* | ⭐⭐⭐⭐⭐ | Good | Beginners |
| **AWS EC2** | Paid | ⭐⭐⭐ | Excellent | Enterprise |
| **DigitalOcean** | Paid | ⭐⭐⭐⭐ | Good | VPS Control |

*Heroku free tier ended, now paid only

---

## 🔍 Monitoring & Logs

### View Application Logs

```bash
# Render
# Go to dashboard → Logs

# Heroku
heroku logs --tail

# Docker
docker logs -f stock-analyzer

# AWS EC2
tail -f /var/log/stock-analyzer.log

# DigitalOcean
# View in App Platform dashboard
```

### Health Check

```bash
curl https://your-app-url.com/
# Should return: {"message": "Stock Analyzer API Running ✓"}
```

---

## 🚨 Troubleshooting

### App won't start

```bash
# Check logs for errors
# Verify all dependencies installed
pip install -r requirements.txt

# Test locally first
python app.py
```

### API keys not working

```bash
# Verify keys are set
echo $FINNHUB_API_KEY

# Test API endpoint
curl https://your-app-url.com/api/dummy
```

### Port issues

```bash
# Kill process on port
lsof -i :5000  # Find PID
kill -9 PID    # Kill process

# Or use different port
PORT=5001 python app.py
```

### CORS errors

- Ensure `flask-cors` installed: `pip install flask-cors`
- Check CORS headers in `app.py`
- Frontend and backend should be able to communicate

---

## 📈 Performance Optimization

### For Production

1. **Enable Gunicorn workers:**
   ```bash
   gunicorn app:app -w 4 -b 0.0.0.0:5000
   ```

2. **Add caching:**
   ```python
   from flask_caching import Cache
   cache = Cache(app, config={'CACHE_TYPE': 'simple'})
   ```

3. **Minify static files:**
   ```bash
   # Use tools like UglifyJS, CSSNano
   ```

4. **Use CDN for static files:**
   - CloudFlare, AWS CloudFront, etc.

5. **Database optimization:**
   - Add indexing for frequently queried fields

---

## 🔐 Security Best Practices

1. **Never commit API keys:**
   ```bash
   # Use .env file
   echo ".env" >> .gitignore
   ```

2. **Use environment variables:**
   ```python
   import os
   api_key = os.getenv('FINNHUB_API_KEY')
   ```

3. **Enable HTTPS:**
   ```bash
   # Always use HTTPS in production
   # Use Let's Encrypt (free)
   ```

4. **Rate limiting:**
   ```python
   from flask_limiter import Limiter
   limiter = Limiter(app)
   ```

5. **Input validation:**
   ```python
   # Validate stock symbols
   # Sanitize user inputs
   ```

---

## 📞 Support

- **Render Docs:** https://render.com/docs
- **Heroku Docs:** https://devcenter.heroku.com/
- **AWS Docs:** https://docs.aws.amazon.com/
- **DigitalOcean Docs:** https://docs.digitalocean.com/

---

**Last Updated:** 2025  
**Version:** 1.0  
**Status:** ✅ Production Ready
