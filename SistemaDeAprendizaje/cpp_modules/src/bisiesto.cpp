/**
 * LogicWeb UTA - Ejercicio 2: Cálculo de Año Bisiesto
 * Este programa evalúa si un año es bisiesto utilizando condicionales compuestos y el operador módulo (%).
 */

#include <iostream>

using namespace std;

int main() {
    int year;
    
    if (!(cin >> year)) {
        cerr << "Error: Entrada no valida en C++ (debe ser un numero entero)." << endl;
        return 1;
    }
    
    // Regla astronómica para años bisiestos
    if ((year % 4 == 0 && year % 100 != 0) || (year % 400 == 0)) {
        cout << "El ano " << year << " es BISIESTO" << endl;
    } else {
        cout << "El ano " << year << " es NO BISIESTO" << endl;
    }
    
    return 0;
}
