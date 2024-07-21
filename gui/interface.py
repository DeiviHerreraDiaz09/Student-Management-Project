from gui.dashboard import Ui_MainWindow
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from data.student import StudentData

class MyInterface(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Interface Menu")
        

        self.list_student_table.setColumnCount(6)
        self.list_student_table.setHorizontalHeaderLabels(['DNI', 'Nombre', 'Grado', 'Tutor', 'Teléfono Tutor', 'Nº Facturas'])
        
        self.students_2.clicked.connect(self.switch_to_studentsPage)
        self.payments_2.clicked.connect(self.switch_to_paymentsPage)
        self.reports_2.clicked.connect(self.switch_to_reportsPage)

   

        self.button_add.clicked.connect(self.switch_to_registerStudent)

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
                self.list_student_table.setItem(row_number, column_number, QTableWidgetItem(str(cell_data)))
    
    def switch_to_studentsPage(self):
        self.content.setCurrentIndex(0)
        
    def switch_to_paymentsPage(self):
        self.content.setCurrentIndex(1)
    
    def switch_to_reportsPage(self):
        self.content.setCurrentIndex(2)

    def switch_to_registerStudent(self):
        self.principal_content.setCurrentIndex(2)

if __name__ == "__main__":
    app = QApplication([])
    interface = MyInterface()
    interface.show()
    app.exec()
