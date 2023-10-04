#include <stdio.h>
#include <stdlib.h>
// ARGS: 3
int main(int argc, char** argv) {
    if (argc < 2) {
        return 1;
    }
    int x = atoi(argv[1]);
    int r1 = x * -3;
    printf("%d x %d = %d\n", x, -3, r1);
    int r2 = x * -245;
    printf("%d x %d = %d\n", x, -245, r2);
    int r3 = x * -63;
    printf("%d x %d = %d\n", x, -63, r3);
    int r4 = x * -1;
    printf("%d x %d = %d\n", x, -1, r4);
    int r5 = x * -43959688;
    printf("%d x %d = %d\n", x, -43959688, r5);
    return 0;
}