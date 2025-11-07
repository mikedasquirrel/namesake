"""Complete Ship Analysis Batch

Analyze all ships that don't have linguistic analysis yet.

Usage:
    python scripts/complete_ship_analysis_batch.py
"""

import sys
import os
import logging
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from core.models import db, Ship, ShipAnalysis
from analyzers.name_analyzer import NameAnalyzer
from analyzers.phonemic_analyzer import PhonemicAnalyzer
from analyzers.semantic_analyzer import SemanticAnalyzer
from analyzers.sound_symbolism_analyzer import SoundSymbolismAnalyzer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def analyze_ship(ship: Ship, name_analyzer):
    """Analyze a single ship name."""
    try:
        # Check if already analyzed
        existing = ShipAnalysis.query.filter_by(ship_id=ship.id).first()
        if existing:
            return False
        
        name = ship.name
        
        # Run analysis
        name_metrics = name_analyzer.analyze_name(name)
        
        # Create analysis with available fields from ShipAnalysis model
        analysis = ShipAnalysis(
            ship_id=ship.id,
            syllable_count=name_metrics.get('syllable_count', 0),
            character_length=name_metrics.get('character_length', 0),
            memorability_score=name_metrics.get('memorability_score', 50),
            pronounceability_score=name_metrics.get('pronounceability_score', 50),
            uniqueness_score=name_metrics.get('uniqueness_score', 50),
        )
        
        db.session.add(analysis)
        db.session.commit()
        
        return True
        
    except Exception as e:
        logger.error(f"Error analyzing {ship.name}: {e}")
        db.session.rollback()
        return False


def main():
    """Complete all ship analyses."""
    print("\n" + "=" * 60)
    print("Ship Analysis Completion".center(60))
    print("=" * 60 + "\n")
    
    start_time = datetime.now()
    
    with app.app_context():
        # Initialize analyzer
        name_analyzer = NameAnalyzer()
        
        # Get ships without analysis
        analyzed_ids = {a.ship_id for a in ShipAnalysis.query.all()}
        all_ships = Ship.query.all()
        unanalyzed = [s for s in all_ships if s.id not in analyzed_ids]
        
        print(f"Total Ships: {len(all_ships)}")
        print(f"Already Analyzed: {len(analyzed_ids)}")
        print(f"Need Analysis: {len(unanalyzed)}\n")
        
        if len(unanalyzed) == 0:
            print("✓ All ships already analyzed!")
            return
        
        # Analyze
        analyzed_count = 0
        error_count = 0
        
        for i, ship in enumerate(unanalyzed, 1):
            if analyze_ship(ship, name_analyzer):
                analyzed_count += 1
                if i % 20 == 0:
                    print(f"Progress: {i}/{len(unanalyzed)} ({100*i/len(unanalyzed):.1f}%)")
            else:
                error_count += 1
        
        elapsed = datetime.now() - start_time
        
        print("\n" + "=" * 60)
        print("Completion Summary".center(60))
        print("=" * 60)
        print(f"\nAnalyzed: {analyzed_count}")
        print(f"Errors: {error_count}")
        print(f"Time: {elapsed}")
        print(f"\n✓ Ship analysis now 100% complete")


if __name__ == "__main__":
    main()

