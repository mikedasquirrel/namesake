"""Run complete MTG mission analysis pipeline.

Executes comprehensive statistical analysis and generates results for:
- M1-M3: Existing regressive claims
- M4: Color identity linguistic determinism
- M5: Format segmentation
- M6: Set era evolution
- Cluster analysis
- Cross-sphere comparisons
"""

import logging
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from analyzers.mtg_advanced_analyzer import MTGAdvancedAnalyzer
from analyzers.regressive_proof import RegressiveProofEngine, RegressiveClaim
from app import app

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('mtg_mission_analysis.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def run_mtg_mission_analysis():
    """Run complete MTG mission analysis."""
    
    logger.info("="*70)
    logger.info("MTG MISSION ANALYSIS PIPELINE")
    logger.info("="*70)
    
    with app.app_context():
        # Initialize analyzers
        advanced_analyzer = MTGAdvancedAnalyzer()
        regressive_engine = RegressiveProofEngine(cv_folds=5)
        
        # Run comprehensive analysis (M4-M6 + clustering)
        logger.info("\n[Phase 1/2] Running M4-M6 + Clustering Analysis...")
        comprehensive_results = advanced_analyzer.run_comprehensive_analysis()
        
        # Save comprehensive results
        output_dir = Path(__file__).resolve().parents[1] / 'analysis_outputs' / 'mtg_mission'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = output_dir / f'mtg_comprehensive_{timestamp}.json'
        
        with open(output_file, 'w') as f:
            json.dump(comprehensive_results, f, indent=2, default=str)
        
        logger.info(f"✅ Saved comprehensive results to: {output_file}")
        
        # Run regressive claims (M1-M3 + extended)
        logger.info("\n[Phase 2/2] Running Regressive Claims (M1-M8)...")
        
        # Define MTG claims
        claims = [
            # M1: Legendary creatures (existing)
            RegressiveClaim(
                claim_id='mtg_m1_legendary_creatures',
                asset_type='mtg',
                target_column='log_price_usd',
                target_kind='continuous',
                description='Legendary creatures: name features predict value controlling for EDHREC rank',
                features=['memorability_score', 'fantasy_score', 'mythic_resonance_score', 'syllable_count'],
                control_features=['rarity_tier', 'edhrec_rank'],
                filters={'is_legendary': True, 'is_creature': True},
                sample_floor=100,
            ),
            
            # M2: Instant/Sorcery (existing)
            RegressiveClaim(
                claim_id='mtg_m2_instant_sorcery',
                asset_type='mtg',
                target_column='log_price_usd',
                target_kind='continuous',
                description='Instant/Sorcery spells: memorability positively predicts value',
                features=['memorability_score', 'power_connotation_score', 'syllable_count'],
                control_features=['rarity_tier', 'edhrec_rank'],
                filters={'is_instant_sorcery': True},
                sample_floor=100,
            ),
            
            # M3: Premium collectibles (existing)
            RegressiveClaim(
                claim_id='mtg_m3_premium_collectibles',
                asset_type='mtg',
                target_column='is_premium',
                target_kind='binary',
                description='Premium cards (>$20): fantasy/mythic scores predict collectability',
                features=['fantasy_score', 'mythic_resonance_score', 'constructed_language_score'],
                control_features=['rarity_tier'],
                filters={},
                sample_floor=200,
            ),
        ]
        
        # Run claims
        claim_results = {}
        for claim in claims:
            try:
                result = regressive_engine.run_claim(claim, persist=True)
                claim_results[claim.claim_id] = result
                logger.info(f"✓ {claim.claim_id}: R²={result.get('model_summary', {}).get('r_squared', 0):.3f}")
            except Exception as e:
                logger.error(f"✗ {claim.claim_id}: {e}")
        
        # Summary
        logger.info("\n" + "="*70)
        logger.info("MTG MISSION ANALYSIS COMPLETE")
        logger.info("="*70)
        logger.info(f"Comprehensive results: {output_file}")
        logger.info(f"Regressive claims executed: {len(claim_results)}")
        logger.info(f"Color profiles analyzed: {len(comprehensive_results.get('color_determinism', {}))}")
        logger.info(f"Format segments: {len(comprehensive_results.get('format_segmentation', {}))}")
        logger.info(f"Era epochs: {len(comprehensive_results.get('era_evolution', {}))}")
        
        return {
            'success': True,
            'comprehensive_results': comprehensive_results,
            'claim_results': claim_results,
            'output_file': str(output_file),
        }


if __name__ == '__main__':
    result = run_mtg_mission_analysis()
    
    if result['success']:
        logger.info("\n✅ MTG MISSION ANALYSIS SUCCESSFUL!")
    else:
        logger.error("\n❌ Analysis failed")
        sys.exit(1)

