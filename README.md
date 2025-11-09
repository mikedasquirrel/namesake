# Nominative Determinism Research Platform

A comprehensive research platform studying the relationship between names and outcomes across multiple domains.

## Overview

This project investigates nominative determinism—the hypothesis that names influence life outcomes—across 18+ domains including sports, natural disasters, cryptocurrencies, and more. The platform combines data collection, statistical analysis, and interactive visualization to explore these patterns.

## Key Features

- **Multi-Domain Analysis**: Research across sports, hurricanes, cryptocurrencies, MTG cards, and more
- **Statistical Framework**: Rigorous analysis with proper controls and validation
- **Interactive Dashboards**: Explore findings through web-based visualizations
- **Sports Betting Intelligence**: Apply linguistic analysis to sports predictions
- **Reproducible Research**: Complete methodology documentation

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the Flask application
python3 app.py

# Visit in browser
http://localhost:5000
```

See [GETTING_STARTED.md](GETTING_STARTED.md) for detailed setup instructions.

## Project Structure

```
FlaskProject/
├── app.py                 # Main Flask application (being refactored into blueprints)
├── analyzers/             # Statistical analysis modules (148 modules)
├── collectors/            # Data collection modules
├── core/                  # Core models and configuration
├── data/                  # Raw and processed datasets
├── templates/             # HTML templates (76 templates)
├── static/                # CSS, JS, and assets
├── docs_organized/        # Organized documentation (241 files)
├── docs_archive/          # Archived documentation (76 files)
└── requirements.txt       # Python dependencies
```

## Documentation

- **Setup**: [GETTING_STARTED.md](GETTING_STARTED.md) - Installation and configuration
- **Organized Docs**: [docs_organized/](docs_organized/) - Comprehensive documentation by category
- **Audit Report**: [AUDIT_REPORT.json](AUDIT_REPORT.json) - Current project status

### Documentation Organization

- `docs_organized/01_START_HERE/` - Entry points and quick starts
- `docs_organized/02_DISCOVERIES/` - Research findings
- `docs_organized/03_DOMAINS/` - Domain-specific analyses
- `docs_organized/04_THEORY/` - Theoretical frameworks
- `docs_organized/07_IMPLEMENTATION/` - Technical documentation

## Current Status

**⚠️ Note**: This project is undergoing major refactoring to improve maintainability:

- ✅ Audit complete (332 routes, 148 analyzers, 76 templates)
- ✅ Documentation archived and organized
- 🔄 Splitting monolithic app.py into blueprints
- 🔄 Consolidating analyzer modules
- 🔄 Improving test coverage

See [AUDIT_REPORT.json](AUDIT_REPORT.json) for detailed analysis.

## Key Domains

### Sports
- NFL, NBA, MLB player name analysis
- Sports betting intelligence system
- Cross-sport meta-analysis

### Natural Events
- Hurricane naming and casualty prediction
- Earthquake nomenclature studies

### Markets
- Cryptocurrency name analysis
- Magic: The Gathering card names
- Board game title analysis

### Human Systems
- Election candidate names
- Immigration patterns
- Band and artist names
- Academic researcher names

## Research Methodology

The platform employs:
- Linguistic feature extraction (syllables, phonemes, harshness, memorability)
- Statistical modeling with appropriate controls
- Cross-validation and replication studies
- Meta-analysis across domains

## Technology Stack

- **Backend**: Flask, SQLAlchemy, SQLite/DuckDB
- **Analysis**: NumPy, Pandas, SciPy, scikit-learn
- **NLP**: NLTK, spaCy
- **Visualization**: Plotly, Matplotlib
- **Frontend**: HTML/CSS/JS with custom styling

## Contributing

This is an active research project. Key areas for contribution:
1. Blueprint refactoring (splitting app.py)
2. Analyzer consolidation (reducing duplication)
3. Test coverage improvement
4. Data quality validation
5. UI/UX enhancements

## License

Research purposes. See individual data sources for licensing.

## Contact

For questions about the research or methodology, see the organized documentation in `docs_organized/`.

---

**Last Updated**: November 2025  
**Status**: Active Development - Refactoring Phase
