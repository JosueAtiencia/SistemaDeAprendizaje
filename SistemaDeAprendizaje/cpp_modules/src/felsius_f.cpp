#include <iostream>
using namespace std;

int main() {
    double celsius;
    cin >> celsius;
    double fahrenheit = (celsius * 9.0 / 5.0) + 32.0;
    cout << "Fahrenheit: " << fahrenheit << endl;
    return 0;
}
