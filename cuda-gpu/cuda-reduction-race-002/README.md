# CUDA Reduction Correctness Repair

## Scenario

This benchmark models a production-style CUDA correctness incident in a two-stage reduction.

The first kernel reduces each input block into one partial sum. A second kernel combines the partial sums into the final result.

The failure is intentionally not limited to one ordinary input size. The implementation must remain correct across:

- empty input;
- partial blocks;
- exact block boundaries;
- multiple blocks;
- more partial sums than final-kernel threads;
- partial-sum counts that do not divide evenly by the final block size.

## Why the task is difficult

The visible reduction loop is largely correct. The important reasoning is at the boundary between the host launcher and the final kernel.

The solver has to follow the data-flow from `n` to `num_blocks`, understand the fixed one-block final launch, and determine how all partial sums can be consumed without changing the required two-stage architecture.

The empty-input case adds a separate host-side CUDA launch edge case. A repair that fixes only the large-input behavior is incomplete.

## Constraints

The repair must preserve:

- the two-stage CUDA design;
- kernel interfaces;
- `BLOCK_SIZE == 256`;
- both existing kernel launch configurations;
- GPU execution;
- shared-memory reduction.

CPU accumulation, hard-coded outputs, test modification, and removal of the reduction are not valid solutions.

## Evaluation

The verifier checks the resulting CUDA source for:

- preservation of the reduction kernels and interfaces;
- preservation of the required launch configuration;
- complete traversal of the partial-sum range;
- accumulation of traversed partial sums;
- preservation of shared-memory reduction and synchronization;
- explicit handling of empty input;
- absence of host-side replacement logic;
- absence of test-specific hard-coding and bypasses.

The environment also contains a CUDA executable with boundary-focused runtime cases.

## Author

Mohamed Ahmed  
engmohamedelshrbeny@gmail.com

## Benchmark metadata

Category: Software Engineering / CUDA  
Domain: GPU correctness and parallel reduction  
Environment: Dockerized, CPU metadata verifier with CUDA runtime test artifact  
Design goal: realistic debugging and repair rather than artificial step count.
