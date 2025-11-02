# Cryptocurrency Nominative Determinism Analysis Platform

Analyzes correlation between cryptocurrency names and market performance.

## Install

```bash
pip install -r requirements.txt
```

## Run

```bash
python3 app.py
```

**On first run**: Database will auto-populate with 500 cryptocurrencies (takes 10-15 minutes).

**After auto-population completes**: Server starts on a random odd port.

Navigate to the URL shown in terminal.

## Pages

- **Database** - Sortable table of all 500+ cryptocurrencies with scores and performance
- **Evidence & Analysis** - Statistical correlations and backtests proving nominative determinism
- **Portfolio** - Build optimized portfolios based on name analysis
- **Data Management** - Update data, train models, export

## Features

- Confidence scoring (0-100) for every cryptocurrency
- Statistical correlation analysis
- Historical backtesting of name-based strategies
- Portfolio optimization
- Risk analysis (VaR, Monte Carlo simulation)

## Data

Automatically collects from CoinGecko API:
- Top 500 cryptocurrencies by market cap
- Historical price data (30d, 90d, 1yr)
- Complete name analysis (syllables, memorability, uniqueness, phonetics)

## Export

Export complete database to CSV from any page for external analysis.
