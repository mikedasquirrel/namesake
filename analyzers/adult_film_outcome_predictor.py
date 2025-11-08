"""
Adult Film Career Outcome Predictor
CRITICAL ANALYSIS: Do name patterns predict tragic outcomes?

This is serious research with potential protective value.
If certain phonetic patterns correlate with early exit or tragic outcomes,
that could identify risk factors worth studying further.
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict
from scipy import stats
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score

from core.models import db, AdultPerformer, AdultPerformerAnalysis

logger = logging.getLogger(__name__)


class CareerOutcomePredictor:
    """Predict career outcomes including tragic cases from name patterns"""
    
    def __init__(self):
        self.tragic_model = None
        self.early_exit_model = None
    
    def analyze_tragic_outcome_predictors(self) -> Dict:
        """
        CRITICAL: Analyze whether name patterns correlate with tragic outcomes
        
        This is not predictive in a deterministic sense - but if patterns exist,
        they could indicate risk factors worth understanding.
        
        Tragic outcomes include: suicide, overdose, violent death
        """
        
        query = db.session.query(AdultPerformer, AdultPerformerAnalysis).join(
            AdultPerformerAnalysis
        )
        
        data = []
        for p, a in query.all():
            data.append({
                'name': p.stage_name,
                'syllables': a.syllable_count or 0,
                'harshness': a.harshness_score or 0,
                'softness': a.softness_score or 0,
                'memorability': a.memorability_score or 0,
                'complexity': a.phonetic_complexity or 0,
                'uniqueness': a.uniqueness_score or 0,
                'fantasy_score': a.fantasy_score or 0,
                'sexy_score': a.sexy_score or 0,
                'alliteration': a.alliteration_score > 50 if a.alliteration_score else False,
                'tragic_outcome': p.tragic_outcome or False,
                'early_exit': p.early_exit or False,
                'career_outcome': p.career_outcome or 'unknown',
                'years_active': p.years_active or 0
            })
        
        df = pd.DataFrame(data)
        
        if len(df) < 30:
            return {
                'status': 'insufficient_data',
                'message': f'Need at least 30 performers, have {len(df)}',
                'note': 'This analysis requires larger sample for statistical power'
            }
        
        # Tragic outcomes analysis
        tragic_cases = df[df['tragic_outcome'] == True]
        non_tragic = df[df['tragic_outcome'] == False]
        
        results = {
            'status': 'complete',
            'sample_size': len(df),
            'tragic_cases': len(tragic_cases),
            'tragic_rate': float(len(tragic_cases) / len(df)) * 100,
            'pattern_analysis': {}
        }
        
        if len(tragic_cases) >= 3:
            # Compare name features between tragic and non-tragic
            features_to_test = ['syllables', 'harshness', 'softness', 'memorability', 
                                'complexity', 'uniqueness', 'fantasy_score', 'sexy_score']
            
            for feature in features_to_test:
                if feature in tragic_cases.columns and feature in non_tragic.columns:
                    tragic_mean = tragic_cases[feature].mean()
                    non_tragic_mean = non_tragic[feature].mean()
                    
                    if len(tragic_cases) > 1 and len(non_tragic) > 1:
                        try:
                            t_stat, p_value = stats.ttest_ind(tragic_cases[feature], non_tragic[feature])
                            
                            results['pattern_analysis'][feature] = {
                                'tragic_mean': float(tragic_mean),
                                'non_tragic_mean': float(non_tragic_mean),
                                'difference': float(tragic_mean - non_tragic_mean),
                                't_statistic': float(t_stat),
                                'p_value': float(p_value),
                                'significant': p_value < 0.10,  # Relaxed threshold for small sample
                                'interpretation': self._interpret_difference(feature, tragic_mean - non_tragic_mean, p_value)
                            }
                        except:
                            pass
            
            # Qualitative patterns
            results['tragic_names'] = tragic_cases['name'].tolist()
            results['avg_syllables_tragic'] = float(tragic_cases['syllables'].mean())
            results['avg_syllables_non_tragic'] = float(non_tragic['syllables'].mean())
            
        else:
            results['note'] = 'Too few tragic cases for statistical comparison'
        
        return results
    
    def analyze_early_exit_predictors(self) -> Dict:
        """
        Analyze whether name patterns predict early career exit (< 3-4 years)
        
        Early exit could indicate:
        - Poor name choice reducing success
        - Industry incompatibility
        - Personal factors
        
        If name patterns predict early exit, that's actionable information
        """
        
        query = db.session.query(AdultPerformer, AdultPerformerAnalysis).join(
            AdultPerformerAnalysis
        )
        
        data = []
        for p, a in query.all():
            early = (p.years_active or 0) < 4
            
            data.append({
                'name': p.stage_name,
                'syllables': a.syllable_count or 0,
                'memorability': a.memorability_score or 0,
                'accessibility': a.accessibility_score or 0,
                'brand_strength': a.brand_strength_score or 0,
                'complexity': a.phonetic_complexity or 0,
                'years_active': p.years_active or 0,
                'early_exit': early
            })
        
        df = pd.DataFrame(data)
        
        if len(df) < 20:
            return {'status': 'insufficient_data'}
        
        early_exit = df[df['early_exit'] == True]
        long_career = df[df['early_exit'] == False]
        
        results = {
            'status': 'complete',
            'sample_size': len(df),
            'early_exit_count': len(early_exit),
            'early_exit_rate': float(len(early_exit) / len(df)) * 100,
            'comparisons': {}
        }
        
        # Compare features
        if len(early_exit) >= 5 and len(long_career) >= 5:
            for feature in ['syllables', 'memorability', 'accessibility', 'brand_strength', 'complexity']:
                early_mean = early_exit[feature].mean()
                long_mean = long_career[feature].mean()
                
                try:
                    t_stat, p_value = stats.ttest_ind(early_exit[feature], long_career[feature])
                    
                    results['comparisons'][feature] = {
                        'early_exit_mean': float(early_mean),
                        'long_career_mean': float(long_mean),
                        'difference': float(early_mean - long_mean),
                        't_statistic': float(t_stat),
                        'p_value': float(p_value),
                        'significant': p_value < 0.05
                    }
                except:
                    pass
        
        return results
    
    def _interpret_difference(self, feature: str, diff: float, p_value: float) -> str:
        """Interpret what a difference means"""
        if p_value >= 0.10:
            return "No significant difference"
        
        direction = "higher" if diff > 0 else "lower"
        magnitude = "significantly" if p_value < 0.05 else "somewhat"
        
        interpretations = {
            'syllables': f"Tragic cases have {magnitude} {direction} syllable counts",
            'harshness': f"Tragic cases have {magnitude} {direction} phonetic harshness",
            'complexity': f"Tragic cases have {magnitude} {direction} name complexity",
            'memorability': f"Tragic cases have {magnitude} {direction} memorability scores"
        }
        
        return interpretations.get(feature, f"Tragic cases {direction} on {feature}")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, '.')
    from app import app
    
    with app.app_context():
        predictor = CareerOutcomePredictor()
        
        print("\n" + "="*70)
        print("CAREER OUTCOME PREDICTION ANALYSIS")
        print("="*70)
        print()
        
        # Tragic outcome analysis
        tragic_results = predictor.analyze_tragic_outcome_predictors()
        
        if tragic_results['status'] == 'complete':
            print(f"Sample: {tragic_results['sample_size']} performers")
            print(f"Tragic cases: {tragic_results['tragic_cases']} ({tragic_results['tragic_rate']:.1f}%)")
            print()
            print("Pattern Analysis:")
            for feature, analysis in tragic_results.get('pattern_analysis', {}).items():
                if analysis['significant']:
                    print(f"  {feature}: {analysis['interpretation']} (p={analysis['p_value']:.3f})")
        
        # Early exit analysis
        print()
        early_results = predictor.analyze_early_exit_predictors()
        
        if early_results['status'] == 'complete':
            print(f"Early exits: {early_results['early_exit_count']} ({early_results['early_exit_rate']:.1f}%)")
            print()
            print("Early Exit Predictors:")
            for feature, comp in early_results.get('comparisons', {}).items():
                if comp['significant']:
                    print(f"  {feature}: Early exit {comp['difference']:+.2f} different (p={comp['p_value']:.3f})")
        
        print()
        print("="*70)

