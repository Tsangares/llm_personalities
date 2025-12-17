# LLM Game Theory Simulator

Simulates classic behavioral economics games with Large Language Models to study emergent strategic behavior and personality consistency.

## Quick Start

### 1. Setup
```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

Create `.env` file:
```
OLLAMA_MODEL=mistral:7b
OLLAMA_HOST=localhost
OLLAMA_PORT=11434
```

### 2. Run Games

**Single game with LLM agents:**
```bash
PYTHONPATH=. python src/llm_games.py dictator
```

**Run simulations (500 rounds):**
```bash
PYTHONPATH=. python src/llm_games.py --simulate dictator 500
```

**Available games:** `dictator`, `ultimatum`, `prisoner`, `public_good`, `trust`, `volunteer`

### 3. Analyze Results

**Analyze all games:**
```bash
python src/analyze.py
```

**Analyze specific game:**
```bash
python src/analyze.py dictator
```

**Generate summary visualization only:**
```bash
python src/analyze.py --summary-only
```

Results saved to `output/` directory (CSV data + PNG plots).

## Project Structure

```
llm_personalities/
├── src/
│   ├── games/              # Game implementations
│   │   ├── game.py        # Base game class
│   │   ├── dictator.py    # Dictator game
│   │   ├── ultimatum.py   # Ultimatum game
│   │   ├── prisoner.py    # Prisoner's Dilemma
│   │   ├── public_good.py # Public Goods game
│   │   ├── trust.py       # Trust game
│   │   └── volunteer.py   # Volunteer's Dilemma
│   ├── query.py           # Ollama API client
│   ├── llm_agent.py       # LLM agent interface
│   ├── llm_games.py       # LLM game runner
│   ├── run_games.py       # Validation tests
│   └── analyze.py         # Analysis & visualization
├── output/                # Generated data and plots
├── docs/                  # Reference materials
│   ├── llm_responsibility.pdf
│   └── personality_consistency_protocol.md
└── claude.md             # Development notes

```

## Games Implemented

1. **Dictator Game** - Allocate endowment between self and recipient
2. **Ultimatum Game** - Propose split, responder accepts/rejects
3. **Prisoner's Dilemma** - Cooperate or defect simultaneously
4. **Public Goods Game** - Contribute to multiplied public pool
5. **Trust Game** - Investor sends (tripled), trustee returns
6. **Volunteer's Dilemma** - At least one must volunteer for group benefit

## Key Findings

From preliminary analysis (mistral:7b, 500 rounds/game):

- **Prosocial Bias**: 100% cooperation in Prisoner's Dilemma (Nash: 0%)
- **Fairness Norms**: Strong preference for 50-50 splits
- **Limited Strategic Reasoning**: No Nash equilibrium play observed
- **Conclusion**: LLMs exhibit training bias toward cooperation/fairness

See `output/summary_analysis.png` for comprehensive results.

## Development

**Run validation tests:**
```bash
PYTHONPATH=. python src/run_games.py
```

**Add new personality:**
Edit `src/games/prompts/default_system_prompt.txt` or modify system prompt dynamically in `llm_agent.py`.

See `claude.md` for personality templates and implementation notes.

## References

- DeAngelo, McCannon, & Wyatt (2025) - "The Role of Responsibility in AI's Strategic Risk-Taking"
- See `docs/` for full protocol and reference materials

## License

Research project - Claremont Graduate University
