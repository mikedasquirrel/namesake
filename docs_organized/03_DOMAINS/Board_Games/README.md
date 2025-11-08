# Board Game Nomenclature Analysis

**Domain:** Board Games  
**Status:** Framework complete, data collection pending  
**Target Sample:** 2,000 games across 75 years (1950-2024)  
**Innovation:** First comprehensive linguistic analysis of board game naming patterns

---

## Research Questions

1. **Commercial Success:** Do name characteristics predict BoardGameGeek ratings?
2. **Naming Clusters:** Are there distinct archetypes by game category?
3. **Temporal Evolution:** How have conventions evolved 1950s-2024?
4. **Cultural Traditions:** Do US, European, and Japanese patterns differ?
5. **Complexity Signals:** Does name complexity correlate with game complexity?

---

## Key Hypotheses

### H1: The Brevity Advantage
**Prediction:** Shorter names (≤3 syllables) correlate with higher BGG ratings (r = -0.15)  
**Rationale:** Cognitive load minimization—easier to remember and recommend

### H2: The Euro Abstraction Hypothesis
**Prediction:** European designers favor abstract names (Agricola, Azul) while American designers prefer thematic names (Pandemic, Betrayal)  
**Cultural Context:** Euro design philosophy emphasizes mechanics over narrative

### H3: Name-Game Complexity Correlation
**Prediction:** Name length predicts game weight (r = 0.30)  
**Mechanism:** Heavy games signal complexity through elaborate names

### H4: Temporal Name Expansion
**Prediction:** Contemporary games (2010+) have 40% longer names than classics  
**Trend:** +1.2 syllables per decade due to market saturation

### H5: The Colon Effect
**Prediction:** Games with colons form distinct naming cluster  
**Pattern:** Brand architecture (base game → expansions with colon syntax)

---

## Infrastructure

### Database Models
- **BoardGame:** Game entity with BGG ratings, complexity, designer data
- **BoardGameAnalysis:** Phonetic and linguistic features

### Data Collection
- **File:** `collectors/board_game_collector.py`
- **Source:** BoardGameGeek XML API
- **Strategy:** Stratified sampling by era (200/400/600/800)
- **Rate Limit:** 2 requests/second (BGG requirement)

### Statistical Analysis
- **File:** `analyzers/board_game_statistical_analyzer.py`
- **Analyses:** 6 comprehensive modules
- **Methods:** Clustering, temporal analysis, cultural comparison, prediction

### Web Interface
- **Dashboard:** `/board-games` → Interactive exploration
- **Findings:** `/board-games/findings` → Research results
- **APIs:** `/api/board-games/stats`, `/clusters`, `/temporal`, `/cultural`

---

## Expected Discoveries

1. **The Memorability Paradox:** Most memorable names aren't highest-rated (quality trumps marketing)
2. **Euro Abstraction:** German games average 2.8 syllables vs American 3.6
3. **Modern Explosion:** +1.8 syllables from 1950s to 2020s
4. **Complexity Signals:** Name length predicts game weight (r ≈ 0.30)
5. **Colon Architecture:** Expansion naming creates systematic brand families

---

## Execution Guide

### 1. Run Data Collection
```bash
cd /Users/michaelsmerconish/Desktop/RandomCode/FlaskProject
source .venv/bin/activate
python scripts/collect_board_games_comprehensive.py --target 2000
```

### 2. Run Analysis
```bash
python -c "from analyzers.board_game_statistical_analyzer import BoardGameStatisticalAnalyzer; analyzer = BoardGameStatisticalAnalyzer(); print(analyzer.generate_summary_report())"
```

### 3. View Results
- Dashboard: http://localhost:5000/board-games
- Findings: http://localhost:5000/board-games/findings
- API: http://localhost:5000/api/board-games/stats

---

## Sample Size Targets

| Era | Years | Target | Status |
|-----|-------|--------|--------|
| Classic | 1950-1979 | 200 | Pending |
| Golden | 1980-1999 | 400 | Pending |
| Modern | 2000-2009 | 600 | Pending |
| Contemporary | 2010-2024 | 800 | Pending |
| **Total** | **75 years** | **2,000** | **Pending** |

---

## Documentation Files

- `README.md` - This file (overview)
- `BOARD_GAMES_METHODOLOGY.md` - Detailed methods
- `BOARD_GAMES_FINDINGS.md` - Results (after analysis)
- `QUICKSTART.md` - Quick execution guide

---

**Status:** ✅ Framework complete, ready for data collection  
**Priority:** High  
**Innovation Rating:** 2/3  
**Timeline:** 10-11 hours for full implementation + collection

