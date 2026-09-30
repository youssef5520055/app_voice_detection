def get_stylesheet() -> str:
    return """
    QWidget {
        font-family: 'Segoe UI Variable Display', 'Segoe UI', 'Inter', -apple-system, sans-serif;
        font-size: 14px;
        background-color: #0A0A0B;
        color: #F3F4F6;
    }
    QPushButton {
        color: #F3F4F6;
        min-height: 42px;
        padding: 0 20px;
        border-radius: 8px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    #sidebar {
        background-color: rgba(18, 18, 20, 0.95);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    #logo {
        color: #FFFFFF;
        font-size: 22px;
        font-weight: 800;
        letter-spacing: 1px;
    }
    #profileCard {
        background-color: rgba(255, 255, 255, 0.03);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    #profileName {
        color: #FFFFFF;
        font-weight: 700;
    }
    #profileMeta {
        color: #9CA3AF;
        font-size: 12px;
    }
    #navButton {
        padding: 12px 16px;
        border-radius: 8px;
        text-align: left;
        background-color: transparent;
        color: #9CA3AF;
        border: none;
        font-weight: 500;
    }
    #navButton:hover {
        background-color: rgba(255, 255, 255, 0.04);
        color: #E5E7EB;
    }
    #navButton:checked {
        background-color: rgba(212, 175, 55, 0.1);
        color: #D4AF37;
        border-left: 3px solid #D4AF37;
        border-top-left-radius: 0;
        border-bottom-left-radius: 0;
    }
    #scoreCard, #card, #tile, #qualitySummary {
        background-color: rgba(20, 20, 22, 0.7);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.06);
    }
    #scoreTitle, #subtitle, #tileTitle, #qualityHint, #qualityDetail, #disclaimer, #statusHint {
        color: #9CA3AF;
        font-size: 13px;
    }
    #scoreValue {
        color: #FFFFFF;
        font-size: 32px;
        font-weight: 800;
    }
    #title, #resultLabel {
        font-size: 28px;
        font-weight: 800;
        color: #FFFFFF;
        letter-spacing: -0.5px;
    }
    #fileLabel {
        padding: 12px;
        border: 1px dashed rgba(255, 255, 255, 0.15);
        border-radius: 8px;
        background-color: rgba(0, 0, 0, 0.2);
        color: #D1D5DB;
        min-height: 48px;
    }
    #primaryButton {
        background-color: #1F2937;
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #F9FAFB;
    }
    #primaryButton:hover {
        background-color: #374151;
    }
    #secondaryButton {
        background-color: transparent;
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #D1D5DB;
    }
    #secondaryButton:hover {
        background-color: rgba(255, 255, 255, 0.05);
        color: #FFFFFF;
    }
    #accentButton {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #B8860B, stop:1 #D4AF37);
        color: #000000;
        border: none;
    }
    #accentButton:hover {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #D4AF37, stop:1 #FDE047);
    }
    #accentButton:disabled {
        background-color: #374151;
        color: #6B7280;
    }
    #assessmentLabel, #qualityStatus, #tileValue, #sectionTitle, #qualityTitle {
        color: #F3F4F6;
        font-weight: 700;
        font-size: 16px;
    }
    #guidanceLabel, #qualityRating {
        color: #9CA3AF;
        font-size: 13px;
    }
    #confidenceBar, #qualityBar {
        height: 8px;
        border-radius: 4px;
        background: rgba(255, 255, 255, 0.05);
    }
    #confidenceBar::chunk, #qualityBar::chunk {
        border-radius: 4px;
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #D4AF37, stop:1 #FDE047);
    }
    #historyList {
        background: transparent;
        border: none;
        color: #D1D5DB;
    }
    #historyList::item {
        padding: 12px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    #historyList::item:hover {
        background-color: rgba(255, 255, 255, 0.02);
    }
    QComboBox, QSpinBox {
        background-color: rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 6px;
        padding: 8px 12px;
        color: #F3F4F6;
        min-height: 38px;
    }
    QComboBox::drop-down {
        border: none;
        width: 28px;
    }
    QComboBox QAbstractItemView {
        background-color: #111827;
        color: #F3F4F6;
        selection-background-color: #1F2937;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 6px;
    }
    """
