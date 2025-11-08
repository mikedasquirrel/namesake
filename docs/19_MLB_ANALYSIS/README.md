# MLB Player Name Analysis

**Domain:** Major League Baseball (MLB)  
**Status:** Framework complete, data collection pending  
**Target Sample:** 2,500-3,000 players  
**Innovation:** First comprehensive position/power/pitcher name analysis in baseball

---

## Research Questions

1. **Position Prediction:** Can name phonetics predict positions (P/C/IF/OF)?
2. **Pitcher Analysis:** Do pitchers have distinct naming patterns (SP vs RP vs CL)?
3. **Power Names:** Do HR leaders have harsher names?
4. **Temporal Evolution:** How have naming conventions changed 1950s-2024?
5. **Internationalization:** Impact of Latino/Asian players post-1990?

---

## Key Hypotheses

### H1: The Pitcher Mystique
**Prediction:** Pitchers have longer names (+0.8 syllables, d=0.35)  
**Rationale:** Professional specialization creates naming formality

### H2: Power Name Hypothesis
**Prediction:** HR leaders +12 harshness points vs contact hitters (r=0.25)  
**Mechanism:** Sound symbolism—harsh names for power players

### H3: Position Prediction
**Prediction:** 60-65% accuracy (matching NBA 68%, NFL success)  
**Method:** Random Forest on phonetic features

### H4: Latino Inflection (1990s)
**Prediction:** Post-1990 names +2.2 syllables (internationalization)  
**Context:** Martinez, Hernandez, Rodriguez, Suzuki, Ohtani pattern

### H5: The Closer Effect
**Prediction:** Closers -0.6 syllables vs starters  
**Psychology:** 9th inning tension demands memorability

---

## Infrastructure

### Database Models
- **MLBPlayer:** Player data, stats, achievements
- **MLBPlayerAnalysis:** Phonetic/linguistic features

### Data Collection
- **File:** `collectors/mlb_collector.py`
- **Source:** Baseball Reference
- **Strategy:** Stratified by position (800 P, 200 C, 800 IF, 600 OF, 100 DH)

### Statistical Analysis
- **File:** `analyzers/mlb_statistical_analyzer.py`
- **Analyses:** 6 modules (position, pitcher, power, temporal, international, closer)

### Web Interface
- **Dashboard:** `/mlb`
- **Findings:** `/mlb/findings`
- **APIs:** `/api/mlb/stats`, `/position-analysis`, `/pitcher-analysis`, `/power-analysis`, `/temporal`

---

## Expected Discoveries

1. **Pitcher Mystique:** +0.8 syllables, professional formality
2. **Power Sound Symbolism:** Harsh names for HR leaders
3. **Closer Brevity:** Shorter names for save situations
4. **Latino Expansion:** +2.2 syllables post-1990
5. **Position Accuracy:** 62-65% prediction from names

---

**Status:** ✅ Framework complete, ready for data  
**Priority:** High  
**Innovation Rating:** 2/3

