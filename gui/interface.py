from Services.studentService import (
    StudentData,
    SearchStudent,
    Service_search_student_by_id,
    Service_search_student_by_name,
    Service_on_student_search_result,
    generate_invoice_pdf,
    change_student
)
from Services.invoiceService import (
    Service_search_student_by_id_for_invoice,
)

from Services.expensesService import (
    Service_register_expense
)

from Services.configurationService import (
    configuration_optionsService,
    update_configurationService,
)
from Services.enrollmentService import showRatesService, showPeriodService

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTableWidgetItem,
    QPushButton,
    QMessageBox,
)
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
)
from reportlab.lib.pagesizes import landscape, A4, A5, A7, A6, A3
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from gui.UI.dashboard import Ui_MainWindow
from reportlab.lib import colors
from PyQt6.QtCore import QTimer
from PyQt6 import QtGui, QtCore
import conexion as con
from conexion import Conexion
from datetime import datetime
import subprocess
import tempfile
import os


class MyInterface(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Interface Menu")

        self.user_role = None

        # INICIALIZACIÓN DE PANTALLA
        self.content.setCurrentIndex(0)
        self.switch_to_listStudent()
        self.report_dinamic_label.setText("")

        # TABLA GENERAL DE ESTUDIANTES
        self.list_student_table.setColumnCount(8)
        self.list_student_table.setHorizontalHeaderLabels(
            [
                "Nombre",
                "Grado",
                "Identificación Tutor",
                "Tutor",
                "Teléfono Tutor",
                "Nº Facturas",
                "Estado",
                "Acciones",
            ]
        )

        # TABLA FACTURAS VINCULADAS AL ESTUDIANTE
        self.history_table.setColumnCount(8)
        self.history_table.setHorizontalHeaderLabels(
            [
                "Nº Factura",
                "Descripción",
                "Fecha Generación",
                "Fecha Vencimiento",
                "Monto total",
                "Monto restante",
                "Estado",
                "Acciones",
            ]
        )

        self.table_reports_payments.setColumnCount(4)
        self.table_reports_payments.setHorizontalHeaderLabels(
            ["Identificador de gasto", "Descripción", "Fecha de realización", "Total gasto"]
        )

        # CONEXIÓN DE BOTONES A FUNCIONES
        self.students_2.clicked.connect(self.switch_to_listStudent)
        self.students_3.clicked.connect(self.switch_to_listStudent)

        self.reports_2.clicked.connect(self.switch_to_expensesPage)
        self.reports_3.clicked.connect(self.switch_to_expensesPage)

        self.pushButton_Rgasto.clicked.connect(self.switch_to_Registerexpenses)
        self.button_back_cost.clicked.connect(self.switch_to_expensesPage)

        self.config.clicked.connect(self.switch_to_configPage)
        self.config_2.clicked.connect(self.switch_to_configPage)

        self.button_add.clicked.connect(self.switch_to_registerStudent)
        self.registerButton.clicked.connect(self.save_data)
        self.button_search.clicked.connect(self.search_student_by_name)
        self.buttonBack.clicked.connect(self.switch_to_listStudent)
        self.buttonBack_2.clicked.connect(self.switch_to_listStudent)

        self.exit.clicked.connect(self.handleExit)
        self.exit_2.clicked.connect(self.handleExit)

        self.button_search_3.clicked.connect(self.actualizar_nombre_colegio)
        self.button_search_4.clicked.connect(self.actualizar_direccion)
        self.button_search_2.clicked.connect(self.actualizar_telefono)
        self.button_search_5.clicked.connect(self.actualizar_mora)
        self.button_search_6.clicked.connect(self.actualizar_ncf)
        self.icon_complete_widget.setHidden(True)

        self.student_data = StudentData()
        self.student_data.data_fetched.connect(self.update_table)
        self.original_data = []
        self.student_ids = {}
        self.load_data()

    def set_user_role(self, object):
        self.user = object
        self.user_role = self.user["role"]
        if self.user_role != "Administrador":
            self.config.setVisible(False)
        self.Login()

    def Login(self):
        user_id = self.user["user_id"]
        self.conexion = Conexion()
        self.conexion.loginService(user_id)

    def Logout(self):
        user_id = self.user["user_id"]
        self.conexion = Conexion()
        self.conexion.logoutService(user_id)

    def closeEvent(self, event):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Cerrar Aplicación")
        msg_box.setText("¿Estás seguro de que deseas salir?")
        msg_box.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)

        msg_box.setStyleSheet(
            """
            QLabel {
                color: black;
            }
            QPushButton {
                background-color: white;
                color: black;
                border: 1px solid black;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
            QMessageBox {
                border: 2px solid black;
            }
        """
        )

        reply = msg_box.exec()

        if reply == QMessageBox.StandardButton.Yes:
            self.Logout()
            event.accept()
            self.showLogin()
        else:
            event.ignore()

    def handleExit(self):
        self.close()

    def showLogin(self):
        from gui.interface2 import MyInterface

        self.login_interface = MyInterface()
        self.login_interface.show()

    # VISTAS ↓

    # LISTADO DE ESTUDIANTES

    def switch_to_listStudent(self):
        self.content.setCurrentIndex(0)
        self.content_pages.setCurrentIndex(0)

    # DETALLES DE ESTUDIANTE

    def switch_to_studentDetails(self, student_ident):
        self.content.setCurrentIndex(0)
        self.content_pages.setCurrentIndex(1)
        self.search_student_by_id(student_ident)

        try:
            self.inactButton.clicked.disconnect()
        except TypeError:
            pass

        self.inactButton.clicked.connect(lambda: change_student(self, student_ident))

        self.button_add_invoice.clicked.connect(
            lambda: self.switch_to_registerInvoice(student_ident)
        )

    # DETALLES DE PAGOS

    def switch_invoice_details(self, invoice_id):
        self.content_pages.setCurrentIndex(4)
        self.switch_invoice_details_view(invoice_id)

    # REGISTRO DE ESTUDIANTE

    def switch_to_registerStudent(self):
        self.content.setCurrentIndex(0)
        self.content_pages.setCurrentIndex(2)
        showRatesService(self)
        showPeriodService(self)

    # REGISTRO DE FACTURAS MANUALES

    def switch_to_registerInvoice(self, student_ident):
        self.content.setCurrentIndex(0)
        self.content_pages.setCurrentIndex(3)
        Service_search_student_by_id_for_invoice(self, student_ident)

    # REGISTRAR UN PAGO

    def switch_to_paymentsPage(self):
        self.content.setCurrentIndex(1)

    # GASTOS

    def switch_to_expensesPage(self):
        self.content.setCurrentIndex(3)
        self.stackedWidget.setCurrentIndex(0)

    def switch_to_Registerexpenses(self):
        self.content.setCurrentIndex(3)
        self.stackedWidget.setCurrentIndex(1)
        self.registerButton_payment_2.clicked.connect(lambda: Service_register_expense(self))

    # CONFIGURACION

    def switch_to_configPage(self):
        self.content.setCurrentIndex(2)
        self.stackedWidget_2.setCurrentIndex(0)
        configuration_optionsService(self)

    def actualizar_nombre_colegio(self):
        valor = self.input_amount_paid_3.text()
        update_configurationService(self, "school_name", valor)

    def actualizar_direccion(self):
        valor = self.input_amount_paid_4.text()
        update_configurationService(self, "school_address", valor)

    def actualizar_telefono(self):
        valor = self.input_amount_paid_2.text()
        update_configurationService(self, "school_phone", valor)

    def actualizar_mora(self):
        valor = self.input_amount_paid_5.text()
        update_configurationService(self, "school_mora", valor)

    def actualizar_ncf(self):
        valor = self.input_amount_paid_6.text()
        update_configurationService(self, "school_nfc", valor)

    # LOGICA INTERNA ↓

    def load_data(self):
        self.student_data.start()

    # INICIALIZACIÓN DE INFORMACIÓN ESTUDIANTES

    def update_table(self, data):
        self.original_data = data
        self.list_student_table.setRowCount(0)
        self.student_ids = {}

        for row_number, row_data in enumerate(data):
            self.list_student_table.insertRow(row_number)
            student_id = row_data[0]
            self.student_ids[row_number] = student_id

            for column_number, cell_data in enumerate(row_data[1:]):
                self.list_student_table.setItem(
                    row_number, column_number, QTableWidgetItem(str(cell_data))
                )

            student_status = row_data[-1]

            if student_status == "Vigente":
                button = QPushButton("Ver más")
                button.setStyleSheet(
                    """
                    QPushButton {
                        background-color:#1770b3;\n
                        border: none;\n
                        border-radius: 6px;\n
                        color:white;\n
                        font-family: Euphemia;\n
                        font-size: 12px;
                    }"""
                )
                button.clicked.connect(
                    lambda _, student_id=student_id: self.switch_to_studentDetails(
                        student_id
                    )
                )
            else:
                button = QPushButton("Renovar")
                button.setStyleSheet(
                    """
                    QPushButton {
                        background-color:#060270;\n
                        border: none;\n
                        border-radius: 6px;\n
                        color:white;\n
                        font-family: Euphemia;\n
                        font-size: 12px;
                    }"""
                )
                button.clicked.connect(
                    lambda _, student_id=student_id: self.renew_student_status()
                )

            button.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
            self.list_student_table.setCellWidget(row_number, 7, button)

    def renew_student_status(self):
        print("APARTADO DE RENOVACIÓN EN PROCESO")

    # FILTRAR TABLA "list_student_table" por NOMBRE

    def search_student_by_name(self):
        Service_search_student_by_name(self)

    # LOGICA PARA FILTRAR INFORMACIÓN DETALLADA DEL ESTUDIANTE

    def search_student_by_id(self, student_ident):
        Service_search_student_by_id(self, student_ident)

    # LOGICA REGISTRO DE ESTUDIANTES

    def save_data(self):
        student_ident = self.input_student_ident.text()
        self.searchStudent = SearchStudent(student_ident)
        self.searchStudent.student_result.connect(
            lambda exists: Service_on_student_search_result(self, exists)
        )
        self.searchStudent.start()

    def handle_create_result(self, success):
        if success:
            self.message.clear()
            self.message_ok.setText("Se ha registrado con éxito")
            QTimer.singleShot(7000, self.clear_message_ok)
            self.switch_to_listStudent()
            self.student_data = StudentData()
            self.student_data.data_fetched.connect(self.update_table)
            self.load_data()
            self.clear_data()
        else:
            self.message.setText("Ha ocurrido un error, intente nuevamente")

    # INFORMACIÓN DETALLES DE PAGOS

    def switch_invoice_details_view(self, invoice_id):
        db = con.Conexion().conectar()
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT s.student_name, f.invoice_id, f.description, f.total_amount, f.created_at, f.due_date, 
                p.payment_id, p.payment_date, p.payment_paid, p.payment_method, s.student_ident
            FROM students as s 
            INNER JOIN invoices f on s.student_ident = f.student_ident_fk 
            LEFT JOIN payments as p on p.invoice_id_fk = f.invoice_id 
            WHERE f.invoice_id = ?
            """,
            (invoice_id,),
        )

        rows = cursor.fetchall()
        cursor.close()
        db.close()

        if rows:
            payments = rows[0]
            self.input_student_name_info.setText(payments[0])
            self.input_number_invoice.setText(str(payments[1]))
            self.input_description_invoice.setText(payments[2])
            self.input_total_amount.setText(str(payments[3]))
            self.input_created_date_info.setText(payments[4])
            self.input_finish_date.setText(payments[5])
            student_ident = payments[10]
            self.history_table_payment.setRowCount(0)

            for row_number, row_data in enumerate(rows):
                self.history_table_payment.insertRow(row_number)
                for column_number, cell_data in enumerate(row_data[6:]):
                    self.history_table_payment.setItem(
                        row_number, column_number, QTableWidgetItem(str(cell_data))
                    )

            self.buttonBack_student_info.clicked.connect(
                lambda: self.switch_to_studentDetails(student_ident)
            )

            self.buttonBack_student_info_3.clicked.connect(
                lambda: generate_invoice_pdf(self, payments, rows, include_ncf=True)
            )

            self.buttonBack_student_info_2.clicked.connect(
                lambda: generate_invoice_pdf(self, payments, rows, include_ncf=False)
            )

    def generate_invoice_pdf(self, payments, rows, include_ncf):
        db = con.Conexion().conectar()
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT school_nfc, school_name, school_address, school_phone FROM configurations LIMIT 1
            """
        )
        ncf_row = cursor.fetchone()
        cursor.close()
        db.close()

        school_info = {
            "school_name": ncf_row[1] if ncf_row else "Nombre no disponible",
            "school_address": ncf_row[2] if ncf_row else "Dirección no disponible",
            "school_phone": ncf_row[3] if ncf_row else "Teléfono no disponible",
        }

        ncf = ncf_row[0] if include_ncf and ncf_row else None

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            pdf_path = temp_pdf.name

        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=landscape(A5),
            rightMargin=10,
            leftMargin=10,
            topMargin=10,
            bottomMargin=10,
        )
        elements = []
        styles = getSampleStyleSheet()

        header_style = ParagraphStyle(
            name="HeaderStyle", fontSize=10, alignment=1, spaceAfter=6
        )

        elements.append(Paragraph(f"{school_info['school_name']}", header_style))
        elements.append(Paragraph(f"{school_info['school_address']}", styles["Normal"]))
        elements.append(
            Paragraph(f"Teléfono: {school_info['school_phone']}", styles["Normal"])
        )
        elements.append(Spacer(1, 8))

        title_style = ParagraphStyle(
            name="TitleStyle",
            fontSize=14,
            leading=18,
            alignment=1,
            spaceAfter=8,
            textColor=colors.darkblue,
        )

        elements.append(Paragraph(f"Factura de: {payments[0]}", title_style))
        elements.append(Spacer(1, 8))

        info_table_data = [
            ["Número de Factura:", str(payments[1])],
            ["Descripción:", payments[2]],
            ["Monto Total:", f"${payments[3]:,.2f}"],
            ["Fecha de Creación:", payments[4]],
            ["Fecha de Vencimiento:", payments[5]],
        ]

        if ncf:
            info_table_data.append(["NCF:", ncf])

        info_table = Table(info_table_data, colWidths=[doc.width / 3.0] * 2)
        info_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )
        elements.append(info_table)
        elements.append(Spacer(1, 16))

        data = [["Número de Pago", "Fecha", "Monto", "Método"]]
        for row in rows:
            data.append([str(row[6]), row[7], f"${row[8]:,.2f}", row[9]])

        table = Table(data, colWidths=[doc.width / 4.0] * 4)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.lightgrey),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )
        elements.append(table)
        elements.append(Spacer(1, 16))

        footer_style = ParagraphStyle(
            name="FooterStyle", fontSize=10, alignment=1, spaceAfter=8
        )

        elements.append(Spacer(1, 16))
        elements.append(
            Paragraph(
                f"Reporte generado el {datetime.now().strftime('%d/%m/%Y')}",
                footer_style,
            )
        )

        doc.build(elements)

        if os.name == "posix":
            subprocess.run(["xdg-open", pdf_path])
        elif os.name == "nt":
            os.startfile(pdf_path)
        elif os.name == "darwin":
            subprocess.run(["open", pdf_path])

    def clear_message_ok(self):
        self.message_ok.clear()
        self.message_ok_pay.clear()

    def clear_data(self):
        self.input_student_ident.clear()
        self.input_student_name_2.clear()
        self.dateEdit.clear()
        self.options_grade.setCurrentIndex(0)
        self.input_dni_2.clear()
        self.input_tutor_name_2.clear()
        self.input_email_2.clear()
        self.input_address_2.clear()
        self.input_phone_2.clear()
        self.input_student_ident.setFocus()


if __name__ == "__main__":
    app = QApplication([])
    window = MyInterface()
    window.show()
    app.exec()
