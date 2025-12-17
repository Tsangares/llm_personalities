"""
Unified analysis and visualization for LLM game theory experiments.

This script loads simulation results, computes statistics, generates visualizations,
and produces summary reports.

Usage:
    python src/analyze.py                    # Analyze all games
    python src/analyze.py dictator           # Analyze specific game
    python src/analyze.py --summary-only     # Generate summary figure only
"""

import csv
import os
import sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
from collections import Counter


OUTPUT_DIR = Path("output")

NASH_EQUILIBRIA = {
    'DictatorGame': {'theory': 0, 'experimental': 30},
    'UltimatumGame': {'proposer_theory': 0.01, 'proposer_experimental': 40, 'responder_threshold': 30},
    'PrisonerDilemma': {'nash': 'D', 'optimal': 'C'},
    'PublicGoodsGame': {'nash': 0, 'optimal': 100},
    'TrustGame': {'investor_nash': 0, 'investor_experimental': 50, 'trustee_return': 0.3},
    'VolunteerDilemma': {'mixed': 0.5}
}


# ============================================================================
# DATA LOADING
# ============================================================================

def load_csv(filename):
    """Load CSV data from output directory."""
    filepath = OUTPUT_DIR / filename
    if not filepath.exists():
        print(f"File not found: {filepath}")
        return []

    with open(filepath, 'r') as f:
        return list(csv.DictReader(f))


# ============================================================================
# STATISTICAL ANALYSIS
# ============================================================================

def analyze_dictator():
    """Analyze Dictator Game results."""
    df = pd.read_csv(OUTPUT_DIR / "dictator_simulation.csv")
    decisions = df['decision'].values

    print("DICTATOR GAME (n=500)")
    print("-" * 40)
    print(f"Mean amount given:    ${decisions.mean():.2f} (Nash: $0)")
    print(f"Median amount given:  ${np.median(decisions):.2f}")
    print(f"Std deviation:        ${decisions.std():.2f}")
    print(f"Min/Max:              ${decisions.min():.2f} / ${decisions.max():.2f}")
    print(f"% giving ≥ 50:        {(decisions >= 50).sum() / len(decisions) * 100:.1f}%")
    print(f"% giving exactly 50:  {(decisions == 50).sum() / len(decisions) * 100:.1f}%")
    print()


def analyze_prisoner():
    """Analyze Prisoner's Dilemma results."""
    df = pd.read_csv(OUTPUT_DIR / "prisoner_simulation.csv")
    df_coop = df[df['decision'].isin(['C', 'COOPERATE'])]
    coop_rate = len(df_coop) / len(df) * 100

    print("PRISONER'S DILEMMA (n=1000)")
    print("-" * 40)
    print(f"Cooperation rate:     {coop_rate:.1f}% (Nash: 0%)")
    print(f"Mean payoff:          {df['payoff'].mean():.2f} (Nash: 1, Max: 3)")
    print(f"Defection rate:       {100-coop_rate:.1f}%")
    print()


def analyze_ultimatum():
    """Analyze Ultimatum Game results."""
    df = pd.read_csv(OUTPUT_DIR / "ultimatum_simulation.csv")
    df_prop = df[df['role'] == 'Proposer']
    df_resp = df[df['role'] == 'Responder']

    proposals = df_prop['decision'].values
    rejections = (df_prop['payoff'] == 0).sum()
    rejection_rate = rejections / len(df_prop) * 100
    thresholds = df_resp['decision'].values

    print("ULTIMATUM GAME (n=1000)")
    print("-" * 40)
    print("PROPOSER:")
    print(f"  Mean offer:         {proposals.mean():.2f} (Nash: minimal)")
    print(f"  Median offer:       {np.median(proposals):.2f}")
    print(f"  % offering ≥ 50:    {(proposals >= 50).sum() / len(proposals) * 100:.1f}%")
    print(f"  Rejection rate:     {rejection_rate:.1f}%")
    print("RESPONDER:")
    print(f"  Mean threshold:     {thresholds.mean():.2f}")
    print(f"  Median threshold:   {np.median(thresholds):.2f}")
    print()


def analyze_trust():
    """Analyze Trust Game results."""
    df = pd.read_csv(OUTPUT_DIR / "trust_simulation.csv")
    df_inv = df[df['role'] == 'Investor']
    df_tru = df[df['role'] == 'Trustee']

    investor_send = df_inv['decision'].values
    trustee_return = df_tru['decision'].values

    print("TRUST GAME (n=1000)")
    print("-" * 40)
    print("INVESTOR:")
    print(f"  Mean sent:          {investor_send.mean():.2%} (Nash: 0%)")
    print(f"  Median sent:        {np.median(investor_send):.2%}")
    print(f"  % sending > 0:      {(investor_send > 0).sum() / len(investor_send) * 100:.1f}%")
    print("TRUSTEE:")
    print(f"  Mean return %:      {trustee_return.mean():.2%} (Nash: 0%)")
    print(f"  Median return:      {np.median(trustee_return):.2%}")
    print()


def analyze_public_good():
    """Analyze Public Goods Game results."""
    df = pd.read_csv(OUTPUT_DIR / "public_good_simulation.csv")
    decisions = df['decision'].values

    print("PUBLIC GOODS GAME")
    print("-" * 40)
    print(f"Mean contribution:    {decisions.mean():.2f} (Nash: 0, Optimal: 100)")
    print(f"Median contribution:  {np.median(decisions):.2f}")
    print()


def analyze_volunteer():
    """Analyze Volunteer's Dilemma results."""
    df = pd.read_csv(OUTPUT_DIR / "volunteer_simulation.csv")
    decisions = df['decision'].apply(lambda x: str(x).lower() == 'true')
    volunteer_rate = decisions.sum() / len(decisions)

    print("VOLUNTEER'S DILEMMA")
    print("-" * 40)
    print(f"Volunteer rate:       {volunteer_rate:.1%} (Nash: ~50%)")
    print()


def print_summary():
    """Print overall summary of findings."""
    print("=" * 80)
    print("KEY FINDINGS")
    print("=" * 80)
    print()
    print("1. PROSOCIAL BIAS:")
    print("   LLM exhibits strong prosocial preferences exceeding Nash predictions")
    print("   - Dictator: ~44% average giving vs Nash 0%")
    print("   - Prisoner: ~100% cooperation vs Nash 0%")
    print("   - Trust: High reciprocity despite no enforcement")
    print()
    print("2. FAIRNESS NORM:")
    print("   Strong preference for 50-50 splits across games")
    print()
    print("3. STRATEGIC REASONING:")
    print("   Model shows limited strategic thinking")
    print("   - No exploitation in Prisoner's Dilemma")
    print("   - Low rejection rates in Ultimatum")
    print()
    print("4. IMPLICATIONS:")
    print("   - LLMs may not replicate human strategic behavior")
    print("   - Training bias toward cooperation/fairness")
    print("   - Useful for prosocial applications, limited for strategic modeling")
    print()
    print("=" * 80)


# ============================================================================
# VISUALIZATION
# ============================================================================

def plot_dictator(data):
    """Create histogram for Dictator Game."""
    decisions = [float(row['decision']) for row in data if row['role'] == 'Dictator']

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(decisions, bins=20, alpha=0.7, edgecolor='black')
    ax.axvline(0, color='red', linestyle='--', label='Nash Eq. (0)', linewidth=2)
    ax.axvline(30, color='green', linestyle='--', label='Experimental (~30)', linewidth=2)
    ax.set_xlabel('Amount Given')
    ax.set_ylabel('Frequency')
    ax.set_title(f'Dictator Game Decisions (n={len(decisions)})')
    ax.legend()
    ax.grid(alpha=0.3)

    return fig


def plot_prisoner(data):
    """Create bar chart for Prisoner's Dilemma."""
    decisions = [row['decision'] for row in data]
    counts = Counter(decisions)

    fig, ax = plt.subplots(figsize=(8, 6))
    labels = list(counts.keys())
    values = list(counts.values())
    colors = ['green' if x == 'C' else 'red' for x in labels]

    ax.bar(labels, values, color=colors, alpha=0.7, edgecolor='black')
    ax.set_xlabel('Decision')
    ax.set_ylabel('Frequency')
    ax.set_title(f'Prisoner\'s Dilemma Decisions (n={len(decisions)})')
    ax.text(0.5, 0.95, 'Nash Eq: D-D | Optimal: C-C',
            transform=ax.transAxes, ha='center', va='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    ax.grid(alpha=0.3, axis='y')

    return fig


def plot_ultimatum(data):
    """Create dual histogram for Ultimatum Game."""
    proposer_decisions = [float(row['decision']) for row in data if row['role'] == 'Proposer']
    responder_decisions = [float(row['decision']) for row in data if row['role'] == 'Responder']

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    ax1.hist(proposer_decisions, bins=15, alpha=0.7, edgecolor='black', color='blue')
    ax1.axvline(40, color='green', linestyle='--', label='Experimental (~40)', linewidth=2)
    ax1.set_xlabel('Offer Amount')
    ax1.set_ylabel('Frequency')
    ax1.set_title(f'Proposer Offers (n={len(proposer_decisions)})')
    ax1.legend()
    ax1.grid(alpha=0.3)

    ax2.hist(responder_decisions, bins=15, alpha=0.7, edgecolor='black', color='orange')
    ax2.axvline(30, color='red', linestyle='--', label='Typical threshold (~30)', linewidth=2)
    ax2.set_xlabel('Minimum Acceptable Offer')
    ax2.set_ylabel('Frequency')
    ax2.set_title(f'Responder Thresholds (n={len(responder_decisions)})')
    ax2.legend()
    ax2.grid(alpha=0.3)

    fig.tight_layout()
    return fig


def plot_trust(data):
    """Create dual histogram for Trust Game."""
    investor_decisions = [float(row['decision']) for row in data if row['role'] == 'Investor']
    trustee_decisions = [float(row['decision']) for row in data if row['role'] == 'Trustee']

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    ax1.hist(investor_decisions, bins=15, alpha=0.7, edgecolor='black', color='blue')
    ax1.axvline(0, color='red', linestyle='--', label='Nash Eq. (0)', linewidth=2)
    ax1.axvline(0.5, color='green', linestyle='--', label='Experimental (~50%)', linewidth=2)
    ax1.set_xlabel('Amount Sent (fraction)')
    ax1.set_ylabel('Frequency')
    ax1.set_title(f'Investor Decisions (n={len(investor_decisions)})')
    ax1.legend()
    ax1.grid(alpha=0.3)

    ax2.hist(trustee_decisions, bins=15, alpha=0.7, edgecolor='black', color='orange')
    ax2.axvline(0.3, color='green', linestyle='--', label='Typical return (~0.3)', linewidth=2)
    ax2.set_xlabel('Fraction Returned')
    ax2.set_ylabel('Frequency')
    ax2.set_title(f'Trustee Returns (n={len(trustee_decisions)})')
    ax2.legend()
    ax2.grid(alpha=0.3)

    fig.tight_layout()
    return fig


def plot_public_good(data):
    """Create histogram for Public Goods Game."""
    decisions = [float(row['decision']) for row in data]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(decisions, bins=20, alpha=0.7, edgecolor='black')
    ax.axvline(0, color='red', linestyle='--', label='Nash Eq. (0)', linewidth=2)
    ax.axvline(100, color='green', linestyle='--', label='Optimal (100)', linewidth=2)
    ax.set_xlabel('Contribution Amount')
    ax.set_ylabel('Frequency')
    ax.set_title(f'Public Goods Game Contributions (n={len(decisions)})')
    ax.legend()
    ax.grid(alpha=0.3)

    return fig


def plot_volunteer(data):
    """Create bar chart for Volunteer's Dilemma."""
    decisions = [row['decision'] == 'True' for row in data]
    volunteer_rate = sum(decisions) / len(decisions) if decisions else 0

    fig, ax = plt.subplots(figsize=(8, 6))
    labels = ['Volunteer', 'Don\'t Volunteer']
    values = [sum(decisions), len(decisions) - sum(decisions)]
    colors = ['green', 'red']

    ax.bar(labels, values, color=colors, alpha=0.7, edgecolor='black')
    ax.axhline(len(decisions) * 0.5, color='blue', linestyle='--',
               label=f'Mixed Nash (~50%)', linewidth=2)
    ax.set_ylabel('Frequency')
    ax.set_title(f'Volunteer Dilemma Decisions (Rate: {volunteer_rate:.1%}, n={len(decisions)})')
    ax.legend()
    ax.grid(alpha=0.3, axis='y')

    return fig


def generate_summary_figure():
    """Generate comprehensive 6-panel summary visualization."""
    import matplotlib
    matplotlib.rcParams['text.usetex'] = False
    matplotlib.rcParams['text.parse_math'] = False

    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('LLM Game Theory Behavior - 500 Round Study (mistral:7b)',
                 fontsize=16, fontweight='bold')

    # 1. Dictator Game
    ax = axes[0, 0]
    df = pd.read_csv(OUTPUT_DIR / "dictator_simulation.csv")
    decisions = df['decision'].values
    ax.hist(decisions, bins=30, alpha=0.7, color='steelblue', edgecolor='black')
    ax.axvline(decisions.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: ${decisions.mean():.1f}')
    ax.axvline(0, color='orange', linestyle=':', linewidth=2, label='Nash: $0')
    ax.set_xlabel('Amount Given ($)', fontsize=10)
    ax.set_ylabel('Frequency', fontsize=10)
    ax.set_title('Dictator Game\nMean: $43.63 | 73% give ≥$50', fontsize=12, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(axis='y', alpha=0.3)

    # 2. Prisoner's Dilemma
    ax = axes[0, 1]
    df = pd.read_csv(OUTPUT_DIR / "prisoner_simulation.csv")
    coop = df[df['decision'].isin(['C', 'COOPERATE'])].shape[0]
    defect = df[~df['decision'].isin(['C', 'COOPERATE'])].shape[0]
    ax.bar(['Cooperate', 'Defect'], [coop, defect], color=['green', 'red'], alpha=0.7, edgecolor='black')
    ax.set_ylabel('Count', fontsize=10)
    ax.set_title(f'Prisoner\'s Dilemma\n{coop/len(df)*100:.1f}% Cooperation (Nash: 0%)', fontsize=12, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)

    # 3. Ultimatum Game
    ax = axes[0, 2]
    df = pd.read_csv(OUTPUT_DIR / "ultimatum_simulation.csv")
    df_prop = df[df['role'] == 'Proposer']
    proposals = df_prop['decision'].values
    ax.hist(proposals, bins=30, alpha=0.7, color='purple', edgecolor='black')
    ax.axvline(proposals.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {proposals.mean():.1f}')
    ax.set_xlabel('Offer Amount', fontsize=10)
    ax.set_ylabel('Frequency', fontsize=10)
    ax.set_title(f'Ultimatum (Proposer)\nMean: {proposals.mean():.1f} | {(df_prop["payoff"]==0).sum()/len(df_prop)*100:.1f}% rejected',
                 fontsize=12, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(axis='y', alpha=0.3)

    # 4. Trust Game (Investor)
    ax = axes[1, 0]
    df = pd.read_csv(OUTPUT_DIR / "trust_simulation.csv")
    df_inv = df[df['role'] == 'Investor']
    sent = df_inv['decision'].values
    ax.hist(sent, bins=30, alpha=0.7, color='teal', edgecolor='black')
    ax.axvline(sent.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {sent.mean():.2f}')
    ax.axvline(0, color='orange', linestyle=':', linewidth=2, label='Nash: 0')
    ax.set_xlabel('Fraction Sent', fontsize=10)
    ax.set_ylabel('Frequency', fontsize=10)
    ax.set_title(f'Trust Game (Investor)\nMean: {sent.mean():.1%} sent | 100% trust', fontsize=12, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(axis='y', alpha=0.3)

    # 5. Trust Game (Trustee)
    ax = axes[1, 1]
    df_tru = df[df['role'] == 'Trustee']
    returned = df_tru['decision'].values
    ax.hist(returned, bins=30, alpha=0.7, color='darkcyan', edgecolor='black')
    ax.axvline(returned.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {returned.mean():.2f}')
    ax.axvline(0, color='orange', linestyle=':', linewidth=2, label='Nash: 0')
    ax.set_xlabel('Fraction Returned', fontsize=10)
    ax.set_ylabel('Frequency', fontsize=10)
    ax.set_title(f'Trust Game (Trustee)\nMean: {returned.mean():.1%} returned', fontsize=12, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(axis='y', alpha=0.3)

    # 6. Summary Statistics
    ax = axes[1, 2]
    ax.axis('off')
    summary_text = """
KEY FINDINGS

Prosocial Bias:
• 100% cooperation in Prisoner's
• 73% give ≥$50 in Dictator
• 100% send money in Trust

Fairness Norms:
• 47% give exactly $50 (Dictator)
• Median threshold: $50 (Ultimatum)
• Modal splits favor equality

Strategic Reasoning:
• Zero exploitation observed
• No Nash equilibrium play
• Training bias dominates

Implications:
• Unsuitable for strategic modeling
• Useful for prosocial AI design
• Reflects cooperative training data
"""
    ax.text(0.05, 0.95, summary_text, transform=ax.transAxes,
            fontsize=10, verticalalignment='top', family='monospace',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

    plt.tight_layout()
    output_path = OUTPUT_DIR / 'summary_analysis.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Summary visualization saved to: {output_path}")
    plt.close(fig)


def visualize_game(game_name):
    """Generate visualization for a specific game."""
    filename = f"{game_name}_simulation.csv"
    data = load_csv(filename)

    if not data:
        return

    game_type = data[0]['game']

    plot_funcs = {
        'DictatorGame': plot_dictator,
        'PrisonerDilemma': plot_prisoner,
        'UltimatumGame': plot_ultimatum,
        'TrustGame': plot_trust,
        'PublicGoodsGame': plot_public_good,
        'VolunteerDilemma': plot_volunteer,
    }

    if game_type in plot_funcs:
        fig = plot_funcs[game_type](data)
        output_file = OUTPUT_DIR / f"{game_name}_plot.png"
        fig.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Saved plot to {output_file}")
        plt.close(fig)
    else:
        print(f"No visualization available for {game_type}")


# ============================================================================
# MAIN INTERFACE
# ============================================================================

def main():
    """Main analysis interface."""
    if len(sys.argv) > 1:
        arg = sys.argv[1]

        if arg == '--summary-only':
            generate_summary_figure()
            return

        # Analyze specific game
        game_name = arg
        print(f"\nAnalyzing {game_name}...")
        print("=" * 80)

        if game_name == 'dictator':
            analyze_dictator()
            visualize_game(game_name)
        elif game_name == 'prisoner':
            analyze_prisoner()
            visualize_game(game_name)
        elif game_name == 'ultimatum':
            analyze_ultimatum()
            visualize_game(game_name)
        elif game_name == 'trust':
            analyze_trust()
            visualize_game(game_name)
        elif game_name == 'public_good':
            analyze_public_good()
            visualize_game(game_name)
        elif game_name == 'volunteer':
            analyze_volunteer()
            visualize_game(game_name)
        else:
            print(f"Unknown game: {game_name}")
            print("Available: dictator, prisoner, ultimatum, trust, public_good, volunteer")
    else:
        # Analyze all games
        print("=" * 80)
        print("LLM GAME THEORY BEHAVIOR ANALYSIS - 500 ROUND STUDY")
        print("Model: mistral:7b via Ollama")
        print("=" * 80)
        print()

        analyze_dictator()
        analyze_prisoner()
        analyze_ultimatum()
        analyze_trust()
        analyze_public_good()
        analyze_volunteer()

        print_summary()

        print("\nGenerating visualizations...")
        for game in ['dictator', 'prisoner', 'ultimatum', 'trust', 'public_good', 'volunteer']:
            visualize_game(game)

        generate_summary_figure()

        print("\nAnalysis complete!")


if __name__ == "__main__":
    main()
