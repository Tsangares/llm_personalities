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

## Recent Changes
- Refactored all games to accept `play(strategies=None)` parameter
- Added Monte Carlo simulation support to base Game class
- Centralized game exports in `__init__.py`
- All games maintain backward compatibility with `submit_strategy()` pattern
