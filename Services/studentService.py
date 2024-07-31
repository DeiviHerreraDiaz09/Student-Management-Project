from PyQt6.QtCore import QObject, pyqtSignal, QThread, QTimer
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QPushButton
from model.student import Student
from Services.paymentService import switch_to_payment
from PyQt6 import QtGui, QtCore
import conexion as con


class StudentData(QThread):
    data_fetched = pyqtSignal(list)
    create_result = pyqtSignal(bool)

    def __init__(self):
        super().__init__()

    def run(self):
        db = con.Conexion().conectar()
        cursor = db.cursor()
        cursor.execute(
            "SELECT student_ident, student_name, grade, tutor_dni, tutor_name, tutor_phone, count(invoices.invoice_id)FROM students INNER JOIN invoices on student_ident = invoices.student_ident_fk GROUP BY student_ident ORDER BY count(invoices.invoice_id) DESC"
        )

        results = cursor.fetchall()
        self.data_fetched.emit(results)
        cursor.close()
        db.close()


class SearchStudent(QThread):
    student_result = pyqtSignal(bool)

    def __init__(self, student_ident):
        super().__init__()
        self.student_ident = student_ident

    def run(self):
        db = con.Conexion().conectar()
        cursor = db.cursor()
        cursor.execute(
            "SELECT * FROM students WHERE student_ident =?", (self.student_ident,)
        )
        fila = cursor.fetchone()
        if fila:
            self.student_result.emit(True)
        else:
            self.student_result.emit(False)

        cursor.close()
        db.close()


class Create(QThread):
    create_result = pyqtSignal(bool)

    def __init__(self, student):
        super().__init__()
        self.student = student

    def run(self):
        try:
            db = con.Conexion().conectar()
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO students (student_ident, student_name, date_of_birth, grade, year_progress, tutor_dni, tutor_name, tutor_email, tutor_phone, address, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    self.student.student_ident,
                    self.student.student_name,
                    self.student.date_of_birth,
                    self.student.grade,
                    self.student.year_progress,
                    self.student.tutor_dni,
                    self.student.tutor_name,
                    self.student.tutor_email,
                    self.student.tutor_phone,
                    self.student.address,
                    self.student.status,
                ),
            )
            db.commit()
            self.create_result.emit(True)
        except Exception as e:
            print(f"Error: {e}")
            self.create_result.emit(False)
        finally:
            cursor.close()
            db.close()


class CreateStudent(QObject):
    create_result = pyqtSignal(bool)

    def __init__(self):
        super().__init__()

    def create_student(self, student: Student):
        self.thread = Create(student)
        self.thread.create_result.connect(self.handle_create_result)
        self.thread.start()

    def handle_create_result(self, success):
        self.create_result.emit(success)


# SERVICIOS UNITARIOS


def Service_search_student_by_id(self, student_ident):
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

            if invoice_status != "Pagado":
                button = QPushButton("Pagar")
                button.setStyleSheet(
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
                button.setCursor(
                    QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor)
                )
                button.clicked.connect(
                    lambda checked, id=invoice_id: switch_to_payment(self, id)
                )
                self.history_table.setCellWidget(row_number, 7, button)
            else:
                details_button = QPushButton("Detalles")
                details_button.setStyleSheet(
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
                details_button.setCursor(
                    QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor)
                )
                details_button.clicked.connect(
                    lambda checked, id=invoice_id: self.switch_invoice_details(id)
                )
                self.history_table.setCellWidget(row_number, 7, details_button)


def Service_search_student_by_name(self):
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


def Service_on_student_search_result(self, exists):
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
        self.input_student_ident.setFocus()
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
