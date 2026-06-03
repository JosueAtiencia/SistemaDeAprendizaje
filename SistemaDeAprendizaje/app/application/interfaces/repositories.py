"""
Interfaces de Repositorio - LogicWeb UTA
Contratos abstractos que debe cumplir cualquier adaptador de persistencia (ej. SQLite, PostgreSQL, en memoria).
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities import Usuario, Ejercicio, Intento

class UsuarioRepository(ABC):
    
    @abstractmethod
    def obtener_por_id(self, usuario_id: int) -> Optional[Usuario]:
        """Recupera un usuario por su clave primaria."""
        pass
        
    @abstractmethod
    def obtener_por_username(self, username: str) -> Optional[Usuario]:
        """Recupera un usuario por su nombre de usuario."""
        pass
        
    @abstractmethod
    def obtener_por_email(self, email: str) -> Optional[Usuario]:
        """Recupera un usuario por su correo electrónico."""
        pass
        
    @abstractmethod
    def guardar(self, usuario: Usuario) -> Usuario:
        """Guarda o actualiza un usuario en la base de datos."""
        pass


class EjercicioRepository(ABC):
    
    @abstractmethod
    def obtener_por_id(self, ejercicio_id: int) -> Optional[Ejercicio]:
        """Recupera un ejercicio por su clave primaria."""
        pass
        
    @abstractmethod
    def obtener_todos(self) -> List[Ejercicio]:
        """Recupera la lista de todos los ejercicios del sistema."""
        pass
        
    @abstractmethod
    def guardar(self, ejercicio: Ejercicio) -> Ejercicio:
        """Guarda o actualiza un ejercicio."""
        pass


class IntentoRepository(ABC):
    
    @abstractmethod
    def obtener_por_id(self, intento_id: int) -> Optional[Intento]:
        """Recupera un intento específico."""
        pass
        
    @abstractmethod
    def obtener_por_usuario(self, usuario_id: int) -> List[Intento]:
        """Recupera el historial de intentos de un estudiante ordenados por fecha descendente."""
        pass
        
    @abstractmethod
    def obtener_por_usuario_y_ejercicio(self, usuario_id: int, ejercicio_id: int) -> List[Intento]:
        """Recupera los intentos de un usuario para un ejercicio particular."""
        pass

    @abstractmethod
    def obtener_estadisticas_usuario(self, usuario_id: int) -> dict:
        """Calcula métricas agregadas del estudiante (tasa de acierto, intentos, etc.)."""
        pass
        
    @abstractmethod
    def guardar(self, intento: Intento) -> Intento:
        """Guarda un intento de resolución en el historial."""
        pass
