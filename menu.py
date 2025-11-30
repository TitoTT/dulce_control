import pymysql
from conexion import *
from consultor import Consultor
from insertor import *

consultor = Consultor()
ins = Insertor()

print("Menu \n 1 consultar \n 2 cargar")
opc = input(":")

if opc == "1":
    
    select = input("seleccione una opcion: ")
    match select:
        case "1":
            consultor.obtener_tabla("cliente")

        case "2":
            consultor.obtener_tabla("ingredientes")

else:
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

    

