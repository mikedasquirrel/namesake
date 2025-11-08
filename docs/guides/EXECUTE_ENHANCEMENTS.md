# Execute Data Enhancements - Quick Reference

## 🚀 Run All Enhancements

Copy and paste these commands to execute comprehensive platform enhancement.

---

## Phase 1: Complete Partial Analyses (Fast - 20-30 min)

```bash
cd /Users/michaelsmerconish/Desktop/RandomCode/FlaskProject
source .venv/bin/activate

# Stock Analysis (1,474 stocks)
python scripts/complete_stock_analysis_batch.py

# Ship Analysis (164 ships)
python scripts/complete_ship_analysis_batch.py

# Domain Analysis (1,278 domains)
python scripts/complete_domain_analysis_batch.py
```

**Result:** Stock + Ship + Domain analysis 100% complete

---

## Phase 2: New Data Collection

### Mental Health (30-60 min)
```bash
python scripts/expand_mental_health_comprehensive.py
```

### NBA Players (2-4 hours)
```bash
# Run in background or overnight
nohup python scripts/collect_nba_comprehensive.py > nba_output.log 2>&1 &

# Monitor progress
tail -f nba_collection.log
```

### Bands (1-2 hours) 
```bash
# May have schema issues - check first
python scripts/collect_bands_comprehensive.py
```

---

## Phase 3: NFL Collection (After Rate Limit)

### Wait 30-60 minutes from last attempt, then:

```bash
# Test single player first
python scripts/test_single_nfl_player.py

# If successful, collect data
python scripts/collect_nfl_mass_scale.py --target-per-position 50
```

---

## Monitor Progress

```bash
# Check all domains
python scripts/monitor_background_jobs.py

# Check specific logs
tail -f mental_health_collection.log
tail -f nba_collection.log
tail -f nfl_collection.log
```

---

## After Collection Complete

```bash
# Run comprehensive analyses
python scripts/nfl_deep_dive_analysis.py

# Start web server
python app.py

# Visit dashboards
open http://localhost:5000/nfl
open http://localhost:5000/nba
open http://localhost:5000/overview
```

---

## Expected Results

- **Stocks:** 1,681/1,681 analyzed (100%)
- **Ships:** 853/853 analyzed (100%)
- **Domains:** 2,278/2,278 analyzed (100%)
- **Mental Health:** 500+ terms
- **NBA:** 1,000+ players
- **NFL:** 500+ players (after rate limit)

**Total Platform: 15,000+ analyzed entities across 12+ domains**

---

## Troubleshooting

### If Rate Limited (429 error):
```bash
# Wait 30-60 minutes
# Scripts have automatic retry with exponential backoff
```

### If Process Hangs:
```bash
# Check logs
tail -f *.log

# Kill if needed
pkill -f "collect_nba"
```

### If Database Locked:
```bash
# Close all connections, restart script
```

---

**Quick Start:** Run Phase 1 scripts first (fast wins!)  
**Monitor:** Use `python scripts/monitor_background_jobs.py`  
**Final Goal:** 15,000+ entities, publication-ready platform

