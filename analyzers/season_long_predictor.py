"""
Season-Long Predictor
MVP, playoff success, and award futures predictions using name patterns
Leverages memorability (+0.406 in Football) and harshness correlations
"""

from typing import Dict, List, Optional
import numpy as np
import logging
from analyzers.sports_betting_analyzer import SportsBettingAnalyzer
from analyzers.betting_ev_calculator import BettingEVCalculator

logger = logging.getLogger(__name__)


class SeasonLongPredictor:
    """Predict season-long outcomes and awards using linguistic patterns"""
    
    def __init__(self):
        """Initialize with betting analyzer and EV calculator"""
        self.betting_analyzer = SportsBettingAnalyzer()
        self.ev_calculator = BettingEVCalculator()
        
        # Award type correlations
        self.award_correlations = self._define_award_correlations()
    
    def _define_award_correlations(self) -> Dict:
        """
        Define which linguistic features predict which awards
        Based on meta-analysis findings
        """
        return {
            'MVP': {
                'key_features': ['memorability', 'harshness', 'syllables'],
                'weights': [0.5, 0.3, 0.2],  # Memorability most important for MVP
                'rationale': 'MVP requires high visibility (memorability) and dominance (harshness)',
                'min_score_threshold': 65
            },
            'Offensive_Player_of_Year': {
                'key_features': ['harshness', 'memorability', 'syllables'],
                'weights': [0.4, 0.4, 0.2],
                'rationale': 'Offensive dominance correlates with harsh, memorable names',
                'min_score_threshold': 60
            },
            'Defensive_Player_of_Year': {
                'key_features': ['harshness', 'syllables', 'memorability'],
                'weights': [0.5, 0.3, 0.2],
                'rationale': 'Defensive dominance heavily correlates with harsh phonetics',
                'min_score_threshold': 62
            },
            'Rookie_of_Year': {
                'key_features': ['memorability', 'syllables', 'harshness'],
                'weights': [0.5, 0.3, 0.2],
                'rationale': 'Rookies need memorable names to stand out quickly',
                'min_score_threshold': 58
            },
            'Comeback_Player': {
                'key_features': ['memorability', 'harshness'],
                'weights': [0.6, 0.4],
                'rationale': 'Comeback narratives require memorable names for media attention',
                'min_score_threshold': 55
            },
            'Championship': {
                'key_features': ['harshness', 'memorability', 'length'],
                'weights': [0.4, 0.3, 0.3],
                'rationale': 'Championship leaders combine dominance and recognition',
                'min_score_threshold': 60
            },
            'Playoff_Success': {
                'key_features': ['harshness', 'memorability'],
                'weights': [0.5, 0.5],
                'rationale': 'Playoff performers need clutch associations (harshness) and recognition',
                'min_score_threshold': 58
            }
        }
    
    def predict_award_probability(self, player_name: str, sport: str, 
                                  award_type: str, linguistic_features: Dict,
                                  statistical_baseline: Optional[float] = None) -> Dict:
        """
        Predict probability of winning a specific award
        
        Args:
            player_name: Player name
            sport: Sport type
            award_type: Type of award (MVP, DPOY, etc.)
            linguistic_features: Name features
            statistical_baseline: Optional statistical win probability baseline
            
        Returns:
            Award probability prediction with reasoning
        """
        if award_type not in self.award_correlations:
            return {'error': f'Award type {award_type} not supported'}
        
        award_def = self.award_correlations[award_type]
        
        # Calculate overall player score
        score_result = self.betting_analyzer.calculate_player_score(linguistic_features, sport)
        overall_score = score_result['overall_score']
        confidence = score_result['confidence']
        
        # Calculate award-specific score
        award_score = 0
        for feature, weight in zip(award_def['key_features'], award_def['weights']):
            if feature in score_result['components']:
                feature_value = score_result['components'][feature]['value']
                # Normalize to 0-100 scale
                if feature == 'syllables':
                    normalized = max(0, min(100, (4 - feature_value) * 25))  # Shorter is better
                else:
                    normalized = feature_value
                
                award_score += normalized * weight
        
        # Adjust for sport-specific effects
        sport_weight = self.betting_analyzer.get_sport_weight(sport)
        award_score *= (sport_weight ** 0.5)  # Dampen sport effect for awards
        
        # Convert to probability
        # Base probability depends on field size (assume 50 candidates)
        base_prob = 0.02  # 1/50
        
        # Award score above threshold increases probability
        threshold = award_def['min_score_threshold']
        if award_score >= threshold:
            # Exponential increase above threshold
            score_excess = award_score - threshold
            prob_multiplier = 1 + (score_excess / 20)  # +1x per 20 points above threshold
            award_probability = base_prob * prob_multiplier
        else:
            # Below threshold, reduce probability
            score_deficit = threshold - award_score
            prob_multiplier = max(0.1, 1 - (score_deficit / 40))
            award_probability = base_prob * prob_multiplier
        
        # Incorporate statistical baseline if provided
        if statistical_baseline:
            # Blend linguistic prediction with statistical baseline
            # 60% stats, 40% name patterns (stats more reliable for awards)
            award_probability = (0.6 * statistical_baseline) + (0.4 * award_probability)
        
        # Cap probability
        award_probability = min(award_probability, 0.40)  # Max 40% probability
        
        # Confidence adjustment
        prediction_confidence = confidence * (award_score / 100)
        prediction_confidence = min(prediction_confidence, 80)  # Cap at 80%
        
        return {
            'player_name': player_name,
            'sport': sport,
            'award_type': award_type,
            'award_probability': round(award_probability, 4),
            'award_probability_pct': round(award_probability * 100, 2),
            'award_score': round(award_score, 2),
            'threshold': threshold,
            'above_threshold': award_score >= threshold,
            'confidence': round(prediction_confidence, 2),
            'rationale': award_def['rationale'],
            'key_features': {feat: score_result['components'][feat] 
                           for feat in award_def['key_features'] 
                           if feat in score_result['components']}
        }
    
    def analyze_futures_bet(self, player_name: str, sport: str, award_type: str,
                           linguistic_features: Dict, futures_odds: int,
                           statistical_baseline: Optional[float] = None) -> Dict:
        """
        Complete futures bet analysis for award
        
        Args:
            player_name: Player name
            sport: Sport type
            award_type: Award category
            linguistic_features: Name features
            futures_odds: Bookmaker's odds (American)
            statistical_baseline: Optional stats-based win probability
            
        Returns:
            Complete analysis with EV and recommendation
        """
        # Get award probability prediction
        prediction = self.predict_award_probability(
            player_name, sport, award_type, linguistic_features, statistical_baseline
        )
        
        if 'error' in prediction:
            return prediction
        
        # Calculate futures EV
        # Futures markets are less efficient (market_efficiency = 0.85)
        futures_ev = self.ev_calculator.calculate_futures_ev(
            win_probability=prediction['award_probability'],
            odds=futures_odds,
            market_efficiency=0.85
        )
        
        # Generate recommendation
        if futures_ev['adjusted_ev'] > 0.10:  # 10%+ edge
            bet_strength = 'STRONG BET'
        elif futures_ev['adjusted_ev'] > 0.05:  # 5%+ edge
            bet_strength = 'MODERATE BET'
        elif futures_ev['adjusted_ev'] > 0:
            bet_strength = 'SMALL BET'
        else:
            bet_strength = 'PASS'
        
        return {
            **prediction,
            'futures_odds': futures_odds,
            'ev_analysis': futures_ev,
            'bet_strength': bet_strength,
            'adjusted_ev': futures_ev['adjusted_ev'],
            'edge': futures_ev['edge']
        }
    
    def rank_award_candidates(self, candidates: List[Dict], sport: str, 
                             award_type: str) -> List[Dict]:
        """
        Rank multiple candidates for an award
        
        Args:
            candidates: List of player dicts with linguistic_features
            sport: Sport type
            award_type: Award category
            
        Returns:
            Ranked list of candidates by probability
        """
        predictions = []
        
        for candidate in candidates:
            prediction = self.predict_award_probability(
                player_name=candidate['name'],
                sport=sport,
                award_type=award_type,
                linguistic_features=candidate['linguistic_features'],
                statistical_baseline=candidate.get('statistical_baseline')
            )
            
            if 'error' not in prediction:
                predictions.append({
                    **candidate,
                    **prediction
                })
        
        # Sort by probability
        predictions.sort(key=lambda x: x['award_probability'], reverse=True)
        
        return predictions
    
    def scan_futures_market(self, futures_list: List[Dict]) -> List[Dict]:
        """
        Scan futures market for best betting opportunities
        
        Args:
            futures_list: List of futures with player info, odds, award type
            
        Returns:
            Ranked list by EV
        """
        analyzed_futures = []
        
        for future in futures_list:
            analysis = self.analyze_futures_bet(
                player_name=future['player_name'],
                sport=future['sport'],
                award_type=future['award_type'],
                linguistic_features=future['linguistic_features'],
                futures_odds=future['odds'],
                statistical_baseline=future.get('statistical_baseline')
            )
            
            if 'error' not in analysis:
                analyzed_futures.append(analysis)
        
        # Rank by adjusted EV
        analyzed_futures.sort(key=lambda x: x['adjusted_ev'], reverse=True)
        
        return analyzed_futures
    
    def predict_playoff_success(self, player_name: str, sport: str,
                               linguistic_features: Dict) -> Dict:
        """
        Predict playoff success probability
        
        Args:
            player_name: Player name
            sport: Sport type
            linguistic_features: Name features
            
        Returns:
            Playoff success prediction
        """
        return self.predict_award_probability(
            player_name, sport, 'Playoff_Success', 
            linguistic_features
        )
    
    def get_supported_awards(self, sport: str) -> List[Dict]:
        """Get supported award types"""
        awards = []
        for award_type, award_def in self.award_correlations.items():
            awards.append({
                'award_type': award_type,
                'rationale': award_def['rationale'],
                'key_features': award_def['key_features'],
                'threshold': award_def['min_score_threshold']
            })
        
        return awards


if __name__ == "__main__":
    # Test season-long predictor
    logging.basicConfig(level=logging.INFO)
    
    predictor = SeasonLongPredictor()
    
    print("\n=== SUPPORTED AWARDS ===")
    awards = predictor.get_supported_awards('football')
    for award in awards:
        print(f"\n{award['award_type']}:")
        print(f"  Rationale: {award['rationale']}")
        print(f"  Key Features: {', '.join(award['key_features'])}")
    
    print("\n=== MVP PREDICTION EXAMPLE ===")
    # Example: NFL MVP candidate
    mvp_analysis = predictor.analyze_futures_bet(
        player_name="Josh Allen",
        sport="football",
        award_type="MVP",
        linguistic_features={
            'syllables': 2,       # Short, punchy
            'harshness': 72,      # High harshness
            'memorability': 68,   # Good memorability
            'length': 9
        },
        futures_odds=800,  # +800 odds (9.0 decimal)
        statistical_baseline=0.08  # 8% baseline from stats
    )
    
    print(f"Player: {mvp_analysis['player_name']}")
    print(f"Award: {mvp_analysis['award_type']}")
    print(f"Predicted Probability: {mvp_analysis['award_probability_pct']}%")
    print(f"Market Odds: +{mvp_analysis['futures_odds']}")
    print(f"Adjusted EV: {mvp_analysis['adjusted_ev']:.4f} ({mvp_analysis['adjusted_ev']*100:.2f}%)")
    print(f"Recommendation: {mvp_analysis['bet_strength']}")
    
    print("\n=== RANKING CANDIDATES ===")
    candidates = [
        {
            'name': 'Patrick Mahomes',
            'linguistic_features': {'syllables': 3, 'harshness': 65, 'memorability': 90, 'length': 15},
            'statistical_baseline': 0.12
        },
        {
            'name': 'Josh Allen',
            'linguistic_features': {'syllables': 2, 'harshness': 72, 'memorability': 68, 'length': 9},
            'statistical_baseline': 0.08
        },
        {
            'name': 'Joe Burrow',
            'linguistic_features': {'syllables': 3, 'harshness': 60, 'memorability': 70, 'length': 9},
            'statistical_baseline': 0.07
        }
    ]
    
    ranked = predictor.rank_award_candidates(candidates, 'football', 'MVP')
    print("\nMVP Rankings:")
    for i, candidate in enumerate(ranked, 1):
        print(f"{i}. {candidate['name']}: {candidate['award_probability_pct']}% "
              f"(Score: {candidate['award_score']:.1f})")

