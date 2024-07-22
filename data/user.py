from PyQt6.QtCore import QObject, pyqtSignal, QThread
import conexion as con
from model.user import User


class LoginThread(QThread):
    login_result = pyqtSignal(bool)

    def __init__(self, user):
        super().__init__()
        self.user = user

    def run(self):
        db = con.Conexion().conectar()
        cursor = db.cursor()
        res = cursor.execute(
            "SELECT * FROM users WHERE user_dni = ? AND password = ?",
            (self.user._user_dni, self.user._password),
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
