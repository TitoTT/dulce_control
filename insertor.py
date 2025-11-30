from conexion import Conexion

class Insertor:
    def __init__(self):
        self.conexion = Conexion()

    def insertar_manual(self, tabla, columnas):
        """
        tabla: nombre de la tabla
        columnas: lista con los nombres de las columnas en orden
        """

        connection = self.conexion.conectar()
        if connection is None:
            print("No se pudo establecer la conexión.")
            return

        try:
            datos = []
            print(f"\n=== Insertando datos en la tabla {tabla} ===")

            # Pedir los valores
            for col in columnas:
                valor = input(f"Ingrese {col}: ")
                datos.append(valor)

            # Crear query dinámico
            col_str = ", ".join(columnas)
            val_str = ", ".join(["%s"] * len(columnas))

            query = f"INSERT INTO {tabla} ({col_str}) VALUES ({val_str})"

            cursor = connection.cursor()
            cursor.execute(query, datos)
            connection.commit()

            print(f"✔ Registro insertado correctamente en '{tabla}'.")

        except Exception as e:
            print("Error al insertar:", e)

        finally:
            self.conexion.cerrar()


# ======= EJECUCIÓN DE PRUEBA ========
if __name__ == "__main__":
    ins = Insertor()

    print("=== MENÚ DE INSERCIÓN ===")
    print("1. Ingredientes")
    print("2. Producto")
    print("3. Cliente")
    print("4. Pedido")
    print("5. Decoración")
    print("6. Detalle pedido")

    op = input("Seleccione una opción: ")

    match op:
        case "1":
            ins.insertar_manual(
                "ingredientes",
                ["id_ingredientes", "nombre", "stock_minimo", "stock_actual", "costo_unitario", "unidad_medida"]
            )

        case "2":
            ins.insertar_manual(
                "producto",
                ["id_producto", "nombre", "stock", "categoria", "tiempo_preparacion",
                 "precio", "descripcion", "id_ingredientes"]
            )

        case "3":
            ins.insertar_manual(
                "cliente",
                ["id_cliente", "nombre", "apellido", "telefono", "direccion"]
            )

        case "4":
            ins.insertar_manual(
                "pedido",
                ["id_pedido", "metodo_de_pago", "estado", "fecha_entrega", "fecha_pedido", "id_cliente"]
            )

        case "5":
            ins.insertar_manual(
                "decoracion_perzonalizada",
                ["id_decoracion", "tipo", "costo_extra", "id_detallePedido"]
            )

        case "6":
            ins.insertar_manual(
                "detalle_pedido",
                ["id_detallePedido", "precio_unitario", "cantidad", "subtotal", "id_producto", "id_pedido", "id_decoracion"]
            )

        case _:
            print("Opción no válida.")
