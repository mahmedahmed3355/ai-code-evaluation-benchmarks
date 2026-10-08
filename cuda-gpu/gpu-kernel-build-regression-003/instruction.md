# GPU Kernel Build Regression Investigation

A GPU-kernel build pipeline is producing an artifact that is internally consistent but violates the project's release optimization contract. A second integrity weakness allows a stale or tampered artifact to be accepted when its reported optimization fields look acceptable.

Investigate the repository, reproduce the failure, identify the configuration-precedence and artifact-integrity problems, and repair the existing workflow.

## Goal

The normal workflow must produce an optimized release artifact whose configuration is derived from the supported release profile and whose provenance can be verified.

The final workflow must:

- resolve the supported release profile correctly;
- prevent legacy local overrides from replacing protected optimization settings;
- preserve legitimate non-contract local settings;
- generate an artifact from the resolved configuration;
- bind the artifact to the configuration that produced it;
- reject stale or tampered artifacts;
- pass the benchmark and complete validation workflow.

## Configuration model

The repository contains four configuration sources:

1. `build.conf` — base build settings;
2. `release.profile` — authoritative release optimization settings;
3. `benchmark.conf` — benchmark requirements and workload metadata;
4. `local.override` — legacy/local compatibility settings.

The optimization contract is the set of release fields required by the benchmark:

- `BUILD_TYPE`
- `OPT_LEVEL`
- `FAST_MATH`
- `VECTOR_WIDTH`
- `DEBUG_SYMBOLS`
- `LTO`
- `ARTIFACT_MODE`

`benchmark.conf` describes requirements; it is not an override layer for the release optimization values.

Legacy local settings must remain usable, but they must not replace protected release fields.

## Investigation

Do not assume the first failing value is the root cause.

Inspect:

- configuration sources and precedence;
- generated resolved/effective configuration;
- artifact generation and provenance;
- benchmark scoring and integrity checks;
- diagnostic output;
- the complete validation workflow.

Reproduce the regression before choosing a fix.

## Artifact integrity

A generated artifact contains a configuration digest. The validation workflow must be able to establish that the artifact corresponds to the configuration currently being validated.

A build that merely prints the expected optimization values is not sufficient.

## Constraints

Do not:

- modify `/tests`;
- modify the reference contract;
- replace the build system;
- bypass or disable validation;
- hard-code a passing benchmark result;
- generate a fake artifact;
- delete configuration sources;
- remove the benchmark stage;
- replace the existing workflow with a new implementation;
- depend on network services or external state.

Preserve the existing repository structure and command interfaces.

## Completion

Run:

`/app/scripts/validate.sh`

The build must produce the correct release artifact, the benchmark must verify both optimization correctness and artifact provenance, and the complete validation workflow must pass.

The solution must remain correct when legacy/local configuration values change without violating the release contract.
