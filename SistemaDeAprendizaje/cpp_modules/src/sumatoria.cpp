#include <iostream>
using namespace std;

int main() {
    int n;
    cin >> n;
    int suma = 0;
    for (int i = 1; i <= n; i++) {
        suma += i;
    }
    cout << "Sumatoria: " << suma << endl;
    return 0;
}
