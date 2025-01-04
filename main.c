#include <stdio.h>

float someFunc(int firstArg, int secondArg) {
    float res = firstArg + secondArg;
    return res;
}
int main() {
    
    float x = someFunc(3, -4);
    printf("%f\n", x);
    
    float res = 3 + 5;
    printf("%f\n", res);
    
    if (res == 8) {
        printf("%s\n", "hello");
    }
    
    int i = 5;
    while (i > 0) {
        printf("%i\n", i);
        i = i - 1;
    }
    return 0;
}
