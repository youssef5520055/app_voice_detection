from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np
import librosa


@dataclass(frozen=True)
class FeatureConfig:
    sample_rate: int = 22050
    n_mfcc: int = 13
    fmin: float = 50.0
    fmax: float = 500.0


def _safe_stats(values: np.ndarray) -> Tuple[float, float, float, float]:
    if values.size == 0:
        return 0.0, 0.0, 0.0, 0.0
    return (
        float(np.mean(values)),
        float(np.std(values)),
        float(np.min(values)),
        float(np.max(values)),
    )


def _mean_std(values: np.ndarray) -> Tuple[float, float]:
    if values.size == 0:
        return 0.0, 0.0
    return float(np.mean(values)), float(np.std(values))


def extract_features(audio_path: str, config: FeatureConfig | None = None) -> np.ndarray:
    """
    Extract MFCCs, pitch-related, and spectral features from a WAV file.
    Returns a 1D numpy array suitable for scikit-learn models.
    """
    cfg = config or FeatureConfig()

    # Load audio
    y, sr = librosa.load(audio_path, sr=cfg.sample_rate, mono=True)
    if y.size == 0:
        raise ValueError("Audio file contains no samples.")

    # MFCCs
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=cfg.n_mfcc)
    mfcc_mean = np.mean(mfcc, axis=1)
    mfcc_std = np.std(mfcc, axis=1)

    # Pitch-related features (using YIN)
    pitch = librosa.yin(y, fmin=cfg.fmin, fmax=cfg.fmax, sr=sr)
    pitch = pitch[np.isfinite(pitch)]
    pitch_mean, pitch_std, pitch_min, pitch_max = _safe_stats(pitch)
    pitch_median = float(np.median(pitch)) if pitch.size else 0.0
    pitch_range = float(pitch_max - pitch_min) if pitch.size else 0.0
    voiced_ratio = float(pitch.size / max(1, len(y)))

    # Spectral features
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
    bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
    rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
    flatness = librosa.feature.spectral_flatness(y=y)
    rms = librosa.feature.rms(y=y)
    contrast = librosa.feature.spectral_contrast(y=y, sr=sr)

    centroid_mean, centroid_std = _mean_std(centroid)
    bandwidth_mean, bandwidth_std = _mean_std(bandwidth)
    rolloff_mean, rolloff_std = _mean_std(rolloff)
    flatness_mean, flatness_std = _mean_std(flatness)
    rms_mean, rms_std = _mean_std(rms)

    contrast_mean = np.mean(contrast, axis=1)
    contrast_std = np.std(contrast, axis=1)

    features = np.concatenate(
        [
            mfcc_mean,
            mfcc_std,
            np.array(
                [
                    pitch_mean,
                    pitch_std,
                    pitch_min,
                    pitch_max,
                    pitch_median,
                    pitch_range,
                    voiced_ratio,
                ]
            ),
            np.array(
                [
                    centroid_mean,
                    centroid_std,
                    bandwidth_mean,
                    bandwidth_std,
                    rolloff_mean,
                    rolloff_std,
                    flatness_mean,
                    flatness_std,
                    rms_mean,
                    rms_std,
                ]
            ),
            contrast_mean,
            contrast_std,
        ]
    )

    return features.astype(np.float32)
