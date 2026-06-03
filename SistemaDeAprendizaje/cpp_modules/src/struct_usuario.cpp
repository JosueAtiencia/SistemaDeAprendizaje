#include <iostream>
#include <string>
using namespace std;

struct Persona {
    string nombre;
    int edad;
};

int main() {
    Persona p;
    cin >> p.nombre >> p.edad;
    cout << "Nombre: " << p.nombre << endl;
    cout << "Edad: " << p.edad << endl;
    return 0;
}
