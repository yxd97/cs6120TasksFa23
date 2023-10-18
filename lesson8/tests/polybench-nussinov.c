/**
 * This version is stamped on May 10, 2016
 *
 * Contact:
 *   Louis-Noel Pouchet <pouchet.ohio-state.edu>
 *   Tomofumi Yuki <tomofumi.yuki.fr>
 *
 * Web address: http://polybench.sourceforge.net
 */
 /* nussinov.c: this file is part of PolyBench/C */

#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <math.h>
#include <stdlib.h>

/* Include benchmark-specific header. */
#define N 180

/* RNA bases represented as chars, range is [0,3] */
typedef char base;

#define match(b1, b2) (((b1)+(b2)) == 3 ? 1 : 0)
#define max_score(s1, s2) ((s1 >= s2) ? s1 : s2)

/* Array initialization. */
static
void init_array(int n,
    base seq[],
    int table[][N]) {
    int i, j;

    //base is AGCT/0..3
    for (i = 0; i < n; i++) {
        seq[i] = (base)((i + 1) % 4);
    }

    for (i = 0; i < n; i++)
        for (j = 0; j < n; j++)
            table[i][j] = 0;
}


/* DCE code. Must scan the entire live-out data.
   Can be used also to check the correctness of the output. */
static
void print_array(int n,
    int table[][N])

{
    int i, j;
    int t = 0;

    for (i = 0; i < n; i++) {
        for (j = i; j < n; j++) {
            if (t % 20 == 0) printf("\n");
            printf("%d", table[i][j]);
            t++;
        }
    }
    printf("\n");

}


/* Main computational kernel. The whole function will be timed,
   including the call and return. */
   /*
     Original version by Dave Wonnacott at Haverford College <davew@cs.haverford.edu>,
     with help from Allison Lake, Ting Zhou, and Tian Jin,
     based on algorithm by Nussinov, described in Allison Lake's senior thesis.
   */
static
void kernel_nussinov(int n, base seq[],
    int table[][N]) {
    int i, j, k;

    for (i = N - 1; i >= 0; i--) {
        for (j = i + 1; j < N; j++) {

            if (j - 1 >= 0)
                table[i][j] = max_score(table[i][j], table[i][j - 1]);
            if (i + 1 < N)
                table[i][j] = max_score(table[i][j], table[i + 1][j]);

            if (j - 1 >= 0 && i + 1 < N) {
                /* don't allow adjacent elements to bond */
                if (i < j - 1)
                    table[i][j] = max_score(table[i][j], table[i + 1][j - 1] + match(seq[i], seq[j]));
                else
                    table[i][j] = max_score(table[i][j], table[i + 1][j - 1]);
            }

            for (k = i + 1; k < j; k++) {
                table[i][j] = max_score(table[i][j], table[i][k] + table[k + 1][j]);
            }
        }
    }
}


int main(int argc, char** argv) {
    /* Retrieve problem size. */
    int n = N;

    /* Variable declaration/allocation. */
    base* seq = malloc(N*sizeof(*seq));
    int (*table)[N];
    table = malloc(N*sizeof(*table));

    /* Initialize array(s). */
    init_array(n, seq, table);

    /* Run kernel. */
    kernel_nussinov(n, seq, table);

    /* Prevent dead-code elimination. All live-out data must be printed
       by the function call in argument. */
    print_array(n, table);

    /* Be clean. */
    free(seq);
    free(table);

    return 0;
}