#include <stdio.h>
#include <stdlib.h>
// ARGS: 35
int main(int argc, char** argv) {
    if (argc < 2) {
        return 1;
    }
    int x = atoi(argv[1]);
    int r1 = x * 2;
    printf("%d x %d = %d\n", x, 2, r1);
    int r2 = x * 16;
    printf("%d x %d = %d\n", x, 16, r2);
    int r3 = x * 65536;
    printf("%d x %d = %d\n", x, 65536, r3);
    int r4 = x * 1024;
    printf("%d x %d = %d\n", x, 1024, r4);
    int r5 = x * 1;
    printf("%d x %d = %d\n", x, 1, r5);
    return 0;
}
