DROP DATABASE IF EXISTS dulce_control;
CREATE DATABASE dulce_control;
USE dulce_control;

-- ############################################
-- 1. TABLAS MAESTRAS
-- ############################################

CREATE TABLE ingredientes(
    id_ingredientes INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    stock_minimo INT NOT NULL,
    stock_actual INT NOT NULL,
    costo_unitario DECIMAL(10,2) DEFAULT 0 NOT NULL,
    unidad_medida VARCHAR(50) NOT NULL
);

CREATE TABLE cliente(
    id_cliente INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    dni INT NOT NULL,
    telefono INT NOT NULL,
    direccion VARCHAR(250) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP 
);

CREATE TABLE decoracion_personalizada(
    id_decoracion INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    costo_extra DECIMAL(10,2) NOT NULL
);

-- ############################################
-- 2. TABLAS RELACIONADAS
-- ############################################

CREATE TABLE producto(
    id_producto INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    stock INT NOT NULL,
    categoria VARCHAR(100) NOT NULL,
    tiempo_preparacion INT,
    precio DECIMAL(10,2) NOT NULL,
    descripcion VARCHAR(100),
    id_ingredientes INT,
    FOREIGN KEY (id_ingredientes) REFERENCES ingredientes(id_ingredientes)
);

CREATE TABLE movimientos_ingredientes (
    id_movimiento INT AUTO_INCREMENT PRIMARY KEY,
    id_ingredientes INT NOT NULL,
    tipo ENUM('entrada','salida') NOT NULL,
    cantidad DECIMAL(10,2) NOT NULL,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    observaciones VARCHAR(255),
    FOREIGN KEY (id_ingredientes) REFERENCES ingredientes(id_ingredientes)
) ENGINE=InnoDB;

CREATE TABLE recetas(
    id_receta INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    id_producto INT NOT NULL,
    id_ingredientes INT NOT NULL,
    cantidad_requerida DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_producto) REFERENCES producto(id_producto),
    FOREIGN KEY (id_ingredientes) REFERENCES ingredientes(id_ingredientes)
);

CREATE TABLE pedido(
    id_pedido INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    metodo_de_pago VARCHAR(50) NOT NULL,
    estado VARCHAR(50) NOT NULL,
    fecha_entrega DATE NOT NULL,
    fecha_pedido DATE NOT NULL,
    total DECIMAL(10,2) NOT NULL DEFAULT 0.00, -- para que funcione el total
    observaciones TEXT,                        -- para corregir el error de la terminal
    id_cliente INT,
    FOREIGN KEY(id_cliente) REFERENCES cliente(id_cliente)
);

CREATE TABLE detalle_pedido(
    id_detallePedido INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    cantidad INT NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL, -- Corregido de INT a DECIMAL
    id_producto INT,
    id_pedido INT,
    id_decoracion INT,
    FOREIGN KEY (id_producto) REFERENCES producto(id_producto),
    FOREIGN KEY (id_pedido) REFERENCES pedido(id_pedido),
    FOREIGN KEY (id_decoracion) REFERENCES decoracion_perzonalizada(id_decoracion)
);

CREATE TABLE movimientos_inventario (
    id_movimiento INT AUTO_INCREMENT PRIMARY KEY,
    id_producto INT NOT NULL,
    tipo ENUM('entrada', 'salida') NOT NULL,
    cantidad INT NOT NULL,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_producto) REFERENCES producto(id_producto)
) ENGINE=InnoDB;

-- ############################################
-- 3. PROCEDIMIENTOS ALMACENADOS
-- ############################################

DELIMITER //

DROP PROCEDURE IF EXISTS registrar_consumo_ingrediente //
CREATE PROCEDURE registrar_consumo_ingrediente(
    IN p_id_ingredientes INT, 
    IN p_cantidad_descontar INT
)
BEGIN
    UPDATE ingredientes 
    SET stock_actual = stock_actual - p_cantidad_descontar
    WHERE id_ingredientes = p_id_ingredientes;
END //

DROP PROCEDURE IF EXISTS registrar_entrada_producto //
CREATE PROCEDURE registrar_entrada_producto(
    IN p_id_producto INT,
    IN p_cantidad INT
)
BEGIN
    UPDATE producto SET stock = stock + p_cantidad WHERE id_producto = p_id_producto;
    INSERT INTO movimientos_inventario (id_producto, tipo, cantidad)
    VALUES (p_id_producto, 'entrada', p_cantidad);
END //

DROP PROCEDURE IF EXISTS registrar_salida_producto //
CREATE PROCEDURE registrar_salida_producto(
    IN p_id_producto INT,
    IN p_cantidad INT
)
BEGIN
    DECLARE v_stock_actual INT;
    SELECT stock INTO v_stock_actual FROM producto WHERE id_producto = p_id_producto;

    IF v_stock_actual >= p_cantidad THEN
        UPDATE producto SET stock = stock - p_cantidad WHERE id_producto = p_id_producto;
        INSERT INTO movimientos_inventario (id_producto, tipo, cantidad)
        VALUES (p_id_producto, 'salida', p_cantidad);
    ELSE
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Stock insuficiente';
    END IF;
END //

DELIMITER ;

-- ############################################
-- 4. INSERT DE DATOS
-- ############################################

INSERT INTO ingredientes (nombre, stock_minimo, stock_actual, costo_unitario, unidad_medida) VALUES
('Harina de Trigo', 5000, 10000, 0.05, 'gramos'),
('Azúcar Blanca', 3000, 8500, 0.03, 'gramos'),
('Mantequilla sin Sal', 2000, 5000, 0.15, 'gramos'),
('Huevos (unidad)', 100, 200, 0.20, 'unidad'),
('Esencia de Vainilla', 500, 1000, 0.08, 'mililitros'),
('Cacao en Polvo', 1000, 2000, 0.10, 'gramos');

INSERT INTO cliente (nombre, apellido, dni, telefono, direccion) VALUES
('Ana', 'Gómez', 12345678, 5551234, 'Av. Siempre Viva 742'),
('Pedro', 'Martínez', 87654321, 5555678, 'Calle Falsa 123');

INSERT INTO decoracion_perzonalizada (tipo, costo_extra) VALUES
('Fondant Temático', 15.00),
('Flores Naturales', 8.50);

INSERT INTO producto (nombre, stock, categoria, tiempo_preparacion, precio, descripcion, id_ingredientes) VALUES
('Tarta de Chocolate Clásica', 15, 'Pastel', 60, 25.00, 'Tarta húmeda con glaseado de cacao', 6);

INSERT INTO pedido (metodo_de_pago, estado, fecha_entrega, fecha_pedido, id_cliente) VALUES
('Efectivo', 'Completado', '2025-12-01', '2025-11-28', 1);

INSERT INTO detalle_pedido (precio_unitario, cantidad, subtotal, id_producto, id_pedido, id_decoracion) VALUES
(25.00, 1, 25.00, 1, 1, 1);

