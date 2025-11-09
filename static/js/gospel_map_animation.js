/**
 * Gospel Spread Map Animation
 * ============================
 * 
 * Animated map showing gospel adoption spreading across regions over 20 centuries.
 * Uses D3.js with geographic projections and timeline slider.
 */

class GospelSpreadMap {
    constructor(containerId) {
        this.container = d3.select('#' + containerId);
        this.width = 960;
        this.height = 600;
        this.currentYear = 100;
        this.isPlaying = false;
        
        this.init();
    }
    
    init() {
        // Create SVG
        this.svg = this.container.append('svg')
            .attr('width', this.width)
            .attr('height', this.height);
        
        // Map projection
        this.projection = d3.geoMercator()
            .center([20, 40])  // Center on Europe/Middle East
            .scale(200)
            .translate([this.width / 2, this.height / 2]);
        
        this.path = d3.geoPath().projection(this.projection);
        
        // Color scale for adoption percentage
        this.colorScale = d3.scaleSequential(d3.interpolateBlues)
            .domain([0, 100]);
        
        // Timeline data (century: regions with adoption %)
        this.timeline = this.generateTimelineData();
        
        // Create map
        this.drawMap();
        
        // Create timeline controls
        this.createTimeline();
        
        // Initial render
        this.updateMap(this.currentYear);
    }
    
    generateTimelineData() {
        // Mock timeline data - in production, fetch from API
        return {
            100: { 'Middle East': 2, 'Mediterranean': 1 },
            200: { 'Middle East': 10, 'Mediterranean': 5, 'North Africa': 3 },
            400: { 'Middle East': 40, 'Mediterranean': 35, 'Europe': 20, 'North Africa': 25 },
            800: { 'Europe': 70, 'Middle East': 30, 'North Africa': 40 },
            1200: { 'Europe': 90, 'Middle East': 20, 'Africa': 5 },
            1600: { 'Europe': 95, 'Americas': 25, 'Africa': 10 },
            1800: { 'Europe': 92, 'Americas': 80, 'Africa': 15, 'Asia': 2 },
            2000: { 'Global': 33, 'Americas': 85, 'Europe': 75, 'Africa': 48, 'Asia': 8 }
        };
    }
    
    drawMap() {
        // Simplified world regions (in production, use actual GeoJSON)
        const regions = [
            { name: 'Europe', center: [15, 50], radius: 15 },
            { name: 'Middle East', center: [45, 30], radius: 10 },
            { name: 'North Africa', center: [15, 25], radius: 12 },
            { name: 'Americas', center: [-80, 20], radius: 20 },
            { name: 'Africa', center: [25, -5], radius: 15 },
            { name: 'Asia', center: [100, 30], radius: 25 }
        ];
        
        this.regions = this.svg.selectAll('.region')
            .data(regions)
            .enter()
            .append('circle')
            .attr('class', 'region')
            .attr('cx', d => this.projection([d.center[0], d.center[1]])[0])
            .attr('cy', d => this.projection([d.center[0], d.center[1]])[1])
            .attr('r', d => d.radius)
            .attr('fill', 'lightgray')
            .attr('opacity', 0.5)
            .attr('stroke', '#333')
            .attr('stroke-width', 1);
        
        // Labels
        this.svg.selectAll('.region-label')
            .data(regions)
            .enter()
            .append('text')
            .attr('class', 'region-label')
            .attr('x', d => this.projection([d.center[0], d.center[1]])[0])
            .attr('y', d => this.projection([d.center[0], d.center[1]])[1])
            .attr('text-anchor', 'middle')
            .attr('font-size', '12px')
            .attr('font-weight', 'bold')
            .text(d => d.name);
    }
    
    createTimeline() {
        // Timeline slider
        const timelineDiv = this.container.append('div')
            .style('margin-top', '20px')
            .style('text-align', 'center');
        
        timelineDiv.append('label')
            .text('Year: ')
            .append('span')
            .attr('id', 'yearDisplay')
            .style('font-weight', 'bold')
            .style('font-size', '18px')
            .text(this.currentYear);
        
        timelineDiv.append('br');
        
        const slider = timelineDiv.append('input')
            .attr('type', 'range')
            .attr('min', 100)
            .attr('max', 2000)
            .attr('step', 100)
            .attr('value', this.currentYear)
            .style('width', '80%')
            .on('input', () => {
                this.currentYear = +slider.property('value');
                d3.select('#yearDisplay').text(this.currentYear);
                this.updateMap(this.currentYear);
            });
        
        // Play button
        const playBtn = timelineDiv.append('button')
            .text('▶ Play')
            .style('margin-left', '20px')
            .style('padding', '10px 20px')
            .on('click', () => this.togglePlay());
        
        this.playButton = playBtn;
    }
    
    updateMap(year) {
        const data = this.timeline[year] || {};
        
        // Update region colors based on adoption percentage
        this.regions
            .transition()
            .duration(500)
            .attr('fill', d => {
                const adoption = data[d.name] || 0;
                return adoption > 0 ? this.colorScale(adoption) : 'lightgray';
            })
            .attr('opacity', d => {
                const adoption = data[d.name] || 0;
                return adoption > 0 ? 0.8 : 0.3;
            });
    }
    
    togglePlay() {
        this.isPlaying = !this.isPlaying;
        this.playButton.text(this.isPlaying ? '⏸ Pause' : '▶ Play');
        
        if (this.isPlaying) {
            this.play();
        }
    }
    
    play() {
        if (!this.isPlaying) return;
        
        this.currentYear += 100;
        if (this.currentYear > 2000) {
            this.currentYear = 100;
        }
        
        d3.select('#yearDisplay').text(this.currentYear);
        d3.select('input[type=range]').property('value', this.currentYear);
        this.updateMap(this.currentYear);
        
        setTimeout(() => this.play(), 1000);
    }
}

// Usage:
// const gospelMap = new GospelSpreadMap('mapContainer');

