#include <iostream>
using namespace std;

int main() {
    double a, b;
    cin >> a >> b;
    cout << "Suma: " << a + b << endl;
    cout << "Resta: " << a - b << endl;
    cout << "Producto: " << a * b << endl;
    if (b != 0) {
        cout << "Division: " << a / b << endl;
    } else {
        cout << "Division: No definida" << endl;
    }
    return 0;
}
