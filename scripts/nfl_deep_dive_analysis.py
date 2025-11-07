"""NFL Deep Dive Analysis Script

Comprehensive analysis script that runs all NFL analyzers.

Executes:
1. Statistical analysis (position prediction, performance prediction)
2. Performance analysis (QB, RB, WR, defensive)
3. Position analysis (linguistic patterns by position)
4. Temporal analysis (decade + rule era evolution)

Generates JSON outputs for API consumption and console display.

Usage:
    python scripts/nfl_deep_dive_analysis.py
"""

import sys
import os
import logging
import json
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from analyzers.nfl_statistical_analyzer import NFLStatisticalAnalyzer
from analyzers.nfl_performance_analyzer import NFLPerformanceAnalyzer
from analyzers.nfl_position_analyzer import NFLPositionAnalyzer
from analyzers.nfl_temporal_analyzer import NFLTemporalAnalyzer

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


def save_results(results: dict, output_dir: str = 'analysis_outputs/current'):
    """Save analysis results to JSON.
    
    Args:
        results: Analysis results dictionary
        output_dir: Output directory path
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Save with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    timestamped_file = f"{output_dir}/nfl_analysis_{timestamp}.json"
    
    with open(timestamped_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Also save as "latest" for easy access
    latest_file = f"{output_dir}/nfl_analysis_latest.json"
    with open(latest_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Results saved to {timestamped_file}")
    logger.info(f"Latest results saved to {latest_file}")


def main():
    """Run comprehensive NFL analysis."""
    print_header("NFL Player Name Analysis - Deep Dive")
    
    start_time = datetime.now()
    
    with app.app_context():
        all_results = {
            'timestamp': datetime.utcnow().isoformat(),
            'analysis_type': 'comprehensive_nfl_analysis',
        }
        
        # 1. Statistical Analysis
        print_section("1. Statistical Analysis")
        logger.info("Running statistical analysis...")
        
        try:
            stat_analyzer = NFLStatisticalAnalyzer()
            stat_results = stat_analyzer.run_comprehensive_analysis()
            all_results['statistical_analysis'] = stat_results
            print("✓ Statistical analysis complete")
        except Exception as e:
            logger.error(f"Statistical analysis error: {e}")
            all_results['statistical_analysis'] = {'error': str(e)}
            print(f"✗ Statistical analysis failed: {e}")
        
        # 2. Performance Analysis
        print_section("2. Performance Analysis")
        logger.info("Running performance analysis...")
        
        try:
            perf_analyzer = NFLPerformanceAnalyzer()
            perf_results = perf_analyzer.run_comprehensive_analysis()
            all_results['performance_analysis'] = perf_results
            print("✓ Performance analysis complete")
        except Exception as e:
            logger.error(f"Performance analysis error: {e}")
            all_results['performance_analysis'] = {'error': str(e)}
            print(f"✗ Performance analysis failed: {e}")
        
        # 3. Position Analysis
        print_section("3. Position Analysis")
        logger.info("Running position analysis...")
        
        try:
            pos_analyzer = NFLPositionAnalyzer()
            pos_results = pos_analyzer.run_comprehensive_analysis()
            all_results['position_analysis'] = pos_results
            print("✓ Position analysis complete")
        except Exception as e:
            logger.error(f"Position analysis error: {e}")
            all_results['position_analysis'] = {'error': str(e)}
            print(f"✗ Position analysis failed: {e}")
        
        # 4. Temporal Analysis
        print_section("4. Temporal Analysis")
        logger.info("Running temporal analysis...")
        
        try:
            temp_analyzer = NFLTemporalAnalyzer()
            temp_results = temp_analyzer.run_comprehensive_analysis()
            all_results['temporal_analysis'] = temp_results
            print("✓ Temporal analysis complete")
        except Exception as e:
            logger.error(f"Temporal analysis error: {e}")
            all_results['temporal_analysis'] = {'error': str(e)}
            print(f"✗ Temporal analysis failed: {e}")
        
        # Save results
        print_section("Saving Results")
        save_results(all_results)
        
        # Summary
        print_header("Analysis Complete")
        elapsed_time = datetime.now() - start_time
        print(f"Total Time: {elapsed_time}")
        print(f"\nResults saved to: analysis_outputs/current/nfl_analysis_latest.json")
        
        logger.info(f"NFL deep dive analysis complete in {elapsed_time}")


if __name__ == "__main__":
    main()

