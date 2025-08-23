from flask import Flask, render_template, request, redirect, url_for
from models import db, Pedido, Item, Producto
from datetime import datetime, timedelta
from escpos.printer import Usb

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///restaurant.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# =================== CREAR BASE DE DATOS ===================
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

# =================== FUNCION DE IMPRESION ===================
def imprimir_comanda(pedido):
    try:
        p = Usb(0x04b8, 0x0202)  # Cambiar por tus IDs
        p.text("===== COMANDA =====\n")
        p.text(f"Mesa: {pedido.mesa}\n")
        p.text(f"Fecha: {pedido.fecha.strftime('%d/%m/%Y %H:%M:%S')}\n")
        p.text("-------------------\n")
        for item in pedido.items:
            p.text(f"{item.producto.nombre} - ${item.producto.precio}\n")
        p.text("-------------------\n")
        total = sum(item.producto.precio for item in pedido.items)
        p.text(f"TOTAL: ${total}\n")
        p.text(f"Método de pago: {pedido.metodo_pago}\n")
        p.text("===================\n\n\n")
        p.cut()
    except Exception as e:
        print("Error imprimiendo comanda:", e)

# =================== RUTAS ===================

@app.route("/")
def index():
    productos = Producto.query.all()
    pedidos = Pedido.query.filter(Pedido.estado != "Entregado").order_by(Pedido.fecha.desc()).all()
    return render_template("index.html", productos=productos, pedidos=pedidos)

@app.route("/crear_pedido", methods=["POST"])
def crear_pedido():
    mesa = request.form["mesa"]
    metodo_pago = request.form.get("metodo_pago", "Efectivo")
    items = request.form.getlist("producto")

    pedido_existente = Pedido.query.filter_by(mesa=mesa, estado="Pendiente").first()

    if pedido_existente:
        for producto_id in items:
            item = Item(pedido_id=pedido_existente.id, producto_id=int(producto_id))
            db.session.add(item)
        pedido_existente.metodo_pago = metodo_pago
        db.session.commit()
        imprimir_comanda(pedido_existente)
    else:
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
        imprimir_comanda(nuevo_pedido)

    return redirect(url_for("index"))

@app.route("/borrar/<int:pedido_id>", methods=["POST"])
def borrar_pedido(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    db.session.delete(pedido)
    db.session.commit()
    return redirect(url_for("index"))

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
        return redirect(url_for("index"))
    return render_template("editar.html", pedido=pedido, productos=productos)

@app.route("/entregado/<int:pedido_id>", methods=["POST"])
def entregado(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    pedido.estado = "Entregado"
    db.session.commit()
    return redirect(request.referrer or url_for("index"))

@app.route("/historial")
def historial():
    pedidos = Pedido.query.filter(Pedido.estado == "Entregado").order_by(Pedido.fecha.desc()).all()
    fecha_inicio_semana = datetime.now() - timedelta(days=7)
    pedidos_semana = [p for p in pedidos if p.fecha >= fecha_inicio_semana]
    fecha_inicio_mes = datetime.now() - timedelta(days=30)
    pedidos_mes = [p for p in pedidos if p.fecha >= fecha_inicio_mes]
    return render_template(
        "historial.html",
        pedidos=pedidos,
        pedidos_semana=pedidos_semana,
        pedidos_mes=pedidos_mes
    )

# =================== PRODUCTOS ===================

@app.route("/agregar_producto_index", methods=["POST"])
def agregar_producto_index():
    nombre = request.form["nombre"]
    precio = float(request.form["precio"])
    producto = Producto(nombre=nombre, precio=precio)
    db.session.add(producto)
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/editar_producto_index/<int:producto_id>", methods=["POST"])
def editar_producto_index(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    producto.nombre = request.form["nombre"]
    producto.precio = float(request.form["precio"])
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/borrar_producto_index/<int:producto_id>", methods=["POST"])
def borrar_producto_index(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    db.session.delete(producto)
    db.session.commit()
    return redirect(url_for("index"))

# =================== RUN ===================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)



