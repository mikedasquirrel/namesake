# Nominative Matchmaker: Marriage Prediction Research

**Principal Investigator:** Michael Andrew Smerconish Jr  
**Study Type:** Pre-registered observational study  
**Status:** Implementation complete, ready for data collection  
**Date:** November 8, 2025

---

## Study Overview

This research tests whether phonetic, semantic, and structural interactions between partners' names predict relationship outcomes (marriage longevity, divorce risk, quality) above and beyond societal baseline expectations.

**Key Innovation:** Uses "relative success" framework rather than binary outcomes, controlling for cohort effects (age, era, geography).

---

## Implementation Status

### ✅ Completed Components

1. **Research Design & Pre-Registration**
   - Full hypothesis pre-registration (`docs/MARRIAGE_PREDICTION_STUDY.md`)
   - Power analysis (N=5,000 target, power>0.95)
   - Analysis plan locked before data collection

2. **Theoretical Framework**
   - Extended relationship formulas with advanced phonetic analysis
   - Four compatibility theories implemented:
     - Similarity (similar names → compatible)
     - Complementarity (opposite names → balance)
     - Golden Ratio (φ relationship → harmony)
     - Resonance (harmonic ratios → success)

3. **Database Models**
   - `MarriedCouple` model with full demographics
   - `MarriageAnalysis` model with all interaction metrics
   - `ChildName` model for parent-child analysis
   - `DivorceBaseline` model for relative success calculation
   - `PredictionLock` model for blind testing audit trail

4. **Analysis Engine**
   - `RelationshipCompatibilityAnalyzer` (full statistical models)
   - Relative success calculator with cohort baselines
   - Theory comparison engine
   - Children's name analysis

5. **Data Collection Framework**
   - `MarriageCollector` (public records template)
   - `CelebrityMarriageCollector` (Wikipedia/IMDb scraper template)
   - Baseline statistics collector (CDC/Census)

6. **Validation Framework**
   - Blind testing protocol (`scripts/marriage_blind_test.py`)
   - Cross-validation pipeline
   - Subgroup analysis templates

7. **Documentation**
   - Data sources guide (`docs/MARRIAGE_DATA_SOURCES.md`)
   - Manuscript template (`papers/MARRIAGE_PREDICTION_MANUSCRIPT.md`)
   - Ethical safeguards documentation

---

## Directory Structure

```
FlaskProject/
├── core/
│   ├── marriage_models.py              # Database models
│   └── domain_configs/
│       └── marriage.yaml               # Domain configuration
│
├── analyzers/
│   └── relationship_compatibility_analyzer.py  # Main analysis engine
│
├── collectors/
│   └── marriage_collector.py           # Data collection
│
├── utils/
│   └── relationship_formulas.py        # Name interaction metrics
│
├── scripts/
│   ├── marriage_prediction_study.py    # Full pipeline
│   └── marriage_blind_test.py          # Blind testing
│
├── docs/
│   ├── MARRIAGE_PREDICTION_STUDY.md    # Pre-registration
│   └── MARRIAGE_DATA_SOURCES.md        # Data acquisition guide
│
├── papers/
│   └── MARRIAGE_PREDICTION_MANUSCRIPT.md  # Publication template
│
└── analysis_outputs/
    └── marriage/                       # Results directory
```

---

## How to Run the Study

### Phase 1: Setup & Approval (2-4 weeks)

1. **Obtain IRB Approval**
   - Submit protocol to institutional review board
   - Use template in `docs/MARRIAGE_PREDICTION_STUDY.md`
   - Emphasize: public records, de-identified, research only

2. **Set Up Database**
   ```bash
   python manage.py db init
   python manage.py db migrate
   python manage.py db upgrade
   ```

3. **Configure Data Sources**
   - Review `docs/MARRIAGE_DATA_SOURCES.md`
   - Obtain necessary permissions/subscriptions
   - Test API access

### Phase 2: Data Collection (8-12 weeks)

1. **Collect Baseline Statistics**
   ```python
   from collectors.marriage_collector import MarriageCollector
   
   collector = MarriageCollector()
   baselines = collector.collect_baseline_statistics()
   
   # Save to database
   for baseline in baselines:
       db.session.add(baseline)
   db.session.commit()
   ```

2. **Collect Marriage Records**
   ```python
   # Target: 5,000 couples, stratified by era
   couples = collector.collect_sample(target_size=5000, stratify_by_era=True)
   
   for couple in couples:
       db.session.add(couple)
   db.session.commit()
   ```

3. **Collect Celebrity Data**
   ```python
   from collectors.marriage_collector import CelebrityMarriageCollector
   
   celeb_collector = CelebrityMarriageCollector()
   celebrities = celeb_collector.collect_celebrity_marriages(target_size=1000)
   ```

### Phase 3: Analysis (6-8 weeks)

1. **Run Full Pipeline**
   ```python
   from scripts.marriage_prediction_study import MarriagePredictionStudy
   
   study = MarriagePredictionStudy()
   study.run_full_pipeline()
   ```

   This executes:
   - Feature engineering (name analysis)
   - Baseline model fitting
   - Name interaction models
   - Theory comparison
   - Cross-validation
   - Subgroup analyses
   - Constants testing

2. **Blind Testing Validation**
   ```python
   from scripts.marriage_blind_test import MarriageBlindTestFramework
   
   framework = MarriageBlindTestFramework(db.session)
   
   # Step 1: Generate blind predictions
   test_couples = [(name1, name2, id) for ...]  # Names only
   predictions = framework.generate_blind_predictions(test_couples)
   
   # Step 2: (Later) Reveal outcomes and test
   actual_outcomes = {id: {'is_divorced': bool, 'duration': float}}
   results = framework.reveal_and_test(actual_outcomes)
   ```

3. **Generate Reports**
   - Results automatically saved to `analysis_outputs/marriage/`
   - JSON files for all analyses
   - Publication-ready figures and tables

### Phase 4: Publication (8-12 weeks)

1. **Complete Manuscript**
   - Use template in `papers/MARRIAGE_PREDICTION_MANUSCRIPT.md`
   - Fill in results sections
   - Create figures and tables
   - Write discussion

2. **Submit to Journal**
   - Target: *Psychological Science*, *PNAS*, or *JPSP*
   - Include all supplementary materials
   - Pre-registration documentation

---

## Key Features

### 1. Relative Success Framework

Unlike binary "divorced/not divorced", we calculate:

```
Relative_Success = Actual_Duration / Expected_Duration
```

Where `Expected_Duration` is based on:
- Age at marriage (younger → shorter expected)
- Marriage year (1980s → higher divorce rates)
- Geography (regional differences)
- Urban vs. rural

**Advantage:** Controls for cohort effects, more nuanced measurement.

### 2. Name Interaction Metrics

**Phonetic Interactions:**
- Edit distance (how different are the names?)
- Vowel harmony (do vowels complement?)
- Consonant compatibility (similar consonant patterns?)
- Stress alignment (rhythmic similarity)

**Structural Interactions:**
- Syllable ratio (approaching φ = 1.618?)
- Complexity balance (similar complexity?)
- Length balance

**Semantic Interactions:**
- Cultural origin match (same background?)
- Social class alignment (similar SES indicators?)

### 3. Four Competing Theories

**Similarity:** Similar names → compatibility  
**Complementarity:** Opposite names → balance  
**Golden Ratio:** φ relationship → optimal harmony  
**Resonance:** Harmonic ratios → success

Analysis adjudicates which theory best predicts outcomes.

### 4. Blind Testing Protocol

1. Generate predictions from names only
2. **Lock predictions** with cryptographic timestamp
3. Later: reveal actual outcomes
4. Calculate prediction accuracy

**Purpose:** Prevents p-hacking, demonstrates genuine prediction.

### 5. Children's Names Analysis

Tests hypotheses:
- **Blending:** Successful couples create blended name styles
- **Dominance:** One partner's style dominates → power imbalance
- **Innovation:** Happy couples choose creative names

---

## Expected Results

Based on pre-registered hypotheses and prior nominative determinism research:

**Primary Hypothesis (H1):**
- Name compatibility predicts relative success: **r = 0.15-0.25** (expected)
- Statistical significance: **p < 0.001**
- Variance explained: **ΔR² = 0.03-0.10** above baseline

**Theory Comparison (H2):**
- One theory will dominate (likely similarity or golden ratio)
- Winner: **r > 0.20**, survives Bonferroni correction

**Replication (H3):**
- Effects stable across eras (1980s→2020s)
- Effects universal across cultures
- Possible age moderation (stronger for younger)

**Children's Names (H4):**
- Blending score correlates with success: **r = 0.10-0.15**
- Dominance pattern predicts power dynamics

---

## Philosophical & Ethical Considerations

### Free Will vs. Determinism

If names predict relationships, what does this mean for human agency?

**Our Position:**
- Names create weak probabilistic nudges (not destiny)
- Effect sizes small (r ~ 0.20 = ~4% variance)
- 96% of outcomes remain individual choice, effort, circumstances
- Similar to height predicting basketball (real but not deterministic)

### Ethical Safeguards

1. **No Individual Predictions:** Only aggregate patterns reported
2. **Emphasize Small Effects:** Always report r values and confidence intervals
3. **No Commercial Use:** Refuse dating app partnerships
4. **Transparent Limitations:** Discuss confounds, alternative explanations
5. **Careful Communication:** Avoid sensationalization

### Communication Strategy

**Tier 1: Academic Audience**
- Full disclosure of methods, limitations
- Emphasize relative success framework
- Discuss causal inference challenges

**Tier 2: Scientific Press**
- Frame as pattern discovery, not prediction tool
- Emphasize small effects (85-90% variance is other factors)
- Avoid clickbait framing

**Tier 3: Public**
- **DO NOT release** as "name compatibility calculator"
- **DO NOT license** to dating platforms
- If discussed: emphasize research context, modest effects

---

## Statistical Power

**Goal:** Detect r ≥ 0.15 with power = 0.80 at α = 0.05

**Required Sample Size:** ~800 couples

**Planned Sample Size:** 5,000 couples

**Achieved Power:** >0.95 (allows robust subgroup analyses)

**Rationale:**
- Small effects require large samples
- Need 500+ per subgroup (era, age, culture)
- Enables interaction tests
- Robust to missing data

---

## Success Criteria

### Study Succeeds If:

1. ✅ Collect 5,000+ couples with <10% missing data
2. ✅ Primary hypothesis supported: r ≥ 0.15, p < 0.001
3. ✅ At least one theory significant after Bonferroni correction
4. ✅ Effects replicate across eras and cultures
5. ✅ Blind testing shows above-chance prediction
6. ✅ Publish in top-tier journal

### Study Fails If:

1. ❌ Primary r < 0.10 or p > 0.05
2. ❌ All theories fail after correction
3. ❌ Effects reverse across samples (instability)
4. ❌ Blind testing at chance level
5. ❌ Effects disappear after confound controls

**Falsifiability:** Study designed to fail if effects are not real.

---

## Limitations

1. **Observational:** Cannot establish causality (names may proxy for unmeasured confounds)
2. **Retrospective:** Selection bias (only observe marriages that happened)
3. **Cultural Specificity:** Primarily U.S. sample (generalizability uncertain)
4. **Small Effects:** r ~ 0.20 explains only 4% of variance
5. **Missing Moderators:** Personality, values, communication patterns unmeasured

---

## Contact & Collaboration

**Principal Investigator:** Michael Andrew Smerconish Jr  
**Email:** [Contact Information]  
**Project Page:** [URL if applicable]

**Collaboration Welcome For:**
- International replication studies
- Cross-cultural validation
- Methodological improvements
- Longitudinal extensions

**Not Open To:**
- Commercial applications
- Individual-level predictions
- Dating platform partnerships

---

## Citation

If using this framework, please cite:

```
Smerconish, M. A., Jr. (2025). Nominative Matchmaker: Marriage Prediction 
Research Framework. [GitHub/Project URL].
```

Manuscript (when published):
```
Smerconish, M. A., Jr. (202X). Name Compatibility and Relationship Outcomes: 
A Nominative Determinism Analysis. [Journal], [Volume](Issue), [Pages].
```

---

## License

**Research Use:** Open for academic/research purposes  
**Commercial Use:** Prohibited without explicit permission  
**Data Sharing:** De-identified data available after publication  
**Code:** MIT License (analysis code), research data restricted

---

## Acknowledgments

This research builds on decades of nominative determinism research, particularly:
- Pelham et al. (2002) on implicit egotism
- Jung et al. (2014) on hurricane names
- Gottman & Levenson (2000) on marital prediction

Special thanks to the nominative determinism research community for establishing this fascinating field.

---

## Version History

- **v1.0** (November 8, 2025): Initial implementation complete
- **v1.1** (TBD): Data collection begins
- **v2.0** (TBD): Analysis complete, manuscript draft
- **v3.0** (TBD): Publication, data release

---

**Last Updated:** November 8, 2025  
**Status:** Ready for data collection phase  
**Next Milestone:** IRB approval and data acquisition

