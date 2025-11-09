# Pre-Registration: Future Gospel Veracity Predictions

**Date:** November 9, 2025  
**Status:** PRE-REGISTERED (Before Analysis)  
**Purpose:** Avoid post-hoc pattern finding by specifying exact predictions beforehand

---

## Registered Hypotheses (Before Seeing New Data)

### Hypothesis 1: Ancient Historian vs Ancient Epic Discrimination

**Prediction:** Ensemble methodology will correctly classify ancient texts with >75% accuracy

**Specific Predictions:**
- Josephus (historian): Predicted variance σ²>0.25, optimization <0.30
- Thucydides (historian): Predicted σ²>0.27, optimization <0.28
- Homer (epic): Predicted σ²<0.18, optimization >0.45
- Virgil (epic): Predicted σ²<0.20, optimization >0.42

**Test:** Calculate actual values, compare to predictions  
**Success Criterion:** ≥3/4 predictions within ±0.05 of actual  
**Alpha:** 0.05  
**Power:** 0.80 (medium effect, n=7 ancient historians, n=7 ancient epics)

### Hypothesis 2: Quran Ensemble Pattern

**Prediction:** Quran will show truth-claiming patterns (claims divine dictation)

**Specific Predictions:**
- Variance: σ²>0.22 (documentary pattern)
- Commonality: Mean Arabic name rank <50 (common names)
- Optimization: <0.35 (low optimization)

**Test:** Extract Quran character names, calculate ensemble statistics  
**Success Criterion:** 2/3 predictions confirmed  
**Alpha:** 0.05

### Hypothesis 3: Gospels Outperform Chance in Blind Classification

**Prediction:** Gospel features will classify as "non-fiction" with >80% confidence

**Specific Test:**
- Train classifier on non-biblical texts (ancient historians + ancient epics)
- Input gospel features WITHOUT label
- Predict classification

**Success Criterion:** Model assigns P(non-fiction|gospel features) > 0.80  
**Alpha:** 0.05

### Hypothesis 4: Heterogeneity Across 4 Gospels

**Prediction:** All 4 gospels show similar variance (I²<30% heterogeneity)

**Specific Test:**
- Calculate variance for each gospel individually
- I² statistic for heterogeneity
- If I²>30%, need random effects model

**Success Criterion:** I²<30% (low heterogeneity)  
**Alternative:** If I²>30%, report as limitation

### Hypothesis 5: Temporal Confound Test

**Prediction:** Within ancient era, historians still differ from epics

**Specific Predictions:**
- Ancient historians (200 BCE - 200 CE): Mean σ²=0.28
- Ancient epics (same era): Mean σ²=0.16
- Difference: d>0.60

**Test:** Era-matched comparison (both ancient)  
**Success Criterion:** Significant difference (p<0.05) even controlling for era  
**Alpha:** 0.05

---

## Statistical Analysis Plan (Locked)

### Primary Analysis:
- **Test:** Two-sample t-test (variance comparison)
- **Alpha:** 0.05 (two-tailed)
- **Effect size:** Cohen's d with 95% CI
- **Power:** ≥0.80
- **Multiple testing:** Bonferroni correction for 5 hypotheses (α=0.01 per test)

### Secondary Analyses:
- ANOVA across all categories
- Post-hoc Tukey HSD
- Levene's test for variance equality
- Bayesian estimation with weakly informative priors

### Robustness Checks:
- Bootstrap CI (10,000 resamples)
- Jackknife sensitivity
- Permutation test
- Cross-validation

---

## Commitment to Honest Reporting

**We commit to:**
1. Report ALL results, even if contradict hypotheses
2. Update Bayesian posteriors honestly (up or down)
3. Acknowledge weaknesses if found
4. Not p-hack or HARKing (Hypothesizing After Results Known)
5. Make data/code available for replication

**If hypotheses fail:**
- Report null results honestly
- Revise confidence downward
- Explain what went wrong
- Don't hide negative results

---

**Timestamp:** 2025-11-09T00:00:00Z  
**Hash:** SHA256 of this document (to prove it predates analysis)  
**Status:** LOCKED - Cannot modify after analysis begins

