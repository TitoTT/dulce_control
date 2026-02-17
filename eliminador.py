import pymysql
from conexion import Conexion
from typing import Union, Any, Optional, cast

class Eliminador:
    def __init__(self):
        self.conexion = Conexion()

    def _ejecutar_dml(self, query: str, params: Optional[tuple[Any, ...]] = None) -> int:
        """
        Método privado para ejecutar sentencias DML (DELETE, INSERT, UPDATE).
        Retorna el número de filas afectadas o -1 si falla.
        """
        connection = self.conexion.conectar()
        if connection is None:
            return -1

        try:
            cursor = connection.cursor()
            cursor.execute(query, params)
            connection.commit()
            return cursor.rowcount
            
        except Exception as e:
            # Captura cualquier error, incluyendo IntegrityError si ocurre
            print(f"❌ Error al ejecutar DML: {e}")
            return -1

        finally:
            self.conexion.cerrar()

    def _ejecutar_select(self, query: str, params: Optional[tuple[Any, ...]] = None) -> Optional[list[tuple[Any, ...]]]:
        """
        Método privado para ejecutar sentencias SELECT.
        Retorna una lista de tuplas con los resultados o None.
        """
        connection = self.conexion.conectar()
        if connection is None:
            return None

        resultados: Optional[list[tuple[Any, ...]]] = None
        try:
            cursor = connection.cursor()
            cursor.execute(query, params)
            resultados = cast(list[tuple[Any, ...]], cursor.fetchall())
            
        except Exception as e:
            print(f"❌ Error al ejecutar SELECT: {e}")
            
        finally:
            self.conexion.cerrar()
            
        return resultados

    def _ejecutar_eliminacion_simple(self, tabla: str, columna_pk: str, pk_valor: Union[int, str]) -> bool:
        """
        Eliminación simple que intenta borrar directamente (usado para registros sin hijos o después de borrar hijos).
        """
        query = f"DELETE FROM {tabla} WHERE {columna_pk} = %s"
        row_count = self._ejecutar_dml(query, (pk_valor,))
        
        if row_count > 0:
            print(f"✅ Registro con {columna_pk} = {pk_valor} eliminado correctamente de '{tabla}'.")
            return True
        elif row_count == 0:
            print(f"🔍 No se encontró un registro en '{tabla}' con {columna_pk} = {pk_valor}.")
            return False
        else:
            return False # Fallo en la ejecución DML

    # --- MÉTODOS DE ELIMINACIÓN CON CASCADA ---

    def eliminar_cliente(self, id_cliente: int):
        """
        Elimina un cliente y todos sus pedidos asociados, y los detalles de esos pedidos (Cascada: Cliente -> Pedido -> Detalle_Pedido).
        """
        print(f"\n⏳ Iniciando eliminación en cascada para Cliente ID: {id_cliente}...")
        
        # 1. Buscar todos los IDs de pedido del cliente
        pedidos_query = "SELECT id_pedido FROM pedido WHERE id_cliente = %s;"
        pedidos_data = self._ejecutar_select(pedidos_query, (id_cliente,))
        
        if pedidos_data:
            id_pedidos = [p[0] for p in pedidos_data]
            print(f"   - Se encontraron {len(id_pedidos)} pedidos a eliminar.")
            
            # 2. Eliminar Detalle_Pedido de cada pedido encontrado (Nivel 2 de cascada)
            for id_p in id_pedidos:
                self._ejecutar_eliminacion_simple("detalle_pedido", "id_pedido", id_p)
                
            # 3. Eliminar los Pedidos (Nivel 1 de cascada)
            pedidos_eliminados = self._ejecutar_eliminacion_simple("pedido", "id_cliente", id_cliente)
            if not pedidos_eliminados:
                print("⚠️ No se pudo completar la eliminación de pedidos. Cancelando.")
                return

        # 4. Eliminar el Cliente (El Padre)
        self._ejecutar_eliminacion_simple("cliente", "id_cliente", id_cliente)

    def eliminar_pedido(self, id_pedido: int):
        """
        Elimina un pedido y todos los detalles de ese pedido (Cascada: Pedido -> Detalle_Pedido).
        """
        print(f"\n⏳ Iniciando eliminación en cascada para Pedido ID: {id_pedido}...")
        
        # 1. Eliminar Detalle_Pedido asociados
        self._ejecutar_eliminacion_simple("detalle_pedido", "id_pedido", id_pedido)

        # 2. Eliminar el Pedido (El Padre)
        self._ejecutar_eliminacion_simple("pedido", "id_pedido", id_pedido)


    def eliminar_producto(self, id_producto: int):
        """
        Elimina un producto y sus registros en detalle_pedido (Cascada: Producto -> Detalle_Pedido).
        """
        print(f"\n⏳ Iniciando eliminación en cascada para Producto ID: {id_producto}...")

        # 1. Eliminar Detalle_Pedido asociados
        self._ejecutar_eliminacion_simple("detalle_pedido", "id_producto", id_producto)

        # 2. Eliminar el Producto (El Padre)
        self._ejecutar_eliminacion_simple("producto", "id_producto", id_producto)

    def eliminar_decoracion_perzonalizada(self, id_decoracion: int):
        """
        Elimina una decoración y sus registros en detalle_pedido (Cascada: Decoracion -> Detalle_Pedido).
        """
        print(f"\n⏳ Iniciando eliminación en cascada para Decoración ID: {id_decoracion}...")

        # 1. Eliminar Detalle_Pedido asociados
        self._ejecutar_eliminacion_simple("detalle_pedido", "id_decoracion", id_decoracion)

        # 2. Eliminar la Decoración (El Padre)
        self._ejecutar_eliminacion_simple("decoracion_perzonalizada", "id_decoracion", id_decoracion)

    def eliminar_ingrediente(self, id_ingrediente: int):
        """
        Elimina un ingrediente y los productos asociados, y los detalles de pedido de esos productos (Cascada: Ingrediente -> Producto -> Detalle_Pedido).
        """
        print(f"\n⏳ Iniciando eliminación en cascada para Ingrediente ID: {id_ingrediente}...")

        # 1. Buscar IDs de productos dependientes
        productos_query = "SELECT id_producto FROM producto WHERE id_ingredientes = %s;"
        productos_data = self._ejecutar_select(productos_query, (id_ingrediente,))
        
        if productos_data:
            id_productos = [p[0] for p in productos_data]
            print(f"   - Se encontraron {len(id_productos)} productos a eliminar.")

            # 2. Eliminar Detalle_Pedido de cada producto (Nivel 2 de cascada)
            for id_p in id_productos:
                self._ejecutar_eliminacion_simple("detalle_pedido", "id_producto", id_p)

            # 3. Eliminar los Productos (Nivel 1 de cascada)
            productos_eliminados = self._ejecutar_eliminacion_simple("producto", "id_ingredientes", id_ingrediente)
            if not productos_eliminados:
                print("⚠️ No se pudo completar la eliminación de productos. Cancelando.")
                return

        # 4. Eliminar el Ingrediente (El Padre)
        self._ejecutar_eliminacion_simple("ingredientes", "id_ingredientes", id_ingrediente)


    # --- MÉTODOS DE ELIMINACIÓN SIN CASCADA (DETALLE ES EL ÚLTIMO NIVEL) ---
        
    def eliminar_detalle_pedido(self, id_detalle_pedido: int):
        """
        Elimina un registro de detalle_pedido por su ID. (No tiene hijos).
        """
        self._ejecutar_eliminacion_simple("detalle_pedido", "id_detallePedido", id_detalle_pedido)

# Suponiendo que la clase Eliminador ya está instanciada
if __name__ == '__main__':
    eliminador = Eliminador() 

    # 1. Eliminar el Ingrediente con ID 5
    eliminador.eliminar_cliente(1)