"""
Comparative Historical Analysis
Compare new coins against historical performance patterns
"""

import numpy as np
import pandas as pd
from core.models import db, Cryptocurrency, NameAnalysis, PriceHistory
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)


class ComparativeAnalyzer:
    """Compare coins against historical patterns"""
    
    def compare_to_historical(self, new_name, new_metrics):
        """
        Compare a new coin against historical database
        
        Args:
            new_name: Name of new cryptocurrency
            new_metrics: Dict with name metrics (syllables, memorability, etc.)
        
        Returns: Comparison results with predictions
        """
        try:
            # Get historical data
            historical_df = self._get_historical_dataset()
            
            if len(historical_df) < 10:
                return None
            
            # Find similar coins
            twins = self._find_similar_coins(new_metrics, historical_df)
            
            # Cohort analysis
            cohort_stats = self._cohort_analysis(new_metrics, historical_df)
            
            # Pattern matching
            pattern_match = self._match_to_patterns(new_metrics, historical_df)
            
            # Prediction based on historical twins
            prediction = self._predict_from_twins(twins)
            
            return {
                'new_coin': new_name,
                'metrics': new_metrics,
                'historical_twins': twins,
                'cohort_analysis': cohort_stats,
                'pattern_match': pattern_match,
                'prediction': prediction
            }
        
        except Exception as e:
            logger.error(f"Comparative analysis error: {e}")
            return None
    
    def _get_historical_dataset(self):
        """Get historical performance data"""
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
            data.append({
                'name': crypto.name,
                'rank': crypto.rank or 999,
                'memorability': analysis.memorability_score or 50,
                'uniqueness': analysis.uniqueness_score or 50,
                'phonetic': analysis.phonetic_score or 50,
                'syllables': analysis.syllable_count or 3,
                'length': analysis.character_length or 7,
                'vowel_ratio': analysis.vowel_ratio or 0.5,
                'name_type': analysis.name_type or 'other',
                'return_30d': price.price_30d_change or 0,
                'return_1yr': price.price_1yr_change or 0
            })
        
        return pd.DataFrame(data)
    
    def _find_similar_coins(self, new_metrics, historical_df, top_n=10):
        """Find most similar historical coins"""
        similarities = []
        
        for _, hist in historical_df.iterrows():
            # Calculate multi-dimensional similarity
            sim_score = 0
            
            # Syllable similarity (exact match bonus)
            if hist['syllables'] == new_metrics.get('syllables', 3):
                sim_score += 30
            else:
                sim_score += max(0, 30 - abs(hist['syllables'] - new_metrics.get('syllables', 3)) * 10)
            
            # Length similarity
            length_diff = abs(hist['length'] - new_metrics.get('length', 7))
            sim_score += max(0, 20 - length_diff * 3)
            
            # Memorability similarity
            mem_diff = abs(hist['memorability'] - new_metrics.get('memorability', 50))
            sim_score += max(0, 25 - mem_diff / 4)
            
            # Uniqueness similarity
            uniq_diff = abs(hist['uniqueness'] - new_metrics.get('uniqueness', 50))
            sim_score += max(0, 25 - uniq_diff / 4)
            
            similarities.append({
                'name': hist['name'],
                'similarity': round(sim_score, 1),
                'syllables': int(hist['syllables']),
                'length': int(hist['length']),
                'memorability': round(hist['memorability'], 1),
                'return_1yr': round(hist['return_1yr'], 2),
                'rank': int(hist['rank'])
            })
        
        # Sort by similarity
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        
        return similarities[:top_n]
    
    def _cohort_analysis(self, new_metrics, historical_df):
        """Analyze cohort of similar coins"""
        # Define cohort criteria
        syllables = new_metrics.get('syllables', 3)
        name_type = new_metrics.get('name_type', 'other')
        
        # Find cohort
        cohort = historical_df[
            (historical_df['syllables'] == syllables) |
            (historical_df['name_type'] == name_type)
        ]
        
        if len(cohort) < 5:
            cohort = historical_df  # Use full dataset if cohort too small
        
        return {
            'cohort_size': len(cohort),
            'avg_return': round(cohort['return_1yr'].mean(), 2),
            'median_return': round(cohort['return_1yr'].median(), 2),
            'std_return': round(cohort['return_1yr'].std(), 2),
            'min_return': round(cohort['return_1yr'].min(), 2),
            'max_return': round(cohort['return_1yr'].max(), 2),
            'top_performers': cohort.nlargest(3, 'return_1yr')[['name', 'return_1yr']].to_dict('records')
        }
    
    def _match_to_patterns(self, new_metrics, historical_df):
        """Match new coin to discovered patterns"""
        matches = []
        
        # Pattern 1: 2-3 syllables with high memorability
        if new_metrics.get('syllables') in [2, 3] and new_metrics.get('memorability', 0) > 70:
            pattern_coins = historical_df[
                (historical_df['syllables'].isin([2, 3])) &
                (historical_df['memorability'] > 70)
            ]
            if len(pattern_coins) >= 5:
                matches.append({
                    'pattern': '2-3 Syllable + High Memorability',
                    'match_strength': 'STRONG',
                    'historical_avg': round(pattern_coins['return_1yr'].mean(), 2),
                    'sample_size': len(pattern_coins)
                })
        
        # Pattern 2: Tech-oriented medium length
        if new_metrics.get('name_type') == 'tech' and 5 <= new_metrics.get('length', 0) <= 8:
            pattern_coins = historical_df[
                (historical_df['name_type'] == 'tech') &
                (historical_df['length'].between(5, 8))
            ]
            if len(pattern_coins) >= 5:
                matches.append({
                    'pattern': 'Tech Names (5-8 chars)',
                    'match_strength': 'STRONG',
                    'historical_avg': round(pattern_coins['return_1yr'].mean(), 2),
                    'sample_size': len(pattern_coins)
                })
        
        # Pattern 3: Portmanteau construction
        if new_metrics.get('name_type') == 'portmanteau':
            pattern_coins = historical_df[historical_df['name_type'] == 'portmanteau']
            if len(pattern_coins) >= 5:
                matches.append({
                    'pattern': 'Portmanteau Construction',
                    'match_strength': 'MEDIUM',
                    'historical_avg': round(pattern_coins['return_1yr'].mean(), 2),
                    'sample_size': len(pattern_coins)
                })
        
        return matches
    
    def _predict_from_twins(self, twins):
        """Generate prediction based on twin performance"""
        if not twins or len(twins) < 3:
            return {
                'expected_return': 0,
                'confidence': 'LOW',
                'reasoning': 'Insufficient similar historical examples'
            }
        
        # Use top 5 most similar
        top_twins = twins[:5]
        returns = [t['return_1yr'] for t in top_twins]
        
        avg_return = np.mean(returns)
        std_return = np.std(returns)
        
        # Weight by similarity
        weighted_returns = [t['return_1yr'] * (t['similarity'] / 100) for t in top_twins]
        weighted_avg = np.mean(weighted_returns) if weighted_returns else 0
        
        confidence = 'HIGH' if len(top_twins) >= 5 and std_return < 100 else 'MEDIUM'
        
        return {
            'expected_return': round(weighted_avg, 1),
            'return_range': {
                'low': round(avg_return - std_return, 1),
                'high': round(avg_return + std_return, 1)
            },
            'confidence': confidence,
            'reasoning': f'Based on {len(top_twins)} similar historical names averaging {avg_return:.1f}% return'
        }
    
    def analyze_new_coin(self, name, syllables, length, memorability, uniqueness, name_type):
        """Quick analysis of a potential new cryptocurrency"""
        new_metrics = {
            'syllables': syllables,
            'length': length,
            'memorability': memorability,
            'uniqueness': uniqueness,
            'name_type': name_type,
            'phonetic': (memorability + uniqueness) / 2,  # Estimate
            'pronounceability': memorability,  # Estimate
            'vowel_ratio': 0.4  # Default estimate
        }
        
        return self.compare_to_historical(name, new_metrics)

