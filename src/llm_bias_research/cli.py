import os
import sys
import google.generativeai as genai
import openai

from .config import config, get_timestamped_results_dir
from .state_manager import StateManager
from .data.loader import load_prompts
from .llm_providers.gemini_provider import GeminiProvider, APIError
from .llm_providers.openai_provider import OpenAIProvider
from .metrics.llm_as_judge import LLMAsJudge

def display_message(message, level="info"):
    """Displays a formatted message to the console."""
    print(f"\n[{level.upper()}] {message}")

def get_user_input(prompt, default=None):
    """Gets validated input from the user."""
    full_prompt = f"{prompt} (default: {default}): " if default else f"{prompt}: "
    return input(full_prompt) or default

def select_provider():
    """Prompts the user to select an LLM provider."""
    display_message("Please select an LLM Provider:", "info")
    providers = ["Gemini", "OpenAI"]
    for i, name in enumerate(providers):
        print(f"  {i + 1}. {name}")
    
    while True:
        choice = get_user_input(f"Enter the number (1-{len(providers)})")
        try:
            index = int(choice) - 1
            if 0 <= index < len(providers):
                return providers[index]
            else:
                display_message("Invalid selection. Please try again.", "warning")
        except (ValueError, TypeError):
            display_message("Invalid input. Please enter a number.", "warning")

def select_model(provider_name):
    """Queries for available models for the selected provider and prompts the user for a choice."""
    display_message(f"Querying for available {provider_name} models...", "info")
    models = []
    try:
        if provider_name == "Gemini":
            if not config.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY not found in .env file.")
            genai.configure(api_key=config.GEMINI_API_KEY)
            models = [m.name for m in genai.list_models() if "generateContent" in m.supported_generation_methods and "gemini" in m.name]
        elif provider_name == "OpenAI":
            if not config.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not found in .env file.")
            # OpenAI's library doesn't have a simple model list function like Gemini's.
            # We will list a few popular and recommended models.
            models = ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]
        
        if not models:
            display_message(f"No suitable models found for {provider_name}.", "error")
            sys.exit(1)

        display_message(f"Please select a model from {provider_name}:", "info")
        for i, model_name in enumerate(models):
            print(f"  {i + 1}. {model_name}")

        while True:
            choice = get_user_input(f"Enter the number (1-{len(models)})")
            try:
                index = int(choice) - 1
                if 0 <= index < len(models):
                    return models[index]
                else:
                    display_message("Invalid selection. Please try again.", "warning")
            except (ValueError, TypeError):
                display_message("Invalid input. Please enter a number.", "warning")

    except Exception as e:
        display_message(f"Failed to get models for {provider_name}: {e}", "error")
        sys.exit(1)

def select_metric(provider):
    """Allows the user to select an evaluation metric."""
    display_message("Using 'LLM as Judge' as the evaluation metric.", "info")
    return LLMAsJudge(provider)

def get_user_choices():
    """Orchestrates the collection of all user choices for the experiment."""
    provider_name = select_provider()
    model_name = select_model(provider_name)

    provider = None
    if provider_name == "Gemini":
        provider = GeminiProvider(model_name=model_name)
    elif provider_name == "OpenAI":
        provider = OpenAIProvider(model_name=model_name)

    metric = select_metric(provider)

    prompts_df = load_prompts()
    if prompts_df is None or prompts_df.empty:
        display_message("Failed to load prompts. Exiting.", "error")
        return None
    total_prompts = len(prompts_df)

    choices = {
        'provider': provider,
        'metric': metric,
        'model_name': model_name,
        'prompts_df': prompts_df,
        'resume_state': None,
        'current_results_dir': None
    }

    # Resumption logic
    resumable_states = StateManager.find_resumable_states(config.RESULTS_DIR)
    if resumable_states:
        display_message("Found incomplete analysis tasks:", "info")
        for i, (folder, state) in enumerate(resumable_states):
            print(f"  {i+1}. {folder} (Model: {state.get('current_model', 'N/A')}, "
                  f"Progress: {state.get('last_processed_index', -1) + 1}/{state.get('total_prompts', 'N/A')})")
        
        resume_choice = get_user_input("Enter number to resume, or 'n' for a new task", default='n')
        if resume_choice.lower() != 'n':
            try:
                idx = int(resume_choice) - 1
                if 0 <= idx < len(resumable_states):
                    choices['resume_state'] = resumable_states[idx][1]
                    choices['current_results_dir'] = os.path.join(config.RESULTS_DIR, resumable_states[idx][0])
            except (ValueError, IndexError):
                display_message("Invalid selection. Starting a new task.", "warning")

    # Determine analysis range
    if choices['resume_state']:
        state = choices['resume_state']
        choices['start_index'] = state['last_processed_index'] + 1
        choices['end_index'] = state['end_index']
        display_message(f"Resuming analysis from prompt #{choices['start_index']}.", "info")
    else:
        display_message(f"There are {total_prompts} prompts available for analysis.", "info")
        start = int(get_user_input("Enter the starting prompt number (0-indexed)", "0"))
        end = int(get_user_input(f"Enter the ending prompt number", str(total_prompts - 1)))
        choices['start_index'], choices['end_index'] = start, end
        choices['current_results_dir'] = get_timestamped_results_dir()
        display_message(f"Starting new analysis from prompt #{start} to #{end}.", "info")

    return choices

def handle_api_error_prompt(error_message, state_manager_instance, last_processed_index, total_prompts, current_model, start_index, end_index):
    """Prompts the user on how to proceed after an API error."""
    display_message(f"An API error occurred: {error_message}", "error")
    choice = get_user_input("Would you like to save progress and exit? (y/n)", default='y')
    if choice.lower() == 'y':
        state_manager_instance.save_state(last_processed_index, total_prompts, current_model, start_index, end_index)
        return False
    return True