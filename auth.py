# auth.py - Sistema de autenticación
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from models import db, Usuario, Restaurante, ConfiguracionRestaurante, Producto
from werkzeug.security import generate_password_hash
import re
import traceback
import secrets
import smtplib
import os
from email.mime.text import MIMEText

auth_bp = Blueprint('auth', __name__, template_folder='auth')

# -------- EMAIL --------
def enviar_email_confirmacion(email, token):
    try:
        # Obtener credenciales de email
        mail_username = current_app.config.get("MAIL_USERNAME") or os.environ.get("MAIL_USERNAME")
        mail_password = current_app.config.get("MAIL_PASSWORD") or os.environ.get("MAIL_PASSWORD")
        
        if not mail_username or not mail_password:
            print("❌ Variables de email no configuradas para confirmación")
            return
        
        msg = MIMEText(f"Confirma tu cuenta ingresando a: {url_for('auth.confirmar', token=token, _external=True)}")
        msg['Subject'] = 'Confirma tu cuenta'
        msg['From'] = mail_username
        msg['To'] = email

        with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as server:
            server.starttls()
            server.login(mail_username, mail_password)
            server.send_message(msg)
            print(f"✅ Email de confirmación enviado a {email}")
    except Exception as e:
        print(f"❌ Error enviando email de confirmación: {e}")

def enviar_email_contacto_plan(nombre, email, restaurante, plan_solicitado, mensaje):
    """Envía email de solicitud de cambio de plan al administrador"""
    try:
        # Verificar que las variables de entorno estén configuradas
        mail_username = current_app.config.get("MAIL_USERNAME") or os.environ.get("MAIL_USERNAME")
        mail_password = current_app.config.get("MAIL_PASSWORD") or os.environ.get("MAIL_PASSWORD")
        
        if not mail_username or not mail_password:
            error_msg = "Variables de entorno MAIL_USERNAME o MAIL_PASSWORD no configuradas"
            print(f"❌ {error_msg}")
            print(f"📧 MAIL_USERNAME disponible: {bool(mail_username)}")
            print(f"📧 MAIL_PASSWORD disponible: {bool(mail_password)}")
            raise ValueError(error_msg)
        
        print(f"📧 Configuración de email encontrada: {mail_username}")
        
        # Crear contenido del email
        contenido = f"""
        === SOLICITUD DE CAMBIO DE PLAN ===
        
        Nombre: {nombre}
        Email: {email}
        Restaurante: {restaurante}
        Plan solicitado: {plan_solicitado}
        
        Mensaje:
        {mensaje}
        
        ===================================
        
        Este email fue enviado desde el sistema de gestión de restaurantes.
        """
        
        msg = MIMEText(contenido)
        msg['Subject'] = f'Solicitud de cambio de plan - {restaurante}'
        msg['From'] = mail_username
        msg['To'] = "abalito95@gmail.com"  # Tu email de administrador
        
        print("📧 Conectando a servidor SMTP...")
        
        # Enviar email con timeout y mejor manejo de errores
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as server:
            print("📧 Iniciando conexión TLS...")
            server.starttls()
            
            print("📧 Autenticando...")
            server.login(mail_username, mail_password)
            
            print("📧 Enviando mensaje...")
            server.send_message(msg)
            
        print(f"✅ Email de contacto enviado exitosamente a abalito95@gmail.com")
        
    except smtplib.SMTPAuthenticationError as e:
        error_msg = f"Error de autenticación SMTP: {e}"
        print(f"❌ {error_msg}")
        raise ValueError(error_msg)
    except smtplib.SMTPException as e:
        error_msg = f"Error SMTP: {e}"
        print(f"❌ {error_msg}")
        raise ValueError(error_msg)
    except Exception as e:
        error_msg = f"Error inesperado enviando email: {e}"
        print(f"❌ {error_msg}")
        raise ValueError(error_msg)

def validar_email(email):
    return re.match(r'^[^@]+@[^@]+\.[^@]+$', email) is not None


def crear_slug(nombre):
    """Crea un slug URL-friendly desde el nombre del restaurante"""
    slug = re.sub(r'[^a-zA-Z0-9\s-]', '', nombre.lower())
    slug = re.sub(r'\s+', '-', slug)
    slug = slug[:50]
    
    # Verificar si el slug ya existe y agregar número si es necesario
    base_slug = slug
    counter = 1
    while Restaurante.query.filter_by(slug=slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    return slug


# -------- LOGIN --------
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')

            usuario = Usuario.query.filter_by(email=email).first()
            if not usuario or not usuario.check_password(password):
                flash('Email o contraseña incorrectos', 'error')
                return render_template('auth/login.html')
            
            if not usuario.confirmado:
                flash('Debes confirmar tu cuenta antes de ingresar', 'error')
                return render_template('auth/login.html')

            if not usuario.activo:
                flash('Tu cuenta está deshabilitada, contacta soporte', 'error')
                return render_template('auth/login.html')

            login_user(usuario)
            session['restaurante_id'] = usuario.restaurante.id if usuario.restaurante else None
            return redirect(url_for('index_redirect'))

        return render_template('auth/login.html')
    except Exception as e:
        import traceback
        print(f"Error en login: {e}")
        traceback.print_exc()
        flash(f'Error interno del servidor: {str(e)}', 'error')
        return render_template('auth/login.html')


# -------- REGISTRO --------
@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    try:
        if request.method == 'POST':
            print("=== INICIO REGISTRO ===")
            
            nombre = request.form.get('nombre', '').strip()
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            confirmar_password = request.form.get('confirmar_password', '')
            nombre_restaurante = request.form.get('nombre_restaurante', '').strip()
            
            print(f"Datos recibidos: nombre={nombre}, email={email}, restaurante={nombre_restaurante}")

            if not validar_email(email):
                flash('Email inválido', 'error')
                return render_template('auth/registro.html')

            if Usuario.query.filter_by(email=email).first():
                flash('Email ya registrado', 'error')
                return render_template('auth/registro.html')

            print("Creando restaurante...")
            # Crear restaurante
            slug = crear_slug(nombre_restaurante)
            print(f"Slug generado: {slug}")
            
            restaurante = Restaurante(nombre=nombre_restaurante, slug=slug, email_contacto=email)
            db.session.add(restaurante)
            db.session.flush()
            print(f"Restaurante creado con ID: {restaurante.id}")

            print("Creando usuario...")
            # Crear usuario
            token = secrets.token_urlsafe(32)
            usuario = Usuario(
            nombre=nombre, email=email,
            es_superadmin=False,  # <-- Solo el registro inicial o desde admin puede ser superadmin
            restaurante_id=restaurante.id,
            confirmado=False, activo=False, token_confirmacion=token
)
            usuario.set_password(password)
            db.session.add(usuario)
            db.session.commit()
            print(f"Usuario creado con ID: {usuario.id}")

            print("Enviando email...")
            # Enviar email de confirmación
            try:
                enviar_email_confirmacion(email, token)
                flash('Registro exitoso. Revisa tu correo para confirmar tu cuenta.', 'success')
                print("Email enviado exitosamente")
            except Exception as e:
                print(f"Error enviando email: {e}")
                flash('Registro exitoso pero error enviando email. Contacta soporte.', 'warning')
            
            print("=== REGISTRO COMPLETADO ===")
            return redirect(url_for('auth.login'))

        return render_template('auth/registro.html')
    except Exception as e:
        import traceback
        print(f"=== ERROR EN REGISTRO ===")
        print(f"Error: {e}")
        print("Traceback completo:")
        traceback.print_exc()
        print("=== FIN ERROR ===")
        db.session.rollback()
        flash(f'Error interno del servidor: {str(e)}', 'error')
        return render_template('auth/registro.html')

# -------- CONFIRMACION --------
@auth_bp.route('/confirmar/<token>')
def confirmar(token):
    usuario = Usuario.query.filter_by(token_confirmacion=token).first()
    if usuario:
        usuario.confirmado = True
        usuario.activo = True
        usuario.token_confirmacion = None
        db.session.commit()
        flash('Cuenta confirmada, ya puedes iniciar sesión', 'success')
        return redirect(url_for('auth.login'))
    flash('Token inválido', 'error')
    return redirect(url_for('auth.login'))

@auth_bp.route('/resend_confirm', methods=['GET', 'POST'])
def resend_confirm():
    """Reenviar email de confirmación"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario and not usuario.confirmado:
            # Generar nuevo token
            token = secrets.token_urlsafe(32)
            usuario.token_confirmacion = token
            db.session.commit()
            
            # Enviar email (simulado por ahora)
            print(f"Email de confirmación enviado a {email} con token: {token}")
            flash('Email de confirmación reenviado', 'success')
        else:
            flash('Email no encontrado o ya confirmado', 'error')
    
    return render_template('auth/resend_confirm.html')

# -------- SUPERADMIN PANEL --------
@auth_bp.route('/admin/usuarios')
@login_required
def admin_usuarios():
    if not current_user.es_superadmin:
        flash("Acceso denegado", "error")
        return redirect(url_for("index_redirect"))
    
    usuarios = Usuario.query.all()
    return render_template("auth/superadmin_usuarios.html", usuarios=usuarios)

@auth_bp.route('/admin/usuarios/toggle/<int:id>')
@login_required
def admin_toggle_usuario(id):
    if not current_user.es_superadmin:
        flash("Acceso denegado", "error")
        return redirect(url_for("index_redirect"))
    usuario = Usuario.query.get_or_404(id)
    usuario.activo = not usuario.activo
    db.session.commit()
    flash("Estado actualizado", "success")
    return redirect(url_for("auth.admin_usuarios"))

@auth_bp.route('/admin/usuarios/crear', methods=['GET', 'POST'])
@login_required
def admin_crear_usuario():
    """Crear nuevo usuario desde panel de superadmin"""
    if not current_user.es_superadmin:
        flash("Acceso denegado", "error")
        return redirect(url_for("index_redirect"))
    
    try:
        if request.method == 'POST':
            nombre = request.form.get('nombre', '').strip()
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            restaurante_id = request.form.get('restaurante_id')
            es_admin = 'es_admin' in request.form
            es_superadmin = 'es_superadmin' in request.form
            
            if not all([nombre, email, password]):
                flash('Nombre, email y contraseña son obligatorios', 'error')
                return render_template('auth/crear_usuario.html')
            
            if Usuario.query.filter_by(email=email).first():
                flash('Email ya registrado', 'error')
                return render_template('auth/crear_usuario.html')
            
            # Verificar límites del plan para usuarios
            if restaurante_id:
                restaurante = Restaurante.query.get(restaurante_id)
                if restaurante:
                    can_add, remaining = restaurante.can_add_user()
                    if not can_add:
                        flash(f'No se pueden agregar más usuarios. Límite del plan alcanzado ({restaurante.get_plan_limits()["usuarios"]} usuarios).', 'error')
                        return render_template('auth/crear_usuario.html')
            
            # Manejar creación de nuevo restaurante
            if restaurante_id == 'nuevo':
                nombre_restaurante = request.form.get('nombre_restaurante', '').strip()
                zona_horaria = request.form.get('zona_horaria', 'America/Argentina/Buenos_Aires')
                direccion = request.form.get('direccion_restaurante', '').strip()
                telefono = request.form.get('telefono_restaurante', '').strip()
                
                if not nombre_restaurante:
                    flash('Nombre del restaurante es obligatorio', 'error')
                    return render_template('auth/crear_usuario.html')
                
                # Crear nuevo restaurante
                slug = crear_slug(nombre_restaurante)
                restaurante = Restaurante(
                    nombre=nombre_restaurante,
                    slug=slug,
                    direccion=direccion,
                    telefono=telefono,
                    zona_horaria=zona_horaria,
                    plan="free"
                )
                db.session.add(restaurante)
                db.session.flush()  # Para obtener el ID
                restaurante_id = restaurante.id
                
                # Crear configuración inicial para el restaurante
                config = ConfiguracionRestaurante(restaurante_id=restaurante.id)
                db.session.add(config)
                
                flash(f'Restaurante "{nombre_restaurante}" creado exitosamente', 'success')
            elif restaurante_id:
                restaurante_id = int(restaurante_id)
            else:
                restaurante_id = None
            
            usuario = Usuario(
                nombre=nombre,
                email=email,
                es_admin=es_admin,
                es_superadmin=es_superadmin,
                restaurante_id=restaurante_id,
                activo=True,
                confirmado=True  # No requiere confirmación por email
            )
            usuario.set_password(password)
            db.session.add(usuario)
            db.session.commit()
            
            flash('Usuario creado exitosamente', 'success')
            return redirect(url_for('auth.admin_usuarios'))
        
        # GET: mostrar formulario
        restaurantes = Restaurante.query.all()
        return render_template('auth/crear_usuario.html', restaurantes=restaurantes)
        
    except Exception as e:
        import traceback
        print(f"Error creando usuario: {e}")
        traceback.print_exc()
        db.session.rollback()
        flash(f'Error creando usuario: {str(e)}', 'error')
        return render_template('auth/crear_usuario.html')

@auth_bp.route('/admin/cambiar_rol/<int:user_id>', methods=['POST'])
@login_required
def superadmin_cambiar_rol(user_id):
    if not current_user.es_superadmin:
        flash("Acceso denegado", "error")
        return redirect(url_for("index_redirect"))
    
    usuario = Usuario.query.get_or_404(user_id)
    rol = request.form.get('rol')
    
    if rol == 'superadmin':
        usuario.es_superadmin = True
    else:  # usuario
        usuario.es_superadmin = False
    
    db.session.commit()
    flash(f"Rol de {usuario.nombre} cambiado a {rol}", "success")
    return redirect(url_for("auth.admin_usuarios"))

@auth_bp.route('/admin/toggle_activo/<int:user_id>', methods=['POST'])
@login_required
def superadmin_toggle_activo(user_id):
    if not current_user.es_superadmin:
        flash("Acceso denegado", "error")
        return redirect(url_for("index_redirect"))
    
    usuario = Usuario.query.get_or_404(user_id)
    usuario.activo = not usuario.activo
    db.session.commit()
    flash(f"Estado de {usuario.nombre} cambiado", "success")
    return redirect(url_for("auth.admin_usuarios"))

@auth_bp.route('/admin/resetpass/<int:user_id>', methods=['POST'])
@login_required
def superadmin_resetpass(user_id):
    if not current_user.es_superadmin:
        flash("Acceso denegado", "error")
        return redirect(url_for("index_redirect"))
    
    usuario = Usuario.query.get_or_404(user_id)
    nueva_pass = request.form.get('nueva')
    
    if nueva_pass and len(nueva_pass) >= 6:
        usuario.set_password(nueva_pass)
        db.session.commit()
        flash(f"Contraseña de {usuario.nombre} actualizada", "success")
    else:
        flash("La contraseña debe tener al menos 6 caracteres", "error")
    
    return redirect(url_for("auth.admin_usuarios"))

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


@auth_bp.route("/configuracion", methods=["GET", "POST"])
@login_required
def configuracion():
    # Verificar que el usuario tenga restaurante
    if not current_user.restaurante:
        flash('Usuario sin restaurante asignado', 'error')
        return redirect(url_for('index_redirect'))

    # Obtener o crear configuración
    config = current_user.restaurante.configuracion
    if not config:
        try:
            config = ConfiguracionRestaurante(
                restaurante_id=current_user.restaurante.id,
                impresora_habilitada=False,
                impresora_tipo='USB',
                impresora_ip='',
                impresora_puerto=9100,
                tema='default',
                mostrar_precios=True
            )
            db.session.add(config)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear configuración inicial: {str(e)}', 'error')
            # Pasamos un objeto temporal para que no falle la plantilla
            class TempConfig:
                impresora_habilitada = False
                impresora_tipo = 'USB'
                impresora_ip = ''
                impresora_puerto = 9100
                tema = 'default'
                mostrar_precios = True
            config = TempConfig()

    # Permitir POST si es admin, superadmin o usuario normal
    if request.method == 'POST':
        try:
            config.impresora_habilitada = 'impresora_habilitada' in request.form
            config.impresora_tipo = request.form.get('impresora_tipo', 'USB')
            config.impresora_ip = request.form.get('impresora_ip', '')
            puerto_str = request.form.get('impresora_puerto', '').strip()
            config.impresora_puerto = int(puerto_str) if puerto_str.isdigit() else 9100
            config.tema = request.form.get('tema', 'default')
            config.mostrar_precios = 'mostrar_precios' in request.form

            current_user.restaurante.nombre = request.form.get('nombre_restaurante', '')
            current_user.restaurante.direccion = request.form.get('direccion', '')
            current_user.restaurante.telefono = request.form.get('telefono', '')
            current_user.restaurante.moneda = request.form.get('moneda', '$')

            db.session.commit()
            flash('Configuración actualizada', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar configuración: {str(e)}', 'error')

    return render_template("auth/configuracion.html", config=config, es_superadmin=current_user.es_superadmin)

@auth_bp.route('/admin/usuarios/eliminar/<int:user_id>', methods=['POST'])
@login_required
def eliminar_usuario(user_id):
    if not current_user.es_superadmin:
        flash("Acceso denegado", "error")
        return redirect(url_for("index_redirect"))
    usuario = Usuario.query.get_or_404(user_id)
    if usuario.id == current_user.id:
        flash("No puedes eliminar tu propio usuario.", "error")
        return redirect(url_for("auth.admin_usuarios"))
    db.session.delete(usuario)
    db.session.commit()
    flash(f"Usuario {usuario.nombre} eliminado.", "success")
    return redirect(url_for("auth.admin_usuarios"))

@auth_bp.route('/admin/planes')
@login_required
def admin_planes():
    """Panel de administración de planes para superadmin"""
    if not current_user.es_superadmin:
        flash("Acceso denegado", "error")
        return redirect(url_for("index_redirect"))
    
    # Obtener todos los restaurantes con información de uso
    restaurantes = Restaurante.query.all()
    restaurantes_info = []
    
    for restaurante in restaurantes:
        limits = restaurante.get_plan_limits()
        usage = restaurante.get_usage_stats()
        restaurantes_info.append({
            'restaurante': restaurante,
            'limits': limits,
            'usage': usage
        })
    
    # Obtener todos los planes disponibles
    all_plans = {
        'free': {
            'nombre': 'Free',
            'descripcion': 'Plan gratuito con limitaciones básicas',
            'productos': 10,
            'usuarios': 1,
            'pedidos_dia': 50,
            'precio': 'Gratis'
        },
        'premium1': {
            'nombre': 'Premium 1',
            'descripcion': 'Plan intermedio para restaurantes pequeños',
            'productos': 30,
            'usuarios': 3,
            'pedidos_dia': 200,
            'precio': '$29/mes'
        },
        'premium_full': {
            'nombre': 'Premium Full',
            'descripcion': 'Plan completo para restaurantes grandes',
            'productos': 'Ilimitado',
            'usuarios': 10,
            'pedidos_dia': 'Ilimitado',
            'precio': '$99/mes'
        }
    }
    
    return render_template('auth/admin_planes.html', 
                         restaurantes_info=restaurantes_info,
                         all_plans=all_plans)

@auth_bp.route('/admin/cambiar_plan_restaurante/<int:restaurante_id>/<plan>')
@login_required
def admin_cambiar_plan_restaurante(restaurante_id, plan):
    """Cambiar el plan de un restaurante desde el panel de admin"""
    if not current_user.es_superadmin:
        flash("Acceso denegado", "error")
        return redirect(url_for("auth.admin_planes"))
    
    restaurante = Restaurante.query.get_or_404(restaurante_id)
    planes_validos = ['free', 'premium1', 'premium_full']
    
    if plan not in planes_validos:
        flash('Plan inválido', 'error')
        return redirect(url_for('auth.admin_planes'))
    
    try:
        restaurante.plan = plan
        db.session.commit()
        flash(f'Plan de {restaurante.nombre} cambiado a {plan} exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error cambiando plan: {str(e)}', 'error')
    
    return redirect(url_for('auth.admin_planes'))

@auth_bp.route('/soy_superadmin')
@login_required
def soy_superadmin():
    return f"Usuario: {current_user.email} | es_superadmin: {current_user.es_superadmin}"

@auth_bp.route('/planes')
@login_required
def planes():
    """Página de gestión de planes"""
    if not current_user.restaurante:
        flash('Usuario sin restaurante asignado', 'error')
        return redirect(url_for('index_redirect'))
    
    restaurante = current_user.restaurante
    limits = restaurante.get_plan_limits()
    usage = restaurante.get_usage_stats()
    
    # Obtener todos los planes disponibles
    all_plans = {
        'free': {
            'nombre': 'Free',
            'descripcion': 'Plan gratuito con limitaciones básicas',
            'productos': 10,
            'usuarios': 1,
            'pedidos_dia': 50,
            'precio': 'Gratis'
        },
        'premium1': {
            'nombre': 'Premium 1',
            'descripcion': 'Plan intermedio para restaurantes pequeños',
            'productos': 30,
            'usuarios': 3,
            'pedidos_dia': 200,
            'precio': '$29/mes'
        },
        'premium_full': {
            'nombre': 'Premium Full',
            'descripcion': 'Plan completo para restaurantes grandes',
            'productos': 'Ilimitado',
            'usuarios': 10,
            'pedidos_dia': 'Ilimitado',
            'precio': '$99/mes'
        }
    }
    
    return render_template('auth/planes.html', 
                         restaurante=restaurante,
                         limits=limits,
                         usage=usage,
                         all_plans=all_plans)

@auth_bp.route('/cambiar_plan/<plan>')
@login_required
def cambiar_plan(plan):
    """Cambiar el plan del restaurante (solo superadmin)"""
    if not current_user.es_superadmin:
        flash('Solo superadmins pueden cambiar planes', 'error')
        return redirect(url_for('auth.planes'))
    
    if not current_user.restaurante:
        flash('Usuario sin restaurante asignado', 'error')
        return redirect(url_for('index_redirect'))
    
    planes_validos = ['free', 'premium1', 'premium_full']
    if plan not in planes_validos:
        flash('Plan inválido', 'error')
        return redirect(url_for('auth.planes'))
    
    try:
        current_user.restaurante.plan = plan
        db.session.commit()
        flash(f'Plan cambiado a {plan} exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error cambiando plan: {str(e)}', 'error')
    
    return redirect(url_for('auth.planes'))

@auth_bp.route('/contacto_plan', methods=['GET', 'POST'])
@login_required
def contacto_plan():
    """Formulario de contacto para solicitar cambio de plan"""
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        email = request.form.get('email', '').strip()
        restaurante = request.form.get('restaurante', '').strip()
        plan_solicitado = request.form.get('plan_solicitado', '').strip()
        mensaje = request.form.get('mensaje', '').strip()
        
        if not all([nombre, email, restaurante, plan_solicitado, mensaje]):
            flash('Todos los campos son obligatorios', 'error')
            return render_template('auth/contacto_plan.html')
        
        try:
            # Enviar email real al administrador
            enviar_email_contacto_plan(nombre, email, restaurante, plan_solicitado, mensaje)
            flash('Solicitud enviada exitosamente. Te contactaremos pronto.', 'success')
        except ValueError as e:
            print(f"❌ Error de configuración o SMTP: {e}")
            flash(f'Error enviando email: {str(e)}. Contacta soporte técnico.', 'error')
        except Exception as e:
            print(f"❌ Error inesperado enviando email: {e}")
            flash('Solicitud enviada pero hubo un error enviando el email. Te contactaremos por otros medios.', 'warning')
        
        return redirect(url_for('auth.planes'))
    
    return render_template('auth/contacto_plan.html')

@auth_bp.route('/usuarios_restaurante')
@login_required
def usuarios_restaurante():
    """Ver usuarios del restaurante actual"""
    if not current_user.restaurante:
        flash('Usuario sin restaurante asignado', 'error')
        return redirect(url_for('index_redirect'))
    
    usuarios_info = current_user.restaurante.get_usuarios_info()
    limits = current_user.restaurante.get_plan_limits()
    
    return render_template('auth/usuarios_restaurante.html', 
                         usuarios=usuarios_info,
                         limits=limits,
                         restaurante=current_user.restaurante)