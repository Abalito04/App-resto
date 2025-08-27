# auth.py - Sistema de autenticación
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from models import db, Usuario, Restaurante, ConfiguracionRestaurante, Producto
from werkzeug.security import generate_password_hash
import re

auth_bp = Blueprint('auth', __name__, template_folder='auth')


def validar_email(email):
    """Valida formato de email"""
    return re.match(r'^[^@]+@[^@]+\.[^@]+$', email) is not None

def crear_slug(nombre):
    """Crea un slug URL-friendly desde el nombre del restaurante"""
    slug = re.sub(r'[^a-zA-Z0-9\s-]', '', nombre.lower())
    slug = re.sub(r'\s+', '-', slug)
    return slug[:50]

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Email y contraseña son obligatorios', 'error')
            return render_template('auth/login.html')
        
        usuario = Usuario.query.filter_by(email=email, activo=True).first()
        
        if usuario and usuario.check_password(password):
            if not usuario.restaurante.activo:
                flash('Restaurante desactivado. Contacta soporte.', 'error')
                return render_template('auth/login.html')
            
            login_user(usuario)
            session['restaurante_id'] = usuario.restaurante.id
            
            # 🔹 Redirigir al index_redirect que maneja la lógica de inicio
            return redirect(url_for('index_redirect'))
        else:
            flash('Email o contraseña incorrectos', 'error')
    
    return render_template('auth/login.html')


@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        # Datos del usuario
        nombre = request.form.get('nombre', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirmar_password = request.form.get('confirmar_password', '')
        
        # Datos del restaurante
        nombre_restaurante = request.form.get('nombre_restaurante', '').strip()
        direccion = request.form.get('direccion', '').strip()
        telefono = request.form.get('telefono', '').strip()
        
        # Validaciones
        errores = []
        
        if not nombre or len(nombre) < 2:
            errores.append('Nombre debe tener al menos 2 caracteres')
        
        if not validar_email(email):
            errores.append('Email inválido')
        
        if Usuario.query.filter_by(email=email).first():
            errores.append('Email ya registrado')
        
        if not password or len(password) < 6:
            errores.append('Contraseña debe tener al menos 6 caracteres')
        
        if password != confirmar_password:
            errores.append('Las contraseñas no coinciden')
        
        if not nombre_restaurante or len(nombre_restaurante) < 2:
            errores.append('Nombre del restaurante es obligatorio')
        
        # Verificar que el slug sea único
        slug = crear_slug(nombre_restaurante)
        if Restaurante.query.filter_by(slug=slug).first():
            errores.append('Ya existe un restaurante con ese nombre. Usa uno diferente.')
        
        if errores:
            for error in errores:
                flash(error, 'error')
            return render_template('auth/registro.html')
        
        try:
            # Crear restaurante
            restaurante = Restaurante(
                nombre=nombre_restaurante,
                slug=slug,
                direccion=direccion,
                telefono=telefono,
                email_contacto=email
            )
            db.session.add(restaurante)
            db.session.flush()  # Para obtener el ID
            
            # Crear usuario administrador
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
                Producto(nombre="Agua Mineral", precio=900, restaurante_id=restaurante.id),
            ]
            db.session.add_all(productos_ejemplo)
            
            db.session.commit()
            
            flash('Registro exitoso. Ya puedes iniciar sesión.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash('Error creando cuenta. Intenta nuevamente.', 'error')
            print(f"Error en registro: {e}")
    
    return render_template('auth/registro.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('auth.login'))

@auth_bp.route('/perfil')
@login_required
def perfil():
    return render_template('auth/perfil.html', usuario=current_user)

@auth_bp.route('/configuracion', methods=['GET', 'POST'])
@login_required
def configuracion():
    if not current_user.es_admin:
        flash('Solo administradores pueden acceder a la configuración', 'error')
        return redirect(url_for('index'))
    
    config = current_user.restaurante.configuracion
    if not config:
        config = ConfiguracionRestaurante(restaurante_id=current_user.restaurante.id)
        db.session.add(config)
        db.session.commit()
    
    if request.method == 'POST':
        try:
            # Actualizar configuración
            config.impresora_habilitada = 'impresora_habilitada' in request.form
            config.impresora_tipo = request.form.get('impresora_tipo', 'USB')
            config.impresora_ip = request.form.get('impresora_ip', '')

            # Validar puerto (si viene vacío, usar 9100 por defecto)
            puerto_str = request.form.get('impresora_puerto', '').strip()
            config.impresora_puerto = int(puerto_str) if puerto_str.isdigit() else 9100

            config.tema = request.form.get('tema', 'default')
            config.mostrar_precios = 'mostrar_precios' in request.form
            
            # Actualizar datos del restaurante
            current_user.restaurante.nombre = request.form.get('nombre_restaurante', '')
            current_user.restaurante.direccion = request.form.get('direccion', '')
            current_user.restaurante.telefono = request.form.get('telefono', '')
            current_user.restaurante.moneda = request.form.get('moneda', '$')
            
            db.session.commit()
            flash('Configuración actualizada', 'success')

        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar configuración: {str(e)}', 'error')
    
    # Renderizar SIEMPRE la plantilla (para GET y POST)
    return render_template("auth/configuracion.html", config=config)

