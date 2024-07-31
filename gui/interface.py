from Services.studentService import (
    StudentData,
    SearchStudent,
    Service_search_student_by_id,
    Service_search_student_by_name,
    Service_on_student_search_result,
)
from Services.invoiceService import (
    Service_search_student_by_id_for_invoice,
)
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QPushButton
from gui.UI.dashboard import Ui_MainWindow
from PyQt6.QtCore import QTimer
from PyQt6 import QtGui, QtCore
import conexion as con
from datetime import datetime


class MyInterface(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Interface Menu")

        # INICIALIZACIÓN DE PANTALLA
        self.content.setCurrentIndex(0)
        self.switch_to_listStudent()

        # TABLA GENERAL DE ESTUDIANTES
        self.list_student_table.setColumnCount(7)
        self.list_student_table.setHorizontalHeaderLabels(
            [
                "Nombre",
                "Grado",
                "Identificación Tutor ",
                "Tutor",
                "Teléfono Tutor",
                "Nº Facturas",
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

        # CONEXIÓN DE BOTONES A FUNCIONES
        self.students_2.clicked.connect(self.switch_to_listStudent)
        self.reports_2.clicked.connect(self.switch_to_reportsPage)
        self.button_add.clicked.connect(self.switch_to_registerStudent)
        self.registerButton.clicked.connect(self.save_data)
        self.button_search.clicked.connect(self.search_student_by_name)
        self.buttonBack.clicked.connect(self.switch_to_listStudent)
        self.buttonBack_2.clicked.connect(self.switch_to_listStudent)

        self.student_data = StudentData()
        self.student_data.data_fetched.connect(self.update_table)
        self.original_data = []
        self.student_ids = {}
        self.load_data()

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

    # REGISTRO DE FACTURAS MANUALES

    def switch_to_registerInvoice(self, student_ident):
        self.content.setCurrentIndex(0)
        self.content_pages.setCurrentIndex(3)
        Service_search_student_by_id_for_invoice(self, student_ident)

    # REGISTRAR UN PAGO

    def switch_to_paymentsPage(self):
        self.content.setCurrentIndex(1)

    # REPORTE DE PAGOS DIARIOS

    def switch_to_reportsPage(self):
        self.content.setCurrentIndex(2)

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
            button.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
            button.clicked.connect(
                lambda _, student_id=student_id: self.switch_to_studentDetails(
                    student_id
                )
            )
            self.list_student_table.setCellWidget(row_number, 6, button)

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
