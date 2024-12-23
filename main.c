#include <stdio.h>

int someFunc(int firstArg, int secondArg) {
    printf("%i\n", firstArg);
    printf("%i\n", secondArg);
    printf("%i\n", -1);
    return -1;
}
    
int main() {
    
    someFunc(3, -2);
    return 0;
}
