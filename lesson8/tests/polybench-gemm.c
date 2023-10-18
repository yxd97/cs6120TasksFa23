/**
 * This version is stamped on May 10, 2016
 *
 * Contact:
 *   Louis-Noel Pouchet <pouchet.ohio-state.edu>
 *   Tomofumi Yuki <tomofumi.yuki.fr>
 *
 * Web address: http://polybench.sourceforge.net
 */
 /* gemm.c: this file is part of PolyBench/C */

#include <stdio.h>
#include <string.h>
#include <math.h>
#include <stdlib.h>

/* Include benchmark-specific header. */
#define NI 40
#define NJ 20
#define NK 65

/* Array initialization. */
static
void init_array(int ni, int nj, int nk,
    double* alpha,
    double* beta,
    double C[][NJ],
    double A[][NK],
    double B[][NJ]) {
    int i, j;

    *alpha = 1.5;
    *beta = 1.2;
    for (i = 0; i < ni; i++)
        for (j = 0; j < nj; j++)
            C[i][j] = (double)((i * j + 1) % ni) / ni;
    for (i = 0; i < ni; i++)
        for (j = 0; j < nk; j++)
            A[i][j] = (double)(i * (j + 1) % nk) / nk;
    for (i = 0; i < nk; i++)
        for (j = 0; j < nj; j++)
            B[i][j] = (double)(i * (j + 2) % nj) / nj;
}


/* DCE code. Must scan the entire live-out data.
   Can be used also to check the correctness of the output. */
void print_array(int ni, int nj,
    double C[][NJ]) {
    int i, j;

    for (i = 0; i < ni; i++)
        for (j = 0; j < nj; j++) {
            if ((i * ni + j) % 20 == 0) printf("\n");
            printf("%05.2lf ", C[i][j]);
    }
    printf("\n");
}


/* Main computational kernel. The whole function will be timed,
   including the call and return. */
void kernel_gemm(int ni, int nj, int nk,
    double alpha,
    double beta,
    double C[][NJ],
    double A[][NK],
    double B[][NJ]) {
    int i, j, k;

    //BLAS PARAMS
    //TRANSA = 'N'
    //TRANSB = 'N'
    // => Form C := alpha*A*B + beta*C,
    //A is NIxNK
    //B is NKxNJ
    //C is NIxNJ

    for (i = 0; i < NI; i++) {
        for (j = 0; j < NJ; j++)
            C[i][j] *= beta;
        for (k = 0; k < NK; k++) {
            for (j = 0; j < NJ; j++)
                C[i][j] += alpha * A[i][k] * B[k][j];
        }
    }
}


int main(int argc, char** argv) {
    /* Retrieve problem size. */
    int ni = NI;
    int nj = NJ;
    int nk = NK;

    /* Variable declaration/allocation. */
    double alpha;
    double beta;
    double (*C)[NJ];
    double (*A)[NK];
    double (*B)[NJ];
    C = malloc(NI*sizeof(*C));
    A = malloc(NI*sizeof(*A));
    B = malloc(NK*sizeof(*B));

    /* Initialize array(s). */
    init_array(ni, nj, nk, &alpha, &beta, C, A, B);

    /* Run kernel. */
    kernel_gemm(ni, nj, nk, alpha, beta, C, A, B);

    /* Prevent dead-code elimination. All live-out data must be printed
       by the function call in argument. */
    print_array(ni, nj, C);

    /* Be clean. */
    free(C);
    free(A);
    free(B);

    return 0;
}