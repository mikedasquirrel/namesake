"""MTG Temporal Analysis: VALUE OVER TIME

Analyzes price appreciation patterns, reprint resilience, and temporal dynamics.
Since we don't have historical price APIs, we'll use:
1. Cross-sectional variance as proxy for volatility
2. EDHREC rank as proxy for sustained interest
3. Reprint count as indicator of depreciation risk
4. Set year to analyze era-based appreciation patterns
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


class MTGTemporalAnalyzer:
    """Analyzes temporal patterns and VALUE OVER TIME dynamics."""
    
    def __init__(self):
        self.scaler = StandardScaler()
    
    def analyze_appreciation_patterns(self, df: pd.DataFrame) -> Dict:
        """Analyze which name features predict long-term value retention.
        
        Using proxies for temporal analysis:
        - High price + low EDHREC rank = sustained value (sticky collectibility)
        - Low reprint count = reprint resilience
        - Set year + current price = appreciation trajectory
        """
        results = {}
        
        # Calculate "Value Stability Score"
        # Cards with high price AND low EDHREC rank have sustained collector interest
        df['value_stability'] = df['price_usd'] / np.log(df['edhrec_rank'] + 1)
        
        # Calculate "Reprint Resilience"  
        # Cards with fewer reprints retain value better
        df['reprint_resilience'] = 1 / (df['reprint_count'] + 1)
        
        # Calculate "Era-Adjusted Value"
        # Older cards should be more expensive (scarcity); deviation = appreciation
        if 'set_year' in df.columns and df['set_year'].notna().any():
            df['card_age'] = 2025 - df['set_year'].fillna(2025)
            df['expected_price_by_age'] = df['card_age'].apply(lambda x: np.log(x + 1) if pd.notna(x) else 1.0)
            df['era_adjusted_value'] = df['price_usd'] / (df['expected_price_by_age'] + 1)
        
        # Correlate name features with these temporal proxies
        name_features = [
            'syllable_count', 'character_length', 'memorability_score',
            'fantasy_score', 'mythic_resonance_score', 'constructed_language_score'
        ]
        
        temporal_metrics = ['value_stability', 'reprint_resilience']
        if 'era_adjusted_value' in df.columns:
            temporal_metrics.append('era_adjusted_value')
        
        correlations = {}
        for feature in name_features:
            if feature not in df.columns:
                continue
            
            feature_cors = {}
            for metric in temporal_metrics:
                if metric not in df.columns:
                    continue
                
                valid_data = df[[feature, metric]].dropna()
                if len(valid_data) < 30:
                    continue
                
                r, p = stats.pearsonr(valid_data[feature], valid_data[metric])
                feature_cors[metric] = {
                    'r': round(r, 3),
                    'p': round(p, 4),
                    'significant': p < 0.05
                }
            
            if feature_cors:
                correlations[feature] = feature_cors
        
        results['temporal_correlations'] = correlations
        
        # Identify "Sticky Collectibles" (high value stability)
        if 'value_stability' in df.columns:
            sticky_threshold = df['value_stability'].quantile(0.75)
            sticky_cards = df[df['value_stability'] > sticky_threshold]
            
            results['sticky_collectibles'] = {
                'count': len(sticky_cards),
                'avg_fantasy_score': round(sticky_cards['fantasy_score'].mean(), 2),
                'avg_mythic_resonance': round(sticky_cards['mythic_resonance_score'].mean(), 2),
                'legendary_rate': round((sticky_cards['is_legendary'].sum() / len(sticky_cards)) * 100, 1)
            }
        
        return results
    
    def analyze_reprint_vulnerability(self, df: pd.DataFrame) -> Dict:
        """Predict reprint vulnerability from name features.
        
        Hypothesis: Memorable, simple names → more reprintable → higher depreciation risk
        Obscure, complex names → reprint-resistant → value retention
        """
        if 'reprint_count' not in df.columns:
            return {'error': 'No reprint data available'}
        
        # High reprint cards
        high_reprint = df[df['reprint_count'] >= 3]
        low_reprint = df[df['reprint_count'] <= 1]
        
        if len(high_reprint) < 20 or len(low_reprint) < 20:
            return {'error': 'Insufficient reprint data'}
        
        # Compare name features
        features_to_test = [
            'memorability_score', 'fantasy_score', 'constructed_language_score',
            'syllable_count', 'character_length'
        ]
        
        comparisons = {}
        for feature in features_to_test:
            if feature not in df.columns:
                continue
            
            high_mean = high_reprint[feature].mean()
            low_mean = low_reprint[feature].mean()
            
            t_stat, p_value = stats.ttest_ind(
                high_reprint[feature].dropna(),
                low_reprint[feature].dropna()
            )
            
            comparisons[feature] = {
                'high_reprint_avg': round(high_mean, 2),
                'low_reprint_avg': round(low_mean, 2),
                'difference': round(high_mean - low_mean, 2),
                'p_value': round(p_value, 4),
                'significant': p_value < 0.05
            }
        
        return {
            'sample_sizes': {
                'high_reprint': len(high_reprint),
                'low_reprint': len(low_reprint)
            },
            'feature_comparisons': comparisons
        }
    
    def classify_price_trajectories(self, df: pd.DataFrame) -> Dict:
        """Classify cards into appreciation trajectory types.
        
        Using current metrics as proxies:
        - Steady Appreciators: High price + low volatility proxy + low reprint
        - Spike Potential: High EDHREC velocity (popular but not yet expensive)
        - Stable Value: High price + high reprint count (eternal staples)
        - Depreciating: Low price + high reprint count
        """
        # Calculate trajectory indicators
        df['price_percentile'] = df['price_usd'].rank(pct=True)
        df['edhrec_popularity'] = 1 / (np.log(df['edhrec_rank'] + 1) + 1)
        
        trajectories = []
        for idx, row in df.iterrows():
            price_pct = row.get('price_percentile', 0.5)
            reprint = row.get('reprint_count', 0)
            popularity = row.get('edhrec_popularity', 0)
            
            # Classification logic
            if price_pct > 0.75 and reprint <= 2:
                trajectory = 'steady_appreciator'
            elif price_pct > 0.75 and reprint >= 3:
                trajectory = 'stable_value'
            elif popularity > 0.7 and price_pct < 0.5:
                trajectory = 'spike_potential'
            elif price_pct < 0.25 and reprint >= 2:
                trajectory = 'depreciating'
            else:
                trajectory = 'moderate'
            
            trajectories.append(trajectory)
        
        df['trajectory'] = trajectories
        
        # Profile each trajectory by name features
        trajectory_profiles = {}
        for traj_type in ['steady_appreciator', 'spike_potential', 'stable_value', 'depreciating']:
            traj_df = df[df['trajectory'] == traj_type]
            
            if len(traj_df) < 10:
                continue
            
            trajectory_profiles[traj_type] = {
                'count': len(traj_df),
                'avg_price': round(traj_df['price_usd'].mean(), 2),
                'avg_fantasy': round(traj_df['fantasy_score'].mean(), 2),
                'avg_mythic_resonance': round(traj_df['mythic_resonance_score'].mean(), 2),
                'avg_memorability': round(traj_df['memorability_score'].mean(), 2),
                'legendary_rate': round((traj_df['is_legendary'].sum() / len(traj_df)) * 100, 1)
            }
        
        return {
            'trajectory_profiles': trajectory_profiles,
            'distribution': df['trajectory'].value_counts().to_dict()
        }
    
    def analyze_era_evolution(self, df: pd.DataFrame) -> Dict:
        """M6: Analyze how naming conventions evolved over time.
        
        Test if fantasy score, syllable count, etc. systematically changed by era.
        """
        if 'set_year' not in df.columns or df['set_year'].isna().all():
            return {'error': 'No set_year data available'}
        
        df_with_year = df[df['set_year'].notna()].copy()
        
        if len(df_with_year) < 100:
            return {'error': 'Insufficient temporal data'}
        
        # Define eras
        eras = {
            'Early (1993-2000)': (1993, 2000),
            'Golden Age (2001-2010)': (2001, 2010),
            'Modern (2011-2020)': (2011, 2020),
            'Contemporary (2021-2025)': (2021, 2025),
        }
        
        era_profiles = {}
        for era_name, (start, end) in eras.items():
            era_df = df_with_year[
                (df_with_year['set_year'] >= start) & 
                (df_with_year['set_year'] <= end)
            ]
            
            if len(era_df) < 20:
                continue
            
            era_profiles[era_name] = {
                'sample_size': len(era_df),
                'avg_syllables': round(era_df['syllable_count'].mean(), 2),
                'avg_length': round(era_df['character_length'].mean(), 2),
                'avg_fantasy': round(era_df['fantasy_score'].mean(), 2),
                'avg_memorability': round(era_df['memorability_score'].mean(), 2),
                'avg_price': round(era_df['price_usd'].mean(), 2),
                'legendary_rate': round((era_df['is_legendary'].sum() / len(era_df)) * 100, 1)
            }
        
        # Test linear trends
        features_to_test = ['syllable_count', 'fantasy_score', 'character_length']
        trend_tests = {}
        
        for feature in features_to_test:
            if feature not in df_with_year.columns:
                continue
            
            X = df_with_year[['set_year']].values
            y = df_with_year[feature].values
            
            valid_idx = ~np.isnan(y)
            if valid_idx.sum() < 50:
                continue
            
            model = LinearRegression()
            model.fit(X[valid_idx], y[valid_idx])
            
            r_squared = model.score(X[valid_idx], y[valid_idx])
            slope = model.coef_[0]
            
            # Test significance
            from scipy.stats import linregress
            lr = linregress(X[valid_idx].flatten(), y[valid_idx])
            
            trend_tests[feature] = {
                'slope_per_year': round(slope, 4),
                'r_squared': round(r_squared, 3),
                'p_value': round(lr.pvalue, 4),
                'significant': lr.pvalue < 0.05,
                'direction': 'increasing' if slope > 0 else 'decreasing'
            }
        
        return {
            'era_profiles': era_profiles,
            'temporal_trends': trend_tests
        }

