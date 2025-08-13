import os
import sys
import google.generativeai as genai # New import
from .config import config, get_timestamped_results_dir
from .state_manager import StateManager
from .data_loader import load_prompts # To get total prompt count
from .llm_api import APIError # New import for handling API errors during model listing

def display_message(message, level="info"):
    """Displays a message to the user with a specific level."""
    if level == "info":
        print(f"\n[信息] {message}")
    elif level == "warning":
        print(f"\n[警告] {message}")
    elif level == "error":
        print(f"\n[错误] {message}")
    else:
        print(f"\n{message}")

def get_user_input(prompt, default=None):
    """Gets input from the user."""
    if default is not None:
        return input(f"{prompt} (默认: {default}): ") or default
    return input(f"{prompt}: ")

def _get_available_llm_models():
    """
    Dynamically queries the Google API for available Gemini models.
    Returns a list of (model_name, description) tuples.
    """
    display_message("正在查询可用的 LLM 模型列表，请稍候...", "info")
    try:
        # Ensure genai is configured with API key before listing models
        # This assumes config.GEMINI_API_KEY is already set and genai.configure is called in main.py
        if not config.GEMINI_API_KEY:
            raise APIError("GEMINI_API_KEY 未设置，无法查询模型列表。")
        
        # Configure genai here as well, in case this function is called directly for testing
        genai.configure(api_key=config.GEMINI_API_KEY)

        available_models = []
        for m in genai.list_models():
            # Filter for models that can generate content and are not deprecated
            if "generateContent" in m.supported_generation_methods and not m.name.endswith("deprecated"):
                available_models.append((m.name, m.description))
        
        if not available_models:
            display_message("未找到任何可用的 LLM 模型。请检查您的 API 密钥和网络连接。", "error")
            return []
        
        return available_models
    except APIError as e:
        display_message(f"查询模型列表失败: {e}", "error")
        return []
    except Exception as e:
        display_message(f"查询模型列表时发生未知错误: {e}", "error")
        return []

def select_model():
    """Prompts the user to select an LLM model from dynamically queried list."""
    available_models_list = _get_available_llm_models()
    
    if not available_models_list:
        display_message("无法获取模型列表，程序退出。", "error")
        sys.exit(1) # Exit if no models are available

    display_message("请选择一个用于分析的 LLM 模型:")
    for i, (model_name, description) in enumerate(available_models_list):
        print(f"  {i+1}. {model_name} - {description}")
    
    while True:
        choice = get_user_input("请输入模型编号")
        try:
            choice_int = int(choice)
            if 1 <= choice_int <= len(available_models_list):
                return available_models_list[choice_int - 1][0] # Return the full model name
            else:
                display_message("无效的模型编号，请重新输入。", "warning")
        except ValueError:
            display_message("请输入一个有效的数字。", "warning")

def get_analysis_range(total_prompts):
    """Prompts the user for the analysis range."""
    display_message(f"总共有 {total_prompts} 条提示词可供分析。")
    while True:
        start_str = get_user_input("请输入起始提示词编号 (从 0 开始)", default="0")
        end_str = get_user_input(f"请输入结束提示词编号 (最大 {total_prompts - 1})", default=str(total_prompts - 1))
        
        try:
            start_index = int(start_str)
            end_index = int(end_str)
            
            if not (0 <= start_index < total_prompts and 0 <= end_index < total_prompts and start_index <= end_index):
                display_message("无效的范围。请确保起始编号小于等于结束编号，且都在有效范围内。", "warning")
                continue
            return start_index, end_index
        except ValueError:
            display_message("请输入有效的数字。", "warning")

def get_user_choices():
    """
    Collects all user choices for the analysis run.
    Returns a dictionary with model, start_index, end_index, and resume_state.
    """
    choices = {}

    # 1. Select Model
    choices['model_name'] = select_model()

    # 2. Load prompts to get total count
    prompts_df = load_prompts()
    if prompts_df is None or prompts_df.empty:
        display_message("无法加载提示词数据，请检查 data/prompts.csv 文件。", "error")
        return None # Indicate critical error
    choices['prompts_df'] = prompts_df
    total_prompts = len(prompts_df)

    # 3. Check for resumable states
    resumable_states = StateManager.find_resumable_states(config.RESULTS_DIR)
    choices['resume_state'] = None
    choices['current_results_dir'] = None # Will be set if resuming or new run

    if resumable_states:
        display_message("检测到未完成的分析任务:")
        for i, (folder, state) in enumerate(resumable_states):
            print(f"  {i+1}. 文件夹: {folder}, 模型: {state.get('current_model', '未知')}, "
                  f"进度: {state.get('last_processed_index', 0)}/{state.get('total_prompts', '未知')}, "
                  f"范围: {state.get('start_index', '未知')}-{state.get('end_index', '未知')}, "
                  f"保存于: {state.get('saved_at', '未知')}")
        
        while True:
            resume_choice = get_user_input("是否要从上述任务中继续？(输入编号继续，或输入 'n' 开始新任务)", default='n')
            if resume_choice.lower() == 'n':
                break
            try:
                choice_idx = int(resume_choice) - 1
                if 0 <= choice_idx < len(resumable_states):
                    choices['resume_state'] = resumable_states[choice_idx][1]
                    choices['current_results_dir'] = os.path.join(config.RESULTS_DIR, resumable_states[choice_idx][0])
                    display_message(f"将从任务 '{resumable_states[choice_idx][0]}' 继续。")
                    break
                else:
                    display_message("无效的编号，请重新输入。", "warning")
            except ValueError:
                display_message("请输入有效的数字或 'n'。", "warning")
    
    # 4. Get analysis range (if not resuming or if resuming but range needs confirmation)
    if choices['resume_state']:
        # If resuming, use the range from the saved state
        choices['start_index'] = choices['resume_state']['last_processed_index'] + 1 # Start from next item
        choices['end_index'] = choices['resume_state']['end_index']
        display_message(f"继续分析范围: 从第 {choices['start_index']} 条到第 {choices['end_index']} 条。")
        if choices['start_index'] > choices['end_index']:
            display_message("上次任务已完成指定范围，请开始新任务或选择其他范围。", "warning")
            return None # Indicate that this resume choice is not valid for continuation
    else:
        choices['start_index'], choices['end_index'] = get_analysis_range(total_prompts)
        choices['current_results_dir'] = get_timestamped_results_dir() # New timestamped dir for new run
        display_message(f"本次分析范围: 从第 {choices['start_index']} 条到第 {choices['end_index']} 条。")
    
    return choices

def handle_api_error_prompt(error_message, state_manager_instance, last_processed_index, total_prompts, current_model, start_index, end_index):
    """
    Prompts the user after an API error, offering to save and exit or continue.
    Returns True if user chooses to continue, False otherwise.
    """
    display_message(f"API 调用发生错误: {error_message}", "error")
    while True:
        choice = get_user_input("是否要保存当前进度并退出？(y/n)", default='y')
        if choice.lower() == 'y':
            state_manager_instance.save_state(last_processed_index, total_prompts, current_model, start_index, end_index)
            return False # User wants to exit
        elif choice.lower() == 'n':
            display_message("将尝试继续分析...")
            return True # User wants to continue
        else:
            display_message("无效输入，请输入 'y' 或 'n'。", "warning")

if __name__ == "__main__":
    # This block is for testing purposes only.
    # In a real scenario, this would be called from main.py.
    
    # Create dummy data and results directories for testing
    from .config import config
    import shutil
    
    # Ensure API key is set for testing this module
    os.environ["GEMINI_API_KEY"] = "YOUR_TEST_API_KEY" # Replace with a real key for actual testing

    if not os.path.exists(config.DATA_DIR):
        os.makedirs(config.DATA_DIR)
    if not os.path.exists(config.RESULTS_DIR):
        os.makedirs(config.RESULTS_DIR)

    # Create a dummy prompts.csv for testing
    dummy_prompts_file = config.PROMPTS_FILE
    with open(dummy_prompts_file, "w", encoding="utf-8") as f:
        f.write("id,prompt\n")
        for i in range(20):
            f.write(f"{i},Test prompt {i}\n")

    print("--- CLI 模块测试 ---")
    try:
        user_choices = get_user_choices()
        if user_choices:
            print("\n用户选择汇总:")
            print(f"模型: {user_choices.get('model_name')}")
            print(f"起始索引: {user_choices.get('start_index')}")
            print(f"结束索引: {user_choices.get('end_index')}")
            if user_choices.get('resume_state'):
                print(f"恢复状态: {user_choices['resume_state']['timestamp']}")
            print(f"结果目录: {user_choices.get('current_results_dir')}")
        else:
            print("用户选择过程被中断或发生错误。")

        # Test handle_api_error_prompt
        print("\n--- 测试 API 错误处理提示 ---")
        # Create a dummy state manager for this test
        dummy_results_dir = os.path.join(config.RESULTS_DIR, "test_error_dir")
        os.makedirs(dummy_results_dir, exist_ok=True)
        dummy_sm = StateManager(dummy_results_dir)
        
        should_continue = handle_api_error_prompt(
            "连接超时", dummy_sm, 5, 10, "gemini-pro", 0, 9
        )
        print(f"用户选择继续: {should_continue}")

    finally:
        # Clean up dummy files and directories
        if os.path.exists(dummy_prompts_file):
            os.remove(dummy_prompts_file)
        if os.path.exists(config.DATA_DIR):
            os.rmdir(config.DATA_DIR) # Only if empty
        if os.path.exists(config.RESULTS_DIR):
            # Need to remove contents first if not empty
            for entry in os.listdir(config.RESULTS_DIR):
                full_path = os.path.join(config.RESULTS_DIR, entry)
                if os.path.isdir(full_path):
                    shutil.rmtree(full_path)
                else:
                    os.remove(full_path)
            os.rmdir(config.RESULTS_DIR)
        print("\n清理测试环境完成。")