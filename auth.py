# auth.py - Sistema de autenticación con debug
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from models import db, Usuario, Restaurante, ConfiguracionRestaurante, Producto
from werkzeug.security import generate_password_hash
import re
import traceback
import secrets
import smtplib
from email.mime.text import MIMEText

auth_bp = Blueprint('auth', __name__, template_folder='auth')

# -------- EMAIL --------
def enviar_email_confirmacion(email, token):
    try:
        msg = MIMEText(f"Confirma tu cuenta ingresando a: {url_for('auth.confirmar', token=token, _external=True)}")
        msg['Subject'] = 'Confirma tu cuenta'
        msg['From'] = current_app.config.get("MAIL_USERNAME", "no-reply@miapp.com")
        msg['To'] = email

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(current_app.config["MAIL_USERNAME"], current_app.config["MAIL_PASSWORD"])
            server.send_message(msg)
    except Exception as e:
        print("Error enviando email:", e)

def validar_email(email):
    return re.match(r'^[^@]+@[^@]+\.[^@]+$', email) is not None


def crear_slug(nombre):
    """Crea un slug URL-friendly desde el nombre del restaurante"""
    slug = re.sub(r'[^a-zA-Z0-9\s-]', '', nombre.lower())
    slug = re.sub(r'\s+', '-', slug)
    return slug[:50]


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
            nombre = request.form.get('nombre', '').strip()
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            confirmar_password = request.form.get('confirmar_password', '')
            nombre_restaurante = request.form.get('nombre_restaurante', '').strip()

            if not validar_email(email):
                flash('Email inválido', 'error')
                return render_template('auth/registro.html')

            if Usuario.query.filter_by(email=email).first():
                flash('Email ya registrado', 'error')
                return render_template('auth/registro.html')

            # Crear restaurante
            slug = crear_slug(nombre_restaurante)
            restaurante = Restaurante(nombre=nombre_restaurante, slug=slug, email_contacto=email)
            db.session.add(restaurante)
            db.session.flush()

            # Crear usuario
            token = secrets.token_urlsafe(32)
            usuario = Usuario(
                nombre=nombre, email=email,
                es_admin=True, restaurante_id=restaurante.id,
                confirmado=False, activo=False, token_confirmacion=token
            )
            usuario.set_password(password)
            db.session.add(usuario)
            db.session.commit()

            # Enviar email de confirmación
            try:
                enviar_email_confirmacion(email, token)
                flash('Registro exitoso. Revisa tu correo para confirmar tu cuenta.', 'success')
            except Exception as e:
                print(f"Error enviando email: {e}")
                flash('Registro exitoso pero error enviando email. Contacta soporte.', 'warning')
            return redirect(url_for('auth.login'))

        return render_template('auth/registro.html')
    except Exception as e:
        import traceback
        print(f"Error en registro: {e}")
        traceback.print_exc()
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
    return render_template("auth/admin_usuarios.html", usuarios=usuarios)

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

    # Solo permitir POST si es admin
    if request.method == 'POST' and current_user.es_admin:
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

    return render_template("auth/configuracion.html", config=config, es_admin=current_user.es_admin)
