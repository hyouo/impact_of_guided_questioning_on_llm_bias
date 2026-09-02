# Support｜使用支持

请根据问题类型选择入口：

- **安装、CLI、测试或报告 bug**：使用 Bug Report Issue 表单。
- **理论表述、来源或证据边界问题**：使用 Theory / Evidence Issue 表单。
- **新实验建议**：使用 Experiment Proposal Issue 表单。
- **安全漏洞**：遵循 [`SECURITY.md`](SECURITY.md)，不要公开提交。
- **一般讨论**：可以创建普通 Issue，并提供具体上下文。

提问前请先运行：

```bash
python --version
pip show llm-theory-lab
llm-theory-lab list
make check
```

Bug 报告请附：

```text
操作系统和 Python 版本
安装命令
完整命令
最小复现输入
完整错误信息
预期行为与实际行为
是否安装 models 可选依赖
```

本项目是研究工具，不提供生产服务 SLA，也不保证所有模型架构都能由开放模型实验适配。
