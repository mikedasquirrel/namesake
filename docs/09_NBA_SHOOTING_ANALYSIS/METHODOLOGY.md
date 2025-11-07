# NBA Shooting Percentage Analysis - Detailed Methodology

## Research Design

### Study Type
- **Design:** Retrospective observational study
- **Approach:** Quantitative linguistic analysis with statistical modeling
- **Timeframe:** 1950-2025 (75 years of NBA history)
- **Domain:** Professional basketball (NBA)

### Hypotheses

**Primary Hypothesis:**
> Linguistic features of player names correlate with shooting performance metrics (FT%, 3PT%), independent of talent, position, and era.

**Secondary Hypotheses:**
1. Soft phonetic features (liquids, nasals) correlate positively with shooting accuracy
2. The correlation strengthens in the modern 3-point era (2010+)
3. The effect is strongest for guards, weakest for centers
4. Elite shooters have distinct linguistic profiles from poor shooters

**Null Hypothesis:**
> There is no significant correlation between name linguistics and shooting performance (r = 0, p > 0.05).

---

## Data Collection

### Player Selection Criteria

**Inclusion Criteria:**
- Played in NBA during 1950-2025
- ≥100 games played (minimum threshold for statistical validity)
- Complete name data available
- Shooting statistics recorded

**Exclusion Criteria:**
- <100 games played (insufficient sample size)
- Missing shooting data
- Name data unavailable or ambiguous

**Final Sample:**
- **Total Players:** 4,823
- **With FT Data:** 4,612 (95.6%)
- **With 3PT Data:** 3,294 (68.3%, post-1979 only)
- **With Both:** 3,178 (65.9%)

### Data Sources

1. **Basketball-Reference.com**
   - Career statistics (FT%, 3PT%, FG%)
   - Games played, minutes, usage rates
   - Position, era, teams
   - Draft information

2. **NBA Official Stats API**
   - Advanced metrics (True Shooting %, Effective FG%)
   - Shot location data
   - Clutch performance stats

3. **Linguistic Data**
   - Carnegie Mellon Pronouncing Dictionary
   - Custom phonetic transcription
   - Syllable counting algorithms
   - Phonosemantic scoring

### Variables

**Dependent Variables (Outcomes):**
```python
shooting_metrics = {
    'ft_percentage': float,      # Free throw percentage (0-1)
    'three_point_percentage': float,  # 3-point percentage (0-1)
    'fg_percentage': float,      # Field goal percentage (0-1)
    'combined_shooting_score': float  # Weighted avg: 0.6*FT + 0.4*3PT
}
```

**Independent Variables (Predictors):**
```python
linguistic_features = {
    # Basic metrics
    'syllable_count': int,           # Total syllables in full name
    'character_length': int,         # Total characters
    'word_count': int,               # Number of words (first, middle, last)
    
    # Phonetic features
    'softness_score': float,         # Liquid/nasal phonemes (0-100)
    'harshness_score': float,        # Plosive/fricative phonemes (0-100)
    'rhythm_score': float,           # Phonetic flow (0-100)
    'vowel_ratio': float,            # Proportion of vowels (0-1)
    
    # Advanced features
    'memorability_score': float,     # Name recall ease (0-100)
    'pronounceability_score': float, # Ease of pronunciation (0-100)
    'uniqueness_score': float,       # Name rarity (0-100)
    'alliteration_score': float,     # First/last initial match (0-100)
    
    # Component analysis
    'first_name_syllables': int,
    'last_name_syllables': int,
    'first_name_memorability': float,
    'last_name_memorability': float
}
```

**Control Variables:**
```python
controls = {
    'position_group': str,          # Guard, Forward, Center
    'era': int,                     # Decade of debut (1950-2020)
    'games_played': int,            # Career games
    'ppg': float,                   # Points per game (talent proxy)
    'usage_rate': float,            # Shot volume
    'draft_position': int,          # Draft order (talent proxy)
}
```

---

## Linguistic Analysis Pipeline

### 1. Name Preprocessing

```python
def preprocess_name(name: str) -> dict:
    """Extract name components and basic metrics."""
    parts = name.strip().split()
    
    return {
        'full_name': name,
        'first_name': parts[0] if len(parts) > 0 else '',
        'last_name': parts[-1] if len(parts) > 1 else '',
        'middle_name': parts[1] if len(parts) > 2 else '',
        'word_count': len(parts),
        'character_length': len(name.replace(' ', ''))
    }
```

### 2. Phonetic Transcription

**Method:** Carnegie Mellon Pronouncing Dictionary (CMUdict) + fallback heuristics

```python
def get_phonemes(name: str) -> List[str]:
    """Convert name to phoneme list."""
    # Example: "Kobe" → ['K', 'OW1', 'B', 'IY0']
    # Example: "LeBron" → ['L', 'AH0', 'B', 'R', 'AA1', 'N']
    ...
```

**Phoneme Categories:**
- **Plosives (harsh):** /p/, /b/, /t/, /d/, /k/, /g/
- **Fricatives (harsh):** /f/, /v/, /s/, /z/, /ʃ/, /ʒ/
- **Liquids (soft):** /l/, /r/
- **Nasals (soft):** /m/, /n/, /ŋ/
- **Glides (soft):** /w/, /j/
- **Vowels (neutral):** /a/, /e/, /i/, /o/, /u/

### 3. Softness Score Calculation

```python
def calculate_softness_score(phonemes: List[str]) -> float:
    """
    Score based on proportion of soft phonemes.
    
    Formula:
        softness = (liquid_count + nasal_count + glide_count) / total_consonants
        
    Normalized to 0-100 scale.
    """
    soft_phonemes = ['L', 'R', 'M', 'N', 'NG', 'W', 'Y']
    soft_count = sum(1 for p in phonemes if p in soft_phonemes)
    consonant_count = sum(1 for p in phonemes if is_consonant(p))
    
    if consonant_count == 0:
        return 50.0  # Neutral score
    
    ratio = soft_count / consonant_count
    return min(100.0, ratio * 150)  # Scale and cap at 100
```

### 4. Harshness Score Calculation

```python
def calculate_harshness_score(phonemes: List[str]) -> float:
    """
    Score based on proportion of harsh phonemes.
    
    Formula:
        harshness = (plosive_count + fricative_count) / total_consonants
        
    Normalized to 0-100 scale.
    """
    harsh_phonemes = ['P', 'B', 'T', 'D', 'K', 'G', 'F', 'V', 'S', 'Z', 'SH', 'ZH']
    harsh_count = sum(1 for p in phonemes if p in harsh_phonemes)
    consonant_count = sum(1 for p in phonemes if is_consonant(p))
    
    if consonant_count == 0:
        return 50.0
    
    ratio = harsh_count / consonant_count
    return min(100.0, ratio * 150)
```

### 5. Rhythm Score Calculation

```python
def calculate_rhythm_score(name: str, syllables: int) -> float:
    """
    Measure phonetic flow and rhythmic smoothness.
    
    Factors:
    - Consonant cluster complexity
    - Vowel-consonant alternation
    - Syllable stress patterns
    """
    # Simplified example
    alternation_score = measure_vc_alternation(name)
    cluster_penalty = count_consonant_clusters(name)
    stress_balance = measure_stress_balance(name)
    
    rhythm = (alternation_score * 0.4 + 
              (100 - cluster_penalty * 10) * 0.3 +
              stress_balance * 0.3)
    
    return max(0, min(100, rhythm))
```

---

## Statistical Analysis

### 1. Correlation Analysis

**Method:** Pearson Product-Moment Correlation

```python
from scipy import stats

# For each linguistic feature
corr, p_value = stats.pearsonr(
    df['linguistic_feature'],
    df['ft_percentage']
)

# Significance threshold: p < 0.05
is_significant = p_value < 0.05
```

**Interpretation:**
- **|r| < 0.1:** Negligible correlation
- **0.1 ≤ |r| < 0.3:** Weak correlation
- **0.3 ≤ |r| < 0.5:** Moderate correlation
- **0.5 ≤ |r| < 0.7:** Strong correlation
- **|r| ≥ 0.7:** Very strong correlation

### 2. Regression Modeling

**Algorithm:** Random Forest Regressor

**Why Random Forest?**
- Handles non-linear relationships
- Robust to multicollinearity
- Provides feature importance
- No assumptions about data distribution

```python
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score

# Train model
model = RandomForestRegressor(
    n_estimators=100,
    max_depth=10,
    random_state=42,
    min_samples_split=10
)

# 5-fold cross-validation
cv_scores = cross_val_score(
    model, X, y, 
    cv=5, 
    scoring='r2'
)

# Feature importance
importances = model.feature_importances_
```

**Model Evaluation Metrics:**
- **R² Score:** Proportion of variance explained
- **RMSE:** Root Mean Square Error (in percentage points)
- **Cross-validation R²:** Average R² across 5 folds
- **Feature Importance:** Relative predictive power

### 3. Elite vs Poor Shooter Comparison

**Method:** Independent Samples T-Test

**Thresholds:**
- **Elite FT Shooters:** ≥85% career FT%
- **Poor FT Shooters:** <65% career FT%
- **Elite 3PT Shooters:** ≥38% career 3PT%
- **Poor 3PT Shooters:** <30% career 3PT%

```python
from scipy import stats

# Compare linguistic features
t_stat, p_value = stats.ttest_ind(
    elite_shooters['softness_score'],
    poor_shooters['softness_score']
)

# Effect size (Cohen's d)
effect_size = (elite_mean - poor_mean) / pooled_std
```

**Effect Size Interpretation:**
- **|d| < 0.2:** Small effect
- **0.2 ≤ |d| < 0.5:** Medium effect
- **0.5 ≤ |d| < 0.8:** Large effect
- **|d| ≥ 0.8:** Very large effect

### 4. Position Stratification

**Method:** Subgroup Analysis

```python
for position in ['Guard', 'Forward', 'Center']:
    position_df = df[df['position_group'] == position]
    
    # Run correlation analysis for this position
    corr, p_value = stats.pearsonr(
        position_df['softness_score'],
        position_df['ft_percentage']
    )
```

**Interaction Effects:**
Test whether the name-shooting correlation differs by position:

```python
# Include interaction term
model = 'ft_percentage ~ softness_score * position_group'
```

### 5. Era Analysis

**Method:** Time-Series Correlation

```python
eras = [1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020]

era_correlations = {}
for era in eras:
    era_df = df[df['era'] == era]
    corr, p_value = stats.pearsonr(
        era_df['softness_score'],
        era_df['ft_percentage']
    )
    era_correlations[era] = {'r': corr, 'p': p_value}
```

**Trend Analysis:**
Test whether correlation strength increases over time:

```python
# Linear regression: correlation ~ year
trend_model = LinearRegression()
trend_model.fit(years, correlations)
trend_slope = trend_model.coef_[0]
```

---

## Quality Control

### Data Validation

1. **Outlier Detection:**
   ```python
   # Remove statistical outliers (>3 SD from mean)
   z_scores = np.abs(stats.zscore(df['ft_percentage']))
   df = df[z_scores < 3]
   ```

2. **Missing Data Handling:**
   - FT% missing: Exclude from FT analysis (but include in 3PT)
   - 3PT% missing for pre-1979: Expected (no 3PT line)
   - Name missing: Exclude entirely

3. **Consistency Checks:**
   - FT% should be 0-1 (or 0-100%)
   - Games played should be ≥100
   - Syllable count should be ≥1

### Bias Mitigation

1. **Survivorship Bias:**
   - Include short-career players (100+ games, not just stars)
   - Don't require All-Star selections or awards

2. **Era Bias:**
   - Stratify analysis by decade
   - Control for rule changes (3PT line introduction)

3. **Position Bias:**
   - Analyze positions separately
   - Don't compare guards to centers directly

4. **Name Length Bias:**
   - Include international players (longer names)
   - Don't exclude based on name complexity

---

## Limitations

### 1. Correlation ≠ Causation
- We observe associations, not causal effects
- Name doesn't cause shooting ability
- Selection bias likely explains most patterns

### 2. Confounding Variables
- Coaching quality
- Training facilities
- Injury history
- Mental factors (confidence, focus)
- Shot selection (easier shots → higher %)

### 3. Sample Size Constraints
- Pre-1979: No 3PT data (N/A)
- 1950s-1960s: Smaller league (fewer players)
- International players: Underrepresented in early eras

### 4. Phonetic Transcription Accuracy
- CMUdict doesn't cover all names
- International names may have incorrect pronunciations
- Nickname usage not always captured

### 5. Measurement Error
- Shooting % varies by season (small sample noise)
- Career % more stable but hides development
- No context (garbage time vs clutch shots)

---

## Reproducibility

### Code Availability
All analysis code is open-source:
```
analyzers/nba_shooting_analyzer.py
scripts/nba_shooting_deep_dive.py
```

### Random Seeds
```python
np.random.seed(42)
random_state = 42  # All models
```

### Software Versions
```
Python: 3.9+
pandas: 1.3.0+
numpy: 1.21.0+
scikit-learn: 0.24.0+
scipy: 1.7.0+
```

### Data Access
- Basketball-Reference: Public (web scraping with rate limits)
- CMUdict: Public domain
- Analysis outputs: Saved in `analysis_outputs/current/`

---

## Ethics & Transparency

### Potential Harms
1. **Stereotyping:** Don't use findings to judge individuals
2. **Discrimination:** Don't use in draft decisions or contracts
3. **Self-fulfilling prophecy:** Awareness may reinforce bias

### Responsible Use
- Findings are **descriptive**, not **prescriptive**
- Use to identify bias, not perpetuate it
- Individual talent always trumps name patterns

### Transparency
- All methods documented
- All code open-source
- All assumptions stated
- All limitations acknowledged

---

## Future Improvements

### Methodological
1. **Causal Inference:** Propensity score matching, instrumental variables
2. **Longitudinal:** Track shooting development year-by-year
3. **Bayesian:** Model uncertainty in correlations
4. **Clustering:** Group players by name-shooting profiles

### Data
1. **Shot Charts:** Analyze shot location (corner 3s vs top of key)
2. **Clutch Stats:** Late-game FT% vs regular FT%
3. **Coach Interviews:** Qualitative insights on role assignment
4. **International Leagues:** Compare NBA to EuroLeague, CBA

### Analysis
1. **Nickname Effects:** Do nicknames change shooting opportunities?
2. **Announcer Analysis:** Quantify name mention frequency
3. **Social Media:** Analyze player brand strength by name
4. **Contract Value:** Model name-shooting effect on salary

---

**Document Version:** 1.0  
**Last Updated:** November 7, 2025  
**Author:** FlaskProject Research Team

