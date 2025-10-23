
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Type


# ============================================================================
# PYDANTIC RESPONSE MODELS
# ============================================================================

class GameAction(BaseModel):
    """Base model for any game action/decision"""
    action: str = Field(..., description="The chosen action")
    reasoning: str = Field(..., description="Explanation for the decision")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Confidence in decision (0-1)")

class DictatorGameResponse(BaseModel):
    """Response for Dictator Game allocation"""
    amount_given: float = Field(..., ge=0, description="Amount allocated to other player")
    amount_kept: float = Field(..., ge=0, description="Amount kept for self")
    reasoning: str = Field(..., description="Explanation for allocation decision")
    
class UltimatumGameResponse(BaseModel):
    """Response for Ultimatum Game (proposer or responder)"""
    role: str = Field(..., description="'proposer' or 'responder'")
    offer: Optional[float] = Field(None, description="Offer amount (proposer only)")
    accept: Optional[bool] = Field(None, description="Accept/reject decision (responder only)")
    reasoning: str = Field(..., description="Explanation for decision")

class PrisonersDilemmaResponse(BaseModel):
    """Response for Prisoner's Dilemma"""
    choice: str = Field(..., description="'cooperate' or 'defect'")
    reasoning: str = Field(..., description="Explanation for choice")
    expectations_about_opponent: Optional[str] = Field(None, description="What they expect opponent to do")

class PublicGoodsResponse(BaseModel):
    """Response for Public Goods Game"""
    contribution: float = Field(..., ge=0, description="Amount contributed to public pool")
    reasoning: str = Field(..., description="Explanation for contribution decision")

class TrustGameResponse(BaseModel):
    """Response for Trust Game"""
    role: str = Field(..., description="'investor' or 'trustee'")
    amount_sent: Optional[float] = Field(None, description="Amount sent (investor only)")
    amount_returned: Optional[float] = Field(None, description="Amount returned (trustee only)")
    reasoning: str = Field(..., description="Explanation for decision")

class RPSResponse(BaseModel):
    """Response for Rock-Paper-Scissors"""
    choice: str = Field(..., description="'rock', 'paper', or 'scissors'")
    reasoning: str = Field(..., description="Explanation for choice")
