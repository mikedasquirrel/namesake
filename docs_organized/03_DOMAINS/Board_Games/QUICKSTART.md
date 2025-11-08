# Board Games Analysis - Quick Start Guide

**Goal:** Collect and analyze 2,000 board games in under 4 hours

---

## Prerequisites

```bash
# Ensure you're in project directory
cd /Users/michaelsmerconish/Desktop/RandomCode/FlaskProject

# Activate virtual environment
source .venv/bin/activate

# Verify dependencies
pip install requests lxml  # For BGG XML API parsing
```

---

## Step 1: Create Database Tables

```bash
# Start Python shell
python

# Create tables
from app import app, db
with app.app_context():
    db.create_all()
    print("✅ Board game tables created")
```

---

## Step 2: Collect Data

### Option A: Quick Test (50 games, ~2 minutes)

```bash
python -c "
from collectors.board_game_collector import BoardGameCollector
from app import app, db

with app.app_context():
    collector = BoardGameCollector()
    result = collector.collect_top_n(50)
    print(f'✅ Collected {result[\"collected\"]} games')
"
```

### Option B: Full Collection (2,000 games, ~3-4 hours)

Create `scripts/collect_board_games_comprehensive.py`:

```python
"""Comprehensive Board Game Collection Script"""

import logging
from collectors.board_game_collector import BoardGameCollector
from app import app, db

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    with app.app_context():
        collector = BoardGameCollector()
        
        # Stratified collection
        targets = {
            'classic_1950_1979': 200,
            'golden_1980_1999': 400,
            'modern_2000_2009': 600,
            'contemporary_2010_2024': 800
        }
        
        result = collector.collect_stratified_sample(targets)
        
        print(f"\n✅ COLLECTION COMPLETE")
        print(f"Total collected: {result['total_collected']}")
        print(f"By era: {result['by_era']}")

if __name__ == "__main__":
    main()
```

Run it:
```bash
python scripts/collect_board_games_comprehensive.py
```

---

## Step 3: Run Analysis

```bash
python -c "
from analyzers.board_game_statistical_analyzer import BoardGameStatisticalAnalyzer
from app import app
import json

with app.app_context():
    analyzer = BoardGameStatisticalAnalyzer()
    report = analyzer.generate_summary_report()
    print(json.dumps(report, indent=2))
"
```

---

## Step 4: View Results

### Web Interface
```bash
# Start Flask app
python app.py

# Visit in browser:
# - Dashboard: http://localhost:5000/board-games
# - Findings: http://localhost:5000/board-games/findings
```

### API Access
```bash
# Overview stats
curl http://localhost:5000/api/board-games/stats | json_pp

# Cluster analysis
curl http://localhost:5000/api/board-games/clusters | json_pp

# Temporal evolution
curl http://localhost:5000/api/board-games/temporal | json_pp

# Cultural comparison
curl http://localhost:5000/api/board-games/cultural | json_pp
```

---

## Verification

```bash
# Check database
python -c "
from app import app, db
from core.models import BoardGame, BoardGameAnalysis

with app.app_context():
    total = BoardGame.query.count()
    analyzed = BoardGameAnalysis.query.count()
    print(f'✅ Games: {total}')
    print(f'✅ Analyzed: {analyzed}')
    
    # By era
    for era in ['classic_1950_1979', 'golden_1980_1999', 'modern_2000_2009', 'contemporary_2010_2024']:
        count = BoardGameAnalysis.query.filter_by(era=era).count()
        print(f'   {era}: {count}')
"
```

---

## Troubleshooting

### Issue: "No data collected yet"
**Solution:** Run data collection first (Step 2)

### Issue: BGG API timeout
**Solution:** BGG API can be slow. Increase timeout in collector or retry failed requests

### Issue: "Insufficient data for analysis"
**Solution:** Need minimum 100 games. Run collection script longer.

### Issue: Rate limiting errors
**Solution:** Collector has built-in delays (0.6s). If still hitting limits, increase delay in `board_game_collector.py`

---

## Next Steps

1. ✅ Collect 2,000+ games
2. ✅ Run full analysis
3. ✅ Generate BOARD_GAMES_FINDINGS.md with results
4. ✅ Add to main navigation (already done)
5. ✅ Share results

---

**Estimated Time:** 10-11 hours total  
**Data Collection:** 3-4 hours  
**Analysis:** < 5 minutes  
**Review & Documentation:** 1 hour

