"""
Interaction Detector - Automatic Discovery of Non-Linear Patterns

Discovers polynomial terms, two-way and three-way interactions, and threshold
effects in phonetic-outcome relationships.

This is critical for the revolutionary approach, as linear models miss:
- Inverse-U relationships (optimal complexity sweet spots)
- Synergistic effects (harshness × genre)
- Threshold gates (memorability > 80 required for high performance)
"""

import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Tuple, Optional
from scipy import stats
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.linear_model import Ridge, Lasso
from sklearn.model_selection import cross_val_score
from itertools import combinations

logger = logging.getLogger(__name__)


class InteractionDetector:
    """
    Detects and quantifies non-linear phonetic interactions.
    
    Methods:
    1. Polynomial terms (x, x², x³)
    2. Two-way interactions (x × y)
    3. Three-way interactions (x × y × z)
    4. Threshold effects (x > threshold gates y's impact)
    5. Sign flips (x positive in one context, negative in another)
    """
    
    def __init__(self, significance_threshold: float = 0.05):
        """
        Initialize interaction detector.
        
        Args:
            significance_threshold: P-value threshold for significance
        """
        self.significance_threshold = significance_threshold
        self.scaler = StandardScaler()
    
    def detect_all_interactions(self, data: pd.DataFrame, 
                                outcome_col: str,
                                feature_cols: List[str],
                                categorical_cols: Optional[List[str]] = None) -> Dict:
        """
        Comprehensive interaction detection.
        
        Args:
            data: DataFrame with features and outcome
            outcome_col: Name of outcome column
            feature_cols: List of phonetic feature columns
            categorical_cols: Optional categorical variables (genre, color, etc.)
            
        Returns:
            Dictionary with detected interactions and their statistics
        """
        results = {
            'polynomial_terms': [],
            'two_way_interactions': [],
            'three_way_interactions': [],
            'threshold_effects': [],
            'sign_flips': [],
            'summary': {}
        }
        
        # Clean data
        clean_data = data[[outcome_col] + feature_cols].dropna()
        
        if len(clean_data) < 30:
            logger.warning(f"Insufficient data for interaction detection: n={len(clean_data)}")
            return results
        
        X = clean_data[feature_cols].values
        y = clean_data[outcome_col].values
        
        # Standardize for comparison
        X_scaled = self.scaler.fit_transform(X)
        
        logger.info(f"Detecting interactions: n={len(clean_data)}, features={len(feature_cols)}")
        
        # 1. Polynomial terms
        results['polynomial_terms'] = self.detect_polynomial_terms(
            X_scaled, y, feature_cols
        )
        
        # 2. Two-way interactions
        results['two_way_interactions'] = self.detect_two_way_interactions(
            X_scaled, y, feature_cols
        )
        
        # 3. Three-way interactions (if enough data)
        if len(clean_data) >= 100:
            results['three_way_interactions'] = self.detect_three_way_interactions(
                X_scaled, y, feature_cols
            )
        
        # 4. Threshold effects
        results['threshold_effects'] = self.detect_threshold_effects(
            X_scaled, y, feature_cols
        )
        
        # 5. Sign flips (if categorical variables provided)
        if categorical_cols:
            results['sign_flips'] = self.detect_sign_flips(
                data, outcome_col, feature_cols, categorical_cols
            )
        
        # Summary statistics
        results['summary'] = {
            'total_polynomial_terms': len(results['polynomial_terms']),
            'total_two_way': len(results['two_way_interactions']),
            'total_three_way': len(results['three_way_interactions']),
            'total_thresholds': len(results['threshold_effects']),
            'total_sign_flips': len(results['sign_flips']),
            'sample_size': len(clean_data),
            'features_tested': len(feature_cols)
        }
        
        return results
    
    def detect_polynomial_terms(self, X: np.ndarray, y: np.ndarray, 
                                feature_names: List[str]) -> List[Dict]:
        """
        Detect polynomial relationships (quadratic, cubic).
        
        Tests if x² or x³ significantly improves prediction.
        """
        polynomial_terms = []
        
        for i, feature_name in enumerate(feature_names):
            x = X[:, i]
            
            # Test quadratic (x²)
            x_squared = x ** 2
            
            # Linear model
            corr_linear, p_linear = stats.pearsonr(x, y)
            
            # Quadratic model (include both x and x²)
            X_quad = np.column_stack([x, x_squared])
            
            try:
                # Use Ridge to avoid multicollinearity issues
                model_quad = Ridge(alpha=0.1)
                scores_quad = cross_val_score(model_quad, X_quad, y, cv=5, scoring='r2')
                
                # Simple linear for comparison
                model_linear = Ridge(alpha=0.1)
                scores_linear = cross_val_score(model_linear, x.reshape(-1, 1), y, cv=5, scoring='r2')
                
                improvement = scores_quad.mean() - scores_linear.mean()
                
                # Statistical test: is quadratic significantly better?
                t_stat, p_val = stats.ttest_ind(scores_quad, scores_linear)
                
                if p_val < self.significance_threshold and improvement > 0.01:
                    # Detect shape (U-shaped or inverted-U)
                    model_quad.fit(X_quad, y)
                    quad_coef = model_quad.coef_[1]
                    
                    polynomial_terms.append({
                        'feature': feature_name,
                        'degree': 2,
                        'shape': 'inverse_u' if quad_coef < 0 else 'u_shaped',
                        'r2_improvement': round(improvement, 4),
                        'p_value': round(p_val, 4),
                        'quadratic_coefficient': round(quad_coef, 4),
                        'interpretation': self._interpret_polynomial(
                            feature_name, 'inverse_u' if quad_coef < 0 else 'u_shaped'
                        )
                    })
            
            except Exception as e:
                logger.debug(f"Error testing polynomial for {feature_name}: {e}")
                continue
        
        return polynomial_terms
    
    def detect_two_way_interactions(self, X: np.ndarray, y: np.ndarray,
                                    feature_names: List[str]) -> List[Dict]:
        """
        Detect two-way interactions (x × y).
        
        Tests if product of two features predicts better than sum.
        """
        interactions = []
        
        # Test all pairwise combinations
        for i, j in combinations(range(len(feature_names)), 2):
            x1 = X[:, i]
            x2 = X[:, j]
            
            # Interaction term
            x_interaction = x1 * x2
            
            # Additive model (x1 + x2)
            X_add = np.column_stack([x1, x2])
            
            # Interaction model (x1 + x2 + x1×x2)
            X_int = np.column_stack([x1, x2, x_interaction])
            
            try:
                model_add = Ridge(alpha=0.1)
                scores_add = cross_val_score(model_add, X_add, y, cv=5, scoring='r2')
                
                model_int = Ridge(alpha=0.1)
                scores_int = cross_val_score(model_int, X_int, y, cv=5, scoring='r2')
                
                improvement = scores_int.mean() - scores_add.mean()
                
                if improvement > 0.02:  # At least 2% R² improvement
                    # Fit to get interaction coefficient
                    model_int.fit(X_int, y)
                    interaction_coef = model_int.coef_[2]
                    
                    # Statistical significance
                    t_stat, p_val = stats.ttest_ind(scores_int, scores_add)
                    
                    if p_val < self.significance_threshold:
                        interactions.append({
                            'feature_1': feature_names[i],
                            'feature_2': feature_names[j],
                            'r2_improvement': round(improvement, 4),
                            'p_value': round(p_val, 4),
                            'interaction_coefficient': round(interaction_coef, 4),
                            'effect_type': 'synergistic' if interaction_coef > 0 else 'antagonistic',
                            'interpretation': self._interpret_two_way(
                                feature_names[i], feature_names[j], interaction_coef
                            )
                        })
            
            except Exception as e:
                logger.debug(f"Error testing interaction {feature_names[i]} × {feature_names[j]}: {e}")
                continue
        
        # Sort by R² improvement
        interactions.sort(key=lambda x: x['r2_improvement'], reverse=True)
        
        # Return top 10
        return interactions[:10]
    
    def detect_three_way_interactions(self, X: np.ndarray, y: np.ndarray,
                                      feature_names: List[str]) -> List[Dict]:
        """
        Detect three-way interactions (x × y × z).
        
        Computationally expensive, so only test most promising triplets.
        """
        interactions = []
        
        # Limit to reasonable number (top features)
        if len(feature_names) > 10:
            # Use correlation with outcome to select top features
            correlations = [abs(stats.pearsonr(X[:, i], y)[0]) for i in range(len(feature_names))]
            top_indices = np.argsort(correlations)[-10:]
            top_features = [feature_names[i] for i in top_indices]
        else:
            top_indices = range(len(feature_names))
            top_features = feature_names
        
        # Test triplets
        count = 0
        max_tests = 20  # Limit computational burden
        
        for i, j, k in combinations(top_indices, 3):
            if count >= max_tests:
                break
            
            x1 = X[:, i]
            x2 = X[:, j]
            x3 = X[:, k]
            
            # Three-way interaction
            x_triple = x1 * x2 * x3
            
            # Two-way model (all two-way interactions)
            X_two = np.column_stack([x1, x2, x3, x1*x2, x1*x3, x2*x3])
            
            # Three-way model (add triple interaction)
            X_three = np.column_stack([x1, x2, x3, x1*x2, x1*x3, x2*x3, x_triple])
            
            try:
                model_two = Ridge(alpha=0.5)
                scores_two = cross_val_score(model_two, X_two, y, cv=3, scoring='r2')
                
                model_three = Ridge(alpha=0.5)
                scores_three = cross_val_score(model_three, X_three, y, cv=3, scoring='r2')
                
                improvement = scores_three.mean() - scores_two.mean()
                
                if improvement > 0.03:  # At least 3% improvement
                    interactions.append({
                        'feature_1': feature_names[i],
                        'feature_2': feature_names[j],
                        'feature_3': feature_names[k],
                        'r2_improvement': round(improvement, 4),
                        'interpretation': f"{feature_names[i]} × {feature_names[j]} × {feature_names[k]}"
                    })
            
            except Exception as e:
                logger.debug(f"Error testing 3-way interaction: {e}")
                continue
            
            count += 1
        
        interactions.sort(key=lambda x: x['r2_improvement'], reverse=True)
        return interactions[:5]
    
    def detect_threshold_effects(self, X: np.ndarray, y: np.ndarray,
                                 feature_names: List[str]) -> List[Dict]:
        """
        Detect threshold effects (gates).
        
        Tests if feature X has different effects above/below threshold.
        Example: memorability > 80 gates high performance in crypto.
        """
        thresholds = []
        
        for i, feature_name in enumerate(feature_names):
            x = X[:, i]
            
            # Try different threshold percentiles
            for percentile in [25, 50, 75]:
                threshold = np.percentile(x, percentile)
                
                # Split into above/below threshold
                above_threshold = x >= threshold
                below_threshold = x < threshold
                
                if np.sum(above_threshold) < 10 or np.sum(below_threshold) < 10:
                    continue  # Need sufficient samples in each group
                
                # Compare outcome distributions
                y_above = y[above_threshold]
                y_below = y[below_threshold]
                
                # Statistical test
                t_stat, p_val = stats.ttest_ind(y_above, y_below)
                
                effect_size = (y_above.mean() - y_below.mean()) / y.std()
                
                if p_val < self.significance_threshold and abs(effect_size) > 0.3:
                    thresholds.append({
                        'feature': feature_name,
                        'threshold_percentile': percentile,
                        'threshold_value': round(threshold, 3),
                        'effect_size': round(effect_size, 3),
                        'p_value': round(p_val, 4),
                        'mean_above': round(y_above.mean(), 2),
                        'mean_below': round(y_below.mean(), 2),
                        'interpretation': self._interpret_threshold(
                            feature_name, percentile, effect_size
                        )
                    })
        
        thresholds.sort(key=lambda x: abs(x['effect_size']), reverse=True)
        return thresholds[:10]
    
    def detect_sign_flips(self, data: pd.DataFrame, outcome_col: str,
                         feature_cols: List[str], categorical_cols: List[str]) -> List[Dict]:
        """
        Detect sign flips across contexts.
        
        Example: memorability positive in MTG, negative in crypto.
        """
        sign_flips = []
        
        for cat_col in categorical_cols:
            if cat_col not in data.columns:
                continue
            
            categories = data[cat_col].unique()
            
            if len(categories) < 2:
                continue
            
            for feature in feature_cols:
                if feature not in data.columns:
                    continue
                
                correlations = {}
                
                for category in categories:
                    cat_data = data[data[cat_col] == category]
                    
                    if len(cat_data) < 20:
                        continue
                    
                    try:
                        corr, p_val = stats.pearsonr(
                            cat_data[feature].dropna(),
                            cat_data[outcome_col].dropna()
                        )
                        
                        if p_val < self.significance_threshold:
                            correlations[category] = corr
                    
                    except:
                        continue
                
                # Check for sign flips
                if len(correlations) >= 2:
                    corr_values = list(correlations.values())
                    
                    # Sign flip if min and max have opposite signs
                    if min(corr_values) < -0.1 and max(corr_values) > 0.1:
                        sign_flips.append({
                            'feature': feature,
                            'context_variable': cat_col,
                            'correlations': {k: round(v, 3) for k, v in correlations.items()},
                            'interpretation': self._interpret_sign_flip(
                                feature, cat_col, correlations
                            )
                        })
        
        return sign_flips
    
    def _interpret_polynomial(self, feature: str, shape: str) -> str:
        """Generate interpretation for polynomial term."""
        if shape == 'inverse_u':
            return f"{feature} has optimal sweet spot (too low or too high both hurt)"
        else:
            return f"{feature} has extreme advantage (very low or very high best)"
    
    def _interpret_two_way(self, feat1: str, feat2: str, coef: float) -> str:
        """Generate interpretation for two-way interaction."""
        if coef > 0:
            return f"{feat1} and {feat2} synergize (work better together)"
        else:
            return f"{feat1} and {feat2} trade off (one works best when other is low)"
    
    def _interpret_threshold(self, feature: str, percentile: int, effect_size: float) -> str:
        """Generate interpretation for threshold effect."""
        direction = "much higher" if effect_size > 0 else "much lower"
        return f"Above {percentile}th percentile of {feature}, outcomes are {direction}"
    
    def _interpret_sign_flip(self, feature: str, context: str, 
                            correlations: Dict) -> str:
        """Generate interpretation for sign flip."""
        contexts = list(correlations.keys())
        return f"{feature} effect flips across {context}: {contexts[0]} vs {contexts[1]}"


# Convenience functions
def quick_interaction_analysis(data: pd.DataFrame, outcome_col: str,
                               feature_cols: List[str]) -> Dict:
    """Quick interaction analysis for exploratory work."""
    detector = InteractionDetector()
    return detector.detect_all_interactions(data, outcome_col, feature_cols)

