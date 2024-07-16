import sqlite3


class Conexion:
    def __init__(self):
        try:
            self.con = sqlite3.connect("schoolDB")
            self.creartablas()
            self.crearAdmin()
        except Exception as ex:
            print(ex)

    def creartablas(self):
        try:
            cursor = self.con.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_dni TEXT PRIMARY KEY UNIQUE,
                    user_name TEXT NOT NULL,
                    user_email TEXT NOT NULL7,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL
                )
            """)
            self.con.commit()
        except Exception as ex:
            print(ex)
        finally:
            cursor.close()

    def crearAdmin(self):
        try:
            cursor = self.con.cursor()
            cursor.execute("""
                INSERT INTO users (
                    user_dni,
                    user_name,
                    user_email,
                    password,
                    role
                ) VALUES ("1033679469", "Deivi", "d@g.com", "1234", "Administrador")
            """)
            self.con.commit()
        except Exception as ex:
            print(ex)
        finally:
            cursor.close()

    def conectar(self):
        return self.con


if __name__ == "__main__":
    conexion = Conexion()
