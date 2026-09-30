import re

with open('src/components/main_window.py', 'r', encoding='utf-8') as f:
    content = f.read()

missing_methods = '''    def _apply_styles(self) -> None:
        self.setStyleSheet(get_stylesheet())

    def _load_model(self) -> None:
        audio_model = resource_path("models/model_audio.joblib")
        audio_scaler = resource_path("models/scaler_audio.joblib")
        csv_model = resource_path("models/model_csv.joblib")
        csv_scaler = resource_path("models/scaler_csv.joblib")
        default_model = resource_path("models/model.joblib")
        default_scaler = resource_path("models/scaler.joblib")

        self.predictor_audio = self._try_load_predictor(audio_model, audio_scaler)
        self.predictor_csv = self._try_load_predictor(csv_model, csv_scaler)

        if self.predictor_audio is None and default_model.exists() and default_scaler.exists():
            self.predictor_audio = self._try_load_predictor(default_model, default_scaler)

        if self.predictor_csv is None and default_model.exists() and default_scaler.exists():
            self.predictor_csv = self._try_load_predictor(default_model, default_scaler)

        self._update_model_status()

        if self.predictor_audio is None and self.predictor_csv is None:
            QMessageBox.critical(
                self,
                "Model Load Error",
                "Could not load model artifacts.\\n\\n"
                "Add model_audio.joblib + scaler_audio.joblib for WAV mode, and\\n"
                "model_csv.joblib + scaler_csv.joblib for CSV mode (or model.joblib + scaler.joblib).",
            )

    def _try_load_predictor(self, model_path, scaler_path) -> ParkinsonPredictor | None:
        try:
            if model_path.exists() and scaler_path.exists():
                return ParkinsonPredictor(model_path, scaler_path)
        except Exception:
            return None
        return None

    def _update_model_status(self) -> None:
        audio_ok = self.predictor_audio is not None
        csv_ok = self.predictor_csv is not None
        status = "Audio: Ready" if audio_ok else "Audio: Missing"
        status += " | CSV: Ready" if csv_ok else " | CSV: Missing"
        if hasattr(self, 'status_tile'):
            self.status_tile.value_label.setText(status)

    def _select_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select WAV file",
            default_dialog_dir(),
            "WAV Files (*.wav);;All Files (*.*)"
        )
        if not file_path:
            return

        self.audio_path = file_path
        self.file_label.setText(Path(file_path).name)
        self._update_quality_view(file_path)
        self._refresh_analyze_state()

    def _select_csv(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select CSV or XLSX file",
            default_dialog_dir(),
            "CSV/XLSX Files (*.csv *.xlsx);;All Files (*.*)"
        )
        if not file_path:
            return

        self.csv_path = file_path
        self.csv_label.setText(Path(file_path).name)
        self._update_quality_view(None)
        self._refresh_analyze_state()

    def _switch_mode(self) -> None:
        is_audio = self.mode_combo.currentIndex() == 0
        if hasattr(self, 'audio_widget'):
            self.audio_widget.setVisible(is_audio)
        if hasattr(self, 'csv_widget'):
            self.csv_widget.setVisible(not is_audio)

        if hasattr(self, 'mode_tile'):
            self.mode_tile.value_label.setText("WAV Audio" if is_audio else "CSV/XLSX Features")
        
        self._update_model_status()
        self._refresh_analyze_state()
        if not is_audio:
            self._update_quality_view(None)
        elif self.audio_path:
            self._update_quality_view(self.audio_path)
'''

content = re.sub(r'    def _switch_mode\(self\) -> None:.*?elif self\.audio_path:.*?\s+self\._update_quality_view\(self\.audio_path\)', missing_methods, content, flags=re.DOTALL)

with open('src/components/main_window.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Patch applied successfully.')
