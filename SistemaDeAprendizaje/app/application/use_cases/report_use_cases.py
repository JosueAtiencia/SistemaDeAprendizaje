"""
Casos de Uso de Reportes y Estadísticas - LogicWeb UTA
Orquesta la generación de métricas de progreso, insignias y el historial del estudiante.
"""

from typing import List, Dict, Any
from app.application.interfaces.repositories import IntentoRepository, EjercicioRepository
from app.domain.entities import Intento

class ObtenerHistorialUsuarioUseCase:
    def __init__(self, intento_repository: IntentoRepository):
        self.intento_repository = intento_repository

    def ejecutar(self, usuario_id: int) -> List[Intento]:
        """Obtiene la lista completa de intentos realizados por el estudiante."""
        return self.intento_repository.obtener_por_usuario(usuario_id)


class ObtenerEstadisticasUsuarioUseCase:
    def __init__(self, intento_repository: IntentoRepository, ejercicio_repository: EjercicioRepository):
        self.intento_repository = intento_repository
        self.ejercicio_repository = ejercicio_repository

    def ejecutar(self, usuario_id: int) -> Dict[str, Any]:
        """
        Calcula y compila todas las estadísticas de rendimiento y gamificación del estudiante.
        Retorna:
            - total_intentos: Número total de envíos realizados.
            - exitos_ac: Cantidad de soluciones con estado Accepted (AC).
            - ejercicios_resueltos: Set de IDs de ejercicios aprobados.
            - tasa_acierto: Porcentaje de intentos exitosos.
            - total_ejercicios: Cantidad total de ejercicios en la plataforma.
            - progreso_porcentaje: Porcentaje de avance en el mapa de aprendizaje.
            - insignias: Lista de logros/insignias desbloqueados por el estudiante.
        """
        intentos = self.intento_repository.obtener_por_usuario(usuario_id)
        ejercicios = self.ejercicio_repository.obtener_todos()
        
        total_intentos = len(intentos)
        exitos_ac = sum(1 for i in intentos if i.estado_oj == "AC")
        
        # Encontrar los IDs únicos de ejercicios que el usuario ha completado con éxito (AC)
        ejercicios_resueltos_ids = {i.ejercicio_id for i in intentos if i.estado_oj == "AC"}
        
        tasa_acierto = round((exitos_ac / total_intentos * 100), 2) if total_intentos > 0 else 0.0
        
        total_ejercicios = len(ejercicios)
        progreso_porcentaje = round((len(ejercicios_resueltos_ids) / total_ejercicios * 100), 2) if total_ejercicios > 0 else 0.0
        
        # Generación de insignias gamificadas basadas en el progreso real del estudiante
        insignias = []
        
        # Insignia 1: Primer intento (Bienvenido)
        if total_intentos > 0:
            insignias.append({
                "id": "primer_paso",
                "titulo": "Primer Paso",
                "descripcion": "Realizaste tu primer envío al Juez Online C++.",
                "icono": "bi-rocket-takeoff",
                "color": "primary"
            })
            
        # Insignia 2: Primera solución correcta (Accepted!)
        if len(ejercicios_resueltos_ids) > 0:
            insignias.append({
                "id": "codigo_limpio",
                "titulo": "Código de Plata",
                "descripcion": "Lograste resolver exitosamente tu primer ejercicio algorítmico (AC).",
                "icono": "bi-award",
                "color": "success"
            })
            
        # Insignia 3: Resolver todos los ejercicios
        if len(ejercicios_resueltos_ids) == total_ejercicios and total_ejercicios > 0:
            insignias.append({
                "id": "maestro_algoritmos",
                "titulo": "Maestro Lógico C++",
                "descripcion": "Resolviste el 100% de los desafíos del mapa de aprendizaje de LogicWeb.",
                "icono": "bi-trophy-fill",
                "color": "warning"
            })
            
        # Insignia 4: Perseverancia (Hacer más de 10 intentos)
        if total_intentos >= 10:
            insignias.append({
                "id": "perseverante",
                "titulo": "Perseverancia Pura",
                "descripcion": "Has realizado 10 o más intentos de optimización. ¡El fracaso es aprendizaje!",
                "icono": "bi-hourglass-split",
                "color": "info"
            })

        # Estructura de progreso por unidades teóricas (6 unidades con 4 ejercicios cada una)
        progreso_unidades = {}
        for u in range(1, 7):
            inicio = (u - 1) * 4 + 1
            fin = u * 4
            ids_unidad = list(range(inicio, fin + 1))
            completados = sum(1 for e in ejercicios_resueltos_ids if e in ids_unidad)
            progreso_unidades[u] = {"completados": completados, "total": 4}

        return {
            "total_intentos": total_intentos,
            "exitos_ac": exitos_ac,
            "ejercicios_resueltos_count": len(ejercicios_resueltos_ids),
            "tasa_acierto": tasa_acierto,
            "total_ejercicios": total_ejercicios,
            "progreso_porcentaje": progreso_porcentaje,
            "progreso_unidades": progreso_unidades,
            "insignias": insignias
        }
