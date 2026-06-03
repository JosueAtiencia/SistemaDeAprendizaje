#include <iostream>
#include <fstream>
#include <string>
using namespace std;

int main() {
    ifstream archivo("entrada.txt");
    string linea;
    if (archivo.is_open()) {
        while (getline(archivo, linea)) {
            cout << linea << endl;
        }
        archivo.close();
    } else {
        cout << "Error" << endl;
    }
    return 0;
}
