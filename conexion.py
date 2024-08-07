from datetime import datetime, timedelta
import sqlite3
import sys
import os

COURSE_FEES = {
    "Nido": 15,
    "Pre Kinder": 30,
    "Kinder": 45,
    "Pre Primario": 60,
    "1ero Primaria": 75,
    "2do Primaria": 105,
    "3ero Primaria": 120,
    "4to Primaria": 135,
    "5to Primaria": 150,
    "6to Primaria": 165,
    "1ero Secundaria": 180,
    "2do Secundaria": 195,
    "3ero Secundaria": 210,
    "4to Secundaria": 225,
    "5to Secundaria": 240,
    "6to Secundaria": 255,
}


class Conexion:
    def __init__(self):
        try:
            db_path = (
                os.path.join(sys._MEIPASS, "DB", "schoolDB")
                if getattr(sys, "frozen", False)
                else os.path.join("DB", "schoolDB")
            )
            self.con = sqlite3.connect(db_path)
            self.creartablas()
            # self.crearTriggers()
            # self.crearAdmin()
            # self.consultar_y_crear_facturas()
            # self.actualizar_grado_estudiantes()
            # self.actualizar_estado_facturas()
        except sqlite3.Error as e:
            print(f"Error al conectar con la base de datos: {e}")
        except Exception as ex:
            print(f"Otro error: {ex}")

    def creartablas(self):
        try:
            cursor = self.con.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_name TEXT NOT NULL,
                    user_email TEXT NOT NULL, 
                    password TEXT NOT NULL,
                    role TEXT NOT NULL
                )
            """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS monitoring_user (
                    monitoring_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id_fk INTEGER NOT NULL,
                    monitoring_date TEXT NOT NULL,
                    action TEXT NOT NULL,
                    FOREIGN KEY (user_id_fk) REFERENCES users(user_id)
                )
            """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS configurations (
                    configuration_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    school_name TEXT NOT NULL,
                    school_address TEXT NOT NULL,
                    school_phone TEXT NOT NULL,
                    school_mora TEXT NOT NULL, 
                    school_nfc TEXT NOT NULL
                )
            """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS students (
                    student_ident TEXT PRIMARY KEY,
                    student_name TEXT NOT NULL,
                    date_of_birth TEXT NOT NULL,
                    tutor_dni TEXT NOT NULL,
                    year_progress INTEGER NOT NULL,
                    tutor_name TEXT NOT NULL,
                    address TEXT NOT NULL,
                    tutor_email TEXT NOT NULL,
                    tutor_phone TEXT NOT NULL,
                    status TEXT NOT NULL
                )
            """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS invoices (
                    invoice_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    description TEXT NOT NULL,
                    total_amount INTEGER NOT NULL,
                    remaining_amount INTEGER NOT NULL,
                    due_date TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    status TEXT NOT NULL,
                    student_ident_fk TEXT NOT NULL,
                    FOREIGN KEY (student_ident_fk) REFERENCES students(student_ident)
                )
            """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS payments (
                    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    payment_date TEXT NOT NULL,
                    payment_paid INTEGER NOT NULL,
                    payment_method TEXT NOT NULL,
                    invoice_id_fk INTEGER NOT NULL,
                    FOREIGN KEY (invoice_id_fk) REFERENCES invoices(invoice_id)
                )
            """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS periods (
                    period_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    initial_period TEXT NOT NULL,
                    final_period TEXT NOT NULL
                    )
            """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS rates (
                    rate_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rate_name TEXT NOT NULL,
                    rate_amount TEXT NOT NULL
                    )
            """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS enrollments (
                    enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    enrollment_date TEXT NOT NULL,
                    status TEXT NOT NULL,
                    grade TEXT NOT NULL,
                    enrollment_amount INTEGER NOT NULL,
                    rate_id_fk INTEGER NOT NULL,
                    period_id_fk INTEGER NOT NULL,
                    student_id_fk INTEGER NOT NULL,
                    FOREIGN KEY (rate_id_fk) REFERENCES rates(rate_id)
                    FOREIGN KEY (period_id_fk) REFERENCES periods(period_id )
                    FOREIGN KEY (student_id_fk) REFERENCES users(user_id)
                )
            """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS expenses (
                    expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    description TEXT NOT NULL,
                    total_amount INTEGER NOT NULL,
                    created_at TEXT NOT NULL 
                )
            """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS cash_closings (
                    cash_closing_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cash_closing_date TEXT NOT NULL,
                    cash_closing_enrollment_amount INTEGER NOT NULL,
                    cash_closing_payments_amount INTEGER NOT NULL,
                    cash_closing_expenses_amount INTEGER NOT NULL,
                    total_amount_closing INTEGER NOT NULL 
                )
            """
            )
            print("Tablas creadas correctamente")
            self.con.commit()
        except sqlite3.Error as e:
            print(f"Error al crear tablas: {e}")
        except Exception as ex:
            print(f"Otro error: {ex}")
        finally:
            cursor.close()

    def crearTriggers(self):
        try:
            cursor = self.con.cursor()
            cursor.execute(
                """
                CREATE TRIGGER IF NOT EXISTS payment_trigger
                AFTER INSERT ON payments
                FOR EACH ROW
                BEGIN
                    UPDATE invoices
                    SET remaining_amount = remaining_amount - NEW.payment_paid
                    WHERE invoice_id = NEW.invoice_id_fk;

                    UPDATE invoices
                    SET status = 'Pagado', remaining_amount = 0
                    WHERE invoice_id = NEW.invoice_id_fk AND remaining_amount <= 0;
                END;
                """
            )
            print("Triggers creados correctamente")
            self.con.commit()
        except sqlite3.Error as e:
            print(f"Error al crear triggers: {e}")
        except Exception as ex:
            print(f"Otro error: {ex}")
        finally:
            cursor.close()

    def crearAdmin(self):
        try:
            cursor = self.con.cursor()
            cursor.execute(
                """
                SELECT COUNT(*) FROM users WHERE user_email = ?
                """,
                ("d@g.com",),
            )
            admin_count = cursor.fetchone()[0]

            if admin_count == 0:
                cursor.execute(
                    """
                    INSERT INTO users (
                        user_name,
                        user_email,
                        password,
                        role
                    ) VALUES (?, ?, ?, ?)
                """,
                    ("Admin", "d@g.com", "1234", "Administrador"),
                )
                print("Admin creado correctamente")
            else:
                print("El administrador ya existe")

            self.con.commit()
        except sqlite3.Error as e:
            print(f"Error al verificar o insertar admin: {e}")
        except Exception as ex:
            print(f"Otro error: {ex}")
        finally:
            cursor.close()

    def actualizar_estado_facturas(self):
        try:
            cursor = self.con.cursor()
            cursor.execute(
                """
                UPDATE invoices
                SET status = 'Tardío'
                WHERE status = 'Generado'
                AND due_date <= date('now')
                """
            )

            self.con.commit()
            print("Estado de facturas actualizado correctamente")

        except sqlite3.Error as e:
            print(f"Error al actualizar el estado de las facturas: {e}")

        finally:
            cursor.close()

    def actualizar_grado_estudiantes(self):
        try:
            cursor = self.con.cursor()
            current_year = datetime.now().year

            grade_mapping = {
                "Nido": "Pre Kinder",
                "Pre Kinder": "Kinder",
                "Kinder": "Pre Primario",
                "Pre primario": "1ero Primaria",
                "1ero Primaria": "2do Primaria",
                "2do Primaria": "3ero Primaria",
                "3ero Primaria": "4to Primaria",
                "4to Primaria": "5to Primaria",
                "5to Primaria": "6to Primaria",
                "6to Primaria": "1ero Secundaria",
                "1ero Secundaria": "2do Secundaria",
                "2do Secundaria": "3ero Secundaria",
                "3ero Secundaria": "4to Secundaria",
                "4to Secundaria": "5to Secundaria",
                "5to Secundaria": "6to Secundaria",
                "6to Secundaria": "Graduado",
            }

            cursor.execute(
                """
                SELECT student_ident, grade, year_progress
                FROM students
                """
            )

            students = cursor.fetchall()

            for student_ident, grade, year_progress in students:
                if int(year_progress) < current_year and grade in grade_mapping:
                    new_grade = grade_mapping[grade]
                    cursor.execute(
                        """
                        UPDATE students
                        SET grade = ?, year_progress = ?
                        WHERE student_ident = ?
                        """,
                        (new_grade, current_year, student_ident),
                    )

            self.con.commit()
        except sqlite3.Error as e:
            print(f"Error al actualizar el grado de los estudiantes: {e}")
        finally:
            cursor.close()

    def crear_factura(self, student_ident, grade, due_date=None):
        try:
            cursor = self.con.cursor()
            fee_amount = COURSE_FEES.get(grade, 100)

            if due_date is None:
                due_date = datetime.now() + timedelta(days=30)
            else:
                due_date = datetime.strptime(due_date, "%Y-%m-%d")

            due_date_str = due_date.strftime("%Y-%m-%d")

            cursor.execute(
                """
                INSERT INTO invoices (description, total_amount, remaining_amount, due_date, created_at, status, student_ident_fk)
                VALUES (?, ?, ?, ?, date('now'), ?, ?)
                """,
                (
                    "Factura mensual",
                    fee_amount,
                    fee_amount,
                    due_date_str,
                    "Generado",
                    student_ident,
                ),
            )
            self.con.commit()
        except sqlite3.Error as e:
            print(f"Error al crear factura: {e}")
        finally:
            cursor.close()

    def consultar_y_crear_facturas(self):
        try:
            cursor = self.con.cursor()
            cursor.execute(
                """
                SELECT s.student_ident, s.grade, MAX(i.due_date) as last_invoice_date
                FROM students s
                LEFT JOIN invoices i ON s.student_ident = i.student_ident_fk
                GROUP BY s.student_ident
                """
            )

            students = cursor.fetchall()
            current_date = datetime.now().date()

            for student_ident, grade, last_invoice_date in students:
                if last_invoice_date:
                    last_invoice_date = datetime.strptime(
                        last_invoice_date, "%Y-%m-%d"
                    ).date()
                    while last_invoice_date <= current_date:
                        last_invoice_date += timedelta(days=30)
                        self.crear_factura(
                            student_ident,
                            grade,
                            due_date=last_invoice_date.strftime("%Y-%m-%d"),
                        )
                else:
                    self.crear_factura(student_ident, grade)

        except sqlite3.Error as e:
            print(f"Error al consultar y crear facturas: {e}")
        finally:
            cursor.close()

    def conectar(self):
        return self.con


if __name__ == "__main__":
    conexion = Conexion()
