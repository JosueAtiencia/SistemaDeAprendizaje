#include <iostream>
using namespace std;

void intercambiar(int &a, int &b) {
    int aux = a;
    a = b;
    b = aux;
}

int main() {
    int a, b;
    cin >> a >> b;
    intercambiar(a, b);
    cout << "Swap: " << a << " " << b << endl;
    return 0;
}
