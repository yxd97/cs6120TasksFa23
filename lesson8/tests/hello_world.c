#include <stdio.h>

int foo() {
    foo_for: for (int i = 10; i > 0; i--) {
        printf("In foo-for: %d", i);
    }
    return 3;
}

int main(int argc, char** argv) {
    printf("Hello world! - %d\n", foo());
    main_for: for (int i = 0; i < 10; i++) {
        main_for_2: for (int j = 0; j < 10; j++) {
            printf("In main-for-2: %d", i + j);
        }
    }
    return 0;
}
