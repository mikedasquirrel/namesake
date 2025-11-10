"""
Competitive Improvement Tester
Tests whether competitive context improves modeling vs absolute features alone
"""

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class CompetitiveImprovementTester:
    """
    Test if competitive context improves predictive models
    Compares: Absolute → Relative → Market → Story Coherence
    """
    
    def __init__(self):
        self.results = {}
    
    def run_comparative_test(self, 
                            entities: List[Dict],
                            domain: str,
                            outcome_key: str = 'views') -> Dict:
        """
        Run complete test comparing model types
        
        Args:
            entities: List with competitive_context added
            domain: Domain name
            outcome_key: What we're predicting
        
        Returns:
            Complete comparison results
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"COMPETITIVE IMPROVEMENT TEST: {domain}")
        logger.info(f"{'='*80}\n")
        
        logger.info(f"Testing on {len(entities)} entities")
        
        # Extract outcomes
        outcomes = np.array([e.get(outcome_key, 0) for e in entities])
        
        # Model 1: Absolute features only
        logger.info("\nModel 1: ABSOLUTE FEATURES")
        logger.info("-" * 80)
        results_abs = self._test_absolute_model(entities, outcomes)
        logger.info(f"  r = {results_abs['r']:.4f}, R² = {results_abs['r2']:.4f}, p = {results_abs['p']:.6f}")
        
        # Model 2: Relative features
        logger.info("\nModel 2: RELATIVE FEATURES (vs cohort)")
        logger.info("-" * 80)
        results_rel = self._test_relative_model(entities, outcomes)
        logger.info(f"  r = {results_rel['r']:.4f}, R² = {results_rel['r2']:.4f}, p = {results_rel['p']:.6f}")
        improvement_rel = (results_rel['r2'] - results_abs['r2']) / results_abs['r2'] * 100 if results_abs['r2'] > 0 else float('inf')
        logger.info(f"  Improvement: +{improvement_rel:.1f}% vs absolute")
        
        # Model 3: Market context
        logger.info("\nModel 3: MARKET CONTEXT (saturation + timing)")
        logger.info("-" * 80)
        results_mkt = self._test_market_model(entities, outcomes)
        logger.info(f"  r = {results_mkt['r']:.4f}, R² = {results_mkt['r2']:.4f}, p = {results_mkt['p']:.6f}")
        improvement_mkt = (results_mkt['r2'] - results_abs['r2']) / results_abs['r2'] * 100 if results_abs['r2'] > 0 else float('inf')
        logger.info(f"  Improvement: +{improvement_mkt:.1f}% vs absolute")
        
        # Model 4: Story coherence
        logger.info("\nModel 4: STORY COHERENCE (across all nominal elements)")
        logger.info("-" * 80)
        results_full = self._test_story_coherence_model(entities, outcomes)
        logger.info(f"  r = {results_full['r']:.4f}, R² = {results_full['r2']:.4f}, p = {results_full['p']:.6f}")
        improvement_full = (results_full['r2'] - results_abs['r2']) / results_abs['r2'] * 100 if results_abs['r2'] > 0 else float('inf')
        logger.info(f"  Improvement: +{improvement_full:.1f}% vs absolute")
        
        # Summary
        logger.info(f"\n{'='*80}")
        logger.info("SUMMARY")
        logger.info(f"{'='*80}")
        logger.info(f"Absolute Model:        r = {results_abs['r']:.4f}")
        logger.info(f"Relative Model:        r = {results_rel['r']:.4f}  (+{improvement_rel:.0f}%)")
        logger.info(f"Market Context Model:  r = {results_mkt['r']:.4f}  (+{improvement_mkt:.0f}%)")
        logger.info(f"Full Story Model:      r = {results_full['r']:.4f}  (+{improvement_full:.0f}%)")
        logger.info(f"\n{'='*80}\n")
        
        return {
            'domain': domain,
            'n_entities': len(entities),
            'models': {
                'absolute': results_abs,
                'relative': results_rel,
                'market': results_mkt,
                'story_coherence': results_full
            },
            'improvements': {
                'relative_vs_absolute': improvement_rel,
                'market_vs_absolute': improvement_mkt,
                'full_vs_absolute': improvement_full
            }
        }
    
    def _test_absolute_model(self, entities: List[Dict], outcomes: np.ndarray) -> Dict:
        """Test model with absolute features only"""
        
        # Extract absolute features
        features_list = []
        for e in entities:
            features_list.append([
                e.get('harshness', 0),
                e.get('syllables', 0),
                e.get('length', 0),
                e.get('memorability', 0)
            ])
        
        X = np.array(features_list)
        
        # Simple correlation for first feature (harshness)
        if len(X) > 0:
            r, p = stats.pearsonr(X[:, 0], outcomes)
            
            # Multiple regression
            model = LinearRegression()
            model.fit(X, outcomes)
            predictions = model.predict(X)
            r2 = r2_score(outcomes, predictions)
            
            return {
                'r': float(r),
                'p': float(p),
                'r2': float(r2),
                'n_features': X.shape[1]
            }
        
        return {'r': 0.0, 'p': 1.0, 'r2': 0.0, 'n_features': 0}
    
    def _test_relative_model(self, entities: List[Dict], outcomes: np.ndarray) -> Dict:
        """Test model with relative features"""
        
        features_list = []
        for e in entities:
            competitive = e.get('competitive_context', {})
            relative = competitive.get('relative_features', {})
            
            features_list.append([
                relative.get('relative_harshness', 0),
                relative.get('relative_syllables', 0),
                relative.get('relative_length', 0),
                relative.get('zscore_harshness', 0)
            ])
        
        X = np.array(features_list)
        
        if len(X) > 0:
            r, p = stats.pearsonr(X[:, 0], outcomes)
            
            model = LinearRegression()
            model.fit(X, outcomes)
            predictions = model.predict(X)
            r2 = r2_score(outcomes, predictions)
            
            return {
                'r': float(r),
                'p': float(p),
                'r2': float(r2),
                'n_features': X.shape[1]
            }
        
        return {'r': 0.0, 'p': 1.0, 'r2': 0.0, 'n_features': 0}
    
    def _test_market_model(self, entities: List[Dict], outcomes: np.ndarray) -> Dict:
        """Test model with market context (saturation, timing)"""
        
        features_list = []
        for e in entities:
            competitive = e.get('competitive_context', {})
            relative = competitive.get('relative_features', {})
            
            features_list.append([
                relative.get('relative_harshness', 0),
                relative.get('zscore_harshness', 0),
                competitive.get('market_saturation', 0.5),
                competitive.get('cohort_size', 100) / 1000  # Normalize
            ])
        
        X = np.array(features_list)
        
        if len(X) > 0:
            r, p = stats.pearsonr(X[:, 0], outcomes)
            
            model = LinearRegression()
            model.fit(X, outcomes)
            predictions = model.predict(X)
            r2 = r2_score(outcomes, predictions)
            
            return {
                'r': float(r),
                'p': float(p),
                'r2': float(r2),
                'n_features': X.shape[1]
            }
        
        return {'r': 0.0, 'p': 1.0, 'r2': 0.0, 'n_features': 0}
    
    def _test_story_coherence_model(self, entities: List[Dict], outcomes: np.ndarray) -> Dict:
        """Test model with story coherence across ALL elements"""
        
        features_list = []
        for e in entities:
            competitive = e.get('competitive_context', {})
            relative = competitive.get('relative_features', {})
            
            features_list.append([
                relative.get('relative_harshness', 0),
                competitive.get('market_saturation', 0.5),
                e.get('title_category_coherence', 0.5),
                e.get('overall_story_coherence', 0.5),
                e.get('n_categories', 3) / 10  # Normalize
            ])
        
        X = np.array(features_list)
        
        if len(X) > 0:
            r, p = stats.pearsonr(X[:, 0], outcomes)
            
            model = LinearRegression()
            model.fit(X, outcomes)
            predictions = model.predict(X)
            r2 = r2_score(outcomes, predictions)
            
            return {
                'r': float(r),
                'p': float(p),
                'r2': float(r2),
                'n_features': X.shape[1]
            }
        
        return {'r': 0.0, 'p': 1.0, 'r2': 0.0, 'n_features': 0}
    
    def document_learned_patterns(self, results: Dict) -> str:
        """
        Create narrative documentation of what was learned
        """
        domain = results['domain']
        models = results['models']
        
        doc = f"# Learned Patterns: {domain}\n\n"
        doc += f"## Model Performance\n\n"
        doc += f"- **Absolute Features**: r = {models['absolute']['r']:.4f}\n"
        doc += f"- **Relative Features**: r = {models['relative']['r']:.4f}\n"
        doc += f"- **Market Context**: r = {models['market']['r']:.4f}\n"
        doc += f"- **Story Coherence**: r = {models['story_coherence']['r']:.4f}\n\n"
        
        doc += f"## Improvements\n\n"
        for comparison, improvement in results['improvements'].items():
            doc += f"- {comparison}: +{improvement:.1f}%\n"
        
        doc += f"\n## Interpretation\n\n"
        doc += self._generate_interpretation(results)
        
        return doc
    
    def _generate_interpretation(self, results: Dict) -> str:
        """Generate human-readable interpretation"""
        
        best_model = max(results['models'].items(), key=lambda x: x[1]['r'])
        model_name = best_model[0]
        model_r = best_model[1]['r']
        
        interp = f"The {model_name} model performed best (r = {model_r:.4f}), "
        
        if model_name == 'absolute':
            interp += "suggesting competitive context doesn't add much value in this domain."
        elif model_name == 'relative':
            interp += "suggesting relative positioning within cohort is crucial."
        elif model_name == 'market':
            interp += "suggesting market saturation and timing drive outcomes."
        else:  # story_coherence
            interp += "suggesting coherent stories across ALL nominal elements matter most."
        
        return interp

