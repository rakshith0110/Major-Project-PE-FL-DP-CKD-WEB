import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.metrics import confusion_matrix, roc_curve, auc as roc_auc

def save_confusion_plot(y_true, y_pred, path):
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(4,3))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
    plt.xlabel("Predicted"); plt.ylabel("True")
    plt.tight_layout(); plt.savefig(path); plt.close()

def save_roc_plot(y_true, prob, path):
    fpr, tpr, _ = roc_curve(y_true, prob)
    a = roc_auc(fpr, tpr)
    plt.figure(figsize=(4,3))
    plt.plot(fpr, tpr, label=f"AUC={a:.3f}")
    plt.plot([0,1],[0,1],'k--',alpha=0.5)
    plt.xlabel("FPR"); plt.ylabel("TPR"); plt.legend()
    plt.tight_layout(); plt.savefig(path); plt.close()

def save_calibration_plot(y_true, prob, path, n_bins=10):
    bins = np.linspace(0,1,n_bins+1)
    xs = []; ys = []; ws = []
    for i in range(n_bins):
        m = (prob >= bins[i]) & (prob < bins[i+1])
        if m.sum()==0: continue
        xs.append(prob[m].mean()); ys.append(y_true[m].mean()); ws.append(m.mean())
    plt.figure(figsize=(4,3))
    plt.plot([0,1],[0,1],'k--',alpha=0.5)
    plt.scatter(xs, ys, s=np.array(ws)*300, c="tab:blue")
    plt.xlabel("Confidence"); plt.ylabel("Accuracy")
    plt.tight_layout(); plt.savefig(path); plt.close()
