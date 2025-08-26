from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)

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

    # ⚡ Importante: cascade para borrar items automáticamente
    items = db.relationship('Item', backref='pedido', cascade="all, delete-orphan")

    @property
    def total(self):
        return sum(item.producto.precio for item in self.items)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedido.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    producto = db.relationship('Producto')


