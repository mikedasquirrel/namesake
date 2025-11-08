# Domain Analysis Template System - Comprehensive Guide

**Author:** Michael Smerconish  
**Date:** November 2025  
**Version:** 1.0

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [System Architecture](#system-architecture)
4. [Usage Examples](#usage-examples)
5. [Creating New Domains](#creating-new-domains)
6. [API Reference](#api-reference)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

---

## Overview

The Domain Analysis Template System provides a production-ready framework for conducting nominative determinism research across multiple domains. It eliminates repetitive setup, ensures consistent methodology, and enables rapid domain expansion.

### Key Benefits

- **No Repetition**: Research framework automatically inherited—never explain project mission again
- **Fast Domain Addition**: New domain scaffolded in <30 minutes
- **Consistent Quality**: All analyses follow same statistical rigor automatically
- **Auto Page Updates**: Findings pages update automatically when analysis completes
- **Progress Visibility**: Clear progress tracking for all background tasks
- **Unified API**: Generic endpoints work for any registered domain

### Core Components

1. **Research Framework** (`core/research_framework.py`): Single source of truth for methodology
2. **Domain Analysis Template** (`core/domain_analysis_template.py`): Abstract base class with standardized pipeline
3. **Progress Tracker** (`utils/progress_tracker.py`): Reusable progress tracking utility
4. **Domain Configs** (`core/domain_configs/*.yaml`): Configuration files for each domain
5. **Unified Runner** (`scripts/run_domain_analysis.py`): CLI for running any domain
6. **Template Generator** (`scripts/generate_domain_template.py`): Scaffolding generator
7. **Background Analyzer** (`utils/background_analyzer.py`): Multi-domain computation support
8. **Generic APIs** (`app.py`): Domain-agnostic endpoints

---

## Quick Start

### Running Existing Domain Analysis

```bash
# Activate virtual environment
cd /Users/michaelsmerconish/Desktop/RandomCode/FlaskProject
source .venv/bin/activate

# Run NFL analysis with fresh data collection
python scripts/run_domain_analysis.py --domain nfl --mode new

# Re-analyze immigration data (use existing data)
python scripts/run_domain_analysis.py --domain immigration --mode reanalyze

# Run multiple domains sequentially
python scripts/run_domain_analysis.py --domains nfl,nba,bands --mode update

# All active domains
python scripts/run_domain_analysis.py --all --mode update
```

### Creating New Domain

```bash
# Generate complete scaffolding
python scripts/generate_domain_template.py --domain soccer --create-all

# Generate specific files only
python scripts/generate_domain_template.py --domain soccer --create-config
python scripts/generate_domain_template.py --domain soccer --create-collector
```

### Accessing Results via API

```bash
# List all domains
curl http://localhost:5000/api/domains/list

# Get domain info
curl http://localhost:5000/api/domain/nfl/info

# Get domain statistics
curl http://localhost:5000/api/domain/nfl/stats

# Get domain findings
curl http://localhost:5000/api/domain/nfl/findings

# Recompute domain analysis
curl -X POST http://localhost:5000/api/admin/recompute-domain/nfl
```

---

## System Architecture

### Component Hierarchy

```
Research Framework (core/research_framework.py)
    ├── Mission & Theoretical Framework
    ├── Statistical Methodology (23 methods)
    ├── Quality Standards
    └── Domain Registry (11+ domains)
           │
           ├─→ Domain Configs (core/domain_configs/*.yaml)
           │      └─→ Collector & Analyzer Classes
           │
           └─→ Domain Analysis Template (core/domain_analysis_template.py)
                  ├── collect_data() [abstract]
                  ├── analyze_data() [abstract]
                  ├── validate_results()
                  ├── generate_findings()
                  └── update_page_data()
```

### Data Flow

```
User Command (CLI or API)
    ↓
Unified Runner / Background Analyzer
    ↓
Load Domain Config (YAML)
    ↓
Instantiate Collector & Analyzer
    ↓
Run Full Pipeline:
    1. Data Collection (with progress tracking)
    2. Statistical Analysis
    3. Quality Validation
    4. Findings Generation
    5. Database Storage (PreComputedStats)
    ↓
API Endpoints Serve Results (instant <100ms)
    ↓
Web Pages Display Findings
```

---

## Usage Examples

### Example 1: Analyzing NFL Player Data

```bash
# Step 1: Run data collection and analysis
python scripts/run_domain_analysis.py --domain nfl --mode new --sample-size 1000

# Output:
# ================================================================================
# RUNNING DOMAIN ANALYSIS: NFL
# ================================================================================
# 
# ================================================================================
# NFL PLAYER PERFORMANCE & POSITION ANALYSIS
# ================================================================================
# Domain ID: nfl
# Mode: new
# Research Questions: 3
#   1. Do phonetic features predict playing position?
#   2. Does name complexity correlate with QB performance metrics?
#   3. Are there temporal shifts in naming conventions?
# Target Sample Size: 1,000
# ================================================================================
# 
# [2025-11-08 14:30:00] ============================================================
# [2025-11-08 14:30:00] NFL DATA COLLECTION
# [2025-11-08 14:30:00] ============================================================
# [2025-11-08 14:30:00] Started: 2025-11-08 14:30:00
# [2025-11-08 14:30:00] Total Steps: 1,000
# [2025-11-08 14:30:00] Progress Updates: Every 50 steps
# [2025-11-08 14:30:00] ============================================================
# 
# [2025-11-08 14:30:10] Progress: 50/1,000 (5.0%) | ETA: 3m 10s | Elapsed: 10.0s | Collected: 50, Updated: 0
# ...
```

### Example 2: Re-analyzing Immigration Data

```bash
# Run analysis on existing data without re-collecting
python scripts/run_domain_analysis.py --domain immigration --mode reanalyze

# This loads existing data from database and runs statistical analysis
# Useful after updating analysis methods or adding new tests
```

### Example 3: Creating New Domain (Soccer)

```bash
# Generate all scaffolding
python scripts/generate_domain_template.py \
    --domain soccer \
    --display-name "Soccer Player Position Analysis" \
    --target-sample-size 2000 \
    --stratification \
    --temporal \
    --create-all

# Output:
# ================================================================================
# DOMAIN TEMPLATE GENERATOR
# ================================================================================
# Domain: soccer
# Display Name: Soccer Player Position Analysis
# Target Sample Size: 2,000
# ================================================================================
# 
# Creating: core/domain_configs/soccer.yaml
# ✓ Config created
# 
# Creating: collectors/soccer_collector.py
# ✓ Collector created
# 
# Creating: analyzers/soccer_statistical_analyzer.py
# ✓ Analyzer created
# 
# Creating: scripts/collect_soccer_comprehensive.py
# ✓ Runner script created
# 
# Creating: templates/soccer.html
# ✓ HTML template created
# 
# Generating model code: soccer_models.py
# ✓ Model code generated
#   → Copy classes from soccer_models.py to core/models.py
# 
# ================================================================================
# SCAFFOLDING COMPLETE
# ================================================================================
# 
# Next steps:
# 1. Review and customize generated files
# 2. Add model classes to core/models.py
# 3. Update research_framework.py to register domain
# 4. Implement data collection logic in collector
# 5. Implement statistical analysis in analyzer
# 6. Run: python scripts/run_domain_analysis.py --domain soccer --mode new
```

### Example 4: Batch Processing Multiple Domains

```bash
# Update all domains with latest data
python scripts/run_domain_analysis.py --all --mode update --output results.json

# This will:
# - Run data collection for each domain
# - Perform comprehensive statistical analysis
# - Store results in PreComputedStats
# - Save summary to results.json
```

### Example 5: Using Progress Tracker in Custom Code

```python
from utils.progress_tracker import ProgressTracker

# Single task
tracker = ProgressTracker(
    total_steps=1000,
    print_interval=50,
    task_name="Data Processing",
    show_eta=True
)

for i in range(1000):
    # Do work
    process_record(i)
    tracker.update(1, message=f"Processing record {i}")

tracker.complete("All records processed successfully")

# Multi-task
from utils.progress_tracker import MultiTaskProgressTracker

multi_tracker = MultiTaskProgressTracker(
    task_names=["Collection", "Analysis", "Validation"],
    task_weights=[0.4, 0.5, 0.1]
)

# Update each task
multi_tracker.update_task(0, 50.0, "Collected 500/1000 records")
multi_tracker.update_task(1, 75.0, "Running regression models")
multi_tracker.update_task(2, 100.0, "Validation complete")

multi_tracker.complete()
```

### Example 6: API Integration

```python
import requests

# Get all domains
response = requests.get('http://localhost:5000/api/domains/list')
domains = response.json()['domains']

# Get NFL domain info
response = requests.get('http://localhost:5000/api/domain/nfl/info')
nfl_info = response.json()
print(f"Research Questions: {nfl_info['research_questions']}")

# Get pre-computed statistics
response = requests.get('http://localhost:5000/api/domain/nfl/stats')
stats = response.json()
print(f"Sample Size: {stats['sample_size']}")

# Trigger recomputation
response = requests.post('http://localhost:5000/api/admin/recompute-domain/nfl')
result = response.json()
print(f"Status: {result['success']}")
print(f"Duration: {result['duration']:.1f}s")
```

---

## Creating New Domains

### Step-by-Step Process

#### 1. Generate Scaffolding

```bash
python scripts/generate_domain_template.py \
    --domain tennis \
    --display-name "Tennis Player Name Analysis" \
    --target-sample-size 1500 \
    --temporal \
    --create-all
```

#### 2. Register Domain in Framework

Edit `core/research_framework.py` and add to `_initialize_domain_registry()`:

```python
"tennis": DomainMetadata(
    domain_id="tennis",
    display_name="Tennis Player Name Analysis",
    research_questions=[
        "Do phonetic features predict Grand Slam wins?",
        "Does name memorability correlate with endorsement value?",
        "Are there geographic naming patterns?"
    ],
    sample_size_target=1500,
    effect_strength_expected="moderate",
    primary_outcome_variable="grand_slam_count",
    key_predictors=["syllables", "phonetic_features", "name_origin"],
    control_variables=["world_rank", "career_length"],
    temporal_component=True,
    status="planned",
    innovation_rating=2
)
```

#### 3. Add Database Models

Copy model classes from `tennis_models.py` to `core/models.py`:

```python
class TennisPlayer(db.Model):
    """Tennis player data model"""
    __tablename__ = 'tennis_records'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    grand_slam_count = db.Column(db.Integer)
    world_rank = db.Column(db.Integer)
    # ... add more fields
    
    analysis = db.relationship('TennisPlayerAnalysis', backref='tennis_record', 
                              uselist=False, cascade='all, delete-orphan')

class TennisPlayerAnalysis(db.Model):
    """Tennis player linguistic analysis"""
    __tablename__ = 'tennis_analysis'
    
    id = db.Column(db.Integer, primary_key=True)
    record_id = db.Column(db.Integer, db.ForeignKey('tennis_records.id'), 
                         nullable=False, unique=True)
    syllable_count = db.Column(db.Integer)
    # ... add analysis fields
```

#### 4. Implement Collector Logic

Edit `collectors/tennis_collector.py`:

```python
def _fetch_record(self, index: int) -> Dict:
    """Fetch tennis player data from ATP/WTA API"""
    response = requests.get(f'{API_BASE_URL}/players/{index}')
    data = response.json()
    
    return {
        'name': data['name'],
        'grand_slam_count': data['grand_slams'],
        'world_rank': data['rank'],
        # ... extract fields
    }
```

#### 5. Implement Analyzer Logic

Edit `analyzers/tennis_statistical_analyzer.py`:

```python
def _load_data(self) -> pd.DataFrame:
    """Load tennis player data"""
    records = TennisPlayer.query.all()
    
    data = []
    for record in records:
        if record.analysis:
            data.append({
                'name': record.name,
                'grand_slams': record.grand_slam_count,
                'syllables': record.analysis.syllable_count,
                'phonetic_score': record.analysis.phonetic_score,
                # ... add fields
            })
    
    return pd.DataFrame(data)

def _compute_correlations(self, df: pd.DataFrame) -> Dict:
    """Compute correlations between name features and performance"""
    correlations = {}
    
    predictors = ['syllables', 'phonetic_score', 'memorability']
    outcome = 'grand_slams'
    
    for predictor in predictors:
        r, p = stats.pearsonr(df[predictor], df[outcome])
        correlations[predictor] = {
            'correlation': float(r),
            'p_value': float(p),
            'significant': bool(p < 0.05),
            'effect_size': self.framework.interpret_effect_size(r, 'correlation')
        }
    
    return correlations
```

#### 6. Customize Configuration

Edit `core/domain_configs/tennis.yaml` with specific parameters:

```yaml
collector_params:
  source: "atp_wta_api"
  api_key: "${TENNIS_API_KEY}"
  rate_limit_seconds: 1.0

stratification:
  enabled: true
  field: gender
  targets:
    male: 750
    female: 750
```

#### 7. Run Analysis

```bash
# Create database tables (if needed)
python -c "from app import app, db; app.app_context().push(); db.create_all()"

# Run collection and analysis
python scripts/run_domain_analysis.py --domain tennis --mode new

# Verify results
curl http://localhost:5000/api/domain/tennis/stats
```

---

## API Reference

### Domain Information

#### GET `/api/domains/list`

List all registered domains.

**Response:**
```json
{
  "total_domains": 11,
  "domains": [
    {
      "domain_id": "hurricanes",
      "display_name": "Hurricane Nomenclature & Casualty Prediction",
      "status": "complete",
      "innovation_rating": 3,
      "sample_size_target": 236,
      "research_questions": ["..."],
      "temporal_component": true,
      "geographic_component": true
    }
  ],
  "framework_summary": "..."
}
```

#### GET `/api/domain/<domain_id>/info`

Get domain metadata and configuration.

**Parameters:**
- `domain_id`: Domain identifier (e.g., "nfl", "nba")

**Response:**
```json
{
  "domain_id": "nfl",
  "display_name": "NFL Player Performance & Position Analysis",
  "research_questions": ["..."],
  "sample_size_target": 1000,
  "effect_strength_expected": "moderate",
  "primary_outcome_variable": "position",
  "key_predictors": ["syllables", "phonetic_strength"],
  "control_variables": ["draft_round", "draft_year"],
  "status": "active",
  "innovation_rating": 2
}
```

#### GET `/api/domain/<domain_id>/stats`

Get pre-computed statistics (instant <100ms if cached).

**Parameters:**
- `domain_id`: Domain identifier

**Response:**
```json
{
  "domain_id": "nfl",
  "sample_size": 987,
  "descriptive_stats": {},
  "correlations": {},
  "regressions": {},
  "precomputed": true,
  "computed_at": "2025-11-08T14:30:00",
  "computation_duration": 45.2
}
```

#### GET `/api/domain/<domain_id>/findings`

Get formatted findings text.

**Parameters:**
- `domain_id`: Domain identifier

**Response:**
```json
{
  "domain_id": "nfl",
  "display_name": "NFL Player Performance & Position Analysis",
  "findings_text": "================================================================================\nNFL Player Performance & Position Analysis - Key Findings\n...",
  "analysis_summary": {
    "sample_size": 987,
    "timestamp": "2025-11-08T14:30:00"
  },
  "computed_at": "2025-11-08T14:30:00"
}
```

### Administration

#### POST `/api/admin/recompute-domain/<domain_id>`

Trigger recomputation for specific domain.

**Parameters:**
- `domain_id`: Domain identifier

**Response:**
```json
{
  "success": true,
  "domain_id": "nfl",
  "display_name": "NFL Player Performance & Position Analysis",
  "message": "Analysis recomputed for NFL Player Performance & Position Analysis",
  "duration": 45.2,
  "sample_size": 987
}
```

#### POST `/api/admin/recompute-all`

Trigger recomputation for ALL domains (crypto legacy method).

**Response:**
```json
{
  "success": true,
  "message": "All analysis pre-computed and stored",
  "results": {},
  "total_precomputed_stats": 25
}
```

---

## Troubleshooting

### Issue: "Unknown domain: soccer"

**Cause:** Domain not registered in research framework.

**Solution:**
1. Add domain to `core/research_framework.py` in `_initialize_domain_registry()`
2. Ensure domain config file exists: `core/domain_configs/soccer.yaml`
3. Restart Flask application

### Issue: "Failed to import collector"

**Cause:** Collector class not found or import error.

**Solution:**
1. Check `collector_class` path in domain config YAML
2. Ensure collector file exists: `collectors/soccer_collector.py`
3. Verify class name matches config
4. Check for syntax errors in collector file

### Issue: "No data collected"

**Cause:** Collector logic not implemented or data source unavailable.

**Solution:**
1. Implement `_fetch_record()` method in collector
2. Verify data source API keys/credentials
3. Check rate limiting settings
4. Review collector logs for error messages

### Issue: "Sample size too small for analysis"

**Cause:** Insufficient data collected for statistical tests.

**Solution:**
1. Increase `target_sample_size` in config
2. Check collection errors/rate limits
3. Verify data source has enough records
4. Review `min_sample_size` thresholds in analyzer

### Issue: "Linter errors after generation"

**Cause:** Generated code may need minor adjustments.

**Solution:**
```bash
# Check for errors
python -m pylint collectors/soccer_collector.py

# Fix common issues:
# - Add missing imports
# - Resolve undefined variables
# - Fix indentation
```

### Issue: "Database model not found"

**Cause:** Model classes not added to `core/models.py`.

**Solution:**
1. Copy model definitions from `{domain}_models.py`
2. Add to `core/models.py`
3. Create tables: `db.create_all()`
4. Restart Flask app

---

## Best Practices

### Data Collection

1. **Rate Limiting**: Always respect API rate limits to avoid bans
   ```yaml
   collector_params:
     rate_limit_seconds: 2.0
     max_retries: 3
   ```

2. **Error Handling**: Implement robust error handling in collectors
   ```python
   try:
       data = self._fetch_record(i)
   except requests.RequestException as e:
       logger.error(f"Failed to fetch record {i}: {e}")
       errors.append(str(e))
       continue
   ```

3. **Progress Tracking**: Always use ProgressTracker for visibility
   ```python
   tracker = ProgressTracker(total_steps=target_size, print_interval=50)
   # ... in loop
   tracker.update(1, message=f"Collected {i}/{target_size}")
   ```

### Statistical Analysis

1. **Sample Size**: Ensure adequate sample for statistical power
   - Minimum 100 for correlations
   - Minimum 200 for basic regression
   - Minimum 500 for publication quality

2. **Effect Sizes**: Always report effect sizes, not just p-values
   ```python
   effect_size = self.framework.interpret_effect_size(r, 'correlation')
   ```

3. **Multiple Testing**: Apply corrections when testing many hypotheses
   ```python
   significant = self.apply_bonferroni_correction(p_values)
   ```

4. **Out-of-Sample Validation**: Always test on held-out data
   ```python
   X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
   ```

### Configuration

1. **Stratification**: Use when sampling from heterogeneous populations
   ```yaml
   stratification:
     enabled: true
     field: position
     targets:
       QB: 100
       RB: 100
   ```

2. **Temporal Analysis**: Enable for longitudinal studies
   ```yaml
   temporal_component: true
   temporal_field: "draft_year"
   ```

3. **Documentation**: Always document research questions clearly
   ```yaml
   research_questions:
     - "Specific, testable question 1?"
     - "Specific, testable question 2?"
   ```

### Performance

1. **Pre-computation**: Use background analyzer for expensive stats
   ```bash
   # Compute and cache results
   curl -X POST http://localhost:5000/api/admin/recompute-domain/nfl
   ```

2. **Caching**: Results stored in PreComputedStats for instant page loads
   - Endpoints serve cached data (<100ms)
   - Manual recomputation when data updates

3. **Batch Processing**: Process multiple domains overnight
   ```bash
   nohup python scripts/run_domain_analysis.py --all --mode update > analysis.log 2>&1 &
   ```

---

## Summary

The Domain Analysis Template System provides a complete, production-ready framework for nominative determinism research. Key advantages:

- **Consistency**: All domains follow same methodology automatically
- **Speed**: New domains created in <30 minutes
- **Quality**: Built-in validation and quality checks
- **Scalability**: Supports 10+ domains with unified interface
- **Maintainability**: Single source of truth for all research standards

For questions or issues, refer to the codebase documentation or contact the research team.

**Happy analyzing!** 🎯

