#!/usr/bin/env python3
"""
NFL Comprehensive Collection with Competitive Context
Collects 2,000+ NFL players with ALL nominal features:
- Player names, nicknames, positions, teams, draft info
- Competitive cohorts (draft classes)
- Story coherence across nominal elements
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask
from core.config import Config
from core.models import db, NFLPlayer, NFLPlayerAnalysis
from collectors.nfl_collector import NFLCollector
from collectors.competitive_context_collector import CompetitiveContextCollector
from analyzers.narrative_features import NarrativeFeatureExtractor
import logging
import json
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    # Create Flask app with context
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        # Create tables
        db.create_all()
        logger.info("Database initialized")
        
        logger.info("="*80)
        logger.info("NFL COMPREHENSIVE COLLECTION WITH COMPETITIVE CONTEXT")
        logger.info("="*80)
        logger.info("")
        logger.info("Target: 2,000 NFL players with complete nominal features")
        logger.info("Features: Names, nicknames, positions, teams, draft info")
        logger.info("Context: Draft class cohorts, position groups")
        logger.info("Expected time: 2-3 hours (with rate limiting)")
        logger.info("")
        logger.info("="*80)
        logger.info("")
        
        # Initialize collector
        collector = NFLCollector()
        
        # Collect stratified sample
        # Target: ~150 players per position × 14 positions ≈ 2,100 players
        logger.info("Starting stratified collection...")
        logger.info("")
        
        stats = collector.collect_stratified_sample(
            target_per_position=150,  # 150 per position = 2,100 total
            target_per_era=500  # Balance across eras
        )
        
        logger.info("")
        logger.info("="*80)
        logger.info("COLLECTION PHASE COMPLETE")
        logger.info("="*80)
        logger.info(f"Total players added: {stats['total_added']}")
        logger.info(f"Total players updated: {stats['total_updated']}")
        logger.info(f"Total analyzed: {stats['total_analyzed']}")
        logger.info(f"Errors: {stats['errors']}")
        logger.info("")
        
        # Show breakdown by position
        logger.info("Position breakdown:")
        for pos, pos_stats in stats['positions_collected'].items():
            logger.info(f"  {pos}: {pos_stats['added']} added, {pos_stats['analyzed']} analyzed")
        
        logger.info("")
        logger.info("="*80)
        logger.info("ADDING COMPETITIVE CONTEXT")
        logger.info("="*80)
        logger.info("")
        
        # Get all NFL players from database
        all_players = NFLPlayer.query.all()
        logger.info(f"Processing {len(all_players)} players for competitive context...")
        
        # Convert to dicts for competitive analysis
        player_dicts = []
        for player in all_players:
            player_dict = {
                'id': player.id,
                'name': player.name,
                'position': player.position,
                'draft_year': player.draft_year,
                'draft_round': player.draft_round,
                'draft_pick': player.draft_pick,
                'team': getattr(player, 'team', 'Unknown'),
                'outcome': player.overall_success_score or 50.0
            }
            
            # Add name analysis features
            if player.analysis:
                player_dict['harshness'] = player.analysis.harshness_score or 50
                player_dict['syllables'] = player.analysis.syllable_count or 2
                player_dict['length'] = player.analysis.character_length or 10
                player_dict['memorability'] = player.analysis.memorability_score or 50
            
            player_dicts.append(player_dict)
        
        # Add competitive context using draft year as cohort
        context_collector = CompetitiveContextCollector()
        enhanced_players = context_collector.batch_collect_with_cohorts(
            player_dicts,
            'sports'
        )
        
        # Save enhanced data
        output_dir = Path('data/sports_competitive')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / 'nfl_with_competitive_context.json'
        with open(output_file, 'w') as f:
            json.dump(enhanced_players, f, indent=2, default=str)
        
        logger.info(f"Saved enhanced data to: {output_file}")
        
        # Calculate statistics
        cohort_sizes = {}
        position_counts = {}
        for player in enhanced_players:
            cohort_key = player.get('competitive_context', {}).get('cohort_key', 'unknown')
            cohort_sizes[cohort_key] = cohort_sizes.get(cohort_key, 0) + 1
            
            position = player.get('position', 'Unknown')
            position_counts[position] = position_counts.get(position, 0) + 1
        
        logger.info("")
        logger.info("Draft class (cohort) distribution:")
        for cohort, size in sorted(cohort_sizes.items())[-10:]:  # Last 10 years
            logger.info(f"  {cohort}: {size} players")
        
        logger.info("")
        logger.info("Position distribution:")
        for position, count in sorted(position_counts.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"  {position}: {count} players")
        
        logger.info("")
        logger.info("="*80)
        logger.info("✅ NFL COLLECTION COMPLETE WITH COMPETITIVE CONTEXT")
        logger.info("="*80)
        logger.info("")
        logger.info(f"Total players: {len(enhanced_players)}")
        logger.info(f"With competitive context: {len([p for p in enhanced_players if 'competitive_context' in p])}")
        logger.info("")
        logger.info("Next steps:")
        logger.info("1. Run: python3 test_nfl_improvements.py")
        logger.info("2. See modeling improvements from competitive context")
        logger.info("3. Compare absolute → relative → market → story coherence models")
        logger.info("")
        
        return enhanced_players

if __name__ == '__main__':
    try:
        result = main()
        sys.exit(0)
    except KeyboardInterrupt:
        logger.info("\n\nCollection interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


