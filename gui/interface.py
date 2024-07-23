from gui.dashboard import Ui_MainWindow
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from data.student import StudentData, CreateStudent, SearchStudent
from model.student import Student
import conexion as con


class MyInterface(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Interface Menu")
        self.list_student_table.setColumnCount(6)
        self.list_student_table.setHorizontalHeaderLabels(
            ["DNI", "Nombre", "Grado", "Tutor", "Teléfono Tutor", "Nº Facturas"]
        )
        self.students_2.clicked.connect(self.switch_to_studentsPage)
        self.payments_2.clicked.connect(self.switch_to_paymentsPage)
        self.reports_2.clicked.connect(self.switch_to_reportsPage)
        self.button_add.clicked.connect(self.switch_to_registerStudent)
        self.registerButton.clicked.connect(self.save_data)
        self.button_searchDNI.clicked.connect(self.search_student_by_dni)
        self.student_data = StudentData()
        self.student_data.data_fetched.connect(self.update_table)

        self.load_data()

    def load_data(self):
        self.student_data.start()

    def update_table(self, data):
        self.list_student_table.setRowCount(0)
        for row_number, row_data in enumerate(data):
            self.list_student_table.insertRow(row_number)
            for column_number, cell_data in enumerate(row_data):
                self.list_student_table.setItem(
                    row_number, column_number, QTableWidgetItem(str(cell_data))
                )

    def switch_to_studentsPage(self):
        self.content.setCurrentIndex(0)

    def switch_to_paymentsPage(self):
        self.content.setCurrentIndex(1)

    def switch_to_reportsPage(self):
        self.content.setCurrentIndex(2)

    def switch_to_registerStudent(self):
        self.principal_content.setCurrentIndex(2)

    def save_data(self):
        dni = self.lineEdit_dni.text()
        self.searchStudent = SearchStudent(dni)
        self.searchStudent.student_result.connect(self.on_student_search_result)
        self.searchStudent.start()

    def on_student_search_result(self, exists):
        student_dni = self.lineEdit_dni.text()
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
        elif len(student_dni) <= 7:
            self.message.setText("El dni debe ser mínimo de 8 caractéres")
            self.lineEdit_dni.setFocus()
        elif len(student_name) <= 5:
            self.message.setText("El nombre completo es requerido")
            self.input_student_name_2.setFocus()
        elif len(tutor_dni) <= 7:
            self.message.setText("El dni del tutor debe ser mínimo de 8 caractéres")
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
                student_dni,
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
            self.student_data = StudentData()
            self.student_data.data_fetched.connect(self.update_table)
            self.load_data()
            self.clear_data()
        else:
            self.message.setText("Ha ocurrido un error, intente nuevamente")

    def clear_data(self):
        self.lineEdit_dni.clear()
        self.input_student_name_2.clear()
        self.dateEdit.clear()
        self.input_dni_2.clear()
        self.input_tutor_name_2.clear()
        self.input_email_2.clear()
        self.input_address_2.clear()
        self.input_phone_2.clear()

    def clear_data_searchStudent(self):
        self.input_student_name.clear()
        self.input_date.clear()
        self.input_grade.clear()
        self.input_dni.clear()
        self.input_tutor_name.clear()
        self.input_email.clear()
        self.input_address.clear()
        self.input_phone.clear()

    def search_student_by_dni(self):
        dni = self.box_dni.text()
        print("DNI ingresado:", dni)
        if dni:
            db = con.Conexion().conectar()
            cursor = db.cursor()
            cursor.execute(
                "SELECT student_name, date_of_birth, grade, tutor_dni, tutor_name, tutor_email, address, tutor_phone FROM students WHERE student_dni = ?",
                (dni,),
            )
            student = cursor.fetchone()
            db.close()

            if student:
                print("Usuario encontrado")
                self.input_student_name.setText(student[0])
                self.input_date.setText(student[1])
                self.input_grade.setText(student[2])
                self.input_dni.setText(student[3])
                self.input_tutor_name.setText(student[4])
                self.input_email.setText(student[5])
                self.input_address.setText(student[6])
                self.input_phone.setText(student[7])
            else:
                self.message.setText("Estudiante no encontrado")
                print("Usuario no encontrado")
                self.clear_data_searchStudent()
        else:
            self.message.setText("Por favor ingrese un DNI válido")
            print("DNI vacío")


if __name__ == "__main__":
    app = QApplication([])
    interface = MyInterface()
    interface.show()
    app.exec()
