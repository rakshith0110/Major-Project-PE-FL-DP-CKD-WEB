import numpy as np
from sklearn.metrics import roc_auc_score, f1_score, precision_score, recall_score, accuracy_score

def metrics_from_logits(logits: np.ndarray, y_true: np.ndarray):
    probs = 1/(1+np.exp(-logits))
    preds = (probs >= 0.5).astype(int)
    return {
        "accuracy": float(accuracy_score(y_true, preds)),
        "precision": float(precision_score(y_true, preds, zero_division=0)),
        "recall": float(recall_score(y_true, preds, zero_division=0)),
        "f1": float(f1_score(y_true, preds, zero_division=0)),
        "auc": float(roc_auc_score(y_true, probs))
    }
