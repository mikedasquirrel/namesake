#!/usr/bin/env python3
"""Band_Members Comprehensive Collection

Collect data for band_members nominative determinism research.

Usage:
    python scripts/collect_band_members_comprehensive.py

Generated: 2025-11-07
"""

import sys
import os
import logging
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from collectors.band_members_collector import BandMembersCollector

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('band_members_collection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Run comprehensive band_members collection."""
    print("\n" + "=" * 70)
    print("BAND_MEMBERS COMPREHENSIVE COLLECTION".center(70))
    print("=" * 70 + "\n")
    
    start_time = datetime.now()
    
    with app.app_context():
        collector = BandMembersCollector()
        
        logger.info("Starting band_members data collection...")
        
        # Customize collection parameters
        stats = collector.collect_sample(target_size=1000)
        
        print("\n" + "=" * 70)
        print("Collection Complete".center(70))
        print("=" * 70)
        print(f"\nTotal Collected: {stats['total_collected']}")
        print(f"Total Updated: {stats['total_updated']}")
        print(f"Errors: {stats.get('total_errors', 0)}")
        
        elapsed = datetime.now() - start_time
        print(f"\nTotal Time: {elapsed}")
        
        logger.info(f"band_members collection complete: {stats['total_collected']} records in {elapsed}")


if __name__ == "__main__":
    main()
