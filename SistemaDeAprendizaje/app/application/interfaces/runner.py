"""
Interfaz del Ejecutor de C++ - LogicWeb UTA
Contrato abstracto para el servicio de ejecución segura e independiente de binarios C++.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class CppRunnerInterface(ABC):
    
    @abstractmethod
    def ejecutar(self, nombre_binario: str, inputs: Dict[str, Any], codigo: Optional[str] = None) -> dict:
        """
        Ejecuta el binario C++ precompilado pasando los datos de entrada por stdin.
        
        Args:
            nombre_binario (str): Nombre del archivo binario ejecutable (ej. 'factorial.exe' o 'factorial').
            inputs (Dict[str, Any]): Diccionario con las entradas ingresadas por el usuario.
            codigo (Optional[str]): Código fuente opcional escrito por el estudiante.
            
        Returns:
            dict: Diccionario que contiene:
                - 'salida': stdout generado por la ejecución.
                - 'error': stderr capturado o descripción del fallo.
                - 'estado_oj': Código del Juez Online ('AC', 'WA', 'RE', 'TLE').
                - 'tiempo_ejecucion': Tiempo en segundos medido del proceso.
        """
        pass

