import json
import os
import datetime

class StateManager:
    def __init__(self, results_dir):
        self.results_dir = results_dir
        self.state_file_path = os.path.join(results_dir, "analysis_state.json")

    def save_state(self, last_processed_index, total_prompts, current_model, start_index, end_index):
        """
        Saves the current analysis state to a JSON file.
        """
        state = {
            "last_processed_index": last_processed_index,
            "total_prompts": total_prompts,
            "current_model": current_model,
            "start_index": start_index,
            "end_index": end_index,
            "timestamp": os.path.basename(self.results_dir), # Store the timestamped folder name
            "saved_at": datetime.datetime.now().isoformat()
        }
        try:
            with open(self.state_file_path, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=4)
            print(f"分析状态已保存到: {self.state_file_path}")
        except Exception as e:
            print(f"保存分析状态失败: {e}")

    def load_state(self):
        """
        Loads the analysis state from a JSON file.
        Returns the state dictionary or None if file not found/error.
        """
        if not os.path.exists(self.state_file_path):
            return None
        
        try:
            with open(self.state_file_path, "r", encoding="utf-8") as f:
                state = json.load(f)
            print(f"分析状态已从 {self.state_file_path} 加载。")
            return state
        except Exception as e:
            print(f"加载分析状态失败: {e}")
            return None

    @staticmethod
    def find_resumable_states(base_results_dir):
        """
        Scans the base results directory for folders containing analysis_state.json.
        Returns a list of (folder_name, state_data) tuples.
        """
        resumable_states = []
        if not os.path.exists(base_results_dir):
            return resumable_states

        for entry in os.listdir(base_results_dir):
            full_path = os.path.join(base_results_dir, entry)
            if os.path.isdir(full_path):
                state_file = os.path.join(full_path, "analysis_state.json")
                if os.path.exists(state_file):
                    try:
                        with open(state_file, "r", encoding="utf-8") as f:
                            state_data = json.load(f)
                        resumable_states.append((entry, state_data))
                    except Exception as e:
                        print(f"警告: 读取 {state_file} 失败: {e}")
        
        # Sort by timestamp (folder name)
        resumable_states.sort(key=lambda x: x[0], reverse=True)
        return resumable_states

if __name__ == "__main__":
    # Example usage for testing
    from .config import config, get_timestamped_results_dir
    import shutil

    print("--- StateManager 模块测试 ---")

    # 1. Test saving state
    test_results_dir = get_timestamped_results_dir()
    os.makedirs(test_results_dir, exist_ok=True)
    print(f"创建测试结果目录: {test_results_dir}")

    sm = StateManager(test_results_dir)
    sm.save_state(
        last_processed_index=10, 
        total_prompts=100, 
        current_model="gemini-test",
        start_index=0,
        end_index=99
    )

    # 2. Test loading state
    loaded_state = sm.load_state()
    if loaded_state:
        print("\n加载的状态:")
        print(json.dumps(loaded_state, indent=4))
        assert loaded_state["last_processed_index"] == 10
        assert loaded_state["total_prompts"] == 100
        print("状态加载测试通过。")
    else:
        print("状态加载测试失败。")

    # 3. Test finding resumable states
    print("\n测试查找可恢复状态:")
    # Create another dummy state
    test_results_dir_old = os.path.join(config.RESULTS_DIR, "20240101_120000")
    os.makedirs(test_results_dir_old, exist_ok=True)
    sm_old = StateManager(test_results_dir_old)
    sm_old.save_state(
        last_processed_index=5, 
        total_prompts=50, 
        current_model="gemini-old",
        start_index=0,
        end_index=49
    )

    resumable = StateManager.find_resumable_states(config.RESULTS_DIR)
    if resumable:
        print(f"找到 {len(resumable)} 个可恢复状态:")
        for folder, state in resumable:
            print(f"- 文件夹: {folder}, 最后处理: {state['last_processed_index']}")
        assert len(resumable) >= 2 # Should find at least the two we created
        print("查找可恢复状态测试通过。")
    else:
        print("查找可恢复状态测试失败。")

    # Clean up test directories
    print("\n清理测试目录...")
    if os.path.exists(test_results_dir):
        shutil.rmtree(test_results_dir)
    if os.path.exists(test_results_dir_old):
        shutil.rmtree(test_results_dir_old)
    print("清理完成。")
