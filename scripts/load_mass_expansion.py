"""Load Mass Ship Expansion - 400+ Additional Ships

Loads the mass expansion dataset to bring total to 800+ ships.
This will give ADEQUATE POWER for all statistical tests.

Usage:
    python scripts/load_mass_expansion.py
"""

import sys
import os
import logging
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from core.config import Config
from core.models import db, Ship
from collectors.ship_collector import ShipCollector
from data.ships_mass_expansion import get_mass_expansion_ships

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    """Load mass expansion ships."""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        # Get current count
        before_count = Ship.query.count()
        logger.info("="*70)
        logger.info("MASS SHIP EXPANSION")
        logger.info("="*70)
        logger.info(f"Current ships: {before_count}")
        
        # Load expansion ships
        expansion_ships = get_mass_expansion_ships()
        logger.info(f"Expansion ships: {len(expansion_ships)}")
        logger.info(f"Target total: {before_count + len(expansion_ships)}")
        logger.info("="*70)
        
        collector = ShipCollector()
        stats = {'added': 0, 'updated': 0, 'skipped': 0, 'analyzed': 0, 'errors': 0}
        
        for i, ship_data in enumerate(expansion_ships, 1):
            try:
                # Check if exists
                existing = Ship.query.filter_by(
                    name=ship_data['name'],
                    nation=ship_data['nation']
                ).first()
                
                if existing:
                    stats['skipped'] += 1
                    continue
                
                # Create ship
                ship = Ship()
                ship.name = ship_data['name']
                ship.full_designation = f"{ship_data.get('prefix', '')} {ship_data['name']}".strip()
                ship.prefix = ship_data.get('prefix')
                ship.nation = ship_data['nation']
                ship.ship_type = ship_data['ship_type']
                ship.launch_year = ship_data['launch_year']
                ship.era = ship_data['era']
                ship.era_decade = (ship_data['launch_year'] // 10) * 10
                ship.historical_significance_score = ship_data['historical_significance_score']
                ship.battles_participated = ship_data.get('battles_participated', 0)
                ship.battles_won = ship_data.get('battles_won', 0)
                ship.primary_purpose = ship_data['ship_type'].title()
                ship.data_completeness_score = ship_data['data_completeness_score']
                ship.primary_source = 'Mass expansion dataset'
                
                # Categorize name
                name_cat = collector._categorize_ship_name(ship.name)
                ship.name_category = name_cat['category']
                ship.geographic_origin = name_cat.get('geographic_origin')
                
                if name_cat['category'] == 'geographic' and name_cat.get('geographic_origin'):
                    ship.place_cultural_prestige_score = collector._get_place_prestige(
                        name_cat['geographic_origin']
                    )
                
                # Save
                db.session.add(ship)
                stats['added'] += 1
                db.session.commit()
                
                # Analyze
                collector._analyze_ship_name(ship)
                stats['analyzed'] += 1
                
                if i % 100 == 0:
                    logger.info(f"Progress: {i}/{len(expansion_ships)} ({i/len(expansion_ships)*100:.1f}%)")
                
            except Exception as e:
                logger.error(f"Error processing {ship_data.get('name')}: {e}")
                db.session.rollback()
                stats['errors'] += 1
        
        after_count = Ship.query.count()
        
        logger.info("\n" + "="*70)
        logger.info("EXPANSION COMPLETE")
        logger.info("="*70)
        logger.info(f"Ships added: {stats['added']}")
        logger.info(f"Ships skipped (duplicates): {stats['skipped']}")
        logger.info(f"Ships analyzed: {stats['analyzed']}")
        logger.info(f"Errors: {stats['errors']}")
        logger.info(f"\nBefore: {before_count} ships")
        logger.info(f"After: {after_count} ships")
        logger.info(f"Net increase: +{after_count - before_count}")
        
        # Show category breakdown
        from sqlalchemy import func
        
        by_category = db.session.query(
            Ship.name_category,
            func.count(Ship.id)
        ).group_by(Ship.name_category).order_by(func.count(Ship.id).desc()).all()
        
        logger.info("\n📌 Updated Category Distribution:")
        for category, count in by_category:
            logger.info(f"  {category:15s}: {count:4d}")
        
        # Check geographic vs saint now
        geographic = Ship.query.filter_by(name_category='geographic').count()
        saint = Ship.query.filter_by(name_category='saint').count()
        
        logger.info("\n📌 Primary Hypothesis Power Check:")
        logger.info(f"  Geographic ships: {geographic}")
        logger.info(f"  Saint ships: {saint}")
        logger.info(f"  Ratio: {geographic/saint:.1f}:1")
        logger.info(f"  Power adequate: {'YES ✓' if saint >= 30 else 'GETTING CLOSER'}")
        
        logger.info("\n" + "="*70)
        logger.info("READY FOR RE-ANALYSIS")
        logger.info("="*70)
        logger.info("Run: python scripts/ship_deep_dive_analysis.py")


if __name__ == "__main__":
    main()

