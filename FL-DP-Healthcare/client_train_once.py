import argparse, json, os, numpy as np, torch, torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
from data_prep import preprocess_split_single, preprocess_client_with_template, load_csv, _drop_ids, _impute, _zscore_cap, TARGET_COL
from models import build_model
from dp import clip_gradients, add_gaussian_noise
from viz import save_confusion_plot, save_roc_plot, save_calibration_plot
from eval_utils import metrics_from_logits


# -------------------------------
# Load template info from global checkpoint
# -------------------------------
def _template_from_ckpt(ckpt_path, template_csv):
    ckpt = torch.load(ckpt_path, map_location="cpu")
    mean = np.array(ckpt["scaler_mean"])
    scale = np.array(ckpt["scaler_scale"])

    class Scaler:
        def transform(self, X):
            return (X - mean) / scale

    df = load_csv(template_csv)
    df = _drop_ids(_impute(_zscore_cap(df, exclude=[TARGET_COL])))
    feature_cols = [c for c in df.columns if c != TARGET_COL]

    return Scaler(), feature_cols, ckpt["input_dim"], ckpt["state_dict"]


# -------------------------------
# Evaluation + Visualization
# -------------------------------
def evaluate_and_visualize(model, X, y, device, out_prefix):
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

    metrics = metrics_from_logits(logits, ytrue)

    save_confusion_plot(ytrue, (prob >= 0.5).astype(int),
                        f"{out_prefix}_confusion_val_final.png")
    save_roc_plot(ytrue, prob,
                  f"{out_prefix}_roc_val_final.png")
    save_calibration_plot(ytrue, prob,
                          f"{out_prefix}_calibration_val_final.png")

    return metrics


# -------------------------------
# Main Training
# -------------------------------
def main(args):
    os.makedirs(args.client_dir, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Load template from global model
    scaler, feature_cols, input_dim, state = _template_from_ckpt(
        args.premodel_ckpt,
        args.template_csv
    )

    # Load client dataset using same template
    Xc, yc = preprocess_client_with_template(
        args.client_csv,
        feature_cols,
        scaler
    )

    model = build_model(input_dim).to(device)
    model.load_state_dict(state)

    ds = TensorDataset(
        torch.tensor(Xc, dtype=torch.float32),
        torch.tensor(yc, dtype=torch.long)
    )
    dl = DataLoader(ds, batch_size=args.batch, shuffle=True)

    loss_fn = nn.BCEWithLogitsLoss()
    opt = torch.optim.Adam(model.parameters(), lr=args.lr, weight_decay=1e-4)

    global_state = {
        k: v.clone().detach().cpu()
        for k, v in model.state_dict().items()
    }

    # ---------------- Training with DP ----------------
    model.train()
    for _ in range(args.local_epochs):
        for xb, yb in dl:
            xb = xb.to(device)
            yb = yb.to(device).float().view(-1, 1)

            opt.zero_grad()
            logits = model(xb)
            loss = loss_fn(logits, yb)
            loss.backward()

            clip_gradients(model, args.max_grad_norm)
            add_gaussian_noise(
                model,
                args.noise_multiplier,
                args.max_grad_norm,
                device=device
            )

            opt.step()

    # Save local model
    torch.save(
        {"state_dict": model.state_dict(), "input_dim": input_dim},
        os.path.join(args.client_dir, "local_model.pt")
    )

    # Compute delta for federated aggregation
    delta = {}
    with torch.no_grad():
        for k, v in model.state_dict().items():
            delta[k] = (v.cpu() - global_state[k])

    torch.save(
        {"delta": delta, "n": len(ds)},
        os.path.join(args.client_dir, "delta_final.pt")
    )

    # Validation using template dataset
    Xtr, ytr, Xv, yv, Xte, yte, _ = preprocess_split_single(args.template_csv)

    m_val = evaluate_and_visualize(
        model,
        Xv,
        yv,
        device,
        out_prefix=os.path.join(args.client_dir, "confusion")
    )

    with open(os.path.join(args.client_dir, "metrics_final.json"), "w") as f:
        json.dump({"val": m_val, "n_samples": len(ds)}, f, indent=2)

    print("==================================================================================================\n")
    print(f"[{args.client_name}] Client training completed successfully.\n")
    print(f"[{args.client_name}] "
          f"\nValidation AUC: {m_val['auc']:.4f}, "
          f"\nF1: {m_val['f1']:.4f}, "
          f"\nAccuracy: {m_val['accuracy']:.4f}")
    print(f"\nVisualization charts have been generated successfully. Check the [{args.client_name}] folder.")
    print("==================================================================================================\n")


# -------------------------------
# Argument Parser
# -------------------------------
if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--client_name", type=str, required=True)
    p.add_argument("--client_dir", type=str, required=True)
    p.add_argument("--client_csv", type=str, required=True)
    p.add_argument("--premodel_ckpt", type=str, required=True)
    p.add_argument("--template_csv", type=str, required=True)
    p.add_argument("--local_epochs", type=int, default=10)
    p.add_argument("--batch", type=int, default=64)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--max_grad_norm", type=float, default=1.0)
    p.add_argument("--noise_multiplier", type=float, default=0.8)

    args = p.parse_args()
    main(args)
