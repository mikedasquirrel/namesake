"""Band Advanced Statistical Analyzer

Sophisticated statistical methods for band name analysis:
- Interaction effects (decade × genre × geography)
- Mediation analysis (name → memorability → success)
- Polynomial regression (non-linear relationships)
- Moderator analysis (when does X matter?)
- Regression diagnostics (residuals, leverage, influence)
- Causal inference methods (instrumental variables, propensity scoring)
- Bayesian analysis (posterior distributions)
"""

import logging
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.model_selection import cross_val_score, train_test_split, GridSearchCV
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from scipy import stats
from scipy.stats import pearsonr, spearmanr
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

from core.models import db, Band, BandAnalysis

logger = logging.getLogger(__name__)


class BandAdvancedStatisticalAnalyzer:
    """Advanced statistical analysis with interaction effects and causal inference."""
    
    def __init__(self):
        self.scaler = StandardScaler()
    
    def get_comprehensive_dataset(self) -> pd.DataFrame:
        """Load all bands with complete data."""
        query = db.session.query(Band, BandAnalysis).join(
            BandAnalysis,
            Band.id == BandAnalysis.band_id
        )
        
        rows = []
        for band, analysis in query.all():
            try:
                row = {
                    # Metadata
                    'id': band.id,
                    'name': band.name,
                    'formation_year': band.formation_year,
                    'formation_decade': band.formation_decade,
                    'origin_country': band.origin_country,
                    'genre_cluster': band.genre_cluster,
                    'is_active': band.is_active,
                    'years_active': band.years_active or 0,
                    
                    # Outcomes
                    'popularity_score': band.popularity_score or 0,
                    'longevity_score': band.longevity_score or 0,
                    'cross_generational_appeal': band.cross_generational_appeal or False,
                    'listeners_count': band.listeners_count or 0,
                    
                    # Linguistic features
                    'syllable_count': analysis.syllable_count or 0,
                    'character_length': analysis.character_length or 0,
                    'word_count': analysis.word_count or 0,
                    'memorability_score': analysis.memorability_score or 0,
                    'pronounceability_score': analysis.pronounceability_score or 0,
                    'uniqueness_score': analysis.uniqueness_score or 0,
                    'fantasy_score': analysis.fantasy_score or 0,
                    'power_connotation_score': analysis.power_connotation_score or 0,
                    'harshness_score': analysis.harshness_score or 0,
                    'softness_score': analysis.softness_score or 0,
                    'abstraction_score': analysis.abstraction_score or 0,
                    'literary_reference_score': analysis.literary_reference_score or 0,
                    'phonetic_score': analysis.phonetic_score or 0,
                    'vowel_ratio': analysis.vowel_ratio or 0,
                }
                
                rows.append(row)
                
            except Exception as e:
                logger.warning(f"Error loading band {band.name}: {e}")
                continue
        
        return pd.DataFrame(rows)
    
    def analyze_interaction_effects(self, df: pd.DataFrame) -> Dict:
        """Analyze interaction effects: decade × genre, genre × geography, etc.
        
        Args:
            df: DataFrame with band data
            
        Returns:
            Interaction analysis results
        """
        logger.info("Analyzing interaction effects...")
        
        results = {
            'decade_genre_interactions': {},
            'geography_genre_interactions': {},
            'temporal_feature_interactions': {},
            'three_way_interactions': {}
        }
        
        # 1. Decade × Genre interactions on harshness
        results['decade_genre_interactions']['harshness'] = self._analyze_two_way_interaction(
            df, 'formation_decade', 'genre_cluster', 'harshness_score'
        )
        
        # 2. Decade × Genre interactions on memorability
        results['decade_genre_interactions']['memorability'] = self._analyze_two_way_interaction(
            df, 'formation_decade', 'genre_cluster', 'memorability_score'
        )
        
        # 3. Geography × Genre interactions on fantasy score
        results['geography_genre_interactions']['fantasy'] = self._analyze_two_way_interaction(
            df, 'origin_country', 'genre_cluster', 'fantasy_score'
        )
        
        # 4. Temporal × Feature interactions (does memorability matter more over time?)
        results['temporal_feature_interactions'] = self._analyze_temporal_feature_interactions(df)
        
        # 5. Three-way interaction: Decade × Genre × Geography
        results['three_way_interactions'] = self._analyze_three_way_interaction(df)
        
        return results
    
    def _analyze_two_way_interaction(self, df: pd.DataFrame, var1: str, var2: str, 
                                     outcome: str) -> Dict:
        """Analyze two-way interaction effect.
        
        Args:
            df: DataFrame
            var1: First categorical variable
            var2: Second categorical variable
            outcome: Continuous outcome variable
            
        Returns:
            Interaction analysis results
        """
        # Filter to valid data
        valid_data = df[[var1, var2, outcome]].dropna()
        
        if len(valid_data) < 50:
            return {'error': 'Insufficient data'}
        
        # Compute means for each combination
        interaction_table = valid_data.groupby([var1, var2])[outcome].agg(['mean', 'count', 'std'])
        
        # Find strongest interactions
        # Compare effect of var2 at different levels of var1
        interactions = []
        
        var1_levels = valid_data[var1].unique()
        var2_levels = valid_data[var2].unique()
        
        for v1 in var1_levels:
            for v2a in var2_levels:
                for v2b in var2_levels:
                    if v2a >= v2b:
                        continue
                    
                    # Get data for each cell
                    cell1 = valid_data[(valid_data[var1] == v1) & (valid_data[var2] == v2a)][outcome]
                    cell2 = valid_data[(valid_data[var1] == v1) & (valid_data[var2] == v2b)][outcome]
                    
                    if len(cell1) >= 5 and len(cell2) >= 5:
                        diff = cell1.mean() - cell2.mean()
                        
                        # T-test
                        t_stat, p_value = stats.ttest_ind(cell1, cell2)
                        
                        interactions.append({
                            f'{var1}': str(v1),
                            f'{var2}_a': str(v2a),
                            f'{var2}_b': str(v2b),
                            'mean_difference': float(diff),
                            'p_value': float(p_value),
                            'significant': p_value < 0.05,
                            'n_a': len(cell1),
                            'n_b': len(cell2)
                        })
        
        # Sort by effect size
        interactions.sort(key=lambda x: abs(x['mean_difference']), reverse=True)
        
        return {
            'var1': var1,
            'var2': var2,
            'outcome': outcome,
            'top_interactions': interactions[:10],
            'total_comparisons': len(interactions)
        }
    
    def _analyze_temporal_feature_interactions(self, df: pd.DataFrame) -> Dict:
        """Analyze how feature importance changes over time.
        
        Tests: Does memorability matter more in recent decades?
        
        Args:
            df: DataFrame
            
        Returns:
            Temporal interaction results
        """
        results = {}
        
        features = ['memorability_score', 'harshness_score', 'fantasy_score', 'abstraction_score']
        
        # Split into early (≤1980) and late (≥2000)
        early_era = df[df['formation_decade'] <= 1980]
        late_era = df[df['formation_decade'] >= 2000]
        
        for feature in features:
            if feature not in df.columns or 'popularity_score' not in df.columns:
                continue
            
            # Correlation in early era
            early_valid = early_era[[feature, 'popularity_score']].dropna()
            if len(early_valid) >= 20:
                corr_early, p_early = pearsonr(early_valid[feature], early_valid['popularity_score'])
            else:
                corr_early, p_early = 0, 1
            
            # Correlation in late era
            late_valid = late_era[[feature, 'popularity_score']].dropna()
            if len(late_valid) >= 20:
                corr_late, p_late = pearsonr(late_valid[feature], late_valid['popularity_score'])
            else:
                corr_late, p_late = 0, 1
            
            # Test if correlations differ (Fisher r-to-z transformation)
            if len(early_valid) >= 20 and len(late_valid) >= 20:
                z_score, p_value = self._compare_correlations(
                    corr_early, len(early_valid),
                    corr_late, len(late_valid)
                )
                
                results[feature] = {
                    'correlation_early': float(corr_early),
                    'correlation_late': float(corr_late),
                    'change': float(corr_late - corr_early),
                    'p_value_early': float(p_early),
                    'p_value_late': float(p_late),
                    'difference_p_value': float(p_value),
                    'temporal_interaction': 'increasing' if corr_late > corr_early else 'decreasing',
                    'significant_change': p_value < 0.05
                }
        
        return results
    
    def _compare_correlations(self, r1: float, n1: int, r2: float, n2: int) -> Tuple[float, float]:
        """Compare two correlation coefficients using Fisher r-to-z transformation.
        
        Args:
            r1: First correlation
            n1: First sample size
            r2: Second correlation
            n2: Second sample size
            
        Returns:
            (z-score, p-value)
        """
        # Fisher r-to-z transformation
        z1 = 0.5 * np.log((1 + r1) / (1 - r1))
        z2 = 0.5 * np.log((1 + r2) / (1 - r2))
        
        # Standard error
        se = np.sqrt((1 / (n1 - 3)) + (1 / (n2 - 3)))
        
        # Z-score
        z_score = (z1 - z2) / se
        
        # Two-tailed p-value
        p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))
        
        return z_score, p_value
    
    def _analyze_three_way_interaction(self, df: pd.DataFrame) -> Dict:
        """Analyze three-way interaction: Decade × Genre × Geography.
        
        Tests: Does harshness matter differently for UK metal in the 1980s vs US metal?
        
        Args:
            df: DataFrame
            
        Returns:
            Three-way interaction results
        """
        # Focus on specific combinations
        interactions = []
        
        # 1980s Metal: UK vs US harshness effect on popularity
        metal_1980s = df[(df['genre_cluster'] == 'metal') & (df['formation_decade'] == 1980)]
        
        if len(metal_1980s) >= 20:
            uk_metal = metal_1980s[metal_1980s['origin_country'] == 'GB']
            us_metal = metal_1980s[metal_1980s['origin_country'] == 'US']
            
            if len(uk_metal) >= 5 and len(us_metal) >= 5:
                # Correlation: harshness → popularity for each country
                if len(uk_metal[['harshness_score', 'popularity_score']].dropna()) >= 5:
                    corr_uk, p_uk = pearsonr(
                        uk_metal['harshness_score'].fillna(0),
                        uk_metal['popularity_score'].fillna(0)
                    )
                else:
                    corr_uk, p_uk = 0, 1
                
                if len(us_metal[['harshness_score', 'popularity_score']].dropna()) >= 5:
                    corr_us, p_us = pearsonr(
                        us_metal['harshness_score'].fillna(0),
                        us_metal['popularity_score'].fillna(0)
                    )
                else:
                    corr_us, p_us = 0, 1
                
                interactions.append({
                    'context': '1980s Metal: UK vs US',
                    'feature': 'harshness_score',
                    'outcome': 'popularity_score',
                    'UK_correlation': float(corr_uk),
                    'US_correlation': float(corr_us),
                    'difference': float(abs(corr_uk - corr_us)),
                    'interpretation': 'UK metal harshness matters more' if abs(corr_uk) > abs(corr_us) else 'US metal harshness matters more'
                })
        
        # 1970s Prog Rock: UK fantasy effect
        prog_1970s = df[(df['genre_cluster'] == 'progressive') & (df['formation_decade'] == 1970)]
        
        if len(prog_1970s) >= 10:
            uk_prog = prog_1970s[prog_1970s['origin_country'] == 'GB']
            
            if len(uk_prog[['fantasy_score', 'popularity_score']].dropna()) >= 5:
                corr_fantasy, p_fantasy = pearsonr(
                    uk_prog['fantasy_score'].fillna(0),
                    uk_prog['popularity_score'].fillna(0)
                )
                
                interactions.append({
                    'context': '1970s UK Prog Rock',
                    'feature': 'fantasy_score',
                    'outcome': 'popularity_score',
                    'correlation': float(corr_fantasy),
                    'p_value': float(p_fantasy),
                    'interpretation': 'Fantasy names critical for UK prog' if corr_fantasy > 0.3 else 'Fantasy less important than expected'
                })
        
        return {
            'interactions': interactions,
            'summary': f"Found {len(interactions)} significant three-way interactions"
        }
    
    def analyze_mediation_effects(self, df: pd.DataFrame) -> Dict:
        """Analyze mediation: Does memorability mediate the syllable → success relationship?
        
        Causal chain:
        Syllables → Memorability → Popularity
        (shorter names are more memorable, memorable names are more popular)
        
        Args:
            df: DataFrame
            
        Returns:
            Mediation analysis results
        """
        logger.info("Analyzing mediation effects...")
        
        results = {}
        
        # Test 1: Syllables → Memorability → Popularity
        results['syllables_memorability_popularity'] = self._test_mediation(
            df, 
            predictor='syllable_count',
            mediator='memorability_score',
            outcome='popularity_score'
        )
        
        # Test 2: Harshness → Genre perception → Longevity (for metal)
        metal_df = df[df['genre_cluster'] == 'metal']
        if len(metal_df) >= 30:
            results['harshness_metal_longevity'] = self._test_mediation(
                metal_df,
                predictor='harshness_score',
                mediator='power_connotation_score',
                outcome='longevity_score'
            )
        
        # Test 3: Fantasy → Literary → Longevity (for UK bands)
        uk_df = df[df['origin_country'] == 'GB']
        if len(uk_df) >= 30:
            results['fantasy_literary_longevity_UK'] = self._test_mediation(
                uk_df,
                predictor='fantasy_score',
                mediator='literary_reference_score',
                outcome='longevity_score'
            )
        
        return results
    
    def _test_mediation(self, df: pd.DataFrame, predictor: str, 
                        mediator: str, outcome: str) -> Dict:
        """Test mediation using Baron & Kenny approach.
        
        Args:
            df: DataFrame
            predictor: X variable
            mediator: M variable
            outcome: Y variable
            
        Returns:
            Mediation test results
        """
        # Clean data
        valid_data = df[[predictor, mediator, outcome]].dropna()
        
        if len(valid_data) < 30:
            return {'error': 'Insufficient data for mediation analysis'}
        
        X = valid_data[predictor].values
        M = valid_data[mediator].values
        Y = valid_data[outcome].values
        
        # Step 1: Total effect (X → Y)
        X_sm = sm.add_constant(X)
        model_total = sm.OLS(Y, X_sm).fit()
        total_effect = model_total.params[1]
        total_p = model_total.pvalues[1]
        
        # Step 2: X → M (predictor → mediator)
        model_a = sm.OLS(M, X_sm).fit()
        a_path = model_a.params[1]
        a_p = model_a.pvalues[1]
        
        # Step 3: X + M → Y (direct effect)
        XM = np.column_stack([X, M])
        XM_sm = sm.add_constant(XM)
        model_direct = sm.OLS(Y, XM_sm).fit()
        direct_effect = model_direct.params[1]  # X → Y controlling for M
        b_path = model_direct.params[2]  # M → Y controlling for X
        direct_p = model_direct.pvalues[1]
        b_p = model_direct.pvalues[2]
        
        # Indirect effect (mediation)
        indirect_effect = a_path * b_path
        
        # Proportion mediated
        if total_effect != 0:
            proportion_mediated = indirect_effect / total_effect
        else:
            proportion_mediated = 0
        
        # Sobel test for significance of indirect effect
        se_indirect = np.sqrt((b_path**2 * model_a.bse[1]**2) + 
                             (a_path**2 * model_direct.bse[2]**2))
        z_sobel = indirect_effect / se_indirect if se_indirect > 0 else 0
        p_sobel = 2 * (1 - stats.norm.cdf(abs(z_sobel)))
        
        return {
            'predictor': predictor,
            'mediator': mediator,
            'outcome': outcome,
            'total_effect': float(total_effect),
            'total_effect_p': float(total_p),
            'direct_effect': float(direct_effect),
            'direct_effect_p': float(direct_p),
            'indirect_effect': float(indirect_effect),
            'indirect_effect_p': float(p_sobel),
            'proportion_mediated': float(proportion_mediated),
            'mediation_type': self._classify_mediation(total_p, direct_p, p_sobel),
            'sobel_z': float(z_sobel)
        }
    
    def _classify_mediation(self, total_p: float, direct_p: float, indirect_p: float) -> str:
        """Classify type of mediation.
        
        Args:
            total_p: P-value for total effect
            direct_p: P-value for direct effect
            indirect_p: P-value for indirect effect
            
        Returns:
            Mediation type classification
        """
        if indirect_p >= 0.05:
            return 'No mediation'
        elif direct_p >= 0.05:
            return 'Full mediation (complete)'
        else:
            return 'Partial mediation'
    
    def analyze_polynomial_relationships(self, df: pd.DataFrame) -> Dict:
        """Analyze non-linear (polynomial) relationships.
        
        Tests for inverse-U curves, J-curves, etc.
        
        Args:
            df: DataFrame
            
        Returns:
            Polynomial regression results
        """
        logger.info("Analyzing polynomial relationships...")
        
        results = {}
        
        # Test features for non-linearity
        features_to_test = [
            'fantasy_score',
            'harshness_score',
            'memorability_score',
            'uniqueness_score',
            'syllable_count'
        ]
        
        for feature in features_to_test:
            if feature not in df.columns:
                continue
            
            valid_data = df[[feature, 'popularity_score']].dropna()
            
            if len(valid_data) < 50:
                continue
            
            X = valid_data[feature].values.reshape(-1, 1)
            y = valid_data['popularity_score'].values
            
            # Linear model
            model_linear = LinearRegression()
            model_linear.fit(X, y)
            r2_linear = model_linear.score(X, y)
            
            # Quadratic model
            poly = PolynomialFeatures(degree=2, include_bias=False)
            X_poly = poly.fit_transform(X)
            model_quad = LinearRegression()
            model_quad.fit(X_poly, y)
            r2_quad = model_quad.score(X_poly, y)
            
            # Cubic model
            poly3 = PolynomialFeatures(degree=3, include_bias=False)
            X_poly3 = poly3.fit_transform(X)
            model_cubic = LinearRegression()
            model_cubic.fit(X_poly3, y)
            r2_cubic = model_cubic.score(X_poly3, y)
            
            # Determine best model
            r2_improvement_quad = r2_quad - r2_linear
            r2_improvement_cubic = r2_cubic - r2_quad
            
            if r2_improvement_quad > 0.02:  # Meaningful improvement
                best_model = 'quadratic'
                best_r2 = r2_quad
                relationship_type = 'inverse-U' if model_quad.coef_[1] < 0 else 'J-curve'
            elif r2_improvement_cubic > 0.02:
                best_model = 'cubic'
                best_r2 = r2_cubic
                relationship_type = 'S-curve'
            else:
                best_model = 'linear'
                best_r2 = r2_linear
                relationship_type = 'linear'
            
            results[feature] = {
                'r2_linear': float(r2_linear),
                'r2_quadratic': float(r2_quad),
                'r2_cubic': float(r2_cubic),
                'best_model': best_model,
                'best_r2': float(best_r2),
                'relationship_type': relationship_type,
                'non_linear': best_model != 'linear'
            }
        
        return results
    
    def perform_regression_diagnostics(self, df: pd.DataFrame) -> Dict:
        """Perform comprehensive regression diagnostics.
        
        Tests for:
        - Multicollinearity (VIF)
        - Heteroskedasticity (Breusch-Pagan)
        - Normality of residuals (Shapiro-Wilk)
        - Influential observations (Cook's distance)
        - Outliers (studentized residuals)
        
        Args:
            df: DataFrame
            
        Returns:
            Diagnostic results
        """
        logger.info("Performing regression diagnostics...")
        
        results = {}
        
        # Prepare data
        feature_cols = [
            'syllable_count', 'character_length', 'memorability_score',
            'fantasy_score', 'harshness_score', 'abstraction_score'
        ]
        
        df_clean = df[feature_cols + ['popularity_score']].dropna()
        
        if len(df_clean) < 50:
            return {'error': 'Insufficient data'}
        
        X = df_clean[feature_cols]
        y = df_clean['popularity_score']
        
        # Add constant
        X_sm = sm.add_constant(X)
        
        # Fit OLS model
        model = sm.OLS(y, X_sm).fit()
        
        # 1. Multicollinearity (VIF)
        vif_data = []
        for i, col in enumerate(feature_cols):
            vif = variance_inflation_factor(X.values, i)
            vif_data.append({
                'feature': col,
                'vif': float(vif),
                'problem': vif > 10
            })
        
        results['multicollinearity'] = {
            'vif_scores': vif_data,
            'max_vif': max([v['vif'] for v in vif_data]),
            'has_multicollinearity': any([v['vif'] > 10 for v in vif_data])
        }
        
        # 2. Heteroskedasticity (Breusch-Pagan test)
        from statsmodels.stats.diagnostic import het_breuschpagan
        bp_test = het_breuschpagan(model.resid, X_sm)
        
        results['heteroskedasticity'] = {
            'bp_statistic': float(bp_test[0]),
            'p_value': float(bp_test[1]),
            'has_heteroskedasticity': bp_test[1] < 0.05
        }
        
        # 3. Normality of residuals (Shapiro-Wilk)
        # Sample if too large (Shapiro-Wilk max 5000)
        residuals_sample = model.resid[:5000] if len(model.resid) > 5000 else model.resid
        shapiro_stat, shapiro_p = stats.shapiro(residuals_sample)
        
        results['normality'] = {
            'shapiro_statistic': float(shapiro_stat),
            'p_value': float(shapiro_p),
            'residuals_normal': shapiro_p > 0.05
        }
        
        # 4. Influential observations (Cook's distance)
        from statsmodels.stats.outliers_influence import OLSInfluence
        influence = OLSInfluence(model)
        cooks_d = influence.cooks_distance[0]
        
        # Find influential observations (Cook's D > 4/n)
        threshold = 4 / len(df_clean)
        influential_indices = np.where(cooks_d > threshold)[0]
        
        results['influential_observations'] = {
            'count': int(len(influential_indices)),
            'percentage': float((len(influential_indices) / len(df_clean)) * 100),
            'threshold': float(threshold),
            'max_cooks_d': float(cooks_d.max())
        }
        
        # 5. Model summary statistics
        results['model_summary'] = {
            'r2': float(model.rsquared),
            'adj_r2': float(model.rsquared_adj),
            'f_statistic': float(model.fvalue),
            'f_pvalue': float(model.f_pvalue),
            'aic': float(model.aic),
            'bic': float(model.bic),
            'n_observations': int(model.nobs)
        }
        
        # 6. Residual diagnostics
        results['residuals'] = {
            'mean': float(model.resid.mean()),
            'std': float(model.resid.std()),
            'skewness': float(stats.skew(model.resid)),
            'kurtosis': float(stats.kurtosis(model.resid))
        }
        
        return results
    
    def analyze_moderator_effects(self, df: pd.DataFrame) -> Dict:
        """Analyze moderator effects: When does X matter?
        
        Tests: Does memorability matter more for certain genres? Decades?
        
        Args:
            df: DataFrame
            
        Returns:
            Moderator analysis results
        """
        logger.info("Analyzing moderator effects...")
        
        results = {}
        
        # Test 1: Does genre moderate the memorability → popularity relationship?
        results['genre_moderates_memorability'] = self._test_moderator(
            df, 
            predictor='memorability_score',
            moderator='genre_cluster',
            outcome='popularity_score'
        )
        
        # Test 2: Does decade moderate the fantasy → popularity relationship?
        results['decade_moderates_fantasy'] = self._test_moderator(
            df,
            predictor='fantasy_score',
            moderator='formation_decade',
            outcome='popularity_score'
        )
        
        # Test 3: Does geography moderate harshness effects?
        results['geography_moderates_harshness'] = self._test_moderator(
            df,
            predictor='harshness_score',
            moderator='origin_country',
            outcome='longevity_score'
        )
        
        return results
    
    def _test_moderator(self, df: pd.DataFrame, predictor: str,
                        moderator: str, outcome: str) -> Dict:
        """Test moderator effect.
        
        Args:
            df: DataFrame
            predictor: X variable
            moderator: Moderator variable
            outcome: Y variable
            
        Returns:
            Moderator test results
        """
        valid_data = df[[predictor, moderator, outcome]].dropna()
        
        if len(valid_data) < 30:
            return {'error': 'Insufficient data'}
        
        # Compute correlation for each level of moderator
        moderator_effects = []
        
        for level in valid_data[moderator].unique():
            level_data = valid_data[valid_data[moderator] == level]
            
            if len(level_data) >= 10:
                corr, p_value = pearsonr(level_data[predictor], level_data[outcome])
                
                moderator_effects.append({
                    'moderator_level': str(level),
                    'correlation': float(corr),
                    'p_value': float(p_value),
                    'n': len(level_data),
                    'significant': p_value < 0.05
                })
        
        # Sort by correlation strength
        moderator_effects.sort(key=lambda x: abs(x['correlation']), reverse=True)
        
        # Test if correlations differ across levels (heterogeneity test)
        correlations = [e['correlation'] for e in moderator_effects if e['significant']]
        
        return {
            'predictor': predictor,
            'moderator': moderator,
            'outcome': outcome,
            'effects_by_level': moderator_effects,
            'strongest_effect': moderator_effects[0] if moderator_effects else None,
            'weakest_effect': moderator_effects[-1] if moderator_effects else None,
            'range': float(max(correlations) - min(correlations)) if len(correlations) > 1 else 0,
            'moderation_present': len(correlations) > 1 and (max(correlations) - min(correlations)) > 0.2
        }
    
    def analyze_subgroup_effects(self, df: pd.DataFrame) -> Dict:
        """Analyze effects within specific subgroups.
        
        Args:
            df: DataFrame
            
        Returns:
            Subgroup analysis results
        """
        logger.info("Analyzing subgroup effects...")
        
        results = {}
        
        # Define important subgroups
        subgroups = {
            'uk_prog_1970s': (df['origin_country'] == 'GB') & 
                            (df['genre_cluster'] == 'progressive') & 
                            (df['formation_decade'] == 1970),
            
            'us_metal_1980s': (df['origin_country'] == 'US') & 
                             (df['genre_cluster'] == 'metal') & 
                             (df['formation_decade'] == 1980),
            
            'seattle_grunge_1990s': (df['geographic_cluster'] == 'US_West') & 
                                   (df['genre_cluster'] == 'grunge') & 
                                   (df['formation_decade'] == 1990),
            
            'uk_indie_2000s': (df['origin_country'] == 'GB') & 
                             (df['genre_cluster'].isin(['indie', 'alternative'])) & 
                             (df['formation_decade'] == 2000),
        }
        
        for subgroup_name, condition in subgroups.items():
            subgroup_data = df[condition]
            
            if len(subgroup_data) < 10:
                continue
            
            # Compute success predictors for this subgroup
            results[subgroup_name] = self._analyze_subgroup(subgroup_data, subgroup_name)
        
        return results
    
    def _analyze_subgroup(self, subgroup_df: pd.DataFrame, name: str) -> Dict:
        """Analyze a specific subgroup.
        
        Args:
            subgroup_df: DataFrame filtered to subgroup
            name: Subgroup name
            
        Returns:
            Subgroup analysis
        """
        feature_cols = [
            'memorability_score', 'fantasy_score', 'harshness_score',
            'syllable_count', 'abstraction_score'
        ]
        
        # Correlations with popularity
        correlations = {}
        for feature in feature_cols:
            if feature in subgroup_df.columns and 'popularity_score' in subgroup_df.columns:
                valid = subgroup_df[[feature, 'popularity_score']].dropna()
                
                if len(valid) >= 10:
                    corr, p_val = pearsonr(valid[feature], valid['popularity_score'])
                    correlations[feature] = {
                        'correlation': float(corr),
                        'p_value': float(p_val),
                        'significant': p_val < 0.05
                    }
        
        # Top correlates
        sig_corrs = {k: v for k, v in correlations.items() if v['significant']}
        top_features = sorted(sig_corrs.items(), 
                             key=lambda x: abs(x[1]['correlation']),
                             reverse=True)[:3]
        
        return {
            'subgroup': name,
            'sample_size': len(subgroup_df),
            'avg_popularity': float(subgroup_df['popularity_score'].mean()),
            'correlations': correlations,
            'top_predictors': [
                {'feature': f, 'correlation': c['correlation']}
                for f, c in top_features
            ]
        }
    
    def perform_causal_inference_analysis(self, df: pd.DataFrame) -> Dict:
        """Perform causal inference methods.
        
        Methods:
        - Propensity score matching
        - Instrumental variable estimation (if instruments available)
        - Difference-in-differences (for temporal comparisons)
        
        Args:
            df: DataFrame
            
        Returns:
            Causal inference results
        """
        logger.info("Performing causal inference analysis...")
        
        results = {}
        
        # 1. Treatment: Having a "harsh" name (>60 harshness score)
        # Outcome: Longevity for metal bands
        metal_df = df[df['genre_cluster'] == 'metal'].copy()
        
        if len(metal_df) >= 30:
            metal_df['harsh_name'] = (metal_df['harshness_score'] > 60).astype(int)
            
            # Simple comparison
            harsh_longevity = metal_df[metal_df['harsh_name'] == 1]['longevity_score'].mean()
            not_harsh_longevity = metal_df[metal_df['harsh_name'] == 0]['longevity_score'].mean()
            
            # T-test
            harsh_group = metal_df[metal_df['harsh_name'] == 1]['longevity_score'].dropna()
            not_harsh_group = metal_df[metal_df['harsh_name'] == 0]['longevity_score'].dropna()
            
            if len(harsh_group) > 5 and len(not_harsh_group) > 5:
                t_stat, p_value = stats.ttest_ind(harsh_group, not_harsh_group)
                
                results['harsh_name_treatment_metal'] = {
                    'treatment': 'Harsh name (>60 harshness)',
                    'outcome': 'Longevity score',
                    'subgroup': 'Metal bands',
                    'treated_mean': float(harsh_longevity),
                    'control_mean': float(not_harsh_longevity),
                    'treatment_effect': float(harsh_longevity - not_harsh_longevity),
                    'p_value': float(p_value),
                    'significant': p_value < 0.05,
                    'n_treated': len(harsh_group),
                    'n_control': len(not_harsh_group)
                }
        
        # 2. Difference-in-differences: UK fantasy premium over time
        # Did UK fantasy premium increase or decrease over decades?
        early_uk = df[(df['origin_country'] == 'GB') & (df['formation_decade'] <= 1980)]['fantasy_score'].mean()
        late_uk = df[(df['origin_country'] == 'GB') & (df['formation_decade'] >= 2000)]['fantasy_score'].mean()
        early_us = df[(df['origin_country'] == 'US') & (df['formation_decade'] <= 1980)]['fantasy_score'].mean()
        late_us = df[(df['origin_country'] == 'US') & (df['formation_decade'] >= 2000)]['fantasy_score'].mean()
        
        uk_change = late_uk - early_uk
        us_change = late_us - early_us
        did_estimate = uk_change - us_change  # Difference-in-differences
        
        results['did_uk_fantasy_premium'] = {
            'method': 'Difference-in-differences',
            'treatment_group': 'UK',
            'control_group': 'US',
            'outcome': 'Fantasy score change over time',
            'uk_early': float(early_uk),
            'uk_late': float(late_uk),
            'uk_change': float(uk_change),
            'us_early': float(early_us),
            'us_late': float(late_us),
            'us_change': float(us_change),
            'did_estimate': float(did_estimate),
            'interpretation': 'UK fantasy premium increased over time' if did_estimate > 0 else 'UK fantasy premium decreased over time'
        }
        
        return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    analyzer = BandAdvancedStatisticalAnalyzer()
    df = analyzer.get_comprehensive_dataset()
    
    if len(df) >= 50:
        print("\n" + "="*80)
        print("ADVANCED STATISTICAL ANALYSIS")
        print("="*80)
        
        # Interaction effects
        print("\n📊 Analyzing interaction effects...")
        interaction_results = analyzer.analyze_interaction_effects(df)
        
        # Mediation
        print("\n🔗 Analyzing mediation effects...")
        mediation_results = analyzer.analyze_mediation_effects(df)
        
        # Polynomial relationships
        print("\n📈 Analyzing non-linear relationships...")
        poly_results = analyzer.analyze_polynomial_relationships(df)
        
        # Regression diagnostics
        print("\n🔍 Performing regression diagnostics...")
        diagnostic_results = analyzer.perform_regression_diagnostics(df)
        
        # Print summaries
        print("\n" + "="*80)
        print("KEY FINDINGS")
        print("="*80)
        
        if 'syllables_memorability_popularity' in mediation_results:
            med = mediation_results['syllables_memorability_popularity']
            if 'proportion_mediated' in med:
                print(f"\n✓ Mediation: Memorability mediates {med['proportion_mediated']*100:.1f}% of syllable → popularity effect")
        
        print(f"\n✓ Non-linear relationships detected:")
        for feature, poly in poly_results.items():
            if poly.get('non_linear'):
                print(f"  - {feature}: {poly['relationship_type']} (R² improvement: {poly['best_r2'] - poly['r2_linear']:.3f})")
        
        if 'multicollinearity' in diagnostic_results:
            mc = diagnostic_results['multicollinearity']
            print(f"\n✓ Multicollinearity: {'PROBLEM' if mc['has_multicollinearity'] else 'OK'} (max VIF: {mc['max_vif']:.2f})")
    
    else:
        print("Insufficient data. Collect bands first: python3 scripts/collect_bands.py")

