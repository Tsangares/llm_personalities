# volunteer.py
from typing import List, Optional
from src.games.game import Game, Strategy

class VolunteerDilemma(Game):
    GAME_RULES = "There are {n_players} players. If at least one volunteers, everyone gets ${benefit}. Volunteers pay ${cost}. If no one volunteers, everyone gets 0. Respond with: volunteer (true) or not (false)."

    def __init__(self, n_players: int = 3, cost: float = 20.0, benefit: float = 100.0):
        """
        Volunteer's Dilemma: If at least one volunteers, whole group gets benefit.
        Volunteers pay the cost.

        Args:
            n_players: Number of players
            cost: Cost paid by volunteers
            benefit: Benefit received by all if anyone volunteers
        """
        super().__init__(num_players=n_players, endowment=0.0, cost=cost, benefit=benefit)

    def play(self, strategies: Optional[List[Strategy]] = None) -> List[float]:
        """
        Each player decides whether to volunteer (True) or not (False).

        Args:
            strategies: List of boolean decisions (one per player)
                       If None, uses submitted strategies.

        Returns:
            List of payoffs (one per player)
        """
        volunteers = []
        for pid in range(self.num_players):
            if strategies is not None:
                raw = strategies[pid]
            else:
                raw = self._resolve(pid)

            vol = bool(raw) if raw is not None else False
            volunteers.append(vol)

        any_vol = any(volunteers)
        cost = float(self.params.get("cost", 0.0))
        benefit = float(self.params.get("benefit", 0.0))

        for pid in range(self.num_players):
            if any_vol:
                self.payoffs[pid] = benefit - (cost if volunteers[pid] else 0.0)
            else:
                self.payoffs[pid] = 0.0

        return self.payoffs
