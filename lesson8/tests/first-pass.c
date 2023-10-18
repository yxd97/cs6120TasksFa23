#include <stdio.h>

int foo(int a, int b) {
    int x = 0;
    int y = 0;
    // x and y does not dominate all their uses
    // in the end, x should be a + b, y should be a - b
    // if hoisted, x will be a + b + 10, y should be a - b + 10
    for (int i = 10; i > 0; i--) {
        if (i < 10) {
            x = a + b;
            y = a * b;
        } else {
            x = x + 1;
            y = y + 1;
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
