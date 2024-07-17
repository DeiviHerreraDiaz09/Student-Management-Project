from PyQt6 import uic, QtGui, QtWidgets, QtCore
from PyQt6.QtWidgets import QApplication, QMainWindow


class MainWindow:
    def __init__(self):
        super().__init__()
        self.main = uic.loadUi("gui/dashboard.ui")
        self.main.show()
