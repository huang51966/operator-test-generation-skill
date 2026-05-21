#!/usr/bin/env python3
"""Validate the real website operator problem JSON structure."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


REQUIRED_TOP_LEVEL = {"op", "cpu_cases", "npu_cases"}
IO_TYPES = {"required", "optional", "dynamic"}
ATTR_TYPES = {"required", "optional"}
DTYPES = {
    "bool",
    "int8",
    "int16",
    "int32",
    "int64",
    "uint8",
    "uint16",
    "uint32",
    "uint64",
    "bfloat16",
    "bf16",
    "float16",
    "fp16",
    "half",
    "float32",
    "fp32",
    "float",
    "float64",
    "fp64",
    "double",
    "complex32",
    "complex64",
    "complex128",
}
ATTR_DTYPES = {
    "bool",
    "int",
    "float",
    "string",
    "list_bool",
    "list_int",
    "list_list_int",
    "list_list_float",
}


def fail(message: str) -> None:
    raise SystemExit(f"error: {message}")


def require_object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        fail(f"{label} must be an object")
    return value


def require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        fail(f"{label} must be a list")
    return value


def require_non_empty_list(value: Any, label: str) -> list[Any]:
    items = require_list(value, label)
    if not items:
        fail(f"{label} must be non-empty")
    return items


def validate_shape(value: Any, label: str) -> None:
    dims = [value] if isinstance(value, int) else value
    if not isinstance(dims, list) or not dims:
        fail(f"{label} must be an int or a non-empty list of ints")
    for index, dim in enumerate(dims):
        if not isinstance(dim, int) or dim < 0:
            fail(f"{label}[{index}] must be a non-negative integer")


def validate_tensor(value: Any, label: str, *, require_range: bool) -> None:
    tensor = require_object(value, label)
    dtype = tensor.get("datatype")
    if dtype not in DTYPES:
        fail(f"{label}.datatype must be a supported dtype")
    validate_shape(tensor.get("shape"), f"{label}.shape")
    if require_range:
        data_range = tensor.get("range")
        if not isinstance(data_range, list) or len(data_range) != 2:
            fail(f"{label}.range must be [min, max]")
        if not all(isinstance(item, (int, float)) for item in data_range):
            fail(f"{label}.range must contain numbers")


def validate_desc(desc: Any, label: str) -> dict[str, Any]:
    item = require_object(desc, label)
    name = item.get("name")
    if not isinstance(name, str) or not name:
        fail(f"{label}.name must be a non-empty string")
    kind = item.get("type")
    if kind not in IO_TYPES:
        fail(f"{label}.type must be one of {sorted(IO_TYPES)}")
    datatypes = require_non_empty_list(item.get("datatype"), f"{label}.datatype")
    for index, dtype in enumerate(datatypes):
        if dtype not in DTYPES:
            fail(f"{label}.datatype[{index}] must be a supported dtype")
    return item


def validate_attr_desc(desc: Any, label: str) -> dict[str, Any]:
    item = require_object(desc, label)
    name = item.get("name")
    if not isinstance(name, str) or not name:
        fail(f"{label}.name must be a non-empty string")
    kind = item.get("type")
    if kind not in ATTR_TYPES:
        fail(f"{label}.type must be one of {sorted(ATTR_TYPES)}")
    datatype = item.get("datatype")
    if datatype not in ATTR_DTYPES:
        fail(f"{label}.datatype must be one of {sorted(ATTR_DTYPES)}")
    if kind == "optional" and "default_value" not in item:
        fail(f"{label}.default_value is required for optional attrs")
    return item


def validate_names_unique(items: list[dict[str, Any]], label: str) -> None:
    names: set[str] = set()
    for item in items:
        name = item["name"]
        if name in names:
            fail(f"{label} contains duplicate name {name!r}")
        names.add(name)


def validate_case_io(value: Any, desc: dict[str, Any], label: str, *, is_input: bool) -> None:
    kind = desc["type"]
    if kind == "required":
        if isinstance(value, list):
            if len(value) != 1:
                fail(f"{label} required value must be one tensor or a single-item list")
            value = value[0]
        validate_tensor(value, label, require_range=is_input)
        return

    if kind == "optional":
        if value == []:
            return
        if isinstance(value, list):
            if len(value) != 1:
                fail(f"{label} optional value must be empty, one tensor, or a single-item list")
            value = value[0]
        validate_tensor(value, label, require_range=is_input)
        return

    if not isinstance(value, list):
        fail(f"{label} dynamic value must be a list")
    for index, tensor in enumerate(value):
        validate_tensor(tensor, f"{label}[{index}]", require_range=is_input)


def validate_attr_value(value: Any, datatype: str, label: str) -> None:
    if datatype == "bool" and not isinstance(value, bool):
        fail(f"{label}.value must be bool")
    if datatype == "int" and not (isinstance(value, int) and not isinstance(value, bool)):
        fail(f"{label}.value must be int")
    if datatype == "float" and not isinstance(value, (int, float)):
        fail(f"{label}.value must be float")
    if datatype == "string" and not isinstance(value, str):
        fail(f"{label}.value must be string")
    if datatype == "list_bool" and not (isinstance(value, list) and all(isinstance(item, bool) for item in value)):
        fail(f"{label}.value must be list_bool")
    if datatype == "list_int" and not (
        isinstance(value, list) and all(isinstance(item, int) and not isinstance(item, bool) for item in value)
    ):
        fail(f"{label}.value must be list_int")
    if datatype == "list_list_int" and not (
        isinstance(value, list)
        and all(
            isinstance(row, list)
            and all(isinstance(item, int) and not isinstance(item, bool) for item in row)
            for row in value
        )
    ):
        fail(f"{label}.value must be list_list_int")
    if datatype == "list_list_float" and not (
        isinstance(value, list)
        and all(isinstance(row, list) and all(isinstance(item, (int, float)) for item in row) for row in value)
    ):
        fail(f"{label}.value must be list_list_float")


def validate_case(case: Any, label: str, input_desc: list[dict[str, Any]], output_desc: list[dict[str, Any]], attr_desc: list[dict[str, Any]]) -> None:
    item = require_object(case, label)
    inputs = require_list(item.get("input"), f"{label}.input")
    outputs = require_list(item.get("output"), f"{label}.output")
    attrs = require_list(item.get("attr"), f"{label}.attr")
    if len(inputs) != len(input_desc):
        fail(f"{label}.input length must match op.input_desc")
    if len(outputs) != len(output_desc):
        fail(f"{label}.output length must match op.output_desc")
    for index, (value, desc) in enumerate(zip(inputs, input_desc)):
        validate_case_io(value, desc, f"{label}.input[{index}]", is_input=True)
    for index, (value, desc) in enumerate(zip(outputs, output_desc)):
        validate_case_io(value, desc, f"{label}.output[{index}]", is_input=False)

    attr_by_name = {desc["name"]: desc for desc in attr_desc}
    seen: set[str] = set()
    for index, attr in enumerate(attrs):
        attr_item = require_object(attr, f"{label}.attr[{index}]")
        name = attr_item.get("name")
        if name not in attr_by_name:
            fail(f"{label}.attr[{index}].name is not declared in op.attr_desc")
        if name in seen:
            fail(f"{label}.attr contains duplicate attr {name!r}")
        seen.add(name)
        if "value" not in attr_item:
            fail(f"{label}.attr[{index}].value is required")
        validate_attr_value(attr_item["value"], attr_by_name[name]["datatype"], f"{label}.attr[{index}]")
    for desc in attr_desc:
        if desc["type"] == "required" and desc["name"] not in seen:
            fail(f"{label}.attr must include required attr {desc['name']!r}")


def validate(path: Path) -> None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON: {exc}")

    root = require_object(data, "root")
    missing = REQUIRED_TOP_LEVEL - set(root)
    if missing:
        fail(f"missing top-level keys: {', '.join(sorted(missing))}")

    op = require_object(root["op"], "op")
    name = op.get("name")
    if not isinstance(name, str) or not name:
        fail("op.name must be a non-empty string")
    impl = op.get("impl")
    if not isinstance(impl, str) or ":" not in impl or not all(impl.split(":", 1)):
        fail("op.impl must be 'pyfile:function'")

    input_desc = [validate_desc(desc, f"op.input_desc[{index}]") for index, desc in enumerate(require_list(op.get("input_desc"), "op.input_desc"))]
    output_desc = [validate_desc(desc, f"op.output_desc[{index}]") for index, desc in enumerate(require_list(op.get("output_desc"), "op.output_desc"))]
    attr_desc = [validate_attr_desc(desc, f"op.attr_desc[{index}]") for index, desc in enumerate(require_list(op.get("attr_desc"), "op.attr_desc"))]
    validate_names_unique(input_desc, "op.input_desc")
    validate_names_unique(output_desc, "op.output_desc")
    validate_names_unique(attr_desc, "op.attr_desc")

    dtype_lengths = {len(desc["datatype"]) for desc in [*input_desc, *output_desc]}
    if len(dtype_lengths) > 1:
        fail("all input_desc/output_desc datatype lists must have the same length")

    for case_group in ("cpu_cases", "npu_cases"):
        cases = require_non_empty_list(root[case_group], case_group)
        for index, case in enumerate(cases):
            validate_case(case, f"{case_group}[{index}]", input_desc, output_desc, attr_desc)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate_problem.py <problem.json>", file=sys.stderr)
        return 2
    validate(Path(argv[1]))
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
