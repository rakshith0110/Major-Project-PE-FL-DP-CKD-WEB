# 🏥 Federated Learning CKD Web Application

## Privacy-Enhanced Federated Learning for Chronic Kidney Disease

A complete web-based federated learning system with differential privacy for collaborative CKD prediction across multiple hospitals without sharing raw patient data.

---

## 🎯 System Overview

### Architecture
- **Backend**: FastAPI (Python)
- **Database**: SQLite
- **ML Framework**: PyTorch
- **Privacy**: Differential Privacy (DP)
- **Aggregation**: Federated Averaging (FedAvg)

### Key Features
✅ **Dual Authentication System**
- Login Password (Dashboard Access)
- Training Password (Model Training Authorization)

✅ **Role-Based Access Control**
- Admin: Global model management, client creation, aggregation
- Client: Local training, predictions, visualization

✅ **Privacy Preservation**
- No raw data sharing
- Differential Privacy on model weights
- Gradient clipping and noise injection

✅ **Dynamic Federated Learning**
- Scalable to any number of clients
- Automatic aggregation detection
- Real-time status updates

---

## 📁 Project Structure

```
App/
├── backend/
│   ├── api/
│   │   ├── admin_routes.py      # Admin API endpoints
│   │   └── client_routes.py     # Client API endpoints
│   ├── core/
│   │   ├── auth.py              # Authentication & JWT
│   │   └── database.py          # Database schema & operations
│   ├── models/
│   │   └── schemas.py           # Pydantic models
│   ├── services/
│   │   ├── fl_service.py        # Federated Learning logic
│   │   └── email_service.py     # Email notifications
│   └── main.py                  # FastAPI application
├── frontend/
│   ├── static/                  # CSS, JS, images
│   └── templates/               # HTML templates
├── models/                      # Saved models
├── uploads/                     # Client datasets
├── requirements.txt
├── run.sh                       # Startup script
└── README.md
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.11 (required)
- pip
- Virtual environment (recommended)

### Step 1: Create Virtual Environment

```bash
cd App
python3.11 -m venv venv
```

Activate the virtual environment:

**Linux/Mac:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Initialize Database

```bash
python3.11 -c "from App.backend.core.database import init_database; init_database()"
```

### Step 4: Start Server

```bash
./run.sh
```

Or manually:

```bash
python3.11 -m uvicorn App.backend.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🌐 Access Points

- **Landing Page**: http://localhost:8000
- **Admin Dashboard**: http://localhost:8000/admin
- **Client Dashboard**: http://localhost:8000/client
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 👑 Admin Workflow

### 1. Login
- **Default Credentials**:
  - Username: `admin`
  - Password: `admin123`

### 2. Initialize Global Model
```
POST /api/admin/initialize-global-model
```
- Trains initial global model
- Required before clients can train

### 3. Create Clients
```
POST /api/admin/clients
```
**Required Fields**:
- Client Name
- Email
- Login Password
- Training Password
- Description (optional)

**Email Notification**: Credentials sent automatically

### 4. Monitor Clients
```
GET /api/admin/clients
GET /api/admin/clients-metrics
GET /api/admin/dashboard/stats
```

### 5. Perform Aggregation
```
POST /api/admin/aggregate
```
- Automatically detects clients with "New Update Available"
- Performs FedAvg aggregation
- Updates global model
- Distributes to all clients

---

## 🏥 Client Workflow

### 1. Login
- Use credentials received via email
- Client Name + Login Password

### 2. Upload Dataset
```
POST /api/client/upload-dataset
```
- Upload CSV file with patient data
- Must match template schema

### 3. Train Local Model
```
POST /api/client/train
```

**Required**:
- Training Password (for authorization)

**Configuration**:
- Epochs (1-100)
- Batch Size (8-256)
- Learning Rate (0.0001-0.1)
- Noise Multiplier (0.1-10.0) - DP parameter
- Max Gradient Norm (0.1-10.0) - DP parameter

**Process**:
1. Loads global model as starting point
2. Trains on local dataset
3. Applies Differential Privacy:
   - Gradient clipping
   - Gaussian noise injection
4. Sends only weight updates (delta) to server
5. Status changes to "New Update Available"

### 4. Make Predictions
```
POST /api/client/predict              # Single prediction
POST /api/client/predict-batch        # Batch predictions
GET /api/client/download-predictions  # Download results
```

### 5. View History
```
GET /api/client/training-history
GET /api/client/prediction-history
```

---

## 🔐 Security Features

### Authentication
- JWT-based token authentication
- Dual password system (login + training)
- Password hashing (SHA-256)
- Token expiration (8 hours)

### Privacy Protection
- **Differential Privacy**:
  - Gradient clipping: Limits gradient magnitude
  - Noise injection: Adds calibrated Gaussian noise
  - Configurable privacy budget

- **Data Isolation**:
  - Each client has separate directory
  - No cross-client data access
  - Only model weights shared

### Audit Logging
- All actions logged with timestamps
- User identification
- IP address tracking (optional)

---

## 📊 Database Schema

### Tables
1. **admin** - Admin users
2. **clients** - Hospital/client information
3. **training_logs** - Training history per client
4. **global_model** - Global model versions
5. **local_models** - Client local models
6. **predictions** - Prediction records
7. **aggregation_logs** - Aggregation history
8. **email_notifications** - Email log
9. **audit_logs** - System audit trail
10. **client_datasets** - Dataset metadata

---

## 📧 Email Notifications

### Configuration
Update in `App/backend/services/email_service.py`:

```python
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "your-email@gmail.com"
SMTP_PASSWORD = "your-app-password"
```

### Notification Types
1. **Client Created** - Credentials sent to new client
2. **Training Started** - Confirmation to client
3. **Training Complete** - Notification to admin
4. **Aggregation Complete** - Notification to all clients

---

## 🔄 Federated Learning Flow

```
1. Admin initializes global model
   ↓
2. Admin creates clients
   ↓
3. Clients upload datasets
   ↓
4. Clients train local models (with DP)
   ↓
5. Clients send weight updates to server
   ↓
6. Admin performs aggregation (FedAvg)
   ↓
7. Updated global model distributed to clients
   ↓
8. Clients use global model for predictions
   ↓
9. Repeat from step 4 for next round
```

---

## 🎨 API Endpoints

### Admin Endpoints
- `POST /api/admin/login` - Admin login
- `POST /api/admin/clients` - Create client
- `GET /api/admin/clients` - List all clients
- `GET /api/admin/clients/{id}` - Get client details
- `GET /api/admin/clients-metrics` - Client metrics
- `POST /api/admin/initialize-global-model` - Initialize model
- `POST /api/admin/aggregate` - Perform aggregation
- `GET /api/admin/global-metrics` - Global model metrics
- `GET /api/admin/dashboard/stats` - Dashboard statistics
- `DELETE /api/admin/clients/{id}` - Deactivate client

### Client Endpoints
- `POST /api/client/login` - Client login
- `POST /api/client/upload-dataset` - Upload dataset
- `POST /api/client/train` - Train local model
- `POST /api/client/predict` - Single prediction
- `POST /api/client/predict-batch` - Batch predictions
- `GET /api/client/download-predictions/{filename}` - Download results
- `GET /api/client/training-history` - Training history
- `GET /api/client/prediction-history` - Prediction history
- `GET /api/client/dashboard/stats` - Dashboard statistics

---

## 🧪 Testing

### Test Admin Login
```bash
curl -X POST http://localhost:8000/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### Test Health Check
```bash
curl http://localhost:8000/health
```

---

## 📝 Configuration

### Differential Privacy Parameters

**Noise Multiplier** (σ):
- Higher = More privacy, less accuracy
- Recommended: 0.5 - 2.0
- Default: 1.0

**Max Gradient Norm** (C):
- Gradient clipping threshold
- Recommended: 0.5 - 2.0
- Default: 1.0

**Privacy Budget** (ε):
- Calculated based on σ, C, and training iterations
- Lower ε = Better privacy

---

## 🐛 Troubleshooting

### Database Issues
```bash
# Reinitialize database
python3.11 -c "from App.backend.core.database import init_database; init_database()"
```

### Port Already in Use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

### Import Errors
```bash
# Ensure you're in the correct directory
cd /path/to/Major-Project-PE-FL-DP-CKD-main
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

---

## 📚 References

- **Federated Learning**: McMahan et al., 2017
- **Differential Privacy**: Dwork & Roth, 2014
- **FastAPI**: https://fastapi.tiangolo.com/
- **PyTorch**: https://pytorch.org/

---

## 👥 Team

1. Rakshith PR - NNM23CS507
2. Yathish - NNM23CS517
3. Muskan
4. Adaline

**Mentor**: Mr. Pawan Hegde  
**Institution**: CSE, NMAM Institute Of Technology, Nitte

---

## 📄 License

This project is for academic purposes.

---

## 🆘 Support

For issues or questions:
1. Check API documentation: http://localhost:8000/docs
2. Review logs in terminal
3. Check database: `federated_ckd.db`

---

**Built with ❤️ for Privacy-Preserving Healthcare AI**