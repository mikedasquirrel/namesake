"""Band Comprehensive Collection - Non-Interactive

Collect 500+ bands/artists across genres.

Usage:
    python scripts/collect_bands_comprehensive.py
"""

import sys
import os
import logging
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from collectors.band_collector import BandCollector

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('band_collection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Run comprehensive band collection."""
    print("\n" + "=" * 70)
    print("BAND COMPREHENSIVE COLLECTION".center(70))
    print("=" * 70 + "\n")
    
    print("Target: 500+ bands across genres")
    print("Estimated Time: 1-2 hours\n")
    
    start_time = datetime.now()
    
    with app.app_context():
        collector = BandCollector()
        
        logger.info("Starting band collection...")
        
        # Collect across genres
        stats = collector.collect_stratified_sample(target_per_genre=100)
        
        print("\n" + "=" * 70)
        print("Collection Complete".center(70))
        print("=" * 70)
        print(f"\nTotal Added: {stats.get('total_added', 0)}")
        print(f"Total Analyzed: {stats.get('total_analyzed', 0)}")
        print(f"Errors: {stats.get('errors', 0)}")
        
        elapsed = datetime.now() - start_time
        print(f"\nTotal Time: {elapsed}")
        
        logger.info(f"Band collection complete in {elapsed}")


if __name__ == "__main__":
    main()
