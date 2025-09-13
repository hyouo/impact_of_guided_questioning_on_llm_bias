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
    display_message("Welcome to the BiasScope LLM Analysis Framework!", "info")

    if not config.GEMINI_API_KEY:
        display_message("GEMINI_API_KEY not found. Please ensure it is set in your .env file.", "error")
        sys.exit(1)

    display_message("Environment is ready.", "info")

    user_choices = get_user_choices()
    if user_choices is None:
        display_message("User cancelled or an error occurred during setup. Exiting.", "error")
        sys.exit(1)

    try:
        engine = AnalysisEngine(
            provider=user_choices['provider'],
            metric=user_choices['metric'],
            user_choices=user_choices
        )
        engine.run_analysis()
    except Exception as e:
        display_message(f"An uncaught error occurred during analysis: {e}", "error")
        sys.exit(1)

    display_message("Analysis run has finished.", "info")


if __name__ == "__main__":
    main()
