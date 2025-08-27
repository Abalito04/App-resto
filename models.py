from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import secrets

db = SQLAlchemy()

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    nombre = db.Column(db.String(100), nullable=False)
    es_admin = db.Column(db.Boolean, default=False)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    
    # Relación con restaurante
    restaurante_id = db.Column(db.Integer, db.ForeignKey('restaurante.id'), nullable=False)
    restaurante = db.relationship('Restaurante', backref='usuarios')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Restaurante(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)  # URL amigable
    direccion = db.Column(db.String(200))
    telefono = db.Column(db.String(20))
    email_contacto = db.Column(db.String(120))
    
    # Configuración específica del restaurante
    moneda = db.Column(db.String(10), default="$")
    zona_horaria = db.Column(db.String(50), default="America/Argentina/Buenos_Aires")
    
    # Plan y billing
    plan = db.Column(db.String(20), default="free")  # free, pro, premium
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    activo = db.Column(db.Boolean, default=True)
    
    # API key única por restaurante
    api_key = db.Column(db.String(64), unique=True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.api_key:
            self.api_key = secrets.token_urlsafe(32)

class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    activo = db.Column(db.Boolean, default=True)
    
    # Multitenancy: cada producto pertenece a un restaurante
    restaurante_id = db.Column(db.Integer, db.ForeignKey('restaurante.id'), nullable=False)
    restaurante = db.relationship('Restaurante')

class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mesa = db.Column(db.String(20))
    nombre_cliente = db.Column(db.String(100))
    direccion_cliente = db.Column(db.String(200))
    fecha = db.Column(db.DateTime, default=datetime.now)
    estado = db.Column(db.String(20), default="Pendiente")
    metodo_pago = db.Column(db.String(50))
    tipo_consumo = db.Column(db.String(20))
    ticket_numero = db.Column(db.String(100))
    titular = db.Column(db.String(100))
    transferencia_info = db.Column(db.String(100))
    deuda_nombre = db.Column(db.String(100))
    hora_cocina = db.Column(db.DateTime)
    
    # Multitenancy: cada pedido pertenece a un restaurante
    restaurante_id = db.Column(db.Integer, db.ForeignKey('restaurante.id'), nullable=False)
    restaurante = db.relationship('Restaurante')
    
    # Usuario que creó el pedido
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    usuario = db.relationship('Usuario')
    
    # Relación con items
    items = db.relationship('Item', backref='pedido', cascade="all, delete-orphan")

    @property
    def total(self):
        return sum(item.producto.precio for item in self.items)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedido.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    cantidad = db.Column(db.Integer, default=1)
    
    # Relaciones
    producto = db.relationship('Producto')

# Configuración por restaurante
class ConfiguracionRestaurante(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    restaurante_id = db.Column(db.Integer, db.ForeignKey('restaurante.id'), nullable=False)
    
    # Configuraciones de impresión
    impresora_habilitada = db.Column(db.Boolean, default=False)
    impresora_tipo = db.Column(db.String(20), default="USB")  # USB, NETWORK, NONE
    impresora_ip = db.Column(db.String(15))
    impresora_puerto = db.Column(db.Integer, default=9100)
    
    # Configuraciones de interfaz
    tema = db.Column(db.String(20), default="default")
    mostrar_precios = db.Column(db.Boolean, default=True)
    
    # LÍNEA CORREGIDA: La relación estaba incompleta
    restaurante = db.relationship('Restaurante', backref=db.backref('configuracion', uselist=False))
