#include <stdio.h>

int foo(int a, int b) {
    int x, y, i, j;
    i = 10;
    j = 0;
    for (; i > 0; i--) {
        for (; j < 5; j++) {
            y = a * b + i;
            x = b + j;
        }
    }
    return x + y;
}

int main(int argc, char** argv) {
    int a = 10;
    int b = 15;

    printf(
        "a:%d, b:%d, foo(a, b) = %d",
        a, b, foo(a, b)
    );
    return 0;
}
