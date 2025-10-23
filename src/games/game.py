# game.py
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Union
import random
import numpy as np

Strategy = Union[str, bool, float, int, Callable[..., Any]]

class Game(ABC):
    """
    Base class for game-theory simulations.

    Usage:
    - play(strategies) executes the game with given strategies
    - Strategies can be: str, bool, int, float, or callable
    - Payoffs returned as List[float], one per player
    - submit_strategy() for manual testing, play(strategies) for programmatic use
    - monte_carlo() runs simulations over strategy spaces
    """

    def __init__(self, num_players: int = 2, endowment: float = 100.0, payoff_matrix: dict = {}, **params: Any):
        self.num_players: int = num_players
        self.endowment: float = float(endowment)
        self.params: Dict[str, Any] = params
        self.strategies: Dict[int, Strategy] = {}
        self.payoffs: List[float] = [0.0] * num_players
        self.payoff_matrix = payoff_matrix


    def calibrate(self, **params: Any) -> None:
        """Adjust model parameters."""
        self.params.update(params)

    def submit_strategy(self, player_id: int, strategy: Strategy) -> None:
        """
        Submit a strategy for player `player_id`.
        strategy can be:
         - a number (e.g., amount or fraction)
         - a callable that will be called during play()
        """
        if not (0 <= player_id < self.num_players):
            raise IndexError("player_id out of range")
        self.strategies[player_id] = strategy

    def _resolve(self, player_id: int, **kwargs: Any) -> Any:
        """Return the strategy value for player_id by calling if callable, else returning constant."""
        strat = self.strategies.get(player_id)
        if strat is None:
            return None
        if callable(strat):
            return strat(player_id=player_id, game=self, **kwargs)
        return strat

    @abstractmethod
    def play(self, strategies: Optional[List[Strategy]] = None) -> List[float]:
        """
        Execute the game with given strategies.

        Args:
            strategies: List of strategies (one per player). If None, uses submitted strategies.

        Returns:
            List of payoffs (one per player)
        """
        raise NotImplementedError


    def get_payoffs(self) -> List[float]:
        """Returns the resulting payoffs (after play)."""
        return self.payoffs
    
    
    def monte_carlo(
            self,
            strategy_space: List[List[Strategy]],
            n_rounds: int = 10_000
        ) -> dict:
            """
            Runs a Monte Carlo simulation sampling random strategies.

            Args:
                strategy_space: List of strategy options per player.
                    Example: [[0.1, 0.3, 0.5], [0.2, 0.4]] for 2 players
                n_rounds: Number of simulation rounds

            Returns:
                Dictionary with avg_payoffs and n_rounds
            """
            payoffs = np.zeros(self.num_players)

            for _ in range(n_rounds):
                chosen_strategies = [
                    random.choice(strats) for strats in strategy_space
                ]
                result = self.play(chosen_strategies)
                payoffs += np.array(result)

            avg_payoffs = payoffs / n_rounds
            return {
                "avg_payoffs": avg_payoffs.tolist(),
                "n_rounds": n_rounds,
            }
