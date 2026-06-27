CREATE DATABASE IF NOT EXISTS biblioteca_duoc;
USE biblioteca_duoc;

-- 1. Tipos de Usuario (Admin, Estudiante)
CREATE TABLE IF NOT EXISTS tipo_usuario (
    idtipousuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL
);

-- 2. Usuarios
CREATE TABLE IF NOT EXISTS usuario (
    rut VARCHAR(12) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(150) NOT NULL, 
    password VARCHAR(255) NOT NULL,
    idtipousuario INT,
    FOREIGN KEY (idtipousuario) REFERENCES tipo_usuario(idtipousuario)
);

-- 3. Categorías / Tipos de Material
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

-- 5. Copias o Ejemplares Físicos
-- Estados usados por el sistema: 'Disponible', 'Reservado', 'Prestado', 'Dañado', 'Baja'
CREATE TABLE IF NOT EXISTS copia (
    idcopia INT AUTO_INCREMENT PRIMARY KEY,
    idmaterial INT,
    estado VARCHAR(50) DEFAULT 'Disponible',
    FOREIGN KEY (idmaterial) REFERENCES material(idmaterial)
);

-- 6. Préstamos y Reservas (tabla unificada)
-- Estados usados por el sistema: 'Reservado', 'Vigente', 'Atrasado', 'Devuelto'
CREATE TABLE IF NOT EXISTS prestamo (
    idprestamo INT AUTO_INCREMENT PRIMARY KEY,
    rut_usuario VARCHAR(12),
    idcopia INT,
    fecha_prestamo DATE,
    fecha_devolucion DATE,
    estado VARCHAR(50) DEFAULT 'Reservado',
    FOREIGN KEY (rut_usuario) REFERENCES usuario(rut),
    FOREIGN KEY (idcopia) REFERENCES copia(idcopia)
);
