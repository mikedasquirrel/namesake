"""
Statistical Rigor Enhancement Module
=====================================

Provides statistical rigor tools for nominative determinism research:
- Effect sizes (Cohen's d, Hedge's g)
- Confidence intervals (bootstrap, parametric)
- Multiple testing corrections (Bonferroni, FDR, Holm)
- Power analysis
- Robustness checks

This module ensures all research findings meet academic publication standards.
"""

import logging
import numpy as np
from scipy import stats
from typing import Dict, List, Tuple, Optional
import warnings

logger = logging.getLogger(__name__)


class StatisticalRigor:
    """Statistical rigor tools for research-grade analysis."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def cohens_d(self, group1: np.ndarray, group2: np.ndarray) -> float:
        """
        Calculate Cohen's d effect size.
        
        Cohen's d interpretation:
        - 0.2: small effect
        - 0.5: medium effect
        - 0.8: large effect
        
        Args:
            group1: First group data
            group2: Second group data
        
        Returns:
            Cohen's d effect size
        """
        n1, n2 = len(group1), len(group2)
        var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
        
        # Pooled standard deviation
        pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
        
        if pooled_std == 0:
            return 0.0
        
        d = (np.mean(group1) - np.mean(group2)) / pooled_std
        return float(d)
    
    def hedges_g(self, group1: np.ndarray, group2: np.ndarray) -> float:
        """
        Calculate Hedge's g effect size (bias-corrected Cohen's d).
        Preferred for small sample sizes (n < 20).
        
        Args:
            group1: First group data
            group2: Second group data
        
        Returns:
            Hedge's g effect size
        """
        d = self.cohens_d(group1, group2)
        n = len(group1) + len(group2)
        
        # Correction factor
        correction = 1 - (3 / (4 * n - 9))
        
        g = d * correction
        return float(g)
    
    def bootstrap_ci(self, data: np.ndarray, statistic_func=np.mean, 
                     n_bootstrap: int = 10000, confidence: float = 0.95) -> Tuple[float, float, float]:
        """
        Calculate bootstrap confidence interval.
        
        Args:
            data: Data array
            statistic_func: Function to calculate statistic (default: mean)
            n_bootstrap: Number of bootstrap samples
            confidence: Confidence level (default: 0.95 for 95% CI)
        
        Returns:
            Tuple of (statistic, lower_ci, upper_ci)
        """
        bootstrap_stats = []
        
        for _ in range(n_bootstrap):
            sample = np.random.choice(data, size=len(data), replace=True)
            bootstrap_stats.append(statistic_func(sample))
        
        bootstrap_stats = np.array(bootstrap_stats)
        
        alpha = 1 - confidence
        lower_percentile = (alpha / 2) * 100
        upper_percentile = (1 - alpha / 2) * 100
        
        statistic = statistic_func(data)
        lower_ci = np.percentile(bootstrap_stats, lower_percentile)
        upper_ci = np.percentile(bootstrap_stats, upper_percentile)
        
        return float(statistic), float(lower_ci), float(upper_ci)
    
    def parametric_ci(self, data: np.ndarray, confidence: float = 0.95) -> Tuple[float, float, float]:
        """
        Calculate parametric confidence interval (assumes normality).
        
        Args:
            data: Data array
            confidence: Confidence level
        
        Returns:
            Tuple of (mean, lower_ci, upper_ci)
        """
        mean = np.mean(data)
        sem = stats.sem(data)
        
        ci = sem * stats.t.ppf((1 + confidence) / 2, len(data) - 1)
        
        return float(mean), float(mean - ci), float(mean + ci)
    
    def bonferroni_correction(self, p_values: List[float], alpha: float = 0.05) -> Dict:
        """
        Apply Bonferroni correction for multiple testing.
        
        Args:
            p_values: List of p-values
            alpha: Significance level
        
        Returns:
            Dictionary with corrected results
        """
        n_tests = len(p_values)
        corrected_alpha = alpha / n_tests
        
        significant = [p < corrected_alpha for p in p_values]
        
        return {
            'n_tests': n_tests,
            'original_alpha': alpha,
            'corrected_alpha': corrected_alpha,
            'p_values': p_values,
            'significant': significant,
            'n_significant': sum(significant)
        }
    
    def fdr_correction(self, p_values: List[float], alpha: float = 0.05, 
                      method: str = 'bh') -> Dict:
        """
        Apply False Discovery Rate correction (Benjamini-Hochberg).
        
        Args:
            p_values: List of p-values
            alpha: Significance level
            method: 'bh' (Benjamini-Hochberg) or 'by' (Benjamini-Yekutieli)
        
        Returns:
            Dictionary with corrected results
        """
        p_array = np.array(p_values)
        n = len(p_array)
        
        # Sort p-values and keep track of original indices
        sorted_indices = np.argsort(p_array)
        sorted_p = p_array[sorted_indices]
        
        # Calculate critical values
        if method == 'bh':
            critical_values = np.arange(1, n + 1) * alpha / n
        elif method == 'by':
            c_n = np.sum(1 / np.arange(1, n + 1))
            critical_values = np.arange(1, n + 1) * alpha / (n * c_n)
        else:
            raise ValueError(f"Unknown method: {method}")
        
        # Find significant p-values
        significant_sorted = sorted_p <= critical_values
        
        # Map back to original order
        significant = np.zeros(n, dtype=bool)
        significant[sorted_indices] = significant_sorted
        
        return {
            'n_tests': n,
            'alpha': alpha,
            'method': method,
            'p_values': list(p_array),
            'significant': list(significant),
            'n_significant': int(np.sum(significant)),
            'adjusted_p_values': self._adjust_p_values_fdr(p_array, method, alpha)
        }
    
    def _adjust_p_values_fdr(self, p_values: np.ndarray, method: str, alpha: float) -> List[float]:
        """Adjust p-values for FDR."""
        n = len(p_values)
        sorted_indices = np.argsort(p_values)
        sorted_p = p_values[sorted_indices]
        
        if method == 'bh':
            adjusted = sorted_p * n / np.arange(1, n + 1)
        elif method == 'by':
            c_n = np.sum(1 / np.arange(1, n + 1))
            adjusted = sorted_p * n * c_n / np.arange(1, n + 1)
        
        # Ensure monotonicity
        adjusted = np.minimum.accumulate(adjusted[::-1])[::-1]
        
        # Map back to original order
        adjusted_original_order = np.zeros(n)
        adjusted_original_order[sorted_indices] = adjusted
        
        return list(np.minimum(adjusted_original_order, 1.0))
    
    def holm_bonferroni(self, p_values: List[float], alpha: float = 0.05) -> Dict:
        """
        Apply Holm-Bonferroni correction (less conservative than Bonferroni).
        
        Args:
            p_values: List of p-values
            alpha: Significance level
        
        Returns:
            Dictionary with corrected results
        """
        p_array = np.array(p_values)
        n = len(p_array)
        
        # Sort p-values
        sorted_indices = np.argsort(p_array)
        sorted_p = p_array[sorted_indices]
        
        # Calculate critical values
        critical_values = alpha / (n - np.arange(n))
        
        # Find first non-significant p-value
        significant_sorted = sorted_p <= critical_values
        
        # All tests after first non-significant are also non-significant
        if not np.all(significant_sorted):
            first_ns = np.where(~significant_sorted)[0][0]
            significant_sorted[first_ns:] = False
        
        # Map back to original order
        significant = np.zeros(n, dtype=bool)
        significant[sorted_indices] = significant_sorted
        
        return {
            'n_tests': n,
            'alpha': alpha,
            'p_values': list(p_array),
            'significant': list(significant),
            'n_significant': int(np.sum(significant))
        }
    
    def power_analysis(self, effect_size: float, alpha: float = 0.05, 
                      power: float = 0.80, alternative: str = 'two-sided') -> int:
        """
        Calculate required sample size for desired power.
        
        Args:
            effect_size: Expected effect size (Cohen's d)
            alpha: Significance level
            power: Desired statistical power
            alternative: 'two-sided' or 'one-sided'
        
        Returns:
            Required sample size per group
        """
        from scipy.stats import norm
        
        if alternative == 'two-sided':
            z_alpha = norm.ppf(1 - alpha / 2)
        else:
            z_alpha = norm.ppf(1 - alpha)
        
        z_beta = norm.ppf(power)
        
        # Formula for two-sample t-test
        n = 2 * ((z_alpha + z_beta) / effect_size) ** 2
        
        return int(np.ceil(n))
    
    def achieved_power(self, group1: np.ndarray, group2: np.ndarray, 
                      alpha: float = 0.05) -> float:
        """
        Calculate achieved statistical power.
        
        Args:
            group1: First group data
            group2: Second group data
            alpha: Significance level
        
        Returns:
            Achieved power (0-1)
        """
        effect_size = self.cohens_d(group1, group2)
        n = len(group1)  # Assuming equal sample sizes
        
        from scipy.stats import norm
        
        # Calculate non-centrality parameter
        ncp = effect_size * np.sqrt(n / 2)
        
        # Critical value
        z_alpha = norm.ppf(1 - alpha / 2)
        
        # Power
        power = 1 - norm.cdf(z_alpha - ncp) + norm.cdf(-z_alpha - ncp)
        
        return float(power)
    
    def robustness_check_outliers(self, data: np.ndarray, 
                                  statistic_func=np.mean) -> Dict:
        """
        Check robustness to outliers using jackknife.
        
        Args:
            data: Data array
            statistic_func: Statistic function to test
        
        Returns:
            Dictionary with robustness metrics
        """
        original_stat = statistic_func(data)
        
        # Jackknife: leave one out
        jackknife_stats = []
        for i in range(len(data)):
            sample = np.delete(data, i)
            jackknife_stats.append(statistic_func(sample))
        
        jackknife_stats = np.array(jackknife_stats)
        
        # Calculate variability
        jackknife_se = np.std(jackknife_stats) * np.sqrt(len(data) - 1)
        max_change = np.max(np.abs(jackknife_stats - original_stat))
        
        return {
            'original_statistic': float(original_stat),
            'jackknife_mean': float(np.mean(jackknife_stats)),
            'jackknife_se': float(jackknife_se),
            'max_change': float(max_change),
            'max_change_percent': float(max_change / original_stat * 100) if original_stat != 0 else 0,
            'is_robust': max_change / abs(original_stat) < 0.1 if original_stat != 0 else True
        }
    
    def comprehensive_comparison(self, group1: np.ndarray, group2: np.ndarray,
                                group1_name: str = "Group 1", 
                                group2_name: str = "Group 2") -> Dict:
        """
        Comprehensive statistical comparison with all rigor metrics.
        
        Args:
            group1: First group data
            group2: Second group data
            group1_name: Name of first group
            group2_name: Name of second group
        
        Returns:
            Complete statistical comparison
        """
        # Basic statistics
        mean1, std1 = np.mean(group1), np.std(group1, ddof=1)
        mean2, std2 = np.mean(group2), np.std(group2, ddof=1)
        
        # T-test
        t_stat, p_value = stats.ttest_ind(group1, group2)
        
        # Effect sizes
        cohens_d = self.cohens_d(group1, group2)
        hedges_g = self.hedges_g(group1, group2)
        
        # Confidence intervals
        ci1 = self.bootstrap_ci(group1)
        ci2 = self.bootstrap_ci(group2)
        
        # Power analysis
        power = self.achieved_power(group1, group2)
        required_n = self.power_analysis(abs(cohens_d))
        
        # Robustness
        robust1 = self.robustness_check_outliers(group1)
        robust2 = self.robustness_check_outliers(group2)
        
        # Effect size interpretation
        if abs(cohens_d) < 0.2:
            effect_interpretation = "negligible"
        elif abs(cohens_d) < 0.5:
            effect_interpretation = "small"
        elif abs(cohens_d) < 0.8:
            effect_interpretation = "medium"
        else:
            effect_interpretation = "large"
        
        return {
            'groups': {
                group1_name: {
                    'n': len(group1),
                    'mean': float(mean1),
                    'std': float(std1),
                    'ci_95': {'mean': ci1[0], 'lower': ci1[1], 'upper': ci1[2]},
                    'robustness': robust1
                },
                group2_name: {
                    'n': len(group2),
                    'mean': float(mean2),
                    'std': float(std2),
                    'ci_95': {'mean': ci2[0], 'lower': ci2[1], 'upper': ci2[2]},
                    'robustness': robust2
                }
            },
            'statistical_test': {
                'test': 'Independent samples t-test',
                't_statistic': float(t_stat),
                'p_value': float(p_value),
                'significant_at_05': p_value < 0.05,
                'significant_at_01': p_value < 0.01
            },
            'effect_size': {
                'cohens_d': float(cohens_d),
                'hedges_g': float(hedges_g),
                'interpretation': effect_interpretation,
                'direction': group1_name if mean1 > mean2 else group2_name
            },
            'power_analysis': {
                'achieved_power': float(power),
                'required_n_per_group': required_n,
                'is_adequately_powered': power >= 0.80
            },
            'interpretation': self._generate_interpretation(
                p_value, cohens_d, effect_interpretation, group1_name, group2_name, mean1, mean2
            )
        }
    
    def _generate_interpretation(self, p_value: float, cohens_d: float, 
                                effect_interp: str, group1_name: str, 
                                group2_name: str, mean1: float, mean2: float) -> str:
        """Generate human-readable interpretation."""
        direction = group1_name if mean1 > mean2 else group2_name
        
        if p_value < 0.001:
            sig_str = "highly significant (p < 0.001)"
        elif p_value < 0.01:
            sig_str = "significant (p < 0.01)"
        elif p_value < 0.05:
            sig_str = "significant (p < 0.05)"
        else:
            sig_str = "not significant (p >= 0.05)"
        
        interpretation = f"The difference between {group1_name} and {group2_name} is {sig_str}. "
        interpretation += f"The effect size is {effect_interp} (Cohen's d = {cohens_d:.3f}). "
        interpretation += f"{direction} shows higher values. "
        
        return interpretation


# Singleton instance
statistical_rigor = StatisticalRigor()

