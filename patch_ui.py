import re

with open('src/components/main_window.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Define replacement methods
replacement = '''    def _build_ui(self) -> None:
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
        upload_btn.clicked.connect(self._upload_audio)
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
        c_upload_btn.clicked.connect(self._upload_csv)
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
'''

# Use regex to replace the UI building methods
content = re.sub(r'    def _build_ui\(self\) -> None:.*?def _build_history_card\(self\) -> QFrame:.*?(?=    def _switch_mode)', replacement + '\n', content, flags=re.DOTALL)

with open('src/components/main_window.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Patch applied successfully.')
