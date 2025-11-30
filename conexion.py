import pymysql

class Conexion:
    def __init__(self):
        self.host = "localhost"
        self.user = "root"
        self.password = "123456"
        self.database = "dulce_control"
        self.connection = None
 
    def conectar(self):
        try:
            self.connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
        )
            return self.connection
        except Exception as e:
            print("Error al conectar:", e)
            return None
        
    def cerrar(self):
        if self.connection:
            self.connection.close()