"""NBA Position Analyzer

Analyzes position-specific linguistic patterns in NBA player names.
Tests hypotheses about naming differences across positions.

Hypotheses:
- Guards: Shorter, "quicker" sounding names
- Centers: "Harder" sounding names (higher harshness)
- Forwards: Balanced/versatile naming patterns
- Position-specific phonetic signatures
"""

import logging
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from scipy import stats

from core.models import db, NBAPlayer, NBAPlayerAnalysis

logger = logging.getLogger(__name__)


class NBAPositionAnalyzer:
    """Analyze position-specific linguistic patterns in player names."""
    
    def __init__(self):
        pass
    
    def get_position_dataset(self) -> pd.DataFrame:
        """Load players with position information.
        
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
                    # Position data
                    'name': player.name,
                    'position': player.position,
                    'position_group': player.position_group,
                    'primary_position': player.primary_position,
                    
                    # Performance
                    'ppg': player.ppg or 0,
                    'apg': player.apg or 0,
                    'rpg': player.rpg or 0,
                    'per': player.per or 0,
                    'performance_score': player.performance_score or 0,
                    'overall_success_score': player.overall_success_score or 0,
                    
                    # Physical
                    'height_inches': player.height_inches or 0,
                    
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
                    'consonant_cluster_complexity': analysis.consonant_cluster_complexity or 50,
                    'alliteration_score': analysis.alliteration_score or 0,
                    'phonetic_score': analysis.phonetic_score or 0,
                    'vowel_ratio': analysis.vowel_ratio or 0,
                    
                    # Name components
                    'first_name_syllables': analysis.first_name_syllables or 0,
                    'first_name_length': analysis.first_name_length or 0,
                    'last_name_syllables': analysis.last_name_syllables or 0,
                    'last_name_length': analysis.last_name_length or 0,
                }
                
                rows.append(row)
                
            except Exception as e:
                logger.warning(f"Error loading player {player.name}: {e}")
                continue
        
        df = pd.DataFrame(rows)
        logger.info(f"Loaded {len(df)} players for position analysis")
        
        return df
    
    def analyze_position_patterns(self, df: pd.DataFrame) -> Dict:
        """Analyze linguistic patterns by position.
        
        Args:
            df: DataFrame with player data
            
        Returns:
            Position pattern analysis
        """
        logger.info("Analyzing position-specific patterns...")
        
        results = {
            'position_group_profiles': {},
            'primary_position_profiles': {},
            'position_comparisons': {},
            'hypothesis_tests': {},
            'position_archetypes': {}
        }
        
        # 1. Position group profiles (Guard, Forward, Center)
        results['position_group_profiles'] = self._analyze_position_groups(df)
        
        # 2. Primary position profiles (PG, SG, SF, PF, C)
        results['primary_position_profiles'] = self._analyze_primary_positions(df)
        
        # 3. Position comparisons (Guard vs Center, etc.)
        results['position_comparisons'] = self._compare_positions(df)
        
        # 4. Hypothesis tests
        results['hypothesis_tests'] = self._test_position_hypotheses(df)
        
        # 5. Position archetypes (typical names per position)
        results['position_archetypes'] = self._identify_archetypes(df)
        
        return results
    
    def analyze_position_correlations(self, df: pd.DataFrame) -> Dict:
        """Analyze correlations between linguistic features and position characteristics.
        
        Args:
            df: DataFrame with player data
            
        Returns:
            Correlation analysis
        """
        logger.info("Analyzing position correlations...")
        
        results = {
            'feature_by_position': {},
            'performance_correlations': {},
            'physical_correlations': {}
        }
        
        # Features to analyze
        features = [
            'syllable_count', 'character_length', 'memorability_score',
            'harshness_score', 'softness_score', 'speed_association_score',
            'strength_association_score', 'rhythm_score'
        ]
        
        # 1. Feature distributions by position
        for position_group in df['position_group'].unique():
            pos_data = df[df['position_group'] == position_group]
            
            if len(pos_data) < 5:
                continue
            
            feature_stats = {}
            for feature in features:
                feature_stats[feature] = {
                    'mean': float(pos_data[feature].mean()),
                    'median': float(pos_data[feature].median()),
                    'std': float(pos_data[feature].std()),
                    'min': float(pos_data[feature].min()),
                    'max': float(pos_data[feature].max())
                }
            
            results['feature_by_position'][position_group] = feature_stats
        
        # 2. Correlations with performance stats
        results['performance_correlations'] = self._correlate_with_performance(df, features)
        
        # 3. Correlations with physical attributes
        if 'height_inches' in df.columns:
            results['physical_correlations'] = self._correlate_with_physical(df, features)
        
        return results
    
    def analyze_role_specific_patterns(self, df: pd.DataFrame) -> Dict:
        """Analyze patterns by player role/style.
        
        Args:
            df: DataFrame with player data
            
        Returns:
            Role-specific pattern analysis
        """
        logger.info("Analyzing role-specific patterns...")
        
        results = {
            'scorer_patterns': {},
            'playmaker_patterns': {},
            'rebounder_patterns': {},
            'defensive_patterns': {}
        }
        
        # Define roles based on stats
        df['is_scorer'] = df['ppg'] >= df['ppg'].quantile(0.75)
        df['is_playmaker'] = df['apg'] >= df['apg'].quantile(0.75)
        df['is_rebounder'] = df['rpg'] >= df['rpg'].quantile(0.75)
        
        features = ['syllable_count', 'harshness_score', 'speed_association_score', 'strength_association_score']
        
        # Compare each role vs non-role
        for role, role_name in [('is_scorer', 'scorer_patterns'), 
                                 ('is_playmaker', 'playmaker_patterns'),
                                 ('is_rebounder', 'rebounder_patterns')]:
            
            role_players = df[df[role] == True]
            non_role_players = df[df[role] == False]
            
            if len(role_players) < 10 or len(non_role_players) < 10:
                continue
            
            comparisons = {}
            for feature in features:
                role_mean = role_players[feature].mean()
                non_role_mean = non_role_players[feature].mean()
                
                # T-test
                t_stat, p_value = stats.ttest_ind(
                    role_players[feature].dropna(),
                    non_role_players[feature].dropna()
                )
                
                comparisons[feature] = {
                    'role_mean': float(role_mean),
                    'non_role_mean': float(non_role_mean),
                    'difference': float(role_mean - non_role_mean),
                    't_statistic': float(t_stat),
                    'p_value': float(p_value),
                    'significant': p_value < 0.05
                }
            
            results[role_name] = {
                'sample_size': len(role_players),
                'comparisons': comparisons,
                'interpretation': self._interpret_role_patterns(role, comparisons)
            }
        
        return results
    
    def _analyze_position_groups(self, df: pd.DataFrame) -> Dict:
        """Analyze Guard, Forward, Center profiles.
        
        Args:
            df: DataFrame with player data
            
        Returns:
            Position group profiles
        """
        profiles = {}
        
        for position_group in df['position_group'].unique():
            pos_data = df[df['position_group'] == position_group]
            
            if len(pos_data) < 5:
                continue
            
            profile = {
                'sample_size': len(pos_data),
                'position': position_group,
                
                # Linguistic averages
                'avg_syllables': float(pos_data['syllable_count'].mean()),
                'avg_character_length': float(pos_data['character_length'].mean()),
                'avg_memorability': float(pos_data['memorability_score'].mean()),
                'avg_uniqueness': float(pos_data['uniqueness_score'].mean()),
                'avg_harshness': float(pos_data['harshness_score'].mean()),
                'avg_softness': float(pos_data['softness_score'].mean()),
                'avg_speed_association': float(pos_data['speed_association_score'].mean()),
                'avg_strength_association': float(pos_data['strength_association_score'].mean()),
                'avg_rhythm': float(pos_data['rhythm_score'].mean()),
                
                # Performance
                'avg_ppg': float(pos_data['ppg'].mean()),
                'avg_apg': float(pos_data['apg'].mean()),
                'avg_rpg': float(pos_data['rpg'].mean()),
                'avg_success': float(pos_data['overall_success_score'].mean()),
                
                # Top players
                'top_players': pos_data.nlargest(10, 'overall_success_score')['name'].tolist()
            }
            
            profiles[position_group] = profile
        
        return profiles
    
    def _analyze_primary_positions(self, df: pd.DataFrame) -> Dict:
        """Analyze specific position profiles (PG, SG, etc.).
        
        Args:
            df: DataFrame with player data
            
        Returns:
            Primary position profiles
        """
        profiles = {}
        
        positions = ['PG', 'SG', 'SF', 'PF', 'C']
        
        for position in positions:
            pos_data = df[df['primary_position'] == position]
            
            if len(pos_data) < 5:
                continue
            
            profile = {
                'sample_size': len(pos_data),
                'position': position,
                'avg_syllables': float(pos_data['syllable_count'].mean()),
                'avg_harshness': float(pos_data['harshness_score'].mean()),
                'avg_speed_association': float(pos_data['speed_association_score'].mean()),
                'avg_strength_association': float(pos_data['strength_association_score'].mean()),
                'avg_success': float(pos_data['overall_success_score'].mean()),
                'top_players': pos_data.nlargest(5, 'overall_success_score')['name'].tolist()
            }
            
            profiles[position] = profile
        
        return profiles
    
    def _compare_positions(self, df: pd.DataFrame) -> Dict:
        """Compare positions statistically.
        
        Args:
            df: DataFrame with player data
            
        Returns:
            Position comparison results
        """
        comparisons = {}
        
        # Guard vs Center
        guards = df[df['position_group'] == 'Guard']
        centers = df[df['position_group'] == 'Center']
        
        if len(guards) >= 10 and len(centers) >= 10:
            comparisons['guard_vs_center'] = self._compare_two_groups(guards, centers, 'Guard', 'Center')
        
        # Guard vs Forward
        forwards = df[df['position_group'] == 'Forward']
        if len(guards) >= 10 and len(forwards) >= 10:
            comparisons['guard_vs_forward'] = self._compare_two_groups(guards, forwards, 'Guard', 'Forward')
        
        # Forward vs Center
        if len(forwards) >= 10 and len(centers) >= 10:
            comparisons['forward_vs_center'] = self._compare_two_groups(forwards, centers, 'Forward', 'Center')
        
        return comparisons
    
    def _compare_two_groups(self, group1: pd.DataFrame, group2: pd.DataFrame, 
                           name1: str, name2: str) -> Dict:
        """Compare two position groups statistically.
        
        Args:
            group1: First group data
            group2: Second group data
            name1: First group name
            name2: Second group name
            
        Returns:
            Comparison results
        """
        features = ['syllable_count', 'harshness_score', 'softness_score', 
                   'speed_association_score', 'strength_association_score']
        
        results = {
            'groups': f"{name1} vs {name2}",
            'sample_sizes': {name1: len(group1), name2: len(group2)},
            'comparisons': {}
        }
        
        for feature in features:
            mean1 = group1[feature].mean()
            mean2 = group2[feature].mean()
            
            # T-test
            t_stat, p_value = stats.ttest_ind(
                group1[feature].dropna(),
                group2[feature].dropna()
            )
            
            results['comparisons'][feature] = {
                f'{name1}_mean': float(mean1),
                f'{name2}_mean': float(mean2),
                'difference': float(mean1 - mean2),
                't_statistic': float(t_stat),
                'p_value': float(p_value),
                'significant': p_value < 0.05,
                'interpretation': self._interpret_difference(feature, name1, name2, mean1, mean2, p_value)
            }
        
        return results
    
    def _test_position_hypotheses(self, df: pd.DataFrame) -> Dict:
        """Test specific hypotheses about position-name relationships.
        
        Args:
            df: DataFrame with player data
            
        Returns:
            Hypothesis test results
        """
        hypotheses = {}
        
        guards = df[df['position_group'] == 'Guard']
        centers = df[df['position_group'] == 'Center']
        forwards = df[df['position_group'] == 'Forward']
        
        # H1: Guards have shorter names (fewer syllables)
        if len(guards) >= 10 and len(centers) >= 10:
            guard_syllables = guards['syllable_count'].mean()
            center_syllables = centers['syllable_count'].mean()
            t_stat, p_value = stats.ttest_ind(guards['syllable_count'].dropna(), centers['syllable_count'].dropna())
            
            hypotheses['guards_shorter_names'] = {
                'hypothesis': 'Guards have shorter names than Centers',
                'guard_avg_syllables': float(guard_syllables),
                'center_avg_syllables': float(center_syllables),
                'difference': float(guard_syllables - center_syllables),
                'p_value': float(p_value),
                'supported': guard_syllables < center_syllables and p_value < 0.05,
                'strength': 'strong' if p_value < 0.01 else 'moderate' if p_value < 0.05 else 'weak'
            }
        
        # H2: Centers have "harder" sounding names (higher harshness)
        if len(guards) >= 10 and len(centers) >= 10:
            guard_harshness = guards['harshness_score'].mean()
            center_harshness = centers['harshness_score'].mean()
            t_stat, p_value = stats.ttest_ind(guards['harshness_score'].dropna(), centers['harshness_score'].dropna())
            
            hypotheses['centers_harder_names'] = {
                'hypothesis': 'Centers have harder/harsher sounding names than Guards',
                'guard_avg_harshness': float(guard_harshness),
                'center_avg_harshness': float(center_harshness),
                'difference': float(center_harshness - guard_harshness),
                'p_value': float(p_value),
                'supported': center_harshness > guard_harshness and p_value < 0.05,
                'strength': 'strong' if p_value < 0.01 else 'moderate' if p_value < 0.05 else 'weak'
            }
        
        # H3: Guards have higher "speed association" scores
        if len(guards) >= 10 and len(centers) >= 10:
            guard_speed = guards['speed_association_score'].mean()
            center_speed = centers['speed_association_score'].mean()
            t_stat, p_value = stats.ttest_ind(guards['speed_association_score'].dropna(), centers['speed_association_score'].dropna())
            
            hypotheses['guards_speedier_names'] = {
                'hypothesis': 'Guards have names with higher speed associations',
                'guard_avg_speed': float(guard_speed),
                'center_avg_speed': float(center_speed),
                'difference': float(guard_speed - center_speed),
                'p_value': float(p_value),
                'supported': guard_speed > center_speed and p_value < 0.05,
                'strength': 'strong' if p_value < 0.01 else 'moderate' if p_value < 0.05 else 'weak'
            }
        
        # H4: Centers have higher "strength association" scores
        if len(guards) >= 10 and len(centers) >= 10:
            guard_strength = guards['strength_association_score'].mean()
            center_strength = centers['strength_association_score'].mean()
            t_stat, p_value = stats.ttest_ind(guards['strength_association_score'].dropna(), centers['strength_association_score'].dropna())
            
            hypotheses['centers_stronger_names'] = {
                'hypothesis': 'Centers have names with higher strength associations',
                'guard_avg_strength': float(guard_strength),
                'center_avg_strength': float(center_strength),
                'difference': float(center_strength - guard_strength),
                'p_value': float(p_value),
                'supported': center_strength > guard_strength and p_value < 0.05,
                'strength': 'strong' if p_value < 0.01 else 'moderate' if p_value < 0.05 else 'weak'
            }
        
        return hypotheses
    
    def _identify_archetypes(self, df: pd.DataFrame) -> Dict:
        """Identify typical/archetypal names for each position.
        
        Args:
            df: DataFrame with player data
            
        Returns:
            Position archetypes
        """
        archetypes = {}
        
        for position_group in df['position_group'].unique():
            pos_data = df[df['position_group'] == position_group]
            
            if len(pos_data) < 10:
                continue
            
            # Find most "typical" names (closest to position mean across features)
            features = ['syllable_count', 'harshness_score', 'speed_association_score']
            
            # Calculate position means
            pos_means = pos_data[features].mean()
            
            # Calculate distance from mean for each player
            distances = []
            for idx, row in pos_data.iterrows():
                dist = np.sqrt(sum((row[f] - pos_means[f])**2 for f in features))
                distances.append((row['name'], dist, row['overall_success_score']))
            
            # Sort by distance (most typical = smallest distance)
            distances.sort(key=lambda x: x[1])
            
            archetypes[position_group] = {
                'most_typical': [name for name, dist, score in distances[:10]],
                'most_successful_typical': sorted(distances[:20], key=lambda x: x[2], reverse=True)[:5]
            }
        
        return archetypes
    
    def _correlate_with_performance(self, df: pd.DataFrame, features: List[str]) -> Dict:
        """Correlate linguistic features with performance by position.
        
        Args:
            df: DataFrame with player data
            features: List of features to correlate
            
        Returns:
            Correlation results
        """
        correlations = {}
        
        for position_group in df['position_group'].unique():
            pos_data = df[df['position_group'] == position_group]
            
            if len(pos_data) < 10:
                continue
            
            pos_correlations = {}
            for feature in features:
                valid_data = pos_data[[feature, 'performance_score']].dropna()
                
                if len(valid_data) < 10:
                    continue
                
                corr, p_value = stats.pearsonr(valid_data[feature], valid_data['performance_score'])
                
                pos_correlations[feature] = {
                    'correlation': float(corr),
                    'p_value': float(p_value),
                    'significant': p_value < 0.05
                }
            
            correlations[position_group] = pos_correlations
        
        return correlations
    
    def _correlate_with_physical(self, df: pd.DataFrame, features: List[str]) -> Dict:
        """Correlate linguistic features with physical attributes.
        
        Args:
            df: DataFrame with player data
            features: List of features to correlate
            
        Returns:
            Correlation results
        """
        correlations = {}
        
        for feature in features:
            valid_data = df[[feature, 'height_inches']].dropna()
            
            if len(valid_data) < 20:
                continue
            
            corr, p_value = stats.pearsonr(valid_data[feature], valid_data['height_inches'])
            
            correlations[feature] = {
                'correlation_with_height': float(corr),
                'p_value': float(p_value),
                'significant': p_value < 0.05,
                'interpretation': f"{'Positive' if corr > 0 else 'Negative'} correlation with height"
            }
        
        return correlations
    
    def _interpret_difference(self, feature: str, name1: str, name2: str, 
                             mean1: float, mean2: float, p_value: float) -> str:
        """Interpret difference between two groups.
        
        Args:
            feature: Feature name
            name1: First group name
            name2: Second group name
            mean1: First group mean
            mean2: Second group mean
            p_value: Statistical significance
            
        Returns:
            Interpretation string
        """
        if p_value >= 0.05:
            return f"No significant difference in {feature}"
        
        higher_group = name1 if mean1 > mean2 else name2
        diff_pct = abs((mean1 - mean2) / mean2 * 100)
        
        magnitude = "slightly" if diff_pct < 10 else "moderately" if diff_pct < 20 else "significantly"
        
        return f"{higher_group}s have {magnitude} higher {feature.replace('_', ' ')}"
    
    def _interpret_role_patterns(self, role: str, comparisons: Dict) -> str:
        """Interpret role-specific patterns.
        
        Args:
            role: Role name
            comparisons: Comparison results
            
        Returns:
            Interpretation string
        """
        sig_features = [f for f, data in comparisons.items() if data.get('significant', False)]
        
        if not sig_features:
            return f"No significant naming patterns for {role.replace('is_', '')}s"
        
        role_name = role.replace('is_', '').title()
        patterns = []
        
        for feature in sig_features:
            diff = comparisons[feature]['difference']
            if diff > 0:
                patterns.append(f"higher {feature.replace('_', ' ')}")
            else:
                patterns.append(f"lower {feature.replace('_', ' ')}")
        
        return f"{role_name}s tend to have {', '.join(patterns)}"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    analyzer = NBAPositionAnalyzer()
    df = analyzer.get_position_dataset()
    
    if len(df) > 50:
        print("\n" + "="*60)
        print("NBA POSITION ANALYSIS")
        print("="*60)
        
        # Position patterns
        patterns = analyzer.analyze_position_patterns(df)
        
        print("\n--- Position Group Profiles ---")
        for position, profile in patterns['position_group_profiles'].items():
            print(f"\n{position} (n={profile['sample_size']}):")
            print(f"  Avg Syllables: {profile['avg_syllables']:.2f}")
            print(f"  Avg Harshness: {profile['avg_harshness']:.1f}")
            print(f"  Avg Speed Association: {profile['avg_speed_association']:.1f}")
        
        print("\n--- Hypothesis Tests ---")
        for hyp_name, hyp_data in patterns['hypothesis_tests'].items():
            print(f"\n{hyp_data['hypothesis']}:")
            print(f"  Supported: {'YES' if hyp_data['supported'] else 'NO'}")
            print(f"  Strength: {hyp_data['strength']}")
            print(f"  p-value: {hyp_data['p_value']:.4f}")
        
        # Correlations
        correlations = analyzer.analyze_position_correlations(df)
        print("\n--- Feature Distributions by Position ---")
        for position, features in correlations['feature_by_position'].items():
            print(f"\n{position}:")
            for feature, stats in list(features.items())[:3]:
                print(f"  {feature}: {stats['mean']:.2f} ± {stats['std']:.2f}")
        
        # Role patterns
        roles = analyzer.analyze_role_specific_patterns(df)
        print("\n--- Role-Specific Patterns ---")
        for role_name, role_data in roles.items():
            if role_data:
                print(f"\n{role_name.replace('_patterns', '').title()}:")
                print(f"  {role_data.get('interpretation', 'N/A')}")
    else:
        print("Insufficient data. Run nba_collector.py to collect players first.")

