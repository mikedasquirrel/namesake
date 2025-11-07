"""NBA Shooting Percentage Analyzer

Advanced analysis of free throw and 3-point shooting percentages correlated with name characteristics.

Research Questions:
1. Do linguistic features predict shooting accuracy (FT% and 3PT%)?
2. Are there phonetic patterns associated with better shooters?
3. How do shooting percentages correlate with name memorability/harshness?
4. Era-specific shooting patterns (3PT era vs. pre-3PT era)
5. Position-specific shooting correlations

Statistical Methods:
- Pearson correlations between linguistic features and shooting %
- Multiple regression models for shooting prediction
- Era-stratified analysis (pre-1979 vs post-1979 for 3PT)
- Position-stratified analysis (Guards vs Forwards vs Centers)
- Cluster analysis: Elite shooters (90%+ FT, 40%+ 3PT) vs Poor shooters
"""

import logging
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.cluster import KMeans
from sklearn.metrics import r2_score, mean_squared_error, silhouette_score
from scipy import stats

from core.models import db, NBAPlayer, NBAPlayerAnalysis

logger = logging.getLogger(__name__)


class NBAShootingAnalyzer:
    """Comprehensive shooting percentage analysis with linguistic correlations."""
    
    def __init__(self):
        """Initialize analyzer."""
        self.scaler = StandardScaler()
        
        # Elite thresholds
        self.ELITE_FT_THRESHOLD = 0.850  # 85%+ FT is elite
        self.ELITE_3PT_THRESHOLD = 0.380  # 38%+ 3PT is elite
        self.POOR_FT_THRESHOLD = 0.650  # <65% FT is poor
        self.POOR_3PT_THRESHOLD = 0.300  # <30% 3PT is poor
    
    def get_shooting_dataset(self) -> pd.DataFrame:
        """Load all players with shooting data.
        
        Returns:
            DataFrame with player, analysis, and shooting data
        """
        query = db.session.query(NBAPlayer, NBAPlayerAnalysis).join(
            NBAPlayerAnalysis,
            NBAPlayer.id == NBAPlayerAnalysis.player_id
        )
        
        rows = []
        for player, analysis in query.all():
            try:
                # Filter out players with insufficient data
                if not player.games_played or player.games_played < 100:
                    continue  # Minimum 100 games for statistical validity
                
                row = {
                    # Metadata
                    'id': player.id,
                    'name': player.name,
                    'debut_year': player.debut_year,
                    'era': player.era,
                    'era_group': player.era_group,
                    'position': player.position,
                    'position_group': player.position_group,
                    'primary_position': player.primary_position,
                    'years_active': player.years_active or 0,
                    'games_played': player.games_played or 0,
                    
                    # Shooting stats (primary outcomes)
                    'ft_percentage': player.ft_percentage if player.ft_percentage else None,
                    'three_point_percentage': player.three_point_percentage if player.three_point_percentage else None,
                    'fg_percentage': player.fg_percentage if player.fg_percentage else None,
                    
                    # Performance context
                    'ppg': player.ppg or 0,
                    'apg': player.apg or 0,
                    'rpg': player.rpg or 0,
                    'performance_score': player.performance_score or 0,
                    'overall_success_score': player.overall_success_score or 0,
                    
                    # Linguistic features (predictors)
                    'syllable_count': analysis.syllable_count or 0,
                    'character_length': analysis.character_length or 0,
                    'word_count': analysis.word_count or 0,
                    'memorability_score': analysis.memorability_score or 0,
                    'pronounceability_score': analysis.pronounceability_score or 0,
                    'uniqueness_score': analysis.uniqueness_score or 0,
                    'power_connotation_score': analysis.power_connotation_score or 0,
                    'harshness_score': analysis.harshness_score or 0,
                    'softness_score': analysis.softness_score or 0,
                    'phonetic_score': analysis.phonetic_score or 0,
                    'vowel_ratio': analysis.vowel_ratio or 0,
                    'speed_association_score': analysis.speed_association_score or 50,
                    'strength_association_score': analysis.strength_association_score or 50,
                    'rhythm_score': analysis.rhythm_score or 50,
                    'consonant_cluster_complexity': analysis.consonant_cluster_complexity or 50,
                    'alliteration_score': analysis.alliteration_score or 0,
                    
                    # Name component analysis
                    'first_name_syllables': analysis.first_name_syllables or 0,
                    'first_name_length': analysis.first_name_length or 0,
                    'first_name_memorability': analysis.first_name_memorability or 0,
                    'last_name_syllables': analysis.last_name_syllables or 0,
                    'last_name_length': analysis.last_name_length or 0,
                    'last_name_memorability': analysis.last_name_memorability or 0,
                }
                
                rows.append(row)
                
            except Exception as e:
                logger.warning(f"Error loading player {player.name}: {e}")
                continue
        
        df = pd.DataFrame(rows)
        
        logger.info(f"Loaded {len(df)} players for shooting analysis")
        logger.info(f"Players with FT%: {df['ft_percentage'].notna().sum()}")
        logger.info(f"Players with 3PT%: {df['three_point_percentage'].notna().sum()}")
        
        return df
    
    def analyze_comprehensive_shooting(self, df: pd.DataFrame) -> Dict:
        """Run complete shooting analysis.
        
        Args:
            df: DataFrame with shooting data
            
        Returns:
            Comprehensive analysis results
        """
        results = {
            'dataset_summary': self._get_dataset_summary(df),
            'ft_analysis': self.analyze_free_throw_correlations(df),
            'three_pt_analysis': self.analyze_three_point_correlations(df),
            'combined_shooting': self.analyze_combined_shooting_ability(df),
            'era_analysis': self.analyze_shooting_by_era(df),
            'position_analysis': self.analyze_shooting_by_position(df),
            'elite_vs_poor': self.analyze_elite_vs_poor_shooters(df),
            'predictive_models': self.build_shooting_prediction_models(df),
            'key_findings': []
        }
        
        # Generate key findings
        results['key_findings'] = self._generate_key_findings(results)
        
        return results
    
    def _get_dataset_summary(self, df: pd.DataFrame) -> Dict:
        """Get summary statistics for the dataset.
        
        Args:
            df: DataFrame
            
        Returns:
            Summary stats
        """
        # Free throw stats
        ft_data = df['ft_percentage'].dropna()
        
        # 3-point stats
        three_pt_data = df['three_point_percentage'].dropna()
        
        # Era breakdown (3PT introduced in 1979-80 season)
        pre_3pt_era = df[df['debut_year'] < 1980]
        post_3pt_era = df[df['debut_year'] >= 1980]
        
        return {
            'total_players': len(df),
            'players_with_ft_data': len(ft_data),
            'players_with_3pt_data': len(three_pt_data),
            'avg_games_played': float(df['games_played'].mean()),
            
            # Free throw summary
            'ft_stats': {
                'mean': float(ft_data.mean()) if len(ft_data) > 0 else None,
                'median': float(ft_data.median()) if len(ft_data) > 0 else None,
                'std': float(ft_data.std()) if len(ft_data) > 0 else None,
                'min': float(ft_data.min()) if len(ft_data) > 0 else None,
                'max': float(ft_data.max()) if len(ft_data) > 0 else None,
                'elite_count': int((ft_data >= self.ELITE_FT_THRESHOLD).sum()) if len(ft_data) > 0 else 0,
                'poor_count': int((ft_data < self.POOR_FT_THRESHOLD).sum()) if len(ft_data) > 0 else 0,
            },
            
            # 3-point summary
            'three_pt_stats': {
                'mean': float(three_pt_data.mean()) if len(three_pt_data) > 0 else None,
                'median': float(three_pt_data.median()) if len(three_pt_data) > 0 else None,
                'std': float(three_pt_data.std()) if len(three_pt_data) > 0 else None,
                'min': float(three_pt_data.min()) if len(three_pt_data) > 0 else None,
                'max': float(three_pt_data.max()) if len(three_pt_data) > 0 else None,
                'elite_count': int((three_pt_data >= self.ELITE_3PT_THRESHOLD).sum()) if len(three_pt_data) > 0 else 0,
                'poor_count': int((three_pt_data < self.POOR_3PT_THRESHOLD).sum()) if len(three_pt_data) > 0 else 0,
            },
            
            # Era breakdown
            'era_breakdown': {
                'pre_3pt_era': len(pre_3pt_era),
                'post_3pt_era': len(post_3pt_era),
            }
        }
    
    def analyze_free_throw_correlations(self, df: pd.DataFrame) -> Dict:
        """Analyze correlations between name features and FT%.
        
        Args:
            df: DataFrame with data
            
        Returns:
            FT correlation analysis
        """
        logger.info("Analyzing free throw correlations...")
        
        # Filter to players with FT data
        ft_df = df[df['ft_percentage'].notna()].copy()
        
        if len(ft_df) < 30:
            return {'error': 'Insufficient FT data', 'sample_size': len(ft_df)}
        
        feature_cols = [
            'syllable_count', 'character_length', 'memorability_score',
            'pronounceability_score', 'uniqueness_score', 'power_connotation_score',
            'harshness_score', 'softness_score', 'phonetic_score', 'vowel_ratio',
            'speed_association_score', 'strength_association_score', 'rhythm_score',
            'consonant_cluster_complexity', 'alliteration_score',
            'first_name_syllables', 'last_name_syllables'
        ]
        
        correlations = {}
        
        for feature in feature_cols:
            if feature not in ft_df.columns:
                continue
            
            valid_data = ft_df[[feature, 'ft_percentage']].dropna()
            
            if len(valid_data) < 30:
                continue
            
            # Pearson correlation
            corr, p_value = stats.pearsonr(valid_data[feature], valid_data['ft_percentage'])
            
            if not np.isnan(corr):
                correlations[feature] = {
                    'correlation': float(corr),
                    'p_value': float(p_value),
                    'significant': p_value < 0.05,
                    'sample_size': len(valid_data),
                    'interpretation': self._interpret_correlation(corr, 'FT%')
                }
        
        # Sort by absolute correlation
        sorted_correlations = sorted(
            [(k, v) for k, v in correlations.items() if v.get('significant', False)],
            key=lambda x: abs(x[1]['correlation']),
            reverse=True
        )
        
        return {
            'sample_size': len(ft_df),
            'avg_ft_percentage': float(ft_df['ft_percentage'].mean()),
            'all_correlations': correlations,
            'significant_correlations': [
                {'feature': k, **v} for k, v in sorted_correlations
            ],
            'top_positive_correlates': [
                {'feature': k, **v} for k, v in sorted_correlations if v['correlation'] > 0
            ][:5],
            'top_negative_correlates': [
                {'feature': k, **v} for k, v in sorted_correlations if v['correlation'] < 0
            ][:5],
        }
    
    def analyze_three_point_correlations(self, df: pd.DataFrame) -> Dict:
        """Analyze correlations between name features and 3PT%.
        
        Args:
            df: DataFrame with data
            
        Returns:
            3PT correlation analysis
        """
        logger.info("Analyzing 3-point correlations...")
        
        # Filter to players with 3PT data
        three_pt_df = df[df['three_point_percentage'].notna()].copy()
        
        if len(three_pt_df) < 30:
            return {'error': 'Insufficient 3PT data', 'sample_size': len(three_pt_df)}
        
        feature_cols = [
            'syllable_count', 'character_length', 'memorability_score',
            'pronounceability_score', 'uniqueness_score', 'power_connotation_score',
            'harshness_score', 'softness_score', 'phonetic_score', 'vowel_ratio',
            'speed_association_score', 'strength_association_score', 'rhythm_score',
            'consonant_cluster_complexity', 'alliteration_score',
            'first_name_syllables', 'last_name_syllables'
        ]
        
        correlations = {}
        
        for feature in feature_cols:
            if feature not in three_pt_df.columns:
                continue
            
            valid_data = three_pt_df[[feature, 'three_point_percentage']].dropna()
            
            if len(valid_data) < 30:
                continue
            
            # Pearson correlation
            corr, p_value = stats.pearsonr(valid_data[feature], valid_data['three_point_percentage'])
            
            if not np.isnan(corr):
                correlations[feature] = {
                    'correlation': float(corr),
                    'p_value': float(p_value),
                    'significant': p_value < 0.05,
                    'sample_size': len(valid_data),
                    'interpretation': self._interpret_correlation(corr, '3PT%')
                }
        
        # Sort by absolute correlation
        sorted_correlations = sorted(
            [(k, v) for k, v in correlations.items() if v.get('significant', False)],
            key=lambda x: abs(x[1]['correlation']),
            reverse=True
        )
        
        return {
            'sample_size': len(three_pt_df),
            'avg_three_point_percentage': float(three_pt_df['three_point_percentage'].mean()),
            'all_correlations': correlations,
            'significant_correlations': [
                {'feature': k, **v} for k, v in sorted_correlations
            ],
            'top_positive_correlates': [
                {'feature': k, **v} for k, v in sorted_correlations if v['correlation'] > 0
            ][:5],
            'top_negative_correlates': [
                {'feature': k, **v} for k, v in sorted_correlations if v['correlation'] < 0
            ][:5],
        }
    
    def analyze_combined_shooting_ability(self, df: pd.DataFrame) -> Dict:
        """Analyze combined shooting ability (FT + 3PT).
        
        Args:
            df: DataFrame
            
        Returns:
            Combined shooting analysis
        """
        logger.info("Analyzing combined shooting ability...")
        
        # Filter to players with both FT and 3PT data
        both_df = df[df['ft_percentage'].notna() & df['three_point_percentage'].notna()].copy()
        
        if len(both_df) < 30:
            return {'error': 'Insufficient data', 'sample_size': len(both_df)}
        
        # Create combined shooting score (weighted average)
        both_df['combined_shooting_score'] = (
            both_df['ft_percentage'] * 0.6 +  # FT more important (higher volume)
            both_df['three_point_percentage'] * 0.4
        )
        
        # Correlate with linguistic features
        feature_cols = [
            'syllable_count', 'character_length', 'memorability_score',
            'harshness_score', 'softness_score', 'rhythm_score'
        ]
        
        correlations = {}
        
        for feature in feature_cols:
            if feature not in both_df.columns:
                continue
            
            valid_data = both_df[[feature, 'combined_shooting_score']].dropna()
            
            if len(valid_data) < 30:
                continue
            
            corr, p_value = stats.pearsonr(valid_data[feature], valid_data['combined_shooting_score'])
            
            if not np.isnan(corr):
                correlations[feature] = {
                    'correlation': float(corr),
                    'p_value': float(p_value),
                    'significant': p_value < 0.05
                }
        
        # Identify elite shooters (both metrics high)
        elite_shooters = both_df[
            (both_df['ft_percentage'] >= self.ELITE_FT_THRESHOLD) &
            (both_df['three_point_percentage'] >= self.ELITE_3PT_THRESHOLD)
        ]
        
        # Identify poor shooters (both metrics low)
        poor_shooters = both_df[
            (both_df['ft_percentage'] < self.POOR_FT_THRESHOLD) &
            (both_df['three_point_percentage'] < self.POOR_3PT_THRESHOLD)
        ]
        
        return {
            'sample_size': len(both_df),
            'avg_combined_score': float(both_df['combined_shooting_score'].mean()),
            'correlations': correlations,
            'elite_shooters': {
                'count': len(elite_shooters),
                'avg_ft': float(elite_shooters['ft_percentage'].mean()) if len(elite_shooters) > 0 else None,
                'avg_3pt': float(elite_shooters['three_point_percentage'].mean()) if len(elite_shooters) > 0 else None,
                'top_players': elite_shooters.nlargest(10, 'combined_shooting_score')[['name', 'ft_percentage', 'three_point_percentage']].to_dict('records') if len(elite_shooters) > 0 else []
            },
            'poor_shooters': {
                'count': len(poor_shooters),
                'avg_ft': float(poor_shooters['ft_percentage'].mean()) if len(poor_shooters) > 0 else None,
                'avg_3pt': float(poor_shooters['three_point_percentage'].mean()) if len(poor_shooters) > 0 else None
            }
        }
    
    def analyze_shooting_by_era(self, df: pd.DataFrame) -> Dict:
        """Analyze shooting patterns by era.
        
        Args:
            df: DataFrame
            
        Returns:
            Era-specific shooting analysis
        """
        logger.info("Analyzing shooting by era...")
        
        results = {}
        
        eras = [1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020]
        
        for era in eras:
            era_df = df[df['era'] == era]
            
            if len(era_df) < 10:
                continue
            
            # FT stats
            ft_data = era_df['ft_percentage'].dropna()
            
            # 3PT stats (only for post-1979)
            three_pt_data = era_df['three_point_percentage'].dropna()
            
            results[f"{era}s"] = {
                'sample_size': len(era_df),
                'ft_stats': {
                    'count': len(ft_data),
                    'mean': float(ft_data.mean()) if len(ft_data) > 0 else None,
                    'median': float(ft_data.median()) if len(ft_data) > 0 else None,
                    'elite_count': int((ft_data >= self.ELITE_FT_THRESHOLD).sum()) if len(ft_data) > 0 else 0
                } if len(ft_data) > 0 else None,
                'three_pt_stats': {
                    'count': len(three_pt_data),
                    'mean': float(three_pt_data.mean()) if len(three_pt_data) > 0 else None,
                    'median': float(three_pt_data.median()) if len(three_pt_data) > 0 else None,
                    'elite_count': int((three_pt_data >= self.ELITE_3PT_THRESHOLD).sum()) if len(three_pt_data) > 0 else 0
                } if len(three_pt_data) > 0 else None
            }
        
        return results
    
    def analyze_shooting_by_position(self, df: pd.DataFrame) -> Dict:
        """Analyze shooting patterns by position.
        
        Args:
            df: DataFrame
            
        Returns:
            Position-specific shooting analysis
        """
        logger.info("Analyzing shooting by position...")
        
        results = {}
        
        positions = df['position_group'].unique()
        
        for position in positions:
            pos_df = df[df['position_group'] == position]
            
            if len(pos_df) < 10:
                continue
            
            # FT stats
            ft_data = pos_df['ft_percentage'].dropna()
            
            # 3PT stats
            three_pt_data = pos_df['three_point_percentage'].dropna()
            
            results[position] = {
                'sample_size': len(pos_df),
                'ft_stats': {
                    'count': len(ft_data),
                    'mean': float(ft_data.mean()) if len(ft_data) > 0 else None,
                    'elite_count': int((ft_data >= self.ELITE_FT_THRESHOLD).sum()) if len(ft_data) > 0 else 0
                },
                'three_pt_stats': {
                    'count': len(three_pt_data),
                    'mean': float(three_pt_data.mean()) if len(three_pt_data) > 0 else None,
                    'elite_count': int((three_pt_data >= self.ELITE_3PT_THRESHOLD).sum()) if len(three_pt_data) > 0 else 0
                }
            }
        
        return results
    
    def analyze_elite_vs_poor_shooters(self, df: pd.DataFrame) -> Dict:
        """Compare linguistic profiles of elite vs poor shooters.
        
        Args:
            df: DataFrame
            
        Returns:
            Elite vs poor shooter comparison
        """
        logger.info("Comparing elite vs poor shooters...")
        
        results = {
            'ft_comparison': {},
            'three_pt_comparison': {}
        }
        
        feature_cols = [
            'syllable_count', 'character_length', 'memorability_score',
            'harshness_score', 'softness_score', 'rhythm_score'
        ]
        
        # FT comparison
        ft_df = df[df['ft_percentage'].notna()].copy()
        elite_ft = ft_df[ft_df['ft_percentage'] >= self.ELITE_FT_THRESHOLD]
        poor_ft = ft_df[ft_df['ft_percentage'] < self.POOR_FT_THRESHOLD]
        
        if len(elite_ft) >= 10 and len(poor_ft) >= 10:
            ft_comparison = {}
            
            for feature in feature_cols:
                if feature not in ft_df.columns:
                    continue
                
                elite_mean = elite_ft[feature].mean()
                poor_mean = poor_ft[feature].mean()
                
                # T-test
                t_stat, p_value = stats.ttest_ind(
                    elite_ft[feature].dropna(),
                    poor_ft[feature].dropna()
                )
                
                ft_comparison[feature] = {
                    'elite_mean': float(elite_mean),
                    'poor_mean': float(poor_mean),
                    'difference': float(elite_mean - poor_mean),
                    'percent_difference': float(((elite_mean - poor_mean) / poor_mean * 100)) if poor_mean != 0 else 0,
                    't_statistic': float(t_stat),
                    'p_value': float(p_value),
                    'significant': p_value < 0.05
                }
            
            results['ft_comparison'] = {
                'elite_count': len(elite_ft),
                'poor_count': len(poor_ft),
                'elite_avg_ft': float(elite_ft['ft_percentage'].mean()),
                'poor_avg_ft': float(poor_ft['ft_percentage'].mean()),
                'feature_differences': ft_comparison,
                'top_elite_shooters': elite_ft.nlargest(10, 'ft_percentage')[['name', 'ft_percentage']].to_dict('records')
            }
        
        # 3PT comparison
        three_pt_df = df[df['three_point_percentage'].notna()].copy()
        elite_3pt = three_pt_df[three_pt_df['three_point_percentage'] >= self.ELITE_3PT_THRESHOLD]
        poor_3pt = three_pt_df[three_pt_df['three_point_percentage'] < self.POOR_3PT_THRESHOLD]
        
        if len(elite_3pt) >= 10 and len(poor_3pt) >= 10:
            three_pt_comparison = {}
            
            for feature in feature_cols:
                if feature not in three_pt_df.columns:
                    continue
                
                elite_mean = elite_3pt[feature].mean()
                poor_mean = poor_3pt[feature].mean()
                
                # T-test
                t_stat, p_value = stats.ttest_ind(
                    elite_3pt[feature].dropna(),
                    poor_3pt[feature].dropna()
                )
                
                three_pt_comparison[feature] = {
                    'elite_mean': float(elite_mean),
                    'poor_mean': float(poor_mean),
                    'difference': float(elite_mean - poor_mean),
                    'percent_difference': float(((elite_mean - poor_mean) / poor_mean * 100)) if poor_mean != 0 else 0,
                    't_statistic': float(t_stat),
                    'p_value': float(p_value),
                    'significant': p_value < 0.05
                }
            
            results['three_pt_comparison'] = {
                'elite_count': len(elite_3pt),
                'poor_count': len(poor_3pt),
                'elite_avg_3pt': float(elite_3pt['three_point_percentage'].mean()),
                'poor_avg_3pt': float(poor_3pt['three_point_percentage'].mean()),
                'feature_differences': three_pt_comparison,
                'top_elite_shooters': elite_3pt.nlargest(10, 'three_point_percentage')[['name', 'three_point_percentage']].to_dict('records')
            }
        
        return results
    
    def build_shooting_prediction_models(self, df: pd.DataFrame) -> Dict:
        """Build predictive models for shooting percentages.
        
        Args:
            df: DataFrame
            
        Returns:
            Model results
        """
        logger.info("Building shooting prediction models...")
        
        results = {
            'ft_model': {},
            'three_pt_model': {}
        }
        
        feature_cols = [
            'syllable_count', 'character_length', 'memorability_score',
            'pronounceability_score', 'power_connotation_score',
            'harshness_score', 'softness_score', 'rhythm_score',
            'consonant_cluster_complexity', 'alliteration_score'
        ]
        
        # FT prediction model
        ft_df = df[feature_cols + ['ft_percentage']].dropna()
        
        if len(ft_df) >= 50:
            X_ft = ft_df[feature_cols]
            y_ft = ft_df['ft_percentage']
            
            X_train, X_test, y_train, y_test = train_test_split(
                X_ft, y_ft, test_size=0.2, random_state=42
            )
            
            model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
            model.fit(X_train, y_train)
            
            y_pred = model.predict(X_test)
            r2 = r2_score(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            
            # Feature importance
            feature_importance = dict(zip(feature_cols, model.feature_importances_))
            top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:5]
            
            results['ft_model'] = {
                'sample_size': len(ft_df),
                'r2_score': float(r2),
                'rmse': float(rmse),
                'top_features': [{'feature': f, 'importance': float(imp)} for f, imp in top_features],
                'all_features': {k: float(v) for k, v in feature_importance.items()}
            }
        
        # 3PT prediction model
        three_pt_df = df[feature_cols + ['three_point_percentage']].dropna()
        
        if len(three_pt_df) >= 50:
            X_3pt = three_pt_df[feature_cols]
            y_3pt = three_pt_df['three_point_percentage']
            
            X_train, X_test, y_train, y_test = train_test_split(
                X_3pt, y_3pt, test_size=0.2, random_state=42
            )
            
            model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
            model.fit(X_train, y_train)
            
            y_pred = model.predict(X_test)
            r2 = r2_score(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            
            # Feature importance
            feature_importance = dict(zip(feature_cols, model.feature_importances_))
            top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:5]
            
            results['three_pt_model'] = {
                'sample_size': len(three_pt_df),
                'r2_score': float(r2),
                'rmse': float(rmse),
                'top_features': [{'feature': f, 'importance': float(imp)} for f, imp in top_features],
                'all_features': {k: float(v) for k, v in feature_importance.items()}
            }
        
        return results
    
    def _interpret_correlation(self, corr: float, metric: str) -> str:
        """Interpret correlation coefficient.
        
        Args:
            corr: Correlation coefficient
            metric: Metric name (FT% or 3PT%)
            
        Returns:
            Human-readable interpretation
        """
        abs_corr = abs(corr)
        direction = "higher" if corr > 0 else "lower"
        
        if abs_corr < 0.1:
            strength = "negligible"
        elif abs_corr < 0.3:
            strength = "weak"
        elif abs_corr < 0.5:
            strength = "moderate"
        elif abs_corr < 0.7:
            strength = "strong"
        else:
            strength = "very strong"
        
        return f"{strength.capitalize()} {direction} {metric} association"
    
    def _generate_key_findings(self, results: Dict) -> List[Dict]:
        """Generate key findings from analysis results.
        
        Args:
            results: Full analysis results
            
        Returns:
            List of key findings
        """
        findings = []
        
        # FT findings
        if 'ft_analysis' in results and 'significant_correlations' in results['ft_analysis']:
            sig_ft = results['ft_analysis']['significant_correlations']
            if sig_ft:
                top_ft = sig_ft[0]
                findings.append({
                    'category': 'Free Throw Shooting',
                    'finding': f"Strongest linguistic predictor of FT%: {top_ft['feature']}",
                    'detail': f"Correlation: {top_ft['correlation']:.3f}, p={top_ft['p_value']:.4f}",
                    'interpretation': top_ft['interpretation']
                })
        
        # 3PT findings
        if 'three_pt_analysis' in results and 'significant_correlations' in results['three_pt_analysis']:
            sig_3pt = results['three_pt_analysis']['significant_correlations']
            if sig_3pt:
                top_3pt = sig_3pt[0]
                findings.append({
                    'category': '3-Point Shooting',
                    'finding': f"Strongest linguistic predictor of 3PT%: {top_3pt['feature']}",
                    'detail': f"Correlation: {top_3pt['correlation']:.3f}, p={top_3pt['p_value']:.4f}",
                    'interpretation': top_3pt['interpretation']
                })
        
        # Elite vs poor findings
        if 'elite_vs_poor' in results:
            if 'ft_comparison' in results['elite_vs_poor'] and 'feature_differences' in results['elite_vs_poor']['ft_comparison']:
                ft_comp = results['elite_vs_poor']['ft_comparison']
                # Find most significant difference
                sig_diffs = [(k, v) for k, v in ft_comp['feature_differences'].items() if v.get('significant', False)]
                if sig_diffs:
                    top_diff = max(sig_diffs, key=lambda x: abs(x[1]['difference']))
                    findings.append({
                        'category': 'Elite FT Shooters',
                        'finding': f"Elite FT shooters differ most in: {top_diff[0]}",
                        'detail': f"Elite: {top_diff[1]['elite_mean']:.2f}, Poor: {top_diff[1]['poor_mean']:.2f} ({top_diff[1]['percent_difference']:.1f}% difference)",
                        'interpretation': 'Significant linguistic difference between elite and poor free throw shooters'
                    })
        
        return findings


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    analyzer = NBAShootingAnalyzer()
    df = analyzer.get_shooting_dataset()
    
    if len(df) > 30:
        print("\n" + "="*60)
        print("NBA SHOOTING PERCENTAGE ANALYSIS")
        print("="*60)
        
        results = analyzer.analyze_comprehensive_shooting(df)
        
        # Print key findings
        print("\n--- KEY FINDINGS ---")
        for finding in results.get('key_findings', []):
            print(f"\n{finding['category']}:")
            print(f"  {finding['finding']}")
            print(f"  {finding['detail']}")
        
        # Save results
        output_file = 'analysis_outputs/current/nba_shooting_analysis.json'
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nFull results saved to: {output_file}")
    else:
        print("Insufficient data. Please collect more NBA players first.")

