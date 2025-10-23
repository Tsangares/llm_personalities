
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Type
from dataclasses import dataclass

@dataclass
class Persona:
    """Represents an LLM persona for behavioral experiments"""
    name: str
    description: str
    system_prompt: str
    demographic_info: Optional[Dict[str, Any]] = None
    
    def get_full_system_prompt(self) -> str:
        """Construct complete system prompt with persona characteristics"""
        base = f"{self.system_prompt}\n\n"
        
        if self.demographic_info:
            demo_text = "Your characteristics:\n"
            for key, value in self.demographic_info.items():
                demo_text += f"- {key}: {value}\n"
            base += demo_text
            
        return base.strip()
