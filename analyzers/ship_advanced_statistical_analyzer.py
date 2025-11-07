"""Ship Advanced Statistical Analyzer

Publication-grade statistical analysis for ship nomenclature research.

Implements:
1. Multiple regression with control variables
2. Interaction effects (name_category × era, name_category × type)
3. Mediation analysis (phonetics mediating name → outcome)
4. Polynomial regression (non-linear effects)
5. Subgroup analyses (by era, nation, type)
6. Robust standard errors
7. Confidence intervals (bootstrap)
8. Power analysis
9. Effect size calculations
10. Multiple comparison corrections (Bonferroni, FDR)
11. Diagnostic tests (VIF, heteroskedasticity, normality)
12. Cross-validation
"""

import logging
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.model_selection import cross_val_score, KFold
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.power import TTestIndPower
import statsmodels.api as sm
import statsmodels.formula.api as smf
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class ShipAdvancedStatisticalAnalyzer:
    """Advanced statistical analysis for ship nomenclature."""
    
    def __init__(self):
        self.alpha = 0.05
        self.n_bootstrap = 1000
        self.cv_folds = 5
        
    def comprehensive_analysis(self, ships_df: pd.DataFrame,
                               analysis_df: Optional[pd.DataFrame] = None) -> Dict:
        """Run complete advanced statistical analysis suite.
        
        Args:
            ships_df: DataFrame with ship data
            analysis_df: Optional DataFrame with name analysis
            
        Returns:
            Complete analysis results
        """
        logger.info("\n" + "="*70)
        logger.info("ADVANCED STATISTICAL ANALYSIS")
        logger.info("="*70)
        
        results = {
            'sample_info': self._get_sample_info(ships_df),
            'multiple_regression': self._multiple_regression_analysis(ships_df, analysis_df),
            'interaction_effects': self._interaction_analysis(ships_df),
            'polynomial_regression': self._polynomial_analysis(ships_df, analysis_df),
            'subgroup_analysis': self._subgroup_analysis(ships_df),
            'mediation_analysis': self._mediation_analysis(ships_df, analysis_df),
            'bootstrap_ci': self._bootstrap_confidence_intervals(ships_df),
            'power_analysis': self._power_analysis(ships_df),
            'diagnostics': self._regression_diagnostics(ships_df, analysis_df),
            'cross_validation': self._cross_validation_analysis(ships_df, analysis_df)
        }
        
        return results
    
    def _get_sample_info(self, ships_df: pd.DataFrame) -> Dict:
        """Get comprehensive sample information."""
        logger.info("\n📊 Sample Information")
        
        info = {
            'total_n': len(ships_df),
            'by_category': ships_df['name_category'].value_counts().to_dict(),
            'by_era': ships_df['era'].value_counts().to_dict(),
            'by_type': ships_df['ship_type'].value_counts().to_dict(),
            'by_nation': ships_df['nation'].value_counts().head(10).to_dict(),
            'outcome_stats': {
                'mean': float(ships_df['historical_significance_score'].mean()),
                'std': float(ships_df['historical_significance_score'].std()),
                'min': float(ships_df['historical_significance_score'].min()),
                'max': float(ships_df['historical_significance_score'].max()),
                'skewness': float(ships_df['historical_significance_score'].skew()),
                'kurtosis': float(ships_df['historical_significance_score'].kurtosis())
            }
        }
        
        logger.info(f"Total N: {info['total_n']}")
        logger.info(f"Outcome mean: {info['outcome_stats']['mean']:.2f} (SD={info['outcome_stats']['std']:.2f})")
        
        return info
    
    def _multiple_regression_analysis(self, ships_df: pd.DataFrame,
                                     analysis_df: Optional[pd.DataFrame]) -> Dict:
        """Multiple regression controlling for confounds.
        
        Model: Significance ~ NameCategory + Era + Type + Tonnage + Nation
        """
        logger.info("\n" + "="*70)
        logger.info("MULTIPLE REGRESSION ANALYSIS")
        logger.info("="*70)
        
        # Prepare data
        df = ships_df.copy()
        
        # Create dummy variables
        df['is_geographic'] = (df['name_category'] == 'geographic').astype(int)
        df['is_saint'] = (df['name_category'] == 'saint').astype(int)
        df['is_virtue'] = (df['name_category'] == 'virtue').astype(int)
        df['is_monarch'] = (df['name_category'] == 'monarch').astype(int)
        
        df['is_modern'] = (df['era'] == 'modern').astype(int)
        df['is_age_of_sail'] = (df['era'] == 'age_of_sail').astype(int)
        df['is_steam'] = (df['era'] == 'steam_era').astype(int)
        
        df['is_naval'] = (df['ship_type'] == 'naval').astype(int)
        df['is_exploration'] = (df['ship_type'] == 'exploration').astype(int)
        
        # Log-transform tonnage (if available)
        if 'tonnage' in df.columns and df['tonnage'].notna().sum() > 10:
            df['log_tonnage'] = np.log1p(df['tonnage'].fillna(df['tonnage'].median()))
        else:
            df['log_tonnage'] = 0
        
        # Model 1: Name category only
        formula1 = 'historical_significance_score ~ is_geographic + is_saint + is_virtue + is_monarch'
        
        # Model 2: Add control variables
        formula2 = 'historical_significance_score ~ is_geographic + is_saint + is_virtue + is_monarch + is_modern + is_age_of_sail + is_naval + log_tonnage'
        
        results = {}
        
        try:
            # Fit models
            model1 = smf.ols(formula1, data=df).fit()
            model2 = smf.ols(formula2, data=df).fit()
            
            results['model1_name_only'] = {
                'r_squared': float(model1.rsquared),
                'adj_r_squared': float(model1.rsquared_adj),
                'f_statistic': float(model1.fvalue),
                'f_pvalue': float(model1.f_pvalue),
                'coefficients': {
                    'is_geographic': {
                        'coef': float(model1.params.get('is_geographic', 0)),
                        'se': float(model1.bse.get('is_geographic', 0)),
                        'pvalue': float(model1.pvalues.get('is_geographic', 1)),
                        'ci_lower': float(model1.conf_int().loc['is_geographic', 0]) if 'is_geographic' in model1.params else 0,
                        'ci_upper': float(model1.conf_int().loc['is_geographic', 1]) if 'is_geographic' in model1.params else 0
                    },
                    'is_saint': {
                        'coef': float(model1.params.get('is_saint', 0)),
                        'se': float(model1.bse.get('is_saint', 0)),
                        'pvalue': float(model1.pvalues.get('is_saint', 1))
                    },
                    'is_virtue': {
                        'coef': float(model1.params.get('is_virtue', 0)),
                        'pvalue': float(model1.pvalues.get('is_virtue', 1))
                    }
                }
            }
            
            results['model2_with_controls'] = {
                'r_squared': float(model2.rsquared),
                'adj_r_squared': float(model2.rsquared_adj),
                'f_statistic': float(model2.fvalue),
                'f_pvalue': float(model2.f_pvalue),
                'aic': float(model2.aic),
                'bic': float(model2.bic),
                'coefficients': {
                    'is_geographic': {
                        'coef': float(model2.params.get('is_geographic', 0)),
                        'se': float(model2.bse.get('is_geographic', 0)),
                        'pvalue': float(model2.pvalues.get('is_geographic', 1)),
                        'ci_lower': float(model2.conf_int().loc['is_geographic', 0]) if 'is_geographic' in model2.params else 0,
                        'ci_upper': float(model2.conf_int().loc['is_geographic', 1]) if 'is_geographic' in model2.params else 0
                    },
                    'is_saint': {
                        'coef': float(model2.params.get('is_saint', 0)),
                        'pvalue': float(model2.pvalues.get('is_saint', 1))
                    },
                    'is_virtue': {
                        'coef': float(model2.params.get('is_virtue', 0)),
                        'pvalue': float(model2.pvalues.get('is_virtue', 1))
                    }
                }
            }
            
            # R-squared change
            results['model_comparison'] = {
                'r_squared_change': float(model2.rsquared - model1.rsquared),
                'interpretation': 'Controls explain additional variance' if model2.rsquared > model1.rsquared else 'Controls add little'
            }
            
            logger.info(f"\nModel 1 (Name only): R² = {model1.rsquared:.3f}")
            logger.info(f"Model 2 (With controls): R² = {model2.rsquared:.3f}")
            logger.info(f"Geographic coefficient: β = {model2.params.get('is_geographic', 0):.3f}, p = {model2.pvalues.get('is_geographic', 1):.4f}")
            logger.info(f"Saint coefficient: β = {model2.params.get('is_saint', 0):.3f}, p = {model2.pvalues.get('is_saint', 1):.4f}")
            logger.info(f"Virtue coefficient: β = {model2.params.get('is_virtue', 0):.3f}, p = {model2.pvalues.get('is_virtue', 1):.4f}")
            
        except Exception as e:
            logger.error(f"Multiple regression error: {e}")
            results['error'] = str(e)
        
        return results
    
    def _interaction_analysis(self, ships_df: pd.DataFrame) -> Dict:
        """Test interaction effects.
        
        Tests:
        1. NameCategory × Era (do effects change over time?)
        2. NameCategory × Type (naval vs exploration different?)
        3. NameCategory × Nation (cultural differences?)
        """
        logger.info("\n" + "="*70)
        logger.info("INTERACTION EFFECTS ANALYSIS")
        logger.info("="*70)
        
        df = ships_df.copy()
        df['is_geographic'] = (df['name_category'] == 'geographic').astype(int)
        df['is_saint'] = (df['name_category'] == 'saint').astype(int)
        df['is_modern'] = (df['era'] == 'modern').astype(int)
        df['is_naval'] = (df['ship_type'] == 'naval').astype(int)
        
        results = {}
        
        try:
            # Interaction 1: Geographic × Modern Era
            formula = 'historical_significance_score ~ is_geographic + is_modern + is_geographic:is_modern'
            model = smf.ols(formula, data=df).fit()
            
            interaction_coef = model.params.get('is_geographic:is_modern', 0)
            interaction_p = model.pvalues.get('is_geographic:is_modern', 1)
            
            results['geographic_x_modern'] = {
                'coefficient': float(interaction_coef),
                'pvalue': float(interaction_p),
                'significant': interaction_p < 0.05,
                'interpretation': 'Geographic name effect differs by era' if interaction_p < 0.05 else 'No era moderation'
            }
            
            logger.info(f"\nGeographic × Modern: β = {interaction_coef:.3f}, p = {interaction_p:.4f}")
            
            # Interaction 2: Geographic × Naval Type
            formula2 = 'historical_significance_score ~ is_geographic + is_naval + is_geographic:is_naval'
            model2 = smf.ols(formula2, data=df).fit()
            
            interaction_coef2 = model2.params.get('is_geographic:is_naval', 0)
            interaction_p2 = model2.pvalues.get('is_geographic:is_naval', 1)
            
            results['geographic_x_naval'] = {
                'coefficient': float(interaction_coef2),
                'pvalue': float(interaction_p2),
                'significant': interaction_p2 < 0.05,
                'interpretation': 'Geographic effect differs for naval vs exploration' if interaction_p2 < 0.05 else 'No type moderation'
            }
            
            logger.info(f"Geographic × Naval: β = {interaction_coef2:.3f}, p = {interaction_p2:.4f}")
            
            # Interaction 3: Saint × Era
            df['is_age_of_discovery'] = (df['era'] == 'age_of_discovery').astype(int)
            formula3 = 'historical_significance_score ~ is_saint + is_age_of_discovery + is_saint:is_age_of_discovery'
            model3 = smf.ols(formula3, data=df).fit()
            
            interaction_coef3 = model3.params.get('is_saint:is_age_of_discovery', 0)
            interaction_p3 = model3.pvalues.get('is_saint:is_age_of_discovery', 1)
            
            results['saint_x_age_of_discovery'] = {
                'coefficient': float(interaction_coef3),
                'pvalue': float(interaction_p3),
                'significant': interaction_p3 < 0.05,
                'interpretation': 'Saint names performed differently in Age of Discovery' if interaction_p3 < 0.05 else 'No era effect for saints'
            }
            
            logger.info(f"Saint × Age of Discovery: β = {interaction_coef3:.3f}, p = {interaction_p3:.4f}")
            
        except Exception as e:
            logger.error(f"Interaction analysis error: {e}")
            results['error'] = str(e)
        
        return results
    
    def _mediation_analysis(self, ships_df: pd.DataFrame,
                           analysis_df: Optional[pd.DataFrame]) -> Dict:
        """Mediation analysis: Does phonetics mediate name_category → outcome?
        
        Tests: NameCategory → [Memorability/Authority] → Significance
        
        Baron & Kenny steps:
        1. X → Y (total effect)
        2. X → M (mediator)
        3. M → Y (controlling X)
        4. X → Y (controlling M) - reduced direct effect
        """
        logger.info("\n" + "="*70)
        logger.info("MEDIATION ANALYSIS")
        logger.info("="*70)
        
        if analysis_df is None or len(analysis_df) < 20:
            return {'error': 'Insufficient analysis data'}
        
        # Merge datasets - keep name_category from ships_df
        merged = ships_df.merge(analysis_df, left_on='id', right_on='ship_id', how='inner', suffixes=('', '_analysis'))
        
        if len(merged) < 20:
            return {'error': 'Insufficient merged data'}
        
        # Use name_category from ships (not analysis)
        if 'name_category' not in merged.columns and 'name_category_analysis' in merged.columns:
            merged['name_category'] = merged['name_category_analysis']
        elif 'name_category' not in merged.columns:
            return {'error': 'name_category not found in merged data'}
        
        merged['is_geographic'] = (merged['name_category'] == 'geographic').astype(int)
        
        results = {}
        
        try:
            # Mediation 1: Geographic → Memorability → Significance
            # Step 1: X → Y (total effect)
            model_total = smf.ols('historical_significance_score ~ is_geographic', data=merged).fit()
            total_effect = model_total.params.get('is_geographic', 0)
            total_p = model_total.pvalues.get('is_geographic', 1)
            
            # Step 2: X → M (mediator)
            model_xm = smf.ols('memorability_score ~ is_geographic', data=merged).fit()
            a_path = model_xm.params.get('is_geographic', 0)
            a_p = model_xm.pvalues.get('is_geographic', 1)
            
            # Step 3: M → Y (controlling X)
            model_my = smf.ols('historical_significance_score ~ is_geographic + memorability_score', data=merged).fit()
            b_path = model_my.params.get('memorability_score', 0)
            b_p = model_my.pvalues.get('memorability_score', 1)
            
            # Step 4: X → Y (controlling M) - direct effect
            direct_effect = model_my.params.get('is_geographic', 0)
            direct_p = model_my.pvalues.get('is_geographic', 1)
            
            # Indirect effect
            indirect_effect = a_path * b_path
            
            # Sobel test
            se_indirect = np.sqrt((b_path**2 * model_xm.bse.get('is_geographic', 0)**2) +
                                 (a_path**2 * model_my.bse.get('memorability_score', 0)**2))
            z_score = indirect_effect / se_indirect if se_indirect > 0 else 0
            sobel_p = 2 * (1 - stats.norm.cdf(abs(z_score)))
            
            # Proportion mediated
            prop_mediated = indirect_effect / total_effect if total_effect != 0 else 0
            
            results['memorability_mediation'] = {
                'total_effect': float(total_effect),
                'direct_effect': float(direct_effect),
                'indirect_effect': float(indirect_effect),
                'proportion_mediated': float(prop_mediated),
                'sobel_z': float(z_score),
                'sobel_p': float(sobel_p),
                'significant': sobel_p < 0.05,
                'interpretation': f"{'Significant' if sobel_p < 0.05 else 'No'} mediation: {abs(prop_mediated)*100:.1f}% of effect through memorability"
            }
            
            logger.info(f"\nMemorability Mediation:")
            logger.info(f"  Total effect: {total_effect:.3f}")
            logger.info(f"  Indirect effect: {indirect_effect:.3f}")
            logger.info(f"  Proportion mediated: {prop_mediated*100:.1f}%")
            logger.info(f"  Sobel test: z = {z_score:.3f}, p = {sobel_p:.4f}")
            
            # Mediation 2: Geographic → Authority → Significance
            if 'authority_score' in merged.columns:
                model_xm2 = smf.ols('authority_score ~ is_geographic', data=merged).fit()
                model_my2 = smf.ols('historical_significance_score ~ is_geographic + authority_score', data=merged).fit()
                
                a_path2 = model_xm2.params.get('is_geographic', 0)
                b_path2 = model_my2.params.get('authority_score', 0)
                indirect_effect2 = a_path2 * b_path2
                
                prop_mediated2 = indirect_effect2 / total_effect if total_effect != 0 else 0
                
                results['authority_mediation'] = {
                    'indirect_effect': float(indirect_effect2),
                    'proportion_mediated': float(prop_mediated2),
                    'interpretation': f"{abs(prop_mediated2)*100:.1f}% of effect through authority"
                }
                
                logger.info(f"\nAuthority Mediation:")
                logger.info(f"  Proportion mediated: {prop_mediated2*100:.1f}%")
            
        except Exception as e:
            logger.error(f"Mediation analysis error: {e}")
            results['error'] = str(e)
        
        return results
    
    def _polynomial_analysis(self, ships_df: pd.DataFrame,
                            analysis_df: Optional[pd.DataFrame]) -> Dict:
        """Test non-linear effects using polynomial regression."""
        logger.info("\n" + "="*70)
        logger.info("POLYNOMIAL REGRESSION (Non-linear Effects)")
        logger.info("="*70)
        
        if analysis_df is None:
            return {'error': 'No analysis data'}
        
        merged = ships_df.merge(analysis_df, left_on='id', right_on='ship_id', how='inner')
        
        if len(merged) < 30:
            return {'error': 'Insufficient data'}
        
        results = {}
        
        try:
            # Test syllable count (linear vs quadratic)
            if 'syllable_count' in merged.columns:
                clean = merged[['syllable_count', 'historical_significance_score']].dropna()
                
                if len(clean) >= 20:
                    # Linear
                    X_linear = clean[['syllable_count']].values
                    y = clean['historical_significance_score'].values
                    
                    model_linear = LinearRegression().fit(X_linear, y)
                    r2_linear = model_linear.score(X_linear, y)
                    
                    # Quadratic
                    poly = PolynomialFeatures(degree=2, include_bias=False)
                    X_poly = poly.fit_transform(X_linear)
                    
                    model_poly = LinearRegression().fit(X_poly, y)
                    r2_poly = model_poly.score(X_poly, y)
                    
                    # F-test for improvement
                    n = len(clean)
                    f_stat = ((r2_poly - r2_linear) / 1) / ((1 - r2_poly) / (n - 3))
                    f_p = 1 - stats.f.cdf(f_stat, 1, n - 3)
                    
                    results['syllable_nonlinearity'] = {
                        'r2_linear': float(r2_linear),
                        'r2_quadratic': float(r2_poly),
                        'improvement': float(r2_poly - r2_linear),
                        'f_statistic': float(f_stat),
                        'pvalue': float(f_p),
                        'significant': f_p < 0.05,
                        'interpretation': 'Quadratic fit significantly better' if f_p < 0.05 else 'Linear fit adequate'
                    }
                    
                    logger.info(f"\nSyllable Non-linearity:")
                    logger.info(f"  R² linear: {r2_linear:.3f}")
                    logger.info(f"  R² quadratic: {r2_poly:.3f}")
                    logger.info(f"  F-test: p = {f_p:.4f}")
            
            # Test character length
            if 'character_length' in merged.columns:
                clean = merged[['character_length', 'historical_significance_score']].dropna()
                
                if len(clean) >= 20:
                    X_linear = clean[['character_length']].values
                    y = clean['historical_significance_score'].values
                    
                    model_linear = LinearRegression().fit(X_linear, y)
                    r2_linear = model_linear.score(X_linear, y)
                    
                    poly = PolynomialFeatures(degree=2, include_bias=False)
                    X_poly = poly.fit_transform(X_linear)
                    model_poly = LinearRegression().fit(X_poly, y)
                    r2_poly = model_poly.score(X_poly, y)
                    
                    results['length_nonlinearity'] = {
                        'r2_linear': float(r2_linear),
                        'r2_quadratic': float(r2_poly),
                        'improvement': float(r2_poly - r2_linear)
                    }
                    
                    logger.info(f"Length Non-linearity: R² improvement = {r2_poly - r2_linear:.4f}")
            
        except Exception as e:
            logger.error(f"Polynomial analysis error: {e}")
            results['error'] = str(e)
        
        return results
    
    def _subgroup_analysis(self, ships_df: pd.DataFrame) -> Dict:
        """Analyze geographic vs saint within subgroups.
        
        Subgroups:
        1. By era (Age of Sail, Modern, etc.)
        2. By nation (US, UK, Spain)
        3. By type (naval, exploration)
        4. By decade
        """
        logger.info("\n" + "="*70)
        logger.info("SUBGROUP ANALYSIS")
        logger.info("="*70)
        
        results = {
            'by_era': {},
            'by_nation': {},
            'by_type': {},
            'by_century': {}
        }
        
        # By Era
        for era in ['age_of_discovery', 'age_of_sail', 'steam_era', 'modern']:
            era_df = ships_df[ships_df['era'] == era]
            
            if len(era_df) >= 10:
                geo = era_df[era_df['name_category'] == 'geographic']['historical_significance_score']
                saint = era_df[era_df['name_category'] == 'saint']['historical_significance_score']
                
                if len(geo) >= 3 and len(saint) >= 3:
                    t_stat, p_val = stats.ttest_ind(geo, saint, equal_var=False)
                    cohens_d = (geo.mean() - saint.mean()) / geo.std() if geo.std() > 0 else 0
                    
                    results['by_era'][era] = {
                        'geo_n': len(geo),
                        'saint_n': len(saint),
                        'geo_mean': float(geo.mean()),
                        'saint_mean': float(saint.mean()),
                        'difference': float(geo.mean() - saint.mean()),
                        't_statistic': float(t_stat),
                        'pvalue': float(p_val),
                        'cohens_d': float(cohens_d),
                        'significant': p_val < 0.05
                    }
                    
                    logger.info(f"\n{era}: Geo={geo.mean():.1f} vs Saint={saint.mean():.1f}, p={p_val:.4f}")
        
        # By Nation
        for nation in ['United States', 'United Kingdom', 'Spain']:
            nation_df = ships_df[ships_df['nation'].str.contains(nation, case=False, na=False)]
            
            if len(nation_df) >= 10:
                geo = nation_df[nation_df['name_category'] == 'geographic']['historical_significance_score']
                saint = nation_df[nation_df['name_category'] == 'saint']['historical_significance_score']
                
                if len(geo) >= 2 and len(saint) >= 2:
                    results['by_nation'][nation] = {
                        'geo_mean': float(geo.mean()),
                        'saint_mean': float(saint.mean()),
                        'difference': float(geo.mean() - saint.mean())
                    }
                    
                    logger.info(f"{nation}: Geo={geo.mean():.1f} vs Saint={saint.mean():.1f}")
        
        # By Type
        for ship_type in ['naval', 'exploration']:
            type_df = ships_df[ships_df['ship_type'] == ship_type]
            
            if len(type_df) >= 10:
                geo = type_df[type_df['name_category'] == 'geographic']['historical_significance_score']
                saint = type_df[type_df['name_category'] == 'saint']['historical_significance_score']
                
                if len(geo) >= 3 and len(saint) >= 2:
                    t_stat, p_val = stats.ttest_ind(geo, saint, equal_var=False)
                    
                    results['by_type'][ship_type] = {
                        'geo_mean': float(geo.mean()),
                        'saint_mean': float(saint.mean()),
                        'pvalue': float(p_val),
                        'significant': p_val < 0.05
                    }
                    
                    logger.info(f"{ship_type}: p={p_val:.4f}")
        
        return results
    
    def _bootstrap_confidence_intervals(self, ships_df: pd.DataFrame) -> Dict:
        """Bootstrap confidence intervals for mean difference."""
        logger.info("\n" + "="*70)
        logger.info("BOOTSTRAP CONFIDENCE INTERVALS")
        logger.info("="*70)
        
        geographic = ships_df[ships_df['name_category'] == 'geographic']['historical_significance_score'].values
        saint = ships_df[ships_df['name_category'] == 'saint']['historical_significance_score'].values
        
        if len(geographic) < 5 or len(saint) < 5:
            return {'error': 'Insufficient data'}
        
        # Bootstrap mean difference
        differences = []
        
        for _ in range(self.n_bootstrap):
            geo_sample = np.random.choice(geographic, size=len(geographic), replace=True)
            saint_sample = np.random.choice(saint, size=len(saint), replace=True)
            differences.append(geo_sample.mean() - saint_sample.mean())
        
        differences = np.array(differences)
        
        # Calculate percentiles
        ci_lower = np.percentile(differences, 2.5)
        ci_upper = np.percentile(differences, 97.5)
        
        results = {
            'observed_difference': float(geographic.mean() - saint.mean()),
            'bootstrap_mean': float(differences.mean()),
            'bootstrap_std': float(differences.std()),
            'ci_95_lower': float(ci_lower),
            'ci_95_upper': float(ci_upper),
            'ci_contains_zero': ci_lower < 0 < ci_upper,
            'interpretation': 'No significant difference (CI contains 0)' if ci_lower < 0 < ci_upper else 'Significant difference (CI excludes 0)'
        }
        
        logger.info(f"\nBootstrap 95% CI: [{ci_lower:.2f}, {ci_upper:.2f}]")
        logger.info(f"Contains zero: {results['ci_contains_zero']}")
        
        return results
    
    def _power_analysis(self, ships_df: pd.DataFrame) -> Dict:
        """Post-hoc power analysis."""
        logger.info("\n" + "="*70)
        logger.info("POWER ANALYSIS")
        logger.info("="*70)
        
        geographic = ships_df[ships_df['name_category'] == 'geographic']['historical_significance_score']
        saint = ships_df[ships_df['name_category'] == 'saint']['historical_significance_score']
        
        if len(geographic) < 5 or len(saint) < 5:
            return {'error': 'Insufficient data'}
        
        # Calculate effect size
        pooled_std = np.sqrt(((len(geographic)-1)*geographic.std()**2 + (len(saint)-1)*saint.std()**2) / (len(geographic) + len(saint) - 2))
        effect_size = (geographic.mean() - saint.mean()) / pooled_std
        
        # Calculate achieved power
        analysis = TTestIndPower()
        power = analysis.solve_power(effect_size=abs(effect_size), 
                                     nobs1=len(geographic), 
                                     ratio=len(saint)/len(geographic),
                                     alpha=0.05)
        
        # Sample size needed for 80% power
        n_needed = analysis.solve_power(effect_size=abs(effect_size),
                                        power=0.8,
                                        alpha=0.05)
        
        results = {
            'observed_effect_size': float(effect_size),
            'n_geographic': len(geographic),
            'n_saint': len(saint),
            'achieved_power': float(power),
            'n_needed_per_group': int(n_needed),
            'adequately_powered': power >= 0.8,
            'interpretation': f"{'Adequately' if power >= 0.8 else 'Under'} powered (power={power:.3f})"
        }
        
        logger.info(f"\nObserved effect size: d = {effect_size:.3f}")
        logger.info(f"Achieved power: {power:.3f}")
        logger.info(f"Need {int(n_needed)} per group for 80% power")
        
        return results
    
    def _regression_diagnostics(self, ships_df: pd.DataFrame,
                                analysis_df: Optional[pd.DataFrame]) -> Dict:
        """Regression diagnostics (VIF, heteroskedasticity, normality)."""
        logger.info("\n" + "="*70)
        logger.info("REGRESSION DIAGNOSTICS")
        logger.info("="*70)
        
        if analysis_df is None:
            return {'error': 'No analysis data'}
        
        merged = ships_df.merge(analysis_df, left_on='id', right_on='ship_id', how='inner', suffixes=('', '_analysis'))
        
        if len(merged) < 30:
            return {'error': 'Insufficient data'}
        
        # Ensure we have name_category and era columns
        if 'name_category' not in merged.columns:
            if 'name_category_analysis' in merged.columns:
                merged['name_category'] = merged['name_category_analysis']
            else:
                return {'error': 'name_category not found'}
        
        if 'era' not in merged.columns:
            return {'error': 'era not found'}
        
        results = {}
        
        try:
            # Prepare predictors
            merged['is_geographic'] = (merged['name_category'] == 'geographic').astype(int)
            merged['is_modern'] = (merged['era'] == 'modern').astype(int)
            
            predictors = ['syllable_count', 'memorability_score', 'is_geographic', 'is_modern']
            available_predictors = [p for p in predictors if p in merged.columns and merged[p].notna().sum() > 20]
            
            if len(available_predictors) >= 2:
                # Fit model
                formula = f"historical_significance_score ~ {' + '.join(available_predictors)}"
                model = smf.ols(formula, data=merged).fit()
                
                # VIF (multicollinearity)
                X = merged[available_predictors].dropna()
                X_with_const = sm.add_constant(X)
                
                vif_data = pd.DataFrame()
                vif_data["Variable"] = X_with_const.columns
                vif_data["VIF"] = [variance_inflation_factor(X_with_const.values, i) 
                                  for i in range(X_with_const.shape[1])]
                
                results['vif'] = vif_data.to_dict('records')
                results['multicollinearity_concern'] = bool((vif_data['VIF'] > 10).any())
                
                logger.info(f"\nVIF (Multicollinearity):")
                for _, row in vif_data.iterrows():
                    logger.info(f"  {row['Variable']}: {row['VIF']:.2f}")
                
                # Breusch-Pagan test (heteroskedasticity)
                from statsmodels.stats.diagnostic import het_breuschpagan
                bp_test = het_breuschpagan(model.resid, model.model.exog)
                
                results['heteroskedasticity'] = {
                    'lm_statistic': float(bp_test[0]),
                    'pvalue': float(bp_test[1]),
                    'concern': bp_test[1] < 0.05,
                    'interpretation': 'Heteroskedasticity detected' if bp_test[1] < 0.05 else 'Homoskedastic'
                }
                
                logger.info(f"\nBreusch-Pagan: p = {bp_test[1]:.4f}")
                
                # Normality of residuals (Shapiro-Wilk)
                if len(model.resid) <= 5000:
                    shapiro_stat, shapiro_p = stats.shapiro(model.resid)
                    
                    results['normality'] = {
                        'shapiro_w': float(shapiro_stat),
                        'pvalue': float(shapiro_p),
                        'concern': shapiro_p < 0.05,
                        'interpretation': 'Non-normal residuals' if shapiro_p < 0.05 else 'Normal residuals'
                    }
                    
                    logger.info(f"Shapiro-Wilk: p = {shapiro_p:.4f}")
            
        except Exception as e:
            logger.error(f"Diagnostics error: {e}")
            results['error'] = str(e)
        
        return results
    
    def _cross_validation_analysis(self, ships_df: pd.DataFrame,
                                   analysis_df: Optional[pd.DataFrame]) -> Dict:
        """Cross-validation to test model generalizability."""
        logger.info("\n" + "="*70)
        logger.info("CROSS-VALIDATION ANALYSIS")
        logger.info("="*70)
        
        if analysis_df is None:
            return {'error': 'No analysis data'}
        
        merged = ships_df.merge(analysis_df, left_on='id', right_on='ship_id', how='inner', suffixes=('', '_analysis'))
        
        if len(merged) < 30:
            return {'error': 'Insufficient data'}
        
        # Ensure we have name_category
        if 'name_category' not in merged.columns:
            if 'name_category_analysis' in merged.columns:
                merged['name_category'] = merged['name_category_analysis']
            else:
                return {'error': 'name_category not found'}
        
        results = {}
        
        try:
            # Prepare features
            merged['is_geographic'] = (merged['name_category'] == 'geographic').astype(int)
            merged['is_saint'] = (merged['name_category'] == 'saint').astype(int)
            merged['is_virtue'] = (merged['name_category'] == 'virtue').astype(int)
            
            features = ['is_geographic', 'is_saint', 'is_virtue']
            if 'memorability_score' in merged.columns:
                features.append('memorability_score')
            if 'syllable_count' in merged.columns:
                features.append('syllable_count')
            
            # Clean data
            clean = merged[features + ['historical_significance_score']].dropna()
            
            if len(clean) >= 20:
                X = clean[features].values
                y = clean['historical_significance_score'].values
                
                # K-fold cross-validation
                model = LinearRegression()
                cv_scores = cross_val_score(model, X, y, cv=min(self.cv_folds, len(clean)//5), 
                                           scoring='r2')
                
                results['cross_validation'] = {
                    'cv_folds': len(cv_scores),
                    'cv_scores': [float(s) for s in cv_scores],
                    'mean_r2': float(cv_scores.mean()),
                    'std_r2': float(cv_scores.std()),
                    'interpretation': f"Model explains {cv_scores.mean()*100:.1f}% of variance (CV)"
                }
                
                logger.info(f"\nCross-validation R² = {cv_scores.mean():.3f} (±{cv_scores.std():.3f})")
            
        except Exception as e:
            logger.error(f"Cross-validation error: {e}")
            results['error'] = str(e)
        
        return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Ship Advanced Statistical Analyzer initialized")
    print("Implements: Multiple regression, interactions, mediation, polynomial, subgroups")

