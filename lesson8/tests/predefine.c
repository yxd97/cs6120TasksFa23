#include <stdio.h>

int foo(int a, int b) {
    int x, y;
    for (int i = 10; i > 0; i--) {
        x = a + b;
        y = a * b;
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
