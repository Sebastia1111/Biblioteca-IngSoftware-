from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import mysql.connector
import os
from mysql.connector import Error
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'clave_secreta_desarrollo_duocuc'


# BASE DE DATOS

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.environ.get('DB_HOST', '127.0.0.1'),
            user='root',
            password='', 
            database='biblioteca_duoc'
        )
        return connection
    except Error as e:
        print(f"Error conectando a MariaDB: {e}")
        return None


# MOTOR DE EXPIRACIÓN DE RESERVAS (2 DÍAS)

def expirar_reservas_vencidas():
    """
    Busca reservas con más de 2 días de antigüedad que no fueron retiradas.
    Las elimina y devuelve las copias al estado 'Disponible'.
    Se ejecuta automáticamente al cargar datos del sistema.
    """
    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    try:
        # 1. Obtener IDs de copias que están en reservas vencidas
        cursor.execute("""
            SELECT p.idcopia 
            FROM prestamo p 
            WHERE p.estado = 'Reservado' 
            AND p.fecha_prestamo < DATE_SUB(NOW(), INTERVAL 2 DAY)
        """)
        copias_a_liberar = [row[0] for row in cursor.fetchall()]
        
        if not copias_a_liberar:
            cursor.close()
            conn.close()
            return  # No hay nada que expirar
        
        # 2. Eliminar los préstamos/reservas vencidas
        cursor.execute("""
            DELETE FROM prestamo 
            WHERE estado = 'Reservado' 
            AND fecha_prestamo < DATE_SUB(NOW(), INTERVAL 2 DAY)
        """)
        
        # 3. Devolver las copias a 'Disponible'
        for idcopia in copias_a_liberar:
            cursor.execute(
                "UPDATE copia SET estado = 'Disponible' WHERE idcopia = %s", 
                (idcopia,)
            )
        
        conn.commit()
        print(f"🔄 [EXPIRACIÓN] Se liberaron {len(copias_a_liberar)} reserva(s) vencida(s)")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ [EXPIRACIÓN] Error: {e}")
    finally:
        cursor.close()
        conn.close()


# MOTOR DE NOTIFICACIONES (MODO REALISTA / DEMO)

def enviar_correo_alerta(destinatario, asunto, mensaje_texto):
    print("\n--- [SISTEMA DE NOTIFICACIONES DUOCUC] ---")
    print(f"📡 Conectando con servidor de retransmisión... OK")
    print(f"📧 Remitente: biblioteca@duocuc.cl")
    print(f"📩 Destinatario: {destinatario}")
    print(f"📝 Asunto: {asunto}")
    print(f"💬 Mensaje: {mensaje_texto}")
    print(f"✅ ¡Correo procesado y enviado exitosamente!")
    print("------------------------------------------------\n")
    return True


# RUTAS DE NAVEGACIÓN Y RENDERIZADO (FRONTEND)

@app.route('/')
def index():
    return render_template('desktop/index.html')

@app.route('/m')
def mobile_app():
    return render_template('mobile/mobile.html')

@app.route('/catalogo')
def catalogo():
    return render_template('desktop/catalogo.html')

@app.route('/prestamos')
def prestamos():
    return render_template('desktop/prestamos.html')


# API ENDPOINTS DE AUTENTICACIÓN Y CONTROL (COMÚN)

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    rut_recibido = data.get('rut')
    password_recibido = data.get('password')
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Error de conexión a la BD"}), 500
        
    cursor = conn.cursor(dictionary=True)
    
    try:
        query = "SELECT rut, nombre, password, idtipousuario FROM usuario WHERE rut = %s"
        cursor.execute(query, (rut_recibido,)) 
        usuario = cursor.fetchone()
    except Exception as e:
        return jsonify({"success": False, "message": f"Error en BD: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()
    
    if usuario and usuario['password'] == password_recibido:
        session['rut_usuario'] = usuario['rut'] 
        session['idtipousuario'] = usuario['idtipousuario']
        
        return jsonify({
            "success": True, 
            "nombre": usuario['nombre'],
            "idtipousuario": usuario['idtipousuario']
        })
    else:
        return jsonify({"success": False, "message": "RUT o contraseña incorrectos"})

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({"success": True})


# API ENDPOINTS PARA MOBILE (ESTUDIANTES)

@app.route('/api/resumen_usuario', methods=['GET', 'POST'])
def api_resumen_usuario():
    # Ejecutar expiración antes de mostrar datos
    expirar_reservas_vencidas()
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "error": "No hay conexión a la base de datos"}), 500
        
    cursor = conn.cursor(dictionary=True)
    usuario_id = session.get('rut_usuario')  

    # --- ACCION: PROCESAR RESERVA (POST) ---
    if request.method == 'POST':
        if not usuario_id:
            cursor.close()
            conn.close()
            return jsonify({"success": False, "error": "No hay una sesión activa."}), 401
            
        data = request.get_json()
        idcopia = data.get('idcopia')
        
        try:
            # Verificar que la copia esté disponible
            cursor.execute("SELECT estado FROM copia WHERE idcopia = %s", (idcopia,))
            copia = cursor.fetchone()
            
            if not copia:
                return jsonify({"success": False, "error": "Copia no encontrada."})
            
            if copia['estado'] != 'Disponible':
                return jsonify({"success": False, "error": f"La copia no está disponible. Estado actual: {copia['estado']}"})
            
            # Verificar límite de 3 reservas
            cursor.execute("SELECT COUNT(*) as total FROM prestamo WHERE rut_usuario = %s AND estado = 'Reservado'", (usuario_id,))
            reservas_activas = cursor.fetchone()['total']
            
            if reservas_activas >= 3:
                return jsonify({"success": False, "error": "Alcanzaste el límite de 3 reservas simultáneas."})
            
            # Insertar reserva
            query_reserva = """
                INSERT INTO prestamo (idcopia, rut_usuario, fecha_prestamo, estado) 
                VALUES (%s, %s, NOW(), 'Reservado')
            """
            cursor.execute(query_reserva, (idcopia, usuario_id))
            
            # Cambiar estado de la copia
            cursor.execute("UPDATE copia SET estado = 'Reservado' WHERE idcopia = %s", (idcopia,))
            
            conn.commit()
            return jsonify({"success": True, "mensaje": "¡Libro reservado con éxito! Tienes 2 días para retirarlo en el mesón."})
            
        except Exception as e:
            conn.rollback()
            return jsonify({"success": False, "error": str(e)})
        finally:
            cursor.close()
            conn.close()

    # --- VISTA: RETORNAR CATÁLOGO Y CONTADORES (GET) ---
    try:
        # Catalogo con estado de copia
        query_catalogo = """
            SELECT c.idcopia, m.titulo, m.autor, c.estado 
            FROM copia c 
            JOIN material m ON c.idmaterial = m.idmaterial
        """
        cursor.execute(query_catalogo)
        libros = cursor.fetchall()
        
        cant_prestamos = 0
        cant_reservas = 0
        cant_atrasos = 0
        
        if usuario_id:
            cursor.execute("SELECT COUNT(*) as total FROM prestamo WHERE rut_usuario = %s AND estado = 'Vigente'", (usuario_id,))
            cant_prestamos = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as total FROM prestamo WHERE rut_usuario = %s AND estado = 'Reservado'", (usuario_id,))
            cant_reservas = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as total FROM prestamo WHERE rut_usuario = %s AND estado = 'Atrasado'", (usuario_id,))
            cant_atrasos = cursor.fetchone()['total']
        
        return jsonify({
            "prestamos": cant_prestamos,
            "reservas": cant_reservas,
            "atrasos": cant_atrasos,
            "catalogo_completo": libros
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/mis_prestamos', methods=['GET'])
def api_mis_prestamos():
    usuario_id = session.get('rut_usuario')
    if not usuario_id:
        return jsonify([]), 401
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        query = """
            SELECT p.idprestamo, p.idcopia, m.titulo, p.fecha_prestamo, p.fecha_devolucion, p.estado 
            FROM prestamo p
            JOIN copia c ON p.idcopia = c.idcopia
            JOIN material m ON c.idmaterial = m.idmaterial
            WHERE p.rut_usuario = %s
            ORDER BY p.fecha_prestamo DESC
        """
        cursor.execute(query, (usuario_id,))
        historial = cursor.fetchall()
        
        for row in historial:
            if row['fecha_prestamo']:
                row['fecha_prestamo'] = row['fecha_prestamo'].strftime('%d/%m/%Y')
            if row['fecha_devolucion']:
                row['fecha_devolucion'] = row['fecha_devolucion'].strftime('%d/%m/%Y')
                
        return jsonify(historial)
    except Error:
        return jsonify([]), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/devolver', methods=['POST'])
def api_devolver():
    usuario_id = session.get('rut_usuario')
    if not usuario_id:
        return jsonify({"success": False, "error": "No hay sesión activa"}), 401
    
    data = request.get_json()
    idcopia = data.get('idcopia')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT idprestamo FROM prestamo 
            WHERE idcopia = %s AND rut_usuario = %s AND estado IN ('Vigente', 'Atrasado')
            LIMIT 1
        """, (idcopia, usuario_id))
        prestamo = cursor.fetchone()
        if not prestamo:
            return jsonify({"success": False, "error": "No tienes un préstamo activo de esa copia"})
        
        cursor = conn.cursor()
        cursor.execute("UPDATE prestamo SET estado = 'Devuelto' WHERE idprestamo = %s", (prestamo['idprestamo'],))
        cursor.execute("UPDATE copia SET estado = 'Disponible' WHERE idcopia = %s", (idcopia,))
        conn.commit()
        return jsonify({"success": True, "mensaje": "Devolución registrada correctamente"})
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "error": str(e)})
    finally:
        cursor.close()
        conn.close()


# API ENDPOINTS PARA DESKTOP (ADMINISTRADOR / MESÓN)


@app.route('/api/admin/ver_reservas', methods=['GET'])
def api_admin_ver_reservas():
    # Ejecutar expiración antes de mostrar
    expirar_reservas_vencidas()
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Error de BD"}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT p.idprestamo, u.nombre as alumno, u.rut, m.titulo, p.fecha_prestamo, p.estado, p.idcopia
            FROM prestamo p
            JOIN usuario u ON p.rut_usuario = u.rut
            JOIN copia c ON p.idcopia = c.idcopia
            JOIN material m ON c.idmaterial = m.idmaterial
            WHERE p.estado = 'Reservado'
        """
        cursor.execute(query)
        reservas = cursor.fetchall()
        
        for r in reservas:
            if r['fecha_prestamo']:
                r['fecha_prestamo'] = r['fecha_prestamo'].strftime('%d/%m/%Y %H:%M')
                
        return jsonify({"success": True, "reservas": reservas})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/admin/entregar_libro', methods=['POST'])
def api_admin_entregar_libro():
    data = request.get_json()
    idprestamo = data.get('idprestamo')
    idcopia = data.get('idcopia')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE prestamo 
            SET estado = 'Vigente', fecha_devolucion = DATE_ADD(NOW(), INTERVAL 7 DAY) 
            WHERE idprestamo = %s
        """, (idprestamo,))
        
        cursor.execute("UPDATE copia SET estado = 'Prestado' WHERE idcopia = %s", (idcopia,))
        
        conn.commit()
        return jsonify({"success": True, "message": "Libro entregado al alumno correctamente."})
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/simular_alerta_vencimiento', methods=['POST'])
def api_simular_alerta_vencimiento():
    datos = request.get_json()
    rut_alumno = datos.get('rut')
    titulo_libro = datos.get('titulo')
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Error de base de datos"}), 500
        
    # BUG CORREGIDO: Era conn.connector.cursor() que no existe
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT nombre, correo FROM usuario WHERE rut = %s", (rut_alumno,))
        alumno = cursor.fetchone()
        
        if alumno:
            enviar_correo_alerta(
                alumno['correo'],
                f"🚨 ALERTA DE DEVOLUCIÓN: Plazo Vencido",
                f"Estimado(a) {alumno['nombre']},\n\nLe informamos que el plazo para la devolución del libro '{titulo_libro}' ha expirado.\nPor favor, acérquese al mesón de la biblioteca a la brevedad para regularizar su situación y evitar suspensiones en el sistema.\n\nAtentamente,\nBiblioteca DuocUC."
            )
            return jsonify({"success": True, "message": f"Alerta enviada a {alumno['correo']}"})
        else:
            return jsonify({"success": False, "message": "Alumno no encontrado"}), 404
            
    except Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/admin/todos_prestamos', methods=['GET'])
def api_admin_todos_prestamos():
    expirar_reservas_vencidas()
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Error de BD"}), 500
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT p.idprestamo, p.idcopia, u.nombre as alumno, u.rut, m.titulo,
                   p.fecha_prestamo, p.fecha_devolucion, p.estado
            FROM prestamo p
            JOIN usuario u ON p.rut_usuario = u.rut
            JOIN copia c ON p.idcopia = c.idcopia
            JOIN material m ON c.idmaterial = m.idmaterial
            ORDER BY p.fecha_prestamo DESC
        """
        cursor.execute(query)
        prestamos = cursor.fetchall()
        
        for p in prestamos:
            if 'fecha_prestamo' in p and p['fecha_prestamo']:
                p['fecha_prestamo'] = p['fecha_prestamo'].strftime('%d/%m/%Y')
            if 'fecha_devolucion' in p and p['fecha_devolucion']:
                p['fecha_devolucion'] = p['fecha_devolucion'].strftime('%d/%m/%Y')
        
        return jsonify({"success": True, "prestamos": prestamos})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/admin/expirar_reservas', methods=['POST'])
def api_admin_expirar_reservas():
    """Permite al admin forzar la expiración manual de reservas."""
    expirar_reservas_vencidas()
    return jsonify({"success": True, "message": "Proceso de expiración ejecutado"})



# API ENDPOINTS: ESTADÍSTICAS Y RANKING


@app.route('/api/stats', methods=['GET'])
def api_stats_generales():
    # Ejecutar expiración antes de calcular
    expirar_reservas_vencidas()
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Error de BD"}), 500
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT COUNT(*) as total FROM prestamo WHERE estado = 'Vigente'")
        prestamos = cursor.fetchone()['total']
        cursor.execute("SELECT COUNT(*) as total FROM prestamo WHERE estado = 'Reservado'")
        reservas = cursor.fetchone()['total']
        cursor.execute("SELECT COUNT(*) as total FROM prestamo WHERE estado = 'Atrasado'")
        atrasos = cursor.fetchone()['total']
        cursor.execute("SELECT COUNT(*) as total FROM prestamo WHERE estado = 'Devuelto'")
        devueltos = cursor.fetchone()['total']
        return jsonify({"success": True, "prestamos": prestamos, "reservas": reservas, "atrasos": atrasos, "devueltos": devueltos})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/admin/top_materiales', methods=['GET'])
def api_top_materiales():
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Error de BD"}), 500
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT m.titulo, m.autor, COUNT(p.idprestamo) as veces_prestado
            FROM material m
            JOIN copia c ON c.idmaterial = m.idmaterial
            LEFT JOIN prestamo p ON p.idcopia = c.idcopia
            GROUP BY m.idmaterial, m.titulo, m.autor
            HAVING veces_prestado > 0
            ORDER BY veces_prestado DESC
            LIMIT 10
        """
        cursor.execute(query)
        ranking = cursor.fetchall()
        return jsonify({"success": True, "materiales": ranking})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()



# API ENDPOINTS: CRUD CATEGORÍAS (Tipo Material)


@app.route('/api/categorias', methods=['GET'])
def api_get_categorias():
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Error de BD"}), 500
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT idtipo, nombre, activo FROM tipo_material ORDER BY idtipo")
        categorias = cursor.fetchall()
        return jsonify({"success": True, "categorias": categorias})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/categorias', methods=['POST'])
def api_crear_categoria():
    data = request.get_json()
    nombre = data.get('nombre', '').strip()
    if not nombre:
        return jsonify({"success": False, "message": "El nombre es obligatorio"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO tipo_material (nombre) VALUES (%s)", (nombre,))
        conn.commit()
        return jsonify({"success": True, "message": "Categoría creada correctamente"})
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/categorias/<int:idtipo>', methods=['PUT'])
def api_editar_categoria(idtipo):
    data = request.get_json()
    nombre = data.get('nombre', '').strip()
    if not nombre:
        return jsonify({"success": False, "message": "El nombre es obligatorio"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE tipo_material SET nombre = %s WHERE idtipo = %s", (nombre, idtipo))
        conn.commit()
        return jsonify({"success": True, "message": "Categoría actualizada"})
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/categorias/<int:idtipo>/toggle', methods=['POST'])
def api_toggle_categoria(idtipo):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT activo FROM tipo_material WHERE idtipo = %s", (idtipo,))
        cat = cursor.fetchone()
        if not cat:
            return jsonify({"success": False, "message": "Categoría no encontrada"}), 404
        
        nuevo_estado = 0 if cat['activo'] == 1 else 1
        cursor = conn.cursor()
        cursor.execute("UPDATE tipo_material SET activo = %s WHERE idtipo = %s", (nuevo_estado, idtipo))
        conn.commit()
        estado_texto = "activada" if nuevo_estado == 1 else "desactivada"
        return jsonify({"success": True, "message": f"Categoría {estado_texto}"})
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()



# API ENDPOINTS: CRUD MATERIALES (para Desktop)


@app.route('/api/material', methods=['GET'])
def api_get_materiales():
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Error de BD"}), 500
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT m.idmaterial, m.titulo, m.autor, t.nombre as tipo,
                   (SELECT COUNT(*) FROM copia c WHERE c.idmaterial = m.idmaterial AND c.estado = 'Disponible') as stock_disponible,
                   (SELECT COUNT(*) FROM copia c WHERE c.idmaterial = m.idmaterial) as stock_total
            FROM material m
            LEFT JOIN tipo_material t ON m.idtipo = t.idtipo
            ORDER BY m.titulo
        """
        cursor.execute(query)
        materiales = cursor.fetchall()
        return jsonify({"success": True, "materiales": materiales})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/material', methods=['POST'])
def api_crear_material():
    data = request.get_json()
    titulo = data.get('titulo', '').strip()
    autor = data.get('autor', '').strip()
    idtipo = data.get('idtipo', 1)
    stock = data.get('stock', 1)
    
    if not titulo or not autor:
        return jsonify({"success": False, "message": "Título y autor son obligatorios"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO material (titulo, autor, idtipo) VALUES (%s, %s, %s)", (titulo, autor, idtipo))
        idmaterial = cursor.lastrowid
        
        for _ in range(int(stock)):
            cursor.execute("INSERT INTO copia (idmaterial, estado) VALUES (%s, 'Disponible')", (idmaterial,))
        
        conn.commit()
        return jsonify({"success": True, "message": f"Material creado con {stock} copia(s)"})
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/material/<int:idmaterial>', methods=['PUT'])
def api_editar_material(idmaterial):
    data = request.get_json()
    titulo = data.get('titulo', '').strip()
    autor = data.get('autor', '').strip()
    idtipo = data.get('idtipo')
    
    if not titulo or not autor:
        return jsonify({"success": False, "message": "Título y autor son obligatorios"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE material SET titulo = %s, autor = %s, idtipo = %s WHERE idmaterial = %s", 
                      (titulo, autor, idtipo, idmaterial))
        conn.commit()
        return jsonify({"success": True, "message": "Material actualizado"})
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/material/<int:idmaterial>', methods=['DELETE'])
def api_eliminar_material(idmaterial):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT COUNT(*) as total FROM copia WHERE idmaterial = %s AND estado NOT IN ('Disponible')", (idmaterial,))
        copias_ocupadas = cursor.fetchone()['total']
        
        if copias_ocupadas > 0:
            return jsonify({"success": False, "message": "No se puede eliminar: tiene copias prestadas o reservadas"}), 400
        
        cursor = conn.cursor()
        cursor.execute("DELETE FROM copia WHERE idmaterial = %s", (idmaterial,))
        cursor.execute("DELETE FROM material WHERE idmaterial = %s", (idmaterial,))
        conn.commit()
        return jsonify({"success": True, "message": "Material eliminado del sistema"})
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()



# API ENDPOINTS: ADMIN INVENTARIO (Cambiar estado de copia)


@app.route('/api/admin/inventario', methods=['POST'])
def api_admin_inventario():
    data = request.get_json()
    idcopia = data.get('idcopia')
    nuevo_estado = data.get('estado')
    
    estados_validos = ['Disponible', 'Dañado', 'Baja']
    if nuevo_estado not in estados_validos:
        return jsonify({"success": False, "message": f"Estado inválido. Use: {', '.join(estados_validos)}"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT c.estado, m.titulo FROM copia c JOIN material m ON c.idmaterial = m.idmaterial WHERE c.idcopia = %s", (idcopia,))
        copia = cursor.fetchone()
        if not copia:
            return jsonify({"success": False, "message": "Copia no encontrada"}), 404
        if copia['estado'] in ('Reservado', 'Prestado'):
            return jsonify({"success": False, "message": "No se puede modificar: la copia está " + copia['estado'].lower()}), 400
        
        cursor = conn.cursor()
        cursor.execute("UPDATE copia SET estado = %s WHERE idcopia = %s", (nuevo_estado, idcopia))
        conn.commit()
        return jsonify({"success": True, "message": f"Copia #{idcopia} actualizada a '{nuevo_estado}'"})
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()



# API ENDPOINTS: ADMIN TRANSACCIONES MANUALES (Mesón)


@app.route('/api/admin/transaccion/prestamo', methods=['POST'])
def api_admin_prestamo_manual():
    data = request.get_json()
    rut_alumno = data.get('rut')
    idcopia = data.get('idcopia')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT rut FROM usuario WHERE rut = %s", (rut_alumno,))
        if not cursor.fetchone():
            return jsonify({"success": False, "message": "RUT no registrado en el sistema"}), 404
        
        cursor.execute("SELECT estado FROM copia WHERE idcopia = %s", (idcopia,))
        copia = cursor.fetchone()
        if not copia:
            return jsonify({"success": False, "message": "Copia no encontrada"}), 404
        if copia['estado'] != 'Disponible':
            return jsonify({"success": False, "message": f"Copia no disponible. Estado: {copia['estado']}"}), 400
        
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO prestamo (rut_usuario, idcopia, fecha_prestamo, fecha_devolucion, estado) 
            VALUES (%s, %s, NOW(), DATE_ADD(NOW(), INTERVAL 7 DAY), 'Vigente')
        """, (rut_alumno, idcopia))
        cursor.execute("UPDATE copia SET estado = 'Prestado' WHERE idcopia = %s", (idcopia,))
        conn.commit()
        return jsonify({"success": True, "message": "Préstamo registrado exitosamente"})
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/admin/transaccion/devolucion', methods=['POST'])
def api_admin_devolucion_manual():
    data = request.get_json()
    idcopia = data.get('idcopia')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT idprestamo, rut_usuario, estado FROM prestamo 
            WHERE idcopia = %s AND estado IN ('Vigente', 'Atrasado') 
            ORDER BY idprestamo DESC LIMIT 1
        """, (idcopia,))
        prestamo = cursor.fetchone()
        if not prestamo:
            return jsonify({"success": False, "message": "No hay préstamo activo para esa copia"}), 404
        
        cursor = conn.cursor()
        cursor.execute("UPDATE prestamo SET estado = 'Devuelto' WHERE idprestamo = %s", (prestamo['idprestamo'],))
        cursor.execute("UPDATE copia SET estado = 'Disponible' WHERE idcopia = %s", (idcopia,))
        conn.commit()
        return jsonify({"success": True, "message": "Devolución registrada exitosamente"})
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# API ENDPOINTS: UTILIDADES

@app.route('/api/usuario/<rut>', methods=['GET'])
def api_get_usuario(rut):
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Error de BD"}), 500
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT rut, nombre, correo FROM usuario WHERE rut = %s", (rut,))
        usuario = cursor.fetchone()
        if usuario:
            return jsonify({"success": True, "usuario": usuario})
        else:
            return jsonify({"success": False, "message": "Usuario no encontrado"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()



# API ENDPOINTS: CATÁLOGO AGRUPADO (Para Mobile)

@app.route('/api/catalogo_agrupado', methods=['GET'])
def api_catalogo_agrupado():
    """Devuelve libros únicos con contador de copias, no copias individuales."""
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "error": "No hay conexión a la base de datos"}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT m.idmaterial, m.titulo, m.autor, t.nombre as tipo,
                   COUNT(c.idcopia) as total_copias,
                   SUM(CASE WHEN c.estado = 'Disponible' THEN 1 ELSE 0 END) as copias_disponibles
            FROM material m
            LEFT JOIN tipo_material t ON m.idtipo = t.idtipo
            LEFT JOIN copia c ON c.idmaterial = m.idmaterial
            GROUP BY m.idmaterial, m.titulo, m.autor, t.nombre
            ORDER BY m.titulo
        """
        cursor.execute(query)
        libros = cursor.fetchall()
        return jsonify({"success": True, "libros": libros})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/api/material/<int:idmaterial>/copias', methods=['GET'])
def api_copias_material(idmaterial):
    """Devuelve las copias de un material específico para ver en el detalle."""
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "error": "No hay conexión"}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        # Info del material
        cursor.execute("""
            SELECT m.idmaterial, m.titulo, m.autor, t.nombre as tipo
            FROM material m
            LEFT JOIN tipo_material t ON m.idtipo = t.idtipo
            WHERE m.idmaterial = %s
        """, (idmaterial,))
        material = cursor.fetchone()
        
        if not material:
            return jsonify({"success": False, "error": "Material no encontrado"}), 404
        
        # Copias del material
        cursor.execute("""
            SELECT idcopia, estado 
            FROM copia 
            WHERE idmaterial = %s 
            ORDER BY 
                CASE estado 
                    WHEN 'Disponible' THEN 1 
                    WHEN 'Reservado' THEN 2 
                    ELSE 3 
                END,
                idcopia
        """, (idmaterial,))
        copias = cursor.fetchall()
        
        return jsonify({
            "success": True, 
            "material": material, 
            "copias": copias
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# INICIO DE APLICACIÓN

if __name__ == '__main__':
    print("\n" + "="*60)
    print("  BIBLIOTECA DUOCUC")
    print("  Escritorio: http://localhost:5000/")
    print("  Móvil:      http://localhost:5000/m")
    print("="*60 + "\n")
    app.run(debug=True, port=5000)