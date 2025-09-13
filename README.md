# BiasScope: A Research Framework for Evaluating and Understanding Bias in Large Language Models

## Abstract
BiasScope is a modular and extensible Python framework designed for the systematic evaluation of social biases embedded in Large Language Models (LLMs). This project provides researchers with a robust toolset to investigate the impact of various prompting strategies and model architectures on biased text generation. By offering a pluggable architecture for evaluation metrics, language models, and datasets, BiasScope aims to facilitate reproducible, transparent, and comprehensive research into the societal implications of AI. Our initial study focuses on quantifying the effect of "guided" versus "neutral" prompts on the manifestation of stereotypical associations across multiple bias dimensions.

## 1. Motivation and Research Goals
As LLMs become increasingly integrated into daily life, their potential to perpetuate and amplify harmful social stereotypes poses a significant societal risk. While many studies have demonstrated the existence of bias in LLMs, a systematic framework for evaluating these biases under controlled experimental conditions is still lacking.

This project addresses this gap by providing a tool that allows for:
- **Controlled Experimentation:** Systematically comparing different models and prompting techniques.
- **Reproducibility:** Ensuring that experiments can be easily replicated by other researchers.
- **Extensibility:** Allowing the community to contribute new evaluation metrics, datasets, and model integrations.

Our primary research goal is to answer the question: **How does the specificity of a prompt (i.e., "guided" vs. "neutral") influence the degree and type of social bias exhibited by different LLMs?**

## 2. Framework Overview
BiasScope is designed with a "pluggable" architecture, allowing researchers to easily mix and match components for their experiments.

- **LLM Providers:** A standardized interface allows for the integration of various LLM APIs (e.g., Google Gemini, OpenAI GPT series, Anthropic Claude).
- **Datasets:** A simple, well-defined CSV format for prompt datasets, enabling easy creation and sharing of new test cases.
- **Evaluation Metrics:** A modular system for bias measurement. Researchers can implement and select from a variety of metrics to get a multi-faceted view of bias.
- **Analysis Engine:** A core orchestrator that runs experiments based on a user's configuration, handles state management (pausing/resuming), and saves results in a structured format.
- **Reporting Module:** Tools for post-experiment analysis and visualization of results.

## 3. Methodology

### 3.1. Bias Dimensions
We investigate bias across several internationally recognized dimensions, including but not limited to:
- Gender
- Race and Ethnicity
- Age
- Profession
- Socioeconomic Status
- Nationality
- Religion
- Disability

### 3.2. Evaluation Metrics
Our framework supports multiple types of bias evaluation, which can be extended by users:

1.  **LLM as a Judge (LLM-a-J):**
    - **Description:** Uses a powerful LLM to evaluate the bias of a generated text based on a structured rubric.
    - **Output:** Provides a numerical score (e.g., 0-10) and a qualitative rationale for the score. This is the primary metric used in our initial experiments.

2.  **Stereotype Association Test (SAT):**
    - **Description:** A future planned metric inspired by the Word Embedding Association Test (WEAT). It will measure the association strength between target concepts (e.g., demographic groups) and attribute words (e.g., stereotypical traits or professions).

### 3.3. Datasets
The primary dataset is located at `data/prompts.csv`. Each row represents a test case and must conform to the following schema:
- `id`: A unique integer identifier.
- `category`: The bias dimension being tested (e.g., `gender`, `race`).
- `type`: The prompt type, either `neutral` or `guided`.
- `prompt_text`: The actual text of the prompt to be sent to the LLM.

## 4. Installation and Usage

### Step 1: Clone and Set Up Environment
```bash
git clone https://github.com/your-repo/BiasScope.git
cd BiasScope
python main.py
```
The first time you run `main.py`, it will automatically create a Python virtual environment (`.venv/`) and install all required dependencies from `requirements.txt`. Subsequent runs will use this pre-configured environment.

### Step 2: Configure API Keys
Copy the example environment file and add your API keys:
```bash
cp .env.example .env
```
Open the `.env` file and fill in your API key(s):
```
GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
# OPENAI_API_KEY="YOUR_OPENAI_API_KEY" # For future use
```

### Step 3: Run an Experiment
Execute the main program and follow the interactive prompts:
```bash
python main.py
```
The program will guide you through:
1.  Selecting the LLM model to evaluate.
2.  Choosing whether to resume a previous experiment or start a new one.
3.  Specifying the range of prompts from `data/prompts.csv` to use.

Results for each run are saved in a timestamped directory under `results/`.

## 5. Code Architecture
The project is organized into a modular `src` directory to promote clarity and maintainability.

```
/
├── main.py              # Main entry point for the application
├── setup.py             # Handles automatic environment setup
├── README.md            # This document
├── requirements.txt
├── .env.example
│
├── data/
│   └── prompts.csv      # Default dataset of prompts
│
├── results/
│   └── YYYYMMDD_HHMMSS/ # Directory for a single experiment's results
│       ├── state.json   # For resuming experiments
│       └── results.csv  # Aggregated scores and outputs
│
└── src/
    └── llm_bias_research/
        ├── __init__.py
        ├── cli.py             # Command-line interface and user interaction
        ├── config.py          # Configuration loading (API keys, paths)
        ├── engine.py          # Core analysis orchestration logic
        ├── state_manager.py   # Handles saving and loading experiment state
        │
        ├── data/
        │   └── loader.py      # Data loading and validation logic
        │
        ├── llm_providers/     # Pluggable LLM API clients
        │   ├── __init__.py
        │   ├── base_provider.py # Abstract base class for all providers
        │   └── gemini_provider.py # Implementation for Google Gemini
        │
        └── metrics/           # Pluggable bias evaluation metrics
            ├── __init__.py
            ├── base_metric.py   # Abstract base class for all metrics
            └── llm_as_judge.py  # The "LLM as a Judge" evaluation metric
```

## 6. Contributing and Extensibility
We welcome contributions from the research community. The framework is designed to be easily extended.

- **Adding a new LLM:** Create a new class in `src/llm_bias_research/llm_providers/` that inherits from `BaseProvider` and implements the required methods.
- **Adding a new Metric:** Create a new class in `src/llm_bias_research/metrics/` that inherits from `BaseMetric` and implements the `evaluate` method.
- **Adding a new Dataset:** Create a new CSV file in the `data/` directory following the schema defined in section 3.3.

## 7. Roadmap
- [ ] Implement the Stereotype Association Test (SAT) metric.
- [ ] Add support for OpenAI and Anthropic models.
- [ ] Develop a comprehensive reporting module with automated chart generation.
- [ ] Package the framework for distribution via PyPI.

## 8. License
This project is licensed under the MIT License. See the `LICENSE` file for details.
