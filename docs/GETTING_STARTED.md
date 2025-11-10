# Getting Started Guide

Complete setup instructions for the Nominative Determinism Research Platform.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- 2GB free disk space (for data and databases)

## Installation

### 1. Clone or Download the Project

```bash
cd /path/to/your/projects
# If you have the project already, navigate to it
cd FlaskProject
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Note**: This will install ~50 packages. The installation may take 5-10 minutes.

### 3. Verify Installation

```bash
python3 -c "import flask; import pandas; import numpy; print('✓ Core dependencies installed')"
```

## Running the Application

### Basic Startup

```bash
python3 app.py
```

The application will:
1. Initialize the database
2. Start the Flask development server
3. Be available at `http://localhost:5000`

### First Run

On first startup, the app will auto-populate cryptocurrency data (if empty):
- This takes 10-15 minutes
- Collects 500 cryptocurrencies from CoinGecko API
- Progress is logged to console

**You can skip this by pressing Ctrl+C and running:**
```bash
# Run without auto-population
SKIP_AUTO_POPULATE=1 python3 app.py
```

## Exploring the Platform

### Main Pages

Once running, visit these URLs:

1. **Home**: `http://localhost:5000/`
   - Executive overview
   - Navigation to all features

2. **Analysis Dashboard**: `http://localhost:5000/analysis`
   - Statistical findings summary

3. **Live Betting**: `http://localhost:5000/live-betting`
   - Sports betting intelligence system

4. **Domain-Specific Pages**:
   - Crypto: `http://localhost:5000/crypto/findings`
   - Hurricanes: `http://localhost:5000/hurricanes`
   - NBA: `http://localhost:5000/nba`
   - NFL: `http://localhost:5000/nfl`
   - Many more available via navigation

### API Endpoints

The platform provides extensive APIs:

```bash
# Get betting opportunities
curl http://localhost:5000/api/betting/opportunities

# Get sport analysis
curl http://localhost:5000/api/sports-meta/characteristics
```

See `AUDIT_REPORT.json` for complete list of 256 API endpoints.

## Database Setup

### Databases Used

1. **SQLite** (`instance/namesake.db`): Main application database
   - Cryptocurrencies, sports players, etc.
   - Auto-created on first run

2. **DuckDB** (`name_study.duckdb`): Name diversity analysis
   - Created by analysis scripts
   - Contains U.S. name statistics

### Populating Data

#### Cryptocurrency Data (Automatic)

```bash
# Collects top 500 cryptocurrencies
python3 app.py
# Wait for auto-population to complete
```

#### Sports Data (Manual)

```bash
# NFL players
python3 -m collectors.nfl_collector

# NBA players
python3 -m collectors.nba_collector

# MLB players
python3 -m collectors.mlb_collector
```

Each collector takes 5-15 minutes and collects 1000-2000 players.

#### Other Domains

See `collectors/` directory for domain-specific collectors:
- `hurricane_collector.py` - Hurricane data
- `mtg_collector.py` - Magic cards
- `board_game_collector.py` - Board games
- And many more

## Configuration

### Environment Variables

```bash
# Optional: API keys for external data
export ODDS_API_KEY="your_key_here"          # For betting odds
export COINGECKO_API_KEY="your_key_here"     # For premium crypto data
```

### Flask Configuration

Edit `core/config.py` to customize:
- Database location
- Debug mode
- API rate limits
- Cache settings

## Troubleshooting

### Database Errors

```bash
# Reset database
rm instance/namesake.db
python3 app.py  # Will recreate
```

### Port Already in Use

```bash
# Run on different port
python3 app.py --port 5001
```

Or edit `app.py`:
```python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
```

### Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Memory Issues

The application can use significant RAM with large datasets:
- Minimum: 2GB RAM
- Recommended: 8GB RAM for full datasets

### Missing Data

If pages show "no data":
1. Run the appropriate collector script (see above)
2. Check `data/` directory for raw files
3. Check database with SQLite browser

## Development Mode

### Enable Debug Mode

In `app.py`:
```python
if __name__ == '__main__':
    app.run(debug=True)  # Auto-reload on code changes
```

### Running Tests

```bash
# Once test suite is implemented
python3 -m pytest tests/
```

## Next Steps

1. **Explore Documentation**: Browse `docs_organized/` for detailed research
2. **Run Analysis**: Execute domain-specific analysis scripts
3. **Check Audit Report**: Review `AUDIT_REPORT.json` for project status
4. **Read Research**: See individual domain findings in web interface

## Project Roadmap

Current refactoring priorities:
1. ✅ Documentation organization (complete)
2. 🔄 Split app.py into blueprints (in progress)
3. 🔄 Consolidate analyzer modules
4. 🔄 Improve test coverage
5. 🔄 Enhance UI/UX

See [README.md](README.md) for current status.

## Getting Help

- **Technical Issues**: Check `AUDIT_REPORT.json` for system status
- **Research Questions**: See `docs_organized/` documentation
- **API Documentation**: Listed in audit report (256 endpoints)

## Performance Notes

- First load may be slow (database initialization)
- Some pages query large datasets (may take 2-3 seconds)
- API endpoints are generally fast (<100ms)
- Consider caching for production deployment

---

**Last Updated**: November 2025  
For detailed research methodology, see `docs_organized/04_THEORY/`

