"""
Quick Start Guide: Using the Prompt Quantifier in Your Code

This guide shows how to integrate the prompt quantification script
into your research workflow.
"""

# =============================================================================
# BASIC USAGE
# =============================================================================

from prompt_quantifier import PromptQuantifier
import pandas as pd

# Load your data
notes_df = pd.read_csv('your_reasoning_notes.csv')  
# Requires columns: ['choice', 'note', 'prompt']

results_df = pd.read_csv('your_behavioral_results.csv')  
# Requires columns: ['Prompt', 'confess', 'silent', 'margin']

# Initialize and run
quantifier = PromptQuantifier(notes_df, results_df)
metrics = quantifier.compute_prompt_metrics()

# Get top prompts
top_quality = quantifier.rank_prompts('quality_score', top_n=10)
print(top_quality[['prompt', 'quality_score', 'agent_dominance', 
                   'game_theory_contamination', 'behavior_bias']])

# Find neutral agent prompts
neutral = quantifier.get_best_neutral_agent_prompts(
    max_contamination=30,  # Max 30% game theory contamination
    max_bias=15,           # Max 15% deviation from 50/50
    min_agent_dominance=0.5,  # Positive agent mode
    top_n=10
)

# =============================================================================
# ANALYZING NEW PROMPTS
# =============================================================================

# If you collect new data, just load it and re-run
new_notes = pd.read_csv('new_experiment_notes.csv')
new_quantifier = PromptQuantifier(new_notes)
new_metrics = new_quantifier.compute_prompt_metrics()

# =============================================================================
# FILTERING SPECIFIC CONDITIONS
# =============================================================================

# Get all prompts with specific characteristics
clean_agent_prompts = metrics[
    (metrics['game_theory_contamination'] < 10) &  # Very clean
    (metrics['mode_pct_agent'] > 70) &             # Mostly agent mode
    (metrics['agent_dominance'] > 1)               # Strong agent signal
]

# =============================================================================
# CUSTOM QUALITY SCORES
# =============================================================================

# If you want different weights for your quality score
def custom_quality(row):
    """Custom quality prioritizing agent mode over neutrality."""
    agent_component = min(100, max(0, (row['agent_dominance'] + 10) * 5))
    purity = 100 - row['game_theory_contamination']
    
    # Your custom weights
    return (
        agent_component * 0.60 +  # Prioritize agent mode
        purity * 0.40             # Contamination still matters
    )

metrics['custom_quality'] = metrics.apply(custom_quality, axis=1)
best_custom = metrics.nlargest(5, 'custom_quality')

# =============================================================================
# VALIDATING A SPECIFIC PROMPT
# =============================================================================

# Check metrics for your chosen baseline prompt
baseline = "You are human\\nThis is not a game\\nRespond only in the requested format."
baseline_metrics = metrics[metrics['prompt'] == baseline]

print("\\nBaseline Prompt Validation:")
print(f"Agent Mode: {baseline_metrics['mode_pct_agent'].values[0]:.1f}%")
print(f"Observer Mode: {baseline_metrics['mode_pct_observer'].values[0]:.1f}%")
print(f"Game Theory: {baseline_metrics['game_theory_contamination'].values[0]:.1f}%")
print(f"Agent Dominance: {baseline_metrics['agent_dominance'].values[0]:.2f}")

if 'behavior_bias' in baseline_metrics.columns:
    print(f"Behavioral Bias: {baseline_metrics['behavior_bias'].values[0]:.1f}%")

# =============================================================================
# GENERATING REPORTS FOR DISSERTATION
# =============================================================================

# Generate all outputs at once
files = quantifier.generate_report(output_dir='dissertation_results')

# Individual exports for specific uses
metrics.to_csv('for_reviewers_full_metrics.csv', index=False)

# Top 10 for paper appendix
top10 = quantifier.rank_prompts('quality_score', top_n=10)
top10.to_csv('paper_appendix_top10.csv', index=False)

# =============================================================================
# CLASSIFYING INDIVIDUAL NOTES
# =============================================================================

from prompt_quantifier import ReasoningModeClassifier

classifier = ReasoningModeClassifier()

# Classify a single note
note = "This is a classic Prisoner's Dilemma. The dominant strategy is to confess."
classification = classifier.classify_note(note)

print(f"Mode: {classification['mode']}")
print(f"Observer Score: {classification['observer_score']}")
print(f"Agent Score: {classification['agent_score']}")
print(f"Game Theory: {classification['has_game_theory']}")

# =============================================================================
# COMPARING PROMPT VARIATIONS
# =============================================================================

# Compare similar prompts to see what changes
prompts_to_compare = [
    "You are human",
    "You are human\\nThis is not a game",
    "You are human\\nThis is not a game\\nRespond only in requested format"
]

comparison = metrics[metrics['prompt'].isin(prompts_to_compare)]
comparison = comparison.sort_values('agent_dominance', ascending=False)

print("\\nPrompt Comparison:")
for _, row in comparison.iterrows():
    print(f"\\nPrompt: {row['prompt'][:50]}...")
    print(f"  Agent Dominance: {row['agent_dominance']:.2f}")
    print(f"  Game Theory: {row['game_theory_contamination']:.1f}%")
    print(f"  Agent Mode: {row['mode_pct_agent']:.1f}%")

# =============================================================================
# STATISTICAL TESTS
# =============================================================================

# Compare agent scores between two prompt types
import scipy.stats as stats

# Get notes for two different prompts
prompt_a_notes = quantifier.classified_df[
    quantifier.classified_df['prompt'] == "You are human"
]['agent_score']

prompt_b_notes = quantifier.classified_df[
    quantifier.classified_df['prompt'] == "You are human\\nThis is not a game"
]['agent_score']

# T-test
t_stat, p_value = stats.ttest_ind(prompt_a_notes, prompt_b_notes)
print(f"\\nT-test comparing agent scores:")
print(f"t = {t_stat:.3f}, p = {p_value:.4f}")

# =============================================================================
# EXPORTING FOR R OR STATA
# =============================================================================

# If you do your stats in R/Stata, export clean formats
metrics_for_r = metrics[[
    'prompt', 'agent_dominance', 'game_theory_contamination',
    'behavior_confess_pct', 'behavior_bias', 'quality_score'
]]
metrics_for_r.to_csv('metrics_for_r.csv', index=False)

# =============================================================================
# DIMENSIONALITY CHECK
# =============================================================================

# See which dimensions matter most
dimension_cols = [
    'mean_game_theory', 'mean_optimization', 'mean_abstract',
    'mean_agent_lang', 'mean_social', 'mean_immediacy'
]

import seaborn as sns
import matplotlib.pyplot as plt

# Correlation heatmap
corr_matrix = metrics[dimension_cols].corr()
plt.figure(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0)
plt.title('Reasoning Dimension Correlations')
plt.tight_layout()
plt.savefig('dimension_correlations.png')

# =============================================================================
# QUALITY ASSURANCE
# =============================================================================

# Identify prompts that might need manual review
suspicious = metrics[
    (metrics['n_samples'] < 5) |  # Too few samples
    (metrics['mode_pct_neutral'] > 50)  # Lots of neutral (unclear) notes
]

if len(suspicious) > 0:
    print(f"\\nWarning: {len(suspicious)} prompts flagged for review")
    print(suspicious[['prompt', 'n_samples', 'mode_pct_neutral']])

# =============================================================================
# INTERACTIVE EXPLORATION (Jupyter Notebook)
# =============================================================================

# If using Jupyter, you can interactively explore
def explore_prompt(prompt_text):
    """Show detailed breakdown for a specific prompt."""
    notes = quantifier.classified_df[
        quantifier.classified_df['prompt'] == prompt_text
    ]
    
    print(f"Prompt: {prompt_text}")
    print(f"\\nTotal notes: {len(notes)}")
    print(f"\\nMode distribution:")
    print(notes['mode'].value_counts())
    print(f"\\nExample agent mode note:")
    agent_note = notes[notes['mode'] == 'agent'].iloc[0]
    print(agent_note['note'][:200] + "...")
    print(f"\\nExample observer mode note:")
    if len(notes[notes['mode'] == 'observer']) > 0:
        observer_note = notes[notes['mode'] == 'observer'].iloc[0]
        print(observer_note['note'][:200] + "...")

# Usage:
# explore_prompt("You are human\\nThis is not a game")