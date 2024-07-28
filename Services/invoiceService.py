from PyQt6.QtCore import QObject, pyqtSignal, QThread
from model.invoice import Invoice
from model.payment import Payment

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

