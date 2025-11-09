"""
Betting Backtester
Validate betting strategies on historical athlete data
Tests if name pattern correlations translate to profitable betting edge
"""

import sqlite3
from pathlib import Path
from typing import Dict, List, Optional
import numpy as np
import logging
from analyzers.sports_betting_analyzer import SportsBettingAnalyzer
from analyzers.betting_ev_calculator import BettingEVCalculator
from utils.betting_bankroll_manager import BettingBankrollManager

logger = logging.getLogger(__name__)


class BettingBacktester:
    """Backtest betting strategies on historical data"""
    
    def __init__(self, initial_bankroll: float = 10000):
        """Initialize backtester"""
        self.betting_analyzer = SportsBettingAnalyzer()
        self.ev_calculator = BettingEVCalculator()
        self.initial_bankroll = initial_bankroll
        
        # Results tracking
        self.results = {
            'bets': [],
            'bankroll_history': [],
            'performance_by_sport': {}
        }
    
    def run_backtest(self, sport: str, min_score: float = 60,
                    min_confidence: float = 50, min_ev: float = 0.03) -> Dict:
        """
        Run backtest on historical athlete data
        
        Args:
            sport: 'football', 'basketball', or 'baseball'
            min_score: Minimum name pattern score threshold
            min_confidence: Minimum confidence threshold
            min_ev: Minimum expected value threshold
            
        Returns:
            Backtest results with performance metrics
        """
        logger.info(f"Starting backtest for {sport}")
        
        # Initialize bankroll manager
        bankroll = BettingBankrollManager(
            initial_bankroll=self.initial_bankroll,
            max_bet_percentage=0.05,
            max_simultaneous_exposure=0.25
        )
        
        # Load athlete data
        athletes = self.betting_analyzer.get_athlete_data(sport, limit=2000)
        
        if not athletes:
            return {'error': f'No athlete data found for {sport}'}
        
        # Split into training and test sets (chronological if possible)
        # For now, use random split to simulate train/test
        np.random.seed(42)
        np.random.shuffle(athletes)
        
        train_size = int(len(athletes) * 0.8)
        test_athletes = athletes[train_size:]
        
        logger.info(f"Backtesting on {len(test_athletes)} athletes")
        
        # Simulate betting on test set
        bets_placed = []
        
        for athlete in test_athletes:
            # Calculate betting score
            linguistic_features = {
                'syllables': athlete['syllables'],
                'harshness': athlete['harshness'],
                'memorability': athlete['memorability'],
                'length': athlete['length']
            }
            
            score_result = self.betting_analyzer.calculate_player_score(linguistic_features, sport)
            
            # Filter by thresholds
            if (score_result['overall_score'] < min_score or 
                score_result['confidence'] < min_confidence):
                continue
            
            # Simulate prop bet
            # Predicted value vs "market line" (use actual success as proxy)
            predicted_value = score_result['overall_score']
            market_line = 50  # Neutral line
            actual_result = athlete['actual_success']
            
            # Calculate EV
            edge = (predicted_value - market_line) / 100
            
            if abs(edge) < min_ev:
                continue
            
            # Determine bet side
            if predicted_value > market_line:
                bet_side = 'over'
                ev_result = self.ev_calculator.calculate_prop_ev(
                    predicted_value=predicted_value,
                    market_line=market_line,
                    over_odds=-110,
                    under_odds=-110,
                    confidence=score_result['confidence']
                )
                best_ev = ev_result['over']['ev']
            else:
                bet_side = 'under'
                ev_result = self.ev_calculator.calculate_prop_ev(
                    predicted_value=predicted_value,
                    market_line=market_line,
                    over_odds=-110,
                    under_odds=-110,
                    confidence=score_result['confidence']
                )
                best_ev = ev_result['under']['ev']
            
            if best_ev < min_ev:
                continue
            
            # Calculate bet size
            bet_size_result = bankroll.calculate_bet_size(
                edge=abs(edge),
                odds=-110,
                confidence=score_result['confidence'],
                ev=best_ev
            )
            
            if not bet_size_result['can_bet'] or bet_size_result['recommended_bet'] == 0:
                continue
            
            bet_amount = bet_size_result['recommended_bet']
            
            # Allocate bet
            bet_id = f"backtest_{len(bets_placed)}"
            if not bankroll.allocate_bet(bet_amount, bet_id):
                continue
            
            # Determine outcome
            if bet_side == 'over':
                won = actual_result > market_line
            else:
                won = actual_result < market_line
            
            # Settle bet
            if won:
                payout = bet_amount * 1.909  # -110 odds = 1.909 decimal
                result = 'win'
            else:
                payout = 0
                result = 'loss'
            
            settlement = bankroll.settle_bet(bet_amount, result, payout)
            
            # Record bet
            bet_record = {
                'athlete_name': athlete['name'],
                'sport': sport,
                'predicted_value': predicted_value,
                'market_line': market_line,
                'actual_result': actual_result,
                'bet_side': bet_side,
                'bet_amount': bet_amount,
                'odds': -110,
                'result': result,
                'profit': settlement['result'] == 'win' and (payout - bet_amount) or -bet_amount,
                'bankroll_after': settlement['current_bankroll'],
                'linguistic_score': score_result['overall_score'],
                'confidence': score_result['confidence'],
                'ev': best_ev
            }
            
            bets_placed.append(bet_record)
        
        # Calculate performance metrics
        performance = self._calculate_backtest_performance(bets_placed, bankroll)
        
        logger.info(f"Backtest complete: {len(bets_placed)} bets, "
                   f"ROI: {performance['roi']:.2f}%, "
                   f"Win Rate: {performance['win_rate']:.2f}%")
        
        return {
            'sport': sport,
            'parameters': {
                'min_score': min_score,
                'min_confidence': min_confidence,
                'min_ev': min_ev,
                'initial_bankroll': self.initial_bankroll
            },
            'dataset': {
                'total_athletes': len(athletes),
                'test_athletes': len(test_athletes),
                'bets_placed': len(bets_placed),
                'bet_rate': round(len(bets_placed) / len(test_athletes) * 100, 2)
            },
            'performance': performance,
            'sample_bets': bets_placed[:10]  # First 10 bets as sample
        }
    
    def _calculate_backtest_performance(self, bets: List[Dict], 
                                       bankroll: BettingBankrollManager) -> Dict:
        """Calculate performance metrics from backtest"""
        if not bets:
            return {
                'error': 'No bets placed',
                'total_bets': 0
            }
        
        total_bets = len(bets)
        wins = len([b for b in bets if b['result'] == 'win'])
        losses = len([b for b in bets if b['result'] == 'loss'])
        
        win_rate = wins / total_bets if total_bets > 0 else 0
        
        total_staked = sum(b['bet_amount'] for b in bets)
        total_profit = sum(b['profit'] for b in bets)
        roi = (total_profit / total_staked * 100) if total_staked > 0 else 0
        
        # Bankroll metrics
        final_bankroll = bankroll.current_bankroll
        total_return = ((final_bankroll - self.initial_bankroll) / self.initial_bankroll * 100)
        
        # Risk metrics
        profits = [b['profit'] for b in bets]
        sharpe = self._calculate_sharpe(profits)
        max_dd = self._calculate_max_drawdown_from_bets(bets)
        
        # EV validation
        avg_ev = np.mean([b['ev'] for b in bets])
        avg_confidence = np.mean([b['confidence'] for b in bets])
        
        # Check if edge was real
        edge_validated = (roi > 0 and win_rate > 0.524)  # 52.4% = breakeven at -110
        
        return {
            'total_bets': total_bets,
            'wins': wins,
            'losses': losses,
            'win_rate': round(win_rate * 100, 2),
            'total_staked': round(total_staked, 2),
            'total_profit': round(total_profit, 2),
            'roi': round(roi, 2),
            'final_bankroll': round(final_bankroll, 2),
            'total_return': round(total_return, 2),
            'sharpe_ratio': round(sharpe, 3),
            'max_drawdown': round(max_dd, 2),
            'avg_ev': round(avg_ev, 4),
            'avg_confidence': round(avg_confidence, 2),
            'edge_validated': edge_validated,
            'profitable': roi > 0
        }
    
    def _calculate_sharpe(self, profits: List[float]) -> float:
        """Calculate Sharpe ratio"""
        if len(profits) < 2:
            return 0
        
        mean = np.mean(profits)
        std = np.std(profits)
        
        if std == 0:
            return 0
        
        return (mean / std) * np.sqrt(len(profits))
    
    def _calculate_max_drawdown_from_bets(self, bets: List[Dict]) -> float:
        """Calculate max drawdown from bet history"""
        cumulative = []
        running_total = 0
        
        for bet in bets:
            running_total += bet['profit']
            cumulative.append(running_total)
        
        if not cumulative:
            return 0
        
        peak = cumulative[0]
        max_dd = 0
        
        for value in cumulative:
            if value > peak:
                peak = value
            if peak > 0:
                dd = (peak - value) / peak * 100
                max_dd = max(max_dd, dd)
        
        return max_dd
    
    def run_comprehensive_backtest(self) -> Dict:
        """
        Run backtest across all sports with multiple parameter combinations
        """
        results = {
            'summary': {},
            'by_sport': {},
            'best_configurations': []
        }
        
        # Parameter grid
        param_grid = [
            {'min_score': 60, 'min_confidence': 50, 'min_ev': 0.03},
            {'min_score': 65, 'min_confidence': 55, 'min_ev': 0.04},
            {'min_score': 70, 'min_confidence': 60, 'min_ev': 0.05},
        ]
        
        all_configs = []
        
        for sport in ['football', 'basketball', 'baseball']:
            logger.info(f"Backtesting {sport}...")
            sport_results = []
            
            for params in param_grid:
                result = self.run_backtest(
                    sport=sport,
                    min_score=params['min_score'],
                    min_confidence=params['min_confidence'],
                    min_ev=params['min_ev']
                )
                
                if 'error' not in result:
                    sport_results.append(result)
                    all_configs.append({
                        'sport': sport,
                        'params': params,
                        'roi': result['performance']['roi'],
                        'win_rate': result['performance']['win_rate'],
                        'total_bets': result['dataset']['bets_placed'],
                        'edge_validated': result['performance']['edge_validated']
                    })
            
            results['by_sport'][sport] = sport_results
        
        # Find best configurations
        profitable_configs = [c for c in all_configs if c['roi'] > 0]
        profitable_configs.sort(key=lambda x: x['roi'], reverse=True)
        
        results['best_configurations'] = profitable_configs[:5]
        
        # Overall summary
        if all_configs:
            results['summary'] = {
                'total_configurations_tested': len(all_configs),
                'profitable_configurations': len(profitable_configs),
                'success_rate': round(len(profitable_configs) / len(all_configs) * 100, 2),
                'best_roi': profitable_configs[0]['roi'] if profitable_configs else 0,
                'avg_roi': round(np.mean([c['roi'] for c in all_configs]), 2),
                'best_sport': profitable_configs[0]['sport'] if profitable_configs else None
            }
        
        return results


if __name__ == "__main__":
    # Test backtester
    logging.basicConfig(level=logging.INFO)
    
    backtester = BettingBacktester(initial_bankroll=10000)
    
    print("\n=== RUNNING FOOTBALL BACKTEST ===")
    result = backtester.run_backtest(
        sport='football',
        min_score=60,
        min_confidence=50,
        min_ev=0.03
    )
    
    if 'error' not in result:
        print(f"\nSport: {result['sport'].upper()}")
        print(f"Bets Placed: {result['dataset']['bets_placed']}")
        print(f"Win Rate: {result['performance']['win_rate']}%")
        print(f"ROI: {result['performance']['roi']}%")
        print(f"Final Bankroll: ${result['performance']['final_bankroll']}")
        print(f"Total Return: {result['performance']['total_return']}%")
        print(f"Edge Validated: {result['performance']['edge_validated']}")
        print(f"Profitable: {result['performance']['profitable']}")
    else:
        print(f"Error: {result['error']}")

