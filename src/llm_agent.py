import os
from pydantic import BaseModel, Field
from typing import Literal



from src.query import OllamaClient

PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "games/prompts")

with open(os.path.join(PROMPTS_DIR, "default_system_prompt.txt")) as f:
    SYSTEM_PROMPT = f.read().strip()

with open(os.path.join(PROMPTS_DIR, "default_game_prompt.txt")) as f:
    GAME_PROMPT_TEMPLATE = f.read().strip()


class NumericStrategy(BaseModel):
    value: float = Field(description="Your strategic choice as a number")


class BinaryStrategy(BaseModel):
    choice: str = Field(description="Your choice: C or D")
    
    
class BooleanStrategy(BaseModel):
    decision: bool = Field(description="Your decision: true or false")


class LLMAgent:
    def __init__(self, model=None, host=None, port=None):
        self.client = OllamaClient(model=model, host=host, port=port)
        
        
    def play(self, prompt, response_model=NumericStrategy, system_prompt="", temperature=0.7):
        try:
            result = self.client.query(
                prompt=prompt,
                response_model=response_model,
                temperature=temperature,
                system_prompt=system_prompt
            )
            return result
        except Exception as e:
            print(f"LLM Error: {e}")
            return None


    def get_strategy(self, game_name=None, role=None, rules=None, response_model=NumericStrategy, prompt=None):
        if game_name is not None and role is not None:
            prompt = GAME_PROMPT_TEMPLATE.format(
                game_name=game_name,
                role=role,
                game_rules=rules
            )
        if prompt is None:
            raise Exception("No User Prompt provided.")
            
        
        try:
            result = self.client.query(
                prompt=prompt,
                response_model=response_model,
                temperature=0.7
            )
            return result
        except Exception as e:
            print(f"LLM Error: {e}")
            return None
