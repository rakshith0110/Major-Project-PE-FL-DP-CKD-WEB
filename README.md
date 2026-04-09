# 🩺 Privacy-Enhanced Federated Learning for Chronic Kidney Disease (CKD)

A complete **Federated Learning (FL) system with Differential Privacy (DP)** for predicting Chronic Kidney Disease while preserving patient privacy. This project enables multiple hospitals to collaboratively train AI models **without sharing raw patient data**.

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
- [System Architecture](#-system-architecture)
- [Prerequisites](#-prerequisites)
- [Installation Guide](#-installation-guide)
- [Running the Project](#-running-the-project)
  - [Option 1: Web Application](#option-1-web-application-recommended)
  - [Option 2: Command-Line Pipeline](#option-2-command-line-fl-pipeline)
- [Usage Guides](#-usage-guides)
- [Project Structure](#-project-structure)
- [API Documentation](#-api-documentation)
- [Troubleshooting](#-troubleshooting)
- [References](#-references)

---

## 🎯 Overview

This project demonstrates how multiple hospitals (clients) can collaboratively train a machine learning model for Chronic Kidney Disease prediction **without sharing raw patient data**. 

### Core Technologies
- **Federated Learning (FL)**: Decentralized training across multiple clients
- **Differential Privacy (DP)**: Mathematical privacy guarantees (gradient clipping + noise injection)
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

---

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

### Required Software
1. **Python 3.11** (Required - specific version)
   ```bash
   python3.11 --version
   ```
   Download from: https://www.python.org/downloads/

2. **Git** (for cloning the repository)
   ```bash
   git --version
   ```

3. **pip** (Python package installer - usually comes with Python)
   ```bash
   pip --version
   ```

### System Requirements
- **OS**: Linux, macOS, or Windows
- **RAM**: Minimum 4GB (8GB recommended)
- **Storage**: At least 2GB free space
- **Internet**: Required for initial setup and email notifications

---

## 🚀 Installation Guide

Follow these steps carefully to set up the project:

### Step 1: Clone the Repository

```bash
git clone https://github.com/rakshith0110/Major-Project-PE-FL-DP-CKD.git
cd Major-Project-PE-FL-DP-CKD-main
```

### Step 2: Create Virtual Environment

**Why?** Virtual environments isolate project dependencies from your system Python.

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

**Verification**: You should see `(venv)` at the beginning of your terminal prompt.

### Step 4: Upgrade pip

```bash
pip install --upgrade pip
```

### Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all required packages including:
- PyTorch 2.3.1
- FastAPI 0.104.1
- Scikit-learn 1.5.1
- NumPy, Pandas, Matplotlib
- And other dependencies

### Step 6: Verify Installation

```bash
python -c "import torch, numpy, pandas, sklearn, fastapi; print('✅ Installation successful!')"
```

If you see "✅ Installation successful!", you're ready to proceed!

---

## 🎮 Running the Project

You have two options to run this project:

---

## Option 1: Web Application (Recommended)

The web application provides a user-friendly interface for both admins and clients.

### Quick Start

```bash
cd App
./run.sh
```

**Or manually:**

```bash
cd App
python3.11 -m uvicorn App.backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### Access the Application

Once the server starts, you'll see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Access Points:**
- **Landing Page**: http://localhost:8000
- **Admin Dashboard**: http://localhost:8000/admin
- **Client Dashboard**: http://localhost:8000/client
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Default Admin Credentials
- **Username**: `admin`
- **Password**: `admin123`

---

### Complete Web Application Workflow

#### 🔷 ADMIN WORKFLOW

**Step 1: Login**
1. Navigate to http://localhost:8000/admin
2. Enter credentials:
   - Username: `admin`
   - Password: `admin123`
3. Click "Login"

**Step 2: Initialize Global Model**
1. Go to "Initialize Model" section
2. Configure parameters:
   - **Epochs**: 20-50 (default: 30)
   - **Batch Size**: 32-128 (default: 64)
   - **Learning Rate**: 0.0001-0.01 (default: 0.001)
3. Click "Initialize Global Model"
4. Wait for completion (typically 2-5 minutes)
5. View training metrics and accuracy

**Step 3: Create Clients (Hospitals)**
1. Navigate to "Client Management"
2. Click "Create New Client"
3. Fill in details:
   - **Client Name**: e.g., "City Hospital"
   - **Email**: client@hospital.com
   - **Login Password**: For dashboard access
   - **Training Password**: For authorizing model training
   - **Description**: Optional details
4. Click "Create Client"
5. Credentials are automatically sent via email

**Step 4: Monitor Clients**
1. View client list with real-time status:
   - ✅ **Active**: Client is registered
   - 🔄 **Training**: Currently training model
   - 📤 **New Update Available**: Ready for aggregation
   - ⏸️ **Inactive**: Deactivated client
2. Check training metrics for each client
3. View training history and logs

**Step 5: Perform Aggregation**
1. Navigate to "Aggregation" section
2. System automatically detects clients with "New Update Available"
3. Review list of participating clients
4. Click "Aggregate Models"
5. Wait for FedAvg aggregation to complete
6. Updated global model is distributed to all clients
7. Client statuses reset to "Active"

---

#### 🔷 CLIENT WORKFLOW

**Step 1: Login**
1. Navigate to http://localhost:8000/client
2. Enter credentials received via email:
   - **Client Name**: Your hospital name
   - **Login Password**: Your login password
3. Click "Login"

**Step 2: Upload Dataset**
1. Click "Upload Dataset" button
2. Select your CSV file containing patient data
3. **Required columns** (must match exactly):
   - age, bp, sg, al, su, rbc, pc, pcc, ba, bgr, bu, sc, sod, pot, hemo, pcv, wc, rc, htn, dm, cad, appet, pe, ane, classification
4. File is validated and stored securely
5. Confirmation message appears

**Step 3: Configure Training Parameters**
1. Navigate to "Training Configuration"
2. Set hyperparameters:
   - **Epochs**: 10-100 (default: 20)
     - More epochs = Better accuracy but longer training
   - **Batch Size**: 8-256 (default: 32)
     - Larger batch = Faster but more memory
   - **Learning Rate**: 0.0001-0.1 (default: 0.001)
     - Controls how fast the model learns

3. Configure Differential Privacy:
   - **Noise Multiplier**: 0.1-10.0 (default: 1.0)
     - Higher = More privacy, slightly less accuracy
     - Recommended: 0.5-2.0
   - **Max Gradient Norm**: 0.1-10.0 (default: 1.0)
     - Gradient clipping threshold
     - Recommended: 0.5-2.0

**Step 4: Train Model**
1. Enter your **Training Password** (for authorization)
2. Click "Start Training"
3. Monitor progress:
   - Training loss (should decrease)
   - Validation accuracy (should increase)
   - Privacy budget (ε) - lower is better
4. Wait for completion (typically 5-15 minutes)
5. Status changes to "New Update Available"
6. Email notification sent to admin

**Step 5: Make Predictions**

**Single Prediction:**
1. Navigate to "Predictions" section
2. Enter patient data manually in the form
3. Click "Predict"
4. View result:
   - CKD Risk: Positive/Negative
   - Confidence Score: 0-100%

**Batch Predictions:**
1. Click "Upload Patient CSV"
2. Select CSV file with multiple patient records
3. Click "Predict Batch"
4. Wait for processing
5. Download results as CSV file
6. Results include predictions and confidence scores

**Step 6: View History**
1. **Training History**:
   - View all past training sessions
   - Check metrics and parameters used
   - Download training reports

2. **Prediction History**:
   - View all predictions made
   - Filter by date or result
   - Export to CSV

---

## Option 2: Command-Line FL Pipeline

For advanced users who want direct control over the FL process.

### Prerequisites
```bash
cd FL-DP-Healthcare
```

### Step 1: Initialize Global Model

Train the initial global model on a template dataset:

```bash
python3.11 init_global.py \
  --template_csv data/chronic_kidney_disease_5000.csv \
  --epochs 30 \
  --batch 64 \
  --lr 1e-3
```

**What this does:**
- Trains initial global model
- Creates baseline for federated learning
- Saves model to `server/global_round0.pt`
- Generates evaluation metrics and visualizations

**Output files:**
- `server/global_round0.pt` - Initial global model
- `server/metrics_initial.json` - Performance metrics
- `server/val_initial_*.png` - Visualization plots

---

### Step 2: Train Client Models

Each hospital trains on their local data independently.

**Client 1 (Hospital A):**
```bash
python3.11 client_train_once.py \
  --client_name Client1 \
  --client_dir client1 \
  --client_csv client1/dataset/client1_ckd.csv \
  --premodel_ckpt client1/premodel_client1.pt \
  --template_csv data/chronic_kidney_disease_5000.csv
```

**Client 2 (Hospital B):**
```bash
python3.11 client_train_once.py \
  --client_name Client2 \
  --client_dir client2 \
  --client_csv client2/dataset/client2_ckd.csv \
  --premodel_ckpt client2/premodel_client2.pt \
  --template_csv data/chronic_kidney_disease_5000.csv
```

**Client 3 (Hospital C):**
```bash
python3.11 client_train_once.py \
  --client_name Client3 \
  --client_dir client3 \
  --client_csv client3/dataset/client3_ckd.csv \
  --premodel_ckpt client3/premodel_client3.pt \
  --template_csv data/chronic_kidney_disease_5000.csv
```

**What this does:**
- Loads global model as starting point
- Trains on local hospital data
- Applies Differential Privacy (gradient clipping + noise)
- Calculates weight updates (delta)
- Saves delta for aggregation

**Output files per client:**
- `client*/delta_final.pt` - Weight updates (DP-protected)
- `client*/local_model.pt` - Local trained model
- `client*/metrics_final.json` - Training metrics
- `client*/confusion_*.png` - Evaluation plots

---

### Step 3: Federated Aggregation

Aggregate all client updates using FedAvg algorithm:

```bash
python3.11 aggregate_once.py \
  --delta1 client1/delta_final.pt \
  --delta2 client2/delta_final.pt \
  --delta3 client3/delta_final.pt \
  --template_csv data/chronic_kidney_disease_5000.csv
```

**What this does:**
- Loads weight updates from all clients
- Performs weighted averaging (FedAvg)
- Updates global model
- Evaluates new global model
- Saves updated model for next round

**Output files:**
- `server/global_final.pt` - Updated global model
- `server/metrics_final.json` - Aggregated metrics
- `server/confusion_*.png` - Global model evaluation

---

### Step 4: Make Predictions

Use the global model to predict CKD for new patients:

**Single patient prediction:**
```bash
python3.11 predict_from_patient_data.py \
  --client_name Client1 \
  --client_dir client1 \
  --template_csv data/chronic_kidney_disease_5000.csv \
  --patient_csv data/patient_data.csv \
  --row_index 0
```

**All patients in CSV:**
```bash
python3.11 predict_from_patient_data.py \
  --client_name Client1 \
  --client_dir client1 \
  --template_csv data/chronic_kidney_disease_5000.csv \
  --patient_csv data/patient_data.csv \
  --all_rows
```

**Output:**
- Predictions printed to console
- Results saved to `client*/new_patients_predictions_last_batch.json`

---

### Step 5: Repeat for Multiple Rounds (Optional)

For improved accuracy, repeat steps 2-3 multiple times:

```bash
# Round 2
python3.11 client_train_once.py --client_name Client1 ...
python3.11 client_train_once.py --client_name Client2 ...
python3.11 client_train_once.py --client_name Client3 ...
python3.11 aggregate_once.py --delta1 ... --delta2 ... --delta3 ...

# Round 3
# Repeat...
```

---

## 📖 Usage Guides

### Dataset Format

Your CSV file must contain these exact columns:

```csv
age,bp,sg,al,su,rbc,pc,pcc,ba,bgr,bu,sc,sod,pot,hemo,pcv,wc,rc,htn,dm,cad,appet,pe,ane,classification
48,80,1.020,1,0,normal,normal,notpresent,notpresent,121,36,1.2,138,4.5,15.4,44,7800,5.2,yes,yes,no,good,no,no,ckd
```

**Column Descriptions:**
- `age`: Patient age
- `bp`: Blood pressure
- `sg`: Specific gravity
- `al`: Albumin
- `su`: Sugar
- `rbc`: Red blood cells
- `pc`: Pus cell
- `pcc`: Pus cell clumps
- `ba`: Bacteria
- `bgr`: Blood glucose random
- `bu`: Blood urea
- `sc`: Serum creatinine
- `sod`: Sodium
- `pot`: Potassium
- `hemo`: Hemoglobin
- `pcv`: Packed cell volume
- `wc`: White blood cell count
- `rc`: Red blood cell count
- `htn`: Hypertension
- `dm`: Diabetes mellitus
- `cad`: Coronary artery disease
- `appet`: Appetite
- `pe`: Pedal edema
- `ane`: Anemia
- `classification`: ckd or notckd

---

### Email Configuration

To enable email notifications, update `App/backend/services/email_service.py`:

```python
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "your-email@gmail.com"
SMTP_PASSWORD = "your-app-password"  # Use App Password for Gmail
```

**For Gmail:**
1. Enable 2-Factor Authentication
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use the generated password in the config

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

**Interactive API Documentation**: http://localhost:8000/docs

---

## 🐛 Troubleshooting

### Common Issues and Solutions

#### 1. Port Already in Use

**Error**: `Address already in use`

**Solution:**
```bash
# Linux/Mac
lsof -ti:8000 | xargs kill -9

# Windows (find PID first)
netstat -ano | findstr :8000
# Then kill the process using Task Manager or:
taskkill /PID <PID> /F
```

#### 2. Module Import Errors

**Error**: `ModuleNotFoundError: No module named 'App'`

**Solution:**
```bash
# Ensure you're in the correct directory
cd /path/to/Major-Project-PE-FL-DP-CKD-main

# Set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or on Windows
set PYTHONPATH=%PYTHONPATH%;%CD%
```

#### 3. Virtual Environment Not Activated

**Error**: Packages not found or wrong Python version

**Solution:**
```bash
# Check if activated (should see (venv))
which python  # Should point to venv/bin/python

# Reactivate
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

#### 4. Database Issues

**Error**: Database locked or corrupted

**Solution:**
```bash
cd App
# Backup existing database
mv federated_ckd.db federated_ckd.db.backup

# Reinitialize
python3.11 -c "from App.backend.core.database import init_database; init_database()"
```

#### 5. CUDA/GPU Issues

**Error**: CUDA out of memory or GPU not available

**Solution:**
```bash
# Force CPU usage
export CUDA_VISIBLE_DEVICES=""

# Or in Python code, the system automatically falls back to CPU
```

#### 6. Permission Denied on run.sh

**Error**: `Permission denied: ./run.sh`

**Solution:**
```bash
chmod +x App/run.sh
./run.sh
```

#### 7. Email Sending Fails

**Error**: Email notifications not working

**Solution:**
1. Check SMTP configuration in `App/backend/services/email_service.py`
2. For Gmail, use App Password (not regular password)
3. Enable "Less secure app access" or use App Password
4. Check firewall settings

---

## 🔐 Security Best Practices

### For Production Deployment

1. **Change Default Credentials**
   ```python
   # Update in App/backend/core/database.py
   admin_password = "your-strong-password"
   ```

2. **Use Environment Variables**
   ```bash
   export SECRET_KEY="your-secret-key"
   export SMTP_PASSWORD="your-smtp-password"
   ```

3. **Enable HTTPS**
   - Use reverse proxy (Nginx/Apache)
   - Obtain SSL certificate (Let's Encrypt)

4. **Database Security**
   - Use PostgreSQL instead of SQLite for production
   - Enable database encryption
   - Regular backups

5. **Rate Limiting**
   - Implement API rate limiting
   - Prevent brute force attacks

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

## 🎯 Quick Reference Card

### Essential Commands

```bash
# Setup
python3.11 -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt

# Run Web App
cd App
./run.sh
# Access: http://localhost:8000

# Run FL Pipeline
cd FL-DP-Healthcare
python3.11 init_global.py --template_csv data/chronic_kidney_disease_5000.csv --epochs 30
python3.11 client_train_once.py --client_name Client1 --client_dir client1 --client_csv client1/dataset/client1_ckd.csv --premodel_ckpt client1/premodel_client1.pt --template_csv data/chronic_kidney_disease_5000.csv
python3.11 aggregate_once.py --delta1 client1/delta_final.pt --delta2 client2/delta_final.pt --delta3 client3/delta_final.pt --template_csv data/chronic_kidney_disease_5000.csv

# Test API
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/admin/login -H "Content-Type: application/json" -d '{"username":"admin","password":"admin123"}'
```

### Default Credentials
- **Admin**: username=`admin`, password=`admin123`
- **Clients**: Created by admin, credentials sent via email

### Key URLs
- Landing: http://localhost:8000
- Admin: http://localhost:8000/admin
- Client: http://localhost:8000/client
- API Docs: http://localhost:8000/docs

---

## 🚀 Project Status

- ✅ **Backend**: 100% Complete
- ✅ **FL Pipeline**: 100% Complete
- ✅ **API**: 100% Complete
- ✅ **Database**: 100% Complete
- ✅ **Authentication**: 100% Complete
- ✅ **Privacy (DP)**: 100% Complete
- 🔄 **Frontend**: In Progress
- ✅ **Documentation**: Complete

---

**Built with ❤️ for Privacy-Preserving Healthcare AI**

*Empowering collaborative medical research while protecting patient privacy*

---

*Last Updated: April 2026*
