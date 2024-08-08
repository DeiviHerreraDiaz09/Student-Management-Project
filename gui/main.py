from PyQt6.QtWidgets import QMainWindow
from gui.interface import MyInterface


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.interface = MyInterface()
        self.interface.show()

    def set_user_role(self, object):
        self.interface.set_user_role(object)
