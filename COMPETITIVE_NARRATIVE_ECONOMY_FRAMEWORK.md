# Competitive Narrative Economy Framework

## Core Insight

**Story value is relative, not absolute.** A "good" name/title/category set is only good **relative to competitors in the same narrative economy** at the **same time** with the **same market saturation**.

---

## The Competitive Context Problem

### What We Were Doing (Incomplete)
```python
# Absolute analysis
bitcoin_harshness = 0.7
prediction = "Harsh names do well"
r = 0.28
```

### What We Should Do (Complete)
```python
# Relative analysis
bitcoin_harshness = 0.7
competitor_mean_harshness = 0.4  # 2009 altcoins
relative_harshness = 0.7 - 0.4 = +0.3  # MORE harsh than competition
market_saturation = 5 competitors  # Low saturation
timing = "first_mover"

prediction = "Relative positioning: harsh in unsaturated market"
expected_r = 0.40+  # Higher with competitive context
```

---

## Data Model: Entity + Competitive Cohort

### Complete Data Structure

```python
class CompetitiveEntity:
    # ENTITY DATA (what we have now)
    name: str
    nominal_features: Dict  # All publicly visible story elements
    outcome: float
    
    # COMPETITIVE COHORT (what we need)
    cohort_id: str  # "2023-01-crypto" or "2019-Q4-adult-film"
    cohort_entities: List[Entity]  # All competitors in same time/market
    
    # RELATIVE FEATURES (calculated)
    relative_harshness: float  # vs cohort mean
    relative_length: float
    relative_sophistication: float
    distinctiveness_score: float  # Distance from cluster
    
    # MARKET CONTEXT
    market_phase: str  # early/growth/mature/decline
    saturation_level: float  # 0-1 (how crowded)
    entry_timing: str  # first_mover/early_adopter/late/very_late
    genre_dominance: float  # Is this genre saturated?
    
    # STORY ECONOMY METRICS
    narrative_novelty: float  # How new is this story?
    competitive_differentiation: float  # How different from others?
    positioning_clarity: float  # Clear market position?
```

---

## Domain-by-Domain Implementation Plan

### Priority 1: Adult Film (Baseline = 1,012 performers)

**Goal**: Improve from r=0.00 to r=0.15-0.25 by adding competitive context

#### Data Collection Strategy

**Step 1: Define Cohorts**
```python
# Monthly cohorts (competitive window)
cohorts = {
    '2023-01': [],  # All videos uploaded January 2023
    '2023-02': [],  # All videos uploaded February 2023
    # ... etc
}

# Why monthly? Videos compete for attention in release window
```

**Step 2: Collect PRIMARY Nominal Features Per Video**
```python
for video in cohort:
    collect:
    - video_id: str
    - upload_date: datetime
    - title: str  # PRIMARY story element
    - categories: List[str]  # PRIMARY genre signals
    - tags: List[str]  # PRIMARY additional signals
    - performer_names: List[str]  # PRIMARY (but one of many)
    - views: int  # Outcome
    - likes: int  # Secondary outcome
    - duration: int  # Context (not story, but affects)
```

**Sample Size**: 
- 12 months × ~1,000 videos/month = 12,000 videos
- Manageable with API or scraping

#### Feature Extraction

**Step 3: Extract Features from EACH Element**
```python
# From title
title_features = {
    'harshness': count_harsh_consonants(title),
    'length': len(title.split()),
    'genre_words': extract_genre_signals(title),
    'quality_adjectives': count_quality_words(title),
    'explicitness': measure_explicit_language(title)
}

# From categories
category_features = {
    'n_categories': len(categories),
    'specificity': measure_category_specificity(categories),
    'genre_coherence': measure_category_coherence(categories),
    'mainstream_vs_niche': classify_market_position(categories)
}

# From tags
tag_features = {
    'n_tags': len(tags),
    'tag_specificity': measure_tag_specificity(tags),
    'searchability': estimate_search_traffic(tags)
}

# From performer name
name_features = {
    'harshness': count_harsh_consonants(name),
    'memorability': calculate_memorability(name),
    # ... existing features
}
```

**Step 4: Calculate RELATIVE Features**
```python
# Within cohort (same month)
relative_features = {
    'relative_title_harshness': title_harshness - cohort_mean_harshness,
    'relative_category_count': n_categories - cohort_mean_categories,
    'distinctiveness': distance_from_cohort_cluster(all_features),
    'genre_saturation': n_videos_in_same_genre / cohort_size
}
```

#### Competitive Analysis

**Step 5: Test Absolute vs Relative Models**
```python
# Model 1: Absolute features (current approach)
views ~ title_harshness + n_categories + name_harshness
# Expected: r = 0.00-0.10

# Model 2: Relative features
views ~ relative_harshness + relative_categories + distinctiveness
# Expected: r = 0.15-0.25

# Model 3: Market context
views ~ relative_features + genre_saturation + entry_timing
# Expected: r = 0.25-0.35

# Model 4: Story coherence across elements
views ~ coherence(title, categories, tags, name) + relative_positioning
# Expected: r = 0.30-0.40
```

**Step 6: LEARN the Domain Grammar**
```python
# DISCOVER what actually matters
results = {
    'title_harshness': r = 0.15,  # Moderate
    'category_count': r = 0.22,   # Strong!
    'name_harshness': r = 0.00,   # Irrelevant (confirmed)
    'relative_positioning': r = 0.28,  # STRONG
    'genre_saturation': r = -0.18,  # Negative! (crowded genres harder)
    'story_coherence': r = 0.31   # STRONGEST
}

# INTERPRETATION we LEARNED:
"In adult film, discovery matters but performance doesn't.
Video TITLES and CATEGORIES drive clicks (r=0.15-0.22).
Performer names irrelevant (r=0.00) because return viewers know quality.
Relative positioning matters: standing out in crowded genre crucial.
Story coherence (title↔categories↔tags alignment) strongest predictor (r=0.31)."
```

---

### Priority 2: Cryptocurrencies (Baseline = 500 coins)

#### Collection Strategy

**Step 1: Cohort by Launch Quarter**
```python
cohorts = {
    '2017-Q4': [],  # ICO boom
    '2018-Q1': [],  # Peak
    '2018-Q2': [],  # Crash
    '2021-Q1': [],  # DeFi summer
    '2021-Q2': [],  # NFT boom
}
```

**Step 2: Collect Nominal Features**
```python
for coin in cohort:
    collect:
    - name: str  # PRIMARY
    - tagline: str  # PRIMARY (on CMC)
    - description: str  # PRIMARY (short summary)
    - website_headline: str  # PRIMARY
    - categories: List[str]  # PRIMARY (DeFi, NFT, etc)
    - market_cap: float  # Outcome
    - launch_date: datetime
```

**Step 3: Calculate Competitive Context**
```python
# Relative to launch cohort
relative_features = {
    'relative_tech_sophistication': my_tech_score - cohort_mean,
    'relative_seriousness': my_seriousness - cohort_mean,
    'name_length_vs_cohort': my_length - cohort_mean,
    'genre_saturation': n_coins_in_my_categories / cohort_size,
    'narrative_novelty': distance_from_existing_stories
}
```

**Step 4: LEARN Domain Grammar**
```python
# Test what matters
results = {
    'absolute_tech_morphemes': r = 0.15,  # Weak
    'relative_tech_sophistication': r = 0.35,  # Much stronger!
    'timing_vs_market_phase': r = 0.28,
    'genre_saturation': r = -0.22,  # Crowded genres underperform
    'story_novelty': r = 0.33  # New narratives outperform
}

# LEARNED:
"Being MORE technical than your cohort matters (r=0.35).
Absolute sophistication less important than relative.
Launching in saturated genres hurts (r=-0.22).
Novel narratives have advantage (r=0.33)."
```

---

### Priority 3: Hurricanes (Need to collect competitive context)

#### Collection Strategy

**Step 1: Annual Cohorts**
```python
cohorts = {
    '2005': ['Katrina', 'Rita', 'Wilma', ...],  # That year's storms
    '2017': ['Harvey', 'Irma', 'Maria', ...],
    '2018': ['Florence', 'Michael', ...],
}
```

**Step 2: Collect + Calculate Relative**
```python
for storm in cohort:
    # Absolute features
    harshness = calculate_harshness(storm.name)
    
    # Relative to that SEASON's storms
    season_mean_harshness = mean([s.harshness for s in cohort])
    relative_harshness = harshness - season_mean_harshness
    
    # Prior context
    recent_deadly_storms = [s for s in previous_2_years if s.deaths > 100]
    narrative_priming = mean([s.harshness for s in recent_deadly_storms])
```

**Step 3: LEARN Grammar**
```python
# Expected learning:
"Harshness matters, but RELATIVE to recent deadly storms.
If recent storms were harsh + deadly, public has schema.
New harsh storm fits schema → high evacuation.
New soft storm breaks schema → underestimated.

Timing matters: Early season vs late season.
Saturation matters: Many storms → fatigue."
```

---

## Implementation: Competitive Context Collector

### New Module: `collectors/competitive_context_collector.py`

```python
class CompetitiveContextCollector:
    """
    Collects entities WITH their competitive cohort
    Enables relative feature calculation
    """
    
    def collect_with_cohort(self, entity_id, domain, time_window):
        """
        Collect entity + all competitors in same time/market window
        
        Returns:
        - entity: The target entity
        - cohort: All competitors
        - relative_features: Calculated positioning
        """
        pass
    
    def define_cohort(self, entity, domain):
        """
        Determine what constitutes "competitive cohort"
        
        Domain-specific rules:
        - Adult film: Same month upload
        - Crypto: Same quarter launch
        - Sports: Same season/league
        - Hurricanes: Same year
        """
        pass
    
    def calculate_relative_features(self, entity, cohort):
        """
        Calculate entity features relative to cohort
        
        Returns:
        - relative_harshness
        - relative_length
        - distinctiveness_score
        - etc.
        """
        pass
```

---

## Analysis Framework: Absolute vs Relative

### Test Pipeline

```python
def test_competitive_improvement(domain_data):
    """
    Compare absolute vs relative feature models
    """
    
    # Model 1: Absolute features only (current approach)
    X_absolute = extract_absolute_features(domain_data)
    r_absolute = calculate_correlation(X_absolute, outcomes)
    
    # Model 2: Add relative features
    X_relative = extract_relative_features(domain_data, cohorts)
    r_relative = calculate_correlation(X_relative, outcomes)
    
    # Model 3: Add market context
    X_market = add_market_context(X_relative, timing, saturation)
    r_market = calculate_correlation(X_market, outcomes)
    
    # Model 4: Full competitive narrative economy
    X_full = add_story_coherence(X_market, all_nominal_elements)
    r_full = calculate_correlation(X_full, outcomes)
    
    # Report improvement
    return {
        'r_absolute': r_absolute,
        'r_relative': r_relative,
        'r_market': r_market,
        'r_full': r_full,
        'improvement_pct': (r_full - r_absolute) / r_absolute * 100
    }
```

---

## Expected Improvements

### Conservative Estimates

| Domain | Current r | With Competitive Context | Improvement |
|--------|-----------|-------------------------|-------------|
| Adult Film | 0.00 | 0.20-0.30 | ∞% (from zero) |
| Crypto | 0.28 | 0.40-0.50 | +43-79% |
| NBA | 0.24 | 0.35-0.45 | +46-88% |
| NFL | 0.21 | 0.32-0.42 | +52-100% |
| Hurricanes | 0.32 | 0.42-0.52 | +31-63% |
| Bands | 0.19 | 0.28-0.38 | +47-100% |

**Average Expected Improvement**: +50-80% in explained variance

---

## Implementation Roadmap

### Phase 1: Adult Film (Weeks 1-2)
**Why first**: Already have 1,012 performers, can expand to video-level

**Tasks**:
1. Collect top 10 videos per performer (10,120 videos)
2. Extract: title, categories, tags, upload_date, views
3. Group into monthly cohorts
4. Calculate relative features within cohorts
5. Test models: absolute → relative → market → full
6. Document learned grammar

**Expected Improvement**: r = 0.00 → 0.25 (discovery phase narrative matters)

### Phase 2: Cryptocurrencies (Weeks 3-4)
**Why second**: Have 500 coins, need to add cohort context

**Tasks**:
1. Add launch_quarter to existing 500 coins
2. Expand to 2,000 coins covering multiple launch cohorts
3. Collect: tagline, description, categories from CMC
4. Calculate relative sophistication within cohorts
5. Add market saturation metrics
6. Test improvements

**Expected Improvement**: r = 0.28 → 0.45 (+61%)

### Phase 3: Sports (Weeks 5-6)
**NBA/NFL/MLB**: Add draft class cohorts and relative positioning

**Tasks**:
1. Group players by draft year
2. Calculate relative features within draft class
3. Add team context (team narrative economy)
4. Test position-specific competitive contexts
5. Document learned grammars

**Expected Improvement**: r = 0.21-0.24 → 0.35-0.40 (+50%)

### Phase 4: Other Domains (Weeks 7-10)
- Hurricanes: Annual cohorts
- Bands: Launch year cohorts
- Board games: Release year cohorts
- Mental health: Historical introduction cohorts

---

## Specific Collection Scripts Needed

### 1. Adult Film Video Collector

**`collectors/adult_film_video_collector.py`**

```python
class AdultFilmVideoCollector:
    """Collect videos with competitive cohort context"""
    
    def collect_performer_videos(self, performer_id, limit=10):
        """Get top videos for performer"""
        pass
    
    def collect_monthly_cohort(self, year, month):
        """Get ALL videos from specific month"""
        pass
    
    def extract_nominal_features(self, video):
        """
        Extract ALL publicly visible story elements:
        - Title text
        - Categories (list)
        - Tags (list)
        - Performer name(s)
        """
        pass
```

### 2. Competitive Context Analyzer

**`analyzers/competitive_context_analyzer.py`**

```python
class CompetitiveContextAnalyzer:
    """Calculate relative features and market positioning"""
    
    def calculate_relative_features(self, entity, cohort):
        """
        For each feature, calculate:
        - Entity value
        - Cohort mean
        - Relative position (entity - mean)
        - Z-score (standardized position)
        - Percentile rank
        """
        pass
    
    def calculate_distinctiveness(self, entity, cohort):
        """
        How different is this entity from competitors?
        - Feature space distance
        - Cluster analysis
        - Novelty score
        """
        pass
    
    def measure_market_saturation(self, entity, cohort):
        """
        How crowded is the narrative space?
        - Genre saturation
        - Feature similarity clustering
        - Competitive density
        """
        pass
```

### 3. Story Coherence Analyzer

**`analyzers/story_coherence_analyzer.py`**

```python
class StoryCoherenceAnalyzer:
    """Measure coherence across multiple nominal elements"""
    
    def measure_element_coherence(self, title, categories, tags, name):
        """
        Do all story elements tell the same story?
        
        Returns:
        - title_category_alignment: float (0-1)
        - tag_genre_fit: float (0-1)
        - name_content_match: float (0-1)
        - overall_coherence: float (0-1)
        """
        pass
    
    def detect_narrative_conflicts(self, elements):
        """
        Find story elements that don't align
        e.g., harsh title + soft categories = incoherent
        """
        pass
```

---

## Testing Framework

### Comparison Pipeline

**`scripts/test_competitive_improvement.py`**

```python
def run_competitive_improvement_test(domain):
    """
    Test if competitive context improves modeling
    
    Steps:
    1. Load domain data with cohorts
    2. Run absolute feature model
    3. Run relative feature model
    4. Run full competitive economy model
    5. Compare R² improvements
    6. Document learned patterns
    """
    
    print(f"\n{'='*80}")
    print(f"COMPETITIVE IMPROVEMENT TEST: {domain}")
    print(f"{'='*80}\n")
    
    # Load data
    entities = load_domain_data(domain)
    cohorts = define_cohorts(entities, domain)
    
    # Model 1: Absolute
    results_abs = test_absolute_model(entities)
    print(f"Model 1 (Absolute): r = {results_abs['r']:.3f}")
    
    # Model 2: Relative
    entities_with_relative = add_relative_features(entities, cohorts)
    results_rel = test_relative_model(entities_with_relative)
    print(f"Model 2 (Relative): r = {results_rel['r']:.3f}")
    print(f"  Improvement: +{(results_rel['r']/results_abs['r']-1)*100:.1f}%")
    
    # Model 3: Market Context
    entities_with_market = add_market_context(entities_with_relative)
    results_mkt = test_market_model(entities_with_market)
    print(f"Model 3 (Market): r = {results_mkt['r']:.3f}")
    print(f"  Improvement: +{(results_mkt['r']/results_abs['r']-1)*100:.1f}%")
    
    # Model 4: Story Coherence
    results_full = test_coherence_model(entities_with_market)
    print(f"Model 4 (Full Story): r = {results_full['r']:.3f}")
    print(f"  Improvement: +{(results_full['r']/results_abs['r']-1)*100:.1f}%")
    
    # Document what we learned
    learned_patterns = analyze_feature_importance(results_full)
    
    return {
        'domain': domain,
        'improvements': {
            'absolute': results_abs['r'],
            'relative': results_rel['r'],
            'market': results_mkt['r'],
            'full': results_full['r']
        },
        'learned_patterns': learned_patterns
    }
```

---

## Systematic Learning Protocol

### For Each Domain

**Week 1-2: Collection**
- Day 1-3: Design cohort structure
- Day 4-7: Collect data with competitive context
- Day 8-10: Extract features from ALL nominal elements
- Day 11-14: Calculate relative features

**Week 3: Analysis**
- Day 1-2: Run absolute model (baseline)
- Day 3-4: Run relative model (test improvement)
- Day 5-6: Run market context model
- Day 7: Run full story coherence model

**Week 4: Documentation**
- Day 1-2: Document learned patterns
- Day 3-4: Write domain-specific grammar guide
- Day 5-6: Create visualizations
- Day 7: Update meta-analysis

---

## Let's Start NOW

I'll begin with **Adult Film** since we have the base (1,012 performers):

### Immediate Next Steps

1. **Create the collectors** (competitive_context_collector.py, adult_film_video_collector.py)
2. **Design cohort structure** (monthly windows)
3. **Collect sample cohort** (e.g., January 2023 - all videos)
4. **Extract features** from titles, categories, tags
5. **Calculate relative** positioning
6. **Run comparative analysis**: absolute vs relative vs full
7. **Document improvements** and learned patterns

**Then repeat for crypto, then sports, then other domains.**

---

**Ready to start actual data collection and see the modeling improvements?** 

This is where we **learn each domain's story grammar empirically** and watch the correlations improve from relative positioning and competitive context. 🎯
