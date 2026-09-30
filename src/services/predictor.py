from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

import numpy as np

from services.feature_extraction import extract_features, FeatureConfig
from services.model_loader import load_artifacts, ModelArtifacts


@dataclass(frozen=True)
class PredictionResult:
    label: str
    confidence: float


class ParkinsonPredictor:
    def __init__(self, model_path: str | Path, scaler_path: str | Path):
        self.artifacts: ModelArtifacts = load_artifacts(model_path, scaler_path)

    def predict_file(self, audio_path: str) -> PredictionResult:
        features = extract_features(audio_path)
        return self.predict_features(features)

    def predict_features(self, features: np.ndarray) -> PredictionResult:
        features = np.asarray(features, dtype=np.float32).reshape(1, -1)
        scaled = self.artifacts.scaler.transform(features)

        model = self.artifacts.model
        pred_class = model.predict(scaled)[0]
        confidence = self._confidence(model, scaled, pred_class)
        label = self._label_from_class(pred_class)

        return PredictionResult(label=label, confidence=confidence)

    @staticmethod
    def _label_from_class(pred_class) -> str:
        if isinstance(pred_class, (int, np.integer, float)) and int(pred_class) == 1:
            return "Likely Parkinson’s"
        if isinstance(pred_class, str) and "park" in pred_class.lower():
            return "Likely Parkinson’s"
        return "Likely Healthy"

    @staticmethod
    def _confidence(model, scaled: np.ndarray, pred_class) -> float:
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(scaled)[0]
            classes = getattr(model, "classes_", None)
            if classes is not None:
                idx = int(np.where(classes == pred_class)[0][0])
            else:
                idx = int(np.argmax(proba))
            return float(proba[idx])

        if hasattr(model, "decision_function"):
            scores = model.decision_function(scaled)
            if scores.ndim == 1:
                score = float(scores[0])
                return float(1.0 / (1.0 + np.exp(-score)))
            exp_scores = np.exp(scores - np.max(scores))
            proba = exp_scores / exp_scores.sum(axis=1, keepdims=True)
            return float(np.max(proba))

        # Fallback: no probability available
        return 0.5
