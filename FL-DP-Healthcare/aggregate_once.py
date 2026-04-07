import argparse, json, shutil, numpy as np, torch, os
from torch.utils.data import TensorDataset, DataLoader
from data_prep import preprocess_split_single
from models import build_model
from eval_utils import metrics_from_logits
from viz import save_confusion_plot, save_roc_plot, save_calibration_plot


# -------------------------------
# Load client delta
# -------------------------------
def load_delta(path):
    obj = torch.load(path, map_location="cpu")
    return obj["delta"], obj["n"]


# -------------------------------
# Apply delta to model weights
# -------------------------------
def apply_delta(state_dict, delta):
    for k in state_dict:
        state_dict[k] += delta[k]


# -------------------------------
# Federated Averaging
# -------------------------------
def fedavg_state(state_dict, delta_list, weights):
    total = sum(weights)
    keys = list(delta_list[0].keys())
    agg = {}

    for k in keys:
        agg[k] = sum(d[k] * (w / total) for d, w in zip(delta_list, weights))

    apply_delta(state_dict, agg)


# -------------------------------
# Evaluation + Visualization
# -------------------------------
def evaluate_and_visualize(model, X, y, device, prefix):
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
            xb = xb.to(device)
            logits = model(xb)
            outs.append(logits.cpu().numpy().ravel())
            ys.append(yb.numpy())

    logits = np.concatenate(outs)
    ytrue = np.concatenate(ys)
    prob = 1 / (1 + np.exp(-logits))

    m = metrics_from_logits(logits, ytrue)

    save_confusion_plot(
        ytrue,
        (prob >= 0.5).astype(int),
        f"{prefix}_confusion_val_final.png"
    )
    save_roc_plot(
        ytrue,
        prob,
        f"{prefix}_roc_val_final.png"
    )
    save_calibration_plot(
        ytrue,
        prob,
        f"{prefix}_calibration_val_final.png"
    )

    return m


# -------------------------------
# Main Aggregation Logic
# -------------------------------
def main(args):
    os.makedirs("server", exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Load initial global model
    ckpt = torch.load("server/global_round0.pt", map_location=device)
    state = ckpt["state_dict"]
    input_dim = ckpt["input_dim"]

    # Load client deltas
    deltas = []
    weights = []

    for dpath in [args.delta1, args.delta2, args.delta3]:
        d, n = load_delta(dpath)
        deltas.append(d)
        weights.append(n)

    # Federated averaging
    fedavg_state(state, deltas, weights)

    # Save updated global model
    torch.save(
        {
            "state_dict": state,
            "input_dim": input_dim,
            "scaler_mean": ckpt.get("scaler_mean"),
            "scaler_scale": ckpt.get("scaler_scale"),
        },
        "server/global_final.pt"
    )

    # Evaluate using CKD template dataset
    Xtr, ytr, Xv, yv, Xte, yte, _ = preprocess_split_single(
        args.template_csv
    )

    model = build_model(input_dim).to(device)
    model.load_state_dict(state)

    m_val = evaluate_and_visualize(
        model,
        Xv,
        yv,
        device,
        prefix="server/confusion"
    )

    # Save metrics
    with open("server/metrics_final.json", "w") as f:
        json.dump({"val": m_val}, f, indent=2)

    # Distribute updated model back to clients
    shutil.copyfile("server/global_final.pt", "client1/premodel_client1.pt")
    shutil.copyfile("server/global_final.pt", "client2/premodel_client2.pt")
    shutil.copyfile("server/global_final.pt", "client3/premodel_client3.pt")

    print("==================================================================================================\n")
    print("Aggregation completed successfully. Global model updated and distributed to clients.\n")
    print("--Global Model--")
    print(
        f"Validation AUC: {m_val['auc']:.4f}\n"
        f"F1: {m_val['f1']:.4f}\n"
        f"Accuracy: {m_val['accuracy']:.4f}"
    )
    print("\nVisualization charts have been generated successfully. Check the [server] folder.")
    print("==================================================================================================\n")


# -------------------------------
# Argument Parser
# -------------------------------
if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--delta1", type=str, default="client1/delta_final.pt")
    p.add_argument("--delta2", type=str, default="client2/delta_final.pt")
    p.add_argument("--delta3", type=str, default="client3/delta_final.pt")
    p.add_argument("--template_csv", type=str, required=True)
    args = p.parse_args()
    main(args)
