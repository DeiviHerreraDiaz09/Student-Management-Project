from PyQt6 import uic, QtGui, QtWidgets, QtCore
from PyQt6.QtWidgets import QApplication, QMainWindow
from gui.interface import MyInterface


class MainWindow:
    def __init__(self):
        self.app = QApplication([])
        self.interface = MyInterface()
        self.interface.show()
        self.app.exec()

if __name__ == "__main__":
    main_window = MainWindow()
