#include <iostream>
using namespace std;

int factorial(int n) {
    int fact = 1;
    for (int i = 1; i <= n; i++) {
        fact *= i;
    }
    return fact;
}

int main() {
    int n;
    cin >> n;
    if (n < 0) {
        cout << "Error" << endl;
    } else {
        cout << "Factorial: " << factorial(n) << endl;
    }
    return 0;
}
