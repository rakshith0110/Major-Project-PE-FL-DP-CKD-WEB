"""
Machine Learning service - Integrates existing FL-DP scripts
"""
import os
import sys
import json
import torch
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Tuple, Optional, Callable
from datetime import datetime

# Add FL-DP-Healthcare to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../FL-DP-Healthcare'))

from data_prep import preprocess_split_single, preprocess_client_with_template, load_csv, _drop_ids, _impute, _zscore_cap, TARGET_COL
from models import build_model
from dp import clip_gradients, add_gaussian_noise
from eval_utils import metrics_from_logits
from viz import save_confusion_plot, save_roc_plot, save_calibration_plot
from torch.utils.data import TensorDataset, DataLoader
import torch.nn as nn

from App.configs.config import settings


class MLService:
    """Service for ML operations"""
    
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.template_csv = settings.TEMPLATE_CSV
        self.server_dir = settings.SERVER_DIR
        self.clients_base_dir = settings.CLIENTS_BASE_DIR
    
    def _ensure_dirs(self, *dirs):
        """Ensure directories exist"""
        for d in dirs:
            os.makedirs(d, exist_ok=True)
    
    def _evaluate_and_visualize(self, model, X, y, out_prefix: str) -> Dict:
        """Evaluate model and generate visualizations"""
        dl = DataLoader(
            TensorDataset(torch.tensor(X, dtype=torch.float32),
                         torch.tensor(y, dtype=torch.long)),
            batch_size=1024
        )
        
        outs = []
        ys = []
        model.eval()
        
        with torch.no_grad():
            for xb, yb in dl:
                xb = xb.to(self.device)
                logits = model(xb)
                outs.append(logits.cpu().numpy().ravel())
                ys.append(yb.numpy())
        
        logits = np.concatenate(outs)
        ytrue = np.concatenate(ys)
        prob = 1 / (1 + np.exp(-logits))
        
        metrics = metrics_from_logits(logits, ytrue)
        
        # Save visualizations
        save_confusion_plot(ytrue, (prob >= 0.5).astype(int), f"{out_prefix}_confusion.png")
        save_roc_plot(ytrue, prob, f"{out_prefix}_roc.png")
        save_calibration_plot(ytrue, prob, f"{out_prefix}_calibration.png")
        
        return metrics
    
    def train_global_model(
        self,
        epochs: int = 30,
        batch_size: int = 64,
        learning_rate: float = 0.001,
        progress_callback: Optional[Callable[[str, int], None]] = None
    ) -> Dict:
        """Train initial global model"""
        try:
            self._ensure_dirs(self.server_dir)
            
            if progress_callback:
                progress_callback("Preprocessing data...", 5)
            
            # Preprocess data
            Xtr, ytr, Xv, yv, Xte, yte, scaler = preprocess_split_single(self.template_csv)
            
            if progress_callback:
                progress_callback("Building model...", 10)
            
            # Build model
            model = build_model(Xtr.shape[1]).to(self.device)
            opt = torch.optim.Adam(model.parameters(), lr=learning_rate, weight_decay=1e-4)
            loss_fn = nn.BCEWithLogitsLoss()
            
            best_auc = -1.0
            
            # Training loop
            for epoch in range(epochs):
                if progress_callback:
                    progress = 10 + int((epoch / epochs) * 70)
                    progress_callback(f"Training epoch {epoch + 1}/{epochs}...", progress)
                
                model.train()
                dl = DataLoader(
                    TensorDataset(torch.tensor(Xtr, dtype=torch.float32),
                                 torch.tensor(ytr, dtype=torch.long)),
                    batch_size=batch_size,
                    shuffle=True
                )
                
                for xb, yb in dl:
                    xb = xb.to(self.device)
                    yb = yb.to(self.device).float().view(-1, 1)
                    
                    opt.zero_grad()
                    logits = model(xb)
                    loss = loss_fn(logits, yb)
                    loss.backward()
                    opt.step()
                
                # Validate
                vm = self._evaluate_and_visualize(
                    model, Xv, yv,
                    out_prefix=os.path.join(self.server_dir, "val_initial")
                )
                
                if vm["auc"] > best_auc:
                    best_auc = vm["auc"]
                    torch.save({
                        "state_dict": model.state_dict(),
                        "input_dim": Xtr.shape[1],
                        "scaler_mean": scaler.mean_.tolist(),
                        "scaler_scale": scaler.scale_.tolist()
                    }, os.path.join(self.server_dir, "global_round0.pt"))
            
            if progress_callback:
                progress_callback("Evaluating model...", 85)
            
            # Final evaluation
            ckpt = torch.load(os.path.join(self.server_dir, "global_round0.pt"), map_location=self.device)
            model.load_state_dict(ckpt["state_dict"])
            
            if progress_callback:
                progress_callback("Evaluating on validation set...", 90)
            
            m_val = self._evaluate_and_visualize(
                model, Xv, yv,
                out_prefix=os.path.join(self.server_dir, "val_initial")
            )
            
            if progress_callback:
                progress_callback("Evaluating on test set...", 95)
            
            m_test = self._evaluate_and_visualize(
                model, Xte, yte,
                out_prefix=os.path.join(self.server_dir, "test_initial")
            )
            
            if progress_callback:
                progress_callback("Saving metrics...", 98)
            
            # Save metrics
            metrics = {"val": m_val, "test": m_test}
            with open(os.path.join(self.server_dir, "metrics_initial.json"), "w") as f:
                json.dump(metrics, f, indent=2)
            
            if progress_callback:
                progress_callback("Training completed!", 100)
            
            return {
                "status": "success",
                "metrics": metrics,
                "model_path": os.path.join(self.server_dir, "global_round0.pt")
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def train_client_model(
        self,
        client_name: str,
        client_dir: str,
        client_csv: str,
        local_epochs: int = 10,
        batch_size: int = 64,
        learning_rate: float = 0.001,
        max_grad_norm: float = 1.0,
        noise_multiplier: float = 0.8,
        progress_callback: Optional[Callable[[str, int], None]] = None
    ) -> Dict:
        """Train client model with differential privacy"""
        try:
            self._ensure_dirs(client_dir)
            
            if progress_callback:
                progress_callback("Initializing client training...", 5)
            
            premodel_path = os.path.join(client_dir, f"premodel_{client_name}.pt")
            
            # Check if premodel exists
            if not os.path.exists(premodel_path):
                if progress_callback:
                    progress_callback("Loading global model...", 10)
                # Copy from server
                import shutil
                server_model = os.path.join(self.server_dir, "global_round0.pt")
                if os.path.exists(server_model):
                    shutil.copyfile(server_model, premodel_path)
                else:
                    return {"status": "error", "error": "Global model not found. Train global model first."}
            
            if progress_callback:
                progress_callback("Loading model template...", 15)
            
            # Load template from global model
            ckpt = torch.load(premodel_path, map_location="cpu")
            mean = np.array(ckpt["scaler_mean"])
            scale = np.array(ckpt["scaler_scale"])
            
            class Scaler:
                def transform(self, X):
                    return (X - mean) / scale
            
            df = load_csv(self.template_csv)
            df = _drop_ids(_impute(_zscore_cap(df, exclude=[TARGET_COL])))
            feature_cols = [c for c in df.columns if c != TARGET_COL]
            
            scaler = Scaler()
            input_dim = ckpt["input_dim"]
            state = ckpt["state_dict"]
            
            if progress_callback:
                progress_callback("Preprocessing client data...", 20)
            
            # Load client dataset
            Xc, yc = preprocess_client_with_template(client_csv, feature_cols, scaler)
            
            if progress_callback:
                progress_callback("Building client model...", 25)
            
            # Build model
            model = build_model(input_dim).to(self.device)
            model.load_state_dict(state)
            
            ds = TensorDataset(
                torch.tensor(Xc, dtype=torch.float32),
                torch.tensor(yc, dtype=torch.long)
            )
            dl = DataLoader(ds, batch_size=batch_size, shuffle=True)
            
            loss_fn = nn.BCEWithLogitsLoss()
            opt = torch.optim.Adam(model.parameters(), lr=learning_rate, weight_decay=1e-4)
            
            global_state = {k: v.clone().detach().cpu() for k, v in model.state_dict().items()}
            
            # Training with DP
            model.train()
            for epoch in range(local_epochs):
                if progress_callback:
                    progress = 25 + int((epoch / local_epochs) * 50)
                    progress_callback(f"Training with DP - Epoch {epoch + 1}/{local_epochs}...", progress)
                
                for xb, yb in dl:
                    xb = xb.to(self.device)
                    yb = yb.to(self.device).float().view(-1, 1)
                    
                    opt.zero_grad()
                    logits = model(xb)
                    loss = loss_fn(logits, yb)
                    loss.backward()
                    
                    clip_gradients(model, max_grad_norm)
                    add_gaussian_noise(model, noise_multiplier, max_grad_norm, device=self.device)
                    
                    opt.step()
            
            if progress_callback:
                progress_callback("Saving local model...", 80)
            
            # Save local model
            torch.save(
                {"state_dict": model.state_dict(), "input_dim": input_dim},
                os.path.join(client_dir, "local_model.pt")
            )
            
            if progress_callback:
                progress_callback("Computing model delta...", 85)
            
            # Compute delta
            delta = {}
            with torch.no_grad():
                for k, v in model.state_dict().items():
                    delta[k] = (v.cpu() - global_state[k])
            
            torch.save(
                {"delta": delta, "n": len(ds)},
                os.path.join(client_dir, "delta_final.pt")
            )
            
            if progress_callback:
                progress_callback("Validating model...", 90)
            
            # Validation
            Xtr, ytr, Xv, yv, Xte, yte, _ = preprocess_split_single(self.template_csv)
            m_val = self._evaluate_and_visualize(
                model, Xv, yv,
                out_prefix=os.path.join(client_dir, "confusion")
            )
            
            if progress_callback:
                progress_callback("Saving metrics...", 98)
            
            metrics = {"val": m_val, "n_samples": len(ds)}
            with open(os.path.join(client_dir, "metrics_final.json"), "w") as f:
                json.dump(metrics, f, indent=2)
            
            if progress_callback:
                progress_callback("Client training completed!", 100)
            
            return {
                "status": "success",
                "metrics": metrics,
                "client_name": client_name
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def aggregate_models(self, client_dirs: list, progress_callback: Optional[Callable[[str, int], None]] = None) -> Dict:
        """Federated aggregation using FedAvg"""
        try:
            if progress_callback:
                progress_callback("Loading global model...", 5)
            
            # Load initial global model
            ckpt = torch.load(
                os.path.join(self.server_dir, "global_round0.pt"),
                map_location=self.device
            )
            state = ckpt["state_dict"]
            input_dim = ckpt["input_dim"]
            
            if progress_callback:
                progress_callback("Loading client deltas...", 15)
            
            # Load client deltas
            deltas = []
            weights = []
            
            for i, client_dir in enumerate(client_dirs):
                if progress_callback:
                    progress = 15 + int((i / len(client_dirs)) * 30)
                    progress_callback(f"Loading delta from client {i + 1}/{len(client_dirs)}...", progress)
                
                delta_path = os.path.join(client_dir, "delta_final.pt")
                if not os.path.exists(delta_path):
                    continue
                
                obj = torch.load(delta_path, map_location="cpu")
                deltas.append(obj["delta"])
                weights.append(obj["n"])
            
            if not deltas:
                return {"status": "error", "error": "No client deltas found"}
            
            if progress_callback:
                progress_callback("Performing federated averaging...", 50)
            
            # Federated averaging
            total = sum(weights)
            keys = list(deltas[0].keys())
            agg = {}
            
            for i, k in enumerate(keys):
                if progress_callback and i % 5 == 0:
                    progress = 50 + int((i / len(keys)) * 20)
                    progress_callback(f"Aggregating layer {i + 1}/{len(keys)}...", progress)
                agg[k] = sum(d[k] * (w / total) for d, w in zip(deltas, weights))
            
            if progress_callback:
                progress_callback("Applying aggregated updates...", 75)
            
            # Apply delta to state
            for k in state:
                state[k] += agg[k]
            
            if progress_callback:
                progress_callback("Saving aggregated model...", 80)
            
            # Save updated global model
            torch.save(
                {
                    "state_dict": state,
                    "input_dim": input_dim,
                    "scaler_mean": ckpt.get("scaler_mean"),
                    "scaler_scale": ckpt.get("scaler_scale"),
                },
                os.path.join(self.server_dir, "global_final.pt")
            )
            
            if progress_callback:
                progress_callback("Evaluating aggregated model...", 85)
            
            # Evaluate
            Xtr, ytr, Xv, yv, Xte, yte, _ = preprocess_split_single(self.template_csv)
            model = build_model(input_dim).to(self.device)
            model.load_state_dict(state)
            
            m_val = self._evaluate_and_visualize(
                model, Xv, yv,
                out_prefix=os.path.join(self.server_dir, "confusion")
            )
            
            if progress_callback:
                progress_callback("Saving metrics...", 95)
            
            metrics = {"val": m_val}
            with open(os.path.join(self.server_dir, "metrics_final.json"), "w") as f:
                json.dump(metrics, f, indent=2)
            
            if progress_callback:
                progress_callback("Aggregation completed!", 100)
            
            return {
                "status": "success",
                "metrics": metrics,
                "num_clients": len(deltas)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def predict(
        self,
        client_name: str,
        client_dir: str,
        patient_data: Dict
    ) -> Dict:
        """Make prediction on patient data"""
        try:
            premodel_path = os.path.join(client_dir, f"premodel_{client_name}.pt")
            
            if not os.path.exists(premodel_path):
                return {"status": "error", "error": "Model not found"}
            
            # Load template
            ckpt = torch.load(premodel_path, map_location="cpu")
            mean = np.array(ckpt["scaler_mean"])
            scale = np.array(ckpt["scaler_scale"])
            
            class Scaler:
                def transform(self, X):
                    return (X - mean) / scale
            
            df = load_csv(self.template_csv)
            df = _drop_ids(_impute(_zscore_cap(df, exclude=[TARGET_COL])))
            feature_cols = [c for c in df.columns if c != TARGET_COL]
            
            # Prepare patient data
            df_patient = pd.DataFrame([patient_data])
            missing = [c for c in feature_cols if c not in df_patient.columns]
            if missing:
                return {"status": "error", "error": f"Missing features: {missing}"}
            
            X = df_patient[feature_cols].values.astype(float)
            X = Scaler().transform(X)
            
            # Load model and predict
            model = build_model(ckpt["input_dim"]).to(self.device)
            model.load_state_dict(ckpt["state_dict"])
            model.eval()
            
            with torch.no_grad():
                logits = model(torch.tensor(X, dtype=torch.float32).to(self.device)).cpu().numpy().ravel()
                prob = 1 / (1 + np.exp(-logits))
                y_pred = (prob >= 0.5).astype(int)
            
            label_text = ["NO", "YES"]
            
            return {
                "status": "success",
                "prediction_class": int(y_pred[0]),
                "prediction_label": label_text[int(y_pred[0])],
                "prediction_probability": float(prob[0]),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }


# Singleton instance
ml_service = MLService()

# Made with Bob
