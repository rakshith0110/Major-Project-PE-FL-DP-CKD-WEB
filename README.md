# 🩺 Privacy-Enhanced Federated Learning for Chronic Kidney Disease (CKD)

A complete **Federated Learning (FL) system with Differential Privacy (DP)** for predicting Chronic Kidney Disease while preserving patient privacy. This project includes both a command-line FL pipeline and a full-featured web application for collaborative healthcare AI.

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.3.1-red.svg)](https://pytorch.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-Academic-yellow.svg)]()

---

## 👥 Team Members

1. **Rakshith PR** - NNM23CS507
2. **Yathish** - NNM23CS517
3. **Muskan**
4. **Adaline**

**Mentor**: Mr. Pawan Hegde  
**Institution**: Department of Computer Science & Engineering, NMAM Institute Of Technology, Nitte

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Project Structure](#-project-structure)
- [Technologies Used](#-technologies-used)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage Guides](#-usage-guides)
  - [Command-Line FL Pipeline](#1-command-line-fl-pipeline)
  - [Web Application](#2-web-application)
- [System Architecture](#-system-architecture)
- [Privacy & Security](#-privacy--security)
- [API Documentation](#-api-documentation)
- [Troubleshooting](#-troubleshooting)
- [References](#-references)

---

## 🎯 Overview

This project demonstrates how multiple hospitals (clients) can collaboratively train a machine learning model for Chronic Kidney Disease prediction **without sharing raw patient data**. The system implements:

- **Federated Learning (FL)**: Decentralized training across multiple clients
- **Differential Privacy (DP)**: Mathematical privacy guarantees through gradient clipping and noise injection
- **FedAvg Algorithm**: Secure model aggregation
- **Web Interface**: User-friendly dashboard for admins and clients
- **Dual Authentication**: Enhanced security with separate login and training passwords

### Why This Matters

- 🏥 **Healthcare Privacy**: Patient data never leaves the hospital
- 🤝 **Collaborative Learning**: Multiple hospitals benefit from shared knowledge
- 🔒 **Privacy Guarantees**: Differential privacy provides mathematical privacy bounds
- 📊 **High Accuracy**: Maintains model performance while preserving privacy

---

## ✨ Key Features

### Core Capabilities
✅ **Privacy-Preserving Training**: No raw data sharing between hospitals  
✅ **Differential Privacy**: Gradient clipping + Gaussian noise injection  
✅ **Federated Aggregation**: FedAvg algorithm for model updates  
✅ **Scalable Architecture**: Support for unlimited number of clients  
✅ **Real-time Predictions**: CKD risk assessment using global model  

### Web Application Features
✅ **Dual Authentication System**: Login password + Training password  
✅ **Role-Based Access Control**: Admin and Client dashboards  
✅ **Dataset Management**: CSV upload with validation  
✅ **Training Configuration**: Customizable hyperparameters and DP settings  
✅ **Batch Predictions**: Process multiple patient records  
✅ **Email Notifications**: Automated updates for training and aggregation  
✅ **Audit Logging**: Complete system activity tracking  
✅ **API Documentation**: Auto-generated Swagger/OpenAPI docs  

---

## 📂 Project Structure

```
Major-Project-PE-FL-DP-CKD-main/
├── App/                              # Web Application
│   ├── backend/
│   │   ├── api/
│   │   │   ├── admin_routes.py      # Admin API endpoints
│   │   │   └── client_routes.py     # Client API endpoints
│   │   ├── core/
│   │   │   ├── auth.py              # JWT authentication
│   │   │   └── database.py          # SQLite database
│   │   ├── models/
│   │   │   └── schemas.py           # Pydantic models
│   │   ├── services/
│   │   │   ├── fl_service.py        # FL logic
│   │   │   └── email_service.py     # Email notifications
│   │   └── main.py                  # FastAPI application
│   ├── frontend/
│   │   ├── static/                  # CSS, JS, images
│   │   └── templates/               # HTML pages
│   ├── models/                      # Saved models
│   │   ├── global_model.pt          # Global model
│   │   ├── scaler.pkl               # Data scaler
│   │   └── client_*/                # Client-specific models
│   ├── uploads/                     # Client datasets
│   ├── federated_ckd.db            # SQLite database
│   ├── run.sh                       # Startup script
│   └── README.md                    # App documentation
│
├── FL-DP-Healthcare/                # Command-Line FL Pipeline
│   ├── models.py                    # Neural network architecture
│   ├── data_prep.py                 # Data preprocessing
│   ├── dp.py                        # Differential privacy
│   ├── eval_utils.py                # Evaluation metrics
│   ├── init_global.py               # Global model initialization
│   ├── client_train_once.py         # Client training
│   ├── aggregate_once.py            # Federated aggregation
│   ├── predict_from_patient_data.py # Prediction script
│   ├── client1/, client2/, client3/ # Client directories
│   ├── server/                      # Server directory
│   └── data/                        # Datasets
│
├── Datasets/                        # Sample datasets
│   ├── chronic_kidney_disease_5000.csv
│   ├── client1_ckd.csv
│   ├── client2_ckd.csv
│   └── client3_ckd.csv
│
├── requirements.txt                 # Python dependencies
├── SETUP_VENV.md                   # Virtual environment guide
└── README.md                        # This file
```

---

## 🛠 Technologies Used

### Core Technologies
- **Python 3.11** - Programming language
- **PyTorch 2.3.1** - Deep learning framework
- **FastAPI 0.104.1** - Web framework
- **SQLite** - Database
- **Uvicorn** - ASGI server

### Machine Learning & Data Science
- **Scikit-learn 1.5.1** - ML utilities
- **NumPy 1.26.4** - Numerical computing
- **Pandas 2.2.2** - Data manipulation
- **Matplotlib 3.9.0** - Visualization
- **Seaborn 0.13.2** - Statistical visualization

### Security & Authentication
- **python-jose** - JWT tokens
- **passlib** - Password hashing
- **Differential Privacy** - Privacy guarantees

### Additional Libraries
- **aiosmtplib** - Async email
- **pydantic** - Data validation
- **python-multipart** - File uploads

---

## 🚀 Installation

### Prerequisites

1. **Python 3.11** (Required)
   ```bash
   python3.11 --version
   ```
   Download from: https://www.python.org/downloads/

2. **Git** (for cloning)
   ```bash
   git --version
   ```

### Step 1: Clone Repository

```bash
git clone https://github.com/rakshith0110/Major-Project-PE-FL-DP-CKD.git
cd Major-Project-PE-FL-DP-CKD-main
```

### Step 2: Create Virtual Environment

```bash
python3.11 -m venv venv
```

### Step 3: Activate Virtual Environment

**Linux/macOS:**
```bash
source venv/bin/activate
```

**Windows (Command Prompt):**
```bash
venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```bash
venv\Scripts\Activate.ps1
```

You should see `(venv)` in your terminal prompt.

### Step 4: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 5: Verify Installation

```bash
python -c "import torch, numpy, pandas, sklearn, fastapi; print('✅ Installation successful!')"
```

---

## ⚡ Quick Start

### Option 1: Web Application (Recommended)

```bash
cd App
./run.sh
```

Or manually:
```bash
cd App
python3.11 -m uvicorn App.backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Access at: **http://localhost:8000**

### Option 2: Command-Line Pipeline

```bash
cd FL-DP-Healthcare

# 1. Initialize global model
python3.11 init_global.py --template_csv data/chronic_kidney_disease_5000.csv --epochs 30

# 2. Train clients
python3.11 client_train_once.py --client_name Client1 --client_dir client1 \
  --client_csv client1/dataset/client1_ckd.csv --premodel_ckpt client1/premodel_client1.pt \
  --template_csv data/chronic_kidney_disease_5000.csv

# 3. Aggregate models
python3.11 aggregate_once.py --delta1 client1/delta_final.pt \
  --delta2 client2/delta_final.pt --delta3 client3/delta_final.pt \
  --template_csv data/chronic_kidney_disease_5000.csv

# 4. Make predictions
python3.11 predict_from_patient_data.py --client_name Client1 --client_dir client1 \
  --template_csv data/chronic_kidney_disease_5000.csv \
  --patient_csv data/patient_data.csv --all_rows
```

---

## 📖 Usage Guides

## 1. Command-Line FL Pipeline

### Step 1: Initialize Global Model

Train the initial global model on a template dataset:

```bash
cd FL-DP-Healthcare
python3.11 init_global.py \
  --template_csv data/chronic_kidney_disease_5000.csv \
  --epochs 30 \
  --batch 64 \
  --lr 1e-3
```

**Output**: `server/global_round0.pt`, metrics, and visualizations

### Step 2: Train Client Models

Each hospital trains on their local data:

**Client 1:**
```bash
python3.11 client_train_once.py \
  --client_name Client1 \
  --client_dir client1 \
  --client_csv client1/dataset/client1_ckd.csv \
  --premodel_ckpt client1/premodel_client1.pt \
  --template_csv data/chronic_kidney_disease_5000.csv
```

**Client 2:**
```bash
python3.11 client_train_once.py \
  --client_name Client2 \
  --client_dir client2 \
  --client_csv client2/dataset/client2_ckd.csv \
  --premodel_ckpt client2/premodel_client2.pt \
  --template_csv data/chronic_kidney_disease_5000.csv
```

**Client 3:**
```bash
python3.11 client_train_once.py \
  --client_name Client3 \
  --client_dir client3 \
  --client_csv client3/dataset/client3_ckd.csv \
  --premodel_ckpt client3/premodel_client3.pt \
  --template_csv data/chronic_kidney_disease_5000.csv
```

**Output**: `client*/delta_final.pt`, `local_model.pt`, metrics

### Step 3: Federated Aggregation

Aggregate client updates using FedAvg:

```bash
python3.11 aggregate_once.py \
  --delta1 client1/delta_final.pt \
  --delta2 client2/delta_final.pt \
  --delta3 client3/delta_final.pt \
  --template_csv data/chronic_kidney_disease_5000.csv
```

**Output**: Updated `server/global_final.pt`

### Step 4: Make Predictions

Use the global model for predictions:

```bash
python3.11 predict_from_patient_data.py \
  --client_name Client1 \
  --client_dir client1 \
  --template_csv data/chronic_kidney_disease_5000.csv \
  --patient_csv data/patient_data.csv \
  --all_rows
```

**Options:**
- `--row_index N`: Predict single row
- `--all_rows`: Predict all rows

---

## 2. Web Application

### Access Points

- **Landing Page**: http://localhost:8000
- **Admin Dashboard**: http://localhost:8000/admin
- **Client Dashboard**: http://localhost:8000/client
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Admin Workflow

#### 1. Login
**Default Credentials:**
- Username: `admin`
- Password: `admin123`

#### 2. Initialize Global Model
- Navigate to "Initialize Model" section
- Configure training parameters:
  - Epochs: 20-50
  - Batch Size: 32-128
  - Learning Rate: 0.0001-0.01
- Click "Initialize Global Model"
- Wait for completion (view metrics)

#### 3. Create Clients
- Go to "Client Management"
- Click "Create New Client"
- Fill in details:
  - Client Name (e.g., "City Hospital")
  - Email address
  - Login Password
  - Training Password
  - Description (optional)
- Click "Create Client"
- Credentials sent via email automatically

#### 4. Monitor Clients
- View client list with status:
  - ✅ Active
  - 🔄 Training
  - 📤 New Update Available
  - ⏸️ Inactive
- Check training metrics
- View training history

#### 5. Perform Aggregation
- Navigate to "Aggregation" section
- System automatically detects clients with updates
- Review participating clients
- Click "Aggregate Models"
- Updated global model distributed to all clients

### Client Workflow

#### 1. Login
- Use credentials received via email
- Enter Client Name and Login Password

#### 2. Upload Dataset
- Click "Upload Dataset"
- Select CSV file (must match template schema)
- Required columns:
  - age, bp, sg, al, su, rbc, pc, pcc, ba, bgr, bu, sc, sod, pot, hemo, pcv, wc, rc, htn, dm, cad, appet, pe, ane, classification
- File validated and stored securely

#### 3. Configure Training
- Set hyperparameters:
  - **Epochs**: 10-100 (default: 20)
  - **Batch Size**: 8-256 (default: 32)
  - **Learning Rate**: 0.0001-0.1 (default: 0.001)
- Configure Differential Privacy:
  - **Noise Multiplier**: 0.1-10.0 (default: 1.0)
    - Higher = More privacy, less accuracy
  - **Max Gradient Norm**: 0.1-10.0 (default: 1.0)
    - Gradient clipping threshold

#### 4. Train Model
- Enter Training Password (for authorization)
- Click "Start Training"
- Monitor progress:
  - Training loss
  - Validation metrics
  - Privacy budget (ε)
- Status changes to "New Update Available"

#### 5. Make Predictions
**Single Prediction:**
- Enter patient data manually
- Click "Predict"
- View result: CKD risk + confidence score

**Batch Predictions:**
- Upload CSV with patient records
- Click "Predict Batch"
- Download results as CSV

#### 6. View History
- Training History: Past training sessions with metrics
- Prediction History: All predictions made
- Download reports

---

## 🏗 System Architecture

### Federated Learning Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    ADMIN (Server)                            │
│  1. Initialize Global Model                                  │
│  2. Create Clients                                           │
│  3. Distribute Global Model                                  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────────┐
        │                                       │
        ▼                                       ▼
┌──────────────────┐                  ┌──────────────────┐
│   CLIENT 1       │                  │   CLIENT 2       │
│  (Hospital A)    │                  │  (Hospital B)    │
│                  │                  │                  │
│ 1. Upload Data   │                  │ 1. Upload Data   │
│ 2. Train Local   │                  │ 2. Train Local   │
│ 3. Apply DP      │                  │ 3. Apply DP      │
│ 4. Send Δweights │                  │ 4. Send Δweights │
└──────────────────┘                  └──────────────────┘
        │                                       │
        └───────────────┬───────────────────────┘
                        ▼
        ┌───────────────────────────────┐
        │    FEDERATED AGGREGATION      │
        │    (FedAvg Algorithm)         │
        │  • Average weight updates     │
        │  • Update global model        │
        │  • Distribute to clients      │
        └───────────────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │   UPDATED GLOBAL MODEL        │
        │   • Better accuracy           │
        │   • Privacy preserved         │
        │   • Ready for predictions     │
        └───────────────────────────────┘
```

### Database Schema

**10 Tables:**
1. `admin` - Admin users
2. `clients` - Hospital/client records
3. `training_logs` - Training history
4. `global_model` - Global model versions
5. `local_models` - Client models
6. `predictions` - Prediction records
7. `aggregation_logs` - Aggregation history
8. `email_notifications` - Email tracking
9. `audit_logs` - System audit trail
10. `client_datasets` - Dataset metadata

---

## 🔐 Privacy & Security

### Differential Privacy Implementation

**Gradient Clipping:**
```python
# Limit gradient magnitude
max_norm = 1.0
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm)
```

**Gaussian Noise Injection:**
```python
# Add calibrated noise to gradients
noise_multiplier = 1.0
for param in model.parameters():
    noise = torch.randn_like(param.grad) * noise_multiplier * max_norm
    param.grad += noise
```

**Privacy Budget (ε):**
- Lower ε = Better privacy
- Calculated based on: σ (noise), C (clipping), iterations
- Typical range: 1.0 - 10.0

### Security Features

✅ **Authentication:**
- JWT tokens (8-hour expiration)
- SHA-256 password hashing
- Dual password system

✅ **Data Protection:**
- No raw data transmission
- Only DP-protected weight updates shared
- Client data isolation

✅ **Audit Trail:**
- All actions logged
- User identification
- Timestamp tracking

---

## 📡 API Documentation

### Admin Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/admin/login` | Admin login |
| POST | `/api/admin/clients` | Create client |
| GET | `/api/admin/clients` | List clients |
| GET | `/api/admin/clients/{id}` | Get client details |
| DELETE | `/api/admin/clients/{id}` | Deactivate client |
| POST | `/api/admin/initialize-global-model` | Initialize model |
| POST | `/api/admin/aggregate` | Perform aggregation |
| GET | `/api/admin/global-metrics` | Global metrics |
| GET | `/api/admin/dashboard/stats` | Dashboard stats |

### Client Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/client/login` | Client login |
| POST | `/api/client/upload-dataset` | Upload CSV |
| POST | `/api/client/train` | Train model |
| POST | `/api/client/predict` | Single prediction |
| POST | `/api/client/predict-batch` | Batch predictions |
| GET | `/api/client/download-predictions/{file}` | Download results |
| GET | `/api/client/training-history` | Training logs |
| GET | `/api/client/prediction-history` | Prediction logs |
| GET | `/api/client/dashboard/stats` | Dashboard stats |

**Full API Documentation**: http://localhost:8000/docs

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9  # Linux/Mac
netstat -ano | findstr :8000   # Windows (find PID, then kill)
```

#### 2. Module Import Errors
```bash
# Ensure correct directory
cd /path/to/Major-Project-PE-FL-DP-CKD-main
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### 3. Database Issues
```bash
# Reinitialize database
cd App
python3.11 -c "from App.backend.core.database import init_database; init_database()"
```

#### 4. Virtual Environment Not Activated
```bash
# Check if activated (should see (venv))
which python  # Should point to venv/bin/python

# Reactivate
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

#### 5. CUDA/GPU Issues
```bash
# Use CPU if GPU unavailable
export CUDA_VISIBLE_DEVICES=""
```

### Getting Help

1. Check API documentation: http://localhost:8000/docs
2. Review logs in terminal
3. Check database: `App/federated_ckd.db`
4. Verify file paths and permissions
5. Ensure Python 3.11 is being used

---

## 📚 References

### Academic Papers
- **Federated Learning**: McMahan et al., "Communication-Efficient Learning of Deep Networks from Decentralized Data" (2017)
- **Differential Privacy**: Dwork & Roth, "The Algorithmic Foundations of Differential Privacy" (2014)
- **Privacy in Healthcare**: Kaissis et al., "Secure, privacy-preserving and federated machine learning in medical imaging" (2020)

### Documentation
- **FastAPI**: https://fastapi.tiangolo.com/
- **PyTorch**: https://pytorch.org/docs/
- **Scikit-learn**: https://scikit-learn.org/
- **Differential Privacy**: https://github.com/pytorch/opacus

### Dataset
- **CKD Dataset**: UCI Machine Learning Repository
- **Features**: 24 clinical features + classification
- **Size**: 5000 patient records (synthetic for demo)

---

## 📄 License

This project is developed for **academic purposes** as part of a major project at NMAM Institute Of Technology, Nitte.

---

## 🙏 Acknowledgments

- **Mentor**: Mr. Pawan Hegde for guidance and support
- **NMAMIT**: For providing resources and infrastructure
- **Open Source Community**: For excellent libraries and tools

---

## 📞 Contact

For questions or support:
- **GitHub**: https://github.com/rakshith0110/Major-Project-PE-FL-DP-CKD
- **Institution**: NMAM Institute Of Technology, Nitte
- **Department**: Computer Science & Engineering

---

## 🎯 Project Status

- ✅ **Backend**: 100% Complete
- ✅ **FL Pipeline**: 100% Complete
- ✅ **API**: 100% Complete
- ✅ **Database**: 100% Complete
- ✅ **Authentication**: 100% Complete
- ✅ **Privacy (DP)**: 100% Complete
- 🔄 **Frontend**: In Progress
- 📝 **Documentation**: Complete

---

## 🚀 Future Enhancements

- [ ] Advanced visualization dashboards
- [ ] Real-time training progress
- [ ] Multi-round federated learning automation
- [ ] Support for more ML models
- [ ] Mobile application
- [ ] Blockchain integration for audit trail
- [ ] Advanced privacy metrics (Rényi DP)

---

**Built with ❤️ for Privacy-Preserving Healthcare AI**

*Empowering collaborative medical research while protecting patient privacy*

---

## 📊 Quick Reference Card

### Essential Commands

```bash
# Setup
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run Web App
cd App && ./run.sh

# Run FL Pipeline
cd FL-DP-Healthcare
python3.11 init_global.py --template_csv data/chronic_kidney_disease_5000.csv
python3.11 client_train_once.py --client_name Client1 --client_dir client1 ...
python3.11 aggregate_once.py --delta1 client1/delta_final.pt ...

# Test API
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/admin/login -H "Content-Type: application/json" -d '{"username":"admin","password":"admin123"}'
```

### Default Credentials
- **Admin**: username=`admin`, password=`admin123`
- **Clients**: Created by admin, credentials sent via email

### Key Directories
- `App/` - Web application
- `FL-DP-Healthcare/` - Command-line pipeline
- `Datasets/` - Sample datasets
- `App/models/` - Saved models
- `App/uploads/` - Client datasets

---

*Last Updated: April 2026*
