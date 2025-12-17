# dictator.py
from typing import List, Optional, Union
from src.games.game import Game, Strategy

class DictatorGame(Game):
    GAME_RULES = "You have ${endowment}. Decide how much to give to the other player. Respond with a number: absolute amount (e.g., 30) or fraction (e.g., 0.3 for 30%)."

    def __init__(self, endowment: float = 100.0):
        super().__init__(num_players=2, endowment=endowment)

    def play(self, strategies: Optional[List[Strategy]] = None) -> List[float]:
        """
        Player 0 (dictator) decides amount to give to player 1.

        Args:
            strategies: [dictator_offer]. Offer can be absolute amount or fraction (0-1).
                       If None, uses submitted strategies.

        Returns:
            [dictator_payoff, recipient_payoff]
        """
        # Get dictator's strategy
        if strategies is not None:
            raw = strategies[0]
        else:
            raw = self._resolve(0)

        if raw is None:
            amount_given = 0.0
        else:
            # treat numbers >1 as absolute, <=1 as fraction
            if isinstance(raw, (int, float)):
                val = float(raw)
                amount_given = val if val > 1.0 else val * self.endowment
            else:
                # if callable returns complex, coerce to float
                amount_given = float(raw)

        amount_given = max(0.0, min(self.endowment, amount_given))
        self.payoffs[0] = self.endowment - amount_given
        self.payoffs[1] = amount_given
        return self.payoffs
