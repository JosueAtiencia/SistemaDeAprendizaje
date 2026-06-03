#include <iostream>
#include <fstream>
#include <string>
using namespace std;

int main() {
    string texto;
    getline(cin >> ws, texto);
    ofstream archivo("salida.txt");
    if (archivo.is_open()) {
        archivo << texto << endl;
        archivo.close();
        cout << "Escrito" << endl;
    } else {
        cout << "Error" << endl;
    }
    return 0;
}
