#include <cuda_runtime.h>

#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <vector>

void reduce_sum(
    const float* d_input,
    float* d_output,
    int n
);

static void check_cuda(cudaError_t err, const char* where) {
    if (err != cudaSuccess) {
        std::fprintf(
            stderr,
            "CUDA error at %s: %s\n",
            where,
            cudaGetErrorString(err)
        );
        std::exit(1);
    }
}

static float cpu_reference(const std::vector<float>& input) {
    float sum = 0.0f;

    for (float value : input) {
        sum += value;
    }

    return sum;
}

static std::vector<float> make_input(int n) {
    std::vector<float> input(n);

    for (int i = 0; i < n; ++i) {
        /*
         * Deterministic pattern with both positive and negative
         * values. Keeping the magnitude small makes the expected
         * result stable across the tested configurations.
         */
        input[i] = static_cast<float>((i % 17) - 8) * 0.125f;
    }

    return input;
}

static bool run_case(int n) {
    std::printf("Testing n=%d ... ", n);
    std::fflush(stdout);

    std::vector<float> input = make_input(n);

    const float expected = cpu_reference(input);

    float* d_input = nullptr;
    float* d_output = nullptr;

    check_cuda(
        cudaMalloc(
            &d_input,
            input.size() * sizeof(float)
        ),
        "cudaMalloc(d_input)"
    );

    check_cuda(
        cudaMalloc(
            &d_output,
            sizeof(float)
        ),
        "cudaMalloc(d_output)"
    );

    check_cuda(
        cudaMemcpy(
            d_input,
            input.data(),
            input.size() * sizeof(float),
            cudaMemcpyHostToDevice
        ),
        "cudaMemcpy(input)"
    );

    check_cuda(
        cudaMemset(
            d_output,
            0,
            sizeof(float)
        ),
        "cudaMemset(output)"
    );

    reduce_sum(
        d_input,
        d_output,
        n
    );

    check_cuda(
        cudaGetLastError(),
        "reduce_sum launch"
    );

    check_cuda(
        cudaDeviceSynchronize(),
        "reduce_sum execution"
    );

    float actual = 0.0f;

    check_cuda(
        cudaMemcpy(
            &actual,
            d_output,
            sizeof(float),
            cudaMemcpyDeviceToHost
        ),
        "cudaMemcpy(output)"
    );

    check_cuda(cudaFree(d_input), "cudaFree(d_input)");
    check_cuda(cudaFree(d_output), "cudaFree(d_output)");

    const float tolerance = 1e-4f;

    const bool passed =
        std::fabs(actual - expected) <= tolerance;

    if (passed) {
        std::printf(
            "PASS (expected=%.6f actual=%.6f)\n",
            expected,
            actual
        );
    } else {
        std::printf(
            "FAIL (expected=%.6f actual=%.6f diff=%.6f)\n",
            expected,
            actual,
            std::fabs(actual - expected)
        );
    }

    return passed;
}

int main() {
    /*
     * These cases deliberately cover:
     *
     * - tiny input
     * - one element
     * - just below a block
     * - exactly one block
     * - just above a block
     * - multiple blocks
     * - a large input
     *
     * The implementation must work for all of them.
     */
    const int test_sizes[] = {
        1,
        7,
        31,
        32,
        127,
        255,
        256,
        257,
        511,
        512,
        1023,
        1024,
        1025,
        4097,
        65537
    };

    constexpr int num_tests =
        sizeof(test_sizes) / sizeof(test_sizes[0]);

    int failures = 0;

    for (int i = 0; i < num_tests; ++i) {
        if (!run_case(test_sizes[i])) {
            ++failures;
        }
    }

    if (failures != 0) {
        std::fprintf(
            stderr,
            "\nFAILED: %d/%d test cases failed.\n",
            failures,
            num_tests
        );
        return 1;
    }

    std::printf(
        "\nALL %d REDUCTION TESTS PASSED.\n",
        num_tests
    );

    return 0;
}
