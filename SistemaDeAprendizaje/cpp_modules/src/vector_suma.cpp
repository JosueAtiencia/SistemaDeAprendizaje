#include <iostream>
using namespace std;

int main() {
    int v[5];
    int suma = 0;
    for (int i = 0; i < 5; i++) {
        cin >> v[i];
        suma += v[i];
    }
    cout << "Suma vector: " << suma << endl;
    return 0;
}
