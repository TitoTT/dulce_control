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

    def insertar_ingrediente(self, nombre: str, stock_actual: float, unidad_medida: str, costo_unitario: float, stock_minimo: float) -> bool:
        """Inserta un nuevo ingrediente en la tabla de ingredientes"""
        conn = self.conexion.conectar()
        if not conn:
            return False
        
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO ingredientes 
                       (nombre, stock_actual, unidad_medida, costo_unitario, stock_minimo) 
                       VALUES (%s, %s, %s, %s, %s)""",
                    (nombre, stock_actual, unidad_medida, costo_unitario, stock_minimo)
                )
                conn.commit()
                return True
        except Exception as e:
            conn.rollback()
            print(f"Error al insertar ingrediente: {e}")
            return False
        finally:
            self.conexion.cerrar()

    def actualizar_ingrediente(self, nombre: str, stock_actual: float, unidad_medida: str, costo_unitario: float, stock_minimo: float) -> bool:
        """Actualiza un ingrediente existente (suma el stock, actualiza costo y stock mínimo)"""
        conn = self.conexion.conectar()
        if not conn:
            return False
        
        try:
            with conn.cursor() as cursor:
                # Obtener el stock actual del ingrediente existente
                cursor.execute("SELECT stock_actual FROM ingredientes WHERE nombre = %s", (nombre,))
                resultado = cursor.fetchone()
                if not resultado:
                    return False
                
                stock_anterior = resultado[0] if isinstance(resultado, tuple) else resultado.get('stock_actual', 0)
                nuevo_stock = stock_anterior + stock_actual  # Sumar los stocks
                
                # Actualizar el ingrediente
                cursor.execute(
                    """UPDATE ingredientes 
                       SET stock_actual = %s, unidad_medida = %s, costo_unitario = %s, stock_minimo = %s
                       WHERE nombre = %s""",
                    (nuevo_stock, unidad_medida, costo_unitario, stock_minimo, nombre)
                )
                conn.commit()
                return True
        except Exception as e:
            conn.rollback()
            print(f"Error al actualizar ingrediente: {e}")
            return False
        finally:
            self.conexion.cerrar()
    
    def eliminar_ingrediente(self, nombre: str) -> tuple:
        """Elimina un ingrediente por su nombre. Retorna (éxito, mensaje)."""
        conn = self.conexion.conectar()
        if not conn:
            return False, "Error de conexión a la base de datos"

        try:
            with conn.cursor() as cursor:
                # Obtener id del ingrediente
                cursor.execute("SELECT id_ingredientes FROM ingredientes WHERE nombre = %s", (nombre,))
                resultado = cursor.fetchone()
                if not resultado:
                    return False, f"El insumo '{nombre}' no existe"
                
                id_ing = resultado[0] if isinstance(resultado, tuple) else resultado.get('id_ingredientes')
                
                # Verificar si tiene recetas asociadas
                cursor.execute("SELECT COUNT(*) as total FROM recetas WHERE id_ingredientes = %s", (id_ing,))
                recetas = cursor.fetchone()
                count_recetas = 0
                if recetas:
                    count_recetas = recetas[0] if isinstance(recetas, tuple) else recetas.get('total', 0)
                
                if count_recetas > 0:
                    return False, f"No se puede eliminar '{nombre}' porque tiene {count_recetas} receta(s) asociada(s). Elimina primero las recetas que lo usan."
                
                # Si no hay recetas, proceder con la eliminación
                cursor.execute("DELETE FROM ingredientes WHERE nombre = %s", (nombre,))
                filas = cursor.rowcount
                conn.commit()
                
                if filas > 0:
                    return True, f"Insumo '{nombre}' eliminado correctamente"
                else:
                    return False, f"No se pudo eliminar '{nombre}'"
        except Exception as e:
            conn.rollback()
            print(f"Error al eliminar ingrediente: {e}")
            return False, f"Error al eliminar: {str(e)}"
        finally:
            self.conexion.cerrar()

    def eliminar_ingrediente_por_id(self, id_ing: int) -> tuple:
        """Elimina un ingrediente específico por su ID. Retorna (éxito, mensaje)."""
        conn = self.conexion.conectar()
        if not conn:
            return False, "Error de conexión a la base de datos"

        try:
            with conn.cursor() as cursor:
                # Obtener nombre del ingrediente
                cursor.execute("SELECT nombre FROM ingredientes WHERE id_ingredientes = %s", (id_ing,))
                resultado = cursor.fetchone()
                if not resultado:
                    return False, f"El insumo con ID {id_ing} no existe"
                
                nombre = resultado[0] if isinstance(resultado, tuple) else resultado.get('nombre')
                
                # Verificar si tiene recetas asociadas
                cursor.execute("SELECT COUNT(*) as total FROM recetas WHERE id_ingredientes = %s", (id_ing,))
                recetas = cursor.fetchone()
                count_recetas = 0
                if recetas:
                    count_recetas = recetas[0] if isinstance(recetas, tuple) else recetas.get('total', 0)
                
                if count_recetas > 0:
                    return False, f"No se puede eliminar '{nombre}' porque tiene {count_recetas} receta(s) asociada(s). Elimina primero las recetas que lo usan."
                
                # Si no hay recetas, proceder con la eliminación por ID
                cursor.execute("DELETE FROM ingredientes WHERE id_ingredientes = %s", (id_ing,))
                filas = cursor.rowcount
                conn.commit()
                
                if filas > 0:
                    return True, f"Insumo '{nombre}' eliminado correctamente"
                else:
                    return False, f"No se pudo eliminar '{nombre}'"
        except Exception as e:
            conn.rollback()
            print(f"Error al eliminar ingrediente: {e}")
            return False, f"Error al eliminar: {str(e)}"
        finally:
            self.conexion.cerrar()