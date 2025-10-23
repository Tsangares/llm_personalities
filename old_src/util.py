from .persona_model import *
from .game_runner import *
from .

# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def quick_run(
    persona: Persona,
    game: Game,
    rounds: int = 1,
    temperature: float = 1.0,
    client: Client = None,
    model: str = "",
    verbose: bool = True
) -> List[BaseModel]:
    """
    Convenience function for quick single game-persona runs
    
    Example:
        >>> persona = Persona(name="Risk Averse", ...)
        >>> game = SomeGame(...)
        >>> responses = quick_run(persona, game, rounds=10)
    """
    runner = GameRunner(client=client, model=model)
    return runner.run_repeated_game(
        game=game,
        persona=persona,
        num_rounds=rounds,
        temperature=temperature,
        verbose=verbose
    )

def compare_personas(
    personas: List[Persona],
    game: Game,
    rounds: int = 1,
    temperature: float = 1.0,
    client: Client = client,
    model: str = MODEL
) -> pd.DataFrame:
    """
    Compare multiple personas on the same game
    
    Example:
        >>> personas = [risk_averse, risk_seeking, cooperative]
        >>> game = PrisonersDilemmaGame(...)
        >>> df = compare_personas(personas, game, rounds=50)
    """
    runner = GameRunner(client=client, model=model)
    return runner.run_experiment(
        games=[game],
        personas=personas,
        rounds_per_game=rounds,
        temperature=temperature
    )

def compare_games(
    persona: Persona,
    games: List[Game],
    rounds: int = 1,
    temperature: float = 1.0,
    client: Client = client,
    model: str = MODEL
) -> pd.DataFrame:
    """
    Test single persona across multiple games
    
    Example:
        >>> persona = Persona(name="Competitive", ...)
        >>> games = [dictator_game, ultimatum_game, trust_game]
        >>> df = compare_games(persona, games, rounds=100)
    """
    runner = GameRunner(client=client, model=model)
    return runner.run_experiment(
        games=games,
        personas=[persona],
        rounds_per_game=rounds,
        temperature=temperature
    )
