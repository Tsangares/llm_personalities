import pandas as pd
import numpy as np
import json
import os
import time
import logging
from pydantic import BaseModel, Field
from typing import Literal
from ollama import Client

# Config
MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:14b-multi")
HOST = os.getenv("OLLAMA_HOST", "localhost")
PORT = os.getenv("OLLAMA_PORT", "11434")
N = 50
INPUT_FILE = "all_prompts.json"
OUTPUT_FILE = f"prisoners_dilemma_notes_{int(time.time())}.csv" #Added in time to make each output unique for each model
CACHE_FILE = "cache.json"

DEFAULT_SYSTEM_PROMPT = ""

USER_PROMPT = """
You and your accomplice have been arrested.
You are being interrogated separately and cannot communicate.
Here are your options:

- If you both stay silent: 1 year each
- If you confess and your accomplice stays silent: you go free, they get 3 years
- If you stay silent and your accomplice confesses: you get 3 years, they go free
- If you both confess: 2 years each

Do you stay silent or confess?
"""

class Response(BaseModel):
    choice: Literal["Stay Silent", "Confess"] = Field(description="Your choice: Stay Silent or Confess")
    note: str = Field(description="A one or two sentences max description explaining your choice.")


def run_agent(user_prompt, response_model, system_prompt="", temperature=0.7):
    client = Client(host=f"http://{HOST}:{PORT}")
    full_system_prompt = DEFAULT_SYSTEM_PROMPT + f"\n{system_prompt}"

    response = client.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": full_system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        format=response_model.model_json_schema(),
        options={"temperature": temperature}
    )
    return response_model.model_validate_json(response.message.content)


# Run


## Loads Prompts
prompts = json.load(open(INPUT_FILE))
print(f"We have a total of {len(prompts)} prompts; Running {N} trails each on {MODEL}\n")

results = []

## Cache in case of crash or reloading.
if os.path.isfile(CACHE_FILE):
    print("Found cache, loading.")
    with open(CACHE_FILE) as c:
        try:
            results = json.load(c)
        except json.decoder.JSONDecodeError as e:
            logging.warning("Failed to load the cache; must be corrupted. ")
    print(f"Found {len(results)} results in the cache.\n")
    

TOTAL_PROMPTS = len(prompts)

# IF the cache retrieves a completed prompt, skip it. 
#Convert results to DF
cached_prompts = pd.DataFrame(results) 
# Count each prompt in the result
completed_prompts = cached_prompts.groupby('prompt')['prompt'].value_counts().reset_index()
#Debug
#print(completed_prompts)
# Return list of prompt that already have N responses. 
completed_prompts = list(completed_prompts[completed_prompts['count']>= N]['prompt'])
print(f"We have {len(completed_prompts)} prompts completed")


for i,system_prompt in enumerate(prompts):
    start_time = time.time()
    
    print(f"\nRunning Prompt [{i+1}/{TOTAL_PROMPTS}]: {str(system_prompt)[:100]}")
    if system_prompt in completed_prompts: 
        print("Skipping, already completed.")
        continue
    
    for _ in range(N):
        response = run_agent(USER_PROMPT, Response, system_prompt=system_prompt)
        results.append({"choice": response.choice, "note": response.note, "prompt": system_prompt, "model": MODEL})
        
    with open(CACHE_FILE, 'w+') as cache:
        json.dump(results, cache, indent=1)
        
    # Prompt Stats
    duration = (time.time() - start_time)/60
    confession_rate = np.mean([result['choice']=="Confess" for result in results if result['prompt']==system_prompt])
    print(f"Confession rate {confession_rate:.02%}")
    print(f"Duration: {duration:.02f} min")

#Saving
pd.DataFrame(results).to_csv(OUTPUT_FILE, index=False)
print(f"Saved {len(results)} results to {OUTPUT_FILE}")
os.remove(CACHE_FILE)
print(f"Removed cache.")
