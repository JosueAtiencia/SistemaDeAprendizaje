#include <iostream>
using namespace std;

int main() {
    int clave;
    do {
        cin >> clave;
    } while (clave != 1234);
    cout << "Clave correcta" << endl;
    return 0;
}
