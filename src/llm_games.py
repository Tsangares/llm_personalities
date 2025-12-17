import csv
import os
from src.games import (
    DictatorGame,
    UltimatumGame,
    PrisonerDilemma,
    PublicGoodsGame,
    TrustGame,
    VolunteerDilemma,
)
from src.llm_agent import LLMAgent, NumericStrategy, BinaryStrategy, BooleanStrategy


GAMES = {
    "dictator": (DictatorGame, NumericStrategy, ["Dictator", "Recipient"], 1),
    "ultimatum": (UltimatumGame, NumericStrategy, ["Proposer", "Responder"], 2),
    "prisoner": (PrisonerDilemma, BinaryStrategy, ["Player 1", "Player 2"], 2),
    "public_good": (PublicGoodsGame, NumericStrategy, ["Player 1", "Player 2", "Player 3", "Player 4"], 4),
    "trust": (TrustGame, NumericStrategy, ["Investor", "Trustee"], 2),
    "volunteer": (VolunteerDilemma, BooleanStrategy, ["Player 1", "Player 2", "Player 3"], 3),
}


def run_game(game_key, model=None):
    if game_key not in GAMES:
        print(f"Unknown game: {game_key}")
        print(f"Available games: {list(GAMES.keys())}")
        return

    game_class, response_model, roles, num_agents = GAMES[game_key]
    game = game_class()
    agent = LLMAgent(model=model)

    print(f"\n=== {game_class.__name__} ===")
    print(f"Model: {agent.client.model}\n")

    strategies = []
    for i in range(num_agents):
        role = roles[i]
        rules = get_game_rules(game, role, i)
        print(f"{role} is thinking...")

        result = agent.get_strategy(
            game_name=game_class.__name__,
            role=role,
            rules=rules,
            response_model=response_model
        )

        if result is None:
            print(f"Failed to get strategy from {role}")
            return

        strategy = extract_strategy(result, response_model)
        strategies.append(strategy)
        print(f"{role} chose: {strategy}\n")

    payoffs = game.play(strategies)
    print("Results:")
    for i, payoff in enumerate(payoffs):
        role = roles[i] if i < len(roles) else f"Player {i+1}"
        print(f"  {role}: {payoff:.2f}")


def get_game_rules(game, role, player_index):
    rules_attr = getattr(game.__class__, "GAME_RULES", None)

    if game.__class__.__name__ == "UltimatumGame":
        rules_attr = game.__class__.PROPOSER_RULES if player_index == 0 else game.__class__.RESPONDER_RULES
    elif game.__class__.__name__ == "TrustGame":
        rules_attr = game.__class__.INVESTOR_RULES if player_index == 0 else game.__class__.TRUSTEE_RULES

    if rules_attr:
        return rules_attr.format(
            endowment=game.endowment,
            multiplier=game.params.get("multiplier", ""),
            n_players=game.num_players,
            cost=game.params.get("cost", ""),
            benefit=game.params.get("benefit", "")
        )
    return "Play the game strategically."


def extract_strategy(result, response_model):
    if response_model == NumericStrategy:
        return result.value
    elif response_model == BinaryStrategy:
        return result.choice.upper()
    elif response_model == BooleanStrategy:
        return result.decision
    return None


def run_simulation(game_key, n_rounds=50, model=None, verbose=False):
    if game_key not in GAMES:
        print(f"Unknown game: {game_key}")
        return []

    game_class, response_model, roles, num_agents = GAMES[game_key]
    agent = LLMAgent(model=model)

    results = []
    print(f"\nRunning {n_rounds} rounds of {game_class.__name__}...")

    for round_num in range(n_rounds):
        game = game_class()
        strategies = []

        for i in range(num_agents):
            role = roles[i]
            rules = get_game_rules(game, role, i)

            result = agent.get_strategy(
                game_name=game_class.__name__,
                role=role,
                rules=rules,
                response_model=response_model
            )

            if result is None:
                print(f"Round {round_num+1}: Failed to get strategy from {role}")
                continue

            strategy = extract_strategy(result, response_model)
            strategies.append(strategy)

        if len(strategies) == num_agents:
            payoffs = game.play(strategies)

            for i in range(num_agents):
                results.append({
                    'round': round_num + 1,
                    'game': game_class.__name__,
                    'player': i,
                    'role': roles[i],
                    'decision': strategies[i],
                    'payoff': payoffs[i]
                })

        if verbose or (round_num + 1) % 10 == 0:
            print(f"  Completed round {round_num + 1}/{n_rounds}")

    return results


def export_to_csv(results, filename):
    os.makedirs('output', exist_ok=True)
    filepath = os.path.join('output', filename)

    if not results:
        print("No results to export")
        return

    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['round', 'game', 'player', 'role', 'decision', 'payoff'])
        writer.writeheader()
        writer.writerows(results)

    print(f"\nExported {len(results)} records to {filepath}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--simulate":
        game_key = sys.argv[2] if len(sys.argv) > 2 else "dictator"
        n_rounds = int(sys.argv[3]) if len(sys.argv) > 3 else 50
        model = sys.argv[4] if len(sys.argv) > 4 else None

        results = run_simulation(game_key, n_rounds=n_rounds, model=model)
        export_to_csv(results, f"{game_key}_simulation.csv")
    else:
        game_key = sys.argv[1] if len(sys.argv) > 1 else "dictator"
        model = sys.argv[2] if len(sys.argv) > 2 else None

        run_game(game_key, model)
