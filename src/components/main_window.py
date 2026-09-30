from __future__ import annotations

from pathlib import Path

import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from PySide6.QtCore import QThread, Signal

class RecordThread(QThread):
    finished_recording = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, duration, sample_rate, output_path):
        super().__init__()
        self.duration = duration
        self.sample_rate = sample_rate
        self.output_path = output_path

    def run(self):
        try:
            import sounddevice as sd
            import soundfile as sf
            recording = sd.rec(
                int(self.duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1,
                dtype="float32",
            )
            sd.wait()
            sf.write(str(self.output_path), recording, self.sample_rate)
            self.finished_recording.emit(str(self.output_path))
        except Exception as exc:
            self.error_occurred.emit(str(exc))

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

from services.predictor import ParkinsonPredictor
from utils.helpers import default_dialog_dir, resource_path
from components.history_view import HistoryStore
from assets.styles.styles import get_stylesheet


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
        container.setObjectName("mainContent")
        root = QHBoxLayout(container)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        sidebar = self._build_sidebar()
        content = self._build_content()

        root.addWidget(sidebar)
        root.addWidget(content, 1)
        self.setCentralWidget(container)

        self._populate_history()
        self._switch_mode()
        self._set_page(0)

    def _nav_button(self, text: str, icon_style: QStyle.StandardPixmap, id: int) -> QPushButton:
        btn = QPushButton(text)
        btn.setObjectName("navButton")
        btn.setCheckable(True)
        self.nav_group.addButton(btn, id)
        return btn

    def _build_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(240)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(16, 32, 16, 32)
        layout.setSpacing(8)

        logo = QLabel("Voice Health")
        logo.setObjectName("logo")
        logo.setContentsMargins(12, 0, 12, 24)
        layout.addWidget(logo)

        nav = QFrame()
        nav_layout = QVBoxLayout(nav)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(4)
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

        self.nav_dashboard = self._nav_button("Overview", QStyle.SP_ComputerIcon, 0)
        self.nav_record = self._nav_button("Record Voice", QStyle.SP_MediaPlay, 1)
        self.nav_quality = self._nav_button("Quality", QStyle.SP_FileDialogDetailedView, 2)
        self.nav_results = self._nav_button("Analysis", QStyle.SP_FileDialogContentsView, 3)
        self.nav_history = self._nav_button("History", QStyle.SP_FileDialogListView, 4)
        
        for btn in [self.nav_dashboard, self.nav_record, self.nav_quality, self.nav_results, self.nav_history]:
            nav_layout.addWidget(btn)
            
        layout.addWidget(nav)
        layout.addStretch(1)

        score_card = QFrame()
        score_card.setObjectName("scoreCard")
        score_layout = QVBoxLayout(score_card)
        score_layout.setContentsMargins(16, 20, 16, 20)
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
        content_layout.setContentsMargins(40, 40, 40, 40)
        content_layout.setSpacing(24)

        header = QWidget()
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 16)
        header_layout.setSpacing(4)
        self.page_title = QLabel(APP_TITLE)
        self.page_title.setObjectName("pageTitle")
        self.page_subtitle = QLabel("Clinical-style acoustic screening")
        self.page_subtitle.setObjectName("subtitle")
        header_layout.addWidget(self.page_title)
        header_layout.addWidget(self.page_subtitle)
        content_layout.addWidget(header)

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
        layout.setSpacing(24)
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
        titles = ["Overview", "Record Voice", "Audio Quality", "Voice Analysis", "History"]
        subtitles = [
            "Your recent acoustic health summary",
            "Record a short voice sample for acoustic analysis",
            "Detailed acoustic signal metrics",
            "Research-grade analysis of acoustic features",
            "Past recordings and acoustic health scores"
        ]
        self.page_title.setText(titles[index])
        self.page_subtitle.setText(subtitles[index])
        
        if index == 0:
            self._compose_page(
                self.dashboard_layout,
                [self.tiles_container, self.record_link_card, self.result_card],
            )
        elif index == 1:
            self._compose_page(self.record_layout, [self.action_card])
        elif index == 2:
            self._compose_page(self.quality_layout, [self.quality_card])
        elif index == 3:
            self._compose_page(self.results_layout, [self.result_card])
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
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        self.status_tile = self._create_tile("Model Status", "Checking...")
        self.mode_tile = self._create_tile("Input Mode", "WAV Audio")
        self.conf_tile = self._create_tile("Last Score", "--")
        layout.addWidget(self.status_tile)
        layout.addWidget(self.mode_tile)
        layout.addWidget(self.conf_tile)
        return container

    def _create_tile(self, title_text: str, value_text: str) -> QFrame:
        tile = QFrame()
        tile.setObjectName("tile")
        layout = QVBoxLayout(tile)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(8)
        title = QLabel(title_text)
        title.setObjectName("tileTitle")
        value = QLabel(value_text)
        value.setObjectName("tileValue")
        value.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(value)
        tile.value_label = value
        return tile

    def _build_record_link_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        layout = QHBoxLayout(card)
        layout.setContentsMargins(24, 24, 24, 24)
        
        text_layout = QVBoxLayout()
        title = QLabel("Record Voice")
        title.setObjectName("sectionTitle")
        title.setContentsMargins(0, 0, 0, 0)
        subtitle = QLabel("Open the recording interface to upload or capture a voice sample.")
        subtitle.setObjectName("subtitle")
        text_layout.addWidget(title)
        text_layout.addWidget(subtitle)
        
        open_btn = QPushButton("Go to Record Voice")
        open_btn.setObjectName("primaryButton")
        open_btn.clicked.connect(self._go_to_record_page)
        
        layout.addLayout(text_layout)
        layout.addStretch(1)
        layout.addWidget(open_btn)
        return card

    def _build_action_card(self) -> QFrame:
        action_card = QFrame()
        action_card.setObjectName("actionCard")
        layout = QVBoxLayout(action_card)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(12)
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["WAV Audio", "CSV / XLSX"])
        self.mode_combo.currentIndexChanged.connect(self._switch_mode)
        controls_layout.addWidget(QLabel("Input Type:"))
        controls_layout.addWidget(self.mode_combo)
        controls_layout.addStretch(1)
        layout.addLayout(controls_layout)

        self.audio_widget = QWidget()
        audio_layout = QVBoxLayout(self.audio_widget)
        audio_layout.setContentsMargins(0, 0, 0, 0)
        audio_layout.setSpacing(24)
        
        # Apple Voice Memos style recording area
        record_area = QFrame()
        record_area.setObjectName("card")
        record_area_layout = QVBoxLayout(record_area)
        record_area_layout.setContentsMargins(0, 40, 0, 40)
        record_area_layout.setAlignment(Qt.AlignCenter)
        
        self.record_waveform = QLabel("~ ~ ~ ~ ~ ~ ~ ~ ~ ~")
        self.record_waveform.setObjectName("title")
        self.record_waveform.setAlignment(Qt.AlignCenter)
        self.record_waveform.setStyleSheet("color: #48484A; font-size: 24px;")
        record_area_layout.addWidget(self.record_waveform)
        
        self.record_btn = QPushButton("?")
        self.record_btn.setFixedSize(64, 64)
        self.record_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 4px solid #32D74B;
                border-radius: 32px;
                color: #FF453A;
                font-size: 24px;
            }
            QPushButton:hover { background-color: rgba(255,69,58,0.1); }
        """)
        self.record_btn.clicked.connect(self._record_audio)
        record_area_layout.addWidget(self.record_btn, 0, Qt.AlignCenter)
        
        dur_layout = QHBoxLayout()
        dur_layout.setAlignment(Qt.AlignCenter)
        dur_layout.addWidget(QLabel("Duration (s):"))
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 60)
        self.duration_spin.setValue(5)
        self.duration_spin.setFixedWidth(80)
        dur_layout.addWidget(self.duration_spin)
        record_area_layout.addLayout(dur_layout)
        
        audio_layout.addWidget(record_area)

        file_layout = QHBoxLayout()
        self.file_label = QLabel("No file selected")
        self.file_label.setObjectName("fileLabel")
        upload_btn = QPushButton("Upload File")
        upload_btn.setObjectName("secondaryButton")
        upload_btn.clicked.connect(self._select_file)
        file_layout.addWidget(self.file_label, 1)
        file_layout.addWidget(upload_btn)
        audio_layout.addLayout(file_layout)

        self.csv_widget = QWidget()
        csv_layout = QVBoxLayout(self.csv_widget)
        csv_layout.setContentsMargins(0, 0, 0, 0)
        csv_layout.setSpacing(16)
        c_file_layout = QHBoxLayout()
        self.csv_label = QLabel("No CSV/XLSX selected")
        self.csv_label.setObjectName("fileLabel")
        c_upload_btn = QPushButton("Upload CSV")
        c_upload_btn.setObjectName("secondaryButton")
        c_upload_btn.clicked.connect(self._select_csv)
        c_file_layout.addWidget(self.csv_label, 1)
        c_file_layout.addWidget(c_upload_btn)
        csv_layout.addLayout(c_file_layout)

        row_layout = QHBoxLayout()
        row_layout.addWidget(QLabel("Row Index:"))
        self.row_spin = QSpinBox()
        self.row_spin.setMinimum(0)
        self.row_spin.setMaximum(999999)
        row_layout.addWidget(self.row_spin)
        row_layout.addStretch(1)
        csv_layout.addLayout(row_layout)

        layout.addWidget(self.audio_widget)
        layout.addWidget(self.csv_widget)
        
        analyze_area = QHBoxLayout()
        analyze_area.addStretch(1)
        self.analyze_btn = QPushButton("Analyze Voice")
        self.analyze_btn.setObjectName("accentButton")
        self.analyze_btn.setMinimumWidth(200)
        self.analyze_btn.clicked.connect(self._run_analysis)
        analyze_area.addWidget(self.analyze_btn)
        layout.addLayout(analyze_area)

        return action_card

    def _build_quality_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        header = QLabel("Audio Quality")
        header.setObjectName("sectionTitle")
        header.setContentsMargins(0,0,0,0)
        hint = QLabel("Acoustic signal clarity and background noise assessment")
        hint.setObjectName("subtitle")
        layout.addWidget(header)
        layout.addWidget(hint)

        self.quality_status = QLabel("Recording Quality: --")
        self.quality_status.setObjectName("qualityStatus")
        self.quality_detail = QLabel("Awaiting audio input.")
        self.quality_detail.setObjectName("qualityDetail")
        layout.addWidget(self.quality_status)
        layout.addWidget(self.quality_detail)

        self.volume_metric = self._build_quality_metric("Signal Volume", layout)
        self.clarity_metric = self._build_quality_metric("Acoustic Clarity", layout)
        self.noise_metric = self._build_quality_metric("Signal-to-Noise", layout)

        return card

    def _build_quality_metric(self, name: str, parent_layout: QVBoxLayout) -> dict:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        row = QHBoxLayout()
        title = QLabel(name)
        title.setObjectName("tileValue")
        title.setStyleSheet("font-size: 14px;")
        rating = QLabel("--")
        rating.setObjectName("qualityRating")
        row.addWidget(title)
        row.addStretch(1)
        row.addWidget(rating)

        bar = QProgressBar()
        bar.setObjectName("qualityBar")
        bar.setRange(0, 100)
        bar.setValue(0)
        bar.setTextVisible(False)

        layout.addLayout(row)
        layout.addWidget(bar)
        parent_layout.addWidget(container)
        return {"bar": bar, "rating": rating}

    def _build_result_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        header = QLabel("Overall Result")
        header.setObjectName("sectionTitle")
        header.setContentsMargins(0,0,0,0)
        layout.addWidget(header)

        score_row = QHBoxLayout()
        self.result_label = QLabel("Awaiting Analysis")
        self.result_label.setObjectName("resultLabel")
        
        score_val_layout = QVBoxLayout()
        score_title = QLabel("Voice Score")
        score_title.setObjectName("subtitle")
        score_val_layout.addWidget(self.result_label)
        score_val_layout.addWidget(score_title)
        score_row.addLayout(score_val_layout)
        score_row.addStretch(1)
        layout.addLayout(score_row)

        self.confidence_bar = QProgressBar()
        self.confidence_bar.setObjectName("confidenceBar")
        self.confidence_bar.setRange(0, 100)
        self.confidence_bar.setValue(0)
        self.confidence_bar.setTextVisible(False)
        layout.addWidget(self.confidence_bar)

        self.assessment_label = QLabel("")
        self.assessment_label.setObjectName("assessmentLabel")
        self.assessment_label.setWordWrap(True)
        self.guidance_label = QLabel("")
        self.guidance_label.setObjectName("guidanceLabel")
        self.guidance_label.setWordWrap(True)
        layout.addWidget(self.assessment_label)
        layout.addWidget(self.guidance_label)

        disclaimer = QLabel("This is an acoustic screening research tool. Not a medical diagnosis.")
        disclaimer.setObjectName("disclaimer")
        layout.addWidget(disclaimer)

        return card

    def _build_history_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.history_list = QListWidget()
        self.history_list.setObjectName("historyList")
        layout.addWidget(self.history_list)
        return card

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
        except Exception as exc:
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
        
        # UI Feedback
        for btn in self.findChildren(QPushButton):
            if btn.text() == "Record Audio":
                btn.setEnabled(False)
                btn.setText("Recording...")
                self._current_rec_btn = btn
                break

        self.record_thread = RecordThread(duration, sample_rate, output_path)
        self.record_thread.finished_recording.connect(self._on_record_finished)
        self.record_thread.error_occurred.connect(self._on_record_error)
        self.record_thread.start()

    def _on_record_finished(self, output_path_str: str) -> None:
        if hasattr(self, '_current_rec_btn') and self._current_rec_btn:
            self._current_rec_btn.setEnabled(True)
            self._current_rec_btn.setText("Record Audio")

        output_path = Path(output_path_str)
        self.audio_path = str(output_path)
        self.file_label.setText(output_path.name)
        self._update_quality_view(str(output_path))
        self._refresh_analyze_state()

    def _on_record_error(self, exc: str) -> None:
        if hasattr(self, '_current_rec_btn') and self._current_rec_btn:
            self._current_rec_btn.setEnabled(True)
            self._current_rec_btn.setText("Record Audio")
        QMessageBox.critical(self, "Recording Error", f"Failed to record audio.\n\n{exc}")

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



