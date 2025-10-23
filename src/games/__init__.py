# games/__init__.py
"""
Game theory implementations for behavioral economics research.

Available games:
- DictatorGame: One player decides how to split an endowment
- UltimatumGame: Proposer offers split, responder can reject
- PrisonerDilemma: Classic cooperation vs. defection game
- PublicGoodsGame: N-player contribution game with multiplier
- TrustGame: Investor sends money, trustee decides return amount
- VolunteerDilemma: Group benefits if at least one volunteers
"""

from src.games.game import Game, Strategy
from src.games.dictator import DictatorGame
from src.games.ultimatum import UltimatumGame
from src.games.prisoner import PrisonerDilemma
from src.games.public_good import PublicGoodsGame
from src.games.trust import TrustGame
from src.games.volunteer import VolunteerDilemma

__all__ = [
    "Game",
    "Strategy",
    "DictatorGame",
    "UltimatumGame",
    "PrisonerDilemma",
    "PublicGoodsGame",
    "TrustGame",
    "VolunteerDilemma",
]
