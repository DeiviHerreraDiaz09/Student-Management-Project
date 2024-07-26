from PyQt6.QtWidgets import QApplication
from gui.interface2 import MyInterface


def main():
    app = QApplication([])
    login = MyInterface()
    app.exec()


if __name__ == "__main__":
    main()
