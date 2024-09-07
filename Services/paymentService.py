import conexion as con
from datetime import datetime
from PyQt6.QtCore import QTimer


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
        self.lineEdit_total_amount.setText( f"${invoice_details[3]:,.2f}")
        self.input_creation_date.setText(invoice_details[4])
        self.input_expiration_date.setText(invoice_details[5])

        current_invoice_id = self.current_invoice_id = invoice_details[1]
        current_student_ident = self.current_student_ident = invoice_details[6]
        self.remaining_amount = invoice_details[3]

        try:
            self.registerButton_payment.clicked.disconnect()
        except TypeError:
            pass

        self.registerButton_payment.clicked.connect(
            lambda: register_payment(self, current_invoice_id, current_student_ident)
        )

        self.button_back_studentDetails.clicked.connect(
            lambda: self.switch_to_studentDetails(current_student_ident)
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

    self.message_ok_pay.setText("Se registró el pago con éxito")
    QTimer.singleShot(7000, self.clear_message_ok)
    self.switch_to_studentDetails(student_ident)
