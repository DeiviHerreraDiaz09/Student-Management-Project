import sys
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
    app = QApplication(sys.argv)
    main_window = MainWindow()
    app.aboutToQuit.connect(app.quit)
    sys.exit(app.exec_())