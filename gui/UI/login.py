from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_formLogin(object):
    def setupUi(self, formLogin):
        formLogin.setObjectName("formLogin")
        formLogin.resize(804, 471)
        formLogin.setStyleSheet("background-color: white;\n" "")
        self.label_3 = QtWidgets.QLabel(parent=formLogin)
        self.label_3.setGeometry(QtCore.QRect(490, 230, 91, 21))
        font = QtGui.QFont()
        font.setFamily("Leelawadee")
        font.setPointSize(12)
        self.label_3.setFont(font)
        self.label_3.setStyleSheet("color: rgb(0, 0, 0);")
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(parent=formLogin)
        self.label_4.setGeometry(QtCore.QRect(460, 280, 121, 21))
        font = QtGui.QFont()
        font.setFamily("Leelawadee")
        font.setPointSize(12)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.txtUser = QtWidgets.QLineEdit(parent=formLogin)
        self.txtUser.setGeometry(QtCore.QRect(580, 230, 171, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.txtUser.setFont(font)
        self.txtUser.setStyleSheet(
            "padding: 3%;\n"
            "border-radius: 8px;\n"
            "border: 1px solid black;\n"
            "color: rgb(0, 0, 0);"
        )
        self.txtUser.setObjectName("txtUser")
        self.txtPassword = QtWidgets.QLineEdit(parent=formLogin)
        self.txtPassword.setGeometry(QtCore.QRect(580, 280, 171, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.txtPassword.setFont(font)
        self.txtPassword.setStyleSheet(
            "padding: 3%;\n"
            "border-radius: 8px;\n"
            "border: 1px solid black;\n"
            "color: rgb(0, 0, 0);"
        )
        self.txtPassword.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.txtPassword.setObjectName("txtPassword")
        self.btnAcceder = QtWidgets.QPushButton(parent=formLogin)
        self.btnAcceder.setGeometry(QtCore.QRect(550, 340, 101, 31))
        self.btnAcceder.setMaximumSize(QtCore.QSize(200, 16777215))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.btnAcceder.setFont(font)
        self.btnAcceder.setCursor(
            QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        )
        self.btnAcceder.setStyleSheet(
            "background-color: rgb(255, 255, 255); color: black;\n"
            "border-radius: 8px;\n"
            "border: 1px solid black;\n"
            ""
        )
        self.btnAcceder.setCheckable(False)
        self.btnAcceder.setObjectName("btnAcceder")
        self.lblMSG = QtWidgets.QLabel(parent=formLogin)
        self.lblMSG.setGeometry(QtCore.QRect(440, 400, 341, 41))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lblMSG.setFont(font)
        self.lblMSG.setStyleSheet("color: red;")
        self.lblMSG.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.lblMSG.setObjectName("lblMSG")
        self.iconUser = QtWidgets.QLabel(parent=formLogin)
        self.iconUser.setGeometry(QtCore.QRect(550, 70, 141, 131))
        self.iconUser.setText("")
        self.iconUser.setPixmap(QtGui.QPixmap(":/xy/user.png"))
        self.iconUser.setScaledContents(True)
        self.iconUser.setObjectName("iconUser")
        self.frame = QtWidgets.QFrame(parent=formLogin)
        self.frame.setGeometry(QtCore.QRect(0, -20, 411, 541))
        self.frame.setStyleSheet("background-color: rgb(34, 162, 242);")
        self.frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame.setObjectName("frame")
        self.bookIcon = QtWidgets.QFrame(parent=self.frame)
        self.bookIcon.setGeometry(QtCore.QRect(100, 170, 200, 200))
        self.bookIcon.setStyleSheet(
            "border-radius: 100px;\n" "background-color: rgb(255, 255, 255);\n" ""
        )
        self.bookIcon.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.bookIcon.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.bookIcon.setObjectName("bookIcon")
        self.bookIcon_2 = QtWidgets.QLabel(parent=self.bookIcon)
        self.bookIcon_2.setGeometry(QtCore.QRect(20, 40, 151, 121))
        self.bookIcon_2.setText("")
        self.bookIcon_2.setPixmap(QtGui.QPixmap(":/xy/R.png"))
        self.bookIcon_2.setScaledContents(True)
        self.bookIcon_2.setObjectName("bookIcon_2")
        self.label_5 = QtWidgets.QLabel(parent=self.frame)
        self.label_5.setGeometry(QtCore.QRect(80, 70, 291, 91))
        font = QtGui.QFont()
        font.setFamily("Georgia")
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")

        self.retranslateUi(formLogin)
        QtCore.QMetaObject.connectSlotsByName(formLogin)

    def retranslateUi(self, formLogin):
        _translate = QtCore.QCoreApplication.translate
        formLogin.setWindowTitle(_translate("formLogin", "Inicio de sesión"))
        self.label_3.setText(
            _translate(
                "formLogin",
                '<html><head/><body><p><span style=" font-size:14pt; font-weight:600; color:#146496;">Usuario:</span></p></body></html>',
            )
        )
        self.label_4.setText(
            _translate(
                "formLogin",
                '<html><head/><body><p><span style=" font-size:14pt; font-weight:600; color:#146496;">Contraseña:</span></p></body></html>',
            )
        )
        self.txtUser.setPlaceholderText(
            _translate("formLogin", "Ingrese identificación")
        )
        self.txtPassword.setPlaceholderText(
            _translate("formLogin", "Ingrese contraseña")
        )
        self.btnAcceder.setText(_translate("formLogin", "Acceder"))
        self.lblMSG.setText(_translate("formLogin", "TextLabel"))
        self.label_5.setText(
            _translate(
                "formLogin",
                '<html><head/><body><p><span style=" font-size:28pt; color:#ffffff;">PROGRAFICO</span></p></body></html>',
            )
        )


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    formLogin = QtWidgets.QDialog()
    ui = Ui_formLogin()
    ui.setupUi(formLogin)
    formLogin.show()
    sys.exit(app.exec())
