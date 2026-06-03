/**
 * LogicWeb UTA - Client-Side Interactive Engine (EdTech Cozy Redesign)
 * Orchestrates AJAX submissions, handles paper stamp animations,
 * manages academic classroom tabs, and coordinates C++ annotator interaction.
 */

document.addEventListener("DOMContentLoaded", () => {
    // 0. Inicializar y Gestionar el Tema (Claro / Oscuro)
    const themeBtn = document.getElementById("theme-toggle-btn");
    const themeIcon = document.getElementById("theme-toggle-icon");

    const aplicarTema = (tema) => {
        if (tema === "light") {
            document.documentElement.setAttribute("data-theme", "light");
            if (themeIcon) {
                themeIcon.className = "bi bi-moon-fill text-accent";
            }
        } else {
            document.documentElement.removeAttribute("data-theme");
            if (themeIcon) {
                themeIcon.className = "bi bi-sun-fill text-warning";
            }
        }
    };

    // Inicialización al cargar la página
    const temaGuardado = localStorage.getItem("theme") || "dark";
    aplicarTema(temaGuardado);

    // Evento Click para alternar temas
    if (themeBtn) {
        themeBtn.addEventListener("click", () => {
            const temaActual = document.documentElement.getAttribute("data-theme") === "light" ? "light" : "dark";
            const nuevoTema = temaActual === "light" ? "dark" : "light";
            localStorage.setItem("theme", nuevoTema);
            aplicarTema(nuevoTema);
        });
    }

    // Evento click para restaurar código original
    const btnReset = document.getElementById("btn-reset-code");
    const editor = document.getElementById("editor-codigo");
    const btnConfirmarRestaurar = document.getElementById("btn-confirmar-restaurar-ok");
    if (btnReset && editor) {
        const modalEl = document.getElementById("modalConfirmarRestaurar");
        const modalInstance = new bootstrap.Modal(modalEl);

        btnReset.addEventListener("click", () => {
            modalInstance.show();
        });

        if (btnConfirmarRestaurar) {
            btnConfirmarRestaurar.addEventListener("click", () => {
                editor.value = editor.getAttribute("data-original");
                modalInstance.hide();
                if (typeof showToast === "function") {
                    showToast("Código original restaurado con éxito.", "success");
                }
            });
        }
    }


    // Autofocus automático al primer campo de entrada editable de cualquier formulario visible
    const primerInput = document.querySelector("form input:not([type='hidden']):not([readonly]):not([disabled]), form select:not([disabled]), form textarea:not([readonly])");
    if (primerInput) {
        setTimeout(() => {
            primerInput.focus();
        }, 100);
    }

    // 1. Inicializar el anotador táctil de C++
    const lineasCodigo = document.querySelectorAll(".code-line-commented");
    const panelExplicacion = document.getElementById("cpp-line-explanation");

    lineasCodigo.forEach(linea => {
        linea.addEventListener("click", () => {
            lineasCodigo.forEach(l => l.classList.remove("code-line-active"));
            linea.classList.add("code-line-active");
            const explicacion = linea.getAttribute("data-explanation");
            if (panelExplicacion && explicacion) {
                panelExplicacion.innerHTML = `
                    <div class="d-flex align-items-start animate-fade-in">
                        <i class="bi bi-info-circle-fill text-accent fs-4 me-2 mt-1"></i>
                        <div>
                            <h6 class="text-white mb-1">Línea: <code>${linea.querySelector('code').innerText}</code></h6>
                            <p class="mb-0 text-muted small">${explicacion}</p>
                        </div>
                    </div>
                `;
            }
        });
    });

    // 2. Manejo interactivo del Formulario de Ejecución C++ (Juez Online)
    const formEjecutar = document.getElementById("form-ejecutar-ejercicio");
    if (formEjecutar) {
        formEjecutar.addEventListener("submit", async (e) => {
            e.preventDefault();

            const ejercicioId = formEjecutar.getAttribute("data-ejercicio-id");
            const loadingOverlay = document.getElementById("loading-overlay");
            const btnSubmit = formEjecutar.querySelector("button[type='submit']");
            const verdictContainer = document.getElementById("verdict-result-container");
            const verdictPlaceholder = document.getElementById("verdict-placeholder-card");

            const formData = new FormData(formEjecutar);
            const data = {};
            formData.forEach((value, key) => data[key] = value);

            const editorEl = document.getElementById("editor-codigo");
            if (editorEl) {
                data["codigo"] = editorEl.value;
            }

            let hayErrores = false;
            formEjecutar.querySelectorAll("input").forEach(input => {
                if (input.value.trim() === "") {
                    input.classList.add("is-invalid");
                    hayErrores = true;
                } else {
                    input.classList.remove("is-invalid");
                }
            });

            if (hayErrores) return;

            // Mostrar cargando con desenfoque
            if (loadingOverlay) loadingOverlay.style.display = "flex";
            if (btnSubmit) {
                btnSubmit.disabled = true;
                btnSubmit.innerHTML = `<span class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>Compilando C++...`;
            }

            try {
                const respuesta = await fetch(`/interactive/${ejercicioId}/run`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(data)
                });

                const resultado = await respuesta.json();

                if (resultado.success) {
                    // Ocultar placeholder inicial
                    if (verdictPlaceholder) {
                        verdictPlaceholder.classList.add("d-none");
                        verdictPlaceholder.classList.remove("d-flex");
                    }

                    // Renderizar veredicto interactivo (Sello del Docente + Pestañas)
                    actualizarVeredictoUI(resultado, verdictContainer, ejercicioId);

                    // Sincronizar tabla de intentos sin recarga
                    agregarIntentoATabla(resultado, data);

                    verdictContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                } else {
                    mostrarAlertaVisual(resultado.error || "Error en la compilación.");
                }

            } catch (error) {
                console.error("Fetch error:", error);
                mostrarAlertaVisual("Fallo de red al conectar con el servidor de evaluación.");
            } finally {
                if (loadingOverlay) loadingOverlay.style.display = "none";
                if (btnSubmit) {
                    btnSubmit.disabled = false;
                    btnSubmit.innerHTML = `<i class="bi bi-play-circle-fill me-1"></i> Ejecutar e Invocar C++`;
                }
            }
        });
    }
});

/**
 * Renderiza el veredicto didáctico con el "Sello del Docente" y un sistema de pestañas de cuaderno de laboratorio
 */
function actualizarVeredictoUI(resultado, container, ejercicioId) {
    if (!container) return;

    const { estado_oj, salida, tiempo_ejecucion, feedback } = resultado;
    ejercicioId = parseInt(ejercicioId);

    // Determinar tokens del sello
    let claseCard = "verdict-ac";
    let textStamp = "ÉXITO";
    let classStamp = "stamp-mark-ac";

    if (estado_oj === "WA") {
        claseCard = "verdict-wa";
        textStamp = "FALLIDO";
        classStamp = "stamp-mark-wa";
    } else if (estado_oj === "RE") {
        claseCard = "verdict-re";
        textStamp = "ERROR RE";
        classStamp = "stamp-mark-re";
    } else if (estado_oj === "TLE") {
        claseCard = "verdict-tle";
        textStamp = "LÍMITE TLE";
        classStamp = "stamp-mark-tle";
    }

    // Generar recomendaciones
    const listaRecomendaciones = feedback.recomendaciones.map(rec => `
        <li class="mb-2 d-flex align-items-start">
            <i class="bi bi-arrow-right-short text-accent me-1 fs-5 mt-0.5"></i>
            <span>${rec}</span>
        </li>
    `).join("");

    // Generar botón de navegación del siguiente reto en caso de éxito
    let nextButtonHtml = "";
    if (estado_oj === "AC") {
        if (ejercicioId < 24) {
            nextButtonHtml = `
                <div class="mt-4 pt-3 border-top border-secondary border-opacity-15 text-center">
                    <a href="/interactive/${ejercicioId + 1}" class="btn btn-success rounded-pill px-4 py-2.5 w-100 fw-bold d-flex align-items-center justify-content-center hover-white">
                        <span>Ir al Siguiente Reto (Reto #${ejercicioId + 1})</span>
                        <i class="bi bi-arrow-right-circle-fill ms-2 fs-5"></i>
                    </a>
                </div>
            `;
        } else {
            nextButtonHtml = `
                <div class="mt-4 pt-3 border-top border-secondary border-opacity-15 text-center">
                    <a href="/theory/path" class="btn btn-warning rounded-pill px-4 py-2.5 w-100 fw-bold d-flex align-items-center justify-content-center">
                        <i class="bi bi-trophy-fill me-2 fs-5 text-dark"></i>
                        <span class="text-dark">¡Felicidades! Has completado todos los retos del mapa</span>
                    </a>
                </div>
            `;
        }
    }

    // Generar explicación del concepto clave por ejercicio
    const conceptosClaveMap = {
        1: `
            <p><strong>Flujo de Salida Estándar (cout):</strong> El objeto <code>cout</code> de la biblioteca <code>&lt;iostream&gt;</code> envía datos al flujo de salida estándar (stdout) conectado a la terminal. El operador de inserción <code>&lt;&lt;</code> serializa el dato a texto.</p>
            <p class="mb-0">Todo programa C++ arranca desde <code>main()</code>. El valor de retorno <code>return 0;</code> indica al sistema operativo que la ejecución finalizó sin errores (código de salida 0). Un valor distinto de cero señala un fallo.</p>
        `,
        2: `
            <p><strong>Operadores Aritméticos y Precedencia:</strong> C++ evalúa <code>*</code> y <code>/</code> antes de <code>+</code> y <code>-</code> (precedencia matemática estándar). La división entre enteros trunca la parte decimal; usar <code>double</code> preserva la precisión.</p>
            <p class="mb-0">La validación <code>if (b != 0)</code> antes de dividir previene errores fatales de ejecución (Floating Point Exception). En sistemas reales, una división por cero no verificada puede colapsar servidores financieros enteros.</p>
        `,
        3: `
            <p><strong>Conversión de Tipos y Fórmulas:</strong> La fórmula <code>F = (C × 9/5) + 32</code> requiere que al menos un operando sea de tipo <code>double</code> para evitar la truncación entera. Si ambos fueran <code>int</code>, <code>9/5</code> daría 1 en vez de 1.8.</p>
            <p class="mb-0">Este fenómeno se llama <em>conversión implícita</em> (casting automático). En C++ se puede forzar una conversión explícita con <code>static_cast&lt;double&gt;(valor)</code> para garantizar la precisión decimal en todo momento.</p>
        `,
        4: `
            <p><strong>Constantes Matemáticas en C++:</strong> La constante <code>M_PI</code> definida en <code>&lt;cmath&gt;</code> proporciona el valor de π con precisión de punto flotante de doble precisión (15-17 dígitos significativos).</p>
            <p class="mb-0">Para cálculos de ingeniería civil (tuberías, secciones circulares), la precisión de <code>double</code> (64 bits IEEE 754) es crítica. Un error de redondeo en π puede acumularse y causar fallos estructurales en cálculos de presión.</p>
        `,
        5: `
            <p><strong>Estructura Condicional if-else:</strong> La sentencia <code>if (edad >= 18)</code> evalúa una expresión booleana. Si es verdadera, ejecuta el bloque del <code>if</code>; de lo contrario, ejecuta el bloque <code>else</code>. Es la base de toda toma de decisiones algorítmica.</p>
            <p class="mb-0">Los operadores relacionales (<code>>=, <=, ==, !=</code>) comparan valores y retornan <code>true</code> (1) o <code>false</code> (0). En sistemas de control de acceso, una condición mal escrita puede abrir puertas a usuarios no autorizados.</p>
        `,
        6: `
            <p><strong>Selección Múltiple con switch-case:</strong> La estructura <code>switch</code> evalúa una expresión entera o de carácter y salta directamente al <code>case</code> correspondiente, siendo más eficiente que cadenas largas de <code>if-else</code>.</p>
            <p class="mb-0">El <code>break</code> es obligatorio después de cada caso para evitar el <em>fall-through</em> (ejecución en cascada). La etiqueta <code>default</code> captura cualquier valor no contemplado, funcionando como red de seguridad contra entradas inválidas.</p>
        `,
        7: `
            <p><strong>Ciclo for y Variable Acumuladora:</strong> El bucle <code>for (int i = 1; i <= N; i++)</code> tiene tres componentes: inicialización, condición de continuación e incremento. La variable acumuladora <code>suma</code> se inicializa en 0 antes del ciclo.</p>
            <p class="mb-0">El patrón acumulador (<code>suma += i</code>) es fundamental en programación: calcular totales de ventas, promedios estadísticos o sumatorias de Gauss. La fórmula cerrada <code>N*(N+1)/2</code> permite verificar que tu bucle es correcto.</p>
        `,
        8: `
            <p><strong>Ciclo do-while para Validación:</strong> A diferencia del <code>while</code>, el ciclo <code>do-while</code> ejecuta el bloque <strong>al menos una vez</strong> antes de evaluar la condición. Es ideal para validar entradas del usuario.</p>
            <p class="mb-0">En sistemas de seguridad (cajeros automáticos, acceso biométrico), se usa este patrón para solicitar credenciales repetidamente hasta que sean correctas, garantizando que el usuario siempre sea consultado al menos una vez.</p>
        `,
        9: `
            <p><strong>Arreglos y Recorrido Secuencial:</strong> Un arreglo <code>int v[5]</code> reserva 5 posiciones contiguas en memoria, indexadas de 0 a 4. Acceder a un índice fuera de rango causa <em>comportamiento indefinido</em> (buffer overflow).</p>
            <p class="mb-0">El recorrido con <code>for</code> y la acumulación <code>suma += v[i]</code> es el patrón básico para procesar listas de datos: precios de productos, lecturas de sensores o calificaciones de estudiantes.</p>
        `,
        10: `
            <p><strong>Algoritmo de Búsqueda del Máximo:</strong> Se inicializa <code>maximo = v[0]</code> (el primer elemento) y se recorre el arreglo comparando cada elemento. Si <code>v[i] > maximo</code>, se actualiza. Al finalizar, <code>maximo</code> contiene el valor más grande.</p>
            <p class="mb-0">Este algoritmo de búsqueda lineal tiene complejidad <strong>O(n)</strong>: examina cada elemento exactamente una vez. Es la técnica estándar para detectar picos de demanda eléctrica, temperaturas máximas o valores críticos en series de datos.</p>
        `,
        11: `
            <p><strong>Cadenas de Caracteres (string):</strong> La clase <code>string</code> de C++ almacena texto como una secuencia de caracteres indexados desde 0. El método <code>.length()</code> retorna la cantidad de caracteres.</p>
            <p class="mb-0">Para invertir una cadena, el bucle inicia en <code>length()-1</code> (último índice) y decrementa hasta 0. Cada <code>s[i]</code> accede al carácter individual en esa posición, imprimiéndolos en orden inverso.</p>
        `,
        12: `
            <p><strong>Estructuras (struct):</strong> Una <code>struct</code> agrupa variables de tipos distintos (string, int, double) bajo un mismo identificador. Cada variable interna se denomina <em>miembro</em> y se accede con el operador punto (<code>.</code>).</p>
            <p class="mb-0">Las estructuras modelan entidades del mundo real: un usuario tiene nombre y edad, un producto tiene precio y código. Son el primer paso hacia la Programación Orientada a Objetos (POO) en C++.</p>
        `,
        13: `
            <p><strong>Funciones y Modularización:</strong> Una función encapsula una tarea reutilizable. Recibe parámetros por valor (copias), procesa la lógica y retorna un resultado con <code>return</code>. El factorial de N se calcula iterativamente: <code>r = r * i</code>.</p>
            <p class="mb-0">El prototipo de función (declaración antes de <code>main()</code>) permite al compilador verificar los tipos de los argumentos y el valor de retorno <strong>antes</strong> de encontrar la definición completa de la función.</p>
        `,
        14: `
            <p><strong>Paso por Referencia (&):</strong> Al declarar un parámetro con <code>&</code>, la función recibe la dirección de la variable original, no una copia. Cualquier modificación dentro de la función altera directamente el valor en el ámbito del llamador.</p>
            <p class="mb-0">El intercambio (swap) usa una variable auxiliar <code>aux</code> para evitar perder datos: <code>aux = a; a = b; b = aux;</code>. Este patrón es la base de todos los algoritmos de ordenamiento (BubbleSort, SelectionSort).</p>
        `,
        15: `
            <p><strong>Sobrecarga de Funciones:</strong> C++ permite definir múltiples funciones con el <strong>mismo nombre</strong> pero con <strong>diferentes parámetros</strong> (distinto número o tipo). El compilador selecciona la versión correcta según los argumentos de la llamada.</p>
            <p class="mb-0">Esto permite calcular áreas de distintas formas geométricas (rectángulo: base × altura, círculo: π × r²) con la misma función <code>calcularArea()</code>, mejorando la legibilidad y mantenibilidad del código.</p>
        `,
        16: `
            <p><strong>Parámetros por Defecto:</strong> C++ permite asignar valores predeterminados a los parámetros de una función: <code>double iva = 0.15</code>. Si el llamador no proporciona ese argumento, se usa el valor por defecto automáticamente.</p>
            <p class="mb-0">Los parámetros por defecto deben declararse de <strong>derecha a izquierda</strong> en la lista de parámetros. Esto simplifica las llamadas frecuentes: <code>calcular(100)</code> usa IVA del 15%, pero <code>calcular(100, 0.19)</code> permite personalizar.</p>
        `,
        17: `
            <p><strong>Punteros y Direcciones de Memoria:</strong> Un puntero (<code>int *p</code>) almacena la dirección hexadecimal de otra variable en la memoria RAM. El operador <code>&</code> obtiene la dirección y <code>*</code> accede al valor apuntado (desreferenciación).</p>
            <p class="mb-0">Los punteros son la conexión directa entre el software y el hardware físico. En sistemas embebidos y drivers, se usan para acceder a registros de periféricos mapeados en direcciones específicas de memoria.</p>
        `,
        18: `
            <p><strong>Aritmética de Punteros:</strong> Cuando se suma un entero <code>i</code> a un puntero, C++ avanza automáticamente <code>i × sizeof(tipo)</code> bytes. Por eso <code>*(p + i)</code> es equivalente a <code>v[i]</code> para acceder al i-ésimo elemento.</p>
            <p class="mb-0">El nombre de un arreglo (<code>v</code>) decae a un puntero constante a su primer elemento. Esta equivalencia arreglo-puntero es uno de los conceptos más importantes y poderosos de C/C++ para programación de bajo nivel.</p>
        `,
        19: `
            <p><strong>Memoria Dinámica (new/delete):</strong> El operador <code>new</code> reserva memoria en el <em>Heap</em> (montón) durante la ejecución. A diferencia de las variables locales (Stack), esta memoria persiste hasta que se libera explícitamente con <code>delete</code>.</p>
            <p class="mb-0">Olvidar llamar a <code>delete</code> causa una <strong>fuga de memoria</strong> (memory leak): el programa consume RAM progresivamente hasta colapsar. En servidores que corren 24/7, una fuga de 1 KB por segundo puede agotar 86 MB de RAM al día.</p>
        `,
        20: `
            <p><strong>Arreglos Dinámicos (new[]/delete[]):</strong> Cuando el tamaño del arreglo no se conoce hasta la ejecución, se usa <code>new int[n]</code> para reservar <code>n</code> posiciones en el Heap. La liberación <strong>obligatoria</strong> se hace con <code>delete[] p</code> (con corchetes).</p>
            <p class="mb-0">Usar <code>delete</code> sin corchetes en un arreglo dinámico causa <em>comportamiento indefinido</em>: solo libera el primer elemento y corrompe la memoria. En C++ moderno, se recomienda usar <code>std::vector</code> para evitar estos errores.</p>
        `,
        21: `
            <p><strong>Recursividad y Caso Base:</strong> Una función recursiva se invoca a sí misma dividiendo el problema en instancias más pequeñas. El <em>caso base</em> (<code>if (n < 2) return n;</code>) detiene la recursión; sin él, la pila de llamadas se desborda (Stack Overflow).</p>
            <p class="mb-0">La secuencia de Fibonacci (<code>fibo(n) = fibo(n-1) + fibo(n-2)</code>) tiene complejidad exponencial O(2ⁿ). Para valores grandes de N, la versión recursiva pura es extremadamente lenta; se optimiza con <em>memoización</em> o programación dinámica.</p>
        `,
        22: `
            <p><strong>Búsqueda Binaria Recursiva:</strong> El algoritmo divide el arreglo ordenado a la mitad en cada paso: compara el elemento central con el objetivo y descarta la mitad que no lo contiene. Su complejidad es <strong>O(log n)</strong>.</p>
            <p class="mb-0">Para un millón de elementos, la búsqueda lineal necesita hasta 1,000,000 comparaciones, pero la binaria solo ~20. El <em>prerrequisito</em> es que el arreglo esté <strong>ordenado</strong>; buscar en un arreglo desordenado produce resultados incorrectos.</p>
        `,
        23: `
            <p><strong>Flujos de Salida a Archivo (ofstream):</strong> La clase <code>ofstream</code> de <code>&lt;fstream&gt;</code> crea un flujo de escritura hacia un archivo de texto en disco. Si el archivo no existe, lo crea; si existe, lo sobrescribe por defecto.</p>
            <p class="mb-0">Es <strong>obligatorio</strong> cerrar el archivo con <code>.close()</code> para vaciar el buffer de escritura al disco. Sin el cierre, los últimos datos pueden perderse porque permanecen en la memoria RAM sin ser transferidos al fichero físico.</p>
        `,
        24: `
            <p><strong>Flujos de Entrada desde Archivo (ifstream):</strong> La clase <code>ifstream</code> abre un archivo existente para lectura secuencial. Se debe verificar con <code>.is_open()</code> que el archivo se abrió correctamente antes de leer.</p>
            <p class="mb-0">El patrón <code>while(getline(archivo, linea))</code> lee el archivo línea por línea hasta alcanzar el fin de archivo (EOF). A diferencia del operador <code>&gt;&gt;</code>, <code>getline()</code> captura líneas completas incluyendo espacios en blanco.</p>
        `
    };
    let conceptoClave = conceptosClaveMap[ejercicioId] || `
        <p class="text-muted mb-0"><i class="bi bi-info-circle me-1"></i> Concepto clave no disponible para este ejercicio.</p>
    `;

    container.innerHTML = `
        <div class="card card-glass border-0 verdict-card ${claseCard} mb-4 position-relative">
            <!-- Sello del Docente (Signature Watermark) -->
            <div class="stamp-mark ${classStamp}">
                ${textStamp}
            </div>

            <div class="card-body p-1">
                <h5 class="text-white fw-bold mb-1">${feedback.titulo}</h5>
                <p class="text-muted small mb-3"><i class="bi bi-cpu me-1"></i> Invocado con éxito en ${tiempo_ejecucion} ms</p>

                <!-- Pestañas del Cuaderno de Laboratorio -->
                <ul class="nav nav-tabs nav-tabs-classroom border-secondary border-opacity-25" id="classroomTabs" role="tablist">
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="analisis-tab" data-bs-toggle="tab" data-bs-target="#analisis-pane" type="button" role="tab" aria-controls="analisis-pane" aria-selected="false">
                            <i class="bi bi-journal-text me-1"></i> Análisis
                        </button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link active" id="consola-tab" data-bs-toggle="tab" data-bs-target="#consola-pane" type="button" role="tab" aria-controls="consola-pane" aria-selected="true">
                            <i class="bi bi-terminal me-1"></i> Consola C++
                        </button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="concepto-tab" data-bs-toggle="tab" data-bs-target="#concepto-pane" type="button" role="tab" aria-controls="concepto-pane" aria-selected="false">
                            <i class="bi bi-lightbulb me-1"></i> Concepto Clave
                        </button>
                    </li>
                </ul>

                <!-- Contenido de las Pestañas -->
                <div class="tab-content" id="classroomTabsContent">
                    <!-- Ficha 1: Análisis Didáctico -->
                    <div class="tab-pane fade" id="analisis-pane" role="tabpanel" aria-labelledby="analisis-tab" tabindex="0">
                        <div class="bg-dark bg-opacity-20 p-3 rounded border border-light border-opacity-5">
                            <h6 class="text-white mb-2 small fw-bold">
                                <i class="bi bi-journal-bookmark-fill text-warning me-1"></i> Notas del Profesor:
                            </h6>
                            <ul class="list-unstyled mb-0 text-secondary small">
                                ${listaRecomendaciones}
                            </ul>
                        </div>
                    </div>

                    <!-- Ficha 2: Consola stdout C++ -->
                    <div class="tab-pane fade show active" id="consola-pane" role="tabpanel" aria-labelledby="consola-tab" tabindex="0">
                        <p class="text-muted small mb-2">Flujo de salida estándar (std::cout) capturado:</p>
                        <pre class="bg-black text-light p-3 rounded font-monospace small border border-secondary border-opacity-20 mb-0" style="max-height: 160px; overflow-y: auto;"><code>${salida || '(Sin salida)'}</code></pre>
                    </div>

                    <!-- Ficha 3: Concepto Clave C++ -->
                    <div class="tab-pane fade" id="concepto-pane" role="tabpanel" aria-labelledby="concepto-tab" tabindex="0">
                        <div class="bg-dark bg-opacity-35 p-3 rounded border border-secondary border-opacity-20 small text-secondary">
                            ${conceptoClave}
                        </div>
                    </div>
                </div>
                ${nextButtonHtml}
            </div>
        </div>
    `;
    container.style.display = "block";

    // Inicializar el sistema de pestañas de Bootstrap en el contenedor inyectado
    const triggerTabList = [].slice.call(container.querySelectorAll('#classroomTabs button'));
    triggerTabList.forEach(triggerEl => {
        const tabTrigger = new bootstrap.Tab(triggerEl);
        triggerEl.addEventListener('click', event => {
            event.preventDefault();
            tabTrigger.show();
        });
    });
}

/**
 * Inserta de manera asíncrona el nuevo intento al inicio de la tabla en el DOM
 */
function agregarIntentoATabla(resultado, inputs) {
    const tablaCuerpo = document.getElementById("attempts-table-body");
    const vacioAlerta = document.getElementById("no-attempts-alert");

    if (!tablaCuerpo) return;
    if (vacioAlerta) vacioAlerta.style.display = "none";

    const { intento_id, estado_oj, salida, feedback } = resultado;
    const inputsStr = Object.entries(inputs).map(([k, v]) => `<strong>${k}:</strong> ${v}`).join(", ");

    let badgeClass = "badge-oj-ac";
    let badgeText = "Éxito";
    if (estado_oj === "WA") {
        badgeClass = "badge-oj-wa";
        badgeText = "Fallecido";
    } else if (estado_oj === "RE" || estado_oj === "TLE") {
        badgeClass = "badge-oj-re";
        badgeText = `Fallecido (${estado_oj})`;
    } else if (estado_oj !== "AC") {
        badgeClass = "badge-oj-re";
        badgeText = estado_oj;
    }

    const fecha = new Date().toLocaleString('es-ES', { hour12: false });

    // Fila principal clicable
    const nuevaFila = document.createElement("tr");
    nuevaFila.className = "animate-fade-in accordion-toggle cursor-pointer bg-transparent border-bottom border-secondary border-opacity-20 text-light-emphasis small";
    nuevaFila.setAttribute("data-bs-toggle", "collapse");
    nuevaFila.setAttribute("data-bs-target", `#collapse-attempt-${intento_id}`);
    nuevaFila.setAttribute("aria-expanded", "false");

    nuevaFila.innerHTML = `
        <td>
            <div class="d-flex align-items-center">
                <i class="bi bi-chevron-down text-muted me-2 collapse-chevron"></i>
                <span class="text-muted small">#${intento_id}</span>
            </div>
        </td>
        <td><code class="text-light-accent">${inputsStr}</code></td>
        <td><pre class="bg-dark text-light p-1 rounded font-monospace small mb-0 d-inline-block px-2" style="max-width: 250px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;"><code>${salida.split('\n')[0] || ''}</code></pre></td>
        <td><span class="badge badge-oj ${badgeClass}">${badgeText}</span></td>
        <td><span class="text-muted small">${fecha}</span></td>
    `;

    // Fila colapsable de detalle
    const nuevaFilaDetalle = document.createElement("tr");
    nuevaFilaDetalle.className = "border-0";

    const recomendaciones = (feedback && feedback.recomendaciones && feedback.recomendaciones.length > 0)
        ? feedback.recomendaciones.map(rec => `
            <li class="mb-1.5 d-flex align-items-start">
                <i class="bi bi-arrow-right-short text-accent me-1 fs-6 mt-0.5"></i>
                <span>${rec}</span>
            </li>
        `).join("")
        : `<li class="text-muted small">No hay recomendaciones adicionales para este intento.</li>`;

    nuevaFilaDetalle.innerHTML = `
        <td colspan="5" class="p-0 border-0">
            <div class="collapse" id="collapse-attempt-${intento_id}">
                <div class="p-3 my-2 rounded border border-secondary border-opacity-15 bg-black bg-opacity-35 mx-3 text-start">
                    <div class="row">
                        <div class="col-md-6 mb-3 mb-md-0">
                            <h6 class="text-white fw-bold mb-2 small">
                                <i class="bi bi-chat-left-text-fill text-accent me-1"></i> Retroalimentación Académica:
                            </h6>
                            <ul class="list-unstyled mb-0 text-secondary small">
                                ${recomendaciones}
                            </ul>
                        </div>
                        <div class="col-md-6">
                            <h6 class="text-white fw-bold mb-2 small">
                                <i class="bi bi-terminal-fill text-accent me-1"></i> Salida stdout Completa:
                            </h6>
                            <pre class="attempt-details-pre text-light p-2.5 rounded font-monospace small mb-0" style="max-height: 150px; overflow-y: auto; font-size: 0.85rem;"><code>${salida}</code></pre>
                        </div>
                    </div>
                </div>
            </div>
        </td>
    `;

    // Insertamos ambas filas consecutivamente al inicio
    tablaCuerpo.insertBefore(nuevaFila, tablaCuerpo.firstChild);
    tablaCuerpo.insertBefore(nuevaFilaDetalle, nuevaFila.nextSibling);
}

/**
 * Muestra alertas de red amigables
 */
function mostrarAlertaVisual(mensaje) {
    if (typeof showToast === "function") {
        showToast(mensaje, "danger");
    } else {
        alert(mensaje);
    }
}
