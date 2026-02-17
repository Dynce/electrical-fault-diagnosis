# 🚀 Deployment Guide - Electrical Fault Diagnosis System

## 📋 Table of Contents
1. [Local Testing](#local-testing)
2. [GitHub Setup](#github-setup)
3. [Render Deployment](#render-deployment)
4. [PythonAnywhere Alternative](#pythonanywhere-alternative)

---

## 🏠 Local Testing

Before deploying, test your app locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python app.py

# Or run with Gunicorn (production-like)
gunicorn wsgi:app
```

Access at: `http://127.0.0.1:5000`

---

## 🐙 GitHub Setup

### Step 1: Create GitHub Repository

1. Go to [github.com/new](https://github.com/new)
2. Repository name: `electrical-fault-diagnosis`
3. Description: `Electrical Fault Diagnosis System - Web App by Denis Mulatya Mutua`
4. Choose **Public** (so Render can access it)
5. Click **Create repository**

### Step 2: Push Code to GitHub

```bash
# Navigate to your project directory
cd c:\Users\Denis Mutua\Desktop\electrical_fault_diagnosis

# Initialize git
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Electrical Fault Diagnosis System"

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/electrical-fault-diagnosis.git

# Push to GitHub
git branch -M main
git push -u origin main
```

---

## ☁️ Render Deployment (Recommended)

### Step 1: Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with GitHub (easiest option)
3. Connect your GitHub account

### Step 2: Create Web Service

1. Click **New +** → **Web Service**
2. Select your `electrical-fault-diagnosis` repository
3. Configure:
   - **Name:** `electrical-fault-diagnosis`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn wsgi:app`
   - **Plan:** `Free`

4. Click **Create Web Service**

### Step 3: Set Environment Variables

1. Go to your service's **Environment** settings
2. Add these environment variables:

```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

### Step 4: Deploy

1. Render automatically deploys when you push to GitHub
2. Your app will be available at: `https://electrical-fault-diagnosis.onrender.com`

### Step 5: Database Persistence

⚠️ **Important:** Render's free tier has ephemeral storage. Your database (`faults.db`) will be deleted after 30 days of inactivity.

**Solution: Use PostgreSQL** (Free tier available)

Create a PostgreSQL database:
1. In Render dashboard, click **New +** → **PostgreSQL**
2. Name: `electrical-fault-diagnosis-db`
3. Free tier is fine
4. Copy the connection string
5. Add to environment variables as `DATABASE_URL`

Update your app to use PostgreSQL (optional upgrade).

---

## 🐍 PythonAnywhere Alternative

### Step 1: Create Account

1. Go to [pythonanywhere.com](https://pythonanywhere.com)
2. Create free account
3. Confirm email

### Step 2: Clone Repository

1. Go to **Consoles**
2. Start a Bash console
3. Run:
```bash
git clone https://github.com/YOUR_USERNAME/electrical-fault-diagnosis.git
cd electrical-fault-diagnosis
pip install --user -r requirements.txt
```

### Step 3: Configure Web App

1. Go to **Web** tab
2. Click **Add a new web app**
3. Choose **Manual configuration**
4. Select **Python 3.10+**
5. In WSGI file, replace content with:

```python
import sys
path = '/home/yourusername/electrical-fault-diagnosis'
if path not in sys.path:
    sys.path.append(path)

from app import app as application
```

6. Set **Source code:** `/home/yourusername/electrical-fault-diagnosis`
7. Set **Working directory:** `/home/yourusername/electrical-fault-diagnosis`

### Step 4: Setup Virtual Environment

```bash
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Update WSGI file to use venv:
```python
import sys
import os

path = '/home/yourusername/electrical-fault-diagnosis'
if path not in sys.path:
    sys.path.append(path)

activate_this = os.path.join(path, 'venv/bin/activate_this.py')
exec(open(activate_this).read(), {'__file__': activate_this})

from app import app as application
```

### Step 5: Set Environment Variables

1. Go to **Web** → **WSGI configuration file**
2. Add at top:
```python
import os
os.environ['MAIL_SERVER'] = 'smtp.gmail.com'
os.environ['MAIL_PORT'] = '587'
# ... etc
```

---

## 📊 Monitoring & Maintenance

### Check Logs (Render)
- Dashboard → Logs tab
- See real-time deployment and runtime logs

### View Metrics (Render)
- Monitor CPU, memory, requests
- Free tier has limits, optimization may be needed

### Update Code
```bash
git add .
git commit -m "Update: Your change description"
git push origin main
```

Render automatically redeploys!

---

## 🔒 Security Checklist

- [ ] Remove sensitive data from `.env` before pushing
- [ ] Use environment variables for all secrets
- [ ] Set `DEBUG=False` in production
- [ ] Use strong database passwords
- [ ] Enable HTTPS (Render does this automatically)
- [ ] Regularly update dependencies

---

## 🆘 Troubleshooting

### "ModuleNotFoundError" on Deploy
- Ensure all imports are in `requirements.txt`
- Check `Procfile` and `wsgi.py` are correct

### Email Not Sending
- Verify Gmail 2FA and app password
- Check environment variables are set
- Test locally first with `.env` file

### Database Issues
- SQLite doesn't persist on Render (use PostgreSQL)
- Check file permissions in app
- Ensure `faults.db` location is writable

### App Crashes
- Check logs for errors
- Test locally with `gunicorn wsgi:app`
- Verify all dependencies installed

---

## 📧 Support & Contact

**Developer:** Denis Mulatya Mutua  
**Email:** denismutua970@gmail.com  
**Phone:** 0700516898  
**Institution:** Moi University, Electrical & Electronics Engineering (2025)

---

## 🎓 Project Information

- **Project:** Electrical Fault Diagnosis System
- **Type:** Flask Web Application with ML
- **Version:** 1.0
- **Year:** 2026
- **License:** All Rights Reserved

---

**Good luck with your deployment! 🚀**
