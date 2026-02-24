# System Prompts as Personality: How Framing Shifts LLM Behavior in the Prisoner's Dilemma

System prompts can shift a large language model from a game-theoretic analyst to a cooperative participant. This repository implements a pipeline for measuring that shift: hundreds of system prompt variations are fed to locally-hosted LLMs playing the Prisoner's Dilemma, and the resulting decisions and free-text explanations are scored along semantic dimensions that capture "embodiment" -- the degree to which the model engages as a situated agent rather than an outside observer. A single embodiment axis predicts defection rates with AUC ~0.92 and a prompt-level correlation of r = -0.94.

## Research Question

Unrestricted LLMs default to academic, game-theoretic reasoning and overwhelmingly cooperate or defect based on training priors rather than strategic calculation. Can short system-prompt interventions -- reframing the task as real, invoking first-person identity, or restricting theoretical elaboration -- shift this behavior in a measurable and predictable way?

## Methodology

### Experimental Design

1. **Prompt Construction.** A combinatorial set of ~300 system prompts is built from atomic components spanning three theoretical dimensions:
   - **Grammatical Perspective** -- first-person ("You are human") vs. impersonal framing
   - **Ontological Framing** -- concrete ("This is real life") vs. abstract/hypothetical
   - **Reasoning Mode** -- moral/relational vs. strategic/game-theoretic cues

   Components are combined with and without periods, newlines, and ordering permutations to control for surface-level formatting effects. The full prompt set is stored in `all_prompts.json`.

2. **Game Play.** Each prompt is used as the system prompt for N trials (typically 50--60) of the Prisoner's Dilemma against a locally-hosted LLM via [Ollama](https://ollama.com). The model returns a structured response (choice + short free-text justification) enforced through Pydantic schema validation.

3. **Semantic Analysis.** Free-text justifications are scored using keyword-based markers validated by log-odds ratios, then reduced via PCA. The analysis pipeline is in `semantic_analysis.ipynb`.

### Games Implemented

The `src/games/` module implements six classic behavioral economics games, though the current study focuses on the Prisoner's Dilemma:

| Game | Description |
|------|-------------|
| Prisoner's Dilemma | Cooperate (stay silent) or defect (confess) simultaneously |
| Dictator Game | Allocate endowment between self and recipient |
| Ultimatum Game | Propose split; responder accepts or rejects |
| Public Goods Game | Contribute to a multiplied public pool |
| Trust Game | Investor sends amount (tripled); trustee returns a portion |
| Volunteer's Dilemma | At least one player must volunteer for group benefit |

### Models Tested

Data has been collected for multiple models, including:
- `qwen2.5:14b-multi` (primary)
- `mistral:7b`
- `llama3.1:8b`
- `llama3.1:70b-instruct` (quantized)

## Key Findings

1. **Embodiment predicts behavior.** An "embodiment score" -- measuring first-person plural language, concrete framing, and moral/relational reasoning -- correlates strongly with cooperation. Cohen's d = 1.98 between cooperators and defectors.

2. **Three dimensions collapse into one.** PCA on theory-driven keyword features shows a single principal component (25% variance explained) that captures an observer-vs-embodied axis. Game-theory language, strategic reasoning, and self-interest load positively (predicting confession); moral reasoning, first-person plural, and collective interest load negatively (predicting silence).

3. **Reasoning mode dominates perspective.** In a 2x2 crossing of grammatical perspective and reasoning mode, reasoning mode accounts for far more variance: strategic + third-person prompts yield 53.8% confession, while moral/relational + third-person yields only 2.9%. Perspective alone shifts rates by ~26 percentage points; reasoning mode shifts them by ~50+.

4. **Data-driven vocabulary confirms theory.** A vocabulary discovery approach (log-odds on the top/bottom 10% of embodiment scores, then PCA on the top 100 discriminating terms) converges with the theory-driven framework (r = -0.47 between data-driven PC1 and theory-driven composite). Combined PC1+PC2 achieves AUC = 0.92, matching the theory-driven AUC of 0.89.

5. **"Dominant strategy" is nearly diagnostic.** The bigram "dominant_strategy" has a log-odds ratio of +5.36, appearing in 35.7% of Confess responses but only 0.2% of Stay Silent responses.

## Repository Structure

```
llm_personalities/
├── src/
│   ├── games/                  # Game implementations
│   │   ├── game.py             # Base Game class
│   │   ├── prisoner.py         # Prisoner's Dilemma
│   │   ├── dictator.py         # Dictator Game
│   │   ├── ultimatum.py        # Ultimatum Game
│   │   ├── public_good.py      # Public Goods Game
│   │   ├── trust.py            # Trust Game
│   │   ├── volunteer.py        # Volunteer's Dilemma
│   │   ├── prompts/            # Default system/game prompt templates
│   │   └── __init__.py         # Centralized exports
│   ├── llm_agent.py            # LLMAgent wrapper (Pydantic-enforced structured output)
│   ├── query.py                # OllamaClient (API client for Ollama)
│   ├── llm_games.py            # CLI game runner for all six games
│   ├── run_games.py            # Validation / Monte Carlo simulations
│   └── analyze.py              # Per-game analysis and visualization
├── generate_notes_prisoners_dilemma.py   # Main experiment runner (multi-GPU, caching)
├── run_system_prompts.py                 # Lightweight experiment runner
├── semantic_analysis.ipynb               # Full analysis pipeline (scoring, PCA, figures)
├── z_system_prompting.ipynb              # Prompt exploration notebook
├── z_system_prompting_descriptions.ipynb # Prompt-level statistics and data collection
├── all_prompts.json              # 300+ system prompt variations
├── output/
│   ├── primordial_system_prompt_notes*.csv   # Raw trial-level data (choice + note + prompt)
│   ├── primordial_system_prompt_options.csv  # Prompt-level summary statistics
│   ├── figures/                              # Publication-quality figures (PDF + PNG)
│   │   ├── fig1_keyword_validation.*         # Log-odds ratios for keyword markers
│   │   ├── fig2_pca_dimension_collapse.*     # PCA scree plot and PC1 loadings
│   │   ├── fig3_embodiment_by_choice.*       # Embodiment score distributions
│   │   ├── fig4_prompt_level_scatter.*       # Prompt-level embodiment vs. confession rate
│   │   ├── fig5_2x2_heatmap.*               # Perspective x Reasoning Mode interaction
│   │   └── fig6_dimension_correlations.*     # Dimension correlation matrix
│   └── full_analysis_results.csv             # Complete analysis output
├── docs/
│   ├── personality_consistency_protocol.md   # Cross-game personality testing protocol
│   └── llm_responsibility.pdf                # Reference: DeAngelo, McCannon & Wyatt (2025)
├── archive/                    # Deprecated notebooks and temp files
└── claude.md                   # Development notes and personality definitions
```

## Setup

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com) running locally (or on a remote host)
- A pulled model (e.g., `ollama pull qwen2.5:14b-multi`)

### Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install pandas numpy matplotlib scikit-learn pydantic ollama python-dotenv
```

### Configuration

Create a `.env` file in the project root (or export environment variables):

```
OLLAMA_MODEL=qwen2.5:14b-multi
OLLAMA_HOST=localhost
OLLAMA_PORT=11434
```

## Usage

### Run Prisoner's Dilemma Experiment

The main experiment script iterates over all system prompts and collects N responses per prompt. It supports caching (crash-safe) and multi-GPU parallelism.

```bash
# Default: 60 samples/prompt on qwen2.5:14b-multi
python generate_notes_prisoners_dilemma.py

# Custom model, sample size, and dual-GPU parallelism
python generate_notes_prisoners_dilemma.py \
    --model llama3.1:8b \
    --n 50 \
    --parallel 2 \
    --ports 11434,11435
```

A simpler, standalone runner is also available:

```bash
python run_system_prompts.py
```

### Run Other Games

```bash
# Single game with an LLM agent
PYTHONPATH=. python src/llm_games.py prisoner

# Monte Carlo simulation (500 rounds)
PYTHONPATH=. python src/llm_games.py --simulate dictator 500
```

### Analyze Results

Open `semantic_analysis.ipynb` in Jupyter for the full analysis pipeline (keyword validation, PCA, embodiment scoring, figures).

For per-game analysis of the six-game suite:

```bash
python src/analyze.py              # All games
python src/analyze.py prisoner     # Single game
python src/analyze.py --summary-only
```

## References

- DeAngelo, McCannon, & Wyatt (2025). "The Role of Responsibility in AI's Strategic Risk-Taking."
- See `docs/` for the full personality consistency protocol and reference materials.

## License

Research project -- Claremont Graduate University
