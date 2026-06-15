CREATE DATABASE IF NOT EXISTS biblioteca_duoc;
USE biblioteca_duoc;

-- 1. Tipos de Usuario (Admin, Estudiante, etc.)
CREATE TABLE IF NOT EXISTS tipo_usuario (
    idtipousuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL
);

-- 2. Usuarios / Alumnos
CREATE TABLE IF NOT EXISTS usuario (
    rut VARCHAR(12) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL,
    idtipousuario INT,
    FOREIGN KEY (idtipousuario) REFERENCES tipo_usuario(idtipousuario)
);

-- 3. Categorías / Tipos de Material (Exigido por el Scrum)
CREATE TABLE IF NOT EXISTS tipo_material (
    idtipo INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    activo TINYINT DEFAULT 1
);

-- 4. Material Bibliográfico General
CREATE TABLE IF NOT EXISTS material (
    idmaterial INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    autor VARCHAR(150) NOT NULL,
    idtipo INT,
    FOREIGN KEY (idtipo) REFERENCES tipo_material(idtipo)
);

-- 5. Copias o Ejemplares Físicos/Digitales (Para el control de Inventario)
CREATE TABLE IF NOT EXISTS copia (
    idcopia INT AUTO_INCREMENT PRIMARY KEY,
    idmaterial INT,
    estado VARCHAR(50) DEFAULT 'Disponible', -- 'Disponible', 'Dañado', 'Baja'
    FOREIGN KEY (idmaterial) REFERENCES material(idmaterial)
);

-- 6. Historial de Préstamos
CREATE TABLE IF NOT EXISTS prestamo (
    idprestamo INT AUTO_INCREMENT PRIMARY KEY,
    rut_usuario VARCHAR(12),
    idcopia INT,
    fecha_prestamo DATE,
    fecha_devolucion DATE,
    estado VARCHAR(50) DEFAULT 'Vigente', -- 'Vigente', 'Devuelto', 'Atrasado'
    FOREIGN KEY (rut_usuario) REFERENCES usuario(rut),
    FOREIGN KEY (idcopia) REFERENCES copia(idcopia)
);

-- INSERTS BASE PARA PRUEBAS (Pasa el login de inmediato)
INSERT INTO tipo_usuario (nombre) VALUES ('Administrador'), ('Estudiante') ON DUPLICATE KEY UPDATE nombre=nombre;

-- Cuentas de prueba (Contraseñas planas para facilitar el desarrollo en el entorno local)
INSERT INTO usuario (rut, nombre, password, idtipousuario) VALUES 
('11111111-1', 'Pedro Estudiante', 'duoc123', 2),
('22222222-2', 'Ana Administradora', 'admin123', 1)
ON DUPLICATE KEY UPDATE nombre=nombre;

-- Tipos de material iniciales
INSERT INTO tipo_material (nombre, activo) VALUES 
('Libro', 1), ('Revista', 1), ('Tesis', 1), ('Material Digital', 0);
