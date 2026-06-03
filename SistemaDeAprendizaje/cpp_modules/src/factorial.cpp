/**
 * LogicWeb UTA - Ejercicio 1: Factorial de un Número
 * Este programa calcula el factorial de un entero N ingresado por teclado (stdin).
 * Muestra el comportamiento clásico de desbordamiento en enteros (overflow) para N > 12.
 */

#include <iostream>

using namespace std;

int main() {
    int n;
    
    // Leer el entero desde la entrada estándar
    if (!(cin >> n)) {
        cerr << "Error: Entrada no valida en C++ (debe ser un numero entero)." << endl;
        return 1;
    }
    
    // Validación de negocio
    if (n < 0) {
        cout << "El factorial de numeros negativos no esta definido." << endl;
        return 0;
    }
    
    // Cálculo multiplicativo acumulado
    int fact = 1;
    for (int i = 1; i <= n; i++) {
        fact *= i; // Aquí ocurre desbordamiento si n > 12
    }
    
    // Salida estándar
    cout << "Resultado: " << fact << endl;
    
    return 0;
}
