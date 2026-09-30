from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Tuple

import joblib


@dataclass(frozen=True)
class ModelArtifacts:
    model: Any
    scaler: Any


def load_artifacts(model_path: str | Path, scaler_path: str | Path) -> ModelArtifacts:
    model_path = Path(model_path)
    scaler_path = Path(scaler_path)

    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")
    if not scaler_path.exists():
        raise FileNotFoundError(f"Scaler file not found: {scaler_path}")

    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)

    return ModelArtifacts(model=model, scaler=scaler)
