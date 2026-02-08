from __future__ import annotations

from ui.main_window import MainWindow, create_app


def main() -> None:
    app = create_app()
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()

