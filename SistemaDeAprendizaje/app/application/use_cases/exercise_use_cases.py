"""
Casos de Uso de Ejercicios - LogicWeb UTA
Orquesta la recuperación de ejercicios algorítmicos y el flujo de ejecución interactivo Flask <-> C++.
"""

import time
import math
from typing import List, Optional, Dict, Any
from app.domain.entities import Ejercicio, Intento, Feedback
from app.domain.exceptions import EjercicioNoEncontrado, IntentoInvalido
from app.application.interfaces.repositories import EjercicioRepository, IntentoRepository
from app.application.interfaces.runner import CppRunnerInterface

class ObtenerEjerciciosUseCase:
    def __init__(self, ejercicio_repository: EjercicioRepository):
        self.ejercicio_repository = ejercicio_repository

    def ejecutar(self) -> List[Ejercicio]:
        return self.ejercicio_repository.obtener_todos()


class ObtenerEjercicioPorIdUseCase:
    def __init__(self, ejercicio_repository: EjercicioRepository):
        self.ejercicio_repository = ejercicio_repository

    def ejecutar(self, ejercicio_id: int) -> Ejercicio:
        ejercicio = self.ejercicio_repository.obtener_por_id(ejercicio_id)
        if not ejercicio:
            raise EjercicioNoEncontrado(ejercicio_id)
        return ejercicio


class EjecutarEjercicioUseCase:
    def __init__(
        self,
        ejercicio_repository: EjercicioRepository,
        intento_repository: IntentoRepository,
        cpp_runner: CppRunnerInterface
    ):
        self.ejercicio_repository = ejercicio_repository
        self.intento_repository = intento_repository
        self.cpp_runner = cpp_runner

    def ejecutar(self, usuario_id: int, ejercicio_id: int, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orquesta la ejecución interactiva:
        1. Valida el ejercicio y las entradas en Python.
        2. Invoca al ejecutor C++ mediante subprocesos.
        3. Compara el resultado obtenido con la lógica esperada (Decisión AC vs WA).
        4. Genera feedback gamificado y persiste el intento en la base de datos sqlite.
        """
        ejercicio = self.ejercicio_repository.obtener_por_id(ejercicio_id)
        if not ejercicio:
            raise EjercicioNoEncontrado(ejercicio_id)

        # 1. Extraer código fuente si se envía
        codigo = inputs.pop("codigo", None)

        # 2. Validaciones de entrada preventivas
        self._validar_entradas(ejercicio.ruta_binario_cpp, inputs)

        # 3. Ejecutar C++ a través de la infraestructura
        # Capturamos excepciones de infraestructura (como TLE o RE) y las mapeamos a estados del Online Judge
        inicio_tiempo = time.perf_counter()
        
        try:
            resultado_runner = self.cpp_runner.ejecutar(ejercicio.ruta_binario_cpp, inputs, codigo=codigo)
            salida = resultado_runner["salida"].strip()
            error_msg = resultado_runner["error"].strip()
            estado_oj = resultado_runner["estado_oj"]
            
            # Si el runner no devolvió un error específico (TLE o RE), evaluamos la exactitud del resultado (AC vs WA)
            if estado_oj == "AC":
                es_correcto = self._evaluar_resultado_matematico(ejercicio.ruta_binario_cpp, inputs, salida)
                if not es_correcto:
                    estado_oj = "WA"  # Wrong Answer (el resultado del C++ es lógicamente incorrecto o se desbordó)
            else:
                salida = error_msg if error_msg else "Ocurrió un error en ejecución (RE)."

        except Exception as e:
            # Fallback en caso de que ocurra un error no controlado en infraestructura
            salida = ""
            error_msg = str(e)
            estado_oj = "RE"

        fin_tiempo = time.perf_counter()
        tiempo_ejecucion = fin_tiempo - inicio_tiempo

        # 3. Guardar el intento del estudiante en la base de datos
        intento = Intento(
            id=None,
            usuario_id=usuario_id,
            ejercicio_id=ejercicio_id,
            datos_ingresados=inputs,
            resultado_obtenido=salida,
            estado_oj=estado_oj
        )
        self.intento_repository.guardar(intento)

        # 4. Generar la retroalimentación didáctica basada en las entidades del Dominio
        feedback = Feedback.generar(estado_oj, salida, ejercicio_id, inputs)

        return {
            "intento_id": intento.id,
            "estado_oj": estado_oj,
            "salida": salida,
            "tiempo_ejecucion": round(tiempo_ejecucion, 4),
            "feedback": {
                "titulo": feedback.titulo,
                "color_clase": feedback.color_clase,
                "recomendaciones": feedback.recomendaciones
            }
        }

    def _validar_entradas(self, binario: str, inputs: Dict[str, Any]) -> None:
        """Valida que los campos requeridos estén presentes y en formatos correctos en el backend."""
        binario = binario.lower()
        if binario in ["factorial", "func_factorial"]:
            if "n" not in inputs or inputs["n"] == "":
                raise IntentoInvalido("El número 'n' es requerido.")
            try:
                int(inputs["n"])
            except ValueError:
                raise IntentoInvalido("El valor ingresado para 'n' debe ser un número entero.")
        elif binario == "aritmetica":
            for c in ["a", "b"]:
                if c not in inputs or inputs[c] == "":
                    raise IntentoInvalido(f"El número '{c}' es requerido.")
                try:
                    float(inputs[c])
                except ValueError:
                    raise IntentoInvalido(f"El valor de '{c}' debe ser un número.")
        elif binario == "felsius_f":
            if "celsius" not in inputs or inputs["celsius"] == "":
                raise IntentoInvalido("Los grados Celsius son requeridos.")
            try:
                float(inputs["celsius"])
            except ValueError:
                raise IntentoInvalido("El valor de Celsius debe ser un número.")
        elif binario == "circulo":
            if "radio" not in inputs or inputs["radio"] == "":
                raise IntentoInvalido("El radio es requerido.")
            try:
                float(inputs["radio"])
            except ValueError:
                raise IntentoInvalido("El radio debe ser un número.")
        elif binario == "mayor_edad":
            if "edad" not in inputs or inputs["edad"] == "":
                raise IntentoInvalido("La edad es requerida.")
            try:
                int(inputs["edad"])
            except ValueError:
                raise IntentoInvalido("La edad debe ser un entero.")
        elif binario == "menu":
            for c in ["opcion", "n1", "n2"]:
                if c not in inputs or inputs[c] == "":
                    raise IntentoInvalido(f"El campo '{c}' es requerido.")
                try:
                    if c == "opcion":
                        int(inputs[c])
                    else:
                        float(inputs[c])
                except ValueError:
                    raise IntentoInvalido(f"El campo '{c}' debe ser numérico.")
        elif binario == "sumatoria":
            if "n" not in inputs or inputs["n"] == "":
                raise IntentoInvalido("El límite N es requerido.")
            try:
                int(inputs["n"])
            except ValueError:
                raise IntentoInvalido("N debe ser un entero.")
        elif binario == "pide_clave":
            if "clave" not in inputs or inputs["clave"] == "":
                raise IntentoInvalido("La clave es requerida.")
            try:
                int(inputs["clave"])
            except ValueError:
                raise IntentoInvalido("La clave debe ser un entero.")
        elif binario in ["vector_suma", "vector_max"]:
            for i in range(1, 6):
                c = f"n{i}"
                if c not in inputs or inputs[c] == "":
                    raise IntentoInvalido(f"El número '{i}' es requerido.")
                try:
                    int(inputs[c])
                except ValueError:
                    raise IntentoInvalido(f"El valor {i} debe ser un entero.")
        elif binario == "texto_reves":
            if "texto" not in inputs or inputs["texto"] == "":
                raise IntentoInvalido("El texto es requerido.")
        elif binario == "struct_usuario":
            if "nombre" not in inputs or inputs["nombre"] == "":
                raise IntentoInvalido("El nombre es requerido.")
            if "edad" not in inputs or inputs["edad"] == "":
                raise IntentoInvalido("La edad es requerida.")
            try:
                int(inputs["edad"])
            except ValueError:
                raise IntentoInvalido("La edad debe ser un entero.")
        elif binario == "func_swap":
            for c in ["a", "b"]:
                if c not in inputs or inputs[c] == "":
                    raise IntentoInvalido(f"El valor '{c}' es requerido.")
                try:
                    int(inputs[c])
                except ValueError:
                    raise IntentoInvalido(f"El valor '{c}' debe ser entero.")
        elif binario == "func_area":
            for c in ["base", "altura"]:
                if c not in inputs or inputs[c] == "":
                    raise IntentoInvalido(f"El campo '{c}' es requerido.")
                try:
                    float(inputs[c])
                except ValueError:
                    raise IntentoInvalido(f"El campo '{c}' debe ser un número.")
        elif binario == "func_defecto":
            if "precio" not in inputs or inputs["precio"] == "":
                raise IntentoInvalido("El precio es requerido.")
            try:
                float(inputs["precio"])
            except ValueError:
                raise IntentoInvalido("El precio debe ser un número.")
        elif binario == "punt_arreglo":
            if "n" not in inputs or inputs["n"] == "":
                raise IntentoInvalido("El tamaño N es requerido.")
            try:
                int(inputs["n"])
            except ValueError:
                raise IntentoInvalido("N debe ser entero.")
        elif binario == "rec_fibo":
            if "n" not in inputs or inputs["n"] == "":
                raise IntentoInvalido("El número N es requerido.")
            try:
                int(inputs["n"])
            except ValueError:
                raise IntentoInvalido("N debe ser un entero.")
        elif binario == "rec_busqueda":
            for c in ["n1", "n2", "n3", "target"]:
                if c not in inputs or inputs[c] == "":
                    raise IntentoInvalido(f"El campo '{c}' es requerido.")
                try:
                    int(inputs[c])
                except ValueError:
                    raise IntentoInvalido(f"El campo '{c}' debe ser entero.")
        elif binario == "file_escribir":
            if "texto" not in inputs or inputs["texto"] == "":
                raise IntentoInvalido("El texto para el archivo es requerido.")

    def _evaluar_resultado_matematico(self, binario: str, inputs: Dict[str, Any], salida: str) -> bool:
        """
        Evalúa matemáticamente si la salida producida por el programa C++ es correcta.
        Detecta desbordamientos y errores de lógica.
        """
        import re
        binario = binario.lower()
        salida_upper = salida.upper()
        
        try:
            if binario == "hola":
                return "HOLA A TODOS" in salida_upper

            elif binario == "aritmetica":
                a = float(inputs["a"])
                b = float(inputs["b"])
                lines = salida.splitlines()
                suma_val = None
                resta_val = None
                prod_val = None
                div_val = None
                for line in lines:
                    if "SUMA:" in line.upper():
                        suma_val = float(line.split(":")[-1].strip())
                    elif "RESTA:" in line.upper():
                        resta_val = float(line.split(":")[-1].strip())
                    elif "PRODUCTO:" in line.upper():
                        prod_val = float(line.split(":")[-1].strip())
                    elif "DIVISION:" in line.upper():
                        val_str = line.split(":")[-1].strip()
                        if "NO DEFINIDA" not in val_str.upper():
                            div_val = float(val_str)
                
                if suma_val is None or resta_val is None or prod_val is None:
                    return False
                if suma_val != a + b: return False
                if resta_val != a - b: return False
                if prod_val != a * b: return False
                if b != 0:
                    if div_val is None or div_val != a / b:
                        return False
                else:
                    if "NO DEFINIDA" not in salida_upper:
                        return False
                return True

            elif binario == "felsius_f":
                c = float(inputs["celsius"])
                f_expected = (c * 9.0 / 5.0) + 32.0
                for line in salida.splitlines():
                    if "FAHRENHEIT:" in line.upper():
                        val = float(line.split(":")[-1].strip())
                        return math.isclose(val, f_expected, rel_tol=1e-5)
                return False

            elif binario == "circulo":
                r = float(inputs["radio"])
                if r < 0:
                    return "NAN" in salida_upper or "ERROR" in salida_upper or not salida
                area_expected = math.pi * r * r
                for line in salida.splitlines():
                    if "AREA:" in line.upper():
                        val = float(line.split(":")[-1].strip())
                        return math.isclose(val, area_expected, rel_tol=1e-5)
                return False

            elif binario == "mayor_edad":
                edad = int(inputs["edad"])
                if edad >= 18:
                    return "MAYOR" in salida_upper and "MENOR" not in salida_upper
                else:
                    return "MENOR" in salida_upper

            elif binario == "menu":
                opcion = int(inputs["opcion"])
                n1 = float(inputs["n1"])
                n2 = float(inputs["n2"])
                if opcion == 1:
                    return f"SUMA: {n1 + n2}" in salida_upper or str(n1 + n2) in salida
                elif opcion == 2:
                    return f"RESTA: {n1 - n2}" in salida_upper or str(n1 - n2) in salida
                elif opcion == 3:
                    return f"PRODUCTO: {n1 * n2}" in salida_upper or str(n1 * n2) in salida
                else:
                    return "NO VALIDA" in salida_upper

            elif binario == "sumatoria":
                n = int(inputs["n"])
                if n < 0: return True
                sum_expected = sum(range(1, n + 1))
                for line in salida.splitlines():
                    if "SUMATORIA:" in line.upper():
                        val = int(line.split(":")[-1].strip())
                        return val == sum_expected
                return str(sum_expected) in salida

            elif binario == "pide_clave":
                clave = int(inputs["clave"])
                if clave == 1234:
                    return "CORRECTA" in salida_upper
                else:
                    return False

            elif binario == "vector_suma":
                vals = [int(inputs[f"n{i}"]) for i in range(1, 6)]
                sum_expected = sum(vals)
                return str(sum_expected) in salida

            elif binario == "vector_max":
                vals = [int(inputs[f"n{i}"]) for i in range(1, 6)]
                max_expected = max(vals)
                return str(max_expected) in salida

            elif binario == "texto_reves":
                texto = inputs["texto"]
                rev_expected = texto[::-1]
                return rev_expected in salida

            elif binario == "struct_usuario":
                nombre = inputs["nombre"]
                edad = int(inputs["edad"])
                return nombre.upper() in salida_upper and str(edad) in salida

            elif binario in ["factorial", "func_factorial"]:
                n = int(inputs["n"])
                if n < 0:
                    return "ERROR" in salida_upper or "NO EXISTE" in salida_upper or "NO DEFINIDO" in salida_upper
                fact_expected = math.factorial(n)
                return str(fact_expected) in salida

            elif binario == "func_swap":
                a = int(inputs["a"])
                b = int(inputs["b"])
                return f"{b} {a}" in salida

            elif binario == "func_area":
                base = float(inputs["base"])
                altura = float(inputs["altura"])
                area_expected = base * altura
                return str(area_expected) in salida or math.isclose(float(salida.split(":")[-1].strip()), area_expected, rel_tol=1e-5)

            elif binario == "func_defecto":
                precio = float(inputs["precio"])
                val_15 = precio * 1.15
                val_21 = precio * 1.21
                numeros = [float(x) for x in re.findall(r"[-+]?\d*\.\d+|\d+", salida)]
                if not numeros: return False
                for val in numeros:
                    if math.isclose(val, val_15, rel_tol=1e-3) or math.isclose(val, val_21, rel_tol=1e-3):
                        return True
                return False

            elif binario == "punt_dir":
                return "DIRECCION" in salida_upper or "0X" in salida_upper

            elif binario == "punt_aritmetica":
                return "10" in salida and "20" in salida and "50" in salida

            elif binario == "punt_dinamico":
                return "100" in salida

            elif binario == "punt_arreglo":
                n = int(inputs["n"])
                parts = salida.split()
                return len(parts) >= n

            elif binario == "rec_fibo":
                n = int(inputs["n"])
                def _fib(k):
                    if k < 2: return k
                    v1, v2 = 0, 1
                    for _ in range(2, k + 1):
                        v1, v2 = v2, v1 + v2
                    return v2
                fib_expected = _fib(n)
                return str(fib_expected) in salida

            elif binario == "rec_busqueda":
                n1 = int(inputs["n1"])
                n2 = int(inputs["n2"])
                n3 = int(inputs["n3"])
                target = int(inputs["target"])
                v = [n1, n2, n3]
                pos_expected = v.index(target) if target in v else -1
                if pos_expected == -1:
                    return "NO ESTA" in salida_upper or "NO ENCONTRADO" in salida_upper or "-1" in salida or "NO ENCUENTRA" in salida_upper
                else:
                    return str(pos_expected) in salida

            elif binario == "file_escribir":
                return "ESCRITO" in salida_upper or "COMPLETADA" in salida_upper or "EXITO" in salida_upper or "TEXTO" in salida_upper or "TEXTO ESCRITO" in salida_upper

            elif binario == "file_leer":
                return True

        except Exception:
            return False
            
        return True
