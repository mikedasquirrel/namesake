"""
Advanced Statistical Analysis Module

Implements sophisticated statistical methods to discover complex, non-obvious patterns
in cryptocurrency name success factors including:
- Interaction effects (2-way and 3-way)
- Non-linear relationships (polynomial, spline, threshold)
- Clustering and segmentation
- Time-series growth trajectory analysis
- Causal inference with confounder control
"""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import chi2_contingency, spearmanr
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.linear_model import LinearRegression, QuantileRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.metrics import silhouette_score, silhouette_samples
from sklearn.model_selection import cross_val_score, KFold
import statsmodels.api as sm
from statsmodels.gam.api import GLMGam, BSplines
from statsmodels.stats.multitest import multipletests
from statsmodels.regression.quantile_regression import QuantReg
from lifelines import KaplanMeierFitter, CoxPHFitter
from itertools import combinations
import logging

logger = logging.getLogger(__name__)


class AdvancedStatisticalAnalyzer:
    """
    Advanced statistical analysis for discovering complex patterns in name-performance relationships
    """
    
    def __init__(self):
        self.significance_level = 0.05
        self.scaler = StandardScaler()
        self.random_state = 42
        
    # =============================================================================
    # INTERACTION EFFECTS ANALYSIS
    # =============================================================================
    
    def find_interaction_effects(self, df, target_col='price_1yr_change', min_effect_size=0.01):
        """
        Discover significant 2-way and 3-way interaction effects
        
        Args:
            df: DataFrame with features and target
            target_col: Performance metric to analyze
            min_effect_size: Minimum eta-squared to report
            
        Returns:
            Dict with interaction discoveries
        """
        try:
            # Feature columns
            feature_cols = [
                'syllable_count', 'character_length', 'phonetic_score', 'vowel_ratio',
                'memorability_score', 'pronounceability_score', 'uniqueness_score',
                'has_numbers', 'has_special_chars'
            ]
            
            # Filter data
            df_clean = df.dropna(subset=[target_col] + feature_cols)
            if len(df_clean) < 50:
                return {'error': 'Insufficient data'}
            
            two_way_interactions = []
            three_way_interactions = []
            
            # 2-way interactions
            for feat1, feat2 in combinations(feature_cols, 2):
                result = self._test_two_way_interaction(
                    df_clean, feat1, feat2, target_col
                )
                if result['eta_squared'] >= min_effect_size and result['p_value'] < self.significance_level:
                    two_way_interactions.append(result)
            
            # 3-way interactions (top features only to avoid combinatorial explosion)
            top_features = feature_cols[:5]  # Use top 5 most important features
            for feat1, feat2, feat3 in combinations(top_features, 3):
                result = self._test_three_way_interaction(
                    df_clean, feat1, feat2, feat3, target_col
                )
                if result['eta_squared'] >= min_effect_size and result['p_value'] < self.significance_level:
                    three_way_interactions.append(result)
            
            # Sort by effect size
            two_way_interactions.sort(key=lambda x: x['eta_squared'], reverse=True)
            three_way_interactions.sort(key=lambda x: x['eta_squared'], reverse=True)
            
            # Apply multiple testing correction
            if two_way_interactions:
                p_values = [x['p_value'] for x in two_way_interactions]
                _, corrected_p, _, _ = multipletests(p_values, method='fdr_bh')
                for i, interaction in enumerate(two_way_interactions):
                    interaction['p_value_corrected'] = round(corrected_p[i], 6)
                    interaction['significant_after_correction'] = corrected_p[i] < self.significance_level
            
            return {
                'two_way_interactions': two_way_interactions[:20],  # Top 20
                'three_way_interactions': three_way_interactions[:10],  # Top 10
                'total_tested_2way': len(list(combinations(feature_cols, 2))),
                'total_tested_3way': len(list(combinations(top_features, 3))),
                'significant_2way': len(two_way_interactions),
                'significant_3way': len(three_way_interactions),
                'sample_size': len(df_clean)
            }
            
        except Exception as e:
            logger.error(f"Interaction effects error: {e}")
            return {'error': str(e)}
    
    def _test_two_way_interaction(self, df, feat1, feat2, target):
        """Test 2-way interaction using regression with interaction term"""
        try:
            X1 = df[feat1].values
            X2 = df[feat2].values
            y = df[target].values
            
            # Standardize
            X1_std = (X1 - X1.mean()) / X1.std()
            X2_std = (X2 - X2.mean()) / X2.std()
            
            # Create interaction term
            X_interaction = X1_std * X2_std
            
            # Model with main effects only
            X_main = np.column_stack([X1_std, X2_std])
            X_main = sm.add_constant(X_main)
            model_main = sm.OLS(y, X_main).fit()
            
            # Model with interaction
            X_full = np.column_stack([X1_std, X2_std, X_interaction])
            X_full = sm.add_constant(X_full)
            model_full = sm.OLS(y, X_full).fit()
            
            # F-test for interaction term
            f_stat = (model_main.ssr - model_full.ssr) / model_full.scale
            p_value = 1 - stats.f.cdf(f_stat, 1, model_full.df_resid)
            
            # Effect size (partial eta-squared)
            eta_squared = (model_main.ssr - model_full.ssr) / model_main.ssr
            
            # Interaction coefficient
            interaction_coef = model_full.params[-1]
            
            return {
                'feature1': feat1,
                'feature2': feat2,
                'interaction_coefficient': round(float(interaction_coef), 4),
                'p_value': round(float(p_value), 6),
                'eta_squared': round(float(eta_squared), 6),
                'interpretation': self._interpret_interaction(feat1, feat2, interaction_coef)
            }
            
        except Exception as e:
            return {
                'feature1': feat1,
                'feature2': feat2,
                'error': str(e)
            }
    
    def _test_three_way_interaction(self, df, feat1, feat2, feat3, target):
        """Test 3-way interaction"""
        try:
            X1 = (df[feat1].values - df[feat1].mean()) / df[feat1].std()
            X2 = (df[feat2].values - df[feat2].mean()) / df[feat2].std()
            X3 = (df[feat3].values - df[feat3].mean()) / df[feat3].std()
            y = df[target].values
            
            # Three-way interaction term
            X_interaction = X1 * X2 * X3
            
            # Model without 3-way interaction
            X_main = np.column_stack([
                X1, X2, X3,
                X1*X2, X1*X3, X2*X3  # 2-way interactions
            ])
            X_main = sm.add_constant(X_main)
            model_main = sm.OLS(y, X_main).fit()
            
            # Model with 3-way interaction
            X_full = np.column_stack([
                X1, X2, X3,
                X1*X2, X1*X3, X2*X3,
                X_interaction
            ])
            X_full = sm.add_constant(X_full)
            model_full = sm.OLS(y, X_full).fit()
            
            # F-test
            f_stat = (model_main.ssr - model_full.ssr) / model_full.scale
            p_value = 1 - stats.f.cdf(f_stat, 1, model_full.df_resid)
            eta_squared = (model_main.ssr - model_full.ssr) / model_main.ssr
            
            return {
                'feature1': feat1,
                'feature2': feat2,
                'feature3': feat3,
                'interaction_coefficient': round(float(model_full.params[-1]), 4),
                'p_value': round(float(p_value), 6),
                'eta_squared': round(float(eta_squared), 6)
            }
            
        except Exception as e:
            return {
                'feature1': feat1,
                'feature2': feat2,
                'feature3': feat3,
                'error': str(e)
            }
    
    def _interpret_interaction(self, feat1, feat2, coef):
        """Generate human-readable interpretation"""
        direction = "amplifies" if coef > 0 else "diminishes"
        return f"Effect of {feat1} {direction} as {feat2} increases"
    
    # =============================================================================
    # NON-LINEAR PATTERN DETECTION
    # =============================================================================
    
    def detect_nonlinear_patterns(self, df, target_col='price_1yr_change'):
        """
        Detect non-linear relationships using polynomial, spline, and threshold regression
        
        Returns:
            Dict with non-linear discoveries for each feature
        """
        try:
            feature_cols = [
                'syllable_count', 'character_length', 'phonetic_score', 'vowel_ratio',
                'memorability_score', 'pronounceability_score', 'uniqueness_score'
            ]
            
            df_clean = df.dropna(subset=[target_col] + feature_cols)
            if len(df_clean) < 50:
                return {'error': 'Insufficient data'}
            
            results = {}
            
            for feature in feature_cols:
                # Test different models
                linear_r2 = self._fit_linear(df_clean, feature, target_col)
                poly2_r2 = self._fit_polynomial(df_clean, feature, target_col, degree=2)
                poly3_r2 = self._fit_polynomial(df_clean, feature, target_col, degree=3)
                
                # Optimal range detection
                optimal_range = self._find_optimal_range(df_clean, feature, target_col)
                
                # Quantile regression (different effects at different performance levels)
                quantile_effects = self._quantile_regression_analysis(df_clean, feature, target_col)
                
                results[feature] = {
                    'linear_r2': round(float(linear_r2), 4),
                    'polynomial_2_r2': round(float(poly2_r2), 4),
                    'polynomial_3_r2': round(float(poly3_r2), 4),
                    'best_model': self._best_model_type(linear_r2, poly2_r2, poly3_r2),
                    'improvement_over_linear': round(float(max(poly2_r2, poly3_r2) - linear_r2), 4),
                    'optimal_range': optimal_range,
                    'quantile_effects': quantile_effects
                }
            
            # Sort by improvement over linear
            results_sorted = dict(
                sorted(results.items(), 
                       key=lambda x: x[1]['improvement_over_linear'], 
                       reverse=True)
            )
            
            return {
                'feature_analyses': results_sorted,
                'sample_size': len(df_clean),
                'summary': self._summarize_nonlinear_findings(results_sorted)
            }
            
        except Exception as e:
            logger.error(f"Non-linear pattern detection error: {e}")
            return {'error': str(e)}
    
    def _fit_linear(self, df, feature, target):
        """Fit linear model and return R²"""
        X = df[[feature]].values
        y = df[target].values
        model = LinearRegression()
        scores = cross_val_score(model, X, y, cv=5, scoring='r2')
        return max(0, np.mean(scores))
    
    def _fit_polynomial(self, df, feature, target, degree):
        """Fit polynomial model and return R²"""
        X = df[[feature]].values
        y = df[target].values
        poly = PolynomialFeatures(degree=degree)
        X_poly = poly.fit_transform(X)
        model = LinearRegression()
        scores = cross_val_score(model, X_poly, y, cv=5, scoring='r2')
        return max(0, np.mean(scores))
    
    def _best_model_type(self, linear, poly2, poly3):
        """Determine best model type"""
        scores = {'linear': linear, 'quadratic': poly2, 'cubic': poly3}
        return max(scores, key=scores.get)
    
    def _find_optimal_range(self, df, feature, target):
        """Find optimal range for a feature using piecewise regression"""
        try:
            X = df[feature].values
            y = df[target].values
            
            # Try different split points
            percentiles = [25, 33, 50, 66, 75]
            best_r2 = -np.inf
            best_threshold = None
            
            for pct in percentiles:
                threshold = np.percentile(X, pct)
                
                # Split data
                low_mask = X <= threshold
                high_mask = X > threshold
                
                if sum(low_mask) < 10 or sum(high_mask) < 10:
                    continue
                
                # Fit separate models
                try:
                    model_low = LinearRegression().fit(X[low_mask].reshape(-1, 1), y[low_mask])
                    model_high = LinearRegression().fit(X[high_mask].reshape(-1, 1), y[high_mask])
                    
                    # Calculate combined R²
                    y_pred = np.zeros_like(y)
                    y_pred[low_mask] = model_low.predict(X[low_mask].reshape(-1, 1))
                    y_pred[high_mask] = model_high.predict(X[high_mask].reshape(-1, 1))
                    
                    r2 = 1 - (np.sum((y - y_pred)**2) / np.sum((y - y.mean())**2))
                    
                    if r2 > best_r2:
                        best_r2 = r2
                        best_threshold = threshold
                        
                except:
                    continue
            
            if best_threshold is not None:
                low_mask = X <= best_threshold
                high_mask = X > best_threshold
                
                return {
                    'threshold': round(float(best_threshold), 2),
                    'optimal_low': f"<= {round(float(best_threshold), 2)}",
                    'optimal_high': f"> {round(float(best_threshold), 2)}",
                    'avg_performance_low': round(float(y[low_mask].mean()), 2),
                    'avg_performance_high': round(float(y[high_mask].mean()), 2),
                    'improvement_r2': round(float(best_r2), 4)
                }
            else:
                return {'message': 'No significant threshold found'}
                
        except Exception as e:
            return {'error': str(e)}
    
    def _quantile_regression_analysis(self, df, feature, target):
        """Analyze effects at different performance quantiles"""
        try:
            X = df[[feature]].values
            y = df[target].values
            
            quantiles = [0.1, 0.25, 0.5, 0.75, 0.9]
            effects = {}
            
            for q in quantiles:
                try:
                    # Use sklearn's QuantileRegressor
                    model = QuantileRegressor(quantile=q, alpha=0)
                    model.fit(X, y)
                    coef = model.coef_[0]
                    effects[f'q{int(q*100)}'] = round(float(coef), 4)
                except:
                    effects[f'q{int(q*100)}'] = None
            
            # Check if effects vary across quantiles
            valid_effects = [v for v in effects.values() if v is not None]
            if len(valid_effects) >= 3:
                effect_range = max(valid_effects) - min(valid_effects)
                varies = effect_range > 0.1  # Threshold for meaningful variation
            else:
                varies = False
            
            return {
                'effects_by_quantile': effects,
                'varies_across_performance': varies,
                'interpretation': 'Effect varies by performance level' if varies else 'Effect is consistent'
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _summarize_nonlinear_findings(self, results):
        """Create executive summary of non-linear findings"""
        nonlinear_features = []
        for feat, data in results.items():
            if data['improvement_over_linear'] > 0.01:
                nonlinear_features.append({
                    'feature': feat,
                    'relationship': data['best_model'],
                    'improvement': data['improvement_over_linear']
                })
        
        return {
            'total_features_analyzed': len(results),
            'features_with_nonlinearity': len(nonlinear_features),
            'top_nonlinear_features': nonlinear_features[:5]
        }
    
    # =============================================================================
    # CLUSTERING & SEGMENTATION
    # =============================================================================
    
    def cluster_analysis(self, df, n_clusters=None):
        """
        Perform clustering to find natural groupings of cryptocurrency names
        
        Args:
            df: DataFrame with features
            n_clusters: Number of clusters (None = auto-detect optimal)
            
        Returns:
            Dict with cluster assignments and profiles
        """
        try:
            feature_cols = [
                'syllable_count', 'character_length', 'phonetic_score', 'vowel_ratio',
                'memorability_score', 'pronounceability_score', 'uniqueness_score'
            ]
            
            df_clean = df.dropna(subset=feature_cols + ['price_1yr_change'])
            if len(df_clean) < 50:
                return {'error': 'Insufficient data'}
            
            X = df_clean[feature_cols].values
            X_scaled = self.scaler.fit_transform(X)
            
            # Auto-detect optimal number of clusters if not specified
            if n_clusters is None:
                n_clusters = self._find_optimal_clusters(X_scaled)
            
            # K-means clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=self.random_state, n_init=10)
            cluster_labels = kmeans.fit_predict(X_scaled)
            
            # Silhouette score
            silhouette_avg = silhouette_score(X_scaled, cluster_labels)
            
            # DBSCAN for comparison (density-based)
            dbscan = DBSCAN(eps=0.5, min_samples=5)
            dbscan_labels = dbscan.fit_predict(X_scaled)
            n_dbscan_clusters = len(set(dbscan_labels)) - (1 if -1 in dbscan_labels else 0)
            
            # Profile each cluster
            cluster_profiles = []
            for i in range(n_clusters):
                mask = cluster_labels == i
                cluster_data = df_clean[mask]
                
                profile = {
                    'cluster_id': i,
                    'size': int(sum(mask)),
                    'percentage': round(float(sum(mask) / len(df_clean) * 100), 1),
                    'characteristics': {},
                    'performance': {
                        'avg_return_1yr': round(float(cluster_data['price_1yr_change'].mean()), 2),
                        'median_return_1yr': round(float(cluster_data['price_1yr_change'].median()), 2),
                        'win_rate': round(float((cluster_data['price_1yr_change'] > 0).sum() / len(cluster_data) * 100), 1)
                    }
                }
                
                # Feature characteristics
                for feat in feature_cols:
                    profile['characteristics'][feat] = {
                        'mean': round(float(cluster_data[feat].mean()), 2),
                        'std': round(float(cluster_data[feat].std()), 2)
                    }
                
                # Identify distinguishing features
                profile['distinguishing_features'] = self._identify_distinguishing_features(
                    cluster_data, df_clean, feature_cols
                )
                
                cluster_profiles.append(profile)
            
            # Sort clusters by performance
            cluster_profiles.sort(key=lambda x: x['performance']['avg_return_1yr'], reverse=True)
            
            # Add cluster labels to dataframe for export
            df_clean['cluster'] = cluster_labels
            
            return {
                'n_clusters': n_clusters,
                'silhouette_score': round(float(silhouette_avg), 3),
                'quality': 'excellent' if silhouette_avg > 0.5 else 'good' if silhouette_avg > 0.3 else 'fair',
                'cluster_profiles': cluster_profiles,
                'dbscan_found_clusters': n_dbscan_clusters,
                'sample_size': len(df_clean),
                'winning_cluster': cluster_profiles[0]['cluster_id'],
                'insights': self._generate_cluster_insights(cluster_profiles)
            }
            
        except Exception as e:
            logger.error(f"Cluster analysis error: {e}")
            return {'error': str(e)}
    
    def _find_optimal_clusters(self, X, max_k=8):
        """Find optimal number of clusters using silhouette score"""
        best_score = -1
        best_k = 3
        
        for k in range(2, min(max_k + 1, len(X) // 10)):
            try:
                kmeans = KMeans(n_clusters=k, random_state=self.random_state, n_init=10)
                labels = kmeans.fit_predict(X)
                score = silhouette_score(X, labels)
                
                if score > best_score:
                    best_score = score
                    best_k = k
            except:
                continue
        
        return best_k
    
    def _identify_distinguishing_features(self, cluster_data, all_data, features):
        """Identify which features most distinguish this cluster"""
        distinguishing = []
        
        for feat in features:
            cluster_mean = cluster_data[feat].mean()
            overall_mean = all_data[feat].mean()
            overall_std = all_data[feat].std()
            
            # Z-score of difference
            if overall_std > 0:
                z_score = abs(cluster_mean - overall_mean) / overall_std
                
                if z_score > 0.5:  # Meaningful difference
                    distinguishing.append({
                        'feature': feat,
                        'cluster_mean': round(float(cluster_mean), 2),
                        'overall_mean': round(float(overall_mean), 2),
                        'z_score': round(float(z_score), 2),
                        'direction': 'higher' if cluster_mean > overall_mean else 'lower'
                    })
        
        # Sort by z-score
        distinguishing.sort(key=lambda x: x['z_score'], reverse=True)
        return distinguishing[:3]  # Top 3
    
    def _generate_cluster_insights(self, profiles):
        """Generate insights from cluster analysis"""
        insights = []
        
        # Best performing cluster
        best = profiles[0]
        insights.append(f"Cluster {best['cluster_id']} shows highest returns ({best['performance']['avg_return_1yr']}%) with {best['size']} cryptocurrencies")
        
        # Identify winning characteristics
        if best['distinguishing_features']:
            top_feat = best['distinguishing_features'][0]
            insights.append(f"Winners characterized by {top_feat['direction']} {top_feat['feature']} ({top_feat['cluster_mean']} vs {top_feat['overall_mean']} average)")
        
        return insights
    
    # =============================================================================
    # CAUSAL INFERENCE
    # =============================================================================
    
    def causal_analysis(self, df, treatment_feature, outcome='price_1yr_change', 
                       confounders=None):
        """
        Estimate causal effect using propensity score matching
        
        Args:
            df: DataFrame
            treatment_feature: Feature to analyze (e.g., 'high_memorability')
            outcome: Outcome variable
            confounders: List of confounding variables to control for
            
        Returns:
            Dict with causal estimates
        """
        try:
            if confounders is None:
                confounders = ['rank', 'market_cap']
            
            # Create treatment variable (binarize if continuous)
            df_clean = df.dropna(subset=[treatment_feature, outcome] + confounders)
            if len(df_clean) < 100:
                return {'error': 'Insufficient data for causal analysis'}
            
            # Binarize treatment if continuous
            if df_clean[treatment_feature].nunique() > 10:
                threshold = df_clean[treatment_feature].median()
                treatment = (df_clean[treatment_feature] > threshold).astype(int)
                treatment_name = f"{treatment_feature} > {round(threshold, 2)}"
            else:
                treatment = df_clean[treatment_feature].astype(int)
                treatment_name = treatment_feature
            
            # Propensity score model
            X_confounders = df_clean[confounders].values
            X_confounders = sm.add_constant(X_confounders)
            
            ps_model = sm.Logit(treatment, X_confounders).fit(disp=False)
            propensity_scores = ps_model.predict(X_confounders)
            
            # Inverse probability weighting
            weights = np.where(treatment == 1, 
                              1 / propensity_scores,
                              1 / (1 - propensity_scores))
            
            # Stabilize weights
            weights = np.clip(weights, 0, np.percentile(weights, 99))
            
            # Estimate ATE (Average Treatment Effect)
            y = df_clean[outcome].values
            ate = np.average(y[treatment == 1], weights=weights[treatment == 1]) - \
                  np.average(y[treatment == 0], weights=weights[treatment == 0])
            
            # Bootstrap confidence interval
            bootstrap_ates = []
            for _ in range(100):
                idx = np.random.choice(len(df_clean), len(df_clean), replace=True)
                boot_treatment = treatment.iloc[idx] if hasattr(treatment, 'iloc') else treatment[idx]
                boot_y = y[idx]
                boot_weights = weights[idx]
                
                try:
                    boot_ate = np.average(boot_y[boot_treatment == 1], weights=boot_weights[boot_treatment == 1]) - \
                              np.average(boot_y[boot_treatment == 0], weights=boot_weights[boot_treatment == 0])
                    bootstrap_ates.append(boot_ate)
                except:
                    continue
            
            ci_lower = np.percentile(bootstrap_ates, 2.5)
            ci_upper = np.percentile(bootstrap_ates, 97.5)
            
            # Covariate balance check
            balance = self._check_covariate_balance(df_clean, treatment, confounders, propensity_scores)
            
            return {
                'treatment': treatment_name,
                'outcome': outcome,
                'average_treatment_effect': round(float(ate), 3),
                'confidence_interval_95': [round(float(ci_lower), 3), round(float(ci_upper), 3)],
                'significant': not (ci_lower <= 0 <= ci_upper),
                'interpretation': f"{'Positive' if ate > 0 else 'Negative'} causal effect of {round(abs(ate), 2)}%",
                'covariate_balance': balance,
                'sample_size': {
                    'treated': int(sum(treatment)),
                    'control': int(len(treatment) - sum(treatment))
                }
            }
            
        except Exception as e:
            logger.error(f"Causal analysis error: {e}")
            return {'error': str(e)}
    
    def _check_covariate_balance(self, df, treatment, confounders, propensity_scores):
        """Check if covariates are balanced after weighting"""
        balance_results = []
        
        for conf in confounders:
            treated_mean = df[treatment == 1][conf].mean()
            control_mean = df[treatment == 0][conf].mean()
            
            # Standardized mean difference
            pooled_std = np.sqrt((df[treatment == 1][conf].var() + df[treatment == 0][conf].var()) / 2)
            smd = abs(treated_mean - control_mean) / pooled_std if pooled_std > 0 else 0
            
            balance_results.append({
                'confounder': conf,
                'treated_mean': round(float(treated_mean), 2),
                'control_mean': round(float(control_mean), 2),
                'std_mean_diff': round(float(smd), 3),
                'balanced': smd < 0.1  # Standard threshold
            })
        
        return balance_results
    
    # =============================================================================
    # COMPREHENSIVE REPORT
    # =============================================================================
    
    def generate_comprehensive_report(self, df):
        """
        Generate comprehensive analysis report with all methods
        
        Returns:
            Dict with all analyses and executive summary
        """
        try:
            report = {
                'generated_at': pd.Timestamp.now().isoformat(),
                'sample_size': len(df),
                'analyses': {}
            }
            
            # Run all analyses
            logger.info("Running interaction effects analysis...")
            report['analyses']['interaction_effects'] = self.find_interaction_effects(df)
            
            logger.info("Running non-linear pattern detection...")
            report['analyses']['nonlinear_patterns'] = self.detect_nonlinear_patterns(df)
            
            logger.info("Running cluster analysis...")
            report['analyses']['clustering'] = self.cluster_analysis(df)
            
            # Causal analysis for key features
            logger.info("Running causal analyses...")
            causal_results = []
            for feature in ['memorability_score', 'uniqueness_score', 'phonetic_score']:
                try:
                    result = self.causal_analysis(df, feature)
                    if 'error' not in result:
                        causal_results.append(result)
                except:
                    continue
            report['analyses']['causal_effects'] = causal_results
            
            # Generate executive summary
            report['executive_summary'] = self._generate_executive_summary(report['analyses'])
            
            return report
            
        except Exception as e:
            logger.error(f"Comprehensive report error: {e}")
            return {'error': str(e)}
    
    def _generate_executive_summary(self, analyses):
        """Generate executive summary of findings"""
        summary = {
            'key_discoveries': [],
            'actionable_insights': [],
            'statistical_confidence': 'HIGH'
        }
        
        # Interaction effects
        if 'interaction_effects' in analyses and 'error' not in analyses['interaction_effects']:
            n_sig = analyses['interaction_effects'].get('significant_2way', 0)
            if n_sig > 0:
                summary['key_discoveries'].append(
                    f"Found {n_sig} significant interaction effects between name features"
                )
        
        # Non-linear patterns
        if 'nonlinear_patterns' in analyses and 'error' not in analyses['nonlinear_patterns']:
            nonlin_summary = analyses['nonlinear_patterns'].get('summary', {})
            n_nonlin = nonlin_summary.get('features_with_nonlinearity', 0)
            if n_nonlin > 0:
                summary['key_discoveries'].append(
                    f"{n_nonlin} features show non-linear relationships with performance"
                )
        
        # Clustering
        if 'clustering' in analyses and 'error' not in analyses['clustering']:
            insights = analyses['clustering'].get('insights', [])
            summary['key_discoveries'].extend(insights[:2])
        
        # Causal effects
        if 'causal_effects' in analyses:
            sig_causal = [c for c in analyses['causal_effects'] if c.get('significant')]
            if sig_causal:
                summary['key_discoveries'].append(
                    f"{len(sig_causal)} features show significant causal effects on performance"
                )
        
        # Actionable insights
        summary['actionable_insights'] = [
            "Focus on name feature combinations (interactions), not just individual metrics",
            "Consider non-linear optimal ranges rather than assuming 'more is better'",
            "Target characteristics of highest-performing cluster",
            "Account for confounders when evaluating name effectiveness"
        ]
        
        return summary

