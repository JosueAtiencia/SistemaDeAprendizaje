"""
Módulo de Excepciones del Dominio - LogicWeb UTA
Define las excepciones semánticas puras de negocio que no dependen de detalles de infraestructura.
"""

class LogicWebException(Exception):
    """Excepción base para todos los errores del dominio en LogicWeb UTA."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class UsuarioNoEncontrado(LogicWebException):
    """Se lanza cuando un usuario buscado no existe en el sistema."""
    def __init__(self, identifier: str):
        super().__init__(f"El usuario '{identifier}' no fue encontrado en el sistema.")


class UsuarioYaExiste(LogicWebException):
    """Se lanza cuando se intenta registrar un usuario con username o email duplicado."""
    def __init__(self, username: str, email: str):
        super().__init__(f"El usuario con nombre '{username}' o correo '{email}' ya se encuentra registrado.")


class CredencialesInvalidas(LogicWebException):
    """Se lanza cuando las credenciales de inicio de sesión son incorrectas."""
    def __init__(self) -> None:
        super().__init__("El nombre de usuario o la contraseña son incorrectos.")


class EjercicioNoEncontrado(LogicWebException):
    """Se lanza cuando un ejercicio no existe en el sistema."""
    def __init__(self, ejercicio_id: int):
        super().__init__(f"El ejercicio con ID {ejercicio_id} no fue encontrado.")


class IntentoInvalido(LogicWebException):
    """Se lanza cuando los datos de entrada de un intento no cumplen con las validaciones básicas."""
    def __init__(self, razon: str):
        super().__init__(f"Los datos del intento no son válidos: {razon}")


class RunnerError(LogicWebException):
    """Excepción base para errores de ejecución de binarios C++."""
    def __init__(self, message: str):
        super().__init__(message)


class CompilationError(RunnerError):
    """Se lanza si ocurre un error al compilar el código C++ en el servidor."""
    def __init__(self, detalles: str):
        super().__init__(f"Error de compilación de C++: {detalles}")


class TimeLimitExceeded(RunnerError):
    """Equivalente a TLE (Time Limit Exceeded) del Juez Online."""
    def __init__(self, timeout_limit: float):
        super().__init__(f"Límite de tiempo excedido (TLE). El proceso tardó más de {timeout_limit} segundos.")


class CppRuntimeError(RunnerError):
    """Equivalente a RE (Runtime Error) del Juez Online."""
    def __init__(self, exit_code: int, error_stderr: str):
        super().__init__(f"Error de ejecución (RE) con código de salida {exit_code}. Detalles: {error_stderr}")
