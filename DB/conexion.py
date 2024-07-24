import sqlite3
import os


class Conexion:
    def __init__(self):
        try:
            db_path = os.path.join("DB", "schoolDB")
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
                    user_dni TEXT PRIMARY KEY UNIQUE,
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
                    student_dni TEXT PRIMARY KEY UNIQUE,
                    student_name TEXT NOT NULL,
                    date_of_birth TEXT NOT NULL,
                    grade TEXT NOT NULL,
                    tutor_dni TEXT NOT NULL,
                    tutor_name TEXT NOT NULL,
                    address TEXT NOT NULL,
                    tutor_email TEXT NOT NULL,
                    tutor_phone TEXT NOT NULL 
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
                    student_dni_fk TEXT NOT NULL,
                    FOREIGN KEY (student_dni_fk) REFERENCES students(student_dni)
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
                    INSERT INTO invoices (description, total_amount, remaining_amount, due_date, created_at, status, student_dni_fk)
                    VALUES (
                        'Factura mensual',
                        100, 
                        100,
                        date('now', '+1 month'),
                        date('now'),
                        'pendiente',
                        NEW.student_dni
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
                INSERT INTO users (
                    user_dni,
                    user_name,
                    user_email,
                    password,
                    role
                ) VALUES (?, ?, ?, ?, ?)
            """,
                ("1234", "Admin", "d@g.com", "1234", "Administrador"),
            )
            print("Admin creado correctamente")
            self.con.commit()
        except sqlite3.IntegrityError as e:
            print(f"Error de integridad: {e}")
        except sqlite3.Error as e:
            print(f"Error al insertar admin: {e}")
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

    def conectar(self):
        return self.con


if __name__ == "__main__":
    conexion = Conexion()
