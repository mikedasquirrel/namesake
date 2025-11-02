"""
Formula Optimizer - Find THE OPTIMAL FORMULA for Nominative Determinism
Assumes theory is TRUE, finds best weighted combination of name features
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize, differential_evolution
from sklearn.model_selection import cross_val_score, KFold
from sklearn.linear_model import Ridge, Lasso, ElasticNet
from sklearn.preprocessing import StandardScaler
from core.models import db, Cryptocurrency, NameAnalysis, PriceHistory
import logging
import json

logger = logging.getLogger(__name__)


class FormulaOptimizer:
    """Find the optimal formula for predicting crypto performance from names"""
    
    def __init__(self):
        self.feature_names = ['syllables', 'length', 'memorability', 'uniqueness', 'phonetic', 'pronounceability']
        self.scaler = StandardScaler()
        self.optimal_weights = None
        self.optimal_intercept = None
        self.formula_performance = None
    
    def get_dataset(self):
        """Get complete dataset for optimization"""
        latest_prices = db.session.query(
            PriceHistory.crypto_id,
            db.func.max(PriceHistory.date).label('max_date')
        ).group_by(PriceHistory.crypto_id).subquery()
        
        query = db.session.query(
            Cryptocurrency, NameAnalysis, PriceHistory
        ).join(NameAnalysis, Cryptocurrency.id == NameAnalysis.crypto_id)\
         .join(PriceHistory, Cryptocurrency.id == PriceHistory.crypto_id)\
         .join(latest_prices, db.and_(
             PriceHistory.crypto_id == latest_prices.c.crypto_id,
             PriceHistory.date == latest_prices.c.max_date
         ))
        
        data = []
        for crypto, analysis, price in query.all():
            if price.price_1yr_change is None:
                continue
            
            data.append({
                'name': crypto.name,
                'syllables': analysis.syllable_count or 0,
                'length': analysis.character_length or 0,
                'memorability': analysis.memorability_score or 0,
                'uniqueness': analysis.uniqueness_score or 0,
                'phonetic': analysis.phonetic_score or 0,
                'pronounceability': analysis.pronounceability_score or 0,
                'performance': price.price_1yr_change
            })
        
        return pd.DataFrame(data)
    
    def optimize_formula(self, method='ridge'):
        """
        Find OPTIMAL FORMULA
        Assumes nominative determinism is TRUE, finds best weights
        """
        logger.info("="*70)
        logger.info("OPTIMIZING NOMINATIVE DETERMINISM FORMULA")
        logger.info("Assuming theory is TRUE - finding optimal weights")
        logger.info("="*70 + "\n")
        
        df = self.get_dataset()
        logger.info(f"Dataset: {len(df)} cryptocurrencies with complete data\n")
        
        if len(df) < 100:
            return {'error': 'Insufficient data for optimization'}
        
        # Prepare features and target
        X = df[self.feature_names].values
        y = df['performance'].values
        
        # Standardize features for optimization
        X_scaled = self.scaler.fit_transform(X)
        
        results = {}
        
        # Method 1: Ridge Regression (L2 regularization)
        logger.info("[1/4] Ridge Regression (prevents overfitting)...")
        ridge_model = Ridge(alpha=1.0)
        ridge_scores = cross_val_score(ridge_model, X_scaled, y, cv=5, scoring='r2')
        ridge_model.fit(X_scaled, y)
        
        results['ridge'] = {
            'weights': ridge_model.coef_.tolist(),
            'intercept': float(ridge_model.intercept_),
            'cv_r2_mean': float(ridge_scores.mean()),
            'cv_r2_std': float(ridge_scores.std())
        }
        logger.info(f"  Cross-validated R²: {ridge_scores.mean():.4f} ± {ridge_scores.std():.4f}")
        
        # Method 2: Lasso Regression (L1 - feature selection)
        logger.info("\n[2/4] Lasso Regression (automatic feature selection)...")
        lasso_model = Lasso(alpha=0.1, max_iter=10000)
        lasso_scores = cross_val_score(lasso_model, X_scaled, y, cv=5, scoring='r2')
        lasso_model.fit(X_scaled, y)
        
        results['lasso'] = {
            'weights': lasso_model.coef_.tolist(),
            'intercept': float(lasso_model.intercept_),
            'cv_r2_mean': float(lasso_scores.mean()),
            'cv_r2_std': float(lasso_scores.std()),
            'non_zero_features': int((lasso_model.coef_ != 0).sum())
        }
        logger.info(f"  Cross-validated R²: {lasso_scores.mean():.4f} ± {lasso_scores.std():.4f}")
        logger.info(f"  Non-zero features: {results['lasso']['non_zero_features']}/{len(self.feature_names)}")
        
        # Method 3: ElasticNet (best of both)
        logger.info("\n[3/4] ElasticNet (balanced approach)...")
        elastic_model = ElasticNet(alpha=0.1, l1_ratio=0.5, max_iter=10000)
        elastic_scores = cross_val_score(elastic_model, X_scaled, y, cv=5, scoring='r2')
        elastic_model.fit(X_scaled, y)
        
        results['elastic'] = {
            'weights': elastic_model.coef_.tolist(),
            'intercept': float(elastic_model.intercept_),
            'cv_r2_mean': float(elastic_scores.mean()),
            'cv_r2_std': float(elastic_scores.std())
        }
        logger.info(f"  Cross-validated R²: {elastic_scores.mean():.4f} ± {elastic_scores.std():.4f}")
        
        # Method 4: Evolutionary Optimization
        logger.info("\n[4/4] Evolutionary Optimization (global search)...")
        
        def objective(weights):
            """Objective: Minimize negative R² (maximize R²)"""
            model = Ridge(alpha=0.1)
            model.coef_ = weights
            model.intercept_ = 0
            scores = cross_val_score(model, X_scaled, y, cv=5, scoring='r2')
            return -scores.mean()  # Negative because we minimize
        
        # Bounds for weights
        bounds = [(-2, 2) for _ in range(len(self.feature_names))]
        
        evo_result = differential_evolution(
            objective,
            bounds,
            maxiter=100,
            popsize=15,
            seed=42
        )
        
        results['evolutionary'] = {
            'weights': evo_result.x.tolist(),
            'intercept': 0.0,
            'cv_r2_mean': float(-evo_result.fun),
            'optimization_success': bool(evo_result.success)
        }
        logger.info(f"  Optimized R²: {-evo_result.fun:.4f}")
        
        # Choose best method
        best_method = max(results.items(), key=lambda x: x[1]['cv_r2_mean'])
        logger.info(f"\n{'='*70}")
        logger.info(f"🏆 BEST METHOD: {best_method[0].upper()}")
        logger.info(f"   Cross-validated R²: {best_method[1]['cv_r2_mean']:.4f}")
        logger.info(f"{'='*70}\n")
        
        # Store optimal weights
        self.optimal_weights = np.array(best_method[1]['weights'])
        self.optimal_intercept = best_method[1]['intercept']
        
        # Build THE FORMULA
        formula = self.build_formula_string()
        
        return {
            'optimal_method': best_method[0],
            'formula': formula,
            'weights': {
                feature: round(float(weight), 4)
                for feature, weight in zip(self.feature_names, self.optimal_weights)
            },
            'intercept': round(float(self.optimal_intercept), 4),
            'performance': {
                'cv_r2_mean': round(float(best_method[1]['cv_r2_mean']), 4),
                'cv_r2_std': round(float(best_method[1].get('cv_r2_std', 0)), 4)
            },
            'sample_size': len(df),
            'all_methods': results
        }
    
    def build_formula_string(self):
        """Build human-readable formula string"""
        if self.optimal_weights is None:
            return "Formula not yet optimized"
        
        terms = []
        for feature, weight in zip(self.feature_names, self.optimal_weights):
            if abs(weight) < 0.001:
                continue  # Skip near-zero terms
            sign = "+" if weight > 0 else ""
            terms.append(f"{sign}{weight:.3f} × {feature}")
        
        formula = "Performance = " + " ".join(terms)
        if self.optimal_intercept != 0:
            sign = "+" if self.optimal_intercept > 0 else ""
            formula += f" {sign}{self.optimal_intercept:.2f}"
        
        return formula
    
    def predict_performance(self, name_features):
        """
        Predict performance using THE OPTIMAL FORMULA
        
        Args:
            name_features: dict with syllables, length, memorability, etc.
        
        Returns:
            Predicted performance score
        """
        if self.optimal_weights is None:
            raise ValueError("Formula not optimized yet - run optimize_formula() first")
        
        # Extract features in correct order
        X = np.array([[name_features.get(f, 0) for f in self.feature_names]])
        X_scaled = self.scaler.transform(X)
        
        # Apply THE FORMULA
        prediction = np.dot(X_scaled, self.optimal_weights) + self.optimal_intercept
        
        return float(prediction[0])
    
    def rank_features_by_importance(self):
        """Rank which name features matter most"""
        if self.optimal_weights is None:
            return []
        
        # Absolute weight magnitude = importance
        importance = [
            {
                'feature': feature,
                'weight': round(float(weight), 4),
                'abs_weight': round(float(abs(weight)), 4),
                'direction': 'positive' if weight > 0 else 'negative',
                'impact': 'high' if abs(weight) > 0.2 else ('medium' if abs(weight) > 0.1 else 'low')
            }
            for feature, weight in zip(self.feature_names, self.optimal_weights)
        ]
        
        # Sort by absolute weight (importance)
        importance.sort(key=lambda x: x['abs_weight'], reverse=True)
        
        return importance

