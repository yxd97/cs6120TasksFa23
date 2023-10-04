#include <stdio.h>
#include <stdlib.h>
// ARGS: 7
int main(int argc, char** argv) {
    if (argc < 2) {
        return 1;
    }
    int x = atoi(argv[1]);
    int r1 = x * 245;
    printf("%d x %d = %d\n", x, 245, r1);
    int r2 = x * 234;
    printf("%d x %d = %d\n", x, 234, r2);
    int r3 = x * 5;
    printf("%d x %d = %d\n", x, 5, r3);
    int r4 = x * 10;
    printf("%d x %d = %d\n", x, 10, r4);
    int r5 = x * 349562397;
    printf("%d x %d = %d\n", x, 349562397, r5);
    return 0;
}