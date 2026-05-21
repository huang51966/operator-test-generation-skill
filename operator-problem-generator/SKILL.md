---
name: operator-problem-generator
description: 生成网站可导入的算子编程赛题。使用场景包括：根据算子说明、PyTorch/NumPy 文档或人工给定规格，创建或审查一组算子题文件；每道题包含一个 JSON 元数据文件，描述 op、输入输出、属性参数、CPU/NPU 测试点、dtype、shape 和随机输入范围，以及一个 Python/NumPy 标准实现文件。也适用于批量生成 benchmark、竞赛网站或训练数据集中的算子题。
---

# 算子赛题生成器

## 概览

使用本 skill 生成网站可导入的算子题资产。每道题默认包含：

- `statement.md`：面向参赛者的算子题面说明。
- `problem.json`：算子原型、CPU/NPU 测试点、输入输出规格和属性参数。
- `reference.py`：用于生成标准输出的 Python/NumPy 标准实现。

当前版本使用 `ref/题目创建` 中确认过的真实网站格式：JSON 顶层为 `op`、`cpu_cases`、`npu_cases`，并通过 `op.impl` 指向 `python_file:function_name`。

## 当前能力

已验证的内置样例覆盖：

- `add`：二元逐元素算子，包含广播。
- `abs`：一元逐元素算子。
- `maximum`：二元逐元素算子，包含广播。
- `sum`：固定轴归约，包含 required/optional 属性参数。
- `equal`：比较算子，输出 bool。
- `tensor_sum`：复杂样例，覆盖 dynamic 输入、optional 输入/输出、required attr 和 optional attr。

## 工作流

1. 明确算子范围。
   - 读取用户请求、算子说明或框架文档。
   - 优先选择 pointwise、comparison、简单 reduction 等 NumPy 语义清晰的算子。
   - 暂缓随机、状态相关、稀疏、FFT、复杂线性代数、设备特定行为或数值容差不明确的算子。

2. 按需读取参考资料。
   - 生成 JSON 前读取 `references/problem-format.md`。
   - 选算子和交付前读取 `references/generation-checklist.md`。
   - 批量生成时读取 `references/batch-generation.md`。

3. 先写算子设计卡。
   - 算子名称和语义。
   - 输入、输出、属性参数。
   - 支持 dtype。
   - shape 与 broadcasting 规则。
   - CPU cases 和 NPU cases 的覆盖策略。
   - 明确哪些是张量输入，哪些只是控制计算模式的 attr。像 `dim`、`axis`、`keep_dims`、`diagonal` 这类配置型参数应放在 `attr_desc`，不要作为 input tensor，除非平台题目明确要求它以张量输入出现。

4. 生成题目文件。
   - 每个算子一个目录。
   - 从 `assets/templates/statement.md` 生成 `statement.md`。
   - 从 `assets/templates/problem.json` 生成 `problem.json`。
   - 从 `assets/templates/reference.py` 生成 `reference.py`。
   - 默认设置 `op.impl` 为 `reference:impl`。
   - Python 函数签名必须与 `input_desc` 加 `attr_desc` 对齐。
   - 优先模仿 `examples/` 中最接近的样例。

5. 优化题目文件。
   - 如果输入里存在配置型参数，优先改为 attr，并同步修改题面、JSON 和 Python。
   - 删除题目暂不要求支持的参数，避免把范围做大，例如从多轴 `axes` 收敛为单轴 `dim`。
   - Python 标准实现优先使用 NumPy/Torch 内置函数，例如 `np.sum`、`np.tril`，避免手写逐元素循环。
   - 修改后重新检查输出 shape、dtype、optional/default attr 和测试点覆盖。

6. 验证后再交付。
   - 单题 JSON：`python scripts/validate_problem.py <problem.json>`
   - 单题 reference：`python scripts/run_reference.py <problem.json> <reference.py>`
   - 目录批量验证：`python scripts/validate_directory.py <root>`
   - 如果仍有网站导入格式不确定点，在最终报告中明确写出。

## 输出约定

单个算子题目录：

```text
<operator-name>/
  statement.md
  problem.json
  reference.py
```

生成产物默认放在：

```text
generated/
  ready/
  failed/
  reports/
```

`generated/` 默认被 `.gitignore` 忽略。若需要把生成题目纳入仓库，需要显式调整位置或跟踪规则。

## 批量生成规则

- 先生成 3 到 5 个小批量题目试跑。
- 通过验证的题目放入 `generated/ready/`。
- 失败或不确定的题目放入 `generated/failed/`，并附失败原因。
- 批量验证时输出机器可读报告。
- 不要静默修补 schema 不确定点；要把假设写入报告。

## 资源索引

- `references/problem-format.md`：网站真实 JSON 与 Python 格式。
- `references/generation-checklist.md`：推荐算子范围、暂缓范围和生成后的检查清单。
- `references/batch-generation.md`：批量生成目录与报告约定。
- `references/problem-optimization.md`：根据反馈优化 Markdown、JSON、Python 三件套的流程。
- `assets/templates/statement.md`：题面 Markdown 模板。
- `assets/templates/problem.json`：题目 JSON 模板。
- `assets/templates/reference.py`：标准实现模板。
- `scripts/validate_problem.py`：单个 `problem.json` 结构校验。
- `scripts/run_reference.py`：导入并执行标准实现，检查输出 shape/dtype。
- `scripts/validate_directory.py`：批量验证目录下所有题目。
- `examples/`：已验证的网站真实格式样例。
