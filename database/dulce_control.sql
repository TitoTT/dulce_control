create database dulce_control;
use dulce_control;

#PRODUCTO####################################
create table ingredientes(
	id_ingredientes int primary key auto_increment not null,
    nombre varchar(150) not null,
    stock_minimo int not null,
    stock_actual int not null,
    costo_unitario decimal(10,2) default 0 not null,
    unidad_medida varchar(50) not null
);

create table producto(
	id_producto int primary key auto_increment not null,
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

#RECETAS#####################################
create table recetas(
	id_receta int primary key auto_increment not null,
    id_producto int not null,
    id_ingredientes int not null,
    cantidad_requerida decimal(10,2) not null,
    foreign key (id_producto) references producto(id_producto),
    foreign key (id_ingredientes) references ingredientes(id_ingredientes)
);
############################################



#PEDIDO#####################################
create table cliente(
	id_cliente int primary key auto_increment not null,
    nombre varchar(100) not null,
    apellido varchar(100) not null,
    dni int not null,
    telefono int not null,
    direccion varchar(250) not null
);

create table pedido(
	id_pedido int primary key auto_increment not null,
    metodo_de_pago varchar(50) not null,
    estado varchar(50) not null,
    fecha_entrega date not null,
    fecha_pedido date not null,
    id_cliente int,
    foreign key(id_cliente) references cliente(id_cliente)
);
#############################################



#DECORACION##################################
create table decoracion_perzonalizada(
	id_decoracion int primary key auto_increment not null,
    tipo varchar(50) not null,
    costo_extra decimal(10,2) not null,
    id_detallePedido int
);

create table detalle_pedido(
	id_detallePedido int primary key auto_increment not null,
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

-- PROCEDIMIENTO ALMACENADO PARA REGISTRAR CONSUMO DE INGREDIENTES
CREATE PROCEDURE registrar_consumo_ingrediente(
    IN p_id_ingredientes INT,
    IN p_cantidad_descontar DECIMAL(10,2)
)
BEGIN
    UPDATE ingredientes
    SET stock_actual = stock_actual - p_cantidad_descontar
    WHERE id_ingredientes = p_id_ingredientes;
END;

INSERT INTO ingredientes (nombre, stock_minimo, stock_actual, costo_unitario, unidad_medida) VALUES
('Harina de Trigo', 5000, 100, 0.05, 'gramos'),
('Azúcar Blanca', 3000, 8500, 0.03, 'gramos'),
('Mantequilla sin Sal', 2000, 50, 0.15, 'gramos'),
('Huevos (unidad)', 100, 1, 0.20, 'unidad'),
('Esencia de Vainilla', 500, 5, 0.08, 'mililitros'),
('Cacao en Polvo', 1000, 50, 0.10, 'gramos'),
('Levadura en Polvo', 500, 5, 0.06, 'gramos'),
('Crema de Leche', 1500, 100, 0.12, 'mililitros'),
('Frutillas Frescas', 800, 200, 0.25, 'gramos');

INSERT INTO cliente (nombre, apellido, dni, telefono, direccion) VALUES
('Ana', 'Gómez', 1,5551234, 'Av. Siempre Viva 742, Springfield'),
('Pedro', 'Martínez', 2,5555678, 'Calle Falsa 123, Ciudad A'),
('Laura', 'Rodríguez', 3,5559012, 'Blvd. del Sol 45, Pueblo B'),
('Carlos', 'Sánchez', 4,5553456, 'Carrera 8 #15-30, Urb. C');

INSERT INTO decoracion_perzonalizada (tipo, costo_extra) VALUES
('Fondant Temático', 15.00),
('Flores Naturales', 8.50),
('Letras de Chocolate', 4.00),
('Glaseado Espejo', 6.75);

INSERT INTO producto (nombre, stock, categoria, tiempo_preparacion, precio, descripcion, id_ingredientes) VALUES
('Tarta de Chocolate Clásica', 15, 'Pastel', 60, 25.00, 'Tarta húmeda con glaseado de cacao', 6), -- Cacao en Polvo
('Muffins de Vainilla', 50, 'Cupcake', 25, 3.50, 'Muffin esponjoso con esencia de vainilla', 5), -- Esencia de Vainilla
('Galletas de Mantequilla (docena)', 30, 'Galleta', 40, 12.00, 'Galletas clásicas de mantequilla', 3), -- Mantequilla
('Cheesecake de Frutilla', 10, 'Postre Frío', 180, 30.00, 'Base de galleta con cobertura de frutilla', 9), -- Frutillas Frescas
('Brownies (unidad)', 40, 'Postre', 35, 4.50, 'Brownie denso y chocolatoso', 6); -- Cacao en Polvo

-- Relaciones de recetas: qué ingredientes usa cada producto
INSERT INTO recetas (id_producto, id_ingredientes, cantidad_requerida) VALUES
(1, 6, 200), -- Tarta Chocolate: 200g de Cacao
(1, 1, 300), -- Tarta Chocolate: 300g de Harina
(1, 3, 150), -- Tarta Chocolate: 150g de Mantequilla
(1, 4, 3), -- Tarta Chocolate: 3 huevos
(2, 5, 10), -- Muffins Vainilla: 10ml Esencia Vainilla
(2, 1, 250), -- Muffins Vainilla: 250g Harina
(2, 7, 10), -- Muffins Vainilla: 10g Levadura
(3, 3, 200), -- Galletas: 200g Mantequilla
(3, 1, 400), -- Galletas: 400g Harina
(4, 9, 300), -- Cheesecake: 300g Frutillas
(4, 8, 200), -- Cheesecake: 200ml Crema Leche
(5, 6, 150), -- Brownies: 150g Cacao
(5, 1, 200), -- Brownies: 200g Harina
(5, 3, 100); -- Brownies: 100g Mantequilla

INSERT INTO pedido (metodo_de_pago, estado, fecha_entrega, fecha_pedido, id_cliente) VALUES
('Efectivo', 'Completado', '2025-12-01', '2025-11-28', 1), -- Cliente Ana Gómez
('Tarjeta', 'En Preparación', '2025-12-05', '2025-12-02', 2), -- Cliente Pedro Martínez
('Efectivo', 'Entregado', '2025-12-03', '2025-12-01', 3), -- Cliente Laura Rodríguez
('Transferencia', 'Cancelado', '2025-12-06', '2025-12-02', 4); -- Cliente Carlos Sánchez

INSERT INTO detalle_pedido (precio_unitario, cantidad, subtotal, id_producto, id_pedido, id_decoracion) VALUES
(25.00, 1, 25.00, 1, 1, 1), -- Tarta de Chocolate (Pedido 1) con Decoración 1 (Fondant Temático)
(3.50, 6, 21.00, 2, 1, NULL), -- 6 Muffins de Vainilla (Pedido 1) sin Decoración
(12.00, 2, 24.00, 3, 2, NULL), -- 2 Docenas de Galletas (Pedido 2)
(30.00, 1, 30.00, 4, 3, 2), -- Cheesecake de Frutilla (Pedido 3) con Decoración 2 (Flores Naturales)
(4.50, 10, 45.00, 5, 4, NULL); -- 10 Brownies (Pedido 4)