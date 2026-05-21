#!/usr/bin/env python3
"""Import and smoke-test a website-format operator reference implementation."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np


DTYPE_ALIASES = {
    "bool": "bool",
    "int8": "int8",
    "int16": "int16",
    "int32": "int32",
    "int64": "int64",
    "uint8": "uint8",
    "uint16": "uint16",
    "uint32": "uint32",
    "uint64": "uint64",
    "float16": "float16",
    "fp16": "float16",
    "half": "float16",
    "float32": "float32",
    "fp32": "float32",
    "float": "float32",
    "float64": "float64",
    "fp64": "float64",
    "double": "float64",
    "complex64": "complex64",
    "complex128": "complex128",
}


def fail(message: str) -> None:
    raise SystemExit(f"error: {message}")


def load_problem(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_dtype(dtype: str) -> np.dtype:
    if dtype in {"bfloat16", "bf16"}:
        try:
            from ml_dtypes import bfloat16  # type: ignore
        except Exception as exc:  # pragma: no cover - depends on local environment
            fail(f"{dtype} requires ml_dtypes.bfloat16: {exc}")
        return np.dtype(bfloat16)
    if dtype == "complex32":
        fail("complex32 is declared by the website format but is not supported by NumPy smoke tests")
    try:
        return np.dtype(DTYPE_ALIASES.get(dtype, dtype))
    except TypeError as exc:
        fail(f"unsupported dtype {dtype!r}: {exc}")


def normalize_shape(shape: Any) -> tuple[int, ...]:
    if isinstance(shape, int):
        return (shape,)
    if isinstance(shape, list):
        return tuple(shape)
    fail(f"invalid shape {shape!r}")


def load_function(problem_path: Path, reference_path: Path | None, impl: str):
    pyfile, function_name = impl.split(":", 1)
    path = reference_path or problem_path.with_name(f"{pyfile}.py")
    spec = importlib.util.spec_from_file_location("operator_reference", path)
    if spec is None or spec.loader is None:
        fail(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    fn = getattr(module, function_name, None)
    if not callable(fn):
        fail(f"reference function {function_name!r} not found in {path}")
    return fn


def make_tensor(spec: dict[str, Any]) -> np.ndarray:
    np_dtype = resolve_dtype(spec["datatype"])
    shape = normalize_shape(spec["shape"])
    size = int(np.prod(shape, dtype=np.int64)) if shape else 1
    low, high = spec.get("range", [0, max(size - 1, 1)])
    values = np.linspace(low, high, num=size, dtype=np.float64).reshape(shape)
    if np.issubdtype(np_dtype, np.bool_):
        return (np.arange(size).reshape(shape) % 2 == 0)
    if np.issubdtype(np_dtype, np.integer):
        return np.rint(values).astype(np_dtype)
    if np.issubdtype(np_dtype, np.complexfloating):
        return (values + values * 0.1j).astype(np_dtype)
    return values.astype(np_dtype)


def build_input(value: Any, desc: dict[str, Any]) -> Any:
    kind = desc["type"]
    if kind == "required":
        if isinstance(value, list):
            value = value[0]
        return make_tensor(value)
    if kind == "optional":
        if value == []:
            return None
        if isinstance(value, list):
            value = value[0]
        return make_tensor(value)
    return [make_tensor(item) for item in value]


def attr_kwargs(case_attrs: list[dict[str, Any]], attr_desc: list[dict[str, Any]]) -> dict[str, Any]:
    values = {desc["name"]: desc["default_value"] for desc in attr_desc if desc["type"] == "optional"}
    for item in case_attrs:
        values[item["name"]] = item["value"]
    return values


def normalize_outputs(result: Any, output_count: int) -> tuple[Any, ...]:
    if output_count == 1 and not isinstance(result, tuple):
        return (result,)
    if isinstance(result, tuple):
        return result
    fail(f"reference returned non-tuple for {output_count} outputs")


def output_shape(value: Any) -> tuple[int, ...]:
    if isinstance(value, np.ndarray):
        return value.shape
    if isinstance(value, np.generic):
        return (1,)
    return np.asarray(value).shape


def output_dtype(value: Any) -> np.dtype:
    if isinstance(value, np.ndarray):
        return value.dtype
    return np.asarray(value).dtype


def check_tensor_output(actual: Any, expected: dict[str, Any], label: str) -> None:
    expected_shape = normalize_shape(expected["shape"])
    if output_shape(actual) != expected_shape:
        fail(f"{label} shape {output_shape(actual)} != {expected_shape}")
    expected_dtype = resolve_dtype(expected["datatype"])
    if output_dtype(actual) != expected_dtype:
        fail(f"{label} dtype {output_dtype(actual)} != {expected_dtype}")


def check_output(actual: Any, expected: Any, desc: dict[str, Any], label: str) -> None:
    kind = desc["type"]
    if kind == "required":
        if isinstance(expected, list):
            expected = expected[0]
        check_tensor_output(actual, expected, label)
        return
    if kind == "optional":
        if expected == []:
            if actual is not None:
                fail(f"{label} expected None for omitted optional output")
            return
        if isinstance(expected, list):
            expected = expected[0]
        check_tensor_output(actual, expected, label)
        return
    if not isinstance(actual, list):
        fail(f"{label} dynamic output must be a list")
    if len(actual) != len(expected):
        fail(f"{label} dynamic output length {len(actual)} != {len(expected)}")
    for index, (actual_item, expected_item) in enumerate(zip(actual, expected)):
        check_tensor_output(actual_item, expected_item, f"{label}[{index}]")


def run_case(fn, case: dict[str, Any], op: dict[str, Any], case_label: str) -> None:
    input_desc = op["input_desc"]
    output_desc = op["output_desc"]
    args = [build_input(value, desc) for value, desc in zip(case["input"], input_desc)]
    kwargs = attr_kwargs(case["attr"], op["attr_desc"])
    result = normalize_outputs(fn(*args, **kwargs), len(output_desc))
    if len(result) != len(output_desc):
        fail(f"{case_label} returned {len(result)} outputs, expected {len(output_desc)}")
    for index, (actual, expected, desc) in enumerate(zip(result, case["output"], output_desc)):
        check_output(actual, expected, desc, f"{case_label}.output[{index}]")


def run(problem_path: Path, reference_path: Path | None) -> None:
    problem = load_problem(problem_path)
    op = problem["op"]
    fn = load_function(problem_path, reference_path, op["impl"])
    for group_name in ("cpu_cases", "npu_cases"):
        for index, case in enumerate(problem[group_name]):
            run_case(fn, case, op, f"{group_name}[{index}]")


def main(argv: list[str]) -> int:
    if len(argv) not in {2, 3}:
        print("usage: run_reference.py <problem.json> [reference.py]", file=sys.stderr)
        return 2
    reference_path = Path(argv[2]) if len(argv) == 3 else None
    run(Path(argv[1]), reference_path)
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
