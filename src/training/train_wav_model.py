from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Tuple

import joblib
import numpy as np
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from feature_extraction import extract_features


def collect_wav_files(root: Path) -> Tuple[List[Path], List[int]]:
    label_map = {
        "healthy": 0,
        "control": 0,
        "parkinson": 1,
        "parkinsons": 1,
        "pd": 1,
    }

    files: List[Path] = []
    labels: List[int] = []

    for label_dir in root.iterdir():
        if not label_dir.is_dir():
            continue
        key = label_dir.name.lower().strip()
        if key not in label_map:
            continue
        for wav_path in label_dir.rglob("*.wav"):
            files.append(wav_path)
            labels.append(label_map[key])

    if not files:
        raise ValueError("No labeled WAV files found. Use subfolders like healthy/ and parkinson/.")

    return files, labels


def build_feature_matrix(files: List[Path]) -> np.ndarray:
    features = []
    for path in files:
        feats = extract_features(str(path))
        features.append(feats)
    return np.vstack(features)


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

    joblib.dump(model, out_dir / "model_audio.joblib")
    joblib.dump(scaler_full, out_dir / "scaler_audio.joblib")
    print("Saved model_audio.joblib and scaler_audio.joblib")


def main() -> None:
    parser = argparse.ArgumentParser(description="Train WAV Parkinsons model.")
    parser.add_argument("--data-dir", required=True, help="Root folder with healthy/ and parkinson/ subfolders")
    parser.add_argument("--out-dir", default="../models", help="Output directory")
    args = parser.parse_args()

    data_dir = Path(args.data_dir).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()

    files, labels = collect_wav_files(data_dir)
    X = build_feature_matrix(files)
    y = np.array(labels)

    train_and_save(X, y, out_dir)


if __name__ == "__main__":
    main()
