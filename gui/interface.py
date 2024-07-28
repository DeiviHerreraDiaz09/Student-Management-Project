from Services.studentService import StudentData, CreateStudent, SearchStudent
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QPushButton
from gui.UI.dashboard import Ui_MainWindow
from model.student import Student
from PyQt6.QtCore import QTimer
from PyQt6 import QtGui, QtCore
import conexion as con


class MyInterface(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Interface Menu")
        self.content.setCurrentIndex(0)
        self.switch_to_listStudent()
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
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels(
            [
                "Nº Factura",
                "Descripción",
                "Fecha Generación",
                "Fecha Vencimiento",
                "Monto total",
                "Estado",
            ]
        )
        self.students_2.clicked.connect(self.switch_to_studentsPage)
        self.payments_2.clicked.connect(self.switch_to_paymentsPage)
        self.reports_2.clicked.connect(self.switch_to_reportsPage)
        self.button_add.clicked.connect(self.switch_to_registerStudent)
        self.registerButton.clicked.connect(self.save_data)
        self.button_search.clicked.connect(self.search_student_by_name)
        self.buttonBack.clicked.connect(self.switch_to_listStudent)
        self.buttonBack_2.clicked.connect(self.switch_to_listStudent)
        self.student_data = StudentData()
        self.student_data.data_fetched.connect(self.update_table)

        self.original_data = []
        self.load_data()

        self.student_ids = {}

    def load_data(self):
        self.student_data.start()

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
                lambda _, student_id=student_id: self.student_details(student_id)
            )
            self.list_student_table.setCellWidget(row_number, 6, button)

    def switch_to_studentsPage(self):
        self.content.setCurrentIndex(0)
        self.switch_to_listStudent()

    def switch_to_paymentsPage(self):
        self.content.setCurrentIndex(1)

    def switch_to_reportsPage(self):
        self.content.setCurrentIndex(2)

    def switch_to_registerStudent(self):
        self.content_pages.setCurrentIndex(2)

    def switch_to_listStudent(self):
        self.content_pages.setCurrentIndex(0)

    def save_data(self):
        student_ident = self.input_student_ident.text()
        self.searchStudent = SearchStudent(student_ident)
        self.searchStudent.student_result.connect(self.on_student_search_result)
        self.searchStudent.start()

    def on_student_search_result(self, exists):
        student_ident = self.input_student_ident.text()
        student_name = self.input_student_name_2.text()
        date_of_birtht = self.dateEdit.text()
        grade = self.options_grade.currentText()
        tutor_dni = self.input_dni_2.text()
        tutor_name = self.input_tutor_name_2.text()
        tutor_email = self.input_email_2.text()
        address = self.input_address_2.text()
        tutor_phone = self.input_phone_2.text()

        if exists:
            self.message.setText("El estudiante ya existe")
            self.clear_data()
        elif len(student_ident) <= 10:
            self.message.setText("El identificador del estudiante debe ser mínimo de 11 caracteres")
            self.student_ident.setFocus()
        elif len(student_name) <= 5:
            self.message.setText("El nombre completo es requerido")
            self.input_student_name_2.setFocus()
        elif len(tutor_dni) <= 10:
            self.message.setText("El identificador del tutor debe ser mínimo de 11 caracteres")
            self.input_dni_2.setFocus()
        elif len(tutor_name) <= 5:
            self.message.setText("El nombre completo del tutor es requerido")
            self.input_tutor_name_2.setFocus()
        elif len(tutor_email) <= 6:
            self.message.setText("Formato de email requerido")
            self.input_email_2.setFocus()
        elif len(address) <= 3:
            self.message.setText("La dirección es requerida")
            self.input_address_2.setFocus()
        elif len(tutor_phone) <= 9:
            self.message.setText("El teléfono del tutor es requerido")
            self.input_phone_2.setFocus()
        else:
            student = Student(
                student_ident,
                student_name,
                date_of_birtht,
                grade,
                tutor_dni,
                tutor_name,
                tutor_email,
                tutor_phone,
                address,
            )
            self.student_data = CreateStudent()
            self.student_data.create_result.connect(self.handle_create_result)
            self.student_data.create_student(student)

    def handle_create_result(self, success):
        if success:
            self.message.clear()
            self.message_ok.setText("Se ha registrado con éxito")
            QTimer.singleShot(3000, self.clear_message_ok)
            self.switch_to_listStudent()
            self.student_data = StudentData()
            self.student_data.data_fetched.connect(self.update_table)
            self.load_data()
            self.clear_data()
        else:
            self.message.setText("Ha ocurrido un error, intente nuevamente")

    def clear_message_ok(self):
        self.message_ok.clear()

    def search_student_by_name(self):
        name = self.box.text()
        if name:
            db = con.Conexion().conectar()
            cursor = db.cursor()
            query = "SELECT student_ident, student_name, grade, tutor_dni, tutor_name, tutor_phone, count(invoices.invoice_id)FROM students INNER JOIN invoices on student_ident = invoices.student_ident_fk  WHERE student_name LIKE ? GROUP BY student_ident  "
            cursor.execute(query, ("%" + name + "%",))
            rows = cursor.fetchall()
            db.close()
            if rows:
                self.list_student_table.setRowCount(0)
                for row_number, row_data in enumerate(rows):
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
                    button.setCursor(
                        QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor)
                    )
                    button.clicked.connect(
                        lambda _, student_id=student_id: self.student_details(
                            student_id
                        )
                    )
                    self.list_student_table.setCellWidget(row_number, 6, button)

            else:
                self.message_error_name.setText(
                    "No se encontraron estudiantes con ese nombre"
                )
                self.update_table(self.original_data)
        else:
            self.update_table(self.original_data)

    def student_details(self, studen_id):
        self.content_pages.setCurrentIndex(1)
        self.search_student_by_id(studen_id)

    def search_student_by_id(self, student_ident):
        db = con.Conexion().conectar()
        cursor = db.cursor()
        cursor.execute(
            """
                SELECT s.student_name, s.date_of_birth, s.grade, s.tutor_dni, s.tutor_name, s.tutor_email, s.address, s.tutor_phone, s.status,
                       f.invoice_id, f.description, f.created_at, f.due_date, f.total_amount, f.status
                FROM students s
                LEFT JOIN invoices f ON s.student_ident = f.student_ident_fk
                WHERE s.student_ident = ?
                """,
            (student_ident,),
        )
        rows = cursor.fetchall()
        db.close()

        if rows:
            student = rows[0]
            self.input_student_name.setText(student[0])
            self.input_date.setText(student[1])
            self.input_grade.setText(student[2])
            self.input_tutor_name.setText(student[3])
            self.input_dni.setText(student[3])
            self.input_email.setText(student[4])
            self.input_address.setText(student[5])
            self.input_phone.setText(student[6])
            self.input_status.setText(student[7])

            self.history_table.setRowCount(0)

            for row_number, row_data in enumerate(rows):
                self.history_table.insertRow(row_number)
                for column_number, cell_data in enumerate(row_data[9:]):
                    self.history_table.setItem(
                        row_number, column_number, QTableWidgetItem(str(cell_data))
                    )

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
