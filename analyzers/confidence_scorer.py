"""
Confidence Scoring System
Real-time cryptocurrency name analysis with confidence scores and signals
"""

import numpy as np
from core.models import db, Cryptocurrency, NameAnalysis, PriceHistory
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ConfidenceScorer:
    """Generate confidence scores and trading signals based on name metrics"""
    
    def __init__(self):
        self.feature_weights = {
            'memorability_score': 0.25,
            'uniqueness_score': 0.20,
            'phonetic_score': 0.15,
            'syllable_count': 0.10,
            'character_length': 0.08,
            'name_type': 0.12,
            'pronounceability_score': 0.10
        }
    
    def score_cryptocurrency(self, crypto_id):
        """
        Calculate comprehensive confidence score for a cryptocurrency
        
        Returns: dict with score, signal, and breakdown
        """
        try:
            crypto = Cryptocurrency.query.get(crypto_id)
            analysis = NameAnalysis.query.filter_by(crypto_id=crypto_id).first()
            
            if not crypto or not analysis:
                return None
            
            # Calculate component scores
            scores = self._calculate_component_scores(analysis)
            
            # Weighted total score (0-100)
            total_score = sum(
                scores[key] * self.feature_weights.get(key, 0)
                for key in scores.keys()
            )
            
            # Generate signal
            signal = self._generate_signal(total_score)
            
            # Calculate confidence level
            confidence = self._calculate_confidence(total_score, analysis)
            
            return {
                'crypto_id': crypto_id,
                'name': crypto.name,
                'symbol': crypto.symbol,
                'score': round(total_score, 2),
                'signal': signal,
                'confidence': confidence,
                'breakdown': scores,
                'timestamp': datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error scoring crypto {crypto_id}: {e}")
            return None
    
    def _calculate_component_scores(self, analysis):
        """Calculate individual component scores"""
        scores = {}
        
        # Normalize memorability (0-100 scale)
        scores['memorability_score'] = min(100, analysis.memorability_score or 50)
        
        # Normalize uniqueness (0-100 scale)
        scores['uniqueness_score'] = min(100, analysis.uniqueness_score or 50)
        
        # Normalize phonetic score (0-100 scale)
        scores['phonetic_score'] = min(100, analysis.phonetic_score or 50)
        
        # Pronounceability score
        scores['pronounceability_score'] = min(100, analysis.pronounceability_score or 50)
        
        # Syllable count (optimal is 2-3 syllables)
        syllables = analysis.syllable_count or 3
        if syllables == 2 or syllables == 3:
            scores['syllable_count'] = 100
        elif syllables == 1 or syllables == 4:
            scores['syllable_count'] = 75
        else:
            scores['syllable_count'] = 50
        
        # Character length (optimal is 5-8 characters)
        length = analysis.character_length or 7
        if 5 <= length <= 8:
            scores['character_length'] = 100
        elif 4 <= length <= 10:
            scores['character_length'] = 75
        else:
            scores['character_length'] = 50
        
        # Name type scoring
        type_scores = {
            'tech': 85,
            'invented': 80,
            'portmanteau': 75,
            'animal': 70,
            'mythological': 70,
            'astronomical': 65,
            'financial': 60,
            'other': 50
        }
        scores['name_type'] = type_scores.get(analysis.name_type, 50)
        
        return scores
    
    def _generate_signal(self, score):
        """Generate BUY/HOLD/SELL signal based on score"""
        if score >= 75:
            return 'BUY'
        elif score >= 55:
            return 'HOLD'
        else:
            return 'SELL'
    
    def _calculate_confidence(self, score, analysis):
        """Calculate confidence level in the score"""
        # Higher uniqueness and memorability = higher confidence
        confidence_factors = [
            analysis.memorability_score or 50,
            analysis.uniqueness_score or 50,
            analysis.phonetic_score or 50
        ]
        
        avg_confidence = np.mean(confidence_factors)
        
        if avg_confidence >= 75:
            return 'HIGH'
        elif avg_confidence >= 55:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def score_all_cryptocurrencies(self):
        """Score all cryptocurrencies in database"""
        cryptos = Cryptocurrency.query.all()
        scores = []
        
        for crypto in cryptos:
            score_data = self.score_cryptocurrency(crypto.id)
            if score_data:
                scores.append(score_data)
        
        # Sort by score descending
        scores.sort(key=lambda x: x['score'], reverse=True)
        
        return scores
    
    def get_top_opportunities(self, min_score=75, limit=20):
        """Get top-scoring cryptocurrencies (high-confidence opportunities)"""
        all_scores = self.score_all_cryptocurrencies()
        
        # Filter by minimum score
        opportunities = [s for s in all_scores if s['score'] >= min_score]
        
        return opportunities[:limit]
    
    def get_signals_by_type(self):
        """Get count of signals by type"""
        all_scores = self.score_all_cryptocurrencies()
        
        signal_counts = {'BUY': 0, 'HOLD': 0, 'SELL': 0}
        for score in all_scores:
            signal_counts[score['signal']] += 1
        
        return signal_counts
    
    def track_accuracy(self, days=30):
        """Track prediction accuracy over time"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Get all cryptocurrencies analyzed before cutoff
            analyses = NameAnalysis.query.filter(
                NameAnalysis.analyzed_date < cutoff_date
            ).all()
            
            accurate_predictions = 0
            total_predictions = 0
            
            for analysis in analyses:
                # Get score from that time
                old_score = self.score_cryptocurrency(analysis.crypto_id)
                if not old_score:
                    continue
                
                # Get actual performance
                price_data = PriceHistory.query.filter_by(
                    crypto_id=analysis.crypto_id
                ).order_by(PriceHistory.date.desc()).first()
                
                if price_data and price_data.price_30d_change is not None:
                    actual_change = price_data.price_30d_change
                    predicted_signal = old_score['signal']
                    
                    # Check if prediction was accurate
                    if predicted_signal == 'BUY' and actual_change > 0:
                        accurate_predictions += 1
                    elif predicted_signal == 'SELL' and actual_change < 0:
                        accurate_predictions += 1
                    elif predicted_signal == 'HOLD' and -5 <= actual_change <= 5:
                        accurate_predictions += 1
                    
                    total_predictions += 1
            
            accuracy = (accurate_predictions / total_predictions * 100) if total_predictions > 0 else 0
            
            return {
                'accuracy_percent': round(accuracy, 2),
                'accurate_count': accurate_predictions,
                'total_count': total_predictions,
                'period_days': days
            }
        
        except Exception as e:
            logger.error(f"Error tracking accuracy: {e}")
            return {'accuracy_percent': 0, 'accurate_count': 0, 'total_count': 0}

