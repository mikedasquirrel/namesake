"""
Betting Performance Analyzer
Calculate ROI, win rate, CLV, and other performance metrics
"""

from core.models import db, SportsBet, BettingPerformance, BankrollHistory
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import numpy as np
import logging

logger = logging.getLogger(__name__)


class BettingPerformanceAnalyzer:
    """Analyze betting performance across various dimensions"""
    
    def __init__(self):
        """Initialize performance analyzer"""
        pass
    
    def calculate_overall_performance(self) -> Dict:
        """Calculate overall performance across all bets"""
        return self._calculate_performance_metrics(
            sport=None,
            market_type=None,
            time_period='all_time'
        )
    
    def calculate_sport_performance(self, sport: str) -> Dict:
        """Calculate performance for specific sport"""
        return self._calculate_performance_metrics(
            sport=sport,
            market_type=None,
            time_period='all_time'
        )
    
    def calculate_market_performance(self, market_type: str) -> Dict:
        """Calculate performance for specific market type"""
        return self._calculate_performance_metrics(
            sport=None,
            market_type=market_type,
            time_period='all_time'
        )
    
    def calculate_recent_performance(self, days: int = 30) -> Dict:
        """Calculate performance for recent period"""
        return self._calculate_performance_metrics(
            sport=None,
            market_type=None,
            time_period=f'last_{days}_days',
            days=days
        )
    
    def _calculate_performance_metrics(self, sport: Optional[str] = None,
                                       market_type: Optional[str] = None,
                                       time_period: str = 'all_time',
                                       days: Optional[int] = None) -> Dict:
        """
        Calculate comprehensive performance metrics
        
        Args:
            sport: Filter by sport
            market_type: Filter by market type
            time_period: Time period label
            days: Days to look back (if applicable)
            
        Returns:
            Performance metrics dict
        """
        # Build query
        query = SportsBet.query.filter(
            SportsBet.bet_status.in_(['won', 'lost', 'push'])
        )
        
        if sport:
            query = query.filter_by(sport=sport)
        
        if market_type:
            query = query.filter_by(market_type=market_type)
        
        if days:
            cutoff = datetime.utcnow() - timedelta(days=days)
            query = query.filter(SportsBet.settled_at >= cutoff)
        
        bets = query.all()
        
        if not bets:
            return {
                'error': 'No settled bets found',
                'sport': sport,
                'market_type': market_type,
                'time_period': time_period
            }
        
        # Calculate metrics
        total_bets = len(bets)
        total_staked = sum(b.stake for b in bets)
        total_returned = sum(b.payout for b in bets if b.payout)
        
        wins = [b for b in bets if b.bet_status == 'won']
        losses = [b for b in bets if b.bet_status == 'lost']
        pushes = [b for b in bets if b.bet_status == 'push']
        
        win_count = len(wins)
        loss_count = len(losses)
        push_count = len(pushes)
        
        # Win rate (excluding pushes)
        decisive_bets = win_count + loss_count
        win_rate = win_count / decisive_bets if decisive_bets > 0 else 0
        
        # Profitability
        net_profit = sum(b.profit for b in bets if b.profit)
        roi = (net_profit / total_staked * 100) if total_staked > 0 else 0
        avg_profit = net_profit / total_bets if total_bets > 0 else 0
        
        # Expected value tracking
        evs = [b.expected_value for b in bets if b.expected_value]
        avg_ev = np.mean(evs) if evs else 0
        
        # CLV tracking
        clvs = [b.clv for b in bets if b.clv is not None]
        avg_clv = np.mean(clvs) if clvs else 0
        positive_clv_count = len([c for c in clvs if c > 0])
        positive_clv_rate = positive_clv_count / len(clvs) if clvs else 0
        
        # Risk metrics
        profits = [b.profit for b in bets if b.profit is not None]
        sharpe_ratio = self._calculate_sharpe_ratio(profits) if len(profits) > 1 else 0
        max_drawdown = self._calculate_max_drawdown(bets)
        longest_streak = self._calculate_longest_losing_streak(bets)
        largest_loss = min(profits) if profits else 0
        
        # Bet sizing
        stakes = [b.stake for b in bets]
        avg_bet_size = np.mean(stakes) if stakes else 0
        bet_percentages = [b.bet_percentage for b in bets if b.bet_percentage]
        avg_bet_percentage = np.mean(bet_percentages) if bet_percentages else 0
        
        # Last bet
        last_bet = max(bets, key=lambda b: b.settled_at) if bets else None
        
        return {
            'sport': sport,
            'market_type': market_type,
            'time_period': time_period,
            'volume': {
                'total_bets': total_bets,
                'total_staked': round(total_staked, 2),
                'total_returned': round(total_returned, 2)
            },
            'record': {
                'wins': win_count,
                'losses': loss_count,
                'pushes': push_count,
                'win_rate': round(win_rate * 100, 2)
            },
            'profitability': {
                'net_profit': round(net_profit, 2),
                'roi': round(roi, 2),
                'avg_profit_per_bet': round(avg_profit, 2)
            },
            'expected_value': {
                'avg_ev': round(avg_ev, 4),
                'avg_clv': round(avg_clv, 2),
                'positive_clv_rate': round(positive_clv_rate * 100, 2)
            },
            'risk': {
                'sharpe_ratio': round(sharpe_ratio, 3),
                'max_drawdown': round(max_drawdown, 2),
                'longest_losing_streak': longest_streak,
                'largest_loss': round(largest_loss, 2)
            },
            'bet_sizing': {
                'avg_bet_size': round(avg_bet_size, 2),
                'avg_bet_percentage': round(avg_bet_percentage, 2)
            },
            'last_bet_date': last_bet.settled_at.isoformat() if last_bet else None
        }
    
    def _calculate_sharpe_ratio(self, profits: List[float]) -> float:
        """
        Calculate Sharpe ratio (risk-adjusted return)
        Assumes zero risk-free rate for simplicity
        """
        if len(profits) < 2:
            return 0
        
        mean_profit = np.mean(profits)
        std_profit = np.std(profits)
        
        if std_profit == 0:
            return 0
        
        # Annualized (assuming ~250 betting days per year)
        sharpe = (mean_profit / std_profit) * np.sqrt(250)
        
        return sharpe
    
    def _calculate_max_drawdown(self, bets: List[SportsBet]) -> float:
        """Calculate maximum drawdown percentage"""
        if not bets:
            return 0
        
        # Sort by settled date
        sorted_bets = sorted(bets, key=lambda b: b.settled_at)
        
        # Calculate cumulative profit
        cumulative = []
        running_total = 0
        for bet in sorted_bets:
            if bet.profit is not None:
                running_total += bet.profit
                cumulative.append(running_total)
        
        if not cumulative:
            return 0
        
        # Find max drawdown
        peak = cumulative[0]
        max_dd = 0
        
        for value in cumulative:
            if value > peak:
                peak = value
            dd = ((peak - value) / peak * 100) if peak > 0 else 0
            max_dd = max(max_dd, dd)
        
        return max_dd
    
    def _calculate_longest_losing_streak(self, bets: List[SportsBet]) -> int:
        """Calculate longest consecutive losing streak"""
        if not bets:
            return 0
        
        sorted_bets = sorted(bets, key=lambda b: b.settled_at)
        
        current_streak = 0
        max_streak = 0
        
        for bet in sorted_bets:
            if bet.bet_status == 'lost':
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        
        return max_streak
    
    def get_performance_by_dimension(self, dimension: str) -> List[Dict]:
        """
        Get performance broken down by dimension
        
        Args:
            dimension: 'sport', 'market_type', 'bet_type'
            
        Returns:
            List of performance metrics for each dimension value
        """
        results = []
        
        if dimension == 'sport':
            sports = db.session.query(SportsBet.sport).distinct().all()
            for (sport,) in sports:
                if sport:
                    perf = self.calculate_sport_performance(sport)
                    if 'error' not in perf:
                        results.append(perf)
        
        elif dimension == 'market_type':
            markets = db.session.query(SportsBet.market_type).distinct().all()
            for (market,) in markets:
                if market:
                    perf = self.calculate_market_performance(market)
                    if 'error' not in perf:
                        results.append(perf)
        
        elif dimension == 'bet_type':
            bet_types = db.session.query(SportsBet.bet_type).distinct().all()
            for (bet_type,) in bet_types:
                if bet_type:
                    perf = self._calculate_performance_metrics(
                        sport=None,
                        market_type=None,
                        time_period='all_time'
                    )
                    if 'error' not in perf:
                        perf['bet_type'] = bet_type
                        results.append(perf)
        
        # Sort by ROI
        results.sort(key=lambda x: x['profitability']['roi'], reverse=True)
        
        return results
    
    def get_bankroll_growth(self, days: int = 90) -> Dict:
        """Get bankroll growth over time"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        snapshots = BankrollHistory.query.filter(
            BankrollHistory.timestamp >= cutoff
        ).order_by(BankrollHistory.timestamp).all()
        
        if not snapshots:
            return {
                'error': 'No bankroll history found',
                'period_days': days
            }
        
        # Extract time series
        timestamps = [s.timestamp.isoformat() for s in snapshots]
        balances = [s.balance for s in snapshots]
        rois = [s.total_roi for s in snapshots if s.total_roi is not None]
        
        initial_balance = balances[0] if balances else 0
        current_balance = balances[-1] if balances else 0
        growth = ((current_balance - initial_balance) / initial_balance * 100) if initial_balance > 0 else 0
        
        return {
            'period_days': days,
            'initial_balance': round(initial_balance, 2),
            'current_balance': round(current_balance, 2),
            'growth_percentage': round(growth, 2),
            'peak_balance': round(max(balances), 2) if balances else 0,
            'timestamps': timestamps,
            'balances': balances,
            'total_snapshots': len(snapshots)
        }
    
    def save_performance_summary(self):
        """Save performance summaries to database for quick access"""
        try:
            # Delete old summaries
            BettingPerformance.query.delete()
            
            # Overall performance
            overall = self.calculate_overall_performance()
            if 'error' not in overall:
                self._save_performance_record(overall)
            
            # By sport
            for sport in ['football', 'basketball', 'baseball']:
                perf = self.calculate_sport_performance(sport)
                if 'error' not in perf:
                    self._save_performance_record(perf)
            
            # Recent periods
            for days in [30, 90]:
                perf = self.calculate_recent_performance(days)
                if 'error' not in perf:
                    self._save_performance_record(perf)
            
            db.session.commit()
            logger.info("Performance summaries saved")
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error saving performance summaries: {e}")
    
    def _save_performance_record(self, perf: Dict):
        """Save performance dict to database"""
        record = BettingPerformance(
            sport=perf.get('sport'),
            market_type=perf.get('market_type'),
            time_period=perf['time_period'],
            total_bets=perf['volume']['total_bets'],
            total_staked=perf['volume']['total_staked'],
            total_returned=perf['volume']['total_returned'],
            wins=perf['record']['wins'],
            losses=perf['record']['losses'],
            pushes=perf['record']['pushes'],
            win_rate=perf['record']['win_rate'] / 100,
            net_profit=perf['profitability']['net_profit'],
            roi=perf['profitability']['roi'],
            avg_profit_per_bet=perf['profitability']['avg_profit_per_bet'],
            avg_ev=perf['expected_value']['avg_ev'],
            avg_clv=perf['expected_value']['avg_clv'],
            positive_clv_rate=perf['expected_value']['positive_clv_rate'] / 100,
            sharpe_ratio=perf['risk']['sharpe_ratio'],
            max_drawdown=perf['risk']['max_drawdown'],
            longest_losing_streak=perf['risk']['longest_losing_streak'],
            largest_loss=perf['risk']['largest_loss'],
            avg_bet_size=perf['bet_sizing']['avg_bet_size'],
            avg_bet_percentage=perf['bet_sizing']['avg_bet_percentage']
        )
        db.session.add(record)


if __name__ == "__main__":
    print("BettingPerformanceAnalyzer module loaded successfully")

