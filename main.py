from PyQt6.QtWidgets import QApplication
from gui.login import Login


def main():
    app = QApplication([])
    login = Login()
    app.exec()


if __name__ == "__main__":
    main()
