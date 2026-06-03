#include <iostream>
using namespace std;

int main() {
    int *p = new int;
    *p = 100;
    cout << "Valor: " << *p << endl;
    delete p;
    return 0;
}
