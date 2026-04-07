# 🩺 FL-DP Healthcare Web Application

A **fully functional web application** for Privacy-Enhanced Federated Learning for Chronic Kidney Disease (CKD) Prediction.

This application transforms the terminal-based FL-DP pipeline into a modern, responsive web interface with role-based access control.

---

## 🚀 Features

### ✅ Backend (FastAPI)
- **JWT-based Authentication** with role-based access control (Admin & Hospital users)
- **RESTful API** with automatic documentation (Swagger/OpenAPI)
- **SQLite Database** for user management, training logs, and predictions
- **Integrated ML Services** - Wraps existing FL-DP scripts into API endpoints
- **Differential Privacy** support for client training
- **Federated Aggregation** (FedAvg) for global model updates

### ✅ Frontend (HTML/CSS/JavaScript)
- **Modern Dashboard UI** with clean, professional design
- **Responsive Layout** - Works on desktop, tablet, and mobile
- **Admin Dashboard** - Global model management, aggregation, and monitoring
- **Hospital Dashboard** - Client training, dataset upload, and predictions
- **Real-time Updates** with loading states and toast notifications
- **Data Visualization** - Training metrics, model performance charts

### ✅ Security
- Password hashing with bcrypt
- JWT token-based authentication
- Role-based access control (RBAC)
- Secure API endpoints

---

## 📂 Project Structure

```
App/
├── backend/
│   ├── main.py              # FastAPI application entry point
│   ├── auth_routes.py       # Authentication endpoints
│   ├── client_routes.py     # Client management endpoints
│   ├── admin_routes.py      # Admin endpoints (global model, aggregation)
│   └── prediction_routes.py # Prediction endpoints
├── frontend/
│   ├── index.html           # Main HTML file
│   ├── styles.css           # Responsive CSS styles
│   └── app.js               # JavaScript for API integration
├── database/
│   ├── models.py            # SQLAlchemy database models
│   └── database.py          # Database connection and session management
├── services/
│   └── ml_service.py        # ML operations service (wraps FL-DP scripts)
├── models/
│   └── schemas.py           # Pydantic schemas for request/response validation
├── utils/
│   └── auth.py              # Authentication utilities (JWT, password hashing)
├── configs/
│   └── config.py            # Application configuration
├── docker/
│   ├── Dockerfile           # Docker image configuration
│   └── docker-compose.yml   # Docker Compose configuration
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.9+
- pip
- (Optional) Docker & Docker Compose

### Method 1: Local Installation

1. **Navigate to the project directory:**
   ```bash
   cd Major-Project-PE-FL-DP-CKD-main
   ```

2. **Install dependencies:**
   ```bash
   pip install -r App/requirements.txt
   ```

3. **Run the application:**
   ```bash
   python -m uvicorn App.backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Access the application:**
   - Frontend: http://localhost:8000
   - API Documentation: http://localhost:8000/api/docs
   - Alternative API Docs: http://localhost:8000/api/redoc

### Method 2: Docker Installation

1. **Navigate to docker directory:**
   ```bash
   cd App/docker
   ```

2. **Build and run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

3. **Access the application:**
   - Frontend: http://localhost:8000
   - API Documentation: http://localhost:8000/api/docs

---

## 🔐 Default Credentials

### Admin Account
- **Username:** `admin`
- **Password:** `admin123`
- **Role:** Administrator (full access)

### Creating Hospital Users
1. Login as admin
2. Or use the registration endpoint via API docs

---

## 📖 User Guide

### For Admin Users

#### 1. Initialize Global Model
- Navigate to **Global Model** page
- Set training parameters (epochs, batch size, learning rate)
- Click **Initialize Global Model**
- Wait for training to complete
- View metrics and visualizations

#### 2. Manage Clients (Hospitals)
- Navigate to **Clients** page
- Click **Add Client** to create new hospital client
- Upload datasets for each client
- Monitor client status and activity

#### 3. Perform Federated Aggregation
- Navigate to **Aggregation** page
- Select clients to aggregate (must have trained models)
- Click **Perform Aggregation**
- View updated global model metrics
- Check client statistics

#### 4. Monitor Dashboard
- View overall statistics
- Track training progress
- Monitor predictions
- View recent activity

### For Hospital Users

#### 1. Upload Dataset
- Navigate to **Clients** page
- Click **Upload** button for your client
- Select CSV file with patient data
- Confirm upload success

#### 2. Train Local Model
- Navigate to **Training** page
- Select your client
- Configure training parameters
- Click **Start Training**
- View training results and metrics

#### 3. Make Predictions
- Navigate to **Predictions** page
- Select your client
- Enter patient data
- Click **Predict**
- View prediction result (CKD: YES/NO)
- Check prediction probability

#### 4. View History
- Check training history
- Review past predictions
- Monitor model performance

---

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info
- `GET /api/auth/users` - List all users (admin only)

### Clients
- `POST /api/clients/` - Create new client
- `GET /api/clients/` - List all clients
- `GET /api/clients/{id}` - Get client details
- `POST /api/clients/{id}/upload-dataset` - Upload dataset
- `POST /api/clients/{id}/train` - Train client model
- `GET /api/clients/{id}/training-history` - Get training history

### Admin
- `POST /api/admin/init-global-model` - Initialize global model
- `POST /api/admin/aggregate` - Perform federated aggregation
- `GET /api/admin/dashboard-stats` - Get dashboard statistics
- `GET /api/admin/client-stats` - Get client statistics
- `GET /api/admin/global-models` - List global model versions
- `GET /api/admin/training-logs` - Get all training logs

### Predictions
- `POST /api/predictions/` - Make prediction
- `GET /api/predictions/` - Get prediction history
- `GET /api/predictions/{id}` - Get specific prediction

---

## 🔄 Complete Workflow

### Initial Setup (Admin)
1. Login as admin
2. Initialize global model
3. Create hospital clients
4. Distribute global model to clients (automatic)

### Hospital Training
1. Hospital users login
2. Upload their local datasets
3. Train local models with differential privacy
4. Models automatically generate deltas for aggregation

### Federated Aggregation (Admin)
1. Admin selects trained clients
2. Performs federated aggregation (FedAvg)
3. Updated global model distributed to all clients
4. Process repeats for multiple rounds

### Making Predictions
1. Hospital users can make predictions anytime
2. Uses latest available model
3. Results stored in database
4. Privacy-preserved throughout

---

## 🎨 UI Features

- **Clean Dashboard Design** - Modern, professional interface
- **Responsive Layout** - Works on all screen sizes
- **Real-time Feedback** - Loading states, progress indicators
- **Toast Notifications** - Success/error messages
- **Data Tables** - Sortable, searchable tables
- **Form Validation** - Client-side and server-side validation
- **Role-based UI** - Admin-only sections hidden for regular users

---

## 🔧 Configuration

Edit `App/configs/config.py` to customize:

```python
# Security
SECRET_KEY = "your-secret-key-here"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

# Database
DATABASE_URL = "sqlite:///./App/database/app.db"

# CORS
CORS_ORIGINS = ["http://localhost:3000", "http://localhost:8000"]

# Training defaults
DEFAULT_EPOCHS = 30
DEFAULT_BATCH_SIZE = 64
DEFAULT_LEARNING_RATE = 0.001
```

---

## 📊 Database Schema

### Users
- id, username, email, hashed_password, full_name, role, is_active, created_at

### Clients
- id, user_id, client_name, client_dir, dataset_path, is_active, created_at

### TrainingLogs
- id, user_id, client_id, training_type, status, accuracy, f1_score, auc, epochs, started_at, completed_at

### Predictions
- id, user_id, client_id, patient_data, prediction_class, prediction_label, prediction_probability, created_at

### GlobalModels
- id, round_number, model_path, accuracy, f1_score, auc, num_clients, is_current, created_at

---

## 🐛 Troubleshooting

### Issue: Import errors
**Solution:** Ensure you're running from the project root directory and all dependencies are installed.

### Issue: Database not found
**Solution:** The database is created automatically on first run. Ensure write permissions in `App/database/` directory.

### Issue: CORS errors
**Solution:** Update `CORS_ORIGINS` in `App/configs/config.py` to include your frontend URL.

### Issue: Model training fails
**Solution:** Ensure the template CSV file exists at `FL-DP-Healthcare/data/chronic_kidney_disease_5000.csv`

---

## 🚀 Production Deployment

### Security Checklist
- [ ] Change default admin password
- [ ] Update SECRET_KEY in config
- [ ] Use environment variables for sensitive data
- [ ] Enable HTTPS
- [ ] Configure proper CORS origins
- [ ] Set up database backups
- [ ] Configure logging
- [ ] Use production WSGI server (Gunicorn)

### Recommended Production Setup
```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn App.backend.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## 📝 Notes

- The application integrates seamlessly with existing FL-DP-Healthcare scripts
- All ML operations use differential privacy for client training
- Visualizations (confusion matrix, ROC curves, calibration plots) are generated automatically
- The frontend is a single-page application (SPA) with no build step required
- Database migrations are handled automatically by SQLAlchemy

---

## 👥 Team

1. Rakshith PR - NNM23CS507
2. Yathish - NNM23CS517
3. Muskan
4. Adaline

**Mentor:** Mr. Pawan Hegde  
**Department:** CSE, NMAM Institute Of Technology, Nitte

---

## 📄 License

This project is for academic purposes.

---

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- PyTorch for deep learning capabilities
- Scikit-learn for ML utilities
- The open-source community

---

**For any issues or questions, please refer to the API documentation at `/api/docs` or contact the development team.**