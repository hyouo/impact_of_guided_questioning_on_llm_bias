import pandas as pd
import os
from .config import config # Import config from the same package

def load_prompts(file_path=config.PROMPTS_FILE):
    """
    Loads prompts from a CSV file.

    Args:
        file_path (str): The absolute path to the prompts CSV file.

    Returns:
        pandas.DataFrame: A DataFrame containing the prompts.
        None: If the file is not found or an error occurs.
    """
    if not os.path.exists(file_path):
        print(f"错误: 提示词文件未找到: {file_path}")
        return None
    
    try:
        # Assuming the CSV has a column named 'prompt' or similar
        # Adjust 'header=None' or 'names' if your CSV has no header or specific column names
        df = pd.read_csv(file_path)
        print(f"成功加载 {len(df)} 条提示词。")
        return df
    except Exception as e:
        print(f"加载提示词文件时发生错误: {e}")
        return None

if __name__ == "__main__":
    # Example usage (for testing this module independently)
    # This assumes prompts.csv is in the 'data' directory relative to the project root
    # For actual run, config.PROMPTS_FILE will provide the correct path
    
    # Create a dummy prompts.csv for testing
    dummy_data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
    dummy_prompts_file = os.path.join(dummy_data_dir, "prompts.csv")
    
    if not os.path.exists(dummy_data_dir):
        os.makedirs(dummy_data_dir)

    with open(dummy_prompts_file, "w", encoding="utf-8") as f:
        f.write("id,prompt\n")
        f.write("1,What is the capital of France?\n")
        f.write("2,Tell me about the history of AI.\n")
        f.write("3,Write a short story about a talking cat.\n")

    prompts_df = load_prompts(dummy_prompts_file)
    if prompts_df is not None:
        print("\n加载的提示词示例:")
        print(prompts_df.head())
    
    # Clean up dummy file
    os.remove(dummy_prompts_file)
    print(f"\n已删除测试文件: {dummy_prompts_file}")
