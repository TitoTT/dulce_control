import pymysql
from conexion import Conexion

class Insertor:
    def __init__(self):
        self.conexion = Conexion()

    def registrar_pedido_completo_gui(self, id_cliente, fecha_entrega, metodo_pago, carrito):
        conn = self.conexion.conectar()
        if not conn: return False
        
        try:
            with conn.cursor() as cursor:
                # 1. Insertar Cabecera
                cursor.execute("INSERT INTO pedido (id_cliente, fecha_pedido, fecha_entrega, metodo_de_pago, estado) VALUES (%s, NOW(), %s, %s, 'Pendiente')", 
                               (id_cliente, fecha_entrega, metodo_pago))
                id_pedido = cursor.lastrowid

                # 2. Detalles y DESCUENTO de inventario
                for p in carrito:
                    # Guardar detalle
                    cursor.execute("INSERT INTO detalle_pedido (id_pedido, id_producto, cantidad, precio_unitario, subtotal) VALUES (%s, %s, %s, %s, %s)",
                                   (id_pedido, p['id'], p['cantidad'], p['precio'], p['precio'] * p['cantidad']))
                    
                    # --- LÓGICA DE DESCUENTO AUTOMÁTICO ---
                    # Buscamos qué ingredientes y qué cantidad usa este producto
                    cursor.execute("SELECT id_ingredientes, cantidad_requerida FROM recetas WHERE id_producto = %s", (p['id'],))
                    ingredientes = cursor.fetchall() or []

                    for row in ingredientes:
                        if not row:
                            continue
                        try:
                            # fetchall aquí devuelve tuplas (id, cantidad)
                            ing_id, cant_req = row
                        except Exception:
                            # fila inesperada, omitirla
                            continue

                        # Calculamos total a descontar (cantidad del producto * cantidad en receta)
                        try:
                            total_descontar = p['cantidad'] * float(cant_req)
                        except Exception:
                            # cantidad no válida en receta, saltar
                            continue

                        # Actualizar stock directamente, pero NO permitir negativo
                        cursor.execute(
                            "UPDATE ingredientes SET stock_actual = GREATEST(0, stock_actual - %s) WHERE id_ingredientes = %s",
                            (total_descontar, ing_id)
                        )

                conn.commit()
                return id_pedido
        except Exception as e:
            conn.rollback()
            print(f"Error en transacción: {e}")
            return False
        finally:
            self.conexion.cerrar()