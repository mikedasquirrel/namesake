# Template Organization

## Current Status

- **Total Templates**: 74 active templates (2 archived)
- **All templates are actively used** in routes
- **Well-organized** by domain

## Template Structure

### Core Templates (3)
- `base.html` - Base template with navigation (extended by all pages)
- `overview.html` - Homepage/landing page
- `analysis.html` - Main analysis dashboard

### Betting Templates (4)
- `betting_performance.html` - Performance metrics dashboard
- `live_betting_dashboard.html` - Real-time betting interface
- `portfolio_history.html` - Historical performance tracking
- `sports_betting_dashboard.html` - Main betting dashboard

### Sports Templates (10)
- `sports_meta_analysis.html` - Cross-sport analysis
- `nba.html`, `nba_findings.html` - NBA research
- `nfl.html`, `nfl_findings.html` - NFL research
- `mlb.html`, `mlb_findings.html` - MLB players
- `mlb_teams.html`, `mlb_teams_findings.html` - MLB teams
- `sports_roster_locality.html` - Geographic patterns

### Markets Templates (7)
- `crypto_findings.html` - Cryptocurrency analysis
- `mtg.html` - Magic: The Gathering cards
- `board_games.html`, `board_games_findings.html` - Board game research
- `formula_dashboard.html` - Formula explorer
- `nominative_dashboard.html` - Main research dashboard
- `research_dashboard.html` - Advanced research features

### Research Domain Templates (48)
Organized by research area:

**Human Systems:**
- `academics.html`, `academics_findings.html` - Academic researchers
- `elections.html`, `election_findings.html` - Electoral linguistics
- `immigration.html`, `immigration_findings.html` - Immigration patterns
- `bands.html`, `band_findings.html`, `band_members.html` - Music research
- `ships.html`, `ship_findings.html` - Naval nomenclature
- `adult_film.html`, `adult_film_findings.html` - Stage names
- `mental_health.html`, `mental_health_findings.html` - Disorder nomenclature

**Specialized Research:**
- `america.html` - Country name phonetics
- `marriage.html` - Compatibility research
- `literary_name_composition.html` - Character names
- `foretold_naming.html` - Selection forces
- `love_words.html` - Romance language phonetics
- `romance_instruments.html` - Instrument nomenclature
- `gospel_success.html` - Biblical character analysis
- `cross_religious.html` - Interfaith analysis
- `the_discoverer.html` - Meta-analysis of researcher

**Natural Events:**
- `hurricanes.html` - Hurricane nomenclature
- `hurricane_demographics.html` - Hurricane impact analysis
- `earthquakes.html` - Earthquake analysis
- `predictions_2026.html` - Hurricane predictions

**Philosophical:**
- `the_nail.html` - Art project viewer
- `the_word_made_flesh.html` - Philosophical synthesis
- `unknown_known.html` - Philosophical implications
- `philosophical_implications_interactive.html` - Interactive philosophy

**Tools & Utilities:**
- `formula.html`, `formula_explorer.html` - Formula exploration
- `pattern_discovery.html` - Pattern finding tool
- `personal_name_analyzer.html` - Name analysis tool
- `brand_optimizer.html` - Brand name optimization
- `convergence_tracker.html` - Convergence analysis

**Specialized Analytics:**
- `bands_analytics.html`, `bands_diagnostic.html`, `bands_docs_hub.html`, `bands_lineage.html` - Advanced band research
- `acoustic_analysis.html` - Phonetic analysis
- `phonetic_universals.html` - Phonetic patterns
- `meta_formulas.html` - Meta-formula analysis
- `africa_funding_linguistics.html` - Geopolitical linguistics
- `analysis_72k.html` - Large-scale analysis
- `disorder_nomenclature.html` - Psychiatric nomenclature

### Error Pages (2)
- `404.html` - Page not found
- `500.html` - Internal server error

## Archived Templates (2)

Moved to `templates_archive/`:
- `research_overview.html` - Duplicate of overview functionality
- `synchronicity_findings.html` - Not referenced in routes

## Template Patterns

### Consistent Structure

All templates follow this pattern:

```html
{% extends "base.html" %}

{% block title %}Page Title{% endblock %}

{% block extra_css %}
<!-- Page-specific CSS -->
{% endblock %}

{% block content %}
<!-- Page content -->
{% endblock %}
```

### Base Template Features

`base.html` provides:
- Unified navigation bar
- Responsive design
- Common styling
- Mobile menu support
- Dropdown menus for domains

## Opportunities for Future Consolidation

While all current templates are used, future improvements could include:

### 1. Dynamic Sport Template

Instead of separate `nba.html`, `nfl.html`, `mlb.html`, create:

```python
# In sports blueprint
@sports_bp.route('/<sport>')
def sport_page(sport):
    return render_template('sport_generic.html', sport=sport, data=get_sport_data(sport))
```

**Benefit**: Reduce 10 templates to 2-3

### 2. Dynamic Findings Template

Many domains have both `domain.html` and `domain_findings.html`. Could consolidate:

```python
@bp.route('/<domain>')
@bp.route('/<domain>/findings')
def domain_page(domain, show_findings=False):
    return render_template('domain_generic.html', domain=domain, findings=show_findings)
```

**Benefit**: Reduce ~20 template pairs to 1 dynamic template

### 3. Research Domain Template

Similar research pages could use one template with domain-specific data:

```python
@research_bp.route('/<domain>')
def research_page(domain):
    config = load_domain_config(domain)
    return render_template('research_generic.html', config=config)
```

**Benefit**: Reduce 48 research templates to ~5-10

## Recommendation: Keep Current Structure

**Why NOT consolidate now:**

1. **All templates actively used** - No dead code to remove
2. **Domain-specific customization** - Each page has unique content
3. **Easy to maintain** - Clear 1:1 mapping of route to template
4. **Low file size** - HTML templates are small (~2-10 KB each)
5. **Development speed** - Easier to edit specific page than manage complex conditionals

**When to consider consolidation:**

- Adding 10+ similar new domains
- Significant code duplication in templates
- Performance issues (unlikely with templates)
- Need for theme/branding changes across all pages

## Best Practices

### Adding New Templates

1. Follow naming convention: `domain.html` or `domain_feature.html`
2. Extend `base.html` for consistent navigation
3. Add to appropriate blueprint
4. Document in this file

### Modifying Templates

1. Test changes don't break base template inheritance
2. Check responsive design (mobile/tablet)
3. Verify navigation links still work
4. Update this documentation if structure changes

### Removing Templates

1. Confirm no routes reference it (use `audit_templates.py`)
2. Move to `templates_archive/` (don't delete immediately)
3. Update documentation
4. Remove from archive after 1 month if no issues

## Template Statistics

- **Average template size**: ~150 lines
- **Largest template**: `base.html` (~200 lines with navigation)
- **Smallest templates**: Error pages (~20 lines)
- **Total template code**: ~11,100 lines (74 × 150 avg)
- **Percentage of total codebase**: <1%

## Performance Notes

Templates are cached by Flask in production:
- First render: ~2-5ms
- Subsequent renders: <1ms (cached)
- No performance issues with 74 templates

## Documentation Update

Last audited: November 2025
- 76 templates evaluated
- 2 archived (unused)
- 74 active and documented
- All actively used in routes

---

**Conclusion**: Template organization is healthy. No immediate consolidation needed. Focus consolidation efforts on analyzers (190 modules) and routes (332 in original app.py) instead.

