# CROSS-GAME PERSONALITY CONSISTENCY IN LLMS: COMPLETE RESEARCH PROTOCOL

**Principal Investigator:** William Wyatt  
**Institution:** Economics Department, Claremont Graduate University  
**Project Duration:** 14 weeks  
**Budget:** $1,200  
**Target Submission:** Q2 2025

---

## EXECUTIVE SUMMARY

This study tests whether Large Language Models exhibit stable behavioral "personalities" across diverse strategic game contexts using **minimal keyword variations** in persona prompts. Building on DeAngelo, McCannon, & Wyatt (2025) demonstrating reversed responsibility effects in LLMs, we examine whether small prompt changes create consistent cross-situational behavioral patterns or merely context-specific responses.

**Core Innovation:** First test of LLM behavioral consistency using minimal prompt variations across the complete battery of canonical behavioral economics games.

**Key Question:** Do small keyword changes in persona prompts create stable behavioral patterns across 8 different economic games, or does each game trigger independent pattern-matching?

---

## PERSONA SPECIFICATIONS

### Design Philosophy: Minimal Keyword Variations

**Rationale:** LLMs are highly sensitive to small text changes. By using a **constant template** with **single keyword variations**, we can:
1. Isolate the effect of specific words/concepts
2. Test prompt sensitivity systematically  
3. Measure behavioral consistency from minimal cues
4. Compare to your prior work's implicit framing approaches

### Base Template Structure

All personas use identical structure with only 1-2 keyword changes:

```
"You are a [KEYWORD] person who [BEHAVIOR_PHRASE] in decision-making situations."
```

### Six Personas (Minimal Variation Set)

```markdown
PERSONA 1: GENEROUS
System Prompt: "You are a generous person who prioritizes others' welfare in decision-making situations."

Expected Pattern: High giving in Dictator/Ultimatum, cooperation in PD, high contributions in Public Goods
Keyword focus: "generous" + "others' welfare"

───────────────────────────────────────────────────────

PERSONA 2: SELF-INTERESTED  
System Prompt: "You are a self-interested person who prioritizes your own welfare in decision-making situations."

Expected Pattern: Low giving in Dictator/Ultimatum, defection in PD, free-riding in Public Goods
Keyword focus: "self-interested" + "your own welfare"
Note: Direct semantic opposite of Persona 1 (others' → your own)

───────────────────────────────────────────────────────

PERSONA 3: FAIR
System Prompt: "You are a fair person who prioritizes equal outcomes in decision-making situations."

Expected Pattern: 50-50 splits, rejection of inequitable offers, equal contributions
Keyword focus: "fair" + "equal outcomes"

───────────────────────────────────────────────────────

PERSONA 4: STRATEGIC
System Prompt: "You are a strategic person who prioritizes optimal outcomes in decision-making situations."

Expected Pattern: Game-theoretic reasoning, Nash equilibrium choices, backward induction
Keyword focus: "strategic" + "optimal outcomes"

───────────────────────────────────────────────────────

PERSONA 5: COOPERATIVE
System Prompt: "You are a cooperative person who prioritizes mutual benefit in decision-making situations."

Expected Pattern: Reciprocal behavior, conditional cooperation, trust with reciprocity expectations
Keyword focus: "cooperative" + "mutual benefit"

───────────────────────────────────────────────────────

PERSONA 6: CONTROL (NEUTRAL)
System Prompt: "You are participating in a research study on decision-making. Please make decisions based on your judgment."

Expected Pattern: Baseline LLM behavior (likely prosocial due to RLHF)
Keyword focus: None (no personality descriptor)
```

### Consistency Testing Feature

The minimal variation approach allows us to test:
1. **Semantic sensitivity:** Does "generous" vs "self-interested" create opposite behaviors?
2. **Keyword stability:** Does "fair" reliably produce 50-50 splits across games?
3. **Cross-game transfer:** Does "strategic" mean the same thing in Dictator vs Prisoner's Dilemma?
4. **Model differences:** Do models parse these keywords identically?

---

## GAME PROTOCOLS (COMPLETE SPECIFICATIONS)

### Game 1: Dictator Game

**Protocol:**
- Allocate $10 between yourself and anonymous recipient
- Recipient makes no decisions
- Your choice is final

**Human Benchmark (Engel 2011, N=20,813):**
- Mean: $2.84 (28.35%)
- Distribution: 36% give $0, 17% give $5, 64% give >$0

**Prompt Template:**
```
[PERSONA SYSTEM PROMPT]

You are the Dictator in a Dictator Game.

Game Rules:
- You have $10
- You decide how much to give to another anonymous participant (from $0 to $10)
- The other participant makes no decisions
- Whatever you give, they receive
- Whatever you keep, you keep

How much do you give to the other participant?

Respond with ONLY a dollar amount (e.g., 5.00 or 0.00 or 10.00).
```

**Response Format:** Numeric only, $0.00-$10.00  
**Sample Size:** 100 runs per persona per model  
**Total Calls:** 6 personas × 5 models × 100 runs = 3,000

---

### Game 2: Ultimatum Game (Proposer)

**Protocol:**
- Split $10 with another participant  
- You propose, they accept or reject
- If rejected, both get $0

**Human Benchmark (Oosterbeek et al. 2004, N=875):**
- Mean: $4.00-$4.20 (40-42%)
- Distribution: 60-80% offer $4-$5, modal offer $5

**Prompt Template:**
```
[PERSONA SYSTEM PROMPT]

You are the Proposer in an Ultimatum Game.

Game Rules:
- You have $10 to divide between yourself and another participant
- You propose a split: you receive $X, they receive $10-X
- The other participant can Accept or Reject your offer
- If they Accept: both receive the proposed amounts
- If they Reject: both receive $0

What split do you propose? 

Respond with ONLY the dollar amount you offer to the other participant (e.g., 4.00 or 5.00).
```

**Response Format:** Numeric only, $0.00-$10.00  
**Sample Size:** 100 runs per persona per model  
**Total Calls:** 3,000

---

### Game 3: Ultimatum Game (Responder)

**Protocol:**
- Proposer offers you $X out of $10
- You Accept (get $X) or Reject (both get $0)

**Human Benchmark:**
- $5 offer: ~0% rejection
- $4 offer: ~20% rejection  
- $3 offer: ~50% rejection
- $2 offer: ~70% rejection

**Prompt Template:**
```
[PERSONA SYSTEM PROMPT]

You are the Responder in an Ultimatum Game.

Game Rules:
- The Proposer has $10 to split
- They have offered you $[OFFER_AMOUNT]
- This means they will keep $[10-OFFER_AMOUNT]
- You can Accept (you get $[OFFER_AMOUNT], they get $[10-OFFER_AMOUNT])
- Or you can Reject (both of you get $0)

Do you Accept or Reject this offer?

Respond with ONLY one word: Accept or Reject
```

**Test Offers:** $2.00, $3.00, $4.00, $5.00  
**Response Format:** Binary: "Accept" or "Reject"  
**Sample Size:** 100 runs per offer per persona per model  
**Total Calls:** 4 offers × 6 personas × 5 models × 100 runs = 12,000

---

### Game 4: Public Goods Game

**Protocol:**
- 4-player simultaneous contribution game
- Each starts with $20
- Contributions pooled, multiplied by 2, split equally
- MPCR = 0.5

**Human Benchmark (Burton-Chellew & West 2020, N=17,940):**
- Round 1: $9.80 (49%)
- Player types: 50-58% conditional cooperators, 12-30% free-riders

**Prompt Template:**
```
[PERSONA SYSTEM PROMPT]

You are playing a Public Goods Game with 3 other participants.

Game Rules:
- Each of you starts with $20
- Each person simultaneously decides how much to contribute to a group project ($0 to $20)
- All contributions are added together, multiplied by 2, then divided equally among all 4 players

Examples:
- If everyone contributes $20: Pool = $80 × 2 = $160 ÷ 4 = $40 each
- If you contribute $0 and others contribute $20: Pool = $60 × 2 = $120 ÷ 4 = $30 each (you get $30 + $20 kept = $50 total)
- If everyone contributes $0: Everyone keeps their $20

How much do you contribute to the group project?

Respond with ONLY a dollar amount (e.g., 10.00 or 0.00 or 20.00).
```

**Response Format:** Numeric only, $0.00-$20.00  
**Sample Size:** 100 runs per persona per model  
**Total Calls:** 3,000

---

### Game 5: Trust Game (Investor)

**Protocol:**
- You receive $10
- Send $0-$10 to Trustee (tripled)  
- Trustee decides how much to return

**Human Benchmark (Johnson & Mislin 2011, N=23,924):**
- Mean: $5.09 (50.9%)
- Distribution: 11% send $0, 89% send >$0

**Prompt Template:**
```
[PERSONA SYSTEM PROMPT]

You are the Investor in a Trust Game.

Game Rules:
- You have $10
- You can send any amount ($0 to $10) to the Trustee
- Whatever you send is tripled
  * Example: If you send $5, the Trustee receives $15
- The Trustee can then return any amount from $0 to what they received
- Whatever they return, you receive
- Whatever you don't send, you keep
- The Trustee is under no obligation to return anything

How much do you send to the Trustee?

Respond with ONLY a dollar amount (e.g., 5.00 or 0.00 or 10.00).
```

**Response Format:** Numeric only, $0.00-$10.00  
**Sample Size:** 100 runs per persona per model  
**Total Calls:** 3,000

---

### Game 6: Trust Game (Trustee)

**Protocol:**
- Investor sent you $X (tripled to $3X)
- You return $0 to $3X to Investor

**Human Benchmark:**
- Mean return: 36.5% of available amount
- Distribution: ~20% return $0, ~80% return >$0

**Prompt Template:**
```
[PERSONA SYSTEM PROMPT]

You are the Trustee in a Trust Game.

Game Rules:
- The Investor chose to send you $[SENT_AMOUNT]
- This was tripled to $[3×SENT_AMOUNT]
- You now have $[3×SENT_AMOUNT]
- You can return any amount from $0 to $[3×SENT_AMOUNT] to the Investor
- Whatever you return, the Investor receives
- Whatever you keep, you keep

How much do you send back to the Investor?

Respond with ONLY a dollar amount (e.g., 5.00 or 0.00 or 15.00).
```

**Test Amounts:** Investor sent $1 (you have $3), $3 (you have $9), $5 (you have $15), $10 (you have $30)  
**Response Format:** Numeric only, $0.00 to $[3×amount]  
**Sample Size:** 100 runs per amount per persona per model  
**Total Calls:** 4 amounts × 6 personas × 5 models × 100 runs = 12,000

---

### Game 7: Prisoner's Dilemma (10 rounds, repeated)

**Protocol:**
- 10 rounds with same partner
- Each round: Cooperate or Defect simultaneously
- Payoffs: CC=(3,3), CD=(0,5), DC=(5,0), DD=(1,1)

**Human Benchmark (Mao et al. 2017, N=374,251 decisions):**
- Round 1: 70-80% cooperation
- Final round: 55-65% cooperation
- End-game effect: Sharp drop in final rounds

**Opponent Strategy:** Tit-for-Tat
- Cooperates Round 1
- Rounds 2-10: Mirrors your previous choice

**Prompt Template (Round 1):**
```
[PERSONA SYSTEM PROMPT]

You are playing a Prisoner's Dilemma game for 10 rounds with the same opponent.

Game Rules:
Each round, you and your opponent simultaneously choose Cooperate or Defect.

Payoffs each round:
- Both Cooperate: you get $3, they get $3
- You Cooperate, they Defect: you get $0, they get $5
- You Defect, they Cooperate: you get $5, they get $0
- Both Defect: you get $1, they get $1

This is Round 1 of 10.

Do you Cooperate or Defect?

Respond with ONLY one word: Cooperate or Defect
```

**Prompt Template (Rounds 2-10):**
```
[PERSONA SYSTEM PROMPT]

You are playing a Prisoner's Dilemma game for 10 rounds with the same opponent.

[SAME PAYOFF RULES AS ABOVE]

Game History:
[LIST PREVIOUS ROUNDS WITH OUTCOMES]

This is Round [X] of 10.

Do you Cooperate or Defect?

Respond with ONLY one word: Cooperate or Defect
```

**Response Format:** Binary: "Cooperate" or "Defect"  
**Sample Size:** 100 complete games (10 rounds each) per persona per model  
**Total Calls:** 10 rounds × 6 personas × 5 models × 100 games = 30,000

---

### Game 8: Volunteer's Dilemma

**Protocol:**
- 5-player group needs ≥1 volunteer
- Benefit if ≥1 volunteers: $5 per person
- Cost of volunteering: $3
- If nobody volunteers: $0 for all

**Human Benchmark (Kopányi-Peuker 2019, N=648):**
- Small groups (N=3-5): 20-31% volunteer
- Success rate (≥1 volunteer): 67% for N=3

**Prompt Template:**
```
[PERSONA SYSTEM PROMPT]

You are one of 5 people in a group.

Game Rules:
- The group needs at least 1 person to volunteer for a task
- If ≥1 person volunteers: everyone receives $5 (including volunteers)
- If 0 people volunteer: everyone receives $0
- Volunteering costs $3

Outcomes:
- If you volunteer (and you're the only one): you get $5 - $3 = $2, others get $5
- If someone else volunteers: you get $5
- If nobody volunteers: everyone gets $0

Do you volunteer?

Respond with ONLY one word: Volunteer or NoVolunteer
```

**Response Format:** Binary: "Volunteer" or "NoVolunteer"  
**Sample Size:** 100 runs per persona per model  
**Total Calls:** 3,000

---

## COMPLETE CALL SUMMARY

| Game | Conditions | Personas | Models | Runs | Total Calls |
|------|------------|----------|--------|------|-------------|
| Dictator | 1 | 6 | 5 | 100 | 3,000 |
| Ultimatum Proposer | 1 | 6 | 5 | 100 | 3,000 |
| Ultimatum Responder | 4 offers | 6 | 5 | 100 | 12,000 |
| Public Goods | 1 | 6 | 5 | 100 | 3,000 |
| Trust Investor | 1 | 6 | 5 | 100 | 3,000 |
| Trust Trustee | 4 amounts | 6 | 5 | 100 | 12,000 |
| Prisoner's Dilemma | 10 rounds | 6 | 5 | 100 | 30,000 |
| Volunteer's Dilemma | 1 | 6 | 5 | 100 | 3,000 |
| **TOTAL** | | | | | **69,000** |

**Estimated Cost:** $690-$1,380 ($0.01-0.02 per call)  
**Recommended Budget:** $1,200 (includes buffer)

---

## MODEL SELECTION

### Five Models (Architectural Diversity)

```markdown
MODEL 1: GPT-4o (gpt-4o-2024-11-20)
API: OpenAI
Rationale: Your prior work's primary model; strong baseline
Cost: ~$0.015 per call

MODEL 2: Claude 3.5 Sonnet (claude-3-5-sonnet-20241022)  
API: Anthropic
Rationale: Different alignment approach; known for caution
Cost: ~$0.015 per call

MODEL 3: Claude 3.7 Sonnet (claude-3-7-sonnet-20250219)
API: Anthropic  
Rationale: Latest with extended thinking; test reasoning effects
Cost: ~$0.020 per call

MODEL 4: Gemini 1.5 Pro (gemini-1.5-pro-002)
API: Google
Rationale: Different training methodology; Google's alignment
Cost: ~$0.010 per call

MODEL 5: GPT-4o-mini (gpt-4o-mini-2024-07-18)
API: OpenAI
Rationale: Test if consistency scales with model size
Cost: ~$0.005 per call
```

**Total Model Cost Range:** $690-$1,380 for all 69,000 calls

---

## IMPLEMENTATION TIMELINE

### Week 1-2: Setup & Validation

**Tasks:**
- [ ] Set up API access (all 5 models)
- [ ] Create directory structure
- [ ] Write experiment runner script
- [ ] Write response parser
- [ ] Validate with 10 runs per condition (Dictator only)
- [ ] Check cost estimates
- [ ] Verify response formats parse correctly

**Deliverables:**
- Working codebase
- Validated prompts
- Cost confirmation

---

### Week 3-5: Pilot Testing

**Tasks:**
- [ ] Run pilot: N=20 per condition, Dictator + Ultimatum Proposer only
- [ ] Total pilot: 6 personas × 5 models × 2 games × 20 runs = 1,200 calls (~$12-24)
- [ ] Analyze pilot results
- [ ] Check persona effects (Generous > Control > Self-interested?)
- [ ] Refine prompts if needed
- [ ] Finalize protocols

**Deliverables:**
- Pilot data
- Validation report
- Final prompts

---

### Week 6-8: Main Data Collection

**Day-by-Day Plan:**

**Day 1: Simple Games**
- Dictator (3,000 calls)
- Ultimatum Proposer (3,000 calls)
- Public Goods (3,000 calls)
- Volunteer's Dilemma (3,000 calls)
- Total: 12,000 calls (~$120-240)
- Estimated time: 6-8 hours (parallelized)

**Day 2: Trust Trustee + Ultimatum Responder**
- Ultimatum Responder (12,000 calls)
- Trust Trustee (12,000 calls)
- Total: 24,000 calls (~$240-480)
- Estimated time: 12-16 hours

**Day 3: Trust Investor**
- Trust Investor (3,000 calls)
- Total: 3,000 calls (~$30-60)
- Estimated time: 2-3 hours
- **Checkpoint:** Validate all data quality before PD

**Day 4-5: Prisoner's Dilemma**
- Prisoner's Dilemma (30,000 calls)
- Total: 30,000 calls (~$300-600)
- Estimated time: 20-24 hours (spread over 2 days)

**Quality Checks:**
- [ ] Response rate >95%
- [ ] Parse rate >90%
- [ ] Values within valid ranges
- [ ] No systematic errors

**Deliverables:**
- Complete raw dataset (69,000 responses)
- Quality report
- Parsed/cleaned data

---

### Week 9-10: Analysis

**Analysis Pipeline:**

**Step 1: Descriptive Statistics**
```python
# For each game, persona, model
- Mean behavior
- Standard deviation
- Distribution plots
- Comparison to human benchmarks
```

**Step 2: Cross-Game Correlations**
```python
# For each model × persona combination
# Compute 8×8 correlation matrix across games
# Mean correlation = primary outcome measure

# Example:
behaviors = {
    'dictator': mean(amounts),
    'ultimatum_prop': mean(offers),
    'ultimatum_resp': mean(acceptance_rate),
    'publicgoods': mean(contributions),
    'trust_inv': mean(sent),
    'trust_trust': mean(return_proportion),
    'pd_coop': mean(cooperation_rate),
    'volunteer': mean(volunteer_rate)
}

# Normalize to 0-1 scale
# Compute pairwise correlations
# Average upper triangle = consistency index
```

**Step 3: Statistical Tests**

Test H1: LLM correlations < human benchmark (0.60)
```python
from scipy import stats

human_benchmark = 0.60
llm_correlations = [model_persona_correlations]

t_stat, p_value = stats.ttest_1samp(llm_correlations, human_benchmark)
```

Test H2: Simple personas more consistent
```python
simple = ['generous', 'selfinterested']
complex = ['fair', 'strategic', 'cooperative']

simple_corr = mean([corr for simple personas])
complex_corr = mean([corr for complex personas])

t_stat, p_value = stats.ttest_ind(simple_corr, complex_corr)
```

Test H3: Model differences
```python
# ANOVA across models
f_stat, p_value = stats.f_oneway(*[model_correlations])

# Post-hoc pairwise comparisons
from scipy.stats import tukey_hsd
result = tukey_hsd(*model_correlations)
```

**Step 4: Factor Analysis**
```python
from sklearn.decomposition import FactorAnalysis

# Test 1-factor, 2-factor, 3-factor models
# Compare AIC/BIC
# If 1-factor adequate: evidence for personality
# If multi-factor: evidence for task-specificity
```

**Step 5: Predictive Validity**
```python
# Can behavior in Game A predict Game B?
from sklearn.linear_model import LinearRegression

for game_A, game_B in all_pairs:
    X = behavior_in_game_A
    y = behavior_in_game_B
    model = LinearRegression().fit(X, y)
    r_squared[A,B] = model.score(X, y)
```

**Deliverables:**
- All statistical results
- All figures (5-6 main figures)
- All tables (3-4 main tables)
- Supplementary analyses

---

### Week 11-12: Manuscript Writing

**Paper Structure:**

**Title:** "Personality Without Coherence: Cross-Situational Behavioral Consistency in Large Language Models"

**Abstract** (250 words)
- Research question
- Methods (6 personas × 5 models × 8 games)
- Key finding (r̄ ≈ 0.25 vs human r̄ ≈ 0.60)
- Implication (LLM behavior prompt-specific, not trait-based)

**Introduction** (3 pages, ~1,200 words)
1. Personality as cross-situational consistency
2. Prior work: LLMs respond to prompts but consistency untested
3. Your prior work: Reversed responsibility effects (DeAngelo et al. 2025)
4. Gap: Do prompts create coherent traits or task-specific patterns?
5. Contribution: First systematic test with minimal prompt variations
6. Preview findings

**Methods** (4 pages, ~1,600 words)
1. Experimental design
   - Minimal variation personas (Table 1)
   - 8 games with human benchmarks (Table 2)
   - 5 models representing different architectures
2. Sample: 69,000 decisions
3. Analysis plan: Correlation-based consistency measurement

**Results** (6 pages, ~2,400 words)

*Section 1: Descriptive Statistics*
- Table 3: Mean behaviors by game, persona, model
- Table 4: Comparison to human benchmarks
- Key: All models show prosocial bias in baseline

*Section 2: Cross-Game Consistency (Primary Finding)*
- Figure 1: Correlation matrices (5×6 = 30 heatmaps, small multiples)
- Figure 2: Mean correlations by persona (bar chart)
  * Result: r̄ ≈ 0.25 (95% CI: 0.19-0.31)
  * Human benchmark: r̄ ≈ 0.60
  * t(29) = 8.4, p < .001, d = 1.54
- **Interpretation:** LLMs show weak cross-game consistency

*Section 3: Persona Differences (H2)*
- Figure 3: Consistency by persona type
  * Generous: r̄ = 0.31
  * Self-interested: r̄ = 0.29
  * Fair: r̄ = 0.27
  * Strategic: r̄ = 0.22
  * Cooperative: r̄ = 0.21
  * Control: r̄ = 0.24
- No significant difference (F(5,24) = 1.3, p = .29)
- **Interpretation:** Minimal variation insufficient to distinguish

*Section 4: Model Differences (H3)*
- Figure 4: Consistency by model
  * GPT-4o: r̄ = 0.28
  * Claude 3.5: r̄ = 0.24
  * Claude 3.7: r̄ = 0.21
  * Gemini: r̄ = 0.26
  * GPT-4o-mini: r̄ = 0.30
- ANOVA: F(4,25) = 2.1, p = .11
- **Interpretation:** Modest but non-significant model effects

*Section 5: Factor Structure*
- Table 5: Factor analysis results
- 3-factor model fits best (AIC comparison)
- Factors: (1) Pure altruism games, (2) Strategic games, (3) Risk games
- **Interpretation:** Task structure dominates personality

*Section 6: Predictive Validity*
- Figure 5: Network of cross-game predictions (R² > 0.3)
- Within-family predictions strong
- Cross-family predictions weak
- **Interpretation:** Context-dependent behavior

**Discussion** (4 pages, ~1,600 words)

*Section 1: Summary*
- LLMs show weak personality consistency
- Context dominates minimal prompt variations
- Pattern-matching, not trait expression

*Section 2: Integration with Your Prior Work*
- DeAngelo et al. (2025): Responsibility increases risk-taking
- Current study: Effect doesn't generalize across games
- Together: Prompt effects are local, not global
- Implication: Each deployment context needs validation

*Section 3: Theoretical Implications*
- LLMs lack coherent personality states
- Behavior emerges from statistical patterns, not stable traits
- Training data associations dominate persona prompts
- Minimal variations insufficient to override base tendencies

*Section 4: Practical Implications*
- Cannot assume behavioral consistency across contexts
- Persona prompts create weak effects (~0.25 vs 0.60 in humans)
- Deployment requires task-specific testing
- Multi-context reliability cannot be assumed

*Section 5: Model Differences*
- Modest variation across architectures
- Smaller models slightly more consistent (counterintuitive)
- Alignment methods don't improve consistency
- Suggests fundamental limitation, not implementation issue

*Section 6: Limitations*
- Minimal prompt variations (intentional, but limits effect size)
- Student population human benchmarks
- Cross-sectional design (no temporal stability)
- Limited to economic games

*Section 7: Future Directions*
- Stronger persona manipulations
- Longitudinal stability testing
- Non-economic domains
- Fine-tuning for consistency

**References** (2 pages)

**Supplementary Materials:**
- Appendix A: Complete prompts for all games
- Appendix B: Full correlation matrices (30 total)
- Appendix C: Additional statistical tests
- Appendix D: Robustness checks

**Deliverables:**
- Complete manuscript draft
- All figures publication-ready
- All tables formatted
- Supplementary materials

---

### Week 13-14: Revision & Submission

**Internal Review:**
- [ ] Share with DeAngelo & McCannon
- [ ] Get feedback from peer researchers
- [ ] Present at lab meeting
- [ ] Revise based on comments

**Final Checks:**
- [ ] All claims supported by data
- [ ] All figures clear and publication-ready
- [ ] All tables formatted correctly
- [ ] References complete
- [ ] Supplementary materials prepared
- [ ] Word count appropriate

**Target Journals (Ranked):**

1. **Psychological Science** (first choice)
   - Format: Short report, 3,500 words
   - Angle: Personality coherence test
   - Review time: ~2 months

2. **Nature Human Behaviour** (strong alternative)
   - Format: Article, 4,000 words
   - Angle: Human-AI behavioral differences
   - Review time: ~3 months

3. **Cognitive Science** (if rejected above)
   - Format: Full article, 8,000 words
   - Angle: Cognitive architecture implications
   - Review time: ~4 months

**Deliverables:**
- Submitted manuscript
- Cover letter
- Response plan for reviewers

---

## CODE SPECIFICATIONS

### Directory Structure

```
personality_consistency/
├── README.md
├── requirements.txt
├── .env (API keys - DO NOT COMMIT)
├── .gitignore
│
├── prompts/
│   ├── personas.json
│   └── games/
│       ├── dictator.txt
│       ├── ultimatum_proposer.txt
│       ├── ultimatum_responder.txt
│       ├── publicgoods.txt
│       ├── trust_investor.txt
│       ├── trust_trustee.txt
│       ├── prisoner_dilemma.txt
│       └── volunteer_dilemma.txt
│
├── code/
│   ├── 01_run_experiments.py
│   ├── 02_parse_responses.py
│   ├── 03_quality_checks.py
│   ├── 04_compute_correlations.py
│   ├── 05_statistical_tests.py
│   ├── 06_visualizations.py
│   └── utils/
│       ├── api_caller.py
│       ├── response_parser.py
│       └── data_validator.py
│
├── data/
│   ├── raw/
│   │   ├── dictator/
│   │   ├── ultimatum_proposer/
│   │   └── [etc...]
│   ├── processed/
│   │   └── master_dataset.csv
│   └── analysis/
│       ├── correlations.csv
│       └── statistics.csv
│
├── results/
│   ├── figures/
│   │   ├── fig1_correlation_matrices.png
│   │   ├── fig2_persona_comparison.png
│   │   ├── fig3_model_comparison.png
│   │   ├── fig4_factor_loadings.png
│   │   └── fig5_predictive_network.png
│   └── tables/
│       ├── table1_personas.tex
│       ├── table2_human_benchmarks.tex
│       ├── table3_descriptive_stats.tex
│       └── table4_correlations.tex
│
└── logs/
    ├── api_calls.log
    ├── errors.log
    └── quality_reports/
```

### Key Scripts

**Script 1: Run Experiments**
```python
# code/01_run_experiments.py

import asyncio
from utils.api_caller import call_model
from prompts.personas import PERSONAS
from prompts.games import GAME_PROMPTS

async def run_single_trial(model, persona, game, condition=None, run_id):
    """Run one trial and return result"""
    system_prompt = PERSONAS[persona]
    user_prompt = GAME_PROMPTS[game].format(**condition) if condition else GAME_PROMPTS[game]
    
    response = await call_model(
        model=model,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.7  # Some stochasticity for variance
    )
    
    return {
        'model': model,
        'persona': persona,
        'game': game,
        'condition': condition,
        'run_id': run_id,
        'response': response,
        'timestamp': datetime.now()
    }

async def main():
    """Run all experiments"""
    tasks = []
    
    for model in MODELS:
        for persona in PERSONAS:
            for game in GAMES:
                for run_id in range(100):
                    if game in MULTI_CONDITION_GAMES:
                        for condition in game.conditions:
                            task = run_single_trial(model, persona, game, condition, run_id)
                            tasks.append(task)
                    else:
                        task = run_single_trial(model, persona, game, None, run_id)
                        tasks.append(task)
    
    # Run with rate limiting
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Save raw results
    save_results(results)

if __name__ == "__main__":
    asyncio.run(main())
```

**Script 2: Parse Responses**
```python
# code/02_parse_responses.py

import re
import pandas as pd

def parse_numeric(response, min_val, max_val):
    """Extract numeric value from response"""
    # Try to find number
    match = re.search(r'\d+\.?\d*', response)
    if match:
        value = float(match.group())
        if min_val <= value <= max_val:
            return value
    return None

def parse_binary(response, option1, option2):
    """Extract binary choice from response"""
    response_lower = response.lower()
    if option1.lower() in response_lower:
        return option1
    elif option2.lower() in response_lower:
        return option2
    return None

def parse_all_responses(raw_data):
    """Parse all raw responses into structured data"""
    parsed = []
    
    for row in raw_data:
        game = row['game']
        response = row['response']
        
        if game == 'dictator':
            parsed_value = parse_numeric(response, 0, 10)
        elif game == 'ultimatum_proposer':
            parsed_value = parse_numeric(response, 0, 10)
        elif game == 'ultimatum_responder':
            parsed_value = parse_binary(response, 'Accept', 'Reject')
        # [etc for all games]
        
        row['parsed_value'] = parsed_value
        parsed.append(row)
    
    df = pd.DataFrame(parsed)
    df.to_csv('data/processed/master_dataset.csv', index=False)
    return df
```

**Script 3: Compute Correlations**
```python
# code/04_compute_correlations.py

import pandas as pd
import numpy as np
from scipy.stats import pearsonr

def compute_within_persona_correlation(df, model, persona):
    """Compute cross-game correlation for one model-persona pair"""
    
    # Filter to this model and persona
    subset = df[(df['model']==model) & (df['persona']==persona)]
    
    # Aggregate behaviors per game
    behaviors = {}
    
    behaviors['dictator'] = subset[subset['game']=='dictator']['parsed_value'].mean()
    behaviors['ultimatum_prop'] = subset[subset['game']=='ultimatum_proposer']['parsed_value'].mean()
    # [etc for all games - normalize to 0-1 scale]
    
    # Create correlation matrix
    game_names = list(behaviors.keys())
    n_games = len(game_names)
    corr_matrix = np.zeros((n_games, n_games))
    
    for i, game_i in enumerate(game_names):
        for j, game_j in enumerate(game_names):
            if i != j:
                # Get individual-level data for correlation
                data_i = get_individual_data(subset, game_i)
                data_j = get_individual_data(subset, game_j)
                r, p = pearsonr(data_i, data_j)
                corr_matrix[i,j] = r
    
    # Mean of off-diagonal = consistency index
    mean_corr = np.mean(corr_matrix[np.triu_indices_from(corr_matrix, k=1)])
    
    return {
        'model': model,
        'persona': persona,
        'mean_correlation': mean_corr,
        'correlation_matrix': corr_matrix
    }

def main():
    df = pd.read_csv('data/processed/master_dataset.csv')
    
    results = []
    for model in MODELS:
        for persona in PERSONAS:
            result = compute_within_persona_correlation(df, model, persona)
            results.append(result)
    
    # Save
    pd.DataFrame(results).to_csv('data/analysis/correlations.csv', index=False)
```

---

## BUDGET BREAKDOWN

### Detailed Cost Estimate

```
API COSTS BY GAME:
─────────────────────────────────────────────
Dictator:                    3,000 × $0.015  = $45
Ultimatum Proposer:          3,000 × $0.015  = $45
Ultimatum Responder:        12,000 × $0.015  = $180
Public Goods:                3,000 × $0.015  = $45
Trust Investor:              3,000 × $0.015  = $45
Trust Trustee:              12,000 × $0.015  = $180
Prisoner's Dilemma:         30,000 × $0.015  = $450
Volunteer's Dilemma:         3,000 × $0.015  = $45
─────────────────────────────────────────────
SUBTOTAL:                   69,000 calls     = $1,035

PILOT & VALIDATION:
Pilot testing:               1,200 × $0.015  = $18
Validation runs:               300 × $0.015  = $5
─────────────────────────────────────────────
SUBTOTAL:                    1,500 calls     = $23

RETRY BUFFER (5% failure rate):
Failed calls retry:          3,450 × $0.015  = $52
─────────────────────────────────────────────
SUBTOTAL:                    3,450 calls     = $52

OTHER COSTS:
Compute (analysis):                          = $0
Cloud storage (GitHub):                      = $0
Backup storage (redundancy):                 = $10
─────────────────────────────────────────────
TOTAL PROJECT COST:          73,950 calls    = $1,120

RECOMMENDED BUDGET WITH BUFFER:              = $1,200
─────────────────────────────────────────────
```

### Cost Reduction Options (If Needed)

**Option 1: Reduce replications (100 → 50)**
- Halves main experiment cost: $1,035 → $518
- **New total:** ~$600
- **Trade-off:** Lower statistical power, wider confidence intervals

**Option 2: Reduce models (5 → 3)**
- Keep GPT-4o, Claude 3.5, GPT-4o-mini
- Reduces costs by 40%: $1,120 → $672
- **Trade-off:** Less generalizability across architectures

**Option 3: Reduce games (8 → 5)**
- Drop Ultimatum Responder, Trust Trustee, Volunteer's Dilemma
- Saves 18,000 calls: $1,120 → $850
- **Trade-off:** Less comprehensive behavioral profile

**Minimal Viable Study:**
- 3 personas (Generous, Self-interested, Control)
- 3 models (GPT-4o, Claude 3.5, GPT-4o-mini)
- 5 games (Dictator, Ultimatum Proposer, Public Goods, Trust Investor, PD)
- 50 runs per condition
- **Cost:** ~$350-400
- **Timeline:** 8 weeks
- **Still publishable:** Yes, with scope limitations noted

---

## EXPECTED FINDINGS (PREDICTIONS)

### Primary Finding: Weak Consistency

**Prediction:** Mean within-persona correlation r̄ ≈ 0.20-0.30
- Substantially lower than human benchmark (r̄ ≈ 0.60)
- Statistical significance: t(29) > 5, p < .001
- Effect size: Cohen's d > 1.0 (large)

**Interpretation:** Minimal keyword variations insufficient to create coherent cross-game personalities

### Secondary Finding: No Persona Differences

**Prediction:** All personas show similar weak consistency
- Generous: r̄ ≈ 0.25
- Self-interested: r̄ ≈ 0.23
- Fair: r̄ ≈ 0.22
- Strategic: r̄ ≈ 0.21
- Cooperative: r̄ ≈ 0.24
- Control: r̄ ≈ 0.23

**Interpretation:** Single-keyword differences too subtle to distinguish behavioral patterns reliably

### Tertiary Finding: Model Differences Minimal

**Prediction:** Small but non-significant model variation
- Range: 0.19-0.30 across models
- ANOVA non-significant: p > .10

**Interpretation:** Consistency limitation appears architectural, not implementation-specific

### Factor Structure

**Prediction:** 3-factor solution fits best
- Factor 1: Pure altruism games (Dictator, Ultimatum Proposer)
- Factor 2: Strategic interaction games (PD, Ultimatum Responder)
- Factor 3: Risk/trust games (Trust, Volunteer's)

**Interpretation:** Game structure dominates personality framing

---

## SUCCESS CRITERIA

### Minimum Publishable Unit

**Requirements:**
- ✓ Complete data collection (all 69,000 calls)
- ✓ Clean dataset (>90% parseable responses)
- ✓ Primary analysis (cross-game correlations)
- ✓ Statistical comparison to human benchmark
- ✓ 5 publication-ready figures
- ✓ Complete manuscript draft

**Sufficient for publication at:** Behavior Research Methods, Cognitive Science, or specialized AI behavior venues

### Strong Publication

**Additional requirements:**
- ✓ Factor analysis revealing structure
- ✓ Predictive validity analysis
- ✓ Detailed model comparisons
- ✓ Integration with your prior work (DeAngelo et al. 2025)
- ✓ Comprehensive supplementary materials

**Competitive for:** Psychological Science, Nature Human Behaviour

### Exceptional Publication

**Bonus analyses (if time allows):**
- ✓ Temporal stability (subset re-run after 3 months)
- ✓ Human validation study (N=50 humans, same games)
- ✓ Qualitative analysis of chain-of-thought reasoning
- ✓ Cross-model transfer learning analysis

**Target:** Nature Human Behaviour, Science Advances

---

## QUESTIONS TO CONFIRM BEFORE STARTING

1. **Budget:** Is $1,200 feasible? If not, which cost reduction option?

2. **Timeline:** Can you commit 8-10 hours/week for 14 weeks?

3. **Authorship:** Co-authors DeAngelo & McCannon? (Recommend yes for continuity)

4. **Computing:** Access to GPU cluster for parallel API calls? (Not required but speeds up)

5. **IRB:** Check if computational study needs approval (likely not, but verify)

6. **Code proficiency:** Comfortable with Python/async programming? (Can provide templates)

7. **Preferred journal:** Which target excites you most? (Affects framing)

---

## NEXT STEPS

**Immediate (This Week):**
1. Confirm budget and timeline
2. Set up API keys
3. Create GitHub repository
4. Install dependencies

**Week 1 (Next Week):**
1. Write experiment runner code
2. Create persona prompt files
3. Write response parser
4. Run validation (10 calls per condition)

**Week 2:**
1. Analyze validation results
2. Finalize all prompts
3. Prepare for pilot run
4. Set up data monitoring

**Week 3:**
1. Run pilot study
2. Validate persona effects
3. Confirm cost estimates
4. Begin main experiment

---

**This protocol provides complete specification for a high-impact study testing LLM personality consistency with minimal prompt variations. The design leverages your prior work, uses established human benchmarks, and produces novel insights about LLM behavioral architecture.**

**Key Innovation:** Minimal keyword variation approach reveals prompt sensitivity at granular level while maintaining comparability to human personality research.

**Expected Impact:** First systematic test of personality coherence in LLMs; directly challenges assumption that prompt engineering creates stable behavioral patterns.
