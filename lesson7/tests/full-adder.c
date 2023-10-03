#include <stdio.h>

int bool_func_ha_s(int a, int b) {
    return (!a && b) || (a && !b);
}

int bool_func_ha_co(int a, int b) {
    return a && b;
}

int bool_func_fa_s(int a, int b, int ci) {
    return bool_func_ha_s(bool_func_ha_s(a, b), ci);
}

int bool_func_fa_co(int a, int b, int ci) {
    return bool_func_ha_co(bool_func_ha_s(a, b), ci) || bool_func_ha_co(a, b);
}

int main() {
    for (int a = 0; a < 2; a++) {
        for (int b = 0; b < 2; b++) {
            for (int ci = 0; ci < 2; ci++) {
                printf(
                    "%d + %d + %d -> %d %d\n",
                    a, b, ci,
                    bool_func_fa_co(a, b, ci), bool_func_fa_s(a, b, ci)
                );
            }
        }
    }
    return 0;
}
