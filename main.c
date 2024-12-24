#include <stdio.h>

float someFunc() {
    float res = 3.5;
    return res;
}

int main() {
    float x = someFunc();
    printf("%f\n", x);
    return 0;
}
