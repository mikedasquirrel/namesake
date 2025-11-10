"""
Hypothesis Testing Framework

Tests specific hypotheses about narrative advantage in cryptocurrency naming.

Hypotheses:
- H1: Story quality predicts better than demographics
- H2: Character role complementarity
- H4: Ensemble diversity predicts openness
- H5: Omissions more predictive than inclusions
- H6: Context-dependent weights outperform static

Author: Narrative Integration System
Date: November 2025
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import logging

logger = logging.getLogger(__name__)


class HypothesisTest:
    """Framework for testing narrative advantage hypotheses."""
    
    def __init__(self, evaluator):
        """
        Initialize hypothesis tester.
        
        Args:
            evaluator: NarrativeEvaluator instance with results
        """
        self.evaluator = evaluator
        self.test_results = {}
    
    def test_h1_narrative_vs_baseline(self, narrative_pipeline: str,
                                     baseline_pipeline: str,
                                     metric: str = 'f1_macro',
                                     threshold: float = 0.05) -> Dict[str, Any]:
        """
        Test H1: Narrative features outperform statistical baseline.
        
        Args:
            narrative_pipeline: Name of narrative pipeline
            baseline_pipeline: Name of baseline pipeline
            metric: Metric to compare
            threshold: Minimum improvement threshold (e.g., 5 percentage points)
        
        Returns:
            Dict with test results
        """
        logger.info("Testing H1: Narrative vs Baseline")
        
        # Get scores
        narrative_scores = self.evaluator.results[narrative_pipeline]['cv_scores'][metric]['test_scores']
        baseline_scores = self.evaluator.results[baseline_pipeline]['cv_scores'][metric]['test_scores']
        
        narrative_mean = np.mean(narrative_scores)
        baseline_mean = np.mean(baseline_scores)
        improvement = narrative_mean - baseline_mean
        
        # Statistical test
        sig_test = self.evaluator.statistical_significance_test(
            narrative_pipeline, baseline_pipeline, metric
        )
        
        # Hypothesis result
        validated = improvement > threshold and sig_test['significant']
        
        result = {
            'hypothesis': 'H1: Story quality predicts better than demographics',
            'narrative_pipeline': narrative_pipeline,
            'baseline_pipeline': baseline_pipeline,
            'metric': metric,
            'narrative_score': narrative_mean,
            'baseline_score': baseline_mean,
            'improvement': improvement,
            'improvement_pct': (improvement / baseline_mean) * 100,
            'threshold': threshold,
            'statistical_test': sig_test,
            'validated': validated,
            'interpretation': self._interpret_h1(validated, improvement, sig_test)
        }
        
        self.test_results['H1'] = result
        logger.info(f"  H1 validated: {validated} (improvement: {improvement:.4f})")
        
        return result
    
    def test_h2_complementarity(self, feature_matrix: np.ndarray,
                               labels: np.ndarray,
                               complementarity_indices: List[int]) -> Dict[str, Any]:
        """
        Test H2: Complementarity features correlate with success.
        
        Args:
            feature_matrix: Full feature matrix
            labels: Target labels
            complementarity_indices: Indices of complementarity features
        
        Returns:
            Dict with test results
        """
        logger.info("Testing H2: Complementarity predicts success")
        
        # Extract complementarity features
        comp_features = feature_matrix[:, complementarity_indices]
        
        # Calculate correlation with success (log market cap or binary)
        correlations = []
        p_values = []
        
        for i in range(comp_features.shape[1]):
            corr, p_val = stats.pearsonr(comp_features[:, i], labels)
            correlations.append(corr)
            p_values.append(p_val)
        
        avg_correlation = np.mean(np.abs(correlations))
        significant_count = np.sum(np.array(p_values) < 0.05)
        
        # Regression test
        reg = LinearRegression()
        reg.fit(comp_features, labels)
        r2 = r2_score(labels, reg.predict(comp_features))
        
        validated = avg_correlation > 0.10 and significant_count > len(complementarity_indices) * 0.5
        
        result = {
            'hypothesis': 'H2: Character role complementarity',
            'n_features': len(complementarity_indices),
            'avg_correlation': avg_correlation,
            'significant_features': significant_count,
            'r2_score': r2,
            'correlations': correlations,
            'p_values': p_values,
            'validated': validated,
            'interpretation': self._interpret_h2(validated, avg_correlation, significant_count)
        }
        
        self.test_results['H2'] = result
        logger.info(f"  H2 validated: {validated} (avg correlation: {avg_correlation:.4f})")
        
        return result
    
    def test_h4_ensemble_diversity(self, feature_matrix: np.ndarray,
                                   labels: np.ndarray,
                                   diversity_indices: List[int]) -> Dict[str, Any]:
        """
        Test H4: Ensemble diversity predicts success.
        
        Args:
            feature_matrix: Full feature matrix
            labels: Target labels
            diversity_indices: Indices of diversity features
        
        Returns:
            Dict with test results
        """
        logger.info("Testing H4: Ensemble diversity predicts success")
        
        # Extract diversity features
        diversity_features = feature_matrix[:, diversity_indices]
        
        # Test correlation
        correlations = []
        for i in range(diversity_features.shape[1]):
            corr, _ = stats.pearsonr(diversity_features[:, i], labels)
            correlations.append(corr)
        
        avg_correlation = np.mean(correlations)
        
        # Compare success groups
        successful = labels > np.median(labels)
        diversity_successful = np.mean(diversity_features[successful], axis=0)
        diversity_unsuccessful = np.mean(diversity_features[~successful], axis=0)
        
        t_stats = []
        p_values = []
        for i in range(diversity_features.shape[1]):
            t_stat, p_val = stats.ttest_ind(
                diversity_features[successful, i],
                diversity_features[~successful, i]
            )
            t_stats.append(t_stat)
            p_values.append(p_val)
        
        significant_count = np.sum(np.array(p_values) < 0.05)
        validated = avg_correlation > 0 and significant_count > 0
        
        result = {
            'hypothesis': 'H4: Ensemble diversity predicts openness',
            'n_features': len(diversity_indices),
            'avg_correlation': avg_correlation,
            'significant_features': significant_count,
            'diversity_successful_mean': diversity_successful.tolist(),
            'diversity_unsuccessful_mean': diversity_unsuccessful.tolist(),
            't_statistics': t_stats,
            'p_values': p_values,
            'validated': validated,
            'interpretation': self._interpret_h4(validated, avg_correlation)
        }
        
        self.test_results['H4'] = result
        logger.info(f"  H4 validated: {validated} (avg correlation: {avg_correlation:.4f})")
        
        return result
    
    def test_h5_omissions_vs_inclusions(self, feature_matrix: np.ndarray,
                                       labels: np.ndarray,
                                       positive_indices: List[int],
                                       negative_indices: List[int]) -> Dict[str, Any]:
        """
        Test H5: Omissions more predictive than inclusions.
        
        Args:
            feature_matrix: Full feature matrix
            labels: Target labels
            positive_indices: Indices of "inclusion" features
            negative_indices: Indices of "omission" features
        
        Returns:
            Dict with test results
        """
        logger.info("Testing H5: Omissions vs inclusions")
        
        # Extract features
        positive_features = feature_matrix[:, positive_indices]
        negative_features = feature_matrix[:, negative_indices]
        
        # Fit separate models
        reg_positive = LinearRegression()
        reg_negative = LinearRegression()
        
        reg_positive.fit(positive_features, labels)
        reg_negative.fit(negative_features, labels)
        
        r2_positive = r2_score(labels, reg_positive.predict(positive_features))
        r2_negative = r2_score(labels, reg_negative.predict(negative_features))
        
        validated = r2_negative > r2_positive
        
        result = {
            'hypothesis': 'H5: Omissions more predictive than inclusions',
            'n_positive_features': len(positive_indices),
            'n_negative_features': len(negative_indices),
            'r2_positive': r2_positive,
            'r2_negative': r2_negative,
            'difference': r2_negative - r2_positive,
            'validated': validated,
            'interpretation': self._interpret_h5(validated, r2_positive, r2_negative)
        }
        
        self.test_results['H5'] = result
        logger.info(f"  H5 validated: {validated} (R² negative: {r2_negative:.4f}, R² positive: {r2_positive:.4f})")
        
        return result
    
    def test_h6_context_dependent(self, feature_matrix_relative: np.ndarray,
                                  feature_matrix_absolute: np.ndarray,
                                  labels: np.ndarray,
                                  pipeline_relative: str,
                                  pipeline_absolute: str,
                                  metric: str = 'f1_macro') -> Dict[str, Any]:
        """
        Test H6: Context-dependent (relative) features outperform static (absolute).
        
        Args:
            feature_matrix_relative: Features with relative/zscore values
            feature_matrix_absolute: Features with absolute values only
            labels: Target labels
            pipeline_relative: Name of pipeline with relative features
            pipeline_absolute: Name of pipeline with absolute features
            metric: Metric to compare
        
        Returns:
            Dict with test results
        """
        logger.info("Testing H6: Context-dependent vs static features")
        
        # Get scores from evaluator if pipelines exist
        if pipeline_relative in self.evaluator.results and pipeline_absolute in self.evaluator.results:
            relative_score = self.evaluator.results[pipeline_relative]['cv_scores'][metric]['test_mean']
            absolute_score = self.evaluator.results[pipeline_absolute]['cv_scores'][metric]['test_mean']
            
            sig_test = self.evaluator.statistical_significance_test(
                pipeline_relative, pipeline_absolute, metric
            )
            
            improvement = relative_score - absolute_score
            validated = improvement > 0.03 and sig_test['significant']
            
            result = {
                'hypothesis': 'H6: Context-dependent weights outperform static',
                'relative_score': relative_score,
                'absolute_score': absolute_score,
                'improvement': improvement,
                'statistical_test': sig_test,
                'validated': validated,
                'interpretation': self._interpret_h6(validated, improvement)
            }
        else:
            # Fallback: just compare R² scores
            reg_relative = LinearRegression()
            reg_absolute = LinearRegression()
            
            reg_relative.fit(feature_matrix_relative, labels)
            reg_absolute.fit(feature_matrix_absolute, labels)
            
            r2_relative = r2_score(labels, reg_relative.predict(feature_matrix_relative))
            r2_absolute = r2_score(labels, reg_absolute.predict(feature_matrix_absolute))
            
            validated = r2_relative > r2_absolute
            
            result = {
                'hypothesis': 'H6: Context-dependent weights outperform static',
                'r2_relative': r2_relative,
                'r2_absolute': r2_absolute,
                'difference': r2_relative - r2_absolute,
                'validated': validated,
                'interpretation': self._interpret_h6(validated, r2_relative - r2_absolute)
            }
        
        self.test_results['H6'] = result
        logger.info(f"  H6 validated: {validated}")
        
        return result
    
    def _interpret_h1(self, validated: bool, improvement: float, sig_test: Dict) -> str:
        """Interpret H1 results."""
        if validated:
            return (f"✓ VALIDATED: Narrative features outperform baseline by {improvement:.4f} "
                   f"({improvement*100:.1f}%). {sig_test['interpretation']}. "
                   f"This supports the core narrative advantage hypothesis.")
        else:
            return (f"✗ NOT VALIDATED: Narrative improvement of {improvement:.4f} "
                   f"does not meet threshold or significance criteria. "
                   f"Baseline may be sufficient or narrative encoding needs refinement.")
    
    def _interpret_h2(self, validated: bool, avg_corr: float, sig_count: int) -> str:
        """Interpret H2 results."""
        if validated:
            return (f"✓ VALIDATED: Complementarity features show average correlation of {avg_corr:.4f} "
                   f"with {sig_count} significant features. Cryptos with complementary semantic "
                   f"profiles achieve better market positioning.")
        else:
            return (f"✗ NOT VALIDATED: Weak complementarity effects (r={avg_corr:.4f}). "
                   f"Portfolio complementarity may not matter in crypto naming.")
    
    def _interpret_h4(self, validated: bool, avg_corr: float) -> str:
        """Interpret H4 results."""
        if validated:
            return (f"✓ VALIDATED: Ensemble diversity positively predicts success (r={avg_corr:.4f}). "
                   f"Cryptos with diverse semantic elements and broad network positioning perform better.")
        else:
            return (f"✗ NOT VALIDATED: Diversity shows weak effects (r={avg_corr:.4f}). "
                   f"Focus or specialization may be more important than diversity.")
    
    def _interpret_h5(self, validated: bool, r2_pos: float, r2_neg: float) -> str:
        """Interpret H5 results."""
        if validated:
            return (f"✓ VALIDATED: Omission features (R²={r2_neg:.4f}) explain more variance than "
                   f"inclusion features (R²={r2_pos:.4f}). What cryptos AVOID matters more than "
                   f"what they include.")
        else:
            return (f"✗ NOT VALIDATED: Inclusion features (R²={r2_pos:.4f}) perform as well or "
                   f"better than omissions (R²={r2_neg:.4f}).")
    
    def _interpret_h6(self, validated: bool, improvement: float) -> str:
        """Interpret H6 results."""
        if validated:
            return (f"✓ VALIDATED: Relative features improve performance by {improvement:.4f}. "
                   f"Competitive context matters—names are evaluated relative to cohort, not absolutely.")
        else:
            return (f"✗ NOT VALIDATED: Relative features show minimal advantage ({improvement:.4f}). "
                   f"Absolute features may be sufficient.")
    
    def export_hypothesis_report(self, output_path: str) -> None:
        """
        Export hypothesis test results to JSON and markdown.
        
        Args:
            output_path: Output path for report
        """
        import json
        from pathlib import Path
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # JSON export
        json_path = output_path.parent / f"{output_path.stem}_hypotheses.json"
        with open(json_path, 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
        
        logger.info(f"✓ Exported hypothesis results to {json_path}")
        
        # Markdown report
        md_path = output_path.parent / f"{output_path.stem}_hypotheses.md"
        with open(md_path, 'w') as f:
            f.write("# Hypothesis Test Results\n\n")
            f.write("## Summary\n\n")
            
            validated_count = sum(1 for r in self.test_results.values() if r.get('validated', False))
            f.write(f"**Validated**: {validated_count}/{len(self.test_results)} hypotheses\n\n")
            
            f.write("## Individual Tests\n\n")
            for h_id, result in self.test_results.items():
                f.write(f"### {h_id}: {result['hypothesis']}\n\n")
                f.write(f"**Status**: {'✓ VALIDATED' if result['validated'] else '✗ NOT VALIDATED'}\n\n")
                f.write(f"{result['interpretation']}\n\n")
                f.write("---\n\n")
        
        logger.info(f"✓ Exported hypothesis report to {md_path}")

