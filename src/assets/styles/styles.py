def get_stylesheet() -> str:
    tokens = {
        'bg_app': '#1C1C1E', # macOS dark mode window background
        'bg_sidebar': 'rgba(28, 28, 30, 0.8)',
        'bg_surface': '#2C2C2E', # Elevated card
        'bg_surface_hover': '#3A3A3C',
        'bg_surface_pressed': '#48484A',
        'text_primary': '#FFFFFF',
        'text_secondary': '#EBEBF5', # 60% opacity white
        'text_tertiary': '#EBEBF5', # 30% opacity white
        'accent_blue': '#0A84FF',
        'accent_green': '#32D74B',
        'accent_orange': '#FF9F0A',
        'accent_red': '#FF453A',
        'border_subtle': 'rgba(255, 255, 255, 0.1)',
        'border_strong': 'rgba(255, 255, 255, 0.15)',
        'radius_sm': '6px',
        'radius_md': '10px',
        'radius_lg': '14px',
        'radius_xl': '18px',
        'font_family': "'SF Pro Display', 'Segoe UI Variable Display', 'Segoe UI', -apple-system, sans-serif"
    }

    return f'''
    QWidget {{
        font-family: {tokens['font_family']};
        font-size: 14px;
        color: {tokens['text_primary']};
    }}
    QMainWindow {{
        background-color: {tokens['bg_app']};
    }}
    #mainContent {{
        background-color: {tokens['bg_app']};
    }}
    #sidebar {{
        background-color: {tokens['bg_sidebar']};
        border-right: 1px solid {tokens['border_subtle']};
    }}
    #sidebar QWidget {{
        background-color: transparent;
    }}
    #logo {{
        color: {tokens['text_primary']};
        font-size: 18px;
        font-weight: 700;
        letter-spacing: 0.5px;
    }}
    #navButton {{
        padding: 8px 12px;
        border-radius: {tokens['radius_sm']};
        text-align: left;
        background-color: transparent;
        color: {tokens['text_secondary']};
        border: none;
        font-weight: 500;
        font-size: 13px;
        margin: 2px 12px;
    }}
    #navButton:hover {{
        background-color: rgba(255, 255, 255, 0.05);
        color: {tokens['text_primary']};
    }}
    #navButton:checked {{
        background-color: {tokens['accent_blue']};
        color: #FFFFFF;
        font-weight: 600;
    }}
    #card, #tile, #qualitySummary, #actionCard, #profileCard {{
        background-color: {tokens['bg_surface']};
        border-radius: {tokens['radius_lg']};
        border: 1px solid {tokens['border_subtle']};
    }}
    #scoreCard {{
        background-color: {tokens['bg_surface']};
        border-radius: {tokens['radius_xl']};
        border: 1px solid {tokens['border_subtle']};
    }}
    #pageTitle {{
        font-size: 32px;
        font-weight: 700;
        color: {tokens['text_primary']};
        margin-bottom: 8px;
    }}
    #sectionTitle {{
        font-size: 18px;
        font-weight: 600;
        color: {tokens['text_primary']};
        margin-top: 16px;
        margin-bottom: 8px;
    }}
    #subtitle, #disclaimer, #statusHint, #qualityHint, #qualityDetail, #tileTitle, #scoreTitle {{
        font-size: 13px;
        color: rgba(235, 235, 245, 0.6);
    }}
    #scoreValue {{
        color: {tokens['text_primary']};
        font-size: 48px;
        font-weight: 700;
        letter-spacing: -1px;
    }}
    #tileValue {{
        color: {tokens['text_primary']};
        font-size: 20px;
        font-weight: 600;
    }}
    QPushButton {{
        padding: 8px 16px;
        border-radius: {tokens['radius_md']};
        font-weight: 600;
        font-size: 13px;
    }}
    #primaryButton {{
        background-color: {tokens['accent_blue']};
        color: #FFFFFF;
        border: none;
    }}
    #primaryButton:hover {{
        background-color: #007AFF;
    }}
    #primaryButton:pressed {{
        background-color: #0066CC;
    }}
    #secondaryButton {{
        background-color: {tokens['bg_surface_hover']};
        color: {tokens['text_primary']};
        border: 1px solid {tokens['border_subtle']};
    }}
    #secondaryButton:hover {{
        background-color: {tokens['bg_surface_pressed']};
    }}
    #dangerButton {{
        background-color: {tokens['accent_red']};
        color: #FFFFFF;
        border: none;
    }}
    #dangerButton:hover {{
        background-color: #FF3B30;
    }}
    #fileLabel {{
        padding: 16px;
        border: 1px dashed {tokens['border_strong']};
        border-radius: {tokens['radius_md']};
        background-color: rgba(0, 0, 0, 0.2);
        color: {tokens['text_secondary']};
        font-size: 13px;
    }}
    QProgressBar {{
        height: 6px;
        border-radius: 3px;
        background-color: rgba(255, 255, 255, 0.1);
        border: none;
        text-align: right;
        color: transparent;
    }}
    QProgressBar::chunk {{
        border-radius: 3px;
        background-color: {tokens['accent_green']};
    }}
    #confidenceBar::chunk {{
        background-color: {tokens['accent_blue']};
    }}
    #historyList {{
        background-color: transparent;
        border: none;
        outline: none;
    }}
    #historyList::item {{
        background-color: {tokens['bg_surface']};
        border-radius: {tokens['radius_md']};
        margin-bottom: 8px;
        padding: 12px;
        border: 1px solid {tokens['border_subtle']};
    }}
    #historyList::item:hover {{
        background-color: {tokens['bg_surface_hover']};
    }}
    #historyList::item:selected {{
        background-color: {tokens['bg_surface_pressed']};
        border: 1px solid {tokens['accent_blue']};
    }}
    QComboBox, QSpinBox, QDoubleSpinBox {{
        background-color: {tokens['bg_surface']};
        border: 1px solid {tokens['border_subtle']};
        border-radius: {tokens['radius_sm']};
        padding: 6px 10px;
        color: {tokens['text_primary']};
        min-height: 32px;
    }}
    QComboBox::drop-down {{
        border: none;
        width: 24px;
    }}
    QComboBox::down-arrow {{
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 5px solid {tokens['text_secondary']};
        margin-right: 8px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {tokens['bg_surface_hover']};
        color: {tokens['text_primary']};
        selection-background-color: {tokens['accent_blue']};
        border: 1px solid {tokens['border_subtle']};
        border-radius: {tokens['radius_sm']};
        outline: none;
    }}
    QScrollBar:vertical {{
        border: none;
        background-color: transparent;
        width: 8px;
        margin: 0px 0px 0px 0px;
    }}
    QScrollBar::handle:vertical {{
        background-color: rgba(255, 255, 255, 0.2);
        min-height: 30px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical:hover {{
        background-color: rgba(255, 255, 255, 0.3);
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
        background: none;
    }}
    '''
