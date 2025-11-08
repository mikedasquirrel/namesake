"""
Cross-Sport Meta-Analyzer
Tests whether sport characteristics predict which linguistic features matter
The core hypothesis: Sport type determines name pattern importance
"""

import json
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CrossSportMetaAnalyzer:
    """
    Meta-analysis across sports testing sport characteristics as moderators
    """
    
    def __init__(self):
        self.sport_characteristics = {}
        self.sport_effects = {}
        self.meta_results = {}
        
    def load_sport_analyses(self, analysis_dir: str = "analysis_outputs/sports_meta_analysis"):
        """Load individual sport analysis results"""
        logger.info("Loading sport analyses...")
        
        # Load sport characteristics
        with open(f"{analysis_dir}/sport_characteristics.json", 'r') as f:
            char_data = json.load(f)
            self.sport_characteristics = char_data['sports_characterized']
        
        # Load individual sport results
        sports_analyzed = []
        for sport in self.sport_characteristics.keys():
            try:
                with open(f"{analysis_dir}/{sport}_analysis.json", 'r') as f:
                    analysis = json.load(f)
                    
                    if 'results' in analysis and 'correlations' in analysis['results']:
                        self.sport_effects[sport] = analysis['results']['correlations']
                        sports_analyzed.append(sport)
                        logger.info(f"  ✓ Loaded {sport}: {len(self.sport_effects[sport])} features")
            except FileNotFoundError:
                logger.warning(f"  ✗ No analysis found for {sport}")
        
        logger.info(f"Loaded analyses for {len(sports_analyzed)} sports: {sports_analyzed}")
        return sports_analyzed
    
    def create_meta_dataframe(self) -> pd.DataFrame:
        """
        Create dataframe with sport characteristics and effect sizes
        Each row is a sport, columns are characteristics and linguistic effects
        """
        logger.info("Creating meta-analysis dataframe...")
        
        meta_data = []
        
        for sport, characteristics in self.sport_characteristics.items():
            if sport not in self.sport_effects:
                continue
            
            row = {
                'sport': sport,
                # Sport characteristics
                'contact_level': characteristics.get('contact_level', 0),
                'team_size': characteristics.get('team_structure', {}).get('team_size', 1),
                'endurance_vs_explosive': characteristics.get('endurance_vs_explosive', 5),
                'precision_vs_power': characteristics.get('precision_vs_power', 5),
                'action_speed': characteristics.get('action_speed', 5),
                'announcer_repetition': characteristics.get('announcer_repetition', 5),
            }
            
            # Extract effect sizes for key linguistic features
            effects = self.sport_effects[sport]
            
            # Add effect sizes (r-values) for each linguistic feature
            for feature, stats_dict in effects.items():
                row[f'effect_{feature}'] = stats_dict.get('r', 0)
                row[f'effect_{feature}_p'] = stats_dict.get('p', 1.0)
            
            meta_data.append(row)
        
        self.meta_df = pd.DataFrame(meta_data)
        logger.info(f"Meta-dataframe: {len(self.meta_df)} sports × {len(self.meta_df.columns)} variables")
        
        return self.meta_df
    
    def test_contact_harshness_hypothesis(self) -> Dict[str, Any]:
        """
        H1: Contact level predicts harshness effect size
        Expected: r > 0.60, combat sports show strongest harsh name effects
        """
        logger.info("\nTesting H1: Contact Level × Harshness Effect")
        
        if 'effect_harshness_score' not in self.meta_df.columns:
            logger.warning("Harshness effect not available in all sports")
            return {}
        
        x = self.meta_df['contact_level'].values
        y = self.meta_df['effect_harshness_score'].values
        
        # Remove any NaN
        valid = ~(np.isnan(x) | np.isnan(y))
        x, y = x[valid], y[valid]
        
        if len(x) < 3:
            logger.warning("Insufficient data for contact-harshness analysis")
            return {}
        
        # Correlation
        r, p = stats.pearsonr(x, y)
        
        # Linear regression
        model = LinearRegression()
        model.fit(x.reshape(-1, 1), y)
        slope = model.coef_[0]
        intercept = model.intercept_
        r2 = model.score(x.reshape(-1, 1), y)
        
        result = {
            'hypothesis': 'Higher contact level predicts stronger harshness effects',
            'n_sports': len(x),
            'correlation': round(r, 4),
            'p_value': round(p, 6),
            'regression_slope': round(slope, 4),
            'regression_intercept': round(intercept, 4),
            'r_squared': round(r2, 4),
            'interpretation': f"Each point increase in contact predicts {abs(slope):.3f} change in harshness effect",
            'hypothesis_supported': r > 0.40 and p < 0.10,
            'sports_analyzed': self.meta_df['sport'].tolist()
        }
        
        logger.info(f"  Correlation: r = {r:.3f}, p = {p:.4f}")
        logger.info(f"  Slope: β = {slope:.3f} per contact point")
        logger.info(f"  Hypothesis supported: {result['hypothesis_supported']}")
        
        self.meta_results['H1_contact_harshness'] = result
        return result
    
    def test_team_size_length_hypothesis(self) -> Dict[str, Any]:
        """
        H2: Team size predicts name length effect (negative correlation)
        Expected: r < -0.50, larger teams prefer shorter names
        """
        logger.info("\nTesting H2: Team Size × Name Length Effect")
        
        length_feature = None
        for col in self.meta_df.columns:
            if 'syllable' in col or 'length' in col:
                length_feature = col
                break
        
        if not length_feature:
            logger.warning("No length-related effect found")
            return {}
        
        x = self.meta_df['team_size'].values
        y = self.meta_df[length_feature].values
        
        valid = ~(np.isnan(x) | np.isnan(y))
        x, y = x[valid], y[valid]
        
        if len(x) < 3:
            return {}
        
        r, p = stats.pearsonr(x, y)
        
        model = LinearRegression()
        model.fit(x.reshape(-1, 1), y)
        slope = model.coef_[0]
        
        result = {
            'hypothesis': 'Larger teams show stronger short name advantage',
            'n_sports': len(x),
            'correlation': round(r, 4),
            'p_value': round(p, 6),
            'regression_slope': round(slope, 4),
            'interpretation': f"Each additional team member predicts {abs(slope):.4f} change in length effect",
            'hypothesis_supported': r < -0.30 and p < 0.10,
            'length_feature_used': length_feature
        }
        
        logger.info(f"  Correlation: r = {r:.3f}, p = {p:.4f}")
        logger.info(f"  Hypothesis supported: {result['hypothesis_supported']}")
        
        self.meta_results['H2_team_size_length'] = result
        return result
    
    def test_precision_memorability_hypothesis(self) -> Dict[str, Any]:
        """
        H3: Precision score predicts memorability > harshness pattern
        Expected: High precision sports prioritize memorability
        """
        logger.info("\nTesting H3: Precision × Memorability Dominance")
        
        if 'effect_memorability_score' not in self.meta_df.columns:
            logger.warning("Memorability effect not available")
            return {}
        
        # Calculate memorability dominance (memo - harshness)
        memo_effect = self.meta_df['effect_memorability_score'].values
        harsh_effect = self.meta_df.get('effect_harshness_score', np.zeros(len(memo_effect))).values
        dominance = memo_effect - harsh_effect
        
        x = self.meta_df['precision_vs_power'].values
        y = dominance
        
        valid = ~(np.isnan(x) | np.isnan(y))
        x, y = x[valid], y[valid]
        
        if len(x) < 3:
            return {}
        
        r, p = stats.pearsonr(x, y)
        
        result = {
            'hypothesis': 'Precision sports prioritize memorability over harshness',
            'n_sports': len(x),
            'correlation': round(r, 4),
            'p_value': round(p, 6),
            'memorability_dominance_metric': 'memo_effect - harsh_effect',
            'hypothesis_supported': r > 0.30 and p < 0.10
        }
        
        logger.info(f"  Correlation: r = {r:.3f}, p = {p:.4f}")
        logger.info(f"  Hypothesis supported: {result['hypothesis_supported']}")
        
        self.meta_results['H3_precision_memorability'] = result
        return result
    
    def calculate_heterogeneity(self) -> Dict[str, Any]:
        """
        Calculate I² statistic for heterogeneity
        Measures how much variance is due to sport differences vs sampling error
        """
        logger.info("\nCalculating heterogeneity statistics...")
        
        # For each linguistic feature, calculate I²
        heterogeneity = {}
        
        effect_cols = [col for col in self.meta_df.columns if col.startswith('effect_') and not col.endswith('_p')]
        
        for feature_col in effect_cols:
            effects = self.meta_df[feature_col].dropna().values
            
            if len(effects) < 3:
                continue
            
            # Simple heterogeneity measure: variance ratio
            total_var = np.var(effects)
            within_var = 0.01  # Assumed within-sport sampling variance
            
            I_squared = max(0, (total_var - within_var) / total_var * 100)
            
            heterogeneity[feature_col.replace('effect_', '')] = {
                'I_squared': round(I_squared, 2),
                'interpretation': 'high' if I_squared > 75 else 'moderate' if I_squared > 50 else 'low',
                'total_variance': round(total_var, 4),
                'n_sports': len(effects)
            }
        
        self.meta_results['heterogeneity'] = heterogeneity
        
        logger.info(f"  Calculated heterogeneity for {len(heterogeneity)} features")
        logger.info(f"  Average I²: {np.mean([h['I_squared'] for h in heterogeneity.values()]):.1f}%")
        
        return heterogeneity
    
    def run_multiple_regression(self) -> Dict[str, Any]:
        """
        Multiple regression: All sport characteristics predict effect patterns
        """
        logger.info("\nRunning multiple regression analysis...")
        
        # Predictor variables (sport characteristics)
        predictors = ['contact_level', 'team_size', 'endurance_vs_explosive', 
                     'precision_vs_power', 'action_speed', 'announcer_repetition']
        
        X = self.meta_df[predictors].fillna(0).values
        
        # Test for several key outcome variables
        regression_results = {}
        
        for outcome_col in ['effect_harshness_score', 'effect_total_syllables', 'effect_memorability_score']:
            if outcome_col not in self.meta_df.columns:
                continue
            
            y = self.meta_df[outcome_col].fillna(0).values
            
            if len(y) < len(predictors) + 1:  # Need more observations than predictors
                continue
            
            model = LinearRegression()
            model.fit(X, y)
            
            r2 = model.score(X, y)
            coefficients = dict(zip(predictors, model.coef_))
            
            regression_results[outcome_col.replace('effect_', '')] = {
                'r_squared': round(r2, 4),
                'coefficients': {k: round(v, 4) for k, v in coefficients.items()},
                'intercept': round(model.intercept_, 4),
                'interpretation': f"Sport characteristics explain {r2*100:.1f}% of variance"
            }
        
        self.meta_results['multiple_regression'] = regression_results
        
        logger.info(f"  Regression models: {len(regression_results)}")
        for outcome, results in regression_results.items():
            logger.info(f"    {outcome}: R² = {results['r_squared']:.3f}")
        
        return regression_results
    
    def generate_predictions(self) -> Dict[str, Any]:
        """
        Generate predictions for untested sports based on their characteristics
        """
        logger.info("\nGenerating predictions for untested sports...")
        
        # Example untested sports with characteristics
        untested_sports = {
            'golf': {
                'contact_level': 0,
                'team_size': 1,
                'endurance_vs_explosive': 3,
                'precision_vs_power': 9,
                'action_speed': 1,
                'announcer_repetition': 8
            },
            'hockey': {
                'contact_level': 8,
                'team_size': 6,
                'endurance_vs_explosive': 6,
                'precision_vs_power': 4,
                'action_speed': 9,
                'announcer_repetition': 7
            },
            'rugby': {
                'contact_level': 9,
                'team_size': 15,
                'endurance_vs_explosive': 7,
                'precision_vs_power': 2,
                'action_speed': 7,
                'announcer_repetition': 6
            }
        }
        
        predictions = {}
        
        # Use regression models to predict effects
        if 'multiple_regression' in self.meta_results:
            for sport, characteristics in untested_sports.items():
                sport_preds = {}
                
                for outcome, model_results in self.meta_results['multiple_regression'].items():
                    # Calculate predicted effect
                    pred_value = model_results['intercept']
                    for characteristic, coef in model_results['coefficients'].items():
                        pred_value += coef * characteristics.get(characteristic, 0)
                    
                    sport_preds[outcome] = round(pred_value, 4)
                
                predictions[sport] = {
                    'characteristics': characteristics,
                    'predicted_effects': sport_preds
                }
        
        self.meta_results['predictions'] = predictions
        
        logger.info(f"  Generated predictions for {len(predictions)} untested sports")
        
        return predictions
    
    def save_results(self, output_file: str = "analysis_outputs/sports_meta_analysis/meta_regression_results.json"):
        """Save all meta-analysis results"""
        results_package = {
            'analysis_date': pd.Timestamp.now().isoformat(),
            'n_sports_analyzed': len(self.meta_df),
            'sports_included': self.meta_df['sport'].tolist(),
            'meta_results': self.meta_results
        }
        
        with open(output_file, 'w') as f:
            json.dump(results_package, f, indent=2)
        
        logger.info(f"\nResults saved to: {output_file}")
        return output_file
    
    def run_complete_meta_analysis(self) -> Dict[str, Any]:
        """Run all meta-analysis steps"""
        logger.info("\n" + "="*80)
        logger.info("CROSS-SPORT META-ANALYSIS")
        logger.info("="*80 + "\n")
        
        self.load_sport_analyses()
        self.create_meta_dataframe()
        
        # Test hypotheses
        self.test_contact_harshness_hypothesis()
        self.test_team_size_length_hypothesis()
        self.test_precision_memorability_hypothesis()
        
        # Additional analyses
        self.calculate_heterogeneity()
        self.run_multiple_regression()
        self.generate_predictions()
        
        # Save results
        self.save_results()
        
        logger.info("\n" + "="*80)
        logger.info("META-ANALYSIS COMPLETE")
        logger.info("="*80)
        
        return self.meta_results


if __name__ == "__main__":
    analyzer = CrossSportMetaAnalyzer()
    results = analyzer.run_complete_meta_analysis()
    
    print("\n=== KEY FINDINGS ===")
    for hypothesis, result in results.items():
        if isinstance(result, dict) and 'hypothesis' in result:
            print(f"\n{hypothesis}:")
            print(f"  {result['hypothesis']}")
            print(f"  Supported: {result.get('hypothesis_supported', 'N/A')}")

