#include <iostream>
using namespace std;

int busqueda_rec(const int v[], int dato, int ini, int fin) {
    if (ini > fin) return -1;
    int medio = (ini + fin) / 2;
    if (dato == v[medio]) {
        return medio;
    } else if (dato < v[medio]) {
        return busqueda_rec(v, dato, ini, medio - 1);
    } else {
        return busqueda_rec(v, dato, medio + 1, fin);
    }
}

int main() {
    int v[3];
    for (int i = 0; i < 3; i++) {
        cin >> v[i];
    }
    int target;
    cin >> target;
    int pos = busqueda_rec(v, target, 0, 2);
    if (pos == -1) {
        cout << "No esta" << endl;
    } else {
        cout << "Posicion: " << pos << endl;
    }
    return 0;
}
