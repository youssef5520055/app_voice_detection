from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Tuple

import numpy as np
from huggingface_hub import snapshot_download

import sys

APP_ROOT = Path(__file__).resolve().parents[1]
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from training.train_wav_model import build_feature_matrix, train_and_save


HF_REPO = "birgermoell/Italian_Parkinsons_Voice_and_Speech"


def collect_hf_wavs(dataset_root: Path) -> Tuple[List[Path], List[int]]:
    base = dataset_root / "italian_parkinson"
    label_map = {
        "28 People with Parkinson's disease": 1,
        "22 Elderly Healthy Control": 0,
        "15 Young Healthy Control": 0,
    }

    files: List[Path] = []
    labels: List[int] = []

    for folder, label in label_map.items():
        folder_path = base / folder
        if not folder_path.exists():
            continue
        for wav_path in folder_path.rglob("*.wav"):
            files.append(wav_path)
            labels.append(label)

    if not files:
        raise ValueError("No WAV files found in the downloaded dataset.")

    return files, labels


def download_dataset(cache_dir: Path) -> Path:
    cache_dir.mkdir(parents=True, exist_ok=True)
    return Path(
        snapshot_download(
            repo_id=HF_REPO,
            repo_type="dataset",
            local_dir=str(cache_dir),
            local_dir_use_symlinks=False,
            allow_patterns=["italian_parkinson/**/*.wav"],
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Train WAV model from HF dataset.")
    parser.add_argument(
        "--cache-dir",
        default="../data/italian_parkinsons_hf",
        help="Local cache directory for the HF dataset",
    )
    parser.add_argument("--out-dir", default="../models", help="Output directory")
    args = parser.parse_args()

    cache_dir = Path(args.cache_dir).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()

    dataset_root = download_dataset(cache_dir)
    files, labels = collect_hf_wavs(dataset_root)
    X = build_feature_matrix(files)
    y = np.array(labels)

    train_and_save(X, y, out_dir)


if __name__ == "__main__":
    main()
