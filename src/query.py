"""
OLLAMA Client with Structured Output using Pydantic
Install: pip install ollama pydantic
"""

from ollama import chat
from pydantic import BaseModel, Field
from typing import Optional


class Response(BaseModel):
    answer: str = Field(description="The main answer to the query")
    confidence: float = Field(description="Confidence score between 0 and 1", ge=0, le=1)
    reasoning: Optional[str] = Field(default=None, description="Reasoning behind the answer")


class OllamaClient:
    def __init__(self, model):
        self.model = model
    
    def get_structured_response(self, prompt,response_model: type[BaseModel] = Response, temperature=0.7):
        response = chat(
            model=self.model,
            messages=[
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            format=response_model.model_json_schema(),  # Pass Pydantic schema
            options={'temperature': temperature}
        )
        
        # Parse and validate the JSON response
        return response_model.model_validate_json(response.message.content)


# Example usage
if __name__ == "__main__":
    # Initialize client
    client = OllamaClient(model="llama3.2")
    
    # Send a request
    try:
        result = client.get_structured_response(
            prompt="What is the capital of France? Rate your confidence from 0 to 1."
        )
        
        print("Structured Response:")
        print(f"Answer: {result.answer}")
        print(f"Confidence: {result.confidence}")
        print(f"Reasoning: {result.reasoning}")
        
        # You can also access it as a dict
        print("\nAs dict:", result.model_dump())
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure:")
        print("1. Ollama is installed and running")
        print("2. You have the model: ollama pull llama3.2")
        print("3. You installed: pip install ollama pydantic")