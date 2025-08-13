# 语言模型偏见研究：引导式提问的影响

本项目旨在通过实验方法，系统性地研究引导式提问对大型语言模型（LLM）在生成文本时所表现出的偏见（Bias）的影响。
## 核心功能

    自动化环境设置: 首次运行时，脚本会自动检测、创建 Python 虚拟环境并安装所有必需的依赖项。
    交互式控制: 程序启动后会引导用户进行选择，包括要使用的 LLM 模型、要分析的数据范围等。
    断点续传: 在 API 请求失败或用户主动中断后，程序会保存当前进度。下次运行时可选择从上次中断的地方继续，避免重复工作和资源浪费。
    错误处理: API 请求会自动重试 3 次。若持续失败，程序会询问用户是否要保存当前进度并退出。

## 如何运行

与传统脚本不同，本项目提供了一键启动的体验。

### 1. 克隆仓库

```bash
git clone <repository_url>
cd project-directory
```

### 2. 配置 API 密钥

本项目需要 Google Gemini API 密钥。

1.  复制 `.env.example` 文件并重命名为 `.env`。
    ```bash
    # Windows
    copy .env.example .env
    # macOS/Linux
    cp .env.example .env
    ```
2.  打开 `.env` 文件，填入您的 API 密钥：
    ```
    GEMINI_API_KEY="YOUR_API_KEY_HERE"
    ```

### 3. 运行主程序

只需执行 `main.py`，程序将引导您完成所有后续步骤。

```bash
python main.py
```

---

## 详细工作流程

运行 `python main.py` 后，您将经历以下步骤：

1.  **环境检查**:
    脚本首先调用 `setup.py` 检查是否存在 `venv` 虚拟环境。
    如果不存在，它会自动创建虚拟环境，并使用 `pip` 安装 `requirements.txt` 中列出的所有依赖。

2.  **模型选择**:
    程序会列出可用的 Google AI 模型（例如 `gemini-1.5-pro`, `gemini-1.0-pro` 等）。
    您将被要求输入数字来选择本次分析要使用的模型。

3.  **数据加载与预览**:
    程序会加载 `data/prompts.csv` 文件。
    它会显示文件的基本信息，如总行数。

4.  **断点续传检查**:
    程序会扫描 `results/` 目录，寻找之前未完成的分析（通过检查 `analysis_state.json` 文件）。
    如果找到，它会询问您是否要从上次的进度继续。

5.  **范围选择**:
    您将被要求指定要分析的数据范围（例如，从第 50 行到第 100 行）。这对于分批次进行大型实验非常有用。

6.  **开始分析**:
    确认后，程序会以当前时间创建一个新的结果文件夹 `results/YYYYMMDD_HHMMSS/`。
    分析开始，屏幕上会显示进度条，并显示当前处理的条目数和总条目数。

7.  **错误与中断处理**:
    如果在与 API 交互时发生错误，程序会静默重试最多 3 次。
    如果依然失败，程序会暂停，并询问您：“API 请求失败，是否要保存当前进度并退出？(y/n)”。
    如果您选择 `y`，`engine.py` 会调用 `state_manager.py` 将已完成的部分写入 `analysis_state.json`，然后安全退出。

8.  **完成与分析**:
    任务完成后，所有原始回复和偏见分数会保存在本次创建的结果文件夹中。
    您可以像以前一样，使用 `notebooks/analysis_and_visualization.ipynb` 进行后续的数据分析。

## 项目结构

```
/
├── main.py              # 唯一的项目入口点
├── setup.py             # 自动化环境安装脚本
├── requirements.txt
├── README.md            # 本文档
├── .env.example
├── .env
│
├── data/
│   └── prompts.csv
│
├── results/
│   └── YYYYMMDD_HHMMSS/
│       ├── analysis_state.json # 断点续传状态文件
│       ├── ...
│
└── src/
    └── llm_bias_research/
        ├── cli.py         # 用户交互模块
        ├── config.py      # 配置模块
        ├── data_loader.py # 数据加载模块
        ├── engine.py      # 核心分析引擎
        ├── llm_api.py     # API 交互与错误处理模块
        └── state_manager.py # 分析状态读写模块
```

## 许可证

本项目采用 MIT 许可证。详情请参阅 `LICENSE` 文件。

## 开发者

yu hong
