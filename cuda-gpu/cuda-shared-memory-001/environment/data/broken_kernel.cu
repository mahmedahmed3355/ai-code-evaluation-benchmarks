#include <cuda_runtime.h>

#ifndef HISTOGRAM_BINS
#define HISTOGRAM_BINS 256
#endif

__global__ void shared_histogram_kernel(
    const unsigned char* input,
    unsigned int* output,
    int n
) {
    __shared__ unsigned int histogram[HISTOGRAM_BINS];

    // Initialize shared memory.
    for (int bin = threadIdx.x;
         bin < HISTOGRAM_BINS;
         bin += blockDim.x) {
        histogram[bin] = 0;
    }

    __syncthreads();

    // Accumulate values into the block-local histogram.
    for (int i = blockIdx.x * blockDim.x + threadIdx.x;
         i < n;
         i += blockDim.x * gridDim.x) {
        atomicAdd(&histogram[input[i]], 1U);
    }

    /*
     * BUG:
     *
     * The block-local histogram is consumed before all threads in
     * the block are guaranteed to have finished updating it.
     *
     * A block-wide synchronization barrier is required here.
     */

    for (int bin = threadIdx.x;
         bin < HISTOGRAM_BINS;
         bin += blockDim.x) {
        atomicAdd(&output[bin], histogram[bin]);
    }
}
