"""
Portfolio Optimization Engine
Modern Portfolio Theory implementation for name-based diversification
"""

import numpy as np
from core.models import Cryptocurrency, NameAnalysis, PriceHistory
from analyzers.confidence_scorer import ConfidenceScorer
import logging

logger = logging.getLogger(__name__)


class PortfolioOptimizer:
    """Optimize cryptocurrency portfolios based on name metrics and performance"""
    
    def __init__(self):
        self.scorer = ConfidenceScorer()
    
    def optimize_weights(self, crypto_ids, objective='sharpe', constraints=None):
        """
        Optimize portfolio weights
        
        Args:
            crypto_ids: List of cryptocurrency IDs to include
            objective: Optimization objective ('sharpe', 'min_variance', 'max_return')
            constraints: Dict with 'min_weight' and 'max_weight'
        
        Returns: dict with optimal weights and metrics
        """
        try:
            if not crypto_ids or len(crypto_ids) < 2:
                return None
            
            constraints = constraints or {'min_weight': 0.05, 'max_weight': 0.40}
            
            # Get returns for each crypto
            returns = []
            valid_ids = []
            
            for crypto_id in crypto_ids:
                price_data = PriceHistory.query.filter_by(crypto_id=crypto_id).first()
                if price_data and price_data.price_1yr_change is not None:
                    returns.append(price_data.price_1yr_change / 100)
                    valid_ids.append(crypto_id)
            
            if len(valid_ids) < 2:
                return None
            
            returns_array = np.array(returns)
            n_assets = len(valid_ids)
            
            # Optimization
            if objective == 'sharpe':
                weights = self._optimize_sharpe(returns_array, constraints)
            elif objective == 'min_variance':
                weights = self._minimize_variance(returns_array, constraints)
            elif objective == 'max_return':
                weights = self._maximize_return(returns_array, constraints)
            else:
                # Equal weight as fallback
                weights = np.ones(n_assets) / n_assets
            
            # Calculate portfolio metrics
            portfolio_return = np.dot(weights, returns_array)
            portfolio_variance = np.dot(weights**2, returns_array**2)  # Simplified
            portfolio_volatility = np.sqrt(portfolio_variance)
            sharpe_ratio = portfolio_return / portfolio_volatility if portfolio_volatility > 0 else 0
            
            # Format output
            allocations = []
            for crypto_id, weight in zip(valid_ids, weights):
                crypto = Cryptocurrency.query.get(crypto_id)
                allocations.append({
                    'crypto_id': crypto_id,
                    'name': crypto.name if crypto else 'Unknown',
                    'symbol': crypto.symbol if crypto else '',
                    'weight': round(weight, 4),
                    'weight_percent': round(weight * 100, 2)
                })
            
            return {
                'objective': objective,
                'allocations': allocations,
                'metrics': {
                    'expected_return': round(portfolio_return * 100, 2),
                    'volatility': round(portfolio_volatility * 100, 2),
                    'sharpe_ratio': round(sharpe_ratio, 2)
                },
                'constraints': constraints
            }
        
        except Exception as e:
            logger.error(f"Portfolio optimization error: {e}")
            return None
    
    def _optimize_sharpe(self, returns, constraints):
        """Optimize for maximum Sharpe ratio"""
        n_assets = len(returns)
        
        # Simplified optimization - weight by returns with constraints
        positive_returns = np.maximum(returns, 0.01)  # Avoid division by zero
        raw_weights = positive_returns / positive_returns.sum()
        
        # Apply constraints
        min_w = constraints.get('min_weight', 0.05)
        max_w = constraints.get('max_weight', 0.40)
        
        weights = np.clip(raw_weights, min_w, max_w)
        weights = weights / weights.sum()  # Normalize
        
        return weights
    
    def _minimize_variance(self, returns, constraints):
        """Minimize portfolio variance (equal weight with constraints)"""
        n_assets = len(returns)
        
        # Start with equal weights
        weights = np.ones(n_assets) / n_assets
        
        # Apply constraints
        min_w = constraints.get('min_weight', 0.05)
        max_w = constraints.get('max_weight', 0.40)
        
        weights = np.clip(weights, min_w, max_w)
        weights = weights / weights.sum()
        
        return weights
    
    def _maximize_return(self, returns, constraints):
        """Maximize expected return"""
        n_assets = len(returns)
        
        # Weight heavily toward highest returns
        sorted_indices = np.argsort(returns)[::-1]
        weights = np.zeros(n_assets)
        
        max_w = constraints.get('max_weight', 0.40)
        
        # Allocate to top performers
        remaining = 1.0
        for idx in sorted_indices:
            if remaining <= 0:
                break
            weight = min(max_w, remaining)
            weights[idx] = weight
            remaining -= weight
        
        weights = weights / weights.sum()
        
        return weights
    
    def efficient_frontier(self, crypto_ids, num_portfolios=50):
        """
        Generate efficient frontier
        
        Args:
            crypto_ids: List of cryptocurrency IDs
            num_portfolios: Number of portfolios to generate
        
        Returns: list of portfolios with returns and risk
        """
        try:
            # Get returns
            returns = []
            valid_ids = []
            
            for crypto_id in crypto_ids:
                price_data = PriceHistory.query.filter_by(crypto_id=crypto_id).first()
                if price_data and price_data.price_1yr_change is not None:
                    returns.append(price_data.price_1yr_change / 100)
                    valid_ids.append(crypto_id)
            
            if len(valid_ids) < 2:
                return []
            
            returns_array = np.array(returns)
            n_assets = len(valid_ids)
            
            portfolios = []
            
            for i in range(num_portfolios):
                # Generate random weights
                weights = np.random.random(n_assets)
                weights = weights / weights.sum()
                
                # Calculate metrics
                portfolio_return = np.dot(weights, returns_array)
                portfolio_variance = np.dot(weights**2, returns_array**2)
                portfolio_volatility = np.sqrt(portfolio_variance)
                sharpe = portfolio_return / portfolio_volatility if portfolio_volatility > 0 else 0
                
                portfolios.append({
                    'return': round(portfolio_return * 100, 2),
                    'volatility': round(portfolio_volatility * 100, 2),
                    'sharpe_ratio': round(sharpe, 2)
                })
            
            # Sort by Sharpe ratio
            portfolios.sort(key=lambda x: x['sharpe_ratio'], reverse=True)
            
            return portfolios
        
        except Exception as e:
            logger.error(f"Efficient frontier error: {e}")
            return []
    
    def risk_parity(self, crypto_ids):
        """
        Risk parity allocation
        Equal risk contribution from each asset
        """
        try:
            # Get volatilities
            volatilities = []
            valid_ids = []
            
            for crypto_id in crypto_ids:
                price_data = PriceHistory.query.filter_by(crypto_id=crypto_id).first()
                if price_data and price_data.price_1yr_change is not None:
                    # Use absolute change as proxy for volatility
                    vol = abs(price_data.price_1yr_change) / 100
                    volatilities.append(max(vol, 0.01))  # Minimum volatility
                    valid_ids.append(crypto_id)
            
            if not volatilities:
                return None
            
            volatilities_array = np.array(volatilities)
            
            # Inverse volatility weighting
            inv_vol = 1 / volatilities_array
            weights = inv_vol / inv_vol.sum()
            
            allocations = []
            for crypto_id, weight in zip(valid_ids, weights):
                crypto = Cryptocurrency.query.get(crypto_id)
                allocations.append({
                    'crypto_id': crypto_id,
                    'name': crypto.name if crypto else 'Unknown',
                    'symbol': crypto.symbol if crypto else '',
                    'weight_percent': round(weight * 100, 2)
                })
            
            return {
                'strategy': 'risk_parity',
                'allocations': allocations
            }
        
        except Exception as e:
            logger.error(f"Risk parity error: {e}")
            return None
    
    def name_based_diversification(self, target_count=10):
        """
        Create diversified portfolio based on name characteristics
        
        Args:
            target_count: Target number of assets
        
        Returns: dict with diversified portfolio
        """
        try:
            # Get all scored cryptocurrencies
            all_scores = self.scorer.score_all_cryptocurrencies()
            
            if len(all_scores) < target_count:
                target_count = len(all_scores)
            
            # Diversification criteria
            selected = []
            name_types_used = set()
            syllable_counts_used = set()
            
            for score_data in all_scores:
                if len(selected) >= target_count:
                    break
                
                crypto_id = score_data['crypto_id']
                analysis = NameAnalysis.query.filter_by(crypto_id=crypto_id).first()
                
                if not analysis:
                    continue
                
                # Prefer diversity in name types and syllable counts
                name_type = analysis.name_type
                syllables = analysis.syllable_count
                
                # Add if high score and adds diversity
                if (score_data['score'] >= 65 and 
                    (name_type not in name_types_used or len(selected) < 5)):
                    
                    selected.append(score_data)
                    name_types_used.add(name_type)
                    syllable_counts_used.add(syllables)
            
            # Optimize weights
            crypto_ids = [s['crypto_id'] for s in selected]
            optimization = self.optimize_weights(crypto_ids, objective='sharpe')
            
            if optimization:
                optimization['diversification_score'] = len(name_types_used) / target_count * 100
                optimization['name_types_included'] = list(name_types_used)
            
            return optimization
        
        except Exception as e:
            logger.error(f"Name-based diversification error: {e}")
            return None

