# Board Game Nomenclature Analysis - Methodology

**Study Design:** Cross-sectional observational with temporal and cultural stratification  
**Sample Size:** 2,000 games  
**Temporal Range:** 75 years (1950-2024)  
**Data Source:** BoardGameGeek XML API

---

## Data Collection

### Primary Source: BoardGameGeek API

**Endpoint:** `https://boardgamegeek.com/xmlapi2/`  
**Rate Limiting:** 2 requests per second (conservative: 1.7 req/sec implemented)  
**Data Points:** Game details, ratings, complexity, designer info

**Fields Collected:**
- Name (primary)
- BGG ID (unique identifier)
- Year published
- BGG rating (Geek Rating)
- Average user rating
- Number of ratings
- Complexity weight (1-5 scale)
- Ownership count
- Player counts (min/max)
- Playing time
- Minimum age
- Categories and mechanics
- Designer name and nationality
- Publisher
- BGG rank (overall and category)

### Sampling Strategy

**Stratified by Era:**
- Classic (1950-1979): 200 games
- Golden Age (1980-1999): 400 games
- Modern (2000-2009): 600 games
- Contemporary (2010-2024): 800 games

**Selection Criteria:**
- Minimum 100 ratings (quality threshold)
- Ranked in BGG database
- Complete metadata (year, category, designer)
- Balanced across game categories

**Quality Filters:**
- Exclude prototypes and unreleased games
- Exclude games with < 100 ratings (insufficient data)
- Require complete name and year information

---

## Linguistic Analysis

### Phonetic Feature Extraction

**Standard Suite (12 features):**
1. Syllable count
2. Word count
3. Character length
4. Harshness score (0-100)
5. Smoothness score (0-100)
6. Plosive ratio (b, p, t, d, k, g)
7. Fricative ratio (f, v, s, z, th, sh)
8. Vowel ratio
9. Consonant cluster density
10. Phonetic complexity
11. Sound symbolism score
12. Alliteration score

**Structural Features (6):**
- Contains colon (expansion pattern)
- Contains number
- Contains article ("The", "A")
- Is fantasy name (made-up words)
- Is Latin-derived
- Is compound word

**Semantic Features (4):**
- Name type (descriptive/abstract/thematic/compound/portmanteau)
- Memorability score (0-100)
- Pronounceability score (0-100)
- Semantic transparency (theme clarity)

---

## Statistical Analyses

### Analysis 1: Descriptive Statistics
- Calculate means, SDs by era and category
- Distribution analyses (syllables, ratings, complexity)
- Frequency tables (name types, cultural origins)

### Analysis 2: Cluster Analysis
- K-means clustering (k=5) on phonetic + semantic features
- Silhouette score validation
- Cluster profiling (characteristics + example games)
- Database updates with cluster assignments

### Analysis 3: Temporal Evolution
- Linear trends (year → syllable count)
- Era comparisons (ANOVA across 4 eras)
- Correlation analysis (year vs name features)
- Effect size calculations (Cohen's d between eras)

### Analysis 4: Cultural Comparison
- Nationality grouping (US vs DE vs GB vs JP vs FR)
- T-tests for pairwise comparisons
- Effect sizes (Cohen's d)
- Name type distribution analysis

### Analysis 5: Success Prediction
- Random Forest regression (name features → BGG rating)
- Feature importance ranking
- Cross-validation (5-fold)
- Train/test split (80/20)
- R² and RMSE metrics
- Simple correlations (Pearson r)

### Analysis 6: Complexity Correlation
- Pearson correlation (name complexity ↔ game complexity)
- Categorization by game weight (light/medium/heavy)
- T-tests across complexity categories
- Control for confounds (year, category)

---

## Hypothesis Testing Framework

### Statistical Thresholds
- α = 0.05 (significance level)
- Power: 0.80 minimum
- Effect sizes: Cohen's conventions (small: 0.2, medium: 0.5, large: 0.8)
- Correlation thresholds: weak < 0.3, moderate 0.3-0.5, strong > 0.5

### Control Variables
- Year published (temporal confound)
- Game category (strategy vs party vs family)
- Designer prominence
- Publisher size

### Validation Methods
- Train/test split for predictions
- Cross-validation for model stability
- Bootstrap resampling for CIs
- Permutation tests for small samples

---

## Quality Assurance

### Data Completeness
- Minimum 85% complete data required
- Missing value handling: imputation for numerical, mode for categorical
- Outlier detection: z-score > 3.5 flagged

### Sample Adequacy
- Minimum 150 games per era
- Minimum 10 games per nationality for cultural comparison
- Power analysis confirms adequate sample for r = 0.15 detection

### Reproducibility
- All analysis code in `analyzers/board_game_statistical_analyzer.py`
- Random seed: 42 (for clustering and model training)
- Complete parameter logging
- Results cached in database (PreComputedStats table)

---

## Limitations

1. **BGG Sampling Bias:** Data represents games popular enough to be rated, excludes obscure/failed games
2. **Survivorship Bias:** Older games over-represent successes (failures forgotten)
3. **Cultural Proxy:** Designer nationality approximates game tradition (imperfect)
4. **Causality:** All findings are correlational—names may predict but don't necessarily cause success
5. **English-Centric:** Analysis optimized for English phonetics, may miss non-English patterns

---

## Ethical Considerations

- **No Designer Identification:** Designer names aggregated by nationality only
- **Transparent Null Results:** Report all findings, even if hypotheses unsupported
- **No Commercial Advantage:** Findings public, not proprietary trading signals
- **Academic Integrity:** Full methodology disclosure, reproducible analysis

---

**Methodology Version:** 1.0  
**Last Updated:** November 8, 2025  
**Principal Investigator:** Research Team

