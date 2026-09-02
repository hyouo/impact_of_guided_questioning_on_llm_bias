# 贡献指南

感谢你改进本仓库。项目同时包含理论整理、来源目录和可运行实验；贡献必须让“主张—证据—代码—结论边界”保持一致。

## 开发环境

```bash
git clone https://github.com/hyouo/impact_of_guided_questioning_on_llm_bias.git
cd impact_of_guided_questioning_on_llm_bias

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -e ".[dev,docs]"
pre-commit install
```

常用命令：

```bash
make format       # 自动格式化
make lint         # 静态检查
make test         # 单元测试
make docs         # 严格构建文档
make check        # 完整本地质量检查
```

## 分支与提交

建议从最新 `main` 创建短生命周期分支：

```text
docs/<topic>
feat/<experiment>
fix/<bug>
refactor/<area>
chore/<maintenance>
```

提交信息建议遵循 Conventional Commits 风格，例如：

```text
docs: clarify QK and OV distinction
feat: add negative control to activation patching
fix: preserve temperature metadata in reports
chore: update dependency constraints
```

## 理论贡献

理论修改至少说明：

```text
Claim：精确主张
Object：参数、激活、特征、头、路径、logit、token 或行为
Scope：适用模型、任务、输入与运行条件
Evidence：来源和证据等级
Alternatives：至少一个替代解释
Falsifier：什么结果会削弱该主张
Forbidden inference：不能据此推出什么
```

请区分原始论文结论、作者解释、仓库综合与个人假设。月度研究更新、玩具模型和正式研究论文不能等权引用。

## 实验贡献

新实验至少包含：

```text
Intervention：改变什么
Invariants：保持什么不变
Positive control：应当出现效应的条件
Negative control：不应出现效应的条件
Metric：看结果前定义的指标
Seeds / samples：随机性和样本规模
Failure cases：保留失败与不确定结果
Conclusion boundary：实验最多支持什么
```

要求：

- 类型提示和清晰错误信息；
- 不依赖未记录的本地状态；
- 固定或保存随机种子；
- 保存模型 revision、tokenizer、模板、依赖和设备信息；
- 为错误输入、正常路径和关键边界添加测试；
- 不把 `pass` 写成“理论已经在所有模型上成立”。

## 文档与来源

修改来源目录后必须运行：

```bash
python scripts/validate_catalog.py
python scripts/validate_source_digest.py
python scripts/check_markdown_links.py
```

数学公式使用 GitHub 支持的 `$...$` 与 `$$...$$`。不要复制大段受版权保护的原文；使用准确转述，并链接原始来源。

## 安全边界

允许：无害代理、拒绝/权限路由分析、检测、审计、缓解和防御性实验。

不接受：真实危险操作步骤、可直接复用的越狱载荷、秘密提取、凭据、自动攻击优化或绕过生产系统的代码。

## Pull Request 检查表

提交 PR 前确认：

- [ ] `make check` 通过；
- [ ] 新行为有测试；
- [ ] 文档与代码路径一致；
- [ ] 新主张有来源、范围和反证条件；
- [ ] 失败案例和限制没有被删除；
- [ ] `CHANGELOG.md` 已在需要时更新；
- [ ] 不包含秘密、模型权重、缓存或大型生成文件。

维护流程和发布规则见 [`GOVERNANCE.md`](GOVERNANCE.md) 与
[`docs/RELEASING.md`](docs/RELEASING.md)。
