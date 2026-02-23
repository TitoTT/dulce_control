import pymysql
from conexion import Conexion
from typing import Optional, Any, List, Dict

class Consultor:
    def __init__(self):
        self.conexion = Conexion()

    def _ejecutar_consulta(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """
        Método privado que centraliza la ejecución. 
        Retorna siempre una LISTA de DICCIONARIOS.
        """
        connection = self.conexion.conectar()
        if connection is None:
            return []

        resultados = []
        try:
            # DictCursor convierte cada fila en un diccionario {'columna': valor}
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                resultados = list(cursor.fetchall())
        except Exception as e:
            print(f"❌ Error en Consultor: {e}")
        finally:
            self.conexion.cerrar()
            
        return resultados
    ##########################################################################################################################################################################

    def obtener_pedidos(self, estado: str = "todos",
                        desde: str | None = None, hasta: str | None = None) -> List[Dict]:
        condiciones = []
        params = []

        if estado != "todos":
            condiciones.append("p.estado = %s")
            params.append(estado)
        if desde:
            condiciones.append("p.fecha_pedido >= %s")
            params.append(desde)
        if hasta:
            condiciones.append("p.fecha_pedido <= %s")
            params.append(hasta)

        where = ("WHERE " + " AND ".join(condiciones)) if condiciones else ""

        query = f"""
            SELECT 
                p.id_pedido,
                CONCAT(c.nombre, ' ', c.apellido) AS cliente,
                p.estado,
                p.fecha_pedido,
                p.fecha_entrega,
                p.metodo_de_pago,
                p.observaciones,
                SUM(dp.subtotal) AS total
            FROM pedido p
            JOIN cliente c ON p.id_cliente = c.id_cliente
            JOIN detalle_pedido dp ON dp.id_pedido = p.id_pedido
            {where}
            GROUP BY p.id_pedido, c.nombre, c.apellido, p.estado,
                     p.fecha_pedido, p.fecha_entrega, p.metodo_de_pago
            ORDER BY p.id_pedido DESC
        """
        return self._ejecutar_consulta(query, tuple(params) if params else None)

    def obtener_items_pedido(self, id_pedido: int) -> List[Dict]:
        """Trae los productos de un pedido específico."""
        query = """
            SELECT 
                pr.nombre AS producto,
                dp.cantidad,
                dp.precio_unitario,
                dp.subtotal
            FROM detalle_pedido dp
            JOIN producto pr ON dp.id_producto = pr.id_producto
            WHERE dp.id_pedido = %s
        """
        return self._ejecutar_consulta(query, (id_pedido,))

    def cambiar_estado_pedido(self, id_pedido: int, nuevo_estado: str) -> bool:
        """Actualiza el estado de un pedido."""
        connection = self.conexion.conectar()
        if not connection:
            return False
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE pedido SET estado = %s WHERE id_pedido = %s",
                    (nuevo_estado, id_pedido)
                )
                connection.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"❌ Error al cambiar estado: {e}")
            return False
        finally:
            self.conexion.cerrar()


    def cancelar_pedido(self, id_pedido: int, motivo: str) -> bool:
        connection = self.conexion.conectar()
        if not connection:
            return False
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """UPDATE pedido SET estado = 'Cancelado', 
                       observaciones = %s WHERE id_pedido = %s""",
                    (motivo, id_pedido)
                )
                connection.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"❌ Error al cancelar pedido: {e}")
            return False
        finally:
            self.conexion.cerrar()

    def guardar_observacion_pedido(self, id_pedido: int, observacion: str) -> bool:
        connection = self.conexion.conectar()
        if not connection:
            return False
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE pedido SET observaciones = %s WHERE id_pedido = %s",
                    (observacion, id_pedido)
                )
                connection.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"❌ Error al guardar observación: {e}")
            return False
        finally:
            self.conexion.cerrar()

    # --- MÉTODOS PARA EL INVENTARIO ---###---###---###---###---###---###---###---###---###---###---###---################################################################

    def buscar_ingrediente_para_gui(self, nombre: str) -> List[Dict]:
        """Busca ingredientes por nombre para la tabla del menú visual."""
        query = """
            SELECT id_ingredientes, nombre, stock_actual, unidad_medida, costo_unitario 
            FROM ingredientes 
            WHERE nombre LIKE %s
        """
        return self._ejecutar_consulta(query, (f"%{nombre}%",))

    def ingrediente_existe(self, nombre: str) -> bool:
        """Verifica si un ingrediente con ese nombre ya existe."""
        query = "SELECT id_ingredientes FROM ingredientes WHERE nombre = %s"
        resultado = self._ejecutar_consulta(query, (nombre,))
        return len(resultado) > 0

    def obtener_todos_con_nombre(self, nombre: str) -> list:
        """Obtiene todos los ingredientes con un nombre dado (puede haber duplicados)."""
        query = """
            SELECT id_ingredientes, nombre, stock_actual, unidad_medida, costo_unitario, stock_minimo
            FROM ingredientes 
            WHERE nombre = %s
            ORDER BY id_ingredientes
        """
        return self._ejecutar_consulta(query, (nombre,))

    def obtener_todos_los_ingredientes(self) -> List[Dict]:
        """Carga inicial de todo el inventario."""
        query = "SELECT id_ingredientes, nombre, stock_actual, unidad_medida FROM ingredientes"
        return self._ejecutar_consulta(query)

    def listar_tablas(self) -> List[str]:
        """Devuelve la lista de tablas presentes en la base de datos."""
        connection = self.conexion.conectar()
        if connection is None:
            return []

        tablas = []
        try:
            with connection.cursor() as cursor:
                cursor.execute('SHOW TABLES')
                rows = cursor.fetchall() or []
                for row in rows:
                    # row puede ser una tupla como ('tabla',) o un dict dependiendo del cursor
                    if isinstance(row, (list, tuple)):
                        tablas.append(row[0])
                    elif isinstance(row, dict):
                        tablas.append(list(row.values())[0])
                    else:
                        tablas.append(str(row))
        except Exception as e:
            print(f"❌ Error al listar tablas: {e}")
        finally:
            self.conexion.cerrar()

        return tablas
    
    def obtener_ultimas_ventas(self, limite: int = 20) -> List[Dict]:
        """Trae las últimas ventas con cliente, productos, monto y método de pago."""
        query = """
            SELECT 
                p.id_pedido,
                CONCAT(c.nombre, ' ', c.apellido) AS cliente,
                p.metodo_de_pago,
                p.fecha_pedido,
                SUM(dp.subtotal) AS total
            FROM pedido p
            JOIN cliente c ON p.id_cliente = c.id_cliente
            JOIN detalle_pedido dp ON dp.id_pedido = p.id_pedido
            GROUP BY p.id_pedido, c.nombre, c.apellido, p.metodo_de_pago, p.fecha_pedido
            ORDER BY p.id_pedido DESC
            LIMIT %s
        """
        return self._ejecutar_consulta(query, (limite,))
    ##################################################################################################################################################################

    def obtener_receta_producto(self, id_producto: int) -> List[Dict]:
        """Trae los ingredientes y cantidades de la receta de un producto."""
        query = """
            SELECT r.id_receta, i.nombre AS ingrediente, 
                   r.cantidad_requerida, i.unidad_medida
            FROM recetas r
            JOIN ingredientes i ON r.id_ingredientes = i.id_ingredientes
            WHERE r.id_producto = %s
            ORDER BY i.nombre
        """
        return self._ejecutar_consulta(query, (id_producto,))

    # --- MÉTODOS PARA EL DASHBOARD ---#######################################################################################################################################

    def obtener_pedidos_hoy(self) -> List[Dict]:
        """Trae los pedidos que vencen hoy para las alertas del Dashboard."""
        query = """
            SELECT p.id_pedido, c.nombre as cliente, p.estado, p.fecha_entrega 
            FROM pedido p 
            JOIN cliente c ON p.id_cliente = c.id_cliente 
            WHERE DATE(p.fecha_entrega) = CURDATE()
            ORDER BY p.fecha_entrega ASC
        """
        return self._ejecutar_consulta(query)

    def contar_stock_bajo(self) -> int:
        """Cuenta cuántos ingredientes están por debajo del stock mínimo."""
        query = "SELECT COUNT(*) as total FROM ingredientes WHERE stock_actual <= stock_minimo"
        res = self._ejecutar_consulta(query)
        return res[0]['total'] if res else 0
    
    def obtener_ingredientes_stock_bajo(self) -> List[Dict]:
        """Devuelve los ingredientes que están por debajo del stock mínimo."""
        query = """
            SELECT nombre, stock_actual, stock_minimo, unidad_medida
            FROM ingredientes
            WHERE stock_actual <= stock_minimo
            ORDER BY (stock_minimo - stock_actual) DESC
        """
        return self._ejecutar_consulta(query)
    
    def obtener_movimientos_recientes(self, dias: int = 30) -> List[Dict]:
        """
        Obtiene todos los movimientos de insumos y productos en los últimos 'dias' días.
        Retorna una lista de diccionarios con los datos.
        """
        query = f"""
            SELECT 
                'Ingrediente' AS tipo_entidad,
                i.nombre AS nombre,
                mi.tipo,
                mi.cantidad,
                mi.fecha,
                mi.observaciones
            FROM movimientos_ingredientes mi
            JOIN ingredientes i ON mi.id_ingredientes = i.id_ingredientes
            WHERE mi.fecha >= CURDATE() - INTERVAL {dias} DAY

            UNION ALL

            SELECT 
                'Producto' AS tipo_entidad,
                p.nombre AS nombre,
                mp.tipo,
                mp.cantidad,
                mp.fecha,
                NULL AS observaciones
            FROM movimientos_inventario mp
            JOIN producto p ON mp.id_producto = p.id_producto
            WHERE mp.fecha >= CURDATE() - INTERVAL {dias} DAY

            ORDER BY fecha DESC;
        """
        return self._ejecutar_consulta(query)


    # --- MÉTODOS PARA CLIENTES ---########################################################################################################################################

    def obtener_todos_los_clientes(self) -> List[Dict]:
        query = """
            SELECT id_cliente, nombre, apellido, dni, telefono, direccion, 
                   created_at
            FROM cliente
            ORDER BY apellido, nombre
        """
        return self._ejecutar_consulta(query)

    def obtener_detalle_cliente(self, id_cliente: int) -> List[Dict]:
        """Historial de pedidos y monto total de un cliente."""
        query = """
            SELECT 
                p.id_pedido,
                p.fecha_pedido,
                p.fecha_entrega,
                p.metodo_de_pago,
                p.estado,
                SUM(dp.subtotal) AS total
            FROM pedido p
            JOIN detalle_pedido dp ON dp.id_pedido = p.id_pedido
            WHERE p.id_cliente = %s
            GROUP BY p.id_pedido, p.fecha_pedido, p.fecha_entrega, 
                     p.metodo_de_pago, p.estado
            ORDER BY p.id_pedido DESC
        """
        return self._ejecutar_consulta(query, (id_cliente,))

    def buscar_cliente_por_dni(self, dni: str) -> List[Dict]:
        query = "SELECT * FROM cliente WHERE dni = %s"
        return self._ejecutar_consulta(query, (dni,))

    def buscar_cliente(self, termino: str) -> List[Dict]:
        """Busca clientes por DNI exacto, o por nombre/apellido con LIKE."""
        query = """
            SELECT id_cliente, nombre, apellido, dni, telefono, direccion
            FROM cliente
            WHERE dni = %s
               OR nombre LIKE %s
               OR apellido LIKE %s
               OR CONCAT(nombre, ' ', apellido) LIKE %s
            ORDER BY apellido, nombre
            LIMIT 20
        """
        like = f"%{termino}%"
        return self._ejecutar_consulta(query, (termino, like, like, like))

    def reporte_ventas_por_periodo(self, desde: str, hasta: str) -> List[Dict]:
        """Ventas entre dos fechas con total por día."""
        query = """
            SELECT 
                p.fecha_pedido,
                COUNT(DISTINCT p.id_pedido) AS cantidad_pedidos,
                SUM(dp.subtotal) AS total_dia
            FROM pedido p
            JOIN detalle_pedido dp ON dp.id_pedido = p.id_pedido
            WHERE p.fecha_pedido BETWEEN %s AND %s
            GROUP BY p.fecha_pedido
            ORDER BY p.fecha_pedido DESC
        """
        return self._ejecutar_consulta(query, (desde, hasta))

    def reporte_productos_mas_vendidos(self, desde: str, hasta: str) -> List[Dict]:
        """Productos más vendidos en un período."""
        query = """
            SELECT 
                pr.nombre,
                SUM(dp.cantidad) AS unidades_vendidas,
                SUM(dp.subtotal) AS total_recaudado
            FROM detalle_pedido dp
            JOIN producto pr ON dp.id_producto = pr.id_producto
            JOIN pedido p ON dp.id_pedido = p.id_pedido
            WHERE p.fecha_pedido BETWEEN %s AND %s
            GROUP BY pr.id_producto, pr.nombre
            ORDER BY unidades_vendidas DESC
            LIMIT 10
        """
        return self._ejecutar_consulta(query, (desde, hasta))

    def reporte_mejores_clientes(self, desde: str, hasta: str) -> List[Dict]:
        """Clientes con más compras en un período."""
        query = """
            SELECT 
                CONCAT(c.nombre, ' ', c.apellido) AS cliente,
                COUNT(DISTINCT p.id_pedido) AS cantidad_pedidos,
                SUM(dp.subtotal) AS total_gastado
            FROM pedido p
            JOIN cliente c ON p.id_cliente = c.id_cliente
            JOIN detalle_pedido dp ON dp.id_pedido = p.id_pedido
            WHERE p.fecha_pedido BETWEEN %s AND %s
            GROUP BY c.id_cliente, c.nombre, c.apellido
            ORDER BY total_gastado DESC
            LIMIT 10
        """
        return self._ejecutar_consulta(query, (desde, hasta))

    # --- MÉTODOS PARA PRODUCTOS (NUEVA VENTA) ---#########################################################################################################################

    def obtener_catalogo_productos(self) -> List[Dict]:
        """Trae los productos disponibles para el punto de venta."""
        query = "SELECT id_producto, nombre, precio, categoria FROM producto"
        return self._ejecutar_consulta(query)
    
    def obtener_todos_los_productos(self) -> List[Dict]:
        query = """
            SELECT id_producto, nombre, precio, stock, categoria, 
                   tiempo_preparacion, descripcion
            FROM producto
            ORDER BY categoria, nombre
        """
        return self._ejecutar_consulta(query)

    def obtener_detalle_pedido(self, id_pedido: int) -> List[Dict]:
        """Trae los artículos de un pedido específico."""
        query = """
            SELECT dp.id_detallePedido, pr.nombre as producto, dp.cantidad, dp.subtotal
            FROM detalle_pedido dp
            JOIN producto pr ON dp.id_producto = pr.id_producto
            WHERE dp.id_pedido = %s
        """
        return self._ejecutar_consulta(query, (id_pedido,))

    def validar_ingredientes_disponibles(self, carrito: List[Dict]) -> tuple[bool, str]:
        """
        Valida si hay suficientes ingredientes para todos los productos del carrito.
        Retorna (es_válido, mensaje) con TODOS los ingredientes insuficientes
        """
        connection = self.conexion.conectar()
        if connection is None:
            return False, "Error de conexión a la BD"
        
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                insuficiencias = []  # Guardar todos los problemas
                
                # Para cada producto en el carrito
                for idx, producto in enumerate(carrito):
                    id_producto = producto.get('id')
                    cantidad = producto.get('cantidad', 1)

                    # Obtener ingredientes necesarios para este producto
                    cursor.execute(
                        "SELECT id_ingredientes, cantidad_requerida FROM recetas WHERE id_producto = %s",
                        (id_producto,)
                    )
                    ingredientes = cursor.fetchall() or []

                    # Verificar si hay suficiente de cada ingrediente
                    for ing in ingredientes:
                        if not ing:
                            continue

                        # usar .get() por seguridad (Pylance: posible None)
                        id_ing = ing.get('id_ingredientes')
                        cant_req_raw = ing.get('cantidad_requerida')
                        # Evitar pasar None a float() — Pylance reporta posible None
                        if cant_req_raw is None:
                            insuficiencias.append(f"• Receta incompleta para producto {id_producto}: falta cantidad_requerida")
                            continue
                        try:
                            cant_req = float(cant_req_raw)
                        except (ValueError, TypeError):
                            # Si la cantidad en receta no es válida, reportarlo
                            insuficiencias.append(f"• Receta inválida para producto {id_producto}: cantidad_requerida={cant_req_raw}")
                            continue

                        total_necesario = cantidad * cant_req

                        # Obtener stock actual
                        cursor.execute(
                            "SELECT stock_actual, nombre FROM ingredientes WHERE id_ingredientes = %s",
                            (id_ing,)
                        )
                        ing_data = cursor.fetchone()
                        if not ing_data:
                            insuficiencias.append(f"• Ingrediente con id {id_ing} no encontrado en inventario")
                            continue

                        # Seguridad al leer valores
                        stock_actual_raw = ing_data.get('stock_actual') if isinstance(ing_data, dict) else None
                        nombre_ing = ing_data.get('nombre') if isinstance(ing_data, dict) else str(id_ing)
                        # Evitar pasar None a float() — Pylance reporta posible None
                        if stock_actual_raw is None:
                            insuficiencias.append(f"• Stock no disponible para {nombre_ing}")
                            continue
                        try:
                            stock_actual = float(stock_actual_raw)
                        except (TypeError, ValueError):
                            insuficiencias.append(f"• Stock inválido para {nombre_ing}: {stock_actual_raw}")
                            continue

                        # Si no hay suficiente, acumular el mensaje
                        if stock_actual < total_necesario:
                            insuficiencias.append(
                                f"• {nombre_ing}: Necesita {total_necesario}, Disponible {stock_actual}"
                            )
                
                # Si hay insuficiencias, mostrar todas
                if insuficiencias:
                    mensaje_completo = "❌ Ingredientes insuficientes:\n\n" + "\n".join(insuficiencias)
                    return False, mensaje_completo
                
                return True, "✅ Ingredientes suficientes"
        except Exception as e:
            return False, f"Error al validar ingredientes: {e}"
        finally:
            self.conexion.cerrar()