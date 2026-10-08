import re
from pathlib import Path

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


def test_source_is_cuda_and_nontrivial():
    source = read_source()
    assert len(source) >= 900
    assert "#include <cuda_runtime.h>" in source
    assert "__global__" in source
    assert "cudaMalloc" in source
    assert "cudaFree" in source
    assert "<<<" in source
    assert ">>>" in source


def test_required_interfaces_and_launches_are_preserved():
    source = read_source()

    assert re.search(r"__global__\s+void\s+reduce_sum_kernel\s*\(", source)
    assert re.search(r"__global__\s+void\s+finalize_sum_kernel\s*\(", source)
    assert re.search(
        r"void\s+reduce_sum\s*\(\s*"
        r"const\s+float\s*\*\s*d_input\s*,\s*"
        r"float\s*\*\s*d_output\s*,\s*"
        r"int\s+n\s*\)",
        source,
        re.DOTALL,
    )

    assert re.search(
        r"reduce_sum_kernel\s*<<<\s*num_blocks\s*,\s*BLOCK_SIZE\s*>>>",
        source,
    )
    assert re.search(
        r"finalize_sum_kernel\s*<<<\s*1\s*,\s*BLOCK_SIZE\s*>>>",
        source,
    )
    assert re.search(r"#define\s+BLOCK_SIZE\s+256\b", source)


def test_first_stage_reduction_architecture_is_preserved():
    source = read_source()
    body = function_body(source, "reduce_sum_kernel")

    assert "threadIdx.x" in body
    assert "blockIdx.x" in body
    assert "blockDim.x" in body
    assert "__shared__ float shared[BLOCK_SIZE]" in body
    assert "__syncthreads()" in body
    assert "shared[tid + stride]" in body
    assert "partial_sums[blockIdx.x]" in body


def test_final_stage_keeps_shared_memory_reduction():
    source = read_source()
    body = function_body(source, "finalize_sum_kernel")

    assert "__shared__ float shared[BLOCK_SIZE]" in body
    assert "__syncthreads()" in body
    assert "shared[tid]" in body
    assert "shared[tid + stride]" in body
    assert re.search(
        r"for\s*\([^)]*\bstride\b[^)]*BLOCK_SIZE\s*/\s*2",
        body,
        re.DOTALL,
    )
    assert re.search(r"if\s*\(\s*tid\s*==\s*0\s*\)", body)
    assert "*output = shared[0]" in body


def test_all_partial_sums_are_consumed():
    source = read_source()
    body = function_body(source, "finalize_sum_kernel")

    assert "num_blocks" in body
    assert re.search(
        r"for\s*\([^;]*\b(?:i|idx|offset|block)\b[^;]*;",
        body,
        re.DOTALL,
    )
    assert re.search(
        r"\b(?:i|idx|offset|block)\s*<[^;\n]*\bnum_blocks\b",
        body,
    )
    assert re.search(
        r"\b(?:i|idx|offset|block)\s*\+=",
        body,
    )
    assert re.search(
        r"partial_sums\s*\[\s*(?:i|idx|offset|block)\s*\]",
        body,
    )
    assert re.search(
        r"\bvalue\s*\+=\s*partial_sums\s*\[",
        body,
    )


def test_empty_input_is_handled_before_zero_grid_launch():
    source = read_source()

    match = re.search(r"void\s+reduce_sum\s*\(", source)
    assert match

    body = source[match.start():]
    zero_case = re.search(
        r"if\s*\(\s*n\s*==\s*0\s*\)\s*\{(?P<body>.*?)\}",
        body,
        re.DOTALL,
    )
    assert zero_case, "No explicit n == 0 handling found."

    block = zero_case.group("body")
    assert "cudaMemset" in block
    assert "d_output" in block
    assert re.search(r"\breturn\s*;", block)


def test_zero_case_precedes_first_stage_launch():
    source = read_source()
    reduce_start = source.find("void reduce_sum(")
    assert reduce_start >= 0
    body = source[reduce_start:]

    zero_pos = re.search(r"if\s*\(\s*n\s*==\s*0\s*\)", body).start() if re.search(r"if\s*\(\s*n\s*==\s*0\s*\)", body) else -1
    launch_pos = body.find("reduce_sum_kernel<<<num_blocks, BLOCK_SIZE>>>")

    assert zero_pos >= 0
    assert launch_pos >= 0
    assert zero_pos < launch_pos


def test_partial_buffer_size_tracks_number_of_blocks():
    source = read_source()
    assert re.search(
        r"cudaMalloc\s*\(\s*&d_partial\s*,\s*"
        r"num_blocks\s*\*\s*sizeof\s*\(\s*float\s*\)",
        source,
        re.DOTALL,
    )
    assert "n + BLOCK_SIZE - 1" in source


def test_no_cpu_or_high_level_replacement():
    source = read_source().lower()

    forbidden = [
        "std::accumulate",
        "std::reduce",
        "thrust::reduce",
        "cub::device",
        "numpy",
        "torch.sum",
        "memcpy",
        "printf(\"answer",
    ]
    for token in forbidden:
        assert token not in source, f"Forbidden replacement detected: {token}"


def test_no_test_specific_constants_or_fake_output():
    source = read_source()
    body = function_body(source, "finalize_sum_kernel")

    assert "partial_sums[" in body
    assert "num_blocks" in body
    assert not re.search(
        r"\*\s*output\s*=\s*[-+]?[0-9]+(?:\.[0-9]+)?\s*;",
        body,
    )
    assert not re.search(
        r"if\s*\(\s*n\s*==\s*(?:1|7|31|32|127|255|256|257|511|512|1023|1024|1025|65535|65536|65537|131071|131072|131073)\s*\)",
        source,
    )


def test_no_comments_in_cuda_source():
    source = read_source()
    assert "//" not in source
    assert "/*" not in source
    assert "*/" not in source


def test_no_direct_final_host_accumulation():
    source = read_source()
    reduce_body = source[source.find("void reduce_sum("):]

    assert not re.search(r"\bfor\s*\([^)]*\)\s*\{[^}]*d_input", reduce_body, re.DOTALL)
    assert not re.search(r"\bfor\s*\([^)]*\)\s*\{[^}]*d_partial", reduce_body, re.DOTALL)


def test_final_kernel_has_no_single_element_only_shortcut():
    source = read_source()
    body = function_body(source, "finalize_sum_kernel")

    assert "num_blocks" in body
    assert "partial_sums" in body
    assert "shared" in body
    assert "__syncthreads()" in body
