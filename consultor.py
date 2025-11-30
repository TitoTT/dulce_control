import pymysql
from conexion import Conexion   # Si tu clase está en un archivo llamado conexion.py

class Consultor:
    def __init__(self):
        self.conexion = Conexion()

    def obtener_tabla(self, nombre_tabla):
        connection = self.conexion.conectar()
        if connection is None:
            print("No se pudo establecer la conexión.")
            return

        try:
            cursor = connection.cursor()
            query = f"SELECT * FROM {nombre_tabla};"
            cursor.execute(query)
            resultados = cursor.fetchall()

            print(f"\n=== Contenido de la tabla: {nombre_tabla} ===")
            for fila in resultados:
                print(fila)

        except Exception as e:
            print(f"Error al obtener datos de {nombre_tabla}:", e)

        finally:
            self.conexion.cerrar()


# Ejecución de prueba
if __name__ == "__main__":
    consultor = Consultor()

    # 🔹 Ejemplos de uso:
    consultor.obtener_tabla("ingredientes")
    consultor.obtener_tabla("producto")
    consultor.obtener_tabla("cliente")
    consultor.obtener_tabla("pedido")
    consultor.obtener_tabla("decoracion_perzonalizada")
    consultor.obtener_tabla("detalle_pedido")
