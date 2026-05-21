## 一、赛题背景

TensorSum 是用于展示复杂题目格式的示例算子，覆盖 dynamic 输入、optional 输入/输出和属性参数。它适合作为创建复杂算子题时的参考样例。

## 二、算子功能描述

输入一个张量列表 `x_list`、一个初始张量 `initial` 和一个可选偏置张量 `bias`，计算：

```text
out = initial + sum(x for x in x_list) + bias(if exists)
```

当 `need_norm=True` 时，额外输出 `x_list` 中所有张量 p 范数之和 `norm`；否则 `norm` 不存在。

## 三、输入输出与属性

| 类型 | 参数名 | 数据类型 / 类型 | 形状 | 说明 |
|------|--------|----------------|------|------|
| INPUT | x_list | half, float / dynamic | 张量列表，各元素同形状 | 待累加张量列表 |
| INPUT | initial | half, float / required | 与 x_list 元素一致 | 初始值张量 |
| INPUT | bias | half, float / optional | 与 x_list 元素一致 | 可选偏置张量 |
| ATTR | p | int / required | 标量 | p 范数阶数 |
| ATTR | need_norm | bool / optional | 标量，默认 false | 是否输出 norm |
| OUTPUT | out | half, float / required | 与输入张量一致 | 累加结果 |
| OUTPUT | norm | float / optional | shape 为 1 | p 范数和 |

## 四、核心约束

- `x_list` 是 dynamic 输入，可以包含多个张量。
- `bias` 是 optional 输入，缺失时不参与累加。
- `norm` 是 optional 输出，仅当 `need_norm=True` 时存在。
- 所有参与累加的张量 shape 和 dtype 应一致。

## 五、精度要求

- float：相对误差和绝对误差按平台 float32 标准检查。
- half：相对误差和绝对误差按平台 float16 标准检查。

## 六、测试覆盖

- CPU cases 覆盖无 bias/无 norm 和有 bias/有 norm 两种模式。
- NPU cases 覆盖多个 float 张量累加的中等规模场景。
