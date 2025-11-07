"""NFL Performance Analyzer

Position-specific deep dive analysis for NFL players.
Analyzes correlations between name linguistics and performance metrics.

Position-Specific Analyses:
- QB: Completion %, Passer Rating, TD/INT Ratio, YPA
- RB: Yards Per Carry, Rushing Efficiency, Fumbles
- WR/TE: Catch Rate, Yards Per Reception, YAC
- Defensive: Tackle Efficiency, Turnover Generation, Sacks
- Special Teams: Field Goal %, Punting Average

Elite vs Poor Performer Comparisons
Predictive Models for Position-Specific Metrics
"""

import logging
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
from scipy import stats

from core.models import db, NFLPlayer, NFLPlayerAnalysis

logger = logging.getLogger(__name__)


class NFLPerformanceAnalyzer:
    """Position-specific performance analysis for NFL players."""
    
    def __init__(self):
        self.scaler = StandardScaler()
    
    def get_position_dataset(self, positions: List[str]) -> pd.DataFrame:
        """Load players for specific positions with complete data.
        
        Args:
            positions: List of position codes (e.g., ['QB', 'RB'])
            
        Returns:
            DataFrame with player and analysis data
        """
        query = db.session.query(NFLPlayer, NFLPlayerAnalysis).join(
            NFLPlayerAnalysis,
            NFLPlayer.id == NFLPlayerAnalysis.player_id
        ).filter(NFLPlayer.position.in_(positions))
        
        rows = []
        for player, analysis in query.all():
            try:
                row = self._extract_player_data(player, analysis)
                rows.append(row)
            except Exception as e:
                logger.warning(f"Error loading player {player.name}: {e}")
                continue
        
        df = pd.DataFrame(rows)
        logger.info(f"Loaded {len(df)} {'/'.join(positions)} players")
        
        return df
    
    def _extract_player_data(self, player: NFLPlayer, analysis: NFLPlayerAnalysis) -> Dict:
        """Extract player data into dictionary.
        
        Args:
            player: NFLPlayer object
            analysis: NFLPlayerAnalysis object
            
        Returns:
            Player data dictionary
        """
        return {
            'id': player.id,
            'name': player.name,
            'position': player.position,
            'position_group': player.position_group,
            'era': player.era,
            'rule_era': player.rule_era,
            'games_played': player.games_played or 0,
            
            # QB stats
            'completion_pct': player.completion_pct,
            'passer_rating': player.passer_rating,
            'td_int_ratio': player.td_int_ratio,
            'yards_per_attempt': player.yards_per_attempt,
            'passing_yards': player.passing_yards,
            'passing_tds': player.passing_tds,
            
            # RB stats
            'yards_per_carry': player.yards_per_carry,
            'rushing_yards': player.rushing_yards,
            'rushing_fumbles': player.rushing_fumbles,
            
            # Receiving stats
            'yards_per_reception': player.yards_per_reception,
            'catch_rate': player.catch_rate,
            'yards_after_catch': player.yards_after_catch,
            'receptions': player.receptions,
            'receiving_yards': player.receiving_yards,
            
            # Defensive stats
            'tackles': player.tackles,
            'sacks': player.sacks,
            'defensive_interceptions': player.defensive_interceptions,
            'forced_fumbles': player.forced_fumbles,
            
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
        }
    
    def analyze_qb_performance(self) -> Dict:
        """Comprehensive QB performance analysis.
        
        Returns:
            QB analysis results
        """
        logger.info("Analyzing QB performance correlations...")
        
        df = self.get_position_dataset(['QB'])
        
        if len(df) < 30:
            logger.warning("Insufficient QB data")
            return {'error': 'Insufficient data'}
        
        results = {
            'position': 'QB',
            'sample_size': len(df),
            'completion_pct_analysis': self._analyze_metric(
                df, 'completion_pct', 'Completion Percentage'
            ),
            'passer_rating_analysis': self._analyze_metric(
                df, 'passer_rating', 'Passer Rating'
            ),
            'td_int_ratio_analysis': self._analyze_metric(
                df, 'td_int_ratio', 'TD/INT Ratio'
            ),
            'yards_per_attempt_analysis': self._analyze_metric(
                df, 'yards_per_attempt', 'Yards Per Attempt'
            ),
            'elite_vs_poor': self._compare_elite_vs_poor_qbs(df),
            'era_analysis': self._analyze_by_era(df, 'passer_rating'),
            'rule_era_analysis': self._analyze_by_rule_era(df, 'passer_rating'),
        }
        
        return results
    
    def analyze_rb_performance(self) -> Dict:
        """Comprehensive RB performance analysis.
        
        Returns:
            RB analysis results
        """
        logger.info("Analyzing RB performance correlations...")
        
        df = self.get_position_dataset(['RB', 'FB'])
        
        if len(df) < 30:
            logger.warning("Insufficient RB data")
            return {'error': 'Insufficient data'}
        
        results = {
            'position': 'RB',
            'sample_size': len(df),
            'yards_per_carry_analysis': self._analyze_metric(
                df, 'yards_per_carry', 'Yards Per Carry'
            ),
            'rushing_yards_analysis': self._analyze_metric(
                df, 'rushing_yards', 'Rushing Yards'
            ),
            'fumbles_analysis': self._analyze_metric(
                df, 'rushing_fumbles', 'Fumbles', inverse=True
            ),
            'elite_vs_poor': self._compare_elite_vs_poor_rbs(df),
            'era_analysis': self._analyze_by_era(df, 'yards_per_carry'),
            'rule_era_analysis': self._analyze_by_rule_era(df, 'yards_per_carry'),
        }
        
        return results
    
    def analyze_wr_performance(self) -> Dict:
        """Comprehensive WR/TE performance analysis.
        
        Returns:
            WR/TE analysis results
        """
        logger.info("Analyzing WR/TE performance correlations...")
        
        df = self.get_position_dataset(['WR', 'TE'])
        
        if len(df) < 30:
            logger.warning("Insufficient WR/TE data")
            return {'error': 'Insufficient data'}
        
        results = {
            'position': 'WR/TE',
            'sample_size': len(df),
            'yards_per_reception_analysis': self._analyze_metric(
                df, 'yards_per_reception', 'Yards Per Reception'
            ),
            'catch_rate_analysis': self._analyze_metric(
                df, 'catch_rate', 'Catch Rate'
            ),
            'receiving_yards_analysis': self._analyze_metric(
                df, 'receiving_yards', 'Receiving Yards'
            ),
            'elite_vs_poor': self._compare_elite_vs_poor_wrs(df),
            'era_analysis': self._analyze_by_era(df, 'yards_per_reception'),
            'rule_era_analysis': self._analyze_by_rule_era(df, 'yards_per_reception'),
        }
        
        return results
    
    def analyze_defensive_performance(self) -> Dict:
        """Comprehensive defensive player performance analysis.
        
        Returns:
            Defensive analysis results
        """
        logger.info("Analyzing defensive performance correlations...")
        
        # Get all defensive positions
        defensive_positions = ['DE', 'DT', 'NT', 'OLB', 'ILB', 'MLB', 'LB', 'CB', 'S', 'FS', 'SS', 'DB']
        df = self.get_position_dataset(defensive_positions)
        
        if len(df) < 30:
            logger.warning("Insufficient defensive data")
            return {'error': 'Insufficient data'}
        
        results = {
            'position': 'Defensive',
            'sample_size': len(df),
            'tackles_analysis': self._analyze_metric(
                df, 'tackles', 'Tackles'
            ),
            'sacks_analysis': self._analyze_metric(
                df, 'sacks', 'Sacks'
            ),
            'interceptions_analysis': self._analyze_metric(
                df, 'defensive_interceptions', 'Interceptions'
            ),
            'elite_vs_poor': self._compare_elite_vs_poor_defensive(df),
            'era_analysis': self._analyze_by_era(df, 'tackles'),
            'rule_era_analysis': self._analyze_by_rule_era(df, 'tackles'),
        }
        
        return results
    
    def _analyze_metric(self, df: pd.DataFrame, metric: str, metric_name: str,
                       inverse: bool = False) -> Dict:
        """Analyze correlations between linguistic features and a performance metric.
        
        Args:
            df: DataFrame with player data
            metric: Metric column name
            metric_name: Human-readable metric name
            inverse: Whether lower is better (e.g., fumbles)
            
        Returns:
            Metric analysis results
        """
        feature_cols = [
            'syllable_count', 'character_length', 'memorability_score',
            'pronounceability_score', 'uniqueness_score', 'power_connotation_score',
            'harshness_score', 'softness_score', 'vowel_ratio',
            'speed_association_score', 'strength_association_score',
            'toughness_score', 'rhythm_score', 'consonant_cluster_complexity'
        ]
        
        metric_data = df[[metric] + feature_cols].dropna()
        
        if len(metric_data) < 30:
            return {'error': 'Insufficient data', 'sample_size': len(metric_data)}
        
        # Calculate correlations
        correlations = {}
        for feature in feature_cols:
            try:
                corr, pval = stats.pearsonr(metric_data[feature], metric_data[metric])
                correlations[feature] = {
                    'correlation': float(corr),
                    'p_value': float(pval),
                    'significant': pval < 0.05
                }
            except:
                continue
        
        # Get top correlations
        significant_corrs = {k: v for k, v in correlations.items() if v['significant']}
        top_corrs = sorted(significant_corrs.items(), 
                          key=lambda x: abs(x[1]['correlation']), 
                          reverse=True)[:5]
        
        # Build prediction model
        X = metric_data[feature_cols]
        y = metric_data[metric]
        
        try:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            model = RandomForestRegressor(
                n_estimators=100, max_depth=10, random_state=42
            )
            model.fit(X_train, y_train)
            
            test_score = model.score(X_test, y_test)
            y_pred = model.predict(X_test)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            
            # Feature importance
            importances = dict(zip(feature_cols, model.feature_importances_))
            top_features = sorted(importances.items(), key=lambda x: x[1], reverse=True)[:5]
            
            prediction_model = {
                'r2_score': float(test_score),
                'rmse': float(rmse),
                'top_features': dict(top_features)
            }
        except:
            prediction_model = {'error': 'Model training failed'}
        
        return {
            'metric_name': metric_name,
            'sample_size': len(metric_data),
            'mean': float(metric_data[metric].mean()),
            'median': float(metric_data[metric].median()),
            'std': float(metric_data[metric].std()),
            'correlations': correlations,
            'top_5_correlations': dict(top_corrs),
            'n_significant_correlations': len(significant_corrs),
            'prediction_model': prediction_model
        }
    
    def _compare_elite_vs_poor_qbs(self, df: pd.DataFrame) -> Dict:
        """Compare elite vs poor QB names.
        
        Args:
            df: DataFrame with QB data
            
        Returns:
            Comparison results
        """
        qb_rating_data = df[['passer_rating', 'syllable_count', 'character_length',
                             'harshness_score', 'softness_score', 'memorability_score',
                             'toughness_score', 'rhythm_score']].dropna()
        
        if len(qb_rating_data) < 50:
            return {'error': 'Insufficient data'}
        
        # Define elite and poor thresholds
        elite_threshold = qb_rating_data['passer_rating'].quantile(0.75)
        poor_threshold = qb_rating_data['passer_rating'].quantile(0.25)
        
        elite = qb_rating_data[qb_rating_data['passer_rating'] >= elite_threshold]
        poor = qb_rating_data[qb_rating_data['passer_rating'] <= poor_threshold]
        
        comparison = {
            'elite_threshold': float(elite_threshold),
            'poor_threshold': float(poor_threshold),
            'elite_count': len(elite),
            'poor_count': len(poor),
            'elite_avg_rating': float(elite['passer_rating'].mean()),
            'poor_avg_rating': float(poor['passer_rating'].mean()),
            'differences': {}
        }
        
        # Compare linguistic features
        features = ['syllable_count', 'character_length', 'harshness_score', 
                   'softness_score', 'memorability_score', 'toughness_score', 'rhythm_score']
        
        for feature in features:
            elite_mean = elite[feature].mean()
            poor_mean = poor[feature].mean()
            diff = elite_mean - poor_mean
            
            # Statistical test
            try:
                t_stat, p_val = stats.ttest_ind(elite[feature], poor[feature])
                significant = p_val < 0.05
            except:
                t_stat, p_val, significant = 0, 1, False
            
            comparison['differences'][feature] = {
                'elite_mean': float(elite_mean),
                'poor_mean': float(poor_mean),
                'difference': float(diff),
                'p_value': float(p_val),
                'significant': significant
            }
        
        return comparison
    
    def _compare_elite_vs_poor_rbs(self, df: pd.DataFrame) -> Dict:
        """Compare elite vs poor RB names."""
        ypc_data = df[['yards_per_carry', 'syllable_count', 'character_length',
                       'harshness_score', 'softness_score', 'speed_association_score',
                       'toughness_score', 'power_connotation_score']].dropna()
        
        if len(ypc_data) < 50:
            return {'error': 'Insufficient data'}
        
        elite_threshold = ypc_data['yards_per_carry'].quantile(0.75)
        poor_threshold = ypc_data['yards_per_carry'].quantile(0.25)
        
        elite = ypc_data[ypc_data['yards_per_carry'] >= elite_threshold]
        poor = ypc_data[ypc_data['yards_per_carry'] <= poor_threshold]
        
        comparison = {
            'elite_threshold': float(elite_threshold),
            'poor_threshold': float(poor_threshold),
            'elite_count': len(elite),
            'poor_count': len(poor),
            'elite_avg_ypc': float(elite['yards_per_carry'].mean()),
            'poor_avg_ypc': float(poor['yards_per_carry'].mean()),
            'differences': {}
        }
        
        features = ['syllable_count', 'character_length', 'harshness_score',
                   'softness_score', 'speed_association_score', 'toughness_score',
                   'power_connotation_score']
        
        for feature in features:
            elite_mean = elite[feature].mean()
            poor_mean = poor[feature].mean()
            diff = elite_mean - poor_mean
            
            try:
                t_stat, p_val = stats.ttest_ind(elite[feature], poor[feature])
                significant = p_val < 0.05
            except:
                t_stat, p_val, significant = 0, 1, False
            
            comparison['differences'][feature] = {
                'elite_mean': float(elite_mean),
                'poor_mean': float(poor_mean),
                'difference': float(diff),
                'p_value': float(p_val),
                'significant': significant
            }
        
        return comparison
    
    def _compare_elite_vs_poor_wrs(self, df: pd.DataFrame) -> Dict:
        """Compare elite vs poor WR/TE names."""
        ypr_data = df[['yards_per_reception', 'syllable_count', 'character_length',
                       'memorability_score', 'speed_association_score', 'softness_score',
                       'rhythm_score']].dropna()
        
        if len(ypr_data) < 50:
            return {'error': 'Insufficient data'}
        
        elite_threshold = ypr_data['yards_per_reception'].quantile(0.75)
        poor_threshold = ypr_data['yards_per_reception'].quantile(0.25)
        
        elite = ypr_data[ypr_data['yards_per_reception'] >= elite_threshold]
        poor = ypr_data[ypr_data['yards_per_reception'] <= poor_threshold]
        
        comparison = {
            'elite_threshold': float(elite_threshold),
            'poor_threshold': float(poor_threshold),
            'elite_count': len(elite),
            'poor_count': len(poor),
            'elite_avg_ypr': float(elite['yards_per_reception'].mean()),
            'poor_avg_ypr': float(poor['yards_per_reception'].mean()),
            'differences': {}
        }
        
        features = ['syllable_count', 'character_length', 'memorability_score',
                   'speed_association_score', 'softness_score', 'rhythm_score']
        
        for feature in features:
            elite_mean = elite[feature].mean()
            poor_mean = poor[feature].mean()
            diff = elite_mean - poor_mean
            
            try:
                t_stat, p_val = stats.ttest_ind(elite[feature], poor[feature])
                significant = p_val < 0.05
            except:
                t_stat, p_val, significant = 0, 1, False
            
            comparison['differences'][feature] = {
                'elite_mean': float(elite_mean),
                'poor_mean': float(poor_mean),
                'difference': float(diff),
                'p_value': float(p_val),
                'significant': significant
            }
        
        return comparison
    
    def _compare_elite_vs_poor_defensive(self, df: pd.DataFrame) -> Dict:
        """Compare elite vs poor defensive player names."""
        tackle_data = df[['tackles', 'syllable_count', 'character_length',
                          'harshness_score', 'toughness_score', 'power_connotation_score',
                          'strength_association_score']].dropna()
        
        if len(tackle_data) < 50:
            return {'error': 'Insufficient data'}
        
        elite_threshold = tackle_data['tackles'].quantile(0.75)
        poor_threshold = tackle_data['tackles'].quantile(0.25)
        
        elite = tackle_data[tackle_data['tackles'] >= elite_threshold]
        poor = tackle_data[tackle_data['tackles'] <= poor_threshold]
        
        comparison = {
            'elite_threshold': float(elite_threshold),
            'poor_threshold': float(poor_threshold),
            'elite_count': len(elite),
            'poor_count': len(poor),
            'elite_avg_tackles': float(elite['tackles'].mean()),
            'poor_avg_tackles': float(poor['tackles'].mean()),
            'differences': {}
        }
        
        features = ['syllable_count', 'character_length', 'harshness_score',
                   'toughness_score', 'power_connotation_score', 'strength_association_score']
        
        for feature in features:
            elite_mean = elite[feature].mean()
            poor_mean = poor[feature].mean()
            diff = elite_mean - poor_mean
            
            try:
                t_stat, p_val = stats.ttest_ind(elite[feature], poor[feature])
                significant = p_val < 0.05
            except:
                t_stat, p_val, significant = 0, 1, False
            
            comparison['differences'][feature] = {
                'elite_mean': float(elite_mean),
                'poor_mean': float(poor_mean),
                'difference': float(diff),
                'p_value': float(p_val),
                'significant': significant
            }
        
        return comparison
    
    def _analyze_by_era(self, df: pd.DataFrame, metric: str) -> Dict:
        """Analyze metric by decade era.
        
        Args:
            df: DataFrame with player data
            metric: Metric to analyze
            
        Returns:
            Era analysis results
        """
        era_data = df[['era', metric, 'harshness_score', 'softness_score']].dropna()
        
        if len(era_data) < 30:
            return {'error': 'Insufficient data'}
        
        era_results = {}
        
        for era in sorted(era_data['era'].unique()):
            era_df = era_data[era_data['era'] == era]
            
            if len(era_df) < 10:
                continue
            
            # Correlation between harshness and metric
            try:
                harsh_corr, harsh_p = stats.pearsonr(era_df['harshness_score'], era_df[metric])
                soft_corr, soft_p = stats.pearsonr(era_df['softness_score'], era_df[metric])
            except:
                harsh_corr, harsh_p, soft_corr, soft_p = 0, 1, 0, 1
            
            era_results[f"{int(era)}s"] = {
                'count': len(era_df),
                'avg_metric': float(era_df[metric].mean()),
                'harshness_correlation': float(harsh_corr),
                'harshness_p_value': float(harsh_p),
                'softness_correlation': float(soft_corr),
                'softness_p_value': float(soft_p)
            }
        
        return era_results
    
    def _analyze_by_rule_era(self, df: pd.DataFrame, metric: str) -> Dict:
        """Analyze metric by rule era.
        
        Args:
            df: DataFrame with player data
            metric: Metric to analyze
            
        Returns:
            Rule era analysis results
        """
        rule_era_data = df[['rule_era', metric, 'harshness_score', 'softness_score']].dropna()
        
        if len(rule_era_data) < 30:
            return {'error': 'Insufficient data'}
        
        rule_era_results = {}
        
        for rule_era in rule_era_data['rule_era'].unique():
            era_df = rule_era_data[rule_era_data['rule_era'] == rule_era]
            
            if len(era_df) < 10:
                continue
            
            try:
                harsh_corr, harsh_p = stats.pearsonr(era_df['harshness_score'], era_df[metric])
                soft_corr, soft_p = stats.pearsonr(era_df['softness_score'], era_df[metric])
            except:
                harsh_corr, harsh_p, soft_corr, soft_p = 0, 1, 0, 1
            
            rule_era_results[rule_era] = {
                'count': len(era_df),
                'avg_metric': float(era_df[metric].mean()),
                'harshness_correlation': float(harsh_corr),
                'harshness_p_value': float(harsh_p),
                'softness_correlation': float(soft_corr),
                'softness_p_value': float(soft_p)
            }
        
        return rule_era_results
    
    def run_comprehensive_analysis(self) -> Dict:
        """Run all performance analyses.
        
        Returns:
            Comprehensive analysis results
        """
        logger.info("Running comprehensive NFL performance analysis...")
        
        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'qb_analysis': self.analyze_qb_performance(),
            'rb_analysis': self.analyze_rb_performance(),
            'wr_analysis': self.analyze_wr_performance(),
            'defensive_analysis': self.analyze_defensive_performance(),
        }
        
        logger.info("Performance analysis complete")
        
        return results

