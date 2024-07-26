from datetime import datetime
import sqlite3
import sys
import os


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
                    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_name TEXT NOT NULL,
                    date_of_birth TEXT NOT NULL,
                    grade TEXT NOT NULL,
                    year_progress INTEGER NOT NULL,
                    tutor_dni TEXT NOT NULL,
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
                    student_id_fk INTEGER NOT NULL,
                    FOREIGN KEY (student_id_fk) REFERENCES students(student_id)
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
                CREATE TRIGGER IF NOT EXISTS invoice_trigger
                AFTER INSERT ON students
                FOR EACH ROW
                BEGIN
                    INSERT INTO invoices (description, total_amount, remaining_amount, due_date, created_at, status, student_id_fk)
                    VALUES (
                        'Factura mensual',
                        100, 
                        100,
                        date('now', '+1 month'),
                        date('now'),
                        'pendiente',
                        NEW.student_id
                    );
                END;
            """
            )
            cursor.execute(
                """
                CREATE TRIGGER IF NOT EXISTS payment_trigger
                AFTER INSERT ON payments
                FOR EACH ROW
                BEGIN
                    UPDATE invoices
                    SET description = 'Factura mensual - abonado ' || (SELECT SUM(payment_paid) FROM payments WHERE invoice_id_fk = NEW.invoice_id_fk),
                        remaining_amount = remaining_amount - NEW.payment_paid
                    WHERE invoice_id = NEW.invoice_id_fk;
                    
                    UPDATE invoices
                    SET status = 'Pagada'
                    WHERE invoice_id = NEW.invoice_id_fk
                    AND (SELECT SUM(payment_paid) FROM payments WHERE invoice_id_fk = NEW.invoice_id_fk) >= (SELECT total_amount FROM invoices WHERE invoice_id = NEW.invoice_id_fk);
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
                "Kinder": "1 primaria",
                "1 primaria": "2 primaria",
                "2 primaria": "3 primaria",
                "3 primaria": "1 secundaria",
                "1 secundaria": "2 secundaria",
                "2 secundaria": "3 secundaria",
                "3 secundaria": "Graduado",
            }

            cursor.execute(
                """
                SELECT student_id, grade, year_progress
                FROM students
                """
            )

            students = cursor.fetchall()

            for student_id, grade, year_progress in students:
                if int(year_progress) < current_year and grade in grade_mapping:
                    new_grade = grade_mapping[grade]
                    cursor.execute(
                        """
                        UPDATE students
                        SET grade = ?, year_progress = ?
                        WHERE student_id = ?
                        """,
                        (new_grade, current_year, student_id),
                    )

            self.con.commit()
            print("Grado de estudiantes actualizado correctamente")
        except sqlite3.Error as e:
            print(f"Error al actualizar el grado de los estudiantes: {e}")
        finally:
            cursor.close()

    def conectar(self):
        return self.con


if __name__ == "__main__":
    conexion = Conexion()
