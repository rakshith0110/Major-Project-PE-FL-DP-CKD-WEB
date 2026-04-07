import argparse, json, os, numpy as np, torch
import pandas as pd
from datetime import datetime
from data_prep import load_csv, _drop_ids, _impute, _zscore_cap, TARGET_COL
from models import build_model

LABEL_TEXT = ["NO", "YES"]


# -------------------------------
# Load template from global model
# -------------------------------
def load_template_from_ckpt(ckpt_path, template_csv):
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
# Predict rows
# -------------------------------
def predict_rows(df_features: pd.DataFrame, premodel_ckpt: str, template_csv: str):
    scaler, feature_cols, input_dim, state = load_template_from_ckpt(
        premodel_ckpt,
        template_csv
    )

    missing = [c for c in feature_cols if c not in df_features.columns]
    if missing:
        raise ValueError(f"Missing required features in patient_data: {missing}")

    X = df_features[feature_cols].values.astype(float)
    X = scaler.transform(X)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = build_model(input_dim).to(device)
    model.load_state_dict(state)
    model.eval()

    with torch.no_grad():
        logits = model(torch.tensor(X, dtype=torch.float32).to(device)).cpu().numpy().ravel()
        prob = 1 / (1 + np.exp(-logits))
        y_pred = (prob >= 0.5).astype(int)

    return y_pred, prob


# -------------------------------
# Append predictions to client dataset
# -------------------------------
def append_predictions_to_client(client_dir: str, predicted_rows: pd.DataFrame):
    ds_dir = os.path.join(client_dir, "dataset")
    os.makedirs(ds_dir, exist_ok=True)

    out_path = os.path.join(ds_dir, "new_patients_records.csv")

    # Append rows; create file with header if missing
    if not os.path.exists(out_path):
        predicted_rows.to_csv(out_path, index=False)
    else:
        predicted_rows.to_csv(out_path, mode="a", index=False, header=False)

    return out_path


# -------------------------------
# Main
# -------------------------------
def main(args):
    if not os.path.exists(args.patient_csv):
        raise FileNotFoundError(f"Patient data not found: {args.patient_csv}")

    df_all = pd.read_csv(args.patient_csv)

    if TARGET_COL in df_all.columns:
        df_all = df_all.drop(columns=[TARGET_COL])

    # Select rows for prediction
    if args.row_index is not None:
        if args.row_index < 0 or args.row_index >= len(df_all):
            raise IndexError(f"row_index {args.row_index} out of range 0..{len(df_all)-1}")
        df_to_pred = df_all.iloc[[args.row_index]].copy()
    elif args.all_rows:
        df_to_pred = df_all.copy()
    else:
        df_to_pred = df_all.iloc[[0]].copy()

    premodel = os.path.join(args.client_dir, f"premodel_{args.client_name}.pt")
    if not os.path.exists(premodel):
        raise FileNotFoundError(f"Premodel not found: {premodel}")

    # -------- Prediction --------
    y_pred, prob = predict_rows(
        df_to_pred,
        premodel,
        args.template_csv
    )

    # Prepare rows with predictions and timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df_out = df_to_pred.copy()
    df_out[TARGET_COL] = y_pred.astype(int)
    df_out["predicted_prob"] = prob.astype(float)
    df_out["predicted_label"] = [LABEL_TEXT[int(c)] for c in y_pred]
    df_out["predicted_date_time"] = timestamp

    out_csv = append_predictions_to_client(args.client_dir, df_out)

    print("==================================================================================================")
    print(f"[{args.client_name}]\n")
    print("Prediction completed.\n")

    first = df_out.iloc[0]
    print(f"RESULT: {first['predicted_label']}")
    print(f"Probability: {first['predicted_prob']:.4f}\n")

    print(f"Appended {len(df_out)} row(s) to: {out_csv}")
    print(
        f"appended columns -> class: {int(first[TARGET_COL])}, "
        f"label: {first['predicted_label']}, "
        f"prob: {first['predicted_prob']:.4f}, "
        f"time: {first['predicted_date_time']}\n"
    )

    out_json = os.path.join(args.client_dir, "new_patients_predictions_last_batch.json")
    preview = df_out.head(10).to_dict(orient="records")
    with open(out_json, "w") as f:
        json.dump({"appended_rows": len(df_out), "preview": preview}, f, indent=2)

    print(f"Saved batch preview JSON: {out_json}")
    print("==================================================================================================\n")


# -------------------------------
# Argument Parser
# -------------------------------
if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--client_name", type=str, required=True)
    p.add_argument("--client_dir", type=str, required=True)
    p.add_argument("--template_csv", type=str, required=True)
    p.add_argument("--patient_csv", type=str, default="data/patient_data.csv")
    p.add_argument("--row_index", type=int, default=None)
    p.add_argument("--all_rows", action="store_true")

    args = p.parse_args()
    main(args)