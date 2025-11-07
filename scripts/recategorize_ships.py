"""Recategorize Ships with Improved Saint Detection

Re-runs categorization on all existing ships to properly detect saint names.

Usage:
    python scripts/recategorize_ships.py
"""

import sys
import os
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from core.config import Config
from core.models import db, Ship
from collectors.ship_collector import ShipCollector

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        collector = ShipCollector()
        
        all_ships = Ship.query.all()
        logger.info(f"Recategorizing {len(all_ships)} ships...")
        
        changes = {'saint': 0, 'geographic': 0, 'other': 0}
        
        for ship in all_ships:
            old_category = ship.name_category
            
            # Recategorize
            name_cat = collector._categorize_ship_name(ship.name)
            new_category = name_cat['category']
            
            if old_category != new_category:
                ship.name_category = new_category
                ship.geographic_origin = name_cat.get('geographic_origin')
                changes[new_category] = changes.get(new_category, 0) + 1
                
                if new_category == 'saint':
                    logger.info(f"  ✓ {ship.name} -> SAINT")
        
        db.session.commit()
        
        logger.info(f"\nRecategorization complete:")
        logger.info(f"  Changed to saint: {changes.get('saint', 0)}")
        logger.info(f"  Changed to geographic: {changes.get('geographic', 0)}")
        logger.info(f"  Changed to other: {changes.get('other', 0)}")
        
        # Show final counts
        from sqlalchemy import func
        
        by_category = db.session.query(
            Ship.name_category,
            func.count(Ship.id)
        ).group_by(Ship.name_category).order_by(func.count(Ship.id).desc()).all()
        
        logger.info("\n📌 Updated Category Distribution:")
        total = sum(count for _, count in by_category)
        for category, count in by_category:
            pct = count / total * 100
            logger.info(f"  {category:15s}: {count:4d} ({pct:5.1f}%)")
        
        saint = Ship.query.filter_by(name_category='saint').count()
        geographic = Ship.query.filter_by(name_category='geographic').count()
        
        logger.info(f"\n✅ Power Check:")
        logger.info(f"  Saint ships: {saint}")
        logger.info(f"  Geographic ships: {geographic}")
        logger.info(f"  Adequate power: {'YES ✓' if saint >= 30 else f'Need {30 - saint} more'}")


if __name__ == "__main__":
    main()

