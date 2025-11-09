"""
Betting Expected Value Calculator
Calculates EV for sports betting opportunities by comparing predicted performance to market lines
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class BettingEVCalculator:
    """Calculate expected value for betting opportunities"""
    
    def __init__(self):
        """Initialize EV calculator"""
        self.vig_percentage = 0.045  # Typical sportsbook vig (4.5%)
    
    def american_to_decimal(self, american_odds: int) -> float:
        """
        Convert American odds to decimal odds
        
        Args:
            american_odds: American format (+150, -110, etc.)
            
        Returns:
            Decimal odds
        """
        if american_odds > 0:
            return (american_odds / 100) + 1
        else:
            return (100 / abs(american_odds)) + 1
    
    def decimal_to_american(self, decimal_odds: float) -> int:
        """Convert decimal odds to American format"""
        if decimal_odds >= 2.0:
            return int((decimal_odds - 1) * 100)
        else:
            return int(-100 / (decimal_odds - 1))
    
    def implied_probability(self, american_odds: int, remove_vig: bool = True) -> float:
        """
        Calculate implied probability from odds
        
        Args:
            american_odds: American format odds
            remove_vig: Whether to remove vig (overround)
            
        Returns:
            Probability (0-1)
        """
        decimal = self.american_to_decimal(american_odds)
        prob = 1 / decimal
        
        if remove_vig:
            # Adjust for vig
            prob = prob * (1 - self.vig_percentage)
        
        return prob
    
    def calculate_prop_ev(self, predicted_value: float, market_line: float,
                         over_odds: int = -110, under_odds: int = -110,
                         confidence: float = 70) -> Dict:
        """
        Calculate EV for player prop bet (over/under)
        
        Args:
            predicted_value: Our predicted stat value
            market_line: Bookmaker's line
            over_odds: Odds for over bet (American)
            under_odds: Odds for under bet (American)
            confidence: Prediction confidence (0-100)
            
        Returns:
            Dict with EV for both over and under, recommended bet
        """
        # Calculate edge (predicted - line)
        edge = predicted_value - market_line
        edge_percentage = (edge / market_line * 100) if market_line != 0 else 0
        
        # Convert confidence to probability adjustment
        # Lower confidence = reduce edge
        confidence_multiplier = confidence / 100
        adjusted_edge = edge * confidence_multiplier
        
        # Determine win probability for each side
        # Use statistical model: edge translates to win probability
        # Assuming normal distribution, 1 point edge ~= 5% probability increase
        edge_to_prob_factor = 0.05
        
        over_win_prob = 0.5 + (adjusted_edge * edge_to_prob_factor)
        over_win_prob = max(0.01, min(0.99, over_win_prob))  # Bound probability
        under_win_prob = 1 - over_win_prob
        
        # Calculate decimal odds
        over_decimal = self.american_to_decimal(over_odds)
        under_decimal = self.american_to_decimal(under_odds)
        
        # Calculate EV for each side
        # EV = (Win Probability × Profit) - (Loss Probability × Stake)
        over_ev = (over_win_prob * (over_decimal - 1)) - (1 - over_win_prob)
        under_ev = (under_win_prob * (under_decimal - 1)) - (1 - under_win_prob)
        
        # Determine recommendation
        if over_ev > 0.05:  # 5% edge threshold
            recommendation = 'BET OVER'
            best_ev = over_ev
            best_odds = over_odds
        elif under_ev > 0.05:
            recommendation = 'BET UNDER'
            best_ev = under_ev
            best_odds = under_odds
        elif max(over_ev, under_ev) > 0:
            recommendation = 'SMALL EDGE'
            best_ev = max(over_ev, under_ev)
            best_odds = over_odds if over_ev > under_ev else under_odds
        else:
            recommendation = 'NO BET'
            best_ev = max(over_ev, under_ev)
            best_odds = None
        
        return {
            'predicted_value': round(predicted_value, 2),
            'market_line': market_line,
            'edge': round(edge, 2),
            'edge_percentage': round(edge_percentage, 2),
            'confidence': confidence,
            'over': {
                'odds': over_odds,
                'win_probability': round(over_win_prob, 3),
                'ev': round(over_ev, 4),
                'ev_percentage': round(over_ev * 100, 2)
            },
            'under': {
                'odds': under_odds,
                'win_probability': round(under_win_prob, 3),
                'ev': round(under_ev, 4),
                'ev_percentage': round(under_ev * 100, 2)
            },
            'recommendation': recommendation,
            'best_ev': round(best_ev, 4),
            'best_ev_percentage': round(best_ev * 100, 2),
            'best_odds': best_odds
        }
    
    def calculate_moneyline_ev(self, win_probability: float, moneyline_odds: int) -> Dict:
        """
        Calculate EV for moneyline bet
        
        Args:
            win_probability: Predicted probability of winning (0-1)
            moneyline_odds: Moneyline odds (American)
            
        Returns:
            Dict with EV and recommendation
        """
        decimal_odds = self.american_to_decimal(moneyline_odds)
        market_prob = self.implied_probability(moneyline_odds)
        
        # Calculate EV
        ev = (win_probability * (decimal_odds - 1)) - (1 - win_probability)
        
        # Edge is difference between our probability and market probability
        edge = win_probability - market_prob
        
        recommendation = 'BET' if ev > 0.03 else 'PASS'
        
        return {
            'win_probability': round(win_probability, 3),
            'market_probability': round(market_prob, 3),
            'edge': round(edge, 3),
            'moneyline_odds': moneyline_odds,
            'ev': round(ev, 4),
            'ev_percentage': round(ev * 100, 2),
            'recommendation': recommendation
        }
    
    def calculate_spread_ev(self, predicted_margin: float, spread_line: float,
                           spread_odds: int = -110, confidence: float = 70) -> Dict:
        """
        Calculate EV for point spread bet
        
        Args:
            predicted_margin: Predicted point differential
            spread_line: Bookmaker's spread (negative = favorite)
            spread_odds: Odds for the spread bet
            confidence: Prediction confidence
            
        Returns:
            Dict with EV and recommendation
        """
        # Calculate edge
        edge = predicted_margin - spread_line
        confidence_multiplier = confidence / 100
        adjusted_edge = edge * confidence_multiplier
        
        # Convert edge to win probability
        # In spreads, 1 point edge ~= 4% probability increase
        edge_to_prob = 0.04
        win_probability = 0.5 + (adjusted_edge * edge_to_prob)
        win_probability = max(0.01, min(0.99, win_probability))
        
        # Calculate EV
        decimal_odds = self.american_to_decimal(spread_odds)
        ev = (win_probability * (decimal_odds - 1)) - (1 - win_probability)
        
        recommendation = 'BET' if ev > 0.03 else 'PASS'
        
        return {
            'predicted_margin': round(predicted_margin, 2),
            'spread_line': spread_line,
            'edge': round(edge, 2),
            'confidence': confidence,
            'win_probability': round(win_probability, 3),
            'odds': spread_odds,
            'ev': round(ev, 4),
            'ev_percentage': round(ev * 100, 2),
            'recommendation': recommendation
        }
    
    def calculate_parlay_ev(self, individual_evs: List[float], 
                           individual_odds: List[int]) -> Dict:
        """
        Calculate EV for parlay bet
        
        Args:
            individual_evs: List of individual bet EVs
            individual_odds: List of individual bet odds (American)
            
        Returns:
            Dict with parlay EV (typically negative due to compounding vig)
        """
        # Convert to win probabilities
        win_probs = []
        for ev, odds in zip(individual_evs, individual_odds):
            decimal = self.american_to_decimal(odds)
            # Back-calculate win probability from EV
            # EV = P(win) × (decimal - 1) - P(lose)
            # Simplified: assume fair odds initially
            prob = (ev + 1) / decimal
            prob = max(0.01, min(0.99, prob))
            win_probs.append(prob)
        
        # Parlay win probability is product of individual probabilities
        parlay_prob = np.prod(win_probs)
        
        # Parlay odds is product of decimal odds
        decimal_odds_list = [self.american_to_decimal(o) for o in individual_odds]
        parlay_decimal_odds = np.prod(decimal_odds_list)
        
        # Calculate parlay EV
        parlay_ev = (parlay_prob * (parlay_decimal_odds - 1)) - (1 - parlay_prob)
        
        return {
            'num_legs': len(individual_evs),
            'individual_win_probs': [round(p, 3) for p in win_probs],
            'parlay_win_prob': round(parlay_prob, 4),
            'parlay_odds': self.decimal_to_american(parlay_decimal_odds),
            'parlay_ev': round(parlay_ev, 4),
            'parlay_ev_percentage': round(parlay_ev * 100, 2),
            'recommendation': 'AVOID PARLAY - Bet legs individually' if parlay_ev < max(individual_evs) else 'ACCEPTABLE'
        }
    
    def calculate_futures_ev(self, win_probability: float, odds: int,
                            market_efficiency: float = 0.85) -> Dict:
        """
        Calculate EV for futures bet (MVP, championship, etc.)
        
        Args:
            win_probability: Predicted probability of outcome
            odds: Futures odds (American, typically long odds)
            market_efficiency: Market efficiency factor (futures less efficient)
            
        Returns:
            Dict with EV adjusted for futures market inefficiency
        """
        decimal_odds = self.american_to_decimal(odds)
        market_prob = self.implied_probability(odds)
        
        # Adjust for lower market efficiency in futures
        # Futures markets have more edge opportunities
        edge_multiplier = 1 / market_efficiency
        
        # Calculate EV
        ev = (win_probability * (decimal_odds - 1)) - (1 - win_probability)
        adjusted_ev = ev * edge_multiplier
        
        edge = win_probability - market_prob
        
        recommendation = 'BET' if adjusted_ev > 0.05 else 'PASS'
        
        return {
            'win_probability': round(win_probability, 3),
            'market_probability': round(market_prob, 3),
            'edge': round(edge, 3),
            'odds': odds,
            'ev': round(ev, 4),
            'adjusted_ev': round(adjusted_ev, 4),
            'ev_percentage': round(adjusted_ev * 100, 2),
            'market_efficiency': market_efficiency,
            'recommendation': recommendation
        }
    
    def rank_opportunities(self, opportunities: List[Dict]) -> List[Dict]:
        """
        Rank betting opportunities by EV × confidence
        
        Args:
            opportunities: List of opportunity dicts with 'ev' and 'confidence'
            
        Returns:
            Sorted list by expected value
        """
        for opp in opportunities:
            opp['ev_score'] = opp.get('ev', 0) * (opp.get('confidence', 50) / 100)
        
        opportunities.sort(key=lambda x: x['ev_score'], reverse=True)
        
        return opportunities
    
    def calculate_breakeven_line(self, predicted_value: float, odds: int = -110,
                                min_ev: float = 0.05) -> float:
        """
        Calculate breakeven line where bet would have minimum EV
        
        Args:
            predicted_value: Our prediction
            odds: Betting odds
            min_ev: Minimum acceptable EV
            
        Returns:
            Line value where bet reaches min EV
        """
        decimal_odds = self.american_to_decimal(odds)
        
        # Work backwards: what line gives us min_ev?
        # Simplified calculation
        edge_needed = min_ev / (decimal_odds - 1)
        breakeven_line = predicted_value - edge_needed
        
        return round(breakeven_line, 1)


if __name__ == "__main__":
    # Test the calculator
    calc = BettingEVCalculator()
    
    print("\n=== PROP BET EXAMPLE ===")
    print("Player predicted: 25.5 points, Market line: 23.5")
    prop_ev = calc.calculate_prop_ev(
        predicted_value=25.5,
        market_line=23.5,
        over_odds=-110,
        under_odds=-110,
        confidence=75
    )
    print(f"Over EV: {prop_ev['over']['ev_percentage']}%")
    print(f"Under EV: {prop_ev['under']['ev_percentage']}%")
    print(f"Recommendation: {prop_ev['recommendation']}")
    print(f"Best EV: {prop_ev['best_ev_percentage']}%")
    
    print("\n=== MONEYLINE EXAMPLE ===")
    print("Win probability: 58%, Moneyline: +150")
    ml_ev = calc.calculate_moneyline_ev(
        win_probability=0.58,
        moneyline_odds=150
    )
    print(f"EV: {ml_ev['ev_percentage']}%")
    print(f"Edge: {ml_ev['edge']:.1%}")
    print(f"Recommendation: {ml_ev['recommendation']}")
    
    print("\n=== FUTURES EXAMPLE ===")
    print("MVP win probability: 12%, Odds: +800")
    futures_ev = calc.calculate_futures_ev(
        win_probability=0.12,
        odds=800
    )
    print(f"Adjusted EV: {futures_ev['ev_percentage']}%")
    print(f"Recommendation: {futures_ev['recommendation']}")

