from PyQt6.QtWidgets import QApplication
from gui.login import Login


class School:
    def __init__(self):
        self.app = QApplication([])
        self.login = Login()
        self.app.exec()


if __name__ == "__main__":
    School()
