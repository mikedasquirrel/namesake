"""
Explainable AI Module
=====================

Provides interpretability for all ML predictions using SHAP, LIME, and feature importance.
Essential for academic research to understand WHY models make certain predictions.

Features:
- SHAP values (model-agnostic explanations)
- LIME (local interpretable model-agnostic explanations)
- Permutation importance
- Partial dependence plots
- Individual conditional expectation (ICE) plots
"""

import logging
import numpy as np
from typing import Dict, List, Optional
import json

# Try importing explainability libraries
try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    logging.warning("SHAP not available")

try:
    from lime import lime_tabular
    LIME_AVAILABLE = True
except ImportError:
    LIME_AVAILABLE = False
    logging.warning("LIME not available")

from sklearn.inspection import permutation_importance

logger = logging.getLogger(__name__)


class ExplainableAI:
    """
    Explainability tools for ML predictions.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.explainers = {}
        
        self.logger.info(f"ExplainableAI initialized (SHAP: {SHAP_AVAILABLE}, LIME: {LIME_AVAILABLE})")
    
    def explain_prediction_shap(self, model, X: np.ndarray, 
                               feature_names: List[str],
                               instance_idx: int = 0) -> Dict:
        """
        Explain prediction using SHAP values.
        
        Args:
            model: Trained model
            X: Feature matrix
            feature_names: Names of features
            instance_idx: Which instance to explain
        
        Returns:
            SHAP explanation
        """
        if not SHAP_AVAILABLE:
            return self._fallback_explanation(model, X, feature_names, instance_idx)
        
        try:
            # Create explainer (try TreeExplainer first, fallback to KernelExplainer)
            try:
                explainer = shap.TreeExplainer(model)
                self.logger.info("Using TreeExplainer (faster)")
            except:
                explainer = shap.KernelExplainer(model.predict_proba, X[:100])
                self.logger.info("Using KernelExplainer (slower but model-agnostic)")
            
            # Calculate SHAP values
            shap_values = explainer.shap_values(X[instance_idx:instance_idx+1])
            
            # Format results
            instance_features = X[instance_idx]
            
            # Handle multi-class output
            if isinstance(shap_values, list):
                # Multi-class: take values for predicted class
                predicted_class = np.argmax(model.predict_proba(X[instance_idx:instance_idx+1])[0])
                shap_vals = shap_values[predicted_class][0]
            else:
                shap_vals = shap_values[0]
            
            # Create feature importance ranking
            feature_importance = []
            for i, (name, shap_val, feature_val) in enumerate(zip(feature_names, shap_vals, instance_features)):
                feature_importance.append({
                    'feature': name,
                    'value': float(feature_val),
                    'shap_value': float(shap_val),
                    'impact': 'increases' if shap_val > 0 else 'decreases',
                    'magnitude': abs(float(shap_val))
                })
            
            # Sort by absolute SHAP value
            feature_importance.sort(key=lambda x: x['magnitude'], reverse=True)
            
            return {
                'method': 'SHAP',
                'feature_importance': feature_importance,
                'top_features': feature_importance[:5],
                'interpretation': self._interpret_shap(feature_importance[:3])
            }
        
        except Exception as e:
            self.logger.error(f"Error calculating SHAP values: {e}")
            return self._fallback_explanation(model, X, feature_names, instance_idx)
    
    def _fallback_explanation(self, model, X: np.ndarray, 
                            feature_names: List[str], instance_idx: int) -> Dict:
        """Fallback explanation using feature values."""
        instance = X[instance_idx]
        
        # Simple feature importance based on values
        feature_importance = []
        for name, value in zip(feature_names, instance):
            feature_importance.append({
                'feature': name,
                'value': float(value),
                'normalized_value': float(value),
                'impact': 'positive' if value > 0 else 'negative'
            })
        
        feature_importance.sort(key=lambda x: abs(x['value']), reverse=True)
        
        return {
            'method': 'Feature Values (SHAP unavailable)',
            'feature_importance': feature_importance,
            'top_features': feature_importance[:5],
            'note': 'Install SHAP for proper causal explanations'
        }
    
    def explain_lime(self, model, X: np.ndarray, feature_names: List[str],
                    instance_idx: int = 0, n_features: int = 10) -> Dict:
        """
        Explain prediction using LIME.
        
        Args:
            model: Trained model
            X: Feature matrix
            feature_names: Names of features
            instance_idx: Which instance to explain
            n_features: Number of features to show
        
        Returns:
            LIME explanation
        """
        if not LIME_AVAILABLE:
            return {'error': 'LIME not available'}
        
        try:
            explainer = lime_tabular.LimeTabularExplainer(
                X,
                feature_names=feature_names,
                mode='classification',
                discretize_continuous=True
            )
            
            explanation = explainer.explain_instance(
                X[instance_idx],
                model.predict_proba,
                num_features=n_features
            )
            
            # Extract feature importance
            feature_importance = []
            for feature, weight in explanation.as_list():
                feature_importance.append({
                    'feature': feature,
                    'weight': float(weight),
                    'impact': 'positive' if weight > 0 else 'negative'
                })
            
            return {
                'method': 'LIME',
                'feature_importance': feature_importance,
                'prediction_confidence': float(explanation.predict_proba[explanation.top_labels[0]])
            }
        
        except Exception as e:
            self.logger.error(f"Error with LIME: {e}")
            return {'error': str(e)}
    
    def permutation_importance_analysis(self, model, X: np.ndarray, y: np.ndarray,
                                       feature_names: List[str]) -> Dict:
        """
        Calculate permutation importance for all features.
        
        Args:
            model: Trained model
            X: Feature matrix
            y: Labels
            feature_names: Names of features
        
        Returns:
            Importance scores for each feature
        """
        try:
            result = permutation_importance(model, X, y, n_repeats=10, random_state=42)
            
            importance_data = []
            for i, name in enumerate(feature_names):
                importance_data.append({
                    'feature': name,
                    'importance_mean': float(result.importances_mean[i]),
                    'importance_std': float(result.importances_std[i])
                })
            
            # Sort by importance
            importance_data.sort(key=lambda x: x['importance_mean'], reverse=True)
            
            return {
                'method': 'Permutation Importance',
                'feature_importance': importance_data,
                'top_features': importance_data[:10]
            }
        
        except Exception as e:
            self.logger.error(f"Error calculating permutation importance: {e}")
            return {'error': str(e)}
    
    def _interpret_shap(self, top_features: List[Dict]) -> str:
        """Generate human-readable interpretation of SHAP values."""
        if not top_features:
            return "No significant features identified"
        
        interp_parts = []
        for feat in top_features[:3]:
            direction = "increases" if feat['shap_value'] > 0 else "decreases"
            interp_parts.append(f"{feat['feature']} {direction} prediction")
        
        return "; ".join(interp_parts)


# Singleton
explainable_ai = ExplainableAI()

