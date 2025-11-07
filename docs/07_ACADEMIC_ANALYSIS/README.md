# Academic Names Analysis - Quick Start

**Status:** ✅ Ready for execution  
**Goal:** Test nominative determinism in academia  
**Target:** ROC AUC > 0.85 (match hurricane 0.916)

---

## Quick Start (5 Minutes)

### 1. Test the System
```bash
cd /Users/michaelsmerconish/Desktop/RandomCode/FlaskProject
python scripts/test_academic_collector.py
```

**Expected:** All tests pass ✓

---

### 2. Collect Pilot Data
```bash
python -c "
from collectors.academic_collector import AcademicCollector
from app import create_app

app = create_app()
with app.app_context():
    collector = AcademicCollector()
    results = collector.collect_pilot_sample(n_target=50)
    print(f'Collected: {results[\"collected\"]} professors')
"
```

**Expected:** ~10 professors with full phonetic analysis

---

### 3. Run Analysis
```bash
python scripts/academic_deep_dive_analysis.py
```

**Expected:** 
- Hypothesis test results
- Figures saved to `analysis_outputs/academic_determinism/figures/`
- Report: `analysis_outputs/academic_determinism/ACADEMIC_FINDINGS.md`

---

## Files Overview

| File | Purpose |
|------|---------|
| **Models** | `core/models.py` - Academic, AcademicAnalysis, AcademicResearchMetrics |
| **Collector** | `collectors/academic_collector.py` - Scraping + Google Scholar |
| **Test** | `scripts/test_academic_collector.py` - Validation suite |
| **Collection** | `scripts/collect_academics_mass_scale.py` - Mass production |
| **Analysis** | `scripts/academic_deep_dive_analysis.py` - 6 hypothesis tests |
| **Docs** | `docs/07_ACADEMIC_ANALYSIS/ACADEMIC_NAMES_PROGRAM.md` - Full program |

---

## The Question

> **Can you predict who teaches at Harvard from their name phonetics alone?**

---

## The Hypotheses

**H1:** Name sophistication → University prestige  
**H2:** Phonetic authority → Academic rank  
**H3:** Memorability → Research citations  
**H4:** STEM has harder names than Humanities  
**H5:** Predict Top-20 university (ROC AUC target: >0.85) 🎯  
**H6:** Gender-name interaction (exploratory)

---

## Success Criteria

- **ROC AUC ≥ 0.90:** 🔥🔥🔥 Nature/Science paper
- **ROC AUC 0.85-0.90:** 🔥🔥 PNAS/Science Advances
- **ROC AUC 0.75-0.85:** 🔥 Top specialty journals
- **ROC AUC < 0.75:** PLOS ONE or null finding

---

## Full Documentation

See: `ACADEMIC_NAMES_COMPLETE.md` (root directory)

Or: `ACADEMIC_NAMES_PROGRAM.md` (this directory)

---

**Ready to discover if "Professor Worthington" really does teach at Princeton.**

✅ All code complete. Ready for execution.

