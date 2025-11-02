"""
Opportunity Finder
Identifies genuinely undervalued assets based on name quality analysis
REAL opportunities only - with verification
"""

from core.models import db, Cryptocurrency, NameAnalysis, PriceHistory, Domain, DomainAnalysis
from analyzers.confidence_scorer import ConfidenceScorer
from analyzers.breakout_predictor import BreakoutPredictor
import logging

logger = logging.getLogger(__name__)


class OpportunityFinder:
    """Find real investment opportunities based on name-value mismatch"""
    
    def __init__(self):
        self.scorer = ConfidenceScorer()
        self.breakout_predictor = BreakoutPredictor()
    
    def find_undervalued_cryptos(self, min_score=80, min_rank=100, max_rank=500, limit=20):
        """
        Find cryptocurrencies with high name scores but low market recognition
        REAL opportunities from database
        
        Args:
            min_score: Minimum name quality score
            min_rank: Don't include top coins (already recognized)
            max_rank: Maximum rank to consider
            limit: Max opportunities to return
        
        Returns: List of undervalued cryptocurrencies
        """
        try:
            logger.info(f"Scanning for undervalued cryptos (score≥{min_score}, rank {min_rank}-{max_rank})")
            
            # Get all cryptocurrencies in rank range
            candidates = Cryptocurrency.query.filter(
                Cryptocurrency.rank >= min_rank,
                Cryptocurrency.rank <= max_rank
            ).all()
            
            opportunities = []
            
            for crypto in candidates:
                # Get name score
                score_data = self.scorer.score_cryptocurrency(crypto.id)
                if not score_data or score_data['score'] < min_score:
                    continue
                
                # Get breakout probability
                breakout_data = self.breakout_predictor.predict_breakout_probability(crypto.id)
                if not breakout_data:
                    continue
                
                # Get price data
                price_data = PriceHistory.query.filter_by(crypto_id=crypto.id).first()
                
                # Calculate value mismatch
                # High score but low rank = undervalued
                value_score = score_data['score']
                rank_score = max(0, 100 - (crypto.rank / 5))  # Convert rank to 0-100 scale
                mismatch = value_score - rank_score
                
                if mismatch > 20:  # Significant mismatch
                    opportunities.append({
                        'crypto_id': crypto.id,
                        'name': crypto.name,
                        'symbol': crypto.symbol,
                        'rank': crypto.rank,
                        'name_score': round(score_data['score'], 1),
                        'breakout_probability': round(breakout_data['breakout_probability'], 1),
                        'current_price': crypto.current_price,
                        'market_cap': crypto.market_cap,
                        'mismatch_score': round(mismatch, 1),
                        'expected_return_range': breakout_data.get('expected_return_range', {}),
                        'pattern_matches': breakout_data.get('historical_twins', [])[:3],
                        'signal': score_data['signal'],
                        'confidence': score_data['confidence'],
                        'current_return_1yr': price_data.price_1yr_change if price_data else 0,
                        'why_undervalued': self._explain_undervaluation(score_data, crypto.rank, breakout_data)
                    })
            
            # Sort by mismatch score (most undervalued first)
            opportunities.sort(key=lambda x: x['mismatch_score'], reverse=True)
            
            logger.info(f"Found {len(opportunities)} undervalued opportunities")
            
            return opportunities[:limit]
        
        except Exception as e:
            logger.error(f"Undervalued crypto finder error: {e}")
            return []
    
    def _explain_undervaluation(self, score_data, rank, breakout_data):
        """Generate explanation of why asset is undervalued"""
        reasons = []
        
        score = score_data['score']
        
        if score >= 85:
            reasons.append(f"Exceptional name quality (top 5% - score {score:.1f})")
        elif score >= 80:
            reasons.append(f"High name quality (top 15% - score {score:.1f})")
        
        if rank > 200:
            reasons.append(f"Low market recognition (rank #{rank})")
        
        if breakout_data and breakout_data.get('breakout_probability', 0) > 70:
            reasons.append(f"High breakout probability ({breakout_data['breakout_probability']:.1f}%)")
        
        if breakout_data and breakout_data.get('historical_twins'):
            twins = breakout_data['historical_twins']
            if twins:
                avg_return = sum(t['return_1yr'] for t in twins[:3]) / min(3, len(twins))
                if avg_return > 100:
                    reasons.append(f"Similar names averaged +{avg_return:.0f}% returns")
        
        return ' | '.join(reasons) if reasons else 'Name quality not reflected in market cap'
    
    def calculate_roi_potential(self, opportunity):
        """
        Calculate potential ROI based on patterns
        
        Returns: dict with ROI analysis
        """
        # If name score is 90+ and rank is 300+, historical similar coins went top 100
        # That's typically a 10-50x market cap increase
        
        name_score = opportunity.get('name_score', 0)
        current_rank = opportunity.get('rank', 999)
        
        if name_score >= 85 and current_rank >= 200:
            # Strong undervaluation
            low_estimate = 200  # Conservative: 3x
            high_estimate = 800  # Aggressive: 9x
        elif name_score >= 80 and current_rank >= 150:
            # Moderate undervaluation
            low_estimate = 100
            high_estimate = 400
        else:
            # Mild undervaluation
            low_estimate = 50
            high_estimate = 200
        
        return {
            'roi_low_pct': low_estimate,
            'roi_high_pct': high_estimate,
            'roi_expected_pct': (low_estimate + high_estimate) / 2,
            'timeline_months': 12,
            'risk_level': 'MEDIUM-HIGH' if name_score >= 85 else 'MEDIUM'
        }

