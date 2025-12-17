# Claude Code - Project Notes

## File Creation Policy

**IMPORTANT:** No files should be created unless absolutely necessary or under the explicit authority and approval of the user.

### Exceptions:
- `.md` note files and documentation (like this file)
- Files explicitly requested by the user
- Files that are absolutely necessary to complete a user-requested task

### Guidelines:
- **ALWAYS prefer editing existing files** over creating new ones
- When in doubt, ask the user before creating a file
- If a task can be accomplished by modifying existing code, do that instead
- Document changes and additions within existing file structures whenever possible

## Working Directory
- Primary work directory: `./src`
- Virtual environment: `./.venv` (in project root)

## Running Tests
```bash
PYTHONPATH=/home/wil/Desktop/llm_personalities .venv/bin/python src/run_games.py
```

## Project Structure
```
./src/
  games/
    game.py           # Base Game class
    dictator.py       # DictatorGame
    ultimatum.py      # UltimatumGame
    prisoner.py       # PrisonerDilemma
    public_good.py    # PublicGoodsGame
    trust.py          # TrustGame
    volunteer.py      # VolunteerDilemma
    __init__.py       # Centralized exports
  run_games.py        # Test runner and Monte Carlo simulations
```

## Programming Style & Methodology

**Code Philosophy:**
- Concise, minimal code - no unnecessary verbosity
- Comments only when essential - code should be self-documenting
- Type hints only for ambiguous cases - skip obvious types
  - Example: `prompt` is clearly a string, don't annotate it
  - Use types when the type is not obvious from context
- Prefer implicit over explicit when clear
- Clean, readable code over defensive programming

**In Practice:**
- A variable named `prompt` doesn't need `prompt: str`
- A function returning payoffs doesn't need verbose comments explaining every step
- Keep it simple, keep it clean

## LLM Personalities

### General Identity-Based Personalities
These are short, implicit personality prompts that create general behavioral dispositions without directly instructing game-specific behavior. Based on personas from DeAngelo, McCannon, & Wyatt (2025) - "The Role of Responsibility in AI's Strategic Risk-Taking".

**Implementation:** Insert one line into system prompt after "You are an agent participating in a decision-making task."

**Demographic-Based:**
1. **Young** - `You are young; a 25-year-old individual.`
2. **Older** - `You are old; a 75-year-old individual.`
3. **Man** - `You are a man.`
4. **Woman** - `You are a woman.`

**Personality-Based:**
5. **Competitive** - `You are a competitive person.`
6. **Introvert** - `You are an introverted person.`
7. **Extrovert** - `You are an extroverted person.`

**Expected Behavioral Patterns (from human economic experiments):**
- **Young vs Older**: Young = more risk-taking; Older = more cautious when responsible for others
- **Man vs Woman**: Men = higher baseline risk; Women = substantially more risk-averse when responsible for others
- **Competitive**: Higher risk-taking, especially when responsible for others (89% vs 18% in Stag-Hare)
- **Introvert**: Low risk across conditions (~4-13%)
- **Extrovert**: Very high risk across conditions (~88-100%)

### Direct Behavioral Personas (Minimal Variation)
From personality_consistency_protocol.md - designed for cross-game consistency testing.

**Template:** `"You are a [KEYWORD] person who [BEHAVIOR_PHRASE] in decision-making situations."`

1. **GENEROUS** - "You are a generous person who prioritizes others' welfare in decision-making situations."
   - Expected: High giving in Dictator/Ultimatum, cooperation in PD, high Public Goods contributions

2. **SELF-INTERESTED** - "You are a self-interested person who prioritizes your own welfare in decision-making situations."
   - Expected: Low giving in Dictator/Ultimatum, defection in PD, free-riding in Public Goods

3. **FAIR** - "You are a fair person who prioritizes equal outcomes in decision-making situations."
   - Expected: 50-50 splits, rejection of inequitable offers, equal contributions

4. **STRATEGIC** - "You are a strategic person who prioritizes optimal outcomes in decision-making situations."
   - Expected: Game-theoretic reasoning, Nash equilibrium choices, backward induction

5. **COOPERATIVE** - "You are a cooperative person who prioritizes mutual benefit in decision-making situations."
   - Expected: Reciprocal behavior, conditional cooperation, trust with reciprocity

6. **CONTROL (Neutral)** - "You are participating in a research study on decision-making. Please make decisions based on your judgment."
   - Expected: Baseline LLM behavior (likely prosocial due to RLHF)

### Implementation Notes

**For current codebase integration:**
```python
# In src/llm_agent.py or system prompt construction
PERSONALITIES = {
    # General (identity-based)
    "young": "You are young; a 25-year-old individual.",
    "older": "You are old; a 75-year-old individual.",
    "man": "You are a man.",
    "woman": "You are a woman.",
    "competitive": "You are a competitive person.",
    "introvert": "You are an introverted person.",
    "extrovert": "You are an extroverted person.",

    # Behavioral (direct)
    "generous": "You are a generous person who prioritizes others' welfare in decision-making situations.",
    "selfish": "You are a self-interested person who prioritizes your own welfare in decision-making situations.",
    "fair": "You are a fair person who prioritizes equal outcomes in decision-making situations.",
    "strategic": "You are a strategic person who prioritizes optimal outcomes in decision-making situations.",
    "cooperative": "You are a cooperative person who prioritizes mutual benefit in decision-making situations.",
    "control": "You are participating in a research study on decision-making. Please make decisions based on your judgment."
}
```

**Usage:**
```python
# Modify system prompt in src/games/prompts/default_system_prompt.txt
# Or inject dynamically:
system_prompt = SYSTEM_PROMPT + "\n" + PERSONALITIES[persona_key]
```

### Research Design Considerations

**General Personalities (Recommended for human behavior extrapolation):**
- Less direct behavioral instruction
- More ecologically valid for studying emergent behavior
- Better for relating to human experimental economics literature
- May show more variance across games

**Direct Behavioral Personas (For consistency testing):**
- Explicitly state behavioral priorities
- Better for testing cross-game personality coherence
- May produce more predictable/stable behavior
- Useful for validation and mechanism testing

**Suggested Approach:**
1. Start with **general personalities** (young, competitive, etc.) for main experiments
2. Use **behavioral personas** for robustness checks and comparisons
3. Compare variance across games between the two sets

## Recent Changes
- Refactored all games to accept `play(strategies=None)` parameter
- Added Monte Carlo simulation support to base Game class
- Centralized game exports in `__init__.py`
- All games maintain backward compatibility with `submit_strategy()` pattern
