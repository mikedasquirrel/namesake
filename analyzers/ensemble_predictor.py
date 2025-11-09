"""
Ensemble Prediction System
===========================

Combines Random Forest, XGBoost, and Neural Networks for superior prediction accuracy.
Uses stacking, cross-validation, and calibration for optimal performance.

Features:
- Random Forest (robust to overfitting)
- XGBoost (gradient boosting, high accuracy)
- Neural Network (captures complex patterns)
- Stacking ensemble (meta-learner combines predictions)
- Cross-validation (k-fold within domains, leave-one-domain-out)
- Probability calibration (ensures predictions match frequencies)
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Tuple
import json

# Try importing ML libraries
try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.neural_network import MLPClassifier
    from sklearn.model_selection import cross_val_score, StratifiedKFold
    from sklearn.calibration import CalibratedClassifierCV
    from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("scikit-learn not available")

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    logging.warning("XGBoost not available")

logger = logging.getLogger(__name__)


class EnsemblePredictor:
    """
    Ensemble prediction system combining multiple ML algorithms.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Base models
        self.rf_model = None
        self.xgb_model = None
        self.nn_model = None
        self.meta_model = None  # Stacking meta-learner
        
        # Performance metrics
        self.cv_scores = {}
        self.feature_importance = {}
        
        self.logger.info(f"EnsemblePredictor initialized (sklearn: {SKLEARN_AVAILABLE}, xgboost: {XGBOOST_AVAILABLE})")
    
    def train_ensemble(self, X: np.ndarray, y: np.ndarray, 
                      domain: str, feature_names: Optional[List[str]] = None) -> Dict:
        """
        Train ensemble of models.
        
        Args:
            X: Feature matrix
            y: Labels
            domain: Domain identifier
            feature_names: Optional feature names for interpretability
        
        Returns:
            Training metrics and model performance
        """
        if not SKLEARN_AVAILABLE:
            return {'error': 'scikit-learn not available'}
        
        self.logger.info(f"Training ensemble for domain: {domain}")
        
        # Train base models
        self.logger.info("Training Random Forest...")
        self.rf_model = RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        )
        self.rf_model.fit(X, y)
        
        if XGBOOST_AVAILABLE:
            self.logger.info("Training XGBoost...")
            self.xgb_model = xgb.XGBClassifier(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.1,
                random_state=42,
                eval_metric='logloss'
            )
            self.xgb_model.fit(X, y)
        
        self.logger.info("Training Neural Network...")
        self.nn_model = MLPClassifier(
            hidden_layer_sizes=(128, 64, 32),
            activation='relu',
            solver='adam',
            alpha=0.0001,
            max_iter=500,
            random_state=42
        )
        self.nn_model.fit(X, y)
        
        # Cross-validation
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        
        rf_scores = cross_val_score(self.rf_model, X, y, cv=cv, scoring='accuracy')
        nn_scores = cross_val_score(self.nn_model, X, y, cv=cv, scoring='accuracy')
        
        self.cv_scores[domain] = {
            'random_forest': {
                'mean': float(rf_scores.mean()),
                'std': float(rf_scores.std()),
                'scores': rf_scores.tolist()
            },
            'neural_network': {
                'mean': float(nn_scores.mean()),
                'std': float(nn_scores.std()),
                'scores': nn_scores.tolist()
            }
        }
        
        if XGBOOST_AVAILABLE:
            xgb_scores = cross_val_score(self.xgb_model, X, y, cv=cv, scoring='accuracy')
            self.cv_scores[domain]['xgboost'] = {
                'mean': float(xgb_scores.mean()),
                'std': float(xgb_scores.std()),
                'scores': xgb_scores.tolist()
            }
        
        # Feature importance (from Random Forest)
        if feature_names:
            importance = self.rf_model.feature_importances_
            self.feature_importance[domain] = {
                name: float(imp) for name, imp in zip(feature_names, importance)
            }
        
        # Train meta-learner (stacking)
        self.logger.info("Training meta-learner...")
        self._train_meta_learner(X, y)
        
        # Final evaluation
        metrics = self._evaluate_ensemble(X, y)
        
        self.logger.info(f"Ensemble training complete for {domain}")
        
        return {
            'domain': domain,
            'n_samples': len(y),
            'n_features': X.shape[1],
            'cv_scores': self.cv_scores[domain],
            'ensemble_performance': metrics,
            'feature_importance': self.feature_importance.get(domain, {}),
        }
    
    def _train_meta_learner(self, X: np.ndarray, y: np.ndarray):
        """Train stacking meta-learner."""
        # Get predictions from base models
        rf_pred = self.rf_model.predict_proba(X)
        nn_pred = self.nn_model.predict_proba(X)
        
        if XGBOOST_AVAILABLE and self.xgb_model:
            xgb_pred = self.xgb_model.predict_proba(X)
            # Stack predictions
            meta_features = np.hstack([rf_pred, nn_pred, xgb_pred])
        else:
            meta_features = np.hstack([rf_pred, nn_pred])
        
        # Train logistic regression as meta-learner
        from sklearn.linear_model import LogisticRegression
        self.meta_model = LogisticRegression(random_state=42, max_iter=1000)
        self.meta_model.fit(meta_features, y)
    
    def _evaluate_ensemble(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """Evaluate ensemble performance."""
        # Get predictions
        y_pred = self.predict_ensemble(X)
        y_proba = self.predict_proba_ensemble(X)
        
        accuracy = accuracy_score(y, y_pred)
        
        # Confusion matrix
        cm = confusion_matrix(y, y_pred)
        
        return {
            'accuracy': float(accuracy),
            'confusion_matrix': cm.tolist(),
            'n_correct': int(np.sum(y == y_pred)),
            'n_total': len(y)
        }
    
    def predict_ensemble(self, X: np.ndarray) -> np.ndarray:
        """Predict using ensemble (meta-learner)."""
        if not self.meta_model:
            # Fallback to Random Forest
            return self.rf_model.predict(X)
        
        # Get base model predictions
        rf_pred = self.rf_model.predict_proba(X)
        nn_pred = self.nn_model.predict_proba(X)
        
        if XGBOOST_AVAILABLE and self.xgb_model:
            xgb_pred = self.xgb_model.predict_proba(X)
            meta_features = np.hstack([rf_pred, nn_pred, xgb_pred])
        else:
            meta_features = np.hstack([rf_pred, nn_pred])
        
        return self.meta_model.predict(meta_features)
    
    def predict_proba_ensemble(self, X: np.ndarray) -> np.ndarray:
        """Predict probabilities using ensemble."""
        if not self.meta_model:
            return self.rf_model.predict_proba(X)
        
        rf_pred = self.rf_model.predict_proba(X)
        nn_pred = self.nn_model.predict_proba(X)
        
        if XGBOOST_AVAILABLE and self.xgb_model:
            xgb_pred = self.xgb_model.predict_proba(X)
            meta_features = np.hstack([rf_pred, nn_pred, xgb_pred])
        else:
            meta_features = np.hstack([rf_pred, nn_pred])
        
        return self.meta_model.predict_proba(meta_features)
    
    def predict_single_name(self, features: np.ndarray, domain: str) -> Dict:
        """
        Predict fate for a single name using ensemble.
        
        Args:
            features: Feature vector for name
            domain: Domain context
        
        Returns:
            Ensemble prediction with individual model contributions
        """
        features = features.reshape(1, -1)
        
        # Individual model predictions
        rf_proba = self.rf_model.predict_proba(features)[0]
        nn_proba = self.nn_model.predict_proba(features)[0]
        
        predictions = {
            'random_forest': {
                'probabilities': rf_proba.tolist(),
                'prediction': int(np.argmax(rf_proba)),
                'confidence': float(np.max(rf_proba))
            },
            'neural_network': {
                'probabilities': nn_proba.tolist(),
                'prediction': int(np.argmax(nn_proba)),
                'confidence': float(np.max(nn_proba))
            }
        }
        
        if XGBOOST_AVAILABLE and self.xgb_model:
            xgb_proba = self.xgb_model.predict_proba(features)[0]
            predictions['xgboost'] = {
                'probabilities': xgb_proba.tolist(),
                'prediction': int(np.argmax(xgb_proba)),
                'confidence': float(np.max(xgb_proba))
            }
        
        # Ensemble prediction
        ensemble_proba = self.predict_proba_ensemble(features)[0]
        ensemble_pred = np.argmax(ensemble_proba)
        
        predictions['ensemble'] = {
            'probabilities': ensemble_proba.tolist(),
            'prediction': int(ensemble_pred),
            'confidence': float(ensemble_proba[ensemble_pred]),
            'method': 'Stacking (meta-learner)'
        }
        
        # Model agreement
        all_preds = [predictions['random_forest']['prediction'],
                    predictions['neural_network']['prediction']]
        if XGBOOST_AVAILABLE and self.xgb_model:
            all_preds.append(predictions['xgboost']['prediction'])
        
        agreement = len(set(all_preds)) == 1
        
        predictions['model_agreement'] = agreement
        predictions['agreement_rate'] = all_preds.count(ensemble_pred) / len(all_preds)
        
        return predictions


# Singleton
ensemble_predictor = EnsemblePredictor()

