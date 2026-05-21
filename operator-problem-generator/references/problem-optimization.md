# 题目文件优化流程

当已有 Markdown、JSON、Python 三个文件，但题目范围或实现方式需要调整时，按本流程优化。

## 1. 先收敛题目语义

先明确本题到底要求参赛者实现什么，删掉暂不要求支持的模式。

常见优化：

- 将多模式支持收敛为单一核心模式，例如 ReduceSum 从多轴 `axes` 收敛为单轴 `dim`。
- 删除暂不需要的参数，例如 `ignore_nan`、`dtype`。
- 明确 dtype、shape、输出形状、误差要求和边界条件。

## 2. 区分 input 与 attr

判断每个参数是“数据输入”还是“配置参数”。

- 数据输入放入 `input_desc`，例如 `x`、`y`、`bias`。
- 控制计算模式的配置参数放入 `attr_desc`，例如 `dim`、`axis`、`keep_dims`、`diagonal`、`p`。
- 如果参数只是一个标量配置，不要为了方便生成测试点而写成 input tensor。

示例：

- `ReduceSum(x, axes)` 如果需求改成只支持单个轴，应改为 `ReduceSum(x, dim)`，其中 `dim` 是 required attr。
- `Tril(x, diagonal=0)` 中 `diagonal` 是 optional attr，不是输入张量。

## 3. 同步修改三个文件

语义调整后必须同步修改：

- `statement.md`：删掉不再支持的参数和场景，保留清晰的输入输出表、核心约束和精度要求。
- `problem.json`：更新 `input_desc`、`output_desc`、`attr_desc`、case 中的 `input/output/attr`。
- `reference.py`：更新函数签名和实现逻辑。

不要只改 Python 或只改 JSON。三者不一致会导致平台生成代码模板或标准输出时出错。

## 4. 优化 Python 标准实现

标准实现用于生成正确输出，应优先保证简洁、确定、可靠。

优先使用内置函数：

- `np.sum(x, axis=dim, keepdims=keep_dims)`
- `np.tril(x, k=diagonal)`
- `np.maximum(x, y)`
- `np.equal(x, y)`

避免手写逐元素循环，除非 NumPy/Torch 没有对应语义。手写循环更容易引入 shape、broadcast、dtype 或性能问题。

标准实现最后应保持输出 dtype 与题面一致：

```python
def impl(x, dim, keep_dims=False):
    return np.sum(x, axis=dim, keepdims=keep_dims).astype(x.dtype)
```

## 5. 重新设计测试点

修改语义后，重新检查测试点：

- CPU cases 覆盖 corner case、小规模、非对齐、不同 attr 值。
- NPU cases 覆盖小到大的性能规模。
- attr 参数至少覆盖默认值、非默认值、边界值。
- 输入 tensor 的 `range` 不要导致无意义 overflow。
- 每个 output 的 shape 必须与 attr 和输入 shape 推导一致。

## 6. 验证

优化后运行：

```bash
python scripts/validate_problem.py <problem.json>
python scripts/run_reference.py <problem.json> <reference.py>
python scripts/validate_directory.py <root>
```

若失败，优先修复失败阶段指出的问题，不要重写整题。
