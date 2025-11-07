# Nominative Determinism Research Platform

**Quantifying the relationship between names and outcomes across multiple domains.**

---

## Overview

This platform analyzes naming patterns and their correlations with real-world phenomena:

- **Hurricane nomenclature** → casualty/damage prediction (phonetic harshness, memorability)
- **Magic: The Gathering cards** → competitive performance (name length, phonosemantic features)
- **Cryptocurrency markets** → price trajectories (naming aesthetics, brand perception)
- **Global name diversity** → economic structures (middle names, dominant names, cultural patterns)

All analyses use reproducible statistical methods: Shannon entropy, Simpson diversity, phonetic feature extraction, and sentiment scoring.

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the platform
python3 app.py

# Access at random odd port (displayed on startup)
# Default: http://localhost:<random_port>
```

---

## Core Features

### 1. Hurricane Name Analysis
- **Data**: 236 Atlantic storms (1950-2024) from NOAA HURDAT2
- **Metrics**: Phonetic harshness, memorability, gender coding, sentiment
- **Finding**: ROC AUC 0.916 for casualty prediction using name features alone
- **Endpoint**: `/hurricanes`

### 2. MTG Card Analysis  
- **Data**: ~25,000 Magic cards across formats
- **Metrics**: Name length, syllables, phonosemantic properties
- **Finding**: Shorter, harsher names correlate with competitive play
- **Endpoint**: `/mtg`

### 3. Crypto Market Intelligence
- **Data**: 500+ cryptocurrencies with price history
- **Metrics**: Name aesthetics, brand perception, market performance
- **API**: `/api/crypto/*` for live analysis

### 4. Name Diversity Study
- **Data**: 2.1M U.S. names (1880-2024) + 10 countries
- **Metrics**: Shannon entropy, Gini, HHI, middle-name prevalence
- **Database**: `name_study.duckdb` (DuckDB analytics)
- **Finding**: U.S. shows exceptional diversity (HHI=20); middle names amplify 30-50%

---

## Project Structure

```
├── app.py                   # Flask application (2578 lines)
├── analysis/                # Research modules
│   ├── data_acquisition.py
│   ├── processing.py
│   ├── metrics.py
│   ├── country_name_linguistics.py
│   └── america_variant_analysis.py
├── collectors/              # Data ingestion
├── analyzers/               # Feature extraction
├── data/
│   ├── raw/                 # Source data
│   └── processed/           # Cleaned datasets
├── figures/                 # Publication-ready visualizations
├── templates/               # Web UI (8 pages)
└── name_study.duckdb        # Unified analytics database
```

---

## Key Endpoints

### Pages
- `/` — Executive dashboard
- `/analysis` — Statistical findings
- `/hurricanes` — Hurricane nomenclature research
- `/mtg` — Magic card analysis
- `/crypto/findings` — Cryptocurrency research

### APIs (selected)
- `/api/hurricanes/stats` — Hurricane dataset statistics
- `/api/mtg/comprehensive-report` — Full MTG analysis
- `/api/crypto/advanced-stats` — Crypto market metrics
- `/api/analytics/*` — Predictive modeling endpoints

---

## Data Sources

- **NOAA HURDAT2**: Atlantic hurricane archive (1950-2024)
- **Scryfall API**: Magic: The Gathering card database
- **CoinGecko**: Cryptocurrency market data
- **U.S. SSA**: Baby names dataset (1880-2024)
- **Google Books Ngrams**: Historical usage patterns
- **Multiple national statistics agencies**: International name data

---

## Research Outputs

All analysis produces:
1. **Parquet datasets** in `data/processed/`
2. **Publication figures** (300 DPI PNG) in `figures/`
3. **DuckDB tables** queryable via SQL
4. **JSON APIs** for programmatic access

---

## Citation

If using this work:

```
Smerconish, M. (2025). Nominative Determinism Research Platform.
Hurricane analysis: ROC AUC 0.916 for name-based casualty prediction.
Name diversity: U.S. marketplace-of-names hypothesis tested across 11 countries.
```

---

## Technical Details

- **Backend**: Flask (Python 3.9+)
- **Database**: DuckDB (analytics), SQLite (operational)
- **Analysis**: pandas, numpy, scipy, nltk
- **Visualization**: matplotlib, seaborn
- **Deployment**: Random odd port to avoid conflicts

---

## Contact

Independent research by Michael Smerconish  
Philadelphia, PA

**License**: Research and educational use  
**Code**: Fully reproducible; see `analysis/` modules
# namesake
