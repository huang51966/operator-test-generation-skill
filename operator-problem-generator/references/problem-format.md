# Problem Format

This is a draft contract for the first implementation phase. Replace or tighten it after collecting real website examples.

## Required Files

Each problem directory contains:

- `problem.json`: metadata, operator prototype, and test case descriptions.
- `reference.py`: NumPy implementation of the expected result.

## Draft JSON Shape

```json
{
  "schema_version": "0.1-draft",
  "operator": {
    "name": "add",
    "summary": "Elementwise addition with NumPy broadcasting.",
    "category": "pointwise"
  },
  "reference": {
    "file": "reference.py",
    "function": "reference"
  },
  "inputs": [
    {"name": "x", "kind": "tensor", "dtype": ["float32"], "shape": ["*"]},
    {"name": "y", "kind": "tensor", "dtype": ["float32"], "shape": ["*"]}
  ],
  "outputs": [
    {"name": "out", "kind": "tensor", "dtype": ["float32"], "shape": ["broadcast(x, y)"]}
  ],
  "test_cases": [
    {
      "name": "same_shape_float32",
      "inputs": [
        {"name": "x", "dtype": "float32", "shape": [2, 3]},
        {"name": "y", "dtype": "float32", "shape": [2, 3]}
      ],
      "outputs": [
        {"name": "out", "dtype": "float32", "shape": [2, 3]}
      ]
    }
  ],
  "tolerance": {
    "rtol": 1e-05,
    "atol": 1e-08
  }
}
```

## Python Reference Contract

`reference.py` must define the function named by `reference.function`.

```python
import numpy as np


def reference(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    return np.add(x, y)
```

For multiple outputs, return a tuple of NumPy arrays in the same order as `outputs`.

## Open Items To Freeze With Real Examples

- Exact website field names.
- Whether scalar attributes are supported and how they are represented.
- Whether dynamic shapes or shape expressions are allowed.
- Whether tests store literal input values or only dtype and shape.
- Allowed dtype vocabulary.
- Tolerance policy for integer, boolean, float, and complex outputs.
