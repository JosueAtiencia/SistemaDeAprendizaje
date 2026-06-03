"""
Blueprint de Autenticación - LogicWeb UTA
Controlador Flask para el Registro, Inicio de Sesión y Control de Accesos.
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash, session, g
from functools import wraps
from werkzeug.security import generate_password_hash
from app.infrastructure.database.repositories import SqliteUsuarioRepository
from app.application.use_cases.auth_use_cases import RegistrarUsuarioUseCase, AutenticarUsuarioUseCase
from app.domain.exceptions import LogicWebException

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Decorador para proteger rutas privadas
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash("Por favor, inicia sesión para acceder a esta sección.", "warning")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.before_app_request
def cargar_usuario_actual():
    """Carga el usuario logueado en la variable 'g' global de Flask."""
    usuario_id = session.get('usuario_id')
    if usuario_id is None:
        g.usuario = None
    else:
        repo = SqliteUsuarioRepository()
        g.usuario = repo.obtener_por_id(usuario_id)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if g.usuario:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validaciones de frontend/backend básicas
        if not username or not email or not password:
            flash("Todos los campos son obligatorios.", "danger")
            return render_template('auth/register.html')
            
        if password != confirm_password:
            flash("Las contraseñas ingresadas no coinciden.", "danger")
            return render_template('auth/register.html')
            
        try:
            repo = SqliteUsuarioRepository()
            use_case = RegistrarUsuarioUseCase(repo)
            usuario_registrado = use_case.ejecutar(username, email, password)
            
            flash(f"¡Registro exitoso! Bienvenido {usuario_registrado.username}. Inicia sesión ahora.", "success")
            return redirect(url_for('auth.login'))
        except LogicWebException as e:
            flash(e.message, "danger")
            
    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if g.usuario:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username_o_email = request.form.get('username_o_email', '').strip()
        password = request.form.get('password', '')
        
        if not username_o_email or not password:
            flash("Por favor, ingresa tus credenciales.", "danger")
            return render_template('auth/login.html')
            
        try:
            repo = SqliteUsuarioRepository()
            use_case = AutenticarUsuarioUseCase(repo)
            usuario = use_case.ejecutar(username_o_email, password)
            
            # Guardar en sesión
            session.clear()
            session['usuario_id'] = usuario.id
            session['username'] = usuario.username
            
            flash(f"¡Bienvenido de vuelta, {usuario.username}!", "success")
            return redirect(url_for('index'))
        except LogicWebException as e:
            flash(e.message, "danger")
            
    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("Has cerrado sesión correctamente. ¡Sigue aprendiendo pronto!", "info")
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Permite al estudiante actualizar sus nombres, correo y contraseña de acceso."""
    repo = SqliteUsuarioRepository()
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not username or not email:
            flash("El nombre de usuario y el correo electrónico son obligatorios.", "danger")
            return render_template('auth/profile.html')

        # Validar duplicados de usuario para otros perfiles
        existente_usr = repo.obtener_por_username(username)
        if existente_usr and existente_usr.id != g.usuario.id:
            flash("El nombre de usuario ya está registrado por otro estudiante.", "danger")
            return render_template('auth/profile.html')

        existente_mail = repo.obtener_por_email(email)
        if existente_mail and existente_mail.id != g.usuario.id:
            flash("El correo electrónico ya está registrado por otro estudiante.", "danger")
            return render_template('auth/profile.html')

        try:
            g.usuario.username = username
            # El correo electrónico está protegido y no se permite su modificación posterior
            # g.usuario.email = email 

            if password:
                if password != confirm_password:
                    flash("Las nuevas contraseñas ingresadas no coinciden.", "danger")
                    return render_template('auth/profile.html')
                g.usuario.password_hash = generate_password_hash(password)

            repo.guardar(g.usuario)
            session['username'] = g.usuario.username
            flash("¡Tus datos de perfil han sido actualizados con éxito!", "success")
            return redirect(url_for('auth.profile'))
        except Exception as e:
            flash(f"Error interno al actualizar datos: {str(e)}", "danger")

    return render_template('auth/profile.html')
