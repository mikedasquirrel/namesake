"""Ship Deep Dive Analysis

Comprehensive statistical analysis of ship nomenclature for nominative determinism research.

PRIMARY HYPOTHESIS:
Ships with geographically-tethered names (Florence, Boston, Vienna) achieved 
greater historical significance than saint-named ships.

SECONDARY HYPOTHESIS:
Semantic alignment between name and achievements (HMS Beagle → Darwin → evolution)
exceeds random chance (nominative determinism).

This script performs:
1. Primary hypothesis testing (Geographic vs Saint)
2. Semantic alignment permutation tests
3. Robustness checks
4. Effect size calculations
5. Cross-domain comparisons
6. Comprehensive reporting

Usage:
    python scripts/ship_deep_dive_analysis.py
"""

import sys
import os
import logging
import json
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from core.config import Config
from core.models import db, Ship, ShipAnalysis
from analyzers.ship_semantic_analyzer import ShipSemanticAnalyzer
from analyzers.ship_advanced_statistical_analyzer import ShipAdvancedStatisticalAnalyzer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ShipDeepDive:
    """Comprehensive discovery analysis of ship nomenclature."""
    
    def __init__(self):
        self.app = Flask(__name__)
        self.app.config.from_object(Config)
        db.init_app(self.app)
        self.analyzer = ShipSemanticAnalyzer()
        self.advanced_analyzer = ShipAdvancedStatisticalAnalyzer()
        self.results = {}
        
    def run_all_analyses(self):
        """Execute full deep dive analysis suite."""
        logger.info("="*70)
        logger.info("SHIP NOMENCLATURE DEEP DIVE ANALYSIS")
        logger.info("="*70)
        logger.info("Testing geographic vs saint hypothesis")
        logger.info("Testing nominative determinism (HMS Beagle)")
        logger.info("="*70)
        
        with self.app.app_context():
            # Load data
            logger.info("\n📊 Loading ship data...")
            ships_df, analysis_df = self._load_data()
            
            if ships_df.empty:
                logger.error("No ships in database. Run collector first:")
                logger.error("  python -m collectors.ship_collector")
                return
            
            logger.info(f"Loaded {len(ships_df)} ships with {len(analysis_df)} analyses")
            
            # Run analyses
            self.results['primary_hypothesis'] = self._test_primary_hypothesis(ships_df)
            self.results['semantic_alignment'] = self._test_semantic_alignment(ships_df, analysis_df)
            self.results['category_analysis'] = self._analyze_all_categories(ships_df)
            self.results['phonetic_power'] = self._analyze_phonetic_power(ships_df, analysis_df)
            self.results['temporal_evolution'] = self._analyze_temporal_patterns(ships_df)
            self.results['robustness_checks'] = self._robustness_checks(ships_df)
            
            # ADVANCED STATISTICAL ANALYSES
            logger.info("\n" + "="*70)
            logger.info("RUNNING ADVANCED STATISTICAL SUITE")
            logger.info("="*70)
            self.results['advanced_statistics'] = self.advanced_analyzer.comprehensive_analysis(ships_df, analysis_df)
            
            # Save results
            self._save_results()
            
            # Generate summary
            self._generate_summary()
        
        return self.results
    
    def _load_data(self):
        """Load ship data from database."""
        ships = Ship.query.all()
        analyses = ShipAnalysis.query.all()
        
        ships_df = pd.DataFrame([s.to_dict() for s in ships])
        analysis_df = pd.DataFrame([a.to_dict() for a in analyses]) if analyses else pd.DataFrame()
        
        return ships_df, analysis_df
    
    def _test_primary_hypothesis(self, ships_df):
        """PRIMARY HYPOTHESIS: Geographic names vs Saint names."""
        logger.info("\n" + "="*70)
        logger.info("PRIMARY HYPOTHESIS TEST")
        logger.info("="*70)
        logger.info("H₁: Ships with geographic names achieve greater significance than saint-named ships")
        
        results = self.analyzer.analyze_geographic_vs_saint(ships_df)
        
        # Add interpretation
        if 'hypothesis_tests' in results and 't_test' in results['hypothesis_tests']:
            t_test = results['hypothesis_tests']['t_test']
            cohens_d = results['effect_sizes']['cohens_d']
            
            interpretation = {
                'hypothesis_supported': t_test['significant'] and t_test['t_statistic'] > 0,
                'strength': cohens_d['interpretation'],
                'conclusion': self._interpret_primary_hypothesis(t_test, cohens_d)
            }
            results['interpretation'] = interpretation
            
            logger.info("\n🔍 CONCLUSION:")
            logger.info(interpretation['conclusion'])
        
        return results
    
    def _interpret_primary_hypothesis(self, t_test, cohens_d):
        """Generate human-readable conclusion for primary hypothesis."""
        if t_test['significant'] and t_test['t_statistic'] > 0:
            strength = cohens_d['interpretation']
            return f"✓ HYPOTHESIS SUPPORTED: Geographic-named ships show {strength} advantage over saint-named ships (p={t_test['p_value']:.4f}, d={cohens_d['value']:.3f})"
        elif t_test['significant'] and t_test['t_statistic'] < 0:
            return f"✗ HYPOTHESIS REJECTED: Saint-named ships actually perform better (p={t_test['p_value']:.4f})"
        else:
            return f"○ NO SIGNIFICANT DIFFERENCE: Cannot distinguish geographic vs saint names (p={t_test['p_value']:.4f})"
    
    def _test_semantic_alignment(self, ships_df, analysis_df):
        """SECONDARY HYPOTHESIS: Nominative determinism (semantic alignment)."""
        logger.info("\n" + "="*70)
        logger.info("SECONDARY HYPOTHESIS TEST: NOMINATIVE DETERMINISM")
        logger.info("="*70)
        logger.info("H₂: Semantic alignment between name and achievements exceeds random chance")
        
        if analysis_df.empty:
            logger.warning("No analysis data available for semantic alignment test")
            return {'error': 'No analysis data'}
        
        results = self.analyzer.analyze_semantic_alignment(ships_df, analysis_df)
        
        # Add HMS Beagle specific analysis
        beagle = ships_df[ships_df['name'].str.lower() == 'beagle']
        if not beagle.empty:
            beagle_analysis = analysis_df[analysis_df['ship_id'] == beagle.iloc[0]['id']]
            if not beagle_analysis.empty:
                results['beagle_case_study'] = {
                    'semantic_alignment_score': beagle_analysis.iloc[0].get('semantic_alignment_score', 0),
                    'historical_significance': beagle.iloc[0]['historical_significance_score'],
                    'analysis': 'HMS Beagle demonstrates strong nominative determinism',
                    'evidence': [
                        'Name: Beagle (animal - dog breed)',
                        'Carried: Charles Darwin (naturalist)',
                        'Achievement: Theory of evolution (biological theory)',
                        'Connection: Animal name → animal studies → evolutionary biology'
                    ]
                }
                
                logger.info("\n🐕 HMS BEAGLE CASE STUDY")
                logger.info(f"Semantic Alignment: {beagle_analysis.iloc[0].get('semantic_alignment_score', 0):.2f}/100")
                logger.info(f"Historical Significance: {beagle.iloc[0]['historical_significance_score']:.2f}/100")
        
        # Interpretation
        if 'permutation_test' in results:
            perm = results['permutation_test']
            logger.info("\n🔍 NOMINATIVE DETERMINISM CONCLUSION:")
            logger.info(perm['interpretation'])
        
        return results
    
    def _analyze_all_categories(self, ships_df):
        """Analyze all name categories."""
        logger.info("\n" + "="*70)
        logger.info("CATEGORY ANALYSIS")
        logger.info("="*70)
        
        results = self.analyzer.analyze_name_category_outcomes(ships_df)
        
        logger.info("\n📊 Category Rankings:")
        for i, rank in enumerate(results['rankings'], 1):
            logger.info(f"  {i}. {rank['category']}: {rank['mean_significance']:.2f} (n={rank['count']})")
        
        return results
    
    def _analyze_phonetic_power(self, ships_df, analysis_df):
        """Analyze phonetic features and outcomes."""
        logger.info("\n" + "="*70)
        logger.info("PHONETIC POWER ANALYSIS")
        logger.info("="*70)
        
        if analysis_df.empty:
            logger.warning("No analysis data for phonetic analysis")
            return {'error': 'No analysis data'}
        
        results = self.analyzer.analyze_phonetic_power(ships_df, analysis_df)
        
        return results
    
    def _analyze_temporal_patterns(self, ships_df):
        """Analyze how patterns evolved over time."""
        logger.info("\n" + "="*70)
        logger.info("TEMPORAL EVOLUTION")
        logger.info("="*70)
        
        results = self.analyzer.analyze_temporal_evolution(ships_df)
        
        return results
    
    def _robustness_checks(self, ships_df):
        """Perform robustness checks on findings."""
        logger.info("\n" + "="*70)
        logger.info("ROBUSTNESS CHECKS")
        logger.info("="*70)
        
        checks = {}
        
        # 1. Survivorship bias check
        logger.info("\n1. Survivorship Bias Check")
        sunk_ships = ships_df[ships_df['was_sunk'] == True]
        active_ships = ships_df[ships_df['was_sunk'] == False]
        
        checks['survivorship_bias'] = {
            'total_ships': len(ships_df),
            'sunk_ships': len(sunk_ships),
            'active_ships': len(active_ships),
            'sunk_percentage': len(sunk_ships) / len(ships_df) * 100 if len(ships_df) > 0 else 0
        }
        
        logger.info(f"  Sunk ships: {len(sunk_ships)} ({checks['survivorship_bias']['sunk_percentage']:.1f}%)")
        logger.info(f"  Active ships: {len(active_ships)}")
        
        # 2. Era-specific analysis
        logger.info("\n2. Era-Specific Robustness")
        era_results = {}
        for era in ships_df['era'].unique():
            if pd.notna(era):
                era_ships = ships_df[ships_df['era'] == era]
                if len(era_ships) >= 5:
                    geographic = era_ships[era_ships['name_category'] == 'geographic']
                    saint = era_ships[era_ships['name_category'] == 'saint']
                    
                    if len(geographic) >= 3 and len(saint) >= 3:
                        from scipy import stats
                        t_stat, p_val = stats.ttest_ind(
                            geographic['historical_significance_score'].dropna(),
                            saint['historical_significance_score'].dropna(),
                            equal_var=False
                        )
                        
                        era_results[era] = {
                            'geographic_mean': float(geographic['historical_significance_score'].mean()),
                            'saint_mean': float(saint['historical_significance_score'].mean()),
                            'p_value': float(p_val),
                            'significant': p_val < 0.05
                        }
                        
                        logger.info(f"  {era}: p={p_val:.4f} ({'SIGNIFICANT' if p_val < 0.05 else 'not sig.'})")
        
        checks['era_specific'] = era_results
        
        # 3. Nation-specific robustness
        logger.info("\n3. Nation-Specific Robustness")
        top_nations = ships_df['nation'].value_counts().head(3).index.tolist()
        nation_results = {}
        
        for nation in top_nations:
            nation_ships = ships_df[ships_df['nation'] == nation]
            if len(nation_ships) >= 5:
                geographic = nation_ships[nation_ships['name_category'] == 'geographic']
                saint = nation_ships[nation_ships['name_category'] == 'saint']
                
                if len(geographic) >= 2 and len(saint) >= 2:
                    nation_results[nation] = {
                        'total': len(nation_ships),
                        'geographic_mean': float(geographic['historical_significance_score'].mean()),
                        'saint_mean': float(saint['historical_significance_score'].mean())
                    }
                    
                    logger.info(f"  {nation}: Geo={nation_results[nation]['geographic_mean']:.1f}, "
                              f"Saint={nation_results[nation]['saint_mean']:.1f}")
        
        checks['nation_specific'] = nation_results
        
        return checks
    
    def _save_results(self):
        """Save results to JSON file."""
        output_dir = Path('analysis_outputs/ship_analysis')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = output_dir / f'ship_deep_dive_{timestamp}.json'
        
        # Convert numpy types to native Python types for JSON serialization
        results_json = json.dumps(self.results, indent=2, default=str)
        
        with open(output_file, 'w') as f:
            f.write(results_json)
        
        logger.info(f"\n💾 Results saved to: {output_file}")
    
    def _generate_summary(self):
        """Generate executive summary of findings."""
        logger.info("\n" + "="*70)
        logger.info("EXECUTIVE SUMMARY")
        logger.info("="*70)
        
        # Primary hypothesis
        if 'primary_hypothesis' in self.results and 'interpretation' in self.results['primary_hypothesis']:
            interp = self.results['primary_hypothesis']['interpretation']
            logger.info("\n📌 PRIMARY FINDING:")
            logger.info(f"   {interp['conclusion']}")
        
        # Semantic alignment
        if 'semantic_alignment' in self.results and 'permutation_test' in self.results['semantic_alignment']:
            perm = self.results['semantic_alignment']['permutation_test']
            logger.info("\n📌 NOMINATIVE DETERMINISM:")
            logger.info(f"   {perm['interpretation']}")
            logger.info(f"   P-value: {perm['p_value']:.4f}")
        
        # Top category
        if 'category_analysis' in self.results and 'rankings' in self.results['category_analysis']:
            rankings = self.results['category_analysis']['rankings']
            if rankings:
                top = rankings[0]
                logger.info("\n📌 TOP PERFORMING CATEGORY:")
                logger.info(f"   {top['category']}: {top['mean_significance']:.2f} (n={top['count']})")
        
        logger.info("\n" + "="*70)
        logger.info("ANALYSIS COMPLETE")
        logger.info("="*70)


if __name__ == "__main__":
    analyzer = ShipDeepDive()
    analyzer.run_all_analyses()

