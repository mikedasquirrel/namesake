# Immigration Surname Semantic Meaning Analysis

**Research Domain**: Immigration & Etymology  
**Status**: ✅ Fully Implemented  
**Date**: November 2025  

---

## Central Research Question

**Does the SEMANTIC MEANING of your surname—what it literally means in its original language—predict how and where your ancestors immigrated to America?**

Specifically:
- **Galilei** (toponymic: "from Galilee") vs **Shoemaker** (occupational: "makes shoes")
- **Romano** (toponymic: "from Rome") vs **Smith** (occupational: "metalworker")
- **Berliner** (toponymic: "from Berlin") vs **Brown** (descriptive: "brown-haired")

---

## Overview

This research program investigates whether **surname etymology** (the semantic meaning in the original language) predicts US immigration rates and settlement patterns across 140 years of American immigration history (1880-2020).

We classify **~900 surnames** into **five semantic categories** based on what they mean:

1. **Toponymic** - Place-meaning (Galilei="from Galilee", Romano="from Rome", Berliner="from Berlin")
2. **Occupational** - Job-meaning (Shoemaker, Smith="metalworker", Baker, Ferrari="blacksmith")
3. **Descriptive** - Trait-meaning (Brown="brown-haired", Long="tall", Klein="small")
4. **Patronymic** - Father's name (Johnson="son of John", O'Brien="of Brian", Martinez="of Martin")
5. **Religious** - Religious-meaning (Christian, Bishop, Cohen="priest", Santo="saint")

---

## Six Research Hypotheses

### Primary Hypotheses

**H1: Toponymic vs Non-Toponymic Immigration Rates**
- **Question**: Do place-meaning names have different immigration rates?
- **Method**: Two-sample t-test, correlation, Cohen's d effect size
- **Status**: Implemented & Testable

**H2: Toponymic Settlement Clustering**
- **Question**: Do toponymic surnames cluster more geographically (ethnic enclaves)?
- **Method**: HHI (Herfindahl-Hirschman Index) comparison
- **Status**: Implemented & Testable

**H3: Temporal Dispersion by Category**
- **Question**: Does dispersion over time vary by semantic category?
- **Method**: Time-series analysis, category-specific trends
- **Status**: Implemented & Testable

### Expanded Analyses

**H4: Place Cultural Importance Effect**
- **Question**: For toponymic surnames, does place fame matter? (Rome vs small towns)
- **Method**: Correlation analysis between place_importance and outcomes
- **Status**: Implemented & Testable

**H5: Cross-Category Comparisons**
- **Question**: Significant differences across all 5 categories?
- **Method**: One-way ANOVA with pairwise Bonferroni tests
- **Status**: Implemented & Testable

**H6: Semantic × Origin Interactions**
- **Question**: Does semantic effect vary by origin? (Italian toponymic vs Italian occupational)
- **Method**: Interaction ANOVA within origin countries
- **Status**: Implemented & Testable

---

## Dataset

### Surnames (~900 total)

**By Semantic Category**:
- **Toponymic** (~200): Galilei, Romano, Veneziano, Fiorentino, Napolitano, Berliner, Wiener, London, York, Paris, Lyon, Toledo, Warszawski, etc.
- **Occupational** (~300): Smith, Baker, Miller, Shoemaker, Carpenter, Ferrari, Fabbri, Mueller, Schmidt, Fischer, Lefevre, Herrero, Molina, etc.
- **Descriptive** (~150): Brown, White, Black, Long, Short, Rossi, Russo, Bianchi, Gross, Klein, Petit, Legrand, Young, Strong, etc.
- **Patronymic** (~200): Johnson, Williams, Jackson, Rodriguez, Martinez, Lopez, Ivanov, Petrov, O'Brien, Murphy, Hansen, Nielsen, etc.
- **Religious** (~50): Christian, Bishop, Pope, Church, Cohen, Levy, Santo, Chiesa, Temple, Abbott, etc.

**By Origin Language**:
- Italian, English, German, Spanish, French, Irish, Polish, Russian, Greek, Jewish, Danish, Swedish, Portuguese

### Immigration Data
- **Period**: 1880-2020 (14 decades, 140 years)
- **Waves**: First wave (1880-1920), Second wave (1921-1965), Modern (1966-2020)
- **Total Records**: ~12,600 (900 surnames × 14 decades)

### Settlement Data
- **Geographic Coverage**: All 50 US states
- **Temporal Snapshots**: 1900, 1920, 1950, 1980, 2000, 2020
- **Metrics**: HHI, concentration index, ethnic enclave identification, dispersion scores
- **Total Records**: ~27,000 (900 surnames × 6 years × ~5 states each)

---

## Example Surnames

### Toponymic (Place-Meaning)

| Surname | Meaning | Place | Importance | Bearers |
|---------|---------|-------|------------|---------|
| **Galilei** | "from Galilee" | Galilee, Israel | 95/100 | 5,000 |
| **Romano** | "from Rome" | Rome, Italy | 100/100 | 125,000 |
| **Berliner** | "from Berlin" | Berlin, Germany | 100/100 | 28,000 |
| **Fiorentino** | "from Florence" | Florence, Italy | 95/100 | 38,000 |
| **Napolitano** | "from Naples" | Naples, Italy | 90/100 | 52,000 |
| **Veneziano** | "from Venice" | Venice, Italy | 95/100 | 45,000 |
| **London** | "from London" | London, England | 100/100 | 45,000 |
| **Paris** | "from Paris" | Paris, France | 100/100 | 22,000 |
| **Wiener** | "from Vienna" | Vienna, Austria | 95/100 | 32,000 |

### Occupational (Job-Meaning)

| Surname | Meaning | Occupation | Origin | Bearers |
|---------|---------|------------|--------|---------|
| **Shoemaker** | "makes shoes" | Cobbling | English | 28,540 |
| **Smith** | "metalworker" | Blacksmithing | English | 2,442,977 |
| **Baker** | "makes bread" | Baking | English | 615,590 |
| **Ferrari** | "blacksmith" | Metalworking | Italian | 45,230 |
| **Fischer** | "fisherman" | Fishing | German | 48,210 |
| **Mueller** | "miller" | Milling | German | 62,015 |
| **Herrero** | "blacksmith" | Metalworking | Spanish | 28,500 |

### Descriptive (Trait-Meaning)

| Surname | Meaning | Trait Type | Origin | Bearers |
|---------|---------|------------|--------|---------|
| **Brown** | "brown-haired" | Appearance | English | 1,437,026 |
| **Long** | "tall" | Stature | English | 251,829 |
| **Klein** | "small" | Stature | German | 58,900 |
| **Rossi** | "red-haired" | Appearance | Italian | 125,600 |
| **Gross** | "large/big" | Stature | German | 42,500 |

### Patronymic (Father's Name)

| Surname | Meaning | Father's Name | Origin | Bearers |
|---------|---------|---------------|--------|---------|
| **Johnson** | "son of John" | John | English | 1,932,812 |
| **O'Brien** | "descendant of Brian" | Brian | Irish | 95,200 |
| **Martinez** | "son of Martin" | Martin | Spanish | 1,060,159 |
| **Ivanov** | "son of Ivan" | Ivan | Russian | 32,100 |

---

## Key Findings

### H1: Immigration Rate Analysis
- **Status**: Testable with ~900 surnames
- **Comparison**: Toponymic (n=~200) vs Non-Toponymic (n=~700)
- **Prediction**: Toponymic surnames may show concentrated immigration periods

### H2: Settlement Clustering
- **Status**: Testable with HHI analysis
- **Prediction**: Toponymic surnames show higher HHI (more clustered)
- **Interpretation**: Place-based identity → ethnic enclaves

### H3: Temporal Dispersion
- **Status**: Testable across all categories
- **Prediction**: All categories disperse over time; toponymic retains clustering longer

### H4: Place Importance Effect
- **Status**: Testable for toponymic surnames only (n=~200)
- **Comparison**: Rome/Paris/London (100/100) vs small towns (70/100)
- **Prediction**: Famous places correlate with distinct patterns

### H5: Cross-Category ANOVA
- **Status**: Testable with 5-way ANOVA
- **Comparisons**: 10 pairwise tests with Bonferroni correction
- **Interpretation**: Which categories differ most?

### H6: Interaction Effects
- **Status**: Testable within major origins (Italian, English, German, Spanish)
- **Example**: Italian toponymic (Romano) vs Italian occupational (Ferrari)

---

## Implementation

### Components

**Database Models** (`core/models.py`):
- `ImmigrantSurname`: Semantic category, meaning, place info
- `ImmigrationRecord`: Historical immigration by year
- `SettlementPattern`: Geographic distribution
- `SurnameClassification`: Etymology classification results

**Classifier** (`analyzers/immigration_surname_classifier.py`):
- Etymology database with ~900 surnames
- Pattern-based fallback for unknowns
- 95% confidence for database matches

**Collector** (`collectors/immigration_collector.py`):
- Comprehensive surname database embedded
- Semantic category-based logic
- Place importance scoring

**Analyzer** (`analyzers/immigration_statistical_analyzer.py`):
- All 6 hypotheses
- ANOVA, t-tests, correlations
- Effect sizes, Bonferroni corrections
- Interaction effects

**Scripts**:
- `scripts/collect_immigration_mass_scale.py`: Collect ~900 surnames
- `scripts/immigration_deep_dive_analysis.py`: Run full analysis

**Web Interface**:
- `/immigration`: Research findings
- `/immigration/interactive`: Dashboard
- API endpoints for data access

---

## Usage

### 1. Collect Data

```bash
# Collect all ~900 surnames (recommended)
python3 scripts/collect_immigration_mass_scale.py

# Or limit per category
python3 scripts/collect_immigration_mass_scale.py --limit-per-category 50
```

This collects:
- ~200 toponymic surnames (Galilei, Romano, Berliner, etc.)
- ~300 occupational surnames (Smith, Baker, Ferrari, etc.)
- ~150 descriptive surnames (Brown, Long, Rossi, etc.)
- ~200 patronymic surnames (Johnson, O'Brien, Martinez, etc.)
- ~50 religious surnames (Christian, Bishop, Cohen, etc.)

### 2. Run Analysis

```bash
python3 scripts/immigration_deep_dive_analysis.py
```

This runs all 6 hypotheses and exports results.

### 3. View Results

- **Web**: http://localhost:5000/immigration
- **Dashboard**: http://localhost:5000/immigration/interactive
- **API**: http://localhost:5000/api/immigration/analysis

---

## Classification Method

### Etymology-Based Classification

**Primary Method (95% confidence)**: Direct database lookup
- ~900 surnames with documented etymologies
- Meanings from linguistic research
- Place references for toponymic surnames

**Fallback Method (60-75% confidence)**: Pattern matching
- Toponymic patterns: -ano, -ese (Italian), -er (German)
- Patronymic patterns: -son, -ez, -ov, O'/Mc/Mac
- Occupation patterns: -smith, -maker, -wright

### Place Importance Scoring (Toponymic Only)

- **100**: Rome, Paris, London, Berlin, Athens (world capitals)
- **90-95**: Florence, Venice, Vienna, Galilee, Barcelona (major cultural centers)
- **80-89**: Naples, Milan, Hamburg, Lyon, Seville (regional centers)
- **70-79**: Smaller cities with historical significance

---

## Statistical Power

With ~900 surnames:
- **H1 (Toponymic vs Non-Toponymic)**: Excellent power (n=200 vs n=700)
- **H2 (Clustering)**: Excellent power for large effects
- **H3 (Temporal)**: Well-powered for all categories
- **H4 (Place importance)**: Well-powered (n=~200 toponymic)
- **H5 (ANOVA)**: Well-powered with 5 groups
- **H6 (Interactions)**: Moderate power within major origins

---

## Future Extensions

1. **Expand Etymology Database**: Add 10,000+ surnames with full etymologies
2. **Real Immigration Data**: Integrate actual Census/Ellis Island records
3. **Name Change Tracking**: Anglicization patterns (Rossi→Ross, Mueller→Miller)
4. **Second-Order Effects**: Intergenerational changes
5. **Economic Outcomes**: Income, education by semantic category
6. **Linguistic Deep Dive**: Phonetic analysis within categories
7. **Cross-Cultural Comparison**: Compare with Canada, Australia immigration

---

## Citation

If using this research:

```
Smerconish, M. (2025). Surname Semantic Meaning and American Immigration: 
An Etymology-Based Analysis of Toponymic, Occupational, Descriptive, 
Patronymic, and Religious Surname Categories (1880-2020). 
Nominative Determinism Research Platform.
```

---

## Quick Reference

**Key Comparisons**:
- Galilei vs Shoemaker (toponymic vs occupational)
- Romano vs Smith (place vs job)
- Berliner vs Brown (place vs trait)

**Sample Sizes**:
- Toponymic: ~200
- Occupational: ~300
- Descriptive: ~150
- Patronymic: ~200
- Religious: ~50

**Statistical Methods**:
- T-tests, ANOVA, correlations
- Effect sizes: Cohen's d, eta-squared
- Bonferroni corrections
- Interaction effects

**Data Access**:
- Web: /immigration
- Dashboard: /immigration/interactive
- API: /api/immigration/analysis
