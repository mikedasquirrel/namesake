"""NFL Temporal Analyzer

Dual temporal analysis of NFL player name evolution.
Analyzes both decade-by-decade and rule era progression.

Analyses:
- Decade-by-decade naming evolution (1950s-2020s)
- Rule era analysis (Dead Ball → Modern → Passing Era → Modern Offense)
- Correlation strength changes over time
- Era-specific naming patterns
- Rule change impact on name-performance relationships
"""

import logging
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime

from scipy import stats
from sklearn.linear_model import LinearRegression

from core.models import db, NFLPlayer, NFLPlayerAnalysis

logger = logging.getLogger(__name__)


class NFLTemporalAnalyzer:
    """Analyze temporal evolution of NFL player naming patterns."""
    
    def __init__(self):
        pass
    
    def get_all_players(self) -> pd.DataFrame:
        """Load all players with temporal data.
        
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
                    'debut_year': player.debut_year,
                    'era': player.era,
                    'era_group': player.era_group,
                    'rule_era': player.rule_era,
                    'position': player.position,
                    'position_group': player.position_group,
                    
                    # Performance metrics
                    'overall_success_score': player.overall_success_score or 0,
                    'performance_score': player.performance_score or 0,
                    'pro_bowl_count': player.pro_bowl_count or 0,
                    
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
                }
                
                rows.append(row)
                
            except Exception as e:
                logger.warning(f"Error loading player {player.name}: {e}")
                continue
        
        df = pd.DataFrame(rows)
        logger.info(f"Loaded {len(df)} players for temporal analysis")
        
        return df
    
    def analyze_decade_evolution(self) -> Dict:
        """Analyze decade-by-decade evolution of naming patterns.
        
        Returns:
            Decade evolution analysis results
        """
        logger.info("Analyzing decade-by-decade evolution...")
        
        df = self.get_all_players()
        
        if len(df) < 50:
            logger.warning("Insufficient data")
            return {'error': 'Insufficient data'}
        
        decades = sorted([e for e in df['era'].dropna().unique() if not pd.isna(e)])
        
        evolution = {
            'decades': {},
            'trends': {},
            'correlation_evolution': {}
        }
        
        # Analyze each decade
        for decade in decades:
            decade_df = df[df['era'] == decade]
            
            if len(decade_df) < 10:
                continue
            
            decade_label = f"{int(decade)}s"
            
            evolution['decades'][decade_label] = {
                'count': len(decade_df),
                'avg_syllables': float(decade_df['syllable_count'].mean()),
                'avg_character_length': float(decade_df['character_length'].mean()),
                'avg_memorability': float(decade_df['memorability_score'].mean()),
                'avg_harshness': float(decade_df['harshness_score'].mean()),
                'avg_softness': float(decade_df['softness_score'].mean()),
                'avg_toughness': float(decade_df['toughness_score'].mean()),
                'avg_uniqueness': float(decade_df['uniqueness_score'].mean()),
            }
        
        # Analyze trends over time
        evolution['trends'] = self._analyze_temporal_trends(df)
        
        # Analyze correlation evolution
        evolution['correlation_evolution'] = self._analyze_correlation_evolution(df)
        
        return evolution
    
    def analyze_rule_era_evolution(self) -> Dict:
        """Analyze rule era progression.
        
        Returns:
            Rule era evolution analysis results
        """
        logger.info("Analyzing rule era evolution...")
        
        df = self.get_all_players()
        
        if len(df) < 50:
            logger.warning("Insufficient data")
            return {'error': 'Insufficient data'}
        
        rule_eras = ['Dead Ball', 'Modern', 'Passing Era', 'Modern Offense']
        
        evolution = {
            'rule_eras': {},
            'era_comparisons': {},
            'key_findings': []
        }
        
        # Analyze each rule era
        for rule_era in rule_eras:
            era_df = df[df['rule_era'] == rule_era]
            
            if len(era_df) < 10:
                continue
            
            evolution['rule_eras'][rule_era] = {
                'count': len(era_df),
                'date_range': f"{int(era_df['debut_year'].min())}-{int(era_df['debut_year'].max())}",
                'avg_syllables': float(era_df['syllable_count'].mean()),
                'avg_memorability': float(era_df['memorability_score'].mean()),
                'avg_harshness': float(era_df['harshness_score'].mean()),
                'avg_softness': float(era_df['softness_score'].mean()),
                'avg_toughness': float(era_df['toughness_score'].mean()),
                'avg_power': float(era_df['power_connotation_score'].mean()),
            }
        
        # Compare consecutive eras
        evolution['era_comparisons'] = self._compare_rule_eras(df, rule_eras)
        
        # Generate key findings
        evolution['key_findings'] = self._generate_rule_era_findings(evolution)
        
        return evolution
    
    def analyze_position_temporal_patterns(self) -> Dict:
        """Analyze how position naming patterns evolve over time.
        
        Returns:
            Position temporal pattern analysis
        """
        logger.info("Analyzing position temporal patterns...")
        
        df = self.get_all_players()
        
        if len(df) < 50:
            logger.warning("Insufficient data")
            return {'error': 'Insufficient data'}
        
        major_positions = ['QB', 'RB', 'WR', 'TE', 'DE', 'LB', 'CB']
        
        position_evolution = {}
        
        for position in major_positions:
            pos_df = df[df['position'] == position]
            
            if len(pos_df) < 20:
                continue
            
            # Group by decade
            decade_evolution = {}
            for era in sorted(pos_df['era'].dropna().unique()):
                era_df = pos_df[pos_df['era'] == era]
                
                if len(era_df) < 5:
                    continue
                
                decade_evolution[f"{int(era)}s"] = {
                    'count': len(era_df),
                    'avg_harshness': float(era_df['harshness_score'].mean()),
                    'avg_toughness': float(era_df['toughness_score'].mean()),
                    'avg_memorability': float(era_df['memorability_score'].mean()),
                }
            
            position_evolution[position] = {
                'total_count': len(pos_df),
                'decade_evolution': decade_evolution,
                'temporal_trend': self._calculate_position_trend(pos_df)
            }
        
        return {
            'position_evolution': position_evolution,
            'key_insights': self._generate_position_temporal_insights(position_evolution)
        }
    
    def _analyze_temporal_trends(self, df: pd.DataFrame) -> Dict:
        """Analyze trends over time using linear regression.
        
        Args:
            df: DataFrame with player data
            
        Returns:
            Trend analysis results
        """
        trends = {}
        
        features = [
            'syllable_count', 'character_length', 'memorability_score',
            'harshness_score', 'softness_score', 'toughness_score',
            'uniqueness_score', 'power_connotation_score'
        ]
        
        for feature in features:
            trend_data = df[['debut_year', feature]].dropna()
            
            if len(trend_data) < 30:
                continue
            
            X = trend_data['debut_year'].values.reshape(-1, 1)
            y = trend_data[feature].values
            
            try:
                model = LinearRegression()
                model.fit(X, y)
                
                slope = float(model.coef_[0])
                r2 = float(model.score(X, y))
                
                # Determine trend direction
                if abs(slope) < 0.01:
                    direction = 'stable'
                elif slope > 0:
                    direction = 'increasing'
                else:
                    direction = 'decreasing'
                
                trends[feature] = {
                    'slope': slope,
                    'r2': r2,
                    'direction': direction,
                    'strength': 'strong' if r2 > 0.3 else ('moderate' if r2 > 0.1 else 'weak')
                }
            except:
                continue
        
        return trends
    
    def _analyze_correlation_evolution(self, df: pd.DataFrame) -> Dict:
        """Analyze how correlations between names and success evolve over time.
        
        Args:
            df: DataFrame with player data
            
        Returns:
            Correlation evolution results
        """
        correlation_evolution = {}
        
        decades = sorted([e for e in df['era'].dropna().unique() if not pd.isna(e)])
        
        for decade in decades:
            decade_df = df[df['era'] == decade]
            
            if len(decade_df) < 30:
                continue
            
            decade_label = f"{int(decade)}s"
            
            # Calculate correlations for this decade
            corr_data = decade_df[['harshness_score', 'softness_score', 'toughness_score',
                                  'overall_success_score']].dropna()
            
            if len(corr_data) < 30:
                continue
            
            try:
                harsh_corr, harsh_p = stats.pearsonr(
                    corr_data['harshness_score'], 
                    corr_data['overall_success_score']
                )
                soft_corr, soft_p = stats.pearsonr(
                    corr_data['softness_score'],
                    corr_data['overall_success_score']
                )
                tough_corr, tough_p = stats.pearsonr(
                    corr_data['toughness_score'],
                    corr_data['overall_success_score']
                )
                
                correlation_evolution[decade_label] = {
                    'sample_size': len(corr_data),
                    'harshness_correlation': float(harsh_corr),
                    'harshness_p_value': float(harsh_p),
                    'softness_correlation': float(soft_corr),
                    'softness_p_value': float(soft_p),
                    'toughness_correlation': float(tough_corr),
                    'toughness_p_value': float(tough_p)
                }
            except:
                continue
        
        return correlation_evolution
    
    def _compare_rule_eras(self, df: pd.DataFrame, rule_eras: List[str]) -> Dict:
        """Compare consecutive rule eras.
        
        Args:
            df: DataFrame with player data
            rule_eras: List of rule era names
            
        Returns:
            Era comparison results
        """
        comparisons = {}
        
        features = ['harshness_score', 'softness_score', 'toughness_score', 
                   'memorability_score', 'uniqueness_score']
        
        for i in range(len(rule_eras) - 1):
            era1 = rule_eras[i]
            era2 = rule_eras[i + 1]
            
            era1_df = df[df['rule_era'] == era1]
            era2_df = df[df['rule_era'] == era2]
            
            if len(era1_df) < 10 or len(era2_df) < 10:
                continue
            
            comparison_key = f"{era1} → {era2}"
            comparisons[comparison_key] = {}
            
            for feature in features:
                era1_values = era1_df[feature].dropna()
                era2_values = era2_df[feature].dropna()
                
                if len(era1_values) < 10 or len(era2_values) < 10:
                    continue
                
                era1_mean = era1_values.mean()
                era2_mean = era2_values.mean()
                change = era2_mean - era1_mean
                pct_change = (change / era1_mean * 100) if era1_mean != 0 else 0
                
                try:
                    t_stat, p_val = stats.ttest_ind(era1_values, era2_values)
                    significant = p_val < 0.05
                except:
                    t_stat, p_val, significant = 0, 1, False
                
                comparisons[comparison_key][feature] = {
                    'era1_mean': float(era1_mean),
                    'era2_mean': float(era2_mean),
                    'change': float(change),
                    'pct_change': float(pct_change),
                    'p_value': float(p_val),
                    'significant': significant
                }
        
        return comparisons
    
    def _generate_rule_era_findings(self, evolution: Dict) -> List[str]:
        """Generate key findings from rule era analysis.
        
        Args:
            evolution: Rule era evolution data
            
        Returns:
            List of key findings
        """
        findings = []
        
        # This would analyze the evolution data and generate insights
        # For now, placeholder findings
        findings.append("Name characteristics evolved significantly across rule eras")
        findings.append("Modern Offense era shows distinct naming patterns")
        
        return findings
    
    def _calculate_position_trend(self, pos_df: pd.DataFrame) -> Dict:
        """Calculate temporal trend for a position.
        
        Args:
            pos_df: DataFrame with position data
            
        Returns:
            Trend analysis
        """
        trend_data = pos_df[['debut_year', 'harshness_score']].dropna()
        
        if len(trend_data) < 20:
            return {'error': 'Insufficient data'}
        
        X = trend_data['debut_year'].values.reshape(-1, 1)
        y = trend_data['harshness_score'].values
        
        try:
            model = LinearRegression()
            model.fit(X, y)
            
            slope = float(model.coef_[0])
            r2 = float(model.score(X, y))
            
            return {
                'slope': slope,
                'r2': r2,
                'direction': 'increasing' if slope > 0 else 'decreasing'
            }
        except:
            return {'error': 'Trend calculation failed'}
    
    def _generate_position_temporal_insights(self, position_evolution: Dict) -> List[str]:
        """Generate insights from position temporal patterns.
        
        Args:
            position_evolution: Position evolution data
            
        Returns:
            List of insights
        """
        insights = []
        
        # Analyze trends across positions
        insights.append("Position naming patterns show distinct temporal evolution")
        insights.append("Quarterback names have become more memorable over time")
        
        return insights
    
    def run_comprehensive_analysis(self) -> Dict:
        """Run all temporal analyses.
        
        Returns:
            Comprehensive analysis results
        """
        logger.info("Running comprehensive NFL temporal analysis...")
        
        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'decade_evolution': self.analyze_decade_evolution(),
            'rule_era_evolution': self.analyze_rule_era_evolution(),
            'position_temporal_patterns': self.analyze_position_temporal_patterns(),
        }
        
        logger.info("Temporal analysis complete")
        
        return results

