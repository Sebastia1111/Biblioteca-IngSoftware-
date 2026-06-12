<h1 align="center">Biblioteca Académica <br>REQUERIMIENTOS</h1> <br>

```mermaid
graph TD
    Repo((Biblioteca Duoc))
    
    %% Archivos Raíz
    Repo --> git[.gitignore]
    Repo --> read[README.md]
    Repo --> req[requirements.txt]
    Repo --> sql[schema.sql]
    Repo --> app[app.py]
    
    %% Carpetas y contenido
    Repo --> sta(static)
    Repo --> tem(templates)

    %% Contenido de static
    sta --> css[style.css]

    %% Contenido de templates
    tem --> ind[index.html]
    tem --> mob[mobile.html]
    tem --> cat[catalogo.html]
    tem --> mis[mis_prestamos.html]
```

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
---
# 2. Conexión con Python

Para conectar HTML con Python y MariaDB:<br>
> # Python:
(Obvio, pero si el entorno es Windows, necesitamos descargarlo por python.org)<br>
> # Flask:
```console
pip install flask
```

> # Conector MariaDB:
```console
pip install mysql-connector-python
```
<br>

---
# Funcionalidad
## ¿Cómo funcionará el sistema ahora?
> MariaDB: esto guardará los datos reales<br>
> Python: recibe las peticiones del html, consulta a MariaDB y devuelve el resultado en formato JSON <br>
> HTML: obvio la parte visual, esto muestra los datos que le envió python <br>
---

# Aplicación/Despliegue
## Es necesario activar el entorno antes de usar activar el app.py:
```console
source venv/bin/activate
```

### y luego ya se puede usar la app:
```console
python app.py
```
---
<br>

# SOLUCIONES
## 1. Errores con venv
Es común al parecer que hayan errores con esto ya que un archivo tan pesado como la carpeta _venv_ no se puede subir al repositorio<br>
la visión que tengo de la carpeta creada en mi entorno se ve de la siguiente forma:
```text
BIBLIOTECA/
  ├── app.py
  ├── venv/ (se queda, pero no se sube a github)
  ├── templates/
  │    ├── index.html
  │    ├── mobile.html
  │    ├── catalogo.html
  │    └── mis_prestamos.html
  └── static/
       └── style.css
```
Al no ser posible Uplodear los archivos en github de esta forma, lo que hice fue lo siguiente (MUY IMPORTANTE)<br>
#### Creé un archivo llamado .gitinore, el cual posee lo siguiente adentro:
```text
venv/
__pycache__/
*.pyc
.DS_Store
```
Esto evita que tenga que subir la carpeta venv (que ocupa mucho espacio) o archivos temporales de Python







---

# Instalación
(para facilitarle la vida otras personas)
### 1. Crear entorno virtual:
   `python -m venv venv` <br>
   `source venv/bin/activate` (Linux) o `venv\Scripts\activate` (Windows)

### 2. Instalar dependencias:
   `pip install -r requirements.txt`

### 3. Configurar Base de Datos:
Ejecuta el script SQL en MariaDB para crear la tabla `biblioteca_duoc`.

### 4. Ejecutar aplicación:
   `python app.py`
   Ir a http://localhost:5000/m

---
