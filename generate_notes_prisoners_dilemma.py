# %%

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from pydantic import BaseModel, Field
from typing import Literal

from math import sqrt
import math
import json
import time

from src.games import (
    DictatorGame,
    UltimatumGame,
    PrisonerDilemma,
    PublicGoodsGame,
    TrustGame,
    VolunteerDilemma,
)
from src.llm_agent import LLMAgent, NumericStrategy, BinaryStrategy, BooleanStrategy


# ============================================
# CONFIGURATION
# ============================================
DEFAULT_MODEL = "qwen2.5:14b-multi"
DEFAULT_N = 60

def parse_args():
    parser = argparse.ArgumentParser(description='Generate notes for Prisoner\'s Dilemma experiment')
    parser.add_argument('--model', '-m', type=str, default=DEFAULT_MODEL,
                        help=f'Model to use (default: {DEFAULT_MODEL})')
    parser.add_argument('--n', type=int, default=DEFAULT_N,
                        help=f'Number of samples per prompt (default: {DEFAULT_N})')
    parser.add_argument('--no-notes', action='store_true',
                        help='Disable notes generation (for aggregate mode)')
    parser.add_argument('--parallel', '-p', type=int, default=1,
                        help='Number of parallel workers (default: 1, set to 2 for dual GPU)')
    parser.add_argument('--ports', type=str, default='11434',
                        help='Comma-separated Ollama ports (e.g., "11434,11435" for dual GPU)')
    return parser.parse_args()

def sanitize_model_name(model: str) -> str:
    """Convert model name to safe filename suffix (e.g., qwen2.5:14b-multi -> qwen2.5-14b-multi)"""
    return model.replace(':', '-').replace('/', '-')


# %%
USER_PROMPT_PRISONER="""
You and your accomplice have been arrested. 
You are being interrogated separately and cannot communicate. 
Here are your options:

- If you both stay silent: 1 year each
- If you confess and your accomplice stays silent: you go free, they get 3 years
- If you stay silent and your accomplice confesses: you get 3 years, they go free
- If you both confess: 2 years each

Do you stay silent or confess?
"""


# %%
# Parse arguments and setup
args = parse_args()
MODEL = args.model
N = args.n
GENERATE_NOTES = not args.no_notes
PARALLEL = args.parallel
PORTS = [p.strip() for p in args.ports.split(',')]
MODEL_SUFFIX = sanitize_model_name(MODEL)

print(f"Model: {MODEL}")
print(f"Samples per prompt: {N}")
print(f"Notes generation: {'ON' if GENERATE_NOTES else 'OFF'}")
print(f"Parallel workers: {PARALLEL}")
print(f"Ollama ports: {PORTS}")

# Create an agent for each port (for multi-GPU setups)
agents = [LLMAgent(model=MODEL, port=port) for port in PORTS]
agent_index = [0]  # Mutable counter for round-robin
agent_lock = threading.Lock()

def get_next_agent():
    """Round-robin agent selection (thread-safe)"""
    with agent_lock:
        agent = agents[agent_index[0] % len(agents)]
        agent_index[0] += 1
        return agent

# For backward compatibility
agent = agents[0]

class BinaryStrategy_Prisoners(BaseModel):
    choice: Literal["Stay Silent", "Confess"] = Field(description="Your choice: Stay Silent or Confess")
    note: str = Field(description="A one or two sentences max description explaining your chocie.")


# ============================================
# FILE PATHS (model-specific)
# ============================================
CACHE_DIR = 'cache'
OUTPUT_DIR = 'output'

os.makedirs(CACHE_DIR, exist_ok=True)

OUTPUT_NOTES_CSV = f'{OUTPUT_DIR}/primordial_system_prompt_notes_{MODEL_SUFFIX}.csv'
OUTPUT_NOTES_JSON = f'{OUTPUT_DIR}/primordial_system_prompt_notes_{MODEL_SUFFIX}.json'
CACHE_FILE = f'{CACHE_DIR}/temp_notes_{MODEL_SUFFIX}.json'

# %%
if os.path.isfile(OUTPUT_NOTES_CSV):
    old_df = pd.read_csv(OUTPUT_NOTES_CSV)
else:
    old_df = None

# %%
def get_stats(df):
    import math
    
    z = 1.96
    n = len(df)
    p_hat = (df['choice'] == 'Confess').mean()
    se = math.sqrt(p_hat * (1 - p_hat) / n)
    
    counts = df['choice'].value_counts()
    confess_count = counts.get('Confess', 0)
    silent_count = counts.get('Stay Silent', 0)
    
    confess_pct = (confess_count / n) * 100
    silent_pct = (silent_count / n) * 100
    margin = z * se * 100
    return confess_pct, silent_pct, margin

# %%
def systemPrompt(prompt=""):
    SYSTEM_PROMPT=prompt
    choices = []
    while len(choices) <= N:
        current_agent = get_next_agent()
        choice = current_agent.play(USER_PROMPT_PRISONER, BinaryStrategy_Prisoners, system_prompt=SYSTEM_PROMPT)
        if choice is None: continue
        c = choice.model_dump() | {"prompt": prompt}
        choices.append(c)
    return choices

# %%
base_df = pd.read_csv('output/primordial_system_prompt_options.csv')
base_df.sample(6)

# %%
completed_prompts = []
if old_df is not None:
    prompt_counts = old_df['prompt'].astype(str).value_counts().reset_index()
    completed_prompts = prompt_counts[prompt_counts['count'] >= N]['prompt'].astype(str).unique()
else:
    print("No old dataframe")

if os.path.isfile(CACHE_FILE):
    cache = json.load(open(CACHE_FILE))
    cache_df = pd.DataFrame(cache)
    if len(cache_df) > 0 :
        print('Checking cache...')
        __limit = cache_df['prompt'].nunique()
        for i, prompt in enumerate(cache_df['prompt'].astype(str).unique()):
            dots = "."*(i+1)
            dots = dots.replace('...','... ')
            dots = ' '*int(__limit-i + int(i/3)) + dots
            #print(dots)
            if prompt not in completed_prompts:
                print(f"Unique Prompt {prompt}")
                print("Saving Cache.")
                if old_df is not None:
                    df = pd.concat([cache_df, old_df])
                    print(len(cache_df), len(old_df), len(df))
                else:
                    df = cache_df
                    print(f"Saving {len(cache_df)} cached results (no previous output file)")
                df.to_csv(OUTPUT_NOTES_CSV, index=False)
                quit(1)
        print("Cache already saved.")

if GENERATE_NOTES:
    results = []
    results_lock = threading.Lock()
    skipped = 0
    start_time = time.time()

    # Filter prompts to process
    prompts_to_process = []
    for prompt in base_df['Prompt']:
        if str(prompt) in completed_prompts:
            skipped += 1
        else:
            prompts_to_process.append(prompt)

    print(f"Skipped {skipped} / {len(base_df)} already completed ({skipped/len(base_df):.0%})")
    print(f"Processing {len(prompts_to_process)} prompts with {PARALLEL} workers...")

    completed_count = [0]  # Use list to allow mutation in nested function

    def process_prompt(prompt):
        """Process a single prompt - thread-safe"""
        result = systemPrompt(prompt)
        with results_lock:
            results.extend(result)
            completed_count[0] += 1
            duration = (time.time() - start_time) / 60
            print(f"Completed {completed_count[0]:03d}/{len(prompts_to_process)} ({duration:.02f} min)")
            # Save cache periodically
            if completed_count[0] % 5 == 0:
                json.dump(results, open(CACHE_FILE, 'w+'))
        return result

    if PARALLEL > 1:
        # Parallel execution
        with ThreadPoolExecutor(max_workers=PARALLEL) as executor:
            futures = {executor.submit(process_prompt, p): p for p in prompts_to_process}
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"Error processing prompt: {e}")
    else:
        # Sequential execution (original behavior)
        for prompt in prompts_to_process:
            process_prompt(prompt)

    # Final cache save
    json.dump(results, open(CACHE_FILE, 'w+'))
else:
    print("Notes generation disabled (--no-notes flag)")
    results = []
    start_time = time.time()

# %%
df = pd.DataFrame(results)

# %%
if len(df) > 0:
    if os.path.isfile(OUTPUT_NOTES_CSV):
        old_df = pd.read_csv(OUTPUT_NOTES_CSV)
        df = pd.concat([df, old_df])
    df = df.reset_index(drop=True)
    df.to_csv(OUTPUT_NOTES_CSV, index=False)
    df.to_json(OUTPUT_NOTES_JSON, orient="records")
    duration = (time.time() - start_time) / 60
    print(f"Saved {OUTPUT_NOTES_CSV} in {duration:.01f} min")
    print(df.describe())
else:
    print("No new results to save")