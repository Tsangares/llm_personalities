# public_good.py
from typing import List, Optional
from src.games.game import Game, Strategy

class PublicGoodsGame(Game):
    GAME_RULES = "You have ${endowment}. Decide how much to contribute to a public pool. Total contributions are multiplied by {multiplier} and split equally among {n_players} players. You keep what you don't contribute plus your share. Respond with contribution (absolute or fraction 0-1)."

    def __init__(self, n_players: int = 4, endowment: float = 100.0, multiplier: float = 1.5):
        super().__init__(num_players=n_players, endowment=endowment, multiplier=multiplier)

    def play(self, strategies: Optional[List[Strategy]] = None) -> List[float]:
        """
        Public goods game with N players.

        Args:
            strategies: List of contributions (one per player).
                       Each can be absolute amount or fraction (0-1).
                       If None, uses submitted strategies.

        Returns:
            List of payoffs (one per player)
        """
        contributions = []
        for pid in range(self.num_players):
            if strategies is not None:
                raw = strategies[pid]
            else:
                raw = self._resolve(pid)

            if raw is None:
                c = 0.0
            else:
                cval = float(raw)
                c = cval if cval > 1.0 else cval * self.endowment
            contributions.append(max(0.0, min(self.endowment, c)))

        total = sum(contributions)
        public_pot = total * float(self.params.get("multiplier", 1.0))
        share = public_pot / self.num_players

        for pid in range(self.num_players):
            self.payoffs[pid] = (self.endowment - contributions[pid]) + share
        return self.payoffs
