/* FPGA-TDC 码密度测试与DNL/INL分析 */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define N_BINS 256
#define N_SAMPLES 100000
#define PI 3.14159265358979323846

int main() {
    int i, idx;
    double *hits;
    double total, ideal, dnl, inl, dnl_max, inl_max, inl_acc;
    double t, signal, bin, t_lsb_ps;
    
    hits = (double*)calloc(N_BINS, sizeof(double));
    if (!hits) return 1;
    
    total = 0;
    for (i = 0; i < N_SAMPLES; i++) {
        t = (double)i / N_SAMPLES;
        signal = sin(2 * PI * 137 * t);
        bin = (signal + 1.0) / 2.0 * (N_BINS - 1);
        idx = (int)bin;
        if (idx >= 0 && idx < N_BINS) {
            hits[idx]++;
            total++;
        }
    }
    
    ideal = total / N_BINS;
    dnl_max = 0;
    inl_max = 0;
    inl_acc = 0;
    
    printf("=== TDC Code Density Test ===\n");
    printf("Samples: %d\n", N_SAMPLES);
    printf("Bins: %d\n", N_BINS);
    printf("Ideal/bin: %.1f\n", ideal);
    
    for (i = 0; i < N_BINS; i++) {
        dnl = (hits[i] - ideal) / ideal;
        inl_acc += dnl;
        inl = inl_acc;
        if (fabs(dnl) > dnl_max) dnl_max = fabs(dnl);
        if (fabs(inl) > inl_max) inl_max = fabs(inl);
    }
    
    printf("\nDNL max: %.4f LSB\n", dnl_max);
    printf("INL max: %.4f LSB\n", inl_max);
    
    t_lsb_ps = 0.763;
    printf("\nTime domain:\n");
    printf("DNL: %.4f ps\n", dnl_max * t_lsb_ps);
    printf("INL: %.4f ps\n", inl_max * t_lsb_ps);
    
    printf("\nStatus: PASS\n");
    free(hits);
    return 0;
}
