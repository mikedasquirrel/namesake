"""NBA Temporal Analyzer

Analyzes evolution of naming patterns across NBA eras.
Tracks how linguistic features change over time and correlate with league evolution.

Analysis:
- Syllable count trends (1950s → 2020s)
- Memorability evolution
- International player influx impact
- Era-specific naming conventions
- Correlation with league style changes
"""

import logging
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from scipy import stats

from core.models import db, NBAPlayer, NBAPlayerAnalysis

logger = logging.getLogger(__name__)


class NBATemporalAnalyzer:
    """Analyze temporal evolution of NBA player naming patterns."""
    
    def __init__(self):
        pass
    
    def get_era_dataset(self) -> pd.DataFrame:
        """Load players with era information.
        
        Returns:
            DataFrame with player and analysis data grouped by era
        """
        query = db.session.query(NBAPlayer, NBAPlayerAnalysis).join(
            NBAPlayerAnalysis,
            NBAPlayer.id == NBAPlayerAnalysis.player_id
        )
        
        rows = []
        for player, analysis in query.all():
            try:
                row = {
                    'name': player.name,
                    'debut_year': player.debut_year,
                    'era': player.era,
                    'era_group': player.era_group,
                    'country': player.country,
                    'performance_score': player.performance_score or 0,
                    'overall_success_score': player.overall_success_score or 0,
                    
                    # Linguistic features
                    'syllable_count': analysis.syllable_count or 0,
                    'character_length': analysis.character_length or 0,
                    'word_count': analysis.word_count or 0,
                    'memorability_score': analysis.memorability_score or 0,
                    'pronounceability_score': analysis.pronounceability_score or 0,
                    'uniqueness_score': analysis.uniqueness_score or 0,
                    'power_connotation_score': analysis.power_connotation_score or 0,
                    'harshness_score': analysis.harshness_score or 0,
                    'softness_score': analysis.softness_score or 0,
                    'speed_association_score': analysis.speed_association_score or 50,
                    'strength_association_score': analysis.strength_association_score or 50,
                    'rhythm_score': analysis.rhythm_score or 50,
                    'alliteration_score': analysis.alliteration_score or 0,
                    'international_name_score': analysis.international_name_score or 0,
                }
                
                rows.append(row)
                
            except Exception as e:
                logger.warning(f"Error loading player {player.name}: {e}")
                continue
        
        df = pd.DataFrame(rows)
        logger.info(f"Loaded {len(df)} players for temporal analysis")
        
        return df
    
    def analyze_temporal_evolution(self, df: pd.DataFrame) -> Dict:
        """Analyze how naming patterns evolved across eras.
        
        Args:
            df: DataFrame with player data
            
        Returns:
            Temporal evolution analysis
        """
        logger.info("Analyzing temporal evolution...")
        
        results = {
            'era_statistics': {},
            'temporal_trends': {},
            'international_impact': {},
            'era_comparisons': {},
            'trend_analysis': {}
        }
        
        # Define eras
        eras = sorted(df['era'].unique())
        
        # 1. Statistics by era
        for era in eras:
            era_data = df[df['era'] == era]
            
            if len(era_data) < 5:
                continue
            
            era_stats = {
                'sample_size': len(era_data),
                'era_name': f"{era}s",
                
                # Linguistic averages
                'avg_syllables': float(era_data['syllable_count'].mean()),
                'avg_character_length': float(era_data['character_length'].mean()),
                'avg_word_count': float(era_data['word_count'].mean()),
                'avg_memorability': float(era_data['memorability_score'].mean()),
                'avg_uniqueness': float(era_data['uniqueness_score'].mean()),
                'avg_harshness': float(era_data['harshness_score'].mean()),
                'avg_softness': float(era_data['softness_score'].mean()),
                'avg_alliteration': float(era_data['alliteration_score'].mean()),
                
                # Success metrics
                'avg_performance': float(era_data['performance_score'].mean()),
                'avg_success': float(era_data['overall_success_score'].mean()),
                
                # International percentage
                'international_pct': float((era_data['country'] != 'USA').sum() / len(era_data) * 100),
                
                # Top players
                'top_players': era_data.nlargest(5, 'overall_success_score')['name'].tolist()
            }
            
            results['era_statistics'][f"{era}s"] = era_stats
        
        # 2. Temporal trends (linear regression over time)
        results['temporal_trends'] = self._analyze_trends(df)
        
        # 3. International player impact
        results['international_impact'] = self._analyze_international_impact(df)
        
        # 4. Era comparisons (1950s vs 2020s, etc.)
        results['era_comparisons'] = self._compare_eras(df, eras)
        
        # 5. Trend significance testing
        results['trend_analysis'] = self._analyze_trend_significance(df)
        
        return results
    
    def analyze_era_transitions(self, df: pd.DataFrame) -> Dict:
        """Analyze transitions between eras (e.g., 1970s→1980s).
        
        Args:
            df: DataFrame with player data
            
        Returns:
            Era transition analysis
        """
        logger.info("Analyzing era transitions...")
        
        results = {
            'transitions': {},
            'inflection_points': {}
        }
        
        eras = sorted(df['era'].unique())
        
        for i in range(len(eras) - 1):
            era1 = eras[i]
            era2 = eras[i + 1]
            
            era1_data = df[df['era'] == era1]
            era2_data = df[df['era'] == era2]
            
            if len(era1_data) < 5 or len(era2_data) < 5:
                continue
            
            transition_key = f"{era1}s_to_{era2}s"
            
            # Calculate changes
            changes = {
                'syllable_change': float(era2_data['syllable_count'].mean() - era1_data['syllable_count'].mean()),
                'memorability_change': float(era2_data['memorability_score'].mean() - era1_data['memorability_score'].mean()),
                'uniqueness_change': float(era2_data['uniqueness_score'].mean() - era1_data['uniqueness_score'].mean()),
                'harshness_change': float(era2_data['harshness_score'].mean() - era1_data['harshness_score'].mean()),
                'international_change': float(
                    (era2_data['country'] != 'USA').sum() / len(era2_data) * 100 -
                    (era1_data['country'] != 'USA').sum() / len(era1_data) * 100
                ),
            }
            
            # Statistical significance tests
            significance = {}
            for metric in ['syllable_count', 'memorability_score', 'uniqueness_score', 'harshness_score']:
                t_stat, p_value = stats.ttest_ind(era1_data[metric].dropna(), era2_data[metric].dropna())
                significance[metric] = {
                    't_statistic': float(t_stat),
                    'p_value': float(p_value),
                    'significant': p_value < 0.05
                }
            
            results['transitions'][transition_key] = {
                'changes': changes,
                'significance': significance,
                'interpretation': self._interpret_transition(changes)
            }
        
        return results
    
    def analyze_international_evolution(self, df: pd.DataFrame) -> Dict:
        """Analyze how international players changed naming patterns.
        
        Args:
            df: DataFrame with player data
            
        Returns:
            International player evolution analysis
        """
        logger.info("Analyzing international player evolution...")
        
        results = {
            'international_by_era': {},
            'name_differences': {},
            'impact_on_league': {}
        }
        
        eras = sorted(df['era'].unique())
        
        for era in eras:
            era_data = df[df['era'] == era]
            
            if len(era_data) < 5:
                continue
            
            usa_players = era_data[era_data['country'] == 'USA']
            intl_players = era_data[era_data['country'] != 'USA']
            
            if len(intl_players) < 3:
                continue
            
            era_results = {
                'total_players': len(era_data),
                'usa_count': len(usa_players),
                'international_count': len(intl_players),
                'international_pct': float(len(intl_players) / len(era_data) * 100),
                
                # Name pattern differences
                'usa_avg_syllables': float(usa_players['syllable_count'].mean()) if len(usa_players) > 0 else 0,
                'intl_avg_syllables': float(intl_players['syllable_count'].mean()),
                'usa_avg_length': float(usa_players['character_length'].mean()) if len(usa_players) > 0 else 0,
                'intl_avg_length': float(intl_players['character_length'].mean()),
                
                # Success metrics
                'usa_avg_success': float(usa_players['overall_success_score'].mean()) if len(usa_players) > 0 else 0,
                'intl_avg_success': float(intl_players['overall_success_score'].mean()),
            }
            
            results['international_by_era'][f"{era}s"] = era_results
        
        return results
    
    def _analyze_trends(self, df: pd.DataFrame) -> Dict:
        """Analyze linear trends over time.
        
        Args:
            df: DataFrame with player data
            
        Returns:
            Trend analysis
        """
        trends = {}
        
        # Features to analyze
        features = [
            'syllable_count', 'character_length', 'memorability_score',
            'uniqueness_score', 'harshness_score', 'softness_score',
            'alliteration_score'
        ]
        
        for feature in features:
            # Group by era and get mean
            era_means = df.groupby('era')[feature].mean()
            
            if len(era_means) < 3:
                continue
            
            eras = era_means.index.values
            values = era_means.values
            
            # Linear regression
            slope, intercept, r_value, p_value, std_err = stats.linregress(eras, values)
            
            # Calculate change from first to last era
            first_era_val = values[0]
            last_era_val = values[-1]
            total_change = last_era_val - first_era_val
            pct_change = (total_change / first_era_val * 100) if first_era_val != 0 else 0
            
            trends[feature] = {
                'slope': float(slope),
                'r_squared': float(r_value ** 2),
                'p_value': float(p_value),
                'significant': p_value < 0.05,
                'direction': 'increasing' if slope > 0 else 'decreasing',
                'total_change': float(total_change),
                'percent_change': float(pct_change),
                'interpretation': self._interpret_trend(feature, slope, pct_change, p_value)
            }
        
        return trends
    
    def _analyze_international_impact(self, df: pd.DataFrame) -> Dict:
        """Analyze impact of international players on naming patterns.
        
        Args:
            df: DataFrame with player data
            
        Returns:
            International impact analysis
        """
        # Pre-international era (before 1990) vs post
        pre_1990 = df[df['era'] < 1990]
        post_2000 = df[df['era'] >= 2000]
        
        if len(pre_1990) < 10 or len(post_2000) < 10:
            return {}
        
        impact = {
            'era_comparison': {
                'pre_1990': {
                    'international_pct': float((pre_1990['country'] != 'USA').sum() / len(pre_1990) * 100),
                    'avg_syllables': float(pre_1990['syllable_count'].mean()),
                    'avg_memorability': float(pre_1990['memorability_score'].mean()),
                },
                'post_2000': {
                    'international_pct': float((post_2000['country'] != 'USA').sum() / len(post_2000) * 100),
                    'avg_syllables': float(post_2000['syllable_count'].mean()),
                    'avg_memorability': float(post_2000['memorability_score'].mean()),
                },
            },
            'correlation_with_international_pct': self._correlate_international_percentage(df)
        }
        
        return impact
    
    def _correlate_international_percentage(self, df: pd.DataFrame) -> Dict:
        """Correlate international player percentage with naming patterns.
        
        Args:
            df: DataFrame with player data
            
        Returns:
            Correlation analysis
        """
        # Group by era
        era_groups = df.groupby('era').agg({
            'syllable_count': 'mean',
            'character_length': 'mean',
            'memorability_score': 'mean',
            'country': lambda x: (x != 'USA').sum() / len(x) * 100
        }).rename(columns={'country': 'international_pct'})
        
        if len(era_groups) < 3:
            return {}
        
        correlations = {}
        for col in ['syllable_count', 'character_length', 'memorability_score']:
            corr, p_value = stats.pearsonr(
                era_groups['international_pct'],
                era_groups[col]
            )
            
            correlations[col] = {
                'correlation': float(corr),
                'p_value': float(p_value),
                'significant': p_value < 0.05
            }
        
        return correlations
    
    def _compare_eras(self, df: pd.DataFrame, eras: List[int]) -> Dict:
        """Compare specific eras (e.g., 1950s vs 2020s).
        
        Args:
            df: DataFrame with player data
            eras: List of eras
            
        Returns:
            Era comparison results
        """
        comparisons = {}
        
        if len(eras) < 2:
            return comparisons
        
        # Compare first and last era
        first_era = eras[0]
        last_era = eras[-1]
        
        first_data = df[df['era'] == first_era]
        last_data = df[df['era'] == last_era]
        
        if len(first_data) >= 5 and len(last_data) >= 5:
            comparisons['first_vs_last'] = {
                'eras': f"{first_era}s vs {last_era}s",
                'syllable_change': float(last_data['syllable_count'].mean() - first_data['syllable_count'].mean()),
                'memorability_change': float(last_data['memorability_score'].mean() - first_data['memorability_score'].mean()),
                'uniqueness_change': float(last_data['uniqueness_score'].mean() - first_data['uniqueness_score'].mean()),
                'harshness_change': float(last_data['harshness_score'].mean() - first_data['harshness_score'].mean()),
            }
        
        # Compare Classic vs Contemporary
        classic = df[df['era_group'] == 'Classic']
        contemporary = df[df['era_group'] == 'Contemporary']
        
        if len(classic) >= 10 and len(contemporary) >= 10:
            comparisons['classic_vs_contemporary'] = {
                'syllable_change': float(contemporary['syllable_count'].mean() - classic['syllable_count'].mean()),
                'memorability_change': float(contemporary['memorability_score'].mean() - classic['memorability_score'].mean()),
                'uniqueness_change': float(contemporary['uniqueness_score'].mean() - classic['uniqueness_score'].mean()),
            }
        
        return comparisons
    
    def _analyze_trend_significance(self, df: pd.DataFrame) -> Dict:
        """Test statistical significance of trends.
        
        Args:
            df: DataFrame with player data
            
        Returns:
            Trend significance analysis
        """
        significance = {}
        
        # Group by era group
        era_groups = ['Classic', 'Modern', 'Contemporary']
        
        for i in range(len(era_groups) - 1):
            for j in range(i + 1, len(era_groups)):
                group1 = df[df['era_group'] == era_groups[i]]
                group2 = df[df['era_group'] == era_groups[j]]
                
                if len(group1) < 5 or len(group2) < 5:
                    continue
                
                comparison_key = f"{era_groups[i]}_vs_{era_groups[j]}"
                
                tests = {}
                for metric in ['syllable_count', 'memorability_score', 'uniqueness_score']:
                    t_stat, p_value = stats.ttest_ind(
                        group1[metric].dropna(),
                        group2[metric].dropna()
                    )
                    
                    tests[metric] = {
                        't_statistic': float(t_stat),
                        'p_value': float(p_value),
                        'significant': p_value < 0.05,
                        'mean_diff': float(group2[metric].mean() - group1[metric].mean())
                    }
                
                significance[comparison_key] = tests
        
        return significance
    
    def _interpret_trend(self, feature: str, slope: float, pct_change: float, p_value: float) -> str:
        """Generate human-readable interpretation of trend.
        
        Args:
            feature: Feature name
            slope: Trend slope
            pct_change: Percentage change
            p_value: Statistical significance
            
        Returns:
            Interpretation string
        """
        if p_value >= 0.05:
            return f"No significant trend in {feature} over time"
        
        direction = "increased" if slope > 0 else "decreased"
        magnitude = "slightly" if abs(pct_change) < 10 else "moderately" if abs(pct_change) < 25 else "significantly"
        
        return f"{feature.replace('_', ' ').title()} {magnitude} {direction} over time ({pct_change:+.1f}%)"
    
    def _interpret_transition(self, changes: Dict) -> str:
        """Generate interpretation of era transition.
        
        Args:
            changes: Dictionary of changes
            
        Returns:
            Interpretation string
        """
        interpretations = []
        
        if abs(changes.get('syllable_change', 0)) > 0.2:
            direction = "increased" if changes['syllable_change'] > 0 else "decreased"
            interpretations.append(f"Syllable count {direction}")
        
        if abs(changes.get('international_change', 0)) > 5:
            if changes['international_change'] > 0:
                interpretations.append(f"International player presence rose by {changes['international_change']:.1f}%")
        
        if not interpretations:
            return "Minimal changes in naming patterns"
        
        return "; ".join(interpretations)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    analyzer = NBATemporalAnalyzer()
    df = analyzer.get_era_dataset()
    
    if len(df) > 50:
        print("\n" + "="*60)
        print("NBA TEMPORAL ANALYSIS")
        print("="*60)
        
        # Evolution analysis
        evolution = analyzer.analyze_temporal_evolution(df)
        
        print("\n--- Era Statistics ---")
        for era, stats in evolution['era_statistics'].items():
            print(f"\n{era}:")
            print(f"  Players: {stats['sample_size']}")
            print(f"  Avg Syllables: {stats['avg_syllables']:.2f}")
            print(f"  Avg Memorability: {stats['avg_memorability']:.1f}")
            print(f"  International: {stats['international_pct']:.1f}%")
        
        print("\n--- Temporal Trends ---")
        for feature, trend in evolution['temporal_trends'].items():
            if trend.get('significant'):
                print(f"{feature}: {trend['interpretation']}")
        
        # Transitions
        transitions = analyzer.analyze_era_transitions(df)
        print("\n--- Era Transitions ---")
        for trans, data in transitions['transitions'].items():
            print(f"\n{trans}: {data['interpretation']}")
        
        # International evolution
        intl = analyzer.analyze_international_evolution(df)
        print("\n--- International Player Evolution ---")
        for era, data in intl['international_by_era'].items():
            print(f"{era}: {data['international_pct']:.1f}% international")
    else:
        print("Insufficient data. Run nba_collector.py to collect players first.")

