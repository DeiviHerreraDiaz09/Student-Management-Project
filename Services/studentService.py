from PyQt6.QtCore import QObject, pyqtSignal, QThread
from model.student import Student
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
            "SELECT student_dni, student_name, grade, tutor_name, tutor_phone, count(invoices.invoice_id)FROM students INNER JOIN invoices on student_dni = invoices.student_dni_fk GROUP BY student_dni ORDER BY count(invoices.invoice_id) DESC"
        )

        results = cursor.fetchall()
        self.data_fetched.emit(results)
        cursor.close()
        db.close()


class SearchStudent(QThread):
    student_result = pyqtSignal(bool)

    def __init__(self, dni):
        super().__init__()
        self.dni = dni

    def run(self):
        db = con.Conexion().conectar()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM students WHERE student_dni =?", (self.dni,))
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
                "INSERT INTO students (student_dni, student_name, date_of_birth, grade, tutor_dni, tutor_name, tutor_email, tutor_phone, address) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    self.student.student_dni,
                    self.student.student_name,
                    self.student.date_of_birth,
                    self.student.grade,
                    self.student.tutor_dni,
                    self.student.tutor_name,
                    self.student.tutor_email,
                    self.student.tutor_phone,
                    self.student.address,
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
