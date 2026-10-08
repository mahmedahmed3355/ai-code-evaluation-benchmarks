#include <cuda_runtime.h>
#include <cstdio>
#include <cstdlib>

#define BLOCK_SIZE 256

__global__ void reduce_sum_kernel(
    const float* input,
    float* partial_sums,
    int n
) {
    __shared__ float shared[BLOCK_SIZE];

    const unsigned int tid = threadIdx.x;
    const unsigned int global_idx =
        blockIdx.x * blockDim.x + threadIdx.x;

    float value = 0.0f;

    if (global_idx < n) {
        value = input[global_idx];
    }

    shared[tid] = value;
    __syncthreads();

    for (unsigned int stride = BLOCK_SIZE / 2;
         stride > 0;
         stride >>= 1) {

        if (tid < stride) {
            shared[tid] += shared[tid + stride];
        }

        __syncthreads();
    }

    if (tid == 0) {
        partial_sums[blockIdx.x] = shared[0];
    }
}

__global__ void finalize_sum_kernel(
    const float* partial_sums,
    float* output,
    int num_blocks
) {
    __shared__ float shared[BLOCK_SIZE];

    const unsigned int tid = threadIdx.x;

    float value = 0.0f;

    if (tid < num_blocks) {
        value = partial_sums[tid];
    }

    shared[tid] = value;
    __syncthreads();

    for (unsigned int stride = BLOCK_SIZE / 2;
         stride > 0;
         stride >>= 1) {

        if (tid < stride) {
            shared[tid] += shared[tid + stride];
        }

        __syncthreads();
    }

    if (tid == 0) {
        *output = shared[0];
    }
}

void reduce_sum(
    const float* d_input,
    float* d_output,
    int n
) {
    const int num_blocks =
        (n + BLOCK_SIZE - 1) / BLOCK_SIZE;

    float* d_partial = nullptr;

    cudaMalloc(
        &d_partial,
        num_blocks * sizeof(float)
    );

    reduce_sum_kernel<<<num_blocks, BLOCK_SIZE>>>(
        d_input,
        d_partial,
        n
    );

    finalize_sum_kernel<<<1, BLOCK_SIZE>>>(
        d_partial,
        d_output,
        num_blocks
    );

    cudaFree(d_partial);
}
