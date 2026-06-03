"""
Blueprint de Ejercicios Interactivos y Juez Online - LogicWeb UTA
Controlador Flask para procesar formularios interactivos, delegar ejecuciones a C++
y devolver respuestas en JSON estructurado para consumo asíncrono con Fetch API.
"""

from flask import Blueprint, render_template, request, jsonify, g, flash, redirect, url_for, current_app
from app.infrastructure.web.auth import login_required
from app.infrastructure.database.repositories import SqliteEjercicioRepository, SqliteIntentoRepository
from app.infrastructure.services.cpp_runner import SubprocessCppRunner
from app.application.use_cases.exercise_use_cases import ObtenerEjercicioPorIdUseCase, EjecutarEjercicioUseCase
from app.domain.exceptions import LogicWebException, IntentoInvalido

interactive_bp = Blueprint('interactive', __name__, url_prefix='/interactive')

# Casos de simulación específicos para orientar al estudiante según el reto del libro
SIMULACION_CASES = {
    1: {"tle": "N/A", "wa": "N/A", "re": "N/A"},
    2: {"tle": "N/A", "wa": "Ingresa letras en lugar de enteros", "re": "N/A"},
    3: {"tle": "N/A", "wa": "Ingresar grados muy extremos (ej. -99999)", "re": "N/A"},
    4: {"tle": "N/A", "wa": "Ingresa radio negativo (-5)", "re": "N/A"},
    5: {"tle": "N/A", "wa": "Ingresar edad ilógica (ej. 300)", "re": "N/A"},
    6: {"tle": "N/A", "wa": "Ingresar opción fuera de rango (ej. 9)", "re": "División por cero en opción de DIV"},
    7: {"tle": "Ingresa un número gigante (ej. 1000000000)", "wa": "Ingresa límite -10", "re": "N/A"},
    8: {"tle": "N/A", "wa": "Ingresar clave '5555' repetidamente", "re": "N/A"},
    9: {"tle": "N/A", "wa": "Ingresar valores no numéricos", "re": "N/A"},
    10: {"tle": "N/A", "wa": "Ingresar números negativos para probar el max", "re": "N/A"},
    11: {"tle": "Ingresa una cadena excesivamente larga", "wa": "N/A", "re": "Caracteres nulos o especiales"},
    12: {"tle": "N/A", "wa": "Edad negativa o nombre vacío", "re": "Sobrescritura de buffer en nombre"},
    13: {"tle": "Ingresa n=9999 (Recursión Infinita)", "wa": "n=20 (Integer Overflow)", "re": "n=-1"},
    14: {"tle": "N/A", "wa": "N/A", "re": "N/A"},
    15: {"tle": "N/A", "wa": "Base y altura negativas", "re": "N/A"},
    16: {"tle": "N/A", "wa": "Precio -5", "re": "N/A"},
    17: {"tle": "N/A", "wa": "N/A", "re": "N/A"},
    18: {"tle": "N/A", "wa": "N/A", "re": "Acceder a índice fuera del arreglo"},
    19: {"tle": "N/A", "wa": "N/A", "re": "Olvidar liberar memoria (Memory Leak)"},
    20: {"tle": "Reservar 999999999 ints", "wa": "N/A", "re": "Tamaño negativo (std::bad_alloc)"},
    21: {"tle": "Fibonacci de 50+ (Cálculo eterno)", "wa": "N/A", "re": "N/A"},
    22: {"tle": "N/A", "wa": "Buscar elemento inexistente", "re": "N/A"},
    23: {"tle": "Ciclo de escritura infinito", "wa": "N/A", "re": "Disco lleno accidental"},
    24: {"tle": "N/A", "wa": "N/A", "re": "Leer archivo no existente"}
}

@interactive_bp.route('/<int:ejercicio_id>', methods=['GET'])
@login_required
def view_interactive(ejercicio_id: int):
    """Muestra la vista de compilación e interacción del ejercicio."""
    try:
        ejercicio_repo = SqliteEjercicioRepository()
        use_case = ObtenerEjercicioPorIdUseCase(ejercicio_repo)
        ejercicio = use_case.ejecutar(ejercicio_id)
        
        # Obtener todos los intentos del estudiante para este ejercicio en particular
        intento_repo = SqliteIntentoRepository()
        ultimos_intentos = intento_repo.obtener_por_usuario_y_ejercicio(g.usuario.id, ejercicio_id)
        
    except LogicWebException as e:
        flash(e.message, "danger")
        return redirect(url_for('theory.learning_path'))

    # Configuración de campos dinámicos para dibujar el formulario HTML según el binario C++ de destino
    formulario_config = []
    binario = ejercicio.ruta_binario_cpp.lower()

    # Mapeo completo de los 24 retos del libro de Francisco Martínez
    if binario == "hola":
        formulario_config = [] # No requiere entrada
    elif binario == "aritmetica":
        formulario_config = [
            {"id": "a", "label": "Primer número (a):", "tipo": "number", "placeholder": "Ej. 10"},
            {"id": "b", "label": "Segundo número (b):", "tipo": "number", "placeholder": "Ej. 5"}
        ]
    elif binario == "felsius_f":
        formulario_config = [
            {"id": "celsius", "label": "Grados Celsius:", "tipo": "number", "placeholder": "Ej. 25"}
        ]
    elif binario == "circulo":
        formulario_config = [
            {"id": "radio", "label": "Radio del círculo:", "tipo": "number", "placeholder": "Ej. 5.5"}
        ]
    elif binario == "mayor_edad":
        formulario_config = [
            {"id": "edad", "label": "Ingresa tu edad:", "tipo": "number", "placeholder": "Ej. 18"}
        ]
    elif binario == "menu":
        formulario_config = [
            {"id": "opcion", "label": "Opción (1:Suma, 2:Resta, 3:Mult):", "tipo": "number", "placeholder": "1-3"},
            {"id": "n1", "label": "Número 1:", "tipo": "number", "placeholder": "Ej. 10"},
            {"id": "n2", "label": "Número 2:", "tipo": "number", "placeholder": "Ej. 5"}
        ]
    elif binario == "sumatoria":
        formulario_config = [
            {"id": "n", "label": "Hasta qué número sumar:", "tipo": "number", "placeholder": "Ej. 100"}
        ]
    elif binario == "pide_clave":
        formulario_config = [
            {"id": "clave", "label": "Ingresa la clave maestra:", "tipo": "number", "placeholder": "Secret: 1234"}
        ]
    elif binario in ["vector_suma", "vector_max"]:
        formulario_config = [
            {"id": "n1", "label": "Número 1:", "tipo": "number", "placeholder": "Ej. 10"},
            {"id": "n2", "label": "Número 2:", "tipo": "number", "placeholder": "Ej. 20"},
            {"id": "n3", "label": "Número 3:", "tipo": "number", "placeholder": "Ej. 30"},
            {"id": "n4", "label": "Número 4:", "tipo": "number", "placeholder": "Ej. 40"},
            {"id": "n5", "label": "Número 5:", "tipo": "number", "placeholder": "Ej. 50"}
        ]
    elif binario == "texto_reves":
        formulario_config = [
            {"id": "texto", "label": "Frase a invertir:", "tipo": "text", "placeholder": "Ej. Hola UTA"}
        ]
    elif binario == "struct_usuario":
        formulario_config = [
            {"id": "nombre", "label": "Tu nombre:", "tipo": "text", "placeholder": "Ej. Juan"},
            {"id": "edad", "label": "Tu edad:", "tipo": "number", "placeholder": "Ej. 20"}
        ]
    elif binario == "func_factorial":
        formulario_config = [
            {"id": "n", "label": "Factorial de n:", "tipo": "number", "placeholder": "Ej. 5", "help": "Prueba 15 para ver overflow de 32 bits."}
        ]
    elif binario == "func_swap":
        formulario_config = [
            {"id": "a", "label": "Valor X:", "tipo": "number", "placeholder": "Ej. 10"},
            {"id": "b", "label": "Valor Y:", "tipo": "number", "placeholder": "Ej. 20"}
        ]
    elif binario == "func_area":
        formulario_config = [
            {"id": "base", "label": "Base:", "tipo": "number", "placeholder": "Ej. 10"},
            {"id": "altura", "label": "Altura:", "tipo": "number", "placeholder": "Ej. 5"}
        ]
    elif binario == "func_defecto":
        formulario_config = [
            {"id": "precio", "label": "Precio producto:", "tipo": "number", "placeholder": "Ej. 100"}
        ]
    elif binario in ["punt_dir", "punt_aritmetica", "punt_dinamico"]:
        formulario_config = [] # Por ahora sin entradas adicionales
    elif binario == "punt_arreglo":
        formulario_config = [
            {"id": "n", "label": "Tamaño del arreglo dinámico:", "tipo": "number", "placeholder": "Ej. 5"}
        ]
    elif binario == "rec_fibo":
        formulario_config = [
            {"id": "n", "label": "Posición Fibonacci:", "tipo": "number", "placeholder": "Ej. 10"}
        ]
    elif binario == "rec_busqueda":
        formulario_config = [
            {"id": "n1", "label": "Número 1:", "tipo": "number", "placeholder": "1"},
            {"id": "n2", "label": "Número 2:", "tipo": "number", "placeholder": "2"},
            {"id": "n3", "label": "Número 3:", "tipo": "number", "placeholder": "3"},
            {"id": "target", "label": "Número a buscar:", "tipo": "number", "placeholder": "Ej. 2"}
        ]
    elif binario == "file_escribir":
        formulario_config = [
            {"id": "texto", "label": "Texto para el archivo:", "tipo": "text", "placeholder": "Ej. Log de sistema"}
        ]
    elif binario == "file_leer":
        formulario_config = [] # Sin entradas adicionales

    # Casos de simulación para el ID actual
    casos = SIMULACION_CASES.get(ejercicio_id, {"tle": "9999", "wa": "13", "re": "0"})

    return render_template(
        'interactive/workspace.html',
        ejercicio=ejercicio,
        formulario=formulario_config,
        casos=casos,
        intentos=ultimos_intentos
    )


@interactive_bp.route('/<int:ejercicio_id>/run', methods=['POST'])
@login_required
def run_exercise(ejercicio_id: int):
    """
    Endpoint AJAX para la ejecución de C++ y obtención del veredicto del Online Judge.
    Procesa peticiones JSON asíncronas y retorna respuestas formateadas.
    """
    try:
        # Extraer entradas del cliente (soporta JSON o Form normal)
        if request.is_json:
            inputs = request.get_json()
        else:
            inputs = request.form.to_dict()
            
        # Repositorios e infraestructura
        ejercicio_repo = SqliteEjercicioRepository()
        intento_repo = SqliteIntentoRepository()
        
        # Instanciar el ejecutor de subprocesos apuntando al directorio raíz del proyecto
        cpp_runner = SubprocessCppRunner(base_dir=current_app.config["ROOT_DIR"])
        
        # Ejecutar Caso de Uso
        use_case = EjecutarEjercicioUseCase(ejercicio_repo, intento_repo, cpp_runner)
        resultado = use_case.ejecutar(
            usuario_id=g.usuario.id,
            ejercicio_id=ejercicio_id,
            inputs=inputs
        )
        
        return jsonify({
            "success": True,
            "intento_id": resultado["intento_id"],
            "estado_oj": resultado["estado_oj"],
            "salida": resultado["salida"],
            "tiempo_ejecucion": resultado["tiempo_ejecucion"],
            "feedback": resultado["feedback"]
        }), 200

    except IntentoInvalido as e:
        return jsonify({
            "success": False,
            "error": e.message
        }), 400
    except LogicWebException as e:
        return jsonify({
            "success": False,
            "error": e.message
        }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Error interno en el servidor de evaluación: {str(e)}"
        }), 500
