# ultimatum.py
from typing import List, Optional
from src.games.game import Game, Strategy

class UltimatumGame(Game):
    PROPOSER_RULES = "You have ${endowment}. Propose how much to offer the other player. They can accept or reject. If rejected, both get 0. Respond with your offer (absolute or fraction 0-1)."
    RESPONDER_RULES = "The proposer will offer you part of ${endowment}. You can accept or reject. If you reject, both get 0. Respond with your minimum acceptable offer (absolute or fraction)."

    def __init__(self, endowment: float = 100.0, responder_threshold = None):
        # responder_threshold: if provided as fraction (0-1) or absolute amount
        super().__init__(num_players=2, endowment=endowment, responder_threshold=responder_threshold)

    def play(self, strategies: Optional[List[Strategy]] = None) -> List[float]:
        """
        Proposer offers a split, responder accepts or rejects.

        Args:
            strategies: [proposer_offer, responder_threshold]
                - proposer_offer: absolute amount or fraction (0-1)
                - responder_threshold: minimum acceptable offer (absolute or fraction)
                If None, uses submitted strategies.

        Returns:
            [proposer_payoff, responder_payoff] if accepted, [0, 0] if rejected
        """
        # Get proposer's offer
        if strategies is not None:
            raw_offer = strategies[0]
        else:
            raw_offer = self._resolve(0)

        if raw_offer is None:
            offer = 0.0
        else:
            if isinstance(raw_offer, (int, float)):
                val = float(raw_offer)
                offer = val if val > 1.0 else val * self.endowment
            else:
                offer = float(raw_offer)

        offer = max(0.0, min(self.endowment, offer))

        # Get responder's decision
        if strategies is not None and len(strategies) > 1:
            responder_strat = strategies[1]
        else:
            responder_strat = self.strategies.get(1)

        accepted = True
        if responder_strat is None:
            # default: accept any positive offer
            accepted = offer >= 0.0
        elif callable(responder_strat):
            accepted = bool(responder_strat(offer=offer, game=self))
        else:
            # numeric threshold
            threshold = float(responder_strat)
            threshold = threshold if threshold > 1.0 else threshold * self.endowment
            accepted = offer >= threshold

        if accepted:
            self.payoffs[0] = self.endowment - offer
            self.payoffs[1] = offer
        else:
            self.payoffs = [0.0, 0.0]
        return self.payoffs
