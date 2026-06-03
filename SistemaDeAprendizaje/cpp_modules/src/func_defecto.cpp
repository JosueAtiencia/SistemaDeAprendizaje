#include <iostream>
using namespace std;

double calc(double p, double iva = 0.15) {
    return p * (1.0 + iva);
}

int main() {
    double precio;
    cin >> precio;
    cout << "Precio con IVA: " << calc(precio) << endl;
    return 0;
}
