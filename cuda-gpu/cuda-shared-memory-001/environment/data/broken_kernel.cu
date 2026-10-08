

__global__ void shared_histogram_kernel(
    const unsigned char* input,
    unsigned int* output,
    int n
) {
    __shared__ unsigned int histogram[HISTOGRAM_BINS];
    __shared__ unsigned int block_total;

    for (int bin = threadIdx.x;
         bin < HISTOGRAM_BINS;
         bin += blockDim.x) {
        histogram[bin] = 0;
    }

    if (threadIdx.x == 0) {
        block_total = 0;
    }

    __syncthreads();

    for (int i = blockIdx.x * blockDim.x + threadIdx.x;
         i < n;
         i += blockDim.x * gridDim.x) {
        atomicAdd(&histogram[input[i]], 1U);
    }

    if (threadIdx.x == 0) {
        for (int bin = 0; bin < HISTOGRAM_BINS; ++bin) {
            block_total += histogram[bin];
        }
    }

    if (threadIdx.x < HISTOGRAM_BINS) {
        atomicAdd(&output[threadIdx.x], histogram[threadIdx.x]);
    }

    if (threadIdx.x == 0 && n > 0) {
        output[HISTOGRAM_BINS] += block_total;
    }
}
