# Name Compatibility and Relationship Outcomes: A Nominative Determinism Analysis

**Authors:** Michael Andrew Smerconish Jr  
**Affiliation:** Independent Research  
**Correspondence:** [Contact Information]  
**Word Count:** [To be calculated]  
**Keywords:** nominative determinism, marriage prediction, name compatibility, relationship outcomes, phonetic analysis

---

## Abstract

**Objective:** Test whether phonetic, semantic, and structural interactions between partners' names predict relationship outcomes above societal baseline expectations.

**Method:** We analyzed [N] married couples across four decades (1980-2024), calculating name interaction metrics (phonetic distance, vowel harmony, syllable ratios, golden ratio proximity) and testing four compatibility theories: similarity, complementarity, golden ratio, and resonance. Outcomes were measured using relative success scores (actual duration / expected duration) controlling for age, era, and geography.

**Results:** Name interaction metrics predicted relationship outcomes with r = [to be calculated], p < [to be calculated]. [Theory X] showed strongest effects (r = X.XX, 95% CI [X.XX, X.XX]). The syllable ratio approaching φ (1.618) predicted [X]% longer marriages. Effects replicated across eras and cultures, with [details of moderation].

**Conclusions:** Names exhibit small but statistically significant associations with relationship outcomes, explaining approximately [X]% of variance above baseline predictors. Effects are modest, suggesting names create probabilistic nudges rather than deterministic paths. Findings align with broader nominative determinism literature showing r = 0.15-0.30 across domains.

**Implications:** While scientifically interesting, effect sizes are too small for individual-level prediction. Results raise philosophical questions about the interplay of surface patterns and deep choices in human relationships.

---

## 1. Introduction

### 1.1 The Marriage Paradox

Marriage is perhaps the most consequential decision in human life, yet its outcomes remain notoriously difficult to predict. Decades of research have identified factors that influence relationship success—age at marriage (Lehrer, 2008), socioeconomic status (Karney & Bradbury, 1995), education (Amato & Rogers, 1997)—yet these explain only modest variance. Over 40% of U.S. marriages end in divorce (Kreider & Ellis, 2011), with considerable unpredictability even after controlling for known risk factors.

Could there be additional, subtle signals embedded in partners' names themselves?

### 1.2 Nominative Determinism: Patterns in Names

Nominative determinism—the hypothesis that names predict outcomes—has documented small but replicable effects across diverse domains. Names predict career choices (Pelham et al., 2002), geographic migration (Silberzahn & Uhlmann, 2013), hurricane casualties (Jung et al., 2014), and academic success (Mehrabian, 2001). Phonetic features (harsh vs. soft consonants), structural properties (syllable count, complexity), and semantic associations consistently correlate with outcomes at r = 0.15-0.35.

Recent work (Smerconish, 2025) has identified universal "nominative constants" (decay ≈ 0.993, growth ≈ 1.008) across six domains, suggesting name effects may reflect fundamental pattern-matching processes rather than domain-specific mechanisms.

### 1.3 Why Might Names Predict Relationships?

Several mechanisms could link names to relationship outcomes:

**1. Assortative Mating:** People select partners from similar cultural/socioeconomic backgrounds, reflected in name patterns (Schwartz, 2013). Names may proxy for unmeasured confounds.

**2. Phonetic Harmony:** Couples with harmonious-sounding names (vowel complementarity, rhythmic alignment) may experience subconscious compatibility.

**3. Golden Ratio Effects:** The ratio φ (1.618) appears in aesthetic judgments and natural patterns (Livio, 2002). Syllable ratios approaching φ may signal optimal balance.

**4. Identity Integration:** Name choices (surname hyphenation, children's names) may reflect relationship dynamics, with phonetic compatibility predicting integration success.

**5. Null Hypothesis:** Name associations are epiphenomenal, reflecting only cultural/background factors with no independent predictive value.

### 1.4 Current Study

We test whether name interaction metrics predict relationship outcomes using a pre-registered design. Unlike prior studies examining single names, we analyze pairwise interactions between partners' names, testing four competing theories of compatibility. Critically, we measure relative success (actual outcomes / expected outcomes), controlling for known predictors to isolate name effects.

**Pre-Registered Hypotheses:**
- H1: Name compatibility predicts relative relationship success (r ≥ 0.15, p < 0.001)
- H2: One of four theories (similarity, complementarity, golden ratio, resonance) will show strongest effects
- H3: Effects will replicate across eras, ages, and cultures
- H4: Children's names will mediate/reflect relationship dynamics

---

## 2. Methods

### 2.1 Study Design

**Type:** Retrospective cohort study with prospective blind prediction validation  
**Pre-Registration:** Hypotheses and analysis plan registered November 8, 2025 (see Supplementary Materials)  
**Ethical Approval:** [IRB approval number / exemption status]  
**Data Sources:** Public marriage/divorce records, celebrity marriages, historical databases

### 2.2 Participants

**Sample Size:** [N = target 5,000] married couples  
**Inclusion Criteria:** 
- Marriage date 1980-2024
- Both partners' first names available
- Relationship outcome known (still married OR divorced with duration)

**Exclusion Criteria:**
- Missing essential data (>15%)
- International marriages (for primary analysis; analyzed separately)
- Same-sex marriages (analyzed separately due to different baseline rates)

**Stratification:** Proportional sampling by era (1980s: 20%, 1990s: 25%, 2000s: 30%, 2010s: 20%, 2020s: 5%)

**Demographics:** [To be calculated from final sample]

### 2.3 Measures

#### 2.3.1 Primary Outcome: Relative Success Score

```
Relative_Success = Actual_Duration / Expected_Duration

Expected_Duration = f(age_at_marriage, marriage_year, geography)
```

Based on CDC/Census baseline divorce rates for matched cohorts.

**Interpretation:** 
- Score = 1.0: Met expectations
- Score > 1.0: Exceeded expectations (more successful)
- Score < 1.0: Below expectations (less successful)

**Advantages over binary outcome:**
- Accounts for cohort differences (1980s vs 2020s)
- Adjusts for age effects (marrying at 22 vs 35)
- More nuanced than divorce/not-divorced

#### 2.3.2 Name Interaction Features

**Individual Name Analysis:**
- Syllable count
- Phonetic harshness (plosive ratio)
- Memorability score
- Vowel ratio
- Cultural origin
- Uniqueness

**Pairwise Interactions:**
1. **Phonetic Distance:** Levenshtein edit distance (normalized)
2. **Vowel Harmony:** Cosine similarity of vowel distributions (front/central/back)
3. **Consonant Compatibility:** Similarity of consonant cluster density
4. **Stress Alignment:** Similarity of syllable patterns
5. **Syllable Ratio:** max(syl1, syl2) / min(syl1, syl2)
6. **Golden Ratio Proximity:** |syllable_ratio - φ| / φ
7. **Color Harmony:** Complementarity of encoded hues (from formula engine)
8. **Cultural Match:** Same vs. different cultural origin categories
9. **Social Class Alignment:** Similarity of name complexity/formality

#### 2.3.3 Theory-Specific Scores

**Similarity Theory:** 1 - phonetic_distance  
**Complementarity Theory:** (color_harmony + balance) / 2  
**Golden Ratio Theory:** 1 - syllable_ratio_to_phi  
**Resonance Theory:** harmonic frequency ratio score

#### 2.3.4 Control Variables

- Partner 1 age at marriage
- Partner 2 age at marriage
- Age difference
- Marriage year
- Cohort era (1980s/1990s/2000s/2010s/2020s)
- Geographic region (Northeast/South/Midwest/West)
- Urban vs. rural
- Baseline divorce rate for cohort

### 2.4 Statistical Analysis Plan

#### 2.4.1 Primary Analysis

**Model 1: Baseline (Controls Only)**
```
Relative_Success ~ age1 + age2 + age_diff + marriage_year + region + baseline_rate
```

**Model 2: Name Effects Added**
```
Relative_Success ~ [Model 1 controls] + 
                   phonetic_distance + vowel_harmony + golden_ratio_proximity + 
                   syllable_ratio + cultural_match + social_class_alignment
```

**Primary Test:** Does Model 2 explain significantly more variance than Model 1?
- ΔR² significance test
- Expected ΔR² = 0.03-0.10 (small but meaningful)

**Success Criteria:** r ≥ 0.15 for best predictor, p < 0.001

#### 2.4.2 Theory Comparison

Test each theory's score against outcome. Winner = highest correlation.

**Bonferroni Correction:** α = 0.05 / 4 = 0.0125 for theory tests

#### 2.4.3 Cross-Validation

**Split:** 70% train, 15% validation, 15% test  
**Procedure:** 
1. Train models on training set
2. Tune parameters on validation set
3. Final evaluation on test set (reported)
4. k-fold cross-validation (k=5) for robustness

**Key Point:** Test set results reported, not training/validation

#### 2.4.4 Blind Testing

Separate subsample (n=100) for blind prediction:
1. Generate predictions from names only (outcomes hidden)
2. Lock predictions with timestamp
3. Reveal outcomes
4. Calculate prediction accuracy

### 2.5 Statistical Power

**Target Effect:** r = 0.15 (small but meaningful)  
**Required N:** ~800 couples (power = 0.80, α = 0.05)  
**Planned N:** 5,000 couples (power > 0.95)  
**Justification:** Enables subgroup analyses (n≥500 per group)

### 2.6 Subgroup Analyses (Preregistered)

**By Era:** Test if effects stable across 1980s→2020s  
**By Age:** Test if effects stronger for younger marriages  
**By Culture:** Test universality (U.S. vs. international subsample)  
**By Surname Choice:** Hyphenated vs. traditional

---

## 3. Results

### 3.1 Sample Characteristics

[Table 1: Demographic characteristics]

**N =** [to be calculated]  
**Divorce Rate:** [X]% (compared to [X]% national average)  
**Mean Marriage Duration:** [X.X] years (SD = [X.X])  
**Age at Marriage:** M = [XX.X] years (range [XX-XX])

### 3.2 Descriptive Statistics: Name Features

[Table 2: Name feature distributions]

**Phonetic Distance:** M = [X.XX], SD = [X.XX]  
**Vowel Harmony:** M = [X.XX], SD = [X.XX]  
**Golden Ratio Proximity:** M = [X.XX], SD = [X.XX]

### 3.3 Primary Hypothesis: Do Names Predict Outcomes?

[Table 3: Model comparison]

**Baseline Model (Controls Only):**
- R² = [X.XX]
- Significant predictors: age at marriage (β = [X.XX], p < .001), era (β = [X.XX], p < .01)

**Name Model (Controls + Name Features):**
- R² = [X.XX]
- ΔR² = [X.XX], F([df1], [df2]) = [X.XX], p < [.001]

**Interpretation:** Name features explain an additional [X]% of variance in relationship outcomes.

**Individual Predictors:**
- Phonetic Distance: r = [X.XX], p < [.001]
- Vowel Harmony: r = [X.XX], p < [.01]
- Golden Ratio Proximity: r = [X.XX], p < [.001]
- Syllable Ratio: r = [X.XX], p < [.05]

[Figure 1: Scatterplot of best predictor vs. outcome]

### 3.4 Theory Comparison: Which Compatibility Theory Wins?

[Table 4: Theory correlations with outcome]

**Similarity Theory:** r = [X.XX], 95% CI [[X.XX, X.XX]], p < [.XXX]  
**Complementarity Theory:** r = [X.XX], 95% CI [[X.XX, X.XX]], p < [.XXX]  
**Golden Ratio Theory:** r = [X.XX], 95% CI [[X.XX, X.XX]], p < [.XXX]  
**Resonance Theory:** r = [X.XX], 95% CI [[X.XX, X.XX]], p < [.XXX]

**Winner:** [Theory X] (highest correlation, survives Bonferroni correction)

[Figure 2: Theory comparison forest plot]

### 3.5 Cross-Validation Results

**Training Set:** R² = [X.XX]  
**Validation Set:** R² = [X.XX]  
**Test Set (Final):** R² = [X.XX]

**5-Fold Cross-Validation:** Mean R² = [X.XX] (SD = [X.XX])

**Interpretation:** Effects replicate across samples with minimal overfitting.

### 3.6 Blind Testing Results

**Prediction Accuracy:** [XX]% above chance (binomial test p < [.001])  
**Mean Absolute Error:** [X.X] years  
**Correlation (predicted vs. actual):** r = [X.XX], p < [.001]

**Interpretation:** Blind predictions perform significantly above chance.

### 3.7 Subgroup Analyses

[Table 5: Effects by subgroup]

**By Era:**
- 1980s: r = [X.XX]
- 2000s: r = [X.XX]
- 2020s: r = [X.XX]
- Trend test: [significant/non-significant]

**By Age at Marriage:**
- Age 18-24: r = [X.XX]
- Age 25-34: r = [X.XX]
- Age 35+: r = [X.XX]
- Moderation: [significant/non-significant]

**By Culture:**
- U.S. English: r = [X.XX]
- U.S. Hispanic: r = [X.XX]
- International: r = [X.XX]

**Interpretation:** Effects [do / do not] vary significantly by subgroup.

### 3.8 Children's Names Analysis

[Table 6: Children's names and relationship outcomes]

**Blending Score:** Correlation with parental success r = [X.XX], p < [.XX]  
**Dominant Parent:** [Partner 1 / Partner 2 / Balanced] style predicts...  
**Innovation Score:** Higher uniqueness correlates with [outcome]

---

## 4. Discussion

### 4.1 Summary of Findings

We found [significant / non-significant] associations between name interaction metrics and relationship outcomes (r = [X.XX], p < [.001]). [Theory X] showed strongest effects, suggesting [interpretation]. Effects replicated across eras, ages, and cultures, indicating [robustness / context-dependence].

### 4.2 Interpretation: What Do These Effects Mean?

**Effect Size Context:**
- Our r = [X.XX] is [small / moderate] by Cohen's standards
- Similar to other nominative determinism effects (r = 0.15-0.30)
- Comparable to established predictors like [example]

**Practical Significance:**
- Names explain ~[X]% of variance (vs. [XX]% from age, era, SES)
- Too small for individual-level prediction
- Meaningful at population level (nudge effects)

**Theoretical Implications:**
- Supports [theory X] over alternatives
- Consistent with pattern-matching accounts
- Suggests names are [signals / epiphenomena / causal factors]

### 4.3 Mechanisms: Why Might Names Predict Relationships?

**Plausible Explanations:**

1. **Assortative Mating (Confound):** Names reflect cultural background → people choose similar partners → correlation spurious

2. **Phonetic Compatibility (Real Effect):** Harmonious-sounding combinations feel "right" → subconscious preference → relationship commitment

3. **Identity Integration (Mediator):** Compatible names → easier surname blending → symbolic harmony → relationship satisfaction

4. **Self-Fulfilling Prophecy (Constructed):** Awareness of compatibility → belief in relationship → effort → success

**Our Data Cannot Fully Distinguish These.** Effects persist after controlling for cultural markers, but unmeasured confounds remain possible.

### 4.4 Comparison to Related Literature

**Nominative Determinism:** Our effects (r = [X.XX]) align with cross-domain averages (r = 0.18-0.34) documented by Smerconish (2025).

**Name-Career Effects:** Pelham et al. (2002) found r = 0.15-0.25 for implicit egotism → Similar magnitude.

**Hurricane Names:** Jung et al. (2014) found strong effects (AUC = 0.92) → Our effects weaker, as expected (relationships more complex).

**Marital Prediction:** Gottman & Levenson (2000) predict divorce with 90%+ accuracy from behavior → Names add modest increment.

### 4.5 Strengths

1. **Pre-registered:** Hypotheses locked before data, preventing p-hacking
2. **Large Sample:** N = [5,000] provides power > 0.95
3. **Relative Success:** Controls for cohort differences
4. **Blind Testing:** Demonstrates genuine prediction, not post-hoc fitting
5. **Cross-Validation:** Effects replicate across samples
6. **Theory Comparison:** Adjudicates between competing accounts

### 4.6 Limitations

1. **Observational:** Cannot establish causality (names may proxy for confounds)
2. **Retrospective:** Selection bias (only observe marriages that happened)
3. **Cultural Specificity:** Primarily U.S. sample (generalizability unclear)
4. **Missing Moderators:** Personality, values, communication unmeasured
5. **Small Effects:** r = [X.XX] explains only [X]% variance
6. **Surname Focus:** Analyzed first names primarily (full names more complete)

### 4.7 Alternative Explanations

**Could effects be entirely spurious?**

Against this:
- Effects persist after controlling for cultural markers
- Replicate across eras and cultures
- Specific phonetic features (not just "any difference") predict

In favor:
- Small effect sizes suggest weak signal
- Many unmeasured confounds possible
- Baseline model already explains most variance

**Verdict:** Effects likely real but modest, with possible confounds remaining.

### 4.8 Philosophical Implications

**Free Will vs. Determinism:**

If names predict relationships, how much choice do we have? Our findings suggest:

- Names create weak probabilistic nudges (not destiny)
- 90-95% of variance remains individual agency
- Similar to height predicting basketball success (real but not deterministic)

**Observer Effect:**

Publication could create self-fulfilling prophecies. Mitigation:
- Emphasize small effects in all communication
- Never provide individual-level predictions
- Stress research context only

### 4.9 Ethical Considerations

**Risks:**
- Name-based discrimination in dating
- Anxiety about name compatibility
- Deterministic thinking ("my name doomed my marriage")

**Safeguards:**
- Aggregate reporting only
- Emphasize modest effects
- Refuse commercial applications
- Transparent limitations

### 4.10 Future Directions

1. **Longitudinal Studies:** Follow couples from dating → marriage → outcomes
2. **Intervention Studies:** Can changing naming choices alter outcomes? (surname hyphenation)
3. **Cross-Cultural Replication:** Test in non-Western cultures
4. **Mechanism Studies:** Mediation analyses to identify causal pathways
5. **Genetic Controls:** Twin studies to separate nature/nurture
6. **Neural Correlates:** fMRI studies of name compatibility perception

---

## 5. Conclusion

Names exhibit small but statistically significant associations with relationship outcomes (r = [X.XX], p < [.001]), explaining approximately [X]% of variance above baseline predictors. Effects replicate across eras, ages, and cultures, with [Theory X] showing strongest associations. While scientifically interesting, effect sizes are too modest for individual-level prediction, suggesting names create probabilistic nudges rather than deterministic paths.

These findings extend nominative determinism research to a new domain (relationships), demonstrating consistent small-to-moderate effects (r = 0.15-0.30) across diverse contexts. The universality of such effects raises intriguing questions about pattern-matching processes in human cognition and the subtle interplay between surface features and deep choices.

**Key Takeaway:** Names matter, but not that much. They create gentle probabilistic winds, not deterministic tides.

---

## References

[To be completed with full citations]

Amato, P. R., & Rogers, S. J. (1997). A longitudinal study of marital problems and subsequent divorce. *Journal of Marriage and Family, 59*(3), 612-624.

Gottman, J. M., & Levenson, R. W. (2000). The timing of divorce: Predicting when a couple will divorce over a 14-year period. *Journal of Marriage and Family, 62*(3), 737-745.

Jung, K., Shavitt, S., Viswanathan, M., & Hilbe, J. M. (2014). Female hurricanes are deadlier than male hurricanes. *Proceedings of the National Academy of Sciences, 111*(24), 8782-8787.

Karney, B. R., & Bradbury, T. N. (1995). The longitudinal course of marital quality and stability: A review of theory, method, and research. *Psychological Bulletin, 118*(1), 3-34.

Kreider, R. M., & Ellis, R. (2011). Number, timing, and duration of marriages and divorces: 2009. *Current Population Reports*, P70-125.

Lehrer, E. L. (2008). Age at marriage and marital instability: Revisiting the Becker–Landes–Michael hypothesis. *Journal of Population Economics, 21*(2), 463-484.

Livio, M. (2002). *The golden ratio: The story of phi, the world's most astonishing number*. Broadway Books.

Mehrabian, A. (2001). Characteristics attributed to individuals on the basis of their first names. *Genetic, Social, and General Psychology Monographs, 127*(1), 59-88.

Pelham, B. W., Mirenberg, M. C., & Jones, J. T. (2002). Why Susie sells seashells by the seashore: Implicit egotism and major life decisions. *Journal of Personality and Social Psychology, 82*(4), 469-487.

Schwartz, C. R. (2013). Trends and variation in assortative mating: Causes and consequences. *Annual Review of Sociology, 39*, 451-470.

Silberzahn, R., & Uhlmann, E. L. (2013). It pays to be Herr Kaiser: Germans with noble-sounding surnames more often work as managers than as employees. *Psychological Science, 24*(12), 2437-2444.

Smerconish, M. A., Jr. (2025). Universal constants in nominative determinism: Discovery of gravitational and dark energy analogs in name-outcome relationships. *[Journal TBD]*.

---

## Supplementary Materials

**Supplement A:** Pre-registration document (full hypotheses and analysis plan)  
**Supplement B:** Data sources and collection procedures  
**Supplement C:** Complete statistical output (all models)  
**Supplement D:** Subgroup analyses (detailed)  
**Supplement E:** Blind testing protocol and results  
**Supplement F:** Code repository and reproducibility materials

---

**Manuscript Status:** TEMPLATE - To be completed after data analysis  
**Word Count:** [TBD]  
**Figures:** [6 planned]  
**Tables:** [6 planned]  
**Supplement Pages:** [TBD]

**Target Journals:**
1. *Psychological Science* (Tier 1)
2. *PNAS* (Tier 1)
3. *Journal of Personality and Social Psychology* (Tier 1)
4. *Social Psychological and Personality Science* (Tier 2)

**Expected Timeline:**
- Data collection: 3-6 months
- Analysis: 2 months
- Manuscript writing: 2 months
- Submission: [Target date]

