"""
Longitudinal Validator
Test stability of effects across eras (1950s-2020s)
Theory: Universal constant should be stable over time
Expected Impact: Foundation validation, risk assessment
"""

from typing import Dict, List, Tuple
import numpy as np
from scipy import stats
import logging

logger = logging.getLogger(__name__)


class LongitudinalValidator:
    """Validate effect stability across historical periods"""
    
    def __init__(self):
        """Initialize validator"""
        self.era_definitions = self._define_eras()
    
    def _define_eras(self) -> Dict:
        """Define historical eras for analysis"""
        return {
            'pre_analytics': {
                'years': (1950, 1999),
                'label': 'Pre-Analytics Era',
                'characteristics': 'Traditional scouting, eye test dominant'
            },
            'early_analytics': {
                'years': (2000, 2009),
                'label': 'Early Analytics Era',
                'characteristics': 'Moneyball emergence, stats beginning to matter'
            },
            'analytics': {
                'years': (2010, 2019),
                'label': 'Analytics Era',
                'characteristics': 'Data-driven decisions, advanced metrics standard'
            },
            'modern': {
                'years': (2020, 2025),
                'label': 'Modern Era',
                'characteristics': 'AI, comprehensive tracking, total information'
            }
        }
    
    def test_era_stability(self, era_correlations: Dict[str, float]) -> Dict:
        """
        Test if correlations are stable across eras
        
        Args:
            era_correlations: Dict mapping era name to correlation value
            
        Returns:
            Stability analysis
        """
        if len(era_correlations) < 3:
            return {'error': 'Need at least 3 eras for stability test'}
        
        eras = list(era_correlations.keys())
        correlations = list(era_correlations.values())
        
        # Test for trend
        era_indices = list(range(len(eras)))
        slope, intercept, r_value, p_value, std_err = stats.linregress(era_indices, correlations)
        
        # Test for heterogeneity
        mean_corr = np.mean(correlations)
        variance = np.var(correlations)
        
        # Classify stability
        if abs(slope) < 0.01 and p_value > 0.10:
            stability = 'STABLE'
            interpretation = 'Effect is stable across eras - robust finding'
            risk_assessment = 'LOW'
        elif abs(slope) < 0.02 and p_value > 0.05:
            stability = 'MOSTLY_STABLE'
            interpretation = 'Effect shows minor variation but generally consistent'
            risk_assessment = 'LOW-MODERATE'
        elif p_value < 0.05 and slope > 0:
            stability = 'INCREASING'
            interpretation = 'Effect is getting stronger over time - modern era amplification'
            risk_assessment = 'LOW' 
        elif p_value < 0.05 and slope < 0:
            stability = 'DECREASING'
            interpretation = 'Effect is weakening over time - market efficiency increasing?'
            risk_assessment = 'MODERATE-HIGH'
        else:
            stability = 'UNSTABLE'
            interpretation = 'Effect shows high variability across eras'
            risk_assessment = 'HIGH'
        
        return {
            'eras_tested': len(eras),
            'mean_correlation': round(mean_corr, 4),
            'variance': round(variance, 4),
            'trend_slope': round(slope, 6),
            'trend_p_value': round(p_value, 4),
            'stability': stability,
            'interpretation': interpretation,
            'risk_assessment': risk_assessment,
            'era_breakdown': dict(zip(eras, [round(c, 4) for c in correlations]))
        }
    
    def test_universal_constant_stability(self, era_ratios: Dict[str, float]) -> Dict:
        """
        Test if universal constant (1.344) is stable across eras
        
        Args:
            era_ratios: Dict mapping era to observed ratio
            
        Returns:
            Constant stability analysis
        """
        UNIVERSAL_CONSTANT = 1.344
        
        eras = list(era_ratios.keys())
        ratios = list(era_ratios.values())
        
        # Test if ratios cluster around 1.344
        mean_ratio = np.mean(ratios)
        std_ratio = np.std(ratios)
        
        # One-sample t-test against universal constant
        t_stat, p_value = stats.ttest_1samp(ratios, UNIVERSAL_CONSTANT)
        
        # Calculate coefficient of variation
        cv = (std_ratio / mean_ratio) * 100
        
        # Classify stability
        if abs(mean_ratio - UNIVERSAL_CONSTANT) < 0.05 and cv < 5:
            stability = 'HIGHLY_STABLE'
            confidence = 'VERY_HIGH'
            betting_implication = 'Universal constant fully validated - maximize confidence'
        elif abs(mean_ratio - UNIVERSAL_CONSTANT) < 0.10 and cv < 10:
            stability = 'STABLE'
            confidence = 'HIGH'
            betting_implication = 'Universal constant validated - use with confidence'
        elif p_value > 0.05:
            stability = 'CONSISTENT'
            confidence = 'MODERATE'
            betting_implication = 'Constant not significantly different from 1.344'
        else:
            stability = 'VARIABLE'
            confidence = 'LOW'
            betting_implication = 'Constant varies across eras - use era-specific values'
        
        return {
            'universal_constant': UNIVERSAL_CONSTANT,
            'observed_mean': round(mean_ratio, 4),
            'observed_std': round(std_ratio, 4),
            'coefficient_of_variation': round(cv, 2),
            't_statistic': round(t_stat, 3),
            'p_value': round(p_value, 4),
            'stability': stability,
            'confidence_level': confidence,
            'betting_implication': betting_implication,
            'era_ratios': {era: round(ratio, 4) for era, ratio in era_ratios.items()}
        }
    
    def validate_effect_persistence(self, historical_effects: List[Tuple[int, float]]) -> Dict:
        """
        Validate that effects persist over long time periods
        
        Args:
            historical_effects: List of (year, effect_size) tuples
            
        Returns:
            Persistence analysis
        """
        if len(historical_effects) < 10:
            return {'error': 'Need at least 10 years of data'}
        
        years, effects = zip(*historical_effects)
        
        # Test for persistence (autocorrelation)
        # If effects are persistent, correlation with lagged values should be high
        lagged_effects = effects[:-1]
        current_effects = effects[1:]
        
        autocorr, p_value = stats.pearsonr(lagged_effects, current_effects)
        
        # Test overall trend
        trend_slope, _, r_value, trend_p, _ = stats.linregress(years, effects)
        
        # Classify persistence
        if autocorr > 0.7 and p_value < 0.05:
            persistence = 'HIGH'
            interpretation = 'Effects highly persistent year-over-year - stable phenomenon'
        elif autocorr > 0.4 and p_value < 0.05:
            persistence = 'MODERATE'
            interpretation = 'Effects moderately persistent - generally reliable'
        elif autocorr > 0 and p_value < 0.10:
            persistence = 'LOW'
            interpretation = 'Weak persistence - effects may be unstable'
        else:
            persistence = 'NONE'
            interpretation = 'No significant persistence - high temporal variance'
        
        return {
            'years_analyzed': len(years),
            'time_span': f"{min(years)}-{max(years)}",
            'autocorrelation': round(autocorr, 4),
            'autocorr_p_value': round(p_value, 4),
            'trend_slope': round(trend_slope, 6),
            'trend_p_value': round(trend_p, 4),
            'persistence': persistence,
            'interpretation': interpretation,
            'mean_effect': round(np.mean(effects), 4),
            'effect_range': (round(min(effects), 4), round(max(effects), 4))
        }
    
    def cohort_analysis(self, cohorts: Dict[str, Dict]) -> Dict:
        """
        Analyze different cohorts (draft classes, position groups, etc.)
        
        Args:
            cohorts: Dict mapping cohort name to correlation data
            
        Returns:
            Cohort heterogeneity analysis
        """
        cohort_effects = []
        
        for cohort_name, cohort_data in cohorts.items():
            effect = cohort_data.get('correlation', 0)
            n = cohort_data.get('n', 0)
            
            if n >= 30:  # Minimum sample size
                cohort_effects.append({
                    'cohort': cohort_name,
                    'effect': effect,
                    'n': n
                })
        
        if len(cohort_effects) < 2:
            return {'error': 'Need at least 2 cohorts for comparison'}
        
        effects = [c['effect'] for c in cohort_effects]
        
        # Test homogeneity
        mean_effect = np.mean(effects)
        variance = np.var(effects)
        
        # Q-statistic for heterogeneity
        Q = sum([(e - mean_effect)**2 for e in effects])
        df = len(effects) - 1
        
        # I² statistic (percentage of variance due to heterogeneity)
        I_squared = max(0, ((Q - df) / Q) * 100)
        
        if I_squared < 25:
            heterogeneity = 'LOW'
            interpretation = 'Effect is homogeneous across cohorts - universal finding'
        elif I_squared < 50:
            heterogeneity = 'MODERATE'
            interpretation = 'Some cohort variation but generally consistent'
        elif I_squared < 75:
            heterogeneity = 'SUBSTANTIAL'
            interpretation = 'Significant cohort differences - context matters'
        else:
            heterogeneity = 'HIGH'
            interpretation = 'High heterogeneity - effect is cohort-specific'
        
        return {
            'cohorts_analyzed': len(cohort_effects),
            'mean_effect': round(mean_effect, 4),
            'effect_range': (round(min(effects), 4), round(max(effects), 4)),
            'Q_statistic': round(Q, 3),
            'I_squared': round(I_squared, 1),
            'heterogeneity': heterogeneity,
            'interpretation': interpretation,
            'cohort_details': cohort_effects
        }


if __name__ == "__main__":
    # Test longitudinal validator
    validator = LongitudinalValidator()
    
    print("="*80)
    print("LONGITUDINAL VALIDATION")
    print("="*80)
    
    # Test 1: Era stability
    print("\n1. ERA STABILITY TEST")
    print("-" * 80)
    
    era_corrs = {
        '1950s': 0.32,
        '1970s': 0.34,
        '1990s': 0.35,
        '2010s': 0.36,
        '2020s': 0.34
    }
    
    stability = validator.test_era_stability(era_corrs)
    print(f"Stability: {stability['stability']}")
    print(f"Trend slope: {stability['trend_slope']}")
    print(f"Interpretation: {stability['interpretation']}")
    print(f"Risk: {stability['risk_assessment']}")
    
    # Test 2: Universal constant stability
    print("\n2. UNIVERSAL CONSTANT STABILITY")
    print("-" * 80)
    
    era_ratios = {
        '1950s': 1.32,
        '1970s': 1.34,
        '1990s': 1.35,
        '2010s': 1.36,
        '2020s': 1.34
    }
    
    constant_test = validator.test_universal_constant_stability(era_ratios)
    print(f"Universal constant: {constant_test['universal_constant']}")
    print(f"Observed mean: {constant_test['observed_mean']}")
    print(f"CV: {constant_test['coefficient_of_variation']}%")
    print(f"Stability: {constant_test['stability']}")
    print(f"Confidence: {constant_test['confidence_level']}")
    print(f"Betting implication: {constant_test['betting_implication']}")
    
    print("\n" + "="*80)

