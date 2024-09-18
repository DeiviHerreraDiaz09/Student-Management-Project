from datetime import datetime, timedelta
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from PyQt6.QtWidgets import QTableWidgetItem, QPushButton
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import landscape, A5
from Services.paymentService import switch_to_payment
from model.enrollment import Enrollment
from Services.enrollmentService import CreateE
from model.student import Student
from PyQt6 import QtGui, QtCore
from reportlab.lib import colors
import conexion as con
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from PyQt6.QtWidgets import (
    QTableWidgetItem,
    QPushButton,
    QMessageBox,
)
import tempfile
import calendar
import os


class StudentData(QThread):
    data_fetched = pyqtSignal(list)
    create_result = pyqtSignal(bool)

    def __init__(self):
        super().__init__()

    def run(self):
        db = con.Conexion().conectar()
        cursor = db.cursor()
        cursor.execute(
            "SELECT student_ident, student_name, enrollments.grade, tutor_dni, tutor_name, tutor_phone, count(invoices.invoice_id), students.status FROM students INNER JOIN enrollments ON student_ident = enrollments.student_id_fk INNER JOIN invoices on invoices.student_ident_fk = students.student_ident GROUP BY student_ident ORDER BY count(invoices.invoice_id) DESC"
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
            "SELECT * FROM students INNER JOIN enrollments ON student_ident = enrollments.student_id_fk WHERE student_ident =?",
            (self.student_ident,),
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
                "INSERT INTO students (student_ident, student_name, date_of_birth, tutor_dni, tutor_name, address, tutor_email, tutor_phone, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    self.student.student_ident,
                    self.student.student_name,
                    self.student.date_of_birth,
                    self.student.tutor_dni,
                    self.student.tutor_name,
                    self.student.address,
                    self.student.tutor_email,
                    self.student.tutor_phone,
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


# CREACIÓN DE INSCRIPCIÓN
class CreateEnrollment(QObject):
    create_result = pyqtSignal(bool)

    def __init__(self):
        super().__init__()

    def create_enrollment(self, enrollment: Enrollment):
        self.thread = CreateE(enrollment)
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
                SELECT s.student_name, s.date_of_birth, e.grade, s.tutor_name, s.tutor_dni, s.tutor_email, s.address, s.tutor_phone, s.status,
                    f.invoice_id, f.description, f.created_at, f.due_date, f.total_amount, f.remaining_amount, f.status
                FROM students s
                INNER JOIN enrollments e ON student_ident = e.student_id_fk 
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

                if column_number == 4 or column_number == 5:

                    try:
                        cell_data = "{:,.2f}".format(int(cell_data))
                        cell_data = f"${cell_data}" 
                    except (ValueError, TypeError):
                        cell_data = "$0" 
                else:
                    cell_data = str(cell_data)
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
        query = """SELECT student_ident, student_name, e.grade, tutor_dni, tutor_name, tutor_phone, 
                          count(invoices.invoice_id), students.status 
                   FROM students 
                   INNER JOIN enrollments e ON student_ident = e.student_id_fk  
                   INNER JOIN invoices ON student_ident = invoices.student_ident_fk  
                   WHERE student_name LIKE ? 
                   GROUP BY student_ident"""
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
                self.list_student_table.setCellWidget(row_number, 7, button)

        else:
            self.message_error_name.setText(
                "No se encontraron estudiantes con ese nombre"
            )
            self.update_table(self.original_data)
    else:
        self.update_table(self.original_data)
        self.message_error_name.clear()


def Service_on_student_search_result(self, exists):
    db = con.Conexion().conectar()
    cursor = db.cursor()
    student_ident = self.input_student_ident.text()
    student_name = self.input_student_name_2.text()
    date_of_birtht = self.dateEdit.text()
    grade = self.options_grade.currentText()
    tutor_dni = self.input_dni_2.text()
    tutor_name = self.input_tutor_name_2.text()
    tutor_email = self.input_email_2.text()
    address = self.input_address_2.text()
    tutor_phone = self.input_phone_2.text()
    enrollment_amount = self.input_incripcion.text()
    enrollment_date = datetime.now()
    rate_id_fk = int(self.options_rate.currentData())
    period_id_fk = int(self.options_periodo.currentData())
    student_id_fk = student_ident
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
    elif len(enrollment_amount) <= 1:
        self.message.setText("El valor de la inscripción es requerido")
        self.input_incripcion.setFocus()
    else:
        student = Student(
            student_ident,
            student_name,
            date_of_birtht,
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

        cursor.execute(
            "INSERT INTO enrollments (enrollment_date, status, grade, enrollment_amount, rate_id_fk, period_id_fk, student_id_fk) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                enrollment_date.strftime("%d/%m/%Y"),
                status,
                grade,
                int(enrollment_amount),
                rate_id_fk,
                period_id_fk,
                student_id_fk,
            ),
        )

        cursor.execute("SELECT rate_amount FROM rates WHERE rate_id = ?", (rate_id_fk,))
        rate_amount = cursor.fetchone()[0]

        cursor.execute(
            "SELECT final_period FROM periods WHERE period_id = ?",
            (period_id_fk,),
        )
        final_period_str = cursor.fetchone()[0]
        final_period_date = datetime.strptime(final_period_str, "%d/%m/%Y")

        current_due_date = enrollment_date

        end_of_current_month = current_due_date.replace(
            day=calendar.monthrange(current_due_date.year, current_due_date.month)[1]
        )

        cursor.execute(
            """
                INSERT INTO invoices (description, original_amount, total_amount, remaining_amount, due_date, created_at, status, student_ident_fk)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "Factura Mensual",
                rate_amount,
                rate_amount,
                rate_amount,
                end_of_current_month.date(),
                enrollment_date.date(),
                "Generado",
                student_ident,
            ),
        )

        next_due_date = end_of_current_month + timedelta(days=1)

        while next_due_date <= final_period_date:
            end_of_month = next_due_date.replace(
                day=calendar.monthrange(next_due_date.year, next_due_date.month)[1]
            )

            cursor.execute(
                """
                    INSERT INTO invoices (description, original_amount, total_amount, remaining_amount, due_date, created_at, status, student_ident_fk)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "Factura Mensual",
                    rate_amount,
                    rate_amount,
                    rate_amount,
                    end_of_month.date(),
                    next_due_date.date(),
                    "Generado",
                    student_ident,
                ),
            )

            next_due_date = end_of_month + timedelta(days=1)

        db.commit()
        db.close()


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

def change_student(self, student_ident):

    msg_box = QMessageBox(self)
    msg_box.setWindowTitle("Inactivar Estudiante")
    msg_box.setText("¿Estás seguro de que deseas inactivar al estudiante?")
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
        try:
            db = con.Conexion().conectar()
            cursor = db.cursor()
            cursor.execute(
                """
                UPDATE students SET status = 'No vigente' WHERE student_ident = ?
                """,
                (student_ident,),
            )
            db.commit()
            self.load_data()
            self.switch_to_listStudent()
            print("Estudiante inactivado correctamente")
        except Exception as e:
            print(f"Error updating student: {e}")
            db.rollback()
        finally:
            cursor.close()
            db.close()
    else:
        print("Inactivación cancelada")