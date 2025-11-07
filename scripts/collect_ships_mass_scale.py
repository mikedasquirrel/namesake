"""Mass Scale Ship Collection

Collects 500-1000 historical ships for comprehensive nominative determinism analysis.

Strategy:
1. Start with bootstrap famous ships (HMS Beagle, Mayflower, etc.)
2. Expand with Wikipedia categories
3. Balance across eras, nations, and types
4. Prioritize ships with documented outcomes

Usage:
    python scripts/collect_ships_mass_scale.py
    
    Options:
    --bootstrap-only    Collect only the curated famous ships (~15 ships)
    --target N          Target number of ships (default: 500)
    --resume            Resume from previous collection
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from core.config import Config
from core.models import db, Ship
from collectors.ship_collector import ShipCollector

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main collection orchestration."""
    parser = argparse.ArgumentParser(description='Mass scale ship data collection')
    parser.add_argument('--bootstrap-only', action='store_true',
                       help='Collect only bootstrap famous ships')
    parser.add_argument('--target', type=int, default=500,
                       help='Target number of ships (default: 500)')
    parser.add_argument('--resume', action='store_true',
                       help='Resume from previous collection')
    
    args = parser.parse_args()
    
    # Initialize Flask app
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        # Create tables
        db.create_all()
        logger.info("Database initialized")
        
        # Initialize collector
        collector = ShipCollector()
        
        # Check current state
        current_count = Ship.query.count()
        logger.info(f"Current ships in database: {current_count}")
        
        if args.resume and current_count > 0:
            logger.info("Resuming from previous collection...")
            remaining = args.target - current_count
            if remaining <= 0:
                logger.info(f"✓ Target already reached ({current_count}/{args.target})")
                return
            logger.info(f"Need {remaining} more ships to reach target of {args.target}")
        
        # Collection strategy
        logger.info("\n" + "="*70)
        logger.info("MASS SCALE SHIP COLLECTION")
        logger.info("="*70)
        logger.info(f"Target: {args.target} ships")
        logger.info(f"Bootstrap only: {args.bootstrap_only}")
        logger.info("="*70 + "\n")
        
        # Phase 1: Bootstrap with famous ships
        logger.info("PHASE 1: Bootstrap Collection (Famous Ships)")
        logger.info("-"*70)
        
        bootstrap_stats = collector.collect_bootstrap_ships()
        
        logger.info(f"\nBootstrap complete:")
        logger.info(f"  Ships added: {bootstrap_stats['ships_added']}")
        logger.info(f"  Ships updated: {bootstrap_stats['ships_updated']}")
        logger.info(f"  Ships analyzed: {bootstrap_stats['ships_analyzed']}")
        logger.info(f"  Errors: {bootstrap_stats['errors']}")
        
        if args.bootstrap_only:
            logger.info("\n✓ Bootstrap-only mode complete")
            return
        
        # Check if we've reached target
        current_count = Ship.query.count()
        if current_count >= args.target:
            logger.info(f"\n✓ Target reached: {current_count}/{args.target} ships")
            return
        
        # Phase 2: Additional collection methods would go here
        # (Wikipedia API, naval databases, etc.)
        logger.info("\n" + "="*70)
        logger.info("COLLECTION COMPLETE")
        logger.info("="*70)
        
        final_count = Ship.query.count()
        logger.info(f"Total ships in database: {final_count}")
        
        # Show breakdown
        from sqlalchemy import func
        
        by_category = db.session.query(
            Ship.name_category,
            func.count(Ship.id)
        ).group_by(Ship.name_category).all()
        
        logger.info("\nBreakdown by category:")
        for category, count in by_category:
            logger.info(f"  {category}: {count}")
        
        by_era = db.session.query(
            Ship.era,
            func.count(Ship.id)
        ).group_by(Ship.era).all()
        
        logger.info("\nBreakdown by era:")
        for era, count in by_era:
            logger.info(f"  {era}: {count}")
        
        by_nation = db.session.query(
            Ship.nation,
            func.count(Ship.id)
        ).group_by(Ship.nation).order_by(func.count(Ship.id).desc()).limit(10).all()
        
        logger.info("\nTop nations:")
        for nation, count in by_nation:
            logger.info(f"  {nation}: {count}")
        
        logger.info("\n" + "="*70)
        logger.info("NEXT STEPS")
        logger.info("="*70)
        logger.info("1. Run analysis: python scripts/ship_deep_dive_analysis.py")
        logger.info("2. View results: http://localhost:<port>/ships")
        logger.info("3. Check API: http://localhost:<port>/api/ships/comprehensive-report")
        logger.info("="*70)


if __name__ == "__main__":
    main()

