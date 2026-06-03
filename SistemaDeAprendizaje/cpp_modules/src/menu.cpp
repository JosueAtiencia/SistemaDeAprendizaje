#include <iostream>
using namespace std;

int main() {
    int opcion;
    double n1, n2;
    cin >> opcion >> n1 >> n2;
    switch (opcion) {
        case 1:
            cout << "Suma: " << n1 + n2 << endl;
            break;
        case 2:
            cout << "Resta: " << n1 - n2 << endl;
            break;
        case 3:
            cout << "Producto: " << n1 * n2 << endl;
            break;
        default:
            cout << "Opcion no valida" << endl;
            break;
    }
    return 0;
}
