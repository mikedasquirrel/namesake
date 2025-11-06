#!/usr/bin/env python3
"""
Band Data Collection Script

Simplified wrapper for collecting band data from MusicBrainz and Last.fm.
Run this script to populate the band database.

Usage:
    python3 scripts/collect_bands.py [--target TARGET] [--test]

Options:
    --target TARGET    Number of bands per decade (default: 600)
    --test            Test mode: collect 50 per decade
"""

import sys
import os
import logging
import argparse
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from core.config import Config
from core.models import db, Band, BandAnalysis
from collectors.band_collector import BandCollector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main collection function"""
    parser = argparse.ArgumentParser(description='Collect band data from MusicBrainz and Last.fm')
    parser.add_argument('--target', type=int, default=600,
                       help='Number of bands per decade (default: 600)')
    parser.add_argument('--test', action='store_true',
                       help='Test mode: collect only 50 bands per decade')
    
    args = parser.parse_args()
    
    target = 50 if args.test else args.target
    
    # Initialize Flask app for database context
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        logger.info("Database tables ready")
        
        # Check existing data
        existing_count = Band.query.count()
        logger.info(f"Current database: {existing_count} bands")
        
        if existing_count > 0:
            response = input(f"\nDatabase already has {existing_count} bands. Continue? (y/n): ")
            if response.lower() != 'y':
                logger.info("Collection cancelled")
                return
        
        # Check Last.fm API key
        if not hasattr(Config, 'LASTFM_API_KEY') or not Config.LASTFM_API_KEY:
            logger.warning("="*60)
            logger.warning("Last.fm API key not found!")
            logger.warning("Popularity metrics will be limited.")
            logger.warning("Get a free key at: https://www.last.fm/api/account/create")
            logger.warning("Add to core/config.py: LASTFM_API_KEY = 'your_key_here'")
            logger.warning("="*60)
            response = input("\nContinue without Last.fm? (y/n): ")
            if response.lower() != 'y':
                logger.info("Collection cancelled")
                return
        
        # Initialize collector
        logger.info("="*60)
        logger.info("BAND DATA COLLECTION")
        logger.info("="*60)
        logger.info(f"Target: {target} bands per decade")
        logger.info(f"Total target: {target * 8} bands (1950s-2020s)")
        logger.info(f"Estimated time: {(target * 8) // 100} hours")
        logger.info("="*60)
        
        collector = BandCollector()
        
        # Start collection
        start_time = datetime.now()
        
        try:
            stats = collector.collect_stratified_sample(target_per_decade=target)
            
            # Print summary
            elapsed = datetime.now() - start_time
            logger.info("\n" + "="*60)
            logger.info("COLLECTION COMPLETE")
            logger.info("="*60)
            logger.info(f"Total added: {stats['total_added']}")
            logger.info(f"Total updated: {stats['total_updated']}")
            logger.info(f"Total analyzed: {stats['total_analyzed']}")
            logger.info(f"Errors: {stats['errors']}")
            logger.info(f"Time elapsed: {elapsed}")
            logger.info("\nDecade breakdown:")
            for decade, decade_stats in stats['decades_collected'].items():
                logger.info(f"  {decade}: {decade_stats['added']} added, {decade_stats['updated']} updated")
            logger.info("="*60)
            
            # Next steps
            logger.info("\nNext steps:")
            logger.info("1. Run analysis: python3 analyzers/band_temporal_analyzer.py")
            logger.info("2. View dashboard: python3 app.py → http://localhost:PORT/bands")
            
        except KeyboardInterrupt:
            logger.info("\n\nCollection interrupted by user")
            logger.info(f"Collected data has been saved to database")
            
        except Exception as e:
            logger.error(f"\n\nCollection failed: {e}")
            logger.error("Check logs for details")
            raise


if __name__ == '__main__':
    main()

