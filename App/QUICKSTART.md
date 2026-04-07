# 🚀 Quick Start Guide

Get the FL-DP Healthcare Web Application running in **5 minutes**!

---

## ⚡ Super Quick Start

### For Linux/Mac:
```bash
cd Major-Project-PE-FL-DP-CKD-main
./App/run.sh
```

### For Windows:
```cmd
cd Major-Project-PE-FL-DP-CKD-main
App\run.bat
```

That's it! The application will:
- ✅ Create virtual environment
- ✅ Install dependencies
- ✅ Create necessary directories
- ✅ Initialize database
- ✅ Start the server

**Access the app at:** http://localhost:8000

---

## 🔐 Login

### Default Admin Account
- **Username:** `admin`
- **Password:** `admin123`

---

## 📋 Step-by-Step First Use

### 1️⃣ Login as Admin
- Open http://localhost:8000
- Enter credentials: `admin` / `admin123`
- Click Login

### 2️⃣ Initialize Global Model
- Click **Global Model** in sidebar
- Keep default settings or adjust:
  - Epochs: 30
  - Batch Size: 64
  - Learning Rate: 0.001
- Click **Initialize Global Model**
- Wait 2-5 minutes for training
- ✅ Global model is ready!

### 3️⃣ Create Hospital Clients
- Click **Clients** in sidebar
- Click **Add Client** button
- Enter client name (e.g., "Hospital1")
- (Optional) Upload CSV dataset
- Click **Create Client**
- Repeat for more hospitals

### 4️⃣ Upload Datasets
- In Clients page, click **Upload** for each client
- Select CSV file with patient data
- Confirm upload

### 5️⃣ Train Client Models
- Click **Training** in sidebar
- Select a client from dropdown
- Adjust training parameters if needed
- Click **Start Training**
- Wait for training to complete
- View metrics (Accuracy, F1, AUC)

### 6️⃣ Perform Aggregation
- Click **Aggregation** in sidebar
- Check clients to aggregate (must have trained models)
- Click **Perform Aggregation**
- View updated global model metrics

### 7️⃣ Make Predictions
- Click **Predictions** in sidebar
- Select a client
- Enter patient data
- Click **Predict**
- View result: CKD YES/NO with probability

---

## 🎯 Common Tasks

### Create New User (Hospital)
```bash
# Via API (use Swagger docs at /api/docs)
POST /api/auth/register
{
  "username": "hospital1",
  "email": "hospital1@example.com",
  "password": "secure_password",
  "full_name": "Hospital One",
  "role": "hospital"
}
```

### Stop the Server
Press `Ctrl + C` in the terminal

### Restart the Server
```bash
# Linux/Mac
./App/run.sh

# Windows
App\run.bat
```

### View API Documentation
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

---

## 🐛 Troubleshooting

### Port 8000 already in use
```bash
# Find and kill the process
# Linux/Mac
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Import errors
```bash
# Ensure you're in the project root
cd Major-Project-PE-FL-DP-CKD-main

# Reinstall dependencies
pip install -r App/requirements.txt
```

### Database errors
```bash
# Delete and recreate database
rm App/database/app.db
# Restart the application - database will be recreated
```

### Module not found errors
```bash
# Make sure you're running from project root
pwd  # Should show: .../Major-Project-PE-FL-DP-CKD-main

# Check Python path
python -c "import sys; print(sys.path)"
```

---

## 📊 Sample Workflow

### Complete FL Training Cycle

1. **Admin: Initialize Global Model** (5 min)
   - Navigate to Global Model page
   - Click Initialize
   - Wait for completion

2. **Admin: Create 3 Clients** (2 min)
   - Create Hospital1, Hospital2, Hospital3
   - Upload datasets for each

3. **Clients: Train Local Models** (3 min each)
   - Each hospital trains their model
   - Models use differential privacy
   - Deltas generated automatically

4. **Admin: Aggregate Models** (2 min)
   - Select all 3 clients
   - Perform aggregation
   - View improved global model

5. **Clients: Make Predictions** (1 min)
   - Enter patient data
   - Get CKD prediction
   - View probability

**Total Time: ~20 minutes for complete cycle**

---

## 🎨 UI Overview

### Admin Dashboard
- **Overview:** Statistics and metrics
- **Clients:** Manage hospitals
- **Global Model:** Initialize and view versions
- **Aggregation:** Federated learning
- **Training Logs:** Monitor all activity

### Hospital Dashboard
- **Overview:** Personal statistics
- **Clients:** View assigned clients
- **Training:** Train local models
- **Predictions:** Make CKD predictions

---

## 🔧 Advanced Configuration

### Change Port
```bash
# Edit run.sh or run.bat
# Change: --port 8000
# To: --port 8080
```

### Enable Debug Mode
```bash
# Edit App/configs/config.py
DEBUG = True
```

### Change Database Location
```bash
# Edit App/configs/config.py
DATABASE_URL = "sqlite:///./path/to/your/database.db"
```

---

## 📱 Mobile Access

The UI is fully responsive! Access from:
- Desktop browsers
- Tablets
- Mobile phones

Just navigate to: `http://YOUR_IP:8000`

---

## 🐳 Docker Quick Start

```bash
cd App/docker
docker-compose up --build
```

Access at: http://localhost:8000

---

## 💡 Tips

1. **Always initialize global model first** before client training
2. **Upload datasets** before training clients
3. **Train at least 2 clients** before aggregation
4. **Check training history** to monitor progress
5. **Use API docs** for advanced operations

---

## 📞 Need Help?

- Check **App/README.md** for detailed documentation
- View **API docs** at `/api/docs`
- Review **training logs** in the dashboard
- Check **browser console** for frontend errors
- Check **terminal output** for backend errors

---

## ✅ Verification Checklist

After setup, verify:
- [ ] Can login as admin
- [ ] Can see dashboard statistics
- [ ] Can create new client
- [ ] Can upload dataset
- [ ] Can initialize global model
- [ ] Can train client model
- [ ] Can perform aggregation
- [ ] Can make predictions
- [ ] Can view training history
- [ ] Can access API docs

---

**🎉 You're all set! Start building your federated learning pipeline!**