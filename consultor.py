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

    # --- MÉTODOS PARA EL INVENTARIO ---

    def buscar_ingrediente_para_gui(self, nombre: str) -> List[Dict]:
        """Busca ingredientes por nombre para la tabla del menú visual."""
        query = """
            SELECT id_ingredientes, nombre, stock_actual, unidad_medida, costo_unitario 
            FROM ingredientes 
            WHERE nombre LIKE %s
        """
        return self._ejecutar_consulta(query, (f"%{nombre}%",))

    def obtener_todos_los_ingredientes(self) -> List[Dict]:
        """Carga inicial de todo el inventario."""
        query = "SELECT id_ingredientes, nombre, stock_actual, unidad_medida FROM ingredientes"
        return self._ejecutar_consulta(query)

    # --- MÉTODOS PARA EL DASHBOARD ---

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

    # --- MÉTODOS PARA CLIENTES ---

    def buscar_cliente_por_dni(self, dni: str) -> List[Dict]:
        query = "SELECT * FROM cliente WHERE dni = %s"
        return self._ejecutar_consulta(query, (dni,))

    # --- MÉTODOS PARA PRODUCTOS (NUEVA VENTA) ---

    def obtener_catalogo_productos(self) -> List[Dict]:
        """Trae los productos disponibles para el punto de venta."""
        query = "SELECT id_producto, nombre, precio, categoria FROM producto"
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