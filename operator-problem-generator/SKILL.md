---
name: operator-problem-generator
description: Generate website-ready operator programming problems from an operator specification or framework documentation. Use when Codex needs to create or review a pair of files for an operator problem: a JSON metadata file describing operator prototype, inputs, outputs, dtypes, shapes, and test cases, plus a Python NumPy reference implementation used as the standard answer. Also use when batch-generating many operator problems for a benchmark, contest website, or training dataset.
---

# Operator Problem Generator

## Overview

Use this skill to produce importable operator problem assets for a contest or practice website. The expected output for each problem is a JSON metadata file and a Python reference implementation.

The skill favors format correctness and executable validation over broad operator coverage. Do not generate a large batch until the format contract has been checked against real website examples.

## Core Workflow

1. Identify the operator and scope.
   - Read the user request, source documentation, or operator list.
   - Prefer simple pointwise, comparison, and simple reduction operators for early batches.
   - Defer operators with randomness, state, sparse tensors, FFT, complex linear algebra, device-specific behavior, or unclear numerical tolerances.

2. Load only the needed references.
   - Read `references/problem-format.md` before creating JSON.
   - Read `references/operator-scope.md` before selecting operators for a batch.
   - Read `references/generation-checklist.md` before final review.

3. Draft the problem design card.
   - Operator name and short semantics.
   - Input and output arity.
   - Supported dtypes.
   - Shape and broadcasting behavior.
   - Edge cases and invalid cases to avoid.

4. Generate files.
   - Create one folder per operator.
   - Create `problem.json` from `assets/templates/problem.json`.
   - Create `reference.py` from `assets/templates/reference.py`.
   - Keep function signatures and argument order consistent between JSON and Python.

5. Validate before claiming completion.
   - Run `scripts/validate_problem.py <problem.json>`.
   - Run `scripts/run_reference.py <problem.json> <reference.py>`.
   - Report any assumptions that remain because the real website schema is not yet available.

## Output Contract

For each operator, produce:

```text
<operator-name>/
  problem.json
  reference.py
```

The Python file must expose the function named by `reference.function` in `problem.json`.

Use NumPy only for the reference implementation unless the user explicitly authorizes another dependency. Do not use PyTorch in generated references for website execution unless the website runtime supports it.

## Batch Generation Rules

- Generate a small pilot batch first, usually 3 to 5 operators.
- Put validated problems under `generated/ready/`.
- Put failed or uncertain problems under `generated/failed/` with a short reason.
- Do not silently patch around schema uncertainty. Mark it in the report and keep the generated files conservative.

## Resource Map

- `references/problem-format.md`: draft JSON and Python format contract.
- `references/operator-scope.md`: recommended MVP operator classes and exclusions.
- `references/generation-checklist.md`: final review checklist.
- `assets/templates/problem.json`: starter JSON file.
- `assets/templates/reference.py`: starter NumPy reference file.
- `scripts/validate_problem.py`: structural JSON validator.
- `scripts/run_reference.py`: imports and executes the NumPy reference against generated inputs.
