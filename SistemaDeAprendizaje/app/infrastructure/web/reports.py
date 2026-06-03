"""
Blueprint de Reportes y Estadísticas - LogicWeb UTA
Controlador Flask para mostrar el cuadro de mando (Dashboard) del estudiante, insignias ganadas y el historial general de envíos.
"""

from flask import Blueprint, render_template, g
from app.infrastructure.web.auth import login_required
from app.infrastructure.database.repositories import SqliteEjercicioRepository, SqliteIntentoRepository
from app.application.use_cases.report_use_cases import ObtenerHistorialUsuarioUseCase, ObtenerEstadisticasUsuarioUseCase

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Recupera y compila todas las estadísticas e historial de intentos
    para renderizar un Dashboard interactivo y visualmente rico para el estudiante.
    """
    ejercicio_repo = SqliteEjercicioRepository()
    intento_repo = SqliteIntentoRepository()
    
    # 1. Recuperar el historial completo de intentos del estudiante
    historial_use_case = ObtenerHistorialUsuarioUseCase(intento_repo)
    intentos = historial_use_case.ejecutar(g.usuario.id)
    
    # 2. Compilar métricas e insignias gamificadas
    stats_use_case = ObtenerEstadisticasUsuarioUseCase(intento_repo, ejercicio_repo)
    stats = stats_use_case.ejecutar(g.usuario.id)
    
    # Mapear los ejercicios para asociar títulos en la tabla del historial
    ejercicios = {e.id: e for e in ejercicio_repo.obtener_todos()}

    # Agrupar intentos por ejercicio para una vista más organizada y resumida
    from collections import defaultdict
    intentos_por_ejercicio = defaultdict(list)
    for intento in intentos:
        intentos_por_ejercicio[intento.ejercicio_id].append(intento)
        
    grouped_history = []
    for ej_id, attempts in intentos_por_ejercicio.items():
        ej = ejercicios.get(ej_id)
        # Ordenar intentos del ejercicio de más nuevo a más viejo
        attempts.sort(key=lambda x: x.id, reverse=True)
        
        total = len(attempts)
        exitos = sum(1 for a in attempts if a.estado_oj == 'AC')
        fracasos = total - exitos
        resuelto = exitos > 0
        ultimo_intento = attempts[0].fecha_intento
        
        grouped_history.append({
            "ejercicio_id": ej_id,
            "titulo": ej.titulo if ej else f"Desafío #{ej_id}",
            "unidad_id": ej.unidad_id if ej else "-",
            "total_intentos": total,
            "exitos": exitos,
            "fracasos": fracasos,
            "resuelto": resuelto,
            "ultimo_intento": ultimo_intento,
            "intentos_detalle": attempts
        })
        
    # Ordenar historial agrupado por la fecha del último intento descending
    grouped_history.sort(key=lambda x: x["ultimo_intento"], reverse=True)

    return render_template(
        'reports/dashboard.html',
        intentos=intentos,
        stats=stats,
        ejercicios=ejercicios,
        grouped_history=grouped_history
    )
