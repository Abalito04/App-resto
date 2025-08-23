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
    mesa = db.Column(db.String(50), nullable=True)  # NULL si es para llevar
    fecha = db.Column(db.DateTime, default=datetime.now)
    estado = db.Column(db.String(20), default="Pendiente")
    metodo_pago = db.Column(db.String(20), default="Efectivo")
    tipo_consumo = db.Column(db.String(20), default="Local")  # Local o Llevar
    nombre_cliente = db.Column(db.String(100), nullable=True)
    direccion_cliente = db.Column(db.String(200), nullable=True)
    
    items = db.relationship("Item", backref="pedido", lazy=True, cascade="all, delete-orphan")

    @property
    def total(self):
        return sum(item.producto.precio for item in self.items)


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedido.id"), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey("producto.id"), nullable=False)
    producto = db.relationship("Producto")

    def __repr__(self):
        return f"<Item {self.producto.nombre} (Pedido {self.pedido_id})>"



