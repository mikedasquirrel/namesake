"""
Narrative Evaluator

Comprehensive evaluation framework for narrative optimization experiments.
Handles cross-validation, metrics calculation, and performance comparison.

Author: Narrative Integration System
Date: November 2025
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from sklearn.model_selection import cross_validate, cross_val_predict
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score,
    roc_auc_score, matthews_corrcoef, confusion_matrix,
    classification_report, make_scorer
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NarrativeEvaluator:
    """Evaluate narrative pipelines with comprehensive metrics."""
    
    def __init__(self, cv_strategy, metrics: Optional[List[str]] = None,
                 random_seed: int = 42):
        """
        Initialize evaluator.
        
        Args:
            cv_strategy: Cross-validation strategy (e.g., StratifiedKFold)
            metrics: List of metric names to compute
            random_seed: Random seed for reproducibility
        """
        self.cv_strategy = cv_strategy
        self.random_seed = random_seed
        
        # Default metrics
        if metrics is None:
            self.metrics = [
                'accuracy', 'f1_macro', 'f1_weighted', 
                'precision_macro', 'recall_macro', 'roc_auc'
            ]
        else:
            self.metrics = metrics
        
        # Results storage
        self.results = {}
    
    def evaluate_pipeline(self, pipeline, X, y, pipeline_name: str) -> Dict[str, Any]:
        """
        Evaluate a single pipeline with cross-validation.
        
        Args:
            pipeline: Sklearn pipeline to evaluate
            X: Feature data (can be text list or array)
            y: Target labels
            pipeline_name: Name for this pipeline
        
        Returns:
            Dict with evaluation results
        """
        logger.info(f"Evaluating pipeline: {pipeline_name}")
        
        # Build scoring dict
        scoring = self._build_scoring_dict()
        
        try:
            # Cross-validation
            cv_results = cross_validate(
                pipeline, X, y,
                cv=self.cv_strategy,
                scoring=scoring,
                return_train_score=True,
                n_jobs=-1,
                error_score='raise'
            )
            
            # Get predictions for confusion matrix
            y_pred = cross_val_predict(
                pipeline, X, y,
                cv=self.cv_strategy,
                n_jobs=-1
            )
            
            # Calculate confusion matrix
            cm = confusion_matrix(y, y_pred)
            
            # Organize results
            results = {
                'pipeline_name': pipeline_name,
                'cv_scores': {},
                'predictions': y_pred,
                'confusion_matrix': cm,
                'classification_report': classification_report(y, y_pred, output_dict=True)
            }
            
            # Extract CV scores
            for metric in self.metrics:
                test_key = f'test_{metric}'
                train_key = f'train_{metric}'
                
                if test_key in cv_results:
                    results['cv_scores'][metric] = {
                        'test_scores': cv_results[test_key],
                        'test_mean': np.mean(cv_results[test_key]),
                        'test_std': np.std(cv_results[test_key]),
                        'train_scores': cv_results[train_key],
                        'train_mean': np.mean(cv_results[train_key]),
                        'train_std': np.std(cv_results[train_key])
                    }
            
            # Store results
            self.results[pipeline_name] = results
            
            logger.info(f"  ✓ {pipeline_name} - F1 Macro: {results['cv_scores']['f1_macro']['test_mean']:.4f} ± {results['cv_scores']['f1_macro']['test_std']:.4f}")
            
            return results
            
        except Exception as e:
            logger.error(f"  ✗ Error evaluating {pipeline_name}: {str(e)}")
            raise
    
    def compare_pipelines(self, results_list: List[Dict]) -> pd.DataFrame:
        """
        Compare multiple pipeline results.
        
        Args:
            results_list: List of result dicts from evaluate_pipeline
        
        Returns:
            DataFrame with comparison
        """
        comparison_data = []
        
        for result in results_list:
            row = {'Pipeline': result['pipeline_name']}
            
            for metric in self.metrics:
                if metric in result['cv_scores']:
                    row[f'{metric}_mean'] = result['cv_scores'][metric]['test_mean']
                    row[f'{metric}_std'] = result['cv_scores'][metric]['test_std']
            
            comparison_data.append(row)
        
        df = pd.DataFrame(comparison_data)
        
        # Sort by primary metric (f1_macro)
        if 'f1_macro_mean' in df.columns:
            df = df.sort_values('f1_macro_mean', ascending=False)
        
        return df
    
    def get_best_pipeline(self, metric: str = 'f1_macro') -> Tuple[str, float]:
        """
        Get best performing pipeline by metric.
        
        Args:
            metric: Metric to use for comparison
        
        Returns:
            Tuple of (pipeline_name, score)
        """
        best_name = None
        best_score = -np.inf
        
        for name, result in self.results.items():
            if metric in result['cv_scores']:
                score = result['cv_scores'][metric]['test_mean']
                if score > best_score:
                    best_score = score
                    best_name = name
        
        return best_name, best_score
    
    def statistical_significance_test(self, pipeline1_name: str, 
                                     pipeline2_name: str,
                                     metric: str = 'f1_macro') -> Dict[str, Any]:
        """
        Test statistical significance between two pipelines.
        
        Uses paired t-test on cross-validation scores.
        
        Args:
            pipeline1_name: Name of first pipeline
            pipeline2_name: Name of second pipeline
            metric: Metric to compare
        
        Returns:
            Dict with test results
        """
        from scipy import stats
        
        if pipeline1_name not in self.results or pipeline2_name not in self.results:
            raise ValueError("Both pipelines must have been evaluated")
        
        scores1 = self.results[pipeline1_name]['cv_scores'][metric]['test_scores']
        scores2 = self.results[pipeline2_name]['cv_scores'][metric]['test_scores']
        
        # Paired t-test
        t_stat, p_value = stats.ttest_rel(scores1, scores2)
        
        # Effect size (Cohen's d)
        diff = scores1 - scores2
        cohens_d = np.mean(diff) / (np.std(diff) + 1e-10)
        
        return {
            'pipeline1': pipeline1_name,
            'pipeline2': pipeline2_name,
            'metric': metric,
            'mean_diff': np.mean(diff),
            't_statistic': t_stat,
            'p_value': p_value,
            'cohens_d': cohens_d,
            'significant': p_value < 0.05,
            'interpretation': self._interpret_significance(p_value, cohens_d)
        }
    
    def _interpret_significance(self, p_value: float, cohens_d: float) -> str:
        """Interpret statistical significance results."""
        if p_value < 0.001:
            sig = "highly significant (p < 0.001)"
        elif p_value < 0.01:
            sig = "very significant (p < 0.01)"
        elif p_value < 0.05:
            sig = "significant (p < 0.05)"
        else:
            sig = "not significant (p ≥ 0.05)"
        
        if abs(cohens_d) < 0.2:
            effect = "negligible effect size"
        elif abs(cohens_d) < 0.5:
            effect = "small effect size"
        elif abs(cohens_d) < 0.8:
            effect = "medium effect size"
        else:
            effect = "large effect size"
        
        direction = "improvement" if cohens_d > 0 else "decline"
        
        return f"{sig} with {effect} ({direction})"
    
    def _build_scoring_dict(self) -> Dict[str, Any]:
        """Build scoring dictionary for cross_validate."""
        scoring = {}
        
        for metric in self.metrics:
            if metric == 'accuracy':
                scoring['accuracy'] = 'accuracy'
            elif metric == 'f1_macro':
                scoring['f1_macro'] = 'f1_macro'
            elif metric == 'f1_weighted':
                scoring['f1_weighted'] = 'f1_weighted'
            elif metric == 'precision_macro':
                scoring['precision_macro'] = 'precision_macro'
            elif metric == 'recall_macro':
                scoring['recall_macro'] = 'recall_macro'
            elif metric == 'roc_auc':
                scoring['roc_auc'] = 'roc_auc'
            elif metric == 'matthews_corrcoef':
                scoring['matthews_corrcoef'] = make_scorer(matthews_corrcoef)
        
        return scoring
    
    def export_results(self, output_path: str) -> None:
        """
        Export results to JSON and CSV.
        
        Args:
            output_path: Base path for output files
        """
        import json
        from pathlib import Path
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Prepare export data (convert numpy arrays to lists)
        export_data = {}
        for name, result in self.results.items():
            cv_scores_serializable = {}
            for metric, scores in result['cv_scores'].items():
                cv_scores_serializable[metric] = {
                    'test_scores': scores['test_scores'].tolist() if hasattr(scores['test_scores'], 'tolist') else scores['test_scores'],
                    'test_mean': float(scores['test_mean']),
                    'test_std': float(scores['test_std']),
                    'train_scores': scores['train_scores'].tolist() if hasattr(scores['train_scores'], 'tolist') else scores['train_scores'],
                    'train_mean': float(scores['train_mean']),
                    'train_std': float(scores['train_std'])
                }
            
            export_data[name] = {
                'cv_scores': cv_scores_serializable,
                'confusion_matrix': result['confusion_matrix'].tolist(),
                'classification_report': result['classification_report']
            }
        
        # Save JSON
        json_path = output_path.parent / f"{output_path.stem}_results.json"
        with open(json_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"✓ Exported results to {json_path}")
        
        # Save comparison CSV
        results_list = [result for result in self.results.values()]
        comparison_df = self.compare_pipelines(results_list)
        csv_path = output_path.parent / f"{output_path.stem}_comparison.csv"
        comparison_df.to_csv(csv_path, index=False)
        
        logger.info(f"✓ Exported comparison to {csv_path}")

