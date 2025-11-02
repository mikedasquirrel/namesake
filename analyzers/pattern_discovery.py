"""
Pattern Discovery Engine
Auto-discovers genuine statistical patterns from cryptocurrency data
"""

import numpy as np
import pandas as pd
from core.models import db, Cryptocurrency, NameAnalysis, PriceHistory
from scipy import stats
from sklearn.tree import DecisionTreeRegressor
from sklearn.cluster import KMeans
import logging

logger = logging.getLogger(__name__)


class PatternDiscovery:
    """Automatically discover patterns in cryptocurrency name data"""
    
    def __init__(self):
        # Adaptive parameters based on dataset size
        self.min_sample_size = 30  # Increased for better statistical power
        self.significance_level = 0.01  # Stricter with large dataset
        self.bonferroni_correction = True  # Enable multiple comparison correction
    
    def discover_all_patterns(self):
        """Discover all statistically significant patterns with rigorous statistics"""
        try:
            # Get dataset
            df = self._get_analysis_dataset()
            
            if len(df) < 50:
                return {'patterns': [], 'message': 'Insufficient data for pattern discovery'}
            
            # Adjust parameters based on dataset size
            dataset_size = len(df)
            if dataset_size > 1000:
                self.min_sample_size = max(50, int(dataset_size * 0.015))  # 1.5% of dataset
                self.significance_level = 0.001  # Very strict for large datasets
            
            patterns = []
            
            # Discover syllable patterns
            patterns.extend(self._discover_syllable_patterns(df))
            
            # Discover name type patterns
            patterns.extend(self._discover_name_type_patterns(df))
            
            # Discover length patterns
            patterns.extend(self._discover_length_patterns(df))
            
            # Discover combination patterns
            patterns.extend(self._discover_combination_patterns(df))
            
            # Discover phonetic patterns
            patterns.extend(self._discover_phonetic_patterns(df))
            
            # Apply Bonferroni correction for multiple comparisons
            if self.bonferroni_correction and patterns:
                num_tests = len(patterns)
                corrected_alpha = self.significance_level / num_tests
                patterns = [p for p in patterns if p['p_value'] < corrected_alpha]
                for p in patterns:
                    p['bonferroni_corrected'] = True
                    p['corrected_alpha'] = round(corrected_alpha, 6)
            
            # Sort by combined score: effect size weighted by sample size
            for p in patterns:
                p['statistical_power'] = self._calculate_statistical_power(
                    p['sample_size'], 
                    p['effect_size'],
                    self.significance_level
                )
                p['combined_score'] = abs(p['effect_size']) * np.sqrt(p['sample_size']) / 10
            
            patterns.sort(key=lambda x: x.get('combined_score', 0), reverse=True)
            
            return {
                'patterns': patterns[:20],  # Top 20 most significant
                'total_coins': len(df),
                'min_sample_size': self.min_sample_size,
                'significance_level': self.significance_level,
                'bonferroni_corrected': self.bonferroni_correction,
                'timestamp': pd.Timestamp.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Pattern discovery error: {e}")
            return {'patterns': [], 'error': str(e)}
    
    def _calculate_statistical_power(self, sample_size, effect_size, alpha):
        """Calculate statistical power of the test"""
        # Simplified power calculation
        # For large sample sizes and moderate effect sizes, power is typically high
        from scipy.stats import norm
        z_alpha = norm.ppf(1 - alpha/2)
        z_beta = abs(effect_size) * np.sqrt(sample_size) - z_alpha
        power = norm.cdf(z_beta)
        return round(float(power), 3)
    
    def _get_analysis_dataset(self):
        """Get complete dataset for analysis"""
        # Get latest price for each crypto
        latest_prices_subq = db.session.query(
            PriceHistory.crypto_id,
            db.func.max(PriceHistory.date).label('max_date')
        ).group_by(PriceHistory.crypto_id).subquery()
        
        query = db.session.query(
            Cryptocurrency,
            NameAnalysis,
            PriceHistory
        ).join(NameAnalysis, Cryptocurrency.id == NameAnalysis.crypto_id)\
         .join(PriceHistory, Cryptocurrency.id == PriceHistory.crypto_id)\
         .join(latest_prices_subq, db.and_(
             PriceHistory.crypto_id == latest_prices_subq.c.crypto_id,
             PriceHistory.date == latest_prices_subq.c.max_date
         ))
        
        data = []
        for crypto, analysis, price in query.all():
            # USE ONLY REAL DATA - NO EXTRAPOLATION OR ESTIMATES!
            # Only use 1-year data for validation (most reliable)
            if price.price_1yr_change is None:
                continue  # Skip if no REAL 1-year data
            
            performance = price.price_1yr_change  # REAL data only
                
            data.append({
                'name': crypto.name,
                'rank': crypto.rank or 9999,
                'syllables': analysis.syllable_count or 0,
                'length': analysis.character_length or 0,
                'memorability': analysis.memorability_score or 0,
                'uniqueness': analysis.uniqueness_score or 0,
                'phonetic': analysis.phonetic_score or 0,
                'pronounceability': analysis.pronounceability_score or 0,
                'name_type': analysis.name_type or 'other',
                'vowel_ratio': analysis.vowel_ratio or 0,
                'return_30d': price.price_30d_change or 0,
                'return_1yr': performance,  # REAL 1-year data
                'is_breakout': performance > 100 if performance else False
            })
        
        return pd.DataFrame(data)
    
    def _discover_syllable_patterns(self, df):
        """Find syllable count patterns with confidence intervals"""
        patterns = []
        
        syllable_groups = df.groupby('syllables')['return_1yr'].agg(['mean', 'median', 'count', 'std', 'sem'])
        market_avg = df['return_1yr'].mean()
        market_std = df['return_1yr'].std()
        
        for syllables, stats_data in syllable_groups.iterrows():
            if stats_data['count'] < self.min_sample_size:
                continue
            
            group_data = df[df['syllables'] == syllables]['return_1yr']
            
            # T-test against market average
            t_stat, p_value = stats.ttest_1samp(group_data, market_avg)
            
            if p_value < 0.1:  # Initial filter, Bonferroni will be applied later
                # Calculate effect size (Cohen's d) - use pooled std
                pooled_std = np.sqrt((stats_data['std']**2 + market_std**2) / 2)
                effect_size = (stats_data['mean'] - market_avg) / pooled_std if pooled_std > 0 else 0
                
                # 95% Confidence interval
                ci_margin = 1.96 * stats_data['sem']
                ci_lower = stats_data['mean'] - ci_margin
                ci_upper = stats_data['mean'] + ci_margin
                
                # Get sample names
                sample_names = df[df['syllables'] == syllables].nlargest(3, 'return_1yr')['name'].tolist()
                
                patterns.append({
                    'name': f'{int(syllables)}-Syllable Names',
                    'description': f'Cryptocurrencies with {int(syllables)} syllables',
                    'sample_size': int(stats_data['count']),
                    'sample_names': sample_names,
                    'avg_return': round(stats_data['mean'], 2),
                    'median_return': round(stats_data['median'], 2),
                    'market_avg': round(market_avg, 2),
                    'outperformance': round(stats_data['mean'] - market_avg, 2),
                    'p_value': round(p_value, 6),
                    't_statistic': round(t_stat, 3),
                    'effect_size': round(effect_size, 3),
                    'ci_95': {'lower': round(ci_lower, 2), 'upper': round(ci_upper, 2)},
                    'confidence': 'HIGH' if p_value < 0.001 else ('MEDIUM' if p_value < 0.01 else 'LOW'),
                    'type': 'syllable'
                })
        
        return patterns
    
    def _discover_name_type_patterns(self, df):
        """Find name type patterns"""
        patterns = []
        
        type_groups = df.groupby('name_type')['return_1yr'].agg(['mean', 'median', 'count', 'std'])
        market_avg = df['return_1yr'].mean()
        
        for name_type, stats_data in type_groups.iterrows():
            if stats_data['count'] < self.min_sample_size:
                continue
            
            group_data = df[df['name_type'] == name_type]['return_1yr']
            
            # T-test
            t_stat, p_value = stats.ttest_1samp(group_data, market_avg)
            
            if p_value < 0.1:  # Slightly relaxed for name types
                effect_size = (stats_data['mean'] - market_avg) / stats_data['std'] if stats_data['std'] > 0 else 0
                
                sample_names = df[df['name_type'] == name_type].nlargest(3, 'return_1yr')['name'].tolist()
                
                patterns.append({
                    'name': f'{name_type.capitalize()} Names',
                    'description': f'{name_type.capitalize()}-oriented cryptocurrency names',
                    'sample_size': int(stats_data['count']),
                    'sample_names': sample_names,
                    'avg_return': round(stats_data['mean'], 2),
                    'market_avg': round(market_avg, 2),
                    'outperformance': round(stats_data['mean'] - market_avg, 2),
                    'p_value': round(p_value, 4),
                    'effect_size': round(effect_size, 2),
                    'confidence': 'HIGH' if p_value < 0.01 else ('MEDIUM' if p_value < 0.05 else 'LOW'),
                    'type': 'name_type'
                })
        
        return patterns
    
    def _discover_length_patterns(self, df):
        """Find character length patterns"""
        patterns = []
        
        # Group into buckets
        df['length_bucket'] = pd.cut(df['length'], bins=[0, 5, 8, 12, 100], labels=['Short (≤5)', 'Medium (6-8)', 'Long (9-12)', 'Very Long (13+)'])
        
        length_groups = df.groupby('length_bucket', observed=True)['return_1yr'].agg(['mean', 'median', 'count', 'std'])
        market_avg = df['return_1yr'].mean()
        
        for length_cat, stats_data in length_groups.iterrows():
            if stats_data['count'] < self.min_sample_size:
                continue
            
            group_data = df[df['length_bucket'] == length_cat]['return_1yr']
            
            t_stat, p_value = stats.ttest_1samp(group_data, market_avg)
            
            if p_value < 0.1:
                effect_size = (stats_data['mean'] - market_avg) / stats_data['std'] if stats_data['std'] > 0 else 0
                
                sample_names = df[df['length_bucket'] == length_cat].nlargest(3, 'return_1yr')['name'].tolist()
                
                patterns.append({
                    'name': f'{length_cat} Character Names',
                    'description': f'Cryptocurrency names in {length_cat} range',
                    'sample_size': int(stats_data['count']),
                    'sample_names': sample_names,
                    'avg_return': round(stats_data['mean'], 2),
                    'market_avg': round(market_avg, 2),
                    'outperformance': round(stats_data['mean'] - market_avg, 2),
                    'p_value': round(p_value, 4),
                    'effect_size': round(effect_size, 2),
                    'confidence': 'HIGH' if p_value < 0.01 else ('MEDIUM' if p_value < 0.05 else 'LOW'),
                    'type': 'length'
                })
        
        return patterns
    
    def _discover_combination_patterns(self, df):
        """Find powerful combinations of characteristics"""
        patterns = []
        market_avg = df['return_1yr'].mean()
        
        # Combination 1: 2-3 syllables + tech type
        mask = (df['syllables'].isin([2, 3])) & (df['name_type'] == 'tech')
        if mask.sum() >= self.min_sample_size:
            group = df[mask]
            t_stat, p_value = stats.ttest_1samp(group['return_1yr'], market_avg)
            
            if p_value < 0.1:
                patterns.append({
                    'name': 'Short Tech Names (2-3 Syllables)',
                    'description': 'Technology-oriented names with 2-3 syllables',
                    'sample_size': int(mask.sum()),
                    'sample_names': group.nlargest(3, 'return_1yr')['name'].tolist(),
                    'avg_return': round(group['return_1yr'].mean(), 2),
                    'market_avg': round(market_avg, 2),
                    'outperformance': round(group['return_1yr'].mean() - market_avg, 2),
                    'p_value': round(p_value, 4),
                    'effect_size': round((group['return_1yr'].mean() - market_avg) / group['return_1yr'].std(), 2),
                    'confidence': 'HIGH' if p_value < 0.01 else 'MEDIUM',
                    'type': 'combination'
                })
        
        # Combination 2: High memorability + medium length
        mask = (df['memorability'] > 80) & (df['length'].between(5, 8))
        if mask.sum() >= self.min_sample_size:
            group = df[mask]
            t_stat, p_value = stats.ttest_1samp(group['return_1yr'], market_avg)
            
            if p_value < 0.1:
                patterns.append({
                    'name': 'Memorable Medium-Length Names',
                    'description': 'High memorability (>80) with optimal length (5-8 chars)',
                    'sample_size': int(mask.sum()),
                    'sample_names': group.nlargest(3, 'return_1yr')['name'].tolist(),
                    'avg_return': round(group['return_1yr'].mean(), 2),
                    'market_avg': round(market_avg, 2),
                    'outperformance': round(group['return_1yr'].mean() - market_avg, 2),
                    'p_value': round(p_value, 4),
                    'effect_size': round((group['return_1yr'].mean() - market_avg) / group['return_1yr'].std(), 2),
                    'confidence': 'HIGH' if p_value < 0.01 else 'MEDIUM',
                    'type': 'combination'
                })
        
        # Combination 3: Portmanteau + vowel ending
        portmanteau_coins = df[df['name_type'] == 'portmanteau']
        if len(portmanteau_coins) >= self.min_sample_size:
            vowel_ending = portmanteau_coins[portmanteau_coins['name'].str.lower().str.endswith(('a', 'e', 'i', 'o', 'u'))]
            
            if len(vowel_ending) >= self.min_sample_size:
                t_stat, p_value = stats.ttest_1samp(vowel_ending['return_1yr'], market_avg)
                
                if p_value < 0.1:
                    patterns.append({
                        'name': 'Vowel-Ending Portmanteaus',
                        'description': 'Portmanteau names ending in vowels',
                        'sample_size': len(vowel_ending),
                        'sample_names': vowel_ending.nlargest(3, 'return_1yr')['name'].tolist(),
                        'avg_return': round(vowel_ending['return_1yr'].mean(), 2),
                        'market_avg': round(market_avg, 2),
                        'outperformance': round(vowel_ending['return_1yr'].mean() - market_avg, 2),
                        'p_value': round(p_value, 4),
                        'effect_size': round((vowel_ending['return_1yr'].mean() - market_avg) / vowel_ending['return_1yr'].std(), 2),
                        'confidence': 'HIGH' if p_value < 0.01 else 'MEDIUM',
                        'type': 'combination'
                    })
        
        return patterns
    
    def _discover_phonetic_patterns(self, df):
        """Find phonetic characteristic patterns"""
        patterns = []
        market_avg = df['return_1yr'].mean()
        
        # High phonetic score pattern
        high_phonetic = df[df['phonetic'] > 80]
        if len(high_phonetic) >= self.min_sample_size:
            t_stat, p_value = stats.ttest_1samp(high_phonetic['return_1yr'], market_avg)
            
            if p_value < 0.1:
                patterns.append({
                    'name': 'High Phonetic Quality Names',
                    'description': 'Names with phonetic scores above 80',
                    'sample_size': len(high_phonetic),
                    'sample_names': high_phonetic.nlargest(3, 'return_1yr')['name'].tolist(),
                    'avg_return': round(high_phonetic['return_1yr'].mean(), 2),
                    'market_avg': round(market_avg, 2),
                    'outperformance': round(high_phonetic['return_1yr'].mean() - market_avg, 2),
                    'p_value': round(p_value, 4),
                    'effect_size': round((high_phonetic['return_1yr'].mean() - market_avg) / high_phonetic['return_1yr'].std(), 2),
                    'confidence': 'HIGH' if p_value < 0.01 else 'MEDIUM',
                    'type': 'phonetic'
                })
        
        return patterns
    
    def validate_pattern(self, pattern_definition):
        """Validate a specific pattern against data"""
        try:
            df = self._get_analysis_dataset()
            
            # Apply pattern filter
            mask = self._apply_pattern_filter(df, pattern_definition)
            matched_coins = df[mask]
            
            if len(matched_coins) < self.min_sample_size:
                return {'valid': False, 'reason': 'Insufficient sample size'}
            
            # Statistical test
            market_avg = df['return_1yr'].mean()
            t_stat, p_value = stats.ttest_1samp(matched_coins['return_1yr'], market_avg)
            
            # Effect size
            cohens_d = (matched_coins['return_1yr'].mean() - market_avg) / matched_coins['return_1yr'].std()
            
            return {
                'valid': p_value < self.significance_level,
                'sample_size': len(matched_coins),
                'avg_return': round(matched_coins['return_1yr'].mean(), 2),
                'market_avg': round(market_avg, 2),
                'p_value': round(p_value, 4),
                'effect_size': round(cohens_d, 2),
                't_statistic': round(t_stat, 2),
                'confidence': 'HIGH' if p_value < 0.01 else ('MEDIUM' if p_value < 0.05 else 'LOW')
            }
        
        except Exception as e:
            logger.error(f"Pattern validation error: {e}")
            return {'valid': False, 'error': str(e)}
    
    def _apply_pattern_filter(self, df, pattern_def):
        """Apply pattern definition to dataframe"""
        mask = pd.Series([True] * len(df), index=df.index)
        
        if 'syllables' in pattern_def:
            mask &= df['syllables'].isin(pattern_def['syllables'])
        if 'name_type' in pattern_def:
            mask &= df['name_type'] == pattern_def['name_type']
        if 'min_memorability' in pattern_def:
            mask &= df['memorability'] >= pattern_def['min_memorability']
        if 'length_range' in pattern_def:
            mask &= df['length'].between(*pattern_def['length_range'])
        
        return mask
    
    def find_anomalies(self):
        """Find coins that defy patterns (outliers)"""
        try:
            df = self._get_analysis_dataset()
            
            # Find high performers with "bad" names
            low_score_mask = (df['memorability'] < 50) & (df['uniqueness'] < 50)
            high_return_mask = df['return_1yr'] > 100
            
            anomalies = df[low_score_mask & high_return_mask]
            
            # Find low performers with "good" names
            high_score_mask = (df['memorability'] > 80) & (df['uniqueness'] > 80)
            low_return_mask = df['return_1yr'] < 0
            
            underperformers = df[high_score_mask & low_return_mask]
            
            return {
                'surprising_winners': anomalies[['name', 'memorability', 'uniqueness', 'return_1yr']].to_dict('records'),
                'disappointing_coins': underperformers[['name', 'memorability', 'uniqueness', 'return_1yr']].to_dict('records')
            }
        
        except Exception as e:
            logger.error(f"Anomaly detection error: {e}")
            return {'surprising_winners': [], 'disappointing_coins': []}
    
    def cross_validate_patterns(self, n_splits=5):
        """
        Cross-validate discovered patterns to prove predictive power
        Tests if patterns hold on unseen data (the ultimate validation)
        """
        try:
            from sklearn.model_selection import KFold
            
            df = self._get_analysis_dataset()
            
            if len(df) < 100:
                return {'error': 'Insufficient data for cross-validation'}
            
            # Get current patterns
            patterns_result = self.discover_all_patterns()
            patterns = patterns_result.get('patterns', [])
            
            if not patterns:
                return {'error': 'No patterns to validate'}
            
            # Cross-validation results for each pattern
            pattern_cv_results = []
            
            kfold = KFold(n_splits=n_splits, shuffle=True, random_state=42)
            
            for pattern in patterns[:10]:  # Validate top 10 patterns
                fold_results = []
                
                for train_idx, test_idx in kfold.split(df):
                    train_df = df.iloc[train_idx]
                    test_df = df.iloc[test_idx]
                    
                    # Apply pattern filter on training set
                    train_mask = self._match_pattern(train_df, pattern)
                    train_matched = train_df[train_mask]
                    
                    # Apply same filter on test set
                    test_mask = self._match_pattern(test_df, pattern)
                    test_matched = test_df[test_mask]
                    
                    if len(train_matched) >= 10 and len(test_matched) >= 5:
                        # Check if pattern's direction holds
                        train_outperformance = train_matched['return_1yr'].mean() - train_df['return_1yr'].mean()
                        test_outperformance = test_matched['return_1yr'].mean() - test_df['return_1yr'].mean()
                        
                        # Pattern validates if direction is same in test as training
                        validates = (train_outperformance > 0 and test_outperformance > 0) or \
                                  (train_outperformance < 0 and test_outperformance < 0)
                        
                        fold_results.append({
                            'validates': validates,
                            'train_outperformance': train_outperformance,
                            'test_outperformance': test_outperformance
                        })
                
                if fold_results:
                    validation_rate = sum(1 for r in fold_results if r['validates']) / len(fold_results)
                    avg_test_outperformance = np.mean([r['test_outperformance'] for r in fold_results])
                    
                    pattern_cv_results.append({
                        'pattern_name': pattern['name'],
                        'validation_rate': round(float(validation_rate), 3),
                        'avg_test_outperformance': round(float(avg_test_outperformance), 2),
                        'n_folds_tested': len(fold_results),
                        'validates_overall': bool(validation_rate >= 0.6),  # 60% of folds must validate
                        'confidence': 'HIGH' if validation_rate >= 0.8 else ('MEDIUM' if validation_rate >= 0.6 else 'LOW')
                    })
            
            # Summary
            validated_patterns = sum(1 for r in pattern_cv_results if r['validates_overall'])
            
            return {
                'total_patterns_tested': len(pattern_cv_results),
                'patterns_validated': validated_patterns,
                'validation_rate': round(validated_patterns / len(pattern_cv_results), 3) if pattern_cv_results else 0,
                'n_splits': n_splits,
                'pattern_results': pattern_cv_results,
                'interpretation': f"{validated_patterns}/{len(pattern_cv_results)} patterns hold predictive power on unseen data",
                'conclusion': 'Patterns demonstrate genuine predictive power' if validated_patterns >= len(pattern_cv_results) * 0.5 else 'Patterns may be overfitting'
            }
        
        except Exception as e:
            logger.error(f"Cross-validation error: {e}")
            return {'error': str(e)}
    
    def _match_pattern(self, df, pattern):
        """Match a pattern to dataframe rows"""
        # This is a simplified matcher - extend based on pattern type
        pattern_type = pattern.get('type', '')
        
        if pattern_type == 'syllable':
            # Extract syllable count from pattern name
            try:
                syllable_count = int(pattern['name'].split('-')[0])
                return df['syllables'] == syllable_count
            except:
                return pd.Series([False] * len(df))
        
        elif pattern_type == 'length':
            # Match length bucket
            if 'Short' in pattern['name']:
                return df['length'] <= 5
            elif 'Medium' in pattern['name']:
                return (df['length'] > 5) & (df['length'] <= 8)
            elif 'Long' in pattern['name']:
                return (df['length'] > 8) & (df['length'] <= 12)
            else:
                return df['length'] > 12
        
        elif pattern_type == 'name_type':
            # Extract name type
            name_type = pattern['name'].lower().split()[0]
            return df['name_type'] == name_type
        
        elif pattern_type == 'combination':
            # More complex matching - simplified here
            if 'High Phonetic' in pattern['name']:
                return df['phonetic'] > 80
            elif 'Memorable' in pattern['name']:
                return (df['memorability'] > 80) & (df['length'] >= 5) & (df['length'] <= 8)
            else:
                return pd.Series([False] * len(df))
        
        else:
            return pd.Series([False] * len(df))

