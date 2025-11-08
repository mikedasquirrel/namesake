# Formula Evolution Engine - Command Cheat Sheet

Quick reference for all commands. Keep this handy! 📋

---

## 🚀 MOST USED COMMANDS

```bash
# Check system status
python3 scripts/formula_cli.py status

# View latest results
python3 scripts/formula_cli.py results --latest

# Quick 2-minute test
python3 scripts/quick_test_analysis.py

# Check scheduler
python3 scripts/formula_cli.py scheduler status
```

---

## 📊 ANALYSIS COMMANDS

```bash
# Quick test (2 minutes)
python3 scripts/quick_test_analysis.py

# Daily analysis (30-60 minutes)
python3 scripts/auto_analyze_formulas.py --mode daily

# Weekly deep dive (4-8 hours)
python3 scripts/auto_analyze_formulas.py --mode weekly

# On-demand (when new data added)
python3 scripts/auto_analyze_formulas.py --mode on-demand --domain crypto
```

---

## ⏰ SCHEDULER COMMANDS

```bash
# Start scheduler (runs in foreground)
python3 scripts/formula_cli.py scheduler start

# Check scheduler status
python3 scripts/formula_cli.py scheduler status

# Trigger job immediately
python3 scripts/formula_cli.py scheduler trigger --job daily_analysis

# Check what's scheduled
python3 scripts/scheduler.py status
```

---

## 📈 RESULTS COMMANDS

```bash
# View latest daily results
python3 scripts/formula_cli.py results --latest

# View latest weekly results
python3 scripts/formula_cli.py results --latest --mode weekly

# Compare two result versions
python3 scripts/formula_cli.py results --compare --v1 file1.json --v2 file2.json

# List all results
ls -lh analysis_outputs/auto_analysis/
```

---

## 💾 EXPORT COMMANDS

```bash
# Export as JSON
python3 scripts/formula_cli.py export --format json

# Export as CSV
python3 scripts/formula_cli.py export --format csv

# Export specific mode
python3 scripts/formula_cli.py export --format csv --mode weekly
```

---

## 🗄️ CACHE COMMANDS

```bash
# View cache statistics
python3 scripts/formula_cli.py cache stats

# Clear cache (use with caution!)
python3 scripts/formula_cli.py cache clear --confirm yes

# Check Redis status
redis-cli ping
```

---

## 🔍 MONITORING COMMANDS

```bash
# System status
python3 scripts/formula_cli.py status

# Watch analysis log
tail -f logs/auto_analysis.log

# Monitor in real-time
python3 scripts/monitor_analysis.py

# Check specific log
tail -f logs/daily_run_*.log
```

---

## 🌐 WEB UI COMMANDS

```bash
# Start Flask app
python3 app.py

# Then visit:
# http://localhost:[PORT]/formula-explorer
# http://localhost:[PORT]/the-word-made-flesh
```

---

## 🧪 TESTING COMMANDS

```bash
# Full system test
python3 scripts/test_formula_system.py

# Quick 2-minute demo
python3 scripts/quick_test_analysis.py

# Test single formula
python3 -c "from utils.formula_engine import *; engine = FormulaEngine(); print(engine.list_formulas())"
```

---

## 🔧 REDIS COMMANDS

```bash
# Start Redis
brew services start redis          # macOS
sudo systemctl start redis         # Linux

# Stop Redis
brew services stop redis           # macOS
sudo systemctl stop redis          # Linux

# Check Redis status
redis-cli ping                     # Should return PONG

# Redis info
redis-cli info | grep used_memory
```

---

## 📁 FILE LOCATIONS

```bash
# Configuration
config/auto_analysis.yaml

# Results
analysis_outputs/auto_analysis/

# Logs
logs/auto_analysis.log

# Scripts
scripts/auto_analyze_formulas.py
scripts/formula_cli.py
scripts/scheduler.py
```

---

## ⚡ QUICK WORKFLOWS

### First Time Setup

```bash
pip install redis flask-caching apscheduler pyyaml tabulate
brew install redis && brew services start redis
python3 scripts/test_formula_system.py
python3 scripts/formula_cli.py scheduler start
```

### Daily Check (Morning Routine)

```bash
python3 scripts/formula_cli.py results --latest
python3 scripts/formula_cli.py status
```

### Manual Analysis

```bash
python3 scripts/auto_analyze_formulas.py --mode daily
python3 scripts/formula_cli.py results --latest
python3 scripts/formula_cli.py export --format csv
```

### Troubleshooting

```bash
python3 scripts/test_formula_system.py
python3 scripts/formula_cli.py status
tail -f logs/auto_analysis.log
```

---

## 🎯 CONFIGURATION TWEAKS

### Change Schedule Time

Edit `config/auto_analysis.yaml`:
```yaml
schedule:
  daily_analysis:
    time: "03:00"  # Change to 3 AM
```

### Adjust Analysis Depth

```yaml
analysis_settings:
  validation:
    daily_limit_per_domain: 100  # Smaller = faster
  evolution:
    daily:
      population_size: 10        # Smaller = faster
      n_generations: 10
```

### Enable Notifications

```yaml
notifications:
  email:
    enabled: true
    to_emails:
      - "your@email.com"
```

---

## 🆘 COMMON ISSUES

**"Redis connection failed"**
```bash
brew services start redis
redis-cli ping
```

**"Scheduler not running"**
```bash
python3 scripts/formula_cli.py scheduler start
```

**"No results found"**
```bash
python3 scripts/auto_analyze_formulas.py --mode daily
```

**"Analysis taking too long"**
- Reduce sample sizes in config
- Use smaller populations
- Check system resources

---

## 📞 GET HELP

```bash
# General help
python3 scripts/formula_cli.py --help

# Command-specific help
python3 scripts/formula_cli.py scheduler --help
python3 scripts/formula_cli.py analyze --help
python3 scripts/formula_cli.py results --help

# Analysis script help
python3 scripts/auto_analyze_formulas.py --help
```

---

## 🎉 QUICK WINS

**Transform any name instantly:**
```python
from utils.formula_engine import FormulaEngine
from analyzers.name_analyzer import NameAnalyzer

analyzer = NameAnalyzer()
features = analyzer.analyze_name("YourName")

engine = FormulaEngine()
encodings = engine.transform_all("YourName", features)

for formula, enc in encodings.items():
    print(f"{formula}: {enc.shape_type}, {enc.hue:.1f}°")
```

**Check cache performance:**
```bash
python3 scripts/formula_cli.py cache stats
```

**Export for presentation:**
```bash
python3 scripts/formula_cli.py export --format csv
```

---

*Quick Reference Card*  
*Formula Evolution Engine v2.0*  
*Keep this handy!* 📋

