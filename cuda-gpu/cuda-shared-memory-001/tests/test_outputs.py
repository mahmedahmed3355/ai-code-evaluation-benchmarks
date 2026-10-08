import re
from pathlib import Path

SOURCE = Path("/app/src/broken_kernel.cu")


def source():
    assert SOURCE.exists(), f"Missing source file: {SOURCE}"
    return SOURCE.read_text(encoding="utf-8")


def barriers(text):
    return [m.start() for m in re.finditer(r"\b__syncthreads\s*\(\s*\)", text)]


def test_kernel_and_signature_are_preserved():
    text = source()
    assert "__global__" in text
    assert "__shared__ unsigned int histogram[HISTOGRAM_BINS];" in text
    assert "__shared__ unsigned int block_total;" in text
    signature = re.compile(
        r"__global__\s+void\s+shared_histogram_kernel\s*"
        r"\(\s*const\s+unsigned\s+char\s*\*\s*input\s*,\s*"
        r"unsigned\s+int\s*\*\s*output\s*,\s*int\s+n\s*\)"
    )
    assert signature.search(text)


def test_accumulation_uses_shared_atomic_histogram():
    text = source()
    assert "atomicAdd(&histogram[input[i]], 1U);" in text
    assert "blockIdx.x * blockDim.x + threadIdx.x" in text
    assert "i += blockDim.x * gridDim.x" in text


def test_accumulation_barrier_precedes_shared_reads():
    text = source()
    accumulation = text.find("atomicAdd(&histogram[input[i]], 1U);")
    reduction = text.find("unsigned int local_total = 0;")
    assert accumulation >= 0 and reduction > accumulation
    assert any(accumulation < p < reduction for p in barriers(text))


def test_reduction_is_distributed_across_the_block():
    text = source()
    assert "for (int bin = threadIdx.x;" in text
    assert "bin += blockDim.x" in text
    assert "local_total += histogram[bin];" in text
    assert "atomicAdd(&block_total, local_total);" in text


def test_reduction_barrier_precedes_final_total_publication():
    text = source()
    reduce_atomic = text.find("atomicAdd(&block_total, local_total);")
    global_publish = text.find("atomicAdd(&output[threadIdx.x], histogram[threadIdx.x]);")
    final_publish = text.find("output[HISTOGRAM_BINS] += block_total;")
    assert 0 <= reduce_atomic < global_publish < final_publish
    assert any(reduce_atomic < p < global_publish for p in barriers(text))


def test_block_wide_barriers_are_unconditional():
    text = source()
    for match in re.finditer(r"if\s*\([^\n{}]*threadIdx\.x[^\n{}]*\)\s*\{[^{}]*__syncthreads", text, re.DOTALL):
        raise AssertionError("__syncthreads() is hidden inside a thread-dependent branch")
    assert len(barriers(text)) >= 3
    assert "return" not in text


def test_no_host_or_cpu_shortcut():
    text = source()
    assert "cudaDeviceSynchronize" not in text
    assert "cudaMemcpy" not in text
    assert "__threadfence" not in text
    assert "system(" not in text
