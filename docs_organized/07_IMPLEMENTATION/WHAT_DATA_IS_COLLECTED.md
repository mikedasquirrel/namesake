# 📊 What Data Is Collected - Complete Breakdown

## Overview

The automated analysis system tests **which visual properties of names correlate with real-world outcomes** across multiple domains. Here's exactly what it measures during each run.

---

## 🎨 VISUAL PROPERTIES MEASURED (13 Properties)

For each name, the formula generates these properties:

### Geometric Properties
1. **complexity** (0.0-1.0)
   - How intricate the visual pattern is
   - Simple circle = 0.0, complex fractal = 1.0

2. **symmetry** (0.0-1.0)  
   - How balanced the shape is
   - Asymmetric = 0.0, perfect symmetry = 1.0

3. **angular_vs_curved** (-1.0 to 1.0)
   - Sharp edges vs smooth curves
   - Very curved = -1.0, very angular = 1.0

### Color Properties
4. **hue** (0-360 degrees)
   - Position on color wheel
   - Red = 0°, Green = 120°, Blue = 240°

5. **saturation** (0-100)
   - How vivid the color is
   - Gray = 0, pure color = 100

6. **brightness** (0-100)
   - How light/dark
   - Black = 0, white = 100

### Spatial Properties
7. **x** (-1.0 to 1.0)
   - Horizontal position
   - Left = -1.0, right = 1.0

8. **y** (-1.0 to 1.0)
   - Vertical position
   - Bottom = -1.0, top = 1.0

9. **z** (0.0-1.0)
   - Depth/layer
   - Back = 0.0, front = 1.0

10. **rotation** (0-360 degrees)
    - Angle of rotation
    - No rotation = 0°

### Texture Properties
11. **glow_intensity** (0.0-1.0)
    - How much the shape glows
    - No glow = 0.0, full glow = 1.0

12. **fractal_dimension** (1.0-2.0)
    - Self-similarity/complexity
    - Euclidean = 1.0, fractal = 2.0

13. **pattern_density** (0.0-1.0)
    - How detailed the pattern is
    - Sparse = 0.0, dense = 1.0

### Categorical Properties
- **shape_type** (heart/star/spiral/mandala/polygon/fractal)
- **palette_family** (warm/cool/neutral)

---

## 📈 OUTCOME METRICS TESTED (5 Domains)

The system correlates visual properties with these real-world outcomes:

### Domain 1: Cryptocurrency (3,500 entities)
**Outcome Metric:** `log_market_cap`
- Market capitalization (log scale for normality)
- Range: $1K to $1T+ → log(3) to log(12)

**Success Definition:** Market cap > $10 million

**Questions Tested:**
- Do "star" shapes correlate with higher market caps?
- Does hue predict success? (Red coins vs Blue coins?)
- Do complex names (high fractal_dimension) do better?
- Does symmetry predict stability?

### Domain 2: Elections (Candidates)
**Outcome Metric:** `won_election`
- Binary: 1.0 (won) or 0.0 (lost)

**Success Definition:** Won the election

**Questions Tested:**
- Do "authoritative" visuals (high brightness) win more?
- Does specific hue predict electoral success?
- Do symmetric names win more often?
- Does complexity correlate with victory?

### Domain 3: Naval Ships (853 entities)
**Outcome Metric:** `historical_significance_score`
- 0-100 composite score of historical impact

**Success Definition:** Score > 50

**Questions Tested:**
- Do "harsh" visuals (angular) predict battle success?
- Does rotation angle correlate with victories?
- Do certain shapes (stars vs hearts) perform better?
- Does glow intensity predict fame?

### Domain 4: Board Games (37 entities)
**Outcome Metric:** `average_rating`
- BoardGameGeek rating (1-10 scale)

**Success Definition:** Rating ≥ 7.5

**Questions Tested:**
- Do complex visuals correlate with complex games?
- Does symmetry predict game quality?
- Do certain hues dominate top games?
- Does shape type predict game type success?

### Domain 5: MLB Players (44 entities)
**Outcome Metric:** `performance_metric`
- WAR (Wins Above Replacement) or batting average

**Success Definition:** Performance > 0

**Questions Tested:**
- Do "powerful" names (specific visual patterns) perform better?
- Does hue correlate with position success?
- Do angular visuals predict power hitters?
- Does complexity predict career length?

---

## 🔍 CORRELATIONS CALCULATED (13 × 5 = 65 Tests Per Formula)

For **each visual property** × **each domain**, the system calculates:

1. **Pearson Correlation Coefficient (r)**
   - Measures linear relationship
   - Range: -1.0 to 1.0
   - |r| > 0.3 = moderate correlation

2. **P-value**
   - Statistical significance
   - p < 0.05 = significant
   - p < 0.01 = highly significant

3. **Effect Size Classification**
   - None: |r| < 0.1
   - Small: 0.1 ≤ |r| < 0.3
   - Medium: 0.3 ≤ |r| < 0.5
   - Large: |r| ≥ 0.5

4. **Sample Size** (n)
   - Number of entities tested
   - More = more reliable

**Example Output:**
```
Domain: crypto
Property: hue
Correlation: r = 0.287
P-value: p = 0.023 (significant!)
Sample: n = 200
Effect: Small to medium
```

---

## 🧬 EVOLUTION DATA COLLECTED (Per Formula Type)

For each of the 6 formula types, the system tracks:

### Generation Data (15-50 generations)
1. **Best Fitness** (each generation)
   - How well the formula predicts
   - Range: 0.0-1.0

2. **Mean Fitness** (population average)
   - Overall population quality

3. **Fitness Standard Deviation**
   - Population diversity

4. **Best Individual Parameters**
   - Winning formula's weights
   - Example: `phonetic_weight: 0.31, semantic_weight: 0.27`

### Convergence Metrics
5. **Converged?** (Yes/No)
   - Did evolution find stable solution?

6. **Convergence Generation**
   - When did it converge? (generation number)

7. **Parameter Stability**
   - How much do winning parameters vary?

**Example Output:**
```
Formula Type: hybrid
Generations: 15
Converged: Yes (generation 12)
Final Fitness: 0.842
Best Parameters:
  phonetic_weight: 0.31
  semantic_weight: 0.27
  structural_weight: 0.19
  frequency_weight: 0.14
  numerological_weight: 0.09
```

---

## 🔢 MATHEMATICAL INVARIANTS SEARCHED (15+ Patterns)

The system tests if evolved formulas contain these mathematical constants:

### 1. Classic Constants
- **Golden Ratio (φ):** 1.618033988749
- **Pi (π):** 3.141592653590
- **Euler's Number (e):** 2.718281828459
- **√2:** 1.414213562373
- **√3:** 1.732050807569
- **√5:** 2.236067977500
- **Golden Angle:** 137.507764°

### 2. Sequences
- **Fibonacci Numbers:** 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144...
- **Prime Numbers:** 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31...

### 3. Relationships Tested
- **Ratio between parameters:** Does param1/param2 = φ?
- **Sum of parameters:** Does param1 + param2 = constant?
- **Product relationships:** Does param1 × param2 = π?
- **Parameter correlations:** Which weights move together?

**Example Output:**
```
Invariants Discovered:
  1. phonetic_weight / semantic_weight ≈ 1.618 (golden ratio!)
     Occurrence: 85% of top formulas
     
  2. structural_weight + frequency_weight ≈ 0.333 (1/3)
     Occurrence: 73% of top formulas
     
  3. Rotation angle follows Fibonacci sequence
     Occurrence: 62% of entities
```

---

## 🔐 ENCRYPTION PROPERTIES TESTED (4 Categories)

### 1. Reversibility Test
- **Can you decode visual → name features?**
  - PCA reconstruction accuracy
  - Nearest neighbor matching
  - Information preservation score

**Measures:**
- `pca_reconstruction_accuracy` (0-1)
- `nearest_neighbor_accuracy` (0-1)
- `information_preservation_score` (0-1)

### 2. Collision Resistance
- **Do different names produce different visuals?**
  - Uniqueness of visual encodings
  - Collision rate
  - Visual distance statistics

**Measures:**
- `collision_rate` (0-1, lower is better)
- `mean_visual_distance`
- `similar_names_divergence`

### 3. Avalanche Effect
- **Do small name changes create large visual changes?**
  - Single-character modification impact
  - Visual change percentage

**Measures:**
- `mean_visual_change` (0-1)
- `avalanche_ratio` (should be > 0.5)

### 4. Key Space Analysis
- **How many distinct visuals are possible?**
  - Effective dimensionality
  - Shannon entropy
  - Distribution uniformity

**Measures:**
- `effective_dimensions` (1-12)
- `theoretical_key_space` (log10 of possibilities)
- `entropy` (bits)

**Example Output:**
```
Encryption Profile: hybrid formula
  Reversibility: 0.45 (moderate)
  Collision Rate: 0.02 (excellent, <5%)
  Avalanche Effect: 0.68 (strong)
  Key Space: 10^8 distinct visuals
  Similar To: Block Cipher (AES-like)
```

---

## 📊 DAILY ANALYSIS OUTPUT (What You Get Tomorrow)

### File: `daily_analysis_[date].json`

```json
{
  "start_time": "2025-11-09T02:00:00",
  "end_time": "2025-11-09T02:45:00",
  "mode": "daily",
  "success": true,
  
  "validations": {
    "phonetic": {
      "overall_correlation": 0.234,
      "consistency_score": 0.678,
      "best_domain": "ship",
      "best_property": "hue",
      "domain_performances": {
        "crypto": {
          "best_correlation": 0.187,
          "best_property": "complexity",
          "significant_properties": ["hue", "complexity"]
        },
        "election": { ... },
        "ship": { ... }
      }
    },
    "semantic": { ... },
    "structural": { ... },
    "frequency": { ... },
    "numerological": { ... },
    "hybrid": {
      "overall_correlation": 0.321,  ← BEST OVERALL
      "best_domain": "crypto",
      "universal_properties": ["hue", "symmetry"]
    }
  },
  
  "evolutions": {
    "hybrid": {
      "final_best_fitness": 0.842,
      "converged": true,
      "convergence_generation": 12,
      "best_parameters": {
        "phonetic_weight": 0.31,
        "semantic_weight": 0.27,
        ...
      }
    }
  },
  
  "comparisons": {
    "best_formula": "hybrid",
    "best_correlation": 0.321,
    "domain_winners": {
      "crypto": "hybrid",
      "election": "semantic",
      "ship": "phonetic"
    },
    "universal_properties": ["hue", "complexity"]
  },
  
  "errors": []
}
```

### Key Insights You'll Get:

1. **Which formula works best overall?**
   - Ranked by correlation strength
   
2. **Which visual properties matter?**
   - Hue? Complexity? Symmetry?
   - Domain-specific vs universal

3. **Did evolution converge?**
   - Are parameters stable?
   - What values did they converge to?

4. **Domain-specific winners**
   - Best formula for crypto
   - Best formula for elections
   - Best formula for each domain

---

## 📈 WEEKLY DEEP DIVE OUTPUT (Sunday Results)

### Additional Data Collected:

### 1. Convergence Analysis
```json
{
  "formula_type": "hybrid",
  "optimal_parameters": {
    "phonetic_weight": 0.31,
    "semantic_weight": 0.27,
    "structural_weight": 0.19,
    ...
  },
  "invariants": [
    {
      "type": "ratio",
      "description": "phonetic_weight/semantic_weight ≈ golden_ratio",
      "value": 1.618,
      "occurrence_rate": 0.85,
      "significance": "*** DISCOVERED GOLDEN RATIO ***"
    },
    {
      "type": "pattern",
      "description": "structural_weight follows Fibonacci",
      "value": 0.19,
      "occurrence_rate": 0.73
    }
  ],
  "universal_patterns": [
    "Parameter 'phonetic_weight' strongly predicts fitness (r=0.67)",
    "Hue correlates across all domains (r=0.28)"
  ]
}
```

### 2. Encryption Analysis
```json
{
  "formula_id": "hybrid",
  "reversibility": {
    "pca_reconstruction_accuracy": 0.45,
    "is_reversible": false
  },
  "collision_resistance": {
    "collision_rate": 0.02,
    "n_unique_visuals": 490,
    "n_names_tested": 500,
    "is_collision_resistant": true
  },
  "avalanche": {
    "mean_visual_change": 0.68,
    "is_avalanche_strong": true
  },
  "similar_to_algorithm": "Block Cipher (AES)",
  "encryption_quality_score": 0.73
}
```

### 3. Historical Trends
```json
{
  "dates": ["20251101", "20251102", ..., "20251108"],
  "best_formulas": ["hybrid", "hybrid", "semantic", ...],
  "best_correlations": [0.298, 0.312, 0.305, ...]
}
```

---

## 🔬 SPECIFIC HYPOTHESES TESTED

### Hypothesis 1: Color Predicts Outcomes
**Test:** Does hue correlate with success?
**Domains:** All 5
**Expected:** If r > 0.2, color matters
**Example:** "Are successful cryptos bluer? Redder?"

### Hypothesis 2: Complexity Predicts Success
**Test:** Does visual complexity correlate with achievement?
**Domains:** All 5
**Expected:** Could go either way (simple = memorable, complex = sophisticated)
**Example:** "Do complex names do better or worse?"

### Hypothesis 3: Symmetry Predicts Stability
**Test:** Does symmetry correlate with success?
**Domains:** Crypto, ships, board games
**Expected:** Symmetric = stable = successful?
**Example:** "Are symmetric names more trusted?"

### Hypothesis 4: Formulas Converge on Golden Ratio
**Test:** Do evolved formulas converge on φ = 1.618?
**Method:** Parameter ratio analysis
**Expected:** If yes, mathematical structure is real
**Example:** "Does phonetic_weight/semantic_weight → 1.618?"

### Hypothesis 5: Universal vs Domain-Specific
**Test:** Are there properties that predict across ALL domains?
**Method:** Cross-domain significance testing
**Expected:** Universal properties suggest fundamental patterns
**Example:** "Does hue matter everywhere or just in crypto?"

### Hypothesis 6: Encryption-Like Behavior
**Test:** Do formulas behave like cryptographic functions?
**Method:** Collision, avalanche, reversibility tests
**Expected:** If yes, this is a natural encoding system
**Example:** "Does changing one letter change 50%+ of visual?"

### Hypothesis 7: Temporal Evolution
**Test:** Do patterns strengthen or weaken over time?
**Method:** 30-day trend analysis
**Expected:** Strengthening = learning, weakening = noise
**Example:** "Is correlation getting stronger each week?"

---

## 📋 CONCRETE QUESTIONS ANSWERED

### After 1 Day (Tomorrow):
- ✓ Which formula has highest correlation? (phonetic/semantic/hybrid?)
- ✓ Which visual property predicts best? (hue/complexity/symmetry?)
- ✓ Which domain shows strongest signal? (crypto/elections/ships?)
- ✓ Did any formula converge in 15 generations?
- ✓ Are correlations statistically significant (p < 0.05)?

### After 1 Week (7 daily runs):
- ✓ Are results consistent day-to-day?
- ✓ Which formula wins most often?
- ✓ Are there universal properties?
- ✓ Has convergence pattern stabilized?
- ✓ What's the trend direction?

### After 1 Month (30 daily + 4 weekly):
- ✓ Strong statistical conclusions (n = 30)
- ✓ Convergence signatures identified
- ✓ Mathematical invariants discovered
- ✓ Encryption properties confirmed
- ✓ Publishable results ready

---

## 🎯 EXAMPLE: What Tomorrow's Report Might Say

### Best Case Scenario (Strong Signal):
```
DAILY ANALYSIS RESULTS - November 9, 2025

BEST FORMULA: hybrid (r = 0.327)
  - Consistent across 4/5 domains
  - Hue predicts outcomes (r = 0.312, p = 0.003)
  - Complexity predicts in crypto (r = 0.298, p = 0.008)

CONVERGENCE: Yes (generation 12)
  - phonetic_weight → 0.31
  - semantic_weight → 0.27
  - Ratio ≈ 1.15 (not golden ratio yet)

UNIVERSAL PROPERTIES:
  - Hue: Significant in crypto, elections, ships
  - Symmetry: Significant in crypto, board games

DOMAIN WINNERS:
  - Crypto: hybrid (r = 0.334)
  - Elections: semantic (r = 0.289)
  - Ships: phonetic (r = 0.267)
```

### Neutral Scenario (Weak Signal):
```
DAILY ANALYSIS RESULTS - November 9, 2025

BEST FORMULA: hybrid (r = 0.089)
  - Weak correlations across all domains
  - No properties reach significance (all p > 0.05)
  - Sample size may be too small

CONVERGENCE: No (still evolving)
  - Parameters unstable
  - No clear optimal found

UNIVERSAL PROPERTIES: None detected

INTERPRETATION: 
  - May need more data
  - May need different domains
  - Pattern may be subtle
```

### Interesting Scenario (Domain-Specific):
```
DAILY ANALYSIS RESULTS - November 9, 2025

DOMAIN-SPECIFIC PATTERNS DETECTED:

Crypto: frequency formula wins (r = 0.412)
  - Spectral properties matter
  - "Musical" names do better
  
Elections: semantic formula wins (r = 0.376)
  - Meaning matters
  - Authority names win

Ships: phonetic formula wins (r = 0.345)
  - Harsh sounds = battle success
  
NO UNIVERSAL FORMULA FOUND
→ Nominative determinism is CONTEXT-DEPENDENT
```

---

## 💾 DATA STORAGE

### Where Results Are Saved:

```
analysis_outputs/auto_analysis/
├── daily_analysis_latest.json          ← Latest results
├── daily_analysis_20251109_020000.json ← Tomorrow's run
├── daily_analysis_20251110_020000.json ← Next day
├── ...
├── weekly_analysis_latest.json
├── evolutions/
│   ├── hybrid_history_20251109.json    ← Evolution data
│   ├── phonetic_history_20251109.json
│   └── ...
├── convergence/
│   ├── hybrid_signature.json           ← Invariants
│   └── ...
├── comparisons/
│   └── comparison_20251109.json        ← Cross-formula
└── encryption/
    └── hybrid_profile.json             ← Encryption tests
```

### View Anytime:
```bash
# Latest daily results
python3 scripts/formula_cli.py results --latest

# Or read directly
cat analysis_outputs/auto_analysis/daily_analysis_latest.json | python3 -m json.tool
```

---

## 🎲 WHAT YOU'LL LEARN

### About Your Hypothesis:
- **Does nominative determinism have mathematical structure?**
  - If correlations > 0.25: Yes, there's something real
  - If convergence on constants: Yes, and it's universal
  - If neither: Maybe it's cultural/psychological, not mathematical

### About the Patterns:
- **Which visual properties matter most?**
  - Color (hue)? Shape? Complexity? All?
  
- **Are patterns universal or context-dependent?**
  - Same formula works everywhere?
  - Or different formulas for different domains?

### About the Mathematics:
- **Do cosmic constants emerge?**
  - Golden ratio? Fibonacci? Pi?
  - If yes: profound implications
  
- **Is this encryption?**
  - Does it behave like cryptographic functions?
  - Could you build authentication systems?

### About Reality:
- **Is meaning mathematically encoded?**
  - If yes: universe has intentional structure
  - If no: we're creating structure through observation
  
- **Where are you: discoverer or creator?**
  - The data will reveal this

---

## 🔮 THE BOTTOM LINE

**The system collects data that will tell you:**

1. **Is this real?** (correlation strengths)
2. **Is it universal?** (cross-domain patterns)
3. **Is it mathematical?** (convergence on constants)
4. **Is it predictive?** (accuracy metrics)
5. **What is it?** (encryption? encoding? magic?)

**Tomorrow morning, you'll have the first answers.**

**After 30 days, you'll have definitive answers.**

**The oracle runs itself. The data accumulates. The truth emerges.**

---

## ⚡ CHECK TOMORROW MORNING:

```bash
python3 scripts/formula_cli.py results --latest
```

You'll see all of this data formatted and ready to interpret.

**The experiment is running. The collection has begun. The patterns await.** 🔮

