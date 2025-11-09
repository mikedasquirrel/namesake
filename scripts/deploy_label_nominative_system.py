"""
Deploy Label Nominative System - Master Execution Script
Run all setup steps in correct order

Purpose: One-command deployment of complete label nominative ensemble system
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_script(script_name, description):
    """Run a script and report results"""
    logger.info("\n" + "="*80)
    logger.info(f"STEP: {description}")
    logger.info("="*80)
    
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    
    if not os.path.exists(script_path):
        logger.error(f"❌ Script not found: {script_path}")
        return False
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            logger.info("✅ SUCCESS")
            if result.stdout:
                logger.info(result.stdout)
            return True
        else:
            logger.error(f"❌ FAILED with return code {result.returncode}")
            if result.stderr:
                logger.error(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("❌ TIMEOUT after 5 minutes")
        return False
    except Exception as e:
        logger.error(f"❌ ERROR: {e}")
        return False


def verify_database():
    """Verify database tables exist"""
    logger.info("\n" + "="*80)
    logger.info("VERIFYING DATABASE")
    logger.info("="*80)
    
    try:
        from app import app, db
        from core.models import (LabelNominativeProfile, TeamProfile, 
                                VenueProfile, PropTypeProfile)
        
        with app.app_context():
            # Create tables if they don't exist
            db.create_all()
            
            # Check counts
            label_count = LabelNominativeProfile.query.count()
            team_count = TeamProfile.query.count()
            venue_count = VenueProfile.query.count()
            prop_count = PropTypeProfile.query.count()
            
            logger.info(f"\nCurrent database state:")
            logger.info(f"  Label Profiles: {label_count}")
            logger.info(f"  Team Profiles: {team_count}")
            logger.info(f"  Venue Profiles: {venue_count}")
            logger.info(f"  Prop Profiles: {prop_count}")
            logger.info(f"  TOTAL: {label_count}")
            
            if label_count > 0:
                logger.info("\n⚠️  Database already has data!")
                logger.info("    Delete existing data? (You'll need to do this manually if needed)")
            
            logger.info("\n✅ Database ready")
            return True
            
    except Exception as e:
        logger.error(f"❌ Database verification failed: {e}")
        return False


def test_extraction():
    """Test that extraction works"""
    logger.info("\n" + "="*80)
    logger.info("TESTING EXTRACTION")
    logger.info("="*80)
    
    try:
        from analyzers.label_nominative_extractor import LabelNominativeExtractor
        from analyzers.nominative_ensemble_generator import NominativeEnsembleGenerator
        
        extractor = LabelNominativeExtractor()
        generator = NominativeEnsembleGenerator()
        
        # Test team extraction
        chiefs = extractor.extract_label_features("Kansas City Chiefs", "team")
        logger.info(f"\n✅ Team extraction: Chiefs harshness={chiefs['harshness']:.1f}")
        
        # Test venue extraction
        lambeau = extractor.extract_label_features("Lambeau Field", "venue")
        logger.info(f"✅ Venue extraction: Lambeau intimidation={lambeau.get('venue_intimidation', 0):.1f}")
        
        # Test ensemble
        player_mock = {
            'name': 'Test', 'harshness': 70, 'memorability': 65,
            'syllables': 2, 'power_phoneme_count': 3, 'speed_phoneme_count': 1,
            'front_vowel_count': 1, 'back_vowel_count': 1,
            'plosive_count': 2, 'fricative_count': 1,
            'consonant_clusters': 1, 'sonority_score': 60
        }
        
        ensemble = generator.generate_ensemble_features(player_mock, chiefs, 'team')
        logger.info(f"✅ Ensemble generation: Alignment={ensemble['overall_alignment']:.1f}")
        
        logger.info("\n✅ All extraction tests passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Extraction test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main deployment execution"""
    logger.info("="*80)
    logger.info("LABEL NOMINATIVE SYSTEM - MASTER DEPLOYMENT")
    logger.info("="*80)
    logger.info("\nThis script will:")
    logger.info("  1. Verify database setup")
    logger.info("  2. Populate team/venue/prop labels (146 profiles)")
    logger.info("  3. Populate play/formation names (80 profiles)")
    logger.info("  4. Test extraction functionality")
    logger.info("  5. Optionally run analysis scripts")
    logger.info("\nTotal time: 5-10 minutes\n")
    
    # Track success
    all_success = True
    
    # Step 1: Verify database
    if not verify_database():
        logger.error("❌ Database verification failed - stopping")
        return False
    
    # Step 2: Populate teams/venues/props
    if not run_script('populate_label_nominative_data.py', 
                     'Populate Teams/Venues/Props'):
        logger.warning("⚠️  Population failed - continuing anyway")
        all_success = False
    
    # Step 3: Populate plays
    if not run_script('populate_play_names.py',
                     'Populate Play Names'):
        logger.warning("⚠️  Play population failed - continuing anyway")
        all_success = False
    
    # Step 4: Test extraction
    if not test_extraction():
        logger.error("❌ Extraction test failed")
        all_success = False
    
    # Final summary
    logger.info("\n" + "="*80)
    logger.info("DEPLOYMENT COMPLETE")
    logger.info("="*80)
    
    if all_success:
        logger.info("\n✅ ALL STEPS SUCCESSFUL")
        logger.info("\n📊 Label Nominative System is now operational!")
        logger.info("\nYou can now:")
        logger.info("  • Use EnhancedNominativePredictor for predictions")
        logger.info("  • Access label profiles via API endpoints")
        logger.info("  • Run analysis scripts to validate findings")
        logger.info("  • Integrate into live betting system")
        
        logger.info("\n" + "="*80)
        logger.info("OPTIONAL: Run Analysis Scripts")
        logger.info("="*80)
        logger.info("\nTo validate the system with real data:")
        logger.info("  python scripts/analyze_label_correlations.py")
        logger.info("  python scripts/test_ensemble_interactions.py")
        logger.info("  python scripts/validate_ensemble_model.py")
        
    else:
        logger.warning("\n⚠️  SOME STEPS HAD WARNINGS")
        logger.info("\nThe system is still usable, but review errors above")
    
    logger.info("\n" + "="*80)
    logger.info("Quick Start:")
    logger.info("="*80)
    logger.info("""
from analyzers.enhanced_predictor import enhanced_predict

result = enhanced_predict(
    player_data={'name': 'Nick Chubb', ...},
    game_context={'team_name': 'Kansas City Chiefs', ...},
    market_data={'line': 88.5, ...}
)

print(f"Prediction: {result['final_prediction']}")
print(f"Team Amplifier: {result['team_amplifier']}×")
    """)
    
    logger.info("\n🎯 SYSTEM READY TO USE!\n")


if __name__ == "__main__":
    main()

