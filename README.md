# Voice-Based Parkinson's Detection — Advanced Acoustic & Machine Learning Screening

A state-of-the-art desktop application designed to screen for Parkinson's Disease through sophisticated acoustic feature extraction and classical machine learning models. Engineered with PySide6 and librosa, it offers a dual-pathway analysis system for both raw audio (WAV) and precomputed numeric features (CSV/XLSX), delivering high-confidence predictive insights in real-time.

### Live Deployment
*Desktop Application — [Clone & Run Locally](https://github.com/youssef5520055/app_voice_detection)*

![Overview Interface](docs/screenshot.png)
![Record Voice Interface](docs/screenshot2.png)

### 🌟 Core Feature Suite

1. **Dual-Pathway Analytical Engine**
   - **Acoustic WAV Processing:** Extracts Mel-frequency cepstral coefficients (MFCCs), fundamental frequency (F0), jitter, shimmer, and other vocal biomarkers using `librosa`.
   - **Numeric Data Ingestion:** Supports standardized precomputed feature datasets via CSV or XLSX for rapid model evaluation.
2. **Advanced Machine Learning Pipeline**
   - **Pre-Trained Classifiers:** Employs robust `scikit-learn` algorithms (e.g., SVM, Random Forest) serialized via `joblib` for immediate inference.
   - **Automated Scaling:** Applies standard scaling to normalize feature vectors, ensuring high accuracy and model stability.
3. **Enterprise-Grade UI/UX**
   - **PySide6 Framework:** Delivers a responsive, hardware-accelerated graphical user interface with modern styling.
   - **Real-Time History Store:** Persists prediction history, confidence metrics, and source data in a JSON-backed local storage system.
4. **Flexible Training Architecture**
   - **Hugging Face Integration:** Seamlessly downloads and processes datasets like the Italian Parkinson's Voice and Speech dataset directly from the HF Hub.
   - **Local Folder Parsing:** Supports training from local directories cleanly separated into `healthy/` and `parkinson/` classes.
