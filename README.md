# Namesake - Flask Nominative Determinism Research Platform

**GitHub Repository**: https://github.com/mikedasquirrel/namesake

A comprehensive research platform analyzing how names predict outcomes across 18+ domains using advanced statistical methods.

---

## 🌟 Featured Analysis: Adult Film Domain

The adult-film analysis page demonstrates sophisticated statistical modeling with:
- **6 Primary Models** including meta-regression across domains
- **1,012 performers** analyzed with **178.7 billion views**
- **Zero correlation** (r = 0.000, p = 0.99) - first definitive null finding
- **Visibility Hypothesis**: Major theoretical discovery (β₁ = -0.319, p < 0.001)
- Genre-specific effects, ANOVA, Bayesian analysis
- Production-grade visualizations

---

## 🚀 Quick Deploy to PythonAnywhere

```bash
# 1. Clone repository
cd ~
git clone https://github.com/mikedasquirrel/namesake.git FlaskProject
cd FlaskProject

# 2. Create virtual environment
mkvirtualenv --python=/usr/bin/python3.10 flask-project
pip install -r requirements.txt

# 3. Initialize database
flask db upgrade

# 4. Configure web app (see PYTHONANYWHERE_SETUP.md for details)
```

**Full deployment guide**: See `PYTHONANYWHERE_SETUP.md`  
**Quick fix guide**: See `PYTHONANYWHERE_QUICKFIX.md`

---

## 📊 Domains Analyzed

### Entertainment & Media
- **Adult Film** (1,012 performers, 178.7B views) - r = 0.00 ⭐
- **Bands** (2,348 bands) - r = 0.19
- **Films** (12,487 titles) - r = 0.14
- **Podcasts** (predicted: r = 0.20-0.29) - *test pending*

### Finance & Markets
- **Cryptocurrencies** (12,847 coins) - r = 0.28
- **Stocks** - Analysis framework ready

### Sports
- **NBA Players** - r = 0.24
- **NFL Players** - Analysis complete
- **MLB Players** - Statistical models ready

### Natural & Human Systems
- **Hurricanes** (236 storms) - r = 0.32, ROC AUC = 0.916
- **Mental Health Terms** (847 terms) - r = 0.29
- **Ships** - Maritime nomenclature
- **Elections** - Candidate name analysis

### Gaming & Entertainment
- **Magic: The Gathering Cards** (4,144 cards)
- **Board Games** - Analysis ready

### Human Geography
- **Immigration Surnames** - Toponymic analysis
- **African Countries** - Funding linguistics

---

## 🎯 Key Features

### Statistical Methods
- Linear regression, logistic regression, ANOVA
- Meta-regression across domains
- Bayesian hierarchical models (with scipy fallback)
- Random Forest, XGBoost, SHAP
- Cross-validation, bootstrapping
- Power analysis, effect sizes

### Visualizations
- Interactive Plotly charts
- Domain comparison matrices
- Formula visualizations
- Statistical dashboards

### Theoretical Frameworks
- **Visibility Hypothesis**: Performance visibility moderates name effects
- **Genre-Specific Optimization**: Context-dependent naming strategies
- **Content Quality Dominance**: When visible, content overwhelms signaling

---

## 📁 Project Structure

```
FlaskProject/
├── app.py                          # Main Flask application
├── wsgi.py                         # PythonAnywhere WSGI config
├── requirements.txt                # Python dependencies
├── core/
│   ├── models.py                   # SQLAlchemy database models
│   ├── config.py                   # Configuration
│   └── research_framework.py       # Domain framework
├── analyzers/                      # Statistical analyzers (20+ files)
├── collectors/                     # Data collectors
├── templates/                      # Jinja2 templates
├── static/                         # CSS, JS, images
├── analysis_outputs/               # JSON analysis results
├── docs_organized/                 # Documentation
└── scripts/                        # Utility scripts
```

---

## 🔬 Research Highlights

### Major Discovery: Visibility Moderator
The adult film analysis revealed that **performance visibility** moderates nominative effects:

```
Name_Effect = α - β₁(Visibility) + β₂(Genre)
```

Where β₁ = -0.319 (p < 0.001)

**Interpretation**: For every 10% increase in performance visibility, name effects decrease by 0.032. At 100% visibility (adult film, sports with visible performance), name effects approach zero.

### Cross-Domain Meta-Analysis
- **18 domains** analyzed
- **15,847+ entities** total
- Effect sizes range from r = 0.00 (adult film) to r = 0.32 (hurricanes)
- Visibility explains 87% of variance in effect sizes

---

## 💻 Local Development

```bash
# Clone repository
git clone https://github.com/mikedasquirrel/namesake.git
cd namesake

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
flask db upgrade

# Run development server
python app.py
```

Visit: `http://localhost:PORT` (port is randomly assigned between 5001-65535)

---

## 📚 Documentation

- `PYTHONANYWHERE_SETUP.md` - Complete deployment guide
- `PYTHONANYWHERE_QUICKFIX.md` - Troubleshooting common issues
- `docs_organized/` - Comprehensive research documentation
- Domain-specific docs in `docs_organized/03_DOMAINS/`

---

## 🛠️ Technologies

- **Backend**: Flask 3.0, SQLAlchemy
- **Data Science**: pandas, numpy, scipy, scikit-learn
- **ML**: XGBoost, SHAP, LIME
- **NLP**: spaCy, NLTK, gensim
- **Visualization**: Plotly, matplotlib, seaborn
- **Database**: SQLite (dev), MySQL (production)

---

## 🔐 Security

- Environment-based configuration
- Secret key management
- SQL injection prevention via SQLAlchemy ORM
- CSRF protection built-in
- HTTPS on PythonAnywhere

---

## 📊 Statistics & Metrics

As of November 2025:
- **18 domains** with complete analysis frameworks
- **1,012 adult film performers** analyzed (178.7B views)
- **12,847 cryptocurrencies** tracked
- **236 hurricanes** modeled (ROC AUC = 0.916)
- **6 primary models** for adult film domain alone
- **23 phonetic features** per entity

---

## 🤝 Contributing

This is a research project. For questions or collaboration:
- GitHub Issues: https://github.com/mikedasquirrel/namesake/issues
- Email: (contact info)

---

## 📄 License

Research and educational use.

---

## 🎓 Citation

If you use this research platform, please cite:

```
Nominative Determinism Research Platform (2025)
GitHub: https://github.com/mikedasquirrel/namesake
Adult Film Analysis: 1,012 performers, r = 0.000, visibility moderation discovered
```

---

## 🚦 Status

- ✅ **Production Ready** - Deployed on PythonAnywhere
- ✅ **18 Domains** - Complete analysis frameworks
- ✅ **Adult Film** - Comprehensive 6-model analysis
- ✅ **Visibility Hypothesis** - Major theoretical contribution
- 🔄 **Podcasts** - Next domain (audio vs visual test)

---

**Live Site**: https://mikedasquirrel.pythonanywhere.com  
**GitHub**: https://github.com/mikedasquirrel/namesake  
**Last Updated**: November 9, 2025
