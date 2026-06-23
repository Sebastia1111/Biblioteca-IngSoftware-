from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import mysql.connector
from mysql.connector import Error
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key = 'clave_secreta_desarrollo_duocuc'

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='', 
            database='biblioteca_duoc'
        )
        return connection
    except Error as e:
        print(f"Error conectando a MariaDB: {e}")
        return None


# ==========================================
# MOTOR DE NOTIFICACIONES (MODO REALISTA / DEMO)
# ==========================================
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

# ==========================================
# RUTAS DE NAVEGACIÓN Y RENDERIZADO
# ==========================================

@app.route('/')
def index():
    return render_template('desktop/index.html')

@app.route('/m')
def mobile_app():
    return render_template('mobile/mobile.html')


# API ENDPOINTS (ACTUALIZADOS CON TU CORREO)

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    rut_recibido = data.get('rut')
    password_recibido = data.get('password')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Buscamos al usuario usando el RUT que viene del celular
        query = "SELECT rut, nombre, password, idtipousuario FROM usuario WHERE rut = %s"
        cursor.execute(query, (rut_recibido,)) 
        usuario = cursor.fetchone()
    except Exception as e:
        return jsonify({"success": False, "message": f"Error en BD: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()
    
    # Validamos si existe y si la contraseña coincide
    if usuario and usuario['password'] == password_recibido:
        # ¡Guardamos el RUT real en la sesión de Flask para la reserva!
        session['rut_usuario'] = usuario['rut'] 
        
        # Le respondemos a JavaScript exactamente lo que pide para armar la pantalla
        return jsonify({
            "success": True, 
            "nombre": usuario['nombre'],
            "idtipousuario": usuario['idtipousuario']
        })
    else:
        return jsonify({"success": False, "message": "RUT o contraseña incorrectos"})

@app.route('/api/resumen_usuario', methods=['GET', 'POST'])
def api_resumen_usuario():
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "error": "No hay conexión a la base de datos"}), 500
        
    cursor = conn.cursor(dictionary=True)

    # --- SI EL USUARIO QUIERE RESERVAR (POST) ---
    if request.method == 'POST':
        data = request.get_json()
        idcopia = data.get('idcopia')
        
        # Saca el RUT automáticamente de la sesión del usuario que se logueó
        usuario_id = session.get('rut_usuario')  
        
        if not usuario_id:
            cursor.close()
            conn.close()
            return jsonify({"success": False, "error": "No hay una sesión activa. Por favor, inicia sesión de nuevo."}), 401
            
        try:
            query_reserva = """
                INSERT INTO prestamo (idcopia, rut_usuario, fecha_prestamo, estado) 
                VALUES (%s, %s, NOW(), 'Reservado')
            """
            cursor.execute(query_reserva, (idcopia, usuario_id))
            
            query_update = "UPDATE copia SET estado = 'Reservado' WHERE idcopia = %s"
            cursor.execute(query_update, (idcopia,))
            
            conn.commit()
            return jsonify({"success": True, "mensaje": "¡Libro reservado con éxito!"})
            
        except Exception as e:
            conn.rollback()
            return jsonify({"success": False, "error": str(e)}), 200
        finally:
            cursor.close()
            conn.close()


    # PARTE 2: MOSTRAR EL CATÁLOGO (Cuando el celular entra normal con un GET)

    try:
        query_catalogo = "SELECT c.idcopia, m.titulo, m.autor, c.estado FROM copia c JOIN material m ON c.idmaterial = m.idmaterial"
        cursor.execute(query_catalogo)
        libros = cursor.fetchall()
        
        # Aquí puedes agregar las consultas de tus contadores si los necesitas más adelante
        return jsonify({
            "prestamos": 0,
            "reservas": 0,
            "atrasos": 0,
            "catalogo_completo": libros
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/mis_prestamos', methods=['GET'])
def api_mis_prestamos():
    if 'user_rut' not in session:
        return jsonify([]), 401
        
    rut = session['user_rut']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        query = """
            SELECT p.idcopia, m.titulo, p.fecha_devolucion, p.estado 
            FROM prestamo p
            JOIN copia c ON p.idcopia = c.idcopia
            JOIN material m ON c.idmaterial = m.idmaterial
            WHERE p.rut_usuario = %s
        """
        cursor.execute(query, (rut,))
        historial = cursor.fetchall()
        
        for row in historial:
            if row['fecha_devolucion']:
                row['fecha_devolucion'] = row['fecha_devolucion'].strftime('%d/%m/%Y')
                
        return jsonify(historial)
    except Error:
        return jsonify([]), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(debug=True, port=5000)


# API: RESERVA DE MATERIALES

@app.route('/api/reservar', methods=['POST'])
def api_reservar():
    if 'user_rut' not in session:
        return jsonify({"success": False, "message": "No autorizado"}), 401
        
    datos = request.get_json()
    idmaterial = datos.get('idmaterial')
    titulo_libro = datos.get('titulo', 'Libro Solicitado')
    

    
    return jsonify({"success": True, "message": "Reserva confirmada y correo enviado."})



# API: ALERTA DE VENCIMIENTO (SIMULACIÓN AUTOMÁTICA)

@app.route('/api/simular_alerta_vencimiento', methods=['POST'])
def api_simular_alerta_vencimiento():
    """
    Ruta pensada para que el Administrador (Sebastián) pueda presionar un botón 
    en el mesón y notificar a los alumnos que tienen libros atrasados.
    """
    datos = request.get_json()
    rut_alumno = datos.get('rut')
    titulo_libro = datos.get('titulo')
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Error de base de datos"}), 500
        
    cursor = conn.cursor(dictionary=True)
    try:
        # Buscamos el correo real del alumno en la base de datos usando su RUT
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

@app.route('/api/catalogo', methods=['GET'])
def api_catalogo():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "No hay conexión a la base de datos"}), 500
        
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT c.idcopia, m.titulo, m.autor, c.estado 
        FROM copia c
        JOIN material m ON c.idmaterial = m.idmaterial
    """
    cursor.execute(query)
    libros = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify(libros)


@app.route('/api/reservar', methods=['POST'])
def api_reservar():
    data = request.get_json()
    idcopia = data.get('idcopia')
    # Aquí asumimos que tienes el RUT o ID del usuario en la sesión, 
    # o que lo mandas desde el cliente. Ajusta 'seba.orellanav' por tu lógica real si es necesario.
    usuario_id = "seba.orellanav" 
    
    if not idcopia:
        return jsonify({"error": "Falta el código de la copia"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "No hay conexión a la base de datos"}), 500
        
    cursor = conn.cursor()
    
    try:
        # 1. Insertamos la reserva (Ajusta los nombres de tus columnas si varían)
        # Por ejemplo: tabla 'reserva' con columnas (idcopia, usuario, fecha_reserva, estado)
        query_reserva = """
            INSERT INTO reserva (idcopia, idusuario, fecha_reserva, estado) 
            VALUES (%s, %s, NOW(), 'Reservado')
        """
        cursor.execute(query_reserva, (idcopia, usuario_id))
        
        # 2. Opcional: Actualizar el estado de la copia a 'Reservado' para que nadie más la pida
        query_update_copia = "UPDATE copia SET estado = 'Reservado' WHERE idcopia = %s"
        cursor.execute(query_update_copia, (idcopia,))
        
        conn.commit()
        return jsonify({"success": True, "mensaje": "¡Reserva realizada con éxito!"})
        
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Error al reservar en MariaDB: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()