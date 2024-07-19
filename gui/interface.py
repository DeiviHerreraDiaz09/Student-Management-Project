
from gui.dashboard import Ui_MainWindow
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget

class MyInterface(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Interface Menu")
        
        
        self.students_2.clicked.connect(self.switch_to_studentsPage)
        
        self.payments_2.clicked.connect(self.switch_to_paymentsPage)
    
        self.reports_2.clicked.connect(self.switch_to_reportsPage)
        
    def switch_to_studentsPage(self):
        self.stackedWidget.setCurrentIndex(0)
        
    def switch_to_paymentsPage(self):
        self.stackedWidget.setCurrentIndex(1)
    
    def switch_to_reportsPage(self):
        self.stackedWidget.setCurrentIndex(2)
        
if __name__ == "__main__":
    app = QApplication([])
    interface = MyInterface()
    interface.show()
    app.exec()