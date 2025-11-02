"""
Risk Analysis Module
VaR, CVaR, Monte Carlo simulation, and stress testing
"""

import numpy as np
from core.models import Cryptocurrency, NameAnalysis, PriceHistory
import logging

logger = logging.getLogger(__name__)


class RiskAnalyzer:
    """Comprehensive risk analysis for cryptocurrency investments"""
    
    def calculate_var(self, returns, confidence=0.95):
        """
        Calculate Value at Risk
        
        Args:
            returns: Array of returns
            confidence: Confidence level (default 95%)
        
        Returns: VaR value
        """
        if not returns or len(returns) == 0:
            return 0
        
        returns_array = np.array(returns)
        var = np.percentile(returns_array, (1 - confidence) * 100)
        
        return round(var, 2)
    
    def calculate_cvar(self, returns, confidence=0.95):
        """
        Calculate Conditional Value at Risk (Expected Shortfall)
        
        Args:
            returns: Array of returns
            confidence: Confidence level (default 95%)
        
        Returns: CVaR value
        """
        if not returns or len(returns) == 0:
            return 0
        
        returns_array = np.array(returns)
        var = self.calculate_var(returns, confidence)
        
        # CVaR is the average of returns worse than VaR
        cvar = returns_array[returns_array <= var].mean()
        
        return round(cvar, 2)
    
    def monte_carlo_simulation(self, crypto_id, num_simulations=1000, days=365):
        """
        Run Monte Carlo simulation for a cryptocurrency
        
        Args:
            crypto_id: Cryptocurrency ID
            num_simulations: Number of simulation runs
            days: Days to simulate
        
        Returns: dict with simulation results
        """
        try:
            crypto = Cryptocurrency.query.get(crypto_id)
            analysis = NameAnalysis.query.filter_by(crypto_id=crypto_id).first()
            
            if not crypto or not analysis:
                return None
            
            # Get historical volatility
            price_data = PriceHistory.query.filter_by(crypto_id=crypto_id).first()
            if not price_data:
                return None
            
            # Estimate parameters from historical data
            annual_return = (price_data.price_1yr_change or 0) / 100
            volatility = self._estimate_volatility(crypto_id)
            
            # Run simulations
            final_prices = []
            paths = []
            
            initial_price = crypto.current_price or 100
            
            for sim in range(num_simulations):
                price = initial_price
                path = [price]
                
                for day in range(days):
                    # Geometric Brownian Motion
                    daily_return = np.random.normal(
                        annual_return / 365,
                        volatility / np.sqrt(365)
                    )
                    price *= (1 + daily_return)
                    path.append(price)
                
                final_prices.append(price)
                if sim < 100:  # Store only first 100 paths for visualization
                    paths.append(path)
            
            # Calculate statistics
            final_prices = np.array(final_prices)
            
            return {
                'crypto': crypto.name,
                'symbol': crypto.symbol,
                'initial_price': round(initial_price, 2),
                'num_simulations': num_simulations,
                'days': days,
                'statistics': {
                    'mean_final_price': round(np.mean(final_prices), 2),
                    'median_final_price': round(np.median(final_prices), 2),
                    'min_final_price': round(np.min(final_prices), 2),
                    'max_final_price': round(np.max(final_prices), 2),
                    'std_final_price': round(np.std(final_prices), 2),
                    'percentile_5': round(np.percentile(final_prices, 5), 2),
                    'percentile_25': round(np.percentile(final_prices, 25), 2),
                    'percentile_75': round(np.percentile(final_prices, 75), 2),
                    'percentile_95': round(np.percentile(final_prices), 2)
                },
                'probability_profit': round((final_prices > initial_price).mean() * 100, 2),
                'sample_paths': [[round(p, 2) for p in path] for path in paths[:10]]
            }
        
        except Exception as e:
            logger.error(f"Monte Carlo simulation error: {e}")
            return None
    
    def _estimate_volatility(self, crypto_id):
        """Estimate historical volatility"""
        # Simplified volatility estimation
        # In production, would use actual daily price data
        price_data = PriceHistory.query.filter_by(crypto_id=crypto_id).first()
        
        if not price_data:
            return 0.5  # Default 50% volatility
        
        # Use 1-year change as proxy for volatility
        change_1yr = abs(price_data.price_1yr_change or 50)
        volatility = change_1yr / 100
        
        return max(0.1, min(2.0, volatility))  # Cap between 10% and 200%
    
    def stress_test(self, crypto_id, scenarios=None):
        """
        Run stress tests under various scenarios
        
        Args:
            crypto_id: Cryptocurrency ID
            scenarios: List of scenario dicts with 'name' and 'shock' (% change)
        
        Returns: dict with stress test results
        """
        try:
            crypto = Cryptocurrency.query.get(crypto_id)
            if not crypto or not crypto.current_price:
                return None
            
            if scenarios is None:
                scenarios = [
                    {'name': 'Market Crash (-50%)', 'shock': -50},
                    {'name': 'Severe Correction (-30%)', 'shock': -30},
                    {'name': 'Moderate Decline (-15%)', 'shock': -15},
                    {'name': 'Bull Market (+50%)', 'shock': 50},
                    {'name': 'Strong Rally (+100%)', 'shock': 100}
                ]
            
            results = []
            current_price = crypto.current_price
            
            for scenario in scenarios:
                shock_pct = scenario['shock']
                new_price = current_price * (1 + shock_pct / 100)
                
                results.append({
                    'scenario': scenario['name'],
                    'shock_percent': shock_pct,
                    'original_price': round(current_price, 2),
                    'stressed_price': round(new_price, 2),
                    'loss_or_gain': round(new_price - current_price, 2)
                })
            
            return {
                'crypto': crypto.name,
                'symbol': crypto.symbol,
                'stress_tests': results
            }
        
        except Exception as e:
            logger.error(f"Stress test error: {e}")
            return None
    
    def calculate_portfolio_risk(self, allocations):
        """
        Calculate portfolio-level risk metrics
        
        Args:
            allocations: List of dicts with 'crypto_id' and 'weight'
        
        Returns: dict with portfolio risk metrics
        """
        try:
            if not allocations:
                return None
            
            # Get returns for each crypto
            returns_matrix = []
            weights = []
            
            for alloc in allocations:
                crypto_id = alloc['crypto_id']
                weight = alloc['weight']
                
                price_data = PriceHistory.query.filter_by(crypto_id=crypto_id).first()
                if price_data and price_data.price_1yr_change is not None:
                    returns_matrix.append(price_data.price_1yr_change / 100)
                    weights.append(weight)
            
            if not returns_matrix:
                return None
            
            returns_array = np.array(returns_matrix)
            weights_array = np.array(weights)
            weights_array = weights_array / weights_array.sum()  # Normalize
            
            # Portfolio return
            portfolio_return = np.dot(weights_array, returns_array)
            
            # Portfolio volatility (simplified - assumes independence)
            portfolio_volatility = np.sqrt(np.dot(weights_array**2, returns_array**2))
            
            # Sharpe ratio
            sharpe = portfolio_return / portfolio_volatility if portfolio_volatility > 0 else 0
            
            # VaR and CVaR
            var_95 = self.calculate_var(returns_matrix, 0.95)
            cvar_95 = self.calculate_cvar(returns_matrix, 0.95)
            
            return {
                'portfolio_return_pct': round(portfolio_return * 100, 2),
                'portfolio_volatility_pct': round(portfolio_volatility * 100, 2),
                'sharpe_ratio': round(sharpe, 2),
                'var_95_pct': round(var_95, 2),
                'cvar_95_pct': round(cvar_95, 2),
                'num_assets': len(allocations),
                'allocations': [
                    {'crypto_id': a['crypto_id'], 'weight_pct': round(w * 100, 2)}
                    for a, w in zip(allocations, weights_array)
                ]
            }
        
        except Exception as e:
            logger.error(f"Portfolio risk calculation error: {e}")
            return None
    
    def downside_protection_analysis(self, crypto_id):
        """Analyze downside protection characteristics"""
        try:
            price_data = PriceHistory.query.filter_by(crypto_id=crypto_id).first()
            
            if not price_data:
                return None
            
            # Analyze downside metrics
            ath_drawdown = abs(price_data.price_ath_change or 0)
            recent_drawdown_30d = min(0, price_data.price_30d_change or 0)
            recent_drawdown_90d = min(0, price_data.price_90d_change or 0)
            
            # Downside capture
            downside_volatility = abs(recent_drawdown_30d) if recent_drawdown_30d < 0 else 0
            
            return {
                'max_drawdown_from_ath': round(ath_drawdown, 2),
                'recent_30d_drawdown': round(abs(recent_drawdown_30d), 2),
                'recent_90d_drawdown': round(abs(recent_drawdown_90d), 2),
                'downside_volatility': round(downside_volatility, 2),
                'risk_rating': self._calculate_risk_rating(ath_drawdown, downside_volatility)
            }
        
        except Exception as e:
            logger.error(f"Downside protection analysis error: {e}")
            return None
    
    def _calculate_risk_rating(self, max_drawdown, volatility):
        """Calculate overall risk rating"""
        risk_score = (max_drawdown + volatility) / 2
        
        if risk_score < 20:
            return 'LOW'
        elif risk_score < 50:
            return 'MEDIUM'
        else:
            return 'HIGH'

