"""
Betting Bankroll Manager
Kelly Criterion optimization and bankroll allocation with risk management
"""

import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BettingBankrollManager:
    """Manage betting bankroll with Kelly Criterion and risk controls"""
    
    def __init__(self, initial_bankroll: float = 10000, 
                 max_bet_percentage: float = 0.05,
                 max_simultaneous_exposure: float = 0.25):
        """
        Initialize bankroll manager
        
        Args:
            initial_bankroll: Starting bankroll amount
            max_bet_percentage: Max % of bankroll per bet (5% default)
            max_simultaneous_exposure: Max % in simultaneous bets (25% default)
        """
        self.initial_bankroll = initial_bankroll
        self.current_bankroll = initial_bankroll
        self.max_bet_percentage = max_bet_percentage
        self.max_simultaneous_exposure = max_simultaneous_exposure
        
        # Risk management
        self.drawdown_halt_threshold = 0.20  # Stop at 20% drawdown
        self.consecutive_loss_threshold = 10
        self.consecutive_losses = 0
        self.peak_bankroll = initial_bankroll
        
        # Tracking
        self.allocated_capital = 0
        self.bet_history = []
    
    def kelly_criterion(self, edge: float, odds: float, 
                       fractional_kelly: float = 0.25) -> float:
        """
        Calculate optimal bet size using Kelly Criterion
        
        Args:
            edge: Betting edge (win_prob - implied_prob)
            odds: Decimal odds
            fractional_kelly: Fraction of Kelly to use (0.25 = 1/4 Kelly, safer)
            
        Returns:
            Optimal bet size as fraction of bankroll
        """
        if edge <= 0 or odds <= 1:
            return 0
        
        # Kelly formula: f = (edge × (odds - 1)) / (odds - 1) = edge
        # For decimal odds: f = edge / (odds - 1)
        kelly_fraction = edge / (odds - 1)
        
        # Apply fractional Kelly for safety
        adjusted_kelly = kelly_fraction * fractional_kelly
        
        # Never bet more than max allowed
        final_fraction = min(adjusted_kelly, self.max_bet_percentage)
        
        return max(0, final_fraction)
    
    def calculate_bet_size(self, edge: float, odds: int, confidence: float = 70,
                          ev: float = 0.05) -> Dict:
        """
        Calculate recommended bet size with risk adjustments
        
        Args:
            edge: Betting edge (probability edge)
            odds: American odds
            confidence: Confidence in prediction (0-100)
            ev: Expected value (decimal)
            
        Returns:
            Dict with recommended bet size and reasoning
        """
        # Convert American odds to decimal
        if odds > 0:
            decimal_odds = (odds / 100) + 1
        else:
            decimal_odds = (100 / abs(odds)) + 1
        
        # Adjust edge by confidence
        confidence_multiplier = confidence / 100
        adjusted_edge = edge * confidence_multiplier
        
        # Calculate Kelly size
        kelly_size = self.kelly_criterion(adjusted_edge, decimal_odds, fractional_kelly=0.25)
        
        # Calculate dollar amount
        bet_amount = kelly_size * self.current_bankroll
        
        # Apply risk controls
        max_bet_amount = self.current_bankroll * self.max_bet_percentage
        bet_amount = min(bet_amount, max_bet_amount)
        
        # Check if we can place bet (not exceeding exposure limits)
        available_capital = self.current_bankroll * self.max_simultaneous_exposure - self.allocated_capital
        
        if bet_amount > available_capital:
            bet_amount = available_capital
            reason = f"Reduced to {available_capital:.0f} due to exposure limits"
        elif kelly_size >= self.max_bet_percentage:
            reason = f"Capped at {self.max_bet_percentage:.1%} max bet size"
        elif confidence < 70:
            reason = f"Reduced due to moderate confidence ({confidence:.0f}%)"
        else:
            reason = f"Optimal Kelly sizing with {confidence:.0f}% confidence"
        
        # Check drawdown
        current_drawdown = (self.peak_bankroll - self.current_bankroll) / self.peak_bankroll
        if current_drawdown >= self.drawdown_halt_threshold:
            bet_amount = 0
            reason = f"BETTING HALTED: {current_drawdown:.1%} drawdown exceeds {self.drawdown_halt_threshold:.1%} limit"
        
        # Check consecutive losses
        if self.consecutive_losses >= self.consecutive_loss_threshold:
            bet_amount = bet_amount * 0.5  # Reduce to half size
            reason = f"Reduced 50% after {self.consecutive_losses} consecutive losses"
        
        return {
            'recommended_bet': round(bet_amount, 2),
            'bet_percentage': round((bet_amount / self.current_bankroll) * 100, 2),
            'kelly_fraction': round(kelly_size, 4),
            'reason': reason,
            'available_capital': round(available_capital, 2),
            'current_bankroll': round(self.current_bankroll, 2),
            'can_bet': bet_amount > 0
        }
    
    def allocate_bet(self, bet_amount: float, bet_id: str) -> bool:
        """
        Allocate capital for a bet
        
        Args:
            bet_amount: Amount to allocate
            bet_id: Unique bet identifier
            
        Returns:
            True if successful, False if insufficient capital
        """
        available = self.current_bankroll * self.max_simultaneous_exposure - self.allocated_capital
        
        if bet_amount > available:
            logger.warning(f"Insufficient capital: need {bet_amount}, have {available}")
            return False
        
        self.allocated_capital += bet_amount
        logger.info(f"Allocated ${bet_amount:.2f} for bet {bet_id}. Total allocated: ${self.allocated_capital:.2f}")
        return True
    
    def settle_bet(self, bet_amount: float, result: str, payout: float = 0) -> Dict:
        """
        Settle a completed bet
        
        Args:
            bet_amount: Original bet amount
            result: 'win', 'loss', or 'push'
            payout: Total payout if won (includes original stake)
            
        Returns:
            Dict with updated bankroll info
        """
        # Release allocated capital
        self.allocated_capital = max(0, self.allocated_capital - bet_amount)
        
        if result == 'win':
            profit = payout - bet_amount
            self.current_bankroll += profit
            self.consecutive_losses = 0
            
            # Update peak
            if self.current_bankroll > self.peak_bankroll:
                self.peak_bankroll = self.current_bankroll
            
            logger.info(f"Bet WON: +${profit:.2f}. Bankroll: ${self.current_bankroll:.2f}")
            
        elif result == 'loss':
            self.current_bankroll -= bet_amount
            self.consecutive_losses += 1
            logger.info(f"Bet LOST: -${bet_amount:.2f}. Bankroll: ${self.current_bankroll:.2f}")
            
        else:  # push
            logger.info(f"Bet PUSHED: ${bet_amount:.2f} returned. Bankroll: ${self.current_bankroll:.2f}")
        
        # Calculate metrics
        total_roi = ((self.current_bankroll - self.initial_bankroll) / self.initial_bankroll) * 100
        current_drawdown = ((self.peak_bankroll - self.current_bankroll) / self.peak_bankroll) * 100
        
        return {
            'result': result,
            'current_bankroll': round(self.current_bankroll, 2),
            'allocated_capital': round(self.allocated_capital, 2),
            'available_capital': round(self.current_bankroll - self.allocated_capital, 2),
            'total_roi': round(total_roi, 2),
            'current_drawdown': round(current_drawdown, 2),
            'consecutive_losses': self.consecutive_losses,
            'is_halted': current_drawdown >= (self.drawdown_halt_threshold * 100)
        }
    
    def get_portfolio_allocation(self, opportunities: List[Dict]) -> List[Dict]:
        """
        Allocate bankroll across multiple opportunities
        
        Args:
            opportunities: List of betting opportunities with edge, odds, confidence, ev
            
        Returns:
            List of opportunities with recommended bet sizes
        """
        # Calculate total desired Kelly allocation
        total_kelly = 0
        for opp in opportunities:
            edge = opp.get('edge', 0)
            odds = opp.get('odds', -110)
            confidence = opp.get('confidence', 70)
            
            # Convert odds
            if odds > 0:
                decimal_odds = (odds / 100) + 1
            else:
                decimal_odds = (100 / abs(odds)) + 1
            
            # Adjusted Kelly
            adjusted_edge = edge * (confidence / 100)
            kelly = self.kelly_criterion(adjusted_edge, decimal_odds)
            opp['kelly_fraction'] = kelly
            total_kelly += kelly
        
        # If total Kelly exceeds max exposure, scale down proportionally
        available_exposure = self.max_simultaneous_exposure
        
        if total_kelly > available_exposure:
            scale_factor = available_exposure / total_kelly
        else:
            scale_factor = 1.0
        
        # Allocate
        for opp in opportunities:
            kelly = opp.get('kelly_fraction', 0)
            scaled_fraction = kelly * scale_factor
            bet_amount = scaled_fraction * self.current_bankroll
            
            # Cap at max bet size
            max_bet = self.current_bankroll * self.max_bet_percentage
            bet_amount = min(bet_amount, max_bet)
            
            opp['recommended_bet'] = round(bet_amount, 2)
            opp['bet_percentage'] = round((bet_amount / self.current_bankroll) * 100, 2)
        
        return opportunities
    
    def get_status(self) -> Dict:
        """Get current bankroll status"""
        total_roi = ((self.current_bankroll - self.initial_bankroll) / self.initial_bankroll) * 100
        current_drawdown = ((self.peak_bankroll - self.current_bankroll) / self.peak_bankroll) * 100
        available = self.current_bankroll - self.allocated_capital
        
        return {
            'current_bankroll': round(self.current_bankroll, 2),
            'initial_bankroll': round(self.initial_bankroll, 2),
            'peak_bankroll': round(self.peak_bankroll, 2),
            'allocated_capital': round(self.allocated_capital, 2),
            'available_capital': round(available, 2),
            'available_percentage': round((available / self.current_bankroll) * 100, 2),
            'total_roi': round(total_roi, 2),
            'current_drawdown': round(current_drawdown, 2),
            'consecutive_losses': self.consecutive_losses,
            'is_halted': current_drawdown >= (self.drawdown_halt_threshold * 100),
            'max_bet_amount': round(self.current_bankroll * self.max_bet_percentage, 2),
            'max_exposure': round(self.current_bankroll * self.max_simultaneous_exposure, 2)
        }
    
    def reset_bankroll(self, new_bankroll: Optional[float] = None):
        """Reset bankroll to initial or specified amount"""
        if new_bankroll:
            self.initial_bankroll = new_bankroll
            self.current_bankroll = new_bankroll
        else:
            self.current_bankroll = self.initial_bankroll
        
        self.peak_bankroll = self.current_bankroll
        self.consecutive_losses = 0
        self.allocated_capital = 0
        logger.info(f"Bankroll reset to ${self.current_bankroll:.2f}")


if __name__ == "__main__":
    # Test bankroll manager
    logging.basicConfig(level=logging.INFO)
    
    manager = BettingBankrollManager(initial_bankroll=10000)
    
    print("\n=== INITIAL STATUS ===")
    status = manager.get_status()
    for key, value in status.items():
        print(f"{key}: {value}")
    
    print("\n=== BET SIZE CALCULATION ===")
    # Example: 5% edge, -110 odds, 75% confidence
    bet_size = manager.calculate_bet_size(edge=0.05, odds=-110, confidence=75, ev=0.05)
    print(f"Recommended bet: ${bet_size['recommended_bet']}")
    print(f"Percentage: {bet_size['bet_percentage']}%")
    print(f"Reason: {bet_size['reason']}")
    
    print("\n=== PORTFOLIO ALLOCATION ===")
    opportunities = [
        {'name': 'Player A', 'edge': 0.06, 'odds': -110, 'confidence': 80, 'ev': 0.06},
        {'name': 'Player B', 'edge': 0.04, 'odds': 120, 'confidence': 70, 'ev': 0.05},
        {'name': 'Player C', 'edge': 0.08, 'odds': -120, 'confidence': 85, 'ev': 0.08}
    ]
    
    allocated = manager.get_portfolio_allocation(opportunities)
    for opp in allocated:
        print(f"{opp['name']}: ${opp['recommended_bet']} ({opp['bet_percentage']}%)")
    
    print("\n=== SIMULATE BETS ===")
    # Allocate first bet
    manager.allocate_bet(bet_size['recommended_bet'], 'bet_001')
    
    # Win
    result = manager.settle_bet(bet_size['recommended_bet'], 'win', payout=bet_size['recommended_bet'] * 1.91)
    print(f"After win: ${result['current_bankroll']}, ROI: {result['total_roi']}%")
    
    # Lose
    bet_size2 = manager.calculate_bet_size(edge=0.05, odds=-110, confidence=75, ev=0.05)
    manager.allocate_bet(bet_size2['recommended_bet'], 'bet_002')
    result = manager.settle_bet(bet_size2['recommended_bet'], 'loss')
    print(f"After loss: ${result['current_bankroll']}, ROI: {result['total_roi']}%")

