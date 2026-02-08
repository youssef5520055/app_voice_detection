# Voice-Based Parkinson's Tool Documentation

## Overview
This app provides two analysis paths:
- WAV audio: extract acoustic features and run a classical ML model.
- CSV/XLSX: run a classical ML model on precomputed numeric features.

This is a screening-style demo and is not a medical diagnosis.

## Project Layout
- app/main.py: app entry point.
- app/ui/main_window.py: UI layout and behavior.
- app/feature_extraction.py: audio feature extraction.
- app/predictor.py: model prediction wrapper.
- app/training/train_csv_model.py: train CSV/XLSX model.
- app/training/train_wav_model.py: train WAV model from labeled folders.
- app/training/train_hf_wav_model.py: download HF dataset and train WAV model.
- app/models/: trained model artifacts.

## Training (WAV)

### Option A: Hugging Face dataset (Italian Parkinson's Voice and Speech)
This will download about 1.4 GB of audio files.

1) Activate the project virtual environment and install requirements (if not already):

```bash
python -m pip install -r app/requirements.txt
python -m pip install huggingface_hub==0.24.6
```

2) Run the training script:

```bash
python app/training/train_hf_wav_model.py --out-dir app/models
```

Outputs:
- app/models/model_audio.joblib
- app/models/scaler_audio.joblib

### Option B: Local labeled folders
Provide a root folder with:
- healthy/
- parkinson/

Run:

```bash
python app/training/train_wav_model.py --data-dir <PATH_TO_DATA> --out-dir app/models
```

## Training (CSV/XLSX)

```bash
python app/training/train_csv_model.py --data <PATH_TO_CSV_OR_XLSX> --out-dir app/models
```

## Running the App

```bash
python app/main.py
```

## Model Files
The UI looks for these artifacts:
- WAV: model_audio.joblib + scaler_audio.joblib
- CSV: model_csv.joblib + scaler_csv.joblib

If those are missing, the UI will show a model status warning.

## Notes
- The HF dataset is licensed under CC BY 4.0. Review the dataset card for details.
- The app is a prototype for research/demo use.
