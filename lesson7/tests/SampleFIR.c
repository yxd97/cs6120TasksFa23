#include <stdio.h>
#include <stdlib.h>

/*

FIR filter designed with
 http://t-filter.appspot.com

sampling frequency: 5000 Hz

fixed point precision: 16 bits

* 0 Hz - 1800 Hz
  gain = 1
  desired ripple = 5 dB
  actual ripple = 4.06 dB

* 2000 Hz - 2500 Hz
  gain = 0
  desired attenuation = -40 dB
  actual attenuation = -40.25 dB

*/

#define SAMPLEFILTER_TAP_NUM 27

typedef struct {
    int history[SAMPLEFILTER_TAP_NUM];
    unsigned int last_index;
} SampleFilter;

void SampleFilter_init(SampleFilter* f);
void SampleFilter_put(SampleFilter* f, int input);
int SampleFilter_get(SampleFilter* f);

/*
static int filter_taps[SAMPLEFILTER_TAP_NUM] = {
    751,
    2830,
    972,
    -1485,
    976,
    -31,
    -1021,
    1708,
    -1493,
    71,
    2380,
    -5189,
    7425,
    24491,
    7425,
    -5189,
    2380,
    71,
    -1493,
    1708,
    -1021,
    -31,
    976,
    -1485,
    972,
    2830,
    751
};
*/

void SampleFilter_init(SampleFilter* f) {
    int i;
    for(i = 0; i < SAMPLEFILTER_TAP_NUM; ++i)
        f->history[i] = 0;
    f->last_index = 0;
}

void SampleFilter_put(SampleFilter* f, int input) {
    f->history[f->last_index++] = input;
    if(f->last_index == SAMPLEFILTER_TAP_NUM)
        f->last_index = 0;
}

int SampleFilter_get(SampleFilter* f) {
    int acc = 0;
    int index = f->last_index;
        index = index != 0 ? index-1 : SAMPLEFILTER_TAP_NUM-1;
        acc += f->history[index] * 751;
        index = index != 0 ? index-1 : SAMPLEFILTER_TAP_NUM-1;
        acc += f->history[index] * 2830;
        index = index != 0 ? index-1 : SAMPLEFILTER_TAP_NUM-1;
        acc += f->history[index] * 972;
        index = index != 0 ? index-1 : SAMPLEFILTER_TAP_NUM-1;
        acc += f->history[index] * -1485;
        index = index != 0 ? index-1 : SAMPLEFILTER_TAP_NUM-1;
        acc += f->history[index] * 976;
        index = index != 0 ? index-1 : SAMPLEFILTER_TAP_NUM-1;
        acc += f->history[index] * -31;
        index = index != 0 ? index-1 : SAMPLEFILTER_TAP_NUM-1;
        acc += f->history[index] * -1021;
        index = index != 0 ? index-1 : SAMPLEFILTER_TAP_NUM-1;
        acc += f->history[index] * 1708;
        index = index != 0 ? index-1 : SAMPLEFILTER_TAP_NUM-1;
        acc += f->history[index] * -1493;
        index = index != 0 ? index-1 : SAMPLEFILTER_TAP_NUM-1;
        acc += f->history[index] * 71;
        index = index != 0 ? index-1 : SAMPLEFILTER_TAP_NUM-1;
        acc += f->history[index] * 2380;
        index = index != 0 ? index-1 : SAMPLEFILTER_TAP_NUM-1;
        acc += f->history[index] * -5189;
        index = index != 0 ? index-1 : SAMPLEFILTER_TAP_NUM-1;
        acc += f->history[index] * 7425;
        index = index != 0 ? index-1 : SAMPLEFILTER_TAP_NUM-1;
        acc += f->history[index] * 24491;
        index = index != 0 ? index-1 : SAMPLEFILTER_TAP_NUM-1;
        acc += f->history[index] * 7425;
        index = index != 0 ? index-1 : SAMPLEFILTER_TAP_NUM-1;
        acc += f->history[index] * -5189;
        index = index != 0 ? index-1 : SAMPLEFILTER_TAP_NUM-1;
        acc += f->history[index] * 2380;
        index = index != 0 ? index-1 : SAMPLEFILTER_TAP_NUM-1;
        acc += f->history[index] * 71;
        index = index != 0 ? index-1 : SAMPLEFILTER_TAP_NUM-1;
        acc += f->history[index] * -1493;
        index = index != 0 ? index-1 : SAMPLEFILTER_TAP_NUM-1;
        acc += f->history[index] * 1708;
        index = index != 0 ? index-1 : SAMPLEFILTER_TAP_NUM-1;
        acc += f->history[index] * -1021;
        index = index != 0 ? index-1 : SAMPLEFILTER_TAP_NUM-1;
        acc += f->history[index] * -31;
        index = index != 0 ? index-1 : SAMPLEFILTER_TAP_NUM-1;
        acc += f->history[index] * 976;
        index = index != 0 ? index-1 : SAMPLEFILTER_TAP_NUM-1;
        acc += f->history[index] * -1485;
        index = index != 0 ? index-1 : SAMPLEFILTER_TAP_NUM-1;
        acc += f->history[index] * 972;
        index = index != 0 ? index-1 : SAMPLEFILTER_TAP_NUM-1;
        acc += f->history[index] * 2830;
        index = index != 0 ? index-1 : SAMPLEFILTER_TAP_NUM-1;
        acc += f->history[index] * 751;
    return acc;
}

// ARGS: 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
int main(int argc, char** argv) {
    if (argc < 2) return 1;
    SampleFilter filter;
    SampleFilter_init(&filter);

    for (int i = 1; i < argc; i++) {
    }
    for (int i = 1; i < argc; i++) {
        SampleFilter_put(&filter, atoi(argv[i]));
        int res = SampleFilter_get(&filter);
        float res_f = (float)res / 65536.0;
        printf("%f ", res_f);
    }

    printf("\n");
    return 0;
}
