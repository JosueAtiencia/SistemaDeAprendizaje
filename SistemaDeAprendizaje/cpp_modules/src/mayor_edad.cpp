#include <iostream>
using namespace std;

int main() {
    int edad;
    cin >> edad;
    if (edad >= 18) {
        cout << "Mayor de edad" << endl;
    } else {
        cout << "Menor de edad" << endl;
    }
    return 0;
}
