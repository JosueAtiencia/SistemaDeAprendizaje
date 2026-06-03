"""
Blueprint de Ejercicios Resueltos - LogicWeb UTA
Controlador Flask para mostrar las guías de estudio paso a paso: enunciados, pseudocódigo, diagramas y soluciones estáticas de C++.
"""

from flask import Blueprint, render_template, g, flash, redirect, url_for
from app.infrastructure.web.auth import login_required
from app.infrastructure.database.repositories import SqliteEjercicioRepository
from app.application.use_cases.exercise_use_cases import ObtenerEjercicioPorIdUseCase
from app.domain.exceptions import LogicWebException

solved_bp = Blueprint('solved', __name__, url_prefix='/solved')

# Catálogo completo de guías didácticas y casos reales para los 24 desafíos
GUIAS_ESTUDIO = {
    1: {
        "caso_real": "En el desarrollo de software, el primer paso es asegurar que el entorno de desarrollo y la salida básica funcionen. Un 'Hola Mundo' personalizado confirma que la comunicación con el monitor es correcta.",
        "analisis_logico": ["Uso de #include <iostream>", "Uso de cout para salida", "Estructura básica de main()"],
        "conceptos_clave": [
            {"titulo": "Directiva #include", "descripcion": "Instrucción de preprocesamiento que incorpora el contenido de una biblioteca estándar (como <iostream>) antes de la compilación, habilitando funcionalidades externas."},
            {"titulo": "Flujo de salida cout", "descripcion": "Objeto de la biblioteca estándar que representa el flujo de salida hacia la consola. Se utiliza con el operador de inserción (<<) para enviar datos al monitor."},
            {"titulo": "Función main()", "descripcion": "Punto de entrada obligatorio de todo programa C++. El sistema operativo invoca esta función al ejecutar el binario y espera un código de retorno entero."},
            {"titulo": "Espacio de nombres std", "descripcion": "Contenedor lógico que agrupa todos los identificadores de la biblioteca estándar de C++. La directiva 'using namespace std' evita anteponer 'std::' a cada identificador."},
        ]
    },
    2: {
        "caso_real": "Cualquier sistema contable requiere realizar cálculos básicos como sumas, restas y promedios. Entender los operadores aritméticos es la base de cualquier lógica financiera.",
        "analisis_logico": ["Operadores +, -, *, /", "Precedencia de operaciones", "Uso de variables tipo double"],
        "conceptos_clave": [
            {"titulo": "Operadores aritméticos", "descripcion": "Símbolos (+, -, *, /, %) que realizan operaciones matemáticas entre operandos. En C++, la división entre enteros trunca la parte decimal."},
            {"titulo": "Precedencia de operadores", "descripcion": "Regla que establece el orden de evaluación: multiplicación y división se ejecutan antes que suma y resta, salvo que se usen paréntesis para alterar la prioridad."},
            {"titulo": "Tipo de dato double", "descripcion": "Tipo numérico de punto flotante con doble precisión (64 bits) que permite almacenar valores decimales con aproximadamente 15 dígitos significativos."},
            {"titulo": "Flujo de entrada cin", "descripcion": "Objeto que representa la entrada estándar (teclado). Se utiliza con el operador de extracción (>>) para leer datos ingresados por el usuario y almacenarlos en variables."},
        ]
    },
    3: {
        "caso_real": "Sistemas climáticos internacionales requieren convertir escalas térmicas (Celsius a Fahrenheit) constantemente. Una fórmula mal escrita puede dar alertas volcánicas erróneas.",
        "analisis_logico": ["Uso de constantes", "Fórmulas matemáticas en código", "Entrada de datos con cin"],
        "conceptos_clave": [
            {"titulo": "Expresiones aritméticas compuestas", "descripcion": "Fórmulas que combinan varios operadores en una sola sentencia. Es fundamental respetar la precedencia y usar paréntesis para garantizar el orden correcto de evaluación."},
            {"titulo": "Conversión de tipos implícita", "descripcion": "Cuando se mezclan tipos enteros y reales en una expresión, C++ promueve automáticamente los enteros a double para preservar la precisión del resultado."},
            {"titulo": "Variables de entrada", "descripcion": "Variables que reciben su valor desde el exterior (teclado) mediante cin. Deben declararse con un tipo compatible antes de ser utilizadas en la lectura."},
        ]
    },
    4: {
        "caso_real": "En ingeniería civil, calcular el área de secciones circulares para tuberías es vital. El uso de precisiones matemáticas (como PI) evita colapsos por presión mal calculada.",
        "analisis_logico": ["Biblioteca <cmath>", "Uso de constantes simbólicas", "Salida con precisión decimal"],
        "conceptos_clave": [
            {"titulo": "Biblioteca <cmath>", "descripcion": "Cabecera estándar de C++ que provee funciones matemáticas (sqrt, pow, sin, cos) y constantes como M_PI para cálculos de alta precisión."},
            {"titulo": "Constante M_PI", "descripcion": "Macro definida en <cmath> que representa el valor de π con la máxima precisión del tipo double. Su uso evita errores por aproximaciones manuales."},
            {"titulo": "Operador de potencia", "descripcion": "C++ no tiene operador nativo de exponenciación. Se utiliza la función pow(base, exponente) de <cmath>, o bien se multiplica la variable por sí misma para elevar al cuadrado."},
        ]
    },
    5: {
        "caso_real": "Sistemas de validación de acceso verifican si un usuario tiene la edad legal. Una estructura condicional decide si permitir o denegar el acceso a un servicio.",
        "analisis_logico": ["Estructura if-else", "Operadores relacionales (>=)", "Salida condicional de mensajes"],
        "conceptos_clave": [
            {"titulo": "Estructura condicional if-else", "descripcion": "Mecanismo de bifurcación que evalúa una expresión booleana: ejecuta un bloque si es verdadera y, opcionalmente, un bloque alternativo si es falsa."},
            {"titulo": "Operadores relacionales", "descripcion": "Operadores (==, !=, <, >, <=, >=) que comparan dos valores y producen un resultado booleano (true o false) utilizado en condiciones de control de flujo."},
            {"titulo": "Evaluación booleana", "descripcion": "En C++, cualquier expresión entera distinta de cero se evalúa como true, y cero como false. Las condiciones del if se reducen siempre a este criterio binario."},
        ]
    },
    6: {
        "caso_real": "Las terminales de punto de venta (POS) usan menús para seleccionar productos. Un switch-case permite procesar la selección del cliente de forma rápida y limpia.",
        "analisis_logico": ["Estructura switch", "Uso de break", "Etiqueta default para errores"],
        "conceptos_clave": [
            {"titulo": "Estructura switch-case", "descripcion": "Estructura de selección múltiple que evalúa una expresión entera o de carácter y salta directamente a la etiqueta case coincidente, siendo más legible que múltiples if-else."},
            {"titulo": "Sentencia break", "descripcion": "Instrucción que termina la ejecución dentro del switch y salta al código posterior. Sin break, la ejecución 'cae' (fall-through) al siguiente case consecutivo."},
            {"titulo": "Etiqueta default", "descripcion": "Caso por defecto que se ejecuta cuando ninguna etiqueta case coincide con el valor evaluado. Funciona como un mecanismo de captura para entradas no previstas."},
            {"titulo": "Restricciones del switch", "descripcion": "Solo acepta expresiones de tipo entero, carácter o enumeración. No se pueden usar cadenas (string) ni rangos como condiciones en las etiquetas case."},
        ]
    },
    7: {
        "caso_real": "El cálculo de acumulados (como el total de una compra o una sumatoria estadística) requiere recorrer rangos numéricos. El bucle for es la herramienta ideal.",
        "analisis_logico": ["Ciclo for", "Variable acumuladora", "Contadores de iteración"],
        "conceptos_clave": [
            {"titulo": "Ciclo for", "descripcion": "Estructura iterativa con tres componentes (inicialización; condición; actualización) que permite repetir un bloque un número determinado de veces de forma compacta."},
            {"titulo": "Variable acumuladora", "descripcion": "Variable inicializada en cero (o un valor neutro) que acumula resultados parciales en cada iteración, como sumas, productos o conteos progresivos."},
            {"titulo": "Contador de iteración", "descripcion": "Variable de control (generalmente 'i') que se incrementa o decrementa en cada ciclo y determina cuántas veces se repite el bloque de instrucciones."},
        ]
    },
    8: {
        "caso_real": "Sistemas de seguridad requieren que el usuario ingrese una contraseña válida. Un bucle do-while garantiza que el usuario sea consultado al menos una vez.",
        "analisis_logico": ["Ciclo do-while", "Validación de entrada", "Condiciones de salida de bucle"],
        "conceptos_clave": [
            {"titulo": "Ciclo do-while", "descripcion": "Estructura iterativa que ejecuta el bloque de código al menos una vez antes de evaluar la condición de permanencia, a diferencia del while que evalúa antes de entrar."},
            {"titulo": "Validación de entrada", "descripcion": "Técnica que verifica que los datos ingresados cumplan criterios de aceptación antes de continuar la ejecución, evitando que datos inválidos propaguen errores."},
            {"titulo": "Condición de salida", "descripcion": "Expresión booleana evaluada al final del ciclo do-while que determina si se repite el bloque. Si es verdadera, el ciclo continúa; si es falsa, termina."},
        ]
    },
    9: {
        "caso_real": "Procesar listas de precios o de sensores requiere almacenar muchos datos. Un vector permite agruparlos y procesarlos en bloque con un solo ciclo.",
        "analisis_logico": ["Declaración de arreglos", "Acceso por índice", "Recorrido de vectores con for"],
        "conceptos_clave": [
            {"titulo": "Arreglos estáticos", "descripcion": "Estructura de datos que almacena una colección de elementos del mismo tipo en posiciones contiguas de memoria. Su tamaño se fija en tiempo de compilación."},
            {"titulo": "Indexación base cero", "descripcion": "En C++, el primer elemento de un arreglo se accede con índice 0 y el último con índice (tamaño - 1). Un acceso fuera de rango causa comportamiento indefinido."},
            {"titulo": "Recorrido con ciclo for", "descripcion": "Patrón estándar que usa un contador desde 0 hasta tamaño-1 para visitar secuencialmente cada elemento del arreglo y aplicar una operación (sumar, imprimir, etc.)."},
        ]
    },
    10: {
        "caso_real": "En análisis de datos, encontrar el valor crítico (máximo) de una serie es fundamental para detectar fallas o picos de demanda eléctrica.",
        "analisis_logico": ["Comparación secuencial", "Inicialización del máximo", "Algoritmo de búsqueda lineal"],
        "conceptos_clave": [
            {"titulo": "Búsqueda lineal del máximo", "descripcion": "Algoritmo que recorre todos los elementos comparando cada uno con un candidato actual. Si encuentra un valor mayor, actualiza el candidato. Complejidad O(n)."},
            {"titulo": "Inicialización del centinela", "descripcion": "El valor máximo debe inicializarse con el primer elemento del arreglo (no con cero), para garantizar resultados correctos incluso con valores negativos."},
            {"titulo": "Comparación secuencial", "descripcion": "Técnica de recorrido que evalúa cada elemento contra una referencia. Es la base de algoritmos de búsqueda y selección en colecciones no ordenadas."},
        ]
    },
    11: {
        "caso_real": "El procesamiento de nombres y textos en C++ usa la clase string. Invertir una cadena es un ejercicio clásico de lógica para entender cómo se mapea el texto en memoria.",
        "analisis_logico": ["Biblioteca <string>", "Método .length()", "Acceso a caracteres individuales"],
        "conceptos_clave": [
            {"titulo": "Clase std::string", "descripcion": "Contenedor de la biblioteca estándar que encapsula arreglos de caracteres, ofreciendo gestión automática de memoria y métodos como length(), substr() y append()."},
            {"titulo": "Acceso por índice a caracteres", "descripcion": "Cada carácter de un string se puede acceder con el operador [] como si fuera un arreglo. El índice 0 corresponde al primer carácter y length()-1 al último."},
            {"titulo": "Recorrido inverso", "descripcion": "Patrón que inicia el iterador en la última posición (length()-1) y decrementa hasta 0, permitiendo procesar la cadena de derecha a izquierda."},
        ]
    },
    12: {
        "caso_real": "Registrar un usuario requiere nombre, edad y correo. Una estructura (struct) permite empaquetar estos datos heterogéneos como una sola entidad.",
        "analisis_logico": ["Definición de struct", "Miembros de la estructura", "Operador punto (.)"],
        "conceptos_clave": [
            {"titulo": "Estructuras (struct)", "descripcion": "Tipo de dato compuesto definido por el usuario que agrupa variables de distintos tipos bajo un solo nombre, modelando entidades del mundo real como registros."},
            {"titulo": "Miembros de la estructura", "descripcion": "Cada variable declarada dentro de un struct se denomina miembro o campo. Pueden ser de cualquier tipo: enteros, cadenas, flotantes u otras estructuras."},
            {"titulo": "Operador punto (.)", "descripcion": "Operador de acceso que permite leer o modificar los miembros individuales de una instancia de struct mediante la sintaxis variable.miembro."},
        ]
    },
    13: {
        "caso_real": "En combinatoria y probabilidad, el factorial es recurrente. Crear una función específica permite reutilizar este cálculo en cualquier parte de un proyecto grande.",
        "analisis_logico": ["Definición de funciones", "Paso de parámetros por valor", "Sentencia return"],
        "conceptos_clave": [
            {"titulo": "Definición de funciones", "descripcion": "Bloque de código reutilizable con nombre, tipo de retorno y lista de parámetros. Permite descomponer un programa en unidades lógicas independientes y testeables."},
            {"titulo": "Paso por valor", "descripcion": "Mecanismo donde la función recibe una copia del argumento. Las modificaciones dentro de la función no afectan a la variable original del llamador."},
            {"titulo": "Sentencia return", "descripcion": "Instrucción que finaliza la ejecución de la función y devuelve un valor al punto de invocación. El tipo del valor retornado debe coincidir con el tipo declarado."},
            {"titulo": "Prototipo de función", "descripcion": "Declaración anticipada de la firma de una función (tipo, nombre y parámetros) antes de main(), que permite al compilador verificar las llamadas antes de encontrar la definición completa."},
        ]
    },
    14: {
        "caso_real": "Intercambiar dos variables es vital en algoritmos de ordenamiento. Usar el paso por referencia evita crear copias innecesarias y modifica los valores originales.",
        "analisis_logico": ["Paso por referencia (&)", "Variables auxiliares", "Ámbito de la función"],
        "conceptos_clave": [
            {"titulo": "Paso por referencia (&)", "descripcion": "Mecanismo que pasa la dirección de la variable original a la función. Cualquier modificación dentro de la función altera directamente el valor en el ámbito del llamador."},
            {"titulo": "Variable auxiliar (temp)", "descripcion": "Variable temporal utilizada para almacenar provisionalmente un valor durante un intercambio, evitando la pérdida de datos al sobrescribir una de las dos variables."},
            {"titulo": "Ámbito de la función", "descripcion": "Región del código donde las variables locales de una función existen. Al terminar la función, las variables locales se destruyen, pero las referencias modifican el ámbito externo."},
        ]
    },
    15: {
        "caso_real": "Un sistema gráfico puede calcular áreas de distintas formas (cuadrados o círculos). La sobrecarga permite usar el mismo nombre de función para lógicas distintas.",
        "analisis_logico": ["Sobrecarga de funciones", "Diferenciación por parámetros", "Reutilización de nombres"],
        "conceptos_clave": [
            {"titulo": "Sobrecarga de funciones", "descripcion": "Capacidad de C++ para definir múltiples funciones con el mismo nombre pero diferente lista de parámetros (cantidad o tipo). El compilador selecciona la versión correcta en tiempo de compilación."},
            {"titulo": "Resolución de sobrecarga", "descripcion": "Proceso del compilador que compara los argumentos de la llamada con las firmas disponibles para determinar cuál versión de la función sobrecargada invocar."},
            {"titulo": "Polimorfismo estático", "descripcion": "La sobrecarga de funciones es una forma de polimorfismo resuelto en compilación, donde un mismo nombre se comporta diferente según los tipos de los argumentos pasados."},
        ]
    },
    16: {
        "caso_real": "En simulaciones físicas, a veces se usan valores por defecto (como la gravedad terrestre) a menos que el usuario especifique lo contrario.",
        "analisis_logico": ["Parámetros por defecto", "Reglas de posición de argumentos", "Simplificación de llamadas"],
        "conceptos_clave": [
            {"titulo": "Parámetros por defecto", "descripcion": "Valores predefinidos asignados a los parámetros de una función en su declaración. Si el llamador omite esos argumentos, se utilizan automáticamente los valores por defecto."},
            {"titulo": "Regla de posición derecha", "descripcion": "Los parámetros con valor por defecto deben ubicarse al final de la lista (de derecha a izquierda). No se permite intercalar parámetros con y sin valor por defecto."},
            {"titulo": "Simplificación de interfaces", "descripcion": "Los valores por defecto reducen la cantidad de sobrecargas necesarias y simplifican las llamadas a funciones, ofreciendo flexibilidad sin duplicar código."},
        ]
    },
    17: {
        "caso_real": "Los sistemas operativos gestionan memoria física. Un puntero nos permite ver dónde reside un dato en el hardware real.",
        "analisis_logico": ["Operador de dirección (&)", "Punteros y tipos", "Lectura de direcciones HEX"],
        "conceptos_clave": [
            {"titulo": "Punteros en C++", "descripcion": "Variable especial que almacena la dirección de memoria de otra variable. Se declara con el asterisco (*) antepuesto al nombre y su tipo debe coincidir con el dato apuntado."},
            {"titulo": "Operador de dirección (&)", "descripcion": "Operador unario que, aplicado a una variable, devuelve su dirección física en memoria RAM. Es el complemento del operador de desreferencia (*)."},
            {"titulo": "Operador de desreferencia (*)", "descripcion": "Aplicado a un puntero, accede al valor almacenado en la dirección que contiene. Permite leer y modificar indirectamente la variable apuntada."},
            {"titulo": "Direcciones hexadecimales", "descripcion": "Las direcciones de memoria se representan en base 16 (hexadecimal). Cada puntero muestra una dirección como 0x7ffc... que identifica la posición exacta del dato en la RAM."},
        ]
    },
    18: {
        "caso_real": "Desplazarse por una lista de datos en memoria es más rápido sumando direcciones que usando índices. Es la base de los sistemas de alto rendimiento.",
        "analisis_logico": ["Aritmética de punteros", "Relación arreglo-puntero", "Desplazamiento binario"],
        "conceptos_clave": [
            {"titulo": "Aritmética de punteros", "descripcion": "Operaciones (+, -, ++, --) sobre punteros que desplazan la dirección en múltiplos del tamaño del tipo apuntado. Sumar 1 a un int* avanza 4 bytes en arquitecturas de 32 bits."},
            {"titulo": "Equivalencia arreglo-puntero", "descripcion": "El nombre de un arreglo decae a un puntero al primer elemento. Por tanto, v[i] es equivalente a *(v + i), y &v[0] es igual a v."},
            {"titulo": "Desreferencia con desplazamiento", "descripcion": "La expresión *(p + i) accede al elemento i-ésimo desde la posición apuntada por p, combinando aritmética de punteros con desreferencia en una sola operación."},
        ]
    },
    19: {
        "caso_real": "Si no sabemos cuánta memoria necesitaremos hasta que el usuario la pida, usamos el montón (Heap). Reservar una variable dinámicamente es el primer paso.",
        "analisis_logico": ["Operador new", "Punteros al montón", "Operador delete"],
        "conceptos_clave": [
            {"titulo": "Operador new", "descripcion": "Reserva memoria en el Heap (montón) en tiempo de ejecución y devuelve un puntero a la dirección asignada. A diferencia del Stack, esta memoria persiste hasta ser liberada explícitamente."},
            {"titulo": "Memoria Heap vs Stack", "descripcion": "El Stack almacena variables locales con gestión automática; el Heap permite asignación dinámica controlada por el programador, ideal cuando el tamaño no se conoce en compilación."},
            {"titulo": "Operador delete", "descripcion": "Libera la memoria previamente asignada con new, devolviendo el bloque al sistema operativo. Omitir delete provoca fugas de memoria (memory leaks) que degradan el rendimiento."},
        ]
    },
    20: {
        "caso_real": "Procesar archivos de tamaño desconocido requiere arreglos dinámicos. Esto evita desperdiciar RAM o quedarse corto de espacio.",
        "analisis_logico": ["Asignación dinámica de arreglos", "Uso de delete[]", "Prevención de memory leaks"],
        "conceptos_clave": [
            {"titulo": "Arreglos dinámicos (new[])", "descripcion": "El operador new[] reserva un bloque contiguo de memoria en el Heap para almacenar N elementos, donde N puede ser una variable definida en tiempo de ejecución."},
            {"titulo": "Liberación con delete[]", "descripcion": "Los arreglos creados con new[] deben liberarse con delete[] (con corchetes). Usar delete sin corchetes causa comportamiento indefinido al no liberar todos los elementos."},
            {"titulo": "Fugas de memoria", "descripcion": "Un memory leak ocurre cuando se pierde la referencia a memoria dinámica sin haberla liberado. En programas de larga ejecución, esto agota progresivamente la RAM disponible."},
            {"titulo": "Ciclo de vida dinámico", "descripcion": "El programador es responsable de todo el ciclo: asignar (new[]), usar, y liberar (delete[]). Este control manual es la base de la gestión de recursos en C++ moderno (RAII)."},
        ]
    },
    21: {
        "caso_real": "La naturaleza sigue patrones recursivos (como conejos o plantas). Fibonacci es el ejemplo clásico de cómo un problema se define por sus pasos anteriores.",
        "analisis_logico": ["Definición recursiva", "Caso base", "Caso inductivo"],
        "conceptos_clave": [
            {"titulo": "Recursión", "descripcion": "Técnica donde una función se invoca a sí misma para resolver subproblemas más pequeños. Cada llamada recursiva se apila en el Stack hasta alcanzar el caso base."},
            {"titulo": "Caso base", "descripcion": "Condición de terminación que detiene la recursión y devuelve un valor directo sin más llamadas recursivas. Sin caso base, la recursión es infinita y causa desbordamiento de pila."},
            {"titulo": "Caso inductivo (recursivo)", "descripcion": "Parte de la función que reduce el problema original en subproblemas más simples y se autoinvoca con parámetros más cercanos al caso base."},
            {"titulo": "Pila de llamadas (Call Stack)", "descripcion": "Estructura LIFO donde se almacenan los marcos de activación de cada llamada recursiva. Un exceso de recursión agota el Stack y genera un error de desbordamiento (stack overflow)."},
        ]
    },
    22: {
        "caso_real": "Buscar un dato en un millón es lento si es lineal. La búsqueda binaria (recursiva) divide la carga a la mitad en cada paso, siendo ultra eficiente.",
        "analisis_logico": ["Divide y vencerás", "Recursión con rangos", "Complejidad logarítmica"],
        "conceptos_clave": [
            {"titulo": "Divide y vencerás", "descripcion": "Paradigma algorítmico que descompone un problema en subproblemas más pequeños, los resuelve recursivamente y combina los resultados. La búsqueda binaria es su ejemplo más representativo."},
            {"titulo": "Precondición de ordenamiento", "descripcion": "La búsqueda binaria requiere que el arreglo esté previamente ordenado. Aplicarla sobre datos desordenados produce resultados incorrectos o indefinidos."},
            {"titulo": "Complejidad O(log n)", "descripcion": "En cada paso se descarta la mitad de los elementos, resultando en una complejidad logarítmica. Para un millón de datos, se necesitan como máximo 20 comparaciones."},
            {"titulo": "Índices inicio, medio y fin", "descripcion": "Tres variables que delimitan el subarreglo de búsqueda. El punto medio se calcula como (inicio + fin) / 2 y se compara con el valor buscado para decidir en qué mitad continuar."},
        ]
    },
    23: {
        "caso_real": "Los logs de un servidor deben guardarse en un archivo para análisis posterior. Escribir datos persistentes asegura que la información no se pierda al apagar el equipo.",
        "analisis_logico": ["Biblioteca <fstream>", "Objeto ofstream", "Cierre de archivos .close()"],
        "conceptos_clave": [
            {"titulo": "Biblioteca <fstream>", "descripcion": "Cabecera estándar de C++ que proporciona las clases ifstream (lectura), ofstream (escritura) y fstream (lectura/escritura) para operaciones con archivos en disco."},
            {"titulo": "Objeto ofstream", "descripcion": "Flujo de salida a archivo que permite escribir datos en disco. Se instancia con el nombre del archivo y, por defecto, crea el archivo si no existe o lo sobrescribe."},
            {"titulo": "Método .close()", "descripcion": "Cierra el flujo de archivo, vaciando el buffer de escritura al disco y liberando el recurso del sistema operativo. Omitirlo puede causar pérdida de datos."},
        ]
    },
    24: {
        "caso_real": "Los sistemas de procesamiento de datos leen archivos de configuración, registros de sensores o bases de datos planas línea por línea. La lectura secuencial desde disco es una operación fundamental en cualquier aplicación empresarial.",
        "analisis_logico": ["Objeto ifstream para lectura", "Función getline() para leer líneas completas", "Detección de fin de archivo (EOF)"],
        "conceptos_clave": [
            {"titulo": "Objeto ifstream", "descripcion": "Flujo de entrada desde archivo que permite leer datos almacenados en disco. Se instancia con la ruta del archivo y debe verificarse con is_open() antes de operar."},
            {"titulo": "Función getline()", "descripcion": "Lee una línea completa del flujo hasta encontrar el carácter de salto de línea ('\\n'). A diferencia del operador >>, no se detiene en espacios en blanco."},
            {"titulo": "Detección de fin de archivo", "descripcion": "El bucle while(getline(archivo, linea)) itera hasta que el flujo alcanza el final del archivo (EOF), momento en que getline devuelve false y el ciclo termina."},
            {"titulo": "Verificación de apertura", "descripcion": "Antes de leer, se debe comprobar que el archivo se abrió correctamente con is_open() o evaluando el flujo como booleano. Un archivo inexistente genera un flujo en estado de error."},
        ]
    }
}

DIAGRAMAS_MERMAID = {
    1: """graph TD
    A([Inicio]) --> B[/"Mostrar: 'Hola a todos'"/] --> C([Fin])""",
    2: """graph TD
    A([Inicio]) --> B[/"Leer a, b"/]
    B --> C["Suma = a + b\\nResta = a - b\\nProducto = a * b"]
    C --> D{"¿b != 0?"}
    D -- SÍ --> E["División = a / b"]
    D -- NO --> F[/"División: No definida"/]
    E --> G[/"Mostrar resultados"/]
    F --> G
    G --> H([Fin])""",
    3: """graph TD
    A([Inicio]) --> B[/"Leer celsius"/]
    B --> C["fahrenheit = (celsius * 9/5) + 32"]
    C --> D[/"Mostrar fahrenheit"/]
    D --> E([Fin])""",
    4: """graph TD
    A([Inicio]) --> B[/"Leer radio"/]
    B --> C{"¿radio < 0?"}
    C -- SÍ --> D[/"Mostrar Error/nan"/]
    C -- NO --> E["area = PI * radio * radio"]
    E --> F[/"Mostrar area"/]
    D --> G([Fin])
    F --> G""",
    5: """graph TD
    A([Inicio]) --> B[/"Leer edad"/]
    B --> C{"¿edad >= 18?"}
    C -- SÍ --> D[/"Mostrar: Mayor de edad"/]
    C -- NO --> E[/"Mostrar: Menor de edad"/]
    D --> F([Fin])
    E --> F""",
    6: """graph TD
    A([Inicio]) --> B[/"Leer opcion, n1, n2"/]
    B --> C{"opcion"}
    C -- 1 --> D[/"Mostrar Suma"/]
    C -- 2 --> E[/"Mostrar Resta"/]
    C -- 3 --> F[/"Mostrar Producto"/]
    C -- default --> G[/"Mostrar Opción no válida"/]
    D --> H([Fin])
    E --> H
    F --> H
    G --> H""",
    7: """graph TD
    A([Inicio]) --> B[/"Leer N"/]
    B --> C["suma = 0\\ni = 1"]
    C --> D{"¿i <= N?"}
    D -- SÍ --> E["suma = suma + i"]
    E --> F["i = i + 1"]
    F --> D
    D -- NO --> G[/"Mostrar suma"/]
    G --> H([Fin])""",
    8: """graph TD
    A([Inicio]) --> B[/"Leer clave"/]
    B --> C{"¿clave == 1234?"}
    C -- NO --> B
    C -- SÍ --> D[/"Mostrar: Clave correcta"/]
    D --> E([Fin])""",
    9: """graph TD
    A([Inicio]) --> B[/"Leer v[5]"/]
    B --> C["suma = 0\\ni = 0"]
    C --> D{"¿i < 5?"}
    D -- SÍ --> E["suma = suma + v[i]"]
    E --> F["i = i + 1"]
    F --> D
    D -- NO --> G[/"Mostrar suma"/]
    G --> H([Fin])""",
    10: """graph TD
    A([Inicio]) --> B[/"Leer v[5]"/]
    B --> C["maximo = v[0]\\ni = 1"]
    C --> D{"¿i < 5?"}
    D -- SÍ --> E{"¿v[i] > maximo?"}
    E -- SÍ --> F["maximo = v[i]"]
    E -- NO --> G["i = i + 1"]
    F --> G
    G --> D
    D -- NO --> H[/"Mostrar maximo"/]
    H --> I([Fin])""",
    11: """graph TD
    A([Inicio]) --> B[/"Leer texto"/]
    B --> C["len = texto.length()\\ni = len - 1"]
    C --> D{"¿i >= 0?"}
    D -- SÍ --> E[/"Mostrar texto[i]"/]
    E --> F["i = i - 1"]
    F --> D
    D -- NO --> G([Fin])""",
    12: """graph TD
    A([Inicio]) --> B[/"Leer Persona (nombre, edad)"/]
    B --> C[/"Mostrar nombre y edad"/]
    C --> D([Fin])""",
    13: """graph TD
    A([Inicio]) --> B[/"Leer n"/]
    B --> C{"¿n < 0?"}
    C -- SÍ --> D[/"Mostrar Error"/]
    C -- NO --> E["Llamar factorial(n)"]
    E --> F[/"Mostrar resultado"/]
    D --> G([Fin])
    F --> G""",
    14: """graph TD
    A([Inicio]) --> B[/"Leer a, b"/]
    B --> C["Llamar swap(a, b)\\n(Intercambiar por referencia)"]
    C --> D[/"Mostrar a y b"/]
    D --> E([Fin])""",
    15: """graph TD
    A([Inicio]) --> B[/"Leer base, altura"/]
    B --> C["Llamar calcularArea(base, altura)"]
    C --> D[/"Mostrar area"/]
    D --> E([Fin])""",
    16: """graph TD
    A([Inicio]) --> B[/"Leer precio"/]
    B --> C["Llamar calcularPrecioConIva(precio)"]
    C --> D[/"Mostrar precio con IVA"/]
    D --> E([Fin])""",
    17: """graph TD
    A([Inicio]) --> B["Definir x = 10\\nDefinir puntero p = &x"]
    B --> C[/"Mostrar dirección p y valor *p"/]
    C --> D([Fin])""",
    18: """graph TD
    A([Inicio]) --> B["Arreglo v[5]\\nPuntero p = v\\ni = 0"]
    B --> C{"¿i < 5?"}
    C -- SÍ --> D[/"Mostrar *(p + i)"/]
    D --> E["i = i + 1"]
    E --> C
    C -- NO --> F([Fin])""",
    19: """graph TD
    A([Inicio]) --> B["Crear p en Heap (new int)\\nAsignar *p = 100"]
    B --> C[/"Mostrar *p"/]
    C --> D["Liberar memoria (delete p)"]
    D --> E([Fin])""",
    20: """graph TD
    A([Inicio]) --> B[/"Leer n"/]
    B --> C["Crear arreglo dinámico en Heap (new int[n])"]
    C --> D["Inicializar y Mostrar elementos"]
    D --> E["Liberar memoria (delete[] p)"]
    E --> F([Fin])""",
    21: """graph TD
    A([Inicio]) --> B[/"Leer n"/]
    B --> C["Llamar recursivo fibo(n)"]
    C --> D[/"Mostrar resultado"/]
    D --> E([Fin])""",
    22: """graph TD
    A([Inicio]) --> B[/"Leer arreglo ordenado y target"/]
    B --> C["Llamar búsqueda recursiva"]
    C --> D[/"Mostrar posición o No encontrado"/]
    D --> E([Fin])""",
    23: """graph TD
    A([Inicio]) --> B[/"Leer texto"/]
    B --> C["Abrir archivo para escribir"]
    C --> D["Escribir texto en archivo"]
    D --> E["Cerrar archivo"]
    E --> F([Fin])""",
    24: """graph TD
    A([Inicio]) --> B["Abrir archivo para leer"]
    B --> C{"¿Se pudo abrir?"}
    C -- SÍ --> D{"¿Fin de archivo?"}
    D -- NO --> E["Leer línea y Mostrar"]
    E --> D
    D -- SÍ --> F["Cerrar archivo"]
    C -- NO --> G[/"Mostrar error de lectura"/]
    F --> H([Fin])
    G --> H"""
}

for k, diag in DIAGRAMAS_MERMAID.items():
    if k in GUIAS_ESTUDIO:
        GUIAS_ESTUDIO[k]["diagrama_mermaid"] = diag

def get_explanation_for_line(binary_name: str, line_text: str, line_number: int) -> str:
    """Devuelve la explicación didáctica para una línea de código específica en C++."""
    lt = line_text.strip()
    binary_name = binary_name.lower()
    
    # Explicaciones genéricas de estructura
    if lt.startswith("#include"):
        if "<iostream>" in lt:
            return "Directiva de preprocesamiento que importa la librería estándar 'iostream' para habilitar flujos de entrada y salida (cin y cout)."
        elif "<algorithm>" in lt:
            return "Directiva que importa funciones algorítmicas altamente optimizadas de la STL, como std::sort para ordenar arreglos."
        return "Directiva de preprocesamiento para importar librerías estándar en C++."
    elif lt.startswith("using namespace std;"):
        return "Espacio de nombres estándar. Evita tener que escribir 'std::' antes de cin, cout, endl, etc., simplificando la escritura de código."
    elif "int main()" in lt:
        return "Punto de entrada obligatorio de todo ejecutable C++ nativo. La ejecución del programa arranca desde aquí."
    elif lt == "{" or lt == "}":
        return "Llave de apertura o cierre que delimita el bloque o ámbito de ejecución."
    elif lt.startswith("return 0;"):
        return "Instrucción de retorno. Indica al sistema operativo que la ejecución finalizó correctamente (código de salida 0)."
    elif lt.startswith("return 1;"):
        return "Instrucción de retorno de error. Indica que el programa finalizó con fallas (código de salida 1)."
        
    # Explicaciones específicas por tipo de ejecutable/módulo
    if "hola" in binary_name:
        if 'cout << "Hola a todos"' in lt or 'cout<<' in lt:
            return "Envía la cadena de caracteres 'Hola a todos' al flujo de salida estándar (cout) seguido de un salto de línea (endl)."
            
    elif "aritmetica" in binary_name:
        if "double a, b;" in lt:
            return "Declara dos variables reales de doble precisión ('a' y 'b') para almacenar los números de entrada."
        elif "cin >> a >> b;" in lt:
            return "Lee dos valores numéricos ingresados por el usuario y los guarda en las variables 'a' y 'b'."
        elif "Suma:" in lt:
            return "Calcula la suma de 'a' y 'b' y la muestra en la salida estándar."
        elif "Resta:" in lt:
            return "Calcula la resta de 'a' y 'b' y la muestra."
        elif "Producto:" in lt:
            return "Calcula el producto de 'a' y 'b' y lo muestra."
        elif "if (b != 0)" in lt:
            return "Verifica que el divisor 'b' no sea cero antes de realizar la división para evitar fallos de ejecución."
        elif "Division:" in lt:
            return "Calcula la división real de 'a' entre 'b' y muestra el resultado."
            
    elif "felsius_f" in binary_name:
        if "double celsius;" in lt:
            return "Declara la variable real 'celsius' para almacenar los grados centígrados ingresados."
        elif "fahrenheit =" in lt:
            return "Aplica la fórmula matemática para convertir Celsius a Fahrenheit: (Celsius * 9/5) + 32."
        elif "Fahrenheit:" in lt:
            return "Muestra la temperatura convertida a Fahrenheit en la consola."
            
    elif "circulo" in binary_name:
        if "double radio;" in lt:
            return "Declara la variable 'radio' para guardar el radio del círculo ingresado."
        elif "M_PI" in lt:
            return "Calcula el área usando M_PI (definida en <cmath>) y el radio al cuadrado."
            
    elif "mayor_edad" in binary_name:
        if "int edad;" in lt:
            return "Declara una variable entera para guardar la edad ingresada."
        elif "edad >= 18" in lt:
            return "Evalúa la condición: si el usuario es mayor o igual a 18 años."
        elif "Mayor de edad" in lt:
            return "Línea que se ejecuta si se cumple la condición de mayoría de edad."
        elif "Menor de edad" in lt:
            return "Línea que se ejecuta en el bloque 'else' si el usuario tiene menos de 18 años."
            
    elif "menu" in binary_name:
        if "switch (opcion)" in lt:
            return "Estructura de control switch para ejecutar diferentes bloques basados en el valor de la opción elegida."
        elif "case 1:" in lt:
            return "Se ejecuta si el usuario selecciona la opción 1 (Suma)."
        elif "case 2:" in lt:
            return "Se ejecuta si el usuario selecciona la opción 2 (Resta)."
        elif "case 3:" in lt:
            return "Se ejecuta si el usuario selecciona la opción 3 (Multiplicación)."
        elif "default:" in lt:
            return "Se ejecuta si la opción introducida es inválida (cualquier valor que no sea 1, 2 o 3)."
            
    elif "sumatoria" in binary_name:
        if "int suma = 0;" in lt:
            return "Declara e inicializa la variable acumuladora 'suma' en cero."
        elif "for (" in lt:
            return "Ciclo for para iterar desde 1 hasta el número N de forma consecutiva."
        elif "suma += i;" in lt:
            return "Suma el valor actual del contador 'i' al acumulador de forma aditiva."
            
    elif "pide_clave" in binary_name:
        if "do {" in lt:
            return "Inicio de un ciclo do-while que garantiza que el bloque interno se ejecute al menos una vez."
        elif "while (clave != 1234)" in lt:
            return "Repite el bucle mientras la clave ingresada sea diferente de la clave correcta (1234)."
            
    elif "vector_suma" in binary_name:
        if "int v[5];" in lt:
            return "Declara un vector estático de 5 enteros indexados de 0 a 4."
        elif "suma += v[i];" in lt:
            return "Suma el elemento del vector en la posición 'i' al acumulador 'suma'."
            
    elif "vector_max" in binary_name:
        if "int maximo = v[0];" in lt:
            return "Inicializa la variable 'maximo' con el primer elemento del vector como punto de partida."
        elif "v[i] > maximo" in lt:
            return "Condición que evalúa si el elemento actual en el recorrido del vector es mayor al máximo temporal."
        elif "maximo = v[i];" in lt:
            return "Actualiza el máximo con el elemento mayor encontrado."
            
    elif "texto_reves" in binary_name:
        if "string s;" in lt:
            return "Declara un string para almacenar la palabra ingresada."
        elif "s.length() - 1" in lt:
            return "Bucle que inicia en la última posición (longitud - 1) y decrece hasta la posición 0."
        elif "cout << s[i]" in lt:
            return "Imprime el carácter individual en la posición 'i', mostrando la palabra al revés."
            
    elif "struct_usuario" in binary_name:
        if "struct Persona" in lt:
            return "Define una estructura personalizada llamada 'Persona' con campos heterogéneos."
        elif "Persona p;" in lt:
            return "Instancia la variable 'p' del tipo de la estructura Persona."
        elif "p.nombre" in lt and "cin" in lt:
            return "Lee los campos nombre y edad del usuario directamente a la estructura."
            
    elif "func_factorial" in binary_name:
        if "int factorial(int n)" in lt:
            return "Declara la función 'factorial' que toma un entero N y devuelve su factorial calculado."
            
    elif "func_swap" in binary_name:
        if "int &a, int &b" in lt:
            return "La función recibe los parámetros por referencia (con '&'), permitiendo modificar las variables originales."
        elif "int aux = a;" in lt:
            return "Almacena temporalmente el valor de 'a' en la variable temporal 'aux' para el intercambio."
            
    elif "func_area" in binary_name:
        if "calcularArea" in lt and "double" in lt:
            return "Define la función modular calcularArea que calcula y retorna el producto de la base y altura."
            
    elif "func_defecto" in binary_name:
        if "double iva = 0.15" in lt:
            return "Define un parámetro por defecto 'iva' con valor inicial del 15% (0.15)."
            
    elif "punt_dir" in binary_name:
        if "int *p = &x;" in lt:
            return "Declara el puntero a entero 'p' y le asigna la dirección física de la variable 'x' usando el operador '&'."
        elif "Direccion:" in lt:
            return "Muestra la dirección de memoria hexadecimal apuntada por el puntero 'p'."
            
    elif "punt_aritmetica" in binary_name:
        if "int *p = v;" in lt:
            return "Apunta el puntero al inicio del vector (el nombre del vector es equivalente a su dirección inicial)."
        elif "*(p + i)" in lt:
            return "Usa aritmética de punteros para desreferenciar el elemento i-ésimo del vector: *(p + i)."
            
    elif "punt_dinamico" in binary_name:
        if "new int" in lt:
            return "Reserva memoria en el montón (Heap) para albergar un entero de forma dinámica."
        elif "delete p;" in lt:
            return "Libera la memoria dinámica reservada en el Heap para evitar fugas de memoria."
            
    elif "punt_arreglo" in binary_name:
        if "new int[n]" in lt:
            return "Reserva memoria dinámica en el montón para un arreglo de tamaño 'n' definido por el usuario."
        elif "delete[] p;" in lt:
            return "Libera la memoria dinámica del arreglo completo utilizando corchetes de liberación."
            
    elif "rec_fibo" in binary_name:
        if "fibo(int n)" in lt:
            return "Función recursiva para calcular la sucesión de Fibonacci."
        elif "n < 2" in lt:
            return "Caso base: si N es 0 o 1, retorna N sin realizar llamadas recursivas."
        elif "fibo(n - 1) + fibo(n - 2)" in lt:
            return "Caso inductivo: se autoinvoca para sumar los dos elementos anteriores de la sucesión."
            
    elif "rec_busqueda" in binary_name:
        if "busqueda_rec" in lt:
            return "Función recursiva para realizar búsqueda binaria en un vector ordenado."
        elif "ini > fin" in lt:
            return "Caso base de fallo: si los límites se cruzan, el elemento no existe en el vector (-1)."
        elif "medio = (ini + fin)" in lt:
            return "Determina el elemento central del vector para dividir la búsqueda en dos mitades."
            
    elif "file_escribir" in binary_name:
        if "ofstream" in lt:
            return "Instancia un flujo de salida a archivo para crear y escribir datos en 'salida.txt'."
        elif "archivo.close();" in lt:
            return "Cierra el archivo para vaciar el buffer e indicar al sistema operativo la liberación del fichero."
            
    elif "file_leer" in binary_name:
        if "ifstream" in lt:
            return "Instancia un flujo de entrada para abrir y leer el archivo 'entrada.txt'."
        elif "getline(archivo" in lt:
            return "Lee el archivo línea a línea guardando cada línea de texto en la variable 'linea'."
            
    return "Instrucción C++ estándar que realiza operaciones y control lógico."

def dar_formato_color_cpp(text: str) -> str:
    """Aplica formato HTML de resaltado de sintaxis a las palabras clave de C++."""
    keywords = {
        "#include": '<span class="text-danger">#include</span>',
        "using namespace": '<span class="text-danger">using namespace</span>',
        "int ": '<span class="text-warning">int </span>',
        "bool ": '<span class="text-warning">bool </span>',
        "float ": '<span class="text-warning">float </span>',
        "double ": '<span class="text-warning">double </span>',
        "char ": '<span class="text-warning">char </span>',
        "void ": '<span class="text-warning">void </span>',
        "if": '<span class="text-danger">if</span>',
        "else": '<span class="text-danger">else</span>',
        "for": '<span class="text-danger">for</span>',
        "while": '<span class="text-danger">while</span>',
        "do": '<span class="text-danger">do</span>',
        "switch": '<span class="text-danger">switch</span>',
        "case": '<span class="text-danger">case</span>',
        "break;": '<span class="text-danger">break;</span>',
        "return": '<span class="text-danger">return</span>',
        "sort": '<span class="text-info">sort</span>',
        "cout": '<span class="text-info">cout</span>',
        "cin": '<span class="text-info">cin</span>',
        "cerr": '<span class="text-info">cerr</span>',
        "endl": '<span class="text-info">endl</span>',
        "std::": '<span class="text-muted">std::</span>',
    }
    
    formatted = text
    for key, repl in keywords.items():
        formatted = formatted.replace(key, repl)
        
    return formatted

@solved_bp.route('/<int:ejercicio_id>')
@login_required
def view_solved(ejercicio_id: int):
    """Muestra la explicación paso a paso de un ejercicio resuelto."""
    try:
        ejercicio_repo = SqliteEjercicioRepository()
        use_case = ObtenerEjercicioPorIdUseCase(ejercicio_repo)
        ejercicio = use_case.ejecutar(ejercicio_id)
    except LogicWebException as e:
        flash(e.message, "danger")
        return redirect(url_for('theory.learning_path'))

    # Obtener o generar guía didáctica
    guia = GUIAS_ESTUDIO.get(ejercicio_id)
    if not guia:
        # Fallback por defecto si la ID no está en el catálogo extendido
        guia = {
            "caso_real": ejercicio.descripcion_caso_real,
            "analisis_logico": [
                "Analice la estructura del algoritmo para resolver el caso de negocio.",
                "Revise el pseudocódigo para comprender el flujo antes de compilar en C++.",
                "Compruebe las condiciones límite y los rangos de entrada en el Juez Online."
            ]
        }

    # Generar explicaciones dinámicas de líneas de código C++
    lineas_codigo = []
    binario = ejercicio.ruta_binario_cpp
    if ejercicio.codigo_fuente_cpp:
        for idx, linea in enumerate(ejercicio.codigo_fuente_cpp.splitlines(), 1):
            explicacion = get_explanation_for_line(binario, linea, idx)
            linea_escapada = linea.replace("<", "&lt;").replace(">", "&gt;")
            linea_html = dar_formato_color_cpp(linea_escapada)
            lineas_codigo.append({
                "number": idx,
                "html_content": linea_html,
                "explanation": explicacion
            })

    return render_template(
        'solved/solved.html',
        ejercicio=ejercicio,
        guia=guia,
        lineas_codigo=lineas_codigo
    )
