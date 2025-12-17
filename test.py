#!/usr/bin/env python3
"""
Semantic Analysis of LLM Embodiment in Prisoner's Dilemma

This script consolidates the full analysis pipeline:
1. Load and explore data
2. Initial three-dimension scoring
3. Keyword validation (log-odds ratios)
4. Discover discriminative terms
5. PCA to examine dimension structure
6. Refined scoring system
7. Generate figures for paper

Structured for easy conversion to Jupyter notebook.
Each section marked with # %% can become a cell.

Usage:
    python consolidated_embodiment_analysis.py [input_file.json]
    
Author: Research collaboration
"""

# %% [markdown]
# # Semantic Analysis of LLM Embodiment in Prisoner's Dilemma
# 
# This notebook analyzes reasoning patterns in LLM responses to the Prisoner's Dilemma,
# operationalizing "embodiment" - the degree to which an LLM engages as a participant
# rather than an external analyst.

# %% Imports and Setup
import json
import re
import sys
import numpy as np
import pandas as pd
from collections import Counter
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Set style for figures
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 11
plt.rcParams['axes.titlesize'] = 13
plt.rcParams['axes.labelsize'] = 11

# Output directory for figures
import os
FIGURE_DIR = '/home/claude/figures'
os.makedirs(FIGURE_DIR, exist_ok=True)

# %% Load Data
def load_data(filepath):
    """Load the JSON data file with choice, note, and prompt fields."""
    with open(filepath) as f:
        data = json.load(f)
    
    # Convert to DataFrame
    records = []
    for idx in data['choice'].keys():
        records.append({
            'idx': idx,
            'choice': data['choice'].get(idx),
            'note': data['note'].get(idx) or '',
            'prompt': data['prompt'].get(idx) or ''
        })
    
    df = pd.DataFrame(records)
    df['confess'] = (df['choice'] == 'Confess').astype(int)
    df['note_length'] = df['note'].str.len()
    
    # Filter to records with actual reasoning
    df = df[df['note_length'] > 20].copy()
    
    return df, data

# Load the data
INPUT_FILE = sys.argv[1] if len(sys.argv) > 1 else '/mnt/user-data/uploads/primordial_system_prompt_notes.json'
print(f"Loading data from: {INPUT_FILE}")
df, raw_data = load_data(INPUT_FILE)

print(f"Total trials with reasoning: {len(df)}")
print(f"Confession rate: {df['confess'].mean()*100:.1f}%")
print(f"Unique prompts: {df['prompt'].nunique()}")

# %% [markdown]
# ## Part 1: Initial Three-Dimension Framework
# 
# We hypothesize three dimensions of embodiment:
# 1. **Grammatical Perspective**: First-person vs third-person language
# 2. **Ontological Framing**: Concrete/real vs abstract/hypothetical
# 3. **Reasoning Mode**: Moral/relational vs strategic/analytical

# %% Define Initial Keyword Lists (Theory-Driven)
# These are the original, theory-motivated keyword lists

INITIAL_MARKERS = {
    # Dimension 1: Grammatical Perspective
    'first_person': [r'\bI\b', r'\bmy\b', r'\bme\b', r'\bwe\b', r'\bour\b', r'\bus\b'],
    'third_person': [r'a rational', r'one would', r'one should', r'the player', 
                     r'an individual', r'people would'],
    
    # Dimension 2: Ontological Framing  
    'abstract': ["prisoner's dilemma", 'game theory', 'nash equilibrium', 
                 'dominant strategy', 'payoff', 'classic example', 
                 'theoretical', 'hypothetical', 'this game'],
    'concrete': ['jail', 'prison', 'sentence', 'arrested', 'accomplice', 
                 'betray', 'guilty', 'go free', 'convicted'],
    
    # Dimension 3: Reasoning Mode
    'strategic': ['optimal', 'maximize', 'minimize', 'rational', 'strategic',
                  'self-interest', 'dominant', 'worst-case', 'best-case', 
                  'risk', 'defect', 'incentive'],
    'moral': ['trust', 'loyal', 'cooperat', 'mutual', 'fair', 'betray',
              'guilt', 'wrong', 'ethical', 'moral', 'together', 'harm'],
}

def count_markers(text, patterns):
    """Count occurrences of patterns in text."""
    text_lower = text.lower()
    count = 0
    for p in patterns:
        if p.startswith(r'\b'):
            count += len(re.findall(p, text, re.IGNORECASE))
        else:
            count += text_lower.count(p)
    return count

def score_dimension(text, positive_markers, negative_markers):
    """Score a dimension from -1 to +1."""
    pos = count_markers(text, positive_markers)
    neg = count_markers(text, negative_markers)
    total = pos + neg
    if total == 0:
        return 0.0
    return (pos - neg) / total

# %% Compute Initial Three-Dimension Scores
# Score each trial on the three dimensions

df['grammatical_score'] = df['note'].apply(
    lambda x: score_dimension(x, INITIAL_MARKERS['first_person'], INITIAL_MARKERS['third_person'])
)
df['ontological_score'] = df['note'].apply(
    lambda x: score_dimension(x, INITIAL_MARKERS['concrete'], INITIAL_MARKERS['abstract'])
)
df['reasoning_score'] = df['note'].apply(
    lambda x: score_dimension(x, INITIAL_MARKERS['moral'], INITIAL_MARKERS['strategic'])
)
df['embodiment_initial'] = (df['grammatical_score'] + df['ontological_score'] + df['reasoning_score']) / 3

print("Initial Three-Dimension Scores (mean ± std):")
print(f"  Grammatical:  {df['grammatical_score'].mean():.3f} ± {df['grammatical_score'].std():.3f}")
print(f"  Ontological:  {df['ontological_score'].mean():.3f} ± {df['ontological_score'].std():.3f}")
print(f"  Reasoning:    {df['reasoning_score'].mean():.3f} ± {df['reasoning_score'].std():.3f}")
print(f"  Composite:    {df['embodiment_initial'].mean():.3f} ± {df['embodiment_initial'].std():.3f}")

# %% Initial Correlations with Confession
print("\nCorrelation with Confession (initial dimensions):")
for col in ['grammatical_score', 'ontological_score', 'reasoning_score', 'embodiment_initial']:
    r, p = stats.pointbiserialr(df['confess'], df[col])
    print(f"  {col:20s}: r = {r:+.3f}, p = {p:.2e}")

# %% [markdown]
# ## Part 2: Keyword Validation
# 
# We validate each keyword by computing log-odds ratios: 
# how much more likely is the keyword to appear in Confess vs Stay Silent responses?

# %% Validate Individual Keywords
def validate_keyword(pattern, df):
    """Compute log-odds ratio for a keyword."""
    confess_notes = df[df['confess'] == 1]['note']
    silent_notes = df[df['confess'] == 0]['note']
    
    n_confess = len(confess_notes)
    n_silent = len(silent_notes)
    
    if pattern.startswith(r'\b'):
        in_confess = confess_notes.apply(lambda x: len(re.findall(pattern, x, re.IGNORECASE)) > 0).sum()
        in_silent = silent_notes.apply(lambda x: len(re.findall(pattern, x, re.IGNORECASE)) > 0).sum()
    else:
        in_confess = confess_notes.apply(lambda x: pattern in x.lower()).sum()
        in_silent = silent_notes.apply(lambda x: pattern in x.lower()).sum()
    
    # Log-odds ratio with smoothing
    lor = (np.log((in_confess + 1) / (n_confess - in_confess + 1)) - 
           np.log((in_silent + 1) / (n_silent - in_silent + 1)))
    
    return {
        'pattern': pattern,
        'in_confess': in_confess,
        'in_silent': in_silent,
        'p_confess': in_confess / n_confess,
        'p_silent': in_silent / n_silent,
        'log_odds': lor
    }

# Validate all keywords
validation_results = []
for category, patterns in INITIAL_MARKERS.items():
    for p in patterns:
        result = validate_keyword(p, df)
        result['category'] = category
        validation_results.append(result)

validation_df = pd.DataFrame(validation_results)

# %% Display Validation Results
print("\n" + "="*70)
print("KEYWORD VALIDATION RESULTS")
print("="*70)

for category in INITIAL_MARKERS.keys():
    cat_df = validation_df[validation_df['category'] == category].sort_values('log_odds', ascending=False)
    print(f"\n{category.upper()}:")
    for _, row in cat_df.iterrows():
        direction = "→ Confess" if row['log_odds'] > 0.3 else ("→ Silent" if row['log_odds'] < -0.3 else "→ Neutral")
        print(f"  {row['pattern']:25s} LOR: {row['log_odds']:+.2f}  {direction}")

# %% [markdown]
# ### Key Finding: First-Person Singular vs Plural
# 
# The validation reveals that first-person **singular** (I, my) does not discriminate,
# while first-person **plural** (we, our, us) strongly predicts cooperation.

# %% Examine First-Person Split
print("\n" + "="*70)
print("CRITICAL FINDING: First-Person Singular vs Plural")
print("="*70)

fp_results = validation_df[validation_df['category'] == 'first_person']
print("\nFirst-person markers and their log-odds ratios:")
for _, row in fp_results.iterrows():
    marker_type = "PLURAL" if row['pattern'] in [r'\bwe\b', r'\bour\b', r'\bus\b'] else "SINGULAR"
    print(f"  {row['pattern']:10s} ({marker_type:8s}): LOR = {row['log_odds']:+.2f}")

print("\n→ Singular pronouns (I, my, me) do NOT discriminate (LOR ≈ 0)")
print("→ Plural pronouns (we, our, us) strongly predict cooperation (LOR < -1.8)")

# %% Figure 1: Keyword Validation - Log-Odds Ratios
fig, ax = plt.subplots(figsize=(12, 8))

# Prepare data for plotting
plot_df = validation_df.copy()
plot_df['display_name'] = plot_df['pattern'].str.replace(r'\\b', '', regex=True)
plot_df = plot_df.sort_values('log_odds')

colors = ['#d62728' if x > 0.3 else '#2ca02c' if x < -0.3 else '#7f7f7f' 
          for x in plot_df['log_odds']]

bars = ax.barh(range(len(plot_df)), plot_df['log_odds'], color=colors)
ax.set_yticks(range(len(plot_df)))
ax.set_yticklabels(plot_df['display_name'], fontsize=9)
ax.axvline(x=0, color='black', linewidth=0.5)
ax.axvline(x=0.3, color='gray', linewidth=0.5, linestyle='--', alpha=0.5)
ax.axvline(x=-0.3, color='gray', linewidth=0.5, linestyle='--', alpha=0.5)

ax.set_xlabel('Log-Odds Ratio (positive = predicts Confession)')
ax.set_title('Figure 1: Keyword Validation\nLog-Odds Ratios for Theory-Driven Keywords')

# Add legend
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='#d62728', label='Predicts Confession (Observer)'),
    Patch(facecolor='#2ca02c', label='Predicts Silence (Embodied)'),
    Patch(facecolor='#7f7f7f', label='Does not discriminate')
]
ax.legend(handles=legend_elements, loc='lower right')

plt.tight_layout()
plt.savefig(f'{FIGURE_DIR}/fig1_keyword_validation.png', dpi=150, bbox_inches='tight')
plt.savefig(f'{FIGURE_DIR}/fig1_keyword_validation.pdf', bbox_inches='tight')
print(f"\nSaved: {FIGURE_DIR}/fig1_keyword_validation.png")
plt.show()

# %% [markdown]
# ## Part 3: Discover Additional Discriminative Terms
# 
# Beyond our theory-driven keywords, what other terms discriminate?

# %% Build Vocabulary and Compute Log-Odds for All Terms
def tokenize(text):
    """Get words and bigrams."""
    words = re.findall(r'\b[a-z]+\b', text.lower())
    bigrams = [f"{words[i]}_{words[i+1]}" for i in range(len(words)-1)]
    return words + bigrams

# Build vocabulary
all_tokens = Counter()
for note in df['note']:
    all_tokens.update(tokenize(note))

# Filter to common tokens
vocab = [w for w, c in all_tokens.items() if c >= 20]
print(f"Vocabulary size (≥20 occurrences): {len(vocab)}")

# Compute log-odds for all vocabulary terms
confess_notes = df[df['confess'] == 1]['note'].tolist()
silent_notes = df[df['confess'] == 0]['note'].tolist()
n_confess, n_silent = len(confess_notes), len(silent_notes)

vocab_stats = []
for word in vocab:
    in_confess = sum(1 for note in confess_notes if word in tokenize(note))
    in_silent = sum(1 for note in silent_notes if word in tokenize(note))
    
    lor = (np.log((in_confess + 1) / (n_confess - in_confess + 1)) - 
           np.log((in_silent + 1) / (n_silent - in_silent + 1)))
    
    vocab_stats.append({
        'word': word,
        'in_confess': in_confess,
        'in_silent': in_silent,
        'log_odds': lor,
        'total': in_confess + in_silent
    })

vocab_df = pd.DataFrame(vocab_stats)

# %% Display Most Discriminative Terms
print("\n" + "="*70)
print("TOP 15 TERMS PREDICTING CONFESSION (Observer Mode)")
print("="*70)
for _, row in vocab_df.nlargest(15, 'log_odds').iterrows():
    print(f"  {row['word']:30s} LOR: {row['log_odds']:+.2f}")

print("\n" + "="*70)
print("TOP 15 TERMS PREDICTING SILENCE (Embodied Mode)")
print("="*70)
for _, row in vocab_df.nsmallest(15, 'log_odds').iterrows():
    print(f"  {row['word']:30s} LOR: {row['log_odds']:+.2f}")

# %% [markdown]
# ### Key Finding: "dominant strategy" is nearly diagnostic
# 
# The bigram "dominant_strategy" has LOR = +5.36, appearing in 35.7% of Confess
# responses but only 0.2% of Stay Silent responses.

# %% [markdown]
# ## Part 4: PCA on Keyword Features
# 
# Do the three theoretical dimensions hold up empirically, or do they collapse?

# %% Build Feature Matrix for PCA
REFINED_CATEGORIES = {
    'first_person_plural': [r'\bwe\b', r'\bour\b', r'\bus\b'],
    'first_person_singular': [r'\bI\b', r'\bmy\b'],
    'game_theory_explicit': ['dominant strategy', 'game theory', "prisoner's dilemma", 'payoff'],
    'self_interest': ['self-interest', 'maximize', 'go free', 'for me'],
    'collective_interest': ['mutual', 'both of us', 'neither of us', 'together'],
    'strategic_reasoning': ['dominant', 'regardless of', 'strategic', 'rational choice'],
    'moral_reasoning': ['trust', 'fair', 'harm', 'betray', 'cooperat', 'ethical'],
    'optimization': ['minimize', 'maximize', 'optimal'],
    'risk_language': ['risk', 'avoid', 'prevent'],
}

for cat, patterns in REFINED_CATEGORIES.items():
    df[cat] = df['note'].apply(lambda x: count_markers(x, patterns))

# %% Run PCA
feature_cols = list(REFINED_CATEGORIES.keys())
X = df[feature_cols].values
X_scaled = StandardScaler().fit_transform(X)

pca = PCA(n_components=min(len(feature_cols), 5))
X_pca = pca.fit_transform(X_scaled)

# Add PC scores to dataframe
for i in range(pca.n_components_):
    df[f'PC{i+1}'] = X_pca[:, i]

print("PCA Results:")
print(f"\nVariance explained by each component:")
for i, var in enumerate(pca.explained_variance_ratio_):
    print(f"  PC{i+1}: {var*100:.1f}%")
print(f"\nCumulative: {pca.explained_variance_ratio_.cumsum()[-1]*100:.1f}%")

# %% PCA Loadings
loadings = pd.DataFrame(
    pca.components_.T,
    index=feature_cols,
    columns=[f'PC{i+1}' for i in range(pca.n_components_)]
)

print("\nPC1 Loadings (primary axis):")
print(loadings['PC1'].sort_values(ascending=False).to_string())

# %% Correlate PCs with Confession
print("\nPC Correlations with Confession:")
for i in range(pca.n_components_):
    r, p = stats.pointbiserialr(df['confess'], df[f'PC{i+1}'])
    print(f"  PC{i+1}: r = {r:+.3f}, p = {p:.2e}")

# %% Figure 2: PCA Loadings - Dimension Collapse
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Panel A: Variance explained
ax1 = axes[0]
components = range(1, len(pca.explained_variance_ratio_) + 1)
ax1.bar(components, pca.explained_variance_ratio_ * 100, color='steelblue', alpha=0.7)
ax1.plot(components, pca.explained_variance_ratio_.cumsum() * 100, 'ro-', linewidth=2, markersize=8)
ax1.set_xlabel('Principal Component')
ax1.set_ylabel('Variance Explained (%)')
ax1.set_title('A: Variance Explained by Each Component')
ax1.set_xticks(components)
ax1.legend(['Cumulative', 'Individual'], loc='center right')

# Panel B: PC1 Loadings
ax2 = axes[1]
pc1_loadings = loadings['PC1'].sort_values()
colors = ['#d62728' if x > 0 else '#2ca02c' for x in pc1_loadings]
ax2.barh(range(len(pc1_loadings)), pc1_loadings.values, color=colors)
ax2.set_yticks(range(len(pc1_loadings)))
ax2.set_yticklabels(pc1_loadings.index)
ax2.axvline(x=0, color='black', linewidth=0.5)
ax2.set_xlabel('Loading on PC1')
ax2.set_title(f'B: PC1 Loadings (explains {pca.explained_variance_ratio_[0]*100:.1f}% variance)')

plt.tight_layout()
plt.savefig(f'{FIGURE_DIR}/fig2_pca_dimension_collapse.png', dpi=150, bbox_inches='tight')
plt.savefig(f'{FIGURE_DIR}/fig2_pca_dimension_collapse.pdf', bbox_inches='tight')
print(f"\nSaved: {FIGURE_DIR}/fig2_pca_dimension_collapse.png")
plt.show()

# %% [markdown]
# ### Key Finding: Dimensions Partially Collapse
# 
# PC1 explains 25% of variance and captures the observer-embodiment axis:
# - Loads positively on: strategic_reasoning, game_theory_explicit, self_interest
# - Loads negatively on: first_person_plural, moral_reasoning, collective_interest
# 
# This single component correlates r = 0.70 with confession, suggesting the three
# theoretical dimensions partially collapse into one primary axis.

# %% [markdown]
# ## Part 5: Refined Scoring System
# 
# Based on empirical validation, we create a refined scoring system using only
# keywords that discriminate in the expected direction, with empirical weights.

# %% Define Refined Marker Lists
STRATEGIC_MARKERS = {
    # Game theory invocation (strongest signals)
    'dominant strategy': 3.0,
    'game theory': 2.0,
    "prisoner's dilemma": 1.5,
    'payoff': 2.0,
    # Self-interest
    'self-interest': 2.0,
    'maximize': 1.5,
    'go free': 1.5,
    # Strategic reasoning
    'regardless of what': 2.0,
    'regardless of': 1.0,
    'even if': 0.5,
}

COOPERATIVE_MARKERS = {
    # First-person PLURAL only
    r'\bwe\b': 1.5,
    r'\bour\b': 1.5,
    r'\bus\b': 1.5,
    # Moral/relational
    'mutual': 2.0,
    'trust': 2.0,
    'cooperat': 2.0,
    'fair': 2.0,
    'harm': 2.5,
    'betray': 1.5,
    # Collective framing
    'both of us': 1.5,
    'neither of us': 1.5,
    'we avoid': 2.0,
}

def count_weighted(text, marker_dict):
    """Count weighted marker occurrences."""
    text_lower = text.lower()
    total = 0.0
    for pattern, weight in marker_dict.items():
        if pattern.startswith(r'\b'):
            matches = len(re.findall(pattern, text, re.IGNORECASE))
        else:
            matches = text_lower.count(pattern)
        total += matches * weight
    return total

def compute_refined_scores(text):
    """Compute refined embodiment scores."""
    strategic = count_weighted(text, STRATEGIC_MARKERS)
    cooperative = count_weighted(text, COOPERATIVE_MARKERS)
    
    # Normalize by text length
    normalizer = max(len(text) / 100.0, 1.0)
    
    return {
        'strategic_refined': strategic / normalizer,
        'cooperative_refined': cooperative / normalizer,
        'embodiment_refined': (cooperative - strategic) / normalizer
    }

# %% Apply Refined Scoring
refined_scores = df['note'].apply(lambda x: pd.Series(compute_refined_scores(x)))
df = pd.concat([df, refined_scores], axis=1)

print("Refined Scoring Results:")
print(f"\nCorrelation with Confession:")
for col in ['strategic_refined', 'cooperative_refined', 'embodiment_refined']:
    r, p = stats.pointbiserialr(df['confess'], df[col])
    print(f"  {col:20s}: r = {r:+.3f}")

# Effect size
confess_emb = df[df['confess'] == 1]['embodiment_refined']
silent_emb = df[df['confess'] == 0]['embodiment_refined']
d = (silent_emb.mean() - confess_emb.mean()) / np.sqrt((confess_emb.var() + silent_emb.var()) / 2)
print(f"\nEffect size (Cohen's d): {d:.2f}")

# Classification accuracy
accuracy = ((df['embodiment_refined'] > 0) == (df['confess'] == 0)).mean()
print(f"Classification accuracy (threshold=0): {accuracy*100:.1f}%")

# %% Figure 3: Embodiment Scores by Choice
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Panel A: Distribution of scores
ax1 = axes[0]
for choice, color, label in [('Confess', '#d62728', 'Confess (Defect)'), 
                              ('Stay Silent', '#2ca02c', 'Stay Silent (Cooperate)')]:
    subset = df[df['choice'] == choice]['embodiment_refined']
    ax1.hist(subset, bins=30, alpha=0.6, color=color, label=label, density=True)

ax1.axvline(x=0, color='black', linewidth=1, linestyle='--')
ax1.set_xlabel('Embodiment Score (Refined)')
ax1.set_ylabel('Density')
ax1.set_title('A: Distribution of Embodiment Scores by Choice')
ax1.legend()

# Panel B: Box plot
ax2 = axes[1]
box_data = [df[df['choice'] == 'Confess']['embodiment_refined'],
            df[df['choice'] == 'Stay Silent']['embodiment_refined']]
bp = ax2.boxplot(box_data, labels=['Confess\n(Observer)', 'Stay Silent\n(Embodied)'],
                  patch_artist=True)
bp['boxes'][0].set_facecolor('#d62728')
bp['boxes'][1].set_facecolor('#2ca02c')
for box in bp['boxes']:
    box.set_alpha(0.6)
ax2.axhline(y=0, color='black', linewidth=1, linestyle='--')
ax2.set_ylabel('Embodiment Score (Refined)')
ax2.set_title(f'B: Embodiment by Choice (Cohen\'s d = {d:.2f})')

plt.tight_layout()
plt.savefig(f'{FIGURE_DIR}/fig3_embodiment_by_choice.png', dpi=150, bbox_inches='tight')
plt.savefig(f'{FIGURE_DIR}/fig3_embodiment_by_choice.pdf', bbox_inches='tight')
print(f"\nSaved: {FIGURE_DIR}/fig3_embodiment_by_choice.png")
plt.show()

# %% [markdown]
# ## Part 6: Prompt-Level Analysis

# %% Aggregate by Prompt
prompt_agg = df.groupby('prompt').agg({
    'confess': 'mean',
    'embodiment_refined': 'mean',
    'strategic_refined': 'mean',
    'cooperative_refined': 'mean',
    'grammatical_score': 'mean',
    'ontological_score': 'mean',
    'reasoning_score': 'mean',
    'idx': 'count'
}).rename(columns={'idx': 'n', 'confess': 'confess_rate'})

prompt_agg = prompt_agg[prompt_agg['n'] >= 10].copy()

r, p = stats.pearsonr(prompt_agg['embodiment_refined'], prompt_agg['confess_rate'])
print(f"Prompt-level correlation (embodiment vs confess rate): r = {r:.3f}, p = {p:.2e}")

# %% Figure 4: Prompt-Level Scatter
fig, ax = plt.subplots(figsize=(10, 7))

scatter = ax.scatter(prompt_agg['embodiment_refined'], prompt_agg['confess_rate'] * 100,
                     s=prompt_agg['n'] * 3, alpha=0.6, c=prompt_agg['confess_rate'],
                     cmap='RdYlGn_r', edgecolors='black', linewidth=0.5)

# Regression line
z = np.polyfit(prompt_agg['embodiment_refined'], prompt_agg['confess_rate'] * 100, 1)
p_line = np.poly1d(z)
x_line = np.linspace(prompt_agg['embodiment_refined'].min(), prompt_agg['embodiment_refined'].max(), 100)
ax.plot(x_line, p_line(x_line), 'k--', linewidth=2, alpha=0.7)

ax.set_xlabel('Mean Embodiment Score')
ax.set_ylabel('Confession Rate (%)')
ax.set_title(f'Figure 4: Prompt-Level Analysis\n(r = {r:.3f}, each point is one prompt condition)')
ax.axhline(y=50, color='gray', linestyle=':', alpha=0.5)
ax.axvline(x=0, color='gray', linestyle=':', alpha=0.5)

# Colorbar
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('Confession Rate')

plt.tight_layout()
plt.savefig(f'{FIGURE_DIR}/fig4_prompt_level_scatter.png', dpi=150, bbox_inches='tight')
plt.savefig(f'{FIGURE_DIR}/fig4_prompt_level_scatter.pdf', bbox_inches='tight')
print(f"\nSaved: {FIGURE_DIR}/fig4_prompt_level_scatter.png")
plt.show()

# %% [markdown]
# ## Part 7: The 2x2 Interaction Table
# 
# Does reasoning mode dominate grammatical perspective?

# %% Create 2x2 Categories
df['perspective_cat'] = pd.cut(df['grammatical_score'], bins=[-np.inf, 0, np.inf],
                                labels=['Third-person/Impersonal', 'First-person'])
df['reasoning_cat'] = pd.cut(df['reasoning_score'], bins=[-np.inf, 0, np.inf],
                              labels=['Strategic', 'Moral/Relational'])

# Pivot table
pivot = df.pivot_table(values='confess', index='perspective_cat', columns='reasoning_cat',
                       aggfunc=['mean', 'count'])

print("\n" + "="*70)
print("2x2 TABLE: Confession Rate by Perspective × Reasoning Mode")
print("="*70)

print("\nConfession Rate:")
print(f"{'':30s} Strategic    Moral/Relational")
print(f"{'Third-person/Impersonal':30s} {pivot[('mean', 'Strategic')].iloc[0]*100:5.1f}%       {pivot[('mean', 'Moral/Relational')].iloc[0]*100:5.1f}%")
print(f"{'First-person':30s} {pivot[('mean', 'Strategic')].iloc[1]*100:5.1f}%       {pivot[('mean', 'Moral/Relational')].iloc[1]*100:5.1f}%")

print("\nSample Sizes:")
print(f"{'':30s} Strategic    Moral/Relational")
print(f"{'Third-person/Impersonal':30s} {int(pivot[('count', 'Strategic')].iloc[0]):5d}        {int(pivot[('count', 'Moral/Relational')].iloc[0]):5d}")
print(f"{'First-person':30s} {int(pivot[('count', 'Strategic')].iloc[1]):5d}        {int(pivot[('count', 'Moral/Relational')].iloc[1]):5d}")

# %% Figure 5: 2x2 Heatmap
fig, ax = plt.subplots(figsize=(8, 6))

# Create matrix for heatmap
heatmap_data = pivot['mean'] * 100
heatmap_data = heatmap_data.reindex(['First-person', 'Third-person/Impersonal'])

sns.heatmap(heatmap_data, annot=True, fmt='.1f', cmap='RdYlGn_r', 
            ax=ax, cbar_kws={'label': 'Confession Rate (%)'},
            linewidths=2, linecolor='white',
            vmin=0, vmax=100)

ax.set_xlabel('Reasoning Mode')
ax.set_ylabel('Grammatical Perspective')
ax.set_title('Figure 5: Confession Rate by Perspective × Reasoning Mode\n(Reasoning mode dominates: 70.1% vs 4.9% for third-person)')

plt.tight_layout()
plt.savefig(f'{FIGURE_DIR}/fig5_2x2_heatmap.png', dpi=150, bbox_inches='tight')
plt.savefig(f'{FIGURE_DIR}/fig5_2x2_heatmap.pdf', bbox_inches='tight')
print(f"\nSaved: {FIGURE_DIR}/fig5_2x2_heatmap.png")
plt.show()

# %% [markdown]
# ## Part 8: Inter-Dimension Correlations

# %% Figure 6: Dimension Correlation Matrix
fig, ax = plt.subplots(figsize=(8, 6))

dim_cols = ['grammatical_score', 'ontological_score', 'reasoning_score', 'embodiment_refined']
dim_labels = ['Grammatical', 'Ontological', 'Reasoning', 'Embodiment\n(Refined)']

corr_matrix = df[dim_cols].corr()
corr_matrix.index = dim_labels
corr_matrix.columns = dim_labels

sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0,
            ax=ax, square=True, linewidths=1, linecolor='white',
            vmin=-1, vmax=1)

ax.set_title('Figure 6: Inter-Dimension Correlations')

plt.tight_layout()
plt.savefig(f'{FIGURE_DIR}/fig6_dimension_correlations.png', dpi=150, bbox_inches='tight')
plt.savefig(f'{FIGURE_DIR}/fig6_dimension_correlations.pdf', bbox_inches='tight')
print(f"\nSaved: {FIGURE_DIR}/fig6_dimension_correlations.png")
plt.show()

# %% [markdown]
# ## Summary Statistics for Paper

# %% Print Summary
print("\n" + "="*70)
print("SUMMARY STATISTICS FOR PAPER")
print("="*70)

print(f"\nDataset:")
print(f"  Total trials: {len(df)}")
print(f"  Unique prompts: {df['prompt'].nunique()}")
print(f"  Confession rate: {df['confess'].mean()*100:.1f}%")

print(f"\nInitial Three-Dimension Framework:")
for col in ['grammatical_score', 'ontological_score', 'reasoning_score', 'embodiment_initial']:
    r, _ = stats.pointbiserialr(df['confess'], df[col])
    print(f"  {col}: r = {r:+.3f} with confession")

print(f"\nRefined Scoring:")
r, _ = stats.pointbiserialr(df['confess'], df['embodiment_refined'])
print(f"  Correlation with confession: r = {r:.3f}")
print(f"  Effect size (Cohen's d): {d:.2f}")
print(f"  Classification accuracy: {accuracy*100:.1f}%")
print(f"  Prompt-level r: {stats.pearsonr(prompt_agg['embodiment_refined'], prompt_agg['confess_rate'])[0]:.3f}")

print(f"\nPCA Results:")
print(f"  PC1 variance explained: {pca.explained_variance_ratio_[0]*100:.1f}%")
r_pc1, _ = stats.pointbiserialr(df['confess'], df['PC1'])
print(f"  PC1 correlation with confession: r = {r_pc1:.3f}")

print(f"\n2x2 Table (Perspective × Reasoning):")
print(f"  Third-person + Strategic: {pivot[('mean', 'Strategic')].iloc[0]*100:.1f}% confess")
print(f"  Third-person + Moral: {pivot[('mean', 'Moral/Relational')].iloc[0]*100:.1f}% confess")
print(f"  First-person + Strategic: {pivot[('mean', 'Strategic')].iloc[1]*100:.1f}% confess")
print(f"  First-person + Moral: {pivot[('mean', 'Moral/Relational')].iloc[1]*100:.1f}% confess")

# %% Save Results
df.to_csv(f'{FIGURE_DIR}/full_analysis_results.csv', index=False)
prompt_agg.to_csv(f'{FIGURE_DIR}/prompt_level_results.csv')
validation_df.to_csv(f'{FIGURE_DIR}/keyword_validation.csv', index=False)

print(f"\nResults saved to {FIGURE_DIR}/")
print("  - full_analysis_results.csv")
print("  - prompt_level_results.csv") 
print("  - keyword_validation.csv")

# %% List all figures
print(f"\nFigures saved to {FIGURE_DIR}/:")
for f in sorted(os.listdir(FIGURE_DIR)):
    if f.endswith('.png') or f.endswith('.pdf'):
        print(f"  - {f}")
