from conexion import Conexion

class Eliminador:
    def __init__(self):
        self.conexion = Conexion()

    def eliminar_manual(self, tabla, columna_pk):
        """
        tabla: nombre de la tabla
        columna_pk: columna clave primaria para eliminar
        """

        connection = self.conexion.conectar()
        if connection is None:
            print("No se pudo establecer la conexión.")
            return

        try:
            print(f"\n=== Eliminando registro de la tabla {tabla} ===")
            pk_valor = input(f"Ingrese el valor de {columna_pk} a eliminar: ")

            query = f"DELETE FROM {tabla} WHERE {columna_pk} = %s"

            cursor = connection.cursor()
            cursor.execute(query, (pk_valor,))
            connection.commit()

            if cursor.rowcount > 0:
                print(f"✔ Registro eliminado correctamente de '{tabla}'.")
            else:
                print("❌ No se encontró un registro con ese ID.")

        except Exception as e:
            print("Error al eliminar:", e)

        finally:
            self.conexion.cerrar()



# ======= EJECUCIÓN DEL MENÚ =======
if __name__ == "__main__":
    elim = Eliminador()

    print("=== MENÚ DE ELIMINACIÓN ===")
    print("1. Ingredientes")
    print("2. Producto")
    print("3. Cliente")
    print("4. Pedido")
    print("5. Decoración")
    print("6. Detalle pedido")

    op = input("Seleccione una opción: ")

    match op:
        case "1":
            elim.eliminar_manual("ingredientes", "id_ingredientes")

        case "2":
            elim.eliminar_manual("producto", "id_producto")

        case "3":
            elim.eliminar_manual("cliente", "id_cliente")

        case "4":
            elim.eliminar_manual("pedido", "id_pedido")

        case "5":
            elim.eliminar_manual("decoracion_perzonalizada", "id_decoracion")

        case "6":
            elim.eliminar_manual("detalle_pedido", "id_detallePedido")

        case _:
            print("Opción no válida.")
