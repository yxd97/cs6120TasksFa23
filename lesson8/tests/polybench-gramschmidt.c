/**
 * This version is stamped on May 10, 2016
 *
 * Contact:
 *   Louis-Noel Pouchet <pouchet.ohio-state.edu>
 *   Tomofumi Yuki <tomofumi.yuki.fr>
 *
 * Web address: http://polybench.sourceforge.net
 */
 /* gramschmidt.c: this file is part of PolyBench/C */

#include <stdio.h>
#include <string.h>
#include <math.h>
#include <stdlib.h>

/* Include polybench common header. */

/* Include benchmark-specific header. */
#define M 40
#define N 55


/* Array initialization. */
void init_array(int m, int n,
    double(*A)[N],
    double(*R)[N],
    double(*Q)[N]) {
    int i, j;

    for (i = 0; i < m; i++)
        for (j = 0; j < n; j++) {
            A[i][j] = (((double)((i * j) % m) / m) * 100) + 10;
            Q[i][j] = 0.0;
        }
    for (i = 0; i < n; i++)
        for (j = 0; j < n; j++)
            R[i][j] = 0.0;
}


/* DCE code. Must scan the entire live-out data.
   Can be used also to check the correctness of the output. */
void print_array(int m, int n,
    double(*A)[N],
    double(*R)[N],
    double(*Q)[N]) {
    int i, j;

    printf("R:[\n");
    for (i = 0; i < n; i++) {
        printf("[");
        for (j = 0; j < n; j++) {
            if (j % 20 == 19) printf("\n");
            printf("%06.2lf ", R[i][j]);
        }
        printf("]\n");
    }
    printf("]\n");

    printf("Q:[\n");
    for (i = 0; i < m; i++) {
        printf("[");
        for (j = 0; j < n; j++) {
            if (j % 20 == 19) printf("\n");
            printf("%06.2lf ", Q[i][j]);
        }
        printf("]\n");
    }
    printf("]\n");
}


/* Main computational kernel. The whole function will be timed,
   including the call and return. */
   /* QR Decomposition with Modified Gram Schmidt:
    http://www.inf.ethz.ch/personal/gander/ */
void kernel_gramschmidt(int m, int n,
    double(*A)[N],
    double(*R)[N],
    double(*Q)[N]) {
    int i, j, k;

    double nrm;

    for (k = 0; k < N; k++) {
        nrm = 0.0;
        for (i = 0; i < M; i++)
            nrm += A[i][k] * A[i][k];
        R[k][k] = sqrt(nrm);
        for (i = 0; i < M; i++)
            Q[i][k] = A[i][k] / R[k][k];
        for (j = k + 1; j < N; j++) {
            R[k][j] = 0.0;
            for (i = 0; i < M; i++)
                R[k][j] += Q[i][k] * A[i][j];
            for (i = 0; i < M; i++)
                A[i][j] = A[i][j] - Q[i][k] * R[k][j];
        }
    }
}


int main(int argc, char** argv) {
    /* Retrieve problem size. */
    int m = M;
    int n = N;

    /* Variable declaration/allocation. */
    double(*A)[N];
    double(*R)[N];
    double(*Q)[N];
    A = malloc(M*sizeof(*A));
    R = malloc(N*sizeof(*R));
    Q = malloc(M*sizeof(*Q));

    /* Initialize array(s). */
    init_array(m, n, A, R, Q);

    /* Run kernel. */
    kernel_gramschmidt(m, n, A, R, Q);

    /* Prevent dead-code elimination. All live-out data must be printed
       by the function call in argument. */
    print_array(m, n, A, R, Q);

    /* Be clean. */
    free(A);
    free(R);
    free(Q);

    return 0;
}
