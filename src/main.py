from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from components.main_window import MainWindow, create_app

def main() -> None:
    app = create_app()
    window = MainWindow()
    window.show()
    app.exec()

if __name__ == '__main__':
    main()
