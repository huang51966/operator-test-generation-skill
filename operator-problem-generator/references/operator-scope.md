# Operator Scope

## MVP Operators

Start with operators whose NumPy reference is simple and deterministic:

- Unary pointwise: `abs`, `negative`, `sqrt`, `exp`, `log`, `sin`, `cos`
- Binary pointwise: `add`, `subtract`, `multiply`, `divide`, `maximum`, `minimum`
- Comparison: `equal`, `not_equal`, `greater`, `less`, `greater_equal`, `less_equal`
- Simple reductions: `sum`, `mean`, `max`, `min`
- Selection: `where`

## Early Test Coverage

For each supported operator, include a small set of cases:

- same-shape tensors
- broadcastable tensors when the operator supports broadcasting
- scalar-like shapes such as `[]` or `[1]` if the website supports them
- at least one non-square shape such as `[2, 3]`
- dtype variation only when NumPy semantics are clear

## Exclude Until The Format Is Stable

Avoid these in the first phase:

- random or stateful operators
- sparse operators
- FFT and spectral operators
- BLAS/LAPACK style linear algebra
- device-specific or memory-format-specific operators
- autograd-only behavior
- operators whose reference behavior depends on PyTorch quirks not mirrored by NumPy
