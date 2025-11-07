"""NBA Shooting Percentage Deep Dive Analysis

Comprehensive analysis script for exploring the relationship between player names
and shooting performance (Free Throw % and 3-Point %).

This script:
1. Loads all NBA player data with shooting statistics
2. Runs comprehensive shooting correlation analysis
3. Identifies elite vs poor shooters
4. Builds predictive models
5. Generates visualizations and reports
6. Saves results for web display

Usage:
    python scripts/nba_shooting_deep_dive.py
"""

import sys
import os
import logging
import json
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from core.models import db, NBAPlayer, NBAPlayerAnalysis
from analyzers.nba_shooting_analyzer import NBAShootingAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_header(text: str, char: str = "="):
    """Print formatted header."""
    width = 80
    print(f"\n{char * width}")
    print(f"{text.center(width)}")
    print(f"{char * width}\n")


def print_section(text: str):
    """Print section header."""
    print(f"\n{'─' * 80}")
    print(f"  {text}")
    print(f"{'─' * 80}")


def format_percentage(value: float) -> str:
    """Format percentage for display."""
    return f"{value * 100:.1f}%" if value else "N/A"


def format_correlation(value: float) -> str:
    """Format correlation for display."""
    return f"{value:+.3f}" if value else "N/A"


def print_dataset_summary(summary: dict):
    """Print dataset summary."""
    print_section("Dataset Summary")
    
    print(f"Total Players: {summary['total_players']}")
    print(f"Players with FT Data: {summary['players_with_ft_data']}")
    print(f"Players with 3PT Data: {summary['players_with_3pt_data']}")
    print(f"Average Games Played: {summary['avg_games_played']:.0f}")
    
    if summary.get('ft_stats'):
        ft = summary['ft_stats']
        print(f"\nFree Throw Statistics:")
        print(f"  Mean: {format_percentage(ft['mean'])}")
        print(f"  Median: {format_percentage(ft['median'])}")
        print(f"  Range: {format_percentage(ft['min'])} - {format_percentage(ft['max'])}")
        print(f"  Elite Shooters (≥85%): {ft['elite_count']}")
        print(f"  Poor Shooters (<65%): {ft['poor_count']}")
    
    if summary.get('three_pt_stats'):
        three_pt = summary['three_pt_stats']
        print(f"\n3-Point Statistics:")
        print(f"  Mean: {format_percentage(three_pt['mean'])}")
        print(f"  Median: {format_percentage(three_pt['median'])}")
        print(f"  Range: {format_percentage(three_pt['min'])} - {format_percentage(three_pt['max'])}")
        print(f"  Elite Shooters (≥38%): {three_pt['elite_count']}")
        print(f"  Poor Shooters (<30%): {three_pt['poor_count']}")


def print_ft_analysis(ft_analysis: dict):
    """Print free throw analysis results."""
    print_section("Free Throw Percentage Analysis")
    
    print(f"Sample Size: {ft_analysis['sample_size']}")
    print(f"Average FT%: {format_percentage(ft_analysis['avg_ft_percentage'])}")
    
    sig_corr = ft_analysis.get('significant_correlations', [])
    
    if sig_corr:
        print(f"\n✓ Found {len(sig_corr)} significant correlations")
        
        print("\nTop Positive Correlates (Higher = Better FT%):")
        for corr in ft_analysis.get('top_positive_correlates', [])[:5]:
            print(f"  • {corr['feature']:30s} {format_correlation(corr['correlation'])} (p={corr['p_value']:.4f})")
            print(f"    → {corr['interpretation']}")
        
        print("\nTop Negative Correlates (Lower = Better FT%):")
        for corr in ft_analysis.get('top_negative_correlates', [])[:5]:
            print(f"  • {corr['feature']:30s} {format_correlation(corr['correlation'])} (p={corr['p_value']:.4f})")
            print(f"    → {corr['interpretation']}")
    else:
        print("\n✗ No significant correlations found")


def print_three_pt_analysis(three_pt_analysis: dict):
    """Print 3-point analysis results."""
    print_section("3-Point Percentage Analysis")
    
    print(f"Sample Size: {three_pt_analysis['sample_size']}")
    print(f"Average 3PT%: {format_percentage(three_pt_analysis['avg_three_point_percentage'])}")
    
    sig_corr = three_pt_analysis.get('significant_correlations', [])
    
    if sig_corr:
        print(f"\n✓ Found {len(sig_corr)} significant correlations")
        
        print("\nTop Positive Correlates (Higher = Better 3PT%):")
        for corr in three_pt_analysis.get('top_positive_correlates', [])[:5]:
            print(f"  • {corr['feature']:30s} {format_correlation(corr['correlation'])} (p={corr['p_value']:.4f})")
            print(f"    → {corr['interpretation']}")
        
        print("\nTop Negative Correlates (Lower = Better 3PT%):")
        for corr in three_pt_analysis.get('top_negative_correlates', [])[:5]:
            print(f"  • {corr['feature']:30s} {format_correlation(corr['correlation'])} (p={corr['p_value']:.4f})")
            print(f"    → {corr['interpretation']}")
    else:
        print("\n✗ No significant correlations found")


def print_elite_vs_poor(elite_vs_poor: dict):
    """Print elite vs poor shooter comparison."""
    print_section("Elite vs Poor Shooters Comparison")
    
    # Free throw comparison
    if 'ft_comparison' in elite_vs_poor and elite_vs_poor['ft_comparison']:
        ft_comp = elite_vs_poor['ft_comparison']
        
        print(f"\nFree Throw Shooters:")
        print(f"  Elite (≥85%): {ft_comp['elite_count']} players, Avg: {format_percentage(ft_comp['elite_avg_ft'])}")
        print(f"  Poor (<65%): {ft_comp['poor_count']} players, Avg: {format_percentage(ft_comp['poor_avg_ft'])}")
        
        # Find significant differences
        sig_diffs = [
            (k, v) for k, v in ft_comp.get('feature_differences', {}).items()
            if v.get('significant', False)
        ]
        
        if sig_diffs:
            print("\n  Significant Linguistic Differences:")
            # Sort by absolute difference
            sig_diffs.sort(key=lambda x: abs(x[1]['difference']), reverse=True)
            
            for feature, diff in sig_diffs[:5]:
                pct_diff = diff['percent_difference']
                arrow = "↑" if diff['difference'] > 0 else "↓"
                print(f"    • {feature:30s} {arrow} {abs(pct_diff):5.1f}% difference (p={diff['p_value']:.4f})")
        
        # Top elite shooters
        if ft_comp.get('top_elite_shooters'):
            print("\n  Top Elite Free Throw Shooters:")
            for player in ft_comp['top_elite_shooters'][:5]:
                print(f"    {player['name']:30s} {format_percentage(player['ft_percentage'])}")
    
    # 3-point comparison
    if 'three_pt_comparison' in elite_vs_poor and elite_vs_poor['three_pt_comparison']:
        three_pt_comp = elite_vs_poor['three_pt_comparison']
        
        print(f"\n3-Point Shooters:")
        print(f"  Elite (≥38%): {three_pt_comp['elite_count']} players, Avg: {format_percentage(three_pt_comp['elite_avg_3pt'])}")
        print(f"  Poor (<30%): {three_pt_comp['poor_count']} players, Avg: {format_percentage(three_pt_comp['poor_avg_3pt'])}")
        
        # Find significant differences
        sig_diffs = [
            (k, v) for k, v in three_pt_comp.get('feature_differences', {}).items()
            if v.get('significant', False)
        ]
        
        if sig_diffs:
            print("\n  Significant Linguistic Differences:")
            sig_diffs.sort(key=lambda x: abs(x[1]['difference']), reverse=True)
            
            for feature, diff in sig_diffs[:5]:
                pct_diff = diff['percent_difference']
                arrow = "↑" if diff['difference'] > 0 else "↓"
                print(f"    • {feature:30s} {arrow} {abs(pct_diff):5.1f}% difference (p={diff['p_value']:.4f})")
        
        # Top elite shooters
        if three_pt_comp.get('top_elite_shooters'):
            print("\n  Top Elite 3-Point Shooters:")
            for player in three_pt_comp['top_elite_shooters'][:5]:
                print(f"    {player['name']:30s} {format_percentage(player['three_point_percentage'])}")


def print_predictive_models(models: dict):
    """Print predictive model results."""
    print_section("Predictive Models")
    
    # FT model
    if 'ft_model' in models and models['ft_model']:
        ft_model = models['ft_model']
        print(f"\nFree Throw Prediction Model:")
        print(f"  Sample Size: {ft_model['sample_size']}")
        print(f"  R² Score: {ft_model['r2_score']:.3f}")
        print(f"  RMSE: {ft_model['rmse']:.4f} ({format_percentage(ft_model['rmse'])})")
        
        print("\n  Top Predictive Features:")
        for feat in ft_model['top_features']:
            print(f"    • {feat['feature']:30s} Importance: {feat['importance']:.3f}")
    
    # 3PT model
    if 'three_pt_model' in models and models['three_pt_model']:
        three_pt_model = models['three_pt_model']
        print(f"\n3-Point Prediction Model:")
        print(f"  Sample Size: {three_pt_model['sample_size']}")
        print(f"  R² Score: {three_pt_model['r2_score']:.3f}")
        print(f"  RMSE: {three_pt_model['rmse']:.4f} ({format_percentage(three_pt_model['rmse'])})")
        
        print("\n  Top Predictive Features:")
        for feat in three_pt_model['top_features']:
            print(f"    • {feat['feature']:30s} Importance: {feat['importance']:.3f}")


def print_key_findings(findings: list):
    """Print key findings."""
    print_section("Key Findings Summary")
    
    if findings:
        for i, finding in enumerate(findings, 1):
            print(f"\n{i}. {finding['category']}")
            print(f"   {finding['finding']}")
            print(f"   → {finding['detail']}")
            if finding.get('interpretation'):
                print(f"   → {finding['interpretation']}")
    else:
        print("No key findings generated.")


def save_results(results: dict, output_path: str):
    """Save results to JSON file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Results saved to: {output_path}")


def main():
    """Run complete shooting analysis."""
    print_header("NBA SHOOTING PERCENTAGE DEEP DIVE ANALYSIS")
    
    with app.app_context():
        # Initialize analyzer
        logger.info("Initializing shooting analyzer...")
        analyzer = NBAShootingAnalyzer()
        
        # Load dataset
        logger.info("Loading shooting dataset...")
        df = analyzer.get_shooting_dataset()
        
        if len(df) < 30:
            logger.error("Insufficient data for analysis. Need at least 30 players with shooting stats.")
            print("\n❌ ERROR: Not enough data")
            print(f"Found only {len(df)} players with shooting stats")
            print("Please run the NBA collector first to gather more data.")
            return
        
        # Run comprehensive analysis
        logger.info("Running comprehensive shooting analysis...")
        results = analyzer.analyze_comprehensive_shooting(df)
        
        # Print results
        print_dataset_summary(results['dataset_summary'])
        print_ft_analysis(results['ft_analysis'])
        print_three_pt_analysis(results['three_pt_analysis'])
        
        if 'elite_vs_poor' in results:
            print_elite_vs_poor(results['elite_vs_poor'])
        
        if 'predictive_models' in results:
            print_predictive_models(results['predictive_models'])
        
        if 'key_findings' in results:
            print_key_findings(results['key_findings'])
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f'analysis_outputs/current/nba_shooting_analysis_{timestamp}.json'
        save_results(results, output_path)
        
        # Also save as latest
        latest_path = 'analysis_outputs/current/nba_shooting_analysis_latest.json'
        save_results(results, latest_path)
        
        print_header("ANALYSIS COMPLETE", "=")
        print(f"\nResults saved to:")
        print(f"  • {output_path}")
        print(f"  • {latest_path}")
        print("\nNext steps:")
        print("  1. Review findings in the JSON output")
        print("  2. Check the web dashboard at /nba for visualizations")
        print("  3. Run additional position-specific or era-specific analyses if needed")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAnalysis interrupted by user.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        print(f"\n❌ ERROR: {e}")
        sys.exit(1)

