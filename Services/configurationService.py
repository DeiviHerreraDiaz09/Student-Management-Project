import conexion as con
from PyQt6.QtWidgets import QMessageBox


def configuration_optionsService(self):
    try:
        db = con.Conexion().conectar()
        cursor = db.cursor()
        cursor.execute(
            """
                SELECT school_name, school_address, school_phone, school_mora, school_nfc 
                FROM configurations LIMIT 1
                """
        )
        configuration = cursor.fetchone()
        if configuration:
            self.input_amount_paid_3.setText(configuration[0])
            self.input_amount_paid_4.setText(configuration[1])
            self.input_amount_paid_2.setText(configuration[2])
            self.input_amount_paid_5.setText(str(configuration[3]))
            self.input_amount_paid_6.setText(configuration[4])
        else:
            print("No se encontró ninguna configuración.")
    except Exception as e:
        print("Error al cargar la configuración en la interfaz:", str(e))


def update_configurationService(self, campo, valor):
    try:
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Confirmación")
        msg_box.setText(f"¿Estás seguro de que deseas actualizar el campo {campo}?")
        msg_box.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        msg_box.setStyleSheet(
            """
                QLabel {
                    color: white;
                }
                QPushButton {
                    background-color: white;
                    color: black;
                    border: 1px solid black;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #e6e6e6;
                }
                QMessageBox {
                    border: 2px solid black;
                }
                """
        )

        response = msg_box.exec()

        if response == QMessageBox.StandardButton.Yes:
            db = con.Conexion().conectar()
            cursor = db.cursor()
            cursor.execute(
                f"UPDATE configurations SET {campo} = ? WHERE configuration_id = 1",
                (valor,),
            )
            db.commit()

            msg_box_success = QMessageBox()
            msg_box_success.setWindowTitle("Éxito")
            msg_box_success.setText(
                f"El campo {campo} se ha actualizado correctamente."
            )

            msg_box_success.setStyleSheet(
                """
                    QLabel {
                        color: white;
                    }
                    QPushButton {
                        background-color: white;
                        color: black;
                        border: 1px solid black;
                        padding: 5px;
                    }
                    QPushButton:hover {
                        background-color: #e6e6e6;
                    }
                    QMessageBox {
                        border: 2px solid black;
                    }
                    """
            )
            msg_box_success.exec()

        else:
            msg_box_cancel = QMessageBox()
            msg_box_cancel.setWindowTitle("Cancelado")
            msg_box_cancel.setText(
                f"La actualización del campo {campo} ha sido cancelada."
            )

            msg_box_cancel.setStyleSheet(
                """
                    QLabel {
                        color: white;
                    }
                    QPushButton {
                        background-color: white;
                        color: black;
                        border: 1px solid black;
                        padding: 5px;
                    }
                    QPushButton:hover {
                        background-color: #e6e6e6;
                    }
                    QMessageBox {
                        border: 2px solid black;
                    }
                    """
            )
            msg_box_cancel.exec()

    except Exception as e:
        msg_box_error = QMessageBox()
        msg_box_error.setWindowTitle("Error")
        msg_box_error.setText(f"Error al actualizar la configuración: {str(e)}")

        msg_box_error.setStyleSheet(
            """
                QLabel {
                    color: black;
                }
                QPushButton {
                    background-color: white;
                    color: black;
                    border: 1px solid black;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #e6e6e6;
                }
                QMessageBox {
                    border: 2px solid black;
                }
                """
        )
        msg_box_error.exec()


def ask_for_ncf_service(self, payments, rows):
    db = con.Conexion().conectar()
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT school_nfc, school_name, school_address, school_phone FROM configurations LIMIT 1
        """
    )
    ncf_row = cursor.fetchone()

    school_info = {
        "school_name": ncf_row[1] if ncf_row else "Nombre no disponible",
        "school_address": ncf_row[2] if ncf_row else "Dirección no disponible",
        "school_phone": ncf_row[3] if ncf_row else "Teléfono no disponible",
    }

    cursor.close()
    db.close()

    msg_box = QMessageBox(self)
    msg_box.setWindowTitle("Incluir NCF")
    msg_box.setText("¿Desea incluir el NCF en el PDFSSSSSS")
    msg_box.setStandardButtons(
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )

    msg_box.setStyleSheet(
        """
        QLabel {
            color: black;
        }
        QPushButton {
            background-color: white;
            color: black;
            border: 1px solid black;
            padding: 5px;
        }
        QPushButton:hover {
            background-color: #e6e6e6;
        }
        QMessageBox {
            border: 2px solid black;
        }
    """
    )

    reply = msg_box.exec()

    if reply == QMessageBox.StandardButton.Yes:
        ncf = ncf_row[0] if ncf_row else "N/A"
        self.generate_pdf(payments, rows, school_info, ncf=ncf)
    elif reply == QMessageBox.StandardButton.No:
        print("HOLA")
        self.generate_pdf(payments, rows, school_info)
    else:
        # Si la ventana se cierra con la "X", exec() retorna un valor no relacionado con "Yes" o "No"
        return
