"""NFL Collector Test Script

Small test collection (5-10 players per position) for validation.

Usage:
    python scripts/test_nfl_collector.py
"""

import sys
import os
import logging

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from collectors.nfl_collector import NFLCollector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Run test collection."""
    print("\n" + "=" * 60)
    print("NFL Collector Test".center(60))
    print("=" * 60 + "\n")
    
    logger.info("Starting test collection...")
    
    with app.app_context():
        collector = NFLCollector()
        
        # Test with small sample
        stats = collector.test_collection(num_players=5)
        
        print("\n" + "=" * 60)
        print("Test Complete".center(60))
        print("=" * 60)
        print(f"\nTotal Added: {stats['total_added']}")
        print(f"Total Updated: {stats['total_updated']}")
        print(f"Total Analyzed: {stats['total_analyzed']}")
        print(f"Errors: {stats['errors']}")
        
        logger.info("Test collection complete")


if __name__ == "__main__":
    main()

