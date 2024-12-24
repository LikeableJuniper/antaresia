#include <stdio.h>

int someFunc(int firstArg, int secondArg) {
    printf("%i\n", firstArg);
    printf("%i\n", secondArg);
    printf("%i\n", -1);
    return -1;
}
    
int main() {
    printf("%s\n", "hello");
    someFunc(3, 6);
    printf("%s\n", "world");
    return 0;
}
