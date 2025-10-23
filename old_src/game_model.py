
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Type
from datetime import datetime
import json

class Game(ABC):
    """Abstract base class for behavioral games"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.history: List[Dict] = []
        
    @abstractmethod
    def get_prompt(self, round_num: int = 1, **context) -> str:
        """Generate the game prompt for the current round"""
        pass
    
    @abstractmethod
    def get_response_model(self) -> Type[BaseModel]:
        """Return the Pydantic model for this game's responses"""
        pass
    
    def record_round(self, round_num: int, response: BaseModel, **metadata):
        """Record the results of a game round"""
        self.history.append({
            'round': round_num,
            'timestamp': datetime.now().isoformat(),
            'response': response.model_dump(),
            **metadata
        })
    
    def get_history_summary(self, rounds: Optional[int] = None) -> str:
        """Get formatted history of previous rounds"""
        if not self.history:
            return "This is the first round."
        
        history_to_show = self.history[-rounds:] if rounds else self.history
        summary = "\nPrevious rounds:\n"
        for entry in history_to_show:
            summary += f"Round {entry['round']}: {json.dumps(entry['response'], indent=2)}\n"
        return summary
