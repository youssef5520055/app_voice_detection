from __future__ import annotations

from pathlib import Path

import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QSizePolicy,
    QStyle,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from predictor import ParkinsonPredictor
from ui.helpers import default_dialog_dir, resource_path
from ui.history import HistoryStore
from ui.styles import get_stylesheet


APP_TITLE = "Parkinson's Voice Analysis Tool"
HISTORY_PATH = Path(__file__).resolve().parents[1] / "data" / "history.json"


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.setMinimumSize(1120, 740)

        self.audio_path: str | None = None
        self.csv_path: str | None = None
        self.predictor_audio: ParkinsonPredictor | None = None
        self.predictor_csv: ParkinsonPredictor | None = None
        self.history = HistoryStore(HISTORY_PATH)

        self._build_ui()
        self._apply_styles()
        self._load_model()

    def _build_ui(self) -> None:
        container = QWidget()
        root = QHBoxLayout(container)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(16)

        sidebar = self._build_sidebar()
        content = self._build_content()

        root.addWidget(sidebar)
        root.addWidget(content, 1)
        self.setCentralWidget(container)

        self._populate_history()
        self._switch_mode()
        self._set_page(0)

    def _build_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(230)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(18, 20, 18, 20)
        layout.setSpacing(16)

        logo = QLabel("Voice Health")
        logo.setObjectName("logo")
        layout.addWidget(logo)

        profile = QFrame()
        profile.setObjectName("profileCard")
        profile_layout = QVBoxLayout(profile)
        profile_layout.setContentsMargins(12, 12, 12, 12)
        profile_layout.setSpacing(6)
        profile_name = QLabel("Research User")
        profile_name.setObjectName("profileName")
        profile_meta = QLabel("Academic Demo")
        profile_meta.setObjectName("profileMeta")
        profile_layout.addWidget(profile_name)
        profile_layout.addWidget(profile_meta)
        layout.addWidget(profile)

        nav = QFrame()
        nav_layout = QVBoxLayout(nav)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(8)
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

        self.nav_dashboard = self._nav_button("Dashboard", QStyle.SP_ComputerIcon, 0)
        self.nav_record = self._nav_button("Record Voice", QStyle.SP_MediaPlay, 1)
        self.nav_quality = self._nav_button("Quality", QStyle.SP_FileDialogDetailedView, 2)
        self.nav_results = self._nav_button("Results", QStyle.SP_FileDialogContentsView, 3)
        self.nav_history = self._nav_button("History", QStyle.SP_FileDialogListView, 4)
        for btn in [
            self.nav_dashboard,
            self.nav_record,
            self.nav_quality,
            self.nav_results,
            self.nav_history,
        ]:
            nav_layout.addWidget(btn)
        layout.addWidget(nav)
        layout.addStretch(1)

        score_card = QFrame()
        score_card.setObjectName("scoreCard")
        score_layout = QVBoxLayout(score_card)
        score_layout.setContentsMargins(12, 12, 12, 12)
        score_title = QLabel("Voice Health Score")
        score_title.setObjectName("scoreTitle")
        self.score_value = QLabel("--")
        self.score_value.setObjectName("scoreValue")
        score_layout.addWidget(score_title)
        score_layout.addWidget(self.score_value)
        layout.addWidget(score_card)

        self.nav_dashboard.setChecked(True)
        self.nav_group.buttonClicked.connect(self._on_nav_clicked)

        return sidebar

    def _build_content(self) -> QFrame:
        content = QFrame()
        content.setObjectName("content")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(16)

        header_card = QFrame()
        header_card.setObjectName("card")
        header_layout = QVBoxLayout(header_card)
        header_layout.setContentsMargins(24, 20, 24, 20)
        title = QLabel(APP_TITLE)
        title.setObjectName("title")
        subtitle = QLabel("Clinical-style acoustic screening using classical ML")
        subtitle.setObjectName("subtitle")
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        content_layout.addWidget(header_card)

        self.stack = QStackedWidget()
        content_layout.addWidget(self.stack, 1)

        self.tiles_container = self._build_tiles_container()
        self.action_card = self._build_action_card()
        self.record_link_card = self._build_record_link_card()
        self.quality_card = self._build_quality_card()
        self.result_card = self._build_result_card()
        self.history_card = self._build_history_card()

        self.dashboard_page, self.dashboard_layout = self._create_page()
        self.record_page, self.record_layout = self._create_page()
        self.quality_page, self.quality_layout = self._create_page()
        self.results_page, self.results_layout = self._create_page()
        self.history_page, self.history_layout = self._create_page()

        self.stack.addWidget(self.dashboard_page)
        self.stack.addWidget(self.record_page)
        self.stack.addWidget(self.quality_page)
        self.stack.addWidget(self.results_page)
        self.stack.addWidget(self.history_page)

        return content

    def _create_page(self) -> tuple[QWidget, QVBoxLayout]:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        return page, layout

    def _clear_layout(self, layout: QVBoxLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)

    def _compose_page(self, layout: QVBoxLayout, widgets: list[QWidget]) -> None:
        self._clear_layout(layout)
        for widget in widgets:
            layout.addWidget(widget)
        layout.addStretch(1)

    def _set_page(self, index: int) -> None:
        if index == 0:
            self._compose_page(
                self.dashboard_layout,
                [self.tiles_container, self.record_link_card, self.result_card, self.history_card],
            )
        elif index == 1:
            self._compose_page(self.record_layout, [self.action_card])
        elif index == 2:
            self._compose_page(self.quality_layout, [self.quality_card])
        elif index == 3:
            self._compose_page(self.results_layout, [self.result_card, self.history_card])
        else:
            self._compose_page(self.history_layout, [self.history_card])

        self.stack.setCurrentIndex(index)

    def _go_to_record_page(self) -> None:
        self.nav_record.setChecked(True)
        self._set_page(1)

    def _on_nav_clicked(self, button: QPushButton) -> None:
        index = self.nav_group.id(button)
        self._set_page(index)

    def _build_tiles_container(self) -> QFrame:
        container = QFrame()
        container.setObjectName("tilesRow")
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        self.status_tile = self._create_tile("Model Status", "Checking...")
        self.mode_tile = self._create_tile("Input Mode", "WAV Audio")
        self.conf_tile = self._create_tile("Last Confidence", "--")
        layout.addWidget(self.status_tile)
        layout.addWidget(self.mode_tile)
        layout.addWidget(self.conf_tile)
        return container

    def _build_action_card(self) -> QFrame:
        action_card = QFrame()
        action_card.setObjectName("card")
        action_layout = QVBoxLayout(action_card)
        action_layout.setContentsMargins(24, 20, 24, 20)
        action_layout.setSpacing(18)

        mode_row = QHBoxLayout()
        mode_row.setSpacing(12)
        self.mode_label = QLabel("Input Mode")
        self.mode_label.setObjectName("fieldLabel")
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["WAV Audio", "CSV/XLSX Features"])
        self.mode_combo.currentIndexChanged.connect(self._switch_mode)
        mode_row.addWidget(self.mode_label)
        mode_row.addWidget(self.mode_combo, 1)

        self.wav_section = QFrame()
        wav_layout = QVBoxLayout(self.wav_section)
        wav_layout.setContentsMargins(0, 0, 0, 0)
        wav_layout.setSpacing(12)

        self.file_label = QLabel("No file selected")
        self.file_label.setObjectName("fileLabel")
        self.file_label.setWordWrap(True)
        self.file_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        wav_layout.addWidget(self.file_label)

        self.upload_btn = QPushButton("Upload Voice (.wav)")
        self.upload_btn.setObjectName("primaryButton")
        self.upload_btn.setMinimumWidth(180)
        self.upload_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.upload_btn.clicked.connect(self._select_file)
        wav_layout.addWidget(self.upload_btn)

        self.record_btn = QPushButton("Record Voice")
        self.record_btn.setObjectName("secondaryButton")
        self.record_btn.setMinimumWidth(180)
        self.record_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.record_btn.clicked.connect(self._record_audio)
        wav_layout.addWidget(self.record_btn)

        duration_row = QHBoxLayout()
        duration_label = QLabel("Duration")
        duration_label.setObjectName("fieldLabel")
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(2, 20)
        self.duration_spin.setValue(6)
        self.duration_spin.setSuffix(" s")
        self.duration_spin.setObjectName("durationSpin")
        self.duration_spin.setFixedWidth(120)
        duration_row.addWidget(duration_label)
        duration_row.addWidget(self.duration_spin)
        duration_row.addStretch(1)
        wav_layout.addLayout(duration_row)

        self.csv_section = QFrame()
        csv_layout = QVBoxLayout(self.csv_section)
        csv_layout.setContentsMargins(0, 0, 0, 0)
        csv_layout.setSpacing(12)

        self.csv_label = QLabel("No CSV selected")
        self.csv_label.setObjectName("fileLabel")
        self.csv_label.setWordWrap(True)
        self.csv_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        csv_layout.addWidget(self.csv_label)

        self.csv_btn = QPushButton("Upload CSV/XLSX")
        self.csv_btn.setObjectName("primaryButton")
        self.csv_btn.setMinimumWidth(180)
        self.csv_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.csv_btn.clicked.connect(self._select_csv)
        csv_layout.addWidget(self.csv_btn)

        row_row = QHBoxLayout()
        self.row_label = QLabel("Row Index")
        self.row_label.setObjectName("fieldLabel")
        self.row_spin = QSpinBox()
        self.row_spin.setRange(0, 100000)
        self.row_spin.setValue(0)
        self.row_spin.setFixedWidth(120)
        row_row.addWidget(self.row_label)
        row_row.addWidget(self.row_spin)
        row_row.addStretch(1)
        csv_layout.addLayout(row_row)

        self.model_status = QLabel("")
        self.model_status.setObjectName("statusHint")

        self.analyze_btn = QPushButton("Analyze")
        self.analyze_btn.setObjectName("accentButton")
        self.analyze_btn.setMinimumHeight(44)
        self.analyze_btn.setEnabled(False)
        self.analyze_btn.clicked.connect(self._run_analysis)

        action_layout.addLayout(mode_row)
        action_layout.addSpacing(10)
        action_layout.addWidget(self.wav_section)
        action_layout.addSpacing(10)
        action_layout.addWidget(self.csv_section)
        action_layout.addWidget(self.model_status)
        action_layout.addWidget(self.analyze_btn)
        return action_card

    def _build_record_link_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(10)

        title = QLabel("Record Voice")
        title.setObjectName("sectionTitle")
        subtitle = QLabel("Open the recording screen to upload or capture audio.")
        subtitle.setObjectName("subtitle")

        open_btn = QPushButton("Go to Record Voice")
        open_btn.setObjectName("accentButton")
        open_btn.setMinimumHeight(44)
        open_btn.clicked.connect(self._go_to_record_page)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(open_btn)
        return card

    def _build_quality_card(self) -> QFrame:
        quality_card = QFrame()
        quality_card.setObjectName("card")
        quality_layout = QVBoxLayout(quality_card)
        quality_layout.setContentsMargins(24, 20, 24, 20)
        quality_layout.setSpacing(14)

        title = QLabel("Quality Assessment")
        title.setObjectName("qualityTitle")
        self.quality_hint = QLabel("Upload or record a WAV file to view recording quality.")
        self.quality_hint.setObjectName("qualityHint")

        self.volume_metric = self._create_quality_metric("Volume Level")
        self.clarity_metric = self._create_quality_metric("Clarity")
        self.noise_metric = self._create_quality_metric("Background Noise")

        summary = QFrame()
        summary.setObjectName("qualitySummary")
        summary_layout = QVBoxLayout(summary)
        summary_layout.setContentsMargins(14, 12, 14, 12)
        summary_layout.setSpacing(4)
        self.quality_status = QLabel("Recording Quality: --")
        self.quality_status.setObjectName("qualityStatus")
        self.quality_detail = QLabel("Awaiting audio input.")
        self.quality_detail.setObjectName("qualityDetail")
        summary_layout.addWidget(self.quality_status)
        summary_layout.addWidget(self.quality_detail)

        quality_layout.addWidget(title)
        quality_layout.addWidget(self.quality_hint)
        quality_layout.addWidget(self.volume_metric["container"])
        quality_layout.addWidget(self.clarity_metric["container"])
        quality_layout.addWidget(self.noise_metric["container"])
        quality_layout.addWidget(summary)

        self._update_quality_view(None)
        return quality_card

    def _create_quality_metric(self, label_text: str) -> dict[str, QWidget]:
        container = QFrame()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        title = QLabel(label_text)
        title.setObjectName("qualityMetricTitle")
        bar = QProgressBar()
        bar.setObjectName("qualityBar")
        bar.setRange(0, 100)
        bar.setValue(0)
        bar.setTextVisible(False)
        rating = QLabel("--")
        rating.setObjectName("qualityRating")
        layout.addWidget(title)
        layout.addWidget(bar)
        layout.addWidget(rating)
        return {"container": container, "bar": bar, "rating": rating}

    def _build_result_card(self) -> QFrame:
        result_card = QFrame()
        result_card.setObjectName("card")
        result_layout = QVBoxLayout(result_card)
        result_layout.setContentsMargins(24, 20, 24, 20)
        result_layout.setSpacing(12)
        self.result_label = QLabel("Awaiting analysis...")
        self.result_label.setObjectName("resultLabel")
        self.result_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.assessment_label = QLabel("Health assessment will appear here.")
        self.assessment_label.setObjectName("assessmentLabel")
        self.assessment_label.setWordWrap(True)
        self.guidance_label = QLabel("This tool is not a medical diagnosis.")
        self.guidance_label.setObjectName("guidanceLabel")
        self.guidance_label.setWordWrap(True)
        self.confidence_bar = QProgressBar()
        self.confidence_bar.setRange(0, 100)
        self.confidence_bar.setValue(0)
        self.confidence_bar.setTextVisible(True)
        self.confidence_bar.setFormat("Confidence: %p%")
        self.confidence_bar.setObjectName("confidenceBar")
        result_layout.addWidget(self.result_label)
        result_layout.addWidget(self.assessment_label)
        result_layout.addWidget(self.guidance_label)
        result_layout.addWidget(self.confidence_bar)
        return result_card

    def _build_history_card(self) -> QFrame:
        history_card = QFrame()
        history_card.setObjectName("card")
        history_layout = QVBoxLayout(history_card)
        history_layout.setContentsMargins(24, 20, 24, 20)
        history_layout.setSpacing(12)
        history_title = QLabel("History")
        history_title.setObjectName("sectionTitle")
        self.history_list = QListWidget()
        self.history_list.setObjectName("historyList")
        history_layout.addWidget(history_title)
        history_layout.addWidget(self.history_list)
        return history_card

    def _nav_button(self, text: str, icon: QStyle.StandardPixmap, idx: int) -> QPushButton:
        button = QPushButton(text)
        button.setObjectName("navButton")
        button.setCheckable(True)
        button.setIcon(self.style().standardIcon(icon))
        self.nav_group.addButton(button, idx)
        return button

    def _create_tile(self, title: str, value: str) -> QFrame:
        tile = QFrame()
        tile.setObjectName("tile")
        layout = QVBoxLayout(tile)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)
        title_label = QLabel(title)
        title_label.setObjectName("tileTitle")
        value_label = QLabel(value)
        value_label.setObjectName("tileValue")
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        tile.value_label = value_label
        return tile

    def _apply_styles(self) -> None:
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
                "Could not load model artifacts.\n\n"
                "Add model_audio.joblib + scaler_audio.joblib for WAV mode, and\n"
                "model_csv.joblib + scaler_csv.joblib for CSV mode (or model.joblib + scaler.joblib).",
            )

    def _try_load_predictor(self, model_path: Path, scaler_path: Path) -> ParkinsonPredictor | None:
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
        self.status_tile.value_label.setText(status)
        hint = "Audio model missing. Train WAV model to enable analysis." if not audio_ok else ""
        if self.mode_combo.currentIndex() == 1 and not csv_ok:
            hint = "CSV model missing. Train CSV model to enable analysis."
        self.model_status.setText(hint)

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
        self.wav_section.setVisible(is_audio)
        self.csv_section.setVisible(not is_audio)

        self.mode_tile.value_label.setText("WAV Audio" if is_audio else "CSV/XLSX Features")
        self._update_model_status()
        self._refresh_analyze_state()
        if not is_audio:
            self._update_quality_view(None)
        elif self.audio_path:
            self._update_quality_view(self.audio_path)

    def _refresh_analyze_state(self) -> None:
        is_audio = self.mode_combo.currentIndex() == 0
        enabled = self.predictor_audio is not None if is_audio else self.predictor_csv is not None
        self.analyze_btn.setEnabled(enabled)
        if enabled:
            self.analyze_btn.setToolTip("")
        else:
            self.analyze_btn.setToolTip("Model not loaded for this mode.")

    def _record_audio(self) -> None:
        try:
            import sounddevice as sd
            import soundfile as sf
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(
                self,
                "Recording Error",
                f"Audio recording dependencies are missing.\n\n{exc}",
            )
            return

        duration = int(self.duration_spin.value())
        sample_rate = 22050
        record_dir = Path(__file__).resolve().parents[1] / "recordings"
        record_dir.mkdir(parents=True, exist_ok=True)
        output_path = record_dir / "recorded_voice.wav"

        try:
            recording = sd.rec(
                int(duration * sample_rate),
                samplerate=sample_rate,
                channels=1,
                dtype="float32",
            )
            sd.wait()
            sf.write(str(output_path), recording, sample_rate)

            self.audio_path = str(output_path)
            self.file_label.setText(output_path.name)
            self._update_quality_view(str(output_path))
            self._refresh_analyze_state()
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(
                self,
                "Recording Error",
                f"Failed to record audio.\n\n{exc}",
            )

    def _run_analysis(self) -> None:
        is_audio = self.mode_combo.currentIndex() == 0
        if is_audio and not self.audio_path:
            QMessageBox.warning(self, "No file", "Please upload or record a .wav file first.")
            return
        if not is_audio and not self.csv_path:
            QMessageBox.warning(self, "No file", "Please upload a CSV/XLSX file first.")
            return
        if is_audio and self.predictor_audio is None:
            QMessageBox.warning(
                self,
                "Model Missing",
                "Audio model is not available. Train the WAV model to enable analysis."
            )
            return
        if not is_audio and self.predictor_csv is None:
            QMessageBox.warning(
                self,
                "Model Missing",
                "CSV model is not available. Train the CSV model to enable analysis."
            )
            return

        try:
            if is_audio:
                result = self.predictor_audio.predict_file(self.audio_path)
                source = Path(self.audio_path).name
            else:
                features = self._load_csv_features(self.csv_path, self.row_spin.value())
                result = self.predictor_csv.predict_features(features)
                source = f"{Path(self.csv_path).name} [row {self.row_spin.value()}]"
            confidence_pct = int(round(result.confidence * 100))

            self.result_label.setText(result.label)
            assessment, guidance = self._build_assessment(result.label, confidence_pct)
            self.assessment_label.setText(assessment)
            self.guidance_label.setText(guidance)
            self.confidence_bar.setValue(confidence_pct)
            self.conf_tile.value_label.setText(f"{confidence_pct}%")
            self.score_value.setText(str(confidence_pct))
            self._append_history(result.label, confidence_pct, source)
            self.nav_results.setChecked(True)
            self._set_page(3)
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(
                self,
                "Analysis Error",
                f"Failed to analyze the input.\n\n{exc}",
            )

    @staticmethod
    def _build_assessment(label: str, confidence_pct: int) -> tuple[str, str]:
        if "park" in label.lower():
            severity = "High" if confidence_pct >= 80 else "Moderate" if confidence_pct >= 60 else "Low"
            assessment = (
                f"Assessment: {severity} likelihood of Parkinsonian voice patterns "
                f"based on this sample ({confidence_pct}%)."
            )
            guidance = (
                "This is a screening-style signal only. If you have symptoms or concerns, "
                "consider a clinical evaluation."
            )
        else:
            stability = "Strong" if confidence_pct >= 80 else "Moderate" if confidence_pct >= 60 else "Low"
            assessment = (
                f"Assessment: {stability} likelihood of healthy voice patterns "
                f"based on this sample ({confidence_pct}%)."
            )
            guidance = (
                "This is not a diagnosis. If you notice ongoing voice or motor changes, "
                "consider medical advice."
            )
        return assessment, guidance

    def _load_csv_features(self, file_path: str, row_index: int) -> list[float]:
        try:
            import pandas as pd
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError("CSV support requires pandas.") from exc

        path = Path(file_path)
        if path.suffix.lower() == ".xlsx":
            df = pd.read_excel(path)
        else:
            df = pd.read_csv(path)

        for col in ["status", "label", "target", "name", "id"]:
            if col in df.columns:
                df = df.drop(columns=[col])

        numeric = df.select_dtypes(include=["number"])
        if numeric.empty:
            raise ValueError("No numeric feature columns found in CSV/XLSX.")

        if row_index < 0 or row_index >= len(numeric):
            raise IndexError("Row index is out of range.")

        return numeric.iloc[row_index].to_numpy(dtype=np.float32)

    def _append_history(self, label: str, confidence: int, source: str) -> None:
        self.history.add(label, confidence, source)
        self._populate_history()

    def _update_quality_view(self, audio_path: str | None) -> None:
        if not audio_path:
            self.volume_metric["bar"].setValue(0)
            self.clarity_metric["bar"].setValue(0)
            self.noise_metric["bar"].setValue(0)
            self.volume_metric["rating"].setText("--")
            self.clarity_metric["rating"].setText("--")
            self.noise_metric["rating"].setText("--")
            self.quality_status.setText("Recording Quality: --")
            self.quality_detail.setText("Awaiting audio input.")
            return

        try:
            metrics = self._compute_quality_metrics(audio_path)
        except Exception as exc:  # noqa: BLE001
            self.quality_status.setText("Recording Quality: Unavailable")
            self.quality_detail.setText(f"Failed to read audio. {exc}")
            return

        volume = metrics["volume"]
        clarity = metrics["clarity"]
        noise = metrics["noise"]
        self.volume_metric["bar"].setValue(volume)
        self.clarity_metric["bar"].setValue(clarity)
        self.noise_metric["bar"].setValue(noise)
        self.volume_metric["rating"].setText(self._quality_rating(volume))
        self.clarity_metric["rating"].setText(self._quality_rating(clarity))
        self.noise_metric["rating"].setText(self._quality_rating(noise))

        average = int(round((volume + clarity + noise) / 3))
        status = "Excellent" if average >= 80 else "Acceptable" if average >= 60 else "Needs Improvement"
        self.quality_status.setText(f"Recording Quality: {status}")
        self.quality_detail.setText(f"Overall score: {average}% based on volume, clarity, and noise.")

    def _quality_rating(self, value: int) -> str:
        if value >= 70:
            return "Good"
        if value >= 45:
            return "Fair"
        return "Poor"

    def _compute_quality_metrics(self, audio_path: str) -> dict[str, int]:
        import librosa

        y, sr = librosa.load(audio_path, sr=22050, mono=True)
        if y.size == 0:
            raise ValueError("Audio file contains no samples.")

        rms = librosa.feature.rms(y=y)[0]
        rms_mean = float(np.mean(rms))
        volume = self._scale_score(rms_mean, low=0.01, high=0.09)

        flatness = librosa.feature.spectral_flatness(y=y)[0]
        clarity = int(np.clip((1.0 - float(np.mean(flatness))) * 100, 0, 100))

        rms_db = librosa.amplitude_to_db(rms, ref=np.max)
        noise_floor = float(np.percentile(rms_db, 10))
        signal_peak = float(np.percentile(rms_db, 95))
        snr = max(0.0, signal_peak - noise_floor)
        noise = self._scale_score(snr, low=8.0, high=30.0)

        return {"volume": volume, "clarity": clarity, "noise": noise}

    @staticmethod
    def _scale_score(value: float, low: float, high: float) -> int:
        if high <= low:
            return 0
        pct = (value - low) / (high - low)
        return int(np.clip(pct * 100, 0, 100))

    def _populate_history(self) -> None:
        self.history_list.clear()
        for entry in self.history.entries[:50]:
            item = QListWidgetItem(
                f"{entry.timestamp} • {entry.label} • {entry.confidence}% • {entry.source}"
            )
            self.history_list.addItem(item)


def create_app() -> QApplication:
    app = QApplication([])
    app.setFont(QFont("Segoe UI", 10))
    return app
