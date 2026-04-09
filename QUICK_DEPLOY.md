# ⚡ Quick Deploy to Render - 5 Minutes

Fast track deployment guide for Render.

---

## 🚀 Quick Steps

### 1. Push to GitHub (2 minutes)

```bash
# Add all deployment files
git add render.yaml Procfile runtime.txt build.sh .renderignore RENDER_DEPLOYMENT.md QUICK_DEPLOY.md

# Commit
git commit -m "Add Render deployment configuration"

# Push to GitHub
git push origin main
```

### 2. Deploy on Render (3 minutes)

1. **Go to:** [render.com](https://render.com)
2. **Sign up/Login** with GitHub
3. **Click:** "New +" → "Blueprint"
4. **Select:** Your repository
5. **Click:** "Apply"
6. **Wait:** 5-10 minutes for deployment

### 3. Access Your App

```
https://federated-learning-ckd.onrender.com
```

**Default Admin Login:**
- Username: `admin`
- Password: `admin123`

---

## 📋 What Gets Deployed

✅ FastAPI backend  
✅ SQLite database (auto-initialized)  
✅ All ML models and dependencies  
✅ Admin & Client dashboards  
✅ API documentation at `/docs`  

---

## ⚙️ Configuration Files

| File | Purpose |
|------|---------|
| `render.yaml` | Render service configuration |
| `Procfile` | Start command |
| `runtime.txt` | Python version (3.11.0) |
| `build.sh` | Build & database initialization |
| `.renderignore` | Files to exclude from deployment |

---

## 🔧 Important Settings

### Persistent Disk (Required)
- **Name:** `federated-data`
- **Mount Path:** `/opt/render/project/src/App`
- **Size:** 10 GB
- **Purpose:** Store database, models, uploads

### Environment Variables (Optional)
```bash
PYTHON_VERSION=3.11.0
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

---

## 💰 Pricing

| Plan | Cost | Features |
|------|------|----------|
| **Free** | $0/month | Spins down after 15 min |
| **Starter** | $7/month | Always-on, recommended |
| **Standard** | $25/month | 2GB RAM, better performance |

---

## ✅ Post-Deployment Checklist

- [ ] App accessible at Render URL
- [ ] Health check: `https://your-app.onrender.com/health`
- [ ] Admin login working
- [ ] Change default admin password
- [ ] Initialize global model
- [ ] Create test client
- [ ] Test training workflow

---

## 🐛 Common Issues

### Build Fails
```bash
# Fix requirements.txt encoding
iconv -f UTF-16 -t UTF-8 requirements.txt > requirements_fixed.txt
mv requirements_fixed.txt requirements.txt
git add requirements.txt && git commit -m "Fix encoding" && git push
```

### Slow First Load
- Normal on Free tier (spin-down)
- Upgrade to Starter plan for always-on

### Database Not Found
- Ensure persistent disk is configured
- Check build logs for initialization errors

---

## 📚 Full Documentation

For detailed instructions, see: **[RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)**

---

## 🆘 Need Help?

1. Check `/docs` endpoint for API documentation
2. View logs in Render Dashboard
3. Test health endpoint: `/health`
4. Review [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)

---

**That's it! Your Federated Learning system is now live! 🎉**

hi