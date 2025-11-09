"""
Team Betting Analyzer
Aggregate player name patterns to team-level predictions
Win probability, point spreads, team totals
"""

from typing import Dict, List, Optional
import numpy as np
import logging
from analyzers.sports_betting_analyzer import SportsBettingAnalyzer
from analyzers.betting_ev_calculator import BettingEVCalculator

logger = logging.getLogger(__name__)


class TeamBettingAnalyzer:
    """Analyze team betting opportunities using roster name patterns"""
    
    def __init__(self):
        """Initialize with betting analyzer and EV calculator"""
        self.betting_analyzer = SportsBettingAnalyzer()
        self.ev_calculator = BettingEVCalculator()
    
    def calculate_roster_score(self, roster: List[Dict], sport: str,
                               position_weights: Optional[Dict] = None) -> Dict:
        """
        Calculate aggregate team score from roster name patterns
        
        Args:
            roster: List of players with linguistic_features
            sport: 'football', 'basketball', or 'baseball'
            position_weights: Optional position importance weights
            
        Returns:
            Team aggregate score and distribution
        """
        if not roster:
            return {'error': 'Empty roster'}
        
        # Default position weights (can be customized)
        if position_weights is None:
            position_weights = self._get_default_weights(sport)
        
        player_scores = []
        weighted_scores = []
        
        for player in roster:
            # Calculate individual player score
            linguistic_features = player.get('linguistic_features', {})
            if not linguistic_features:
                continue
            
            score_result = self.betting_analyzer.calculate_player_score(
                linguistic_features, sport
            )
            
            player_score = score_result['overall_score']
            player_weight = position_weights.get(player.get('position', 'default'), 1.0)
            
            player_scores.append(player_score)
            weighted_scores.append(player_score * player_weight)
            
            player['betting_score'] = player_score
            player['weight'] = player_weight
        
        if not player_scores:
            return {'error': 'No valid player scores'}
        
        # Calculate team metrics
        team_score = np.average(player_scores)
        weighted_team_score = np.sum(weighted_scores) / np.sum([p['weight'] for p in roster if 'betting_score' in p])
        score_std = np.std(player_scores)
        
        # Quality tier classification
        if weighted_team_score >= 65:
            quality_tier = 'ELITE'
        elif weighted_team_score >= 55:
            quality_tier = 'ABOVE_AVERAGE'
        elif weighted_team_score >= 45:
            quality_tier = 'AVERAGE'
        else:
            quality_tier = 'BELOW_AVERAGE'
        
        return {
            'sport': sport,
            'roster_size': len(roster),
            'scored_players': len(player_scores),
            'team_score': round(team_score, 2),
            'weighted_team_score': round(weighted_team_score, 2),
            'score_std': round(score_std, 2),
            'score_range': [round(min(player_scores), 2), round(max(player_scores), 2)],
            'quality_tier': quality_tier,
            'top_players': sorted(
                [{'name': p['name'], 'score': p['betting_score']} 
                 for p in roster if 'betting_score' in p],
                key=lambda x: x['score'], reverse=True
            )[:5]
        }
    
    def _get_default_weights(self, sport: str) -> Dict:
        """Get default position importance weights"""
        weights = {
            'football': {
                'QB': 3.0,    # Quarterback most important
                'RB': 1.5,    # Running backs significant
                'WR': 1.5,    # Wide receivers significant
                'TE': 1.0,    # Tight ends moderate
                'OL': 0.8,    # Offensive line lower individual impact
                'DL': 1.2,    # Defensive line important
                'LB': 1.0,    # Linebackers moderate
                'DB': 1.0,    # Defensive backs moderate
                'default': 1.0
            },
            'basketball': {
                'PG': 1.5,    # Point guard elevated importance
                'SG': 1.2,    # Shooting guard important
                'SF': 1.2,    # Small forward important
                'PF': 1.0,    # Power forward baseline
                'C': 1.0,     # Center baseline
                'default': 1.0
            },
            'baseball': {
                'SP': 2.0,    # Starting pitchers most important
                'RP': 0.8,    # Relief pitchers less weight
                'C': 1.2,     # Catcher elevated
                'IF': 1.0,    # Infielders baseline
                'OF': 1.0,    # Outfielders baseline
                'DH': 1.3,    # Designated hitter important
                'default': 1.0
            }
        }
        return weights.get(sport, {'default': 1.0})
    
    def predict_game_outcome(self, home_roster: List[Dict], away_roster: List[Dict],
                            sport: str) -> Dict:
        """
        Predict game outcome based on roster name patterns
        
        Args:
            home_roster: Home team roster with linguistic features
            away_roster: Away team roster with linguistic features
            sport: Sport type
            
        Returns:
            Prediction with win probability and expected margin
        """
        # Calculate team scores
        home_analysis = self.calculate_roster_score(home_roster, sport)
        away_analysis = self.calculate_roster_score(away_roster, sport)
        
        if 'error' in home_analysis or 'error' in away_analysis:
            return {'error': 'Invalid roster data'}
        
        home_score = home_analysis['weighted_team_score']
        away_score = away_analysis['weighted_team_score']
        
        # Calculate score differential
        score_diff = home_score - away_score
        
        # Add home field advantage (empirically ~3 points in most sports)
        home_advantage = 3.0
        adjusted_diff = score_diff + home_advantage
        
        # Convert score differential to win probability
        # Using logistic function: P(win) = 1 / (1 + exp(-k * diff))
        # k = 0.1 means 10-point difference ~= 73% win probability
        k = 0.10
        home_win_prob = 1 / (1 + np.exp(-k * adjusted_diff))
        
        # Estimate point spread
        # Score differential translates to point spread
        # 10-point score difference ~= 7-point spread (approximate)
        spread_factor = 0.7
        predicted_spread = adjusted_diff * spread_factor
        
        # Confidence based on score differential magnitude
        confidence = min(abs(adjusted_diff) * 2, 85)  # Cap at 85%
        
        return {
            'home_team': {
                'score': home_score,
                'quality_tier': home_analysis['quality_tier'],
                'top_players': home_analysis['top_players'][:3]
            },
            'away_team': {
                'score': away_score,
                'quality_tier': away_analysis['quality_tier'],
                'top_players': away_analysis['top_players'][:3]
            },
            'prediction': {
                'home_win_probability': round(home_win_prob, 3),
                'away_win_probability': round(1 - home_win_prob, 3),
                'predicted_spread': round(predicted_spread, 1),  # Negative = home favored
                'confidence': round(confidence, 1),
                'score_differential': round(adjusted_diff, 2),
                'home_advantage_applied': home_advantage
            },
            'recommendation': 'BET HOME' if home_win_prob > 0.6 else 'BET AWAY' if home_win_prob < 0.4 else 'NO CLEAR EDGE'
        }
    
    def analyze_spread_bet(self, home_roster: List[Dict], away_roster: List[Dict],
                          sport: str, market_spread: float, 
                          spread_odds: int = -110) -> Dict:
        """
        Analyze point spread betting opportunity
        
        Args:
            home_roster: Home team roster
            away_roster: Away team roster
            sport: Sport type
            market_spread: Bookmaker's spread (negative = home favored)
            spread_odds: Odds for the spread
            
        Returns:
            Spread analysis with EV
        """
        # Get game prediction
        game_prediction = self.predict_game_outcome(home_roster, away_roster, sport)
        
        if 'error' in game_prediction:
            return game_prediction
        
        predicted_spread = game_prediction['prediction']['predicted_spread']
        confidence = game_prediction['prediction']['confidence']
        
        # Calculate EV for spread bet
        spread_ev = self.ev_calculator.calculate_spread_ev(
            predicted_margin=predicted_spread,
            spread_line=market_spread,
            spread_odds=spread_odds,
            confidence=confidence
        )
        
        # Determine recommendation
        edge = predicted_spread - market_spread
        
        if abs(edge) > 3.0 and spread_ev['ev'] > 0.03:
            if edge > 0:
                bet_recommendation = 'BET HOME (cover spread)'
            else:
                bet_recommendation = 'BET AWAY (cover spread)'
        else:
            bet_recommendation = 'NO BET - Insufficient edge'
        
        return {
            **game_prediction,
            'market_spread': market_spread,
            'spread_edge': round(edge, 2),
            'spread_ev': spread_ev,
            'bet_recommendation': bet_recommendation
        }
    
    def analyze_moneyline_bet(self, home_roster: List[Dict], away_roster: List[Dict],
                             sport: str, home_odds: int, away_odds: int) -> Dict:
        """
        Analyze moneyline betting opportunity
        
        Args:
            home_roster: Home team roster
            away_roster: Away team roster
            sport: Sport type
            home_odds: Home team moneyline odds
            away_odds: Away team moneyline odds
            
        Returns:
            Moneyline analysis with EV
        """
        # Get game prediction
        game_prediction = self.predict_game_outcome(home_roster, away_roster, sport)
        
        if 'error' in game_prediction:
            return game_prediction
        
        home_win_prob = game_prediction['prediction']['home_win_probability']
        away_win_prob = game_prediction['prediction']['away_win_probability']
        
        # Calculate EV for each side
        home_ev = self.ev_calculator.calculate_moneyline_ev(home_win_prob, home_odds)
        away_ev = self.ev_calculator.calculate_moneyline_ev(away_win_prob, away_odds)
        
        # Determine best bet
        if home_ev['ev'] > 0.03 and home_ev['ev'] > away_ev['ev']:
            bet_recommendation = f"BET HOME at {home_odds} (EV: {home_ev['ev_percentage']}%)"
        elif away_ev['ev'] > 0.03:
            bet_recommendation = f"BET AWAY at {away_odds} (EV: {away_ev['ev_percentage']}%)"
        else:
            bet_recommendation = 'NO BET - Insufficient edge'
        
        return {
            **game_prediction,
            'home_moneyline': {
                'odds': home_odds,
                'ev': home_ev
            },
            'away_moneyline': {
                'odds': away_odds,
                'ev': away_ev
            },
            'best_bet': bet_recommendation
        }


if __name__ == "__main__":
    # Test team analyzer
    logging.basicConfig(level=logging.INFO)
    
    analyzer = TeamBettingAnalyzer()
    
    print("\n=== EXAMPLE TEAM ANALYSIS ===")
    
    # Example rosters (simplified)
    home_roster = [
        {
            'name': 'Patrick Mahomes',
            'position': 'QB',
            'linguistic_features': {'syllables': 3, 'harshness': 65, 'memorability': 85, 'length': 15}
        },
        {
            'name': 'Travis Kelce',
            'position': 'TE',
            'linguistic_features': {'syllables': 3, 'harshness': 70, 'memorability': 80, 'length': 12}
        },
        {
            'name': 'Chris Jones',
            'position': 'DL',
            'linguistic_features': {'syllables': 2, 'harshness': 75, 'memorability': 65, 'length': 10}
        }
    ]
    
    away_roster = [
        {
            'name': 'Joe Burrow',
            'position': 'QB',
            'linguistic_features': {'syllables': 3, 'harshness': 60, 'memorability': 70, 'length': 9}
        },
        {
            'name': 'Ja\'Marr Chase',
            'position': 'WR',
            'linguistic_features': {'syllables': 3, 'harshness': 55, 'memorability': 75, 'length': 12}
        }
    ]
    
    # Analyze game
    game_analysis = analyzer.predict_game_outcome(home_roster, away_roster, 'football')
    
    print(f"Home Team Score: {game_analysis['home_team']['score']}")
    print(f"Away Team Score: {game_analysis['away_team']['score']}")
    print(f"Home Win Probability: {game_analysis['prediction']['home_win_probability']:.1%}")
    print(f"Predicted Spread: {game_analysis['prediction']['predicted_spread']}")
    print(f"Recommendation: {game_analysis['recommendation']}")
    
    # Analyze spread bet
    print("\n=== SPREAD BET ANALYSIS ===")
    spread_analysis = analyzer.analyze_spread_bet(
        home_roster, away_roster, 'football',
        market_spread=-3.5,  # Home team favored by 3.5
        spread_odds=-110
    )
    print(f"Market Spread: {spread_analysis['market_spread']}")
    print(f"Spread Edge: {spread_analysis['spread_edge']} points")
    print(f"Spread EV: {spread_analysis['spread_ev']['ev_percentage']}%")
    print(f"Recommendation: {spread_analysis['bet_recommendation']}")

