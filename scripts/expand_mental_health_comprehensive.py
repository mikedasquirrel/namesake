"""Expand Mental Health Data - Non-Interactive

Comprehensive mental health term collection WITHOUT user prompts.
Collects 500+ terms automatically.

Usage:
    python scripts/expand_mental_health_comprehensive.py
"""

import sys
import os
import logging
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from collectors.mental_health_collector import MentalHealthCollector

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mental_health_collection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Run comprehensive mental health collection."""
    print("\n" + "=" * 70)
    print("MENTAL HEALTH COMPREHENSIVE COLLECTION".center(70))
    print("=" * 70 + "\n")
    
    start_time = datetime.now()
    
    with app.app_context():
        collector = MentalHealthCollector()
        
        logger.info("Starting comprehensive mental health collection...")
        
        # Run collection (no user input required)
        stats = collector.collect_all_data()
        
        print("\n" + "=" * 70)
        print("Collection Complete".center(70))
        print("=" * 70)
        print(f"\nDiagnoses Added: {stats['diagnoses_added']}")
        print(f"Medications Added: {stats['medications_added']}")
        print(f"Total Terms: {stats['total_terms_added']}")
        print(f"Analyses Complete: {stats['analyses_added']}")
        
        if stats['errors']:
            print(f"\nErrors: {len(stats['errors'])}")
        
        elapsed = datetime.now() - start_time
        print(f"\nTotal Time: {elapsed}")
        
        logger.info(f"Mental health collection complete: {stats['total_terms_added']} terms in {elapsed}")


if __name__ == "__main__":
    main()

