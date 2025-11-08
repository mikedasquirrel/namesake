# Immigration Surname Semantic Meaning: Detailed Methodology

**Research Design**: Etymology-Based Quantitative Analysis  
**Version**: 2.0 (Semantic Meaning Focus)  
**Last Updated**: November 7, 2025

---

## Research Question

**Does the semantic meaning of your surname in its original language predict US immigration rates and settlement patterns?**

Comparing:
- **Toponymic** (place-meaning): Galilei, Romano, Berliner, London, Paris
- **Occupational** (job-meaning): Shoemaker, Smith, Baker, Ferrari, Fischer
- **Descriptive** (trait-meaning): Brown, Long, Klein, Rossi, Gross
- **Patronymic** (father's name): Johnson, O'Brien, Martinez, Ivanov
- **Religious** (religious-meaning): Christian, Bishop, Cohen, Santo

---

## Hypotheses

### H1: Toponymic vs Non-Toponymic Immigration Rates

**Null**: μ_toponymic = μ_non-toponymic  
**Alternative**: μ_toponymic ≠ μ_non-toponymic (two-tailed)  
**α** = 0.05

**Rationale**: Place-based surnames may indicate stronger homeland geographic identity, potentially affecting migration decisions. People named "Romano" (from Rome) may have different ties to their origin place than people named "Shoemaker" (job-based identity).

**Outcome Variable**: Immigration rate (immigrants per current bearer)

**Test**: Independent samples t-test, Cohen's d effect size

### H2: Toponymic Settlement Clustering

**Null**: HHI_toponymic = HHI_non-toponymic  
**Alternative**: HHI_toponymic > HHI_non-toponymic (one-tailed, directional)  
**α** = 0.05

**Rationale**: Toponymic surnames carry place-based identity, potentially leading to stronger ethnic enclave formation (clustering near origin-community members).

**Outcome Variable**: HHI (Herfindahl-Hirschman Index) of state-level concentration

**Metric**:
```
HHI = Σ(state_share²) × 10,000
where state_share = population_in_state / total_population
```

**Interpretation**:
- HHI > 2500: High concentration (ethnic enclave)
- HHI 1500-2500: Moderate concentration
- HHI < 1500: Dispersed (assimilated)

### H3: Temporal Dispersion by Category

**Null**: Dispersion_change = 0 for all categories  
**Alternative**: Dispersion_change > 0 (one-tailed)  
**α** = 0.05

**Rationale**: All immigrant groups disperse over time (assimilation), but toponymic surnames may retain clustering longer due to stronger place identity.

**Outcome Variable**: Dispersion change (Dispersion_2020 - Dispersion_1900)

**Test**: One-sample t-test by category, interaction ANOVA

### H4: Place Cultural Importance Effect

**Null**: ρ(place_importance, immigration_rate) = 0  
**Alternative**: ρ ≠ 0  
**α** = 0.05

**Rationale**: Famous places (Rome=100, Paris=100, London=100) may have different cultural meaning than obscure places (small towns=70), affecting immigration patterns.

**Tested Correlations**:
1. Place importance vs immigration rate
2. Place importance vs settlement HHI

**Applies to**: Toponymic surnames only (~200)

### H5: Cross-Category Comparisons

**Null**: μ₁ = μ₂ = μ₃ = μ₄ = μ₅ (all equal)  
**Alternative**: At least one pair differs  
**α** = 0.05

**Method**: One-way ANOVA with post-hoc pairwise comparisons

**Categories**: Toponymic, Occupational, Descriptive, Patronymic, Religious

**Pairwise Tests**: 10 comparisons with Bonferroni correction (α=0.01)

**Effect Size**: Eta-squared (η²)

### H6: Semantic × Origin Interactions

**Null**: No interaction effect  
**Alternative**: Semantic category effect varies by origin  
**α** = 0.05

**Method**: Two-way ANOVA (semantic × origin)

**Example**: Within Italian surnames, do toponymic (Romano) differ from occupational (Ferrari)?

**Tested Origins**: Italian, English, German, Spanish (major groups with multiple categories)

---

## Classification System

### Etymology-Based Classification

**Data Source**: Comprehensive etymology database built from:
- Behind the Name (surname etymology database)
- Forebears.io (global surname database)
- Dictionary of American Family Names (Hanks, 2003)
- Academic linguistics research
- Native language etymology resources

**Database Size**: ~900 surnames with documented meanings

### Five Semantic Categories

#### 1. Toponymic (Place-Meaning)

**Definition**: Surnames that mean "from [place]" in original language

**Identification Criteria**:
- Etymology explicitly references geographic location
- Contains place name or locative suffix
- Means "from [city]", "of [region]", "[place]-dweller"

**Examples**:
- **Italian**: Galilei (from Galilee), Romano (from Rome), Veneziano (from Venice), Fiorentino (from Florence), Napolitano (from Naples), Milanese (from Milan)
- **German**: Berliner (from Berlin), Wiener (from Vienna), Hamburger (from Hamburg), Frankfurter (from Frankfurt)
- **English**: London (from London), York (from York), Lancaster (from Lancaster)
- **French**: Paris (from Paris), Lyon (from Lyon), Marseille (from Marseille)
- **Spanish**: Toledo (from Toledo), Cordoba (from Córdoba), Sevilla (from Seville)
- **Polish**: Warszawski (from Warsaw), Krakowski (from Kraków)

**Linguistic Patterns**:
- Italian: -ano, -ese suffixes (Milanese, Genovese)
- German: -er suffix (Berliner, Wiener)
- Polish: -ski suffix + city name (Warszawski)

#### 2. Occupational (Job-Meaning)

**Definition**: Surnames meaning a profession, trade, or occupation

**Examples**:
- **Metalworking**: Smith, Ferrari (blacksmith), Schmidt, Fabbri, Lefevre, Herrero
- **Food**: Baker, Cook, Boucher (butcher), Boulanger (baker), Becker
- **Textiles**: Taylor, Weaver, Schneider (tailor), Sartori, Weber
- **Construction**: Carpenter, Mason, Zimmermann (carpenter), Charpentier
- **Agriculture**: Farmer, Miller, Mueller (miller), Molina, Molinari
- **Fishing**: Fisher, Fischer, Pesci
- **Others**: Shoemaker, Barber, Brewer, Hunter

#### 3. Descriptive (Trait-Meaning)

**Definition**: Surnames describing physical or character traits

**Subtypes**:
- **Color/Appearance**: Brown, White, Black, Rossi (red), Bianchi (white), Schwarz (black)
- **Stature**: Long (tall), Short, Klein (small), Gross (big), Petit (small), Grande (large)
- **Age**: Young, Old
- **Character**: Strong, Wise, Good, Savage

#### 4. Patronymic (Father's Name-Meaning)

**Definition**: Surnames meaning "son of [name]" or "descendant of [name]"

**Linguistic Patterns**:
- **English**: -son suffix (Johnson = son of John)
- **Spanish**: -ez, -az, -iz (Martinez = son of Martin)
- **Russian**: -ov, -ev, -in (Ivanov = son of Ivan)
- **Irish**: O', Mc, Mac (O'Brien = descendant of Brian)
- **Scandinavian**: -sen, -son (Hansen = son of Hans)

#### 5. Religious (Religious-Meaning)

**Definition**: Surnames with religious/spiritual meaning

**Examples**:
- **Occupations**: Bishop, Priest, Pope, Abbott, Monk
- **Concepts**: Christian, Church, Temple, Santo (saint), Chiesa (church)
- **Jewish**: Cohen (priest), Levy (Levite)

---

## Classification Confidence

**Database Matches**: 95% confidence
- Direct etymology documentation
- Multiple source confirmation
- Native language meaning verified

**Pattern-Based**: 60-75% confidence
- Linguistic pattern inference
- Less direct evidence
- May have exceptions

**Unknown**: 20% confidence
- Not in database
- No clear pattern
- Requires manual review

---

## Data Collection

### Surname Collection

**Source**: Embedded comprehensive database in collector

**Coverage**:
- Top US surnames by frequency
- Balanced across semantic categories
- Multiple origins per category
- Range of place importance scores (for toponymic)

### Immigration Records

**Temporal Coverage**: 1880-2020 (by decade)

**Attributes**:
- Year, decade, immigration wave
- Immigrant count per surname
- Origin country
- Entry port
- Demographic data (where available)

**Generation Method**: Synthetic data based on:
- Historical immigration patterns by origin
- Peak immigration periods (Italian 1890-1920, Vietnamese 1975-2000, etc.)
- Semantic category influences (toponymic more concentrated, occupational steadier)

### Settlement Patterns

**Temporal Snapshots**: 1900, 1920, 1950, 1980, 2000, 2020

**Geographic Granularity**: State-level (50 states)

**Metrics**:
- Population count per state
- Concentration index (% of total)
- HHI calculation
- Distance from entry port
- Ethnic enclave identification (concentration > 25% + toponymic)
- Dispersion score (100 - concentration_factor)

**Generation Logic**:
- Origin-specific state preferences (Italian→NY/NJ, Irish→MA/NY, etc.)
- Semantic category effects (toponymic starts concentrated, disperses slower)
- Temporal evolution (all categories disperse over time)

---

## Statistical Methods

### Descriptive Statistics

**By Semantic Category**:
- N, percentage of total
- Mean current bearers
- Example surnames

**By Origin Country**:
- N per category
- Mean immigration rates
- Settlement HHI

### Hypothesis Tests

#### T-Tests (H1, H2)

**Independent Samples T-Test**:
```
t = (M₁ - M₂) / SE_diff
df = n₁ + n₂ - 2
```

**Effect Size (Cohen's d)**:
```
d = (M₁ - M₂) / SD_pooled
where SD_pooled = √[((n₁-1)×SD₁² + (n₂-1)×SD₂²) / (n₁+n₂-2)]
```

**Interpretation**:
- d < 0.2: Negligible
- 0.2 ≤ d < 0.5: Small
- 0.5 ≤ d < 0.8: Medium
- d ≥ 0.8: Large

#### ANOVA (H5)

**One-Way ANOVA**:
```
F = MS_between / MS_within
```

**Effect Size (Eta-squared)**:
```
η² = SS_between / SS_total
```

**Post-Hoc**: Pairwise t-tests with Bonferroni correction
```
α_bonferroni = 0.05 / number_of_comparisons
For 5 groups: 10 pairwise comparisons → α = 0.01
```

#### Correlation (H4)

**Pearson Correlation**:
```
r = Σ[(x - x̄)(y - ȳ)] / √[Σ(x - x̄)² × Σ(y - ȳ)²]
```

**R-squared**: Variance explained

**Significance**: t-test on correlation coefficient

### Concentration Metrics

**HHI (Herfindahl-Hirschman Index)**:
```
HHI = Σ(share_i²) × 10,000
where share_i = population_state_i / population_total
```

**Dispersion Score**:
```
Dispersion = 100 × (1 - max_state_share)
```

---

## Quality Controls

### Sample Size Requirements
- Minimum n = 20 for each group in t-tests
- Minimum n = 30 per category for ANOVA
- Power analysis documented for each test

### Significance Levels
- Standard α = 0.05 (two-tailed)
- Bonferroni α = 0.01 for multiple comparisons
- Confidence intervals: 95%

### Data Quality
- All synthetic data flagged (`is_estimated = True`)
- Data quality scores (0-100)
- Source documentation for all records

### Effect Size Reporting
- Cohen's d for all t-tests
- Eta-squared for ANOVA
- R-squared for correlations
- Practical significance interpretation

---

## Limitations

### Classification Limitations
1. **Etymology Ambiguity**: Some surnames have multiple possible meanings
2. **Language Evolution**: Meanings may have shifted over time
3. **Pattern Matching**: Fallback method less reliable than database
4. **Coverage**: ~900 surnames is comprehensive but not exhaustive

### Data Limitations
1. **Synthetic Data**: Using modeled data for development (real data integration planned)
2. **Name Changes**: Anglicization not fully tracked (Rossi→Ross)
3. **Spelling Variations**: May split single surname into multiple entries
4. **Early Census**: Undercounts in pre-1920 censuses

### Causal Limitations
1. **Correlational Design**: Cannot prove causation
2. **Omitted Variables**: Economic factors, wars, policy changes
3. **Selection Effects**: Who immigrates vs who doesn't
4. **Reverse Causality**: Settlement patterns may affect surname retention

---

## Ethical Considerations

### Respectful Treatment
- Surname ≠ current identity
- No value judgments on categories
- Cultural sensitivity to all groups
- Privacy: aggregate data only

### Transparency
- Open methodology
- Limitations acknowledged
- Data sources documented
- Code available for review

---

## References

### Academic Literature

**Nominative Determinism**:
- Pelham et al. (2002). "Why Susie Sells Seashells by the Seashore"
- Joubert (1994). "Nama sunt omina"

**Immigration Studies**:
- Portes & Rumbaut (2014). "Immigrant America"
- Alba & Nee (2003). "Remaking the American Mainstream"
- Zhou (1992). "Chinatown: The Socioeconomic Potential of an Urban Enclave"

**Surname Linguistics**:
- Hanks (2003). "Dictionary of American Family Names"
- Hanks & Hodges (1988). "A Dictionary of Surnames"
- Reaney & Wilson (1997). "A Dictionary of English Surnames"

**Etymology**:
- Behind the Name. behindthename.com
- Forebears. forebears.io
- Various linguistic and etymological resources

### Data Sources

- US Census Bureau: census.gov
- Social Security Administration: ssa.gov
- Ellis Island Foundation: libertyellisfoundation.org
- Immigration & Naturalization Service historical data

---

## Reproducibility

### Code Availability
- All code in project repository
- Version controlled (Git)
- Comprehensive docstrings
- Type hints where applicable

### Data Availability
- Etymology database embedded in code
- Synthetic data generation scripts
- Real data integration planned

### Environment
- Python 3.8+
- Dependencies in requirements.txt
- No additional packages required

---

**Document Version**: 2.0 (Semantic Meaning Focus)  
**Last Updated**: November 7, 2025  
**Authors**: Michael Smerconish & Research Team
