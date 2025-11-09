"""
Blind Classification Test
==========================

OBJECTIVE validation of ensemble methodology.

Method:
1. Take texts with KNOWN truth-status (documentary vs fiction)
2. Remove all labels (blind analysis)
3. Classify based ONLY on ensemble patterns (variance, commonality, optimization)
4. Calculate accuracy, precision, recall, F1-score

If >70% accurate → methodology validated
If <60% accurate → methodology unreliable

This is CRITICAL for establishing method validity.
"""

import logging
import numpy as np
from typing import Dict, List, Tuple
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score, roc_curve
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

logger = logging.getLogger(__name__)


class BlindClassifier:
    """
    Blind classification of texts as fiction vs non-fiction using ONLY ensemble patterns.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.model = None
        self.feature_names = ['variance', 'mean_melodiousness', 'optimization_score', 
                             'mean_commonality', 'commonality_variance', 'repetition_rate']
        self.logger.info("BlindClassifier initialized")
    
    def blind_classification_test(self, labeled_texts: List[Dict]) -> Dict:
        """
        Perform blind classification test.
        
        Args:
            labeled_texts: List of dicts with:
                - 'features': [variance, mean_melod, optimization, ...]
                - 'true_label': 0 (fiction) or 1 (non-fiction/documentary)
                - 'text_name': Name of text (for reporting)
        
        Returns:
            Complete accuracy assessment
        """
        if len(labeled_texts) < 20:
            return {'error': 'Insufficient sample size for validation (need ≥20)'}
        
        # Extract features and labels
        X = np.array([t['features'] for t in labeled_texts])
        y = np.array([t['true_label'] for t in labeled_texts])
        text_names = [t['text_name'] for t in labeled_texts]
        
        # Train-test split (80-20)
        n_train = int(len(labeled_texts) * 0.8)
        indices = np.random.permutation(len(labeled_texts))
        
        train_idx = indices[:n_train]
        test_idx = indices[n_train:]
        
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        
        # Train simple logistic regression (interpretable)
        self.model = LogisticRegression(random_state=42, max_iter=1000)
        self.model.fit(X_train, y_train)
        
        # Predict on test set (BLIND - model hasn't seen these)
        y_pred = self.model.predict(X_test)
        y_proba = self.model.predict_proba(X_test)[:, 1]
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        
        # AUC-ROC
        if len(np.unique(y_test)) > 1:
            auc = roc_auc_score(y_test, y_proba)
        else:
            auc = None
        
        # Cross-validation on full dataset
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        cv_scores = cross_val_score(self.model, X, y, cv=cv, scoring='accuracy')
        
        # Feature importance (coefficients)
        feature_importance = {
            name: float(coef) 
            for name, coef in zip(self.feature_names, self.model.coef_[0])
        }
        
        return {
            'test_set_performance': {
                'accuracy': float(accuracy),
                'precision': float(precision),
                'recall': float(recall),
                'f1_score': float(f1),
                'auc_roc': float(auc) if auc else None
            },
            'confusion_matrix': {
                'true_negative': int(cm[0,0]),  # Correctly identified fiction
                'false_positive': int(cm[0,1]),  # Fiction called non-fiction
                'false_negative': int(cm[1,0]),  # Non-fiction called fiction
                'true_positive': int(cm[1,1])   # Correctly identified non-fiction
            },
            'cross_validation': {
                'mean_accuracy': float(cv_scores.mean()),
                'std_accuracy': float(cv_scores.std()),
                'scores': cv_scores.tolist()
            },
            'feature_importance': feature_importance,
            'interpretation': self._interpret_accuracy(accuracy, precision, recall),
            'methodology_validated': accuracy > 0.70
        }
    
    def _interpret_accuracy(self, accuracy: float, precision: float, recall: float) -> str:
        """Interpret classification accuracy."""
        if accuracy > 0.80:
            verdict = "EXCELLENT"
            interpretation = "Methodology strongly validated. Ensemble patterns reliably discriminate truth-status."
        elif accuracy > 0.70:
            verdict = "GOOD"
            interpretation = "Methodology validated. Ensemble patterns provide useful information about truth-status."
        elif accuracy > 0.60:
            verdict = "MODERATE"
            interpretation = "Methodology shows promise but needs refinement. Better than chance but not reliable."
        else:
            verdict = "POOR"
            interpretation = "Methodology not validated. Ensemble patterns don't reliably predict truth-status. Back to drawing board."
        
        return f"{verdict}: Accuracy={accuracy:.1%}, Precision={precision:.1%}, Recall={recall:.1%}. {interpretation}"
    
    def classify_unknown_text(self, features: np.ndarray) -> Dict:
        """
        Classify a text of unknown truth-status.
        
        Args:
            features: Feature vector [variance, mean_melodiousness, ...]
        
        Returns:
            Classification with probability
        """
        if self.model is None:
            return {'error': 'Model not trained. Run blind_classification_test first.'}
        
        features = features.reshape(1, -1)
        prediction = self.model.predict(features)[0]
        probability = self.model.predict_proba(features)[0]
        
        return {
            'prediction': 'non-fiction/documentary' if prediction == 1 else 'fiction',
            'confidence': float(probability[prediction]),
            'probabilities': {
                'fiction': float(probability[0]),
                'non-fiction': float(probability[1])
            }
        }


# Singleton
blind_classifier = BlindClassifier()

