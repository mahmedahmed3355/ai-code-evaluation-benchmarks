from pathlib import Path
import re


SOURCE = Path("/app/src/reduction.cu")


def read_source():
    assert SOURCE.exists(), f"Missing required artifact: {SOURCE}"
    source = SOURCE.read_text()
    assert source.strip(), "reduction.cu is empty"
    return source


def function_body(source, name):
    match = re.search(
        rf"__global__\s+void\s+{re.escape(name)}\s*\([^)]*\)\s*\{{",
        source,
        re.MULTILINE,
    )
    assert match, f"Missing CUDA kernel: {name}"

    start = match.end()
    depth = 1
    pos = start

    while pos < len(source) and depth:
        if source[pos] == "{":
            depth += 1
        elif source[pos] == "}":
            depth -= 1
        pos += 1

    assert depth == 0, f"Could not parse body of {name}"
    return source[start:pos - 1]


def test_cuda_source_exists_and_is_nontrivial():
    source = read_source()

    assert len(source) >= 1000
    assert "__global__" in source
    assert "cudaMalloc" in source
    assert "cudaFree" in source


def test_reduction_kernel_is_preserved():
    source = read_source()
    body = function_body(source, "reduce_sum_kernel")

    assert "threadIdx.x" in body
    assert "blockIdx.x" in body
    assert "blockDim.x" in body
    assert "__shared__" in body
    assert "__syncthreads()" in body
    assert "partial_sums" in body


def test_finalize_kernel_is_preserved():
    source = read_source()
    body = function_body(source, "finalize_sum_kernel")

    assert "partial_sums" in body
    assert "num_blocks" in body
    assert "__shared__ float shared[BLOCK_SIZE]" in body
    assert "__syncthreads()" in body
    assert "shared[tid]" in body
    assert "*output" in body


def test_kernel_interfaces_are_preserved():
    source = read_source()

    assert re.search(
        r"__global__\s+void\s+reduce_sum_kernel\s*\(",
        source,
    )

    assert re.search(
        r"__global__\s+void\s+finalize_sum_kernel\s*\(",
        source,
    )

    assert re.search(
        r"void\s+reduce_sum\s*\(\s*"
        r"const\s+float\s*\*\s*d_input\s*,\s*"
        r"float\s*\*\s*d_output\s*,\s*"
        r"int\s+n\s*"
        r"\)",
        source,
        re.DOTALL,
    )


def test_launch_configuration_is_preserved():
    source = read_source()

    assert re.search(
        r"reduce_sum_kernel\s*<<<\s*num_blocks\s*,\s*BLOCK_SIZE\s*>>>",
        source,
    )

    assert re.search(
        r"finalize_sum_kernel\s*<<<\s*1\s*,\s*BLOCK_SIZE\s*>>>",
        source,
    )


def test_input_boundary_handling_is_preserved():
    source = read_source()

    assert "n + BLOCK_SIZE - 1" in source

    body = function_body(source, "reduce_sum_kernel")

    assert "blockIdx.x" in body
    assert "blockDim.x" in body


def test_all_partial_sums_are_addressable():
    source = read_source()
    body = function_body(source, "finalize_sum_kernel")

    # The repaired final reduction must explicitly iterate over
    # num_blocks rather than loading only partial_sums[tid].
    assert "num_blocks" in body

    assert re.search(
        r"\bfor\s*\([^)]*\b(?:i|idx|offset|block)\b[^)]*;",
        body,
        re.DOTALL,
    ), "No loop found for traversing partial sums."

    # The loop bound may contain a cast, e.g.
    # i < static_cast<unsigned int>(num_blocks)
    assert re.search(
        r"\b(?:i|idx|offset|block)\s*<[^;\n]*\bnum_blocks\b",
        body,
    ), "Partial-sum traversal is not bounded by num_blocks."


def test_multi_block_stride_is_present():
    source = read_source()
    body = function_body(source, "finalize_sum_kernel")

    assert re.search(
        r"\b(?:i|idx|offset|block)\s*\+=",
        body,
    ), "No loop stride found for multi-block traversal."

    assert "BLOCK_SIZE" in body
    assert "num_blocks" in body


def test_shared_memory_reduction_is_not_removed():
    source = read_source()
    body = function_body(source, "finalize_sum_kernel")

    assert "__shared__ float shared[BLOCK_SIZE]" in body

    assert re.search(
        r"for\s*\([^)]*\bstride\b[^)]*BLOCK_SIZE\s*/\s*2",
        body,
        re.DOTALL,
    ), "Original shared-memory reduction loop was removed."

    assert "shared[tid + stride]" in body
    assert "__syncthreads()" in body


def test_cuda_implementation_is_preserved():
    source = read_source()
    lowered = source.lower()

    forbidden = [
        "std::accumulate",
        "std::reduce",
        "numpy",
        "torch.sum",
    ]

    for token in forbidden:
        assert token not in lowered, (
            f"Forbidden CPU/high-level replacement detected: {token}"
        )

    assert "__global__" in source
    assert "cudaMalloc" in source
    assert "cudaFree" in source
    assert "<<<" in source
    assert ">>>" in source


def test_no_hardcoded_results():
    source = read_source()
    body = function_body(source, "finalize_sum_kernel")

    assert "partial_sums[" in body
    assert "num_blocks" in body

    assert not re.search(
        r"\*\s*output\s*=\s*[0-9]+(?:\.[0-9]+)?\s*;",
        body,
    )


def test_final_reduction_consumes_every_partial_sum():
    source = read_source()
    body = function_body(source, "finalize_sum_kernel")

    # Must have a traversal loop.
    assert re.search(r"\bfor\s*\(", body)

    # Must use the actual number of partial blocks.
    assert "num_blocks" in body

    # Accept the normal repaired form:
    # partial_sums[i]
    # and equivalent loop-variable names.
    assert re.search(
        r"partial_sums\s*\[\s*(?:i|idx|offset|block)\s*\]",
        body,
    ), "Partial sums are not indexed by the traversal variable."

    # Must accumulate them instead of merely reading them.
    assert re.search(
        r"\bvalue\s*\+=\s*partial_sums\s*\[",
        body,
    )


def test_no_trivial_zero_workload_solution():
    source = read_source()

    assert "reduce_sum_kernel" in source
    assert "finalize_sum_kernel" in source
    assert "partial_sums" in source

    body = function_body(source, "finalize_sum_kernel")

    assert re.search(
        r"if\s*\(\s*tid\s*==\s*0\s*\)",
        body,
    )
