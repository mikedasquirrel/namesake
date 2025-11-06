"""NBA Statistical Analyzer

Comprehensive statistical modeling for NBA player name analysis.
Implements prediction models for position, performance, and career success.

Models:
- Position prediction: linguistic features → position (Guard/Forward/Center)
- Performance prediction: linguistic features → PPG, APG, RPG, PER
- Career success: linguistic features → achievement score
- Era-specific formulas: what works in each era
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

from core.models import db, NBAPlayer, NBAPlayerAnalysis

logger = logging.getLogger(__name__)


class NBAStatisticalAnalyzer:
    """Comprehensive statistical analysis for NBA player name prediction."""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.position_model = None
        self.performance_model = None
        self.achievement_model = None
    
    def get_comprehensive_dataset(self) -> pd.DataFrame:
        """Load all players with complete data.
        
        Returns:
            DataFrame with player and analysis data
        """
        query = db.session.query(NBAPlayer, NBAPlayerAnalysis).join(
            NBAPlayerAnalysis,
            NBAPlayer.id == NBAPlayerAnalysis.player_id
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
                    'position': player.position,
                    'position_group': player.position_group,
                    'primary_position': player.primary_position,
                    'years_active': player.years_active or 0,
                    'is_active': player.is_active,
                    
                    # Outcomes (dependent variables)
                    'ppg': player.ppg or 0,
                    'apg': player.apg or 0,
                    'rpg': player.rpg or 0,
                    'per': player.per or 0,
                    'performance_score': player.performance_score or 0,
                    'career_achievement_score': player.career_achievement_score or 0,
                    'longevity_score': player.longevity_score or 0,
                    'overall_success_score': player.overall_success_score or 0,
                    'all_star_count': player.all_star_count or 0,
                    'hof_inducted': player.hof_inducted or False,
                    
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
                    'last_name_syllables': analysis.last_name_syllables or 0,
                    'last_name_length': analysis.last_name_length or 0,
                    
                    # Contextual
                    'temporal_cohort': analysis.temporal_cohort,
                    'position_cluster': analysis.position_cluster,
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
            'strength_association_score', 'rhythm_score', 'consonant_cluster_complexity',
            'alliteration_score', 'first_name_syllables', 'last_name_syllables'
        ]
        
        # Prepare data
        df_clean = df[feature_cols + ['position_group', 'primary_position']].dropna()
        
        if len(df_clean) < 50:
            logger.warning("Insufficient data for position modeling")
            return results
        
        X = df_clean[feature_cols]
        
        # 1. Position Group prediction (Guard/Forward/Center)
        y_group = df_clean['position_group']
        if len(y_group.unique()) >= 2:
            results['position_group_model'] = self._train_classification_model(
                X, y_group, 'Position Group', feature_cols
            )
        
        # 2. Primary Position prediction (PG/SG/SF/PF/C)
        y_primary = df_clean['primary_position']
        if len(y_primary.unique()) >= 3:
            results['primary_position_model'] = self._train_classification_model(
                X, y_primary, 'Primary Position', feature_cols
            )
        
        # 3. Position-specific profiles
        results['position_profiles'] = self._analyze_position_profiles(df, feature_cols)
        
        # 4. Feature correlations with position
        results['correlations'] = self._analyze_position_correlations(df, feature_cols)
        
        return results
    
    def analyze_performance_predictors(self, df: pd.DataFrame) -> Dict:
        """Analyze which linguistic features predict performance.
        
        Args:
            df: DataFrame with player data
            
        Returns:
            Performance prediction analysis results
        """
        logger.info("Analyzing performance predictors...")
        
        results = {
            'ppg_model': {},
            'apg_model': {},
            'rpg_model': {},
            'per_model': {},
            'performance_score_model': {},
            'feature_importance': {},
        }
        
        # Define feature columns
        feature_cols = [
            'syllable_count', 'character_length', 'word_count',
            'memorability_score', 'pronounceability_score', 'uniqueness_score',
            'power_connotation_score', 'harshness_score', 'softness_score',
            'phonetic_score', 'vowel_ratio', 'speed_association_score',
            'strength_association_score', 'rhythm_score', 'consonant_cluster_complexity',
            'alliteration_score'
        ]
        
        # 1. PPG prediction
        df_ppg = df[feature_cols + ['ppg']].dropna()
        if len(df_ppg) >= 50:
            X_ppg = df_ppg[feature_cols]
            y_ppg = df_ppg['ppg']
            results['ppg_model'] = self._train_regression_model(
                X_ppg, y_ppg, 'PPG', feature_cols
            )
        
        # 2. APG prediction
        df_apg = df[feature_cols + ['apg']].dropna()
        if len(df_apg) >= 50:
            X_apg = df_apg[feature_cols]
            y_apg = df_apg['apg']
            results['apg_model'] = self._train_regression_model(
                X_apg, y_apg, 'APG', feature_cols
            )
        
        # 3. RPG prediction
        df_rpg = df[feature_cols + ['rpg']].dropna()
        if len(df_rpg) >= 50:
            X_rpg = df_rpg[feature_cols]
            y_rpg = df_rpg['rpg']
            results['rpg_model'] = self._train_regression_model(
                X_rpg, y_rpg, 'RPG', feature_cols
            )
        
        # 4. PER prediction
        df_per = df[feature_cols + ['per']].dropna()
        if len(df_per) >= 50:
            X_per = df_per[feature_cols]
            y_per = df_per['per']
            results['per_model'] = self._train_regression_model(
                X_per, y_per, 'PER', feature_cols
            )
        
        # 5. Overall performance score prediction
        df_perf = df[feature_cols + ['performance_score']].dropna()
        if len(df_perf) >= 50:
            X_perf = df_perf[feature_cols]
            y_perf = df_perf['performance_score']
            results['performance_score_model'] = self._train_regression_model(
                X_perf, y_perf, 'Performance Score', feature_cols
            )
        
        # 6. Combined feature importance
        results['feature_importance'] = self._analyze_performance_feature_importance(results, feature_cols)
        
        return results
    
    def analyze_career_success_predictors(self, df: pd.DataFrame) -> Dict:
        """Analyze which linguistic features predict career success.
        
        Args:
            df: DataFrame with player data
            
        Returns:
            Career success prediction analysis results
        """
        logger.info("Analyzing career success predictors...")
        
        results = {
            'achievement_score_model': {},
            'longevity_model': {},
            'all_star_model': {},
            'hof_model': {},
            'overall_success_model': {},
            'feature_importance': {},
        }
        
        # Define feature columns
        feature_cols = [
            'syllable_count', 'character_length', 'word_count',
            'memorability_score', 'pronounceability_score', 'uniqueness_score',
            'power_connotation_score', 'harshness_score', 'softness_score',
            'phonetic_score', 'vowel_ratio', 'speed_association_score',
            'strength_association_score', 'rhythm_score', 'alliteration_score'
        ]
        
        # 1. Achievement score prediction
        df_ach = df[feature_cols + ['career_achievement_score']].dropna()
        if len(df_ach) >= 50:
            X_ach = df_ach[feature_cols]
            y_ach = df_ach['career_achievement_score']
            results['achievement_score_model'] = self._train_regression_model(
                X_ach, y_ach, 'Achievement Score', feature_cols
            )
        
        # 2. Longevity prediction
        df_long = df[feature_cols + ['longevity_score']].dropna()
        if len(df_long) >= 50:
            X_long = df_long[feature_cols]
            y_long = df_long['longevity_score']
            results['longevity_model'] = self._train_regression_model(
                X_long, y_long, 'Longevity Score', feature_cols
            )
        
        # 3. All-Star classification (0+ vs 3+)
        df['is_all_star'] = df['all_star_count'] >= 3
        df_as = df[feature_cols + ['is_all_star']].dropna()
        if len(df_as) >= 50 and df_as['is_all_star'].sum() > 10:
            X_as = df_as[feature_cols]
            y_as = df_as['is_all_star'].astype(int)
            results['all_star_model'] = self._train_classification_model(
                X_as, y_as, 'All-Star Status', feature_cols
            )
        
        # 4. Hall of Fame prediction
        df_hof = df[feature_cols + ['hof_inducted']].dropna()
        if len(df_hof) >= 50 and df_hof['hof_inducted'].sum() > 5:
            X_hof = df_hof[feature_cols]
            y_hof = df_hof['hof_inducted'].astype(int)
            results['hof_model'] = self._train_classification_model(
                X_hof, y_hof, 'Hall of Fame', feature_cols
            )
        
        # 5. Overall success score
        df_success = df[feature_cols + ['overall_success_score']].dropna()
        if len(df_success) >= 50:
            X_success = df_success[feature_cols]
            y_success = df_success['overall_success_score']
            results['overall_success_model'] = self._train_regression_model(
                X_success, y_success, 'Overall Success', feature_cols
            )
        
        # 6. Feature importance
        results['feature_importance'] = self._analyze_success_feature_importance(results, feature_cols)
        
        return results
    
    def analyze_era_formulas(self, df: pd.DataFrame) -> Dict:
        """Analyze era-specific success formulas.
        
        Args:
            df: DataFrame with all data
            
        Returns:
            Era-specific formulas
        """
        logger.info("Analyzing era-specific formulas...")
        
        formulas = {}
        
        feature_cols = [
            'syllable_count', 'character_length', 'memorability_score',
            'power_connotation_score', 'harshness_score', 'speed_association_score'
        ]
        
        eras = [1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020]
        
        for era in eras:
            era_data = df[df['era'] == era]
            
            if len(era_data) < 20:
                continue
            
            # Correlations with success
            correlations = {}
            for feature in feature_cols:
                if feature in era_data.columns and 'overall_success_score' in era_data.columns:
                    valid_data = era_data[[feature, 'overall_success_score']].dropna()
                    
                    if len(valid_data) < 10:
                        continue
                    
                    corr, p_value = stats.pearsonr(
                        valid_data[feature],
                        valid_data['overall_success_score']
                    )
                    
                    if not np.isnan(corr):
                        correlations[feature] = {
                            'correlation': float(corr),
                            'p_value': float(p_value),
                            'significant': p_value < 0.05
                        }
            
            # Top correlates
            sig_correlations = {k: v for k, v in correlations.items() if v.get('significant', False)}
            top_correlates = sorted(sig_correlations.items(),
                                   key=lambda x: abs(x[1]['correlation']),
                                   reverse=True)[:5]
            
            formulas[f"{era}s"] = {
                'sample_size': len(era_data),
                'avg_success': float(era_data['overall_success_score'].mean()),
                'success_formula': [
                    {
                        'feature': f,
                        'correlation': float(c['correlation']),
                        'direction': 'positive' if c['correlation'] > 0 else 'negative'
                    }
                    for f, c in top_correlates
                ] if top_correlates else [],
                'era_profile': {
                    feature: float(era_data[feature].mean())
                    for feature in feature_cols
                    if feature in era_data.columns
                }
            }
        
        return formulas
    
    def _train_regression_model(self, X: pd.DataFrame, y: pd.Series, 
                                 target_name: str, feature_names: List[str]) -> Dict:
        """Train Random Forest regression model.
        
        Args:
            X: Feature matrix
            y: Target variable
            target_name: Name of target (for logging)
            feature_names: List of feature names
            
        Returns:
            Model results
        """
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train model
        model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        r2 = r2_score(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        # Cross-validation
        cv_scores = cross_val_score(model, X, y, cv=5, scoring='r2')
        
        # Feature importance
        feature_importance = dict(zip(feature_names, model.feature_importances_))
        top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'target': target_name,
            'r2_score': float(r2),
            'rmse': float(rmse),
            'cv_mean': float(cv_scores.mean()),
            'cv_std': float(cv_scores.std()),
            'sample_size': len(X),
            'top_features': [{'feature': f, 'importance': float(imp)} for f, imp in top_features],
            'all_feature_importance': {k: float(v) for k, v in feature_importance.items()}
        }
    
    def _train_classification_model(self, X: pd.DataFrame, y: pd.Series,
                                     target_name: str, feature_names: List[str]) -> Dict:
        """Train Random Forest classification model.
        
        Args:
            X: Feature matrix
            y: Target variable
            target_name: Name of target
            feature_names: List of feature names
            
        Returns:
            Model results
        """
        # Handle string labels
        if y.dtype == 'object':
            le = LabelEncoder()
            y_encoded = le.fit_transform(y)
            class_names = list(le.classes_)
        else:
            y_encoded = y
            class_names = list(y.unique())
        
        # Split data
        try:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
            )
        except:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y_encoded, test_size=0.2, random_state=42
            )
        
        # Train model
        model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
        model.fit(X_train, y_train)
        
        # Evaluate
        accuracy = model.score(X_test, y_test)
        
        # Cross-validation
        cv_scores = cross_val_score(model, X, y_encoded, cv=5, scoring='accuracy')
        
        # Feature importance
        feature_importance = dict(zip(feature_names, model.feature_importances_))
        top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'target': target_name,
            'accuracy': float(accuracy),
            'cv_mean': float(cv_scores.mean()),
            'cv_std': float(cv_scores.std()),
            'sample_size': len(X),
            'classes': class_names,
            'top_features': [{'feature': f, 'importance': float(imp)} for f, imp in top_features],
            'all_feature_importance': {k: float(v) for k, v in feature_importance.items()}
        }
    
    def _analyze_position_profiles(self, df: pd.DataFrame, feature_cols: List[str]) -> Dict:
        """Analyze linguistic profiles by position.
        
        Args:
            df: DataFrame with all data
            feature_cols: Feature columns
            
        Returns:
            Position-specific profiles
        """
        profiles = {}
        
        positions = df['position_group'].unique()
        
        for position in positions:
            pos_data = df[df['position_group'] == position]
            
            if len(pos_data) < 10:
                continue
            
            profile = {
                'sample_size': len(pos_data),
                'avg_performance': float(pos_data['performance_score'].mean()),
                'linguistic_profile': {
                    feature: float(pos_data[feature].mean())
                    for feature in feature_cols
                    if feature in pos_data.columns
                },
                'top_players': pos_data.nlargest(5, 'overall_success_score')['name'].tolist()
            }
            
            profiles[position] = profile
        
        return profiles
    
    def _analyze_position_correlations(self, df: pd.DataFrame, feature_cols: List[str]) -> Dict:
        """Analyze correlations between features and position groups.
        
        Args:
            df: DataFrame with all data
            feature_cols: Feature columns
            
        Returns:
            Correlation analysis
        """
        correlations = {}
        
        # One-hot encode position groups
        position_dummies = pd.get_dummies(df['position_group'], prefix='pos')
        
        for col in position_dummies.columns:
            correlations[col] = {}
            
            for feature in feature_cols:
                if feature in df.columns:
                    valid_data = df[[feature]].join(position_dummies[col]).dropna()
                    
                    if len(valid_data) > 10:
                        corr, p_value = stats.pearsonr(valid_data[feature], valid_data[col])
                        
                        if not np.isnan(corr):
                            correlations[col][feature] = {
                                'correlation': float(corr),
                                'p_value': float(p_value),
                                'significant': p_value < 0.05
                            }
        
        return correlations
    
    def _analyze_performance_feature_importance(self, results: Dict, feature_cols: List[str]) -> Dict:
        """Analyze combined feature importance across performance models.
        
        Args:
            results: Performance model results
            feature_cols: List of features
            
        Returns:
            Combined importance rankings
        """
        combined_importance = {}
        
        models = ['ppg_model', 'apg_model', 'rpg_model', 'per_model', 'performance_score_model']
        
        for feature in feature_cols:
            importances = []
            
            for model_name in models:
                if model_name in results and results[model_name]:
                    imp = results[model_name].get('all_feature_importance', {}).get(feature, 0)
                    importances.append(imp)
            
            if importances:
                combined_importance[feature] = {
                    'average_importance': float(np.mean(importances)),
                    'max_importance': float(np.max(importances)),
                    'std_importance': float(np.std(importances))
                }
        
        # Rank by average importance
        ranked = sorted(combined_importance.items(), 
                       key=lambda x: x[1]['average_importance'],
                       reverse=True)
        
        return {
            'ranked_features': [
                {'feature': f, **stats} for f, stats in ranked
            ],
            'top_5_universal': [f for f, _ in ranked[:5]]
        }
    
    def _analyze_success_feature_importance(self, results: Dict, feature_cols: List[str]) -> Dict:
        """Analyze combined feature importance across success models.
        
        Args:
            results: Success model results
            feature_cols: List of features
            
        Returns:
            Combined importance rankings
        """
        combined_importance = {}
        
        models = ['achievement_score_model', 'longevity_model', 'overall_success_model']
        
        for feature in feature_cols:
            importances = []
            
            for model_name in models:
                if model_name in results and results[model_name]:
                    imp = results[model_name].get('all_feature_importance', {}).get(feature, 0)
                    importances.append(imp)
            
            if importances:
                combined_importance[feature] = {
                    'average_importance': float(np.mean(importances)),
                    'max_importance': float(np.max(importances))
                }
        
        # Rank by average importance
        ranked = sorted(combined_importance.items(), 
                       key=lambda x: x[1]['average_importance'],
                       reverse=True)
        
        return {
            'ranked_features': [
                {'feature': f, **stats} for f, stats in ranked
            ],
            'top_5_universal': [f for f, _ in ranked[:5]]
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    analyzer = NBAStatisticalAnalyzer()
    df = analyzer.get_comprehensive_dataset()
    
    if len(df) > 50:
        print("\n" + "="*60)
        print("NBA PLAYER NAME ANALYSIS")
        print("="*60)
        
        # Position prediction
        position_results = analyzer.analyze_position_predictors(df)
        print("\n--- Position Prediction ---")
        if 'position_group_model' in position_results and position_results['position_group_model']:
            print(f"Accuracy: {position_results['position_group_model'].get('accuracy', 0):.3f}")
        
        # Performance prediction
        performance_results = analyzer.analyze_performance_predictors(df)
        print("\n--- Performance Prediction ---")
        if 'performance_score_model' in performance_results and performance_results['performance_score_model']:
            print(f"R² Score: {performance_results['performance_score_model'].get('r2_score', 0):.3f}")
        
        # Career success
        success_results = analyzer.analyze_career_success_predictors(df)
        print("\n--- Career Success Prediction ---")
        if 'overall_success_model' in success_results and success_results['overall_success_model']:
            print(f"R² Score: {success_results['overall_success_model'].get('r2_score', 0):.3f}")
        
        # Era formulas
        era_results = analyzer.analyze_era_formulas(df)
        print("\n--- Era-Specific Formulas ---")
        for era, data in era_results.items():
            print(f"{era}: {data['sample_size']} players")
    else:
        print("Insufficient data. Run nba_collector.py to collect players first.")

