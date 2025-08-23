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
    """
    Imprime la comanda de un pedido en impresora USB.
    pedido: objeto Pedido de SQLAlchemy
    """
    try:
        # Cambiar Vendor ID y Product ID por los de tu impresora
        p = Usb(0x04b8, 0x0202)  # Ejemplo Epson

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

    # Revisar si ya hay un pedido activo en la misma mesa
    pedido_existente = Pedido.query.filter_by(mesa=mesa, estado="Pendiente").first()

    if pedido_existente:
        # Si existe, agregamos los ítems al pedido existente
        for producto_id in items:
            item = Item(pedido_id=pedido_existente.id, producto_id=int(producto_id))
            db.session.add(item)
        # También podemos actualizar el metodo de pago si queremos
        pedido_existente.metodo_pago = metodo_pago
        db.session.commit()
        imprimir_comanda(pedido_existente)  # Opcional: imprimir solo lo nuevo
    else:
        # Si no existe, se crea un nuevo pedido
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
    # Todos los pedidos entregados
    pedidos = Pedido.query.filter(Pedido.estado == "Entregado").order_by(Pedido.fecha.desc()).all()

    # Pedidos por semana
    fecha_inicio_semana = datetime.now() - timedelta(days=7)
    pedidos_semana = [p for p in pedidos if p.fecha >= fecha_inicio_semana]

    # Pedidos por mes
    fecha_inicio_mes = datetime.now() - timedelta(days=30)
    pedidos_mes = [p for p in pedidos if p.fecha >= fecha_inicio_mes]

    return render_template(
        "historial.html",
        pedidos=pedidos,
        pedidos_semana=pedidos_semana,
        pedidos_mes=pedidos_mes
    )

# =================== Gestión de productos ===================

# =================== GESTIÓN DE PRODUCTOS ===================

# Página de gestión de productos (mozo/admin)
@app.route("/productos", methods=["GET", "POST"])
def gestion_productos():
    productos = Producto.query.all()
    if request.method == "POST":
        # Crear nuevo producto
        nombre = request.form["nombre"]
        precio = float(request.form["precio"])
        nuevo_producto = Producto(nombre=nombre, precio=precio)
        db.session.add(nuevo_producto)
        db.session.commit()
        return redirect(url_for("gestion_productos"))
    return render_template("productos.html", productos=productos)

# Editar producto desde gestión
@app.route("/productos/editar/<int:producto_id>", methods=["POST"])
def editar_producto_gestion(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    producto.nombre = request.form["nombre"]
    producto.precio = float(request.form["precio"])
    db.session.commit()
    return redirect(url_for("gestion_productos"))

# Borrar producto desde gestión
@app.route("/productos/borrar/<int:producto_id>", methods=["POST"])
def borrar_producto_gestion(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    db.session.delete(producto)
    db.session.commit()
    return redirect(url_for("gestion_productos"))

# =================== PRODUCTOS EN INDEX (MOZO) ===================

# Agregar producto desde index
@app.route("/agregar_producto", methods=["POST"])
def agregar_producto_index():
    nombre = request.form["nombre"]
    precio = float(request.form["precio"])
    producto = Producto(nombre=nombre, precio=precio)
    db.session.add(producto)
    db.session.commit()
    return redirect(url_for("index"))

# Editar producto desde index
@app.route("/editar_producto/<int:producto_id>", methods=["POST"])
def editar_producto_index(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    producto.nombre = request.form["nombre"]
    producto.precio = float(request.form["precio"])
    db.session.commit()
    return redirect(url_for("index"))

# Borrar producto desde index
@app.route("/borrar_producto/<int:producto_id>", methods=["POST"])
def borrar_producto_index(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    db.session.delete(producto)
    db.session.commit()
    return redirect(url_for("index"))

# =================== RUN ===================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)


