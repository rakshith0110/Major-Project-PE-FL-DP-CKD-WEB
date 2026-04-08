# 🚀 Deploying Federated Learning CKD System on Render

This guide provides step-by-step instructions to deploy your Federated Learning application on Render.

---

## 📋 Prerequisites

1. **GitHub Account** - Your code must be in a GitHub repository
2. **Render Account** - Sign up at [render.com](https://render.com)
3. **Git** - Ensure your project is committed and pushed to GitHub

---

## 🔧 Deployment Files Created

The following files have been created for Render deployment:

1. **`render.yaml`** - Render Blueprint configuration
2. **`Procfile`** - Process file for starting the application
3. **`runtime.txt`** - Python version specification
4. **`build.sh`** - Build script for dependencies and database initialization

---

## 📝 Step-by-Step Deployment Guide

### Step 1: Prepare Your Repository

1. **Commit all deployment files:**
   ```bash
   git add render.yaml Procfile runtime.txt build.sh RENDER_DEPLOYMENT.md
   git commit -m "Add Render deployment configuration"
   git push origin main
   ```

2. **Ensure your repository is public or connected to Render**

### Step 2: Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up using GitHub (recommended)
3. Authorize Render to access your repositories

### Step 3: Deploy Using Blueprint (Recommended)

#### Option A: Deploy via Dashboard

1. **Login to Render Dashboard**
2. Click **"New +"** → **"Blueprint"**
3. **Connect Repository:**
   - Select your GitHub repository
   - Branch: `main` (or your default branch)
4. **Blueprint Detection:**
   - Render will automatically detect `render.yaml`
   - Review the configuration
5. **Click "Apply"**
6. Wait for deployment to complete (5-10 minutes)

#### Option B: Deploy via render.yaml

1. **Push render.yaml to your repository**
2. **In Render Dashboard:**
   - Go to "Blueprints"
   - Click "New Blueprint Instance"
   - Select your repository
   - Render will use `render.yaml` automatically

### Step 4: Manual Web Service Setup (Alternative)

If you prefer manual setup:

1. **Click "New +"** → **"Web Service"**
2. **Connect Repository:**
   - Select your GitHub repository
   - Branch: `main`
3. **Configure Service:**
   - **Name:** `federated-learning-ckd`
   - **Region:** Oregon (or closest to you)
   - **Branch:** `main`
   - **Runtime:** Python 3
   - **Build Command:** `bash build.sh`
   - **Start Command:** `cd App && python -m uvicorn App.backend.main:app --host 0.0.0.0 --port $PORT`
4. **Environment Variables:**
   - `PYTHON_VERSION`: `3.11.0`
5. **Plan:** Free or Starter ($7/month recommended)
6. **Add Disk (Important for persistent data):**
   - Name: `federated-data`
   - Mount Path: `/opt/render/project/src/App`
   - Size: 10 GB
7. **Click "Create Web Service"**

---

## 🔐 Environment Variables (Optional)

Add these in Render Dashboard → Your Service → Environment:

```bash
# Email Configuration (if using email notifications)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Security (optional - defaults are set)
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_HOURS=8
```

---

## 📊 Post-Deployment Configuration

### 1. Access Your Application

Once deployed, Render provides a URL like:
```
https://federated-learning-ckd.onrender.com
```

**Access Points:**
- Landing Page: `https://your-app.onrender.com/`
- Admin Dashboard: `https://your-app.onrender.com/admin`
- Client Dashboard: `https://your-app.onrender.com/client`
- API Docs: `https://your-app.onrender.com/docs`
- Health Check: `https://your-app.onrender.com/health`

### 2. Default Credentials

**Admin Login:**
- Username: `admin`
- Password: `admin123`

⚠️ **IMPORTANT:** Change the default admin password immediately after first login!

### 3. Initialize Global Model

1. Login as admin
2. Navigate to "Initialize Model" section
3. Configure parameters and initialize the global model

### 4. Create Clients

1. Go to "Client Management"
2. Create clients (hospitals) with their credentials
3. Clients will receive login credentials via email (if configured)

---

## 🗄️ Database & Persistent Storage

### SQLite Database

The application uses SQLite (`federated_ckd.db`) which is stored in the persistent disk.

**Location:** `/opt/render/project/src/App/federated_ckd.db`

### Persistent Disk Configuration

Render's disk ensures data persists across deployments:
- **Models:** `/opt/render/project/src/App/models/`
- **Uploads:** `/opt/render/project/src/App/uploads/`
- **Database:** `/opt/render/project/src/App/federated_ckd.db`

---

## 🔍 Monitoring & Logs

### View Logs

1. Go to Render Dashboard
2. Select your service
3. Click "Logs" tab
4. View real-time application logs

### Health Monitoring

Check application health:
```bash
curl https://your-app.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Federated Learning CKD System",
  "version": "1.0.0"
}
```

---

## ⚙️ Scaling & Performance

### Free Tier Limitations

- **Spins down after 15 minutes of inactivity**
- **First request after spin-down takes 30-60 seconds**
- **512 MB RAM**

### Upgrade to Starter Plan ($7/month)

Benefits:
- ✅ No spin-down
- ✅ 512 MB RAM (upgradeable)
- ✅ Better performance
- ✅ Custom domains
- ✅ Persistent disk included

### Performance Tips

1. **Use Starter Plan** for production
2. **Enable persistent disk** for data storage
3. **Monitor logs** for errors
4. **Set up health checks** for uptime monitoring

---

## 🐛 Troubleshooting

### Build Failures

**Issue:** Build fails during pip install

**Solution:**
```bash
# Check requirements.txt encoding
# Ensure all dependencies are compatible with Python 3.11
# Remove Windows-specific packages if deploying from Windows
```

**Fix requirements.txt encoding:**
```bash
# Convert to UTF-8
iconv -f UTF-16 -t UTF-8 requirements.txt > requirements_fixed.txt
mv requirements_fixed.txt requirements.txt
```

### Database Initialization Errors

**Issue:** Database not initializing

**Solution:**
1. Check build logs in Render
2. Ensure `build.sh` has execute permissions:
   ```bash
   chmod +x build.sh
   git add build.sh
   git commit -m "Make build.sh executable"
   git push
   ```

### Port Binding Issues

**Issue:** Application not accessible

**Solution:**
- Ensure start command uses `$PORT` environment variable
- Render automatically assigns a port
- Your app must bind to `0.0.0.0:$PORT`

### Import Errors

**Issue:** Module import errors

**Solution:**
- Ensure `PYTHONPATH` includes project root
- Check that all imports use correct paths
- Verify `App` directory structure is maintained

### Slow First Request

**Issue:** First request takes 30-60 seconds

**Solution:**
- This is normal on Free tier (spin-down)
- Upgrade to Starter plan for always-on service
- Or use a cron job to ping your app every 10 minutes

---

## 🔄 Continuous Deployment

### Auto-Deploy on Git Push

Render automatically deploys when you push to your connected branch:

```bash
git add .
git commit -m "Update application"
git push origin main
```

Render will:
1. Detect the push
2. Run build script
3. Deploy new version
4. Zero-downtime deployment

### Manual Deploy

In Render Dashboard:
1. Go to your service
2. Click "Manual Deploy"
3. Select "Clear build cache & deploy"

---

## 📧 Email Configuration

To enable email notifications:

1. **Get Gmail App Password:**
   - Go to Google Account Settings
   - Security → 2-Step Verification → App Passwords
   - Generate password for "Mail"

2. **Add to Render Environment Variables:**
   ```
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-16-char-app-password
   ```

3. **Update code if needed:**
   - Check `App/backend/services/email_service.py`
   - Ensure it reads from environment variables

---

## 🔒 Security Best Practices

### 1. Change Default Credentials
```sql
-- Connect to database and update admin password
UPDATE admin SET password = 'new-hashed-password' WHERE username = 'admin';
```

### 2. Set Strong Secret Key
```bash
# Generate a secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
Add to Render environment variables as `SECRET_KEY`

### 3. Enable HTTPS
- Render provides free SSL certificates
- All traffic is automatically encrypted

### 4. Restrict CORS
Update `App/backend/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],  # Specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📊 Cost Estimation

### Free Tier
- **Cost:** $0/month
- **Limitations:** Spins down after 15 min inactivity
- **Best for:** Testing, development

### Starter Plan
- **Cost:** $7/month
- **Features:** Always-on, 512 MB RAM, persistent disk
- **Best for:** Small production deployments

### Standard Plan
- **Cost:** $25/month
- **Features:** 2 GB RAM, better performance
- **Best for:** Production with multiple clients

---

## 🆘 Support & Resources

### Render Documentation
- [Render Docs](https://render.com/docs)
- [Python on Render](https://render.com/docs/deploy-fastapi)
- [Persistent Disks](https://render.com/docs/disks)

### Application Support
- **API Documentation:** `https://your-app.onrender.com/docs`
- **Health Check:** `https://your-app.onrender.com/health`
- **GitHub Issues:** Create issues in your repository

### Common Commands

```bash
# View logs
render logs -s federated-learning-ckd

# SSH into service (Starter plan+)
render ssh -s federated-learning-ckd

# Restart service
render restart -s federated-learning-ckd
```

---

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Render account created and connected to GitHub
- [ ] Deployment files committed (render.yaml, Procfile, etc.)
- [ ] Service created on Render
- [ ] Persistent disk configured (10 GB)
- [ ] Environment variables set (if needed)
- [ ] Build completed successfully
- [ ] Application accessible via Render URL
- [ ] Health check endpoint responding
- [ ] Admin login working
- [ ] Default admin password changed
- [ ] Global model initialized
- [ ] Test client created and working
- [ ] Email notifications configured (optional)
- [ ] Custom domain configured (optional)

---

## 🎉 Success!

Your Federated Learning CKD System is now deployed on Render!

**Next Steps:**
1. Share the URL with your team
2. Create client accounts for hospitals
3. Upload datasets and start training
4. Monitor performance and logs
5. Scale as needed

---

## 📞 Need Help?

- **Render Support:** [support@render.com](mailto:support@render.com)
- **Documentation:** Check README.md and App/README.md
- **API Docs:** Visit `/docs` endpoint on your deployed app

---

**Built with ❤️ for Privacy-Preserving Healthcare AI**

*Deployed on Render - Fast, Secure, Scalable*