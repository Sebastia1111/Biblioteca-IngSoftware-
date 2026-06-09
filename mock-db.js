// --- BASE DE DATOS SIMULADA (En Memoria) ---

// Tabla: Usuario
const usuarioActual = {
    id: 1,
    rut: "12.345.678-9",
    nombre: "Estudiante Duoc",
    tipo: "Estudiante"
};

// Tabla: TipoMaterial
const tiposMaterial = [
    { id: 1, nombre: "Libro" },
    { id: 2, nombre: "Revista" },
    { id: 3, nombre: "Tesis" }
];

// Tabla: Material + Copia (Simplificado: stock maneja las copias)
let materiales = [
    { 
        id: 101, 
        idtipo: 1, 
        titulo: "Física Universitaria Vol.1", 
        autor: "Serway", 
        stock: 3 
    },
    { 
        id: 102, 
        idtipo: 1, 
        titulo: "Clean Code", 
        autor: "Robert C. Martin", 
        stock: 5 
    },
    { 
        id: 103, 
        idtipo: 2, 
        titulo: "National Geographic", 
        autor: "Varios", 
        stock: 2 
    },
    { 
        id: 104, 
        idtipo: 1, 
        titulo: "Diseño UX/UI", 
        autor: "Norman", 
        stock: 0 // Agotado
    }
];

// Tabla: Reserva (Detallereserva implícito en el objeto)
let reservas = [
    { 
        id: 1, 
        idusuario: 1, 
        idmaterial: 101, 
        fecha_reserva: new Date().toISOString().split('T')[0], // Hoy
        estado: "Activa" 
    }
];

// Tabla: Prestamo (DetallePrestamo implícito)
let prestamos = [
    { 
        id: 1, 
        idusuario: 1, 
        idmaterial: 102, 
        fecha_prestamo: "2023-10-01", 
        fecha_devolucion: "2023-10-15", 
        estado: "Devuelto" 
    },
    { 
        id: 2, 
        idusuario: 1, 
        idmaterial: 103, 
        fecha_prestamo: new Date(Date.now() - 86400000 * 5).toISOString().split('T')[0], // Hace 5 dias
        fecha_devolucion: new Date(Date.now() + 86400000 * 2).toISOString().split('T')[0], // Mañana
        estado: "Pendiente" 
    }
];

// --- LÓGICA DE NEGOCIO ---

// 1. CRUD Materiales
function agregarMaterial(material) {
    material.id = Date.now(); // ID autogenerado
    materiales.push(material);
}

function eliminarMaterial(id) {
    materiales = materiales.filter(m => m.id !== id);
}

function editarMaterial(id, nuevosDatos) {
    const idx = materiales.findIndex(m => m.id === id);
    if(idx !== -1) materiales[idx] = { ...materiales[idx], ...nuevosDatos };
}

// 2. Reservas (Límite 3, 2 días)
function crearReserva(idmaterial) {
    // Validación: Stock > 0
    const material = materiales.find(m => m.id == idmaterial);
    if(material.stock <= 0) return { success: false, msg: "No hay copias disponibles." };

    // Validación: Usuario < 3 reservas activas
    const reservasUsuario = reservas.filter(r => r.idusuario === usuarioActual.id && r.estado === 'Activa');
    if(reservasUsuario.length >= 3) return { success: false, msg: "Alcanzaste el límite de 3 reservas." };

    // Crear reserva
    const hoy = new Date();
    const vencimiento = new Date();
    vencimiento.setDate(hoy.getDate() + 2); // +2 días

    reservas.push({
        id: Date.now(),
        idusuario: usuarioActual.id,
        idmaterial: idmaterial,
        fecha_reserva: hoy.toISOString().split('T')[0],
        fecha_vencimiento: vencimiento.toISOString().split('T')[0],
        estado: 'Activa'
    });

    // Reducir stock (lógica de copia)
    material.stock--;

    return { success: true, msg: "Reserva exitosa. Vence en 2 días." };
}

// 3. Top Materials (Más prestados)
function obtenerTopMateriales() {
    const conteo = {};
    prestamos.forEach(p => {
        conteo[p.idmaterial] = (conteo[p.idmaterial] || 0) + 1;
    });
    
    // Ordenar y mapear
    return materiales
        .map(m => ({ ...m, veces_prestado: conteo[m.id] || 0 }))
        .sort((a, b) => b.veces_prestado - a.veces_prestado)
        .slice(0, 5); // Top 5
}

// 4. Prestamos Pendientes (Distinguir Atrasados)
function obtenerPrestamosUsuario() {
    const misPrestamos = prestamos.filter(p => p.idusuario === usuarioActual.id);
    const hoy = new Date().toISOString().split('T')[0];

    return misPrestamos.map(p => {
        const mat = materiales.find(m => m.id === p.idmaterial);
        const esAtrasado = p.fecha_devolucion < hoy && p.estado === 'Pendiente';
        return { 
            ...p, 
            titulo_material: mat ? mat.titulo : 'Desconocido', 
            atrasado: esAtrasado 
        };
    });
}