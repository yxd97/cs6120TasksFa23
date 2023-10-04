#include <stdio.h>
#include <stdlib.h>
// ARGS: 2
int main(int argc, char** argv) {
    if (argc < 2) {
        return 1;
    }
    int x = atoi(argv[1]);
    int r1 = x * 3;
    printf("%d x %d = %d\n", x, 3, r1);
    return 0;
}
