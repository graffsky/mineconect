from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_socketio import SocketIO, emit
from sqlalchemy import text
from dotenv import load_dotenv
import os
import click
import logging
from flask_mail import Mail, Message
import random
from datetime import datetime, timedelta, timezone
from flask_migrate import Migrate
from extensions import db

# --- IMPORTAMOS TODOS LOS MODELOS DE LA BASE DE DATOS ---
from models import (
    Usuario, Emprendedor, TipoPerfil, Empresario, Inversionista, Institucion,
    EmpresarioMercado, EmpresarioAlianza, EmpresarioDiagnostico,
    InstitucionConvocatoria, InstitucionPrograma, InstitucionNoticia,
    EmpresarioDiscusion, EmprendedorProyecto, EmpresarioMensaje,
    InstitucionMensaje, Comentario, ConvocatoriaPostulacion, ProgramaPostulacion
)

# Configuración básica del logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Cargar variables del archivo .env
load_dotenv()

# Crear la aplicación Flask
app = Flask(__name__)

# Configuración de la base de datos y secret key
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "clave_por_defecto_muy_segura")

# --- Configuración de Flask-Mail ---
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'true').lower() in ['true', '1', 't']
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'false').lower() in ['true', '1', 't']
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = ('Mineconect', os.getenv('MAIL_USERNAME'))

# Inicializar extensiones
db.init_app(app)
mail = Mail(app)
migrate = Migrate(app, db)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('Principal'))

# ✅ Prueba de conexión a la base de datos
with app.app_context():
    try:
        with db.engine.connect() as connection:
            connection.execute(text("SELECT 1;"))
        app.logger.info("✅ Conexión a la base de datos exitosa")
    except Exception as e:
        app.logger.error(f"❌ Error al conectar con la base de datos: {e}")

def formato_fecha_es(fecha):
    if not fecha:
        return ""
    meses = {
        1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun",
        7: "Jul", 8: "Ago", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"
    }
    return f"{fecha.day} {meses[fecha.month]}, {fecha.year}"

# --- RUTAS PRINCIPALES ---
@app.route('/')
def Principal():
    return render_template('Principal.html')

@app.route("/habeasdata")
def habeasdata():
    return render_template("Habeasdata.html")

# ==========================================
# RUTAS DE REGISTRO Y LOGIN (Mantenemos tu lógica original)
# ==========================================

@app.route('/registro_emprendedor', methods=['GET', 'POST'])
def registro_emprendedor():
    """
    Ruta para manejar el registro de nuevos usuarios con el perfil 'Emprendedor'.
    Si el método es POST, recopila la información del formulario (datos personales y del proyecto SENA),
    crea el objeto Usuario, enlaza el perfil Emprendedor, y lo guarda en la base de datos.
    En caso de éxito, redirige a la página de éxito. Si hay error, deshace los cambios (rollback).
    """
    if request.method == 'POST':
        try:
            nuevo_usuario = Usuario(email=request.form['correo'], tipo_perfil=TipoPerfil.EMPRENDEDOR)
            nuevo_usuario.set_password(request.form['contrasena'])

            nuevo_emprendedor = Emprendedor(
                nombre_completo=request.form['nombre_completo'],
                tipo_documento=request.form['tipo_documento'],
                numero_documento=request.form['numero_documento'],
                numero_celular=request.form['numero_celular'],
                programa_formacion=request.form['programa_formacion'],
                titulo_proyecto=request.form['titulo_proyecto'],
                descripcion_proyecto=request.form['descripcion_proyecto'],
                relacion_sector=request.form['relacion_sector'],
                tipo_apoyo=request.form['tipo_apoyo']
            )

            nuevo_usuario.emprendedor = nuevo_emprendedor
            db.session.add(nuevo_usuario)
            db.session.commit()
            return render_template('registro_exitoso.html', tipo_cuenta='Emprendedor', nombre_perfil=nuevo_emprendedor.nombre_completo)
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error: {e}")
            flash(f'Hubo un error en el registro: {e}', 'danger')
    return render_template('Registro_emprendedor.html')

@app.route('/registro_empresario', methods=['GET', 'POST'])
def registro_empresario():
    """
    Ruta para registrar nuevos usuarios con perfil 'Empresario'.
    Contiene lógica adicional para diferenciar el 'tipo de contribuyente' (Persona Natural vs Jurídica)
    y así asignar correctamente los documentos de identificación o NIT.
    Verifica también que el correo electrónico no exista previamiente en el sistema para evitar duplicados.
    """
    if request.method == 'POST':
        try:
            correo = request.form['correo']
            if db.session.execute(db.select(Usuario).filter_by(email=correo)).first():
                flash('El correo electrónico ya está registrado.', 'error')
                return redirect(url_for('registro_empresario'))

            nuevo_usuario = Usuario(email=correo, tipo_perfil=TipoPerfil.EMPRESARIO)
            nuevo_usuario.set_password(request.form['contrasena'])
            
            tipo_contribuyente = request.form.get('tipo_contribuyente')
            num_doc_contribuyente = request.form.get('numero_documento_contribuyente') if tipo_contribuyente == 'natural' else None
            nit_contribuyente = request.form.get('nit') if tipo_contribuyente == 'juridica' else None

            nuevo_empresario = Empresario(
                nombre_completo=request.form['nombre_completo'],
                tipo_documento_personal=request.form['tipo_documento_personal'],
                numero_documento_personal=request.form['numero_documento_personal'],
                numero_celular=request.form['numero_celular'],
                nombre_empresa=request.form['nombre_empresa'],
                tipo_contribuyente=tipo_contribuyente,
                numero_documento_contribuyente=num_doc_contribuyente,
                nit=nit_contribuyente,
                tamano=request.form['tamano'],
                sector_produccion=request.form['sector_produccion'],
                sector_transformacion=request.form['sector_transformacion'],
                sector_comercializacion=request.form['sector_comercializacion']
            )
            
            nuevo_usuario.empresario = nuevo_empresario
            db.session.add(nuevo_usuario)
            db.session.commit()
            return render_template('registro_exitoso.html', tipo_cuenta='Empresario', nombre_perfil=nuevo_empresario.nombre_completo)
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error: {e}")
            flash('Error inesperado en el registro.', 'error')
            return redirect(url_for('registro_empresario'))
    return render_template('Registro_empresario.html')

@app.route('/registro_institucion', methods=['GET', 'POST'])
def registro_institucion():
    """
    Ruta para manejar la creación de cuentas Institucionales (Aliados, SENA, Gobierno).
    Captura datos específicos como el NIT, municipio, área de especialización y las 
    áreas en las que la institución desea tener "participación activa" (las cuales se guardan como string separado por comas).
    """
    if request.method == 'POST':
        try:
            correo = request.form['correo']
            nit = request.form['nit']
            if db.session.execute(db.select(Usuario).filter_by(email=correo)).first():
                flash('El correo ya existe.', 'error')
                return redirect(url_for('registro_institucion'))

            nuevo_usuario = Usuario(email=correo, tipo_perfil=TipoPerfil.INSTITUCION)
            nuevo_usuario.set_password(request.form['contrasena'])

            participacion = request.form.getlist('participacion_activa')
            participacion_str = ','.join(participacion)

            nueva_institucion = Institucion(
                nombre_completo=request.form['nombre_institucion'],
                nit=nit,
                tipo_institucion=request.form['tipo_institucion'],
                municipio=request.form['municipio'],
                descripcion=request.form['descripcion'],
                area_especializacion=request.form['area_especializacion'],
                participacion_activa=participacion_str
            )
            nuevo_usuario.institucion = nueva_institucion
            db.session.add(nuevo_usuario)
            db.session.commit()
            return render_template('registro_exitoso.html', tipo_cuenta='Institución', nombre_perfil=nueva_institucion.nombre_completo)
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error: {e}")
            flash('Hubo un error inesperado.', 'danger')
    return render_template('Registro_institucion.html')

@app.route('/registro_inversionista', methods=['GET', 'POST'])
def registro_inversionista():
    """
    Ruta para la inscripción de Inversionistas o Fondos de Inversión Privados.
    Registra áreas de interés y etapas de interés, procesando las listas del formulario
    y convirtiéndolas a strings planos separados por comas para su almacenamiento en DB.
    """
    # ... (Tu código actual de inversionista se mantiene igual) ...
    if request.method == 'POST':
        try:
            correo = request.form['correo']
            if db.session.execute(db.select(Usuario).filter_by(email=correo)).first():
                flash('El correo ya está registrado.', 'error')
                return redirect(url_for('registro_inversionista'))
            
            nuevo_usuario = Usuario(email=correo, tipo_perfil=TipoPerfil.INVERSIONISTA)
            nuevo_usuario.set_password(request.form['contrasena'])

            etapas_str = ','.join(request.form.getlist('etapas'))
            areas_str = ','.join(request.form.getlist('areas'))

            nuevo_inversionista = Inversionista(
                nombre_completo=request.form['nombreCompleto'],
                tipo_documento=request.form['tipoDocumento'],
                numero_documento=request.form['numeroDocumento'],
                numero_celular=request.form['numeroCelular'],
                nombre_fondo=request.form['nombreFondo'],
                tipo_inversion=request.form['tipoInversion'],
                etapas_interes=etapas_str,
                areas_interes=areas_str
            )

            nuevo_usuario.inversionista = nuevo_inversionista
            db.session.add(nuevo_usuario)
            db.session.commit()

            return render_template('registro_exitoso.html', tipo_cuenta='Inversionista', nombre_perfil=nuevo_inversionista.nombre_completo)

        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error: {e}")
            flash('Error inesperado.', 'error')
            return redirect(url_for('registro_inversionista'))
    return render_template('Registro_inversionista.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Ruta para manejar el inicio de sesión de los usuarios.
    - Recibe: Petición POST con JSON que contiene `email`, `password` y `profile` (tipo de perfil).
    - Proceso: 
      1. Valida las credenciales en la base de datos contra el hash de seguridad.
      2. Si son válidas, genera un código de verificación de 6 dígitos (2FA simulado).
      3. Guarda el código en la sesión (vigencia de 10 min) e intenta enviarlo por correo vía SMTP.
    - Retorna: JSON con éxito o fallo para que el frontend abra el modal de ingreso de código.
    """
    if request.method == 'POST':
        try:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
            profile_type_str = data.get('profile')

            if not email or not password or not profile_type_str:
                return jsonify({'success': False, 'message': 'Faltan campos.'}), 400

            profile_type = TipoPerfil(profile_type_str)
        except ValueError:
            return jsonify({'success': False, 'message': 'Perfil inválido.'}), 400
        except Exception:
            return jsonify({'success': False, 'message': 'Solicitud incorrecta.'}), 400

        usuario = db.session.execute(db.select(Usuario).filter_by(email=email, tipo_perfil=profile_type)).scalar_one_or_none()

        if usuario and usuario.check_password(password):
            verification_code = f"{random.randint(100000, 999999)}"
            expiration_time = datetime.now(timezone.utc) + timedelta(minutes=10)
            
            # Guardo pre-sesión del usuario en espera de validación del código
            session['verification_code'] = verification_code
            session['code_expiration'] = expiration_time.isoformat()
            session['user_to_verify'] = usuario.id

            # IMPRIMIR CÓDIGO EN TERMINAL SIEMPRE (Útil para pruebas o fallos de SMTP)
            print(f"==========================================")
            print(f"🔐 CÓDIGO DE VERIFICACIÓN PARA {email}: {verification_code}")
            print(f"==========================================")

            try:
                # Envío de correo usando Flask-Mail
                msg = Message(subject="Código de verificación Mineconect", recipients=[usuario.email])
                perfil = usuario.get_perfil()
                msg.html = render_template('Email/verificacion-codigo.html', code=verification_code, nombre_completo=perfil.nombre_completo)
                mail.send(msg)
                
                user_part, domain_part = usuario.email.split('@')
                masked_email = f"{user_part[:2]}****{user_part[-2:]}@{domain_part}"
                return jsonify({'success': True, 'message': 'Código enviado.', 'email': masked_email})
            except Exception as e:
                app.logger.error(f"❌ Error enviando email: {e}")
                # Si falla el email, permitimos continuar usando el código de la terminal local
                user_part, domain_part = usuario.email.split('@')
                masked_email = f"{user_part[:2]}****{user_part[-2:]}@{domain_part}"
                return jsonify({'success': True, 'message': 'Error enviando email, revise terminal para código.', 'email': masked_email})
        else:
            return jsonify({'success': False, 'message': 'Credenciales incorrectas.'}), 401
    return redirect(url_for('Principal'))

@app.route('/verify_code', methods=['POST'])
def verify_code():
    """
    Ruta para la validación del código 2FA ingresado tras el login.
    - Recibe: JSON con el parámetro `code`.
    - Proceso: Compara el código ingresado con el guardado temporalmente en la `session`.
      Si coinciden, consolida el inicio de sesión oficial en Flask guardando el ID del usuario en `session`.
    - Retorna: Objeto JSON. Si es correcto, el frontend redirigirá al dashboard correspondiente.
    """
    data = request.get_json()
    user_code = data.get('code')
    stored_code = session.get('verification_code')
    user_id = session.get('user_to_verify')

    # Validación exitosa del código
    if user_code == stored_code and user_id:
        usuario = db.session.get(Usuario, user_id)
        
        # Consolidación real de la sesión (el usuario ya está logueado formalmente)
        session['user_id'] = usuario.id
        session['user_email'] = usuario.email
        session['user_profile'] = usuario.tipo_perfil.value
        
        # Guardar el nombre en sesión para mostrarlo globalmente en la barra superior
        perfil = usuario.get_perfil()
        if hasattr(perfil, 'nombre_empresa'):
            session['nombre_usuario'] = perfil.nombre_empresa
            session['nombre_empresa'] = perfil.nombre_empresa
        elif hasattr(perfil, 'nombre_completo'):
             session['nombre_usuario'] = perfil.nombre_completo
        
        return jsonify({'success': True, 'message': 'Bienvenido', 'role': usuario.tipo_perfil.value})
        
    return jsonify({'success': False, 'message': 'Código incorrecto.'}), 400

@app.route('/forgot_password', methods=['POST'])
def forgot_password():
    """
    Ruta para manejar la solicitud de recuperación de contraseña olvidada.
    - Recibe: JSON con el `email` del usuario.
    - Manejo seguro: Intencionalmente en este proyecto se confirma siempre el modelo "si el correo está
      registrado, recibirás un código", para evitar listar correos existentes a atacantes.
    - Acción: Genera un token aleatorio, lo almacena en sesión, y envía un correo con 10 min de expiración.
    """
    try:
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({'success': False, 'message': 'El correo es requerido.'}), 400

        usuario = db.session.execute(db.select(Usuario).filter_by(email=email)).scalar_one_or_none()
        
        if not usuario:
            # Por seguridad (prevención de enumeración de usuarios), damos una respuesta ambigua exitosa
            return jsonify({'success': True, 'message': 'Si el correo está registrado, recibirás un código.'})

        recovery_code = f"{random.randint(100000, 999999)}"
        expiration_time = datetime.now(timezone.utc) + timedelta(minutes=10)
        
        session['recovery_code'] = recovery_code
        session['recovery_expiration'] = expiration_time.isoformat()
        session['user_to_recover'] = usuario.id

        # IMPRIMIR CÓDIGO EN TERMINAL SIEMPRE (Ayuda a pruebas)
        print(f"==========================================")
        print(f"🔑 CÓDIGO DE RECUPERACIÓN PARA {email}: {recovery_code}")
        print(f"==========================================")

        try:
            msg = Message(subject="Restablecer Contraseña - Mineconect", recipients=[usuario.email])
            perfil = usuario.get_perfil()
            nombre = getattr(perfil, 'nombre_completo', getattr(perfil, 'nombre_empresa', 'Usuario'))
            msg.html = render_template('Email/recuperacion-password.html', code=recovery_code, nombre_completo=nombre)
            mail.send(msg)
            return jsonify({'success': True, 'message': 'Código de recuperación enviado.'})
        except Exception as e:
            app.logger.error(f"❌ Error enviando email de recuperación: {e}")
            return jsonify({'success': True, 'message': 'Error enviando email, revise terminal para código.'})

    except Exception as e:
        app.logger.error(f"❌ Error en forgot_password: {e}")
        return jsonify({'success': False, 'message': 'Ocurrió un error inesperado.'}), 500

@app.route('/reset_password', methods=['POST'])
def reset_password():
    try:
        data = request.get_json()
        code = data.get('code')
        new_password = data.get('password')
        confirm_password = data.get('confirm_password')
        
        stored_code = session.get('recovery_code')
        user_id = session.get('user_to_recover')
        expiration_str = session.get('recovery_expiration')

        if not code or not new_password or not confirm_password:
            return jsonify({'success': False, 'message': 'Todos los campos son obligatorios.'}), 400

        if new_password != confirm_password:
            return jsonify({'success': False, 'message': 'Las contraseñas no coinciden.'}), 400
            
        if len(new_password) > 8:
            return jsonify({'success': False, 'message': 'La contraseña no debe exceder los 8 caracteres.'}), 400

        if not stored_code or code != stored_code:
            return jsonify({'success': False, 'message': 'Código inválido o expirado.'}), 400

        if expiration_str:
            expiration_time = datetime.fromisoformat(expiration_str)
            if datetime.now(timezone.utc) > expiration_time:
                return jsonify({'success': False, 'message': 'El código ha expirado.'}), 400

        usuario = db.session.get(Usuario, user_id)
        if not usuario:
            return jsonify({'success': False, 'message': 'Usuario no encontrado.'}), 404

        usuario.set_password(new_password)
        db.session.commit()

        # Limpiar sesión de recuperación
        session.pop('recovery_code', None)
        session.pop('recovery_expiration', None)
        session.pop('user_to_recover', None)

        return jsonify({'success': True, 'message': 'Contraseña restablecida con éxito.'})

    except Exception as e:
        app.logger.error(f"❌ Error en reset_password: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Ocurrió un error al restablecer la contraseña.'}), 500

@app.route('/Empresario/config/update_photo', methods=['POST'])
def update_empresario_photo():
    data = request.get_json()
    photo_url = data.get('photo_url')
    if photo_url:
        session['profile_image'] = photo_url
        return jsonify({'success': True, 'message': 'Foto actualizada'})
    return jsonify({'success': False, 'message': 'URL no válida'}), 400

# ==========================================
# RUTAS DE EMPRESARIO (CONECTADAS A LA BD REAL)
# ==========================================

@app.route('/Empresario-inicio')
def empresario_inicio():
    """
    Ruta del Dashboard Principal del Empresario tras iniciar sesión.
    - Acciones:
      1. Verifica que el usuario tenga una sesión válida y un perfil de Empresario.
      2. Recopila y unifica en una sola lista cronológica sus publicaciones activas
         (Mercado, Alianzas y Discusiones) para mostrar en su panel.
      3. Extrae las Convocatorias Abiertas, Programas Activos y Noticias del Sector 
         para mostrar recomendaciones y oportunidades en la pantalla principal.
    - Retorna: Renderiza 'Empresario-inicio.html' con múltiples contextos.
    """
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('Principal'))
    
    usuario = db.session.get(Usuario, user_id)
    if not usuario or not usuario.empresario:
        # Fallback si por alguna razón no tiene perfil empresario
        return render_template('Empresario-inicio.html', publicaciones=[], convocatorias=[])

    # Unificar Mis Publicaciones
    mis_publicaciones = []

    # 1. Mercado
    productos = EmpresarioMercado.query.filter_by(empresario_id=usuario.empresario.id).all()
    for p in productos:
        mis_publicaciones.append({
            'titulo': p.titulo,
            'tipo': p.tipo, # Venta / Alquiler
            'tipo_class': 'success' if p.tipo == 'Venta' else 'accent',
            'icon': 'storefront',
            'tipo_class': 'success' if p.tipo == 'Venta' else 'accent',
            'icon': 'storefront',
            'fecha': formato_fecha_es(p.fecha_publicacion),
            'estado': 'Publicado',
            'estado': 'Publicado',
            'estado_class': 'success',
            'edit_url': '#', # Pendiente implementar edit mercado modal
            'delete_url': f'/Empresario-mercado/eliminar/{p.id}'
        })

    # 2. Alianzas
    alianzas = EmpresarioAlianza.query.filter_by(empresario_id=usuario.empresario.id).all()
    for a in alianzas:
        mis_publicaciones.append({
            'titulo': f"Alianza: {a.tipo_oferta}",
            'tipo': 'Alianza',
            'tipo_class': 'primary',
            'icon': 'groups',
            'tipo_class': 'primary',
            'icon': 'groups',
            'fecha': formato_fecha_es(a.fecha_publicacion),
            'estado': 'Activa',
            'estado': 'Activa',
            'estado_class': 'success',
            'edit_url': '#', # Pendiente
            'delete_url': '#' # Pendiente
        })

    # 3. Discusiones
    discusiones = EmpresarioDiscusion.query.filter_by(usuario_id=user_id).all()
    for d in discusiones:
        mis_publicaciones.append({
            'titulo': d.titulo,
            'tipo': 'Discusión',
            'tipo_class': 'purple-600',
            'icon': 'forum',
            'tipo_class': 'purple-600',
            'icon': 'forum',
            'fecha': formato_fecha_es(d.fecha_creacion),
            'estado': 'Abierta',
            'estado': 'Abierta',
            'estado_class': 'success',
            'edit_url': '#', 
            'delete_url': f'/Empresario-discusiones/eliminar/{d.id}'
        })

    # Ordenar por fecha reciente (si fuera objeto datetime, pero aqui es string formateado, 
    # idealmente ordenar antes de formatear. Por simplicidad, lo dejamos asi por ahora)
    
    # Convocatorias Recientes (Oportunidades)
    convocatorias_bd = InstitucionConvocatoria.query.filter_by(estado='Abierta')\
                    .order_by(InstitucionConvocatoria.fecha_cierre.asc()).limit(5).all()
    convocatorias = []
    for c in convocatorias_bd:
        convocatorias.append({
            'titulo': c.titulo,
            'descripcion': c.descripcion,
            'fecha_cierre': c.fecha_cierre, # Objeto fecha crudo para posible lógica en la plantilla
            'fecha_cierre_str': formato_fecha_es(c.fecha_cierre), # Formato en español para mostrar al usuario
            'fecha_cierre_raw': c.fecha_cierre # Fecha sin formato para ordenar si es necesario
        })

    # Programas de Formación (Oferta Educativa)
    programas = InstitucionPrograma.query.filter(InstitucionPrograma.estado == 'Inscripciones Abiertas').limit(5).all()

    # Noticias del Sector
    noticias_bd = InstitucionNoticia.query.order_by(InstitucionNoticia.fecha_publicacion.desc()).limit(3).all()
    noticias = []
    for n in noticias_bd:
        noticias.append({
            'titulo': n.titulo,
            'categoria': n.categoria,
            'contenido': n.contenido,
            'imagen_url': n.imagen_url,
            'fecha': formato_fecha_es(n.fecha_publicacion)
        })

    return render_template('Empresario-inicio.html', publicaciones=mis_publicaciones, convocatorias=convocatorias, programas=programas, noticias=noticias)




@app.route('/Empresario-mercado', methods=['GET', 'POST'])
def empresario_mercado():
    """
    Ruta del módulo "Mercado Minero" para el Empresario.
    - GET: Lee todos los productos tipo Venta o Alquiler ordenador del más reciente al antiguo.
    - POST: Permite al empresario publicar un nuevo activo (maquinaria, insumos) vinculándolo a su ID.
    """
    if request.method == 'POST':
        try:
            user_id = session.get('user_id')
            usuario = db.session.get(Usuario, user_id)
            
            # Verificar si el usuario existe y es empresario
            if usuario and usuario.empresario:
                nuevo_item = EmpresarioMercado(
                    empresario_id=usuario.empresario.id,
                    titulo=request.form.get('titulo'),
                    tipo=request.form.get('tipo'), # Venta o Alquiler
                    precio=request.form.get('celular'),
                    ubicacion=request.form.get('ubicacion'),
                    imagen_url=request.form.get('imagen_url') or "https://via.placeholder.com/400x300"
                )
                db.session.add(nuevo_item)
                db.session.commit()
                flash('Anuncio publicado exitosamente', 'success')
            else:
                flash('Error: No tienes permiso para publicar', 'danger')
            return redirect(url_for('empresario_mercado'))
        except Exception as e:
            app.logger.error(f"Error mercado: {e}")
            flash('Error al publicar', 'danger')

    # LEER DE BASE DE DATOS (Ordenado por más reciente)
    productos_bd = EmpresarioMercado.query.order_by(EmpresarioMercado.fecha_publicacion.desc()).all()
    return render_template('Empresario-mercado.html', productos=productos_bd)

@app.route('/Empresario-mercado/editar/<int:id>', methods=['POST'])
def editar_producto(id):
    try:
        producto = db.session.get(EmpresarioMercado, id)
        if producto:
            producto.titulo = request.form.get('titulo')
            producto.tipo = request.form.get('tipo')
            producto.celular = request.form.get('celular')
            producto.ubicacion = request.form.get('ubicacion')
            if request.form.get('imagen_url'):
                producto.imagen_url = request.form.get('imagen_url')
            
            db.session.commit()
            flash('Anuncio actualizado', 'success')
        return redirect(url_for('empresario_mercado'))
    except Exception as e:
        db.session.rollback()
        app.logger.error(e)
        return redirect(url_for('empresario_mercado'))

@app.route('/Empresario-mercado/eliminar/<int:id>', methods=['POST'])
def eliminar_producto(id):
    producto = db.session.get(EmpresarioMercado, id)
    if producto:
        db.session.delete(producto)
        db.session.commit()
        flash('Anuncio eliminado', 'success')
    return redirect(url_for('empresario_mercado'))

@app.route('/Empresario-alianzas', methods=['GET', 'POST'])
def empresario_alianzas():
    """
    Ruta del módulo "Alianzas Estratégicas".
    - Permite la publicación y lectura de propuestas de colaboración o búsqueda de socios 
      por parte del sector empresarial minero.
    """
    if request.method == 'POST':
        try:
            user_id = session.get('user_id')
            usuario = db.session.get(Usuario, user_id)
            
            if usuario and usuario.empresario:
                nueva_alianza = EmpresarioAlianza(
                    empresario_id=usuario.empresario.id,
                    tipo_oferta=request.form.get('tipo_oferta'),
                    descripcion=request.form.get('descripcion'),
                    ubicacion=request.form.get('ubicacion')
                )
                db.session.add(nueva_alianza)
                db.session.commit()
                flash('Alianza publicada', 'success')
            return redirect(url_for('empresario_alianzas'))
        except Exception as e:
            app.logger.error(f"Error alianzas: {e}")

    # LEER DE BASE DE DATOS
    alianzas_bd = EmpresarioAlianza.query.order_by(EmpresarioAlianza.fecha_publicacion.desc()).all()
    return render_template('Empresario-alianzas.html', alianzas=alianzas_bd)

@app.route('/Empresario-alianzas/editar/<int:id>', methods=['POST'])
def editar_alianza(id):
    try:
        alianza = db.session.get(EmpresarioAlianza, id)
        if alianza:
            alianza.tipo_oferta = request.form.get('tipo_oferta')
            alianza.descripcion = request.form.get('descripcion')
            alianza.ubicacion = request.form.get('ubicacion')
            db.session.commit()
            flash('Oferta actualizada', 'success')
        return redirect(url_for('empresario_alianzas'))
    except Exception as e:
        db.session.rollback()
        app.logger.error(e)
        return redirect(url_for('empresario_alianzas'))

@app.route('/Empresario-alianzas/eliminar/<int:id>', methods=['POST'])
def eliminar_alianza(id):
    alianza = db.session.get(EmpresarioAlianza, id)
    if alianza:
        db.session.delete(alianza)
        db.session.commit()
        flash('Oferta eliminada', 'success')
    return redirect(url_for('empresario_alianzas'))


@app.route('/Empresario-proyectos', methods=['GET', 'POST'])
def empresario_proyectos_view():
    """
    Ruta donde los Empresarios visualizan el catálogo de "Proyectos" creados por Emprendedores SENA.
    - Implementa un buscador opcional por palabra clave en el título.
    - (Nota de desarrollo: Actualmente incluye un Dummy Data integrado para propósitos de 
      demostración visual en ferias o validaciones institucionales tempranas).
    """
    # Los empresarios VEN proyectos (que crean los emprendedores)
    busqueda = request.form.get('search_query', '')
    
    if busqueda:
        proyectos_bd = EmprendedorProyecto.query.filter(EmprendedorProyecto.titulo.ilike(f'%{busqueda}%')).all()
    else:
        proyectos_bd = EmprendedorProyecto.query.all()

    # --- DATOS DE PRUEBA PARA VISUALIZACIÓN (DUMMY DATA) ---
    dummy_projects = [
        {
            "titulo": "EcoMinería Sostenible 4.0",
            "estado": "En Revisión",
            "descripcion": "Implementación de sensores IoT para monitoreo ambiental en tiempo real en pequeñas minas de carbón, reduciendo el impacto ambiental y mejorando la seguridad operativa.",
            "capital_requerido": "$45.000.000",
            "tipo_apoyo_buscado": "Inversión Tecnológica",
            "emprendedor": {
                "nombre_completo": "Carlos Rodríguez",
                "programa_formacion": "Aprendiz SENA - Tecnólogo en Minería",
                "usuario_id": 999
            }
        },
        {
            "titulo": "Plataforma de Trazabilidad del Oro",
            "estado": "Aprobado",
            "descripcion": "Sistema basado en Blockchain para certificar el origen limpio del oro artesanal, conectando mineros locales con compradores internacionales certificados.",
            "capital_requerido": "$120.000.000",
            "tipo_apoyo_buscado": "Alianza Comercial",
            "emprendedor": {
                "nombre_completo": "Ana María López",
                "programa_formacion": "Aprendiz SENA - Ingeniería de Sistemas",
                "usuario_id": 998
            }
        },
        {
            "titulo": "Bio-Recuperación de Suelos Mineros",
            "estado": "En Proceso",
            "descripcion": "Servicio de restauración ecológica utilizando especies nativas y microorganismos para recuperar suelos degradados por la actividad minera a cielo abierto.",
            "capital_requerido": "$30.000.000",
            "tipo_apoyo_buscado": "Capital Semilla",
            "emprendedor": {
                "nombre_completo": "Jorge Esteban Silva",
                "programa_formacion": "Aprendiz SENA - Gestión Ambiental",
                "usuario_id": 997
            }
        },
        {
            "titulo": "Automatización de Ventilación Minera",
            "estado": "En Revisión",
            "descripcion": "Desarrollo de un sistema automatizado de ventilación bajo demanda que reduce el consumo energético en un 40% y mejora la calidad del aire.",
            "capital_requerido": "$80.000.000",
            "tipo_apoyo_buscado": "Socio Industrial",
            "emprendedor": {
                "nombre_completo": "Luisa Fernanda Torres",
                "programa_formacion": "Aprendiz SENA - Electromecánica",
                "usuario_id": 996
            }
        },
        {
            "titulo": "Seguridad Aumentada con IA",
            "estado": "Nuevo",
            "descripcion": "Uso de cámaras con visión artificial para detectar EPPs y zonas de riesgo en tiempo real, enviando alertas a los supervisores.",
            "capital_requerido": "$65.000.000",
            "tipo_apoyo_buscado": "Validación Técnica",
            "emprendedor": {
                "nombre_completo": "Mateo Gómez",
                "programa_formacion": "Aprendiz SENA - Desarrollo de Software",
                "usuario_id": 995
            }
        },
        {
            "titulo": "Transformación de Residuos en Adoquines",
            "estado": "Aprobado",
            "descripcion": "Proyecto de economía circular que aprovecha los estériles de mina para fabricar materiales de construcción de bajo costo y alta resistencia.",
            "capital_requerido": "$55.000.000",
            "tipo_apoyo_buscado": "Maquinaria",
            "emprendedor": {
                "nombre_completo": "Sofia Vargas",
                "programa_formacion": "Aprendiz SENA - Construcción",
                "usuario_id": 994
            }
        }
    ]

    # Combinar proyectos reales con los dummy para la vista
    # Convertimos los objetos SQLAlchemy a dicts o usamos una lista mixta si Jinja lo soporta (Jinja soporta ambos)
    # Para consistencia visual, mostramos ambos.
    
    todos_los_proyectos = list(proyectos_bd) + dummy_projects

    stats = {
        "capital_total": "$1.2B COP", 
        "activos": len(todos_los_proyectos),
        "aliados": 15
    }
    return render_template('Empresario-proyectos.html', projects=todos_los_proyectos, stats=stats)

@app.route('/Empresario-convocatorias')
def empresario_convocatorias():
    # Los empresarios VEN convocatorias (que crean las instituciones)
    convocatorias_bd = InstitucionConvocatoria.query.filter_by(estado='Abierta').all()
    return render_template('Empresario-convocatorias.html', convocatorias=convocatorias_bd)

@app.route('/Empresario-convocatorias/postular', methods=['POST'])
def empresario_convocatorias_postular():
    try:
        data = request.get_json()
        convocatoria_id = data.get('convocatoria_id')
        nombre_proyecto = data.get('nombre_proyecto')
        descripcion = data.get('descripcion')

        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': 'No autorizado'}), 401
            
        usuario = db.session.get(Usuario, user_id)
        if not usuario or not hasattr(usuario, 'empresario') or not usuario.empresario:
            return jsonify({'success': False, 'message': 'Solo empresarios pueden postularse'}), 403

        if not convocatoria_id or not nombre_proyecto or not descripcion:
             return jsonify({'success': False, 'message': 'Faltan datos'}), 400

        nueva_postulacion = ConvocatoriaPostulacion(
            convocatoria_id=convocatoria_id,
            empresario_id=usuario.empresario.id,
            nombre_proyecto=nombre_proyecto,
            descripcion=descripcion
        )
        db.session.add(nueva_postulacion)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Postulación enviada exitosamente'})

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error en postulación: {str(e)}")
        return jsonify({'success': False, 'message': 'Ocurrió un error al procesar la solicitud'}), 500

@app.route('/Empresario-diagnostico', methods=['GET', 'POST'])
def empresario_diagnostico():
    user_id = session.get('user_id')
    usuario = db.session.get(Usuario, user_id)

    if request.method == 'POST':
        try:
            data = request.get_json()
            if usuario and usuario.empresario:
                nuevo_diag = EmpresarioDiagnostico(
                    empresario_id=usuario.empresario.id,
                    tipo=data.get('tipo_diagnostico'),
                    respuestas=data.get('respuestas'),
                    puntaje_global=data.get('puntaje_global')
                )
                db.session.add(nuevo_diag)
                db.session.commit()
                return jsonify({'success': True, 'message': 'Guardado'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

    diagnosticos_data = {
        'actividades': None,
        'competitividad': None
    }
    
    if usuario and hasattr(usuario, 'empresario') and usuario.empresario:
        ultimo_act = EmpresarioDiagnostico.query.filter_by(
            empresario_id=usuario.empresario.id, tipo='actividades'
        ).order_by(EmpresarioDiagnostico.fecha.desc()).first()
        
        if ultimo_act:
            diagnosticos_data['actividades'] = {
                'puntaje_global': ultimo_act.puntaje_global,
                'respuestas': ultimo_act.respuestas
            }
            
        ultimo_comp = EmpresarioDiagnostico.query.filter_by(
            empresario_id=usuario.empresario.id, tipo='competitividad'
        ).order_by(EmpresarioDiagnostico.fecha.desc()).first()
        
        if ultimo_comp:
            diagnosticos_data['competitividad'] = {
                'puntaje_global': ultimo_comp.puntaje_global,
                'respuestas': ultimo_comp.respuestas
            }

    return render_template('Empresario-diagnostico.html', diagnosticos_previos=diagnosticos_data)

@app.route('/Empresario-discusiones/editar/<int:id>', methods=['POST'])
def editar_discusion(id):
    try:
        discusion = db.session.get(EmpresarioDiscusion, id)
        if discusion:
            discusion.titulo = request.form.get('titulo_nuevo')
            discusion.categoria = request.form.get('categoria')
            discusion.contenido = request.form.get('descripcion')
            db.session.commit()
            flash('Discusión actualizada', 'success')
    except Exception as e:
        db.session.rollback()
        app.logger.error(e)
    return redirect(url_for('empresario_discusiones'))

@app.route('/Empresario-discusiones/eliminar/<int:id>', methods=['POST'])
def eliminar_discusion(id):
    try:
        discusion = db.session.get(EmpresarioDiscusion, id)
        if discusion:
            db.session.delete(discusion)
            db.session.commit()
            flash('Discusión eliminada', 'success')
    except Exception as e:
        db.session.rollback()
        app.logger.error(e)
    return redirect(url_for('empresario_discusiones'))

@app.route('/Empresario-discusiones/comentar', methods=['POST'])
def responder_discusion():
    try:
        data = request.get_json()
        discusion_id = data.get('discusion_id')
        contenido = data.get('contenido')
        user_id = session.get('user_id')

        if not user_id:
             return jsonify({'success': False, 'message': 'No autorizado'}), 401

        if not discusion_id or not contenido:
            return jsonify({'success': False, 'message': 'Datos incompletos'}), 400

        nuevo_comentario = Comentario(
            discusion_id=discusion_id,
            usuario_id=user_id,
            contenido=contenido
        )
        db.session.add(nuevo_comentario)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Comentario agregado', 'data': nuevo_comentario.to_dict})

    except Exception as e:
        app.logger.error(e)
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/Empresario-discusiones', methods=['GET', 'POST'])
def empresario_discusiones():
    if request.method == 'POST':
        if 'titulo_nuevo' in request.form:
            try:
                user_id = session.get('user_id')
                if user_id:
                    nueva_discusion = EmpresarioDiscusion(
                        usuario_id=user_id,
                        titulo=request.form.get('titulo_nuevo'),
                        categoria=request.form.get('categoria'),
                        contenido=request.form.get('descripcion')
                    )
                    db.session.add(nueva_discusion)
                    db.session.commit()
                    flash('Discusión creada', 'success')
                return redirect(url_for('empresario_discusiones'))
            except Exception as e:
                app.logger.error(e)

    # LEER DISCUSIONES
    discusiones_bd = EmpresarioDiscusion.query.order_by(EmpresarioDiscusion.fecha_creacion.desc()).all()
    # Pre-renderizar a dict para evitar errores en Jinja
    discusiones_data = [d.to_dict for d in discusiones_bd]
    
    return render_template('Empresario-discusiones.html', discusiones=discusiones_bd, discusiones_data=discusiones_data)


@app.route('/Empresario-mensajes', methods=['GET'])
def empresario_mensajes():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('Principal'))
    
    chat_with_id = request.args.get('chat_with')
    target_user = None

    # Obtener TODOS los mensajes de AMBAS tablas donde participa este usuario
    # 1. Mensajes entre Empresarios
    msgs_emp = EmpresarioMensaje.query.filter(
        ((EmpresarioMensaje.remitente_id == user_id) & (EmpresarioMensaje.eliminado_por_remitente == False)) | 
        ((EmpresarioMensaje.destinatario_id == user_id) & (EmpresarioMensaje.eliminado_por_destinatario == False))
    ).all()

    # 2. Mensajes con Instituciones (por si el empresario chatea con una institución)
    msgs_inst = InstitucionMensaje.query.filter(
        ((InstitucionMensaje.remitente_id == user_id) & (InstitucionMensaje.eliminado_por_remitente == False)) | 
        ((InstitucionMensaje.destinatario_id == user_id) & (InstitucionMensaje.eliminado_por_destinatario == False))
    ).all()

    # Combinar y ordenar por fecha (el más reciente primero para la barra lateral)
    all_messages = msgs_emp + msgs_inst
    all_messages.sort(key=lambda x: x.fecha_envio if x.fecha_envio else datetime.min, reverse=True)

    recent_chats_map = {}
    for msg in all_messages:
        # Determinar quién es la "otra" persona involucrada en el mensaje
        other_id = msg.destinatario_id if msg.remitente_id == user_id else msg.remitente_id
        
        # Solo se necesita el usuario válido y el Último mensaje por cada conversación (uno por usuario)
        if other_id and other_id not in recent_chats_map:
            usuario_otro = db.session.get(Usuario, other_id)
            if usuario_otro:
                perfil = usuario_otro.get_perfil()
                nombre = "Usuario"
                status = "Empresario"
                if hasattr(perfil, 'nombre_empresa'): 
                    nombre = perfil.nombre_empresa
                    status = "Empresa"
                elif hasattr(perfil, 'nombre_completo'): 
                    nombre = perfil.nombre_completo
                elif hasattr(perfil, 'nombre_institucion'):
                    nombre = perfil.nombre_institucion
                    status = "Institución"
                
                recent_chats_map[other_id] = {
                    'id': other_id,
                    'nombre': nombre,
                    'last_msg': msg.contenido,
                    'status': status
                }

    recent_chats = list(recent_chats_map.values())

    # Lógica para el chat específico seleccionado en la barra lateral
    if chat_with_id:
        chat_with_id = int(chat_with_id)
        # Si el usuario solicitado ya está en nuestros chats recientes, usar ese dato. Si no, buscarlo en DB.
        if chat_with_id in recent_chats_map:
            target_user = recent_chats_map[chat_with_id]
        else:
            usuario_destino = db.session.get(Usuario, chat_with_id)
            if usuario_destino:
                perfil = usuario_destino.get_perfil()
                nombre = "Usuario"
                status = "Empresario"
                if hasattr(perfil, 'nombre_empresa'): 
                    nombre = perfil.nombre_empresa
                    status = "Empresa"
                elif hasattr(perfil, 'nombre_completo'): 
                    nombre = perfil.nombre_completo
                elif hasattr(perfil, 'nombre_institucion'):
                    nombre = perfil.nombre_institucion
                    status = "Institución"
                
                target_user = {
                    'id': usuario_destino.id,
                    'nombre': nombre,
                    'status': status
                }

    # Obtener solo los mensajes del chat activo actualmente
    mensajes_data = []
    if chat_with_id:
        chat_with_id = int(chat_with_id)
        # Filtrar para este chat particular
        mensajes_filtrados = [
            m for m in all_messages 
            if m.remitente_id == chat_with_id or m.destinatario_id == chat_with_id
        ]
        # Ordenar cronológicamente (de más antiguo a más reciente) para mostrarlos en pantalla
        mensajes_filtrados.sort(key=lambda x: x.fecha_envio if x.fecha_envio else datetime.min)
        
        mensajes_data = [m.to_dict for m in mensajes_filtrados]
    
    return render_template('Empresario-mensajes.html', mensajes=mensajes_data, target_user=target_user, recent_chats=recent_chats)

@app.route('/Empresario-mensajes/eliminar', methods=['POST'])
def eliminar_conversacion_empresario():
    try:
        data = request.get_json()
        target_id = data.get('target_id')
        user_id = session.get('user_id')
        
        if not user_id or not target_id:
            return jsonify({'success': False, 'message': 'Datos faltantes'}), 400

        # Eliminar de EmpresarioMensaje
        EmpresarioMensaje.query.filter(
            (EmpresarioMensaje.remitente_id == user_id) & (EmpresarioMensaje.destinatario_id == target_id)
        ).update({'eliminado_por_remitente': True}, synchronize_session=False)

        EmpresarioMensaje.query.filter(
            (EmpresarioMensaje.destinatario_id == user_id) & (EmpresarioMensaje.remitente_id == target_id)
        ).update({'eliminado_por_destinatario': True}, synchronize_session=False)

        # Eliminar de InstitucionMensaje
        InstitucionMensaje.query.filter(
            (InstitucionMensaje.remitente_id == user_id) & (InstitucionMensaje.destinatario_id == target_id)
        ).update({'eliminado_por_remitente': True}, synchronize_session=False)

        InstitucionMensaje.query.filter(
            (InstitucionMensaje.destinatario_id == user_id) & (InstitucionMensaje.remitente_id == target_id)
        ).update({'eliminado_por_destinatario': True}, synchronize_session=False)

        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        app.logger.error(e)
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/Institucion-mensajes/eliminar', methods=['POST'])
def eliminar_conversacion_institucion():
    try:
        data = request.get_json()
        target_id = data.get('target_id')
        user_id = session.get('user_id')
        
        if not user_id or not target_id:
            return jsonify({'success': False, 'message': 'Datos faltantes'}), 400

        # Eliminar de InstitucionMensaje
        InstitucionMensaje.query.filter(
            (InstitucionMensaje.remitente_id == user_id) & (InstitucionMensaje.destinatario_id == target_id)
        ).update({'eliminado_por_remitente': True}, synchronize_session=False)

        InstitucionMensaje.query.filter(
            (InstitucionMensaje.destinatario_id == user_id) & (InstitucionMensaje.remitente_id == target_id)
        ).update({'eliminado_por_destinatario': True}, synchronize_session=False)

        # Eliminar de EmpresarioMensaje
        EmpresarioMensaje.query.filter(
            (EmpresarioMensaje.remitente_id == user_id) & (EmpresarioMensaje.destinatario_id == target_id)
        ).update({'eliminado_por_remitente': True}, synchronize_session=False)

        EmpresarioMensaje.query.filter(
            (EmpresarioMensaje.destinatario_id == user_id) & (EmpresarioMensaje.remitente_id == target_id)
        ).update({'eliminado_por_destinatario': True}, synchronize_session=False)

        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        app.logger.error(e)
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/Empresario-mensajes/enviar', methods=['POST'])
def enviar_mensaje():
    try:
        data = request.get_json()
        contenido = data.get('texto')
        destinatario_id = data.get('destinatario_id') # Puede ser None por ahora

        user_id = session.get('user_id')
        if user_id and contenido:
            nuevo_mensaje = EmpresarioMensaje(
                remitente_id=user_id,
                destinatario_id=destinatario_id,
                contenido=contenido
            )
            db.session.add(nuevo_mensaje)
            db.session.commit()
            
            # Emitir evento socket para real-time
            socketio.emit('mensaje_recibido', nuevo_mensaje.to_dict)

            return jsonify({'success': True, 'message': 'Mensaje enviado', 'data': nuevo_mensaje.to_dict})
        
        return jsonify({'success': False, 'message': 'Datos inválidos'}), 400
    except Exception as e:
        app.logger.error(e)
        return jsonify({'success': False, 'message': str(e)}), 500


        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/Institucion-mensajes', methods=['GET'])
def institucion_mensajes():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('Principal'))
    
    chat_with_id = request.args.get('chat_with')
    target_user = None

    # Obtener TODOS los mensajes de AMBAS tablas donde participa este usuario
    # 1. Mensajes de tipo Institución (cuando la institución escribe o recibe de alguien)
    msgs_inst = InstitucionMensaje.query.filter(
        ((InstitucionMensaje.remitente_id == user_id) & (InstitucionMensaje.eliminado_por_remitente == False)) | 
        ((InstitucionMensaje.destinatario_id == user_id) & (InstitucionMensaje.eliminado_por_destinatario == False))
    ).all()

    # 2. Mensajes de tipo Empresario (cuando un empresario le escribe a la institución)
    msgs_emp = EmpresarioMensaje.query.filter(
        ((EmpresarioMensaje.remitente_id == user_id) & (EmpresarioMensaje.eliminado_por_remitente == False)) | 
        ((EmpresarioMensaje.destinatario_id == user_id) & (EmpresarioMensaje.eliminado_por_destinatario == False))
    ).all()

    # Combinar y ordenar por fecha (más reciente primero)
    all_messages = msgs_inst + msgs_emp
    all_messages.sort(key=lambda x: x.fecha_envio, reverse=True)

    # Agrupar mensajes por interlocutor (para mostrar en la barra lateral de chats recientes)
    recent_chats_map = {}
    for msg in all_messages:
        other_id = msg.destinatario_id if msg.remitente_id == user_id else msg.remitente_id
        
        if other_id and other_id not in recent_chats_map:
            usuario_otro = db.session.get(Usuario, other_id)
            if usuario_otro:
                perfil = usuario_otro.get_perfil()
                nombre = "Usuario"
                status = "Empresario"
                # Determinar el nombre y rol del interlocutor dinámicamente
                if hasattr(perfil, 'nombre_empresa'): 
                    nombre = perfil.nombre_empresa
                    status = "Empresa"
                elif hasattr(perfil, 'nombre_completo'): # Empresario o Persona Natural
                    nombre = perfil.nombre_completo
                elif hasattr(perfil, 'nombre_institucion'): # En caso de que otra institución escriba
                   nombre = perfil.nombre_institucion
                   status = "Institución"
                
                recent_chats_map[other_id] = {
                    'id': other_id,
                    'nombre': nombre,
                    'last_msg': msg.contenido,
                    'time': msg.fecha_envio.strftime('%H:%M') if msg.fecha_envio else '',
                    'status': status,
                    'initials': nombre[:2].upper()
                }

    recent_chats = list(recent_chats_map.values())

    # Lógica para el chat específico seleccionado en la barra lateral
    if chat_with_id:
        chat_with_id = int(chat_with_id)
        if chat_with_id in recent_chats_map:
            target_user = recent_chats_map[chat_with_id]
        else:
             # Caso de un chat nuevo o iniciado desde otro módulo
            usuario_destino = db.session.get(Usuario, chat_with_id)
            if usuario_destino:
                perfil = usuario_destino.get_perfil()
                nombre = "Usuario"
                status = "Empresario"
                if hasattr(perfil, 'nombre_empresa'): 
                    nombre = perfil.nombre_empresa
                    status = "Empresa"
                elif hasattr(perfil, 'nombre_completo'): 
                     nombre = perfil.nombre_completo

                target_user = {
                    'id': chat_with_id,
                    'nombre': nombre,
                    'status': status,
                    'initials': nombre[:2].upper(),
                    'last_msg': '', 
                    'time': ''
                }


    mensajes_data = []
    if chat_with_id:
        chat_with_id = int(chat_with_id)
        # Filtrar solo mensajes de ESTA conversación
        mensajes_filtrados = [
            m for m in all_messages 
            if m.remitente_id == chat_with_id or m.destinatario_id == chat_with_id
        ]
        # Ordenar Cronológicamente (Ascendente: Antiguo -> Nuevo)
        mensajes_filtrados.sort(key=lambda x: x.fecha_envio)
        
        mensajes_data = [m.to_dict for m in mensajes_filtrados]
    
    return render_template('Institucion-mensajes.html', mensajes=mensajes_data, recent_chats=recent_chats, target_user=target_user)

@app.route('/Institucion-mensajes/enviar', methods=['POST'])
def enviar_mensaje_institucion():
    print("--- [POST] /Institucion-mensajes/enviar llamado ---") # DEPURACIÓN
    if 'user_id' not in session:
        print("Error: No hay user_id en la sesión")
        return jsonify({'success': False, 'message': 'No autorizado'}), 401

    try:
        data = request.get_json()
        print(f"[DEBUG] Payload recibido: {data}") # DEPURACIÓN
        
        destinatario_id = data.get('destinatario_id')
        texto = data.get('texto')

        if not destinatario_id or not texto:
            print("Error: Faltan destinatario_id o texto en el payload")
            return jsonify({'success': False, 'message': 'Datos incompletos'}), 400

        # Convertir a entero para mayor seguridad
        destinatario_id = int(destinatario_id)
        current_user_id = int(session['user_id'])

        usuario_dest = db.session.get(Usuario, destinatario_id)
        if not usuario_dest:
             print(f"Error: El usuario {destinatario_id} no fue encontrado en la base de datos")
             return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

        print(f"[INFO] Tipo de perfil del destinatario: {usuario_dest.tipo_perfil}")

        nuevo_mensaje = None
        
        # Validar el tipo de Enum o String para mayor robustez entre entornos
        is_empresario = False
        if isinstance(usuario_dest.tipo_perfil, TipoPerfil):
            is_empresario = (usuario_dest.tipo_perfil == TipoPerfil.EMPRESARIO)
        else:
            # Alternativa si el valor está almacenado como string (poco probable con SQLAlchemy Enum)
            is_empresario = (str(usuario_dest.tipo_perfil).lower() == 'empresario')
        
        if is_empresario:
             print("[INFO] Guardando mensaje en tabla EmpresarioMensaje")
             nuevo_mensaje = EmpresarioMensaje(
                remitente_id=current_user_id,
                destinatario_id=destinatario_id,
                contenido=texto
            )
        else:
            print("[INFO] Guardando mensaje en tabla InstitucionMensaje (Por defecto)")
            nuevo_mensaje = InstitucionMensaje(
                remitente_id=current_user_id,
                destinatario_id=destinatario_id,
                contenido=texto
            )

        db.session.add(nuevo_mensaje)
        db.session.commit()
        print("[INFO] Mensaje guardado exitosamente en la base de datos")
        
        # Emitir evento socket para real-time
        socketio.emit('mensaje_recibido', nuevo_mensaje.to_dict)
        
        return jsonify({'success': True, 'data': nuevo_mensaje.to_dict})

    except Exception as e:
        db.session.rollback()
        print(f"!!! ERROR CRÍTICO al enviar el mensaje: {e}")
        import traceback
        traceback.print_exc() # Imprimir el stack trace completo en la terminal para depurar
        return jsonify({'success': False, 'message': str(e)}), 500

# ==========================================
# RUTAS DE INSTITUCIÓN (CONECTADAS A LA BD REAL)
# ==========================================

@app.route('/Institucion-inicio')
def institucion_inicio():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('Principal'))
    
    usuario = db.session.get(Usuario, user_id)
    if not usuario or not usuario.institucion:
        return redirect(url_for('Principal'))

    # Unificar todas las publicaciones para el dashboard
    publicaciones = []

    # 1. Convocatorias
    convs = InstitucionConvocatoria.query.filter_by(institucion_id=usuario.institucion.id).all()
    for c in convs:
        publicaciones.append({
            'titulo': c.titulo,
            'tipo': 'Convocatoria',
            'tipo_class': 'primary', # Para el badge
            'icon': 'campaign',
            'titulo': c.titulo,
            'tipo': 'Convocatoria',
            'tipo_class': 'primary', # Para el badge
            'icon': 'campaign',
            'fecha': formato_fecha_es(c.fecha_cierre) if c.fecha_cierre else 'N/A',
            'estado': c.estado,
            'estado': c.estado,
            'estado_class': 'success' if c.estado == 'Abierta' else 'gray-500',
            'edit_url': f'/Institucion-convocatorias/editar/{c.id}',
            'delete_url': f'/Institucion-convocatorias/eliminar/{c.id}' # Asumiendo ruta
        })

    # 2. Programas
    progs = InstitucionPrograma.query.filter_by(institucion_id=usuario.institucion.id).all()
    for p in progs:
        publicaciones.append({
            'titulo': p.nombre,
            'tipo': 'Programa',
            'tipo_class': 'accent',
            'icon': 'school',
            'fecha': 'Permanente',
            'estado': p.estado,
            'estado_class': 'success' if 'Abierta' in p.estado else 'warning',
            'edit_url': f'/Institucion-programas/editar/{p.id}',
            'delete_url': f'/Institucion-programas/eliminar/{p.id}'
        })

    # 3. Noticias
    news = InstitucionNoticia.query.filter_by(institucion_id=usuario.institucion.id).all()
    for n in news:
        publicaciones.append({
            'titulo': n.titulo,
            'tipo': 'Noticia',
            'tipo_class': 'blue-600', # Ajuste manual o usar n.categoria_bg
            'icon': 'article',
            'titulo': n.titulo,
            'tipo': 'Noticia',
            'tipo_class': 'blue-600', # Ajuste manual o usar n.categoria_bg
            'icon': 'article',
            'fecha': formato_fecha_es(n.fecha_publicacion),
            'estado': 'Publicada',
            'estado': 'Publicada',
            'estado_class': 'success',
            'edit_url': f'/Institucion-noticias/editar/{n.id}',
            'delete_url': f'/Institucion-noticias/eliminar/{n.id}'
        })

    # Ordenar por fecha (simulada/real) o simplemente mezclar
    # Por simplicidad, las dejamos en orden de inserción o podríamos ordenarlas
    
    return render_template('Institucion-inicio.html', publicaciones=publicaciones)

@app.route('/Institucion/config/update_photo', methods=['POST'])
def update_institucion_photo():
    data = request.get_json()
    photo_url = data.get('photo_url')
    if photo_url:
        session['profile_image'] = photo_url
        return jsonify({'success': True, 'message': 'Foto actualizada'})
    return jsonify({'success': False, 'message': 'URL no válida'}), 400

@app.route('/Empresario-programas/postular', methods=['POST'])
def postular_programa():
    try:
        data = request.get_json()
        programa_id = data.get('programa_id')
        
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': 'No has iniciado sesión.'}), 401
            
        usuario = db.session.get(Usuario, user_id)
        if not usuario or not usuario.empresario:
            return jsonify({'success': False, 'message': 'Solo los empresarios pueden postularse.'}), 403
            
        if not programa_id:
            return jsonify({'success': False, 'message': 'Datos incompletos.'}), 400
            
        # Verificar si ya está inscrito
        postulacion_existente = ProgramaPostulacion.query.filter_by(
            programa_id=programa_id,
            empresario_id=usuario.empresario.id
        ).first()
        
        if postulacion_existente:
             return jsonify({'success': False, 'message': 'Ya estás inscrito en este programa.'}), 400
             
        # Guardar en BD
        nueva_postulacion = ProgramaPostulacion(
            programa_id=programa_id,
            empresario_id=usuario.empresario.id
        )
        db.session.add(nueva_postulacion)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Te has inscrito al programa correctamente.'})
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error al postular a programa: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor.'}), 500

@app.route('/Institucion-programas', methods=['GET', 'POST'])
def institucion_programas():
    if request.method == 'POST':
        try:
            user_id = session.get('user_id')
            usuario = db.session.get(Usuario, user_id)
            
            if usuario and usuario.institucion:
                nuevo_programa = InstitucionPrograma(
                    institucion_id=usuario.institucion.id,
                    nombre=request.form.get('nombre'),
                    descripcion=request.form.get('descripcion'),
                    modalidad=request.form.get('modalidad'),
                    duracion=request.form.get('duracion'),
                    cupos_totales=int(request.form.get('cupos', 30))
                )
                db.session.add(nuevo_programa)
                db.session.commit()
                flash('Programa creado', 'success')
            return redirect(url_for('institucion_programas'))
        except Exception as e:
            app.logger.error(e)

    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('Principal'))
    
    usuario = db.session.get(Usuario, user_id)
    if not usuario or not usuario.institucion:
        return redirect(url_for('Principal'))

    programas_bd = InstitucionPrograma.query.filter_by(institucion_id=usuario.institucion.id).all()
    return render_template('Institucion-programas.html', programas=programas_bd)

@app.route('/Institucion-convocatorias', methods=['GET', 'POST'])
def institucion_convocatorias():
    if request.method == 'POST':
        if 'titulo' in request.form:
            try:
                user_id = session.get('user_id')
                usuario = db.session.get(Usuario, user_id)
                
                if usuario and usuario.institucion:
                    # Parsear la fecha del formulario
                    fecha_cierre = datetime.strptime(request.form.get('fecha_limite'), '%Y-%m-%d')
                    
                    nueva_convocatoria = InstitucionConvocatoria(
                        institucion_id=usuario.institucion.id,
                        titulo=request.form.get('titulo'),
                        descripcion=request.form.get('descripcion'),
                        requisitos=request.form.get('requisitos'),
                        fecha_cierre=fecha_cierre,
                        publico_objetivo=",".join(request.form.getlist('publico'))
                    )
                    db.session.add(nueva_convocatoria)
                    db.session.commit()
                    flash('Convocatoria creada', 'success')
                return redirect(url_for('institucion_convocatorias'))
            except Exception as e:
                app.logger.error(e)
                flash('Error al crear', 'danger')

    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('Principal'))
    
    usuario = db.session.get(Usuario, user_id)
    if not usuario or not usuario.institucion:
        return redirect(url_for('Principal'))

    convocatorias_bd = InstitucionConvocatoria.query.filter_by(institucion_id=usuario.institucion.id).all()
    return render_template('Institucion-convocatorias.html', convocatorias=convocatorias_bd)

@app.route('/Institucion-noticias', methods=['GET', 'POST'])
def institucion_noticias():
    if request.method == 'POST':
        try:
            user_id = session.get('user_id')
            usuario = db.session.get(Usuario, user_id)
            
            # Si el usuario es institución, obtenemos su ID
            inst_id = usuario.institucion.id if (usuario and usuario.institucion) else None
            
            if inst_id:
                today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                today_end = today_start + timedelta(days=1)
                news_count = InstitucionNoticia.query.filter(
                    InstitucionNoticia.institucion_id == inst_id,
                    InstitucionNoticia.fecha_publicacion >= today_start,
                    InstitucionNoticia.fecha_publicacion < today_end
                ).count()
                
                if news_count >= 3:
                    flash('Has alcanzado el límite de 3 noticias por día. Intenta de nuevo mañana.', 'danger')
                    return redirect(url_for('institucion_noticias'))
            
            nueva_noticia = InstitucionNoticia(
                institucion_id=inst_id,
                titulo=request.form.get('titulo'),
                categoria=request.form.get('categoria'),
                contenido=request.form.get('contenido'),
                imagen_url=request.form.get('imagen_url') or "https://via.placeholder.com/500x300"
            )
            db.session.add(nueva_noticia)
            db.session.commit()
            flash('Noticia publicada', 'success')
            return redirect(url_for('institucion_noticias'))
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)

    user_id = session.get('user_id')
    usuario = db.session.get(Usuario, user_id)
    inst_id = usuario.institucion.id if (usuario and usuario.institucion) else None
    
    if not inst_id:
         # Si no es institución, mostrar vacío o redirigir (en dashboard solo debería entrar institución)
         noticias_bd = []
    else:
        noticias_bd = InstitucionNoticia.query.filter_by(institucion_id=inst_id).order_by(InstitucionNoticia.fecha_publicacion.desc()).all()

    return render_template('Institucion-noticias.html', noticias=noticias_bd)

@app.route('/Institucion-noticias/editar/<int:id>', methods=['POST'])
def editar_noticia(id):
    try:
        noticia = db.session.get(InstitucionNoticia, id)
        if noticia:
            noticia.titulo = request.form.get('titulo')
            noticia.categoria = request.form.get('categoria')
            noticia.contenido = request.form.get('contenido')
            if request.form.get('imagen_url'):
                noticia.imagen_url = request.form.get('imagen_url')
            
            db.session.commit()
            flash('Noticia actualizada', 'success')
    except Exception as e:
        db.session.rollback()
        app.logger.error(e)
    return redirect(url_for('institucion_noticias'))

@app.route('/Institucion-noticias/eliminar/<int:id>', methods=['POST'])
def eliminar_noticia(id):
    noticia = db.session.get(InstitucionNoticia, id)
    if noticia:
        db.session.delete(noticia)
        db.session.commit()
        flash('Noticia eliminada', 'success')
    return redirect(url_for('institucion_noticias'))

@app.route('/Institucion-convocatorias/editar/<int:id>', methods=['POST'])
def editar_convocatoria(id):
    try:
        convocatoria = db.session.get(InstitucionConvocatoria, id)
        if convocatoria:
            convocatoria.titulo = request.form.get('titulo')
            convocatoria.descripcion = request.form.get('descripcion')
            # Parsear fecha
            if request.form.get('fecha_limite'):
                convocatoria.fecha_cierre = datetime.strptime(request.form.get('fecha_limite'), '%Y-%m-%d')
            
            # Parsear checkboxes
            convocatoria.publico_objetivo = ",".join(request.form.getlist('publico'))

            db.session.commit()
            flash('Convocatoria actualizada', 'success')
    except Exception as e:
        db.session.rollback()
        app.logger.error(e)
    return redirect(url_for('institucion_convocatorias'))

@app.route('/Institucion-convocatorias/eliminar/<int:id>', methods=['POST'])
def eliminar_convocatoria(id):
    convocatoria = db.session.get(InstitucionConvocatoria, id)
    if convocatoria:
        db.session.delete(convocatoria)
        db.session.commit()
        flash('Convocatoria eliminada', 'success')
    return redirect(url_for('institucion_convocatorias'))

@app.route('/Institucion-programas/editar/<int:id>', methods=['POST'])
def editar_programa(id):
    try:
        programa = db.session.get(InstitucionPrograma, id)
        if programa:
            programa.nombre = request.form.get('nombre')
            programa.modalidad = request.form.get('modalidad')
            programa.duracion = request.form.get('duracion')
            programa.cupos_totales = int(request.form.get('cupos', 0))
            
            db.session.commit()
            flash('Programa actualizado', 'success')
    except Exception as e:
        db.session.rollback()
        app.logger.error(e)
    return redirect(url_for('institucion_programas'))

@app.route('/Institucion-programas/eliminar/<int:id>', methods=['POST'])
def eliminar_programa(id):
    programa = db.session.get(InstitucionPrograma, id)
    if programa:
        db.session.delete(programa)
        db.session.commit()
        flash('Programa eliminado', 'success')
    return redirect(url_for('institucion_programas'))

# --- CHAT ---
# @app.route('/Empresario-mensajes') -> MOVIDO ARRIBA
# def chat():
#     return render_template('Empresario-mensajes.html')

@app.route('/respuesta')
def respuesta():
    return render_template('respuesta.html')

@socketio.on('nuevo_mensaje')
def manejar_mensaje(data):
    emit('mensaje_recibido', data, broadcast=True)

# --- Comandos de Línea de Comandos (CLI) ---
@app.cli.command("create-superuser")
@click.argument("email")
@click.argument("password")
def create_superuser(email, password):
    if db.session.execute(db.select(Usuario).filter_by(email=email)).first():
        print("Usuario ya existe.")
        return
    try:
        admin_user = Usuario(email=email, tipo_perfil=TipoPerfil.ADMIN, is_admin=True, activo=True)
        admin_user.set_password(password)
        db.session.add(admin_user)
        db.session.commit()
        print("✅ Superusuario creado.")
    except Exception as e:
        print(f"Error: {e}")

@app.cli.command("delete-user")
@click.argument("email")
def delete_user(email):
    usuario = db.session.execute(db.select(Usuario).filter_by(email=email)).scalar_one_or_none()
    if not usuario:
        print("Usuario no encontrado.")
        return
    try:
        db.session.delete(usuario)
        db.session.commit()
        print("✅ Usuario eliminado.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    socketio.run(app, port=84, debug=True)