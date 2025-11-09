"""Run Sports Roster Locality & Demographic Composition Analysis

Executes the full analysis pipeline using the Domain Analysis Template System.

Usage:
    python scripts/run_sports_roster_locality_analysis.py [--mode MODE]

Modes:
    new: Fresh data collection and analysis (default)
    reanalyze: Use existing data, rerun analysis

Author: Michael Smerconish
Date: November 2025
"""

import sys
import argparse
import logging
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app
from analyzers.sports_roster_locality_analyzer import SportsRosterLocalityAnalyzer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'sports_roster_locality_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def setup_output_directory():
    """Create output directory if it doesn't exist."""
    output_dir = Path('analysis_outputs/sports_roster_locality')
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Output directory: {output_dir}")
    return output_dir


def save_results(results: dict, output_dir: Path):
    """Save analysis results to JSON file."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = output_dir / f'full_analysis_{timestamp}.json'
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"Results saved to: {output_file}")
    
    # Also save a "latest" version
    latest_file = output_dir / 'full_analysis_latest.json'
    with open(latest_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"Latest results saved to: {latest_file}")
    
    return output_file


def generate_summary_report(results: dict, output_dir: Path):
    """Generate human-readable summary report."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = output_dir / f'summary_report_{timestamp}.txt'
    
    with open(report_file, 'w') as f:
        f.write("="*80 + "\n")
        f.write("SPORTS ROSTER LOCALITY & DEMOGRAPHIC COMPOSITION ANALYSIS\n")
        f.write("="*80 + "\n\n")
        
        f.write(f"Analysis Date: {results.get('timestamp', 'N/A')}\n")
        f.write(f"Sample Size: {results.get('sample_size', 0):,} players\n")
        f.write(f"Teams Analyzed: {results.get('team_count', 0)}\n\n")
        
        f.write("="*80 + "\n")
        f.write("SPORT-LEVEL AGGREGATES\n")
        f.write("="*80 + "\n\n")
        
        sport_aggs = results.get('sport_aggregates', {})
        for sport in ['nfl', 'nba', 'mlb']:
            if sport in sport_aggs:
                agg = sport_aggs[sport]
                f.write(f"{sport.upper()}:\n")
                f.write(f"  Teams: {agg.get('team_count', 0)}\n")
                f.write(f"  Mean Americanness: {agg.get('mean_americanness', 0):.1f}\n")
                f.write(f"  Mean Melodiousness: {agg.get('mean_melodiousness', 0):.1f}\n")
                f.write(f"  Demographics:\n")
                f.write(f"    Anglo: {agg.get('mean_demo_anglo', 0):.1f}%\n")
                f.write(f"    Latino: {agg.get('mean_demo_latino', 0):.1f}%\n")
                f.write(f"    Asian: {agg.get('mean_demo_asian', 0):.1f}%\n")
                f.write(f"    Black: {agg.get('mean_demo_black', 0):.1f}%\n\n")
        
        f.write("="*80 + "\n")
        f.write("BASELINE COMPARISONS\n")
        f.write("="*80 + "\n\n")
        
        comparison_results = results.get('comparison_results', {})
        vs_random = comparison_results.get('vs_random_baseline', {})
        
        am_test = vs_random.get('americanness_ttest', {})
        f.write(f"Americanness vs Random Baseline:\n")
        f.write(f"  t-statistic: {am_test.get('statistic', 0):.2f}\n")
        f.write(f"  p-value: {am_test.get('pvalue', 1):.4f}\n")
        f.write(f"  Significant: {am_test.get('significant', False)}\n\n")
        
        mel_test = vs_random.get('melodiousness_ttest', {})
        f.write(f"Melodiousness vs Random Baseline:\n")
        f.write(f"  t-statistic: {mel_test.get('statistic', 0):.2f}\n")
        f.write(f"  p-value: {mel_test.get('pvalue', 1):.4f}\n")
        f.write(f"  Significant: {mel_test.get('significant', False)}\n\n")
        
        effect_sizes = comparison_results.get('effect_sizes', {})
        f.write(f"Effect Sizes (Cohen's d):\n")
        f.write(f"  Americanness: {effect_sizes.get('americanness_cohens_d', 0):.2f}\n")
        f.write(f"  Melodiousness: {effect_sizes.get('melodiousness_cohens_d', 0):.2f}\n\n")
        
        demo_tests = comparison_results.get('demographic_tests', {})
        f.write(f"Demographic Distribution Test:\n")
        f.write(f"  Chi-square: {demo_tests.get('chi_square', 0):.2f}\n")
        f.write(f"  p-value: {demo_tests.get('pvalue', 1):.4f}\n")
        f.write(f"  Cramer's V: {demo_tests.get('cramers_v', 0):.3f}\n")
        f.write(f"  Significant: {demo_tests.get('significant', False)}\n\n")
        
        f.write("="*80 + "\n")
        f.write("SPORT CHARACTERISTIC CORRELATIONS\n")
        f.write("="*80 + "\n\n")
        
        correlations = results.get('sport_correlations', {})
        f.write(f"Contact Level vs Americanness: r = {correlations.get('contact_vs_americanness', 0):.3f}\n")
        f.write(f"Precision vs Melodiousness: r = {correlations.get('precision_vs_melodiousness', 0):.3f}\n")
        f.write(f"Speed vs Complexity: r = {correlations.get('speed_vs_complexity', 0):.3f}\n\n")
        
        f.write("="*80 + "\n")
        f.write("TOP 10 MOST AMERICAN ROSTERS\n")
        f.write("="*80 + "\n\n")
        
        rosters = results.get('roster_analyses', [])
        top_american = sorted(rosters, key=lambda x: x.get('americanness_score', 0), reverse=True)[:10]
        
        for i, roster in enumerate(top_american, 1):
            f.write(f"{i}. {roster.get('team_name', 'Unknown')} ({roster.get('sport', '').upper()}): {roster.get('americanness_score', 0):.1f}\n")
        
        f.write("\n" + "="*80 + "\n")
        f.write("TOP 10 MOST MELODIOUS ROSTERS\n")
        f.write("="*80 + "\n\n")
        
        top_melodious = sorted(rosters, key=lambda x: x.get('melodiousness_score', 0), reverse=True)[:10]
        
        for i, roster in enumerate(top_melodious, 1):
            f.write(f"{i}. {roster.get('team_name', 'Unknown')} ({roster.get('sport', '').upper()}): {roster.get('melodiousness_score', 0):.1f}\n")
        
        f.write("\n" + "="*80 + "\n")
        f.write("ANALYSIS COMPLETE\n")
        f.write("="*80 + "\n")
    
    logger.info(f"Summary report saved to: {report_file}")
    
    return report_file


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Run Sports Roster Locality & Demographic Composition Analysis'
    )
    parser.add_argument(
        '--mode',
        choices=['new', 'reanalyze'],
        default='new',
        help='Analysis mode: new (collect fresh data) or reanalyze (use existing data)'
    )
    
    args = parser.parse_args()
    
    logger.info("="*80)
    logger.info("SPORTS ROSTER LOCALITY & DEMOGRAPHIC COMPOSITION ANALYSIS")
    logger.info("="*80)
    logger.info(f"Mode: {args.mode}")
    logger.info(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*80 + "\n")
    
    # Setup output directory
    output_dir = setup_output_directory()
    
    # Initialize Flask app context
    logger.info("Initializing Flask app context...")
    app = create_app()
    
    with app.app_context():
        try:
            # Initialize analyzer
            logger.info("Initializing analyzer...")
            analyzer = SportsRosterLocalityAnalyzer(mode=args.mode)
            
            # Run full pipeline
            logger.info("Running full analysis pipeline...\n")
            results = analyzer.run_full_pipeline()
            
            # Save results
            logger.info("\nSaving results...")
            output_file = save_results(results, output_dir)
            
            # Generate summary report
            logger.info("Generating summary report...")
            report_file = generate_summary_report(results, output_dir)
            
            # Print summary
            logger.info("\n" + "="*80)
            logger.info("ANALYSIS COMPLETE")
            logger.info("="*80)
            logger.info(f"Teams analyzed: {results.get('team_count', 0)}")
            logger.info(f"Players analyzed: {results.get('sample_size', 0):,}")
            logger.info(f"Rosters processed: {results.get('rosters_analyzed', 0)}")
            logger.info(f"\nOutput files:")
            logger.info(f"  - Full results: {output_file}")
            logger.info(f"  - Summary report: {report_file}")
            logger.info("="*80)
            
            # Check for errors
            if results.get('errors'):
                logger.warning(f"\n{len(results['errors'])} errors occurred during analysis:")
                for error in results['errors'][:5]:
                    logger.warning(f"  - {error}")
                if len(results['errors']) > 5:
                    logger.warning(f"  ... and {len(results['errors']) - 5} more")
            
            # Print key findings
            if 'comparison_results' in results:
                logger.info("\nKey Findings:")
                comparison = results['comparison_results']
                vs_random = comparison.get('vs_random_baseline', {})
                
                am_test = vs_random.get('americanness_ttest', {})
                if am_test.get('significant'):
                    logger.info(f"  ✓ Rosters differ significantly from American baseline in americanness (p={am_test.get('pvalue', 1):.4f})")
                
                demo_test = comparison.get('demographic_tests', {})
                if demo_test.get('significant'):
                    logger.info(f"  ✓ Demographic distribution differs from US Census (χ²={demo_test.get('chi_square', 0):.1f}, p={demo_test.get('pvalue', 1):.4f})")
            
            logger.info("\nDone!")
            
            return 0
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            logger.exception("Full traceback:")
            return 1


if __name__ == '__main__':
    sys.exit(main())

