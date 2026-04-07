# 📁 Project Structure Documentation

Complete overview of the FL-DP Healthcare Web Application architecture.

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│  (HTML/CSS/JavaScript - Single Page Application)            │
│  - Login/Authentication UI                                   │
│  - Admin Dashboard                                           │
│  - Hospital Dashboard                                        │
│  - Responsive Design                                         │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/REST API
                     │ (JSON)
┌────────────────────▼────────────────────────────────────────┐
│                    FastAPI Backend                           │
│  - Authentication (JWT)                                      │
│  - API Routes                                                │
│  - Request Validation                                        │
│  - Authorization                                             │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
┌───────▼──────┐ ┌──▼──────┐ ┌──▼──────────────┐
│   Database   │ │ ML      │ │ File Storage    │
│   (SQLite)   │ │ Service │ │ (Uploads/Models)│
│              │ │         │ │                 │
│ - Users      │ │ - Train │ │ - Datasets      │
│ - Clients    │ │ - Agg   │ │ - Models        │
│ - Logs       │ │ - Pred  │ │ - Visualizations│
└──────────────┘ └─────────┘ └─────────────────┘
```

---

## 📂 Directory Structure

```
Major-Project-PE-FL-DP-CKD-main/
│
├── App/                              # Web Application Root
│   ├── backend/                      # FastAPI Backend
│   │   ├── main.py                   # Application entry point
│   │   ├── auth_routes.py            # Authentication endpoints
│   │   ├── client_routes.py          # Client management endpoints
│   │   ├── admin_routes.py           # Admin endpoints
│   │   └── prediction_routes.py      # Prediction endpoints
│   │
│   ├── frontend/                     # Frontend Application
│   │   ├── index.html                # Main HTML file
│   │   ├── styles.css                # Responsive CSS
│   │   └── app.js                    # JavaScript (API integration)
│   │
│   ├── database/                     # Database Layer
│   │   ├── models.py                 # SQLAlchemy models
│   │   ├── database.py               # DB connection & session
│   │   └── app.db                    # SQLite database (created at runtime)
│   │
│   ├── services/                     # Business Logic
│   │   └── ml_service.py             # ML operations service
│   │
│   ├── models/                       # Data Models
│   │   └── schemas.py                # Pydantic schemas
│   │
│   ├── utils/                        # Utilities
│   │   └── auth.py                   # Auth utilities (JWT, hashing)
│   │
│   ├── configs/                      # Configuration
│   │   └── config.py                 # App settings
│   │
│   ├── docker/                       # Docker Configuration
│   │   ├── Dockerfile                # Docker image
│   │   └── docker-compose.yml        # Docker Compose
│   │
│   ├── uploads/                      # File Uploads (created at runtime)
│   │
│   ├── requirements.txt              # Python dependencies
│   ├── .env.example                  # Environment variables template
│   ├── run.sh                        # Linux/Mac startup script
│   ├── run.bat                       # Windows startup script
│   ├── README.md                     # Main documentation
│   ├── QUICKSTART.md                 # Quick start guide
│   └── PROJECT_STRUCTURE.md          # This file
│
├── FL-DP-Healthcare/                 # Original ML Pipeline
│   ├── init_global.py                # Global model initialization
│   ├── client_train_once.py          # Client training
│   ├── aggregate_once.py             # Federated aggregation
│   ├── predict_from_patient_data.py  # Prediction
│   ├── models.py                     # Neural network models
│   ├── data_prep.py                  # Data preprocessing
│   ├── dp.py                         # Differential privacy
│   ├── eval_utils.py                 # Evaluation metrics
│   ├── viz.py                        # Visualization
│   ├── utils_io.py                   # I/O utilities
│   │
│   ├── data/                         # Template datasets
│   │   └── chronic_kidney_disease_5000.csv
│   │
│   ├── server/                       # Global model storage
│   │   ├── global_round0.pt          # Initial model
│   │   ├── global_final.pt           # Aggregated model
│   │   └── metrics_*.json            # Metrics
│   │
│   └── client[1-3]/                  # Client directories
│       ├── dataset/                  # Client datasets
│       ├── local_model.pt            # Trained model
│       ├── delta_final.pt            # Model delta
│       ├── premodel_*.pt             # Pre-training model
│       └── metrics_final.json        # Training metrics
│
├── Datasets/                         # Original datasets
│   └── *.csv
│
└── README.md                         # Project README
```

---

## 🔄 Data Flow

### 1. Authentication Flow
```
User → Login Form → POST /api/auth/login
                  → Verify credentials
                  → Generate JWT token
                  → Return token
                  → Store in localStorage
                  → Include in all API requests
```

### 2. Global Model Training Flow
```
Admin → Global Model Page → POST /api/admin/init-global-model
                          → ml_service.train_global_model()
                          → Load template dataset
                          → Train neural network
                          → Save model to server/
                          → Generate visualizations
                          → Return metrics
                          → Update database
                          → Display results
```

### 3. Client Training Flow
```
Hospital → Upload Dataset → POST /api/clients/{id}/upload-dataset
                         → Save CSV file
                         → Update client record

Hospital → Training Page → POST /api/clients/{id}/train
                        → ml_service.train_client_model()
                        → Load client dataset
                        → Load global model
                        → Train with DP
                        → Compute delta
                        → Save local model
                        → Generate visualizations
                        → Return metrics
                        → Update database
```

### 4. Aggregation Flow
```
Admin → Aggregation Page → Select clients
                        → POST /api/admin/aggregate
                        → ml_service.aggregate_models()
                        → Load client deltas
                        → FedAvg algorithm
                        → Update global model
                        → Distribute to clients
                        → Return metrics
                        → Update database
```

### 5. Prediction Flow
```
Hospital → Predictions Page → Enter patient data
                           → POST /api/predictions/
                           → ml_service.predict()
                           → Load client model
                           → Preprocess data
                           → Make prediction
                           → Return result
                           → Save to database
                           → Display result
```

---

## 🗄️ Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role ENUM('admin', 'hospital') NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME,
    updated_at DATETIME
);
```

### Clients Table
```sql
CREATE TABLE clients (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    client_name VARCHAR(100) UNIQUE NOT NULL,
    client_dir VARCHAR(255) NOT NULL,
    dataset_path VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME,
    updated_at DATETIME
);
```

### Training Logs Table
```sql
CREATE TABLE training_logs (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    client_id INTEGER REFERENCES clients(id),
    training_type VARCHAR(50),
    status VARCHAR(50),
    accuracy FLOAT,
    f1_score FLOAT,
    auc FLOAT,
    loss FLOAT,
    epochs INTEGER,
    batch_size INTEGER,
    learning_rate FLOAT,
    n_samples INTEGER,
    error_message TEXT,
    started_at DATETIME,
    completed_at DATETIME
);
```

### Predictions Table
```sql
CREATE TABLE predictions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    client_id INTEGER REFERENCES clients(id),
    patient_data TEXT,
    prediction_class INTEGER,
    prediction_label VARCHAR(10),
    prediction_probability FLOAT,
    model_version VARCHAR(100),
    created_at DATETIME
);
```

### Global Models Table
```sql
CREATE TABLE global_models (
    id INTEGER PRIMARY KEY,
    round_number INTEGER,
    model_path VARCHAR(255) NOT NULL,
    accuracy FLOAT,
    f1_score FLOAT,
    auc FLOAT,
    num_clients INTEGER,
    is_current BOOLEAN DEFAULT TRUE,
    created_at DATETIME
);
```

---

## 🔌 API Endpoints

### Authentication (`/api/auth`)
- `POST /register` - Register new user
- `POST /login` - Login and get token
- `GET /me` - Get current user
- `GET /users` - List users (admin)

### Clients (`/api/clients`)
- `POST /` - Create client
- `GET /` - List clients
- `GET /{id}` - Get client
- `POST /{id}/upload-dataset` - Upload dataset
- `POST /{id}/train` - Train model
- `GET /{id}/training-history` - Get history

### Admin (`/api/admin`)
- `POST /init-global-model` - Initialize global model
- `POST /aggregate` - Aggregate models
- `GET /dashboard-stats` - Get statistics
- `GET /client-stats` - Get client stats
- `GET /global-models` - List models
- `GET /training-logs` - Get logs

### Predictions (`/api/predictions`)
- `POST /` - Make prediction
- `GET /` - List predictions
- `GET /{id}` - Get prediction

---

## 🔐 Security Features

### Authentication
- JWT tokens with expiration
- Password hashing with bcrypt
- Secure token storage (localStorage)

### Authorization
- Role-based access control (RBAC)
- Admin-only endpoints
- User-specific data access

### Data Protection
- Differential privacy in training
- Gradient clipping
- Gaussian noise injection
- No raw data sharing

---

## 🎨 Frontend Components

### Pages
1. **Login Page** - Authentication
2. **Overview** - Dashboard statistics
3. **Clients** - Client management
4. **Training** - Model training
5. **Predictions** - CKD predictions
6. **Global Model** - Admin only
7. **Aggregation** - Admin only

### UI Components
- Navigation sidebar
- Top bar with user info
- Stat cards
- Data tables
- Forms with validation
- Modals
- Toast notifications
- Loading overlays

---

## 🧪 Testing Checklist

### Backend Tests
- [ ] User registration
- [ ] User login
- [ ] JWT token validation
- [ ] Client creation
- [ ] Dataset upload
- [ ] Global model training
- [ ] Client model training
- [ ] Federated aggregation
- [ ] Predictions
- [ ] Database operations

### Frontend Tests
- [ ] Login form
- [ ] Navigation
- [ ] Client creation
- [ ] File upload
- [ ] Training form
- [ ] Prediction form
- [ ] Data display
- [ ] Error handling
- [ ] Responsive design

### Integration Tests
- [ ] Complete FL workflow
- [ ] Multi-client aggregation
- [ ] Prediction accuracy
- [ ] Data persistence

---

## 🚀 Deployment Considerations

### Development
- Use `run.sh` or `run.bat`
- Debug mode enabled
- Auto-reload on changes

### Production
- Use Gunicorn/Uvicorn workers
- Disable debug mode
- Use environment variables
- Set up HTTPS
- Configure CORS properly
- Use production database
- Set up logging
- Monitor performance

---

## 📊 Performance Metrics

### Expected Performance
- **Global Model Training:** 2-5 minutes (30 epochs)
- **Client Training:** 1-3 minutes (10 epochs)
- **Aggregation:** 10-30 seconds
- **Prediction:** < 1 second
- **API Response:** < 100ms (non-ML endpoints)

### Scalability
- Supports multiple concurrent users
- Handles multiple clients
- Efficient database queries
- Async operations where possible

---

## 🔧 Maintenance

### Regular Tasks
- Monitor disk space (models, database)
- Review training logs
- Update dependencies
- Backup database
- Clean old model versions

### Troubleshooting
- Check logs in terminal
- Review browser console
- Verify database integrity
- Check file permissions
- Validate configurations

---

**For detailed usage instructions, see README.md and QUICKSTART.md**