from __future__ import annotations

import argparse
from pathlib import Path
from typing import Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC


def load_csv_dataset(path: Path) -> Tuple[np.ndarray, np.ndarray]:
    if path.suffix.lower() == ".xlsx":
        df = pd.read_excel(path)
    else:
        df = pd.read_csv(path)

    label_col = None
    for candidate in ["status", "label", "target"]:
        if candidate in df.columns:
            label_col = candidate
            break

    if label_col is None:
        raise ValueError("Label column not found. Expected one of: status, label, target.")

    y = df[label_col].to_numpy()
    drop_cols = [label_col]
    for col in ["name", "id", "subject"]:
        if col in df.columns:
            drop_cols.append(col)

    X = df.drop(columns=drop_cols)
    X = X.select_dtypes(include=["number"])

    if X.empty:
        raise ValueError("No numeric feature columns found after cleaning.")

    return X.to_numpy(dtype=np.float32), y


def train_and_save(X: np.ndarray, y: np.ndarray, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    splitter = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    train_idx, test_idx = next(splitter.split(X, y))

    X_train, y_train = X[train_idx], y[train_idx]
    X_test, y_test = X[test_idx], y[test_idx]

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = SVC(kernel="rbf", C=2.0, gamma="scale", probability=True, random_state=42)
    model.fit(X_train_scaled, y_train)

    accuracy = float(np.mean(model.predict(X_test_scaled) == y_test))
    print(f"Holdout accuracy: {accuracy:.3f}")

    scaler_full = StandardScaler().fit(X)
    X_full_scaled = scaler_full.transform(X)
    model.fit(X_full_scaled, y)

    joblib.dump(model, out_dir / "model_csv.joblib")
    joblib.dump(scaler_full, out_dir / "scaler_csv.joblib")
    print("Saved model_csv.joblib and scaler_csv.joblib")


def main() -> None:
    parser = argparse.ArgumentParser(description="Train CSV Parkinsons model.")
    parser.add_argument("--data", required=True, help="Path to CSV/XLSX file")
    parser.add_argument("--out-dir", default="../models", help="Output directory")
    args = parser.parse_args()

    data_path = Path(args.data).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()

    X, y = load_csv_dataset(data_path)
    train_and_save(X, y, out_dir)


if __name__ == "__main__":
    main()
