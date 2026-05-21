## 一、赛题背景

Sum 是常见归约算子，用于沿指定维度对张量求和，广泛用于特征聚合、损失计算和统计计算。

## 二、算子功能描述

沿属性 `axis` 指定的维度对输入张量 `x` 求和：

```text
out = sum(x, axis=axis, keepdims=keepdims)
```

`keepdims` 控制是否保留被归约维度。

## 三、输入输出与属性

| 类型 | 参数名 | 数据类型 / 类型 | 形状 | 说明 |
|------|--------|----------------|------|------|
| INPUT | x | float | rank >= 2 | 输入张量 |
| ATTR | axis | int | 标量 | 归约维度 |
| ATTR | keepdims | bool | 标量，默认 false | 是否保留归约维度 |
| OUTPUT | out | float | 由 axis 和 keepdims 决定 | 求和结果 |

## 四、核心约束

- `axis` 是 required attr。
- `keepdims` 是 optional attr，默认值为 `false`。
- `axis` 必须在输入 rank 范围内。
- 输出 dtype 与输入 dtype 一致。

## 五、精度要求

float：相对误差和绝对误差按平台 float32 标准检查。

## 六、测试覆盖

- CPU cases 覆盖二维归约和三维 keepdims 场景。
- NPU cases 覆盖较大规模二维归约。
