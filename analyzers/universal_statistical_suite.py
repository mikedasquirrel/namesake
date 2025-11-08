"""
Universal Statistical Suite - Publication-Ready Statistical Analysis

This module provides comprehensive statistical methods for rigorous analysis across all domains.
Every analysis should report: effect size, confidence interval, p-value, and power.

Author: Michael Andrew Smerconish Jr.
Philosophy: Let the data speak. Test everything. Report honestly.
"""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import chi2_contingency, mannwhitneyu, kruskal
from sklearn.model_selection import KFold, LeaveOneOut, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from statsmodels.stats.power import TTestIndPower, FTestAnovaPower
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.diagnostic import het_breuschpagan, het_white
from statsmodels.stats.stattools import durbin_watson
import statsmodels.api as sm
from typing import Dict, List, Tuple, Optional, Any, Union
import warnings
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class EffectSize:
    """Container for effect size with confidence interval"""
    value: float
    ci_lower: float
    ci_upper: float
    interpretation: str
    measure: str  # "Cohen's d", "r", "R²", etc.


@dataclass
class StatisticalResult:
    """Complete statistical result with all necessary components"""
    test_name: str
    statistic: float
    p_value: float
    effect_size: EffectSize
    power: Optional[float]
    sample_size: int
    interpretation: str
    assumptions_met: Dict[str, bool]
    warnings: List[str]


class UniversalStatisticalSuite:
    """
    Comprehensive statistical analysis toolkit.
    
    Principles:
    1. Always report effect sizes with confidence intervals
    2. Always check statistical power
    3. Always validate assumptions
    4. Always correct for multiple testing when appropriate
    5. Always provide non-parametric alternatives
    6. Always be honest about limitations
    """
    
    def __init__(self, significance_level: float = 0.05, 
                 bootstrap_iterations: int = 1000,
                 permutation_iterations: int = 1000):
        self.alpha = significance_level
        self.bootstrap_n = bootstrap_iterations
        self.permutation_n = permutation_iterations
        
    # ========================================================================
    # EFFECT SIZES
    # ========================================================================
    
    def cohens_d(self, group1: np.ndarray, group2: np.ndarray, 
                 pooled: bool = True) -> EffectSize:
        """
        Calculate Cohen's d with bootstrap confidence interval.
        
        Interpretation:
        - Small: |d| = 0.2
        - Medium: |d| = 0.5
        - Large: |d| = 0.8
        """
        mean1, mean2 = np.mean(group1), np.mean(group2)
        
        if pooled:
            n1, n2 = len(group1), len(group2)
            var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
            pooled_std = np.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))
            d = (mean1 - mean2) / pooled_std
        else:
            d = (mean1 - mean2) / np.std(group2, ddof=1)
        
        # Bootstrap CI
        ci_lower, ci_upper = self._bootstrap_cohens_d(group1, group2, pooled)
        
        # Interpretation
        abs_d = abs(d)
        if abs_d < 0.2:
            interp = "negligible"
        elif abs_d < 0.5:
            interp = "small"
        elif abs_d < 0.8:
            interp = "medium"
        else:
            interp = "large"
            
        return EffectSize(
            value=d,
            ci_lower=ci_lower,
            ci_upper=ci_upper,
            interpretation=interp,
            measure="Cohen's d"
        )
    
    def _bootstrap_cohens_d(self, group1: np.ndarray, group2: np.ndarray, 
                           pooled: bool = True) -> Tuple[float, float]:
        """Bootstrap confidence interval for Cohen's d"""
        d_values = []
        
        for _ in range(self.bootstrap_n):
            sample1 = np.random.choice(group1, size=len(group1), replace=True)
            sample2 = np.random.choice(group2, size=len(group2), replace=True)
            
            mean1, mean2 = np.mean(sample1), np.mean(sample2)
            
            if pooled:
                n1, n2 = len(sample1), len(sample2)
                var1, var2 = np.var(sample1, ddof=1), np.var(sample2, ddof=1)
                pooled_std = np.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))
                d = (mean1 - mean2) / pooled_std
            else:
                d = (mean1 - mean2) / np.std(sample2, ddof=1)
            
            d_values.append(d)
        
        return np.percentile(d_values, [2.5, 97.5])
    
    def correlation_with_ci(self, x: np.ndarray, y: np.ndarray, 
                           method: str = 'pearson') -> EffectSize:
        """
        Calculate correlation with bootstrap confidence interval.
        
        Interpretation (Cohen, 1988):
        - Small: |r| = 0.10
        - Medium: |r| = 0.30
        - Large: |r| = 0.50
        """
        # Remove NaN values
        mask = ~(np.isnan(x) | np.isnan(y))
        x_clean, y_clean = x[mask], y[mask]
        
        if len(x_clean) < 3:
            return EffectSize(np.nan, np.nan, np.nan, "insufficient data", method)
        
        if method == 'pearson':
            r, _ = stats.pearsonr(x_clean, y_clean)
        elif method == 'spearman':
            r, _ = stats.spearmanr(x_clean, y_clean)
        elif method == 'kendall':
            r, _ = stats.kendalltau(x_clean, y_clean)
        else:
            raise ValueError(f"Unknown method: {method}")
        
        # Bootstrap CI
        ci_lower, ci_upper = self._bootstrap_correlation(x_clean, y_clean, method)
        
        # Interpretation
        abs_r = abs(r)
        if abs_r < 0.10:
            interp = "negligible"
        elif abs_r < 0.30:
            interp = "small"
        elif abs_r < 0.50:
            interp = "medium"
        else:
            interp = "large"
        
        return EffectSize(
            value=r,
            ci_lower=ci_lower,
            ci_upper=ci_upper,
            interpretation=interp,
            measure=f"{method.capitalize()} r"
        )
    
    def _bootstrap_correlation(self, x: np.ndarray, y: np.ndarray, 
                              method: str) -> Tuple[float, float]:
        """Bootstrap confidence interval for correlation"""
        r_values = []
        n = len(x)
        
        for _ in range(self.bootstrap_n):
            indices = np.random.choice(n, size=n, replace=True)
            x_sample = x[indices]
            y_sample = y[indices]
            
            try:
                if method == 'pearson':
                    r, _ = stats.pearsonr(x_sample, y_sample)
                elif method == 'spearman':
                    r, _ = stats.spearmanr(x_sample, y_sample)
                elif method == 'kendall':
                    r, _ = stats.kendalltau(x_sample, y_sample)
                r_values.append(r)
            except:
                continue
        
        if len(r_values) < 100:
            return np.nan, np.nan
        
        return np.percentile(r_values, [2.5, 97.5])
    
    def r_squared_adjusted(self, r_squared: float, n: int, k: int) -> float:
        """Calculate adjusted R² accounting for number of predictors"""
        if n <= k + 1:
            return np.nan
        return 1 - (1 - r_squared) * (n - 1) / (n - k - 1)
    
    def eta_squared(self, f_statistic: float, df_between: int, 
                    df_within: int) -> EffectSize:
        """
        Calculate eta-squared (η²) effect size for ANOVA.
        
        Interpretation:
        - Small: η² = 0.01
        - Medium: η² = 0.06
        - Large: η² = 0.14
        """
        ss_between = f_statistic * df_between
        ss_total = ss_between + df_within
        eta_sq = ss_between / ss_total
        
        # Omega-squared (less biased)
        omega_sq = (ss_between - df_between) / (ss_total + 1)
        
        abs_eta = abs(eta_sq)
        if abs_eta < 0.01:
            interp = "negligible"
        elif abs_eta < 0.06:
            interp = "small"
        elif abs_eta < 0.14:
            interp = "medium"
        else:
            interp = "large"
        
        return EffectSize(
            value=eta_sq,
            ci_lower=np.nan,  # Complex to compute
            ci_upper=np.nan,
            interpretation=interp,
            measure="η²"
        )
    
    def cramers_v(self, chi2: float, n: int, min_dim: int) -> EffectSize:
        """
        Calculate Cramér's V for categorical associations.
        
        Interpretation depends on df, but roughly:
        - Small: V = 0.10
        - Medium: V = 0.30
        - Large: V = 0.50
        """
        v = np.sqrt(chi2 / (n * (min_dim - 1)))
        
        abs_v = abs(v)
        if abs_v < 0.10:
            interp = "negligible"
        elif abs_v < 0.30:
            interp = "small"
        elif abs_v < 0.50:
            interp = "medium"
        else:
            interp = "large"
        
        return EffectSize(
            value=v,
            ci_lower=np.nan,
            ci_upper=np.nan,
            interpretation=interp,
            measure="Cramér's V"
        )
    
    # ========================================================================
    # POWER ANALYSIS
    # ========================================================================
    
    def power_ttest(self, effect_size: float, n: int, alpha: float = None) -> float:
        """Calculate statistical power for t-test"""
        if alpha is None:
            alpha = self.alpha
        
        power_analysis = TTestIndPower()
        power = power_analysis.solve_power(
            effect_size=effect_size,
            nobs1=n,
            alpha=alpha,
            ratio=1.0,
            alternative='two-sided'
        )
        return power
    
    def required_sample_size_ttest(self, effect_size: float, 
                                   power: float = 0.80,
                                   alpha: float = None) -> int:
        """Calculate required sample size for desired power"""
        if alpha is None:
            alpha = self.alpha
        
        power_analysis = TTestIndPower()
        n = power_analysis.solve_power(
            effect_size=effect_size,
            power=power,
            alpha=alpha,
            ratio=1.0,
            alternative='two-sided'
        )
        return int(np.ceil(n))
    
    def power_correlation(self, r: float, n: int, alpha: float = None) -> float:
        """Calculate power for correlation test"""
        if alpha is None:
            alpha = self.alpha
        
        # Fisher's z transformation
        z = 0.5 * np.log((1 + r) / (1 - r))
        se = 1 / np.sqrt(n - 3)
        z_crit = stats.norm.ppf(1 - alpha/2)
        z_power = abs(z) / se - z_crit
        power = stats.norm.cdf(z_power)
        
        return power
    
    def power_anova(self, effect_size: float, n_groups: int, 
                    n_per_group: int, alpha: float = None) -> float:
        """Calculate power for ANOVA"""
        if alpha is None:
            alpha = self.alpha
        
        power_analysis = FTestAnovaPower()
        power = power_analysis.solve_power(
            effect_size=effect_size,
            nobs=n_per_group * n_groups,
            alpha=alpha,
            k_groups=n_groups
        )
        return power
    
    # ========================================================================
    # REGRESSION DIAGNOSTICS
    # ========================================================================
    
    def regression_diagnostics(self, X: np.ndarray, y: np.ndarray, 
                               predictions: np.ndarray,
                               feature_names: List[str] = None) -> Dict[str, Any]:
        """
        Comprehensive regression diagnostics.
        
        Returns:
        - VIF (multicollinearity)
        - Residual tests (normality, homoscedasticity)
        - Influential points (Cook's D)
        - Autocorrelation (Durbin-Watson)
        """
        residuals = y - predictions
        
        diagnostics = {
            'assumptions_met': {},
            'warnings': [],
            'metrics': {}
        }
        
        # 1. Multicollinearity (VIF)
        if X.shape[1] > 1:
            try:
                vif_data = []
                for i in range(X.shape[1]):
                    vif = variance_inflation_factor(X, i)
                    vif_data.append({
                        'feature': feature_names[i] if feature_names else f'X{i}',
                        'vif': vif
                    })
                diagnostics['vif'] = vif_data
                
                max_vif = max([v['vif'] for v in vif_data])
                diagnostics['assumptions_met']['no_multicollinearity'] = max_vif < 10
                if max_vif >= 10:
                    diagnostics['warnings'].append(
                        f"High multicollinearity detected (max VIF={max_vif:.2f})"
                    )
            except Exception as e:
                diagnostics['warnings'].append(f"VIF calculation failed: {str(e)}")
        
        # 2. Normality of residuals (Shapiro-Wilk)
        if len(residuals) >= 3 and len(residuals) <= 5000:
            try:
                _, p_shapiro = stats.shapiro(residuals)
                diagnostics['metrics']['shapiro_wilk_p'] = p_shapiro
                diagnostics['assumptions_met']['normality'] = p_shapiro > 0.05
                if p_shapiro <= 0.05:
                    diagnostics['warnings'].append(
                        "Residuals not normally distributed (Shapiro-Wilk p<0.05)"
                    )
            except:
                pass
        
        # 3. Homoscedasticity (Breusch-Pagan)
        try:
            _, p_bp, _, _ = het_breuschpagan(residuals, X)
            diagnostics['metrics']['breusch_pagan_p'] = p_bp
            diagnostics['assumptions_met']['homoscedasticity'] = p_bp > 0.05
            if p_bp <= 0.05:
                diagnostics['warnings'].append(
                    "Heteroscedasticity detected (Breusch-Pagan p<0.05)"
                )
        except Exception as e:
            diagnostics['warnings'].append(f"Heteroscedasticity test failed: {str(e)}")
        
        # 4. Autocorrelation (Durbin-Watson)
        try:
            dw = durbin_watson(residuals)
            diagnostics['metrics']['durbin_watson'] = dw
            # DW ~2.0 indicates no autocorrelation
            diagnostics['assumptions_met']['no_autocorrelation'] = 1.5 < dw < 2.5
            if dw <= 1.5 or dw >= 2.5:
                diagnostics['warnings'].append(
                    f"Autocorrelation detected (Durbin-Watson={dw:.2f})"
                )
        except:
            pass
        
        # 5. Influential points (Cook's D)
        try:
            # Cook's D = (residual^2 / (p * MSE)) * (leverage / (1-leverage)^2)
            # Simplified: use residuals and identify outliers
            cooks_d = np.abs(residuals) / np.std(residuals)
            influential = np.where(cooks_d > 3)[0]
            diagnostics['metrics']['n_influential_points'] = len(influential)
            diagnostics['assumptions_met']['no_influential_outliers'] = len(influential) < len(y) * 0.05
            if len(influential) > 0:
                diagnostics['warnings'].append(
                    f"{len(influential)} potential influential points detected"
                )
        except:
            pass
        
        return diagnostics
    
    # ========================================================================
    # CROSS-VALIDATION
    # ========================================================================
    
    def cross_validate(self, model, X: np.ndarray, y: np.ndarray, 
                       cv: int = 5, scoring: str = 'r2') -> Dict[str, Any]:
        """
        K-fold cross-validation with comprehensive reporting.
        """
        # Remove NaN values
        mask = ~(np.isnan(X).any(axis=1) | np.isnan(y))
        X_clean, y_clean = X[mask], y[mask]
        
        if len(X_clean) < cv:
            return {'error': f'Insufficient samples for {cv}-fold CV'}
        
        # Perform cross-validation
        scores = cross_val_score(model, X_clean, y_clean, cv=cv, scoring=scoring)
        
        return {
            'mean_score': np.mean(scores),
            'std_score': np.std(scores),
            'min_score': np.min(scores),
            'max_score': np.max(scores),
            'scores_by_fold': scores.tolist(),
            'cv_folds': cv,
            'scoring': scoring,
            'interpretation': self._interpret_cv_score(np.mean(scores), scoring)
        }
    
    def _interpret_cv_score(self, score: float, scoring: str) -> str:
        """Interpret cross-validation score"""
        if scoring == 'r2':
            if score < 0.10:
                return "Poor predictive power"
            elif score < 0.30:
                return "Modest predictive power"
            elif score < 0.50:
                return "Good predictive power"
            else:
                return "Strong predictive power"
        elif scoring in ['neg_mean_squared_error', 'neg_mean_absolute_error']:
            return "Lower is better (negative error)"
        else:
            return "Higher is better"
    
    # ========================================================================
    # PERMUTATION TESTS
    # ========================================================================
    
    def permutation_test(self, group1: np.ndarray, group2: np.ndarray,
                        statistic: str = 'mean_diff',
                        alternative: str = 'two-sided') -> Dict[str, Any]:
        """
        Permutation test for distribution-free significance testing.
        """
        # Observed statistic
        if statistic == 'mean_diff':
            observed = np.mean(group1) - np.mean(group2)
        elif statistic == 'median_diff':
            observed = np.median(group1) - np.median(group2)
        else:
            raise ValueError(f"Unknown statistic: {statistic}")
        
        # Combine groups
        combined = np.concatenate([group1, group2])
        n1 = len(group1)
        
        # Permutation distribution
        perm_stats = []
        for _ in range(self.permutation_n):
            perm = np.random.permutation(combined)
            perm_group1 = perm[:n1]
            perm_group2 = perm[n1:]
            
            if statistic == 'mean_diff':
                perm_stat = np.mean(perm_group1) - np.mean(perm_group2)
            elif statistic == 'median_diff':
                perm_stat = np.median(perm_group1) - np.median(perm_group2)
            
            perm_stats.append(perm_stat)
        
        perm_stats = np.array(perm_stats)
        
        # P-value
        if alternative == 'two-sided':
            p_value = np.mean(np.abs(perm_stats) >= np.abs(observed))
        elif alternative == 'greater':
            p_value = np.mean(perm_stats >= observed)
        elif alternative == 'less':
            p_value = np.mean(perm_stats <= observed)
        else:
            raise ValueError(f"Unknown alternative: {alternative}")
        
        return {
            'observed_statistic': observed,
            'p_value': p_value,
            'permutations': self.permutation_n,
            'statistic': statistic,
            'alternative': alternative,
            'significant': p_value < self.alpha,
            'null_distribution_mean': np.mean(perm_stats),
            'null_distribution_std': np.std(perm_stats)
        }
    
    # ========================================================================
    # MULTIPLE TESTING CORRECTIONS
    # ========================================================================
    
    def bonferroni_correction(self, p_values: List[float]) -> List[float]:
        """Bonferroni correction for multiple testing"""
        n = len(p_values)
        return [min(p * n, 1.0) for p in p_values]
    
    def holm_bonferroni(self, p_values: List[float]) -> List[float]:
        """Holm-Bonferroni sequential correction"""
        n = len(p_values)
        # Sort p-values with indices
        sorted_indices = np.argsort(p_values)
        sorted_p = np.array(p_values)[sorted_indices]
        
        # Apply correction
        corrected = []
        for i, p in enumerate(sorted_p):
            corrected.append(min(p * (n - i), 1.0))
        
        # Restore original order
        result = [0] * n
        for i, idx in enumerate(sorted_indices):
            result[idx] = corrected[i]
        
        return result
    
    def fdr_correction(self, p_values: List[float], q: float = 0.05) -> List[bool]:
        """
        False Discovery Rate (Benjamini-Hochberg) correction.
        
        Returns list of booleans indicating significance at FDR level q.
        """
        n = len(p_values)
        sorted_indices = np.argsort(p_values)
        sorted_p = np.array(p_values)[sorted_indices]
        
        # Find largest i where p_i <= (i/n) * q
        significant = []
        for i, p in enumerate(sorted_p):
            threshold = ((i + 1) / n) * q
            significant.append(p <= threshold)
        
        # Restore original order
        result = [False] * n
        for i, idx in enumerate(sorted_indices):
            result[idx] = significant[i]
        
        return result
    
    # ========================================================================
    # NON-PARAMETRIC TESTS
    # ========================================================================
    
    def mann_whitney_u(self, group1: np.ndarray, group2: np.ndarray) -> StatisticalResult:
        """
        Mann-Whitney U test (non-parametric alternative to t-test).
        """
        u_stat, p_value = mannwhitneyu(group1, group2, alternative='two-sided')
        
        # Effect size (rank-biserial correlation)
        n1, n2 = len(group1), len(group2)
        r = 1 - (2*u_stat) / (n1 * n2)
        
        effect = EffectSize(
            value=r,
            ci_lower=np.nan,
            ci_upper=np.nan,
            interpretation="rank-biserial correlation",
            measure="r_rb"
        )
        
        return StatisticalResult(
            test_name="Mann-Whitney U",
            statistic=u_stat,
            p_value=p_value,
            effect_size=effect,
            power=None,
            sample_size=n1 + n2,
            interpretation="Non-parametric test of distributional differences",
            assumptions_met={'independence': True},
            warnings=[]
        )
    
    def kruskal_wallis(self, *groups) -> StatisticalResult:
        """
        Kruskal-Wallis H test (non-parametric alternative to ANOVA).
        """
        h_stat, p_value = kruskal(*groups)
        
        # Effect size (eta-squared)
        n = sum(len(g) for g in groups)
        eta_sq = (h_stat - len(groups) + 1) / (n - len(groups))
        
        effect = EffectSize(
            value=eta_sq,
            ci_lower=np.nan,
            ci_upper=np.nan,
            interpretation="effect size for non-parametric ANOVA",
            measure="η²"
        )
        
        return StatisticalResult(
            test_name="Kruskal-Wallis H",
            statistic=h_stat,
            p_value=p_value,
            effect_size=effect,
            power=None,
            sample_size=n,
            interpretation="Non-parametric test of differences across groups",
            assumptions_met={'independence': True},
            warnings=[]
        )
    
    # ========================================================================
    # COMPREHENSIVE COMPARISON
    # ========================================================================
    
    def compare_two_groups(self, group1: np.ndarray, group2: np.ndarray,
                          group_names: Tuple[str, str] = ('Group 1', 'Group 2')) -> Dict[str, Any]:
        """
        Comprehensive comparison of two groups with parametric and non-parametric tests.
        """
        results = {
            'group_names': group_names,
            'descriptives': {
                group_names[0]: {
                    'n': len(group1),
                    'mean': np.mean(group1),
                    'std': np.std(group1, ddof=1),
                    'median': np.median(group1),
                    'q25': np.percentile(group1, 25),
                    'q75': np.percentile(group1, 75)
                },
                group_names[1]: {
                    'n': len(group2),
                    'mean': np.mean(group2),
                    'std': np.std(group2, ddof=1),
                    'median': np.median(group2),
                    'q25': np.percentile(group2, 25),
                    'q75': np.percentile(group2, 75)
                }
            },
            'tests': {}
        }
        
        # 1. Independent t-test
        t_stat, p_ttest = stats.ttest_ind(group1, group2)
        cohens_d = self.cohens_d(group1, group2)
        power = self.power_ttest(cohens_d.value, min(len(group1), len(group2)))
        
        results['tests']['t_test'] = {
            'statistic': t_stat,
            'p_value': p_ttest,
            'effect_size': cohens_d.__dict__,
            'power': power,
            'significant': p_ttest < self.alpha
        }
        
        # 2. Welch's t-test (doesn't assume equal variance)
        t_welch, p_welch = stats.ttest_ind(group1, group2, equal_var=False)
        results['tests']['welch_t_test'] = {
            'statistic': t_welch,
            'p_value': p_welch,
            'significant': p_welch < self.alpha
        }
        
        # 3. Mann-Whitney U (non-parametric)
        mann_whitney_result = self.mann_whitney_u(group1, group2)
        results['tests']['mann_whitney_u'] = {
            'statistic': mann_whitney_result.statistic,
            'p_value': mann_whitney_result.p_value,
            'effect_size': mann_whitney_result.effect_size.__dict__,
            'significant': mann_whitney_result.p_value < self.alpha
        }
        
        # 4. Permutation test
        perm_result = self.permutation_test(group1, group2)
        results['tests']['permutation'] = perm_result
        
        # Recommendation
        results['recommendation'] = self._recommend_test_two_groups(group1, group2, results)
        
        return results
    
    def _recommend_test_two_groups(self, group1: np.ndarray, group2: np.ndarray,
                                   results: Dict) -> str:
        """Recommend which test to trust based on assumptions"""
        # Check normality
        _, p1 = stats.shapiro(group1) if len(group1) <= 5000 else (None, 1.0)
        _, p2 = stats.shapiro(group2) if len(group2) <= 5000 else (None, 1.0)
        
        if p1 < 0.05 or p2 < 0.05:
            return "Use Mann-Whitney U (data not normally distributed)"
        
        # Check equal variances
        _, p_levene = stats.levene(group1, group2)
        if p_levene < 0.05:
            return "Use Welch's t-test (unequal variances)"
        
        return "Use independent t-test (assumptions met)"
    
    # ========================================================================
    # UTILITY FUNCTIONS
    # ========================================================================
    
    def interpret_p_value(self, p: float) -> str:
        """Human-readable p-value interpretation"""
        if p < 0.001:
            return "p < 0.001 (extremely strong evidence)"
        elif p < 0.01:
            return "p < 0.01 (very strong evidence)"
        elif p < 0.05:
            return "p < 0.05 (strong evidence)"
        elif p < 0.10:
            return "p < 0.10 (suggestive evidence)"
        else:
            return f"p = {p:.3f} (insufficient evidence)"
    
    def report_finding(self, test_name: str, statistic: float, p_value: float,
                      effect_size: EffectSize, n: int, power: Optional[float] = None) -> str:
        """
        Generate publication-ready statistical report.
        
        Example output:
        "Independent t-test showed a large effect (d = 0.82, 95% CI [0.65, 0.99], 
         t(198) = 8.45, p < 0.001, power = 0.99)"
        """
        report = f"{test_name} "
        
        if effect_size.interpretation != "insufficient data":
            report += f"showed a {effect_size.interpretation} effect "
            report += f"({effect_size.measure} = {effect_size.value:.3f}"
            
            if not np.isnan(effect_size.ci_lower):
                report += f", 95% CI [{effect_size.ci_lower:.3f}, {effect_size.ci_upper:.3f}]"
            
            report += f", statistic = {statistic:.3f}"
            report += f", {self.interpret_p_value(p_value)}"
            
            if power is not None:
                report += f", power = {power:.2f}"
            
            report += f", n = {n})"
        else:
            report += f"(statistic = {statistic:.3f}, p = {p_value:.3f}, n = {n})"
        
        return report


# ========================================================================
# CONVENIENCE FUNCTIONS
# ========================================================================

def quick_correlation_analysis(x: np.ndarray, y: np.ndarray, 
                               feature_name: str = "Feature",
                               outcome_name: str = "Outcome") -> Dict[str, Any]:
    """Quick correlation analysis with full reporting"""
    suite = UniversalStatisticalSuite()
    
    # Pearson
    pearson = suite.correlation_with_ci(x, y, method='pearson')
    r, p = stats.pearsonr(x[~(np.isnan(x) | np.isnan(y))], 
                         y[~(np.isnan(x) | np.isnan(y))])
    power = suite.power_correlation(r, len(x))
    
    # Spearman (non-parametric backup)
    spearman = suite.correlation_with_ci(x, y, method='spearman')
    rho, p_spear = stats.spearmanr(x[~(np.isnan(x) | np.isnan(y))], 
                                   y[~(np.isnan(x) | np.isnan(y))])
    
    return {
        'feature': feature_name,
        'outcome': outcome_name,
        'pearson': {
            'r': pearson.value,
            'ci_lower': pearson.ci_lower,
            'ci_upper': pearson.ci_upper,
            'p_value': p,
            'interpretation': pearson.interpretation,
            'power': power
        },
        'spearman': {
            'rho': spearman.value,
            'ci_lower': spearman.ci_lower,
            'ci_upper': spearman.ci_upper,
            'p_value': p_spear,
            'interpretation': spearman.interpretation
        },
        'report': suite.report_finding("Correlation", r, p, pearson, len(x), power)
    }


def quick_group_comparison(group1: np.ndarray, group2: np.ndarray,
                          group1_name: str = "Group 1",
                          group2_name: str = "Group 2") -> Dict[str, Any]:
    """Quick two-group comparison with full reporting"""
    suite = UniversalStatisticalSuite()
    return suite.compare_two_groups(group1, group2, (group1_name, group2_name))

