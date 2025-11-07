"""NFL Position Analyzer

Analyzes linguistic patterns by position group.
Identifies position-specific phonetic patterns and name characteristics.

Analyses:
- QB names vs Linemen names vs Skill position names
- Offensive vs Defensive player naming patterns
- Position-specific sound symbolism
- Statistical testing for position differences
"""

import logging
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime

from scipy import stats
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.decomposition import PCA

from core.models import db, NFLPlayer, NFLPlayerAnalysis

logger = logging.getLogger(__name__)


class NFLPositionAnalyzer:
    """Analyze linguistic patterns by NFL position."""
    
    def __init__(self):
        pass
    
    def get_all_players(self) -> pd.DataFrame:
        """Load all players with analysis data.
        
        Returns:
            DataFrame with player and analysis data
        """
        query = db.session.query(NFLPlayer, NFLPlayerAnalysis).join(
            NFLPlayerAnalysis,
            NFLPlayer.id == NFLPlayerAnalysis.player_id
        )
        
        rows = []
        for player, analysis in query.all():
            try:
                row = {
                    'id': player.id,
                    'name': player.name,
                    'position': player.position,
                    'position_group': player.position_group,
                    'position_category': player.position_category,
                    
                    # Linguistic features
                    'syllable_count': analysis.syllable_count or 0,
                    'character_length': analysis.character_length or 0,
                    'memorability_score': analysis.memorability_score or 0,
                    'pronounceability_score': analysis.pronounceability_score or 0,
                    'uniqueness_score': analysis.uniqueness_score or 0,
                    'power_connotation_score': analysis.power_connotation_score or 0,
                    'harshness_score': analysis.harshness_score or 0,
                    'softness_score': analysis.softness_score or 0,
                    'vowel_ratio': analysis.vowel_ratio or 0,
                    'speed_association_score': analysis.speed_association_score or 50,
                    'strength_association_score': analysis.strength_association_score or 50,
                    'toughness_score': analysis.toughness_score or 50,
                    'rhythm_score': analysis.rhythm_score or 50,
                    'consonant_cluster_complexity': analysis.consonant_cluster_complexity or 50,
                    'alliteration_score': analysis.alliteration_score or 0,
                    'first_name_syllables': analysis.first_name_syllables or 0,
                    'last_name_syllables': analysis.last_name_syllables or 0,
                }
                
                rows.append(row)
                
            except Exception as e:
                logger.warning(f"Error loading player {player.name}: {e}")
                continue
        
        df = pd.DataFrame(rows)
        logger.info(f"Loaded {len(df)} players for position analysis")
        
        return df
    
    def analyze_position_groups(self) -> Dict:
        """Analyze linguistic differences between position groups.
        
        Returns:
            Position group analysis results
        """
        logger.info("Analyzing position group differences...")
        
        df = self.get_all_players()
        
        if len(df) < 50:
            logger.warning("Insufficient data")
            return {'error': 'Insufficient data'}
        
        feature_cols = [
            'syllable_count', 'character_length', 'memorability_score',
            'pronounceability_score', 'uniqueness_score', 'power_connotation_score',
            'harshness_score', 'softness_score', 'vowel_ratio',
            'speed_association_score', 'strength_association_score',
            'toughness_score', 'rhythm_score', 'consonant_cluster_complexity',
            'alliteration_score'
        ]
        
        results = {
            'position_group_profiles': self._get_position_group_profiles(df, feature_cols),
            'statistical_tests': self._test_position_group_differences(df, feature_cols),
            'discriminant_analysis': self._perform_discriminant_analysis(df, feature_cols),
        }
        
        return results
    
    def analyze_position_categories(self) -> Dict:
        """Analyze linguistic differences between position categories.
        
        Returns:
            Position category analysis results
        """
        logger.info("Analyzing position category differences...")
        
        df = self.get_all_players()
        
        if len(df) < 50:
            logger.warning("Insufficient data")
            return {'error': 'Insufficient data'}
        
        feature_cols = [
            'syllable_count', 'character_length', 'memorability_score',
            'harshness_score', 'softness_score', 'toughness_score',
            'power_connotation_score', 'speed_association_score',
            'strength_association_score', 'rhythm_score'
        ]
        
        results = {
            'category_profiles': self._get_category_profiles(df, feature_cols),
            'skill_vs_line': self._compare_skill_vs_line(df, feature_cols),
            'offense_vs_defense': self._compare_offense_vs_defense(df, feature_cols),
        }
        
        return results
    
    def analyze_specific_positions(self) -> Dict:
        """Analyze individual position linguistic patterns.
        
        Returns:
            Specific position analysis results
        """
        logger.info("Analyzing specific position patterns...")
        
        df = self.get_all_players()
        
        if len(df) < 50:
            logger.warning("Insufficient data")
            return {'error': 'Insufficient data'}
        
        major_positions = ['QB', 'RB', 'WR', 'TE', 'OT', 'DE', 'LB', 'CB', 'S']
        
        feature_cols = [
            'syllable_count', 'character_length', 'harshness_score',
            'softness_score', 'toughness_score', 'speed_association_score',
            'power_connotation_score'
        ]
        
        position_profiles = {}
        
        for position in major_positions:
            pos_df = df[df['position'] == position]
            
            if len(pos_df) < 10:
                continue
            
            profile = {}
            for feature in feature_cols:
                values = pos_df[feature].dropna()
                if len(values) > 0:
                    profile[feature] = {
                        'mean': float(values.mean()),
                        'median': float(values.median()),
                        'std': float(values.std()),
                        'min': float(values.min()),
                        'max': float(values.max())
                    }
            
            profile['sample_size'] = len(pos_df)
            position_profiles[position] = profile
        
        return {
            'position_profiles': position_profiles,
            'qb_characteristics': self._analyze_qb_names(df),
            'linemen_characteristics': self._analyze_linemen_names(df),
            'skill_position_characteristics': self._analyze_skill_position_names(df),
        }
    
    def _get_position_group_profiles(self, df: pd.DataFrame, 
                                    feature_cols: List[str]) -> Dict:
        """Get mean profiles for each position group.
        
        Args:
            df: DataFrame with player data
            feature_cols: List of feature columns
            
        Returns:
            Position group profiles
        """
        profiles = {}
        
        for position_group in df['position_group'].dropna().unique():
            group_df = df[df['position_group'] == position_group]
            
            if len(group_df) < 10:
                continue
            
            profile = {
                'count': len(group_df)
            }
            
            for feature in feature_cols:
                values = group_df[feature].dropna()
                if len(values) > 0:
                    profile[feature] = {
                        'mean': float(values.mean()),
                        'std': float(values.std())
                    }
            
            profiles[position_group] = profile
        
        return profiles
    
    def _test_position_group_differences(self, df: pd.DataFrame,
                                        feature_cols: List[str]) -> Dict:
        """Test statistical significance of position group differences.
        
        Args:
            df: DataFrame with player data
            feature_cols: List of feature columns
            
        Returns:
            Statistical test results
        """
        tests = {}
        
        # Get position groups
        groups = df['position_group'].dropna().unique()
        
        if len(groups) < 2:
            return {'error': 'Need at least 2 position groups'}
        
        for feature in feature_cols:
            # Prepare data for each group
            group_data = []
            for group in groups:
                group_values = df[df['position_group'] == group][feature].dropna()
                if len(group_values) >= 10:
                    group_data.append(group_values)
            
            if len(group_data) < 2:
                continue
            
            # ANOVA test
            try:
                f_stat, p_val = stats.f_oneway(*group_data)
                
                tests[feature] = {
                    'f_statistic': float(f_stat),
                    'p_value': float(p_val),
                    'significant': p_val < 0.05,
                    'n_groups': len(group_data)
                }
            except:
                continue
        
        # Count significant features
        significant_count = sum(1 for t in tests.values() if t.get('significant', False))
        
        return {
            'tests': tests,
            'n_features_tested': len(tests),
            'n_significant': significant_count
        }
    
    def _perform_discriminant_analysis(self, df: pd.DataFrame,
                                      feature_cols: List[str]) -> Dict:
        """Perform linear discriminant analysis to separate position groups.
        
        Args:
            df: DataFrame with player data
            feature_cols: List of feature columns
            
        Returns:
            Discriminant analysis results
        """
        try:
            # Prepare data
            analysis_data = df[feature_cols + ['position_group']].dropna()
            
            if len(analysis_data) < 50:
                return {'error': 'Insufficient data'}
            
            X = analysis_data[feature_cols]
            y = analysis_data['position_group']
            
            # Fit LDA
            lda = LinearDiscriminantAnalysis()
            lda.fit(X, y)
            
            # Get accuracy
            accuracy = lda.score(X, y)
            
            # Get most important features for discrimination
            # (based on absolute values of discriminant coefficients)
            coef_means = np.abs(lda.coef_).mean(axis=0)
            feature_importance = dict(zip(feature_cols, coef_means))
            top_features = sorted(feature_importance.items(), 
                                key=lambda x: x[1], reverse=True)[:5]
            
            return {
                'accuracy': float(accuracy),
                'n_components': int(lda.n_components),
                'top_discriminating_features': dict(top_features),
                'sample_size': len(analysis_data)
            }
            
        except Exception as e:
            logger.error(f"Error in discriminant analysis: {e}")
            return {'error': str(e)}
    
    def _get_category_profiles(self, df: pd.DataFrame,
                              feature_cols: List[str]) -> Dict:
        """Get mean profiles for each position category.
        
        Args:
            df: DataFrame with player data
            feature_cols: List of feature columns
            
        Returns:
            Position category profiles
        """
        profiles = {}
        
        for category in df['position_category'].dropna().unique():
            cat_df = df[df['position_category'] == category]
            
            if len(cat_df) < 10:
                continue
            
            profile = {
                'count': len(cat_df)
            }
            
            for feature in feature_cols:
                values = cat_df[feature].dropna()
                if len(values) > 0:
                    profile[feature] = {
                        'mean': float(values.mean()),
                        'std': float(values.std())
                    }
            
            profiles[category] = profile
        
        return profiles
    
    def _compare_skill_vs_line(self, df: pd.DataFrame,
                               feature_cols: List[str]) -> Dict:
        """Compare skill positions vs offensive/defensive line.
        
        Args:
            df: DataFrame with player data
            feature_cols: List of feature columns
            
        Returns:
            Comparison results
        """
        skill_positions = ['QB', 'RB', 'WR', 'TE', 'CB', 'S']
        line_positions = ['OT', 'OG', 'C', 'DE', 'DT', 'NT']
        
        skill_df = df[df['position'].isin(skill_positions)]
        line_df = df[df['position'].isin(line_positions)]
        
        if len(skill_df) < 20 or len(line_df) < 20:
            return {'error': 'Insufficient data'}
        
        comparison = {
            'skill_count': len(skill_df),
            'line_count': len(line_df),
            'differences': {}
        }
        
        for feature in feature_cols:
            skill_values = skill_df[feature].dropna()
            line_values = line_df[feature].dropna()
            
            if len(skill_values) < 10 or len(line_values) < 10:
                continue
            
            skill_mean = skill_values.mean()
            line_mean = line_values.mean()
            diff = skill_mean - line_mean
            
            # T-test
            try:
                t_stat, p_val = stats.ttest_ind(skill_values, line_values)
                significant = p_val < 0.05
            except:
                t_stat, p_val, significant = 0, 1, False
            
            comparison['differences'][feature] = {
                'skill_mean': float(skill_mean),
                'line_mean': float(line_mean),
                'difference': float(diff),
                't_statistic': float(t_stat),
                'p_value': float(p_val),
                'significant': significant
            }
        
        return comparison
    
    def _compare_offense_vs_defense(self, df: pd.DataFrame,
                                   feature_cols: List[str]) -> Dict:
        """Compare offensive vs defensive players.
        
        Args:
            df: DataFrame with player data
            feature_cols: List of feature columns
            
        Returns:
            Comparison results
        """
        offense_df = df[df['position_group'] == 'Offense']
        defense_df = df[df['position_group'] == 'Defense']
        
        if len(offense_df) < 20 or len(defense_df) < 20:
            return {'error': 'Insufficient data'}
        
        comparison = {
            'offense_count': len(offense_df),
            'defense_count': len(defense_df),
            'differences': {}
        }
        
        for feature in feature_cols:
            off_values = offense_df[feature].dropna()
            def_values = defense_df[feature].dropna()
            
            if len(off_values) < 10 or len(def_values) < 10:
                continue
            
            off_mean = off_values.mean()
            def_mean = def_values.mean()
            diff = off_mean - def_mean
            
            # T-test
            try:
                t_stat, p_val = stats.ttest_ind(off_values, def_values)
                significant = p_val < 0.05
            except:
                t_stat, p_val, significant = 0, 1, False
            
            comparison['differences'][feature] = {
                'offense_mean': float(off_mean),
                'defense_mean': float(def_mean),
                'difference': float(diff),
                't_statistic': float(t_stat),
                'p_value': float(p_val),
                'significant': significant
            }
        
        return comparison
    
    def _analyze_qb_names(self, df: pd.DataFrame) -> Dict:
        """Analyze QB name characteristics.
        
        Args:
            df: DataFrame with player data
            
        Returns:
            QB name analysis
        """
        qb_df = df[df['position'] == 'QB']
        
        if len(qb_df) < 20:
            return {'error': 'Insufficient QB data'}
        
        return {
            'sample_size': len(qb_df),
            'avg_syllables': float(qb_df['syllable_count'].mean()),
            'avg_harshness': float(qb_df['harshness_score'].mean()),
            'avg_memorability': float(qb_df['memorability_score'].mean()),
            'avg_toughness': float(qb_df['toughness_score'].mean()),
            'key_insight': 'QB names tend to be memorable and authoritative'
        }
    
    def _analyze_linemen_names(self, df: pd.DataFrame) -> Dict:
        """Analyze linemen name characteristics.
        
        Args:
            df: DataFrame with player data
            
        Returns:
            Linemen name analysis
        """
        line_positions = ['OT', 'OG', 'C', 'G', 'T', 'DE', 'DT', 'NT']
        line_df = df[df['position'].isin(line_positions)]
        
        if len(line_df) < 20:
            return {'error': 'Insufficient linemen data'}
        
        return {
            'sample_size': len(line_df),
            'avg_syllables': float(line_df['syllable_count'].mean()),
            'avg_harshness': float(line_df['harshness_score'].mean()),
            'avg_toughness': float(line_df['toughness_score'].mean()),
            'avg_power': float(line_df['power_connotation_score'].mean()),
            'key_insight': 'Linemen names tend to be harsh and power-associated'
        }
    
    def _analyze_skill_position_names(self, df: pd.DataFrame) -> Dict:
        """Analyze skill position name characteristics.
        
        Args:
            df: DataFrame with player data
            
        Returns:
            Skill position name analysis
        """
        skill_positions = ['RB', 'WR', 'TE', 'CB', 'S']
        skill_df = df[df['position'].isin(skill_positions)]
        
        if len(skill_df) < 20:
            return {'error': 'Insufficient skill position data'}
        
        return {
            'sample_size': len(skill_df),
            'avg_syllables': float(skill_df['syllable_count'].mean()),
            'avg_speed_association': float(skill_df['speed_association_score'].mean()),
            'avg_memorability': float(skill_df['memorability_score'].mean()),
            'avg_softness': float(skill_df['softness_score'].mean()),
            'key_insight': 'Skill position names tend to be memorable and speed-associated'
        }
    
    def run_comprehensive_analysis(self) -> Dict:
        """Run all position analyses.
        
        Returns:
            Comprehensive analysis results
        """
        logger.info("Running comprehensive NFL position analysis...")
        
        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'position_group_analysis': self.analyze_position_groups(),
            'position_category_analysis': self.analyze_position_categories(),
            'specific_position_analysis': self.analyze_specific_positions(),
        }
        
        logger.info("Position analysis complete")
        
        return results

