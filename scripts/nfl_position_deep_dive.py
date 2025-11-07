"""NFL Position-Specific Deep Dive

Position-specific detailed analysis.
Compares positions within same era and across-era position evolution.

Usage:
    python scripts/nfl_position_deep_dive.py [position]

Examples:
    python scripts/nfl_position_deep_dive.py QB
    python scripts/nfl_position_deep_dive.py RB
    python scripts/nfl_position_deep_dive.py WR
"""

import sys
import os
import logging
import json
import argparse
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from analyzers.nfl_performance_analyzer import NFLPerformanceAnalyzer
from analyzers.nfl_position_analyzer import NFLPositionAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Position-specific NFL analysis')
    parser.add_argument('position', nargs='?', default='QB',
                       help='Position to analyze (QB, RB, WR, TE, DE, LB, CB, S)')
    return parser.parse_args()


def print_header(text: str, char: str = "="):
    """Print formatted header."""
    width = 80
    print(f"\n{char * width}")
    print(f"{text.center(width)}")
    print(f"{char * width}\n")


def main():
    """Run position-specific analysis."""
    args = parse_args()
    position = args.position.upper()
    
    print_header(f"NFL {position} Position Analysis")
    
    start_time = datetime.now()
    
    with app.app_context():
        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'position': position,
        }
        
        # Performance analyzer
        perf_analyzer = NFLPerformanceAnalyzer()
        
        # Position-specific analysis based on position
        if position == 'QB':
            logger.info("Running QB-specific analysis...")
            qb_results = perf_analyzer.analyze_qb_performance()
            results['analysis'] = qb_results
            
        elif position == 'RB':
            logger.info("Running RB-specific analysis...")
            rb_results = perf_analyzer.analyze_rb_performance()
            results['analysis'] = rb_results
            
        elif position in ['WR', 'TE']:
            logger.info("Running WR/TE-specific analysis...")
            wr_results = perf_analyzer.analyze_wr_performance()
            results['analysis'] = wr_results
            
        elif position in ['DE', 'DT', 'NT', 'LB', 'CB', 'S']:
            logger.info("Running defensive-specific analysis...")
            def_results = perf_analyzer.analyze_defensive_performance()
            results['analysis'] = def_results
            
        else:
            print(f"Unknown position: {position}")
            print("Supported positions: QB, RB, WR, TE, DE, LB, CB, S")
            return
        
        # Save results
        output_dir = 'analysis_outputs/current'
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        output_file = f"{output_dir}/nfl_{position.lower()}_analysis.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print_header("Analysis Complete")
        elapsed_time = datetime.now() - start_time
        print(f"Total Time: {elapsed_time}")
        print(f"\nResults saved to: {output_file}")
        
        logger.info(f"{position} analysis complete in {elapsed_time}")


if __name__ == "__main__":
    main()

