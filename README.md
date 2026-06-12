<h1 align="center">Biblioteca Académica <br>REQUERIMIENTOS</h1> <br>

# 1. Estructura BD

```sql
-- Base de Datos
CREATE DATABASE IF NOT EXISTS biblioteca_duoc;
USE biblioteca_duoc;

-- Tabla Tipo Usuario
CREATE TABLE IF NOT EXISTS tipo_usuario (
    idtipousuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL
);

-- Tabla Usuario
CREATE TABLE IF NOT EXISTS usuario (
    idusuario INT AUTO_INCREMENT PRIMARY KEY,
    rut VARCHAR(12) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    idtipousuario INT,
    FOREIGN KEY (idtipousuario) REFERENCES tipo_usuario(idtipousuario)
);

-- Tabla Tipo Material (Fijo: Libro, Revista, Tesis)
CREATE TABLE IF NOT EXISTS tipo_material (
    idtipo INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL
);

INSERT INTO tipo_material (nombre) VALUES ('Libro'), ('Revista'), ('Tesis');

-- Tabla Material (Info del libro)
CREATE TABLE IF NOT EXISTS material (
    idmaterial INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    autor VARCHAR(100),
    idtipo INT,
    FOREIGN KEY (idtipo) REFERENCES tipo_material(idtipo)
);

-- Tabla Copia (Ejemplares físicos)
CREATE TABLE IF NOT EXISTS copia (
    idcopia INT AUTO_INCREMENT PRIMARY KEY,
    idmaterial INT,
    estado ENUM('Disponible', 'Prestado', 'Reservada', 'Mantenimiento') DEFAULT 'Disponible',
    FOREIGN KEY (idmaterial) REFERENCES material(idmaterial)
);

-- Tabla Reserva
CREATE TABLE IF NOT EXISTS reserva (
    idreserva INT AUTO_INCREMENT PRIMARY KEY,
    idusuario INT,
    idmaterial INT,
    idcopia INT, -- Opcional: Para saber qué copia específica reservó
    fecha_reserva DATE,
    fecha_vencimiento DATE,
    estado ENUM('Activa', 'Cancelada', 'Completada') DEFAULT 'Activa',
    FOREIGN KEY (idusuario) REFERENCES usuario(idusuario),
    FOREIGN KEY (idmaterial) REFERENCES material(idmaterial)
);

-- Tabla Prestamo
CREATE TABLE IF NOT EXISTS prestamo (
    idprestamo INT AUTO_INCREMENT PRIMARY KEY,
    idusuario INT,
    idcopia INT,
    fecha_prestamo DATE,
    fecha_devolucion DATE,
    fecha_devolucion_real DATE,
    estado ENUM('Pendiente', 'Devuelto', 'Atrasado') DEFAULT 'Pendiente',
    FOREIGN KEY (idusuario) REFERENCES usuario(idusuario),
    FOREIGN KEY (idcopia) REFERENCES copia(idcopia)
);
```

# 2. Conexión con Python

Para conectar HTML con Python y MariaDB:<br>
> Python (Obvio, pero si el entorno es Windows, necesitamos descargarlo por python.org)<br>
> Flask: pip install flask<br>
> Conector MariaDB: pip install mysql-connector-python<br>


# Funcionalidad
## ¿Cómo funcionará el sistema ahora?
> MariaDB: esto guardará los datos reales<br>
> Python: recibe las peticiones del html, consulta a MariaDB y devuelve el resultado en formato JSON <br>
> HTML: obvio la parte visual, esto muestra los datos que le envió python <br>
