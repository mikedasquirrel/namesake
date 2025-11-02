import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from core.models import Cryptocurrency, NameAnalysis, PriceHistory
import json
import logging

logger = logging.getLogger(__name__)


class StatisticalAnalyzer:
    """Statistical analysis for hypothesis testing"""
    
    def __init__(self):
        self.significance_level = 0.05
    
    def get_dataset(self):
        """
        Create comprehensive dataset for analysis
        
        Returns:
            pandas DataFrame with all metrics
        """
        # Join cryptocurrency, name analysis, and price history
        cryptos = Cryptocurrency.query.all()
        
        data = []
        for crypto in cryptos:
            if not crypto.name_analysis:
                continue
            
            # Get latest price history
            latest_price = PriceHistory.query.filter_by(
                crypto_id=crypto.id
            ).order_by(PriceHistory.date.desc()).first()
            
            if not latest_price:
                continue
            
            row = {
                'name': crypto.name,
                'symbol': crypto.symbol,
                'rank': crypto.rank,
                'market_cap': crypto.market_cap,
                'current_price': crypto.current_price,
                
                # Name metrics
                'syllable_count': crypto.name_analysis.syllable_count,
                'character_length': crypto.name_analysis.character_length,
                'phonetic_score': crypto.name_analysis.phonetic_score,
                'vowel_ratio': crypto.name_analysis.vowel_ratio,
                'memorability_score': crypto.name_analysis.memorability_score,
                'pronounceability_score': crypto.name_analysis.pronounceability_score,
                'uniqueness_score': crypto.name_analysis.uniqueness_score,
                'name_type': crypto.name_analysis.name_type,
                'has_numbers': 1 if crypto.name_analysis.has_numbers else 0,
                'has_special_chars': 1 if crypto.name_analysis.has_special_chars else 0,
                'name_type_percentile': crypto.name_analysis.name_type_percentile,
                
                # Performance metrics
                'price_30d_change': latest_price.price_30d_change,
                'price_90d_change': latest_price.price_90d_change,
                'price_1yr_change': latest_price.price_1yr_change,
                'price_ath_change': latest_price.price_ath_change,
            }
            data.append(row)
        
        df = pd.DataFrame(data)
        return df
    
    def correlation_analysis(self, performance_metric='price_1yr_change'):
        """
        Calculate correlations between name metrics and performance
        
        Args:
            performance_metric: Which price metric to correlate against
            
        Returns:
            Dict with correlation results
        """
        df = self.get_dataset()
        
        if df.empty:
            return {'error': 'No data available'}
        
        # Name metric columns
        name_metrics = [
            'syllable_count', 'character_length', 'phonetic_score', 'vowel_ratio',
            'memorability_score', 'pronounceability_score', 'uniqueness_score',
            'has_numbers', 'has_special_chars', 'name_type_percentile'
        ]
        
        # Filter out rows with missing performance data
        df_filtered = df.dropna(subset=[performance_metric])
        
        correlations = {}
        p_values = {}
        
        for metric in name_metrics:
            if metric in df_filtered.columns:
                # Calculate Pearson correlation
                corr, p_val = stats.pearsonr(
                    df_filtered[metric].fillna(df_filtered[metric].median()),
                    df_filtered[performance_metric]
                )
                correlations[metric] = round(corr, 4)
                p_values[metric] = round(p_val, 4)
        
        # Sort by absolute correlation
        sorted_correlations = dict(
            sorted(correlations.items(), key=lambda x: abs(x[1]), reverse=True)
        )
        
        return {
            'performance_metric': performance_metric,
            'correlations': sorted_correlations,
            'p_values': p_values,
            'sample_size': len(df_filtered),
            'significant_correlations': {
                k: v for k, v in sorted_correlations.items() 
                if p_values.get(k, 1) < self.significance_level
            }
        }
    
    def regression_analysis(self, performance_metric='price_1yr_change'):
        """
        Multiple regression to predict performance from name metrics
        
        Args:
            performance_metric: Target variable to predict
            
        Returns:
            Dict with regression results
        """
        df = self.get_dataset()
        df_filtered = df.dropna(subset=[performance_metric])
        
        if len(df_filtered) < 10:
            return {'error': 'Insufficient data for regression'}
        
        # Features for regression
        features = [
            'syllable_count', 'character_length', 'phonetic_score', 'vowel_ratio',
            'memorability_score', 'pronounceability_score', 'uniqueness_score',
            'has_numbers', 'has_special_chars', 'name_type_percentile'
        ]
        
        X = df_filtered[features].fillna(df_filtered[features].median())
        y = df_filtered[performance_metric]
        
        # Linear regression
        lr_model = LinearRegression()
        lr_model.fit(X, y)
        lr_score = lr_model.score(X, y)
        
        # Random forest for feature importance
        rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        rf_model.fit(X, y)
        rf_score = rf_model.score(X, y)
        
        # Feature importance
        feature_importance = dict(zip(features, rf_model.feature_importances_))
        feature_importance = dict(
            sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        )
        
        # Coefficients
        coefficients = dict(zip(features, lr_model.coef_))
        
        return {
            'performance_metric': performance_metric,
            'linear_regression': {
                'r_squared': round(lr_score, 4),
                'intercept': round(lr_model.intercept_, 4),
                'coefficients': {k: round(v, 4) for k, v in coefficients.items()}
            },
            'random_forest': {
                'r_squared': round(rf_score, 4),
                'feature_importance': {k: round(v, 4) for k, v in feature_importance.items()}
            },
            'sample_size': len(df_filtered)
        }
    
    def name_type_comparison(self, performance_metric='price_1yr_change'):
        """
        Compare performance across different name types
        
        Args:
            performance_metric: Performance metric to compare
            
        Returns:
            Dict with comparison results including ANOVA
        """
        df = self.get_dataset()
        df_filtered = df.dropna(subset=[performance_metric, 'name_type'])
        
        if len(df_filtered) < 3:
            return {'error': 'Insufficient data'}
        
        # Group by name type
        grouped = df_filtered.groupby('name_type')[performance_metric]
        
        # Calculate statistics per group
        type_stats = {}
        groups_for_anova = []
        
        for name_type, group in grouped:
            if len(group) >= 3:  # Need at least 3 samples
                type_stats[name_type] = {
                    'mean': round(group.mean(), 2),
                    'median': round(group.median(), 2),
                    'std': round(group.std(), 2),
                    'count': len(group),
                    'min': round(group.min(), 2),
                    'max': round(group.max(), 2)
                }
                groups_for_anova.append(group.values)
        
        # ANOVA test
        anova_result = None
        if len(groups_for_anova) >= 2:
            f_stat, p_val = stats.f_oneway(*groups_for_anova)
            anova_result = {
                'f_statistic': round(f_stat, 4),
                'p_value': round(p_val, 4),
                'significant': p_val < self.significance_level
            }
        
        # Sort by mean performance
        type_stats = dict(
            sorted(type_stats.items(), key=lambda x: x[1]['mean'], reverse=True)
        )
        
        return {
            'performance_metric': performance_metric,
            'type_statistics': type_stats,
            'anova': anova_result,
            'total_samples': len(df_filtered)
        }
    
    def syllable_analysis(self, performance_metric='price_1yr_change'):
        """
        Analyze performance by syllable count
        
        Args:
            performance_metric: Performance metric to analyze
            
        Returns:
            Dict with syllable-based analysis
        """
        df = self.get_dataset()
        df_filtered = df.dropna(subset=[performance_metric, 'syllable_count'])
        
        # Group by syllable count
        grouped = df_filtered.groupby('syllable_count')[performance_metric]
        
        syllable_stats = {}
        for syllables, group in grouped:
            syllable_stats[int(syllables)] = {
                'mean': round(group.mean(), 2),
                'median': round(group.median(), 2),
                'count': len(group),
                'std': round(group.std(), 2)
            }
        
        # Sort by syllable count
        syllable_stats = dict(sorted(syllable_stats.items()))
        
        return {
            'performance_metric': performance_metric,
            'syllable_statistics': syllable_stats
        }
    
    def length_analysis(self, performance_metric='price_1yr_change'):
        """
        Analyze performance by name length
        
        Args:
            performance_metric: Performance metric to analyze
            
        Returns:
            Dict with length-based analysis
        """
        df = self.get_dataset()
        df_filtered = df.dropna(subset=[performance_metric, 'character_length'])
        
        # Create length bins
        df_filtered['length_category'] = pd.cut(
            df_filtered['character_length'],
            bins=[0, 4, 7, 10, 100],
            labels=['very_short', 'short', 'medium', 'long']
        )
        
        # Group by length category
        grouped = df_filtered.groupby('length_category')[performance_metric]
        
        length_stats = {}
        for length_cat, group in grouped:
            if len(group) > 0:
                length_stats[str(length_cat)] = {
                    'mean': round(group.mean(), 2),
                    'median': round(group.median(), 2),
                    'count': len(group),
                    'std': round(group.std(), 2)
                }
        
        return {
            'performance_metric': performance_metric,
            'length_statistics': length_stats
        }
    
    def generate_investment_strategy(self, performance_metric='price_1yr_change', min_return=50):
        """
        Generate investment strategy based on validated correlations
        
        Args:
            performance_metric: Target performance metric
            min_return: Minimum return threshold (percentage)
            
        Returns:
            Dict with strategy recommendations
        """
        # Get correlation analysis
        corr_results = self.correlation_analysis(performance_metric)
        if 'error' in corr_results:
            return {'error': corr_results['error']}
        
        # Get regression analysis
        reg_results = self.regression_analysis(performance_metric)
        
        # Get name type comparison
        type_results = self.name_type_comparison(performance_metric)
        
        # Build strategy
        strategy = {
            'performance_target': performance_metric,
            'minimum_return': min_return,
            'generated_at': pd.Timestamp.now().isoformat(),
            'recommendations': []
        }
        
        # Top correlations
        sig_corrs = corr_results.get('significant_correlations', {})
        if sig_corrs:
            top_positive = {k: v for k, v in sig_corrs.items() if v > 0}
            top_negative = {k: v for k, v in sig_corrs.items() if v < 0}
            
            if top_positive:
                strategy['recommendations'].append({
                    'type': 'positive_correlations',
                    'description': 'Favor cryptocurrencies with these characteristics',
                    'metrics': top_positive
                })
            
            if top_negative:
                strategy['recommendations'].append({
                    'type': 'negative_correlations',
                    'description': 'Avoid cryptocurrencies with these characteristics',
                    'metrics': top_negative
                })
        
        # Best performing name types
        if 'type_statistics' in type_results:
            top_types = list(type_results['type_statistics'].items())[:3]
            strategy['recommendations'].append({
                'type': 'best_name_types',
                'description': 'Top performing name categories',
                'types': {name_type: stats['mean'] for name_type, stats in top_types}
            })
        
        # Feature importance
        if 'random_forest' in reg_results:
            top_features = dict(list(
                reg_results['random_forest']['feature_importance'].items()
            )[:5])
            strategy['recommendations'].append({
                'type': 'most_important_features',
                'description': 'Name characteristics with strongest predictive power',
                'features': top_features
            })
        
        # Statistical confidence
        strategy['confidence'] = {
            'sample_size': corr_results.get('sample_size', 0),
            'r_squared': reg_results.get('random_forest', {}).get('r_squared', 0),
            'significant_factors': len(sig_corrs)
        }
        
        return strategy
    
    def hypothesis_test(self, hypothesis_text):
        """
        Perform hypothesis test based on natural language hypothesis
        
        Args:
            hypothesis_text: Description of hypothesis
            
        Returns:
            Dict with test results
        """
        # This is a simplified version - could be expanded with NLP
        results = {
            'hypothesis': hypothesis_text,
            'tested_at': pd.Timestamp.now().isoformat(),
            'tests_performed': []
        }
        
        # Run multiple tests
        for metric in ['price_30d_change', 'price_90d_change', 'price_1yr_change']:
            corr = self.correlation_analysis(metric)
            results['tests_performed'].append({
                'metric': metric,
                'significant_correlations': corr.get('significant_correlations', {}),
                'sample_size': corr.get('sample_size', 0)
            })
        
        # Overall conclusion
        all_sig_corrs = []
        for test in results['tests_performed']:
            all_sig_corrs.extend(test['significant_correlations'].keys())
        
        if all_sig_corrs:
            results['conclusion'] = 'SUPPORTED'
            results['evidence'] = f"Found {len(set(all_sig_corrs))} significant name-performance correlations"
        else:
            results['conclusion'] = 'NOT_SUPPORTED'
            results['evidence'] = "No significant correlations found between name metrics and performance"
        
        return results

