"""
Blueprint de Contenidos Teóricos - LogicWeb UTA
Controlador Flask para mostrar el mapa de conceptos (Skill Tree) y los contenidos académicos de la asignatura.
"""

from flask import Blueprint, render_template, g, redirect, url_for
from app.infrastructure.web.auth import login_required
from app.infrastructure.database.repositories import SqliteEjercicioRepository, SqliteIntentoRepository
from app.application.use_cases.report_use_cases import ObtenerEstadisticasUsuarioUseCase

theory_bp = Blueprint('theory', __name__, url_prefix='/theory')

@theory_bp.route('/path')
@login_required
def learning_path():
    """
    Renderiza el Mapa de Aprendizaje (Skill Tree) estilo Exercism.
    Calcula el progreso del usuario para activar visualmente los nodos desbloqueados.
    """
    ejercicio_repo = SqliteEjercicioRepository()
    intento_repo = SqliteIntentoRepository()
    
    stats_use_case = ObtenerEstadisticasUsuarioUseCase(intento_repo, ejercicio_repo)
    estadisticas = stats_use_case.ejecutar(g.usuario.id)
    
    # Lista de todos los ejercicios del sistema para mapear en el árbol
    ejercicios = ejercicio_repo.obtener_todos()
    
    # Agrupar ejercicios por unidad para el mapa (6 unidades con 4 ejercicios cada una)
    unidades_data = [
        {
            "id": 1,
            "titulo": "Unidad 1: Fundamentos y Condicionales",
            "descripcion": "Bases de la lógica y toma de decisiones."
        },
        {
            "id": 2,
            "titulo": "Unidad 2: Ciclos y Bucles Iterativos",
            "descripcion": "Domina la repetición y optimización."
        },
        {
            "id": 3,
            "titulo": "Unidad 3: Funciones y Modularización",
            "descripcion": "Divide y vencerás en el código."
        },
        {
            "id": 4,
            "titulo": "Unidad 4: Arreglos y Estructuras de Datos",
            "descripcion": "Gestión de colecciones de datos."
        },
        {
            "id": 5,
            "titulo": "Unidad 5: Punteros y Gestión de Memoria",
            "descripcion": "Control total sobre el hardware."
        },
        {
            "id": 6,
            "titulo": "Unidad 6: Programación Orientada a Objetos",
            "descripcion": "Modelando el mundo real con C++."
        }
    ]

    mapa_unidades = []
    for u in unidades_data:
        ejercicios_unidad = [e for e in ejercicios if e.unidad_id == u["id"]]
        mapa_unidades.append({
            "id": u["id"],
            "titulo": u["titulo"],
            "descripcion": u["descripcion"],
            "ejercicios": ejercicios_unidad,
            "completados": estadisticas["progreso_unidades"][u["id"]]["completados"],
            "total": estadisticas["progreso_unidades"][u["id"]]["total"]
        })

    # Datos estructurados para dibujar la ruta educativa en el frontend
    mapa_ruta = {
        "unidades": mapa_unidades,
        "progreso_general": estadisticas["progreso_porcentaje"],
        "ejercicios_resueltos": list(estadisticas["progreso_unidades"]) # Lista de IDs resueltos
    }

    # Obtener el conjunto de IDs de ejercicios aprobados (AC) para marcarlos como completados
    intentos = intento_repo.obtener_por_usuario(g.usuario.id)
    ejercicios_completados = {i.ejercicio_id for i in intentos if i.estado_oj == "AC"}

    return render_template(
        'theory/path.html',
        mapa=mapa_ruta,
        ejercicios_completados=ejercicios_completados
    )


# Diccionario Académico de Teoría de Lógica y Algoritmos (LogicWeb UTA)
UNIDADES_TEORIA = {
    1: {
        "titulo": "Unidad 1: Introducción, E/S y Expresiones",
        "introduccion": "Esta unidad cubre la sintaxis básica para escribir un primer programa en C++, los tipos de datos primitivos y las expresiones aritméticas y lógicas que componen los cálculos de bajo nivel.",
        "logica_algoritmos": "Todo programa en C++ inicia su ejecución en la función 'main()'. Declaramos variables especificando su tipo estático (como int, double, char, bool) para indicarle al compilador cuántos bytes debe reservar en memoria RAM. Usamos cin para lectura y cout para escritura.",
        "sintaxis_cpp": "Usamos '#include <iostream>' para operaciones de entrada/salida y '#include <cmath>' para funciones matemáticas como sqrt() y pow(). Los operadores de incremento (++ y --) y asignación compuesta (+=, -=) optimizan la escritura del código.",
        "secciones": [
            {"subtitulo": "1. Estructura y Entrada/Salida", "contenido": "Uso de la directiva include, el espacio de nombres std, la función main() y los flujos básicos cin y cout."},
            {"subtitulo": "2. Tipos de Datos y Variables", "contenido": "Uso de int, float, double, char, bool. Reglas de identificadores válidos y constantes usando la palabra clave const."},
            {"subtitulo": "3. Expresiones y Operadores", "contenido": "Precedencia y asociatividad de operadores aritméticos (+, -, *, /, %). Conversiones implícitas y explícitas (cast)."}
        ],
        "ejercicio_referencia": {
            "titulo": "Cálculo de Área de Círculo",
            "descripcion": "Escriba un programa que lea el radio de un círculo y calcule su área utilizando M_PI.",
            "pseudocodigo": "Algoritmo AreaCirculo\n  Leer radio\n  area <- 3.141592 * radio * radio\n  Escribir area\nFinAlgoritmo",
            "codigo_cpp": "#include <iostream>\n#include <cmath>\nusing namespace std;\n\nint main() {\n    double radio;\n    cin >> radio;\n    double area = M_PI * radio * radio;\n    cout << \"Area: \" << area << endl;\n    return 0;\n}"
        }
    },
    2: {
        "titulo": "Unidad 2: Estructuras de Control",
        "introduccion": "Las estructuras de control determinan el flujo de ejecución del programa a través de condiciones lógicas y repeticiones controladas.",
        "logica_algoritmos": "La evaluación de condiciones lógicas utiliza operadores de comparación y operadores lógicos (&&, ||, !). Las estructuras repetitivas permiten procesar secuencias de datos, acumular cálculos y validar entradas de datos.",
        "sintaxis_cpp": "Usamos 'if' y 'else' para bifurcaciones simples, y 'switch' para selección múltiple basada en valores enteros o caracteres. Para ciclos usamos 'while' (mientras), 'do-while' (hacer-mientras) y 'for' (para ciclos controlados por contador).",
        "secciones": [
            {"subtitulo": "1. Sentencias Condicionales", "contenido": "Estructuras if, else, if-else anidadas y el operador condicional ternario (? : )."},
            {"subtitulo": "2. Selección Múltiple", "contenido": "La sentencia switch-case, el uso del break y la etiqueta default para flujos alternativos."},
            {"subtitulo": "3. Bucle Iterativo y Control", "contenido": "Ciclos for, while, do-while. Uso de break y continue para alterar dinámicamente las iteraciones."}
        ],
        "ejercicio_referencia": {
            "titulo": "Validar Contraseña",
            "descripcion": "Lea valores enteros hasta que el usuario introduzca la clave maestra correcta (1234).",
            "pseudocodigo": "Algoritmo ValidarClave\n  Repetir\n    Leer clave\n  Hasta Que clave = 1234\n  Escribir \"Acceso concedido\"\nFinAlgoritmo",
            "codigo_cpp": "#include <iostream>\nusing namespace std;\n\nint main() {\n    int clave;\n    do {\n        cin >> clave;\n    } while (clave != 1234);\n    cout << \"Clave correcta\" << endl;\n    return 0;\n}"
        }
    },
    3: {
        "titulo": "Unidad 3: Tipos de Datos Estructurados",
        "introduccion": "Los tipos de datos estructurados permiten agrupar colecciones de datos contiguos del mismo tipo (vectores) o agrupar variables de tipos heterogéneos (estructuras).",
        "logica_algoritmos": "Un vector (arreglo unidimensional) agrupa múltiples elementos que comparten tipo de datos. Las cadenas (strings) representan secuencias de caracteres. Las estructuras (structs) definen nuevos tipos personalizados agrupando campos.",
        "sintaxis_cpp": "Declaramos vectores estáticos como 'tipo nombre[TAMANO];'. Los strings se manipulan mediante la clase 'string' de la biblioteca '<string>'. Las estructuras se definen con 'struct' y sus campos se acceden con el operador punto (.).",
        "secciones": [
            {"subtitulo": "1. Vectores y Arrays", "contenido": "Definición de arreglos, indexación en base 0, y recorrido secuencial mediante ciclos."},
            {"subtitulo": "2. Cadenas de Caracteres", "contenido": "Uso del tipo string, concatenación, longitud (.length()) y lectura con espacios usando getline()."},
            {"subtitulo": "3. Estructuras (struct)", "contenido": "Definición de estructuras, inicialización de miembros y vectores de estructuras."}
        ],
        "ejercicio_referencia": {
            "titulo": "Mayor de edad en Registro",
            "descripcion": "Defina una estructura Persona y determine si los datos ingresados indican que es mayor de edad.",
            "pseudocodigo": "Estructura Persona { string nombre; int edad; }\nAlgoritmo Registro\n  Leer p.nombre, p.edad\n  Si p.edad >= 18 Entonces Escribir p.nombre\nFinAlgoritmo",
            "codigo_cpp": "#include <iostream>\n#include <string>\nusing namespace std;\n\nstruct Persona {\n    string nombre;\n    int edad;\n};\n\nint main() {\n    Persona p;\n    cin >> p.nombre >> p.edad;\n    cout << \"Nombre: \" << p.nombre << endl;\n    cout << \"Edad: \" << p.edad << endl;\n    return 0;\n}"
        }
    },
    4: {
        "titulo": "Unidad 4: Modularización con Funciones",
        "introduccion": "Las funciones permiten dividir un problema complejo en subproblemas más sencillos y reutilizables, aplicando el enfoque modular.",
        "logica_algoritmos": "Una función encapsula una tarea específica. Recibe parámetros de entrada, ejecuta la lógica en su pila local de variables y retorna un resultado de salida.",
        "sintaxis_cpp": "Declaramos funciones con su prototipo (interfaz) antes de main. El paso de parámetros puede ser por valor (copia) o por referencia (usando '&' para modificar la variable original).",
        "secciones": [
            {"subtitulo": "1. Definición y Prototipos", "contenido": "Sintaxis de funciones, funciones void, tipo de retorno y orden de definición en C++."},
            {"subtitulo": "2. Paso por Referencia", "contenido": "Diferencia entre paso por valor (copia) y por referencia, uso del carácter & para modificar variables del llamador."},
            {"subtitulo": "3. Argumentos por Defecto y Sobrecarga", "contenido": "Funciones con parámetros opcionales e implementación de funciones con el mismo nombre pero distintas firmas."}
        ],
        "ejercicio_referencia": {
            "titulo": "Intercambio de Variables (Swap)",
            "descripcion": "Implemente una función con paso por referencia para intercambiar los valores de dos variables enteras.",
            "pseudocodigo": "Procedimiento swap(ref x, ref y)\n  aux <- x; x <- y; y <- aux\nFinProcedimiento",
            "codigo_cpp": "#include <iostream>\nusing namespace std;\n\nvoid intercambiar(int &a, int &b) {\n    int aux = a;\n    a = b;\n    b = aux;\n}\n\nint main() {\n    int x, y;\n    cin >> x >> y;\n    intercambiar(x, y);\n    cout << \"Swap: \" << x << \" \" << y << endl;\n    return 0;\n}"
        }
    },
    5: {
        "titulo": "Unidad 5: Punteros y Gestión Dinámica",
        "introduccion": "Los punteros y la memoria dinámica otorgan control directo sobre la memoria RAM física del computador, permitiendo crear estructuras flexibles en tiempo de ejecución.",
        "logica_algoritmos": "Un puntero almacena la dirección de memoria de otra variable. La gestión de memoria dinámica permite solicitar espacio en el montón (Heap) cuando el tamaño de los datos no se conoce de antemano.",
        "sintaxis_cpp": "Declaramos punteros con '*'. El operador de dirección '&' obtiene la dirección de una variable. Usamos 'new' para reservar memoria y 'delete' o 'delete[]' para liberarla obligatoriamente.",
        "secciones": [
            {"subtitulo": "1. Punteros y Direcciones", "contenido": "El tipo puntero, asignación de direcciones, desreferenciación con el operador *."},
            {"subtitulo": "2. Aritmética de Punteros", "contenido": "Desplazamiento por arreglos mediante sumas al puntero base, relación estrecha entre vectores y punteros."},
            {"subtitulo": "3. Memoria Dinámica", "contenido": "El montón (Heap), reserva con new y new[], liberación estricta con delete y delete[] para evitar fugas de memoria."}
        ],
        "ejercicio_referencia": {
            "titulo": "Arreglo Dinámico de Enteros",
            "descripcion": "Solicite al usuario el tamaño de un arreglo, reserve memoria dinámicamente y libérela al finalizar.",
            "pseudocodigo": "Algoritmo VectorDinamico\n  Leer n\n  p <- nuevo int[n]\n  liberar[] p\nFinAlgoritmo",
            "codigo_cpp": "#include <iostream>\nusing namespace std;\n\nint main() {\n    int n;\n    cin >> n;\n    int *p = new int[n];\n    delete[] p;\n    return 0;\n}"
        }
    },
    6: {
        "titulo": "Unidad 6: Recursividad y Flujos de Datos",
        "introduccion": "Esta unidad enseña a resolver problemas complejos autoinvocando funciones (recursión) y a persistir datos en archivos de texto (flujos).",
        "logica_algoritmos": "Una función recursiva divide el problema en casos idénticos más pequeños hasta alcanzar un caso base. Los flujos permiten que los datos persistan en el disco duro tras cerrarse el programa.",
        "sintaxis_cpp": "La recursión requiere definir un caso base que detenga la pila de llamadas. Para archivos, incluimos '<fstream>' y usamos 'ifstream' para lectura y 'ofstream' para escritura.",
        "secciones": [
            {"subtitulo": "1. Conceptos Recursivos", "contenido": "Estructura de una función recursiva, el caso base, caso inductivo y ejemplos como la serie de Fibonacci."},
            {"subtitulo": "2. Flujos y Archivos de Salida", "contenido": "Creación y escritura de archivos de texto con ofstream, asociación de ficheros y el cierre de flujos."},
            {"subtitulo": "3. Flujos de Entrada y Estado", "contenido": "Lectura secuencial con ifstream, verificación del estado de apertura (.is_open()) y fin de fichero (.eof())."}
        ],
        "ejercicio_referencia": {
            "titulo": "Guardar texto en Archivo",
            "descripcion": "Escriba un programa que reciba una frase del usuario y la almacene de manera persistente en 'salida.txt'.",
            "pseudocodigo": "Algoritmo EscribirArchivo\n  Leer linea\n  Abrir \"salida.txt\"\n  Escribir linea\n  Cerrar\nFinAlgoritmo",
            "codigo_cpp": "#include <iostream>\n#include <fstream>\n#include <string>\nusing namespace std;\n\nint main() {\n    string texto;\n    getline(cin >> ws, texto);\n    ofstream archivo(\"salida.txt\");\n    if (archivo.is_open()) {\n        archivo << texto << endl;\n        archivo.close();\n    }\n    return 0;\n}"
        }
    }
}


@theory_bp.route('/unit/<int:unit_id>')
@login_required
def unit_details(unit_id: int):
    """Muestra la teoría académica de la unidad seleccionada."""
    ejercicio_repo = SqliteEjercicioRepository()
    ejercicios = [e for e in ejercicio_repo.obtener_todos() if e.unidad_id == unit_id]
    
    teoria_actual = UNIDADES_TEORIA.get(unit_id)
    if not teoria_actual:
        return redirect(url_for('theory.learning_path'))

    return render_template(
        'theory/unit.html',
        unit_id=unit_id,
        titulo=teoria_actual["titulo"],
        teoria=teoria_actual,
        ejercicios=ejercicios
    )

@theory_bp.route('/material')
@login_required
def study_material():
    """Renderiza el módulo central de materia (Teoría y Ejercicios Resueltos paso a paso)."""
    ejercicio_repo = SqliteEjercicioRepository()
    todos_ejercicios = ejercicio_repo.obtener_todos()

    # Estructurar las unidades con sus contenidos teóricos y ejercicios resueltos correspondientes
    unidades_material = []
    for uid, teoria in UNIDADES_TEORIA.items():
        ejercicios_unidad = [e for e in todos_ejercicios if e.unidad_id == uid]
        unidades_material.append({
            "id": uid,
            "titulo": teoria["titulo"],
            "introduccion": teoria["introduccion"],
            "logica_algoritmos": teoria["logica_algoritmos"],
            "sintaxis_cpp": teoria["sintaxis_cpp"],
            "secciones": teoria["secciones"],
            "ejercicio_referencia": teoria["ejercicio_referencia"],
            "ejercicios": ejercicios_unidad
        })

    return render_template(
        'theory/material.html',
        unidades=unidades_material
    )

