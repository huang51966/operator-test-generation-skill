# Generation Checklist

Use this checklist before marking generated files as ready.

## Format

- `problem.json` is valid JSON.
- Required top-level keys exist: `schema_version`, `operator`, `reference`, `inputs`, `outputs`, `test_cases`.
- Test case input names match the prototype input names.
- Test case output names match the prototype output names.
- Dtypes use the agreed website vocabulary.

## Reference Implementation

- `reference.py` imports with no side effects.
- The function named in `problem.json` exists.
- Argument count and order match `inputs`.
- The return value count matches `outputs`.
- The returned arrays have the expected dtype and shape for each test case.

## Problem Quality

- Test cases cover representative shapes, not only `[1]`.
- Broadcasting is tested when supported.
- Edge cases are included only when semantics are clear.
- Numerical tolerance is explicit for floating-point outputs.
- Any schema or semantic uncertainty is documented in the final report.
