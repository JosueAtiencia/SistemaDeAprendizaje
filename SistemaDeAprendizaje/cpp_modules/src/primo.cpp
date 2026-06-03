/**
 * LogicWeb UTA - Ejercicio 3: Verificador de Números Primos
 * Este programa verifica si un entero es primo usando el límite optimizado de raíz cuadrada.
 */

#include <iostream>

using namespace std;

int main() {
    int n;
    
    if (!(cin >> n)) {
        cerr << "Error: Entrada no valida en C++ (debe ser un numero entero)." << endl;
        return 1;
    }
    
    // Los números <= 1 no son primos
    if (n <= 1) {
        cout << "El numero " << n << " es NO PRIMO" << endl;
        return 0;
    }
    
    bool es_primo = true;
    
    // Optimización crucial: iterar únicamente hasta la raíz cuadrada de n (i * i <= n)
    for (int i = 2; i * i <= n; i++) {
        if (n % i == 0) {
            es_primo = false;
            break; // Romper el ciclo de inmediato
        }
    }
    
    if (es_primo) {
        cout << "El numero " << n << " es PRIMO" << endl;
    } else {
        cout << "El numero " << n << " es NO PRIMO" << endl;
    }
    
    return 0;
}
