from PyQt6 import uic, QtGui
from data.user import UserData
from model.user import User

class Login:
    def __init__(self):
        self.login = uic.loadUi("gui/login.ui")
        pixmap = QtGui.QPixmap("logo.png")
        self.login.logoIcon.setPixmap(pixmap)
        self.initGUI()
        self.login.lblMSG.setText("")
        self.login.show()

    def ingresar(self):
        if len(self.login.txtDNI.text()) < 2:
            self.login.lblMSG.setText("Ingrese un usuario Válido")
            self.login.txtDNI.setFocus()
        elif len(self.login.txtPassword.text()) < 3:
            self.login.lblMSG.setText("Ingrese una contraseña Válida")
            self.login.txtPassword.setFocus()
        else:
            self.login.lblMSG.setText("")
            user = User(user_dni=self.login.txtDNI.text(), password=self.login.txtPassword.text())
            self.user_data = UserData()
            self.user_data.login_result.connect(self.handle_login_result)
            self.user_data.login(user)

    def handle_login_result(self, success):
        if success:
            self.login.lblMSG.setText("Login Correcto")
        else:
            self.login.lblMSG.setText("Datos incorrectos")

    def initGUI(self):
        self.login.btnAcceder.clicked.connect(self.ingresar)
