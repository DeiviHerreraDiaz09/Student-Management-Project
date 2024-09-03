from datetime import datetime
import conexion as con
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
            self.configuration_default()
            self.period_rates_initial()
            self.actualizar_estado_facturas()
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
                    school_mora REAL NOT NULL, 
                    school_nfc TEXT NOT NULL,
                    school_mora_progress TEXT NOT NULL
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
                    original_amount INTEGER NOT NULL,
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
                    rate_amount REAL NOT NULL
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
                    FOREIGN KEY (student_id_fk) REFERENCES students(student_ident)
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

    def period_rates_initial(self):
        try:
            cursor = self.con.cursor()

            cursor.execute(
                """
            SELECT COUNT(*) FROM periods WHERE initial_period = ? AND final_period = ?
            """,
                ("01/01/2024", "31/12/2024"),
            )
            count = cursor.fetchone()[0]

            if count == 0:
                cursor.execute(
                    """
                INSERT INTO periods (initial_period, final_period) VALUES (?, ?)
                """,
                    ("01/01/2024", "31/12/2024"),
                )

            cursor.execute(
                """
            SELECT COUNT(*) FROM rates WHERE rate_name = ?
            """,
                ("Normal",),
            )
            count = cursor.fetchone()[0]

            if count == 0:
                cursor.execute(
                    """
                INSERT INTO rates (rate_name, rate_amount) VALUES (?, ?)
                """,
                    ("Normal", 2000),
                )

            print("periodos/tarifas cread@s correctamente")
            self.con.commit()
        except sqlite3.Error as e:
            print(f"Error al cargar el periodo y la tarifa inicial")
        except Exception as ex:
            print(f"Otro error: {ex}")
        finally:
            cursor.close()

    def actualizar_estado_facturas(self):
        try:
            cursor = self.con.cursor()
            cursor.execute(
                "SELECT school_mora, school_mora_progress FROM configurations LIMIT 1"
            )
            config = cursor.fetchone()

            mora_base = config[0]
            mora_progress = config[1]

            if mora_base is None or mora_progress is None:
                raise ValueError(
                    "La mora o el progreso de la mora no están definidos en la configuración."
                )

            mora_base_decimal = mora_base / 100.0

            cursor.execute(
                """
                SELECT invoice_id, original_amount, total_amount, remaining_amount, due_date
                FROM invoices
                WHERE (status = 'Generado' OR status = 'Tardío')
                AND due_date <= date('now')
                """
            )
            facturas_vencidas = cursor.fetchall()

            for factura in facturas_vencidas:
                (
                    invoice_id,
                    original_amount,
                    total_amount,
                    remaining_amount,
                    due_date,
                ) = factura

                due_date_dt = datetime.strptime(due_date, "%Y-%m-%d")
                days_overdue = (datetime.now() - due_date_dt).days

                if mora_progress == "Sí" and days_overdue > 0:
                    mora_accumulada = mora_base_decimal + (days_overdue * 0.005)
                    total_amount_con_mora = original_amount * (1 + mora_accumulada)
                else:
                    total_amount_con_mora = original_amount * (1 + mora_base_decimal)

                cursor.execute(
                    """
                    SELECT SUM(payment_paid)
                    FROM payments
                    WHERE invoice_id_fk = ?
                    """,
                    (invoice_id,),
                )
                pagos_realizados = cursor.fetchone()[0] or 0

                restante_actual = total_amount_con_mora - pagos_realizados

                cursor.execute(
                    """
                    UPDATE invoices
                    SET status = 'Tardío',
                        total_amount = ?,
                        remaining_amount = ?
                    WHERE invoice_id = ?
                    """,
                    (total_amount_con_mora, restante_actual, invoice_id),
                )

            self.con.commit()
            print("Estado de facturas actualizado correctamente")

        except sqlite3.Error as e:
            print(f"Error al actualizar el estado de las facturas: {e}")
        except ValueError as ve:
            print(ve)
        finally:
            cursor.close()

    def loginService(self, user_id):
        db = con.Conexion().conectar()
        cursor = db.cursor()
        try:
            query = """
                INSERT INTO monitoring_user (user_id_fk, monitoring_date, action)
                VALUES (?, ?, ?)
            """
            cursor.execute(
                query,
                (
                    user_id,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "El usuario entró al sistema",
                ),
            )
            db.commit()
            print("Registro de monitoreo insertado correctamente.")
        except Exception as e:
            print(f"Error al insertar el registro de monitoreo: {e}")
        finally:
            cursor.close()
            db.close()

    def logoutService(self, user_id):
        db = con.Conexion().conectar()
        cursor = db.cursor()
        try:
            query = """
                INSERT INTO monitoring_user (user_id_fk, monitoring_date, action)
                VALUES (?, ?, ?)
            """
            cursor.execute(
                query,
                (
                    user_id,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "El usuario cerró sesión",
                ),
            )
            db.commit()
        except Exception as e:
            print(f"Error al insertar el registro de monitoreo: {e}")
        finally:
            cursor.close()
            db.close()

    def configuration_default(self):
        try:
            cursor = self.con.cursor()
            cursor.execute("SELECT COUNT(*) FROM configurations")
            count = cursor.fetchone()[0]

            if count == 0:
                cursor.execute(
                    """
                    INSERT INTO configurations (school_name, school_address, school_phone, school_mora, school_nfc, school_mora_progress)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        "Default School",
                        "123 Default Address",
                        "555-555-5555",
                        3.75,
                        "No NFC",
                        "Sí",
                    ),
                )
                self.con.commit()
                print("Configuración por defecto creada.")
            else:
                print("Configuración existente, no se necesita crear una nueva.")
        except Exception as e:
            print("Error al consultar o crear la configuración por defecto:", str(e))

    def conectar(self):
        return self.con


if __name__ == "__main__":
    conexion = Conexion()
