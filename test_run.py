import sys
import time
from pathlib import Path

# Add src to pythonpath
sys.path.insert(0, str(Path('./src').resolve()))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from components.main_window import MainWindow, create_app

def main():
    app = create_app()
    window = MainWindow()
    window.show()
    
    # Timer to close the application successfully after 2 seconds
    QTimer.singleShot(2000, app.quit)
    
    print('Application started successfully. Exiting after 2 seconds...')
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
