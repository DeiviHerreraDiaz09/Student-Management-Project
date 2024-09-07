import conexion as con
from PyQt6.QtCore import QDate

def Service_register_expense(self):
    try:
        db = con.Conexion().conectar()
        cursor = db.cursor()

        description = self.plainText_description_cost.toPlainText()
        total_amount = self.lineEdit_totalC.text()
        created_at = self.dateCost_2.date().toString("yyyy-MM-dd")

        if len(description) <= 6:
            self.message_2.setText("Es necesario una descripción válida (mínimo 10 caracteres)")  # INTEGRAR MENSAJE EN LA INTERFAZ
            self.plainText_description_cost.setFocus()
            return
        if not total_amount.isdigit() or int(total_amount) <= 0:
            self.message_2.setText("Ingrese un monto válido")  # INTEGRAR MENSAJE EN LA INTERFAZ
            self.lineEdit_totalC.setFocus()
            return
        if not QDate.fromString(created_at, "yyyy-MM-dd").isValid():
            self.message_2.setText("Seleccione una fecha válida")
            self.dateCost_2.setFocus()
            return

        cursor.execute(
            """
            INSERT INTO expenses (description, total_amount, created_at)
            VALUES (?, ?, ?)
            """,
            (description, total_amount, created_at)
        )

        db.commit()
        db.close()

        self.plainText_description_cost.clear()
        self.lineEdit_totalC.clear()
        self.dateCost_2.clear()

        self.switch_to_expensesPage()

    except Exception as e:
        print(f"Error al registrar el gasto: {e}")
        self.message_2.setText(f"Error: {e}")
