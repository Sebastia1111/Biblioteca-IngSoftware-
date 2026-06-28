<div align="center">

# 📚 Biblioteca DuocUC

**Sistema de Gestión Bibliotecaria Integral**

[![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![MariaDB](https://img.shields.io/badge/MariaDB-11.x-003545?style=for-the-badge&logo=mariadb&logoColor=white)](https://mariadb.org) <br>

*[Ingeniería de Software — DuocUC]*

---

<p align="center">
  <img src="https://media.giphy.com/media/qgQUggAC3Pfv687qPC/giphy.gif" width="400" alt="Biblioteca Animation">
</p>

</div>

## Descripción

Sistema completo de gestión bibliotecaria desarrollado para la asignatura de Ingeniería de Software en DuocUC. Permite administrar el inventario de materiales, gestionar préstamos y devoluciones, y mantener un seguimiento detallado de las operaciones del mesón bibliográfico.

### Características Principales

| Módulo | Funcionalidades |
|--------|-----------------|
| 🔐 **Autenticación** | Login por RUT, sesiones seguras, roles diferenciados |
| 📱 **Vista Estudiante** | Reservar libros, ver historial, buscar en catálogo |
| 💻 **Vista Administrador** | Dashboard, CRUD materiales, gestión de préstamos |
| 📊 **Estadísticas** | Materiales populares, contadores en tiempo real |
| 🔔 **Alertas** | Sistema de notificaciones por vencimiento |
| 📦 **Inventario** | Control de copias, estados, bajas y daños |

---

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                    Arquitectura Cliente-Servidor                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │                   Flask Backend (app.py)                 │  │
│   │              mysql-connector-python + Sessions           │  │
│   └──────────────────────────────┬───────────────────────────┘  │
│                                  │                              │
│                      ┌───────────┴───────────┐                  │
│                      ▼                       ▼                  │
│             ┌──────────────────┐    ┌──────────────────┐        │
│             │   Vista Mobile   │    │   Vista Desktop  │        │
│             │   (Estudiantes)  │    │   (Admin/Mesón)  │        │
│             └──────────────────┘    └──────────────────┘        │
│                                  │                              │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │                   MariaDB / MySQL                        │  │
│   │           6 tablas • Relaciones completas                │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Stack Tecnológico

| Componente | Tecnología | Versión |
|------------|------------|---------|
| **Backend** | Python + Flask | 3.x / 3.x |
| **Base de Datos** | MariaDB | 11.x |
| **Conector BD** | mysql-connector-python | 8.x |
| **Frontend** | HTML5 + CSS3 + JavaScript | ES6+ |
| **Estilos** | CSS Custom Properties | - |
| **Servidor** | Flask Development Server | - |

---

## Estructura del Proyecto

```
biblioteca-duocuc/
│
├── 📄 app.py                    # Backend principal (Flask)
├── 📄 requirements.txt          # Dependencias Python
├── 📄 README.md                 # Este archivo
├── 📄 .gitignore                # Archivos ignorados por Git
│
├── 📁 database/                 # Scripts de base de datos
│   ├── 📄 schema.sql            # Estructura de tablas
│   └── 📄 inserts.sql           # Datos de prueba
│
├── 📁 static/                   # Archivos estáticos
│   └── 📁 css/
│       └── 📄 style.css         # Estilos globales
│
└── 📁 templates/                # Vistas HTML
    ├── 📁 desktop/              # Interfaz de escritorio
    │   ├── 📄 index.html        # Dashboard administrativo
    │   ├── 📄 catalogo.html     # CRUD de materiales
    │   └── 📄 prestamos.html    # Historial global de préstamos
    │
    └── 📁 mobile/               # Interfaz móvil
        └── 📄 mobile.html       # App completa para estudiantes
```

---

## Modelo de Datos

```mermaid
erDiagram
    tipo_usuario ||--o{ usuario : "tiene"
    tipo_material ||--o{ material : "clasifica"
    material ||--|{ copia : "tiene"
    usuario ||--o{ prestamo : "realiza"
    copia ||--o{ prestamo : "se usa en"

    tipo_usuario {
        int idtipousuario PK
        string nombre
    }

    usuario {
        string rut PK
        string nombre
        string correo
        string password
        int idtipousuario FK
    }

    tipo_material {
        int idtipo PK
        string nombre
        boolean activo
    }

    material {
        int idmaterial PK
        string titulo
        string autor
        int idtipo FK
    }

    copia {
        int idcopia PK
        int idmaterial FK
        string estado
    }

    prestamo {
        int idprestamo PK
        string rut_usuario FK
        int idcopia FK
        date fecha_prestamo
        date fecha_devolucion
        string estado
    }
```

### Estados del Sistema

| Entidad | Estados | Descripción |
|---------|---------|-------------|
| **Copia** | `Disponible` | Lista para ser reservada |
| | `Reservado` | Un alumno la reservó |
| | `Prestado` | Entregada físicamente |
| | `Dañado` | Fuera de circulación por daño |
| | `Baja` | Dada de baja definitivamente |
| **Préstamo** | `Reservado` | Esperando retiro en mesón |
| | `Vigente` | En posesión del alumno (7 días) |
| | `Atrasado` | Pasó la fecha de devolución |
| | `Devuelto` | Devuelta correctamente |

---

## Instalación y Configuración

### Prerrequisitos

- [Python 3.8+](https://python.org/downloads/)
- [MariaDB 10.6+](https://mariadb.org/download/)
- [Git](https://git-scm.com/downloads)

### Pasos de Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/biblioteca-duocuc.git
cd biblioteca-duocuc

# 2. Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar base de datos
# Iniciar sesión en MariaDB
mysql -u root -p

# Ejecutar scripts
source database/schema.sql
source database/inserts.sql
exit

# 5. Verificar conexión en app.py
# Ajustar credenciales si es necesario:
# host='127.0.0.1'
# user='root'
# password='tu_password'

# 6. Ejecutar la aplicación
python app.py
```

### Acceder al Sistema

| Vista | URL | Descripción |
|-------|-----|-------------|
| 🖥️ Desktop | `http://localhost:5000/` | Panel de administración |
| 📱 Mobile | `http://localhost:5000/m` | App para estudiantes |

---

## 👤 Credenciales de Prueba

| Rol | RUT | Contraseña | Nombre |
|-----|-----|------------|--------|
| 🔴 Administrador | `22130895-6` | `ad####23` | Sebastian Orellana |
| 🟢 Estudiante | `22163627-9` | `m###a` | Magdalena Zuñiga |
| 🟢 Estudiante | `22182484-9` | `fe######as` | Felipe Cea |

---

## 🔌 API Endpoints

### Autenticación
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/login` | Iniciar sesión |
| `POST` | `/api/logout` | Cerrar sesión |

### Estudiante (Mobile)
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/resumen_usuario` | Obtener catálogo y contadores |
| `POST` | `/api/resumen_usuario` | Reservar un libro |
| `GET` | `/api/mis_prestamos` | Historial personal |
| `POST` | `/api/devolver` | Devolver libro |

### Administrador (Desktop)
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/stats` | Estadísticas generales |
| `GET` | `/api/admin/top_materiales` | Materiales más solicitados |
| `GET` | `/api/admin/ver_reservas` | Reservas pendientes |
| `POST` | `/api/admin/entregar_libro` | Entregar libro reservado |
| `POST` | `/api/admin/todos_prestamos` | Historial completo |
| `POST` | `/api/admin/inventario` | Cambiar estado de copia |
| `POST` | `/api/admin/transaccion/prestamo` | Préstamo manual |
| `POST` | `/api/admin/transaccion/devolucion` | Devolución manual |
| `POST` | `/api/simular_alerta_vencimiento` | Enviar alerta |

### CRUD Categorías
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/categorias` | Listar categorías |
| `POST` | `/api/categorias` | Crear categoría |
| `PUT` | `/api/categorias/<id>` | Editar categoría |
| `POST` | `/api/categorias/<id>/toggle` | Activar/Desactivar |

### CRUD Materiales
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/material` | Listar con stock |
| `POST` | `/api/material` | Crear material + copias |
| `PUT` | `/api/material/<id>` | Editar material |
| `DELETE` | `/api/material/<id>` | Eliminar material |

---

## Capturas del Sistema

### Vista Móvil - Estudiante
<table>
<tr>
<td align="center">
<strong>Login</strong><br>
<img src="https://github.com/user-attachments/assets/08a86fa9-0756-470b-a481-10366f0f48c7"?text=Login" alt="Login" width="200">
</td>
<td align="center">
<strong>Dashboard</strong><br>
<img src="https://github.com/user-attachments/assets/634bdd30-578f-4ea8-b520-d68dcd80b8f6"?text=Dashboard" alt="Dashboard" width="200">
</td>
<td align="center">
<strong>Búsqueda</strong><br>
<img src="https://github.com/user-attachments/assets/d82145e9-f251-415d-964f-9e4d46502e61"?text=Busqueda" alt="Búsqueda" width="200">
</td>
</tr>
<tr>
<td align="center">
<strong>Detalle</strong><br>
<img src="https://github.com/user-attachments/assets/5dd2eacc-3b36-4564-a6ea-7f0f4c349d47"?text=Detalle" alt="Detalle" width="200">
</td>
<td align="center">
<strong>Mi Ficha</strong><br>
<img src="https://github.com/user-attachments/assets/d992e0b8-7273-473f-96c9-695b0ede58f8"?text=Mi+Ficha" alt="Mi Ficha" width="200">
</td>
<td align="center">
<strong>Admin</strong><br>
<img src="https://github.com/user-attachments/assets/c907b512-01fd-4740-80c2-2a6e8166d9ab"?text=Admin" alt="Admin" width="200">
</td>
</tr>
</table>

### Vista Desktop - Administrador
<table>
<tr>
<td align="center">
<strong>Dashboard</strong><br>
<img src="https://github.com/user-attachments/assets/98ebb8f3-e33d-4c0d-b518-bbf398ed0b21"?text=Dashboard+Admin" alt="Dashboard Admin" width="400">
</td>
</tr>
<tr>
<td align="center">
<strong>Inventario</strong><br>
<img src="https://github.com/user-attachments/assets/a377df57-b2b6-4dd6-90aa-ecfd9624c6f0"?text=CRUD+Materiales" alt="CRUD Materiales" width="400">
</td>
</tr>
<tr>
<td align="center">
<strong>Préstamos</strong><br>
<img src="https://github.com/user-attachments/assets/8df5a33c-0d75-40fa-9aff-42d5f1a06af2"?text=Historial+Prestamos" alt="Historial Préstamos" width="400">
</td>
</tr>
</table>

---

## 🔄 Flujo de Operaciones

```mermaid
flowchart TD
    A[🟢 Estudiante] --> B[Reserva libro en Mobile]
    B --> C[Estado: Reservado]
    C --> D[🔴 Admin ve reserva pendiente]
    D --> E[Admin entrega libro]
    E --> F[Estado: Vigente + 7 días plazo]
    F --> G{¿Devuelve a tiempo?}
    G -- Sí --> H[Estado: Devuelto ✅]
    G -- No --> I[Estado: Atrasado ❌]
    I --> J[Admin envía alerta]
    J --> H
```

---

## Requerimientos Cubiertos

| # | Requerimiento | Estado |
|---|---------------|--------|
| 1 | CRUD Tipos de Libro | ✅ Completo |
| 2 | Actualización de Inventario | ✅ Completo |
| 3 | Reserva de Materiales (máx. 3, válida 2 días)* | ✅ Parcial |
| 4 | Préstamo y Devolución de Libros | ✅ Completo |
| 5 | Consulta Materiales Populares | ✅ Completo |
| 6 | Ficha de Usuario (prestados/no devueltos/devueltos) | ✅ Completo |
| 7 | Consulta Materiales Atrasados y No Atrasados | ✅ Completo |

*La expiración automática a los 2 días es una mejora futura opcional.

---

## 👥 Desarrolladores

<div align="center">
<table>
<tr>
<td align="center">
<a href="https://github.com/Sebastia1111">
<img src="https://github.com/Sebastia1111.png" width="100" style="border-radius:50%"><br>
<strong>Sebastian Orellana</strong><br>
<sub>Desarrollo Full Stack</sub>
</a>
</td>
<td align="center">
<a href="https://github.com/magdzuniga">
<img src="https://github.com/magdzuniga.png" width="100" style="border-radius:50%"><br>
<strong>Magdalena Zuñiga</strong><br>
<sub>Documentación y CRUD</sub>
</a>
</td>
<td align="center">
<a href="https://github.com/feliduoc">
<img src="https://github.com/feliduoc.png" width="100" style="border-radius:50%"><br>
<strong>Felipe Cea</strong><br>
<sub>Diseño y Documentación</sub>
</a>
</td>
</tr>
</table>
</div>

---

## 📄 Licencia

Este proyecto fue desarrollado con fines **educativos** como parte de la asignatura de Ingeniería de Software en DuocUC.

<div align="center">

**Hecho con ❤️ para DuocUC**

<p>
<img src="https://img.shields.io/badge/Ingeniería_de_Software-2026-FFC20E?style=for-the-badge">
</p>

</div>

---
