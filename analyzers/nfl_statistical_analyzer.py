"""NFL Statistical Analyzer

Comprehensive statistical modeling for NFL player name analysis.
Implements prediction models for position, performance, and career success.

Models:
- Position prediction: linguistic features → position (Offense/Defense/Special Teams)
- Performance prediction by position:
  - QB: passer_rating, completion_pct, TD/INT ratio
  - RB: yards_per_carry, rushing_yards
  - WR/TE: yards_per_reception, catch_rate
  - Defensive: tackles, sacks, interceptions
- Career success: linguistic features → achievement score
- Era-specific formulas: what works in each era (decade + rule era)
- Position-specific patterns: naming patterns by position
"""

import logging
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, r2_score, mean_squared_error, accuracy_score, classification_report
from scipy import stats

from core.models import db, NFLPlayer, NFLPlayerAnalysis

logger = logging.getLogger(__name__)


class NFLStatisticalAnalyzer:
    """Comprehensive statistical analysis for NFL player name prediction."""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.position_model = None
        self.performance_models = {}
    
    def get_comprehensive_dataset(self) -> pd.DataFrame:
        """Load all players with complete data.
        
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
                    # Metadata
                    'id': player.id,
                    'name': player.name,
                    'debut_year': player.debut_year,
                    'era': player.era,
                    'era_group': player.era_group,
                    'rule_era': player.rule_era,
                    'position': player.position,
                    'position_group': player.position_group,
                    'position_category': player.position_category,
                    'primary_position': player.primary_position,
                    'years_active': player.years_active or 0,
                    'is_active': player.is_active,
                    'games_played': player.games_played or 0,
                    'games_started': player.games_started or 0,
                    
                    # QB stats (outcomes)
                    'completion_pct': player.completion_pct,
                    'passing_yards': player.passing_yards,
                    'passing_tds': player.passing_tds,
                    'interceptions': player.interceptions,
                    'passer_rating': player.passer_rating,
                    'qbr': player.qbr,
                    'yards_per_attempt': player.yards_per_attempt,
                    'td_int_ratio': player.td_int_ratio,
                    
                    # RB stats
                    'rushing_yards': player.rushing_yards,
                    'rushing_tds': player.rushing_tds,
                    'yards_per_carry': player.yards_per_carry,
                    'rushing_fumbles': player.rushing_fumbles,
                    
                    # Receiving stats
                    'receptions': player.receptions,
                    'receiving_yards': player.receiving_yards,
                    'receiving_tds': player.receiving_tds,
                    'yards_per_reception': player.yards_per_reception,
                    'catch_rate': player.catch_rate,
                    'yards_after_catch': player.yards_after_catch,
                    
                    # Defensive stats
                    'tackles': player.tackles,
                    'sacks': player.sacks,
                    'defensive_interceptions': player.defensive_interceptions,
                    'forced_fumbles': player.forced_fumbles,
                    'pass_deflections': player.pass_deflections,
                    
                    # Special teams
                    'field_goal_pct': player.field_goal_pct,
                    'punting_avg': player.punting_avg,
                    
                    # Success metrics
                    'performance_score': player.performance_score or 0,
                    'career_achievement_score': player.career_achievement_score or 0,
                    'longevity_score': player.longevity_score or 0,
                    'overall_success_score': player.overall_success_score or 0,
                    'pro_bowl_count': player.pro_bowl_count or 0,
                    'hof_inducted': player.hof_inducted or False,
                    'approximate_value': player.approximate_value,
                    'career_av': player.career_av,
                    
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
                    'toughness_score': analysis.toughness_score or 50,
                    'rhythm_score': analysis.rhythm_score or 50,
                    'consonant_cluster_complexity': analysis.consonant_cluster_complexity or 50,
                    'alliteration_score': analysis.alliteration_score or 0,
                    
                    # Name component analysis
                    'first_name_syllables': analysis.first_name_syllables or 0,
                    'first_name_length': analysis.first_name_length or 0,
                    'last_name_syllables': analysis.last_name_syllables or 0,
                    'last_name_length': analysis.last_name_length or 0,
                    
                    # Contextual
                    'temporal_cohort': analysis.temporal_cohort,
                    'rule_era_cohort': analysis.rule_era_cohort,
                    'position_cluster': analysis.position_cluster,
                    'position_category_cluster': analysis.position_category_cluster,
                }
                
                rows.append(row)
                
            except Exception as e:
                logger.warning(f"Error loading player {player.name}: {e}")
                continue
        
        df = pd.DataFrame(rows)
        logger.info(f"Loaded {len(df)} players for statistical analysis")
        
        return df
    
    def analyze_position_predictors(self, df: pd.DataFrame) -> Dict:
        """Analyze which linguistic features predict position.
        
        Args:
            df: DataFrame with player data
            
        Returns:
            Position prediction analysis results
        """
        logger.info("Analyzing position predictors...")
        
        results = {
            'position_group_model': {},
            'position_category_model': {},
            'primary_position_model': {},
            'feature_importance': {},
            'position_profiles': {},
            'correlations': {}
        }
        
        # Define feature columns
        feature_cols = [
            'syllable_count', 'character_length', 'word_count',
            'memorability_score', 'pronounceability_score', 'uniqueness_score',
            'power_connotation_score', 'harshness_score', 'softness_score',
            'phonetic_score', 'vowel_ratio', 'speed_association_score',
            'strength_association_score', 'toughness_score', 'rhythm_score', 
            'consonant_cluster_complexity', 'alliteration_score', 
            'first_name_syllables', 'last_name_syllables'
        ]
        
        # Prepare data
        df_clean = df[feature_cols + ['position_group', 'position_category', 'primary_position']].dropna()
        
        if len(df_clean) < 50:
            logger.warning("Insufficient data for position modeling")
            return results
        
        X = df_clean[feature_cols]
        
        # 1. Position Group prediction (Offense/Defense/Special Teams)
        y_group = df_clean['position_group']
        if len(y_group.unique()) >= 2:
            results['position_group_model'] = self._train_classification_model(
                X, y_group, 'Position Group', feature_cols
            )
        
        # 2. Position Category prediction (Skill/Offensive Line/Defensive Line/etc.)
        y_category = df_clean['position_category']
        if len(y_category.unique()) >= 3:
            results['position_category_model'] = self._train_classification_model(
                X, y_category, 'Position Category', feature_cols
            )
        
        # 3. Primary Position prediction (QB/RB/WR/etc.)
        y_primary = df_clean['primary_position']
        if len(y_primary.unique()) >= 3:
            results['primary_position_model'] = self._train_classification_model(
                X, y_primary, 'Primary Position', feature_cols
            )
        
        # 4. Position-specific profiles
        results['position_profiles'] = self._analyze_position_profiles(df, feature_cols)
        
        # 5. Feature correlations with position
        results['correlations'] = self._analyze_position_correlations(df, feature_cols)
        
        return results
    
    def analyze_qb_performance_predictors(self, df: pd.DataFrame) -> Dict:
        """Analyze QB-specific performance predictors.
        
        Args:
            df: DataFrame with player data
            
        Returns:
            QB performance prediction results
        """
        logger.info("Analyzing QB performance predictors...")
        
        # Filter to QBs only
        qb_df = df[df['position'] == 'QB'].copy()
        
        if len(qb_df) < 30:
            logger.warning("Insufficient QB data for modeling")
            return {}
        
        results = {
            'completion_pct_model': {},
            'passer_rating_model': {},
            'td_int_ratio_model': {},
            'yards_per_attempt_model': {},
            'feature_importance': {},
            'correlations': {}
        }
        
        feature_cols = self._get_feature_columns()
        
        # Completion percentage prediction
        qb_comp = qb_df[['completion_pct'] + feature_cols].dropna()
        if len(qb_comp) >= 30:
            X = qb_comp[feature_cols]
            y = qb_comp['completion_pct']
            results['completion_pct_model'] = self._train_regression_model(
                X, y, 'Completion %', feature_cols
            )
        
        # Passer rating prediction
        qb_rating = qb_df[['passer_rating'] + feature_cols].dropna()
        if len(qb_rating) >= 30:
            X = qb_rating[feature_cols]
            y = qb_rating['passer_rating']
            results['passer_rating_model'] = self._train_regression_model(
                X, y, 'Passer Rating', feature_cols
            )
        
        # TD/INT ratio prediction
        qb_ratio = qb_df[['td_int_ratio'] + feature_cols].dropna()
        if len(qb_ratio) >= 30:
            X = qb_ratio[feature_cols]
            y = qb_ratio['td_int_ratio']
            results['td_int_ratio_model'] = self._train_regression_model(
                X, y, 'TD/INT Ratio', feature_cols
            )
        
        # Yards per attempt prediction
        qb_ypa = qb_df[['yards_per_attempt'] + feature_cols].dropna()
        if len(qb_ypa) >= 30:
            X = qb_ypa[feature_cols]
            y = qb_ypa['yards_per_attempt']
            results['yards_per_attempt_model'] = self._train_regression_model(
                X, y, 'Yards Per Attempt', feature_cols
            )
        
        # Correlations
        results['correlations'] = self._calculate_correlations(qb_df, feature_cols, 
                                                               ['completion_pct', 'passer_rating', 
                                                                'td_int_ratio', 'yards_per_attempt'])
        
        return results
    
    def analyze_rb_performance_predictors(self, df: pd.DataFrame) -> Dict:
        """Analyze RB-specific performance predictors.
        
        Args:
            df: DataFrame with player data
            
        Returns:
            RB performance prediction results
        """
        logger.info("Analyzing RB performance predictors...")
        
        rb_df = df[df['position'] == 'RB'].copy()
        
        if len(rb_df) < 30:
            logger.warning("Insufficient RB data for modeling")
            return {}
        
        results = {
            'yards_per_carry_model': {},
            'rushing_yards_model': {},
            'fumbles_model': {},
            'feature_importance': {},
            'correlations': {}
        }
        
        feature_cols = self._get_feature_columns()
        
        # Yards per carry prediction
        rb_ypc = rb_df[['yards_per_carry'] + feature_cols].dropna()
        if len(rb_ypc) >= 30:
            X = rb_ypc[feature_cols]
            y = rb_ypc['yards_per_carry']
            results['yards_per_carry_model'] = self._train_regression_model(
                X, y, 'Yards Per Carry', feature_cols
            )
        
        # Rushing yards prediction
        rb_yards = rb_df[['rushing_yards'] + feature_cols].dropna()
        if len(rb_yards) >= 30:
            X = rb_yards[feature_cols]
            y = rb_yards['rushing_yards']
            results['rushing_yards_model'] = self._train_regression_model(
                X, y, 'Rushing Yards', feature_cols
            )
        
        # Correlations
        results['correlations'] = self._calculate_correlations(rb_df, feature_cols,
                                                               ['yards_per_carry', 'rushing_yards', 
                                                                'rushing_fumbles'])
        
        return results
    
    def analyze_wr_performance_predictors(self, df: pd.DataFrame) -> Dict:
        """Analyze WR/TE-specific performance predictors.
        
        Args:
            df: DataFrame with player data
            
        Returns:
            WR/TE performance prediction results
        """
        logger.info("Analyzing WR/TE performance predictors...")
        
        wr_df = df[df['position'].isin(['WR', 'TE'])].copy()
        
        if len(wr_df) < 30:
            logger.warning("Insufficient WR/TE data for modeling")
            return {}
        
        results = {
            'yards_per_reception_model': {},
            'catch_rate_model': {},
            'receiving_yards_model': {},
            'feature_importance': {},
            'correlations': {}
        }
        
        feature_cols = self._get_feature_columns()
        
        # Yards per reception prediction
        wr_ypr = wr_df[['yards_per_reception'] + feature_cols].dropna()
        if len(wr_ypr) >= 30:
            X = wr_ypr[feature_cols]
            y = wr_ypr['yards_per_reception']
            results['yards_per_reception_model'] = self._train_regression_model(
                X, y, 'Yards Per Reception', feature_cols
            )
        
        # Catch rate prediction
        wr_catch = wr_df[['catch_rate'] + feature_cols].dropna()
        if len(wr_catch) >= 30:
            X = wr_catch[feature_cols]
            y = wr_catch['catch_rate']
            results['catch_rate_model'] = self._train_regression_model(
                X, y, 'Catch Rate', feature_cols
            )
        
        # Correlations
        results['correlations'] = self._calculate_correlations(wr_df, feature_cols,
                                                               ['yards_per_reception', 'catch_rate', 
                                                                'receiving_yards'])
        
        return results
    
    def analyze_defensive_performance_predictors(self, df: pd.DataFrame) -> Dict:
        """Analyze defensive player performance predictors.
        
        Args:
            df: DataFrame with player data
            
        Returns:
            Defensive performance prediction results
        """
        logger.info("Analyzing defensive performance predictors...")
        
        def_df = df[df['position_group'] == 'Defense'].copy()
        
        if len(def_df) < 30:
            logger.warning("Insufficient defensive data for modeling")
            return {}
        
        results = {
            'tackles_model': {},
            'sacks_model': {},
            'interceptions_model': {},
            'feature_importance': {},
            'correlations': {}
        }
        
        feature_cols = self._get_feature_columns()
        
        # Tackles prediction
        def_tackles = def_df[['tackles'] + feature_cols].dropna()
        if len(def_tackles) >= 30:
            X = def_tackles[feature_cols]
            y = def_tackles['tackles']
            results['tackles_model'] = self._train_regression_model(
                X, y, 'Tackles', feature_cols
            )
        
        # Sacks prediction
        def_sacks = def_df[['sacks'] + feature_cols].dropna()
        if len(def_sacks) >= 30:
            X = def_sacks[feature_cols]
            y = def_sacks['sacks']
            results['sacks_model'] = self._train_regression_model(
                X, y, 'Sacks', feature_cols
            )
        
        # Interceptions prediction
        def_int = def_df[['defensive_interceptions'] + feature_cols].dropna()
        if len(def_int) >= 30:
            X = def_int[feature_cols]
            y = def_int['defensive_interceptions']
            results['interceptions_model'] = self._train_regression_model(
                X, y, 'Interceptions', feature_cols
            )
        
        # Correlations
        results['correlations'] = self._calculate_correlations(def_df, feature_cols,
                                                               ['tackles', 'sacks', 
                                                                'defensive_interceptions'])
        
        return results
    
    def _get_feature_columns(self) -> List[str]:
        """Get standard feature columns for modeling."""
        return [
            'syllable_count', 'character_length', 'word_count',
            'memorability_score', 'pronounceability_score', 'uniqueness_score',
            'power_connotation_score', 'harshness_score', 'softness_score',
            'phonetic_score', 'vowel_ratio', 'speed_association_score',
            'strength_association_score', 'toughness_score', 'rhythm_score',
            'consonant_cluster_complexity', 'alliteration_score',
            'first_name_syllables', 'last_name_syllables'
        ]
    
    def _train_classification_model(self, X: pd.DataFrame, y: pd.Series, 
                                   model_name: str, feature_names: List[str]) -> Dict:
        """Train random forest classification model.
        
        Args:
            X: Feature matrix
            y: Target labels
            model_name: Name of the model
            feature_names: List of feature names
            
        Returns:
            Model results dictionary
        """
        try:
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Train model
            model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=10,
                min_samples_leaf=5,
                random_state=42
            )
            
            model.fit(X_train, y_train)
            
            # Evaluate
            train_score = model.score(X_train, y_train)
            test_score = model.score(X_test, y_test)
            
            y_pred = model.predict(X_test)
            
            # Feature importance
            importances = dict(zip(feature_names, model.feature_importances_))
            top_features = sorted(importances.items(), key=lambda x: x[1], reverse=True)[:10]
            
            results = {
                'model_name': model_name,
                'train_accuracy': float(train_score),
                'test_accuracy': float(test_score),
                'n_classes': len(np.unique(y)),
                'sample_size': len(X),
                'feature_importance': dict(top_features),
                'top_3_features': [f[0] for f in top_features[:3]]
            }
            
            logger.info(f"{model_name} - Test Accuracy: {test_score:.3f}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error training {model_name} model: {e}")
            return {'error': str(e)}
    
    def _train_regression_model(self, X: pd.DataFrame, y: pd.Series,
                               model_name: str, feature_names: List[str]) -> Dict:
        """Train random forest regression model.
        
        Args:
            X: Feature matrix
            y: Target values
            model_name: Name of the model
            feature_names: List of feature names
            
        Returns:
            Model results dictionary
        """
        try:
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Train model
            model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                min_samples_split=10,
                min_samples_leaf=5,
                random_state=42
            )
            
            model.fit(X_train, y_train)
            
            # Evaluate
            train_score = model.score(X_train, y_train)
            test_score = model.score(X_test, y_test)
            
            y_pred = model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            
            # Feature importance
            importances = dict(zip(feature_names, model.feature_importances_))
            top_features = sorted(importances.items(), key=lambda x: x[1], reverse=True)[:10]
            
            results = {
                'model_name': model_name,
                'train_r2': float(train_score),
                'test_r2': float(test_score),
                'rmse': float(rmse),
                'sample_size': len(X),
                'feature_importance': dict(top_features),
                'top_3_features': [f[0] for f in top_features[:3]]
            }
            
            logger.info(f"{model_name} - Test R²: {test_score:.3f}, RMSE: {rmse:.3f}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error training {model_name} model: {e}")
            return {'error': str(e)}
    
    def _analyze_position_profiles(self, df: pd.DataFrame, feature_cols: List[str]) -> Dict:
        """Analyze linguistic profiles by position.
        
        Args:
            df: DataFrame with player data
            feature_cols: List of feature columns
            
        Returns:
            Position profiles dictionary
        """
        profiles = {}
        
        for position_group in df['position_group'].unique():
            if pd.isna(position_group):
                continue
            
            group_df = df[df['position_group'] == position_group]
            
            if len(group_df) < 10:
                continue
            
            profile = {}
            for feature in feature_cols:
                if feature in group_df.columns:
                    values = group_df[feature].dropna()
                    if len(values) > 0:
                        profile[feature] = {
                            'mean': float(values.mean()),
                            'median': float(values.median()),
                            'std': float(values.std())
                        }
            
            profiles[position_group] = profile
        
        return profiles
    
    def _analyze_position_correlations(self, df: pd.DataFrame, feature_cols: List[str]) -> Dict:
        """Analyze correlations between features and position groups.
        
        Args:
            df: DataFrame with player data
            feature_cols: List of feature columns
            
        Returns:
            Correlations dictionary
        """
        correlations = {}
        
        # Encode position group as numeric
        position_groups = df['position_group'].dropna().unique()
        position_map = {pos: i for i, pos in enumerate(position_groups)}
        df_corr = df.copy()
        df_corr['position_numeric'] = df_corr['position_group'].map(position_map)
        
        for feature in feature_cols:
            if feature in df_corr.columns:
                valid_data = df_corr[[feature, 'position_numeric']].dropna()
                if len(valid_data) > 30:
                    corr, pval = stats.pearsonr(valid_data[feature], valid_data['position_numeric'])
                    correlations[feature] = {
                        'correlation': float(corr),
                        'p_value': float(pval),
                        'significant': pval < 0.05
                    }
        
        return correlations
    
    def _calculate_correlations(self, df: pd.DataFrame, feature_cols: List[str],
                               outcome_cols: List[str]) -> Dict:
        """Calculate correlations between features and outcomes.
        
        Args:
            df: DataFrame with player data
            feature_cols: List of feature columns
            outcome_cols: List of outcome columns
            
        Returns:
            Correlations dictionary
        """
        correlations = {}
        
        for outcome in outcome_cols:
            if outcome not in df.columns:
                continue
            
            outcome_corrs = {}
            for feature in feature_cols:
                if feature in df.columns:
                    valid_data = df[[feature, outcome]].dropna()
                    if len(valid_data) > 30:
                        corr, pval = stats.pearsonr(valid_data[feature], valid_data[outcome])
                        outcome_corrs[feature] = {
                            'correlation': float(corr),
                            'p_value': float(pval),
                            'significant': pval < 0.05
                        }
            
            # Get top correlations
            significant_corrs = {k: v for k, v in outcome_corrs.items() if v['significant']}
            top_corrs = sorted(significant_corrs.items(), 
                             key=lambda x: abs(x[1]['correlation']), 
                             reverse=True)[:5]
            
            correlations[outcome] = {
                'all_correlations': outcome_corrs,
                'top_5_correlations': dict(top_corrs),
                'n_significant': len(significant_corrs)
            }
        
        return correlations
    
    def run_comprehensive_analysis(self) -> Dict:
        """Run all statistical analyses.
        
        Returns:
            Comprehensive analysis results
        """
        logger.info("Running comprehensive NFL statistical analysis...")
        
        # Load data
        df = self.get_comprehensive_dataset()
        
        if len(df) == 0:
            logger.error("No data available for analysis")
            return {'error': 'No data available'}
        
        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'dataset_size': len(df),
            'position_analysis': self.analyze_position_predictors(df),
            'qb_analysis': self.analyze_qb_performance_predictors(df),
            'rb_analysis': self.analyze_rb_performance_predictors(df),
            'wr_analysis': self.analyze_wr_performance_predictors(df),
            'defensive_analysis': self.analyze_defensive_performance_predictors(df),
        }
        
        logger.info("Comprehensive analysis complete")
        
        return results

