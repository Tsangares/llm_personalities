from .game_model import *
from .persona_model import *
from .response_models import *

from datetime import datetime
from ollama import chat, Client
import pandas as pd
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Type


# ============================================================================
# GAME RUNNER
# ============================================================================

class GameRunner:
    """Orchestrates running behavioral games with LLM personas"""
    
    def __init__(self, client: Client, model: str = ""):
        self.client = client
        self.model = model
        self.results: List[Dict] = []
        
    def run_single_round(
        self,
        game: Game,
        persona: Persona,
        round_num: int = 1,
        temperature: float = 1.0,
        context: Optional[Dict] = None,
        verbose: bool = True
    ) -> BaseModel:
        """
        Run a single round of a game with a persona
        
        Args:
            game: The game instance to play
            persona: The persona to use
            round_num: Current round number
            temperature: Sampling temperature for LLM
            context: Additional context to pass to game prompt
            verbose: Print progress messages
            
        Returns:
            Pydantic model instance with structured response
        """
        if verbose:
            print(f"\n{'='*60}")
            print(f"Round {round_num}: {game.name}")
            print(f"Persona: {persona.name}")
            print(f"{'='*60}")
        
        # Get game prompt with any additional context
        game_context = context or {}
        
        # Add history to context if game has been played before
        if game.history and round_num > 1:
            game_context['history'] = game.get_history_summary()
        
        user_prompt = game.get_prompt(round_num=round_num, **game_context)
        
        if verbose:
            print(f"\nPrompt:\n{user_prompt[:200]}...")
        
        # Get response model for this game
        response_model = game.get_response_model()
        
        # Call Ollama with structured output
        try:
            response = self.client.chat(
                model=self.model,
                messages=[
                    {
                        'role': 'system',
                        'content': persona.get_full_system_prompt()
                    },
                    {
                        'role': 'user',
                        'content': user_prompt
                    }
                ],
                format=response_model.model_json_schema(),
                options={'temperature': temperature}
            )
            
            # Parse response into Pydantic model
            structured_response = response_model.model_validate_json(
                response.message.content
            )
            
            if verbose:
                print(f"\nResponse:\n{structured_response.model_dump_json(indent=2)}")
            
            # Record this round in the game
            game.record_round(
                round_num=round_num,
                response=structured_response,
                persona=persona.name,
                model=self.model,
                temperature=temperature
            )
            
            # Store in results
            self.results.append({
                'timestamp': datetime.now().isoformat(),
                'game': game.name,
                'persona': persona.name,
                'round': round_num,
                'model': self.model,
                'temperature': temperature,
                'response': structured_response.model_dump(),
                'raw_content': response.message.content
            })
            
            return structured_response
            
        except Exception as e:
            print(f"Error in round {round_num}: {e}")
            raise
    
    def run_repeated_game(
        self,
        game: Game,
        persona: Persona,
        num_rounds: int,
        temperature: float = 1.0,
        context: Optional[Dict] = None,
        verbose: bool = True
    ) -> List[BaseModel]:
        """
        Run multiple rounds of a game with the same persona
        
        Returns:
            List of Pydantic model responses, one per round
        """
        responses = []
        
        for round_num in range(1, num_rounds + 1):
            response = self.run_single_round(
                game=game,
                persona=persona,
                round_num=round_num,
                temperature=temperature,
                context=context,
                verbose=verbose
            )
            responses.append(response)
        
        return responses
    
    def run_experiment(
        self,
        games: List[Game],
        personas: List[Persona],
        rounds_per_game: int = 1,
        temperature: float = 1.0,
        replications: int = 1,
        verbose: bool = True
    ) -> pd.DataFrame:
        """
        Run a full factorial experiment across games and personas
        
        Args:
            games: List of game instances to play
            personas: List of personas to test
            rounds_per_game: Number of rounds for each game
            temperature: Sampling temperature
            replications: Number of times to repeat each game-persona combination
            verbose: Print progress
            
        Returns:
            DataFrame with all experimental results
        """
        total_runs = len(games) * len(personas) * replications
        current_run = 0
        
        for replication in range(1, replications + 1):
            for game in games:
                for persona in personas:
                    current_run += 1
                    
                    if verbose:
                        print(f"\n\n{'#'*60}")
                        print(f"Run {current_run}/{total_runs} - Replication {replication}")
                        print(f"Game: {game.name} | Persona: {persona.name}")
                        print(f"{'#'*60}")
                    
                    # Reset game history for new persona
                    game.history = []
                    
                    # Run the repeated game
                    self.run_repeated_game(
                        game=game,
                        persona=persona,
                        num_rounds=rounds_per_game,
                        temperature=temperature,
                        verbose=verbose
                    )
        
        # Convert results to DataFrame
        return pd.DataFrame(self.results)
    
    def save_results(self, filepath: str):
        """Save results to CSV"""
        df = pd.DataFrame(self.results)
        df.to_csv(filepath, index=False)
        print(f"\nResults saved to {filepath}")
        
    def get_results_df(self) -> pd.DataFrame:
        """Get results as pandas DataFrame"""
        return pd.DataFrame(self.results)
