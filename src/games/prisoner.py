# prisoner.py
from typing import List, Optional
from src.games.game import Game, Strategy

class PrisonerDilemma(Game):
    GAME_RULES = "Choose: Cooperate (C) or Defect (D). Payoffs: Both C = 3 each, Both D = 1 each, One defects = Defector gets 5, Cooperator gets 0. Respond with C or D."

    def __init__(self, payoff_matrix = None):
        """
        Prisoner's Dilemma game.

        Args:
            payoff_matrix: Dict with keys ('C','C'),('C','D'),('D','C'),('D','D')
                          mapping to (player0_payoff, player1_payoff).
                          Default: R=3 (reward), T=5 (temptation), S=0 (sucker), P=1 (punishment)
        """
        default = {
            ('C','C'): (3.0, 3.0),
            ('C','D'): (0.0, 5.0),
            ('D','C'): (5.0, 0.0),
            ('D','D'): (1.0, 1.0),
        }
        super().__init__(num_players=2, payoff_matrix=payoff_matrix or default)
    
    def play(self, strategies: Optional[List[Strategy]] = None) -> List[float]:
        """
        Each player chooses to Cooperate ('C') or Defect ('D').

        Args:
            strategies: [action0, action1] where each action is 'C' or 'D'
                       If None, uses submitted strategies.

        Returns:
            [payoff0, payoff1] based on payoff matrix
        """
        # Get actions
        if strategies is not None:
            a0 = strategies[0]
            a1 = strategies[1]
        else:
            a0 = self._resolve(0)
            a1 = self._resolve(1)

        action0 = str(a0).upper() if a0 is not None else 'D'
        action1 = str(a1).upper() if a1 is not None else 'D'

        key = (action0, action1)
        pm = self.payoff_matrix
        payoff = pm.get(key)
        if payoff is None:
            # fallback to mutual defection
            payoff = pm[('D','D')]

        self.payoffs[0], self.payoffs[1] = float(payoff[0]), float(payoff[1])
        return self.payoffs
