from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Producto {self.nombre} (${self.precio})>"


class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mesa = db.Column(db.String(50), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.now)
    estado = db.Column(db.String(20), default="Pendiente")
    metodo_pago = db.Column(db.String(20), default="Efectivo")  # 👈 Nuevo campo
    items = db.relationship("Item", backref="pedido", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Pedido Mesa {self.mesa} - {self.estado} ({self.metodo_pago})>"


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedido.id"), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey("producto.id"), nullable=False)

    # Relación con Producto
    producto = db.relationship("Producto")

    def __repr__(self):
        return f"<Item {self.producto.nombre} (Pedido {self.pedido_id})>"


