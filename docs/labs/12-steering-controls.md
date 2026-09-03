# C12｜Steering 的剂量、反向与随机方向对照

## 问题

沿某个方向注入激活后行为改变，怎样判断它不是“任意大扰动都能改变输出”？

## 先做预测

目标 readout 方向为 $v$。比较：

- $-v,-0.5v,0,0.5v,v$ 的剂量响应；
- 等范数随机方向的效应分布；
- 与 $v$ 正交的方向；
- 反向干预是否产生反号效应。

## 运行

```bash
llm-theory-lab explain C12
llm-theory-lab run-toy --ids C12 --output-dir reports/c12
python examples/08_steering_controls.py
```

## 要检查的量

- `target_scores` 是否随剂量单调；
- 正向与反向效应的符号；
- `random_abs_q99`；
- 目标效应是否超过随机方向 99% 分位；
- `orthogonal_effect` 是否接近零。

## 改动实验

打开 `steering_controls.py`：

- 改变维度，观察随机方向投影分布；
- 让目标方向与 readout 只部分对齐；
- 加入非线性饱和，使剂量响应不再线性；
- 增加错误层/位置的抽象对照；
- 测量目标行为以外的副作用。

## 结论边界

**支持：** 相比等范数随机/正交方向，目标方向具有更强且符号一致的可操纵性。  
**不支持：** 该方向是唯一自然表征、模型自然运行依赖它，或 steering 在所有提示上都安全稳定。
