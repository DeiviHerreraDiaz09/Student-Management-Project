import conexion as con
from datetime import datetime, timedelta
from PyQt6.QtCore import QTimer

# REGISTRO DE FACTURA MANUAL


def Service_search_student_by_id_for_invoice(self, student_ident):
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
            lambda: Service_register_invoice(self, student_ident)
        )

        self.buttonBack_3.clicked.connect(
            lambda: self.switch_to_studentDetails(student_ident)
        )
    else:
        print("Estudiante no encontrado")


def Service_register_invoice(self, student_ident):
    try:
        db = con.Conexion().conectar()
        cursor = db.cursor()

        description = self.lineEdit_description_invoice.text()
        total_amount = self.input_total_invoice.text()

        created_at = datetime.now().date()
        due_date = (datetime.now() + timedelta(days=30)).date()

        if len(description) <= 10:
            self.message.setText("Es necesario una descripción válida")
            self.input_student_ident.setFocus()
        elif len(total_amount) <= 1:
            self.message.setText("Ingrese un valor válido")
            self.input_student_name_2.setFocus()
        else:
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
        self.message_ok_pay.setText("Creación de factura exitosamente")
        QTimer.singleShot(7000, self.clear_message_ok)
        self.load_data()
        self.switch_to_studentDetails(student_ident)
    except Exception as e:
        print(f"Error al registrar la factura: {e}")
