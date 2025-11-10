# Visual Enhancements Plan

## Current State

Based on audit and inspection:
- **74 templates** with custom CSS
- Basic styling via `static/css/style.css`
- Minimal JavaScript (3 files in `static/js/`)
- **No interactive charts or visualizations**
- Inconsistent UI across domains

## Problems Identified

1. **No Data Visualization**
   - Statistical results shown as text tables
   - No charts, graphs, or interactive visualizations
   - Hard to understand patterns visually

2. **Inconsistent Styling**
   - Different pages have different layouts
   - No unified design system
   - Color schemes vary by domain

3. **Limited Interactivity**
   - Static pages with no user interaction
   - No filtering, sorting, or exploration features
   - No real-time updates visualization

4. **Poor Mobile Experience**
   - Many templates not mobile-optimized
   - Navigation difficult on small screens
   - Charts (if any) don't resize

## Enhancement Strategy

### Phase 1: Chart Library Integration ✅

Add Plotly for interactive charting:

```html
<!-- Add to base.html -->
<script src="https://cdn.plot.ly/plotly-2.26.0.min.js"></script>
```

**Benefits:**
- Interactive zoom, pan, hover
- Export to PNG/SVG
- Responsive sizing
- Python integration (`plotly.py`)

### Phase 2: Core Visualizations

Add charts to key pages:

#### 1. Analysis Dashboard (`analysis.html`)

```javascript
// Correlation visualization
const correlationData = [{
    x: ['NFL', 'NBA', 'MLB', 'Hurricanes', 'Crypto'],
    y: [0.427, 0.196, 0.221, 0.45, 0.12],
    type: 'bar',
    marker: {color: 'rgb(55, 128, 191)'}
}];

Plotly.newPlot('correlation-chart', correlationData, {
    title: 'Correlation by Domain',
    xaxis: {title: 'Domain'},
    yaxis: {title: 'Pearson r'}
});
```

#### 2. Sports Meta-Analysis (`sports_meta_analysis.html`)

```javascript
// Scatter plot: contact level vs effect size
const scatterData = [{
    x: contactLevels,
    y: effectSizes,
    mode: 'markers+text',
    text: sportNames,
    textposition: 'top',
    marker: {
        size: 12,
        color: effectSizes,
        colorscale: 'Viridis'
    }
}];
```

#### 3. Betting Performance (`betting_performance.html`)

```javascript
// Time series: ROI over time
const timeSeriesData = [{
    x: dates,
    y: rois,
    type: 'scatter',
    mode: 'lines+markers',
    name: 'ROI'
}];

// Add cumulative profit line
```

### Phase 3: Design System

Create consistent styling:

```css
/* static/css/design-system.css */

:root {
    /* Colors */
    --primary: #2563eb;
    --secondary: #64748b;
    --success: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
    --background: #f8fafc;
    --surface: #ffffff;
    --text: #1e293b;
    --text-muted: #64748b;
    
    /* Typography */
    --font-sans: 'Inter', system-ui, sans-serif;
    --font-mono: 'Fira Code', monospace;
    
    /* Spacing */
    --space-xs: 0.25rem;
    --space-sm: 0.5rem;
    --space-md: 1rem;
    --space-lg: 1.5rem;
    --space-xl: 2rem;
    
    /* Borders */
    --radius-sm: 0.25rem;
    --radius-md: 0.5rem;
    --radius-lg: 1rem;
}

/* Component Classes */
.card {
    background: var(--surface);
    border-radius: var(--radius-md);
    padding: var(--space-lg);
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.stat-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
}

.stat-value {
    font-size: 2.5rem;
    font-weight: 700;
    color: var(--primary);
}

.stat-label {
    font-size: 0.875rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.chart-container {
    width: 100%;
    height: 400px;
    margin: var(--space-lg) 0;
}
```

### Phase 4: Interactive Components

Add filtering and exploration:

```javascript
// static/js/interactive-table.js

class InteractiveTable {
    constructor(containerId, data) {
        this.container = document.getElementById(containerId);
        this.data = data;
        this.filteredData = data;
        this.sortColumn = null;
        this.sortDirection = 'asc';
        
        this.render();
    }
    
    filter(column, value) {
        this.filteredData = this.data.filter(row => 
            row[column].toString().toLowerCase().includes(value.toLowerCase())
        );
        this.render();
    }
    
    sort(column) {
        if (this.sortColumn === column) {
            this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            this.sortColumn = column;
            this.sortDirection = 'asc';
        }
        
        this.filteredData.sort((a, b) => {
            const multiplier = this.sortDirection === 'asc' ? 1 : -1;
            return multiplier * (a[column] > b[column] ? 1 : -1);
        });
        
        this.render();
    }
    
    render() {
        // Render table HTML
    }
}
```

### Phase 5: Real-time Updates

Add WebSocket or polling for live data:

```javascript
// static/js/live-updates.js

class LiveDataUpdater {
    constructor(endpoint, updateInterval = 15000) {
        this.endpoint = endpoint;
        this.interval = updateInterval;
        this.callbacks = [];
    }
    
    start() {
        this.update();  // Initial update
        this.timer = setInterval(() => this.update(), this.interval);
    }
    
    stop() {
        if (this.timer) {
            clearInterval(this.timer);
        }
    }
    
    async update() {
        try {
            const response = await fetch(this.endpoint);
            const data = await response.json();
            this.callbacks.forEach(cb => cb(data));
        } catch (error) {
            console.error('Update failed:', error);
        }
    }
    
    onUpdate(callback) {
        this.callbacks.push(callback);
    }
}

// Usage
const updater = new LiveDataUpdater('/api/betting/opportunities');
updater.onUpdate(data => {
    updateBettingTable(data);
    updateChart(data);
});
updater.start();
```

## Implementation Checklist

### Immediate (Week 1)

- [x] Document current state
- [x] Create enhancement plan
- [ ] Add Plotly to base template
- [ ] Create design system CSS
- [ ] Add chart to analysis dashboard

### Short-term (Week 2-3)

- [ ] Add charts to 5 key pages:
  - Analysis dashboard
  - Sports meta-analysis
  - Betting performance
  - Portfolio history
  - Live betting

- [ ] Implement interactive tables
- [ ] Add filtering/sorting
- [ ] Improve mobile responsiveness

### Long-term (Month 2+)

- [ ] Add WebSocket for real-time updates
- [ ] Create data exploration interface
- [ ] Add export functionality (PDF reports)
- [ ] Implement dark mode
- [ ] Add customizable dashboards

## Quick Wins

### 1. Add Plotly (5 minutes)

```html
<!-- In base.html, before </body> -->
<script src="https://cdn.plot.ly/plotly-2.26.0.min.js"></script>
```

### 2. Sample Chart on Analysis Page (15 minutes)

```html
<!-- In analysis.html -->
<div id="domain-correlation-chart" style="width:100%;height:400px"></div>

<script>
const data = [{
    x: ['NFL', 'NBA', 'MLB', 'Hurricanes', 'Crypto', 'MTG', 'Ships'],
    y: [0.427, 0.196, 0.221, 0.45, 0.12, 0.15, 0.28],
    type: 'bar',
    marker: {
        color: ['#ef4444', '#f59e0b', '#10b981', '#3b82f6', '#8b5cf6', '#ec4899', '#06b6d4']
    }
}];

const layout = {
    title: 'Correlation Strength by Domain',
    xaxis: {title: 'Domain'},
    yaxis: {title: 'Pearson r', range: [0, 0.6]},
    plot_bgcolor: '#f8fafc',
    paper_bgcolor: '#ffffff'
};

Plotly.newPlot('domain-correlation-chart', data, layout, {responsive: true});
</script>
```

### 3. Stat Cards (10 minutes)

```html
<!-- Reusable component -->
<div class="stats-grid">
    <div class="stat-card">
        <div class="stat-value">17</div>
        <div class="stat-label">Domains Analyzed</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">21,473</div>
        <div class="stat-label">Total Entities</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">p&lt;10⁻¹⁵</div>
        <div class="stat-label">Significance</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">48-62%</div>
        <div class="stat-label">Portfolio ROI</div>
    </div>
</div>

<style>
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
    margin: 2rem 0;
}
</style>
```

## Priority Pages for Enhancement

1. **Analysis Dashboard** (`/analysis`) - High traffic, needs visualization
2. **Sports Meta-Analysis** (`/sports/meta-analysis`) - Complex data, needs charts
3. **Betting Performance** (`/betting/performance`) - Time-series data
4. **Portfolio History** (`/betting/portfolio`) - Historical trends
5. **Live Betting** (`/betting/live`) - Real-time updates

## Success Metrics

- [ ] At least 5 pages with interactive charts
- [ ] Consistent design system across all pages
- [ ] Mobile-responsive on all pages
- [ ] Improved user engagement (time on site)
- [ ] Positive user feedback

## Resources

- **Plotly Docs**: https://plotly.com/javascript/
- **Chart Examples**: https://plotly.com/javascript/basic-charts/
- **Design System**: Tailwind CSS or custom
- **Icons**: Heroicons or Font Awesome

---

**Status**: Plan documented, ready for implementation  
**Priority**: High - significantly improves user experience  
**Effort**: Medium - 2-3 weeks for complete implementation  
**Impact**: High - transforms static pages into interactive dashboards

