# LLM Theory Lab

本仓库将 Transformer Circuits 研究线索组织成一套可检验的大模型理论，并提供对应实验代码。

## 从哪里开始

第一次阅读建议按以下顺序：

1. [第一性原理教程](13_FIRST_PRINCIPLES_TUTORIAL.md)
2. [统一理论综合](09_UNIFIED_SYNTHESIS.md)
3. [经典机制案例](11_CANONICAL_CASE_STUDIES.md)
4. [方法与解释矩阵](12_METHODS_AND_INTERPRETATION_MATRIX.md)
5. [理论到代码实验](14_THEORY_TO_CODE_LAB.md)
6. [全部来源逐条精华](10_SOURCE_BY_SOURCE_DIGEST.md)

## 核心框架

```text
训练分布 → 权重
输入与历史 + 固定权重 → 激活与条件路由
激活与回路 → logits
解码 → token
token 写回 → 下一步状态
```

研究目标不是为模型行为编写听起来合理的故事，而是提出能够通过对照、干预和反事实预测被检验的机制命题。

## 运行实验

```bash
pip install -e ".[dev]"
llm-theory-lab list
llm-theory-lab run-toy
pytest
```

完整安装、治理和安全说明见仓库根目录 README。
