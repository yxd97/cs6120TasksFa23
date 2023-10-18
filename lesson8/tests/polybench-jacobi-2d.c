/**
 * This version is stamped on May 10, 2016
 *
 * Contact:
 *   Louis-Noel Pouchet <pouchet.ohio-state.edu>
 *   Tomofumi Yuki <tomofumi.yuki.fr>
 *
 * Web address: http://polybench.sourceforge.net
 */
 /* jacobi-2d.c: this file is part of PolyBench/C */

#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <math.h>
#include <stdlib.h>

/* Include polybench common header. */

/* Include benchmark-specific header. */
#define TSTEPS 40
#define N 90


/* Array initialization. */
static
void init_array(int n,
    double A[][N],
    double B[][N]) {
    int i, j;

    for (i = 0; i < n; i++)
        for (j = 0; j < n; j++) {
            A[i][j] = ((double)i * (j + 2) + 2) / n;
            B[i][j] = ((double)i * (j + 3) + 3) / n;
        }
}


/* DCE code. Must scan the entire live-out data.
   Can be used also to check the correctness of the output. */
static
void print_array(int n,
    double A[][N])

{
    int i, j;
    for (i = 0; i < n; i++)
        for (j = 0; j < n; j++) {
            if ((i * n + j) % 20 == 0) printf("\n");
            printf("%05.2lf ", A[i][j]);
        }
    printf("\n");
}


/* Main computational kernel. The whole function will be timed,
   including the call and return. */
static
void kernel_jacobi_2d(int tsteps,
    int n,
    double A[][N],
    double B[][N]) {
    int t, i, j;

#pragma scop
    for (t = 0; t < TSTEPS; t++) {
        for (i = 1; i < N - 1; i++)
            for (j = 1; j < N - 1; j++)
                B[i][j] = 0.2 * (A[i][j] + A[i][j - 1] + A[i][1 + j] + A[1 + i][j] + A[i - 1][j]);
        for (i = 1; i < N - 1; i++)
            for (j = 1; j < N - 1; j++)
                A[i][j] = 0.2 * (B[i][j] + B[i][j - 1] + B[i][1 + j] + B[1 + i][j] + B[i - 1][j]);
    }
#pragma endscop

}


int main(int argc, char** argv) {
    /* Retrieve problem size. */
    int n = N;
    int tsteps = TSTEPS;
    double (*A)[N];
    double (*B)[N];

    /* Variable declaration/allocation. */
    A = malloc(N*sizeof(*A));
    B = malloc(N*sizeof(*B));


    /* Initialize array(s). */
    init_array(n, A, B);

    /* Run kernel. */
    kernel_jacobi_2d(tsteps, n, A, B);

    /* Prevent dead-code elimination. All live-out data must be printed
       by the function call in argument. */
    print_array(n, A);

    /* Be clean. */
    free(A);
    free(B);

    return 0;
}