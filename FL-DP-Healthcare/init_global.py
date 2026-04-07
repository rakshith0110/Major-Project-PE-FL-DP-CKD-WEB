import argparse, shutil, json, numpy as np, torch
from pathlib import Path
from torch.utils.data import TensorDataset, DataLoader
from data_prep import preprocess_split_single
from models import build_model
from eval_utils import metrics_from_logits
from viz import save_confusion_plot, save_roc_plot, save_calibration_plot
from utils_io import ensure_dirs

def evaluate_and_visualize(model, X, y, device, out_prefix):
    dl = DataLoader(TensorDataset(torch.tensor(X, dtype=torch.float32),
                                  torch.tensor(y, dtype=torch.long)), batch_size=1024)
    outs = []; ys = []
    model.eval()
    with torch.no_grad():
        for xb, yb in dl:
            xb = xb.to(device)
            logits = model(xb)
            outs.append(logits.cpu().numpy().ravel()); ys.append(yb.numpy())
    logits = np.concatenate(outs); ytrue = np.concatenate(ys)
    prob = 1/(1+np.exp(-logits))
    metrics = metrics_from_logits(logits, ytrue)
    save_confusion_plot(ytrue, (prob>=0.5).astype(int), f"{out_prefix}_confusion.png")
    save_roc_plot(ytrue, prob, f"{out_prefix}_roc.png")
    save_calibration_plot(ytrue, prob, f"{out_prefix}_calibration.png")
    return metrics

def main(args):
    ensure_dirs(Path("server"))
    for c in ["client1","client2","client3"]:
        ensure_dirs(Path(c)); ensure_dirs(Path(c)/"dataset")

    Xtr, ytr, Xv, yv, Xte, yte, scaler = preprocess_split_single(args.template_csv)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = build_model(Xtr.shape[1]).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=args.lr, weight_decay=1e-4)
    loss_fn = torch.nn.BCEWithLogitsLoss()

    best_auc = -1.0
    for epoch in range(args.epochs):
        model.train()
        dl = DataLoader(TensorDataset(torch.tensor(Xtr, dtype=torch.float32),
                                      torch.tensor(ytr, dtype=torch.long)), batch_size=args.batch, shuffle=True)
        for xb, yb in dl:
            xb = xb.to(device); yb = yb.to(device).float().view(-1,1)
            opt.zero_grad()
            logits = model(xb)
            loss = loss_fn(logits, yb)
            loss.backward()
            opt.step()
        vm = evaluate_and_visualize(model, Xv, yv, device, out_prefix="server/val_initial")
        if vm["auc"] > best_auc:
            best_auc = vm["auc"]
            torch.save({"state_dict": model.state_dict(),
                        "input_dim": Xtr.shape[1],
                        "scaler_mean": scaler.mean_.tolist(),
                        "scaler_scale": scaler.scale_.tolist()}, "server/global_round0.pt")

    ckpt = torch.load("server/global_round0.pt", map_location=device)
    model.load_state_dict(ckpt["state_dict"])
    m_val = evaluate_and_visualize(model, Xv, yv, device, out_prefix="server/val_initial")
    m_test = evaluate_and_visualize(model, Xte, yte, device, out_prefix="server/test_initial")
    with open("server/metrics_initial.json", "w") as f:
        json.dump({"val": m_val, "test": m_test}, f, indent=2)

    for i in [1,2,3]:
        shutil.copyfile("server/global_round0.pt", f"client{i}/premodel_client{i}.pt")
    print("==================================================================================================\n")
    print("Initial Global model training Completed successfully and Global model updated to clients premodel.\n")
    print("--Global Model--")
    print(f"Accuracy: {m_val['accuracy']:.4f}")
    print(f"F1: {m_val['f1']:.4f}")
    print(f"Validation AUC: {m_val['auc']:.4f}")
    print("\nVisualization charts have been generated successfully. Check the [server] folder.")

    print("=================================================================================================\n")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--template_csv", type=str, default="data/chronic_kidney_disease_5000.csv")
    p.add_argument("--epochs", type=int, default=20)
    p.add_argument("--batch", type=int, default=64)
    p.add_argument("--lr", type=float, default=1e-3)
    args = p.parse_args()
    main(args)
