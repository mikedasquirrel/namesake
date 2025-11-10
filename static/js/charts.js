/**
 * Chart Utilities for Nominative Determinism Research Platform
 * Provides common charting functions using Plotly.js
 */

const Charts = {
    /**
     * Create a bar chart showing correlation by domain
     */
    correlationBarChart: function(elementId, domains, correlations) {
        const data = [{
            x: domains,
            y: correlations,
            type: 'bar',
            marker: {
                color: correlations.map(r => {
                    if (r > 0.4) return '#10b981';  // Strong - green
                    if (r > 0.2) return '#f59e0b';  // Medium - orange
                    return '#ef4444';                // Weak - red
                })
            },
            text: correlations.map(r => `r=${r.toFixed(3)}`),
            textposition: 'outside'
        }];

        const layout = {
            title: 'Effect Strength by Domain',
            xaxis: { title: 'Domain' },
            yaxis: { title: 'Correlation (r)', range: [0, Math.max(...correlations) * 1.1] },
            plot_bgcolor: '#f8fafc',
            paper_bgcolor: '#ffffff',
            margin: { t: 50, r: 30, b: 80, l: 60 }
        };

        Plotly.newPlot(elementId, data, layout, {responsive: true});
    },

    /**
     * Create a scatter plot showing two variables
     */
    scatterPlot: function(elementId, x, y, labels, title) {
        const data = [{
            x: x,
            y: y,
            mode: 'markers+text',
            type: 'scatter',
            text: labels,
            textposition: 'top center',
            marker: {
                size: 12,
                color: y,
                colorscale: 'Viridis',
                showscale: true
            }
        }];

        const layout = {
            title: title,
            xaxis: { title: 'X Variable' },
            yaxis: { title: 'Y Variable' },
            plot_bgcolor: '#f8fafc',
            paper_bgcolor: '#ffffff',
            hovermode: 'closest'
        };

        Plotly.newPlot(elementId, data, layout, {responsive: true});
    },

    /**
     * Create a time series line chart
     */
    timeSeriesChart: function(elementId, dates, values, label) {
        const data = [{
            x: dates,
            y: values,
            type: 'scatter',
            mode: 'lines+markers',
            name: label,
            line: { color: '#2563eb', width: 2 },
            marker: { size: 6 }
        }];

        const layout = {
            title: `${label} Over Time`,
            xaxis: { title: 'Date' },
            yaxis: { title: label },
            plot_bgcolor: '#f8fafc',
            paper_bgcolor: '#ffffff'
        };

        Plotly.newPlot(elementId, data, layout, {responsive: true});
    },

    /**
     * Create a pie chart showing distribution
     */
    pieChart: function(elementId, labels, values, title) {
        const data = [{
            labels: labels,
            values: values,
            type: 'pie',
            hole: 0.4,  // Donut chart
            marker: {
                colors: ['#ef4444', '#f59e0b', '#10b981', '#3b82f6', '#8b5cf6', '#ec4899']
            }
        }];

        const layout = {
            title: title,
            paper_bgcolor: '#ffffff'
        };

        Plotly.newPlot(elementId, data, layout, {responsive: true});
    },

    /**
     * Create a box plot showing distribution
     */
    boxPlot: function(elementId, groups, values, title) {
        const data = groups.map(group => ({
            y: values[group],
            type: 'box',
            name: group
        }));

        const layout = {
            title: title,
            yaxis: { title: 'Value' },
            plot_bgcolor: '#f8fafc',
            paper_bgcolor: '#ffffff'
        };

        Plotly.newPlot(elementId, data, layout, {responsive: true});
    }
};

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Charts;
}

