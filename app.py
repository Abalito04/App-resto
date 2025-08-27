from flask import Flask, render_template, request, redirect, url_for, jsonify
from models import db, Pedido, Item, Producto
from datetime import datetime, timedelta
import os
from escpos.printer import Usb, Network, File
from escpos.exceptions import *
import json
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///restaurant.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

if os.getenv('FLASK_ENV') == 'production':
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('DATABASE_URL', "sqlite:///restaurant.db")
    app.config['DEBUG'] = False
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///restaurant.db"
    app.config['DEBUG'] = True

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

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
        if pedido.metodo_pago == "Tarjeta":
            p.text(f"Ticket: {pedido.ticket_numero}\nTitular: {pedido.titular}\n")
        p.text("===================\n\n\n")
        p.cut()
    except Exception as e:
        print("Error imprimiendo comanda:", e)

# =================== FUNCIONES DE NOTIFICACIÓN ===================
def enviar_notificacion_pedido(pedido):
    """Envía notificación cuando se crea un nuevo pedido"""
    try:
        print(f"🔔 Nuevo pedido: Mesa {pedido.mesa} - Total: ${pedido.total}")
        return True
    except Exception as e:
        print(f"Error enviando notificación: {e}")
        return False

# =================== RUTAS ===================
@app.route("/")
def index():
    productos = Producto.query.all()
    pedidos = Pedido.query.filter(Pedido.estado != "Entregado").order_by(Pedido.fecha.desc()).all()
    return render_template("index.html", productos=productos, pedidos=pedidos)

@app.route("/crear_pedido", methods=["POST"])
def crear_pedido():
    mesa = request.form.get("mesa")
    nombre_cliente = request.form.get("nombre_cliente")
    direccion_cliente = request.form.get("direccion_cliente")
    tipo_consumo = request.form.get("tipo_consumo", "Local")
    metodo_pago = request.form.get("metodo_pago", "Efectivo")

    # Campos de pago extra
    ticket_numero = request.form.get("ticket_numero")
    titular = request.form.get("titular")
    transferencia_info = request.form.get("transferencia_info")
    deuda_nombre = request.form.get("deuda_nombre")

    items = request.form.getlist("producto")

    # Validación: si es local, la mesa es obligatoria
    if tipo_consumo == "Local" and (not mesa or mesa.strip() == ""):
        return "❌ Debe ingresar el número de mesa", 400

    if not items:
        return redirect(url_for("index"))

    # Crear nuevo pedido
    nuevo_pedido = Pedido(
        mesa=mesa,
        nombre_cliente=nombre_cliente,
        direccion_cliente=direccion_cliente,
        fecha=datetime.now(),
        estado="Pendiente",
        metodo_pago=metodo_pago,
        tipo_consumo=tipo_consumo,
        ticket_numero=ticket_numero,
        titular=titular,
        transferencia_info=transferencia_info,
        deuda_nombre=deuda_nombre
    )
    db.session.add(nuevo_pedido)
    db.session.commit()
    
    for producto_id in items:
        item = Item(pedido_id=nuevo_pedido.id, producto_id=int(producto_id))
        db.session.add(item)
    db.session.commit()

    imprimir_comanda(nuevo_pedido)
    enviar_notificacion_pedido(nuevo_pedido)

    return redirect(url_for("index"))



# =================== Otras rutas (borrar, editar, entregado, historial) ===================
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
        pedido.mesa = request.form.get("mesa")
        pedido.nombre_cliente = request.form.get("nombre_cliente")
        pedido.direccion_cliente = request.form.get("direccion_cliente")
        pedido.tipo_consumo = request.form.get("tipo_consumo")
        pedido.metodo_pago = request.form.get("metodo_pago")
        if pedido.metodo_pago == "Tarjeta":
            pedido.ticket_numero = request.form.get("ticket_numero")
            pedido.titular = request.form.get("titular")
        else:
            pedido.ticket_numero = None
            pedido.titular = None
        
        # Eliminar items existentes y agregar los nuevos
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
    filtro = request.args.get("filtro", "todos")
    pedidos = Pedido.query.filter(Pedido.estado == "Entregado").order_by(Pedido.fecha.desc()).all()
    
    fecha_inicio_semana = datetime.now() - timedelta(days=7)
    pedidos_semana = [p for p in pedidos if p.fecha >= fecha_inicio_semana]
    
    fecha_inicio_mes = datetime.now() - timedelta(days=30)
    pedidos_mes = [p for p in pedidos if p.fecha >= fecha_inicio_mes]

    if filtro == "semana":
        pedidos_filtrados = pedidos_semana
    elif filtro == "mes":
        pedidos_filtrados = pedidos_mes
    else:
        pedidos_filtrados = pedidos

    return render_template(
        "historial.html",
        pedidos=pedidos_filtrados,
        pedidos_semana=pedidos_semana,
        pedidos_mes=pedidos_mes,
        filtro=filtro
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
    Item.query.filter_by(producto_id=producto.id).delete()
    db.session.delete(producto)
    db.session.commit()
    return redirect(url_for("index"))


# =================== COCINA ===================
@app.route("/cocina")
def cocina():
    pedidos = Pedido.query.filter(Pedido.estado != "Entregado").order_by(Pedido.fecha.desc()).all()
    
    lista_pedidos = []
    for p in pedidos:
        if not p.hora_cocina:
            p.hora_cocina = datetime.now()
            db.session.commit()
        tiempo = None
        if p.hora_cocina:
            delta = datetime.now() - p.hora_cocina
            minutos = int(delta.total_seconds() // 60)
            segundos = int(delta.total_seconds() % 60)
            tiempo = f"{minutos}m {segundos}s"
        lista_pedidos.append({"pedido": p, "tiempo": tiempo})
    
    return render_template("cocina.html", lista_pedidos=lista_pedidos)

# =================== API PARA NOTIFICACIONES ===================
@app.route("/api/pedidos/activos")
def api_pedidos_activos():
    pedidos = Pedido.query.filter(Pedido.estado != "Entregado").all()
    return jsonify({
        "count": len(pedidos),
        "pedidos": [{
            "id": p.id,
            "mesa": p.mesa,
            "nombre_cliente": p.nombre_cliente,
            "tipo_consumo": p.tipo_consumo,
            "total": p.total,
            "fecha": p.fecha.isoformat()
        } for p in pedidos]
    })

@app.route("/api/subscribe", methods=["POST"])
def api_subscribe():
    subscription = request.get_json()
    print("Nueva suscripción:", subscription)
    return jsonify({"success": True})


@app.route("/static/manifest.json")
def manifest():
    return app.send_static_file("manifest.json")

@app.route("/static/sw.js")
def service_worker():
    return app.send_static_file("sw.js")

# Para debugging de PWA
@app.route("/pwa-debug")
def pwa_debug():
    import os
    static_files = os.listdir("static") if os.path.exists("static") else []
    return jsonify({
        "manifest_exists": "manifest.json" in static_files,
        "sw_exists": "sw.js" in static_files,
        "icons_exist": {
            "192": "icon-192.png" in static_files,
            "512": "icon-512.png" in static_files
        }
    })

# Configuración de impresora desde variables de entorno o config
PRINTER_TYPE = os.getenv("PRINTER_TYPE", "USB")  # USB, NETWORK, FILE
PRINTER_VENDOR_ID = int(os.getenv("PRINTER_VENDOR_ID", "0x04b8"), 16)
PRINTER_PRODUCT_ID = int(os.getenv("PRINTER_PRODUCT_ID", "0x0202"), 16)
PRINTER_IP = os.getenv("PRINTER_IP", "192.168.1.100")
PRINTER_PORT = int(os.getenv("PRINTER_PORT", "9100"))

def obtener_impresora():
    """Factory function para obtener la impresora según configuración"""
    try:
        if PRINTER_TYPE == "USB":
            return Usb(PRINTER_VENDOR_ID, PRINTER_PRODUCT_ID)
        elif PRINTER_TYPE == "NETWORK":
            return Network(PRINTER_IP, port=PRINTER_PORT)
        elif PRINTER_TYPE == "FILE":
            # Para testing - imprime a archivo
            return File("/tmp/comanda.txt")
        else:
            raise ValueError(f"Tipo de impresora no soportado: {PRINTER_TYPE}")
    except Exception as e:
        print(f"Error conectando impresora: {e}")
        return None

def imprimir_comanda(pedido):
    """Función mejorada de impresión con mejor manejo de errores"""
    printer = obtener_impresora()
    
    if not printer:
        print("❌ No se pudo conectar con la impresora")
        return False
    
    try:
        # Header
        printer.set(align='center', text_type='B', width=2, height=2)
        printer.text("COMANDA\n")
        printer.set()  # Reset formatting
        
        # Info del pedido
        printer.text("=" * 32 + "\n")
        
        if pedido.tipo_consumo == "Local":
            printer.text(f"MESA: {pedido.mesa}\n")
        else:
            printer.text(f"PARA LLEVAR\n")
            printer.text(f"Cliente: {pedido.nombre_cliente}\n")
            if pedido.direccion_cliente:
                printer.text(f"Dirección: {pedido.direccion_cliente}\n")
        
        printer.text(f"Fecha: {pedido.fecha.strftime('%d/%m/%Y %H:%M')}\n")
        printer.text(f"Pedido #{pedido.id}\n")
        printer.text("-" * 32 + "\n")
        
        # Items
        total = 0
        for item in pedido.items:
            precio = item.producto.precio
            total += precio
            # Formato: Producto................$1234
            nombre = item.producto.nombre[:20]  # Limitar longitud
            linea = f"{nombre:<20}${precio:>8.0f}\n"
            printer.text(linea)
        
        printer.text("-" * 32 + "\n")
        
        # Total
        printer.set(text_type='B')  # Bold
        printer.text(f"TOTAL: ${total:.0f}\n")
        printer.set()  # Reset
        
        # Método de pago
        printer.text(f"Pago: {pedido.metodo_pago}\n")
        
        if pedido.metodo_pago == "Tarjeta" and pedido.ticket_numero:
            printer.text(f"Ticket: {pedido.ticket_numero}\n")
            if pedido.titular:
                printer.text(f"Titular: {pedido.titular}\n")
        
        printer.text("=" * 32 + "\n")
        
        # Pie
        printer.set(align='center')
        printer.text("¡Buen provecho!\n")
        printer.text("\n\n\n")  # Espacio para cortar
        
        # Cortar papel
        printer.cut()
        printer.close()
        
        print(f"✅ Comanda impresa para pedido #{pedido.id}")
        return True
        
    except Exception as e:
        print(f"❌ Error imprimiendo comanda: {e}")
        try:
            printer.close()
        except:
            pass
        return False

# Función para testing de impresora
@app.route("/test-printer")
def test_printer():
    """Endpoint para probar la impresora"""
    printer = obtener_impresora()
    if not printer:
        return jsonify({"error": "No se pudo conectar con la impresora"}), 500
    
    try:
        printer.text("TEST DE IMPRESORA\n")
        printer.text("Conexión exitosa\n")
        printer.text(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
        printer.text("\n\n")
        printer.cut()
        printer.close()
        return jsonify({"success": "Test de impresión exitoso"})
    except Exception as e:
        return jsonify({"error": f"Error en test: {str(e)}"}), 500

# =================== RUN ===================
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    debug = os.getenv('FLASK_ENV') != 'production'
    app.run(host="0.0.0.0", port=port, debug=debug)
