import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

TARGET_COL = "class"

def load_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(path)

def _impute(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for c in df.columns:
        if df[c].dtype.kind in "biufc":
            df[c] = df[c].fillna(df[c].mean())
        else:
            df[c] = df[c].fillna(df[c].mode().iloc[0])
    return df

def _zscore_cap(df: pd.DataFrame, z=4.0, exclude=None) -> pd.DataFrame:
    df = df.copy()
    exclude = set(exclude or [])

    for c in df.columns:
        if c in exclude:
            continue

        if df[c].dtype.kind in "biufc":
            df[c] = df[c].astype(float)

            mu = df[c].mean()
            sd = df[c].std(ddof=0) or 1.0
            zsc = (df[c] - mu) / sd

            df.loc[zsc > z, c] = mu + z * sd
            df.loc[zsc < -z, c] = mu - z * sd

    return df


def _drop_ids(df: pd.DataFrame) -> pd.DataFrame:
    for col in list(df.columns):
        if "id" in col.lower():
            df = df.drop(columns=[col])
    return df

def _upsample_minority(X, y, seed=42):
    rng = np.random.RandomState(seed)
    classes, counts = np.unique(y, return_counts=True)
    if len(classes)!=2:
        return X, y
    need = counts.max()-counts.min()
    if need<=0:
        return X, y
    min_class = classes[np.argmin(counts)]
    idx_min = np.where(y==min_class)[0]
    add = rng.choice(idx_min, size=need, replace=True)
    return np.concatenate([X, X[add]],0), np.concatenate([y, y[add]],0)

def preprocess_split_single(path: str, test_size=0.2, val_size=0.1, seed=42):
    df = load_csv(path)
    df = _drop_ids(_impute(_zscore_cap(df, exclude=[TARGET_COL])))
    assert TARGET_COL in df.columns, f"Missing '{TARGET_COL}' column"
    y = df[TARGET_COL].values.astype(int)
    X = df.drop(columns=[TARGET_COL]).values.astype(float)

    scaler = StandardScaler().fit(X)
    X = scaler.transform(X)

    X_tr, X_tmp, y_tr, y_tmp = train_test_split(X, y, test_size=test_size+val_size, stratify=y, random_state=seed)
    rel_val = val_size/(test_size+val_size)
    X_val, X_te, y_val, y_te = train_test_split(X_tmp, y_tmp, test_size=1-rel_val, stratify=y_tmp, random_state=seed)
    X_tr_bal, y_tr_bal = _upsample_minority(X_tr, y_tr, seed=seed)
    return (X_tr_bal, y_tr_bal, X_val, y_val, X_te, y_te, scaler)

def preprocess_client_with_template(path: str, feature_cols, scaler):
    df = load_csv(path)
    df = _drop_ids(_impute(_zscore_cap(df, exclude=[TARGET_COL])))
    missing = [c for c in feature_cols if c not in df.columns]
    assert not missing, f"Client data missing features: {missing}"
    X = df[feature_cols].values.astype(float)
    y = df[TARGET_COL].values.astype(int)
    X = scaler.transform(X)
    return X, y
