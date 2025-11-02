"""
Name Success Predictor
Predict cryptocurrency success based on name characteristics
"""

import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from core.models import db, Cryptocurrency, NameAnalysis, PriceHistory
from analyzers.advanced_analyzer import AdvancedAnalyzer
from analyzers.esoteric_analyzer import EsotericAnalyzer
from analyzers.name_analyzer import NameAnalyzer
import json


class NamePredictor:
    """Predict cryptocurrency success from name characteristics"""
    
    def __init__(self):
        self.name_analyzer = NameAnalyzer()
        self.advanced_analyzer = AdvancedAnalyzer()
        self.esoteric_analyzer = EsotericAnalyzer()
        
        self.models = {}
        self.scalers = {}
        self.feature_names = []
        self.is_trained = False
    
    def extract_features(self, name, launch_date=None):
        """
        Extract all available features from a name
        
        Returns:
            Dict of feature_name: value
        """
        features = {}
        
        # Basic analysis
        basic = self.name_analyzer.analyze_name(name, None)
        for key, value in basic.items():
            if isinstance(value, (int, float, bool)):
                features[f'basic_{key}'] = float(value) if isinstance(value, bool) else value
            elif value is None:
                features[f'basic_{key}'] = 0
        
        # Advanced analysis
        advanced = self.advanced_analyzer.analyze(name, None)
        for key, value in advanced.items():
            if isinstance(value, (int, float, bool)):
                features[f'adv_{key}'] = float(value) if isinstance(value, bool) else value
            elif isinstance(value, list):
                features[f'adv_{key}_count'] = len(value)
            elif value is None:
                features[f'adv_{key}'] = 0
        
        # Esoteric analysis
        esoteric = self.esoteric_analyzer.analyze(name, launch_date)
        for key, value in esoteric.items():
            if isinstance(value, (int, float, bool)):
                features[f'eso_{key}'] = float(value) if isinstance(value, bool) else value
            elif value is None:
                features[f'eso_{key}'] = 0
        
        return features
    
    def train(self, performance_metric='price_1yr_change'):
        """
        Train prediction models on existing data
        
        Args:
            performance_metric: Target metric to predict
        """
        print(f"Training predictor for {performance_metric}...")
        
        # Get all cryptocurrencies with complete data
        cryptos = db.session.query(Cryptocurrency, NameAnalysis, PriceHistory)\
            .join(NameAnalysis, Cryptocurrency.id == NameAnalysis.crypto_id)\
            .join(PriceHistory, Cryptocurrency.id == PriceHistory.crypto_id)\
            .filter(getattr(PriceHistory, performance_metric).isnot(None))\
            .all()
        
        if len(cryptos) < 10:
            raise ValueError("Insufficient training data (need at least 10 samples)")
        
        # Extract features and targets
        X_data = []
        y_data = []
        
        for crypto, analysis, price_hist in cryptos:
            try:
                # Extract all features
                features = self.extract_features(crypto.name, crypto.ath_date)
                
                # Get target value
                target = getattr(price_hist, performance_metric)
                
                # Clean features (replace inf/nan with 0)
                for key in features:
                    val = features[key]
                    if not isinstance(val, (int, float)):
                        features[key] = 0
                    elif np.isnan(val) or np.isinf(val):
                        features[key] = 0
                
                if target is not None and not np.isnan(target) and not np.isinf(target):
                    X_data.append(features)
                    y_data.append(target)
            except Exception as e:
                print(f"Error processing {crypto.name}: {e}")
                continue
        
        if len(X_data) < 10:
            raise ValueError("Insufficient valid training samples")
        
        # Convert to consistent feature vectors
        self.feature_names = sorted(X_data[0].keys())
        X = np.array([[sample.get(f, 0) for f in self.feature_names] for sample in X_data])
        y = np.array(y_data)
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Train multiple models
        models = {
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10),
            'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=42, max_depth=5),
            'ridge': Ridge(alpha=1.0)
        }
        
        for name, model in models.items():
            model.fit(X_scaled, y)
        
        # Store trained models
        self.models[performance_metric] = models
        self.scalers[performance_metric] = scaler
        self.is_trained = True
        
        # Calculate training scores
        scores = {}
        for name, model in models.items():
            scores[name] = model.score(X_scaled, y)
        
        print(f"Training complete. R² scores: {scores}")
        
        return scores
    
    def predict(self, name, performance_metric='price_1yr_change', launch_date=None):
        """
        Predict performance for a given name
        
        Args:
            name: Cryptocurrency name to predict
            performance_metric: Which metric to predict
            launch_date: Optional launch date for temporal analysis
            
        Returns:
            Dict with predictions and confidence intervals
        """
        if not self.is_trained or performance_metric not in self.models:
            raise ValueError(f"Model not trained for {performance_metric}. Call train() first.")
        
        # Extract features
        features = self.extract_features(name, launch_date)
        
        # Convert to feature vector
        X = np.array([[features.get(f, 0) for f in self.feature_names]])
        
        # Scale features
        X_scaled = self.scalers[performance_metric].transform(X)
        
        # Get predictions from all models
        predictions = {}
        for model_name, model in self.models[performance_metric].items():
            pred = model.predict(X_scaled)[0]
            predictions[model_name] = round(pred, 2)
        
        # Ensemble prediction (average)
        ensemble_pred = np.mean(list(predictions.values()))
        
        # Estimate confidence interval (std of model predictions)
        std = np.std(list(predictions.values()))
        confidence_interval = (
            round(ensemble_pred - 1.96 * std, 2),
            round(ensemble_pred + 1.96 * std, 2)
        )
        
        # Calculate percentile vs existing cryptos
        percentile = self._calculate_percentile(ensemble_pred, performance_metric)
        
        # Find similar names
        similar = self._find_similar_names(name, limit=5)
        
        return {
            'name': name,
            'metric': performance_metric,
            'prediction': round(ensemble_pred, 2),
            'confidence_interval': confidence_interval,
            'model_predictions': predictions,
            'percentile': percentile,
            'similar_names': similar,
            'risk_assessment': self._assess_risk(std),
            'recommendation': self._generate_recommendation(ensemble_pred, std)
        }
    
    def predict_all_timeframes(self, name, launch_date=None):
        """
        Predict across all timeframes
        
        Returns:
            Dict with predictions for 30d, 90d, 1yr, ATH
        """
        timeframes = ['price_30d_change', 'price_90d_change', 'price_1yr_change', 'price_ath_change']
        
        results = {}
        for timeframe in timeframes:
            try:
                if timeframe in self.models:
                    results[timeframe] = self.predict(name, timeframe, launch_date)
            except Exception as e:
                results[timeframe] = {'error': str(e)}
        
        return results
    
    def compare_names(self, names, performance_metric='price_1yr_change'):
        """
        Compare multiple name candidates
        
        Args:
            names: List of name strings
            performance_metric: Metric to compare on
            
        Returns:
            List of predictions sorted by expected performance
        """
        predictions = []
        
        for name in names:
            try:
                pred = self.predict(name, performance_metric)
                predictions.append(pred)
            except Exception as e:
                print(f"Error predicting {name}: {e}")
        
        # Sort by prediction (descending)
        predictions.sort(key=lambda x: x['prediction'], reverse=True)
        
        return predictions
    
    def _calculate_percentile(self, prediction, performance_metric):
        """Calculate percentile rank of prediction vs existing data"""
        # Get all actual values
        values = db.session.query(getattr(PriceHistory, performance_metric))\
            .filter(getattr(PriceHistory, performance_metric).isnot(None))\
            .all()
        
        values = [v[0] for v in values if v[0] is not None]
        
        if not values:
            return 50
        
        # Calculate percentile
        values_sorted = sorted(values)
        position = sum(1 for v in values_sorted if v < prediction)
        percentile = (position / len(values_sorted)) * 100
        
        return round(percentile, 1)
    
    def _find_similar_names(self, name, limit=5):
        """Find historically similar names"""
        # Get all cryptocurrencies
        all_cryptos = db.session.query(Cryptocurrency, NameAnalysis, PriceHistory)\
            .join(NameAnalysis, Cryptocurrency.id == NameAnalysis.crypto_id)\
            .join(PriceHistory, Cryptocurrency.id == PriceHistory.crypto_id)\
            .limit(100).all()
        
        # Extract features for target name
        target_features = self.extract_features(name)
        target_vector = np.array([target_features.get(f, 0) for f in self.feature_names])
        
        # Calculate similarity to each existing crypto
        similarities = []
        for crypto, analysis, price_hist in all_cryptos:
            try:
                crypto_features = self.extract_features(crypto.name)
                crypto_vector = np.array([crypto_features.get(f, 0) for f in self.feature_names])
                
                # Cosine similarity
                similarity = np.dot(target_vector, crypto_vector) / \
                           (np.linalg.norm(target_vector) * np.linalg.norm(crypto_vector) + 1e-10)
                
                similarities.append({
                    'name': crypto.name,
                    'symbol': crypto.symbol,
                    'similarity': round(similarity, 3),
                    'performance_1yr': price_hist.price_1yr_change
                })
            except:
                continue
        
        # Sort by similarity and return top N
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        return similarities[:limit]
    
    def _assess_risk(self, prediction_std):
        """Assess prediction risk based on model disagreement"""
        if prediction_std < 10:
            return 'low'
        elif prediction_std < 25:
            return 'moderate'
        else:
            return 'high'
    
    def _generate_recommendation(self, prediction, std):
        """Generate human-readable recommendation"""
        risk = self._assess_risk(std)
        
        if prediction > 100:
            quality = 'excellent'
        elif prediction > 50:
            quality = 'strong'
        elif prediction > 0:
            quality = 'moderate'
        elif prediction > -25:
            quality = 'weak'
        else:
            quality = 'poor'
        
        return f"{quality.capitalize()} predicted performance with {risk} confidence"
    
    def get_feature_importance(self, performance_metric='price_1yr_change'):
        """
        Get feature importance from random forest model
        
        Returns:
            Dict of feature: importance
        """
        if not self.is_trained or performance_metric not in self.models:
            raise ValueError("Model not trained")
        
        rf_model = self.models[performance_metric]['random_forest']
        
        importances = dict(zip(self.feature_names, rf_model.feature_importances_))
        
        # Sort by importance
        sorted_importance = dict(sorted(importances.items(), key=lambda x: x[1], reverse=True))
        
        return sorted_importance
    
    def explain_prediction(self, name, performance_metric='price_1yr_change'):
        """
        Explain why a prediction was made
        
        Returns:
            Dict with explanatory factors
        """
        # Get prediction
        prediction = self.predict(name, performance_metric)
        
        # Get feature importance
        importance = self.get_feature_importance(performance_metric)
        
        # Extract features for this name
        features = self.extract_features(name)
        
        # Get top contributing features
        top_features = []
        for feature, imp in list(importance.items())[:10]:
            value = features.get(feature, 0)
            top_features.append({
                'feature': feature.replace('_', ' ').title(),
                'value': round(value, 2),
                'importance': round(imp * 100, 2)
            })
        
        return {
            'prediction': prediction,
            'top_factors': top_features,
            'explanation': self._generate_explanation(name, features, importance)
        }
    
    def _generate_explanation(self, name, features, importance):
        """Generate natural language explanation"""
        # Get top 3 most important features
        top_3 = list(importance.items())[:3]
        
        explanations = []
        for feature, imp in top_3:
            value = features.get(feature, 0)
            
            if 'memorability' in feature.lower():
                if value > 70:
                    explanations.append(f"high memorability score ({value:.1f})")
                elif value < 40:
                    explanations.append(f"low memorability score ({value:.1f})")
            
            elif 'uniqueness' in feature.lower():
                if value > 70:
                    explanations.append(f"high uniqueness ({value:.1f})")
                elif value < 40:
                    explanations.append(f"common name pattern ({value:.1f})")
            
            elif 'syllable' in feature.lower():
                explanations.append(f"{int(value)}-syllable name")
        
        if explanations:
            return f"Driven by {', '.join(explanations)}"
        else:
            return "Based on comprehensive name analysis"

