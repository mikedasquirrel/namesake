"""
Bayesian Hierarchical Model for Destiny Alignment
==================================================

Implements Bayesian statistical framework for analyzing prophetic name-outcome alignment.
Uses hierarchical modeling to account for nested structure (names within cultural origins within eras).

Features:
- Hierarchical Bayesian regression for destiny alignment
- Posterior distributions for prophetic scores
- Credible intervals (Bayesian confidence intervals)
- MCMC sampling with diagnostics
- Prior elicitation from expert knowledge
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

# Try importing PyMC3 - if not available, use scipy-based approximation
try:
    import pymc3 as pm
    PYMC3_AVAILABLE = True
except ImportError:
    PYMC3_AVAILABLE = False
    logging.warning("PyMC3 not available. Using scipy-based Bayesian approximation.")

from scipy import stats
import json

logger = logging.getLogger(__name__)


class BayesianDestinyAnalyzer:
    """
    Bayesian hierarchical analysis of destiny alignment.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.models = {}  # Store trained models
        self.traces = {}  # Store MCMC traces
        
        # Prior parameters (expert-elicited)
        self.priors = {
            'alignment_mean': 0.5,  # Prior belief: neutral alignment on average
            'alignment_std': 0.3,   # Moderate uncertainty
            'cultural_variance': 0.1,  # Within-culture variation
            'era_variance': 0.15    # Between-era variation
        }
        
        self.logger.info(f"BayesianDestinyAnalyzer initialized (PyMC3: {PYMC3_AVAILABLE})")
    
    def hierarchical_destiny_model(self, data: List[Dict], n_samples: int = 2000) -> Dict:
        """
        Fit hierarchical Bayesian model for destiny alignment.
        
        Model structure:
        alignment_score ~ Normal(μ_cultural + μ_era, σ)
        μ_cultural ~ Normal(μ_global, σ_cultural)
        μ_era ~ Normal(μ_global, σ_era)
        
        Args:
            data: List of dicts with 'alignment_score', 'cultural_origin', 'era'
            n_samples: Number of MCMC samples
        
        Returns:
            Dictionary with posterior summaries and diagnostics
        """
        if not data:
            return {'error': 'No data provided'}
        
        # Extract data
        scores = np.array([d['alignment_score'] for d in data])
        cultures = [d.get('cultural_origin', 'unknown') for d in data]
        eras = [d.get('era', 'unknown') for d in data]
        
        # Create indices
        unique_cultures = list(set(cultures))
        unique_eras = list(set(eras))
        
        culture_idx = np.array([unique_cultures.index(c) for c in cultures])
        era_idx = np.array([unique_eras.index(e) for e in eras])
        
        if PYMC3_AVAILABLE:
            result = self._fit_pymc3_model(scores, culture_idx, era_idx, 
                                          len(unique_cultures), len(unique_eras), n_samples)
        else:
            result = self._fit_approximate_model(scores, culture_idx, era_idx,
                                                len(unique_cultures), len(unique_eras))
        
        # Add metadata
        result['n_observations'] = len(scores)
        result['n_cultures'] = len(unique_cultures)
        result['n_eras'] = len(unique_eras)
        result['cultures'] = unique_cultures
        result['eras'] = unique_eras
        
        return result
    
    def _fit_pymc3_model(self, scores: np.ndarray, culture_idx: np.ndarray,
                        era_idx: np.ndarray, n_cultures: int, n_eras: int,
                        n_samples: int) -> Dict:
        """Fit full Bayesian hierarchical model using PyMC3."""
        with pm.Model() as model:
            # Hyperpriors
            mu_global = pm.Normal('mu_global', mu=self.priors['alignment_mean'], 
                                 sigma=self.priors['alignment_std'])
            
            sigma_cultural = pm.HalfNormal('sigma_cultural', sigma=self.priors['cultural_variance'])
            sigma_era = pm.HalfNormal('sigma_era', sigma=self.priors['era_variance'])
            sigma_obs = pm.HalfNormal('sigma_obs', sigma=0.2)
            
            # Cultural effects
            mu_culture = pm.Normal('mu_culture', mu=mu_global, sigma=sigma_cultural, 
                                  shape=n_cultures)
            
            # Era effects
            mu_era = pm.Normal('mu_era', mu=mu_global, sigma=sigma_era,
                              shape=n_eras)
            
            # Expected value
            mu = mu_culture[culture_idx] + mu_era[era_idx] - mu_global
            
            # Likelihood
            y_obs = pm.Normal('y_obs', mu=mu, sigma=sigma_obs, observed=scores)
            
            # Sample
            trace = pm.sample(n_samples, tune=1000, return_inferencedata=False,
                            progressbar=False)
        
        # Extract posterior summaries
        summary = pm.summary(trace)
        
        return {
            'method': 'PyMC3 MCMC',
            'posterior': {
                'mu_global': {
                    'mean': float(trace['mu_global'].mean()),
                    'std': float(trace['mu_global'].std()),
                    'hdi_95': self._hdi(trace['mu_global'], 0.95)
                },
                'sigma_cultural': {
                    'mean': float(trace['sigma_cultural'].mean()),
                    'std': float(trace['sigma_cultural'].std()),
                    'hdi_95': self._hdi(trace['sigma_cultural'], 0.95)
                },
                'sigma_era': {
                    'mean': float(trace['sigma_era'].mean()),
                    'std': float(trace['sigma_era'].std()),
                    'hdi_95': self._hdi(trace['sigma_era'], 0.95)
                }
            },
            'convergence': {
                'rhat': self._check_rhat(summary),
                'effective_n': self._get_effective_n(summary)
            },
            'trace_available': True
        }
    
    def _fit_approximate_model(self, scores: np.ndarray, culture_idx: np.ndarray,
                               era_idx: np.ndarray, n_cultures: int, n_eras: int) -> Dict:
        """Approximate Bayesian inference using maximum likelihood + bootstrap."""
        # Maximum likelihood estimates
        global_mean = np.mean(scores)
        global_std = np.std(scores)
        
        # Cultural effects
        cultural_means = []
        for i in range(n_cultures):
            mask = culture_idx == i
            if mask.any():
                cultural_means.append(np.mean(scores[mask]))
            else:
                cultural_means.append(global_mean)
        
        cultural_variance = np.var(cultural_means)
        
        # Era effects
        era_means = []
        for i in range(n_eras):
            mask = era_idx == i
            if mask.any():
                era_means.append(np.mean(scores[mask]))
            else:
                era_means.append(global_mean)
        
        era_variance = np.var(era_means)
        
        # Bootstrap for uncertainty
        n_bootstrap = 1000
        bootstrap_global = []
        
        for _ in range(n_bootstrap):
            indices = np.random.choice(len(scores), len(scores), replace=True)
            bootstrap_global.append(np.mean(scores[indices]))
        
        bootstrap_global = np.array(bootstrap_global)
        
        return {
            'method': 'Maximum Likelihood + Bootstrap',
            'posterior': {
                'mu_global': {
                    'mean': float(global_mean),
                    'std': float(np.std(bootstrap_global)),
                    'hdi_95': (float(np.percentile(bootstrap_global, 2.5)),
                              float(np.percentile(bootstrap_global, 97.5)))
                },
                'sigma_cultural': {
                    'mean': float(np.sqrt(cultural_variance)),
                    'std': float(np.sqrt(cultural_variance) * 0.2),  # Approximate
                    'hdi_95': (float(np.sqrt(cultural_variance) * 0.6),
                              float(np.sqrt(cultural_variance) * 1.4))
                },
                'sigma_era': {
                    'mean': float(np.sqrt(era_variance)),
                    'std': float(np.sqrt(era_variance) * 0.2),
                    'hdi_95': (float(np.sqrt(era_variance) * 0.6),
                              float(np.sqrt(era_variance) * 1.4))
                }
            },
            'convergence': {
                'rhat': 'N/A (not MCMC)',
                'effective_n': len(scores)
            },
            'trace_available': False,
            'note': 'Approximate inference. Install PyMC3 for full Bayesian analysis.'
        }
    
    def _hdi(self, trace: np.ndarray, credibility: float = 0.95) -> Tuple[float, float]:
        """Calculate Highest Density Interval (Bayesian credible interval)."""
        sorted_trace = np.sort(trace)
        n = len(sorted_trace)
        interval_size = int(np.floor(credibility * n))
        n_intervals = n - interval_size
        
        # Find interval with smallest width
        interval_widths = sorted_trace[interval_size:] - sorted_trace[:n_intervals]
        min_idx = np.argmin(interval_widths)
        
        hdi_min = float(sorted_trace[min_idx])
        hdi_max = float(sorted_trace[min_idx + interval_size])
        
        return (hdi_min, hdi_max)
    
    def _check_rhat(self, summary) -> str:
        """Check R-hat convergence diagnostic."""
        try:
            rhats = summary['r_hat'].values
            max_rhat = np.max(rhats[~np.isnan(rhats)])
            if max_rhat < 1.01:
                return f"Excellent (max R-hat: {max_rhat:.4f})"
            elif max_rhat < 1.05:
                return f"Good (max R-hat: {max_rhat:.4f})"
            else:
                return f"Poor - rerun with more samples (max R-hat: {max_rhat:.4f})"
        except:
            return "Unable to compute"
    
    def _get_effective_n(self, summary) -> float:
        """Get effective sample size."""
        try:
            ess = summary['ess_bulk'].values
            return float(np.mean(ess[~np.isnan(ess)]))
        except:
            return 0.0
    
    def posterior_predictive_check(self, model_result: Dict, observed_data: np.ndarray) -> Dict:
        """
        Perform posterior predictive check.
        
        Args:
            model_result: Result from hierarchical_destiny_model
            observed_data: Actual observed alignment scores
        
        Returns:
            Diagnostic metrics
        """
        # Generate predictions from posterior
        mu = model_result['posterior']['mu_global']['mean']
        sigma = model_result['posterior']['sigma_cultural']['mean']
        
        # Simulate data from posterior predictive
        n_sims = 1000
        predicted_data = []
        
        for _ in range(n_sims):
            predicted_data.append(np.random.normal(mu, sigma, len(observed_data)))
        
        predicted_data = np.array(predicted_data)
        
        # Calculate test statistics
        obs_mean = np.mean(observed_data)
        obs_std = np.std(observed_data)
        
        pred_means = np.mean(predicted_data, axis=1)
        pred_stds = np.std(predicted_data, axis=1)
        
        # Bayesian p-values
        p_value_mean = np.mean(pred_means >= obs_mean)
        p_value_std = np.mean(pred_stds >= obs_std)
        
        return {
            'observed': {
                'mean': float(obs_mean),
                'std': float(obs_std)
            },
            'predicted': {
                'mean': float(np.mean(pred_means)),
                'mean_95_hdi': (float(np.percentile(pred_means, 2.5)),
                               float(np.percentile(pred_means, 97.5))),
                'std': float(np.mean(pred_stds)),
                'std_95_hdi': (float(np.percentile(pred_stds, 2.5)),
                              float(np.percentile(pred_stds, 97.5)))
            },
            'bayesian_p_values': {
                'mean': float(p_value_mean),
                'std': float(p_value_std)
            },
            'interpretation': self._interpret_ppc(p_value_mean, p_value_std)
        }
    
    def _interpret_ppc(self, p_mean: float, p_std: float) -> str:
        """Interpret posterior predictive check."""
        if 0.05 < p_mean < 0.95 and 0.05 < p_std < 0.95:
            return "Model fits data well"
        elif p_mean < 0.05 or p_mean > 0.95:
            return "Model may not capture mean structure well"
        elif p_std < 0.05 or p_std > 0.95:
            return "Model may not capture variance structure well"
        else:
            return "Model fit adequate but could be improved"
    
    def compare_cultural_origins(self, data: List[Dict]) -> Dict:
        """
        Compare destiny alignment across cultural origins using Bayesian approach.
        
        Args:
            data: List of dicts with 'alignment_score' and 'cultural_origin'
        
        Returns:
            Bayesian comparison results
        """
        # Group by cultural origin
        by_culture = defaultdict(list)
        for d in data:
            culture = d.get('cultural_origin', 'unknown')
            score = d.get('alignment_score', 0.5)
            by_culture[culture].append(score)
        
        # Bayesian comparison for each pair
        cultures = list(by_culture.keys())
        comparisons = []
        
        for i, culture1 in enumerate(cultures):
            for culture2 in cultures[i+1:]:
                scores1 = np.array(by_culture[culture1])
                scores2 = np.array(by_culture[culture2])
                
                # Bayesian t-test (using BEST approximation)
                comparison = self._bayesian_ttest(scores1, scores2, culture1, culture2)
                comparisons.append(comparison)
        
        return {
            'n_cultures': len(cultures),
            'cultures': cultures,
            'comparisons': comparisons,
            'summary': self._summarize_comparisons(comparisons)
        }
    
    def _bayesian_ttest(self, group1: np.ndarray, group2: np.ndarray,
                       name1: str, name2: str) -> Dict:
        """
        Bayesian equivalent of t-test.
        Estimates probability that group1 > group2.
        """
        # Bootstrap approximation of Bayesian posterior
        n_bootstrap = 5000
        differences = []
        
        for _ in range(n_bootstrap):
            sample1 = np.random.choice(group1, len(group1), replace=True)
            sample2 = np.random.choice(group2, len(group2), replace=True)
            differences.append(np.mean(sample1) - np.mean(sample2))
        
        differences = np.array(differences)
        
        # Probability of superiority
        prob_greater = np.mean(differences > 0)
        
        # Effect size
        effect_size = np.mean(differences) / np.std(differences)
        
        return {
            'group1': name1,
            'group2': name2,
            'mean_difference': float(np.mean(differences)),
            'difference_hdi_95': (float(np.percentile(differences, 2.5)),
                                 float(np.percentile(differences, 97.5))),
            'prob_group1_greater': float(prob_greater),
            'effect_size': float(effect_size),
            'interpretation': self._interpret_comparison(prob_greater, effect_size)
        }
    
    def _interpret_comparison(self, prob_greater: float, effect_size: float) -> str:
        """Interpret Bayesian comparison."""
        if prob_greater > 0.95:
            strength = "very strong"
        elif prob_greater > 0.9:
            strength = "strong"
        elif prob_greater > 0.8:
            strength = "moderate"
        else:
            strength = "weak"
        
        if abs(effect_size) > 0.8:
            magnitude = "large"
        elif abs(effect_size) > 0.5:
            magnitude = "medium"
        else:
            magnitude = "small"
        
        return f"{strength} evidence of difference ({magnitude} effect size)"
    
    def _summarize_comparisons(self, comparisons: List[Dict]) -> str:
        """Summarize multiple comparisons."""
        strong_diffs = sum(1 for c in comparisons if c['prob_group1_greater'] > 0.9 or c['prob_group1_greater'] < 0.1)
        
        return f"{strong_diffs}/{len(comparisons)} comparisons show strong evidence of difference"


# Singleton
bayesian_analyzer = BayesianDestinyAnalyzer()

