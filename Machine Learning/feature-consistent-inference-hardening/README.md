# Feature-Consistent Inference Hardening

## Difficulty explanation
This task is difficult because the repair crosses CSV parsing, transactional streaming, persisted preprocessing, model calibration, artifact replacement, evaluation semantics, and an independently checked audit result. The failures interact across stages, so a locally plausible repair can still produce inconsistent predictions, stale deployment state, incorrect metrics, or an audit that does not describe the committed batch.

## Solution explanation
The reference repair uses a validation pass followed by bounded chunk processing, applies the persisted transformation contract in order, treats artifact content as the deployment identity, isolates evaluation state, and computes audit counts from the same accepted input stream as inference. The implementation preserves the public API while adding the optional audit CLI mode.

## Verification explanation
The verifier recomputes expected predictions and audit counts independently and exercises reordered and malformed inputs, late failures, large files, tied scores, artifact replacement, atomic replacement, and evaluation isolation. Positive controls are included so rejecting broad classes of inputs is not sufficient for full credit.

## Relevant experience
I have hands-on experience building Python ML and agent-evaluation systems, including PyTorch, pytest, Docker, Harbor, and Terminal-Bench task environments. I have authored task environments, reference solutions, verifiers, hidden tests, and multi-file debugging tasks across ML, CUDA, backend, MLOps, and infrastructure domains.
