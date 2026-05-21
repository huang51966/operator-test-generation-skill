# 题目格式说明

本文件描述网站可导入算子题的真实格式。

每个题目目录包含：

- `statement.md`：算子题面说明。
- `problem.json`：算子信息、CPU/NPU 测试点规格。
- `reference.py`：用于生成标准输出的标准实现。

## JSON 顶层结构

```json
{
  "op": {},
  "cpu_cases": [],
  "npu_cases": []
}
```

- `op`：算子原型与标准实现入口。
- `cpu_cases`：CPU 评测用例，主要用于正确性验证。建议覆盖 corner case、非对齐形状、optional/dynamic 存在与否等情况，规模不必很大。
- `npu_cases`：NPU 评测用例，用于正确性验证和性能测量。建议覆盖从小到大的规模，并包含少量 corner case。

## op

```json
{
  "name": "Add",
  "impl": "reference:impl",
  "input_desc": [],
  "output_desc": [],
  "attr_desc": []
}
```

- `name`：算子名称，建议使用大驼峰。
- `impl`：标准实现入口，格式为不带 `.py` 的 `python_file:function_name`。例如 `reference:impl` 表示 `reference.py` 中的 `impl` 函数。
- `input_desc`：输入张量描述。
- `output_desc`：输出张量描述。
- `attr_desc`：属性参数描述。

如果算子没有属性参数，`attr_desc` 写空列表 `[]`。这种情况下，每个 case 的 `attr` 也写空列表 `[]`。例如 `Add`、`Abs`、`Tril` 以外的许多纯逐元素算子都不需要属性参数。

## input_desc 与 output_desc

```json
{
  "name": "x",
  "type": "required",
  "datatype": ["half", "float"]
}
```

`type` 可选值：

- `required`：必选，恰好一个张量。
- `optional`：可选，不存在或一个张量。
- `dynamic`：动态数量，表示张量列表。

所有输入和输出的 `datatype` 列表长度必须一致。如果某个输出只有固定 dtype，而输入有多个 dtype 模式，需要重复该固定 dtype，例如 `["bool", "bool"]`。

支持的 dtype 名称：

```text
bool
int8 int16 int32 int64
uint8 uint16 uint32 uint64
bfloat16 bf16
float16 fp16 half
float32 fp32 float
float64 fp64 double
complex32 complex64 complex128
```

## attr_desc

```json
{
  "name": "axis",
  "type": "optional",
  "datatype": "int",
  "default_value": 1
}
```

`type` 可选值：

- `required`：每个 case 都必须显式提供。
- `optional`：case 可以省略，但 `attr_desc` 中必须提供 `default_value`。

支持的属性 dtype：

```text
bool
int
float
string
list_bool
list_int
list_list_int
list_list_float
```

## 测试点 case

`cpu_cases` 和 `npu_cases` 中每个元素结构如下：

```json
{
  "input": [],
  "output": [],
  "attr": []
}
```

- `input` 长度必须与 `input_desc` 一致。
- `output` 长度必须与 `output_desc` 一致。
- `attr` 顺序可以不同于 `attr_desc`。required attr 必须出现，optional attr 可以省略。
- 如果 `attr_desc` 为空，`attr` 就应为空。

张量实例格式：

```json
{
  "datatype": "float",
  "shape": [2, 3],
  "range": [-1.0, 1.0]
}
```

- `shape` 可以是整数，表示一维张量；也可以是列表，表示多维张量。
- 输入张量必须提供 `range`，用于随机生成输入数据。
- 输出张量不需要 `range`。

输入输出实例规则：

- `required`：一个张量对象，也可以写成只含一个张量的列表。
- `optional`：`[]` 或一个张量。
- `dynamic`：零个或多个张量组成的列表。

## Python 标准实现

Python 文件必须暴露 `op.impl` 指向的函数。

```python
import numpy as np


def impl(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    return np.add(x, y)
```

函数输入：

- required 输入：`np.ndarray`
- optional 输入：`np.ndarray` 或 `None`
- dynamic 输入：`list[np.ndarray]`
- attr：以关键字参数传入

函数输出：

- 单输出：可以直接返回该输出，也可以返回单元素 tuple。
- 多输出：返回 tuple。
- 输出元素可以是 `np.ndarray`、`np.number`、`list[np.ndarray]` 或 `None`。

默认使用 NumPy。只有在网站运行环境明确支持时才使用 Torch。使用 bfloat16 时，需要 `from ml_dtypes import bfloat16`。
