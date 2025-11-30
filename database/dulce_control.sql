create database dulce_control;
use dulce_control;
#PRODUCTO####################################
create table ingredientes(
	id_ingredientes int primary key not null,
    nombre varchar(150) not null,
    stock_minimo int not null,
    stock_actual int not null,
    costo_unitario decimal(10,2) default 0 not null,
    unidad_medida varchar(50) not null
);

create table producto(
	id_producto int primary key not null,
    nombre varchar(150) not null,
    stock int not null,
    categoria varchar(100) not null,
    tiempo_preparacion int,
    precio decimal(10,2 )not null,
    descripcion varchar(100),
    id_ingredientes int,
    foreign key (id_ingredientes) references ingredientes(id_ingredientes)
);
############################################



#PEDIDO#####################################
create table cliente(
	id_cliente int primary key not null,
    nombre varchar(100) not null,
    apellido varchar(100) not null,
    telefono int not null,
    direccion varchar(250) not null
);

create table pedido(
	id_pedido int primary key not null,
    metodo_de_pago decimal not null,
    estado varchar(50) not null,
    fecha_entrega date not null,
    fecha_pedido date not null,
    id_cliente int,
    foreign key(id_cliente) references cliente(id_cliente)
);
#############################################



#DECORACION##################################
create table decoracion_perzonalizada(
	id_decoracion int primary key not null,
    tipo varchar(50) not null,
    costo_extra decimal(10,2) not null,
    id_detallePedido int
);

create table detalle_pedido(
	id_detallePedido int primary key not null,
    precio_unitario decimal(10,2) not null,
    cantidad int not null,
    subtotal int not null,
    id_producto int,
    id_pedido int,
    id_decoracion int,
    foreign key (id_producto) references producto(id_producto),
    foreign key (id_pedido) references pedido(id_pedido),
    foreign key (id_decoracion) references decoracion_perzonalizada(id_decoracion)
);
###########################################

drop table producto;
drop table pedido;
drop table ingredientes;
drop table cliente;
drop table detalle_pedido;
drop table decoracion_perzonalizada;