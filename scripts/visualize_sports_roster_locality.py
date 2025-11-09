"""Visualization Script for Sports Roster Locality Analysis

Generates publication-quality figures:
- Bar charts: Americanness and melodiousness by team/sport
- Scatter plots: Raw vs sport-adjusted melodiousness
- Stacked bars: Demographic composition (roster vs baseline)
- Heat maps: Team × metric comparisons
- Correlation plots: Sport characteristics vs roster composition

Author: Michael Smerconish
Date: November 2025
"""

import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime

# Setup paths
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
sns.set_context("paper", font_scale=1.2)


def load_latest_results():
    """Load the latest analysis results."""
    results_file = Path('analysis_outputs/sports_roster_locality/full_analysis_latest.json')
    
    if not results_file.exists():
        print(f"Error: Results file not found: {results_file}")
        print("Please run the analysis first: python scripts/run_sports_roster_locality_analysis.py")
        sys.exit(1)
    
    with open(results_file, 'r') as f:
        results = json.load(f)
    
    print(f"Loaded results with {len(results.get('roster_analyses', []))} rosters")
    return results


def setup_output_directory():
    """Create figures output directory."""
    output_dir = Path('analysis_outputs/sports_roster_locality/figures')
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {output_dir}")
    return output_dir


def plot_americanness_by_sport(results, output_dir):
    """Bar chart: Americanness scores by sport."""
    rosters = results['roster_analyses']
    
    # Group by sport
    sport_data = {sport: [] for sport in ['nfl', 'nba', 'mlb']}
    for roster in rosters:
        sport_data[roster['sport']].append(roster['americanness_score'])
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot bars
    x_pos = np.arange(3)
    means = [np.mean(sport_data[s]) for s in ['nfl', 'nba', 'mlb']]
    stds = [np.std(sport_data[s]) for s in ['nfl', 'nba', 'mlb']]
    
    bars = ax.bar(x_pos, means, yerr=stds, capsize=10, alpha=0.7,
                   color=['#1f77b4', '#ff7f0e', '#2ca02c'])
    
    # Baseline line
    baseline = results['baseline_statistics']['stratified']['americanness_score']
    ax.axhline(y=baseline, color='red', linestyle='--', linewidth=2, label='US Baseline')
    
    ax.set_xlabel('Sport', fontsize=14, fontweight='bold')
    ax.set_ylabel('Americanness Score (0-100)', fontsize=14, fontweight='bold')
    ax.set_title('Roster Americanness by Sport\nvs. US Demographic Baseline', 
                 fontsize=16, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(['NFL', 'NBA', 'MLB'], fontsize=12)
    ax.legend(fontsize=12)
    ax.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for i, (bar, mean) in enumerate(zip(bars, means)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + stds[i] + 2,
                f'{mean:.1f}', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'americanness_by_sport.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("  ✓ Created: americanness_by_sport.png")


def plot_melodiousness_comparison(results, output_dir):
    """Scatter plot: Raw vs sport-adjusted melodiousness."""
    rosters = results['roster_analyses']
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Plot by sport
    colors = {'nfl': '#1f77b4', 'nba': '#ff7f0e', 'mlb': '#2ca02c'}
    labels = {'nfl': 'NFL', 'nba': 'NBA', 'mlb': 'MLB'}
    
    for sport in ['nfl', 'nba', 'mlb']:
        sport_rosters = [r for r in rosters if r['sport'] == sport]
        raw = [r['melodiousness_score'] for r in sport_rosters]
        adjusted = [r['melodiousness_sport_adjusted'] for r in sport_rosters]
        
        ax.scatter(raw, adjusted, c=colors[sport], label=labels[sport], 
                  s=100, alpha=0.6, edgecolors='black', linewidth=0.5)
    
    # Diagonal line (no adjustment)
    ax.plot([0, 100], [0, 100], 'k--', alpha=0.3, linewidth=2, label='No Adjustment')
    
    ax.set_xlabel('Raw Melodiousness Score', fontsize=14, fontweight='bold')
    ax.set_ylabel('Sport-Adjusted Melodiousness Score', fontsize=14, fontweight='bold')
    ax.set_title('Melodiousness: Raw vs Sport-Adjusted\n(Sport characteristics: contact, precision, speed)',
                 fontsize=16, fontweight='bold')
    ax.legend(fontsize=12, loc='upper left')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(20, 100)
    ax.set_ylim(20, 100)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'melodiousness_raw_vs_adjusted.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("  ✓ Created: melodiousness_raw_vs_adjusted.png")


def plot_demographic_composition(results, output_dir):
    """Stacked bar chart: Demographic composition (roster vs baseline)."""
    rosters = results['roster_analyses']
    
    # Calculate sport-level averages
    demo_data = []
    for sport in ['nfl', 'nba', 'mlb']:
        sport_rosters = [r for r in rosters if r['sport'] == sport]
        
        if sport_rosters:
            demo_data.append({
                'Sport': sport.upper(),
                'Anglo': np.mean([r['demographics']['anglo_pct'] for r in sport_rosters]),
                'Latino': np.mean([r['demographics']['latino_pct'] for r in sport_rosters]),
                'Asian': np.mean([r['demographics']['asian_pct'] for r in sport_rosters]),
                'Black': np.mean([r['demographics']['black_pct'] for r in sport_rosters]),
                'Other': np.mean([r['demographics']['other_pct'] for r in sport_rosters]),
            })
    
    # Add baseline
    demo_data.append({
        'Sport': 'US\nBaseline',
        'Anglo': 60,
        'Latino': 18,
        'Asian': 6,
        'Black': 13,
        'Other': 3,
    })
    
    df = pd.DataFrame(demo_data)
    df = df.set_index('Sport')
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Stacked bar chart
    df.plot(kind='bar', stacked=True, ax=ax, 
            color=['#3498db', '#e74c3c', '#f39c12', '#9b59b6', '#95a5a6'],
            width=0.7, edgecolor='black', linewidth=1.5)
    
    ax.set_xlabel('Sport', fontsize=14, fontweight='bold')
    ax.set_ylabel('Percentage (%)', fontsize=14, fontweight='bold')
    ax.set_title('Demographic Composition: Professional Sports Rosters vs US Baseline',
                 fontsize=16, fontweight='bold')
    ax.legend(title='Demographic', fontsize=11, title_fontsize=12, 
             bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0, fontsize=12)
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_ylim(0, 100)
    
    # Add horizontal line at 100%
    ax.axhline(y=100, color='black', linestyle='-', linewidth=1)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'demographic_composition_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("  ✓ Created: demographic_composition_comparison.png")


def plot_team_heatmap(results, output_dir):
    """Heat map: Team × metric comparisons (top 30 teams)."""
    rosters = results['roster_analyses']
    
    # Select top 30 teams by americanness
    top_rosters = sorted(rosters, key=lambda x: x.get('americanness_score', 0), reverse=True)[:30]
    
    # Build data matrix
    team_names = []
    americanness = []
    melodiousness = []
    anglo_pct = []
    latino_pct = []
    asian_pct = []
    
    for roster in top_rosters:
        team_name = f"{roster['team_name']} ({roster['sport'].upper()})"
        team_names.append(team_name)
        americanness.append(roster['americanness_score'])
        melodiousness.append(roster['melodiousness_score'])
        anglo_pct.append(roster['demographics']['anglo_pct'])
        latino_pct.append(roster['demographics']['latino_pct'])
        asian_pct.append(roster['demographics']['asian_pct'])
    
    # Create DataFrame
    data = {
        'Americanness': americanness,
        'Melodiousness': melodiousness,
        'Anglo %': anglo_pct,
        'Latino %': latino_pct,
        'Asian %': asian_pct,
    }
    
    df = pd.DataFrame(data, index=team_names)
    
    # Normalize for heatmap (0-1 scale)
    df_norm = (df - df.min()) / (df.max() - df.min())
    
    fig, ax = plt.subplots(figsize=(10, 16))
    
    sns.heatmap(df_norm, annot=False, fmt='.2f', cmap='RdYlGn', 
                cbar_kws={'label': 'Normalized Score'}, 
                linewidths=0.5, ax=ax)
    
    ax.set_title('Top 30 Teams: Multi-Metric Comparison (Normalized 0-1)',
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Metric', fontsize=14, fontweight='bold')
    ax.set_ylabel('Team', fontsize=14, fontweight='bold')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right', fontsize=11)
    ax.set_yticklabels(ax.get_yticklabels(), fontsize=8)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'team_metric_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("  ✓ Created: team_metric_heatmap.png")


def plot_sport_characteristics_correlation(results, output_dir):
    """Scatter plots: Sport characteristics vs roster composition."""
    sport_aggs = results.get('sport_aggregates', {})
    
    if len(sport_aggs) < 2:
        print("  ✗ Skipped: sport_characteristics_correlation.png (insufficient data)")
        return
    
    # Extract data
    sports_data = []
    for sport, agg in sport_aggs.items():
        # Get sport characteristics from first roster
        rosters = results['roster_analyses']
        sport_rosters = [r for r in rosters if r['sport'] == sport]
        
        if sport_rosters:
            # Reconstruction from stored data or defaults
            char_defaults = {
                'nfl': {'contact': 9, 'precision': 3, 'speed': 5},
                'nba': {'contact': 6, 'precision': 6, 'speed': 9},
                'mlb': {'contact': 2, 'precision': 7, 'speed': 3},
            }
            
            sports_data.append({
                'sport': sport.upper(),
                'contact': char_defaults[sport]['contact'],
                'precision': char_defaults[sport]['precision'],
                'speed': char_defaults[sport]['speed'],
                'americanness': agg['mean_americanness'],
                'melodiousness': agg['mean_melodiousness'],
                'latino_pct': agg['mean_demo_latino'],
            })
    
    df = pd.DataFrame(sports_data)
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    
    # Plot 1: Contact vs Americanness
    ax = axes[0, 0]
    for _, row in df.iterrows():
        ax.scatter(row['contact'], row['americanness'], s=300, alpha=0.6)
        ax.text(row['contact'] + 0.2, row['americanness'], row['sport'], 
               fontsize=12, fontweight='bold')
    ax.set_xlabel('Contact Level (0-10)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Mean Americanness', fontsize=12, fontweight='bold')
    ax.set_title('Contact Level vs Americanness', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # Plot 2: Precision vs Melodiousness
    ax = axes[0, 1]
    for _, row in df.iterrows():
        ax.scatter(row['precision'], row['melodiousness'], s=300, alpha=0.6)
        ax.text(row['precision'] + 0.2, row['melodiousness'], row['sport'], 
               fontsize=12, fontweight='bold')
    ax.set_xlabel('Precision (0-10)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Mean Melodiousness', fontsize=12, fontweight='bold')
    ax.set_title('Precision vs Melodiousness', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # Plot 3: Speed vs Americanness
    ax = axes[1, 0]
    for _, row in df.iterrows():
        ax.scatter(row['speed'], row['americanness'], s=300, alpha=0.6)
        ax.text(row['speed'] + 0.2, row['americanness'], row['sport'], 
               fontsize=12, fontweight='bold')
    ax.set_xlabel('Action Speed (0-10)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Mean Americanness', fontsize=12, fontweight='bold')
    ax.set_title('Action Speed vs Americanness', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # Plot 4: Contact vs Latino %
    ax = axes[1, 1]
    for _, row in df.iterrows():
        ax.scatter(row['contact'], row['latino_pct'], s=300, alpha=0.6)
        ax.text(row['contact'] + 0.2, row['latino_pct'], row['sport'], 
               fontsize=12, fontweight='bold')
    ax.set_xlabel('Contact Level (0-10)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Mean Latino %', fontsize=12, fontweight='bold')
    ax.set_title('Contact Level vs Latino Representation', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    plt.suptitle('Sport Characteristics vs Roster Composition', 
                 fontsize=16, fontweight='bold', y=1.00)
    plt.tight_layout()
    plt.savefig(output_dir / 'sport_characteristics_correlation.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("  ✓ Created: sport_characteristics_correlation.png")


def plot_top_teams_comparison(results, output_dir):
    """Bar chart: Top 10 most American and most melodious teams."""
    rosters = results['roster_analyses']
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    
    # Top 10 most American
    top_american = sorted(rosters, key=lambda x: x['americanness_score'], reverse=True)[:10]
    
    ax = axes[0]
    teams = [f"{r['team_name']}\n({r['sport'].upper()})" for r in top_american]
    scores = [r['americanness_score'] for r in top_american]
    colors = ['#1f77b4' if r['sport'] == 'nfl' else '#ff7f0e' if r['sport'] == 'nba' else '#2ca02c' 
              for r in top_american]
    
    bars = ax.barh(range(len(teams)), scores, color=colors, alpha=0.7, edgecolor='black')
    ax.set_yticks(range(len(teams)))
    ax.set_yticklabels(teams, fontsize=10)
    ax.set_xlabel('Americanness Score', fontsize=12, fontweight='bold')
    ax.set_title('Top 10 Most American Rosters', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')
    ax.invert_yaxis()
    
    # Add value labels
    for i, (bar, score) in enumerate(zip(bars, scores)):
        width = bar.get_width()
        ax.text(width + 1, bar.get_y() + bar.get_height()/2., 
                f'{score:.1f}', ha='left', va='center', fontsize=9, fontweight='bold')
    
    # Top 10 most melodious
    top_melodious = sorted(rosters, key=lambda x: x['melodiousness_score'], reverse=True)[:10]
    
    ax = axes[1]
    teams = [f"{r['team_name']}\n({r['sport'].upper()})" for r in top_melodious]
    scores = [r['melodiousness_score'] for r in top_melodious]
    colors = ['#1f77b4' if r['sport'] == 'nfl' else '#ff7f0e' if r['sport'] == 'nba' else '#2ca02c' 
              for r in top_melodious]
    
    bars = ax.barh(range(len(teams)), scores, color=colors, alpha=0.7, edgecolor='black')
    ax.set_yticks(range(len(teams)))
    ax.set_yticklabels(teams, fontsize=10)
    ax.set_xlabel('Melodiousness Score', fontsize=12, fontweight='bold')
    ax.set_title('Top 10 Most Melodious Rosters', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')
    ax.invert_yaxis()
    
    # Add value labels
    for i, (bar, score) in enumerate(zip(bars, scores)):
        width = bar.get_width()
        ax.text(width + 1, bar.get_y() + bar.get_height()/2., 
                f'{score:.1f}', ha='left', va='center', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'top_teams_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("  ✓ Created: top_teams_comparison.png")


def main():
    """Main visualization function."""
    print("="*80)
    print("SPORTS ROSTER LOCALITY VISUALIZATION")
    print("="*80)
    print()
    
    # Load results
    print("Loading analysis results...")
    results = load_latest_results()
    
    # Setup output
    output_dir = setup_output_directory()
    
    # Generate figures
    print("\nGenerating figures...")
    plot_americanness_by_sport(results, output_dir)
    plot_melodiousness_comparison(results, output_dir)
    plot_demographic_composition(results, output_dir)
    plot_team_heatmap(results, output_dir)
    plot_sport_characteristics_correlation(results, output_dir)
    plot_top_teams_comparison(results, output_dir)
    
    print("\n" + "="*80)
    print("VISUALIZATION COMPLETE")
    print("="*80)
    print(f"All figures saved to: {output_dir}")
    print("="*80)


if __name__ == '__main__':
    main()

