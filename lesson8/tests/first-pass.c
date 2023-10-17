#include <stdio.h>

int foo(int a, int b) {
    int x, y;
    for (int i = 10; i > 0; i--) {
        if (i == 10) {
            x = a + b;
            y = a * b;
        } else {
            int xx = x + 1;
            int yy = y - 1;
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
