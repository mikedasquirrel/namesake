"""
Run Marriage Prediction Analysis

Executes complete analysis pipeline on collected data.
"""

import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
import json
import numpy as np
import pandas as pd
from datetime import datetime
from scipy import stats

from core.models import db
from core.marriage_models import MarriedCouple, MarriageAnalysis
from analyzers.relationship_compatibility_analyzer import RelationshipCompatibilityAnalyzer
from app import app

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_analysis():
    """Run complete marriage prediction analysis"""
    logger.info("=" * 80)
    logger.info("MARRIAGE PREDICTION ANALYSIS")
    logger.info("=" * 80)
    
    with app.app_context():
        analyzer = RelationshipCompatibilityAnalyzer(db.session)
        
        # Get all analyzed couples
        couples = db.session.query(MarriedCouple).join(MarriageAnalysis).all()
        
        if len(couples) == 0:
            logger.error("No analyzed couples found. Run initialize_marriage_study.py first.")
            return
        
        logger.info(f"\nAnalyzing {len(couples)} couples...")
        
        # Convert to DataFrame
        df = analyzer.batch_analyze_couples(couples)
        
        logger.info(f"✓ DataFrame created: {df.shape}")
        
        # Basic statistics
        logger.info("\n" + "=" * 80)
        logger.info("DESCRIPTIVE STATISTICS")
        logger.info("=" * 80)
        
        logger.info(f"\nSample Size: {len(df)}")
        logger.info(f"Divorce Rate: {df['is_divorced'].mean():.1%}")
        logger.info(f"Mean Duration: {df['marriage_duration'].mean():.1f} years (SD={df['marriage_duration'].std():.1f})")
        
        logger.info(f"\nName Metrics:")
        logger.info(f"  Compatibility Score: μ={df['compatibility_score'].mean():.3f}, σ={df['compatibility_score'].std():.3f}")
        logger.info(f"  Phonetic Distance: μ={df['phonetic_distance'].mean():.3f}, σ={df['phonetic_distance'].std():.3f}")
        logger.info(f"  Golden Ratio Proximity: μ={df['golden_ratio_proximity'].mean():.3f}, σ={df['golden_ratio_proximity'].std():.3f}")
        logger.info(f"  Vowel Harmony: μ={df['vowel_harmony'].mean():.3f}, σ={df['vowel_harmony'].std():.3f}")
        
        # Test hypotheses
        logger.info("\n" + "=" * 80)
        logger.info("HYPOTHESIS TESTING")
        logger.info("=" * 80)
        
        # H1: Does compatibility predict duration?
        logger.info("\n[H1] Compatibility → Duration")
        r_compat, p_compat = stats.pearsonr(df['compatibility_score'], df['marriage_duration'])
        logger.info(f"  r = {r_compat:.3f}, p = {p_compat:.4f}")
        logger.info(f"  {'✓ SIGNIFICANT' if p_compat < 0.05 else '✗ Not significant'}")
        
        # H2: Does phonetic distance predict divorce?
        logger.info("\n[H2] Phonetic Distance → Divorce")
        divorced_distance = df[df['is_divorced'] == True]['phonetic_distance'].mean()
        married_distance = df[df['is_divorced'] == False]['phonetic_distance'].mean()
        t_stat, p_dist = stats.ttest_ind(
            df[df['is_divorced'] == True]['phonetic_distance'],
            df[df['is_divorced'] == False]['phonetic_distance']
        )
        logger.info(f"  Divorced couples: μ={divorced_distance:.3f}")
        logger.info(f"  Married couples: μ={married_distance:.3f}")
        logger.info(f"  t({len(df)-2}) = {t_stat:.3f}, p = {p_dist:.4f}")
        logger.info(f"  {'✓ SIGNIFICANT' if p_dist < 0.05 else '✗ Not significant'}")
        
        # H3: Golden ratio effect
        logger.info("\n[H3] Golden Ratio → Duration")
        r_golden, p_golden = stats.pearsonr(df['golden_ratio_proximity'], df['marriage_duration'])
        logger.info(f"  r = {r_golden:.3f}, p = {p_golden:.4f}")
        logger.info(f"  {'✓ SIGNIFICANT' if p_golden < 0.05 else '✗ Not significant'}")
        
        # H4: Vowel harmony
        logger.info("\n[H4] Vowel Harmony → Duration")
        r_vowel, p_vowel = stats.pearsonr(df['vowel_harmony'], df['marriage_duration'])
        logger.info(f"  r = {r_vowel:.3f}, p = {p_vowel:.4f}")
        logger.info(f"  {'✓ SIGNIFICANT' if p_vowel < 0.05 else '✗ Not significant'}")
        
        # Theory comparison
        logger.info("\n" + "=" * 80)
        logger.info("THEORY COMPARISON")
        logger.info("=" * 80)
        
        theories = {
            'Similarity': df['similarity_theory'].corr(df['marriage_duration']),
            'Complementarity': df['complementarity_theory'].corr(df['marriage_duration']),
            'Golden Ratio': df['golden_ratio_theory'].corr(df['marriage_duration']),
            'Resonance': df['resonance_theory'].corr(df['marriage_duration'])
        }
        
        logger.info("\nCorrelation with Marriage Duration:")
        for theory, r in sorted(theories.items(), key=lambda x: abs(x[1]), reverse=True):
            logger.info(f"  {theory:20s}: r = {r:.3f}")
        
        winner = max(theories, key=lambda k: abs(theories[k]))
        logger.info(f"\n✓ WINNER: {winner} (r = {theories[winner]:.3f})")
        
        # Relationship types
        logger.info("\n" + "=" * 80)
        logger.info("RELATIONSHIP TYPES")
        logger.info("=" * 80)
        
        type_counts = df['relationship_type'].value_counts()
        logger.info("\nDistribution:")
        for rtype, count in type_counts.items():
            pct = count / len(df) * 100
            logger.info(f"  {rtype:20s}: {count:3d} ({pct:.1f}%)")
        
        # Duration by type
        logger.info("\nMean Duration by Type:")
        for rtype in type_counts.index:
            subset = df[df['relationship_type'] == rtype]
            logger.info(f"  {rtype:20s}: {subset['marriage_duration'].mean():.1f} years")
        
        # Save results
        output_dir = Path('analysis_outputs/marriage')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'n_couples': len(df),
            'divorce_rate': float(df['is_divorced'].mean()),
            'mean_duration': float(df['marriage_duration'].mean()),
            'hypotheses': {
                'H1_compatibility_duration': {'r': float(r_compat), 'p': float(p_compat)},
                'H2_distance_divorce': {'t': float(t_stat), 'p': float(p_dist)},
                'H3_golden_ratio': {'r': float(r_golden), 'p': float(p_golden)},
                'H4_vowel_harmony': {'r': float(r_vowel), 'p': float(p_vowel)},
            },
            'theory_comparison': {k: float(v) for k, v in theories.items()},
            'winner': winner
        }
        
        results_file = output_dir / f'analysis_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"\n✓ Results saved to {results_file}")
        
        # Save DataFrame
        df_file = output_dir / f'couples_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        df.to_csv(df_file, index=False)
        logger.info(f"✓ Data saved to {df_file}")
        
        logger.info("\n" + "=" * 80)
        logger.info("ANALYSIS COMPLETE")
        logger.info("=" * 80)


if __name__ == '__main__':
    try:
        run_analysis()
    except Exception as e:
        logger.error(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

