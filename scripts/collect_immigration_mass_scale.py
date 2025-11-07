#!/usr/bin/env python3
"""Collect Immigration Data at Mass Scale - SEMANTIC MEANING ANALYSIS

Collects comprehensive surname dataset across ALL semantic categories:
- Toponymic (place-meaning): Galilei, Romano, Berliner, London, Paris
- Occupational (job-meaning): Smith, Baker, Shoemaker, Ferrari, Fischer
- Descriptive (trait-meaning): Brown, Long, Klein, Rossi, Gross
- Patronymic (father's name): Johnson, O'Brien, Martinez, Ivanov
- Religious (religious-meaning): Christian, Bishop, Cohen, Santo

Total Dataset: ~900 surnames with full etymology and immigration patterns

Usage:
    python3 scripts/collect_immigration_mass_scale.py [--limit-per-category LIMIT]

Args:
    --limit-per-category: Limit per semantic category (default: None = all ~900 surnames)

Author: Michael Smerconish
Date: November 2025
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
from collectors.immigration_collector import ImmigrationCollector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'immigration_collection_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Main collection function."""
    parser = argparse.ArgumentParser(
        description='Collect immigration data - SEMANTIC MEANING ANALYSIS'
    )
    parser.add_argument(
        '--limit-per-category',
        type=int,
        default=None,
        help='Limit per semantic category (default: None = collect all ~900 surnames)'
    )
    
    args = parser.parse_args()
    
    logger.info("="*70)
    logger.info("IMMIGRATION DATA MASS COLLECTION - SEMANTIC ANALYSIS")
    logger.info("="*70)
    logger.info(f"Limit per category: {args.limit_per_category if args.limit_per_category else 'None (collecting all)'}")
    logger.info(f"Expected total: ~900 surnames across 5 semantic categories")
    logger.info(f"Categories: Toponymic, Occupational, Descriptive, Patronymic, Religious")
    logger.info(f"Started at: {datetime.now()}")
    logger.info("="*70)
    
    with app.app_context():
        # Initialize collector
        collector = ImmigrationCollector()
        
        # Run mass collection
        stats = collector.collect_mass_scale(limit_per_category=args.limit_per_category)
        
        # Display results
        logger.info("\n" + "="*70)
        logger.info("COLLECTION COMPLETE")
        logger.info("="*70)
        logger.info(f"Surnames collected: {stats['surnames_collected']}")
        logger.info(f"  - Toponymic: {stats['by_category']['toponymic']}")
        logger.info(f"  - Occupational: {stats['by_category']['occupational']}")
        logger.info(f"  - Descriptive: {stats['by_category']['descriptive']}")
        logger.info(f"  - Patronymic: {stats['by_category']['patronymic']}")
        logger.info(f"  - Religious: {stats['by_category']['religious']}")
        logger.info(f"Surnames classified: {stats['surnames_classified']}")
        logger.info(f"Immigration records: {stats['immigration_records_added']}")
        logger.info(f"Settlement patterns: {stats['settlement_patterns_added']}")
        logger.info(f"Errors: {stats['errors']}")
        logger.info(f"Completed at: {datetime.now()}")
        logger.info("="*70)
        
        # Calculate rates
        if stats['surnames_collected'] > 0:
            success_rate = (stats['surnames_classified'] / stats['surnames_collected']) * 100
            logger.info(f"\nSuccess rate: {success_rate:.1f}%")
        
        if stats['errors'] > 0:
            logger.warning(f"\n⚠️  {stats['errors']} errors occurred during collection")
            logger.warning("Check log file for details")
        else:
            logger.info("\n✅ Collection completed without errors!")
        
        return 0 if stats['errors'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())

