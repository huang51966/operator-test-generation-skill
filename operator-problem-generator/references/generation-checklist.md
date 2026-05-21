# 生成检查清单

将生成文件标记为 ready 前，使用本清单检查。

## 格式

- 每个题目目录都包含 `statement.md`、`problem.json`、`reference.py`。
- `statement.md` 简洁描述算子背景、功能、输入输出、属性、约束、精度和测试覆盖。
- `problem.json` 是合法 JSON。
- 顶层字段包含 `op`、`cpu_cases`、`npu_cases`。
- `op.impl` 指向存在的 Python 文件和函数，通常为 `reference:impl`。
- `op.input_desc`、`op.output_desc`、`op.attr_desc` 使用真实网站字段名。
- 所有输入/输出的 `datatype` 列表长度一致。
- 每个 case 的 `input` 和 `output` 长度分别匹配 `input_desc` 和 `output_desc`。
- required attr 在每个 case 中都存在；optional attr 在 `attr_desc` 中有 `default_value`。
- 输入张量都有具体的 `datatype`、`shape`、`range`。
- 输出张量都有具体的 `datatype`、`shape`。
- 如果算子没有属性参数，`attr_desc` 写 `[]`，每个 case 的 `attr` 也写 `[]`。
- 如果算子有属性参数，`attr_desc` 必须声明所有 attr；每个 case 的 `attr` 只需写 required attr 和需要覆盖非默认值的 optional attr。

## 标准实现

- `reference.py` 导入时没有副作用。
- `op.impl` 指定的函数存在。
- 位置参数数量和顺序匹配 `input_desc`。
- `attr_desc` 中的属性名可以作为关键字参数传入。
- 返回值数量匹配 `output_desc`。
- 每个测试点返回的输出 shape 和 dtype 符合 JSON 预期。

## 题目质量

- 优先选择 NumPy 标准实现简单、确定性强的算子：
  - 一元逐元素：`abs`、`negative`、`sqrt`、`exp`、`log`、`sin`、`cos`
  - 二元逐元素：`add`、`subtract`、`multiply`、`divide`、`maximum`、`minimum`
  - 比较算子：`equal`、`not_equal`、`greater`、`less`、`greater_equal`、`less_equal`
  - 简单归约：`sum`、`mean`、`max`、`min`
  - 选择算子：`where`
- 暂缓随机、有状态、稀疏、FFT、复杂线性代数、设备特定、autograd-only 或 NumPy 不易复现的算子。
- 测试点覆盖有代表性的 shape，而不是只用 `[1]`。
- 算子支持广播时必须包含广播测试点。
- 网站支持时可加入标量形状，例如 `[]` 或 `[1]`。
- 至少包含一个非方形 shape，例如 `[2, 3]`。
- 仅在 NumPy 语义清晰时加入 dtype 变化。
- 只有在语义明确时才加入边界值。
- 浮点输出的数值范围应避免无意义 overflow。
- 标准实现优先调用 NumPy/Torch 内置函数，不要手写可被内置函数替代的逐元素循环。
- 如果仍存在 schema 或语义不确定点，需要写入最终报告。
