"""
Bet Tracker
Log and track all placed bets with immutable records
"""

from core.models import db, SportsBet, BankrollHistory
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)


class BetTracker:
    """Track sports bets with immutable records"""
    
    def __init__(self):
        """Initialize bet tracker"""
        pass
    
    def generate_bet_id(self) -> str:
        """Generate unique bet ID"""
        return f"BET_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8].upper()}"
    
    def place_bet(self, bet_data: dict, bankroll_state: dict) -> SportsBet:
        """
        Record a placed bet (immutable once created)
        
        Args:
            bet_data: Dict with all bet details
            bankroll_state: Current bankroll state
            
        Returns:
            SportsBet object
        """
        try:
            bet_id = self.generate_bet_id()
            
            bet = SportsBet(
                bet_id=bet_id,
                sport=bet_data['sport'],
                bet_type=bet_data['bet_type'],
                market_type=bet_data.get('market_type'),
                player_name=bet_data.get('player_name'),
                team_name=bet_data.get('team_name'),
                opponent_name=bet_data.get('opponent_name'),
                market_line=bet_data.get('market_line'),
                bet_side=bet_data.get('bet_side'),
                odds=bet_data['odds'],
                stake=bet_data['stake'],
                predicted_value=bet_data.get('predicted_value'),
                confidence_score=bet_data.get('confidence_score'),
                expected_value=bet_data.get('expected_value'),
                linguistic_score=bet_data.get('linguistic_score'),
                syllables=bet_data.get('syllables'),
                harshness=bet_data.get('harshness'),
                memorability=bet_data.get('memorability'),
                name_length=bet_data.get('name_length'),
                bankroll_at_bet=bankroll_state.get('current_bankroll'),
                bet_percentage=bet_data.get('bet_percentage'),
                kelly_fraction=bet_data.get('kelly_fraction'),
                game_date=bet_data.get('game_date'),
                is_locked=True,  # Lock immediately
                bet_status='pending'
            )
            
            db.session.add(bet)
            
            # Log bankroll snapshot
            self._log_bankroll_snapshot(
                bankroll_state,
                event_type='bet_placed',
                event_id=bet_id
            )
            
            db.session.commit()
            
            logger.info(f"Bet placed: {bet_id} - {bet.player_name or bet.team_name} "
                       f"{bet.bet_type} @ {bet.odds}")
            
            return bet
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error placing bet: {e}")
            raise
    
    def settle_bet(self, bet_id: str, result_data: dict, bankroll_state: dict) -> SportsBet:
        """
        Settle a bet with actual outcome (bet record remains locked)
        
        Args:
            bet_id: Bet identifier
            result_data: Dict with actual_result, closing_line, closing_odds
            bankroll_state: Updated bankroll state
            
        Returns:
            Updated SportsBet object
        """
        try:
            bet = SportsBet.query.filter_by(bet_id=bet_id).first()
            
            if not bet:
                raise ValueError(f"Bet {bet_id} not found")
            
            if bet.bet_status != 'pending':
                raise ValueError(f"Bet {bet_id} already settled as {bet.bet_status}")
            
            # Update outcome fields (only fields allowed to change)
            bet.actual_result = result_data.get('actual_result')
            bet.closing_line = result_data.get('closing_line')
            bet.closing_odds = result_data.get('closing_odds')
            bet.settled_at = datetime.utcnow()
            
            # Determine win/loss/push
            if result_data.get('status'):
                bet.bet_status = result_data['status']
            else:
                bet.bet_status = self._determine_outcome(bet, result_data['actual_result'])
            
            # Calculate financials
            if bet.bet_status == 'won':
                decimal_odds = self._american_to_decimal(bet.odds)
                bet.payout = bet.stake * decimal_odds
                bet.profit = bet.payout - bet.stake
            elif bet.bet_status == 'lost':
                bet.payout = 0
                bet.profit = -bet.stake
            else:  # push or cancelled
                bet.payout = bet.stake
                bet.profit = 0
            
            bet.roi = (bet.profit / bet.stake * 100) if bet.stake > 0 else 0
            
            # Calculate CLV
            if bet.closing_line and bet.market_line:
                bet.clv = self._calculate_clv(bet)
            
            # Check if edge realized
            if bet.predicted_value and bet.actual_result:
                bet.prediction_error = abs(bet.predicted_value - bet.actual_result)
                bet.edge_realized = self._check_edge_realized(bet)
            
            # Log bankroll snapshot
            self._log_bankroll_snapshot(
                bankroll_state,
                event_type='bet_settled',
                event_id=bet_id
            )
            
            db.session.commit()
            
            logger.info(f"Bet settled: {bet_id} - {bet.bet_status.upper()} - "
                       f"Profit: ${bet.profit:.2f}")
            
            return bet
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error settling bet: {e}")
            raise
    
    def _determine_outcome(self, bet: SportsBet, actual_result: float) -> str:
        """Determine win/loss/push based on bet type and actual result"""
        if bet.bet_type == 'player_prop':
            if bet.bet_side == 'over':
                if actual_result > bet.market_line:
                    return 'won'
                elif actual_result == bet.market_line:
                    return 'push'
                else:
                    return 'lost'
            elif bet.bet_side == 'under':
                if actual_result < bet.market_line:
                    return 'won'
                elif actual_result == bet.market_line:
                    return 'push'
                else:
                    return 'lost'
        
        # Default to manual entry needed
        return 'pending'
    
    def _american_to_decimal(self, american_odds: int) -> float:
        """Convert American odds to decimal"""
        if american_odds > 0:
            return (american_odds / 100) + 1
        else:
            return (100 / abs(american_odds)) + 1
    
    def _calculate_clv(self, bet: SportsBet) -> float:
        """
        Calculate Closing Line Value
        Positive CLV = we bet better line than closing
        """
        if not bet.closing_line or not bet.market_line:
            return 0
        
        if bet.bet_side == 'over':
            # Lower line is better for over (easier to hit)
            clv = bet.closing_line - bet.market_line
        elif bet.bet_side == 'under':
            # Higher line is better for under
            clv = bet.market_line - bet.closing_line
        else:
            clv = 0
        
        return round(clv, 2)
    
    def _check_edge_realized(self, bet: SportsBet) -> bool:
        """Check if predicted edge was realized"""
        if not bet.predicted_value or not bet.actual_result or not bet.market_line:
            return False
        
        # Did prediction match direction correctly?
        predicted_over = bet.predicted_value > bet.market_line
        actual_over = bet.actual_result > bet.market_line
        
        return predicted_over == actual_over
    
    def _log_bankroll_snapshot(self, bankroll_state: dict, event_type: str, event_id: str):
        """Log bankroll state snapshot"""
        snapshot = BankrollHistory(
            balance=bankroll_state.get('current_bankroll'),
            allocated_capital=bankroll_state.get('allocated_capital', 0),
            available_capital=bankroll_state.get('available_capital'),
            peak_balance=bankroll_state.get('peak_bankroll'),
            total_roi=bankroll_state.get('total_roi', 0),
            current_drawdown=bankroll_state.get('current_drawdown', 0),
            total_bets=bankroll_state.get('total_bets', 0),
            consecutive_losses=bankroll_state.get('consecutive_losses', 0),
            is_halted=bankroll_state.get('is_halted', False),
            event_type=event_type,
            event_id=event_id
        )
        db.session.add(snapshot)
    
    def get_pending_bets(self) -> list:
        """Get all pending bets"""
        bets = SportsBet.query.filter_by(bet_status='pending').order_by(SportsBet.game_date).all()
        return [bet.to_dict() for bet in bets]
    
    def get_bet_history(self, sport: str = None, limit: int = 100) -> list:
        """Get bet history"""
        query = SportsBet.query
        
        if sport:
            query = query.filter_by(sport=sport)
        
        bets = query.order_by(SportsBet.placed_at.desc()).limit(limit).all()
        return [bet.to_dict() for bet in bets]
    
    def get_bet(self, bet_id: str) -> dict:
        """Get specific bet"""
        bet = SportsBet.query.filter_by(bet_id=bet_id).first()
        return bet.to_dict() if bet else None
    
    def get_bankroll_history(self, limit: int = 100) -> list:
        """Get bankroll history"""
        snapshots = BankrollHistory.query.order_by(
            BankrollHistory.timestamp.desc()
        ).limit(limit).all()
        
        return [snapshot.to_dict() for snapshot in snapshots]
    
    def get_recent_performance(self, days: int = 30) -> dict:
        """Get performance summary for recent period"""
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        bets = SportsBet.query.filter(
            SportsBet.settled_at >= cutoff_date,
            SportsBet.bet_status.in_(['won', 'lost', 'push'])
        ).all()
        
        if not bets:
            return {
                'period_days': days,
                'total_bets': 0,
                'message': 'No settled bets in period'
            }
        
        total_staked = sum(b.stake for b in bets)
        total_profit = sum(b.profit for b in bets)
        wins = len([b for b in bets if b.bet_status == 'won'])
        losses = len([b for b in bets if b.bet_status == 'lost'])
        pushes = len([b for b in bets if b.bet_status == 'push'])
        
        win_rate = wins / (wins + losses) if (wins + losses) > 0 else 0
        roi = (total_profit / total_staked * 100) if total_staked > 0 else 0
        
        positive_clv = len([b for b in bets if b.clv and b.clv > 0])
        clv_rate = positive_clv / len(bets) if bets else 0
        
        return {
            'period_days': days,
            'total_bets': len(bets),
            'wins': wins,
            'losses': losses,
            'pushes': pushes,
            'win_rate': round(win_rate * 100, 2),
            'total_staked': round(total_staked, 2),
            'total_profit': round(total_profit, 2),
            'roi': round(roi, 2),
            'positive_clv_rate': round(clv_rate * 100, 2)
        }


if __name__ == "__main__":
    # Would need Flask app context to test
    print("BetTracker module loaded successfully")

