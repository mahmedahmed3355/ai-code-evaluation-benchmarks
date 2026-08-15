# Benchmark Engineering Playbook

> Design principles, task-engineering strategies, anti-cheating defenses,
> coverage methodology, difficulty calibration, and validation practices
> used in this benchmark portfolio.

This document summarizes the engineering methodology used to design the
Terminal-Bench 3–oriented tasks in this repository.

The objective is not to make tasks difficult for the sake of difficulty.

The objective is to create evaluations that are:

- Solvable
- Reliable
- Sensitive
- Robust
- Generalizable
- Reproducible
- Resistant to shortcuts
- Scientifically meaningful

---

# 1. Core Benchmark Philosophy

An AI-agent benchmark is treated as an engineered evaluation system rather
than a collection of coding questions.

A benchmark consists of:

```text
Task Instructions
       +
Agent Environment
       +
Reference / Oracle Solution
       +
Evaluation Protocol
       +
Verification
       +
Anti-Cheating Mechanisms
       +
Failure-Mode Analysis
       ↓
Meaningful Evaluation Signal


The central distinction is:

Benchmark Score ≠ True Capability

The benchmark should maximize the relationship between measured performance
and the underlying capability being evaluated.

A benchmark should therefore resist:

Benchmark-specific tricks
Memorization
Hardcoding
Test exploitation
Environment exploitation
Reward hacking
Narrow pattern matching
2. The Validation Hierarchy

The most important rule in the workflow is:

Capability Definition
        ↓
Oracle PASS
        ↓
Coverage PASS
        ↓
Difficulty Calibration
        ↓
Security Review
        ↓
Release

Difficulty is never used to hide an invalid task.

A broken Oracle cannot be fixed by increasing difficulty.

Poor coverage cannot be fixed by making the task harder.

An insecure benchmark cannot be fixed by adding more complexity.

The task must first be correct, then complete, then difficult.

3. Task Design Principles

Before implementing a task, define:

Target capability
Real-world engineering context
Expected failure modes
Required artifacts
Constraints that must remain unchanged
Correct system state
Oracle behavior
Verification contract
Potential shortcuts
Generalization requirements

A task should have a clear engineering objective.

The agent should be able to discover the solution through investigation,
reasoning, modification, and validation.

4. Capability Decomposition

A broad capability should be decomposed before task construction.

For software engineering, possible sub-capabilities include:

Code reading
Debugging
Planning
Tool usage
State inspection
Dependency reasoning
API reasoning
Configuration analysis
Concurrency reasoning
Recovery reasoning
Testing
Refactoring
Performance analysis
Architecture reasoning

A benchmark that evaluates only one narrow behavior provides incomplete
coverage.

5. Cross-Artifact Reasoning

A strong Terminal-style task should not necessarily place the entire problem
inside one file.

Related state can be distributed across:

Configuration
     ↓
Runtime State
     ↓
Workloads
     ↓
Dependencies
     ↓
Recovery State
     ↓
Verification Contract

The agent must infer the relationship between these artifacts.

Useful strategies include:

Conflicting configuration/state values
Related state distributed across files
Dependency chains
Generation/epoch mismatches
Configuration/runtime mismatches
Workload/state inconsistencies
Recovery-state inconsistencies
Cross-component invariants

The objective is to force system-level reasoning rather than single-token
editing.

6. Anti-Cheating Engineering

Anti-cheating should use defense in depth.

No single protection should be considered sufficient.

6.1 Hardcoding Resistance

Avoid tasks where a fixed visible example can be hardcoded.

Use:

Multiple interacting invariants
Variable inputs
Multiple workloads
Structural variations
Hidden evaluation cases
State-dependent verification
6.2 Test Leakage Prevention

The agent environment must not expose evaluation internals unnecessarily.

Protect:

test_outputs.py
test.sh
Verifier implementations
Reference solutions
Expected outputs
Evaluation-only datasets

The environment image should contain only the artifacts required by the
agent to solve the task.

6.3 Reference Solution Isolation

Reference solutions belong to the benchmark-development layer.

They should not be copied into the agent environment.

Typical separation:

Agent Environment
├── environment/
│   ├── Dockerfile
│   └── data/
│
Reference Layer
└── solution/
    └── solve.sh


Verification Layer
└── tests/
    ├── Dockerfile
    ├── test.sh
    └── test_outputs.py
6.4 Environment Isolation

The agent environment and verifier environment should be independently
constructed.

The agent should receive:

Problem + Dependencies + Input State

rather than:

Problem + Dependencies + Evaluator + Solution
6.5 State Leakage Resistance

Do not allow agents to exploit:

Previous execution state
Caches
Temporary artifacts
Persistent databases
Leftover generated files
Previous benchmark runs

Tasks should be tested in clean environments where applicable.

6.6 Persistence-Exploit Resistance

A solution should not depend on artifacts surviving a restart unless persistence
is explicitly part of the task.

Where relevant, validate:

Clean Run
    ↓
Modified State
    ↓
Restart
    ↓
Recovery
6.7 Shortcut Rejection

Explicitly reject invalid shortcuts when they violate the engineering contract.

Examples:

Destructive state resets
Removing workloads
Removing partitions
Disabling the relevant subsystem
Bypassing recovery logic
Global synchronization replacing required asynchronous dependencies
Deleting functionality instead of repairing it
6.8 Reward-Hacking Resistance

Verification should validate the actual system contract rather than superficial
signals.

A task should not award success merely because:

A file exists
A string was inserted
A command returned zero
A superficial test passed
A process was disabled

The resulting state must satisfy the intended invariants.

7. Test / Verifier Leakage Audit

Before release, inspect the built agent environment.

Example:

find /app -type f \
  \( \
    -name "test_outputs.py" -o \
    -name "test.sh" -o \
    -name "solve.sh" -o \
    -name "*verifier*" \
  \) \
  -print

Expected result:

No evaluation artifacts exposed to the agent.

The environment should be independently audited after Docker build.

8. Canary / Artifact Tracking

Tasks may contain a Harbor canary identifier to help detect:

Accidental artifact mixing
Task contamination
Incorrect file copying
Repository construction errors

The canary is a development and integrity mechanism.

It should not become part of the task's solution logic.

9. Coverage Engineering

Coverage is not the same as difficulty.

A task can be:

High Difficulty
+
Low Coverage

and still be a poor benchmark.

Coverage should consider:

Functional coverage
Concept coverage
Structural coverage
Semantic coverage
Failure-mode coverage
Adversarial coverage

The handbook defines coverage conceptually as:

Coverage = Breadth × Diversity × Difficulty

Quantity alone is not coverage.

10. Coverage Through Failure Modes

A practical strategy is:

Enumerate Failure Modes
        ↓
Design Tests That Expose Them
        ↓
Identify Coverage Gaps
        ↓
Add Missing Cases

Failure modes should include:

Incorrect assumptions
Planning failures
Execution failures
Recovery failures
Generalization failures
Environmental failures
Shortcut solutions
Partial repairs

The handbook explicitly recommends failure-mode enumeration as a way to
discover missing coverage.

11. Coverage Through Distribution Shift

The same capability should ideally be evaluated under different conditions.

Useful variations include:

Different data sizes
Different input formats
Different environments
Different workloads
Different vocabularies
Different state configurations
Different structural layouts

This reduces dependence on a single visible pattern.

12. Coverage Gaps

Before release, look specifically for:

Missing edge cases
Missing failure modes
Missing scale variations
Missing distribution shifts
Missing adversarial cases
Repeated examples
Overrepresented easy cases
Narrow concept coverage

A benchmark containing many tasks can still suffer from a
Coverage Illusion.

Many files do not automatically mean many capabilities are being measured.

13. Hidden-Test Strategy

Hidden tests can increase evaluation coverage by introducing:

Additional concepts
Rare cases
Adversarial scenarios
Distribution shifts
Unseen structural variations

Hidden tests should not merely repeat visible examples.

Their purpose is to measure generalization and expose shortcuts.

The handbook specifically identifies hidden tests as an important mechanism for
increasing effective coverage.

14. Difficulty Engineering

Difficulty should emerge from genuine reasoning requirements.

Useful difficulty dimensions include:

14.1 Discovery Difficulty

The root cause is not immediately obvious.

14.2 Planning Difficulty

The agent must determine a sequence of correct actions.

14.3 Long-Horizon Difficulty

The solution requires multiple dependent investigation and repair steps.

14.4 Cross-Artifact Difficulty

The correct diagnosis requires combining evidence from several artifacts.

14.5 Generalization Difficulty

The solution must satisfy the underlying contract rather than one visible case.

14.6 Failure-Mode Complexity

Multiple plausible failure mechanisms must be distinguished.

14.7 Preservation Difficulty

The agent must repair the target failure while preserving unrelated behavior.

14.8 Adaptation Difficulty

The agent must respond correctly to intermediate observations or failed
attempts.

15. Difficulty Calibration Strategies

After Coverage PASS, difficulty can be increased through:

Increasing reasoning depth
Increasing artifact relationships
Increasing state dependencies
Increasing long-horizon requirements
Adding plausible distractors
Increasing generalization requirements
Increasing preservation constraints
Introducing multiple interacting failure modes

Avoid artificial difficulty such as:

Broken dependencies
Random failures
Missing packages
Ambiguous instructions
Unstable environments
Arbitrary file changes
Unrelated complexity

Difficulty should come from the capability being measured.

16. Difficulty Escalation Pattern

A useful progression is:

Simple Failure
      ↓
Cross-Artifact Failure
      ↓
Multiple Failure Modes
      ↓
Hidden Dependencies
      ↓
Generalization Requirements
      ↓
Long-Horizon Repair
      ↓
Adversarial / Shortcut-Resistant Task

The benchmark should remain solvable throughout the escalation.

17. Oracle Engineering

The Oracle is not merely a convenient solution script.

It serves as:

Proof of solvability
Reference implementation
Regression detector
Validation instrument
Experimental control

The handbook states that the Oracle establishes the upper bound of achievable
performance.

Before increasing difficulty:

Oracle PASS

must already be established.

18. Specification Synchronization

The following components must remain synchronized:

Instructions
     +
Oracle
     +
Verifier
     +
Tests

A mismatch creates Specification Drift.

Examples:

Instruction ≠ Oracle
Oracle ≠ Verifier
Verifier ≠ Intended Contract

Every benchmark modification should trigger another Oracle validation.

19. Oracle Regression Testing

After modifying:

Instructions
Environment
Data
Tests
Verifier
Oracle

re-run the Oracle.

The target workflow is:

Modification
     ↓
Oracle PASS
     ↓
Coverage Review
     ↓
Security Review
     ↓
Agent Evaluation

Do not assume that a small modification cannot invalidate the benchmark.

20. Failure-Mode Engineering

Before release, ask:

What assumptions can fail?
What shortcuts are possible?
What exploits exist?
What partial solutions might pass?
What state can be manipulated?
What happens after restart?
What happens under different workloads?
What happens under unseen inputs?

Failure-mode analysis often reveals weaknesses that ordinary happy-path tests
do not expose.

21. Agent Evaluation

Benchmark construction is incomplete until agents are evaluated.

Agent runs can reveal:

Unexpected shortcuts
Hidden environment assumptions
Failure trajectories
Weak task instructions
Benchmark saturation
Unintended exploits
Measurement problems

A useful loop is:

Run Agent
    ↓
Analyze Trajectory
    ↓
Identify Weakness
    ↓
Improve Benchmark
    ↓
Re-run Agent
22. Signal Engineering

The benchmark should provide useful separation between systems.

Important properties include:

Score separation
Measurement sensitivity
Stable scoring
Low noise
Failure interpretability
Generalization signal
Resistance to saturation

The objective is not:

Make Everyone Fail

The objective is:

Measure Meaningful Capability Differences
23. Benchmark Saturation

Benchmarks can become saturated when models learn:

Repeated patterns
Benchmark-specific heuristics
Shortcut strategies
Dataset-specific structures

A benchmark should therefore evolve through:

Evaluation
   ↓
Failure Analysis
   ↓
Coverage Expansion
   ↓
Difficulty Calibration
   ↓
New Evaluation

This helps preserve evaluation signal as models improve.

24. Benchmark Design Patterns

Useful patterns include:

Cross-Artifact Invariant Pattern

Correctness depends on relationships between several files.

Recovery-State Pattern

The agent must restore durable state after a failure or restart.

Dependency-Graph Pattern

Multiple components must be repaired in the correct dependency order.

Preservation Pattern

The target repair must not modify unrelated workloads or functionality.

Asynchronous-Ordering Pattern

Correctness depends on event, stream, or concurrency relationships.

Configuration-Contract Pattern

Several configuration fields must remain mutually consistent.

Build-Regression Pattern

A build or compilation regression must be repaired without bypassing the
intended build contract.

State-Reconciliation Pattern

The agent must determine which state represents durable truth and reconcile
inconsistent runtime state.

25. Anti-Patterns

Avoid:

Tasks with no valid solution
Broken Oracle
Unstable environments
Tests that directly expose the solution
Expected outputs embedded in agent-visible artifacts
Single-token fixes presented as complex tasks
Difficulty created by missing dependencies
Ambiguous requirements
Tests that verify implementation rather than behavior
Excessive duplicated examples
Hidden tests unrelated to the intended capability
Reward signals that can be gamed
26. Recommended Task Lifecycle
Capability Definition
        ↓
Task Design
        ↓
Environment Construction
        ↓
Oracle Construction
        ↓
Verifier Construction
        ↓
Infrastructure PASS
        ↓
Oracle PASS
        ↓
Coverage PASS
        ↓
Failure-Mode Review
        ↓
Security / Leakage Audit
        ↓
Difficulty Calibration
        ↓
Agent Evaluation
        ↓
Signal Analysis
        ↓
Iteration
        ↓
Release

This follows the validation hierarchy described in the Terminal-Bench
handbook.

27. Release Checklist

Before considering a task ready:

Capability
 Target capability clearly defined
 Relevant concepts identified
 Failure modes enumerated
 Preservation constraints defined
Infrastructure
 Environment builds successfully
 Verifier builds successfully
 Dependencies are reproducible
 Clean environment tested
Oracle
 Valid solution exists
 Oracle PASS
 Oracle is deterministic
 Oracle survives relevant restart scenarios
 Oracle agrees with the specification
Coverage
 Concepts covered
 Failure modes covered
 Edge cases considered
 Structural diversity considered
 Generalization considered
 Hidden/adversarial coverage considered where applicable
Security
 Verifier isolated
 Reference solution isolated
 Expected outputs protected
 Environment leakage audited
 Shortcut paths reviewed
 State/persistence exploits reviewed
Difficulty
 Oracle PASS completed first
 Coverage PASS completed first
 Difficulty comes from genuine reasoning
 No artificial environment breakage
 Generalization requirements validated
Final Evaluation
 NOP baseline tested
 Oracle tested
 Agent evaluation performed
 Failure trajectories reviewed
 Benchmark signal evaluated
 Final reproducibility check completed
28. Golden Rules
Rule 1 — Oracle Before Difficulty

Never calibrate difficulty before proving solvability.

Rule 2 — Coverage Before Complexity

A difficult task with poor coverage is still a poor benchmark.

Rule 3 — Difficulty Cannot Repair Poor Coverage

More complexity does not automatically create better measurement.

Rule 4 — Security Is Part of Evaluation Quality

A benchmark that can be trivially exploited does not provide reliable signal.

Rule 5 — Verify the Contract, Not the Patch

Multiple valid implementations should be possible when the engineering contract
allows them.

Rule 6 — Preserve Real-World Constraints

Do not reward destructive shortcuts that would be unacceptable in production.

Rule 7 — Analyze Failures, Not Only Scores

A score tells us what happened.

A trajectory and failure analysis help explain why.

Rule 8 — Revalidate After Every Significant Change

Benchmark evolution requires repeated Oracle, coverage, and security validation.

29. Final Principle

The benchmark engineering process can be summarized as:

CORRECT
   ↓
COMPLETE
   ↓
SECURE
   ↓
DIFFICULT
   ↓
INFORMATIVE

Or, more formally:

Oracle PASS
     ↓
Coverage PASS
     ↓
Difficulty Calibration
     ↓
Security Review
     ↓
Signal Validation
     ↓
Release

The goal is not to create the hardest possible benchmark.

The goal is to create a benchmark where success provides credible evidence of
the capability being measured.

A benchmark should first be correct, then complete, then difficult.
