"""
Casos de Uso de Autenticación - LogicWeb UTA
Orquesta la lógica empresarial de registro y autenticación de usuarios.
"""

from typing import Optional
from werkzeug.security import generate_password_hash, check_password_hash
from app.domain.entities import Usuario
from app.domain.exceptions import UsuarioYaExiste, CredencialesInvalidas
from app.application.interfaces.repositories import UsuarioRepository

class RegistrarUsuarioUseCase:
    def __init__(self, usuario_repository: UsuarioRepository):
        self.usuario_repository = usuario_repository

    def ejecutar(self, username: str, email: str, contrasenia: str) -> Usuario:
        """
        Registra un nuevo usuario en el sistema después de validar duplicados
        y realizar el hash seguro de la contraseña.
        """
        # Validar si ya existe el usuario por nombre o correo
        if self.usuario_repository.obtener_por_username(username) or \
           self.usuario_repository.obtener_por_email(email):
            raise UsuarioYaExiste(username, email)

        # Cifrar contraseña de manera segura
        password_hash = generate_password_hash(contrasenia)
        
        # Crear entidad pura del dominio
        nuevo_usuario = Usuario(
            id=None,
            username=username,
            email=email,
            password_hash=password_hash
        )
        
        # Guardar en repositorio de infraestructura
        return self.usuario_repository.guardar(nuevo_usuario)


class AutenticarUsuarioUseCase:
    def __init__(self, usuario_repository: UsuarioRepository):
        self.usuario_repository = usuario_repository

    def ejecutar(self, username_o_email: str, contrasenia: str) -> Usuario:
        """
        Autentica un usuario en la plataforma comparando su hash de contraseña.
        Acepta tanto el nombre de usuario como el correo electrónico.
        """
        # Buscar usuario por nombre o por correo electrónico
        usuario = self.usuario_repository.obtener_por_username(username_o_email)
        if not usuario:
            usuario = self.usuario_repository.obtener_por_email(username_o_email)

        # Validar credenciales
        if not usuario or not check_password_hash(usuario.password_hash, contrasenia):
            raise CredencialesInvalidas()

        return usuario
