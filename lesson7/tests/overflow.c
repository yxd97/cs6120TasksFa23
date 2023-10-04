#include <stdio.h>
#include <stdlib.h>
// ARGS: 124235
int main(int argc, char** argv) {
    if (argc < 2) {
        return 1;
    }
    int x = atoi(argv[1]);
    int r1 = x * -1234986295;
    printf("%d x %d = %d\n", x, -1234986295, r1);
    int r2 = x * 363563234;
    printf("%d x %d = %d\n", x, 363563234, r2);
    int r3 = x * -1000000000;
    printf("%d x %d = %d\n", x, -1000000000, r3);
    int r4 = x * (1 << 30);
    printf("%d x %d = %d\n", x, (1 << 30), r4);
    int r5 = x * (1 << 31);
    printf("%d x %d = %d\n", x, (1 << 31), r5);
    return 0;
}
