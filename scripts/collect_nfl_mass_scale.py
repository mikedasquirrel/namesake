"""NFL Mass Scale Collection Script

Stratified collection across all positions and eras.
Target: 5,000+ players (balanced across positions)

Usage:
    python scripts/collect_nfl_mass_scale.py

Options:
    --target-per-position: Number of players per major position (default 200)
    --target-per-era: Number of players per era (default 500)
"""

import sys
import os
import logging
import argparse
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from core.models import db
from collectors.nfl_collector import NFLCollector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nfl_collection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Collect NFL players at mass scale')
    parser.add_argument('--target-per-position', type=int, default=200,
                       help='Target number of players per major position')
    parser.add_argument('--target-per-era', type=int, default=500,
                       help='Target number of players per era')
    return parser.parse_args()


def print_header(text: str):
    """Print formatted header."""
    width = 80
    print(f"\n{'=' * width}")
    print(f"{text.center(width)}")
    print(f"{'=' * width}\n")


def main():
    """Main collection function."""
    args = parse_args()
    
    print_header("NFL Player Mass Scale Collection")
    
    logger.info("Starting NFL player collection...")
    logger.info(f"Target: {args.target_per_position} per position, {args.target_per_era} per era")
    
    start_time = datetime.now()
    
    with app.app_context():
        # Initialize collector
        collector = NFLCollector()
        
        # Run stratified collection
        stats = collector.collect_stratified_sample(
            target_per_position=args.target_per_position,
            target_per_era=args.target_per_era
        )
        
        # Print results
        print_header("Collection Complete")
        
        print(f"Total Players Added: {stats['total_added']}")
        print(f"Total Players Updated: {stats['total_updated']}")
        print(f"Total Analyzed: {stats['total_analyzed']}")
        print(f"Errors: {stats['errors']}")
        
        print(f"\nPositions Collected:")
        for position, pos_stats in stats.get('positions_collected', {}).items():
            print(f"  {position}: {pos_stats['added']} added, {pos_stats['updated']} updated")
        
        elapsed_time = datetime.now() - start_time
        print(f"\nTotal Time: {elapsed_time}")
        
        logger.info(f"Collection complete: {stats['total_added']} added, {stats['total_updated']} updated")


if __name__ == "__main__":
    main()

