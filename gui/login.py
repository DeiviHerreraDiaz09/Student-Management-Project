from Services.userService import UserData
from gui.main import MainWindow
from DB.conexion import Conexion
from PyQt6 import uic, QtGui
from model.user import User


class Login:
    def __init__(self):
        self.login = uic.loadUi("gui/UI/login.ui")
        user = QtGui.QPixmap("./assets/img/user.png")
        book = QtGui.QPixmap("./assets/img/bookIcon.png")
        self.login.iconUser.setPixmap(user)
        self.login.bookIcon_2.setPixmap(book)
        self.initGUI()
        self.login.lblMSG.setText("")
        self.login.show()

    def ingresar(self):
        if len(self.login.txtUser.text()) < 2:
            self.login.lblMSG.setText("Ingrese un usuario Válido")
            self.login.txtUser.setFocus()
        elif len(self.login.txtPassword.text()) < 3:
            self.login.lblMSG.setText("Ingrese una contraseña Válida")
            self.login.txtPassword.setFocus()
        else:
            user = User(
                user_name=self.login.txtUser.text(),
                password=self.login.txtPassword.text(),
            )
            self.user_data = UserData()
            self.user_data.login_result.connect(self.handle_login_result)
            self.user_data.login(user)

    def handle_login_result(self, success):
        if success:
            self.login.lblMSG.setText("Login exitoso")
            self.conexion = Conexion()
            self.conexion.actualizar_estado_facturas()
            self.main = MainWindow()
            self.login.hide()
        else:
            self.login.lblMSG.setText("Datos incorrectos")

    def initGUI(self):
        self.login.btnAcceder.clicked.connect(self.ingresar)
