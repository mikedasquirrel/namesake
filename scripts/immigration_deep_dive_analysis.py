#!/usr/bin/env python3
"""Immigration Deep Dive Analysis - SEMANTIC MEANING ANALYSIS

Runs comprehensive statistical analysis on immigration patterns by surname SEMANTIC CATEGORY.

RESEARCH QUESTION:
Do toponymic surnames (Galilei="from Galilee", Romano="from Rome") show different 
immigration/settlement patterns than occupational (Smith, Baker), descriptive (Brown, Long),
patronymic (Johnson, O'Brien), or religious surnames?

Performs:
1. H1: Toponymic vs Non-Toponymic Immigration Rates
2. H2: Toponymic vs Non-Toponymic Settlement Clustering (HHI)
3. H3: Temporal Dispersion by Semantic Category
4. H4: Place Cultural Importance Effect (toponymic only)
5. H5: Cross-Category Comparisons (ANOVA across all 5 categories)
6. H6: Semantic × Origin Interaction Effects

Statistical Methods:
- T-tests and ANOVA
- Effect sizes (Cohen's d, eta-squared)
- Bonferroni corrections
- Correlation analyses
- Interaction effects

Exports results to:
- analysis_outputs/immigration_analysis/

Usage:
    python3 scripts/immigration_deep_dive_analysis.py

Author: Michael Smerconish
Date: November 2025
"""

import sys
import os
import logging
import json
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from core.models import db, ImmigrantSurname
from analyzers.immigration_statistical_analyzer import ImmigrationStatisticalAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'immigration_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Main analysis function."""
    logger.info("="*70)
    logger.info("IMMIGRATION SURNAME SEMANTIC MEANING ANALYSIS")
    logger.info("="*70)
    logger.info("Research Question: Galilei (toponymic) vs Shoemaker (occupational)?")
    logger.info("="*70)
    logger.info(f"Started at: {datetime.now()}")
    logger.info("="*70)
    
    with app.app_context():
        # Check if we have data
        surname_count = ImmigrantSurname.query.count()
        
        if surname_count == 0:
            logger.error("No surname data found in database!")
            logger.error("Please run scripts/collect_immigration_mass_scale.py first")
            return 1
        
        logger.info(f"Found {surname_count} surnames in database")
        
        # Initialize analyzer
        analyzer = ImmigrationStatisticalAnalyzer()
        
        # Run full analysis
        logger.info("\nRunning comprehensive statistical analysis...")
        results = analyzer.run_full_analysis()
        
        # Create output directory
        output_dir = Path('analysis_outputs/immigration_analysis')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Convert numpy types to native Python types for JSON
        import numpy as np
        def convert_numpy(obj):
            if isinstance(obj, dict):
                return {key: convert_numpy(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy(item) for item in obj]
            elif isinstance(obj, (np.integer, np.int64, np.int32)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float64, np.float32)):
                return float(obj)
            elif isinstance(obj, (np.bool_, bool)):
                return bool(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            return obj
        
        results = convert_numpy(results)
        
        # Export results
        logger.info("\nExporting results...")
        
        # 1. Summary statistics
        with open(output_dir / 'summary_statistics.json', 'w') as f:
            json.dump({
                'analysis_date': results['analysis_date'],
                'dataset_summary': results['dataset_summary'],
                'descriptive_statistics': results['descriptive_statistics']
            }, f, indent=2)
        logger.info("✓ Saved summary_statistics.json")
        
        # 2. Hypothesis test results (primary hypotheses)
        with open(output_dir / 'hypothesis_tests.json', 'w') as f:
            json.dump({
                'primary_hypotheses': results.get('primary_hypotheses', {}),
                'expanded_analyses': results.get('expanded_analyses', {}),
                'cross_category_comparisons': results.get('cross_category_comparisons', {}),
                'interaction_effects': results.get('interaction_effects', {})
            }, f, indent=2)
        logger.info("✓ Saved hypothesis_tests.json")
        
        # 4. Temporal trends
        with open(output_dir / 'temporal_trends.json', 'w') as f:
            json.dump(results['temporal_trends'], f, indent=2)
        logger.info("✓ Saved temporal_trends.json")
        
        # 5. Complete results
        with open(output_dir / 'complete_analysis.json', 'w') as f:
            json.dump(results, f, indent=2)
        logger.info("✓ Saved complete_analysis.json")
        
        # Print key findings
        logger.info("\n" + "="*70)
        logger.info("KEY FINDINGS")
        logger.info("="*70)
        
        # H1: Toponymic vs Non-Toponymic Immigration
        if 'primary_hypotheses' in results and 'H1_toponymic_vs_nontoponlaymic_immigration' in results['primary_hypotheses']:
            h1 = results['primary_hypotheses']['H1_toponymic_vs_nontoponlaymic_immigration']
            if 'conclusion' in h1:
                logger.info(f"\nH1 (Toponymic vs Non-Toponymic Immigration):")
                logger.info(f"  {h1['conclusion']}")
        
        # H2: Toponymic Settlement Clustering
        if 'primary_hypotheses' in results and 'H2_toponymic_clustering' in results['primary_hypotheses']:
            h2 = results['primary_hypotheses']['H2_toponymic_clustering']
            if 'conclusion' in h2:
                logger.info(f"\nH2 (Toponymic Settlement Clustering):")
                logger.info(f"  {h2['conclusion']}")
        
        # H3: Temporal Dispersion by Category
        if 'primary_hypotheses' in results and 'H3_temporal_dispersion_by_category' in results['primary_hypotheses']:
            h3 = results['primary_hypotheses']['H3_temporal_dispersion_by_category']
            if 'conclusion' in h3:
                logger.info(f"\nH3 (Temporal Dispersion by Category):")
                logger.info(f"  {h3['conclusion']}")
        
        # H4: Place Importance
        if 'expanded_analyses' in results and 'H4_place_importance' in results['expanded_analyses']:
            h4 = results['expanded_analyses']['H4_place_importance']
            if 'conclusion' in h4:
                logger.info(f"\nH4 (Place Cultural Importance Effect):")
                logger.info(f"  {h4['conclusion']}")
        
        # H5: Cross-Category ANOVA
        if 'cross_category_comparisons' in results and 'conclusion' in results['cross_category_comparisons']:
            logger.info(f"\nH5 (Cross-Category Comparisons):")
            logger.info(f"  {results['cross_category_comparisons']['conclusion']}")
        
        # H6: Semantic × Origin Interactions
        if 'interaction_effects' in results and 'conclusion' in results['interaction_effects']:
            logger.info(f"\nH6 (Semantic × Origin Interactions):")
            logger.info(f"  {results['interaction_effects']['conclusion']}")
        
        logger.info("\n" + "="*70)
        logger.info(f"Analysis complete! Results exported to {output_dir}/")
        logger.info(f"Completed at: {datetime.now()}")
        logger.info("="*70)
        
        return 0


if __name__ == '__main__':
    sys.exit(main())

