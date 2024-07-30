from Services.studentService import StudentData, CreateStudent, SearchStudent
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QPushButton
from gui.UI.dashboard import Ui_MainWindow
from model.student import Student
from PyQt6.QtCore import QTimer
from PyQt6 import QtGui, QtCore
import conexion as con
from datetime import datetime, timedelta


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

    # LISTADO DE ESTUDIANTES

    def switch_to_listStudent(self):
        self.content.setCurrentIndex(0)
        self.content_pages.setCurrentIndex(0)

    # DETALLES DE ESTUDIANTE

    def switch_to_studentDetails(self, student_ident):
        self.content.setCurrentIndex(0)
        self.content_pages.setCurrentIndex(1)
        self.search_student_by_id(student_ident)
        self.pushButton.clicked.connect(
            lambda: self.switch_to_registerInvoice(student_ident)
        )

    # REGISTRO DE ESTUDIANTE

    def switch_to_registerStudent(self):
        self.content.setCurrentIndex(0)
        self.content_pages.setCurrentIndex(2)

    # REGISTRO DE FACTURAS MANUALES

    def switch_to_registerInvoice(self, student_ident):
        self.content.setCurrentIndex(0)
        self.content_pages.setCurrentIndex(3)
        self.search_student_by_id_for_invoice(student_ident)

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
                        lambda _, student_id=student_id: self.switch_to_studentDetails(
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
            self.message_error_name.clear()

    # LOGICA PARA FILTRAR INFORMACIÓN DETALLADA DEL ESTUDIANTE

    def search_student_by_id(self, student_ident):
        db = con.Conexion().conectar()
        cursor = db.cursor()
        cursor.execute(
            """
                SELECT s.student_name, s.date_of_birth, s.grade, s.tutor_name, s.tutor_dni, s.tutor_email, s.address, s.tutor_phone, s.status,
                    f.invoice_id, f.description, f.created_at, f.due_date, f.total_amount, f.remaining_amount, f.status
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
            self.input_dni.setText(student[4])
            self.input_email.setText(student[5])
            self.input_address.setText(student[6])
            self.input_phone.setText(student[7])
            self.input_status.setText(student[8])

            self.history_table.setRowCount(0)

            for row_number, row_data in enumerate(rows):
                self.history_table.insertRow(row_number)
                for column_number, cell_data in enumerate(row_data[9:]):
                    self.history_table.setItem(
                        row_number, column_number, QTableWidgetItem(str(cell_data))
                    )
                invoice_id = row_data[9]
                invoice_status = row_data[15]

                if invoice_status != "Pagada":
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
                        lambda checked, id=invoice_id: self.switch_to_payment(id)
                    )
                    self.history_table.setCellWidget(row_number, 7, button)
                else:
                    details_button = QPushButton("Detalles")
                    details_button.setStyleSheet(
                        """
                        QPushButton {
                            background-color:#4caf50;\n
                            border: none;\n
                            border-radius: 6px;\n
                            color:white;\n
                            font-family: Euphemia;\n
                            font-size: 12px;
                        }"""
                    )
                    details_button.setCursor(
                        QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor)
                    )
                    details_button.clicked.connect(
                        # Modificar esta parte con la nueva seccion del historial de pagos de la factura vinculada
                        lambda checked, id=invoice_id: self.show_invoice_details(id)
                    )
                    self.history_table.setCellWidget(row_number, 7, details_button)

    # LOGICA REGISTRO DE ESTUDIANTES

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
        year_progress = "2024"
        status = "Vigente"

        if exists:
            self.message.setText("El estudiante ya existe")
            self.clear_data()
        elif len(student_ident) <= 10:
            self.message.setText(
                "El identificador del estudiante debe ser mínimo de 11 caracteres"
            )
            self.student_ident.setFocus()
        elif len(student_name) <= 5:
            self.message.setText("El nombre completo es requerido")
            self.input_student_name_2.setFocus()
        elif len(tutor_dni) <= 10:
            self.message.setText(
                "El identificador del tutor debe ser mínimo de 11 caracteres"
            )
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
                year_progress,
                tutor_dni,
                tutor_name,
                tutor_email,
                tutor_phone,
                address,
                status,
            )
            self.student_data = CreateStudent()
            self.student_data.create_result.connect(self.handle_create_result)
            self.student_data.create_student(student)

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

    # REGISTRO DE FACTURA MANUAL

    def search_student_by_id_for_invoice(self, student_ident):
        db = con.Conexion().conectar()
        cursor = db.cursor()
        cursor.execute(
            """
                SELECT student_ident, student_name, grade, tutor_name
                FROM students
                WHERE student_ident = ?
                """,
            (student_ident,),
        )
        row = cursor.fetchone()
        db.close()

        if row:
            self.input_student_ident__invoice.setText(row[0])
            self.input_student_name__invoice.setText(row[1])

            student_ident = row[0]

            try:
                self.registerButton_Invoice.clicked.disconnect()
            except TypeError:
                pass

            self.registerButton_Invoice.clicked.connect(
                lambda: self.register_invoice(student_ident)
            )

            self.buttonBack_3.clicked.connect(
                lambda: self.switch_to_studentDetails(student_ident)
            )
        else:
            print("Estudiante no encontrado")

    def register_invoice(self, student_ident):
        try:
            db = con.Conexion().conectar()
            cursor = db.cursor()

            description = self.lineEdit_description_invoice.text()
            total_amount = self.input_total_invoice.text()
            created_at = datetime.now().date()
            due_date = (datetime.now() + timedelta(days=30)).date()

            cursor.execute(
                """
                INSERT INTO invoices (description, total_amount, remaining_amount, due_date, created_at, status, student_ident_fk)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    description,
                    total_amount,
                    total_amount,
                    due_date,
                    created_at,
                    "Pendiente",
                    student_ident,
                ),
            )

            db.commit()
            db.close()

            self.lineEdit_description_invoice.clear()
            self.input_total_invoice.clear()
            print("Factura registrada exitosamente")
            self.load_data()
            self.switch_to_studentDetails(student_ident)
        except Exception as e:
            print(f"Error al registrar la factura: {e}")

    # INFORMACIÓN FACTURA A PAGAR

    def switch_to_payment(self, invoice_id):
        self.content.setCurrentIndex(1)
        db = con.Conexion().conectar()
        cursor = db.cursor()
        cursor.execute(
            """
                SELECT s.student_name, f.invoice_id, f.description, f.remaining_amount, f.created_at, f.due_date, s.student_ident
                FROM students s
                LEFT JOIN invoices f ON s.student_ident = f.student_ident_fk
                WHERE f.invoice_id = ?
                """,
            (invoice_id,),
        )
        rows = cursor.fetchall()
        db.close()

        if rows:
            invoice_details = rows[0]
            self.input_student_name_invo.setText(invoice_details[0])
            self.input_id_invoice.setText(str(invoice_details[1]))
            self.lineEdit_description.setText(invoice_details[2])
            self.lineEdit_total_amount.setText(str(invoice_details[3]))
            self.input_creation_date.setText(invoice_details[4])
            self.input_expiration_date.setText(invoice_details[5])

            self.current_invoice_id = invoice_details[1]
            self.current_student_ident = invoice_details[6]
            self.remaining_amount = invoice_details[3]

            try:
                self.registerButton_payment.clicked.disconnect()
            except TypeError:
                pass

            self.registerButton_payment.clicked.connect(
                lambda: self.register_payment(
                    self.current_invoice_id, self.current_student_ident
                )
            )

    def register_payment(self, invoice_id, student_ident):
        payment_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        amount_paid = self.input_amount_paid.text()
        payment_method = self.option_payment_method.currentText()

        if not amount_paid.isdigit():
            self.message_erro_payment.setText("El monto ingresado no es válido")
            self.message_erro_payment.show()
            return

        amount_paid = int(amount_paid)

        if amount_paid > self.remaining_amount:
            self.message_erro_payment.setText(
                f"El monto no debe ser superior a {self.remaining_amount}"
            )
            self.message_erro_payment.show()
            return

        db = con.Conexion().conectar()
        cursor = db.cursor()
        cursor.execute(
            """
                INSERT INTO payments (payment_date, payment_paid, payment_method, invoice_id_fk)
                VALUES (?, ?, ?, ?)
                """,
            (payment_date, amount_paid, payment_method, invoice_id),
        )
        db.commit()
        db.close()

        self.input_amount_paid.clear()
        self.option_payment_method.setCurrentIndex(0)
        self.message_erro_payment.clear()

        self.switch_to_studentDetails(student_ident)

    def clear_message_ok(self):
        self.message_ok.clear()

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
