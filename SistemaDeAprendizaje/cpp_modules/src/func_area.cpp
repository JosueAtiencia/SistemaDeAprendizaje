#include <iostream>
using namespace std;

double calcularArea(double b, double h) {
    return b * h;
}

int main() {
    double base, altura;
    cin >> base >> altura;
    cout << "Area: " << calcularArea(base, altura) << endl;
    return 0;
}
