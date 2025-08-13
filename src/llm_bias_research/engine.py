import os
import pandas as pd
from tqdm import tqdm
import time # For simulating work
import shutil # For creating/removing directories

from .config import config, get_timestamped_results_dir
from .data_loader import load_prompts
from .llm_api import LLMAPI, APIError
from .state_manager import StateManager
from .cli import display_message, handle_api_error_prompt # Import CLI functions for interaction

class AnalysisEngine:
    def __init__(self, user_choices):
        self.model_name = user_choices['model_name']
        self.prompts_df = user_choices['prompts_df']
        self.start_index = user_choices['start_index']
        self.end_index = user_choices['end_index']
        self.resume_state = user_choices['resume_state']
        self.current_results_dir = user_choices['current_results_dir']

        self.llm_api = LLMAPI(self.model_name)
        self.state_manager = StateManager(self.current_results_dir)

        self.raw_responses_dir = os.path.join(self.current_results_dir, "raw_responses")
        os.makedirs(self.raw_responses_dir, exist_ok=True)

        self.bias_scores_file = os.path.join(self.current_results_dir, "bias_scores.csv")
        self.bias_results = [] # To store results before saving to CSV

        display_message(f"分析引擎初始化完成。结果将保存到: {self.current_results_dir}")

    def _load_existing_results(self):
        """Loads existing bias scores if resuming, to append new results."""
        if self.resume_state and os.path.exists(self.bias_scores_file):
            try:
                existing_df = pd.read_csv(self.bias_scores_file)
                self.bias_results = existing_df.to_dict(orient='records')
                display_message(f"已加载 {len(self.bias_results)} 条现有结果进行续传。")
            except Exception as e:
                display_message(f"加载现有结果失败，将从头开始收集: {e}", "warning")
                self.bias_results = []
        else:
            self.bias_results = []

    def _save_bias_scores(self):
        """Saves the collected bias scores to a CSV file."""
        if not self.bias_results:
            display_message("没有偏见分数可保存。", "warning")
            return

        df = pd.DataFrame(self.bias_results)
        try:
            df.to_csv(self.bias_scores_file, index=False, encoding="utf-8")
            display_message(f"偏见分数已保存到: {self.bias_scores_file}")
        except Exception as e:
            display_message(f"保存偏见分数失败: {e}", "error")

    def run_analysis(self):
        """Executes the main analysis loop."""
        total_prompts_to_process = self.end_index - self.start_index + 1
        
        # Load existing results if resuming
        self._load_existing_results()

        # Determine the actual starting point for the loop
        current_loop_start_index = self.start_index
        if self.resume_state:
            # If resuming, the loop should start from the next item after last_processed_index
            current_loop_start_index = self.resume_state['last_processed_index'] + 1
            if current_loop_start_index > self.end_index:
                display_message("指定范围内的所有任务已完成，无需继续。", "info")
                return

        display_message(f"开始分析提示词 (范围: {current_loop_start_index} 到 {self.end_index})")

        # Use tqdm for progress bar
        with tqdm(total=total_prompts_to_process, initial=current_loop_start_index - self.start_index, 
                  desc=f"分析进度 ({self.model_name})", 
                  unit="条") as pbar:
            
            for i in range(current_loop_start_index, self.end_index + 1):
                prompt_data = self.prompts_df.iloc[i]
                prompt_id = prompt_data['id']
                prompt_text = prompt_data['prompt_text']

                raw_response_file = os.path.join(self.raw_responses_dir, f"response_{prompt_id}.txt")

                try:
                    # Phase 1: Get LLM Response
                    response_text = self.llm_api.get_response(prompt_text)
                    with open(raw_response_file, "w", encoding="utf-8") as f:
                        f.write(response_text)
                    
                    # Phase 2: Evaluate Bias
                    bias_evaluation = self.llm_api.evaluate_bias(response_text)
                    
                    self.bias_results.append({
                        "prompt_id": prompt_id,
                        "prompt_text": prompt_text,
                        "model_name": self.model_name,
                        "response_text_path": os.path.basename(raw_response_file), # Store filename
                        "bias_score": bias_evaluation['score'],
                        "bias_reason": bias_evaluation['reason'],
                        "raw_bias_evaluation": bias_evaluation['raw_evaluation']
                    })
                    
                    # Update state after each successful prompt
                    self.state_manager.save_state(
                        last_processed_index=i, 
                        total_prompts=len(self.prompts_df), 
                        current_model=self.model_name,
                        start_index=self.start_index,
                        end_index=self.end_index
                    )
                    
                    pbar.update(1) # Update progress bar
                    pbar.set_postfix_str(f"处理中: {i+1}/{self.end_index+1}") # Update current/total display

                except APIError as e:
                    display_message(f"处理提示词 {prompt_id} 时 API 错误: {e}", "error")
                    # Ask user if they want to continue or save and exit
                    should_continue = handle_api_error_prompt(
                        str(e), 
                        self.state_manager, 
                        last_processed_index=i, 
                        total_prompts=len(self.prompts_df), 
                        current_model=self.model_name,
                        start_index=self.start_index,
                        end_index=self.end_index
                    )
                    if not should_continue:
                        display_message("用户选择退出。分析已中断。", "info")
                        self._save_bias_scores() # Save results collected so far
                        return # Exit analysis loop
                except Exception as e:
                    display_message(f"处理提示词 {prompt_id} 时发生未知错误: {e}", "error")
                    # For other errors, also ask user
                    should_continue = handle_api_error_prompt(
                        str(e), 
                        self.state_manager, 
                        last_processed_index=i, 
                        total_prompts=len(self.prompts_df), 
                        current_model=self.model_name,
                        start_index=self.start_index,
                        end_index=self.end_index
                    )
                    if not should_continue:
                        display_message("用户选择退出。分析已中断。", "info")
                        self._save_bias_scores() # Save results collected so far
                        return # Exit analysis loop

        display_message("所有指定范围内的提示词分析完成。", "info")
        self._save_bias_scores() # Save final results

if __name__ == "__main__":
    # This block is for testing purposes only.
    # In a real scenario, this would be called from main.py.
    
    # Setup dummy environment for testing
    from .config import config
    from .data_loader import load_prompts
    import shutil
    
    # Clean up previous test runs
    if os.path.exists(config.RESULTS_DIR):
        shutil.rmtree(config.RESULTS_DIR)
    os.makedirs(config.RESULTS_DIR, exist_ok=True)
    os.makedirs(config.DATA_DIR, exist_ok=True)

    # Create a dummy prompts.csv for testing
    dummy_prompts_file = config.PROMPTS_FILE
    with open(dummy_prompts_file, "w", encoding="utf-8") as f:
        f.write("id,prompt\n")
        for i in range(10): # 10 dummy prompts
            f.write(f"{i},Test prompt {i} about a neutral topic.\n")

    print("--- Engine 模块测试 ---")

    # Simulate user choices for a new run
    test_prompts_df = load_prompts(dummy_prompts_file)
    if test_prompts_df is None:
        print("无法加载测试提示词。")
        sys.exit(1)

    user_choices_new_run = {
        'model_name': config.DEFAULT_MODEL,
        'prompts_df': test_prompts_df,
        'start_index': 0,
        'end_index': 9,
        'resume_state': None,
        'current_results_dir': get_timestamped_results_dir()
    }

    print("\n--- 测试新任务运行 ---")
    engine_new = AnalysisEngine(user_choices_new_run)
    engine_new.run_analysis()

    # Simulate user choices for a resumed run (after a partial run)
    # Manually create a partial state for testing resume
    partial_results_dir = get_timestamped_results_dir()
    os.makedirs(partial_results_dir, exist_ok=True)
    partial_state_manager = StateManager(partial_results_dir)
    partial_state_manager.save_state(
        last_processed_index=4, # Processed up to index 4 (5 items)
        total_prompts=len(test_prompts_df),
        current_model=config.DEFAULT_MODEL,
        start_index=0,
        end_index=9
    )
    
    user_choices_resume_run = {
        'model_name': config.DEFAULT_MODEL,
        'prompts_df': test_prompts_df,
        'start_index': 0, # This will be overridden by resume_state
        'end_index': 9,   # This will be overridden by resume_state
        'resume_state': partial_state_manager.load_state(), # Load the partial state
        'current_results_dir': partial_results_dir
    }

    print("\n--- 测试续传任务运行 ---")
    engine_resume = AnalysisEngine(user_choices_resume_run)
    engine_resume.run_analysis()

    print("\n清理测试环境...")
    if os.path.exists(config.DATA_DIR):
        shutil.rmtree(config.DATA_DIR)
    if os.path.exists(config.RESULTS_DIR):
        shutil.rmtree(config.RESULTS_DIR)
    print("清理完成。")
