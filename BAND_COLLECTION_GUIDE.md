# Band Data Collection Guide - 8,000-10,000 Bands

**Objective:** Collect comprehensive band dataset for geopolitical linguistics and phonetic lineage analysis  
**Target:** 8,000-10,000 bands with demographic/geopolitical enrichment  
**Timeline:** 2-4 weeks (8-16 hours API time total)  
**Cost:** $0 (free APIs, rate-limited)

---

## I. Collection Strategy

### Stratified Sampling Approach

To ensure representative coverage across:
- **Decades:** 1950s through 2020s (10 cohorts)
- **Genres:** Rock, Metal, Pop, Hip-Hop, Electronic, Country, Jazz, etc. (15+ genres)
- **Geography:** 35+ countries with music scenes

**Target per stratum:**
- 10 decades × 15 genres × 5 countries = ~750 strata
- 10-15 bands per stratum where available
- Total: 8,000-10,000 bands

---

## II. Existing Infrastructure

### Scripts Ready to Use

**1. Basic Collection:**
```bash
python3 scripts/collect_bands.py
```

**2. Comprehensive Collection (Recommended):**
```bash
python3 scripts/collect_bands_comprehensive.py --target 10000 --resume
```

Features:
- Progress tracking
- Resumable (saves checkpoints)
- Stratified sampling built-in
- Error handling
- Rate limit management

**3. Test Mode:**
```bash
python3 scripts/collect_bands.py --test
```
- Collects 100 bands for testing
- Verifies API connectivity
- Checks data quality

### Database Models Ready

`core/models.py` includes:
- `Band` model (50+ fields)
- `BandAnalysis` model (24+ linguistic fields)
- Demographic enrichment fields (40+ fields)
- Geopolitical enrichment fields (30+ fields)

---

## III. API Configuration

### Required APIs

**1. MusicBrainz API**
- Base URL: `https://musicbrainz.org/ws/2/`
- Rate limit: 1 request/second (strict)
- Coverage: ~2M artists, comprehensive metadata
- Free, no API key needed
- Provides: Band name, origin country, active years, genre tags

**2. Last.fm API (Optional but Recommended)**
- Base URL: `http://ws.audioscrobbler.com/2.0/`
- Rate limit: 5 requests/second
- Free tier: 60,000 requests/day
- API key: Required (free signup)
- Provides: Play counts, listener counts, tags, similar artists

### API Keys Setup

Create `instance/config.json`:
```json
{
  "LASTFM_API_KEY": "your_key_here",
  "LASTFM_SHARED_SECRET": "your_secret_here"
}
```

Get Last.fm API key:
1. Go to https://www.last.fm/api/account/create
2. Register application
3. Copy API Key and Shared Secret
4. Add to config.json

---

## IV. Collection Execution Plan

### Week 1: Setup & Pilot (Days 1-3)

**Day 1: Environment Setup**
```bash
# Verify dependencies
pip install -r requirements.txt

# Test database connection
python3 -c "from core.models import db, Band; print('DB OK')"

# Test APIs
python3 scripts/collect_bands.py --test
```

**Day 2: Pilot Collection (100 bands)**
```bash
# Collect pilot sample
python3 scripts/collect_bands.py --limit 100

# Verify data quality
python3 -c "
from core.models import db, Band, BandAnalysis
from app import app

with app.app_context():
    bands = Band.query.limit(10).all()
    for b in bands:
        print(f'{b.name} - {b.origin_country} - {b.formation_year}')
"
```

**Day 3: Review & Adjust**
- Check data completeness
- Verify demographic enrichment working
- Adjust sampling if needed
- Fix any bugs

### Week 2-3: Main Collection (Days 4-17)

**Strategy:** Collect 500-750 bands per day

**Daily Routine:**
```bash
# Morning: Start collection
nohup python3 scripts/collect_bands_comprehensive.py \
  --target 10000 \
  --resume \
  --checkpoint-every 100 \
  > band_collection.log 2>&1 &

# Monitor progress
tail -f band_collection.log

# Evening: Check stats
python3 -c "
from core.models import db, Band
from app import app

with app.app_context():
    total = Band.query.count()
    by_country = db.session.query(
        Band.origin_country, 
        db.func.count(Band.id)
    ).group_by(Band.origin_country).all()
    
    print(f'Total bands: {total}')
    print(f'Countries: {len(by_country)}')
    for country, count in sorted(by_country, key=lambda x: -x[1])[:10]:
        print(f'  {country}: {count}')
"
```

**Rate Limiting:**
- MusicBrainz: 1 request/second = 3,600/hour = 86,400/day
- At 5 bands/request average: ~17,000 bands/day theoretical max
- Realistic with errors: 5,000-10,000 bands/day

**Monitoring:**
- Check log file hourly for errors
- Verify database growth
- Monitor disk space (SQLite grows ~1MB per 1,000 bands)

### Week 4: Quality Assurance (Days 18-21)

**Day 18: Data Quality Audit**
```python
# Check completeness
from core.models import db, Band, BandAnalysis
from app import app

with app.app_context():
    total_bands = Band.query.count()
    with_analysis = Band.query.join(BandAnalysis).count()
    with_country = Band.query.filter(Band.origin_country != None).count()
    with_year = Band.query.filter(Band.formation_year != None).count()
    
    print(f"Total bands: {total_bands}")
    print(f"With analysis: {with_analysis} ({with_analysis/total_bands*100:.1f}%)")
    print(f"With country: {with_country} ({with_country/total_bands*100:.1f}%)")
    print(f"With year: {with_year} ({with_year/total_bands*100:.1f}%)")
```

**Day 19: Fill Gaps**
- Identify under-represented strata
- Target collection for gaps
- Ensure geographic diversity

**Day 20: Demographic Enrichment**
```bash
# Run demographic enrichment (if not automatic)
python3 scripts/enrich_bands_demographics.py
```

Enriches each band with:
- Language family
- Colonial history
- Socioeconomic indicators (GDP, HDI)
- Cultural dimensions (Hofstede)
- Geopolitical relations (if from US/UK/etc)

**Day 21: Final Validation**
- Verify 8,000+ bands collected
- Check analysis completeness
- Export summary statistics
- Backup database

---

## V. Demographic Enrichment

### Automatic Enrichment (Built-in)

When collecting, `band_collector.py` automatically enriches with:

**From `data/demographic_data/country_demographics.json`:**
- Language family (Germanic, Romance, Slavic, Asian, etc.)
- Phonological features (consonant clusters, L/R distinction, etc.)
- Colonial history (former colony, power, independence year)
- Socioeconomic (GDP, HDI, Gini, urbanization)
- Cultural dimensions (Hofstede 6 dimensions)
- Religious context
- Music industry metrics

**From `data/international_relations/us_country_relations.json`:**
- US favorability score
- Relationship status (ally, rival, adversary)
- Military cooperation
- Trade volume
- Historical conflicts
- Pronunciation harshness (standard)
- Exonym usage rate

### Manual Enrichment (If Needed)

If automatic enrichment fails:
```bash
python3 scripts/enrich_bands_demographics.py --force-recompute
```

---

## VI. Sampling Strategy Details

### Geographic Stratification

**Tier 1 Countries (Target: 500+ each):**
- United States
- United Kingdom
- Germany
- Japan
- France

**Tier 2 Countries (Target: 200-500 each):**
- Canada, Australia, Sweden, Norway, Finland
- Brazil, Mexico, Spain, Italy
- China, Korea, India

**Tier 3 Countries (Target: 50-200 each):**
- All other countries with active music scenes
- Focus on geopolitical diversity:
  - NATO allies vs non-allies
  - Post-colonial nations
  - Communist/former-communist
  - Middle East, Africa representation

### Genre Stratification

**Major Genres (Target: 800+ each):**
- Rock, Metal, Pop, Hip-Hop/Rap

**Secondary Genres (Target: 300-500 each):**
- Electronic/Dance, Country, R&B/Soul, Punk
- Indie/Alternative, Jazz, Blues

**Minor Genres (Target: 100+ each):**
- Folk, Reggae, Latin, World, Classical

### Temporal Stratification

**By Decade (Target: 800+ each):**
- 1950s: 400 (fewer bands, smaller scene)
- 1960s: 800
- 1970s: 1,000 (peak diversity)
- 1980s: 1,000
- 1990s: 1,000
- 2000s: 1,200
- 2010s: 1,500
- 2020s: 1,100

**Ensures temporal coverage for:**
- Era-specific formulas
- Generational cycles
- Historical evolution patterns

---

## VII. Quality Metrics

### Minimum Acceptable

- **Total bands:** ≥ 8,000
- **Geographic coverage:** ≥ 25 countries
- **Temporal coverage:** All decades 1950s-2020s represented
- **Genre diversity:** ≥ 10 major genres
- **Analysis completeness:** ≥ 90% with BandAnalysis records
- **Demographic enrichment:** ≥ 80% with country demographics

### Target Goals

- **Total bands:** 10,000
- **Geographic coverage:** 35+ countries
- **With popularity data:** ≥ 60% (Last.fm listeners)
- **With genre tags:** ≥ 80%
- **Full enrichment:** 90%+ with all demographic fields

### Excellence Criteria

- **Total bands:** 12,000+
- **Geographic coverage:** 50+ countries
- **Stratification balance:** All strata ≥ 10 bands
- **Data completeness:** 95%+ all fields
- **Ready for analysis:** Can start immediately

---

## VIII. Troubleshooting

### Common Issues

**1. API Rate Limiting**
```
Error: HTTP 503 Service Unavailable (MusicBrainz)
```
Solution: Collector has built-in backoff, wait and resume

**2. Database Locked**
```
sqlite3.OperationalError: database is locked
```
Solution: Only run one collector at a time, check for zombie processes

**3. Missing API Key**
```
Last.fm API error: Invalid API key
```
Solution: Check `instance/config.json`, verify key is correct

**4. Memory Issues**
```
MemoryError or killed by OS
```
Solution: Process in smaller batches, add --checkpoint-every 50

**5. Network Errors**
```
Connection timeout, DNS errors
```
Solution: Check internet connection, retry failed batches

### Recovery

**If collection crashes:**
```bash
# Find latest checkpoint
ls -ltr data/collection_checkpoints/

# Resume from checkpoint
python3 scripts/collect_bands_comprehensive.py --resume
```

**If database corrupted:**
```bash
# Backup current database
cp name_study.duckdb name_study.duckdb.backup_$(date +%Y%m%d)

# Check integrity
sqlite3 name_study.duckdb "PRAGMA integrity_check;"

# If corrupted, restore from backup
cp name_study.duckdb.backup_YYYYMMDD name_study.duckdb
```

---

## IX. Post-Collection Analysis

### Immediate (Week 4)

**1. Generate Summary Statistics:**
```bash
python3 scripts/generate_band_report.py
```

Outputs:
- Total counts by country, decade, genre
- Completeness metrics
- Sample distributions
- Data quality report

**2. Run Basic Analyses:**
```bash
# Temporal analysis
python3 -m analyzers.band_temporal_analyzer

# Geographic analysis
python3 -m analyzers.band_geographic_analyzer

# Statistical models
python3 -m analyzers.band_statistical_analyzer
```

**3. Verify Geopolitical Data:**
```bash
# Check pronunciation/favorability enrichment
python3 -c "
from core.models import db, Band
from app import app

with app.app_context():
    with_geo = Band.query.filter(Band.us_favorability != None).count()
    total = Band.query.count()
    print(f'Bands with geopolitical data: {with_geo}/{total} ({with_geo/total*100:.1f}%)')
"
```

### Following Weeks

**4. Run All 7 Analyzers:**
- band_temporal_analyzer.py
- band_geographic_analyzer.py
- band_statistical_analyzer.py
- band_advanced_statistical_analyzer.py
- band_phonetic_lineage_analyzer.py
- band_cross_cultural_analyzer.py
- band_exonym_pronunciation_analyzer.py

**5. Generate Comprehensive Report:**
- Executive summary
- Key findings
- Visualizations
- Publication-ready tables

---

## X. Success Checklist

Before marking collection complete, verify:

- [ ] ≥ 8,000 bands collected
- [ ] ≥ 25 countries represented
- [ ] All decades 1950s-2020s covered
- [ ] ≥ 10 major genres included
- [ ] ≥ 90% have BandAnalysis records
- [ ] ≥ 80% have demographic enrichment
- [ ] ≥ 60% have popularity metrics
- [ ] Database integrity verified
- [ ] Backup created
- [ ] Summary statistics generated
- [ ] Ready for analysis phase

---

## XI. Timeline Summary

| Week | Days | Activity | Output |
|------|------|----------|--------|
| 1 | 1-3 | Setup & pilot | 100 bands, verified system |
| 2 | 4-10 | Collection sprint | 3,500 bands |
| 3 | 11-17 | Collection sprint | +3,500 bands (7,000 total) |
| 4 | 18-21 | Fill gaps & QA | 8,000-10,000 final |

**Total elapsed time:** 3-4 weeks  
**Total API time:** 8-16 hours  
**Hands-on time:** ~20-30 hours

---

## XII. Next Steps After Collection

1. **Mark todo complete:** ✅ Band collection sprint
2. **Start analysis:** Run all 7 analyzers
3. **Validate hypotheses:** Test 23 predictions
4. **Generate findings:** Document what emerges
5. **Compare to predictions:** Discovery orientation
6. **Write papers:** Geopolitical linguistics, phonetic lineage
7. **Update framework:** Cross-domain synthesis with band data

---

**Document Status:** Ready for execution  
**Infrastructure Status:** ✅ Complete (collectors, models, analyzers ready)  
**API Status:** ✅ Free and available  
**Next Action:** Run pilot collection (100 bands) to verify

**Total Cost:** $0  
**Total Time:** 3-4 weeks  
**Total Bands:** 8,000-10,000  
**Impact:** Unlocks 3-4 major papers

