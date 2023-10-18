#include <stdio.h>

int foo(int a, int b) {
    int y, i;
    i = 10;
    // define i out of for statement
    // so that if `y=a*b+i' is hoisted, i is still defined
    for (; i > 0; i--) {
        y = a * b + i;
    }
    return y;
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
