"""
Comprehensive Prompt Quantification for Agent Mode Analysis

This script evaluates system prompts on two critical dimensions:
1. MODE: Observer (meta-analytical) vs Agent (situated decision-making)
2. NEUTRALITY: Behavioral bias toward cooperation or defection

The goal is to identify prompts that induce agent mode while remaining
behaviorally neutral, allowing demographic traits to modulate responses.

Author: Wil (Claremont Graduate University)
For: Dissertation on LLM behavioral impacts
"""

import pandas as pd
import numpy as np
import re
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')


class ReasoningModeClassifier:
    """
    Multi-dimensional classifier for observer vs agent mode reasoning.
    
    Based on linguistic markers in reasoning notes, scores each note along
    6 dimensions (3 observer markers, 3 agent markers).
    """
    
    def __init__(self):
        # Observer Mode Markers
        self.game_theory_terms = [
            r"prisoner'?s? dilemma",
            r"nash equilibrium", 
            r"game theory",
            r"dominant strategy",
            r"payoff matrix",
            r"rational choice theory",
            r"optimal strategy",
            r"zero-sum",
            r"pareto",
            r"strategic equilibrium",
        ]
        
        self.optimization_terms = [
            r"maximize\s+(?:personal\s+)?(?:benefit|outcome|utility|advantage)",
            r"minimize\s+(?:personal\s+)?(?:risk|penalty|punishment|cost)",
            r"optimal\s+(?:choice|decision|outcome|solution)",
            r"rational\s+(?:choice|decision|strategy|actor)",
            r"strategic\s+(?:advantage|standpoint|perspective|analysis)",
            r"dominant\s+strategy",
            r"better\s+outcome\s+for\s+you(?:rself)?",
            r"self-interested?\s+perspective",
        ]
        
        self.abstract_terms = [
            r"from\s+a\s+(?:purely\s+)?(?:self-interested|strategic|rational)\s+perspective",
            r"given\s+the\s+scenario",
            r"in\s+the\s+context\s+of",
            r"based\s+on\s+(?:the\s+)?(?:given|potential)\s+outcomes?",
            r"regardless\s+of\s+what\s+(?:your|the)\s+accomplice",
            r"individual\s+perspective",
            r"according\s+to\s+game\s+theory",
            r"theoretical\s+(?:framework|analysis)",
        ]
        
        # Agent Mode Markers
        self.agent_terms = [
            r"\bwe\b",
            r"\bour\b",
            r"\bus\b",
            r"both\s+of\s+us",
            r"between\s+(?:the\s+two\s+of\s+)?us",
            r"my\s+accomplice\s+and\s+(?:I|me)",
            r"together\b",
            r"each\s+other",
        ]
        
        self.social_terms = [
            r"mutual\s+(?:trust|cooperation|benefit|understanding|respect)",
            r"trust\s+(?:in|between|with|each\s+other)",
            r"cooperat(?:e|ion|ive|ing)",
            r"collective\s+(?:outcome|benefit|good)",
            r"relationship",
            r"faith\s+in",
            r"work\s+together",
            r"partnering",
        ]
        
        self.immediacy_terms = [
            r"avoid\s+the\s+risk",
            r"safer\s+(?:option|choice|bet)",
            r"requires?\s+(?:mutual\s+)?(?:trust|understanding)",
            r"assume\s+(?:the\s+other|accomplice)",
            r"if\s+(?:we|both)\s+(?:stay|choose)",
            r"better\s+for\s+(?:both|everyone)",
            r"in\s+(?:this|my)\s+(?:situation|position)",
            r"right\s+now",
        ]
    
    def count_pattern_matches(self, text: str, patterns: List[str]) -> int:
        """Count unique pattern matches in text."""
        if pd.isna(text):
            return 0
        text_lower = text.lower()
        return sum(1 for pattern in patterns if re.search(pattern, text_lower))
    
    def classify_note(self, note: str) -> Dict:
        """Classify a single reasoning note along all dimensions."""
        if pd.isna(note):
            return self._empty_classification()
        
        scores = {
            # Observer markers (meta-analytical reasoning)
            'game_theory_lang': self.count_pattern_matches(note, self.game_theory_terms),
            'optimization_lang': self.count_pattern_matches(note, self.optimization_terms),
            'abstract_framing': self.count_pattern_matches(note, self.abstract_terms),
            
            # Agent markers (situated reasoning)
            'agent_language': self.count_pattern_matches(note, self.agent_terms),
            'social_reasoning': self.count_pattern_matches(note, self.social_terms),
            'immediacy_framing': self.count_pattern_matches(note, self.immediacy_terms),
        }
        
        # Composite scores (weighted by importance)
        scores['observer_score'] = (
            scores['game_theory_lang'] * 3 +      # Game theory = strong observer signal
            scores['optimization_lang'] * 2 +     # Optimization = moderate signal
            scores['abstract_framing'] * 1        # Abstraction = weak signal
        )
        
        scores['agent_score'] = (
            scores['agent_language'] * 2 +        # "We/us" = strong agent signal
            scores['social_reasoning'] * 2 +      # Trust/cooperation = strong signal
            scores['immediacy_framing'] * 1       # Situational = moderate signal
        )
        
        # Classification
        total = scores['observer_score'] + scores['agent_score']
        if total == 0:
            scores['mode'] = 'neutral'
            scores['confidence'] = 0.0
        elif scores['observer_score'] > scores['agent_score']:
            scores['mode'] = 'observer'
            scores['confidence'] = scores['observer_score'] / total
        else:
            scores['mode'] = 'agent'
            scores['confidence'] = scores['agent_score'] / total
        
        # Critical validity check
        scores['has_game_theory'] = scores['game_theory_lang'] > 0
        
        return scores
    
    def _empty_classification(self) -> Dict:
        """Return empty classification for missing notes."""
        return {
            'game_theory_lang': 0, 'optimization_lang': 0, 'abstract_framing': 0,
            'agent_language': 0, 'social_reasoning': 0, 'immediacy_framing': 0,
            'observer_score': 0, 'agent_score': 0,
            'mode': 'missing', 'confidence': 0.0, 'has_game_theory': False
        }


class PromptQuantifier:
    """
    Comprehensive quantification of system prompts for agent mode induction
    and behavioral neutrality.
    """
    
    def __init__(self, notes_df: pd.DataFrame, results_df: pd.DataFrame = None):
        """
        Initialize with reasoning notes and optional behavioral results.
        
        Args:
            notes_df: DataFrame with columns ['choice', 'note', 'prompt']
            results_df: DataFrame with behavioral outcomes by prompt
        """
        self.notes_df = notes_df.copy()
        self.results_df = results_df.copy() if results_df is not None else None
        self.classifier = ReasoningModeClassifier()
        self.classified_df = None
        self.metrics_df = None
    
    def classify_all_notes(self):
        """Classify all reasoning notes and store results."""
        print("Classifying reasoning notes...")
        
        classifications = []
        for idx, row in self.notes_df.iterrows():
            result = self.classifier.classify_note(row['note'])
            result['original_index'] = idx
            classifications.append(result)
        
        class_df = pd.DataFrame(classifications)
        
        # Merge with original data
        self.classified_df = self.notes_df.copy()
        for col in class_df.columns:
            if col != 'original_index':
                self.classified_df[col] = class_df[col].values
        
        print(f"✓ Classified {len(self.classified_df)} notes")
        return self.classified_df
    
    def compute_prompt_metrics(self) -> pd.DataFrame:
        """
        Compute comprehensive metrics for each prompt.
        
        Returns DataFrame with columns:
        - prompt: The system prompt text
        - n_samples: Number of reasoning notes
        - mode_pct_observer: % classified as observer mode
        - mode_pct_agent: % classified as agent mode
        - mode_pct_neutral: % classified as neutral
        - game_theory_contamination: % with game theory language
        - mean_observer_score: Average observer score
        - mean_agent_score: Average agent score
        - agent_dominance: Agent score minus observer score (positive = more agent)
        - behavior_*: Behavioral metrics (if results_df provided)
        """
        if self.classified_df is None:
            self.classify_all_notes()
        
        # Group by prompt
        grouped = self.classified_df.groupby('prompt')
        
        metrics = []
        for prompt, group in grouped:
            # Mode distribution
            mode_dist = group['mode'].value_counts(normalize=True)
            
            metric = {
                'prompt': prompt,
                'n_samples': len(group),
                
                # Mode percentages
                'mode_pct_observer': mode_dist.get('observer', 0) * 100,
                'mode_pct_agent': mode_dist.get('agent', 0) * 100,
                'mode_pct_neutral': mode_dist.get('neutral', 0) * 100,
                
                # Contamination check
                'game_theory_contamination': (group['has_game_theory'].sum() / len(group)) * 100,
                
                # Average scores
                'mean_observer_score': group['observer_score'].mean(),
                'mean_agent_score': group['agent_score'].mean(),
                'std_observer_score': group['observer_score'].std(),
                'std_agent_score': group['agent_score'].std(),
                
                # Dominance metric (positive = agent, negative = observer)
                'agent_dominance': group['agent_score'].mean() - group['observer_score'].mean(),
                
                # Dimensional breakdown
                'mean_game_theory': group['game_theory_lang'].mean(),
                'mean_optimization': group['optimization_lang'].mean(),
                'mean_abstract': group['abstract_framing'].mean(),
                'mean_agent_lang': group['agent_language'].mean(),
                'mean_social': group['social_reasoning'].mean(),
                'mean_immediacy': group['immediacy_framing'].mean(),
            }
            
            # Add behavioral metrics if available
            if self.results_df is not None:
                behavior = self.results_df[self.results_df['Prompt'] == prompt]
                if not behavior.empty:
                    row = behavior.iloc[0]
                    metric['behavior_confess_pct'] = row['confess']
                    metric['behavior_silent_pct'] = row['silent']
                    metric['behavior_margin'] = row['margin']
                    
                    # Neutrality metric: distance from 50/50
                    metric['behavior_bias'] = abs(50 - row['confess'])
                    
                    # Combined quality score (explained below)
                    metric['quality_score'] = self._compute_quality_score(
                        metric['agent_dominance'],
                        metric['game_theory_contamination'],
                        metric['behavior_bias'],
                        metric['behavior_margin']
                    )
            
            metrics.append(metric)
        
        self.metrics_df = pd.DataFrame(metrics)
        return self.metrics_df
    
    def _compute_quality_score(self, agent_dom: float, contamination: float, 
                               bias: float, margin: float) -> float:
        """
        Compute overall prompt quality score.
        
        Quality = Agent Mode + Neutrality + Diversity
        
        Components:
        1. Agent dominance (want positive, high)
        2. Low game theory contamination (want near 0)
        3. Low behavioral bias (want near 0)
        4. High margin/entropy (want high diversity)
        
        Score range: 0-100 (higher = better)
        """
        # Normalize each component to 0-100 scale
        
        # Agent mode score (scale: -10 to +10 → 0 to 100)
        agent_component = min(100, max(0, (agent_dom + 10) * 5))
        
        # Purity score (inverse of contamination: 100% contamination = 0, 0% = 100)
        purity_component = 100 - contamination
        
        # Neutrality score (distance from 50: 0 bias = 100, 50 bias = 0)
        neutrality_component = 100 - (bias * 2)
        
        # Diversity score (margin: typically 0-5, scale to 0-100)
        diversity_component = min(100, margin * 20)
        
        # Weighted combination
        quality = (
            agent_component * 0.35 +      # 35% weight on agent mode
            purity_component * 0.30 +     # 30% weight on no game theory
            neutrality_component * 0.25 + # 25% weight on behavioral neutrality
            diversity_component * 0.10    # 10% weight on response diversity
        )
        
        return quality
    
    def rank_prompts(self, by: str = 'quality_score', top_n: int = 10) -> pd.DataFrame:
        """
        Rank prompts by specified metric.
        
        Args:
            by: Column to rank by ('quality_score', 'agent_dominance', etc.)
            top_n: Number of top prompts to return
        
        Returns:
            Ranked DataFrame
        """
        if self.metrics_df is None:
            self.compute_prompt_metrics()
        
        if by not in self.metrics_df.columns:
            raise ValueError(f"Metric '{by}' not found. Available: {list(self.metrics_df.columns)}")
        
        ranked = self.metrics_df.sort_values(by, ascending=False).head(top_n)
        return ranked
    
    def get_best_neutral_agent_prompts(self, 
                                       max_contamination: float = 30,
                                       max_bias: float = 15,
                                       min_agent_dominance: float = 0.5,
                                       top_n: int = 10) -> pd.DataFrame:
        """
        Find prompts that induce agent mode while remaining behaviorally neutral.
        
        Filters:
        - Low game theory contamination (< threshold %)
        - Low behavioral bias (< threshold %)
        - Positive agent dominance (agent > observer)
        
        Args:
            max_contamination: Maximum % with game theory language
            max_bias: Maximum deviation from 50/50 cooperation rate
            min_agent_dominance: Minimum agent-observer score difference
            top_n: Number of results to return
        
        Returns:
            Filtered and ranked DataFrame
        """
        if self.metrics_df is None:
            self.compute_prompt_metrics()
        
        # Apply filters
        filtered = self.metrics_df[
            (self.metrics_df['game_theory_contamination'] <= max_contamination) &
            (self.metrics_df['agent_dominance'] >= min_agent_dominance)
        ]
        
        # Add behavioral filter if available
        if 'behavior_bias' in filtered.columns:
            filtered = filtered[filtered['behavior_bias'] <= max_bias]
        
        # Rank by quality score
        if 'quality_score' in filtered.columns:
            ranked = filtered.sort_values('quality_score', ascending=False).head(top_n)
        else:
            ranked = filtered.sort_values('agent_dominance', ascending=False).head(top_n)
        
        return ranked
    
    def generate_report(self, output_dir: str = '/mnt/user-data/outputs'):
        """
        Generate comprehensive analysis report with multiple views.
        """
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        if self.metrics_df is None:
            self.compute_prompt_metrics()
        
        # 1. Full metrics table
        metrics_path = f'{output_dir}/prompt_metrics_full.csv'
        self.metrics_df.to_csv(metrics_path, index=False)
        print(f"✓ Saved full metrics: {metrics_path}")
        
        # 2. Top prompts by quality
        if 'quality_score' in self.metrics_df.columns:
            top_quality = self.rank_prompts('quality_score', 20)
            quality_path = f'{output_dir}/top_prompts_by_quality.csv'
            top_quality.to_csv(quality_path, index=False)
            print(f"✓ Saved top quality prompts: {quality_path}")
        
        # 3. Best neutral agent prompts
        if 'behavior_bias' in self.metrics_df.columns:
            neutral_agents = self.get_best_neutral_agent_prompts(
                max_contamination=30,
                max_bias=15,
                min_agent_dominance=0.5,
                top_n=20
            )
            neutral_path = f'{output_dir}/best_neutral_agent_prompts.csv'
            neutral_agents.to_csv(neutral_path, index=False)
            print(f"✓ Saved neutral agent prompts: {neutral_path}")
        
        # 4. Classified notes (for validation)
        if self.classified_df is not None:
            notes_path = f'{output_dir}/classified_notes_full.csv'
            self.classified_df.to_csv(notes_path, index=False)
            print(f"✓ Saved classified notes: {notes_path}")
        
        # 5. Summary statistics
        self._print_summary()
        
        return {
            'metrics': metrics_path,
            'top_quality': quality_path if 'quality_score' in self.metrics_df.columns else None,
            'neutral_agents': neutral_path if 'behavior_bias' in self.metrics_df.columns else None,
            'classified_notes': notes_path
        }
    
    def _print_summary(self):
        """Print summary statistics to console."""
        print("\n" + "="*80)
        print("PROMPT QUANTIFICATION SUMMARY")
        print("="*80)
        
        print(f"\nTotal prompts analyzed: {len(self.metrics_df)}")
        print(f"Total reasoning notes: {len(self.classified_df)}")
        
        # Overall mode distribution
        mode_counts = self.classified_df['mode'].value_counts()
        print("\nOverall Mode Distribution:")
        for mode, count in mode_counts.items():
            pct = (count / len(self.classified_df)) * 100
            print(f"  {mode}: {count} ({pct:.1f}%)")
        
        # Contamination statistics
        contam = self.metrics_df['game_theory_contamination']
        print(f"\nGame Theory Contamination:")
        print(f"  Mean: {contam.mean():.1f}%")
        print(f"  Median: {contam.median():.1f}%")
        print(f"  Range: {contam.min():.1f}% - {contam.max():.1f}%")
        
        # Agent dominance statistics
        dom = self.metrics_df['agent_dominance']
        print(f"\nAgent Dominance (agent - observer):")
        print(f"  Mean: {dom.mean():.2f}")
        print(f"  Median: {dom.median():.2f}")
        print(f"  Range: {dom.min():.2f} - {dom.max():.2f}")
        
        # Behavioral statistics (if available)
        if 'behavior_bias' in self.metrics_df.columns:
            bias = self.metrics_df['behavior_bias']
            print(f"\nBehavioral Bias (deviation from 50/50):")
            print(f"  Mean: {bias.mean():.1f}%")
            print(f"  Median: {bias.median():.1f}%")
            print(f"  Range: {bias.min():.1f}% - {bias.max():.1f}%")
        
        # Best prompts
        print("\n" + "-"*80)
        print("TOP 5 PROMPTS BY QUALITY SCORE")
        print("-"*80)
        
        if 'quality_score' in self.metrics_df.columns:
            top5 = self.metrics_df.nlargest(5, 'quality_score')
            for idx, row in top5.iterrows():
                prompt_preview = row['prompt'][:60] + "..." if len(str(row['prompt'])) > 60 else row['prompt']
                print(f"\n{idx+1}. {prompt_preview}")
                print(f"   Quality: {row['quality_score']:.1f}/100")
                print(f"   Agent Dominance: {row['agent_dominance']:.2f}")
                print(f"   Game Theory: {row['game_theory_contamination']:.1f}%")
                if 'behavior_bias' in row:
                    print(f"   Behavioral Bias: {row['behavior_bias']:.1f}%")
        else:
            top5 = self.metrics_df.nlargest(5, 'agent_dominance')
            for idx, row in top5.iterrows():
                prompt_preview = row['prompt'][:60] + "..." if len(str(row['prompt'])) > 60 else row['prompt']
                print(f"\n{idx+1}. {prompt_preview}")
                print(f"   Agent Dominance: {row['agent_dominance']:.2f}")
                print(f"   Game Theory: {row['game_theory_contamination']:.1f}%")


def main():
    """Example usage with your dissertation data."""
    
    # Load your data
    notes_df = pd.read_csv('/mnt/user-data/uploads/primordial_system_prompt_notes.csv')
    results_df = pd.read_csv('/mnt/user-data/uploads/primordial_system_prompt_options.csv')
    
    print("="*80)
    print("PROMPT QUANTIFICATION ANALYSIS")
    print("="*80)
    print(f"\nLoaded {len(notes_df)} reasoning notes")
    print(f"Loaded {len(results_df)} behavioral results")
    
    # Initialize quantifier
    quantifier = PromptQuantifier(notes_df, results_df)
    
    # Classify all notes
    quantifier.classify_all_notes()
    
    # Compute metrics
    quantifier.compute_prompt_metrics()
    
    # Generate full report
    files = quantifier.generate_report()
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print("\nGenerated files:")
    for name, path in files.items():
        if path:
            print(f"  {name}: {path}")
    
    # Return the quantifier for interactive use
    return quantifier


if __name__ == '__main__':
    quantifier = main()
