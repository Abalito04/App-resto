# app.py - Versión SaaS con autenticación
import os
import logging
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from flask_login import LoginManager, login_required, current_user
from models import db, Usuario, Restaurante, Pedido, Item, Producto, ConfiguracionRestaurante
from auth import auth_bp, crear_slug
from datetime import datetime, timedelta
from dotenv import load_dotenv


# Configurar logging
logging.basicConfig(level=logging.DEBUG)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'tu-clave-secreta-muy-segura')

# Configuración de base de datos
database_url = os.getenv('DATABASE_URL')
if database_url:
    # Corregir URL de Railway/Heroku si es necesario
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config['DEBUG'] = False
else:
    # Desarrollo local
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///restaurant.db"
    app.config['DEBUG'] = True

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Inicializar extensiones
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Debes iniciar sesión para acceder.'
login_manager.login_message_category = 'error'

# Registrar blueprint de autenticación
app.register_blueprint(auth_bp, url_prefix='/auth')

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Filtro de context processor para templates
@app.context_processor
def inject_user():
    return {
        'current_user': current_user,
        'current_restaurante': current_user.restaurante if current_user.is_authenticated else None
    }

# Helper function para filtrar por restaurante
def get_user_restaurante():
    """Obtiene el ID del restaurante del usuario logueado"""
    if not current_user.is_authenticated:
        return None
    return current_user.restaurante_id

# =================== CREAR BASE DE DATOS ===================
with app.app_context():
    db.create_all()

# =================== FUNCIÓN DE IMPRESIÓN (SIMULADA) ===================
def imprimir_comanda(pedido):
    """Función de impresión - versión SaaS"""
    config = pedido.restaurante.configuracion
    
    if not config or not config.impresora_habilitada:
        print(f"Impresión deshabilitada para {pedido.restaurante.nombre}")
        return False
    
    try:
        # Simulación de impresión (en producción conectaría con la impresora real)
        print("=== COMANDA ===")
        print(f"Restaurante: {pedido.restaurante.nombre}")
        if pedido.tipo_consumo == "Local":
            print(f"Mesa: {pedido.mesa}")
        else:
            print(f"Para llevar: {pedido.nombre_cliente}")
        print(f"Fecha: {pedido.fecha.strftime('%d/%m/%Y %H:%M:%S')}")
        print("-------------------")
        for item in pedido.items:
            print(f"{item.producto.nombre} - {pedido.restaurante.moneda}{item.producto.precio}")
        print("-------------------")
        print(f"TOTAL: {pedido.restaurante.moneda}{pedido.total}")
        print(f"Método de pago: {pedido.metodo_pago}")
        print("===================")
        return True
    except Exception as e:
        print("Error imprimiendo comanda:", e)
        return False

# =================== RUTAS PRINCIPALES ===================

@app.route("/")
def index_redirect():
    """Redirige al setup si no hay usuarios, sino al dashboard"""
    if not current_user.is_authenticated:
        # Si no hay usuarios en el sistema, ir a setup
        if not Usuario.query.first():
            return redirect(url_for('setup_inicial'))
        # Si hay usuarios pero no está logueado, ir a login
        return redirect(url_for('auth.login'))
    
    # Si está logueado, mostrar la app normal
    return index_logueado()

@app.route("/dashboard")
@login_required
def index_logueado():
    """Dashboard principal - la función index original"""
    restaurante_id = get_user_restaurante()
    productos = Producto.query.filter_by(restaurante_id=restaurante_id, activo=True).all()
    pedidos = Pedido.query.filter_by(restaurante_id=restaurante_id)\
                         .filter(Pedido.estado != "Entregado")\
                         .order_by(Pedido.fecha.desc()).all()
    return render_template("index.html", productos=productos, pedidos=pedidos)

@app.route("/setup", methods=["GET", "POST"])
def setup_inicial():
    """Setup inicial - solo si no hay usuarios en el sistema"""
    
    # Verificar si ya hay usuarios en el sistema
    if Usuario.query.first():
        flash('El sistema ya está configurado. Usa el login normal.', 'info')
        return redirect(url_for('auth.login'))
    
    if request.method == "POST":
        # Datos del primer usuario admin
        nombre = request.form.get('nombre', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        # Datos del primer restaurante
        nombre_restaurante = request.form.get('nombre_restaurante', '').strip()
        direccion = request.form.get('direccion', '').strip()
        telefono = request.form.get('telefono', '').strip()
        
        # Validaciones básicas
        if not all([nombre, email, password, nombre_restaurante]):
            flash('Todos los campos son obligatorios', 'error')
            return render_template('setup.html')
        
        if len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres', 'error')
            return render_template('setup.html')
        
        try:
            # Crear el primer restaurante
            slug = crear_slug(nombre_restaurante)
            restaurante = Restaurante(
                nombre=nombre_restaurante,
                slug=slug,
                direccion=direccion,
                telefono=telefono,
                email_contacto=email,
                plan="free"
            )
            db.session.add(restaurante)
            db.session.flush()
            
            # Crear el primer usuario admin
            usuario = Usuario(
                nombre=nombre,
                email=email,
                es_admin=True,
                restaurante_id=restaurante.id
            )
            usuario.set_password(password)
            db.session.add(usuario)
            
            # Crear configuración inicial
            config = ConfiguracionRestaurante(restaurante_id=restaurante.id)
            db.session.add(config)
            
            # Productos de ejemplo
            productos_ejemplo = [
                Producto(nombre="Pizza Muzzarella", precio=2500, restaurante_id=restaurante.id),
                Producto(nombre="Hamburguesa Completa", precio=3200, restaurante_id=restaurante.id),
                Producto(nombre="Coca-Cola 500ml", precio=1200, restaurante_id=restaurante.id),
                Producto(nombre="Empanada de Carne", precio=800, restaurante_id=restaurante.id),
            ]
            db.session.add_all(productos_ejemplo)
            
            db.session.commit()
            
            flash('¡Sistema configurado exitosamente! Ya puedes iniciar sesión.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash('Error configurando el sistema. Intenta nuevamente.', 'error')
            print(f"Error en setup: {e}")
    
    return render_template('setup.html')

@app.route("/crear_pedido", methods=["POST"])
@login_required
def crear_pedido():
    restaurante_id = get_user_restaurante()
    
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
        return "Debe ingresar el número de mesa", 400

    if not items:
        return redirect(url_for("index_redirect"))

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
        deuda_nombre=deuda_nombre,
        restaurante_id=restaurante_id,
        usuario_id=current_user.id
    )
    db.session.add(nuevo_pedido)
    db.session.commit()
    
    # Agregar items (solo productos del mismo restaurante)
    for producto_id in items:
        producto = Producto.query.filter_by(id=int(producto_id), restaurante_id=restaurante_id).first()
        if producto:
            item = Item(pedido_id=nuevo_pedido.id, producto_id=producto.id)
            db.session.add(item)
    db.session.commit()

    imprimir_comanda(nuevo_pedido)
    return redirect(url_for("index_redirect"))

@app.route("/borrar/<int:pedido_id>", methods=["POST"])
@login_required
def borrar_pedido(pedido_id):
    pedido = Pedido.query.filter_by(id=pedido_id, restaurante_id=get_user_restaurante()).first_or_404()
    db.session.delete(pedido)
    db.session.commit()
    return redirect(url_for("index_redirect"))

@app.route("/editar/<int:pedido_id>", methods=["GET", "POST"])
@login_required
def editar_pedido(pedido_id):
    restaurante_id = get_user_restaurante()
    pedido = Pedido.query.filter_by(id=pedido_id, restaurante_id=restaurante_id).first_or_404()
    productos = Producto.query.filter_by(restaurante_id=restaurante_id, activo=True).all()
    
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
            producto = Producto.query.filter_by(id=int(producto_id), restaurante_id=restaurante_id).first()
            if producto:
                item = Item(pedido_id=pedido.id, producto_id=producto.id)
                db.session.add(item)
        
        db.session.commit()
        return redirect(url_for("index_redirect"))
    
    return render_template("editar.html", pedido=pedido, productos=productos)

@app.route("/entregado/<int:pedido_id>", methods=["POST"])
@login_required
def entregado(pedido_id):
    pedido = Pedido.query.filter_by(id=pedido_id, restaurante_id=get_user_restaurante()).first_or_404()
    pedido.estado = "Entregado"
    db.session.commit()
    return redirect(request.referrer or url_for("index_redirect"))

@app.route("/historial")
@login_required
def historial():
    restaurante_id = get_user_restaurante()
    filtro = request.args.get("filtro", "todos")
    pedidos = Pedido.query.filter_by(restaurante_id=restaurante_id, estado="Entregado")\
                         .order_by(Pedido.fecha.desc()).all()
    
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
@login_required
def agregar_producto_index():
    nombre = request.form["nombre"]
    precio = float(request.form["precio"])
    producto = Producto(nombre=nombre, precio=precio, restaurante_id=get_user_restaurante())
    db.session.add(producto)
    db.session.commit()
    return redirect(url_for("index_redirect"))

@app.route("/editar_producto_index/<int:producto_id>", methods=["POST"])
@login_required
def editar_producto_index(producto_id):
    producto = Producto.query.filter_by(id=producto_id, restaurante_id=get_user_restaurante()).first_or_404()
    producto.nombre = request.form["nombre"]
    producto.precio = float(request.form["precio"])
    db.session.commit()
    return redirect(url_for("index_redirect"))

@app.route("/borrar_producto_index/<int:producto_id>", methods=["POST"])
@login_required
def borrar_producto_index(producto_id):
    producto = Producto.query.filter_by(id=producto_id, restaurante_id=get_user_restaurante()).first_or_404()
    Item.query.filter_by(producto_id=producto.id).delete()
    db.session.delete(producto)
    db.session.commit()
    return redirect(url_for("index_redirect"))

# =================== COCINA ===================
@app.route("/cocina")
@login_required
def cocina():
    restaurante_id = get_user_restaurante()
    pedidos = Pedido.query.filter_by(restaurante_id=restaurante_id)\
                         .filter(Pedido.estado != "Entregado")\
                         .order_by(Pedido.fecha.desc()).all()
    
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

# =================== API PARA MULTITENANCY ===================
@app.route("/api/pedidos/activos")
@login_required
def api_pedidos_activos():
    restaurante_id = get_user_restaurante()
    pedidos = Pedido.query.filter_by(restaurante_id=restaurante_id)\
                         .filter(Pedido.estado != "Entregado").all()
    
    pedidos_data = []
    for p in pedidos:
        items_data = []
        for item in p.items:
            items_data.append({
                "nombre": item.producto.nombre,
                "precio": item.producto.precio
            })
        
        pedido_data = {
            "id": p.id,
            "mesa": p.mesa,
            "nombre_cliente": p.nombre_cliente,
            "direccion_cliente": p.direccion_cliente,
            "tipo_consumo": p.tipo_consumo,
            "metodo_pago": p.metodo_pago,
            "fecha": p.fecha.isoformat(),
            "items": items_data,
            "total": p.total
        }
        pedidos_data.append(pedido_data)
    
    return jsonify({
        "count": len(pedidos_data),
        "pedidos": pedidos_data,
        "restaurante": current_user.restaurante.nombre
    })

# API publica con API Key
@app.route("/api/public/pedidos/<api_key>")
def api_public_pedidos(api_key):
    """API pública para clientes de impresión externos"""
    restaurante = Restaurante.query.filter_by(api_key=api_key, activo=True).first()
    if not restaurante:
        return jsonify({"error": "API Key inválida"}), 401
    
    pedidos = Pedido.query.filter_by(restaurante_id=restaurante.id)\
                         .filter(Pedido.estado != "Entregado").all()
    
    pedidos_data = []
    for p in pedidos:
        items_data = []
        for item in p.items:
            items_data.append({
                "nombre": item.producto.nombre,
                "precio": item.producto.precio
            })
        
        pedido_data = {
            "id": p.id,
            "mesa": p.mesa,
            "nombre_cliente": p.nombre_cliente,
            "tipo_consumo": p.tipo_consumo,
            "metodo_pago": p.metodo_pago,
            "fecha": p.fecha.isoformat(),
            "items": items_data,
            "total": p.total
        }
        pedidos_data.append(pedido_data)
    
    return jsonify({
        "count": len(pedidos_data),
        "pedidos": pedidos_data,
        "restaurante": restaurante.nombre
    })

@app.route("/api/test")
def api_test():
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "message": "API funcionando correctamente"
    })

# =================== MANIFEST PWA ===================
@app.route("/static/manifest.json")
def manifest():
    return app.send_static_file("manifest.json")

@app.route("/static/sw.js")
def service_worker():
    return app.send_static_file("sw.js")

# Redirigir a login por defecto
@app.route("/login")
def login_redirect():
    return redirect(url_for('auth.login'))

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    debug = os.getenv('FLASK_ENV') != 'production'
    app.run(host="0.0.0.0", port=port, debug=debug)