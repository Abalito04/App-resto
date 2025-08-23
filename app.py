from flask import Flask, render_template, request, redirect, url_for
from models import db, Pedido, Item, Producto
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///restaurant.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Crear BD en el primer run
with app.app_context():
    db.create_all()
    if not Producto.query.first():
        productos = [
            Producto(nombre="Pizza Muzzarella", precio=2500),
            Producto(nombre="Hamburguesa Completa", precio=3200),
            Producto(nombre="Coca-Cola 500ml", precio=1200),
            Producto(nombre="Agua Mineral", precio=900),
        ]
        db.session.add_all(productos)
        db.session.commit()

# =================== RUTAS ===================

@app.route("/")
def index():
    productos = Producto.query.all()
    pedidos = Pedido.query.filter(Pedido.estado != "Entregado").order_by(Pedido.fecha.desc()).all()
    return render_template("index.html", productos=productos, pedidos=pedidos)


@app.route("/pedido", methods=["POST"])
def crear_pedido():
    mesa = request.form["mesa"]
    metodo_pago = request.form.get("metodo_pago", "Efectivo")  # Default Efectivo
    items = request.form.getlist("producto")

    nuevo_pedido = Pedido(
        mesa=mesa,
        fecha=datetime.now(),
        estado="Pendiente",
        metodo_pago=metodo_pago
    )
    db.session.add(nuevo_pedido)
    db.session.commit()

    for producto_id in items:
        item = Item(pedido_id=nuevo_pedido.id, producto_id=int(producto_id))
        db.session.add(item)
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/cocina")
def cocina():
    pedidos = Pedido.query.filter(Pedido.estado != "Entregado").order_by(Pedido.fecha.desc()).all()
    return render_template("cocina.html", pedidos=pedidos)


@app.route("/borrar/<int:pedido_id>", methods=["POST"])
def borrar_pedido(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    db.session.delete(pedido)
    db.session.commit()
    return redirect(url_for("cocina"))


@app.route("/editar/<int:pedido_id>", methods=["GET", "POST"])
def editar_pedido(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    productos = Producto.query.all()
    if request.method == "POST":
        pedido.mesa = request.form["mesa"]
        Item.query.filter_by(pedido_id=pedido.id).delete()
        items = request.form.getlist("producto")
        for producto_id in items:
            item = Item(pedido_id=pedido.id, producto_id=int(producto_id))
            db.session.add(item)
        db.session.commit()
        return redirect(url_for("cocina"))
    return render_template("editar.html", pedido=pedido, productos=productos)


@app.route("/entregado/<int:pedido_id>", methods=["POST"])
def entregado(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    pedido.estado = "Entregado"
    db.session.commit()
    return redirect(request.referrer or url_for("cocina"))


@app.route("/historial")
def historial():
    pedidos = Pedido.query.filter(Pedido.estado == "Entregado").order_by(Pedido.fecha.desc()).all()
    return render_template("historial.html", pedidos=pedidos)


# =================== RUN ===================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)


