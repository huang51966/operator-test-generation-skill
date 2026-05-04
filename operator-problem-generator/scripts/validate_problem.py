#!/usr/bin/env python3
"""Validate the draft operator problem JSON structure."""

from __future__ import annotations

import json
import sys
from pathlib import Path


REQUIRED_TOP_LEVEL = {
    "schema_version",
    "operator",
    "reference",
    "inputs",
    "outputs",
    "test_cases",
}

ALLOWED_DTYPES = {
    "bool",
    "int8",
    "int16",
    "int32",
    "int64",
    "uint8",
    "uint16",
    "uint32",
    "uint64",
    "float16",
    "float32",
    "float64",
}


def fail(message: str) -> None:
    raise SystemExit(f"error: {message}")


def require_object(value: object, label: str) -> dict:
    if not isinstance(value, dict):
        fail(f"{label} must be an object")
    return value


def require_list(value: object, label: str) -> list:
    if not isinstance(value, list) or not value:
        fail(f"{label} must be a non-empty list")
    return value


def require_name_set(items: list, label: str) -> set[str]:
    names: set[str] = set()
    for index, item in enumerate(items):
        obj = require_object(item, f"{label}[{index}]")
        name = obj.get("name")
        if not isinstance(name, str) or not name:
            fail(f"{label}[{index}].name must be a non-empty string")
        if name in names:
            fail(f"{label} contains duplicate name {name!r}")
        names.add(name)
    return names


def validate_shape(value: object, label: str) -> None:
    if not isinstance(value, list):
        fail(f"{label} must be a list")
    for index, dim in enumerate(value):
        if not isinstance(dim, int) or dim < 0:
            fail(f"{label}[{index}] must be a non-negative integer")


def validate_concrete_tensor(item: dict, label: str) -> None:
    dtype = item.get("dtype")
    if not isinstance(dtype, str) or dtype not in ALLOWED_DTYPES:
        fail(f"{label}.dtype must be one of: {', '.join(sorted(ALLOWED_DTYPES))}")
    validate_shape(item.get("shape"), f"{label}.shape")


def validate_prototype_tensor(item: dict, label: str) -> None:
    kind = item.get("kind")
    if kind != "tensor":
        fail(f"{label}.kind must be 'tensor'")
    dtype = item.get("dtype")
    if not isinstance(dtype, list) or not dtype:
        fail(f"{label}.dtype must be a non-empty list")
    for index, value in enumerate(dtype):
        if not isinstance(value, str) or value not in ALLOWED_DTYPES:
            fail(f"{label}.dtype[{index}] must be one of: {', '.join(sorted(ALLOWED_DTYPES))}")
    shape = item.get("shape")
    if not isinstance(shape, list) or not shape:
        fail(f"{label}.shape must be a non-empty list")


def validate(path: Path) -> None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON: {exc}")

    root = require_object(data, "root")
    missing = REQUIRED_TOP_LEVEL - set(root)
    if missing:
        fail(f"missing top-level keys: {', '.join(sorted(missing))}")

    operator = require_object(root["operator"], "operator")
    if not isinstance(operator.get("name"), str) or not operator["name"]:
        fail("operator.name must be a non-empty string")

    reference = require_object(root["reference"], "reference")
    if not isinstance(reference.get("file"), str) or not reference["file"]:
        fail("reference.file must be a non-empty string")
    if not isinstance(reference.get("function"), str) or not reference["function"]:
        fail("reference.function must be a non-empty string")

    inputs = require_list(root["inputs"], "inputs")
    outputs = require_list(root["outputs"], "outputs")
    input_names = require_name_set(inputs, "inputs")
    output_names = require_name_set(outputs, "outputs")
    for index, item in enumerate(inputs):
        validate_prototype_tensor(item, f"inputs[{index}]")
    for index, item in enumerate(outputs):
        validate_prototype_tensor(item, f"outputs[{index}]")

    test_cases = require_list(root["test_cases"], "test_cases")
    for case_index, case in enumerate(test_cases):
        case_obj = require_object(case, f"test_cases[{case_index}]")
        case_inputs = require_list(case_obj.get("inputs"), f"test_cases[{case_index}].inputs")
        case_outputs = require_list(case_obj.get("outputs"), f"test_cases[{case_index}].outputs")
        case_input_names = require_name_set(case_inputs, f"test_cases[{case_index}].inputs")
        case_output_names = require_name_set(case_outputs, f"test_cases[{case_index}].outputs")
        if case_input_names != input_names:
            fail(f"test_cases[{case_index}] input names do not match prototype inputs")
        if case_output_names != output_names:
            fail(f"test_cases[{case_index}] output names do not match prototype outputs")
        for input_index, item in enumerate(case_inputs):
            validate_concrete_tensor(item, f"test_cases[{case_index}].inputs[{input_index}]")
        for output_index, item in enumerate(case_outputs):
            validate_concrete_tensor(item, f"test_cases[{case_index}].outputs[{output_index}]")


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate_problem.py <problem.json>", file=sys.stderr)
        return 2
    validate(Path(argv[1]))
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
