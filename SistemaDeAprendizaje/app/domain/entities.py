"""
Módulo de Entidades del Dominio - LogicWeb UTA
Contiene las clases puras que modelan el negocio de la plataforma: Usuario, Ejercicio, Intento y Feedback.
Implementa validaciones puras de negocio y de protección de estado de las entidades.
"""

import re
from datetime import datetime
from typing import Dict, Any, Optional, List
from app.domain.exceptions import IntentoInvalido

class Usuario:
    """Representa a un estudiante o administrador en el sistema."""
    def __init__(
        self,
        id: Optional[int],
        username: str,
        email: str,
        password_hash: str,
        fecha_registro: Optional[datetime] = None
    ):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.fecha_registro = fecha_registro or datetime.utcnow()
        self.validar_entidad()

    def validar_entidad(self) -> None:
        """Asegura la consistencia estructural del usuario en el dominio."""
        if not self.username or len(self.username.strip()) < 3:
            raise IntentoInvalido("El nombre de usuario debe tener al menos 3 caracteres.")
        
        # Expresión regular simple para validar formato de correo electrónico
        patron_email = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not self.email or not re.match(patron_email, self.email):
            raise IntentoInvalido("El formato del correo electrónico ingresado es inválido.")

    def __repr__(self) -> str:
        return f"<Usuario {self.username} (ID: {self.id})>"


class Ejercicio:
    """Representa un problema algorítmico o ejercicio interactivo en C++."""
    def __init__(
        self,
        id: Optional[int],
        unidad_id: int,
        titulo: str,
        descripcion_caso_real: str,
        pseudocodigo: str,
        diagrama_ruta: str,  # Ruta al SVG o identificador visual del diagrama
        ruta_binario_cpp: str,  # Nombre o ruta relativa del ejecutable de C++
        codigo_fuente_cpp: Optional[str] = None # Código real C++ para mostrar al estudiante
    ):
        self.id = id
        self.unidad_id = unidad_id
        self.titulo = titulo
        self.descripcion_caso_real = descripcion_caso_real
        self.pseudocodigo = pseudocodigo
        self.diagrama_ruta = diagrama_ruta
        self.ruta_binario_cpp = ruta_binario_cpp
        self.codigo_fuente_cpp = codigo_fuente_cpp
        self.validar_entidad()

    def validar_entidad(self) -> None:
        """Garantiza la consistencia básica de un ejercicio en el catálogo."""
        if not self.titulo or len(self.titulo.strip()) == 0:
            raise IntentoInvalido("El título del ejercicio es requerido.")
        if self.unidad_id <= 0:
            raise IntentoInvalido("El ejercicio debe estar asignado a una Unidad válida.")
        if not self.ruta_binario_cpp or len(self.ruta_binario_cpp.strip()) == 0:
            raise IntentoInvalido("La ruta del ejecutable C++ es requerida para procesar subprocesos.")

    def __repr__(self) -> str:
        return f"<Ejercicio {self.titulo} (ID: {self.id})>"


class Intento:
    """Representa el intento de un estudiante para resolver un ejercicio interactivo."""
    ESTADOS_VALIDOS = {"AC", "WA", "RE", "TLE"}

    def __init__(
        self,
        id: Optional[int],
        usuario_id: int,
        ejercicio_id: int,
        datos_ingresados: Dict[str, Any],  # Diccionario/JSON de entradas
        resultado_obtenido: str,          # Salida estándar (stdout) capturada
        estado_oj: str,                   # Estado del Online Judge: AC, WA, RE, TLE
        fecha_intento: Optional[datetime] = None
    ):
        self.id = id
        self.usuario_id = usuario_id
        self.ejercicio_id = ejercicio_id
        self.datos_ingresados = datos_ingresados
        self.resultado_obtenido = resultado_obtenido
        self.estado_oj = estado_oj.upper()
        self.fecha_intento = fecha_intento or datetime.utcnow()
        self.validar_entidad()

    def validar_entidad(self) -> None:
        """Valida que los estados y relaciones del intento sean lógicamente consistentes."""
        if self.estado_oj not in self.ESTADOS_VALIDOS:
            raise IntentoInvalido(f"El veredicto del juez '{self.estado_oj}' es desconocido en el dominio.")
        if self.usuario_id <= 0:
            raise IntentoInvalido("El intento debe estar asociado a un usuario real.")
        if self.ejercicio_id <= 0:
            raise IntentoInvalido("El intento debe estar asociado a un ejercicio existente.")

    def obtener_feedback(self) -> 'Feedback':
        return Feedback.generar(self.estado_oj, self.resultado_obtenido, self.ejercicio_id, self.datos_ingresados)

    def __repr__(self) -> str:
        return f"<Intento ID: {self.id} | Ejercicio: {self.ejercicio_id} | Estado: {self.estado_oj}>"


class Feedback:
    """Genera recomendaciones didácticas y gamificadas basadas en el resultado de la evaluación."""
    
    TITULOS = {
        "AC": "¡Excelente Trabajo! Solución Aceptada (Accepted)",
        "WA": "Resultado Incorrecto (Wrong Answer)",
        "RE": "Error en Tiempo de Ejecución (Runtime Error)",
        "TLE": "Límite de Tiempo Excedido (Time Limit Exceeded)"
    }
    
    COLORES = {
        "AC": "success",
        "WA": "warning",
        "RE": "danger",
        "TLE": "danger"
    }

    def __init__(self, estado_oj: str, salida: str, recomendaciones: List[str]):
        self.estado_oj = estado_oj
        self.salida = salida
        self.titulo = self.TITULOS.get(estado_oj, "Evaluación Desconocida")
        self.color_clase = self.COLORES.get(estado_oj, "secondary")
        self.recomendaciones = recomendaciones

    @classmethod
    def generar(cls, estado_oj: str, salida: str, ejercicio_id: int, datos_ingresados: Dict[str, Any]) -> 'Feedback':
        """
        Fábrica del Dominio para generar retroalimentación didáctica específica basada en el tipo de error
        y el ejercicio evaluado.
        """
        recomendaciones = []
        
        if estado_oj == "AC":
            recomendaciones.append("Tu lógica de programación es impecable para este caso de prueba.")
            recomendaciones.append("¡Has ganado 50 puntos de experiencia (XP) y desbloqueado el siguiente nodo!")
            recomendaciones.append("Revisa la sección de 'Ejercicio Resuelto' para comparar tu lógica con alternativas óptimas.")
        elif estado_oj == "WA":
            recomendaciones.append("El programa compiló y se ejecutó con éxito, pero la salida no coincide con la esperada.")
            recomendaciones.append("Verifica si estás manejando correctamente los casos extremos (límites numéricos).")
            # Recomendaciones didácticas específicas por ejercicio
            if ejercicio_id == 1:  # Factorial
                n = int(datos_ingresados.get("n", 0))
                if n < 0:
                    recomendaciones.append("Consejo: El factorial de un número negativo no está definido en los números enteros.")
                elif n > 12:
                    recomendaciones.append("Consejo: Los números mayores a 12 superan el límite de almacenamiento de un tipo `int` común (desbordamiento).")
            elif ejercicio_id == 2:  # Año Bisiesto
                year = int(datos_ingresados.get("year", 0))
                recomendaciones.append(f"Consejo: Recuerda la regla para el año {year}. Un año es bisiesto si es divisible por 4, excepto cuando es divisible por 100, a menos que también sea divisible por 400.")
        elif estado_oj == "RE":
            recomendaciones.append("El ejecutable colapsó debido a una violación del entorno o un error aritmético.")
            recomendaciones.append("Posible División por Cero: Revisa que tus datos de entrada no obliguen a dividir para cero en el algoritmo C++.")
            recomendaciones.append("Desbordamiento de Memoria o Buffer: Revisa si el tamaño de tus inputs causó que el programa consumiera recursos inválidos.")
        elif estado_oj == "TLE":
            recomendaciones.append("El algoritmo tardó más de los 3.0 segundos permitidos en el Juez Online (Límite de Tiempo Excedido - TLE).")
            recomendaciones.append("Esto ocurre comúnmente por dos razones:")
            recomendaciones.append("1) Bucle Infinito: El ciclo repetitivo ('while' o 'for') no tiene una condición de parada correcta o su variable de control no se modifica, quedando atrapado en una repetición eterna.")
            recomendaciones.append("2) Complejidad Temporal Excesiva: Ingresaste un valor numérico extremadamente grande (como 999999999) que obliga al bucle a dar cientos de millones de vueltas, superando el tiempo de procesamiento permitido por el Juez para proteger el servidor.")
            
        return cls(estado_oj, salida, recomendaciones)
