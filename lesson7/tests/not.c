#include <stdio.h>

int bool_func(int a) {
    return !a;
}

int main() {
    for (int a = 0; a < 2; a++) {
        printf("not %d -> %d\n", a, bool_func(a));
    }
    return 0;
}
