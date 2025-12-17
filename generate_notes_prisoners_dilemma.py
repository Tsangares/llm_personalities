# %%

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

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

N = 10
agent = LLMAgent(model="qwen2.5:14b-multi")

class BinaryStrategy_Prisoners(BaseModel):
    choice: Literal["Stay Silent", "Confess"] = Field(description="Your choice: Stay Silent or Confess")
    note: str = Field(description="A one or two sentences max description explaining your chocie.")

# %%
if os.path.isfile('output/primordial_system_prompt_notes.csv'):
    old_df = pd.read_csv('output/primordial_system_prompt_notes.csv')
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
        choice = agent.play(USER_PROMPT_PRISONER, BinaryStrategy_Prisoners, system_prompt=SYSTEM_PROMPT)
        if choice is None: continue
        c = choice.model_dump() | {"prompt": prompt}
        choices.append(c)
    print(choices)
    return choices

# %%
base_df = pd.read_csv('output/primordial_system_prompt_options.csv')
base_df.sample(6)

# %%
N=60

completed_prompts = []
if old_df is not None:
    prompt_counts = old_df['prompt'].astype(str).value_counts().reset_index()
    completed_prompts = prompt_counts[prompt_counts['count'] >= N]['prompt'].astype(str).unique()
else:
    print("No old dataframe")

if os.path.isfile('./output/temp_system_prompt_notes.csv'):
    cache = json.load(open('./output/temp_system_prompt_notes.csv'))
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
                    df.to_csv('output/primordial_system_prompt_notes.csv',index=False)
                    quit(1)
                else:
                    raise Exception("Failed to save cache.")
        print("Cache already saved.")
results = []
skipped=0
start_time = time.time()
for i,prompt in enumerate(base_df['Prompt']):
    if str(prompt) in completed_prompts: 
        skipped+=1
        continue
    
    duration = (start_time - time.time())/60
    print(f"Processing {(i-skipped):03d} total duration {(start_time - time.time())/60:.02f} min")
    result = systemPrompt(prompt)
    results.extend(result)
    json.dump(results, open("./output/temp_system_prompt_notes.csv", 'w+'))
print(f"Skipped {skipped} / {len(base_df)}; ({skipped/len(base_df):.0%})")

# %%
df = pd.DataFrame(results)

# %%
if os.path.isfile('output/primordial_system_prompt_notes.csv'):
    old_df = pd.read_csv('output/primordial_system_prompt_notes.csv')
    df = pd.concat([df,old_df])
#df = df.drop_duplicates()
df.to_csv('output/primordial_system_prompt_notes.csv',index=False)
df.to_json('output/primordial_system_prompt_notes.json', orient="columns")
duration = (start_time - time.time())/60
print(f"Saved output/primordial_system_prompt_notes.csv {duration:.01f} min")


print(df.describe())