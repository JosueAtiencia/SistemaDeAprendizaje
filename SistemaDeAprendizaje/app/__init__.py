"""
Inicializador de la Aplicación Flask (Factory Pattern) - LogicWeb UTA
Orquesta la integración de SQLAlchemy, registra Blueprints y realiza la semilla (seeding) automática de la base de datos sqlite.
"""

import os
from flask import Flask, redirect, url_for, session, g, render_template
from config import Config
from app.infrastructure.database.models import db, ExerciseModel

def create_app(config_class=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializar Base de Datos
    db.init_app(app)

    # Registrar Blueprints
    from app.infrastructure.web.auth import auth_bp
    from app.infrastructure.web.theory import theory_bp
    from app.infrastructure.web.solved import solved_bp
    from app.infrastructure.web.interactive import interactive_bp
    from app.infrastructure.web.reports import reports_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(theory_bp)
    app.register_blueprint(solved_bp)
    app.register_blueprint(interactive_bp)
    app.register_blueprint(reports_bp)

    # Redirección en el punto de entrada raíz
    @app.route('/')
    def index():
        return render_template('index.html')

    # Inicializar Base de Datos e Inyectar Ejercicios Base
    with app.app_context():
        db.create_all()
        _seeding_ejercicios_base()

    return app


def _seeding_ejercicios_base():
    """Siembra inicial de los 24 ejercicios académicos con C++ integrado."""
    from app.infrastructure.database.models import ExerciseModel
    import os

    # Leer contenidos de C++ para sembrar
    src_path = os.path.join(os.getcwd(), "cpp_modules", "src")
    cpp_codes = {}
    lista_archivos = [
        "hola", "aritmetica", "felsius_f", "circulo", 
        "mayor_edad", "menu", "sumatoria", "pide_clave", 
        "vector_suma", "vector_max", "texto_reves", "struct_usuario", 
        "func_factorial", "func_swap", "func_area", "func_defecto", 
        "punt_dir", "punt_aritmetica", "punt_dinamico", "punt_arreglo", 
        "rec_fibo", "rec_busqueda", "file_escribir", "file_leer"
    ]
    try:
        for f_name in lista_archivos:
            f_full_path = os.path.join(src_path, f_name + ".cpp")
            if os.path.exists(f_full_path):
                with open(f_full_path, "r", encoding="utf-8") as f_file:
                    cpp_codes[f_name] = f_file.read()
            else:
                cpp_codes[f_name] = "// Fuente del libro Francisco Martínez\n#include <iostream>\nusing namespace std;\nint main() { return 0; }"
    except Exception as e:
        print(f"[!] Error leyendo código C++ para seeding: {e}")

    # Estructura: (id, unidad_id, titulo, binario_cpp, descripcion, pseudocodigo)
    datos_ejercicios = [
        # UNIDAD 1: Introducción, E/S y Expresiones
        (1, 1, "Hola Mundo", "hola", "El primer programa del libro. Muestra un mensaje en pantalla usando cout.", "Algoritmo HolaMundo\n  Escribir \"Hola a todos\"\nFinAlgoritmo"),
        (2, 1, "Aritmética Básica", "aritmetica", "Lee dos valores reales y calcula su suma, resta, producto y división.", "Algoritmo Aritmetica\n  Leer a, b\n  Escribir a + b, a - b, a * b, a / b\nFinAlgoritmo"),
        (3, 1, "Conversión de Temperatura", "felsius_f", "Implementa la conversión de grados Celsius a Fahrenheit.", "Algoritmo CelsiusFahrenheit\n  Leer celsius\n  fahrenheit <- (celsius * 9/5) + 32\n  Escribir fahrenheit\nFinAlgoritmo"),
        (4, 1, "Área del Círculo", "circulo", "Calcula el área de un círculo usando PI y el radio ingresado.", "Algoritmo AreaCirculo\n  Leer radio\n  area <- 3.141592 * radio * radio\n  Escribir area\nFinAlgoritmo"),

        # UNIDAD 2: Estructuras de Control
        (5, 2, "Mayor de Edad", "mayor_edad", "Determina si una persona es mayor de edad (18+).", "Algoritmo MayorEdad\n  Leer edad\n  Si edad >= 18 Entonces Escribir \"Mayor\"\n  Sino Escribir \"Menor\"\nFinSi\nFinAlgoritmo"),
        (6, 2, "Menú de Operaciones", "menu", "Usa switch-case para elegir entre Suma, Resta y Multiplicación.", "Algoritmo Menu\n  Leer op, n1, n2\n  Segun op Caso 1: +\n  Caso 2: -\n  Caso 3: *\nFinAlgoritmo"),
        (7, 2, "Sumatoria N primeros", "sumatoria", "Usa un bucle for para sumar números desde 1 hasta N.", "Algoritmo Sumatoria\n  Para i <- 1 Hasta N Hacer sum <- sum + i\n  Escribir sum\nFinAlgoritmo"),
        (8, 2, "Validar Clave", "pide_clave", "Usa do-while para pedir una clave hasta que sea correcta (1234).", "Algoritmo Clave\n  Hacer Leer c Mientras c != 1234\nFinAlgoritmo"),

        # UNIDAD 3: Tipos de Datos Estructurados
        (9, 3, "Suma de Vector", "vector_suma", "Almacena 5 números en un arreglo y calcula su suma.", "Algoritmo SumaVec\n  Leer v[5]\n  Para cada x en v Hacer s <- s + x\nFinAlgoritmo"),
        (10, 3, "Máximo del Vector", "vector_max", "Encuentra el número más grande dentro de un arreglo de 5 elementos.", "Algoritmo MaxVec\n  Para cada x en v Hacer Si x > m Entonces m <- x\nFinAlgoritmo"),
        (11, 3, "Texto Invertido", "texto_reves", "Lee una cadena (string) y la imprime de atrás hacia adelante.", "Algoritmo Invertir\n  Leer s\n  Para i desde length-1 Hasta 0 Hacer Escribir s[i]\nFinAlgoritmo"),
        (12, 3, "Registro Usuario", "struct_usuario", "Usa una estructura Persona para guardar Nombre y Edad.", "Estructura Persona { string nombre; int edad; }\nAlgoritmo Registro\n  Leer p.nombre, p.edad\nFinAlgoritmo"),

        # UNIDAD 4: Modularización con Funciones
        (13, 4, "Factorial con Función", "func_factorial", "Crea una función que reciba N y retorne su factorial.", "Funcion fact(n)\n  r <- 1; Para i <- 1 Hasta n Hacer r <- r * i\n  Retornar r\nFinFuncion"),
        (14, 4, "Intercambio (Swap)", "func_swap", "Usa paso por referencia para intercambiar dos enteros.", "Funcion Intercambiar(ref a, ref b)\n  aux <- a; a <- b; b <- aux\nFinFuncion"),
        (15, 4, "Área Modular", "func_area", "Calcula el área usando una función que recibe base y altura.", "Funcion calcularArea(b, h) Retornar b * h"),
        (16, 4, "IVA por Defecto", "func_defecto", "Función con parámetro por defecto para el IVA del 15%.", "Funcion calc(p, iva=0.15) Retornar p * (1+iva)"),

        # UNIDAD 5: Punteros y Gestión Dinámica
        (17, 5, "Dirección Física", "punt_dir", "Muestra la dirección de memoria de una variable con el operador &.", "Algoritmo Dir\n  Escribir &x\nFinAlgoritmo"),
        (18, 5, "Aritmética Punteros", "punt_aritmetica", "Recorre un arreglo sumando posiciones al puntero base.", "Algoritmo PuntAritmetica\n  Escribir *(p + i)\nFinAlgoritmo"),
        (19, 5, "Entero Dinámico", "punt_dinamico", "Crea un entero en el montón (Heap) con new y lo libera con delete.", "Algoritmo Dinamico\n  p <- nuevo int; liberar p\nFinAlgoritmo"),
        (20, 5, "Arreglo Dinámico N", "punt_arreglo", "Pide tamaño N y reserva exactamente esa memoria en el Heap.", "Algoritmo ArrDin\n  p <- nuevo int[N]; liberar[] p\nFinAlgoritmo"),

        # UNIDAD 6: Recursividad y Flujos de Datos
        (21, 6, "Fibonacci Recursivo", "rec_fibo", "Calcula la serie de Fibonacci usando autollamadas recursivas.", "Funcion fibo(n)\n  Si n < 2 Retornar n\n  Sino fibo(n-1) + fibo(n-2)\nFinFuncion"),
        (22, 6, "Búsqueda Binaria", "rec_busqueda", "Busca un elemento dividiendo el vector a la mitad de forma recursiva.", "Función busquedaRec(arr, inf, sup, x)"),
        (23, 6, "Escritura en Archivo", "file_escribir", "Guarda un texto en el archivo 'salida.txt'.", "Algoritmo ArchEscribir\n  Abrir \"salida.txt\"; Escribir x; Cerrar\nFinAlgoritmo"),
        (24, 6, "Lectura de Archivo", "file_leer", "Lee y muestra el contenido de 'entrada.txt' línea a línea.", "Algoritmo ArchLeer\n  Mientras !EOF Hacer Leer x\nFinAlgoritmo")
    ]

    # Si ya existen registros, los actualizamos in-place para preservar relaciones y claves foráneas
    existing_count = ExerciseModel.query.count()
    if existing_count == 24:
        print("[*] Sincronizando y actualizando base de datos de ejercicios con la lógica del libro...")
        for id_e, unidad, titulo, binario, desc, pseudo in datos_ejercicios:
            ej = ExerciseModel.query.get(id_e)
            if ej:
                ej.unidad_id = unidad
                ej.titulo = f"Reto #{id_e}: {titulo}"
                ej.descripcion_caso_real = desc
                ej.pseudocodigo = pseudo
                ej.ruta_binario_cpp = binario
                ej.codigo_fuente_cpp = cpp_codes.get(binario, "// Código fuente no disponible")
        db.session.commit()
        print("[+] Sincronización in-place completada con éxito.")
        return

    # Si no hay 24 registros, borramos y volvemos a sembrar
    ExerciseModel.query.delete()
    db.session.commit()

    ejercicios_base = []
    for id_e, unidad, titulo, binario, desc, pseudo in datos_ejercicios:
        ejercicios_base.append(
            ExerciseModel(
                id=id_e,
                unidad_id=unidad,
                titulo=f"Reto #{id_e}: {titulo}",
                descripcion_caso_real=desc,
                pseudocodigo=pseudo,
                diagrama_ruta=f"unidad{unidad}_ej{id_e}.svg",
                ruta_binario_cpp=binario,
                codigo_fuente_cpp=cpp_codes.get(binario, "// Código fuente no disponible")
            )
        )

    db.session.bulk_save_objects(ejercicios_base)
    db.session.commit()
    print(f"[+] Se sembraron los 24 ejercicios académicos del libro en la base de datos.")
