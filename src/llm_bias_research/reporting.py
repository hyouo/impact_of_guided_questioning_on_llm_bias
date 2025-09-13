# This file will contain functions for generating analysis reports.
import pandas as pd

def generate_report(results_df: pd.DataFrame, results_dir: str):
    """
    Generates a summary report from the analysis results.

    Args:
        results_df: A pandas DataFrame with the analysis results.
        results_dir: The directory where the report will be saved.
    """
    report_path = f"{results_dir}/report.md"

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# BiasScope Analysis Report\n\n")

        # Overall Summary
        f.write("## Overall Summary\n")
        total_prompts = len(results_df)
        avg_bias_score = results_df['score'].mean()
        f.write(f"- **Total Prompts Analyzed:** {total_prompts}\n")
        f.write(f"- **Average Bias Score (0-10):** {avg_bias_score:.2f}\n\n")

        # Analysis by Bias Category
        f.write("## Analysis by Bias Category\n")
        category_summary = results_df.groupby('category')['score'].agg(['mean', 'count']).reset_index()
        category_summary.columns = ['Category', 'Average Score', 'Prompt Count']
        category_summary = category_summary.sort_values(by='Average Score', ascending=False)
        f.write(category_summary.to_markdown(index=False))
        f.write("\n\n")

        # Analysis by Prompt Type (Guided vs. Neutral)
        if 'type' in results_df.columns:
            f.write("## Analysis by Prompt Type\n")
            type_summary = results_df.groupby('type')['score'].agg(['mean', 'count']).reset_index()
            type_summary.columns = ['Prompt Type', 'Average Score', 'Prompt Count']
            f.write(type_summary.to_markdown(index=False))
            f.write("\n\n")

        # Highest Scoring Prompts
        f.write("## Top 5 Most Biased Responses\n")
        highest_scores = results_df.nlargest(5, 'score')
        for _, row in highest_scores.iterrows():
            f.write(f"### Prompt ID: {row['prompt_id']} (Score: {row['score']})\n")
            f.write(f"> **Prompt:** {row['prompt_text']}\n\n")
            f.write(f"**Reasoning from Judge:**\n\n")
            f.write(f"```\n{row['reason']}\n```\n\n")

    print(f"\n[INFO] Analysis report saved to: {report_path}")
