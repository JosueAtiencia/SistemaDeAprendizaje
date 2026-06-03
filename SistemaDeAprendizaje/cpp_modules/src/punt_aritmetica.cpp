#include <iostream>
using namespace std;

int main() {
    int v[5] = {10, 20, 30, 40, 50};
    int *p = v;
    for (int i = 0; i < 5; i++) {
        cout << *(p + i) << " ";
    }
    cout << endl;
    return 0;
}
