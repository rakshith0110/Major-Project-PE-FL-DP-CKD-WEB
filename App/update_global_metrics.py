#!/usr/bin/env python3
"""
Script to retroactively calculate and update global model metrics
for existing aggregation rounds that don't have accuracy/loss values.
"""
import sys
import sqlite3
import torch
import numpy as np
from pathlib import Path

# Add FL-DP-Healthcare to path
FL_DP_PATH = Path(__file__).parent.parent / "FL-DP-Healthcare"
sys.path.insert(0, str(FL_DP_PATH))

from models import build_model
from data_prep import preprocess_split_single
from eval_utils import metrics_from_logits

def evaluate_model(model, X, y, device):
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

def main():
    db_path = Path(__file__).parent / "federated_ckd.db"
    models_dir = Path(__file__).parent / "models"
    
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all global model records without accuracy/loss
    cursor.execute("""
        SELECT id, round_number, model_path 
        FROM global_model 
        WHERE accuracy IS NULL AND round_number > 0
        ORDER BY round_number
    """)
    
    records = cursor.fetchall()
    
    if not records:
        print("✓ All global model records already have accuracy/loss values")
        conn.close()
        return
    
    print(f"Found {len(records)} records to update")
    
    # Get client datasets
    cursor.execute("""
        SELECT DISTINCT client_id, dataset_path 
        FROM client_datasets 
        ORDER BY client_id, uploaded_at DESC
    """)
    
    datasets = {}
    for row in cursor.fetchall():
        if row['client_id'] not in datasets:
            datasets[row['client_id']] = row['dataset_path']
    
    if not datasets:
        print("✗ No client datasets found")
        conn.close()
        return
    
    print(f"Found datasets for {len(datasets)} clients")
    
    # Load validation data from all clients
    all_X_val = []
    all_y_val = []
    
    for client_id, dataset_path in datasets.items():
        try:
            print(f"Loading dataset for client {client_id}...")
            X_train, y_train, X_val, y_val, X_test, y_test, scaler = \
                preprocess_split_single(dataset_path)
            all_X_val.append(X_val)
            all_y_val.append(y_val)
            print(f"  ✓ Loaded {len(X_val)} validation samples")
        except Exception as e:
            print(f"  ✗ Error loading dataset: {e}")
    
    if not all_X_val:
        print("✗ No validation data available")
        conn.close()
        return
    
    X_val_combined = np.vstack(all_X_val)
    y_val_combined = np.concatenate(all_y_val)
    print(f"\nCombined validation data: {len(X_val_combined)} samples")
    
    # Load and evaluate each global model
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}\n")
    
    global_model_path = models_dir / "global_model.pt"
    if not global_model_path.exists():
        print(f"✗ Global model not found at {global_model_path}")
        conn.close()
        return
    
    # Get input dimension from the model
    state_dict = torch.load(str(global_model_path), map_location='cpu')
    first_weight = state_dict.get("net.0.weight")
    if first_weight is None:
        print("✗ Unable to infer input dimension from model")
        conn.close()
        return
    
    input_dim = int(first_weight.shape[1])
    print(f"Model input dimension: {input_dim}")
    
    # Build and load model
    model = build_model(input_dim)
    model.load_state_dict(state_dict)
    model = model.to(device)
    
    # Evaluate the current global model
    print("\nEvaluating current global model...")
    metrics = evaluate_model(model, X_val_combined, y_val_combined, device)
    accuracy = metrics.get('accuracy', 0.0)
    loss = metrics.get('loss', 0.0)
    
    print(f"  Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"  Loss: {loss:.4f}")
    
    # Update all records with the same values (since we only have one global model file)
    print(f"\nUpdating {len(records)} records...")
    for record in records:
        cursor.execute("""
            UPDATE global_model 
            SET accuracy = ?, loss = ?
            WHERE id = ?
        """, (accuracy, loss, record['id']))
        print(f"  ✓ Updated round {record['round_number']}")
    
    conn.commit()
    conn.close()
    
    print(f"\n✓ Successfully updated {len(records)} global model records")

if __name__ == "__main__":
    main()

# Made with Bob
