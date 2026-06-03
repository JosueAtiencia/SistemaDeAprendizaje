/**
 * LogicWeb UTA - Ejercicio 4: Ordenamiento de 3 Números
 * Este programa lee tres enteros y los imprime ordenados de menor a mayor usando std::sort.
 */

#include <iostream>
#include <algorithm>

using namespace std;

int main() {
    int a, b, c;
    
    if (!(cin >> a >> b >> c)) {
        cerr << "Error: Entradas no validas en C++ (deben ser tres enteros)." << endl;
        return 1;
    }
    
    int arr[3] = {a, b, c};
    
    // Usar la ordenación estándar optimizada de C++
    sort(arr, arr + 3);
    
    cout << "Numeros ordenados: " << arr[0] << " " << arr[1] << " " << arr[2] << endl;
    
    return 0;
}
