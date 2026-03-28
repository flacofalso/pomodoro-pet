import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from pet_window import PetWindow


def main():
    # High-DPI support
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setApplicationName("Pomodoro Pet")
    app.setQuitOnLastWindowClosed(False)   # tray icon keeps it alive

    pet = PetWindow()
    pet.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
