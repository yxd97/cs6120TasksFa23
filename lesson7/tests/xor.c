#include <stdio.h>

int bool_func(int a, int b) {
    return (!a && b) || (a && !b);
}

int main() {
    for (int a = 0; a < 2; a++) {
        for (int b = 0; b < 2; b++) {
            printf("%d xor %d -> %d\n", a, b, bool_func(a, b));
        }
    }
    return 0;
}
