"""
Populate Play Names from Taxonomy
Extract nominative features from play, formation, and scheme names

Purpose: Complete the label nominative database with play-level analysis
Expected Impact: +2-3% ROI from play-type matching
"""

import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from core.models import LabelNominativeProfile
from analyzers.label_nominative_extractor import LabelNominativeExtractor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_play_taxonomy():
    """Load play names from JSON taxonomy"""
    taxonomy_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'data', 'play_names_taxonomy.json'
    )
    
    with open(taxonomy_path, 'r') as f:
        return json.load(f)


def populate_play_names():
    """Extract and populate play name nominative profiles"""
    logger.info("="*80)
    logger.info("POPULATING PLAY NAME NOMINATIVE PROFILES")
    logger.info("="*80)
    
    extractor = LabelNominativeExtractor()
    taxonomy = load_play_taxonomy()
    
    total_plays = 0
    
    for sport, categories in taxonomy.items():
        logger.info(f"\nProcessing {sport} plays...")
        
        for category_name, plays in categories.items():
            logger.info(f"  Category: {category_name}")
            
            for play_data in plays:
                play_name = play_data['name']
                
                # Extract nominative features
                features = extractor.extract_label_features(
                    play_name, 
                    'play',
                    {'sport': sport, 'category': play_data.get('category')}
                )
                
                # Create or update label nominative profile
                profile = LabelNominativeProfile.query.filter_by(
                    label_text=play_name,
                    label_type='play',
                    domain='sports',
                    sport=sport
                ).first()
                
                if not profile:
                    profile = LabelNominativeProfile(
                        label_text=play_name,
                        label_type='play',
                        domain='sports',
                        sport=sport
                    )
                
                # Set base features
                profile.syllables = features.get('syllables')
                profile.length = features.get('length')
                profile.harshness = features.get('harshness')
                profile.memorability = features.get('memorability')
                profile.pronounceability = features.get('pronounceability')
                profile.uniqueness = features.get('uniqueness')
                profile.vowel_ratio = features.get('vowel_ratio')
                profile.consonant_clusters = features.get('consonant_clusters')
                profile.first_letter_harsh = features.get('first_letter_harsh', False)
                profile.last_letter_harsh = features.get('last_letter_harsh', False)
                
                # Phonetic features
                profile.plosive_count = features.get('plosive_count')
                profile.fricative_count = features.get('fricative_count')
                profile.power_phoneme_count = features.get('power_phoneme_count')
                profile.speed_phoneme_count = features.get('speed_phoneme_count')
                profile.power_phoneme_ratio = features.get('power_phoneme_ratio')
                profile.speed_phoneme_ratio = features.get('speed_phoneme_ratio')
                profile.initial_consonant_strength = features.get('initial_consonant_strength')
                profile.final_consonant_strength = features.get('final_consonant_strength')
                profile.sonority_score = features.get('sonority_score')
                
                # Semantic features
                profile.word_count = features.get('word_count')
                profile.power_semantic = features.get('power_semantic', False)
                profile.speed_semantic = features.get('speed_semantic', False)
                
                # Play-specific features
                play_specific = {
                    'play_complexity': features.get('play_complexity', 1),
                    'play_power_indicator': features.get('play_power_indicator', 0),
                    'play_speed_indicator': features.get('play_speed_indicator', 0),
                    'play_trick_indicator': features.get('play_trick_indicator', 0),
                    'play_type': play_data.get('type'),
                    'play_category': play_data.get('category')
                }
                profile.set_specific_features(play_specific)
                
                db.session.add(profile)
                total_plays += 1
                
                if total_plays % 20 == 0:
                    logger.info(f"    Processed {total_plays} plays...")
                    db.session.commit()
    
    db.session.commit()
    logger.info(f"\n✅ Successfully populated {total_plays} play/formation/scheme profiles")
    
    # Summary by sport
    logger.info("\nSummary by sport:")
    for sport in taxonomy.keys():
        count = LabelNominativeProfile.query.filter_by(
            label_type='play',
            sport=sport
        ).count()
        logger.info(f"  {sport}: {count} plays")


def main():
    """Main execution function"""
    with app.app_context():
        logger.info("="*80)
        logger.info("PLAY NAMES NOMINATIVE DATA POPULATION")
        logger.info("="*80)
        logger.info("\nThis script will populate play/formation/scheme names")
        logger.info("from the comprehensive taxonomy across 6 sports\n")
        
        try:
            # Create tables if needed
            db.create_all()
            
            # Populate play names
            populate_play_names()
            
            logger.info("\n" + "="*80)
            logger.info("PLAY NAMES POPULATION COMPLETE!")
            logger.info("="*80)
            
            total_plays = LabelNominativeProfile.query.filter_by(label_type='play').count()
            logger.info(f"\nTotal play profiles created: {total_plays}")
            logger.info("\n✅ Ready for play-player nominative matching analysis")
            logger.info("✅ Ready for play-type prop betting enhancement\n")
            
        except Exception as e:
            logger.error(f"❌ Error during population: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            raise


if __name__ == "__main__":
    main()

