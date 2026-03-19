# ==========================================
# 1. IMPORTACIONES Y CONFIGURACIÓN (NO TOCAR)
# ==========================================
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from enum import Enum
from extensions import db # Importa la instancia 'db' desde extensions.py
from flask import session

# ==========================================
# 2. SISTEMA DE USUARIOS Y PERFILES (TU CÓDIGO ACTUAL)
# ==========================================

class TipoPerfil(Enum):
    EMPRESARIO = "empresario"
    EMPRENDEDOR = "emprendedor"
    INVERSIONISTA = "inversionista"
    INSTITUCION = "institucion"
    ADMIN = "admin"

class Usuario(db.Model):
    """
    Modelo principal de autenticación. Representa a cualquier usuario registrado en el sistema.
    De este modelo heredan o se vinculan los perfiles específicos (Empresario, Emprendedor, etc.)
    mediante una relación uno a uno.
    """
    __tablename__ = 'usuarios' 

    # Identificador único del usuario
    id = db.Column(db.Integer, primary_key=True)
    # Correo electrónico usado para iniciar sesión
    email = db.Column(db.String(120), unique=True, nullable=False)
    # Contraseña encriptada (hash) por seguridad
    password_hash = db.Column(db.String(200), nullable=False)
    # Rol o tipo de perfil del usuario (determina a qué dashboard tiene acceso)
    tipo_perfil = db.Column(db.Enum(TipoPerfil, native_enum=False), nullable=False)
    # Bandera de administrador para accesos privilegiados
    is_admin = db.Column(db.Boolean, default=False, nullable=False, server_default='false')
    # Bandera para suspender o desactivar cuentas sin borrarlas
    activo = db.Column(db.Boolean, default=True)
    # Auditoría de fechas
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    ultima_conexion = db.Column(db.DateTime)
    
    # --- Relaciones Uno a Uno (One-to-One) con los perfiles específicos ---
    # cascade='all, delete-orphan' asegura que si se borra el Usuario, se borra su perfil asociado
    empresario = db.relationship('Empresario', backref='usuario', uselist=False, cascade='all, delete-orphan')
    emprendedor = db.relationship('Emprendedor', backref='usuario', uselist=False, cascade='all, delete-orphan')
    inversionista = db.relationship('Inversionista', backref='usuario', uselist=False, cascade='all, delete-orphan')
    institucion = db.relationship('Institucion', backref='usuario', uselist=False, cascade='all, delete-orphan')

    # --- Métodos de Ayuda (Helpers) ---
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_perfil(self):
        if self.tipo_perfil == TipoPerfil.EMPRESARIO:
            return self.empresario
        elif self.tipo_perfil == TipoPerfil.EMPRENDEDOR:
            return self.emprendedor
        elif self.tipo_perfil == TipoPerfil.INVERSIONISTA:
            return self.inversionista
        elif self.tipo_perfil == TipoPerfil.INSTITUCION:
            return self.institucion
        elif self.tipo_perfil == TipoPerfil.ADMIN:
            return type('AdminProfile', (), {'nombre_completo': 'Administrador'})()
        return None

    def __repr__(self):
        return f'<Usuario {self.email} - {self.tipo_perfil.value}>'

class Emprendedor(db.Model):
    """
    Modelo del perfil Emprendedor SENA.
    Contiene la información personal y los detalles iniciales de su proyecto en formación.
    """
    __tablename__ = 'emprendedores'

    id = db.Column(db.Integer, primary_key=True)
    # Llave foránea que lo enlaza estrictamente a un único registro en la tabla 'usuarios'
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), unique=True, nullable=False)

    # Datos Personales
    nombre_completo = db.Column(db.String(150), nullable=False)
    tipo_documento = db.Column(db.String(10), nullable=False)
    numero_documento = db.Column(db.String(30), unique=True, nullable=False)
    numero_celular = db.Column(db.String(15), nullable=False)
    
    # Datos Académicos y de Proyecto
    programa_formacion = db.Column(db.String(150), nullable=False)
    titulo_proyecto = db.Column(db.String(150), nullable=False)
    descripcion_proyecto = db.Column(db.Text, nullable=False)
    relacion_sector = db.Column(db.String(250), nullable=False)
    tipo_apoyo = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<Emprendedor {self.nombre_completo}>'

class Empresario(db.Model):
    """
    Modelo del perfil Empresario.
    Almacena tanto la información personal del representante como los datos legales
    y operativos de la empresa minera u organización vinculada.
    """
    __tablename__ = 'empresarios'
    
    id = db.Column(db.Integer, primary_key=True)
    # Vínculo con el usuario base
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), unique=True, nullable=False)
    
    # Datos Personales del Representante
    nombre_completo = db.Column(db.String(150), nullable=False)
    tipo_documento_personal = db.Column(db.String(10), nullable=False)
    numero_documento_personal = db.Column(db.String(30), unique=True, nullable=False)
    numero_celular = db.Column(db.String(15), nullable=False)
    
    # Datos Empresariales / Corporativos
    nombre_empresa = db.Column(db.String(150), nullable=False)
    tipo_contribuyente = db.Column(db.String(20), nullable=False) # ej: persona natural o jurídica
    numero_documento_contribuyente = db.Column(db.String(30), unique=True, nullable=True)
    nit = db.Column(db.String(30), unique=True, nullable=True)
    tamano = db.Column(db.String(20), nullable=False) # ej: Micro, Pequeña, Mediana
    
    # Clasificación Sectorial
    sector_produccion = db.Column(db.String(100), nullable=False)
    sector_transformacion = db.Column(db.String(100), nullable=False)
    sector_comercializacion = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Empresario {self.nombre_empresa}>'

class Inversionista(db.Model):
    """
    Modelo del perfil Inversionista.
    Diseñado para actores privados, fondos o ángeles inversores interesados
    en inyectar capital o recursos en los proyectos de los emprendedores.
    """
    __tablename__ = 'inversionistas'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), unique=True, nullable=False)
    
    nombre_completo = db.Column(db.String(150), nullable=False)
    tipo_documento = db.Column(db.String(10), nullable=False)
    numero_documento = db.Column(db.String(30), unique=True, nullable=False)
    numero_celular = db.Column(db.String(15), nullable=False)
    
    # Perfil Financiero / Intereses
    nombre_fondo = db.Column(db.String(150))
    tipo_inversion = db.Column(db.String(50), nullable=False) # ej: Capital Semilla, Deuda, Equity
    etapas_interes = db.Column(db.String(255)) # Fases del proyecto que les interesan
    areas_interes = db.Column(db.String(255)) # Subsectores mineros o tecnológicos

class Institucion(db.Model):
    """
    Modelo del perfil Institución (ej. Gubernamentales, Universidades, ONG).
    Actores estratégicos que publican Convocatorias, Noticias y Programas de Formación
    para fomentar el desarrollo del ecosistema minero.
    """
    __tablename__ = 'instituciones'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), unique=True, nullable=False)
    
    # Identidad Institucional
    nombre_completo = db.Column(db.String(150), nullable=False)
    nit = db.Column(db.String(30), unique=True, nullable=False)
    tipo_institucion = db.Column(db.String(50), nullable=False)
    municipio = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    area_especializacion = db.Column(db.String(100), nullable=False)
    
    # Modos en los que contribuye al ecosistema (ej: "Financiamiento, Formación")
    participacion_activa = db.Column(db.String(255))

    def __repr__(self):
        return f'<Institucion {self.nombre_completo}>'

# ==========================================
# 3. NUEVAS TABLAS (MODELOS DE DASHBOARDS)
# ==========================================

class EmpresarioMercado(db.Model):
    """Dashboard: Empresario-mercado.html"""
    __tablename__ = 'empresario_mercado'

    id = db.Column(db.Integer, primary_key=True)
    empresario_id = db.Column(db.Integer, db.ForeignKey('empresarios.id', ondelete='CASCADE'), nullable=False)
    
    titulo = db.Column(db.String(150), nullable=False)
    tipo = db.Column(db.String(50), nullable=False) # 'Venta' o 'Alquiler'
    precio = db.Column(db.String(50), nullable=False)
    ubicacion = db.Column(db.String(100), nullable=False)
    imagen_url = db.Column(db.Text, nullable=True)
    fecha_publicacion = db.Column(db.DateTime, default=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)

    empresario = db.relationship('Empresario', backref=db.backref('mercado_items', lazy=True))

    @property
    def celular(self):
        return self.precio
    
    @celular.setter
    def celular(self, value):
        self.precio = value

class EmpresarioAlianza(db.Model):
    """Dashboard: Empresario-alianzas.html"""
    __tablename__ = 'empresario_alianzas'

    id = db.Column(db.Integer, primary_key=True)
    empresario_id = db.Column(db.Integer, db.ForeignKey('empresarios.id', ondelete='CASCADE'), nullable=False)
    
    tipo_oferta = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    ubicacion = db.Column(db.String(100))
    fecha_publicacion = db.Column(db.DateTime, default=datetime.utcnow)

    empresario = db.relationship('Empresario', backref=db.backref('alianzas_items', lazy=True))

    @property
    def tipo(self):
        return self.tipo_oferta

    @property
    def empresa(self):
        return self.empresario.nombre_empresa if self.empresario else "Usuario"

    @property
    def iniciales(self):
        name = self.empresa
        return name[:2].upper() if name else "NN"

    @property
    def color_bg(self):
        colors = ['blue-100', 'green-100', 'purple-100', 'yellow-100', 'red-100']
        return colors[self.id % len(colors)]

    @property
    def color_text(self):
        colors = ['blue-700', 'green-700', 'purple-700', 'yellow-700', 'red-700']
        return colors[self.id % len(colors)]

    @property
    def servicios(self):
        if self.empresario:
            return f"{self.empresario.sector_produccion}, {self.empresario.sector_transformacion}"
        return "General"

    @property
    def certificaciones(self):
        return None  # Placeholder

    @property
    def telefono(self):
        return self.empresario.numero_celular if self.empresario else ""

class InstitucionConvocatoria(db.Model):
    """Dashboard: Institucion-convocatorias.html"""
    __tablename__ = 'institucion_convocatorias'

    id = db.Column(db.Integer, primary_key=True)
    institucion_id = db.Column(db.Integer, db.ForeignKey('instituciones.id', ondelete='CASCADE'), nullable=False)
    
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    requisitos = db.Column(db.Text)
    fecha_cierre = db.Column(db.Date, nullable=False)
    publico_objetivo = db.Column(db.String(100))
    estado = db.Column(db.String(50), default='Abierta')
    
    @property
    def publico(self):
        if self.publico_objetivo:
            return self.publico_objetivo.split(',')
        return []

    institucion = db.relationship('Institucion', backref=db.backref('convocatorias_items', lazy=True))

class ConvocatoriaPostulacion(db.Model):
    """Postulaciones de empresarios a convocatorias"""
    __tablename__ = 'convocatoria_postulaciones'

    id = db.Column(db.Integer, primary_key=True)
    convocatoria_id = db.Column(db.Integer, db.ForeignKey('institucion_convocatorias.id', ondelete='CASCADE'), nullable=False)
    empresario_id = db.Column(db.Integer, db.ForeignKey('empresarios.id', ondelete='CASCADE'), nullable=False)
    
    nombre_proyecto = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    
    fecha_postulacion = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(50), default='Pendiente') 

    convocatoria = db.relationship('InstitucionConvocatoria', backref=db.backref('postulaciones', lazy=True, cascade='all, delete-orphan'))
    empresario = db.relationship('Empresario', backref=db.backref('postulaciones_convocatorias', lazy=True, cascade='all, delete-orphan'))

class InstitucionPrograma(db.Model):
    """Dashboard: Institucion-programas.html"""
    __tablename__ = 'institucion_programas'

    id = db.Column(db.Integer, primary_key=True)
    institucion_id = db.Column(db.Integer, db.ForeignKey('instituciones.id', ondelete='CASCADE'), nullable=False)
    
    nombre = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    modalidad = db.Column(db.String(50), nullable=False)
    duracion = db.Column(db.String(50))
    cupos_totales = db.Column(db.Integer, default=30)
    cupos_ocupados = db.Column(db.Integer, default=0)
    estado = db.Column(db.String(50), default='Inscripciones Abiertas')

    institucion = db.relationship('Institucion', backref=db.backref('programas_items', lazy=True))

class ProgramaPostulacion(db.Model):
    """Inscripciones de empresarios a programas"""
    __tablename__ = 'programa_postulaciones'
    
    id = db.Column(db.Integer, primary_key=True)
    programa_id = db.Column(db.Integer, db.ForeignKey('institucion_programas.id', ondelete='CASCADE'), nullable=False)
    empresario_id = db.Column(db.Integer, db.ForeignKey('empresarios.id', ondelete='CASCADE'), nullable=False)
    
    fecha_postulacion = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(50), default='Inscrito') 
    
    programa = db.relationship('InstitucionPrograma', backref=db.backref('postulaciones', lazy=True, cascade='all, delete-orphan'))
    empresario = db.relationship('Empresario', backref=db.backref('inscripciones_programas', lazy=True, cascade='all, delete-orphan'))


class InstitucionNoticia(db.Model):
    """Dashboard: Institucion-noticias.html"""
    __tablename__ = 'institucion_noticias'

    id = db.Column(db.Integer, primary_key=True)
    institucion_id = db.Column(db.Integer, db.ForeignKey('instituciones.id'), nullable=True)
    
    titulo = db.Column(db.String(200), nullable=False)
    categoria = db.Column(db.String(50))
    contenido = db.Column(db.Text, nullable=False)
    imagen_url = db.Column(db.Text)
    vistas = db.Column(db.Integer, default=0)
    vistas = db.Column(db.Integer, default=0)
    fecha_publicacion = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def fecha(self):
        return self.fecha_publicacion.strftime('%d %b, %Y')

    @property
    def categoria_bg(self):
        colores = {
            'Eventos': 'primary',
            'Normativa': 'danger',
            'Tecnología': 'accent',
            'Sostenibilidad': 'success',
            'General': 'gray-500'
        }
        return colores.get(self.categoria, 'primary')

    institucion = db.relationship('Institucion', backref=db.backref('noticias_items', lazy=True))

class EmprendedorProyecto(db.Model):
    """Dashboard: Empresario-proyecto.html (Creado por Emprendedor)"""
    __tablename__ = 'emprendedor_proyectos'

    id = db.Column(db.Integer, primary_key=True)
    emprendedor_id = db.Column(db.Integer, db.ForeignKey('emprendedores.id', ondelete='CASCADE'), nullable=False)
    
    titulo = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    tipo_apoyo_buscado = db.Column(db.String(100))
    capital_requerido = db.Column(db.String(50))
    estado = db.Column(db.String(50), default='En Revisión') 
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    emprendedor = db.relationship('Emprendedor', backref=db.backref('proyectos_items', lazy=True))

class EmpresarioDiscusion(db.Model):
    """Dashboard: Empresario-discusiones.html"""
    __tablename__ = 'empresario_discusiones'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    
    titulo = db.Column(db.String(200), nullable=False)
    categoria = db.Column(db.String(100))
    contenido = db.Column(db.Text, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    autor = db.relationship('Usuario', backref=db.backref('discusiones_items', lazy=True))
    comentarios = db.relationship('Comentario', backref='discusion', lazy=True, cascade='all, delete-orphan')

    @property
    def fecha_fmt(self):
        return self.fecha_creacion.strftime('%d %b, %Y')

    @property
    def autor_nombre(self):
        # Intentar obtener nombre legible
        if self.autor:
            perfil = self.autor.get_perfil()
            if hasattr(perfil, 'nombre_empresa'):
                return perfil.nombre_empresa
            if hasattr(perfil, 'nombre_completo'):
                return perfil.nombre_completo
            return self.autor.email.split('@')[0]
        return "Anónimo"

    @property
    def iniciales(self):
        nombre = self.autor_nombre
        return nombre[:2].upper() if nombre else "NN"

    @property
    def color_bg(self):
        colors = ['blue-100', 'green-100', 'purple-100', 'yellow-100', 'red-100']
        return colors[self.id % len(colors)]

    @property
    def color_txt(self):
        colors = ['blue-700', 'green-700', 'purple-700', 'yellow-700', 'red-700']
        return colors[self.id % len(colors)]

    @property
    def to_dict(self):
        return {
            "id": self.id,
            "titulo": self.titulo,
            "categoria": self.categoria,
            "autor": self.autor_nombre,
            "fecha": self.fecha_fmt,
            "contenido": self.contenido,
            "iniciales": self.iniciales,
            "color_bg": self.color_bg,
            "color_txt": self.color_txt,
            "comentarios": [c.to_dict for c in self.comentarios],
            "respuestas": len(self.comentarios)
        }

class Comentario(db.Model):
    """Comentarios dentro de discusiones"""
    __tablename__ = 'comentarios'
    id = db.Column(db.Integer, primary_key=True)
    discusion_id = db.Column(db.Integer, db.ForeignKey('empresario_discusiones.id', ondelete='CASCADE'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    fecha_comentario = db.Column(db.DateTime, default=datetime.utcnow)
    autor = db.relationship('Usuario', backref=db.backref('comentarios_items', lazy=True))

    @property
    def to_dict(self):
        nombre = "Anónimo"
        if self.autor:
            perfil = self.autor.get_perfil()
            if hasattr(perfil, 'nombre_empresa'): nombre = perfil.nombre_empresa
            elif hasattr(perfil, 'nombre_completo'): nombre = perfil.nombre_completo
            else: nombre = self.autor.email.split('@')[0]
        
        return {
            "id": self.id,
            "text": self.contenido,
            "user": nombre,
            "date": self.fecha_comentario.strftime('%d %b, %Y')
        }

class EmpresarioDiagnostico(db.Model):
    """
    Tabla para el dashboard: Empresario-diagnostico.html
    Almacena los resultados de los test de competitividad.
    """
    __tablename__ = 'empresario_diagnostico'

    id = db.Column(db.Integer, primary_key=True)
    # Relación: Pertenece a un empresario
    empresario_id = db.Column(db.Integer, db.ForeignKey('empresarios.id', ondelete='CASCADE'), nullable=False)
    
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    tipo = db.Column(db.String(50)) # Ej: 'competitividad', 'madurez_digital'
    
    # IMPORTANTE: Usamos JSON para guardar las respuestas porque son muchas preguntas
    # Postgres soporta esto nativamente.
    respuestas = db.Column(db.JSON) 
    
    puntaje_global = db.Column(db.Float) # Ej: 85.5

    # Relación para acceder desde el usuario
    empresario = db.relationship('Empresario', backref=db.backref('diagnosticos_items', lazy=True))

class EmpresarioMensaje(db.Model):
    """
    Tabla para el dashboard: Empresario-mensajes.html
    Almacena los mensajes simples del chat.
    """
    __tablename__ = 'empresario_mensajes'

    id = db.Column(db.Integer, primary_key=True)
    remitente_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    destinatario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=True) # Null si es mensaje general o a soporte
    
    contenido = db.Column(db.Text, nullable=False)
    fecha_envio = db.Column(db.DateTime, default=datetime.utcnow)
    leido = db.Column(db.Boolean, default=False)
    
    # Tipo de mensaje: 'texto', 'imagen', 'archivo' (aunque por ahora solo texto)
    tipo = db.Column(db.String(50), default='texto')
    eliminado_por_remitente = db.Column(db.Boolean, default=False)
    eliminado_por_destinatario = db.Column(db.Boolean, default=False)

    remitente = db.relationship('Usuario', foreign_keys=[remitente_id], backref=db.backref('mensajes_enviados', lazy=True))
    destinatario = db.relationship('Usuario', foreign_keys=[destinatario_id], backref=db.backref('mensajes_recibidos', lazy=True))

    @property
    def fecha_fmt(self):
        # Formato de hora legible (ej: 10:30 AM)
        return self.fecha_envio.strftime('%I:%M %p')
    
    @property
    def to_dict(self):
        return {
            "id": self.id,
            "remitente_id": self.remitente_id,
            "destinatario_id": self.destinatario_id,
            "contenido": self.contenido,
            "text": self.contenido, # Compatibilidad con versiones anteriores del frontend
            "fecha_envio": (self.fecha_envio.isoformat() + 'Z') if self.fecha_envio else None,
            "time": self.fecha_fmt,
            "type": "outgoing" if self.remitente_id == session.get('user_id') else "incoming"
        }

class InstitucionMensaje(db.Model):
    """
    Tabla para el dashboard: Institucion-mensajes.html
    Almacena los mensajes institucionales.
    """
    __tablename__ = 'instituciones_mensajes'

    id = db.Column(db.Integer, primary_key=True)
    remitente_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    destinatario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=True)
    
    contenido = db.Column(db.Text, nullable=False)
    fecha_envio = db.Column(db.DateTime, default=datetime.utcnow)
    leido = db.Column(db.Boolean, default=False)
    
    tipo = db.Column(db.String(50), default='texto')
    eliminado_por_remitente = db.Column(db.Boolean, default=False)
    eliminado_por_destinatario = db.Column(db.Boolean, default=False)

    remitente = db.relationship('Usuario', foreign_keys=[remitente_id], backref=db.backref('inst_mensajes_enviados', lazy=True))
    destinatario = db.relationship('Usuario', foreign_keys=[destinatario_id], backref=db.backref('inst_mensajes_recibidos', lazy=True))

    @property
    def fecha_fmt(self):
        return self.fecha_envio.strftime('%I:%M %p')
    
    @property
    def to_dict(self):
        return {
            "id": self.id,
            "remitente_id": self.remitente_id,
            "destinatario_id": self.destinatario_id,
            "contenido": self.contenido,
            "text": self.contenido,
            "fecha_envio": (self.fecha_envio.isoformat() + 'Z') if self.fecha_envio else None,
            "time": self.fecha_fmt,
            "type": "outgoing" if self.remitente_id == session.get('user_id') else "incoming"
        }