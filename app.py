# app.py - Versión SaaS con autenticación - CORREGIDA
import os
import logging
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from flask_login import LoginManager, login_required, current_user
from datetime import datetime, timedelta
from dotenv import load_dotenv
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from sqlalchemy import text
from collections import Counter
import pytz

# Configurar logging
logging.basicConfig(level=logging.DEBUG)

# Configurar zona horaria del servidor para que coincida con la PC local
import os
timezone_server = os.getenv('SERVER_TIMEZONE', 'America/Argentina/Buenos_Aires')
print(f"🔧 Configurando zona horaria del servidor: {timezone_server}")
os.environ['TZ'] = timezone_server
try:
    import time
    time.tzset()
    print(f"✅ Zona horaria configurada: {timezone_server}")
except:
    print("⚠️ No se pudo configurar zona horaria (Windows o sistema no compatible)")
    pass  # En Windows no existe tzset()

load_dotenv()



app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'tu-clave-secreta-muy-segura')

# Configuración de base de datos
database_url = os.getenv('CUSTOM_DATABASE_URL', '')
if not database_url:
    database_url = os.getenv('DATABASE_URL', '')  # fallback a la original

# Forzar URL pública si detectamos que Railway está usando la interna
if database_url and 'railway.internal' in database_url:
    print("⚠️ Railway está usando URL interna, forzando URL pública...")
    # Usar la URL pública directamente
    database_url = "postgresql://postgres:hISwhPDoevhhPocdYdIIOlawevrfPgcN@yamabiko.proxy.rlwy.net:35702/railway"

if database_url:
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
    parsed = urlparse(database_url)
    q = dict(parse_qsl(parsed.query))
    q.setdefault('sslmode', 'require')
    q.setdefault('connect_timeout', '5')
    database_url = urlunparse(parsed._replace(query=urlencode(q)))

    print(f"🔗 Usando URL de DB: {database_url}")
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "connect_args": {"sslmode": "require", "connect_timeout": 5},
        "pool_pre_ping": True,
    }
    app.config['DEBUG'] = False
else:
    # Desarrollo local (sin DATABASE_URL)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///restaurant.db"
    app.config['DEBUG'] = True

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Importar modelos DESPUÉS de configurar la app
from models import db, Usuario, Restaurante, Pedido, Item, Producto, ConfiguracionRestaurante
from auth import auth_bp, crear_slug

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
    try:
        return Usuario.query.get(int(user_id))
    except Exception as e:
        print(f"Error cargando usuario {user_id}: {e}")
        return None

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

def get_local_time(restaurante_id=None):
    """Obtiene la hora local del restaurante"""
    if not restaurante_id:
        restaurante_id = get_user_restaurante()
    
    # Obtener la zona horaria del restaurante
    zona_horaria = 'America/Argentina/Buenos_Aires'  # Default
    if restaurante_id:
        restaurante = Restaurante.query.get(restaurante_id)
        if restaurante and restaurante.zona_horaria:
            zona_horaria = restaurante.zona_horaria
    
    try:
        # Convertir UTC a zona horaria local
        tz = pytz.timezone(zona_horaria)
        utc_now = datetime.now(pytz.UTC)
        local_time = utc_now.astimezone(tz)
        return local_time.replace(tzinfo=None)  # Retornar sin timezone para compatibilidad
    except:
        # Fallback a hora del servidor
        return datetime.now()

# =================== CREAR BASE DE DATOS CON MANEJO DE ERRORES ===================
def init_db():
    """Inicializar base de datos con manejo de errores"""
    try:
        with app.app_context():
            db.create_all()
            print("Base de datos inicializada correctamente")
    except Exception as e:
        print(f"Error inicializando base de datos: {e}")

# Llamar a init_db al importar
init_db()

# =================== RUTAS CON MANEJO DE ERRORES ===================



@app.route("/")
def index_redirect():
    """Redirige al setup si no hay usuarios, sino al dashboard"""
    try:
        if not current_user.is_authenticated:
            # Verificar si hay usuarios en el sistema
            try:
                usuario_existe = Usuario.query.first()
                if not usuario_existe:
                    return redirect(url_for('setup_inicial'))
            except Exception as e:
                print(f"Error verificando usuarios: {e}")
                return redirect(url_for('setup_inicial'))
            
            # Si hay usuarios pero no está logueado, ir a login
            return redirect(url_for('auth.login'))
        
        # Si está logueado, mostrar la app normal
        return index_logueado()
    
    except Exception as e:
        print(f"Error en index_redirect: {e}")
        return redirect(url_for('setup_inicial'))

@app.route("/clear-session")
def clear_session():
    """Limpiar sesión - útil después de resetear DB"""
    session.clear()
    flash('Sesión limpiada', 'info')
    return redirect(url_for('setup_inicial'))

@app.route("/dashboard")
@login_required
def index_logueado():
    """Dashboard principal - la función index original"""
    try:
        restaurante_id = get_user_restaurante()
        productos = Producto.query.filter_by(restaurante_id=restaurante_id, activo=True).all()
        pedidos = Pedido.query.filter_by(restaurante_id=restaurante_id)\
                             .filter(Pedido.estado != "Entregado")\
                             .order_by(Pedido.fecha.desc()).all()
        return render_template("index.html", productos=productos, pedidos=pedidos)
    except Exception as e:
        flash(f'Error cargando dashboard: {str(e)}', 'error')
        return redirect(url_for('setup_inicial'))







@app.route("/make-superadmin/<email>")
def make_superadmin(email):
    """Ruta temporal para hacer superadmin a un usuario - REMOVER EN PRODUCCIÓN"""
    try:
        user = Usuario.query.filter_by(email=email).first()
        if user:
            user.es_superadmin = True
            db.session.commit()
            return f"Usuario {email} ahora es superadmin"
        return "Usuario no encontrado"
    except Exception as e:
        return f"Error: {str(e)}"

# =================== FUNCIÓN DE IMPRESIÓN (SIMULADA) ===================
def imprimir_comanda(pedido):
    """Función de impresión - versión SaaS"""
    try:
        config = pedido.restaurante.configuracion
        
        if not config or not config.impresora_habilitada:
            print(f"Impresión deshabilitada para {pedido.restaurante.nombre}")
            return False
        
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

@app.route("/setup", methods=["GET", "POST"])
def setup_inicial():
    """Setup inicial - solo si no hay usuarios en el sistema"""
    
    try:
        # Verificar si ya hay usuarios en el sistema
        usuario_existe = Usuario.query.first()
        if usuario_existe:
            flash('El sistema ya está configurado. Usa el login normal.', 'info')
            return redirect(url_for('auth.login'))
    except Exception as e:
        print(f"Error verificando usuarios existentes: {e}")
        # Si hay error, continúa con el setup
    
    if request.method == "POST":
        # Datos del primer usuario admin
        nombre = request.form.get('nombre', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        # Datos del primer restaurante
        nombre_restaurante = request.form.get('nombre_restaurante', '').strip()
        direccion = request.form.get('direccion', '').strip()
        telefono = request.form.get('telefono', '').strip()
        zona_horaria = request.form.get('zona_horaria', 'America/Argentina/Buenos_Aires')
        
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
                zona_horaria=zona_horaria,
                plan="free"
            )
            db.session.add(restaurante)
            db.session.flush()
            
            # Crear el primer usuario admin
            usuario = Usuario(
                nombre=nombre,
                email=email,
                es_admin=True,
                es_superadmin=True,  # Hacer que el primer usuario sea superadmin
                restaurante_id=restaurante.id,
                activo=True,
                confirmado=True  # No requiere confirmación por email
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
            import traceback
            print("Error en setup:", e)
            traceback.print_exc()
            flash(f'Error configurando el sistema. Intenta nuevamente.', 'error')
    
    return render_template('setup.html')

# =================== RESTO DE RUTAS (sin cambios) ===================

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

    # 1. Buscar pedido activo para esa mesa y restaurante
    pedido = None
    if tipo_consumo == "Local":
        pedido = Pedido.query.filter_by(
            mesa=mesa,
            restaurante_id=restaurante_id,
            estado="Pendiente"
        ).first()
    else:
        # Para llevar: podrías usar nombre_cliente o algún otro criterio
        pedido = None

    if not pedido:
        # 2. Si no existe, crear nuevo pedido
        pedido = Pedido(
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
        db.session.add(pedido)
        db.session.commit()

    # 3. Agregar productos al pedido existente (sumar ítems correctamente)
    conteo = Counter(items)  # Cuenta cuántas veces se seleccionó cada producto

    for producto_id_str, cantidad in conteo.items():
        producto_id = int(producto_id_str)
        producto = Producto.query.filter_by(id=producto_id, restaurante_id=restaurante_id).first()
        if producto:
            # Buscar si ya existe un item con este producto en el pedido
            item_existente = Item.query.filter_by(
                pedido_id=pedido.id, 
                producto_id=producto.id
            ).first()
            
            if item_existente:
                # Si ya existe, sumar la cantidad
                item_existente.cantidad += cantidad
                print(f"Sumando {cantidad} al item existente: {producto.nombre}")
            else:
                # Si no existe, crear nuevo item
                nuevo_item = Item(
                    pedido_id=pedido.id, 
                    producto_id=producto.id, 
                    cantidad=cantidad
                )
                db.session.add(nuevo_item)
                print(f"Creando nuevo item: {producto.nombre} x{cantidad}")
    
    db.session.commit()
    print(f"Pedido actualizado: {pedido.id} con {len(pedido.items)} items")

    imprimir_comanda(pedido)
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

@app.route("/llegada_cocina/<int:pedido_id>", methods=["POST"])
@login_required
def llegada_cocina(pedido_id):
    """Marca cuando un pedido llega a cocina"""
    pedido = Pedido.query.filter_by(id=pedido_id, restaurante_id=get_user_restaurante()).first_or_404()
    if not pedido.hora_cocina:
        pedido.hora_cocina = get_local_time()
        db.session.commit()
        flash("Pedido marcado como recibido en cocina", "success")
    return redirect(url_for("cocina"))

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
    try:
        # Verificar límites del plan
        restaurante = current_user.restaurante
        can_add, remaining = restaurante.can_add_product()
        
        if not can_add:
            flash(f'No puedes agregar más productos. Límite del plan alcanzado. Contacta al administrador para cambiar de plan.', 'error')
            return redirect(url_for("index_redirect"))
        
        nombre = request.form["nombre"]
        precio = float(request.form["precio"])
        producto = Producto(nombre=nombre, precio=precio, restaurante_id=get_user_restaurante())
        db.session.add(producto)
        db.session.commit()
        
        if remaining is not None:
            flash(f'Producto agregado exitosamente. Te quedan {remaining} productos disponibles.', 'success')
        else:
            flash('Producto agregado exitosamente', 'success')
            
    except Exception as e:
        db.session.rollback()
        flash(f'Error agregando producto: {str(e)}', 'error')
    
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
        tiempo = None
        if p.hora_cocina:
            # Calcular tiempo desde que llegó a cocina usando hora local
            ahora = get_local_time(restaurante_id)
            delta = ahora - p.hora_cocina
            minutos = int(delta.total_seconds() // 60)
            segundos = int(delta.total_seconds() % 60)
            tiempo = f"{minutos}m {segundos}s"
        else:
            # Si no tiene hora_cocina, mostrar "Pendiente"
            tiempo = "Pendiente"
        lista_pedidos.append({"pedido": p, "tiempo": tiempo})
    
    # Obtener la zona horaria del restaurante
    restaurante = Restaurante.query.get(restaurante_id)
    zona_horaria = restaurante.zona_horaria if restaurante else 'UTC'
    
    return render_template("cocina.html", lista_pedidos=lista_pedidos, zona_horaria=zona_horaria)

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