# run_games.py
"""
Game validation and Monte Carlo simulation runner.

This module provides:
1. Single-shot validation tests for each game
2. Monte Carlo simulations to test strategy distributions and payoffs
"""

from src.games import (
    DictatorGame,
    UltimatumGame,
    PublicGoodsGame,
    TrustGame,
    PrisonerDilemma,
    VolunteerDilemma,
)


# ============================================================================
# SINGLE-SHOT VALIDATION TESTS
# ============================================================================

def test_dictator():
    """Test Dictator game with submit_strategy pattern."""
    g = DictatorGame(endowment=100)
    g.submit_strategy(0, 0.3)  # dictator gives 30%
    payoffs = g.play()
    print("Dictator Game:", payoffs, "Expected:", [70, 30])


def test_ultimatum():
    """Test Ultimatum game with accept/reject scenarios."""
    g = UltimatumGame(endowment=100)
    g.submit_strategy(0, 0.4)  # proposer offers 40%
    g.submit_strategy(1, 0.3)  # responder accepts ≥30%
    payoffs = g.play()
    print("Ultimatum Game:", payoffs, "Expected: accepted, [60, 40]")

    # Try rejection case
    g = UltimatumGame(endowment=100)
    g.submit_strategy(0, 0.2)
    g.submit_strategy(1, 0.3)
    payoffs = g.play()
    print("Ultimatum (reject):", payoffs, "Expected: [0, 0]")


def test_public_good():
    """Test Public Goods game with multiple players."""
    g = PublicGoodsGame(n_players=4, endowment=100, multiplier=1.6)
    for i in range(4):
        g.submit_strategy(i, 0.25)  # everyone contributes 25%
    payoffs = g.play()
    print("Public Goods:", payoffs, "Expected all same")


def test_trust():
    """Test Trust game with investor/trustee interaction."""
    g = TrustGame(endowment=100, multiplier=3)
    g.submit_strategy(0, 0.5)   # investor sends 50%
    g.submit_strategy(1, 0.3)   # trustee returns 30% of received
    payoffs = g.play()
    print("Trust Game:", payoffs, "Expected investor > 100? depends on return")


def test_prisoner():
    """Test Prisoner's Dilemma with cooperation and defection."""
    g = PrisonerDilemma()
    g.submit_strategy(0, 'D')
    g.submit_strategy(1, 'D')
    payoffs = g.play()
    print("Prisoner's Dilemma (D,D):", payoffs, "Expected Nash: mutual defection [1,1]")

    g = PrisonerDilemma()
    g.submit_strategy(0, 'C')
    g.submit_strategy(1, 'C')
    payoffs = g.play()
    print("Prisoner's Dilemma (C,C):", payoffs, "Expected cooperative [3,3]")


def test_volunteer():
    """Test Volunteer's Dilemma with one volunteer."""
    g = VolunteerDilemma(n_players=3, cost=20, benefit=100)
    g.submit_strategy(0, True)
    g.submit_strategy(1, False)
    g.submit_strategy(2, False)
    payoffs = g.play()
    print("Volunteer Dilemma:", payoffs, "Expected: [80,100,100]")


# ============================================================================
# MONTE CARLO SIMULATIONS
# ============================================================================

def mc_dictator():
    """Monte Carlo simulation for Dictator game."""
    print("\n=== Dictator Game Monte Carlo ===")
    g = DictatorGame(endowment=100)

    # Test different offer levels
    strategy_space = [
        [0.0, 0.1, 0.2, 0.3, 0.4, 0.5],  # dictator offers
    ]

    results = g.monte_carlo(strategy_space, n_rounds=10_000)
    print(f"Average payoffs over {results['n_rounds']} rounds:")
    print(f"  Dictator: {results['avg_payoffs'][0]:.2f}")
    print(f"  Recipient: {results['avg_payoffs'][1]:.2f}")
    print(f"  Expected: Dictator ~62.5, Recipient ~37.5 (uniform distribution)")


def mc_ultimatum():
    """Monte Carlo simulation for Ultimatum game."""
    print("\n=== Ultimatum Game Monte Carlo ===")
    g = UltimatumGame(endowment=100)

    # Proposer offers: 0% to 50%, Responder thresholds: 10% to 40%
    strategy_space = [
        [0.0, 0.1, 0.2, 0.3, 0.4, 0.5],  # proposer offers
        [0.1, 0.2, 0.3, 0.4],             # responder minimum acceptance
    ]

    results = g.monte_carlo(strategy_space, n_rounds=10_000)
    print(f"Average payoffs over {results['n_rounds']} rounds:")
    print(f"  Proposer: {results['avg_payoffs'][0]:.2f}")
    print(f"  Responder: {results['avg_payoffs'][1]:.2f}")
    print(f"  Note: Many rejections expected, bringing averages down")


def mc_prisoner():
    """Monte Carlo simulation for Prisoner's Dilemma."""
    print("\n=== Prisoner's Dilemma Monte Carlo ===")
    g = PrisonerDilemma()

    # Equal probability of cooperation and defection
    strategy_space = [
        ['C', 'D'],  # player 0 actions
        ['C', 'D'],  # player 1 actions
    ]

    results = g.monte_carlo(strategy_space, n_rounds=10_000)
    print(f"Average payoffs over {results['n_rounds']} rounds:")
    print(f"  Player 0: {results['avg_payoffs'][0]:.2f}")
    print(f"  Player 1: {results['avg_payoffs'][1]:.2f}")
    print(f"  Expected: ~2.25 each (C,C)=3, (C,D)=0, (D,C)=5, (D,D)=1")
    print(f"  Nash equilibrium: (D,D) = 1 each")


def mc_public_good():
    """Monte Carlo simulation for Public Goods game."""
    print("\n=== Public Goods Game Monte Carlo ===")
    g = PublicGoodsGame(n_players=4, endowment=100, multiplier=1.6)

    # Contribution levels from 0% to 100%
    contribution_levels = [0.0, 0.25, 0.5, 0.75, 1.0]
    strategy_space = [contribution_levels] * 4  # same options for all players

    results = g.monte_carlo(strategy_space, n_rounds=10_000)
    print(f"Average payoffs over {results['n_rounds']} rounds:")
    for i, payoff in enumerate(results['avg_payoffs']):
        print(f"  Player {i}: {payoff:.2f}")
    print(f"  Expected: All similar due to symmetry, ~100 with random contributions")


def mc_trust():
    """Monte Carlo simulation for Trust game."""
    print("\n=== Trust Game Monte Carlo ===")
    g = TrustGame(endowment=100, multiplier=3)

    # Investor sends 0-100%, Trustee returns 0-50% of tripled amount
    strategy_space = [
        [0.0, 0.25, 0.5, 0.75, 1.0],  # investor sends
        [0.0, 0.1, 0.2, 0.3, 0.4, 0.5],  # trustee returns fraction
    ]

    results = g.monte_carlo(strategy_space, n_rounds=10_000)
    print(f"Average payoffs over {results['n_rounds']} rounds:")
    print(f"  Investor: {results['avg_payoffs'][0]:.2f}")
    print(f"  Trustee: {results['avg_payoffs'][1]:.2f}")
    print(f"  Expected: Depends on return rate, investor baseline is 100")


def mc_volunteer():
    """Monte Carlo simulation for Volunteer's Dilemma."""
    print("\n=== Volunteer Dilemma Monte Carlo ===")
    g = VolunteerDilemma(n_players=3, cost=20, benefit=100)

    # Each player volunteers or not (50/50)
    strategy_space = [
        [True, False],  # player 0
        [True, False],  # player 1
        [True, False],  # player 2
    ]

    results = g.monte_carlo(strategy_space, n_rounds=10_000)
    print(f"Average payoffs over {results['n_rounds']} rounds:")
    for i, payoff in enumerate(results['avg_payoffs']):
        print(f"  Player {i}: {payoff:.2f}")
    print(f"  Expected: ~77.5 each")
    print(f"  Probability no volunteer: 12.5% (0 payoff)")
    print(f"  Probability 1 volunteer: 37.5% (80 for volunteer, 100 for others)")
    print(f"  Probability 2+ volunteers: 50% (80 for volunteers, 100 or 80 for others)")


# ============================================================================
# MAIN RUNNER
# ============================================================================

def run_validation_tests():
    """Run all single-shot validation tests."""
    print("=" * 60)
    print("SINGLE-SHOT GAME VALIDATION TESTS")
    print("=" * 60)
    test_dictator()
    test_ultimatum()
    test_public_good()
    test_trust()
    test_prisoner()
    test_volunteer()


def run_monte_carlo_simulations():
    """Run all Monte Carlo simulations."""
    print("\n" + "=" * 60)
    print("MONTE CARLO SIMULATIONS")
    print("=" * 60)
    mc_dictator()
    mc_ultimatum()
    mc_prisoner()
    mc_public_good()
    mc_trust()
    mc_volunteer()


if __name__ == "__main__":
    run_validation_tests()
    run_monte_carlo_simulations()

    print("\n" + "=" * 60)
    print("All tests and simulations complete!")
    print("=" * 60)
