"""
Backtesting Engine
Historical performance simulation and strategy validation
"""

import numpy as np
import pandas as pd
from core.models import db, Cryptocurrency, NameAnalysis, PriceHistory
from datetime import datetime, timedelta
from analyzers.confidence_scorer import ConfidenceScorer
import logging

logger = logging.getLogger(__name__)


class Backtester:
    """Backtest trading strategies based on name metrics"""
    
    def __init__(self):
        self.scorer = ConfidenceScorer()
    
    def run_backtest(self, start_date=None, end_date=None, strategy='score_based', params=None):
        """
        Run historical backtest
        
        Args:
            start_date: Start date for backtest
            end_date: End date for backtest
            strategy: Strategy type ('score_based', 'name_type', 'syllable')
            params: Strategy-specific parameters
        
        Returns: dict with backtest results
        """
        try:
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=365)
            if not end_date:
                end_date = datetime.utcnow()
            
            params = params or {}
            
            # Get all cryptocurrencies with data
            cryptos = Cryptocurrency.query.all()
            
            trades = []
            for crypto in cryptos:
                analysis = NameAnalysis.query.filter_by(crypto_id=crypto.id).first()
                if not analysis:
                    continue
                
                # Get price history
                price_data = PriceHistory.query.filter_by(crypto_id=crypto.id).first()
                if not price_data or price_data.price_1yr_change is None:
                    continue
                
                # Apply strategy
                trade = self._apply_strategy(crypto, analysis, price_data, strategy, params)
                if trade:
                    trades.append(trade)
            
            # Calculate metrics
            metrics = self._calculate_metrics(trades)
            
            # Generate equity curve
            equity_curve = self._generate_equity_curve(trades)
            
            return {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'strategy': strategy,
                'params': params,
                'trades': trades,
                'metrics': metrics,
                'equity_curve': equity_curve
            }
        
        except Exception as e:
            logger.error(f"Backtest error: {e}")
            return None
    
    def _apply_strategy(self, crypto, analysis, price_data, strategy, params):
        """Apply trading strategy to determine trade"""
        
        if strategy == 'score_based':
            # Score-based strategy
            score_data = self.scorer.score_cryptocurrency(crypto.id)
            if not score_data:
                return None
            
            min_score = params.get('min_score', 70)
            if score_data['score'] >= min_score and score_data['signal'] == 'BUY':
                return {
                    'crypto': crypto.name,
                    'symbol': crypto.symbol,
                    'entry_signal': 'BUY',
                    'score': score_data['score'],
                    'return_1yr': price_data.price_1yr_change or 0,
                    'strategy': strategy
                }
        
        elif strategy == 'name_type':
            # Name type strategy
            preferred_types = params.get('types', ['tech', 'invented', 'portmanteau'])
            if analysis.name_type in preferred_types:
                return {
                    'crypto': crypto.name,
                    'symbol': crypto.symbol,
                    'entry_signal': 'BUY',
                    'name_type': analysis.name_type,
                    'return_1yr': price_data.price_1yr_change or 0,
                    'strategy': strategy
                }
        
        elif strategy == 'syllable':
            # Syllable-based strategy
            optimal_syllables = params.get('syllables', [2, 3])
            if analysis.syllable_count in optimal_syllables:
                memorability_threshold = params.get('memorability_min', 70)
                if (analysis.memorability_score or 0) >= memorability_threshold:
                    return {
                        'crypto': crypto.name,
                        'symbol': crypto.symbol,
                        'entry_signal': 'BUY',
                        'syllables': analysis.syllable_count,
                        'memorability': analysis.memorability_score,
                        'return_1yr': price_data.price_1yr_change or 0,
                        'strategy': strategy
                    }
        
        return None
    
    def _calculate_metrics(self, trades):
        """Calculate backtest performance metrics"""
        if not trades:
            return {}
        
        returns = [t['return_1yr'] for t in trades]
        positive_returns = [r for r in returns if r > 0]
        negative_returns = [r for r in returns if r < 0]
        
        total_return = np.sum(returns)
        avg_return = np.mean(returns)
        median_return = np.median(returns)
        
        win_rate = (len(positive_returns) / len(returns) * 100) if returns else 0
        
        # Sharpe ratio (simplified, assuming risk-free rate = 0)
        sharpe = (avg_return / np.std(returns)) if np.std(returns) > 0 else 0
        
        # Sortino ratio (downside deviation)
        downside_returns = [r for r in returns if r < 0]
        downside_std = np.std(downside_returns) if downside_returns else 1
        sortino = avg_return / downside_std if downside_std > 0 else 0
        
        # Maximum drawdown
        max_drawdown = abs(min(returns)) if returns else 0
        
        # Profit factor
        gross_profit = sum(positive_returns) if positive_returns else 0
        gross_loss = abs(sum(negative_returns)) if negative_returns else 1
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        return {
            'total_trades': len(trades),
            'total_return_pct': round(total_return, 2),
            'avg_return_pct': round(avg_return, 2),
            'median_return_pct': round(median_return, 2),
            'win_rate_pct': round(win_rate, 2),
            'sharpe_ratio': round(sharpe, 2),
            'sortino_ratio': round(sortino, 2),
            'max_drawdown_pct': round(max_drawdown, 2),
            'profit_factor': round(profit_factor, 2),
            'winners': len(positive_returns),
            'losers': len(negative_returns)
        }
    
    def _generate_equity_curve(self, trades):
        """Generate equity curve data"""
        if not trades:
            return []
        
        equity = [100]  # Start with $100
        cumulative_return = 0
        
        for i, trade in enumerate(trades):
            cumulative_return += trade['return_1yr']
            equity.append(100 * (1 + cumulative_return / 100))
        
        return [{'trade': i, 'equity': round(eq, 2)} for i, eq in enumerate(equity)]
    
    def statistical_significance(self, strategy_results):
        """Test if strategy results are statistically significant"""
        try:
            from scipy import stats
            
            returns = [t['return_1yr'] for t in strategy_results.get('trades', [])]
            if len(returns) < 10:
                return {'significant': False, 'reason': 'Insufficient data'}
            
            # T-test against zero (market neutral)
            t_stat, p_value = stats.ttest_1samp(returns, 0)
            
            significant = p_value < 0.05
            
            return {
                'significant': significant,
                't_statistic': round(t_stat, 4),
                'p_value': round(p_value, 4),
                'confidence_level': '95%',
                'interpretation': 'Statistically significant' if significant else 'Not statistically significant'
            }
        
        except ImportError:
            logger.warning("scipy not available for statistical tests")
            return {'significant': None, 'reason': 'scipy not installed'}
        except Exception as e:
            logger.error(f"Statistical significance error: {e}")
            return {'significant': None, 'error': str(e)}
    
    def compare_strategies(self, strategies_list):
        """Compare multiple strategies"""
        results = []
        
        for strategy_config in strategies_list:
            strategy_type = strategy_config.get('type')
            params = strategy_config.get('params', {})
            
            backtest_result = self.run_backtest(strategy=strategy_type, params=params)
            if backtest_result:
                results.append({
                    'strategy': strategy_type,
                    'params': params,
                    'metrics': backtest_result['metrics']
                })
        
        # Rank by Sharpe ratio
        results.sort(key=lambda x: x['metrics'].get('sharpe_ratio', 0), reverse=True)
        
        return results

