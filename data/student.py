from PyQt6.QtCore import QObject, pyqtSignal, QThread
import conexion as con

class StudentData(QThread):
    data_fetched = pyqtSignal(list) 

    def __init__(self):
        super().__init__()
        
    def run(self):
        db = con.Conexion().conectar()
        cursor = db.cursor()
        cursor.execute(
            "SELECT student_dni, student_name, grade, tutor_name, tutor_phone, tutor_email FROM students")
        
        results = cursor.fetchall()
        self.data_fetched.emit(results) 
        cursor.close()
        db.close()
  
      