"""
Market Simulator
Monte Carlo simulations and A/B testing for cryptocurrency names
"""

import numpy as np
from predictor import NamePredictor
import random


class MarketSimulator:
    """Simulate market performance for name testing"""
    
    def __init__(self):
        self.predictor = NamePredictor()
    
    def monte_carlo_simulation(self, name, performance_metric='price_1yr_change', 
                               simulations=1000, volatility=0.3):
        """
        Run Monte Carlo simulation for a cryptocurrency name
        
        Args:
            name: Cryptocurrency name to simulate
            performance_metric: Which metric to simulate
            simulations: Number of simulation runs
            volatility: Price volatility factor (0-1)
            
        Returns:
            Dict with simulation results
        """
        # Ensure predictor is trained
        if not self.predictor.is_trained or performance_metric not in self.predictor.models:
            self.predictor.train(performance_metric)
        
        # Get base prediction
        base_prediction = self.predictor.predict(name, performance_metric)
        
        # Run simulations
        results = []
        
        for _ in range(simulations):
            # Add randomness based on volatility and prediction uncertainty
            noise_std = volatility * abs(base_prediction['prediction'])
            simulated_return = np.random.normal(
                base_prediction['prediction'],
                max(noise_std, 10)  # Minimum 10% std
            )
            results.append(simulated_return)
        
        results = np.array(results)
        
        # Calculate statistics
        return {
            'name': name,
            'simulations': simulations,
            'mean_return': round(float(np.mean(results)), 2),
            'median_return': round(float(np.median(results)), 2),
            'std_dev': round(float(np.std(results)), 2),
            'min_return': round(float(np.min(results)), 2),
            'max_return': round(float(np.max(results)), 2),
            'percentiles': {
                '5th': round(float(np.percentile(results, 5)), 2),
                '25th': round(float(np.percentile(results, 25)), 2),
                '75th': round(float(np.percentile(results, 75)), 2),
                '95th': round(float(np.percentile(results, 95)), 2)
            },
            'probability_positive': round(float(np.sum(results > 0) / len(results) * 100), 2),
            'probability_above_50': round(float(np.sum(results > 50) / len(results) * 100), 2),
            'probability_above_100': round(float(np.sum(results > 100) / len(results) * 100), 2),
            'value_at_risk_5': round(float(np.percentile(results, 5)), 2),  # 5% VaR
            'value_at_risk_1': round(float(np.percentile(results, 1)), 2),  # 1% VaR
            'base_prediction': base_prediction['prediction']
        }
    
    def ab_test(self, name_a, name_b, performance_metric='price_1yr_change', 
                simulations=1000):
        """
        A/B test two cryptocurrency names
        
        Args:
            name_a: First name to test
            name_b: Second name to test
            performance_metric: Performance metric to compare
            simulations: Number of simulation runs
            
        Returns:
            Dict with A/B test results and winner
        """
        # Run simulations for both names
        sim_a = self.monte_carlo_simulation(name_a, performance_metric, simulations)
        sim_b = self.monte_carlo_simulation(name_b, performance_metric, simulations)
        
        # Calculate probability that A > B
        # Using normal distribution assumption
        diff_mean = sim_a['mean_return'] - sim_b['mean_return']
        diff_std = np.sqrt(sim_a['std_dev']**2 + sim_b['std_dev']**2)
        
        # Z-score and probability
        if diff_std > 0:
            z_score = diff_mean / diff_std
            # Probability that A > B
            prob_a_better = 50 + 50 * (z_score / abs(z_score)) * (1 - np.exp(-abs(z_score)/2))
        else:
            prob_a_better = 50
        
        # Determine winner
        if diff_mean > 0:
            winner = name_a
            margin = diff_mean
        elif diff_mean < 0:
            winner = name_b
            margin = abs(diff_mean)
        else:
            winner = 'tie'
            margin = 0
        
        return {
            'name_a': name_a,
            'name_b': name_b,
            'metric': performance_metric,
            'simulations': simulations,
            'results_a': sim_a,
            'results_b': sim_b,
            'winner': winner,
            'margin': round(margin, 2),
            'probability_a_better': round(prob_a_better, 2),
            'confidence': 'high' if abs(diff_mean) > diff_std else 'moderate' if abs(diff_mean) > diff_std/2 else 'low'
        }
    
    def multi_name_tournament(self, names, performance_metric='price_1yr_change'):
        """
        Run tournament-style comparison of multiple names
        
        Args:
            names: List of name strings
            performance_metric: Performance metric to compare
            
        Returns:
            Dict with tournament results
        """
        if len(names) < 2:
            raise ValueError("Need at least 2 names for tournament")
        
        # Get predictions for all names
        predictions = []
        for name in names:
            try:
                sim = self.monte_carlo_simulation(name, performance_metric, simulations=500)
                predictions.append({
                    'name': name,
                    'mean_return': sim['mean_return'],
                    'median_return': sim['median_return'],
                    'std_dev': sim['std_dev'],
                    'prob_positive': sim['probability_positive'],
                    'prob_above_100': sim['probability_above_100']
                })
            except Exception as e:
                print(f"Error simulating {name}: {e}")
        
        # Sort by mean return
        predictions.sort(key=lambda x: x['mean_return'], reverse=True)
        
        # Assign ranks
        for i, pred in enumerate(predictions):
            pred['rank'] = i + 1
        
        return {
            'names_count': len(predictions),
            'metric': performance_metric,
            'winner': predictions[0]['name'] if predictions else None,
            'rankings': predictions
        }
    
    def risk_analysis(self, name, performance_metric='price_1yr_change',
                     investment_amount=10000):
        """
        Comprehensive risk analysis for a name
        
        Args:
            name: Cryptocurrency name
            performance_metric: Performance metric
            investment_amount: Hypothetical investment amount
            
        Returns:
            Dict with risk metrics
        """
        sim = self.monte_carlo_simulation(name, performance_metric, simulations=10000)
        
        # Calculate potential returns
        returns = {
            'best_case': investment_amount * (1 + sim['percentiles']['95th'] / 100),
            'likely_case': investment_amount * (1 + sim['mean_return'] / 100),
            'worst_case': investment_amount * (1 + sim['percentiles']['5th'] / 100),
            'median_case': investment_amount * (1 + sim['median_return'] / 100)
        }
        
        # Risk metrics
        downside_deviation = np.sqrt(
            np.mean([min(0, r - sim['mean_return'])**2 for r in [
                sim['percentiles']['5th'], sim['percentiles']['25th'], 
                sim['median_return'], sim['percentiles']['75th'], 
                sim['percentiles']['95th']
            ]])
        )
        
        sharpe_ratio = (sim['mean_return'] - 0) / sim['std_dev'] if sim['std_dev'] > 0 else 0
        
        return {
            'name': name,
            'investment': investment_amount,
            'potential_returns': {
                k: round(v, 2) for k, v in returns.items()
            },
            'potential_gains': {
                'best_case': round(returns['best_case'] - investment_amount, 2),
                'likely_case': round(returns['likely_case'] - investment_amount, 2),
                'worst_case': round(returns['worst_case'] - investment_amount, 2)
            },
            'risk_metrics': {
                'volatility': round(sim['std_dev'], 2),
                'downside_deviation': round(downside_deviation, 2),
                'sharpe_ratio': round(sharpe_ratio, 3),
                'value_at_risk_5': round(investment_amount * (sim['value_at_risk_5'] / 100), 2),
                'value_at_risk_1': round(investment_amount * (sim['value_at_risk_1'] / 100), 2)
            },
            'probabilities': {
                'profit': sim['probability_positive'],
                'double': sim['probability_above_100'],
                'above_50': sim['probability_above_50']
            }
        }
    
    def scenario_analysis(self, names_dict, performance_metric='price_1yr_change'):
        """
        Analyze different scenarios for name selection
        
        Args:
            names_dict: Dict of {scenario_name: crypto_name}
            performance_metric: Performance metric
            
        Returns:
            Dict comparing scenarios
        """
        scenarios = {}
        
        for scenario_name, crypto_name in names_dict.items():
            try:
                risk = self.risk_analysis(crypto_name, performance_metric)
                scenarios[scenario_name] = {
                    'name': crypto_name,
                    'expected_return': risk['risk_metrics'],
                    'probabilities': risk['probabilities']
                }
            except Exception as e:
                print(f"Error analyzing scenario {scenario_name}: {e}")
        
        return {
            'scenarios': scenarios,
            'recommendation': max(scenarios.items(), 
                                key=lambda x: x[1].get('expected_return', {}).get('sharpe_ratio', 0))[0]
            if scenarios else None
        }

