"""
Player Prop Analyzer
Sport-specific prop bet predictions using linguistic name patterns
NFL: Passing yards, rushing yards, receptions
NBA: Points, rebounds, assists  
MLB: Hits, home runs, strikeouts
"""

from typing import Dict, List, Optional
import logging
from analyzers.sports_betting_analyzer import SportsBettingAnalyzer
from analyzers.betting_ev_calculator import BettingEVCalculator

logger = logging.getLogger(__name__)


class PlayerPropAnalyzer:
    """Analyze player props using name pattern correlations"""
    
    def __init__(self):
        """Initialize with betting analyzer and EV calculator"""
        self.betting_analyzer = SportsBettingAnalyzer()
        self.ev_calculator = BettingEVCalculator()
        
        # Sport-specific prop mappings
        # Maps linguistic features to performance metrics
        self.prop_correlations = self._define_prop_correlations()
    
    def _define_prop_correlations(self) -> Dict:
        """
        Define which linguistic features predict which props per sport
        Based on meta-analysis results
        """
        return {
            'football': {
                'passing_yards': {
                    'primary_features': ['memorability', 'length'],
                    'direction': [1, -1],  # Higher memorability, shorter names
                    'weight': 1.0,
                    'rationale': 'Quarterbacks need memorable, concise names for rapid playcalling'
                },
                'rushing_yards': {
                    'primary_features': ['harshness', 'syllables'],
                    'direction': [1, -1],  # Harsher, shorter names
                    'weight': 2.0,  # Football shows strongest effects
                    'rationale': 'RBs with harsh, short names correlate with power running (r=0.427 harshness)'
                },
                'receptions': {
                    'primary_features': ['memorability', 'syllables'],
                    'direction': [1, -1],  # Memorable, short names
                    'weight': 1.5,
                    'rationale': 'WRs/TEs need memorable names for frequent targeting'
                },
                'touchdowns': {
                    'primary_features': ['harshness', 'memorability'],
                    'direction': [1, 1],  # Harsh and memorable
                    'weight': 2.0,
                    'rationale': 'Scoring combines power (harshness) and recognition (memorability)'
                }
            },
            'basketball': {
                'points': {
                    'primary_features': ['harshness', 'memorability'],
                    'direction': [1, 1],  # Harsher, memorable names
                    'weight': 1.0,
                    'rationale': 'Scoring correlates with harsh phonetics (r=0.196) and fan recognition'
                },
                'rebounds': {
                    'primary_features': ['harshness', 'syllables'],
                    'direction': [1, -1],  # Harsh, short names
                    'weight': 1.0,
                    'rationale': 'Physical play requires harsh-sounding names'
                },
                'assists': {
                    'primary_features': ['memorability', 'length'],
                    'direction': [1, -1],  # Memorable, shorter names
                    'weight': 0.8,
                    'rationale': 'Playmakers need memorable names for team communication'
                },
                'three_pointers': {
                    'primary_features': ['memorability', 'harshness'],
                    'direction': [1, -1],  # Memorable, less harsh (precision)
                    'weight': 0.7,
                    'rationale': 'Precision shooting inversely correlates with harshness'
                }
            },
            'baseball': {
                'hits': {
                    'primary_features': ['memorability', 'syllables'],
                    'direction': [1, -1],  # Memorable, short names
                    'weight': 1.1,
                    'rationale': 'Contact hitters benefit from memorable names for fan engagement'
                },
                'home_runs': {
                    'primary_features': ['harshness', 'syllables'],
                    'direction': [1, -1],  # Harsh, short names
                    'weight': 1.2,
                    'rationale': 'Power correlates with harsh phonetics (r=0.221)'
                },
                'strikeouts_pitcher': {
                    'primary_features': ['harshness', 'memorability'],
                    'direction': [1, 1],  # Harsh and memorable
                    'weight': 1.1,
                    'rationale': 'Dominant pitchers have harsh, memorable names'
                },
                'rbis': {
                    'primary_features': ['harshness', 'memorability'],
                    'direction': [1, 1],  # Harsh and memorable
                    'weight': 1.1,
                    'rationale': 'Clutch performance requires both power and recognition'
                }
            }
        }
    
    def predict_prop_value(self, player_name: str, sport: str, prop_type: str,
                          linguistic_features: Dict, baseline_average: float) -> Dict:
        """
        Predict player prop value using name patterns
        
        Args:
            player_name: Player name
            sport: 'football', 'basketball', or 'baseball'
            prop_type: Type of prop (e.g., 'passing_yards', 'points', 'hits')
            linguistic_features: Dict with syllables, harshness, memorability, length
            baseline_average: Player's season average for this prop
            
        Returns:
            Dict with predicted value and confidence
        """
        if sport not in self.prop_correlations:
            return {'error': f'Sport {sport} not supported'}
        
        if prop_type not in self.prop_correlations[sport]:
            return {'error': f'Prop type {prop_type} not supported for {sport}'}
        
        # Get prop correlation definition
        prop_def = self.prop_correlations[sport][prop_type]
        
        # Calculate player betting score
        score_result = self.betting_analyzer.calculate_player_score(linguistic_features, sport)
        overall_score = score_result['overall_score']
        confidence = score_result['confidence']
        
        # Extract relevant feature contributions
        features = prop_def['primary_features']
        directions = prop_def['direction']
        weight = prop_def['weight']
        
        # Calculate prop-specific adjustment
        adjustment_score = 0
        for feature, direction in zip(features, directions):
            if feature in score_result['components']:
                contribution = score_result['components'][feature]['contribution']
                adjustment_score += contribution * direction
        
        # Apply sport and prop-specific weighting
        adjustment_score *= weight
        
        # Convert score adjustment to percentage change
        # Score of 70 = +10% to baseline, 50 = no change, 30 = -10%
        percentage_adjustment = (overall_score - 50) / 200  # ±0.25 range
        
        # Apply to baseline
        predicted_value = baseline_average * (1 + percentage_adjustment)
        
        # Confidence adjustment based on prop type relevance
        prop_confidence = confidence * (weight / 2.0)  # Scale by prop weight
        prop_confidence = min(prop_confidence, 90)  # Cap at 90%
        
        return {
            'player_name': player_name,
            'sport': sport,
            'prop_type': prop_type,
            'baseline_average': round(baseline_average, 2),
            'predicted_value': round(predicted_value, 2),
            'adjustment_percentage': round(percentage_adjustment * 100, 2),
            'confidence': round(prop_confidence, 2),
            'overall_score': round(overall_score, 2),
            'rationale': prop_def['rationale'],
            'key_features': {feat: score_result['components'][feat] 
                           for feat in features if feat in score_result['components']}
        }
    
    def analyze_prop_bet(self, player_name: str, sport: str, prop_type: str,
                        linguistic_features: Dict, baseline_average: float,
                        market_line: float, over_odds: int = -110, 
                        under_odds: int = -110) -> Dict:
        """
        Full prop bet analysis with EV calculation
        
        Args:
            player_name: Player name
            sport: Sport type
            prop_type: Prop category
            linguistic_features: Name features
            baseline_average: Player's average
            market_line: Bookmaker's line
            over_odds: Odds for over
            under_odds: Odds for under
            
        Returns:
            Complete analysis with prediction and EV
        """
        # Get prediction
        prediction = self.predict_prop_value(
            player_name, sport, prop_type, linguistic_features, baseline_average
        )
        
        if 'error' in prediction:
            return prediction
        
        # Calculate EV
        ev_result = self.ev_calculator.calculate_prop_ev(
            predicted_value=prediction['predicted_value'],
            market_line=market_line,
            over_odds=over_odds,
            under_odds=under_odds,
            confidence=prediction['confidence']
        )
        
        # Combine results
        return {
            **prediction,
            'market_line': market_line,
            'over_odds': over_odds,
            'under_odds': under_odds,
            'ev_analysis': ev_result,
            'recommended_bet': ev_result['recommendation'],
            'best_ev': ev_result['best_ev_percentage']
        }
    
    def scan_props(self, props_list: List[Dict]) -> List[Dict]:
        """
        Scan multiple props and rank by betting value
        
        Args:
            props_list: List of prop dicts with player info and market data
            
        Returns:
            Ranked list of best betting opportunities
        """
        analyzed_props = []
        
        for prop in props_list:
            analysis = self.analyze_prop_bet(
                player_name=prop['player_name'],
                sport=prop['sport'],
                prop_type=prop['prop_type'],
                linguistic_features=prop['linguistic_features'],
                baseline_average=prop['baseline_average'],
                market_line=prop['market_line'],
                over_odds=prop.get('over_odds', -110),
                under_odds=prop.get('under_odds', -110)
            )
            
            if 'error' not in analysis:
                analyzed_props.append(analysis)
        
        # Rank by EV
        analyzed_props.sort(key=lambda x: x['best_ev'], reverse=True)
        
        return analyzed_props
    
    def get_supported_props(self, sport: str) -> List[Dict]:
        """Get list of supported prop types for a sport"""
        if sport not in self.prop_correlations:
            return []
        
        props = []
        for prop_type, prop_def in self.prop_correlations[sport].items():
            props.append({
                'prop_type': prop_type,
                'weight': prop_def['weight'],
                'rationale': prop_def['rationale'],
                'key_features': prop_def['primary_features']
            })
        
        return props


if __name__ == "__main__":
    # Test prop analyzer
    logging.basicConfig(level=logging.INFO)
    
    analyzer = PlayerPropAnalyzer()
    
    print("\n=== SUPPORTED PROPS ===")
    for sport in ['football', 'basketball', 'baseball']:
        print(f"\n{sport.upper()}:")
        props = analyzer.get_supported_props(sport)
        for prop in props:
            print(f"  - {prop['prop_type']}: {prop['rationale']}")
    
    print("\n=== EXAMPLE PROP ANALYSIS ===")
    # Example: NFL rushing yards prop
    analysis = analyzer.analyze_prop_bet(
        player_name="Nick Chubb",
        sport="football",
        prop_type="rushing_yards",
        linguistic_features={
            'syllables': 2,      # Short name
            'harshness': 68,     # High harshness (Chubb has plosives)
            'memorability': 72,  # Memorable
            'length': 9          # Moderate length
        },
        baseline_average=85.5,   # Season average
        market_line=82.5,        # Bookmaker line
        over_odds=-110,
        under_odds=-110
    )
    
    print(f"\nPlayer: {analysis['player_name']}")
    print(f"Prop: {analysis['prop_type']}")
    print(f"Baseline Average: {analysis['baseline_average']}")
    print(f"Predicted Value: {analysis['predicted_value']}")
    print(f"Market Line: {analysis['market_line']}")
    print(f"Edge: {analysis['predicted_value'] - analysis['market_line']:.1f} yards")
    print(f"Confidence: {analysis['confidence']}%")
    print(f"Best EV: {analysis['best_ev']}%")
    print(f"Recommendation: {analysis['recommended_bet']}")

