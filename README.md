# 🩺 Privacy-Enhanced Federated Learning for Chronic Kidney Disease (CKD)

A complete **Federated Learning (FL) pipeline with Differential Privacy (DP)** for predicting Chronic Kidney Disease while preserving patient privacy.

This project demonstrates how multiple hospitals (clients) can collaboratively train a machine learning model without sharing raw patient data.

---
## Team Members:
1. Rakshith PR - NNM23CS507
2. Yathish - NNM23CS517
3. Muskan
4. Adaline

## Mentor: 
Mr. Pawan Hegde

## Dept & Collage: 
CSE, NMAM Institute Of Technology,Nitte

---

## 🚀 Features

✔ Global centralized model initialization  
✔ Privacy-preserving client training (Differential Privacy)  
✔ Federated Aggregation using FedAvg  
✔ Secure prediction on shared patient data  
✔ Automatic visualization and metrics generation  
✔ High accuracy CKD prediction  

---

## 🛠 Technologies Used

- Python 3.9+
- PyTorch 2.x
- Scikit-learn
- NumPy
- Pandas
- Matplotlib

---

## 📂 Project Structure

<img width="395" height="732" alt="image" src="https://github.com/user-attachments/assets/24527bd5-84d9-4898-b6ab-bdefd6f4b699" />
<br>

----------------------------
# 🚀 Project Setup & Execution Guide

---

## ✅ Step 1 — Install Python 3.11

Download Python 3.11 from:

https://www.python.org/downloads/

During installation:
- ✔ Enable **Add Python to PATH**
- ✔ Click **Install Now**

Verify installation:

```bash
python3.11 --version
pip3.11 --version
```

**Note:** This project requires Python 3.11 specifically.

---

## ✅ Step 2 — Download Project

Clone from GitHub:

```bash
git clone https://github.com/rakshith0110/Major-Project-PE-FL-DP-CKD.git
```
```bash
cd Major-Project-PE-FL-DP-CKD/FL-DP-Healthcare
```

Or download ZIP and extract the folder.

FL-DP-Healthcare (open this folder in VS code)

---

## ✅ Step 3 — Create Virtual Environment

Inside project folder:

```bash
python3.11 -m venv venv
```

---

## ✅ Step 4 — Activate Virtual Environment

### Windows

```powershell
venv\Scripts\activate
```

### Linux / Mac

```bash
source venv/bin/activate
```

You should see:

```
(venv)
```

---

## ✅ Step 5 — Install Project Dependencies

```bash
pip install -r requirements.txt
```

Wait until installation completes.

---

## ✅ Step 6 — Verify Installation

```bash
python3.11 -c "import torch, numpy, pandas, sklearn, matplotlib; print('Environment ready')"
```

If no error → setup successful ✅

---

## ▶️ Step 7 — Run the Project Pipeline

---

### ▶️ Step 7.1 — Global Model Training

```bash
python3.11 init_global.py --template_csv data/chronic_kidney_disease_5000.csv --epochs 30 --batch 64 --lr 1e-3
```

---

### ▶️ Step 7.2 — Client Training

Client 1:

```bash
python3.11 client_train_once.py --client_name Client1 --client_dir client1 --client_csv client1/dataset/client1_ckd.csv --premodel_ckpt client1/premodel_client1.pt --template_csv data/chronic_kidney_disease_5000.csv
```

Client 2:

```bash
python3.11 client_train_once.py --client_name Client2 --client_dir client2 --client_csv client2/dataset/client2_ckd.csv --premodel_ckpt client2/premodel_client2.pt --template_csv data/chronic_kidney_disease_5000.csv
```

Client 3:

```bash
python3.11 client_train_once.py --client_name Client3 --client_dir client3 --client_csv client3/dataset/client3_ckd.csv --premodel_ckpt client3/premodel_client3.pt --template_csv data/chronic_kidney_disease_5000.csv
```

---

### ▶️ Step 7.3 — Federated Aggregation

```bash
python3.11 aggregate_once.py --delta1 client1/delta_final.pt --delta2 client2/delta_final.pt --delta3 client3/delta_final.pt --template_csv data/chronic_kidney_disease_5000.csv
```

---

### ▶️ Step 7.4 — Prediction

```bash
python3.11 predict_from_patient_data.py --client_name Client2 --client_dir client2 --template_csv data/chronic_kidney_disease_5000.csv --patient_csv data/patient_data.csv
```

Optional:
- Predict one row → `--row_index N`
- Predict all rows → `--all_rows`

---

## 🚪 Step 8 — Deactivate Environment

```bash
deactivate
```

---

outputs:
```
  server:
    - global_final.pt
    - metrics_final.json
    - confusion plots
    - ROC curves
    - calibration plots

  clients:
    - local_model.pt
    - delta_final.pt
    - metrics_final.json
    - new_patients_records.csv
```
privacy:
```
  method: "Differential Privacy"
  techniques:
    - Gradient clipping
    - Gaussian noise injection
  tuning_parameters:
    - max_grad_norm
    - noise_multiplier
```

notes:
  - Template dataset defines feature schema and scaling parameters.
  - All datasets must follow the same column structure.
  - Visualizations are generated automatically.
  - Project is suitable for academic demonstration and evaluation.

