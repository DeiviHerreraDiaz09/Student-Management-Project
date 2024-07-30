from datetime import datetime, timedelta
import sqlite3
import sys
import os

COURSE_FEES = {
    "Kinder": 15,
    "1° Primaria": 30,
    "2° Primaria": 45,
    "3° Primaria": 60,
    "4° Primaria": 75,
    "5° Primaria": 90,
    "1° Secundaria": 105,
    "2° Secundaria": 120,
    "3° Secundaria": 135,
    "4° Secundaria": 150,
    "5° Secundaria": 165,
    "6° Secundaria": 180,
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
            self.crearTriggers()
            self.crearAdmin()
            self.consultar_y_crear_facturas()
            self.actualizar_grado_estudiantes()
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
                CREATE TABLE IF NOT EXISTS students (
                    student_ident TEXT PRIMARY KEY,
                    student_name TEXT NOT NULL,
                    date_of_birth TEXT NOT NULL,
                    grade TEXT NOT NULL,
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
                    SET status = 'Pagada', remaining_amount = 0
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
                SET status = 'Mora'
                WHERE status = 'pendiente'
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
                "Kinder": "1° primaria",
                "1° Primaria": "2° Primaria",
                "2° Primaria": "3° Primaria",
                "3° Primaria": "4° primaria",
                "4° Primaria": "5° Secundaria",
                "5° Primaria": "1° Secundaria",
                "1° Secundaria": "2° Secundaria",
                "2° Secundaria": "3° Secundaria",
                "3° Secundaria": "4° Secundaria",
                "4° Secundaria": "5° Secundaria",
                "5° Secundaria": "6° Secundaria",
                "6° Secundaria": "Graduado",
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
            print("Grado de estudiantes actualizado correctamente")
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
                    "pendiente",
                    student_ident,
                ),
            )
            self.con.commit()
            print(
                f"Factura creada para el estudiante {student_ident} con tarifa {fee_amount}"
            )
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
