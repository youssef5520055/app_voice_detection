from __future__ import annotations


def get_stylesheet() -> str:
    return """
    QWidget {
        font-family: "Segoe UI", "Arial";
        font-size: 14px;
        background-color: #0E1116;
        color: #E6EDF3;
    }
    QPushButton {
        color: #E6EDF3;
        min-height: 38px;
        padding: 0 16px;
        border-radius: 16px;
    }
    #sidebar {
        background-color: #0B1E2B;
        border-radius: 18px;
    }
    #logo {
        color: #EAF1F8;
        font-size: 20px;
        font-weight: 700;
    }
    #profileCard {
        background-color: #122B3D;
        border-radius: 12px;
    }
    #profileName {
        color: #FFFFFF;
        font-weight: 600;
    }
    #profileMeta {
        color: #B7C8D7;
        font-size: 12px;
    }
    #navButton {
        padding: 10px 12px;
        border-radius: 10px;
        text-align: left;
        background-color: transparent;
        color: #DCE7F2;
        border: none;
        font-weight: 600;
    }
    #navButton:hover {
        background-color: #16354A;
    }
    #navButton:checked {
        background-color: #1E4866;
        color: #FFFFFF;
    }
    #scoreCard {
        background-color: #122B3D;
        border-radius: 12px;
    }
    #scoreTitle {
        color: #9FB2C3;
        font-size: 12px;
    }
    #scoreValue {
        color: #FFFFFF;
        font-size: 22px;
        font-weight: 700;
    }
    #card {
        background-color: #121821;
        border-radius: 16px;
        border: 1px solid #1E2A36;
    }
    #title {
        font-size: 26px;
        font-weight: 700;
        color: #EAF1F8;
    }
    #subtitle {
        font-size: 14px;
        color: #9AA9B7;
    }
    #fileLabel {
        padding: 10px;
        border: 1px dashed #2E3A48;
        border-radius: 10px;
        background-color: #0F1720;
        color: #D8E1EA;
        min-height: 40px;
        qproperty-alignment: "AlignVCenter|AlignLeft";
    }
    #primaryButton, #accentButton {
        padding: 10px 18px;
        border-radius: 18px;
        border: none;
        font-weight: 600;
    }
    #primaryButton, #secondaryButton, #accentButton {
        min-height: 44px;
    }
    #primaryButton {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                          stop:0 #1F2C3B, stop:1 #0E1B29);
        color: #E6EDF3;
    }
    #primaryButton:hover {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                          stop:0 #2A3C50, stop:1 #172636);
    }
    #secondaryButton {
        padding: 10px 18px;
        border-radius: 18px;
        border: 1px solid #2E3A48;
        background-color: #0E1722;
        color: #E6EDF3;
        font-weight: 600;
    }
    #secondaryButton:hover {
        background-color: #172636;
    }
    #accentButton {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #22D3EE, stop:1 #3B82F6);
        color: #FFFFFF;
    }
    #accentButton:hover {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #38BDF8, stop:1 #2563EB);
    }
    #accentButton:disabled {
        background-color: #1C2B3A;
        color: #7C8B98;
    }
    #resultLabel {
        font-size: 22px;
        font-weight: 700;
        color: #EAF1F8;
    }
    #assessmentLabel {
        color: #C7D2DC;
        font-size: 14px;
    }
    #guidanceLabel {
        color: #8A98A7;
        font-size: 12px;
    }
    #confidenceBar {
        height: 24px;
        border-radius: 8px;
        background: #0F1720;
        text-align: center;
        color: #E6EDF3;
    }
    #confidenceBar::chunk {
        border-radius: 8px;
        background-color: #22C55E;
    }
    #disclaimer {
        color: #8A98A7;
        font-size: 12px;
    }
    #fieldLabel {
        color: #C7D2DC;
        font-weight: 600;
    }
    #tile {
        background-color: #121821;
        border-radius: 14px;
        border: 1px solid #1E2A36;
    }
    #tileTitle {
        color: #9AA9B7;
        font-size: 12px;
    }
    #tileValue {
        color: #EAF1F8;
        font-size: 18px;
        font-weight: 700;
    }
    #sectionTitle {
        font-size: 18px;
        font-weight: 700;
        color: #EAF1F8;
    }
    #historyList {
        background: #0F1720;
        border-radius: 12px;
        padding: 8px;
        color: #E6EDF3;
    }
    #qualityTitle {
        font-size: 18px;
        font-weight: 700;
        color: #EAF1F8;
    }
    #qualityHint {
        color: #9AA9B7;
        font-size: 12px;
    }
    #qualityMetricTitle {
        color: #C7D2DC;
        font-weight: 600;
    }
    #qualityRating {
        color: #9FB2C3;
        font-size: 12px;
    }
    #qualityBar {
        height: 12px;
        border-radius: 6px;
        background: #0F1720;
    }
    #qualityBar::chunk {
        border-radius: 6px;
        background-color: #38BDF8;
    }
    #qualitySummary {
        background-color: #0F1720;
        border-radius: 12px;
        border: 1px solid #1E2A36;
    }
    #qualityStatus {
        color: #EAF1F8;
        font-weight: 700;
    }
    #qualityDetail {
        color: #9AA9B7;
        font-size: 12px;
    }
    QComboBox, QSpinBox {
        background-color: #0F1720;
        border: 1px solid #2E3A48;
        border-radius: 8px;
        padding: 6px 10px;
        color: #E6EDF3;
        min-height: 34px;
    }
    QComboBox::drop-down {
        border: none;
        width: 24px;
    }
    QComboBox QAbstractItemView {
        background-color: #0F1720;
        color: #E6EDF3;
        selection-background-color: #24384C;
    }
    #statusHint {
        color: #8A98A7;
        font-size: 12px;
    }
    """
