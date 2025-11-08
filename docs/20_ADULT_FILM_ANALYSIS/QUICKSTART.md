# Adult Film Performer Analysis - Quick Start Guide

## Framework Status

✅ **COMPLETE** - All infrastructure ready  
⏳ **Awaiting** - Data collection initiation

---

## View the Framework

### Web Dashboard

```bash
# Start Flask server
python3 app.py

# Navigate to:
http://localhost:PORT/adult-film
```

### Research Page

```bash
http://localhost:PORT/adult-film/findings
```

### API Endpoints

```bash
# Overview stats
curl http://localhost:PORT/api/adult-film/stats

# Success analysis
curl http://localhost:PORT/api/adult-film/success-analysis

# Genre patterns
curl http://localhost:PORT/api/adult-film/genre-patterns

# Name format effects
curl http://localhost:PORT/api/adult-film/name-formats

# Temporal evolution
curl http://localhost:PORT/api/adult-film/temporal-evolution
```

---

## Data Collection (When Ready)

### Prerequisites

1. **API Access:**
   - IAFD database access (or scraping approval)
   - Public platform API keys if available
   - AVN/XBIZ awards database access

2. **Compliance:**
   - Terms of service review completed
   - Legal approval for data collection
   - Ethical review if required by institution

3. **Infrastructure:**
   - Sufficient storage for 2,500+ performer records
   - Database migrations run
   - Backup systems in place

### Run Collection

```bash
# Test with small sample first
python3 collectors/adult_film_collector.py

# Or use collection script (when created)
python3 scripts/collect_adult_film_comprehensive.py --target 2500
```

### Monitor Progress

```bash
# Check collection stats
python3 -c "from collectors.adult_film_collector import AdultFilmCollector; \
            c = AdultFilmCollector(); \
            print(c.get_dataset_summary())"
```

---

## Run Analysis

### After Data Collection Complete

```bash
# Run statistical analysis
python3 analyzers/adult_film_statistical_analyzer.py

# This will output:
# - Success prediction results
# - Genre specialization analysis
# - Name format comparisons
# - Temporal evolution findings
```

### View Results

Results automatically populate:
- Web dashboard (`/adult-film`)
- API endpoints
- Database analysis tables

---

## Expected Timeline

### Phase 1: Data Collection (2-3 weeks)
- Day 1-7: Setup and initial collection (500 performers)
- Day 8-14: Scale collection (1,500 performers)
- Day 15-21: Complete collection (2,500 performers)

### Phase 2: Analysis (1 week)
- Day 22-23: Run linguistic analysis on all names
- Day 24-25: Statistical modeling and correlation analysis
- Day 26-27: Cross-validation and hypothesis testing
- Day 28: Results compilation

### Phase 3: Integration (1 week)
- Day 29-30: Write findings report
- Day 31-32: Create visualizations
- Day 33-34: Update platform and "Silence" artwork
- Day 35: Final documentation

**Total:** 5-6 weeks from start to completion

---

## Current State

### What Exists Now

✅ Database models (AdultPerformer, AdultPerformerAnalysis)  
✅ Data collector framework  
✅ Statistical analyzer  
✅ Temporal analyzer  
✅ Web templates (dashboard + findings)  
✅ API endpoints (5 endpoints)  
✅ Navigation integration  
✅ Documentation

### What's Needed

⏳ Actual data collection  
⏳ Analysis execution  
⏳ Results documentation  
⏳ Platform integration

---

## Quick Commands Reference

```bash
# View framework status
curl http://localhost:PORT/api/adult-film/stats

# Check database
python3 -c "from core.models import AdultPerformer; \
            print(f'Performers: {AdultPerformer.query.count()}')"

# Test collector
python3 collectors/adult_film_collector.py

# Run analysis
python3 analyzers/adult_film_statistical_analyzer.py

# Add to Silence artwork (after collection)
python3 scripts/evolve_the_nail.py --add
```

---

## Integration with Platform

Once data is collected and analyzed, this domain will:

1. **Add to Research Platform**
   - Becomes domain #18
   - Accessible via "Human Systems" → "Stage Names"

2. **Update "Silence" Artwork**
   - New data point added
   - Composition regenerates
   - Heart either holds or breaks further

3. **Cross-Domain Synthesis**
   - Compare to bands, films, sports
   - Test entertainment pattern generalization
   - Strengthen or refine overall theory

---

## For Questions or Issues

1. Check documentation in this directory
2. Review methodology and ethical statement
3. Consult existing domain analyses for comparison
4. See main project README for platform overview

---

**Status:** Framework complete, ready for data collection  
**Next Action:** Secure data access and begin collection  
**Expected Results:** Strongest effects yet (r = 0.30-0.40)

---

**Last Updated:** November 8, 2025  
**Framework Version:** 1.0

