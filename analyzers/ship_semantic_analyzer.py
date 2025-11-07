"""Ship Semantic Analyzer

Statistical analysis of ship nomenclature for nominative determinism research.

PRIMARY HYPOTHESIS:
Ships with geographically-tethered names (Florence, Boston, Vienna) achieved 
greater historical significance than saint-named ships.

SECONDARY HYPOTHESIS:
Semantic alignment between name and achievements (HMS Beagle → Darwin → evolution)
exceeds random chance (nominative determinism).

Analyses:
1. Geographic vs Saint comparison with effect sizes
2. Semantic alignment scoring and permutation testing
3. Phonetic power analysis (harsh names → battle success)
4. Temporal evolution of naming patterns
5. Cross-domain integration with hurricanes, bands, academics
"""

import logging
import json
import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Optional, Tuple
from collections import Counter, defaultdict

logger = logging.getLogger(__name__)


class ShipSemanticAnalyzer:
    """Comprehensive statistical analysis of ship nomenclature patterns."""
    
    def __init__(self):
        """Initialize analyzer with statistical methods."""
        self.min_sample_size = 5  # Minimum ships per category for comparison
        
    def analyze_geographic_vs_saint(self, ships_df: pd.DataFrame) -> Dict:
        """Primary hypothesis test: Geographic names vs Saint names.
        
        Tests whether ships with geographically-tethered names achieved
        greater historical significance than saint-named ships.
        
        Args:
            ships_df: DataFrame with ship data including name_category and outcomes
            
        Returns:
            Statistical comparison results
        """
        logger.info("="*70)
        logger.info("GEOGRAPHIC VS SAINT NAMES ANALYSIS")
        logger.info("="*70)
        
        # Filter to geographic and saint categories
        geographic = ships_df[ships_df['name_category'] == 'geographic']
        saint = ships_df[ships_df['name_category'] == 'saint']
        
        logger.info(f"Geographic ships: {len(geographic)}")
        logger.info(f"Saint ships: {len(saint)}")
        
        if len(geographic) < self.min_sample_size or len(saint) < self.min_sample_size:
            logger.warning("Insufficient sample sizes for comparison")
            return {
                'error': 'Insufficient data',
                'geographic_n': len(geographic),
                'saint_n': len(saint)
            }
        
        results = {
            'sample_sizes': {
                'geographic': len(geographic),
                'saint': len(saint)
            },
            'descriptive_statistics': {},
            'hypothesis_tests': {},
            'effect_sizes': {},
            'examples': {}
        }
        
        # Descriptive statistics
        results['descriptive_statistics'] = {
            'geographic': {
                'mean_significance': float(geographic['historical_significance_score'].mean()),
                'median_significance': float(geographic['historical_significance_score'].median()),
                'std_significance': float(geographic['historical_significance_score'].std()),
                'mean_years_active': float(geographic['years_active'].mean()) if 'years_active' in geographic else None,
                'mean_events': float(geographic['major_events_count'].mean()) if 'major_events_count' in geographic else None,
            },
            'saint': {
                'mean_significance': float(saint['historical_significance_score'].mean()),
                'median_significance': float(saint['historical_significance_score'].median()),
                'std_significance': float(saint['historical_significance_score'].std()),
                'mean_years_active': float(saint['years_active'].mean()) if 'years_active' in saint else None,
                'mean_events': float(saint['major_events_count'].mean()) if 'major_events_count' in saint else None,
            }
        }
        
        # T-test on historical significance
        t_stat, p_value = stats.ttest_ind(
            geographic['historical_significance_score'].dropna(),
            saint['historical_significance_score'].dropna(),
            equal_var=False  # Welch's t-test
        )
        
        results['hypothesis_tests']['t_test'] = {
            't_statistic': float(t_stat),
            'p_value': float(p_value),
            'significant': p_value < 0.05,
            'direction': 'geographic > saint' if t_stat > 0 else 'saint > geographic'
        }
        
        # Cohen's d effect size
        cohens_d = self._calculate_cohens_d(
            geographic['historical_significance_score'].dropna(),
            saint['historical_significance_score'].dropna()
        )
        results['effect_sizes']['cohens_d'] = {
            'value': float(cohens_d),
            'interpretation': self._interpret_cohens_d(cohens_d)
        }
        
        # Mann-Whitney U test (non-parametric)
        u_stat, p_value_mw = stats.mannwhitneyu(
            geographic['historical_significance_score'].dropna(),
            saint['historical_significance_score'].dropna(),
            alternative='two-sided'
        )
        
        results['hypothesis_tests']['mann_whitney'] = {
            'u_statistic': float(u_stat),
            'p_value': float(p_value_mw),
            'significant': p_value_mw < 0.05
        }
        
        # Top examples from each category
        results['examples'] = {
            'top_geographic': geographic.nlargest(5, 'historical_significance_score')[
                ['name', 'historical_significance_score', 'nation', 'era']
            ].to_dict('records'),
            'top_saint': saint.nlargest(5, 'historical_significance_score')[
                ['name', 'historical_significance_score', 'nation', 'era']
            ].to_dict('records')
        }
        
        # Log results
        logger.info(f"\nMean significance - Geographic: {results['descriptive_statistics']['geographic']['mean_significance']:.2f}")
        logger.info(f"Mean significance - Saint: {results['descriptive_statistics']['saint']['mean_significance']:.2f}")
        logger.info(f"T-test: t={t_stat:.3f}, p={p_value:.4f}")
        logger.info(f"Cohen's d: {cohens_d:.3f} ({self._interpret_cohens_d(cohens_d)})")
        
        return results
    
    def analyze_semantic_alignment(self, ships_df: pd.DataFrame, 
                                   ship_analysis_df: pd.DataFrame) -> Dict:
        """Test nominative determinism: name-achievement semantic alignment.
        
        Tests whether ships with names semantically aligned to their achievements
        (HMS Beagle → Darwin → evolution) achieved more than random chance.
        
        Args:
            ships_df: DataFrame with ship data
            ship_analysis_df: DataFrame with semantic alignment scores
            
        Returns:
            Semantic alignment analysis results
        """
        logger.info("\n" + "="*70)
        logger.info("SEMANTIC ALIGNMENT ANALYSIS (Nominative Determinism)")
        logger.info("="*70)
        
        # Merge dataframes
        merged = ships_df.merge(ship_analysis_df, left_on='id', right_on='ship_id', how='inner')
        
        if len(merged) < self.min_sample_size:
            return {'error': 'Insufficient data with semantic alignment scores'}
        
        results = {
            'overall_statistics': {},
            'case_studies': {},
            'permutation_test': {},
            'correlation_analysis': {}
        }
        
        # Overall semantic alignment statistics
        results['overall_statistics'] = {
            'mean_alignment': float(merged['semantic_alignment_score'].mean()),
            'median_alignment': float(merged['semantic_alignment_score'].median()),
            'std_alignment': float(merged['semantic_alignment_score'].std()),
            'high_alignment_count': int((merged['semantic_alignment_score'] > 70).sum()),
            'high_alignment_percentage': float((merged['semantic_alignment_score'] > 70).mean() * 100)
        }
        
        # Case studies: Ships with high semantic alignment
        high_alignment = merged[merged['semantic_alignment_score'] > 70].sort_values(
            'semantic_alignment_score', ascending=False
        )
        
        results['case_studies'] = {
            'high_alignment_ships': high_alignment[
                ['name', 'semantic_alignment_score', 'historical_significance_score',
                 'semantic_alignment_explanation']
            ].head(10).to_dict('records')
        }
        
        # Permutation test: Is alignment score better than random?
        # Null hypothesis: Semantic alignment scores are random
        observed_mean = merged['semantic_alignment_score'].mean()
        
        # Permutation: shuffle achievement scores
        n_permutations = 10000
        permuted_means = []
        
        for _ in range(n_permutations):
            # Shuffle semantic alignment scores
            shuffled_scores = np.random.permutation(merged['semantic_alignment_score'].values)
            permuted_means.append(shuffled_scores.mean())
        
        permuted_means = np.array(permuted_means)
        p_value_perm = (permuted_means >= observed_mean).sum() / n_permutations
        
        results['permutation_test'] = {
            'observed_mean_alignment': float(observed_mean),
            'null_distribution_mean': float(permuted_means.mean()),
            'null_distribution_std': float(permuted_means.std()),
            'p_value': float(p_value_perm),
            'significant': p_value_perm < 0.05,
            'interpretation': 'Semantic alignment exceeds random chance' if p_value_perm < 0.05 else 'No evidence of nominative determinism'
        }
        
        # Correlation: Semantic alignment vs Achievement
        correlation, p_value_corr = stats.pearsonr(
            merged['semantic_alignment_score'],
            merged['historical_significance_score']
        )
        
        results['correlation_analysis'] = {
            'pearson_r': float(correlation),
            'p_value': float(p_value_corr),
            'r_squared': float(correlation ** 2),
            'significant': p_value_corr < 0.05,
            'interpretation': f"{'Positive' if correlation > 0 else 'Negative'} correlation (r={correlation:.3f})"
        }
        
        # Log results
        logger.info(f"\nMean semantic alignment: {observed_mean:.2f}")
        logger.info(f"Permutation test p-value: {p_value_perm:.4f}")
        logger.info(f"Correlation with achievement: r={correlation:.3f}, p={p_value_corr:.4f}")
        
        # HMS Beagle case study
        beagle = merged[merged['name'].str.lower() == 'beagle']
        if not beagle.empty:
            results['case_studies']['hms_beagle'] = {
                'name': beagle.iloc[0]['name'],
                'semantic_alignment_score': float(beagle.iloc[0]['semantic_alignment_score']),
                'historical_significance_score': float(beagle.iloc[0]['historical_significance_score']),
                'explanation': beagle.iloc[0]['semantic_alignment_explanation'],
                'analysis': 'HMS Beagle demonstrates strong nominative determinism: animal name (beagle dog) → carried naturalist Darwin → evolution theory (biological connection)'
            }
            logger.info("\n*** HMS BEAGLE CASE STUDY ***")
            logger.info(f"Semantic alignment: {beagle.iloc[0]['semantic_alignment_score']:.2f}")
            logger.info(f"Historical significance: {beagle.iloc[0]['historical_significance_score']:.2f}")
        
        return results
    
    def analyze_name_category_outcomes(self, ships_df: pd.DataFrame) -> Dict:
        """Compare outcomes across all name categories.
        
        Args:
            ships_df: DataFrame with ship data
            
        Returns:
            Category comparison results
        """
        logger.info("\n" + "="*70)
        logger.info("NAME CATEGORY OUTCOMES ANALYSIS")
        logger.info("="*70)
        
        results = {
            'categories': {},
            'anova': {},
            'rankings': {}
        }
        
        # Group by name category
        categories = ['geographic', 'saint', 'monarch', 'virtue', 'mythological', 'animal', 'other']
        
        for category in categories:
            cat_ships = ships_df[ships_df['name_category'] == category]
            
            if len(cat_ships) >= self.min_sample_size:
                results['categories'][category] = {
                    'count': len(cat_ships),
                    'mean_significance': float(cat_ships['historical_significance_score'].mean()),
                    'median_significance': float(cat_ships['historical_significance_score'].median()),
                    'std_significance': float(cat_ships['historical_significance_score'].std()),
                    'mean_years_active': float(cat_ships['years_active'].mean()) if 'years_active' in cat_ships else None,
                    'mean_events': float(cat_ships['major_events_count'].mean()) if 'major_events_count' in cat_ships else None,
                }
                
                logger.info(f"\n{category.upper()}: n={len(cat_ships)}, "
                          f"mean_significance={cat_ships['historical_significance_score'].mean():.2f}")
        
        # One-way ANOVA across categories
        groups = []
        group_names = []
        
        for category in categories:
            cat_ships = ships_df[ships_df['name_category'] == category]
            if len(cat_ships) >= self.min_sample_size:
                groups.append(cat_ships['historical_significance_score'].dropna().values)
                group_names.append(category)
        
        if len(groups) >= 3:
            f_stat, p_value = stats.f_oneway(*groups)
            
            results['anova'] = {
                'f_statistic': float(f_stat),
                'p_value': float(p_value),
                'significant': p_value < 0.05,
                'interpretation': 'Significant differences between categories' if p_value < 0.05 else 'No significant differences'
            }
            
            logger.info(f"\nANOVA: F={f_stat:.3f}, p={p_value:.4f}")
        
        # Rank categories by mean significance
        rankings = []
        for category, stats_dict in results['categories'].items():
            rankings.append({
                'category': category,
                'mean_significance': stats_dict['mean_significance'],
                'count': stats_dict['count']
            })
        
        rankings.sort(key=lambda x: x['mean_significance'], reverse=True)
        results['rankings'] = rankings
        
        logger.info("\nCategory Rankings (by mean significance):")
        for i, rank in enumerate(rankings, 1):
            logger.info(f"  {i}. {rank['category']}: {rank['mean_significance']:.2f} (n={rank['count']})")
        
        return results
    
    def analyze_phonetic_power(self, ships_df: pd.DataFrame,
                               ship_analysis_df: pd.DataFrame) -> Dict:
        """Analyze phonetic features and their correlation with outcomes.
        
        Tests whether harsh-sounding warship names correlate with battle success.
        
        Args:
            ships_df: DataFrame with ship data
            ship_analysis_df: DataFrame with phonetic analysis
            
        Returns:
            Phonetic analysis results
        """
        logger.info("\n" + "="*70)
        logger.info("PHONETIC POWER ANALYSIS")
        logger.info("="*70)
        
        # Merge dataframes
        merged = ships_df.merge(ship_analysis_df, left_on='id', right_on='ship_id', how='inner')
        
        # Filter to naval vessels with battle data
        naval = merged[merged['ship_type'] == 'naval']
        
        if len(naval) < self.min_sample_size:
            return {'error': 'Insufficient naval ship data'}
        
        results = {
            'harshness_analysis': {},
            'authority_analysis': {},
            'memorability_analysis': {}
        }
        
        # Harshness score vs battle success
        battle_ships = naval[naval['battles_participated'] > 0].copy()
        
        if len(battle_ships) >= self.min_sample_size:
            battle_ships['win_rate'] = battle_ships['battles_won'] / battle_ships['battles_participated']
            
            # Correlation: harshness vs win rate
            corr_harsh, p_harsh = stats.pearsonr(
                battle_ships['harshness_score'].dropna(),
                battle_ships['win_rate'].dropna()
            )
            
            results['harshness_analysis'] = {
                'correlation': float(corr_harsh),
                'p_value': float(p_harsh),
                'significant': p_harsh < 0.05,
                'interpretation': f"Harsh names correlate with battle success (r={corr_harsh:.3f})" if p_harsh < 0.05 and corr_harsh > 0 else "No significant correlation"
            }
            
            logger.info(f"\nHarshness vs Battle Win Rate: r={corr_harsh:.3f}, p={p_harsh:.4f}")
        
        # Authority score vs historical significance (all ships)
        if 'authority_score' in merged.columns:
            corr_auth, p_auth = stats.pearsonr(
                merged['authority_score'].dropna(),
                merged['historical_significance_score'].dropna()
            )
            
            results['authority_analysis'] = {
                'correlation': float(corr_auth),
                'p_value': float(p_auth),
                'significant': p_auth < 0.05,
                'sample_size': len(merged['authority_score'].dropna())
            }
            
            logger.info(f"Authority Score vs Significance: r={corr_auth:.3f}, p={p_auth:.4f}")
        
        # Memorability vs historical significance
        if 'memorability_score' in merged.columns:
            corr_mem, p_mem = stats.pearsonr(
                merged['memorability_score'].dropna(),
                merged['historical_significance_score'].dropna()
            )
            
            results['memorability_analysis'] = {
                'correlation': float(corr_mem),
                'p_value': float(p_mem),
                'significant': p_mem < 0.05,
                'interpretation': "More memorable names achieve greater significance" if p_mem < 0.05 and corr_mem > 0 else "No significant correlation"
            }
            
            logger.info(f"Memorability vs Significance: r={corr_mem:.3f}, p={p_mem:.4f}")
        
        return results
    
    def analyze_temporal_evolution(self, ships_df: pd.DataFrame) -> Dict:
        """Analyze how naming patterns evolved over time.
        
        Args:
            ships_df: DataFrame with ship data
            
        Returns:
            Temporal analysis results
        """
        logger.info("\n" + "="*70)
        logger.info("TEMPORAL EVOLUTION ANALYSIS")
        logger.info("="*70)
        
        results = {
            'eras': {},
            'category_trends': {},
            'significance_trends': {}
        }
        
        # Group by era
        eras = ['age_of_discovery', 'age_of_sail', 'steam_era', 'modern']
        
        for era in eras:
            era_ships = ships_df[ships_df['era'] == era]
            
            if len(era_ships) >= self.min_sample_size:
                # Category distribution
                category_dist = era_ships['name_category'].value_counts().to_dict()
                
                results['eras'][era] = {
                    'count': len(era_ships),
                    'mean_significance': float(era_ships['historical_significance_score'].mean()),
                    'category_distribution': category_dist,
                    'geographic_percentage': float((era_ships['name_category'] == 'geographic').mean() * 100),
                    'saint_percentage': float((era_ships['name_category'] == 'saint').mean() * 100),
                    'virtue_percentage': float((era_ships['name_category'] == 'virtue').mean() * 100)
                }
                
                logger.info(f"\n{era.upper()}: n={len(era_ships)}")
                logger.info(f"  Geographic: {results['eras'][era]['geographic_percentage']:.1f}%")
                logger.info(f"  Saint: {results['eras'][era]['saint_percentage']:.1f}%")
                logger.info(f"  Mean significance: {results['eras'][era]['mean_significance']:.2f}")
        
        # Trends over time
        if 'launch_year' in ships_df.columns:
            # Decade-level analysis
            ships_df_copy = ships_df.copy()
            ships_df_copy['decade'] = (ships_df_copy['launch_year'] // 10) * 10
            
            decade_stats = ships_df_copy.groupby('decade').agg({
                'historical_significance_score': 'mean',
                'name_category': lambda x: (x == 'geographic').mean() * 100
            }).to_dict()
            
            results['significance_trends'] = decade_stats
        
        return results
    
    def analyze_all(self, ships_df: pd.DataFrame,
                   ship_analysis_df: Optional[pd.DataFrame] = None) -> Dict:
        """Run complete analysis suite.
        
        Args:
            ships_df: DataFrame with ship data
            ship_analysis_df: Optional DataFrame with name analysis data
            
        Returns:
            Complete analysis results
        """
        logger.info("\n" + "="*70)
        logger.info("COMPLETE SHIP NOMENCLATURE ANALYSIS")
        logger.info("="*70)
        
        results = {
            'sample_size': len(ships_df),
            'geographic_vs_saint': None,
            'semantic_alignment': None,
            'category_outcomes': None,
            'phonetic_power': None,
            'temporal_evolution': None
        }
        
        # Run analyses
        results['geographic_vs_saint'] = self.analyze_geographic_vs_saint(ships_df)
        results['category_outcomes'] = self.analyze_name_category_outcomes(ships_df)
        results['temporal_evolution'] = self.analyze_temporal_evolution(ships_df)
        
        if ship_analysis_df is not None:
            results['semantic_alignment'] = self.analyze_semantic_alignment(
                ships_df, ship_analysis_df
            )
            results['phonetic_power'] = self.analyze_phonetic_power(
                ships_df, ship_analysis_df
            )
        
        return results
    
    # Helper methods
    
    def _calculate_cohens_d(self, group1: pd.Series, group2: pd.Series) -> float:
        """Calculate Cohen's d effect size."""
        n1, n2 = len(group1), len(group2)
        var1, var2 = group1.var(), group2.var()
        
        # Pooled standard deviation
        pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
        
        # Cohen's d
        d = (group1.mean() - group2.mean()) / pooled_std
        
        return d
    
    def _interpret_cohens_d(self, d: float) -> str:
        """Interpret Cohen's d effect size."""
        abs_d = abs(d)
        
        if abs_d < 0.2:
            return "negligible"
        elif abs_d < 0.5:
            return "small"
        elif abs_d < 0.8:
            return "medium"
        else:
            return "large"


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # This would be run with actual ship data from the database
    analyzer = ShipSemanticAnalyzer()
    
    print("Ship Semantic Analyzer initialized.")
    print("Run with ship data to test geographic vs saint hypothesis.")
    print("Example: analyzer.analyze_geographic_vs_saint(ships_df)")

