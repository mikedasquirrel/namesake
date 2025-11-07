"""NBA Comprehensive Collection - Non-Interactive

Collect 1,000+ NBA players across all eras.
Runs with respectful rate limiting to avoid 429 errors.

Usage:
    python scripts/collect_nba_comprehensive.py
"""

import sys
import os
import logging
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from collectors.nba_collector import NBACollector

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nba_collection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Run comprehensive NBA collection."""
    print("\n" + "=" * 70)
    print("NBA COMPREHENSIVE COLLECTION".center(70))
    print("=" * 70 + "\n")
    
    print("Target: 1,000+ players (125+ per era)")
    print("Estimated Time: 2-4 hours (with rate limiting)\n")
    
    start_time = datetime.now()
    
    with app.app_context():
        collector = NBACollector()
        
        logger.info("Starting NBA player collection...")
        
        # Collect 125 per era = 1,000 total
        stats = collector.collect_stratified_sample(target_per_era=125)
        
        print("\n" + "=" * 70)
        print("Collection Complete".center(70))
        print("=" * 70)
        print(f"\nTotal Added: {stats['total_added']}")
        print(f"Total Updated: {stats['total_updated']}")
        print(f"Total Analyzed: {stats['total_analyzed']}")
        print(f"Errors: {stats['errors']}")
        
        print(f"\nEras Collected:")
        for era, era_stats in stats.get('eras_collected', {}).items():
            print(f"  {era}: {era_stats['added']} players")
        
        elapsed = datetime.now() - start_time
        print(f"\nTotal Time: {elapsed}")
        
        logger.info(f"NBA collection complete: {stats['total_added']} players in {elapsed}")


if __name__ == "__main__":
    main()

