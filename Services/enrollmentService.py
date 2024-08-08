from PyQt6.QtCore import QObject, pyqtSignal, QThread, QTimer
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QPushButton
from model.enrollment import Enrollment
from PyQt6 import QtGui, QtCore
import conexion as con

class CreateE(QThread):
    create_result = pyqtSignal(bool)

    def __init__(self, enrollment):
        super().__init__()
        self.enrollment = enrollment

    def run(self):
        print(type(self.enrollment.enrollment_date))
        print(type(self.enrollment.status))
        print(type(self.enrollment.grade))
        print(type(self.enrollment.enrollment_amount))
        print(type(self.enrollment.rate_id_fk))
        print(type(self.enrollment.period_id_fk))
        print(type(self.enrollment.student_id_fk))
        try:
            db = con.Conexion().conectar()
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO enrollments (enrollment_date , status , grade , enrollment_amount , rate_id_fk , period_id_fk , student_id_fk ) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    self.enrollment.enrollment_date,
                    self.enrollment.status,
                    self.enrollment.grade,
                    self.enrollment.enrollment_amount,
                    self.enrollment.rate_id_fk,
                    self.enrollment.period_id_fk,
                    self.enrollment.student_id_fk,
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

