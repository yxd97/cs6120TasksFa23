#include <stdio.h>

int bool_func(int a, int b, int c) {
    return (a && b) || (a && c) || (b && c);
}

int bool_func_dual(int a, int b, int c) {
    return !((!a || !b) && (!a || !c) && (!b || !c));
}

int main() {
    for (int a = 0; a < 2; a++) {
        for (int b = 0; b < 2; b++) {
            for (int c = 0; c < 2; c++) {
                printf("     f(%d, %d, %d) -> %d\n", a, b, c, bool_func(a, b, c));
            }
        }
    }
    for (int a = 0; a < 2; a++) {
        for (int b = 0; b < 2; b++) {
            for (int c = 0; c < 2; c++) {
                printf("f_dual(%d, %d, %d) -> %d\n", a, b, c, bool_func_dual(a, b, c));
            }
        }
    }
    return 0;
}
