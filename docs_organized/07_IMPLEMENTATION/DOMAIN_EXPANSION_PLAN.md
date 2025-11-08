# 🚀 Domain Expansion Plan - Add 10+ New Research Areas

## Overview

Expand the Formula Evolution Engine to test nominative determinism across **20+ total domains** by collecting, analyzing, and integrating new research areas with full automation.

---

## 🎯 NEW DOMAINS TO ADD (Priority Order)

### Tier 1: High Value, Easy to Collect (Add First)

**1. YouTube Channels** (Target: 1,000+)
- **Data Source:** YouTube Data API (free)
- **Outcome:** Subscriber count, views
- **Collection Time:** 2-3 hours
- **Why:** Huge sample, modern naming conventions, clear success metrics
- **Hypothesis:** Do memorable/short names get more subscribers?

**2. Startup Companies** (Target: 500+)
- **Data Source:** Crunchbase API (free tier)
- **Outcome:** Funding raised, valuation
- **Collection Time:** 1-2 hours
- **Why:** Business naming is intentional, high-stakes
- **Hypothesis:** Do "innovative" visual patterns predict funding?

**3. Podcast Names** (Target: 500+)
- **Data Source:** Apple Podcasts API, Spotify
- **Outcome:** Downloads, ratings
- **Collection Time:** 2-3 hours
- **Why:** Recent phenomenon, diverse naming styles
- **Hypothesis:** Do conversational names perform better?

**4. Video Games** (Target: 1,000+)
- **Data Source:** IGDB API, Steam API (free)
- **Outcome:** Sales, ratings, player count
- **Collection Time:** 2-3 hours
- **Why:** Large dataset, clear success metrics
- **Hypothesis:** Do fantasy/complex names predict game quality?

**5. CEOs/Business Leaders** (Target: 500+)
- **Data Source:** Fortune 500, Forbes lists (public data)
- **Outcome:** Company performance, tenure
- **Collection Time:** 1-2 hours
- **Why:** Classic nominative determinism domain
- **Hypothesis:** Do "authoritative" names predict CEO success?

---

### Tier 2: Medium Value, Moderate Effort

**6. Tennis Players** (Target: 500+)
- **Data Source:** ATP/WTA rankings (public)
- **Outcome:** Career titles, ranking
- **Collection Time:** 2-3 hours
- **Why:** Individual sport, clear metrics
- **Hypothesis:** Do "elegant" names predict tennis success?

**7. Soccer Players** (Target: 1,000+)
- **Data Source:** FIFA rankings, transfer market
- **Outcome:** Goals, market value
- **Collection Time:** 3-4 hours
- **Why:** Global sport, huge dataset
- **Hypothesis:** Cultural naming patterns?

**8. Musicians/Artists** (Target: 500+)
- **Data Source:** Spotify API, Last.fm
- **Outcome:** Monthly listeners, streams
- **Collection Time:** 2-3 hours
- **Why:** Stage names are intentional experiments
- **Hypothesis:** Do stage names outperform birth names?

**9. Authors/Writers** (Target: 500+)
- **Data Source:** Goodreads API, bestseller lists
- **Outcome:** Book sales, ratings
- **Collection Time:** 2-3 hours
- **Why:** Pen names common, literary tradition
- **Hypothesis:** Do pen names have patterns?

**10. Scientists/Researchers** (Target: 500+)
- **Data Source:** Google Scholar, arXiv
- **Outcome:** Citations, h-index, awards
- **Collection Time:** 3-4 hours
- **Why:** Nobel Prize, Fields Medal data available
- **Hypothesis:** Do "intellectual" names predict achievement?

---

### Tier 3: Novel/Experimental

**11. Restaurant Names** (Target: 500+)
- **Outcome:** Michelin stars, Yelp ratings
- **Hypothesis:** Do certain name patterns predict culinary success?

**12. Dog Breeds** (Target: 100+)
- **Outcome:** AKC popularity rankings
- **Hypothesis:** Do breed names predict popularity?

**13. Paint Colors** (Target: 500+)
- **Outcome:** Sales data from manufacturers
- **Hypothesis:** Do color names affect purchasing?

**14. Pharmaceutical Drugs** (Target: 500+)
- **Outcome:** Sales, prescription rates
- **Hypothesis:** Do friendlier names sell better?

**15. Cities/Countries** (Target: 200+)
- **Outcome:** GDP, population growth, tourism
- **Hypothesis:** Do geographic names predict prosperity?

---

## 🤖 AUTOMATED COLLECTION SYSTEM

### Master Collection Script

**File:** `scripts/domain_expansion_manager.py`

```python
class DomainExpansionManager:
    """Manages automated collection of new research domains"""
    
    def collect_all_tier1(self):
        """Collect all Tier 1 domains in sequence"""
        # YouTube Channels
        # Startups
        # Podcasts
        # Video Games
        # CEOs
    
    def run_parallel_collection(self, domains):
        """Collect multiple domains in parallel"""
        # Uses multiprocessing
        # Respects rate limits
        # Progress tracking
    
    def analyze_on_collect(self, domain):
        """Analyze immediately after collection"""
        # Run linguistic analysis
        # Integrate with formula system
        # Update statistics
```

**Features:**
- Rate limit respect
- Error recovery
- Progress tracking
- Automatic retries
- Result validation

---

## 📊 COLLECTION SCRIPTS (One Per Domain)

### Template Structure

**File:** `collectors/youtube_collector.py`

```python
class YouTubeChannelCollector:
    """Collects YouTube channel data"""
    
    def __init__(self):
        self.api_key = os.getenv('YOUTUBE_API_KEY')
        self.rate_limiter = RateLimiter(calls=10000, period=86400)
    
    def collect_channels(self, target_count=1000):
        """Collect top channels by category"""
        # Categories: Gaming, Education, Entertainment, etc.
        # Use YouTube Data API v3
        # Collect: name, subscribers, views, uploads
    
    def analyze_collected(self):
        """Run linguistic analysis on collected channels"""
        # Use NameAnalyzer
        # Store in YouTubeChannel + YouTubeChannelAnalysis tables
    
    def integrate_with_formulas(self):
        """Make available to formula system"""
        # Create YouTubeChannelLoader
        # Add to ExtendedDomainType
```

**Similar scripts for:**
- `collectors/startup_collector.py`
- `collectors/podcast_collector.py`
- `collectors/video_game_collector.py`
- `collectors/ceo_collector.py`
- (And 10 more)

---

## 🗄️ DATABASE MODELS (Add to models.py)

### YouTube Channels

```python
class YouTubeChannel(db.Model):
    __tablename__ = 'youtube_channels'
    
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    channel_url = db.Column(db.String(200))
    
    # Metrics (outcomes)
    subscriber_count = db.Column(db.Integer)
    total_views = db.Column(db.BigInteger)
    video_count = db.Column(db.Integer)
    
    # Categorization
    category = db.Column(db.String(50))
    created_year = db.Column(db.Integer)
    
    # Success indicators
    verified = db.Column(db.Boolean)
    monetized = db.Column(db.Boolean)
    
    collected_date = db.Column(db.DateTime)


class YouTubeChannelAnalysis(db.Model):
    __tablename__ = 'youtube_channel_analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    channel_id = db.Column(db.String(50), db.ForeignKey('youtube_channels.id'))
    
    # Standard linguistic features
    syllable_count = db.Column(db.Integer)
    character_length = db.Column(db.Integer)
    word_count = db.Column(db.Integer)
    
    # Phonetic
    harshness_score = db.Column(db.Float)
    memorability_score = db.Column(db.Float)
    pronounceability_score = db.Column(db.Float)
    
    # Semantic
    name_type = db.Column(db.String(50))
    brandability_score = db.Column(db.Float)
    uniqueness_score = db.Column(db.Float)
    
    analyzed_date = db.Column(db.DateTime)
```

**Similar models for:**
- Startup, StartupAnalysis
- Podcast, PodcastAnalysis
- VideoGame, VideoGameAnalysis
- CEO, CEOAnalysis
- (And 10 more pairs)

---

## 🎨 WEB PAGES (One Per Domain)

### Template Structure

**File:** `templates/youtube_analysis.html`

**Features:**
- Domain-specific dashboard
- Top performers by name pattern
- Visual correlation charts
- Name-outcome scatter plots
- Formula comparison
- Export functionality

**Similar pages for:**
- `/startups`
- `/podcasts`
- `/video-games`
- `/ceos`
- (And 10 more)

---

## 📊 VISUAL INTEGRATION

### Update Formula Explorer

**Add domain selector:**
```html
<select id="domainSelect">
  <!-- Existing -->
  <option value="crypto">Cryptocurrency (65K)</option>
  <option value="mtg_card">MTG Cards (4K)</option>
  
  <!-- NEW -->
  <option value="youtube">YouTube Channels (1K)</option>
  <option value="startup">Startups (500)</option>
  <option value="podcast">Podcasts (500)</option>
  <option value="video_game">Video Games (1K)</option>
  <option value="ceo">CEOs (500)</option>
  <option value="tennis">Tennis Players (500)</option>
  <option value="soccer">Soccer Players (1K)</option>
  <option value="musician">Musicians (500)</option>
  <option value="author">Authors (500)</option>
  <option value="scientist">Scientists (500)</option>
</select>
```

### Master Dashboard

**File:** `templates/domain_overview.html`

**Features:**
- Grid of all 20+ domains
- Entity counts
- Best correlations
- Collection status
- "Add New Domain" button

---

## 🔄 BACKGROUND COLLECTION WORKFLOW

### Automated Pipeline

**1. Schedule Collection Jobs:**
```yaml
# config/domain_expansion.yaml

collection_schedule:
  youtube_channels:
    enabled: true
    frequency: "weekly"
    day: "Monday"
    time: "01:00"
    target_count: 1000
  
  startups:
    enabled: true
    frequency: "monthly"
    day: 1
    time: "02:00"
    target_count: 500
  
  # ... (all domains)
```

**2. Collection Script:**
```bash
# Runs automatically
python3 scripts/collect_domain.py --domain youtube --target 1000
```

**3. Immediate Analysis:**
```bash
# Automatically triggered after collection
python3 scripts/analyze_domain.py --domain youtube
```

**4. Formula Integration:**
```bash
# Automatically integrates new domain into formula tests
python3 scripts/auto_analyze_formulas.py --mode on-demand --domain youtube
```

---

## 📈 GROWTH TRAJECTORY

### Month 1:
- Existing: 72,300 entities (10 domains)
- Add Tier 1: +4,000 entities (5 domains)
- **Total: 76,300 entities across 15 domains**

### Month 2:
- Add Tier 2: +4,000 entities (5 domains)
- **Total: 80,300 entities across 20 domains**

### Month 3:
- Add Tier 3: +2,000 entities (5 domains)
- **Total: 82,300 entities across 25 domains**

**By Month 3: 82K+ entities across 25 research domains = Most comprehensive nominative determinism study ever conducted.**

---

## 🎯 IMMEDIATE IMPLEMENTATION

I'll now create the complete infrastructure for domain expansion with:

1. **Master expansion manager** (schedules & coordinates)
2. **5 Tier 1 collection scripts** (YouTube, Startups, Podcasts, Games, CEOs)
3. **Database models** for all new domains
4. **Web pages** for each domain
5. **Automatic integration** with formula system
6. **Background scheduling** for continuous expansion
7. **Visual dashboards** showing all domains
8. **Written reports** for each domain

This will run in background collecting new domains while your existing system continues analyzing.

**Ready to implement all of this?**

This is a large implementation (~5,000 more lines of code). Shall I proceed with complete build-out?

