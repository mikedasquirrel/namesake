"""
Crypto Narrative Experiments - Master Execution Script

Runs comprehensive narrative optimization experiments on cryptocurrency data.

Workflow:
1. Load Format C data
2. Build all pipelines
3. Run cross-validation experiments
4. Test hypotheses
5. Generate results and visualizations
6. Export findings

Author: Narrative Integration System
Date: November 2025
"""

import sys
from pathlib import Path
import pickle
import logging
import numpy as np
from sklearn.model_selection import StratifiedKFold
import warnings
warnings.filterwarnings('ignore')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from narrative_integration.pipelines.pipeline_builder import NarrativePipelineBuilder
from narrative_integration.experiments.evaluation import NarrativeEvaluator
from narrative_integration.experiments.hypothesis_tests import HypothesisTest


def main():
    """Main execution function."""
    
    logger.info("="*80)
    logger.info("CRYPTO NARRATIVE OPTIMIZATION EXPERIMENTS")
    logger.info("="*80)
    logger.info("")
    
    # =========================================================================
    # STEP 1: Load Data
    # =========================================================================
    logger.info("STEP 1: Loading Format C Data")
    logger.info("-"*80)
    
    data_path = project_root / 'narrative_integration' / 'data' / 'crypto_format_c.pkl'
    
    try:
        with open(data_path, 'rb') as f:
            format_c_data = pickle.load(f)
        
        logger.info(f"✓ Loaded Format C data from {data_path}")
        
        # Extract data
        X_text = format_c_data['data']['texts']
        X_features = format_c_data['data']['features']
        y_binary = format_c_data['data']['labels_binary']
        y_regression = format_c_data['data']['labels_regression']
        metadata = format_c_data['data']['metadata']
        
        logger.info(f"  - Samples: {len(X_text)}")
        logger.info(f"  - Features: {X_features.shape[1]}")
        logger.info(f"  - Class distribution: {np.bincount(y_binary)}")
        logger.info("")
        
    except FileNotFoundError:
        logger.error(f"✗ Format C data not found at {data_path}")
        logger.error("  Run crypto_format_c.py first to generate data")
        return
    
    # =========================================================================
    # STEP 2: Build Pipelines
    # =========================================================================
    logger.info("STEP 2: Building Narrative Pipelines")
    logger.info("-"*80)
    
    config_path = project_root / 'narrative_integration' / 'crypto_pipeline_config.json'
    builder = NarrativePipelineBuilder(str(config_path))
    
    # Build individual transformer pipelines
    pipelines = {}
    
    logger.info("Building individual transformer pipelines...")
    
    # 1. Nominative Analysis
    pipelines['nominative_analysis'] = builder.build_pipeline(
        'nominative',
        classifier_type='gradient_boosting',
        transformer_params={'n_semantic_fields': 10, 'crypto_specific': True}
    )
    
    # 2. Narrative Potential
    pipelines['narrative_potential'] = builder.build_pipeline(
        'potential',
        classifier_type='gradient_boosting',
        transformer_params={'track_modality': True, 'innovation_markers': True}
    )
    
    # 3. Ensemble Effects
    pipelines['ensemble_effects'] = builder.build_pipeline(
        'ensemble',
        classifier_type='gradient_boosting',
        transformer_params={'n_top_terms': 50, 'network_metrics': True}
    )
    
    # 4. Relational Value
    pipelines['relational_value'] = builder.build_pipeline(
        'relational',
        classifier_type='gradient_boosting',
        transformer_params={'n_features': 100, 'complementarity_threshold': 0.3}
    )
    
    # 5. Semantic Clustering
    pipelines['semantic_clustering'] = builder.build_pipeline(
        'semantic',
        classifier_type='gradient_boosting',
        transformer_params={'n_components': 50, 'n_clusters': 10}
    )
    
    # 6. Statistical Baseline
    pipelines['statistical_baseline'] = builder.build_pipeline(
        'statistical',
        classifier_type='gradient_boosting',
        transformer_params={'max_features': 1000}
    )
    
    # 7. Combined pipeline
    logger.info("Building combined multi-transformer pipeline...")
    pipelines['combined_narrative'] = builder.build_combined_pipeline(
        ['nominative', 'potential', 'ensemble', 'relational'],
        classifier_type='gradient_boosting'
    )
    
    logger.info(f"✓ Built {len(pipelines)} pipelines")
    logger.info("")
    
    # =========================================================================
    # STEP 3: Run Experiments with Cross-Validation
    # =========================================================================
    logger.info("STEP 3: Running Cross-Validation Experiments")
    logger.info("-"*80)
    
    # Setup evaluator
    cv_strategy = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    evaluator = NarrativeEvaluator(
        cv_strategy=cv_strategy,
        metrics=['f1_macro', 'f1_weighted', 'accuracy', 'roc_auc', 
                'precision_macro', 'recall_macro', 'matthews_corrcoef']
    )
    
    # Evaluate each pipeline
    results = []
    for pipeline_name, pipeline in pipelines.items():
        logger.info(f"\nEvaluating: {pipeline_name}")
        try:
            result = evaluator.evaluate_pipeline(pipeline, X_text, y_binary, pipeline_name)
            results.append(result)
        except Exception as e:
            logger.error(f"  ✗ Failed to evaluate {pipeline_name}: {str(e)}")
            continue
    
    logger.info("")
    logger.info("✓ All experiments complete")
    logger.info("")
    
    # =========================================================================
    # STEP 4: Compare Performance
    # =========================================================================
    logger.info("STEP 4: Performance Comparison")
    logger.info("-"*80)
    
    comparison_df = evaluator.compare_pipelines(results)
    
    logger.info("\nPerformance Rankings (by F1 Macro):")
    logger.info("")
    for i, row in comparison_df.iterrows():
        logger.info(f"  {i+1}. {row['Pipeline']:30s} - F1: {row['f1_macro_mean']:.4f} ± {row['f1_macro_std']:.4f}")
    
    logger.info("")
    
    # Best pipeline
    best_name, best_score = evaluator.get_best_pipeline('f1_macro')
    logger.info(f"🏆 Best Pipeline: {best_name} (F1 = {best_score:.4f})")
    logger.info("")
    
    # =========================================================================
    # STEP 5: Statistical Significance Tests
    # =========================================================================
    logger.info("STEP 5: Statistical Significance Testing")
    logger.info("-"*80)
    
    # Compare top narrative pipeline vs baseline
    if 'statistical_baseline' in evaluator.results:
        sig_test = evaluator.statistical_significance_test(
            best_name, 'statistical_baseline', 'f1_macro'
        )
        
        logger.info(f"\n{best_name} vs Statistical Baseline:")
        logger.info(f"  Mean difference: {sig_test['mean_diff']:.4f}")
        logger.info(f"  P-value: {sig_test['p_value']:.4f}")
        logger.info(f"  Cohen's d: {sig_test['cohens_d']:.4f}")
        logger.info(f"  Significant: {sig_test['significant']}")
        logger.info(f"  {sig_test['interpretation']}")
        logger.info("")
    
    # =========================================================================
    # STEP 6: Hypothesis Testing
    # =========================================================================
    logger.info("STEP 6: Testing Hypotheses")
    logger.info("-"*80)
    
    hypothesis_tester = HypothesisTest(evaluator)
    
    # H1: Narrative vs Baseline
    logger.info("\nH1: Story quality predicts better than demographics")
    try:
        h1_result = hypothesis_tester.test_h1_narrative_vs_baseline(
            best_name, 'statistical_baseline', 
            metric='f1_macro', threshold=0.05
        )
        logger.info(f"  Result: {'✓ VALIDATED' if h1_result['validated'] else '✗ NOT VALIDATED'}")
        logger.info(f"  {h1_result['interpretation']}")
    except Exception as e:
        logger.error(f"  ✗ H1 test failed: {str(e)}")
    
    # H2: Complementarity
    logger.info("\nH2: Character role complementarity")
    try:
        # Find relational features from combined pipeline
        if 'relational_value' in evaluator.results:
            # For H2, we need the relational features
            # This is a simplified version - in full implementation,
            # we'd extract features from fitted transformer
            logger.info("  (Requires fitted transformer feature extraction - placeholder)")
            # h2_result = hypothesis_tester.test_h2_complementarity(...)
    except Exception as e:
        logger.error(f"  ✗ H2 test failed: {str(e)}")
    
    # H4: Ensemble diversity
    logger.info("\nH4: Ensemble diversity predicts openness")
    try:
        if 'ensemble_effects' in evaluator.results:
            logger.info("  (Requires fitted transformer feature extraction - placeholder)")
            # h4_result = hypothesis_tester.test_h4_ensemble_diversity(...)
    except Exception as e:
        logger.error(f"  ✗ H4 test failed: {str(e)}")
    
    # H6: Context-dependent features
    logger.info("\nH6: Context-dependent weights outperform static")
    try:
        # Compare performance with/without relative features
        logger.info("  (Requires ablation study - placeholder)")
        # Would need to create pipelines with/without relative features
    except Exception as e:
        logger.error(f"  ✗ H6 test failed: {str(e)}")
    
    logger.info("")
    
    # =========================================================================
    # STEP 7: Export Results
    # =========================================================================
    logger.info("STEP 7: Exporting Results")
    logger.info("-"*80)
    
    results_dir = project_root / 'narrative_integration' / 'results'
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # Export evaluator results
    evaluator.export_results(str(results_dir / 'crypto_experiments'))
    
    # Export hypothesis results
    hypothesis_tester.export_hypothesis_report(str(results_dir / 'crypto_experiments'))
    
    # Save best pipeline
    best_pipeline = pipelines[best_name]
    logger.info(f"Training best pipeline on full dataset: {best_name}")
    best_pipeline.fit(X_text, y_binary)
    builder.save_pipeline(best_pipeline, str(results_dir / 'models' / f'{best_name}.pkl'))
    
    # Save all pipelines
    logger.info("Saving all trained pipelines...")
    for name, pipeline in pipelines.items():
        logger.info(f"  Training: {name}")
        pipeline.fit(X_text, y_binary)
        builder.save_pipeline(pipeline, str(results_dir / 'models' / f'{name}.pkl'))
    
    logger.info("")
    logger.info("="*80)
    logger.info("✅ EXPERIMENTS COMPLETE")
    logger.info("="*80)
    logger.info("")
    logger.info(f"Results saved to: {results_dir}")
    logger.info(f"Best pipeline: {best_name} (F1 = {best_score:.4f})")
    logger.info("")
    logger.info("Next steps:")
    logger.info("  1. Review results in narrative_integration/results/")
    logger.info("  2. Examine hypothesis validation reports")
    logger.info("  3. Create visualizations")
    logger.info("  4. Integrate into Flask app")
    logger.info("")


if __name__ == '__main__':
    main()

