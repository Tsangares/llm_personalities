import os
from ollama import Client
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import logging
load_dotenv()

PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "games/prompts")

with open(os.path.join(PROMPTS_DIR, "default_system_prompt.txt")) as f:
    SYSTEM_PROMPT = f.read().strip()


class Response(BaseModel):
    answer: str = Field(description="Main answer")
    confidence: float = Field(description="Confidence 0-1", ge=0, le=1)
    reasoning: str = Field(default="", description="Reasoning")


class OllamaClient:
    def __init__(self, model=None, host=None, port=None):
        self.model = model or os.getenv("OLLAMA_MODEL", "mistral")
        host = host or os.getenv("OLLAMA_HOST", "localhost")
        port = port or os.getenv("OLLAMA_PORT", "11434")
        self.base_url = f"http://{host}:{port}"
        self.client = Client(host=self.base_url)
        
    def query(self, prompt, response_model=Response, temperature=0.7, system_prompt=""):
        logging.debug(str({"role": "system", "content": SYSTEM_PROMPT+f"\n{system_prompt}"}))
        response = self.client.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT+f"\n{system_prompt}"},
                {"role": "user", "content": prompt}
            ],
            format=response_model.model_json_schema(),
            options={"temperature": temperature}
        )
        return response_model.model_validate_json(response.message.content)


if __name__ == "__main__":
    client = OllamaClient()

    print(f"Connecting to: {client.base_url}")
    print(f"Model: {client.model}\n")

    try:
        result = client.query("What is the capital of France? Rate confidence 0-1.")
        print(f"Answer: {result.answer}")
        print(f"Confidence: {result.confidence}")
        print(f"Reasoning: {result.reasoning}")
    except Exception as e:
        print(f"Error: {e}")
        print("\nCheck:")
        print(f"  1. Ollama running on {client.base_url}")
        print(f"  2. Model available: ollama pull {client.model}")
