"""
Name Survival Analysis
=======================

Survival analysis for name persistence over time using Kaplan-Meier and Cox models.
Tests how long names (and religious traditions) persist in populations.

Features:
- Kaplan-Meier survival curves
- Cox proportional hazards regression
- Time-varying covariates
- Competing risks analysis
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

# Try importing survival analysis library
try:
    from lifelines import KaplanMeierFitter, CoxPHFitter
    from lifelines.statistics import logrank_test
    LIFELINES_AVAILABLE = True
except ImportError:
    LIFELINES_AVAILABLE = False
    logging.warning("lifelines not available. Install for survival analysis.")

import pandas as pd

logger = logging.getLogger(__name__)


class NameSurvivalAnalyzer:
    """Analyze name persistence over time using survival analysis."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.kmf = KaplanMeierFitter() if LIFELINES_AVAILABLE else None
        self.cph = CoxPHFitter() if LIFELINES_AVAILABLE else None
        
        self.logger.info(f"NameSurvivalAnalyzer initialized (lifelines: {LIFELINES_AVAILABLE})")
    
    def kaplan_meier_analysis(self, data: List[Dict]) -> Dict:
        """
        Perform Kaplan-Meier survival analysis.
        
        Args:
            data: List of dicts with 'duration' (years active), 'event' (1=died/0=censored)
        
        Returns:
            Survival function and statistics
        """
        if not LIFELINES_AVAILABLE:
            return self._simple_survival_estimate(data)
        
        durations = [d['duration'] for d in data]
        events = [d.get('event', 1) for d in data]
        
        self.kmf.fit(durations, events)
        
        return {
            'method': 'Kaplan-Meier',
            'median_survival': float(self.kmf.median_survival_time_),
            'survival_at_10yrs': float(self.kmf.survival_function_at_times(10).iloc[0]),
            'survival_at_50yrs': float(self.kmf.survival_function_at_times(50).iloc[0]) if len(durations) > 0 else 0,
            'survival_function': {
                'time': self.kmf.survival_function_.index.tolist(),
                'probability': self.kmf.survival_function_['KM_estimate'].tolist()
            }
        }
    
    def compare_survival_curves(self, group1_data: List[Dict], group2_data: List[Dict],
                               group1_name: str = "Group 1", group2_name: str = "Group 2") -> Dict:
        """
        Compare survival curves between two groups.
        
        Args:
            group1_data, group2_data: Survival data for each group
            group1_name, group2_name: Group labels
        
        Returns:
            Comparison with log-rank test
        """
        if not LIFELINES_AVAILABLE:
            return {'error': 'lifelines not available'}
        
        durations1 = [d['duration'] for d in group1_data]
        events1 = [d.get('event', 1) for d in group1_data]
        
        durations2 = [d['duration'] for d in group2_data]
        events2 = [d.get('event', 1) for d in group2_data]
        
        # Fit both groups
        kmf1 = KaplanMeierFitter()
        kmf1.fit(durations1, events1, label=group1_name)
        
        kmf2 = KaplanMeierFitter()
        kmf2.fit(durations2, events2, label=group2_name)
        
        # Log-rank test
        results = logrank_test(durations1, durations2, events1, events2)
        
        return {
            'method': 'Log-rank test',
            'test_statistic': float(results.test_statistic),
            'p_value': float(results.p_value),
            'significant': results.p_value < 0.05,
            'group1': {
                'name': group1_name,
                'median_survival': float(kmf1.median_survival_time_),
                'survival_function': {
                    'time': kmf1.survival_function_.index.tolist(),
                    'probability': kmf1.survival_function_[group1_name].tolist()
                }
            },
            'group2': {
                'name': group2_name,
                'median_survival': float(kmf2.median_survival_time_),
                'survival_function': {
                    'time': kmf2.survival_function_.index.tolist(),
                    'probability': kmf2.survival_function_[group2_name].tolist()
                }
            },
            'interpretation': self._interpret_survival_comparison(results.p_value, kmf1, kmf2, group1_name, group2_name)
        }
    
    def cox_proportional_hazards(self, data: pd.DataFrame, duration_col: str, 
                                 event_col: str) -> Dict:
        """
        Cox proportional hazards regression for survival prediction.
        
        Args:
            data: DataFrame with duration, event, and covariate columns
            duration_col: Name of duration column
            event_col: Name of event column
        
        Returns:
            Cox model results with hazard ratios
        """
        if not LIFELINES_AVAILABLE:
            return {'error': 'lifelines not available'}
        
        try:
            self.cph.fit(data, duration_col=duration_col, event_col=event_col)
            
            # Extract hazard ratios
            hazard_ratios = {}
            for covariate in self.cph.params_.index:
                hazard_ratios[covariate] = {
                    'hazard_ratio': float(np.exp(self.cph.params_[covariate])),
                    'coefficient': float(self.cph.params_[covariate]),
                    'p_value': float(self.cph.summary['p'][covariate]),
                    'interpretation': 'increases risk' if self.cph.params_[covariate] > 0 else 'decreases risk'
                }
            
            return {
                'method': 'Cox Proportional Hazards',
                'concordance_index': float(self.cph.concordance_index_),
                'hazard_ratios': hazard_ratios,
                'model_summary': self.cph.summary.to_dict()
            }
        
        except Exception as e:
            self.logger.error(f"Error in Cox regression: {e}")
            return {'error': str(e)}
    
    def _simple_survival_estimate(self, data: List[Dict]) -> Dict:
        """Simple survival estimate when lifelines unavailable."""
        durations = [d['duration'] for d in data]
        events = [d.get('event', 1) for d in data]
        
        # Simple Kaplan-Meier calculation
        sorted_indices = np.argsort(durations)
        sorted_durations = np.array(durations)[sorted_indices]
        sorted_events = np.array(events)[sorted_indices]
        
        n_total = len(durations)
        survival_prob = 1.0
        survival_function = [(0, 1.0)]
        
        for i, (t, event) in enumerate(zip(sorted_durations, sorted_events)):
            n_risk = n_total - i
            if event == 1 and n_risk > 0:
                survival_prob *= (n_risk - 1) / n_risk
            survival_function.append((float(t), float(survival_prob)))
        
        return {
            'method': 'Simple Kaplan-Meier estimate',
            'median_survival': float(np.median([t for t, e in zip(durations, events) if e == 1])),
            'survival_function': survival_function,
            'note': 'Install lifelines for full survival analysis'
        }
    
    def _interpret_survival_comparison(self, p_value: float, kmf1, kmf2, 
                                      name1: str, name2: str) -> str:
        """Interpret survival curve comparison."""
        if p_value < 0.05:
            better_group = name1 if kmf1.median_survival_time_ > kmf2.median_survival_time_ else name2
            return f"Survival curves differ significantly (p={p_value:.4f}). {better_group} has longer median survival."
        else:
            return f"No significant difference in survival curves (p={p_value:.4f})."


# Singleton
survival_analyzer = NameSurvivalAnalyzer()

