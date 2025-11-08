#!/usr/bin/env python3
"""
Comprehensive Adult Film Performer Data Collection
Collects stage name and career data from publicly documented sources
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from collectors.adult_film_collector import AdultFilmCollector
from core.models import db
from app import app
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Run comprehensive data collection"""
    
    print("\n" + "="*70)
    print("ADULT FILM PERFORMER STAGE NAME ANALYSIS")
    print("Data Collection - Publicly Documented Performers")
    print("="*70)
    print()
    
    with app.app_context():
        # Initialize database
        db.create_all()
        
        collector = AdultFilmCollector()
        
        # Collect across all eras
        print("Starting stratified collection across 4 eras...")
        print()
        
        stats = collector.collect_stratified_sample(
            target_total=40,  # 10 per era from our curated lists
            eras=['golden_age', 'video_era', 'internet_era', 'streaming_era']
        )
        
        print()
        print("="*70)
        print("COLLECTION COMPLETE")
        print("="*70)
        print(f"Total collected: {stats['total_collected']}")
        print()
        print("By Era:")
        for era, count in stats['by_era'].items():
            print(f"  {era}: {count}")
        
        if stats['errors']:
            print()
            print("Errors encountered:")
            for error in stats['errors']:
                print(f"  - {error}")
        
        print()
        print("Database updated. View at /adult-film")
        print("="*70)
        print()


if __name__ == "__main__":
    main()

