#include <stdio.h>
#include <stdlib.h>
// ARGS: 3
int main(int argc, char** argv) {
    if (argc < 2) {
        return 1;
    }
    int x = atoi(argv[1]);
    int r1 = -3 * x ;
    printf("%d x %d = %d\n", -3, x, r1);
    int r2 = 112233 * x;
    printf("%d x %d = %d\n", 112233, x, r2);
    int r3 = 0x00c0ffee * x;
    printf("%d x %d = %d\n", 0x00c0ffee, x, r3);
    int r4 = -1 * x;
    printf("%d x %d = %d\n", -1, x, r4);
    int r5 = -43958 * x;
    printf("%d x %d = %d\n", -43958, x,  r5);
    return 0;
}
