from PyQt6.QtCore import QObject, pyqtSignal, QThread
from model.user import User
import conexion as con
import os
import sys


class LoginThread(QThread):
    login_result = pyqtSignal(bool)

    def __init__(self, user):
        super().__init__()
        self.user = user

    def run(self):
        db = con.Conexion().conectar()
        cursor = db.cursor()
        res = cursor.execute(
            "SELECT * FROM users WHERE user_name = ? AND password = ?",
            (self.user._user_name, self.user._password),
        )
        fila = res.fetchone()
        if fila:
            self.login_result.emit(True)
        else:
            self.login_result.emit(False)
        db.close()


class UserData(QObject):
    login_result = pyqtSignal(bool)

    def login(self, user: User):
        self.thread = LoginThread(user)
        self.thread.login_result.connect(self.handle_login_result)
        self.thread.start()

    def handle_login_result(self, success):
        self.login_result.emit(success)


def resolver_ruta(ruta_relativa):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, ruta_relativa)
        return os.path.join(os.path.abspath('.'), ruta_relativa)