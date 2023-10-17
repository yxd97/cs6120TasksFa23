#include <stdio.h>

int foo(int a, int b) {
    for (int i = 10; i > 0; i--) {
        int x = a + b;
        int y = a * b;
    }
    return a + b + a * b;
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
