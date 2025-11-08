# MLB Analysis - Methodology

**Study Design:** Cross-sectional with temporal and cultural stratification  
**Sample Size:** 2,500-3,000 players  
**Temporal Range:** 75 years (1950-2024)  
**Data Source:** Baseball Reference

---

## Data Collection

### Stratification Strategy

**By Position Group:**
- Pitchers: 800 (400 SP, 300 RP, 100 CL)
- Catchers: 200
- Infielders: 800 (200 per position)
- Outfielders: 600 (200 per position)
- DH: 100

**By Era:**
- Classic (1950-1979): ~750 players
- Modern (1980-1999): ~900 players
- Contemporary (2000-2024): ~850 players

**Inclusion Criteria:**
- Minimum 100 career games
- Complete name and position data
- Career statistics available

---

## Statistical Analyses

### 1. Position Prediction
- Random Forest classification
- 5-fold cross-validation
- Target accuracy: 60-65%

### 2. Pitcher Analysis
- T-tests (pitchers vs position players)
- ANOVA (SP vs RP vs CL)
- Effect sizes (Cohen's d)

### 3. Power Analysis
- Correlation (harshness ↔ home runs)
- T-tests (power vs contact hitters)
- Control for era and position

### 4. Temporal Evolution
- Linear trends (year → syllables)
- Era comparisons (ANOVA)
- Inflection point analysis (1990, 2000)

### 5. Internationalization
- Pre/post-1990 comparison
- By name origin (Anglo/Latino/Asian)
- Effect sizes

### 6. Closer Effect
- T-test (closers vs starters)
- Memorability comparison

---

## Control Variables

- Debut year (temporal confound)
- Birth country (cultural confound)
- Draft round (talent indicator)
- Position group (for non-position analyses)

---

**Methodology Version:** 1.0  
**Last Updated:** November 8, 2025

