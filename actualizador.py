from conexion import Conexion

class Actualizador:
    def __init__(self):
        self.conexion = Conexion()

    def actualizar_manual(self, tabla, columna_pk, columnas):
        """
        tabla: nombre de la tabla
        columna_pk: columna clave primaria (id)
        columnas: lista de columnas a actualizar
        """

        connection = self.conexion.conectar()
        if connection is None:
            print("No se pudo establecer la conexión.")
            return

        try:
            print(f"\n=== Actualizando registro en la tabla {tabla} ===")
            pk_valor = input(f"Ingrese el valor de {columna_pk} del registro a actualizar: ")

            nuevos_valores = []

            print("\nIngrese los nuevos valores (deje vacío para NO modificar ese campo):\n")

            for col in columnas:
                nuevo = input(f"{col}: ")
                nuevos_valores.append(nuevo if nuevo != "" else None)

            # Construcción dinámica del SET
            set_clause = ", ".join([f"{col} = %s" for col in columnas])

            query = f"UPDATE {tabla} SET {set_clause} WHERE {columna_pk} = %s"

            # Agregamos el valor del ID al final
            valores_finales = nuevos_valores + [pk_valor]

            cursor = connection.cursor()
            cursor.execute(query, valores_finales)
            connection.commit()

            if cursor.rowcount > 0:
                print(f"✔ Registro actualizado correctamente en '{tabla}'.")
            else:
                print("❌ No se encontró un registro con ese ID.")

        except Exception as e:
            print("Error al actualizar:", e)

        finally:
            self.conexion.cerrar()



# ======= MENÚ DE ACTUALIZACIÓN =======
if __name__ == "__main__":
    act = Actualizador()

    print("=== MENÚ DE ACTUALIZACIÓN ===")
    print("1. Ingredientes")
    print("2. Producto")
    print("3. Cliente")
    print("4. Pedido")
    print("5. Decoración")
    print("6. Detalle pedido")

    op = input("Seleccione una opción: ")

    match op:
        case "1":
            act.actualizar_manual(
                "ingredientes",
                "id_ingredientes",
                ["nombre", "stock_minimo", "stock_actual", "costo_unitario", "unidad_medida"]
            )

        case "2":
            act.actualizar_manual(
                "producto",
                "id_producto",
                ["nombre", "stock", "categoria", "tiempo_preparacion", "precio", "descripcion", "id_ingredientes"]
            )

        case "3":
            act.actualizar_manual(
                "cliente",
                "id_cliente",
                ["nombre", "apellido", "telefono", "direccion"]
            )

        case "4":
            act.actualizar_manual(
                "pedido",
                "id_pedido",
                ["metodo_de_pago", "estado", "fecha_entrega", "fecha_pedido", "id_cliente"]
            )

        case "5":
            act.actualizar_manual(
                "decoracion_perzonalizada",
                "id_decoracion",
                ["tipo", "costo_extra", "id_detallePedido"]
            )

        case "6":
            act.actualizar_manual(
                "detalle_pedido",
                "id_detallePedido",
                ["precio_unitario", "cantidad", "subtotal", "id_producto", "id_pedido", "id_decoracion"]
            )

        case _:
            print("Opción no válida.")
