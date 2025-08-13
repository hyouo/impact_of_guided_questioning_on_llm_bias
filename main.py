import sys
import os
import subprocess

# --- Venv Re-execution Check ---
venv_dir = "venv"
venv_python_executable = os.path.join(os.path.abspath(venv_dir), "Scripts", "python.exe") if sys.platform == "win32" else os.path.join(os.path.abspath(venv_dir), "bin", "python")

# Check if we are already running inside the venv
if not sys.executable.startswith(os.path.abspath(venv_dir)):
    print("检测到未在虚拟环境中运行。正在设置环境并重新启动...")
    
    # Run setup.py using the current (system) python
    # This will create the venv and install dependencies into it
    try:
        subprocess.check_call([sys.executable, "setup.py"])
    except subprocess.CalledProcessError as e:
        print(f"环境设置失败: {e}")
        sys.exit(1)

    # Re-execute main.py using the venv's python
    print("环境设置完成，正在虚拟环境中重新启动程序...")
    try:
        subprocess.check_call([venv_python_executable, os.path.abspath(__file__)] + sys.argv[1:])
    except subprocess.CalledProcessError as e:
        print(f"在虚拟环境中重新启动失败: {e}")
        sys.exit(1)
    sys.exit(0) # Exit the current process, as the new one is taking over

# --- End Venv Re-execution Check ---

# Add src directory to Python path for module imports (only runs if in venv)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

# Now, safe to import modules from src and external packages
from llm_bias_research.cli import get_user_choices, display_message
from llm_bias_research.engine import AnalysisEngine
from llm_bias_research.config import config # Import config to check API key

def main():
    display_message("欢迎使用语言模型偏见研究工具！", level="info")

    # Check if API key is set after environment setup
    if not config.GEMINI_API_KEY:
        display_message("错误: GEMINI_API_KEY 未设置。请在 .env 文件中配置您的 API 密钥。", level="error")
        sys.exit(1)

    display_message("环境已准备就绪。", level="info")

    # Step 2: Get user choices (model, range, resume)
    user_choices = get_user_choices()
    if user_choices is None:
        display_message("用户选择过程被中断或发生错误，程序退出。", level="error")
        sys.exit(1)

    # Step 3: Initialize and run the analysis engine
    try:
        engine = AnalysisEngine(user_choices)
        engine.run_analysis()
    except Exception as e:
        display_message(f"程序运行过程中发生未捕获错误: {e}", level="error")
        sys.exit(1)

    display_message("分析任务完成。", level="info")


if __name__ == "__main__":
    main()
