# 批量生成

生成多个算子题时使用本参考。

## 目录布局

```text
generated/
  ready/
    add/
      problem.json
      reference.py
  failed/
    unsupported-op/
      problem.json
      reference.py
      failure.md
  reports/
    validation-report.json
```

内置样例目录：

```text
examples/
  add/
  abs/
  maximum/
  sum/
  equal/
  tensor_sum/
```

## 生成顺序

1. 为每个算子创建设计卡。
2. 生成 `problem.json`。
3. 生成 `reference.py`。
4. 运行单题验证。
5. 运行目录级验证。
6. 仅将通过验证的题目放入 `ready/`。

## 报告字段

批量验证报告应包含：

- 题目目录
- 验证状态
- 失败阶段，如果存在
- 错误信息，如果存在
- 通过和失败数量统计

## 当前限制

- 暂不生成网站导入压缩包。
- 使用真实 `op/cpu_cases/npu_cases` 网站 schema。
- 默认不在生成的标准实现中引入 PyTorch 运行时依赖。
