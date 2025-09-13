import os
import pandas as pd
from tqdm import tqdm
import time

from .config import get_timestamped_results_dir
from .data.loader import load_prompts
from .llm_providers.base_provider import BaseProvider
from .llm_providers.gemini_provider import APIError
from .metrics.base_metric import BaseMetric
from .state_manager import StateManager
from .reporting import generate_report
from .cli import display_message, handle_api_error_prompt

class AnalysisEngine:
    def __init__(self, provider: BaseProvider, metric: BaseMetric, user_choices: dict):
        self.provider = provider
        self.metric = metric
        self.model_name = user_choices['model_name']
        self.prompts_df = user_choices['prompts_df']
        self.start_index = user_choices['start_index']
        self.end_index = user_choices['end_index']
        self.resume_state = user_choices['resume_state']
        self.current_results_dir = user_choices['current_results_dir']

        self.state_manager = StateManager(self.current_results_dir)
        self.raw_responses_dir = os.path.join(self.current_results_dir, "raw_responses")
        os.makedirs(self.raw_responses_dir, exist_ok=True)

        self.results_file = os.path.join(self.current_results_dir, "results.csv")
        self.results = []

        display_message(f"Analysis Engine initialized. Results will be saved to: {self.current_results_dir}", "info")

    def _load_existing_results(self):
        if self.resume_state and os.path.exists(self.results_file):
            try:
                existing_df = pd.read_csv(self.results_file)
                self.results = existing_df.to_dict(orient='records')
                display_message(f"Loaded {len(self.results)} existing results.", "info")
            except Exception as e:
                display_message(f"Could not load existing results, starting fresh: {e}", "warning")
                self.results = []

    def _save_results(self):
        if not self.results:
            display_message("No results to save.", "warning")
            return
        try:
            pd.DataFrame(self.results).to_csv(self.results_file, index=False, encoding="utf-8")
            display_message(f"Results saved to: {self.results_file}", "info")
        except Exception as e:
            display_message(f"Failed to save results: {e}", "error")

    def run_analysis(self):
        self._load_existing_results()

        start_point = self.resume_state['last_processed_index'] + 1 if self.resume_state else self.start_index
        if start_point > self.end_index:
            display_message("All tasks in the specified range are already complete.", "info")
            return

        display_message(f"Starting analysis from prompt #{start_point} to #{self.end_index}", "info")

        with tqdm(total=(self.end_index - start_point + 1), desc=f"Analyzing with {self.model_name}", unit="prompt") as pbar:
            for i in range(start_point, self.end_index + 1):
                prompt_data = self.prompts_df.iloc[i]

                try:
                    response_text = self.provider.get_response(prompt_data['prompt_text'])

                    # Save raw response
                    raw_response_file = os.path.join(self.raw_responses_dir, f"response_{prompt_data['id']}.txt")
                    with open(raw_response_file, "w", encoding="utf-8") as f:
                        f.write(response_text)

                    evaluation = self.metric.evaluate(response_text)

                    result_data = {
                        "prompt_id": prompt_data['id'],
                        "category": prompt_data['category'],
                        "type": prompt_data['type'],
                        "prompt_text": prompt_data['prompt_text'],
                        "model_name": self.model_name,
                        "response_path": os.path.basename(raw_response_file),
                    }
                    result_data.update(evaluation)
                    self.results.append(result_data)
                    
                    self.state_manager.save_state(i, len(self.prompts_df), self.model_name, self.start_index, self.end_index)
                    pbar.update(1)

                except APIError as e:
                    should_continue = handle_api_error_prompt(str(e), self.state_manager, i, len(self.prompts_df), self.model_name, self.start_index, self.end_index)
                    if not should_continue:
                        display_message("User chose to exit. Analysis interrupted.", "info")
                        break
                except Exception as e:
                    display_message(f"An unexpected error occurred on prompt {prompt_data['id']}: {e}", "error")
                    should_continue = handle_api_error_prompt(str(e), self.state_manager, i, len(self.prompts_df), self.model_name, self.start_index, self.end_index)
                    if not should_continue:
                        display_message("User chose to exit. Analysis interrupted.", "info")
                        break

        self._save_results()
        if self.results:
            generate_report(pd.DataFrame(self.results), self.current_results_dir)
        display_message("Analysis complete.", "info")
