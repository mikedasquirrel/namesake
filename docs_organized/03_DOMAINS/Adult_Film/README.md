# Adult Film Performer Stage Name Analysis

**Research Domain:** Strategic naming in professional entertainment  
**Framework Status:** ✅ Complete  
**Data Status:** Awaiting collection  
**Expected Effect Size:** r = 0.30-0.40 (strongest yet)

---

## Overview

This research domain examines how strategically chosen stage names predict career outcomes in adult film entertainment. Adult performers consciously select stage names for audience appeal and brand recognition, making this domain uniquely valuable for testing nominative determinism in contexts where names are explicitly optimized for success.

### Why This Domain Matters

1. **Strategic Selection:** Names are deliberately chosen for career optimization (not assigned at birth)
2. **Natural Experiment:** Can compare stage names vs real names when both are known
3. **Measurable Outcomes:** View counts, subscriber numbers, awards provide objective metrics
4. **Large Sample:** Thousands of performers across 50+ year history
5. **High Competition:** Small advantages matter in saturated market

### Comparison to Other Domains

- **Bands:** r = 0.19 (3.1× sales for 1-word names)
- **NBA:** r = 0.24 (+12.8% PPG for harsh names)
- **Films:** r = 0.14 (+41% revenue for short titles)
- **Adult Film Expected:** r = 0.30-0.40 (strongest due to strategic optimization)

---

## Framework Components

### Database Models ✅
- `AdultPerformer`: Career metrics, success scores, platform data
- `AdultPerformerAnalysis`: 25+ linguistic features, stage-specific metrics

### Data Collector ✅
- `collectors/adult_film_collector.py`
- Multi-source architecture (IAFD, public platforms, awards)
- Stratified sampling across eras and genres
- Target: 2,000-3,000 performers

### Statistical Analyzers ✅
- `analyzers/adult_film_statistical_analyzer.py`
- Success prediction, genre specialization, format effects
- Temporal evolution tracking
- Cross-validation and feature importance

### Web Interface ✅
- `/adult-film` - Main dashboard
- `/adult-film/findings` - Research framework
- Professional, academic presentation

### API Endpoints ✅
- `/api/adult-film/stats` - Overview statistics
- `/api/adult-film/success-analysis` - Name → success correlations
- `/api/adult-film/genre-patterns` - Genre prediction
- `/api/adult-film/name-formats` - Format comparisons
- `/api/adult-film/temporal-evolution` - Era evolution

---

## Research Questions

### Q1: Syllable Effect
**Hypothesis:** 1-2 syllable names predict 25-35% higher success  
**Mechanism:** Memorability and search discoverability  
**Expected r:** 0.32-0.38

### Q2: Genre Specialization
**Hypothesis:** Phonetics predict genre with 65-75% accuracy  
**Mechanism:** Strategic name-genre alignment  
**Expected patterns:** Soft names for certain genres, harsh for others

### Q3: Stage vs Real Names
**Hypothesis:** Stage names outperform real names by 40-60%  
**Mechanism:** Optimization vs arbitrary assignment  
**Natural experiment:** Within-industry comparison

### Q4: Memorability Premium
**Hypothesis:** +20 memorability points = +30% longevity  
**Mechanism:** Repeat audience recognition  
**Expected r:** 0.28-0.32

### Q5: Alliteration Advantage
**Hypothesis:** 25-35% success premium like bands  
**Mechanism:** Enhanced memorability  
**Examples:** Similar to music industry

### Q6: Era Evolution
**Hypothesis:** -0.5 syllables per decade (simplifying trend)  
**Mechanism:** Algorithm optimization, search-friendly  
**Eras:** Golden Age → Video → Internet → Streaming

### Q7: Platform Differences
**Hypothesis:** OnlyFans shows different patterns  
**Mechanism:** Personal branding vs traditional studio system  
**Expected:** Unique names more important

---

## Ethical Framework

### Approach
- **Professional treatment:** Performers as business professionals
- **Academic tone:** Linguistics research, not sensationalism
- **Public data only:** No private or explicit content
- **Respectful framing:** Strategic branding decisions
- **Clear purpose:** Nominative determinism research

### Data Sources
- **IAFD:** Career filmography (public database)
- **Pornhub:** Verified performer metrics (public profiles)
- **AVN/XBIZ:** Awards data (public records)
- **No scraping of private/explicit content**
- **Terms of service compliance**

### Academic Legitimacy
- Comparable to band name analysis (musical entertainment)
- Comparable to film title analysis (visual entertainment)
- Stage name selection is serious business decision
- Contributes to broader understanding of strategic naming

---

## Expected Findings

Based on patterns from 17 previous domains:

**Strong Effects Expected:**
- This domain likely shows **strongest correlations yet** (r = 0.35+)
- Strategic selection amplifies nominative effects
- Similar to popes (100% accuracy) and revolutionaries (89% alignment)

**Key Patterns Anticipated:**
1. Syllable count inversely correlates with success
2. Memorability strongly predicts career longevity
3. Stage names systematically outperform real names
4. Genre predictable from phonetic properties
5. Names simplifying over time (algorithm optimization)
6. Alliteration provides measurable advantage

**Significance:**
- Adds 18th domain to platform
- May show peak nominative effects
- Tests theory where names explicitly chosen for outcomes
- Completes entertainment domain analysis

---

## Files in This Directory

- `README.md` - This overview
- `METHODOLOGY.md` - Detailed research design
- `FINDINGS.md` - Results (after collection)
- `QUICKSTART.md` - How to run analysis
- `ETHICAL_STATEMENT.md` - Research justification

---

## Next Steps

### To Collect Data:
```bash
python scripts/collect_adult_film_comprehensive.py
```

### To Run Analysis:
```bash
python scripts/analyze_adult_film.py
```

### To View Framework:
Navigate to `/adult-film` or click "Stage Names" under "Human Systems" in navbar

---

## Integration with Platform

Upon data collection and analysis, this domain will:

1. Add 18th data point to "Silence" artwork
2. Test entertainment naming pattern in new context
3. Potentially demonstrate strongest effects yet
4. Complete "chosen names" category (popes, revolutionaries, performers)
5. Strengthen overall nominative determinism theory

---

**Status:** Framework Complete - Ready for Data Collection  
**Expected Timeline:** 2-3 weeks data collection, 1 week analysis  
**Expected Publication Value:** High (unique natural experiment)

