#include <stdio.h>
#include <stdlib.h>
// ARGS: 3 5
int main(int argc, char** argv) {
    if (argc < 3) {
        return 1;
    }
    int x1 = atoi(argv[1]);
    int x2 = atoi(argv[2]);
    int r1 = -3 * x1 * x2 ;
    printf("%d x %d x %d = %d\n", -3, x1, x2, r1);
    int r2 = 1233 * x1 * -233;
    printf("%d x %d x %d = %d\n", 1233, x1, -233, r2);
    int r3 = x1 * 213 * x2;
    printf("%d x %d x %d = %d\n", x1, 213, x2, r3);
    int r4 = x2 * -214 * -9;
    printf("%d x %d x %d = %d\n", x2, -214, -9, r4);
    int r5 = x1 * 134 * x2 * 2 * x1 * -3;
    printf("%d x %d x %d x %d x %d x %d = %d\n", x1, 134, x2, 2, x1, -3, r5);
    return 0;
}
