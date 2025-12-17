# trust.py
from typing import List, Optional
from src.games.game import Game, Strategy

class TrustGame(Game):
    INVESTOR_RULES = "You have ${endowment}. Decide how much to send to the trustee. It will be multiplied by {multiplier}. The trustee then decides how much to return. Respond with amount to send (absolute or fraction 0-1)."
    TRUSTEE_RULES = "The investor will send you some amount, which gets multiplied by {multiplier}. Decide what fraction to return to the investor. Respond with fraction to return (0-1)."

    def __init__(self, endowment: float = 100.0, multiplier: float = 3.0):
        super().__init__(num_players=2, endowment=endowment, multiplier=multiplier)

    def play(self, strategies: Optional[List[Strategy]] = None) -> List[float]:
        """
        Trust game: investor sends money, trustee decides how much to return.

        Args:
            strategies: [investor_send, trustee_return_fraction]
                - investor_send: amount to send (absolute or fraction 0-1)
                - trustee_return_fraction: fraction of received amount to return (0-1)
                If None, uses submitted strategies.

        Returns:
            [investor_payoff, trustee_payoff]
        """
        # Get investor's strategy
        if strategies is not None:
            raw_send = strategies[0]
        else:
            raw_send = self._resolve(0)

        if raw_send is None:
            send = 0.0
        else:
            sval = float(raw_send)
            send = sval if sval > 1.0 else sval * self.endowment
        send = max(0.0, min(self.endowment, send))
        received = send * float(self.params.get("multiplier", 3.0))

        # Get trustee's strategy
        if strategies is not None and len(strategies) > 1:
            raw_return = strategies[1]
        else:
            raw_return = self._resolve(1, received=received, sent=send)

        if raw_return is None:
            ret = 0.0
        else:
            rval = float(raw_return)
            ret = rval if rval > 1.0 else rval * received
        ret = max(0.0, min(received, ret))

        self.payoffs[0] = self.endowment - send + ret
        self.payoffs[1] = received - ret
        return self.payoffs
