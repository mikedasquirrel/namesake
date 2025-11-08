"""Comprehensive Board Game Collection Script

Collects 2,000 board games from BoardGameGeek with stratified sampling across eras.

Usage:
    python scripts/collect_board_games_comprehensive.py --target 2000
    python scripts/collect_board_games_comprehensive.py --quick-test  # 50 games for testing
"""

import logging
import argparse
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from collectors.board_game_collector import BoardGameCollector
from core.models import BoardGame, BoardGameAnalysis

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('board_games_collection.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def run_collection(target: int = 2000, quick_test: bool = False):
    """Run the board game collection process.
    
    Args:
        target: Target number of games to collect
        quick_test: If True, collect only 50 games for testing
    """
    logger.info("=" * 80)
    logger.info("BOARD GAME COLLECTION STARTING")
    logger.info("=" * 80)
    
    start_time = datetime.now()
    
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        logger.info("✅ Database tables ready")
        
        # Check existing data
        existing_count = BoardGame.query.count()
        logger.info(f"Existing games in database: {existing_count}")
        
        # Initialize collector
        collector = BoardGameCollector()
        
        # Collect data
        if quick_test:
            logger.info("\n🧪 QUICK TEST MODE: Collecting 50 games")
            result = collector.collect_top_n(50)
        else:
            logger.info(f"\n📊 FULL COLLECTION: Target {target} games")
            
            # Stratified sampling
            if target == 2000:
                targets = {
                    'classic_1950_1979': 200,
                    'golden_1980_1999': 400,
                    'modern_2000_2009': 600,
                    'contemporary_2010_2024': 800
                }
            else:
                # Proportional distribution
                targets = {
                    'classic_1950_1979': int(target * 0.10),
                    'golden_1980_1999': int(target * 0.20),
                    'modern_2000_2009': int(target * 0.30),
                    'contemporary_2010_2024': int(target * 0.40)
                }
            
            result = collector.collect_stratified_sample(targets)
        
        # Final statistics
        final_count = BoardGame.query.count()
        analyzed_count = BoardGameAnalysis.query.count()
        
        duration = (datetime.now() - start_time).total_seconds()
        
        logger.info("\n" + "=" * 80)
        logger.info("COLLECTION COMPLETE")
        logger.info("=" * 80)
        logger.info(f"✅ Total games in database: {final_count}")
        logger.info(f"✅ Total analyzed: {analyzed_count}")
        logger.info(f"✅ Newly collected: {final_count - existing_count}")
        logger.info(f"⏱️  Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
        
        if isinstance(result, dict) and 'by_era' in result:
            logger.info("\n📊 By Era:")
            for era, count in result['by_era'].items():
                logger.info(f"   {era}: {count}")
        
        # Show sample of collected games
        logger.info("\n🎲 Sample of collected games:")
        samples = BoardGame.query.order_by(BoardGame.id.desc()).limit(10).all()
        for game in samples:
            logger.info(f"   - {game.name} ({game.year_published}): Rating {game.bgg_rating:.2f}" if game.bgg_rating else f"   - {game.name} ({game.year_published})")
        
        return {
            'total': final_count,
            'analyzed': analyzed_count,
            'duration_seconds': duration
        }


def main():
    parser = argparse.ArgumentParser(description='Collect board game data from BoardGameGeek')
    parser.add_argument('--target', type=int, default=2000, help='Target number of games to collect')
    parser.add_argument('--quick-test', action='store_true', help='Quick test with 50 games')
    
    args = parser.parse_args()
    
    try:
        result = run_collection(
            target=args.target,
            quick_test=args.quick_test
        )
        
        logger.info("\n✅ SUCCESS - Collection completed")
        logger.info(f"Total games: {result['total']}")
        logger.info(f"Analyzed: {result['analyzed']}")
        logger.info(f"Duration: {result['duration_seconds']/60:.1f} minutes")
        
    except KeyboardInterrupt:
        logger.info("\n⚠️  Collection interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

