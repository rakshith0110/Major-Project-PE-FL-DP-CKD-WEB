"""
Federated Learning Service - Simplified integration with existing FL-DP-Healthcare code
"""
import sys
import os
import torch
import torch.nn as nn
import json
import time
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Add FL-DP-Healthcare to path
FL_DP_PATH = Path(__file__).parent.parent.parent.parent / "FL-DP-Healthcare"
sys.path.insert(0, str(FL_DP_PATH))

from models import MLP, build_model
from data_prep import preprocess_split_single, preprocess_client_with_template
from dp import clip_gradients, add_gaussian_noise
from eval_utils import metrics_from_logits

from backend.core.database import get_db_connection

class FederatedLearningService:
    """Service for managing federated learning operations"""
    
    def __init__(self):
        self.models_dir = Path(__file__).parent.parent.parent / "models"
        self.uploads_dir = Path(__file__).parent.parent.parent / "uploads"
        self.models_dir.mkdir(exist_ok=True)
        self.uploads_dir.mkdir(exist_ok=True)
    
    def resolve_dataset_path(self, dataset_path: str) -> Path:
        """Resolve dataset path against project root and app root."""
        candidate = Path(dataset_path)

        if candidate.is_absolute() and candidate.exists():
            return candidate

        project_root = Path(__file__).parent.parent.parent.parent
        app_root = Path(__file__).parent.parent.parent

        possible_paths = [
            candidate,
            project_root / candidate,
            app_root / candidate,
            project_root / "Datasets" / candidate.name,
        ]

        for path in possible_paths:
            if path.exists():
                return path.resolve()

        raise FileNotFoundError(f"Dataset file not found: {dataset_path}")

    def get_client_dir(self, client_id: int) -> Path:
        """Get client-specific directory"""
        client_dir = self.models_dir / f"client_{client_id}"
        client_dir.mkdir(exist_ok=True)
        return client_dir
    
    def get_global_model_path(self) -> Path:
        """Get global model path"""
        return self.models_dir / "global_model.pt"

    def get_model_input_dim(self, model_path: Path) -> int:
        """Infer model input dimension from saved state dict."""
        state_dict = torch.load(str(model_path), map_location='cpu')
        first_weight = state_dict.get("net.0.weight")
        if first_weight is None:
            raise ValueError(f"Unable to infer input dimension from model: {model_path}")
        return int(first_weight.shape[1])
    
    def save_model(self, model: nn.Module, path: str):
        """Save model to file"""
        torch.save(model.state_dict(), path)
    
    def load_model(self, model: nn.Module, path: str) -> nn.Module:
        """Load model from file"""
        model.load_state_dict(torch.load(path, map_location='cpu'))
        return model
    
    def evaluate_model(self, model: nn.Module, X: np.ndarray, y: np.ndarray, device) -> Dict:
        """Evaluate model and return metrics"""
        model.eval()
        with torch.no_grad():
            X_tensor = torch.FloatTensor(X).to(device)
            logits = model(X_tensor).cpu().numpy().flatten()
        
        metrics = metrics_from_logits(logits, y)
        # Add loss calculation
        probs = 1/(1+np.exp(-logits))
        loss = -np.mean(y * np.log(probs + 1e-8) + (1-y) * np.log(1-probs + 1e-8))
        metrics['loss'] = float(loss)
        
        return metrics
    
    def initialize_global_model(self, template_csv: str, epochs: int = 30, 
                               batch_size: int = 64, lr: float = 0.001) -> Dict:
        """Initialize global model (Admin only)"""
        try:
            # Load and prepare data
            resolved_template_csv = self.resolve_dataset_path(template_csv)
            X_train, y_train, X_val, y_val, X_test, y_test, scaler = \
                preprocess_split_single(str(resolved_template_csv))
            
            input_dim = X_train.shape[1]
            model = build_model(input_dim)
            
            # Train initial global model
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            model = model.to(device)
            
            criterion = nn.BCEWithLogitsLoss()
            optimizer = torch.optim.Adam(model.parameters(), lr=lr)
            
            # Training loop
            train_dataset = torch.utils.data.TensorDataset(
                torch.FloatTensor(X_train), 
                torch.FloatTensor(y_train)
            )
            train_loader = torch.utils.data.DataLoader(
                train_dataset, 
                batch_size=batch_size, 
                shuffle=True
            )
            
            model.train()
            for epoch in range(epochs):
                for batch_X, batch_y in train_loader:
                    batch_X, batch_y = batch_X.to(device), batch_y.to(device)
                    
                    optimizer.zero_grad()
                    outputs = model(batch_X).squeeze()
                    loss = criterion(outputs, batch_y)
                    loss.backward()
                    optimizer.step()
            
            # Evaluate
            val_metrics = self.evaluate_model(model, X_val, y_val, device)
            
            # Save global model
            global_model_path = self.get_global_model_path()
            self.save_model(model, str(global_model_path))
            
            # Save scaler for later use
            scaler_path = self.models_dir / "scaler.pkl"
            import pickle
            with open(scaler_path, 'wb') as f:
                pickle.dump(scaler, f)
            
            # Update database
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE global_model 
                SET model_path = ?, accuracy = ?, loss = ?, 
                    metrics_json = ?, created_at = CURRENT_TIMESTAMP
                WHERE round_number = 0
            """, (
                str(global_model_path),
                val_metrics.get('accuracy', 0.0),
                val_metrics.get('loss', 0.0),
                json.dumps(val_metrics)
            ))
            conn.commit()
            conn.close()
            
            return {
                "status": "success",
                "message": "Global model initialized successfully",
                "accuracy": val_metrics.get('accuracy', 0.0),
                "loss": val_metrics.get('loss', 0.0),
                "model_path": str(global_model_path)
            }
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "message": f"Failed to initialize global model: {str(e)}"
            }
    
    def train_client_model(self, client_id: int, dataset_path: str, 
                          config: Dict, template_csv: str) -> Dict:
        """Train client's local model with DP"""
        try:
            start_time = time.time()
            
            # Load client data
            resolved_dataset_path = self.resolve_dataset_path(dataset_path)
            X_train, y_train, X_val, y_val, X_test, y_test, scaler = \
                preprocess_split_single(str(resolved_dataset_path))
            
            # Load global model as starting point
            global_model_path = self.get_global_model_path()
            if not global_model_path.exists():
                return {
                    "status": "error",
                    "message": "Global model not initialized. Contact admin."
                }
            
            input_dim = X_train.shape[1]
            model = build_model(input_dim)
            model = self.load_model(model, str(global_model_path))
            
            # Store pre-training weights
            pre_training_state = {k: v.clone() for k, v in model.state_dict().items()}
            
            # Training
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            model = model.to(device)
            
            criterion = nn.BCEWithLogitsLoss()
            optimizer = torch.optim.Adam(model.parameters(), lr=config['learning_rate'])
            
            train_dataset = torch.utils.data.TensorDataset(
                torch.FloatTensor(X_train), 
                torch.FloatTensor(y_train)
            )
            train_loader = torch.utils.data.DataLoader(
                train_dataset, 
                batch_size=config['batch_size'], 
                shuffle=True
            )
            
            # Training loop with DP
            model.train()
            for epoch in range(config['epochs']):
                for batch_X, batch_y in train_loader:
                    batch_X, batch_y = batch_X.to(device), batch_y.to(device)
                    
                    optimizer.zero_grad()
                    outputs = model(batch_X).squeeze()
                    loss = criterion(outputs, batch_y)
                    loss.backward()
                    
                    # Apply DP: Gradient clipping
                    clip_gradients(model, config['max_grad_norm'])
                    
                    # Apply DP: Add Gaussian noise
                    add_gaussian_noise(
                        model, 
                        config['noise_multiplier'],
                        config['max_grad_norm'],
                        device
                    )
                    
                    optimizer.step()
            
            # Evaluate
            val_metrics = self.evaluate_model(model, X_val, y_val, device)
            
            # Calculate delta (weight updates)
            post_training_state = model.state_dict()
            delta = {}
            for key in post_training_state:
                delta[key] = post_training_state[key].cpu() - pre_training_state[key].cpu()
            
            # Save local model and delta
            client_dir = self.get_client_dir(client_id)
            local_model_path = client_dir / "local_model.pt"
            delta_path = client_dir / "delta.pt"
            
            self.save_model(model, str(local_model_path))
            torch.save(delta, str(delta_path))
            
            training_time = time.time() - start_time
            
            # Update database
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get current global model round number
            cursor.execute("SELECT round_number FROM global_model ORDER BY round_number DESC LIMIT 1")
            global_model_row = cursor.fetchone()
            current_round = global_model_row["round_number"] if global_model_row else 0
            
            # Update client status and increment total_records_trained
            cursor.execute("""
                UPDATE clients
                SET last_trained_time = CURRENT_TIMESTAMP,
                    update_status = 'New Update Available',
                    total_records_trained = total_records_trained + ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (len(X_train), client_id))
            
            # Log training with round number
            cursor.execute("""
                INSERT INTO training_logs
                (client_id, round_number, epochs, batch_size, learning_rate, noise_multiplier,
                 max_grad_norm, accuracy, loss, training_time, dataset_size,
                 metrics_json, started_at, completed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                client_id,
                current_round,
                config['epochs'],
                config['batch_size'],
                config['learning_rate'],
                config['noise_multiplier'],
                config['max_grad_norm'],
                val_metrics.get('accuracy', 0.0),
                val_metrics.get('loss', 0.0),
                training_time,
                len(X_train),
                json.dumps(val_metrics),
                datetime.now().isoformat()
            ))
            
            # Save local model record
            cursor.execute("""
                INSERT INTO local_models 
                (client_id, model_path, delta_path, accuracy, loss, is_aggregated)
                VALUES (?, ?, ?, ?, ?, 0)
            """, (
                client_id,
                str(local_model_path),
                str(delta_path),
                val_metrics.get('accuracy', 0.0),
                val_metrics.get('loss', 0.0)
            ))
            
            conn.commit()
            conn.close()
            
            return {
                "status": "success",
                "message": "Training completed successfully",
                "accuracy": val_metrics.get('accuracy', 0.0),
                "loss": val_metrics.get('loss', 0.0),
                "training_time": training_time,
                "metrics": val_metrics
            }
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "message": f"Training failed: {str(e)}"
            }
    
    def aggregate_models(self, client_ids: Optional[List[int]] = None) -> Dict:
        """Perform FedAvg aggregation (Admin only)"""
        try:
            start_time = time.time()
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get clients with new updates
            if client_ids:
                placeholders = ','.join('?' * len(client_ids))
                cursor.execute(f"""
                    SELECT id, client_name FROM clients
                    WHERE id IN ({placeholders})
                    AND update_status = 'New Update Available'
                """, client_ids)
            else:
                cursor.execute("""
                    SELECT id, client_name FROM clients
                    WHERE update_status = 'New Update Available'
                """)
            
            clients = cursor.fetchall()
            
            if not clients:
                conn.close()
                return {
                    "status": "error",
                    "message": "No clients with new updates available"
                }
            
            # Load deltas
            deltas = []
            client_names = []
            for client in clients:
                client_id = client['id']
                client_names.append(client['client_name'])
                
                delta_path = self.get_client_dir(client_id) / "delta.pt"
                if delta_path.exists():
                    delta = torch.load(str(delta_path), map_location='cpu')
                    deltas.append(delta)
            
            if not deltas:
                conn.close()
                return {
                    "status": "error",
                    "message": "No valid deltas found"
                }
            
            # Get previous global model accuracy
            cursor.execute("""
                SELECT accuracy FROM global_model
                ORDER BY round_number DESC LIMIT 1
            """)
            prev_result = cursor.fetchone()
            previous_accuracy = prev_result['accuracy'] if prev_result else None
            
            # Perform FedAvg
            aggregated_delta = {}
            for key in deltas[0].keys():
                aggregated_delta[key] = sum(d[key] for d in deltas) / len(deltas)
            
            # Load current global model using saved input dimension
            global_model_path = self.get_global_model_path()
            input_dim = self.get_model_input_dim(global_model_path)
            global_model = build_model(input_dim)
            global_model = self.load_model(global_model, str(global_model_path))
            
            # Store original model state for potential rollback
            original_state = {k: v.clone() for k, v in global_model.state_dict().items()}
            
            # Apply aggregated delta
            current_state = global_model.state_dict()
            new_state = {}
            for key in current_state:
                new_state[key] = current_state[key] + aggregated_delta[key]
            
            global_model.load_state_dict(new_state)
            
            # Get current round number
            cursor.execute("SELECT MAX(round_number) as max_round FROM global_model")
            result = cursor.fetchone()
            new_round = (result['max_round'] or 0) + 1
            
            # Evaluate global model using validation data from participating clients
            global_accuracy = None
            global_loss = None
            
            try:
                print(f"[AGGREGATION] Starting global model evaluation...")
                # Collect validation data from all participating clients
                all_X_val = []
                all_y_val = []
                
                for client in clients:
                    client_id = client['id']
                    # Get the most recent dataset for this client
                    cursor.execute("""
                        SELECT dataset_path FROM client_datasets
                        WHERE client_id = ?
                        ORDER BY uploaded_at DESC LIMIT 1
                    """, (client_id,))
                    dataset_row = cursor.fetchone()
                    
                    if dataset_row:
                        try:
                            dataset_path = self.resolve_dataset_path(dataset_row['dataset_path'])
                            print(f"[AGGREGATION] Loading dataset for client {client_id}: {dataset_path}")
                            
                            # Load and preprocess the client's data
                            X_train, y_train, X_val, y_val, X_test, y_test, scaler = \
                                preprocess_split_single(str(dataset_path))
                            
                            all_X_val.append(X_val)
                            all_y_val.append(y_val)
                            print(f"[AGGREGATION] Loaded {len(X_val)} validation samples from client {client_id}")
                        except Exception as client_error:
                            print(f"[AGGREGATION] Warning: Could not load dataset for client {client_id}: {str(client_error)}")
                
                # If we have validation data, evaluate the global model
                if all_X_val and all_y_val:
                    X_val_combined = np.vstack(all_X_val)
                    y_val_combined = np.concatenate(all_y_val)
                    print(f"[AGGREGATION] Combined validation data: {len(X_val_combined)} samples")
                    
                    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
                    global_model = global_model.to(device)
                    
                    val_metrics = self.evaluate_model(global_model, X_val_combined, y_val_combined, device)
                    global_accuracy = val_metrics.get('accuracy', None)
                    global_loss = val_metrics.get('loss', None)
                    
                    print(f"[AGGREGATION] ✓ Global model evaluated - Accuracy: {global_accuracy:.4f}, Loss: {global_loss:.4f}")
                    
                    # Validate improvement: Only accept if accuracy improves or is first round
                    if previous_accuracy is not None and global_accuracy is not None:
                        if global_accuracy < previous_accuracy:
                            print(f"[AGGREGATION] ⚠️ WARNING: New accuracy ({global_accuracy:.4f}) is lower than previous ({previous_accuracy:.4f})")
                            print(f"[AGGREGATION] Rolling back to previous model state...")
                            # Rollback to original state
                            global_model.load_state_dict(original_state)
                            global_accuracy = previous_accuracy
                            print(f"[AGGREGATION] ✓ Model rolled back. Keeping previous accuracy: {previous_accuracy:.4f}")
                        else:
                            print(f"[AGGREGATION] ✓ Model improved from {previous_accuracy:.4f} to {global_accuracy:.4f}")
                    
                    # Save the model (either improved or rolled back)
                    self.save_model(global_model, str(global_model_path))
                else:
                    print(f"[AGGREGATION] Warning: No validation data available for evaluation")
                    # Save model anyway if no validation data
                    self.save_model(global_model, str(global_model_path))
            except Exception as eval_error:
                print(f"[AGGREGATION] ERROR: Could not evaluate global model: {str(eval_error)}")
                import traceback
                traceback.print_exc()
                # Save model anyway on error
                self.save_model(global_model, str(global_model_path))
            
            # Calculate accuracy improvement
            accuracy_improvement = None
            if previous_accuracy is not None and global_accuracy is not None:
                accuracy_improvement = global_accuracy - previous_accuracy
            
            # Save new global model record
            cursor.execute("""
                INSERT INTO global_model (round_number, model_path, accuracy, loss)
                VALUES (?, ?, ?, ?)
            """, (new_round, str(global_model_path), global_accuracy, global_loss))
            
            # Copy global model to all clients as predict_model
            for client in clients:
                client_id = client['id']
                client_dir = self.get_client_dir(client_id)
                predict_model_path = client_dir / "predict_model.pt"
                self.save_model(global_model, str(predict_model_path))
                
                # Reset update status
                cursor.execute("""
                    UPDATE clients 
                    SET update_status = 'No Update',
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (client_id,))
                
                # Mark local models as aggregated
                cursor.execute("""
                    UPDATE local_models 
                    SET is_aggregated = 1
                    WHERE client_id = ? AND is_aggregated = 0
                """, (client_id,))
            
            aggregation_time = time.time() - start_time
            
            # Log aggregation with improvement metrics
            cursor.execute("""
                INSERT INTO aggregation_logs
                (round_number, clients_participated, num_clients, previous_accuracy,
                 global_accuracy, accuracy_improvement, global_loss, aggregation_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                new_round,
                json.dumps(client_names),
                len(clients),
                previous_accuracy,
                global_accuracy,
                accuracy_improvement,
                global_loss,
                aggregation_time
            ))
            
            conn.commit()
            conn.close()
            
            return {
                "status": "success",
                "message": f"Aggregation completed for round {new_round}",
                "round_number": new_round,
                "clients_participated": client_names,
                "num_clients": len(clients),
                "aggregation_time": aggregation_time,
                "previous_accuracy": previous_accuracy,
                "global_accuracy": global_accuracy,
                "accuracy_improvement": accuracy_improvement,
                "global_loss": global_loss
            }
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print("=" * 80)
            print("AGGREGATION ERROR:")
            print(error_trace)
            print("=" * 80)
            return {
                "status": "error",
                "message": f"Aggregation failed: {str(e)}"
            }
    
    def predict(self, client_id: int, patient_data: Dict, template_csv: str) -> Dict:
        """Make prediction using global model"""
        try:
            # Load predict model for this client
            client_dir = self.get_client_dir(client_id)
            predict_model_path = client_dir / "predict_model.pt"
            
            if not predict_model_path.exists():
                # Fall back to global model
                predict_model_path = self.get_global_model_path()
            
            if not predict_model_path.exists():
                return {
                    "status": "error",
                    "message": "No model available for prediction"
                }
            
            # Load scaler
            scaler_path = self.models_dir / "scaler.pkl"
            if not scaler_path.exists():
                return {
                    "status": "error",
                    "message": "Scaler not found. Please initialize the global model first."
                }
            
            import pickle
            with open(scaler_path, 'rb') as f:
                scaler = pickle.load(f)
            
            # Load template CSV to get feature columns and preprocessing
            resolved_template_csv = self.resolve_dataset_path(template_csv)
            template_df = pd.read_csv(str(resolved_template_csv))
            
            # Drop ID columns and get feature columns (excluding target)
            for col in list(template_df.columns):
                if "id" in col.lower():
                    template_df = template_df.drop(columns=[col])
            
            if "class" in template_df.columns:
                feature_cols = [c for c in template_df.columns if c != "class"]
            else:
                feature_cols = list(template_df.columns)
            
            # Create DataFrame from patient data
            patient_df = pd.DataFrame([patient_data])
            
            # Ensure all required features are present
            missing_features = [f for f in feature_cols if f not in patient_df.columns]
            if missing_features:
                return {
                    "status": "error",
                    "message": f"Missing required features: {missing_features}"
                }
            
            # Convert all columns to numeric, handling any string inputs
            for c in feature_cols:
                try:
                    # Try to convert to numeric, coercing errors to NaN
                    patient_df[c] = pd.to_numeric(patient_df[c], errors='coerce')
                except Exception:
                    pass
            
            # Apply preprocessing: imputation and z-score capping
            for c in feature_cols:
                # Check if value is missing or NaN
                if pd.isna(patient_df[c].iloc[0]):
                    # Fill with mean from template
                    patient_df.loc[0, c] = template_df[c].mean()
            
            # Z-score capping (using template statistics)
            z_threshold = 4.0
            for c in feature_cols:
                try:
                    mu = template_df[c].mean()
                    sd = template_df[c].std(ddof=0) or 1.0
                    val = float(patient_df[c].iloc[0])
                    z_score = (val - mu) / sd
                    
                    if z_score > z_threshold:
                        patient_df.loc[0, c] = mu + z_threshold * sd
                    elif z_score < -z_threshold:
                        patient_df.loc[0, c] = mu - z_threshold * sd
                except (ValueError, TypeError) as e:
                    # If conversion fails, use template mean
                    patient_df.loc[0, c] = template_df[c].mean()
            
            # Extract features in correct order and convert to float
            X = patient_df[feature_cols].values.astype(float)
            
            # Apply scaling
            X_scaled = scaler.transform(X)
            
            # Load model using saved input dimension
            input_dim = self.get_model_input_dim(predict_model_path)
            model = build_model(input_dim)
            model = self.load_model(model, str(predict_model_path))
            model.eval()
            
            # Convert to tensor
            X_tensor = torch.FloatTensor(X_scaled)
            
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            model = model.to(device)
            X_tensor = X_tensor.to(device)
            
            with torch.no_grad():
                logit = model(X_tensor).squeeze().item()
                prob = 1 / (1 + np.exp(-logit))
                prediction = "CKD" if prob > 0.5 else "No CKD"
            
            # Save prediction to database
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO predictions
                (client_id, patient_data_json, prediction_result, confidence)
                VALUES (?, ?, ?, ?)
            """, (
                client_id,
                json.dumps(patient_data),
                prediction,
                float(prob)
            ))
            conn.commit()
            conn.close()
            
            return {
                "status": "success",
                "prediction": prediction,
                "confidence": float(prob),
                "patient_data": patient_data
            }
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "message": f"Prediction failed: {str(e)}"
            }

# Made with Bob
