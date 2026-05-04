#!/usr/bin/env python3
"""Import and smoke-test a draft NumPy reference implementation."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np


def fail(message: str) -> None:
    raise SystemExit(f"error: {message}")


def load_problem(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_function(path: Path, function_name: str):
    spec = importlib.util.spec_from_file_location("operator_reference", path)
    if spec is None or spec.loader is None:
        fail(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    fn = getattr(module, function_name, None)
    if not callable(fn):
        fail(f"reference function {function_name!r} not found")
    return fn


def make_input(dtype: str, shape: list[int]) -> np.ndarray:
    np_dtype = np.dtype(dtype)
    size = int(np.prod(shape, dtype=np.int64)) if shape else 1
    values = np.arange(size, dtype=np.float64).reshape(shape or [])
    if np.issubdtype(np_dtype, np.bool_):
        return (values.astype(np.int64) % 2 == 0)
    if np.issubdtype(np_dtype, np.integer):
        return values.astype(np_dtype)
    return (values / 10 + 1).astype(np_dtype)


def normalize_outputs(result: Any) -> tuple[Any, ...]:
    if isinstance(result, tuple):
        return result
    return (result,)


def run(problem_path: Path, reference_path: Path) -> None:
    problem = load_problem(problem_path)
    fn = load_function(reference_path, problem["reference"]["function"])
    output_count = len(problem["outputs"])

    for case in problem["test_cases"]:
        args = [make_input(item["dtype"], item["shape"]) for item in case["inputs"]]
        result = normalize_outputs(fn(*args))
        if len(result) != output_count:
            fail(f"{case.get('name', '<unnamed>')} returned {len(result)} outputs, expected {output_count}")
        for index, (actual, expected) in enumerate(zip(result, case["outputs"])):
            if not isinstance(actual, np.ndarray):
                fail(f"output {index} is not a numpy.ndarray")
            expected_shape = tuple(expected["shape"])
            if actual.shape != expected_shape:
                fail(f"output {index} shape {actual.shape} != {expected_shape}")
            if np.dtype(expected["dtype"]) != actual.dtype:
                fail(f"output {index} dtype {actual.dtype} != {expected['dtype']}")


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: run_reference.py <problem.json> <reference.py>", file=sys.stderr)
        return 2
    run(Path(argv[1]), Path(argv[2]))
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
