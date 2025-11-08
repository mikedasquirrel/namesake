# Adult Film Performer Stage Name Analysis - Methodology

**Research Design:** Observational study with natural experiment component  
**Sample Target:** 2,000-3,000 performers (1970-2024)  
**Analysis:** Correlational with predictive modeling

---

## Research Questions

1. Do shorter, memorable stage names predict longer careers?
2. Can name phonetics predict genre specialization?
3. Do stage names outperform real names?
4. Does alliteration provide advantage?
5. How have naming patterns evolved across eras?
6. Do awards correlate with name sophistication?
7. Do platform differences (traditional vs OnlyFans) affect naming strategies?

---

## Data Collection

### Sample Frame

**Target:** 2,000-3,000 adult film performers

**Stratification:**
- **By Era:**
  - Golden Age (1970-1989): 400 performers
  - Video Era (1990-2004): 600 performers
  - Internet Era (2005-2014): 600 performers
  - Streaming Era (2015-2024): 900 performers

- **By Gender:** Balanced representation

- **By Career Level:**
  - Award winners: 200
  - High-profile (>100M views): 500
  - Mid-tier: 1,000
  - Emerging: 800

### Data Sources

**Primary Sources:**
1. **IAFD (Internet Adult Film Database)**
   - Comprehensive filmography
   - Career timelines (debut to retirement)
   - Genre classifications
   - Awards and nominations

2. **Public Platform Metrics**
   - Pornhub: Verified performer view counts, subscriber numbers
   - xVideos: Public view metrics
   - OnlyFans: Subscriber counts (when publicly disclosed)

3. **Industry Awards Databases**
   - AVN (Adult Video News) Awards
   - XBIZ Awards
   - Public nomination and winner lists

**Data Collection Protocol:**
- Use public APIs where available
- Scrape only publicly accessible profile pages
- Follow all terms of service
- No collection of explicit content
- Focus on career metrics only

### Variables Collected

**Dependent Variables (Outcomes):**
- Career length (years active)
- Total films/videos
- Cumulative views across platforms
- Subscriber counts
- Award nominations and wins
- Success scores (computed composite)

**Independent Variables (Name Features):**
- Syllable count, word count, character length
- Harshness, softness, memorability scores
- Pronounceability, uniqueness, accessibility
- Sexy score, fantasy score, brand strength
- Alliteration, vowel ratio, phonetic complexity
- Name format (single vs full, with/without descriptors)
- Stage vs real name comparison (when known)

---

## Linguistic Analysis Pipeline

### Step 1: Basic Metrics
- Syllable counting (CMU dictionary)
- Word count and character length
- Name format classification

### Step 2: Phonetic Analysis
- Harshness score (plosives, stops)
- Softness score (liquids, vowels)
- Memorability (multiple factors)
- Pronounceability (phonotactic probability)

### Step 3: Stage-Specific Metrics
- **Sexy Score:** Vowel-heavy, liquid sounds, flowing phonetics
- **Fantasy Score:** Exotic elements, unusual spelling, aspirational quality
- **Accessibility Score:** Ease of saying, remembering, searching
- **Brand Strength:** Overall naming power for professional branding

### Step 4: Genre Alignment
- Innocent-sounding score (soft, simple)
- Aggressive-sounding score (harsh, complex)
- Exotic-sounding score (international appeal)
- Girl-next-door score (relatable, accessible)

---

## Statistical Methods

### Correlation Analysis
- Pearson r for continuous outcomes
- Point-biserial for binary outcomes
- Significance testing (p < 0.05 threshold)
- Effect size reporting (Cohen's d)

### Regression Modeling
- **Success Prediction:** Random Forest Regressor
  - Input: 20+ name features
  - Output: Overall success score
  - Cross-validation: 5-fold
  - Feature importance ranking

- **Genre Prediction:** Random Forest Classifier
  - Input: Phonetic features
  - Output: Primary genre
  - Accuracy target: 65-75%

### Comparative Analysis
- **Stage vs Real Names:** T-tests comparing success scores
- **Name Formats:** ANOVA across format types
- **Era Evolution:** Temporal trend analysis
- **Alliteration Effect:** Comparison with/without alliteration

### Cross-Validation
- 5-fold CV for all predictive models
- Out-of-sample R² reporting
- Train/test split (80/20)
- Overfitting checks

---

## Ethical Considerations

### Professional Treatment
- Performers treated as business professionals making strategic decisions
- Focus on naming as professional branding
- No sensationalism or judgmental framing
- Comparable to analysis of athlete nicknames or band stage names

### Data Privacy
- Public data sources only
- No scraping of private content
- Compliance with platform terms of service
- No personally identifiable information beyond publicly chosen stage names

### Academic Framing
- Contribution to nominative determinism research
- Understanding strategic naming across all human domains
- Professional branding and identity construction
- Entertainment industry business practices

### Research Purpose
- Linguistic analysis of naming strategies
- Career outcome prediction from name features
- Strategic decision-making in competitive industries
- Not focused on content, only on names and career metrics

---

## Expected Findings

### Primary Hypotheses

**H1: Strong Syllable Effect**
- Expected r = -0.32 (negative correlation)
- 1-2 syllable names predict +30% success
- Mechanism: Memorability in visual medium

**H2: Memorability Premium**
- Expected r = 0.35
- Critical in competitive industry
- Search and recall advantages

**H3: Stage Name Advantage**
- Stage names +40-60% over real names
- Natural experiment validation
- Demonstrates strategic optimization

**H4: Genre Prediction**
- 70% accuracy from phonetics
- Innocent vs aggressive sound profiles
- Strategic genre-name alignment

**H5: Alliteration Effect**
- +25% success premium
- Similar to band names
- Enhanced memorability

**H6: Era Evolution**
- Names simplifying over time
- Algorithm optimization
- Platform-specific patterns

### Significance

If confirmed, this domain would:
- Show strongest nominative effects yet
- Validate that strategic selection amplifies effects
- Complete "chosen names" category analysis
- Add compelling natural experiment evidence
- Strengthen overall nominative determinism theory

---

## Data Quality Control

### Inclusion Criteria
- Verifiable career data (dates, filmography)
- Public profile with metrics
- At least 1 year active
- Quantifiable success metrics

### Exclusion Criteria
- Unverifiable data
- Private/amateur content only
- Insufficient career information
- Duplicate entries

### Validation
- Cross-source verification
- Outlier detection and investigation
- Missing data handling (imputation or exclusion)
- Quality scoring for each record

---

## Analysis Timeline

### Phase 1: Data Collection (2-3 weeks)
- Build comprehensive performer list
- Collect career metrics from sources
- Verify data quality
- Stratify sample appropriately

### Phase 2: Linguistic Analysis (1 week)
- Run name analyzer on all performers
- Compute all phonetic features
- Calculate stage-specific scores
- Compare to real names where known

### Phase 3: Statistical Analysis (1 week)
- Train predictive models
- Run correlation analyses
- Test all hypotheses
- Cross-validate findings

### Phase 4: Documentation (1 week)
- Write findings report
- Create visualizations
- Prepare for integration
- Update platform

**Total Timeline:** 5-6 weeks from initiation to completion

---

## Files in This Framework

### Core
- `core/models.py` - Database models (lines 3863-4023)
- `collectors/adult_film_collector.py` - Data collection
- `analyzers/adult_film_statistical_analyzer.py` - Analysis

### Web
- `templates/adult_film.html` - Dashboard
- `templates/adult_film_findings.html` - Research page
- API endpoints in `app.py` (lines 4969-5068)

### Documentation
- `README.md` - This overview
- `METHODOLOGY.md` - Research design
- `ETHICAL_STATEMENT.md` - Justification
- `FINDINGS.md` - Results (after collection)
- `QUICKSTART.md` - Execution guide

---

## Contact & Collaboration

This research is part of the broader Nominative Determinism Research Platform examining how names predict outcomes across 18+ domains.

For questions about methodology or collaboration:
- See main project README
- Review ethical framework
- Consult existing domain analyses for comparable approaches

---

**Last Updated:** November 8, 2025  
**Framework Version:** 1.0  
**Status:** Ready for Data Collection

