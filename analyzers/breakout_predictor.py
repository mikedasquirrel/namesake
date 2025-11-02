"""
Breakout Prediction Model
Predicts which cryptocurrencies will achieve 100%+ gains based on name patterns
"""

import numpy as np
import pandas as pd
from core.models import db, Cryptocurrency, NameAnalysis, PriceHistory
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score
import logging

logger = logging.getLogger(__name__)


class BreakoutPredictor:
    """Predict breakout potential based on name characteristics"""
    
    def __init__(self):
        self.model = None
        self.feature_names = []
        self.is_trained = False
        self.accuracy = 0
        self.feature_importance = {}
    
    def train_model(self):
        """Train breakout prediction model"""
        try:
            df = self._get_training_data()
            
            if len(df) < 30:
                return {'success': False, 'error': 'Insufficient data for training'}
            
            # Prepare features and target
            X, y = self._prepare_training_data(df)
            
            if len(y.unique()) < 2:
                return {'success': False, 'error': 'Need both breakout and non-breakout examples'}
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Train model
            self.model = GradientBoostingClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
            
            self.model.fit(X_train, y_train)
            
            # Evaluate
            y_pred = self.model.predict(X_test)
            self.accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, zero_division=0)
            recall = recall_score(y_test, y_pred, zero_division=0)
            
            # Cross-validation
            cv_scores = cross_val_score(self.model, X, y, cv=5)
            
            # Feature importance
            self.feature_importance = dict(zip(self.feature_names, self.model.feature_importances_))
            
            self.is_trained = True
            
            return {
                'success': True,
                'accuracy': round(self.accuracy, 3),
                'precision': round(precision, 3),
                'recall': round(recall, 3),
                'cv_mean': round(cv_scores.mean(), 3),
                'cv_std': round(cv_scores.std(), 3),
                'training_samples': len(df),
                'breakout_count': int(y.sum()),
                'feature_importance': {k: round(v, 3) for k, v in sorted(self.feature_importance.items(), key=lambda x: x[1], reverse=True)}
            }
        
        except Exception as e:
            logger.error(f"Training error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _get_training_data(self):
        """Get dataset for training"""
        latest_prices_subq = db.session.query(
            PriceHistory.crypto_id,
            db.func.max(PriceHistory.date).label('max_date')
        ).group_by(PriceHistory.crypto_id).subquery()
        
        query = db.session.query(
            Cryptocurrency,
            NameAnalysis,
            PriceHistory
        ).join(NameAnalysis, Cryptocurrency.id == NameAnalysis.crypto_id)\
         .join(PriceHistory, Cryptocurrency.id == PriceHistory.crypto_id)\
         .join(latest_prices_subq, db.and_(
             PriceHistory.crypto_id == latest_prices_subq.c.crypto_id,
             PriceHistory.date == latest_prices_subq.c.max_date
         ))
        
        data = []
        for crypto, analysis, price in query.all():
            # USE ONLY REAL 1-YEAR DATA - NO EXTRAPOLATION!
            if price.price_1yr_change is None:
                continue  # Skip if no verified 1-year data
            
            data.append({
                'crypto_id': crypto.id,
                'name': crypto.name,
                'rank': crypto.rank or 9999,
                'memorability': analysis.memorability_score or 50,
                'uniqueness': analysis.uniqueness_score or 50,
                'phonetic': analysis.phonetic_score or 50,
                'pronounceability': analysis.pronounceability_score or 50,
                'syllables': analysis.syllable_count or 3,
                'length': analysis.character_length or 7,
                'vowel_ratio': analysis.vowel_ratio or 0.5,
                'is_tech': 1 if analysis.name_type == 'tech' else 0,
                'is_portmanteau': 1 if analysis.name_type == 'portmanteau' else 0,
                'is_invented': 1 if analysis.name_type == 'invented' else 0,
                'return_1yr': price.price_1yr_change,  # REAL 1-year data only
                'is_breakout': 1 if price.price_1yr_change > 100 else 0
            })
        
        return pd.DataFrame(data)
    
    def _prepare_training_data(self, df):
        """Prepare features and target"""
        self.feature_names = [
            'memorability', 'uniqueness', 'phonetic', 'pronounceability',
            'syllables', 'length', 'vowel_ratio',
            'is_tech', 'is_portmanteau', 'is_invented'
        ]
        
        X = df[self.feature_names]
        y = df['is_breakout']
        
        return X, y
    
    def predict_breakout_probability(self, crypto_id):
        """Predict breakout probability for a cryptocurrency"""
        try:
            if not self.is_trained:
                train_result = self.train_model()
                if not train_result['success']:
                    return None
            
            # Get crypto data
            analysis = NameAnalysis.query.filter_by(crypto_id=crypto_id).first()
            crypto = Cryptocurrency.query.get(crypto_id)
            
            if not analysis or not crypto:
                return None
            
            # Prepare features
            features = pd.DataFrame([{
                'memorability': analysis.memorability_score or 50,
                'uniqueness': analysis.uniqueness_score or 50,
                'phonetic': analysis.phonetic_score or 50,
                'pronounceability': analysis.pronounceability_score or 50,
                'syllables': analysis.syllable_count or 3,
                'length': analysis.character_length or 7,
                'vowel_ratio': analysis.vowel_ratio or 0.5,
                'is_tech': 1 if analysis.name_type == 'tech' else 0,
                'is_portmanteau': 1 if analysis.name_type == 'portmanteau' else 0,
                'is_invented': 1 if analysis.name_type == 'invented' else 0
            }])
            
            # Predict probability
            prob = self.model.predict_proba(features)[0][1] * 100  # Probability of breakout class
            
            # Find historical twins
            twins = self.find_historical_twins(crypto.name)
            
            # Get price data
            price_data = PriceHistory.query.filter_by(crypto_id=crypto_id).first()
            current_return = price_data.price_1yr_change if (price_data and price_data.price_1yr_change is not None) else 0
            
            return {
                'crypto_id': crypto_id,
                'name': crypto.name,
                'symbol': crypto.symbol,
                'rank': crypto.rank or 999,
                'breakout_probability': round(prob, 1),
                'current_return_1yr': round(float(current_return), 2),
                'historical_twins': twins[:3],
                'prediction': 'HIGH POTENTIAL' if prob > 70 else ('MODERATE POTENTIAL' if prob > 50 else 'LOW POTENTIAL'),
                'expected_return_range': self._estimate_return_range(prob, twins)
            }
        
        except Exception as e:
            logger.error(f"Prediction error for {crypto_id}: {e}")
            return None
    
    def find_historical_twins(self, target_name):
        """Find cryptocurrencies with similar name characteristics"""
        try:
            # Get target analysis
            target_crypto = Cryptocurrency.query.filter_by(name=target_name).first()
            if not target_crypto:
                return []
            
            target_analysis = NameAnalysis.query.filter_by(crypto_id=target_crypto.id).first()
            if not target_analysis:
                return []
            
            # Get all cryptos
            df = self._get_training_data()
            
            # Calculate similarity score
            twins = []
            for _, row in df.iterrows():
                if row['name'] == target_name:
                    continue
                
                # Weighted similarity
                similarity = (
                    (1 - abs(row['syllables'] - (target_analysis.syllable_count or 3)) / 5) * 0.3 +
                    (1 - abs(row['length'] - (target_analysis.character_length or 7)) / 10) * 0.2 +
                    (1 - abs(row['memorability'] - (target_analysis.memorability_score or 50)) / 100) * 0.25 +
                    (1 - abs(row['uniqueness'] - (target_analysis.uniqueness_score or 50)) / 100) * 0.25
                )
                
                twins.append({
                    'name': row['name'],
                    'similarity': round(similarity * 100, 1),
                    'return_1yr': round(row['return_1yr'], 2),
                    'syllables': int(row['syllables']),
                    'length': int(row['length'])
                })
            
            # Sort by similarity
            twins.sort(key=lambda x: x['similarity'], reverse=True)
            
            return twins[:10]
        
        except Exception as e:
            logger.error(f"Twin finding error: {e}")
            return []
    
    def _estimate_return_range(self, probability, twins):
        """Estimate expected return range based on probability and twins"""
        if not twins:
            # Base estimate on probability
            if probability > 70:
                return {'low': 150, 'high': 500}
            elif probability > 50:
                return {'low': 50, 'high': 200}
            else:
                return {'low': -20, 'high': 50}
        
        # Use twin performance
        twin_returns = [t['return_1yr'] for t in twins[:5]]
        avg_twin_return = np.mean(twin_returns)
        std_twin_return = np.std(twin_returns)
        
        # Adjust by probability
        factor = probability / 100
        
        return {
            'low': round(avg_twin_return - std_twin_return, 0),
            'high': round(avg_twin_return + std_twin_return, 0),
            'expected': round(avg_twin_return * factor, 0)
        }
    
    def get_top_breakout_candidates(self, min_rank=50, limit=20):
        """Get top breakout candidates from lower-ranked coins"""
        try:
            if not self.is_trained:
                self.train_model()
            
            # Get all cryptocurrencies ranked below threshold
            candidates = Cryptocurrency.query.filter(Cryptocurrency.rank >= min_rank).all()
            
            predictions = []
            for crypto in candidates:
                pred = self.predict_breakout_probability(crypto.id)
                if pred and pred['breakout_probability'] > 50:
                    predictions.append(pred)
            
            # Sort by probability
            predictions.sort(key=lambda x: x['breakout_probability'], reverse=True)
            
            return predictions[:limit]
        
        except Exception as e:
            logger.error(f"Error getting breakout candidates: {e}")
            return []

