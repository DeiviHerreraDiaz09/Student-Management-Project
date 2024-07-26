from Services.userService import UserData, resolver_ruta
from PyQt6.QtWidgets import QMainWindow
from gui.UI.login import Ui_formLogin
from gui.main import MainWindow
from conexion import Conexion
from model.user import User
from PyQt6 import QtGui  

class MyInterface(QMainWindow, Ui_formLogin):

    
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("LOGIN")

        user_image_path = resolver_ruta("assets/img/user.png")
        book_image_path = resolver_ruta("assets/img/bookIcon.png")

        user = QtGui.QPixmap(user_image_path)
        book = QtGui.QPixmap(book_image_path)

        self.iconUser.setPixmap(user)
        self.bookIcon_2.setPixmap(book)

        self.initGUI()
        self.lblMSG.setText("")
        self.show()



    def ingresar(self):
        if len(self.txtUser.text()) < 2:
            self.lblMSG.setText("Ingrese un usuario Válido")
            self.txtUser.setFocus()
        elif len(self.txtPassword.text()) < 3:
            self.lblMSG.setText("Ingrese una contraseña Válida")
            self.txtPassword.setFocus()
        else:
            user = User(
                user_name=self.txtUser.text(),
                password=self.txtPassword.text(),
            )
            self.user_data = UserData()
            self.user_data.login_result.connect(self.handle_login_result)
            self.user_data.login(user)

    def handle_login_result(self, success):
        if success:
            self.lblMSG.setText("Login exitoso")
            self.conexion = Conexion()
            self.conexion.actualizar_estado_facturas()
            self.conexion.actualizar_grado_estudiantes()
            self.main = MainWindow()
            self.hide()
        else:
            self.lblMSG.setText("Datos incorrectos")

    def initGUI(self):
        self.btnAcceder.clicked.connect(self.ingresar)
