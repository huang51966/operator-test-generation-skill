# operator-test-generation-skill

本仓库包含 `operator-problem-generator` Codex skill，用于生成网站可导入的算子编程赛题。

当前能力：

- 网站真实 `op/cpu_cases/npu_cases` JSON 格式说明
- Markdown 题面模板
- NumPy 标准实现模板
- 单题 JSON 结构校验
- 标准实现冒烟测试
- 批量目录验证
- 已验证样例：`add`、`abs`、`maximum`、`sum`、`equal`、`tensor_sum`

## 项目结构

```text
operator-test-generation-skill/
  README.md
  operator-problem-generator/
    SKILL.md
    agents/
      openai.yaml
    assets/
      templates/
        statement.md
        problem.json
        reference.py
    references/
      problem-format.md
      generation-checklist.md
      batch-generation.md
      problem-optimization.md
    scripts/
      validate_problem.py
      run_reference.py
      validate_directory.py
    examples/
      add/
      abs/
      maximum/
      sum/
      equal/
      tensor_sum/
    generated/
      ready/
      failed/
      reports/
```

说明：

- `SKILL.md` 是 Codex 调用该 skill 时首先读取的中文工作流说明。
- `references/` 存放按需读取的详细格式、检查清单、批量生成和优化流程说明。
- `assets/templates/` 存放生成新题时复制和改写的题面、JSON、Python 模板。
- `scripts/` 存放确定性验证脚本。
- `examples/` 存放已通过验证的样例题。
- `generated/` 存放本地生成结果，默认被 `.gitignore` 忽略。
