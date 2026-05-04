# Batch Generation

Use this reference when generating more than one operator problem.

## Directory Layout

```text
generated/
  ready/
    add/
      problem.json
      reference.py
  failed/
    unsupported-op/
      problem.json
      reference.py
      failure.md
  reports/
    validation-report.json
```

For bundled examples, use:

```text
examples/
  add/
  abs/
  maximum/
  sum/
  equal/
```

## Generation Order

1. Create a design card for each operator.
2. Generate `problem.json`.
3. Generate `reference.py`.
4. Run per-problem validation.
5. Run directory validation.
6. Move only passing problems to `ready/`.

## Report Fields

Batch validation reports should include:

- problem directory
- validation status
- failed stage, if any
- error message, if any
- total passed and failed counts

## V2 Limits

- Do not generate website import packages yet.
- Do not infer the final website schema from the draft examples.
- Do not include PyTorch as a runtime dependency in generated reference files.
