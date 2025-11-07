"""Immigration Statistical Analyzer - Semantic Meaning Analysis

Comprehensive statistical analysis of immigration patterns by surname SEMANTIC CATEGORY.

PRIMARY RESEARCH QUESTION:
Do toponymic surnames (Galilei="from Galilee", Romano="from Rome") show different 
immigration rates and settlement patterns than occupational (Smith, Baker), descriptive 
(Brown, Long), patronymic (Johnson, O'Brien), or religious surnames?

EXPANDED HYPOTHESES:
H1: Toponymic vs Non-Toponymic Immigration Rates
H2: Toponymic vs Non-Toponymic Settlement Clustering (HHI)
H3: Temporal Dispersion by Semantic Category (Assimilation)
H4: Place Cultural Importance Effect (famous places → different patterns)
H5: Cross-Category Comparisons (all 5 categories)
H6: Semantic × Origin Interactions (Italian toponymic vs Italian occupational)

ANALYTICAL DEPTH:
- Effect sizes (Cohen's d, eta-squared)
- Cross-category ANOVA
- Pairwise comparisons with Bonferroni correction
- Interaction effects
- Place importance correlations
- Temporal trend analysis

Author: Michael Smerconish
Date: November 2025
"""

import logging
import json
import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Optional, Tuple
from collections import Counter, defaultdict
from datetime import datetime

from core.models import db, ImmigrantSurname, ImmigrationRecord, SettlementPattern, SurnameClassification

logger = logging.getLogger(__name__)


class ImmigrationStatisticalAnalyzer:
    """Comprehensive statistical analysis of surname semantic meaning and immigration."""
    
    def __init__(self):
        """Initialize analyzer with statistical parameters."""
        self.min_sample_size = 20  # Minimum for statistical tests
        self.alpha = 0.05  # Significance level
        self.bonferroni_alpha = 0.01  # For multiple comparisons
        
    def run_full_analysis(self) -> Dict:
        """Run complete statistical analysis pipeline.
        
        Returns:
            Comprehensive analysis results
        """
        logger.info("="*70)
        logger.info("IMMIGRATION SURNAME SEMANTIC MEANING ANALYSIS")
        logger.info("="*70)
        
        results = {
            'analysis_date': datetime.now().isoformat(),
            'dataset_summary': self._get_dataset_summary(),
            'primary_hypotheses': {},
            'expanded_analyses': {},
            'cross_category_comparisons': {},
            'interaction_effects': {},
            'temporal_trends': {},
            'place_importance_analysis': {}
        }
        
        # Load data
        logger.info("Loading data from database...")
        surnames_df = self._load_surnames_data()
        immigration_df = self._load_immigration_data()
        settlement_df = self._load_settlement_data()
        
        logger.info(f"Loaded {len(surnames_df)} surnames, {len(immigration_df)} immigration records, {len(settlement_df)} settlement patterns")
        
        if len(surnames_df) == 0:
            logger.error("No surname data found!")
            return {'error': 'No data in database'}
        
        # PRIMARY HYPOTHESES
        
        # H1: Toponymic vs Non-Toponymic Immigration Rates
        logger.info("\n" + "="*70)
        logger.info("H1: Toponymic vs Non-Toponymic Immigration Rates")
        logger.info("="*70)
        results['primary_hypotheses']['H1_toponymic_vs_nontoponlaymic_immigration'] = \
            self.analyze_toponymic_immigration_rates(surnames_df, immigration_df)
        
        # H2: Toponymic vs Non-Toponymic Settlement Clustering
        logger.info("\n" + "="*70)
        logger.info("H2: Toponymic vs Non-Toponymic Settlement Clustering")
        logger.info("="*70)
        results['primary_hypotheses']['H2_toponymic_clustering'] = \
            self.analyze_toponymic_settlement_clustering(surnames_df, settlement_df)
        
        # H3: Temporal Dispersion by Semantic Category
        logger.info("\n" + "="*70)
        logger.info("H3: Temporal Dispersion by Semantic Category")
        logger.info("="*70)
        results['primary_hypotheses']['H3_temporal_dispersion_by_category'] = \
            self.analyze_temporal_dispersion_by_category(surnames_df, settlement_df)
        
        # EXPANDED ANALYSES
        
        # H4: Place Cultural Importance Effect
        logger.info("\n" + "="*70)
        logger.info("H4: Place Cultural Importance Effect")
        logger.info("="*70)
        results['expanded_analyses']['H4_place_importance'] = \
            self.analyze_place_importance_effect(surnames_df, immigration_df, settlement_df)
        
        # H5: Cross-Category Comparisons (All 5 categories)
        logger.info("\n" + "="*70)
        logger.info("H5: Cross-Category Comparisons (ANOVA)")
        logger.info("="*70)
        results['cross_category_comparisons'] = \
            self.analyze_cross_category_comparisons(surnames_df, immigration_df, settlement_df)
        
        # H6: Semantic × Origin Interactions
        logger.info("\n" + "="*70)
        logger.info("H6: Semantic × Origin Interaction Effects")
        logger.info("="*70)
        results['interaction_effects'] = \
            self.analyze_semantic_origin_interactions(surnames_df, immigration_df)
        
        # Descriptive statistics by category
        results['descriptive_statistics'] = self.calculate_descriptive_statistics(
            surnames_df, immigration_df, settlement_df
        )
        
        # Temporal trends
        results['temporal_trends'] = self.analyze_temporal_trends(
            immigration_df, settlement_df
        )
        
        logger.info("\n" + "="*70)
        logger.info("ANALYSIS COMPLETE")
        logger.info("="*70)
        
        return results
    
    def _get_dataset_summary(self) -> Dict:
        """Get summary of dataset."""
        return {
            'total_surnames': ImmigrantSurname.query.count(),
            'toponymic_surnames': ImmigrantSurname.query.filter_by(is_toponymic=True).count(),
            'by_semantic_category': {
                category: ImmigrantSurname.query.filter_by(semantic_category=category).count()
                for category in ['toponymic', 'occupational', 'descriptive', 'patronymic', 'religious']
            },
            'total_immigration_records': ImmigrationRecord.query.count(),
            'total_settlement_patterns': SettlementPattern.query.count()
        }
    
    def _load_surnames_data(self) -> pd.DataFrame:
        """Load surname data into DataFrame."""
        surnames = ImmigrantSurname.query.all()
        
        data = []
        for s in surnames:
            data.append({
                'surname_id': s.id,
                'surname': s.surname,
                'origin_country': s.origin_country,
                'semantic_category': s.semantic_category,
                'is_toponymic': s.is_toponymic,
                'meaning': s.meaning_in_original,
                'place_name': s.place_name,
                'place_importance': s.place_cultural_importance,
                'total_bearers': s.total_bearers_current
            })
        
        return pd.DataFrame(data)
    
    def _load_immigration_data(self) -> pd.DataFrame:
        """Load immigration records into DataFrame."""
        records = ImmigrationRecord.query.all()
        
        data = []
        for r in records:
            data.append({
                'surname_id': r.surname_id,
                'year': r.year,
                'decade': r.decade,
                'wave': r.immigration_wave,
                'count': r.immigrant_count,
                'origin': r.origin_country
            })
        
        return pd.DataFrame(data)
    
    def _load_settlement_data(self) -> pd.DataFrame:
        """Load settlement patterns into DataFrame."""
        patterns = SettlementPattern.query.all()
        
        data = []
        for p in patterns:
            data.append({
                'surname_id': p.surname_id,
                'state': p.state,
                'year': p.year,
                'population': p.population_count,
                'concentration_index': p.concentration_index,
                'is_enclave': p.is_ethnic_enclave,
                'dispersion_score': p.dispersion_score
            })
        
        return pd.DataFrame(data)
    
    def analyze_toponymic_immigration_rates(self, surnames_df: pd.DataFrame,
                                           immigration_df: pd.DataFrame) -> Dict:
        """H1: Test if toponymic surnames have different immigration rates.
        
        Args:
            surnames_df: Surname data
            immigration_df: Immigration records
            
        Returns:
            Statistical test results
        """
        # Merge data
        merged = immigration_df.merge(surnames_df, on='surname_id')
        
        # Calculate total immigration by surname
        immigration_totals = merged.groupby('surname_id').agg({
            'count': 'sum',
            'is_toponymic': 'first',
            'semantic_category': 'first',
            'total_bearers': 'first'
        }).reset_index()
        
        # Calculate immigration rate (per capita)
        immigration_totals['immigration_rate'] = (
            immigration_totals['count'] / immigration_totals['total_bearers']
        )
        
        # Split by toponymic
        toponymic = immigration_totals[immigration_totals['is_toponymic'] == True]
        non_toponymic = immigration_totals[immigration_totals['is_toponymic'] == False]
        
        if len(toponymic) < self.min_sample_size or len(non_toponymic) < self.min_sample_size:
            return {
                'error': 'Insufficient sample sizes',
                'toponymic_n': len(toponymic),
                'non_toponymic_n': len(non_toponymic)
            }
        
        # T-test
        t_stat, p_value = stats.ttest_ind(
            toponymic['immigration_rate'],
            non_toponymic['immigration_rate']
        )
        
        # Effect size (Cohen's d)
        cohens_d = self._calculate_cohens_d(
            toponymic['immigration_rate'],
            non_toponymic['immigration_rate']
        )
        
        # Correlation
        correlation, corr_p = stats.pearsonr(
            immigration_totals['is_toponymic'].astype(int),
            immigration_totals['immigration_rate']
        )
        
        results = {
            'sample_sizes': {
                'toponymic': len(toponymic),
                'non_toponymic': len(non_toponymic)
            },
            'descriptive_statistics': {
                'toponymic': {
                    'mean_rate': float(toponymic['immigration_rate'].mean()),
                    'median_rate': float(toponymic['immigration_rate'].median()),
                    'std_rate': float(toponymic['immigration_rate'].std())
                },
                'non_toponymic': {
                    'mean_rate': float(non_toponymic['immigration_rate'].mean()),
                    'median_rate': float(non_toponymic['immigration_rate'].median()),
                    'std_rate': float(non_toponymic['immigration_rate'].std())
                }
            },
            'hypothesis_test': {
                't_statistic': float(t_stat),
                'p_value': float(p_value),
                'significant': p_value < self.alpha,
                'effect_size_cohens_d': float(cohens_d),
                'interpretation': self._interpret_cohens_d(cohens_d)
            },
            'correlation': {
                'r': float(correlation),
                'p_value': float(corr_p),
                'r_squared': float(correlation ** 2)
            },
            'conclusion': self._generate_h1_conclusion(p_value, cohens_d, toponymic, non_toponymic)
        }
        
        logger.info(f"H1 Results: t={t_stat:.3f}, p={p_value:.4f}, d={cohens_d:.3f}")
        
        return results
    
    def analyze_toponymic_settlement_clustering(self, surnames_df: pd.DataFrame,
                                               settlement_df: pd.DataFrame) -> Dict:
        """H2: Test if toponymic surnames cluster more geographically."""
        # Merge data
        merged = settlement_df.merge(surnames_df, on='surname_id')
        
        # Calculate HHI for each surname (using most recent year)
        hhi_by_surname = []
        
        for surname_id in merged['surname_id'].unique():
            surname_data = merged[merged['surname_id'] == surname_id]
            is_toponymic = surname_data['is_toponymic'].iloc[0]
            
            recent_year = surname_data['year'].max()
            recent_data = surname_data[surname_data['year'] == recent_year]
            
            total_pop = recent_data['population'].sum()
            if total_pop > 0:
                shares = recent_data['population'] / total_pop
                hhi = (shares ** 2).sum() * 10000
                
                hhi_by_surname.append({
                    'surname_id': surname_id,
                    'is_toponymic': is_toponymic,
                    'hhi': hhi,
                    'num_states': len(recent_data)
                })
        
        hhi_df = pd.DataFrame(hhi_by_surname)
        
        # Split by toponymic
        toponymic = hhi_df[hhi_df['is_toponymic'] == True]
        non_toponymic = hhi_df[hhi_df['is_toponymic'] == False]
        
        if len(toponymic) < self.min_sample_size or len(non_toponymic) < self.min_sample_size:
            return {
                'error': 'Insufficient sample sizes',
                'toponymic_n': len(toponymic),
                'non_toponymic_n': len(non_toponymic)
            }
        
        # T-test
        t_stat, p_value = stats.ttest_ind(
            toponymic['hhi'],
            non_toponymic['hhi']
        )
        
        # Effect size
        cohens_d = self._calculate_cohens_d(
            toponymic['hhi'],
            non_toponymic['hhi']
        )
        
        results = {
            'sample_sizes': {
                'toponymic': len(toponymic),
                'non_toponymic': len(non_toponymic)
            },
            'descriptive_statistics': {
                'toponymic': {
                    'mean_hhi': float(toponymic['hhi'].mean()),
                    'median_hhi': float(toponymic['hhi'].median()),
                    'mean_num_states': float(toponymic['num_states'].mean())
                },
                'non_toponymic': {
                    'mean_hhi': float(non_toponymic['hhi'].mean()),
                    'median_hhi': float(non_toponymic['hhi'].median()),
                    'mean_num_states': float(non_toponymic['num_states'].mean())
                }
            },
            'hypothesis_test': {
                't_statistic': float(t_stat),
                'p_value': float(p_value),
                'significant': p_value < self.alpha,
                'effect_size_cohens_d': float(cohens_d),
                'interpretation': self._interpret_cohens_d(cohens_d)
            },
            'conclusion': self._generate_h2_conclusion(p_value, cohens_d, toponymic, non_toponymic)
        }
        
        logger.info(f"H2 Results: t={t_stat:.3f}, p={p_value:.4f}, d={cohens_d:.3f}")
        
        return results
    
    def analyze_temporal_dispersion_by_category(self, surnames_df: pd.DataFrame,
                                                settlement_df: pd.DataFrame) -> Dict:
        """H3: Analyze dispersion over time by semantic category."""
        # Merge
        merged = settlement_df.merge(surnames_df, on='surname_id')
        
        # Calculate dispersion change for each surname
        dispersion_changes = []
        
        for surname_id in merged['surname_id'].unique():
            surname_data = merged[merged['surname_id'] == surname_id]
            category = surname_data['semantic_category'].iloc[0]
            
            years = sorted(surname_data['year'].unique())
            if len(years) < 2:
                continue
            
            early_year = years[0]
            late_year = years[-1]
            
            early_dispersion = surname_data[surname_data['year'] == early_year]['dispersion_score'].mean()
            late_dispersion = surname_data[surname_data['year'] == late_year]['dispersion_score'].mean()
            
            dispersion_change = late_dispersion - early_dispersion
            
            dispersion_changes.append({
                'surname_id': surname_id,
                'semantic_category': category,
                'early_dispersion': early_dispersion,
                'late_dispersion': late_dispersion,
                'dispersion_change': dispersion_change,
                'years_elapsed': late_year - early_year
            })
        
        dispersion_df = pd.DataFrame(dispersion_changes)
        
        # Test if dispersion increases over time
        t_stat_overall, p_value_overall = stats.ttest_1samp(dispersion_df['dispersion_change'], 0)
        
        # Compare across categories
        category_results = {}
        for category in dispersion_df['semantic_category'].unique():
            cat_data = dispersion_df[dispersion_df['semantic_category'] == category]
            if len(cat_data) >= self.min_sample_size:
                t_stat, p_value = stats.ttest_1samp(cat_data['dispersion_change'], 0)
                category_results[category] = {
                    'n': len(cat_data),
                    'mean_change': float(cat_data['dispersion_change'].mean()),
                    't_statistic': float(t_stat),
                    'p_value': float(p_value),
                    'significant': p_value < self.alpha
                }
        
        results = {
            'overall_trend': {
                'n': len(dispersion_df),
                'mean_change': float(dispersion_df['dispersion_change'].mean()),
                't_statistic': float(t_stat_overall),
                'p_value': float(p_value_overall),
                'significant': p_value_overall < self.alpha,
                'interpretation': 'Dispersion increases over time' if p_value_overall < self.alpha else 'No significant trend'
            },
            'by_semantic_category': category_results,
            'conclusion': f"Overall dispersion {'significantly increases' if p_value_overall < self.alpha else 'does not significantly change'} over time (p={p_value_overall:.4f})"
        }
        
        logger.info(f"H3 Results: Overall t={t_stat_overall:.3f}, p={p_value_overall:.4f}")
        
        return results
    
    def analyze_place_importance_effect(self, surnames_df: pd.DataFrame,
                                       immigration_df: pd.DataFrame,
                                       settlement_df: pd.DataFrame) -> Dict:
        """H4: Test if place cultural importance affects patterns (toponymic only)."""
        # Filter to toponymic surnames with place importance data
        toponymic = surnames_df[
            (surnames_df['is_toponymic'] == True) &
            (surnames_df['place_importance'].notna())
        ]
        
        if len(toponymic) < self.min_sample_size:
            return {'error': 'Insufficient toponymic surnames with place importance data'}
        
        # Merge with immigration data
        merged_immig = immigration_df.merge(toponymic, on='surname_id')
        immigration_totals = merged_immig.groupby('surname_id').agg({
            'count': 'sum',
            'place_importance': 'first',
            'total_bearers': 'first'
        }).reset_index()
        immigration_totals['immigration_rate'] = immigration_totals['count'] / immigration_totals['total_bearers']
        
        # Correlation: place importance vs immigration rate
        corr_immig, p_immig = stats.pearsonr(
            immigration_totals['place_importance'],
            immigration_totals['immigration_rate']
        )
        
        # Merge with settlement data for HHI
        merged_settle = settlement_df.merge(toponymic, on='surname_id')
        hhi_by_surname = []
        for surname_id in merged_settle['surname_id'].unique():
            surname_data = merged_settle[merged_settle['surname_id'] == surname_id]
            recent_year = surname_data['year'].max()
            recent_data = surname_data[surname_data['year'] == recent_year]
            
            total_pop = recent_data['population'].sum()
            if total_pop > 0:
                shares = recent_data['population'] / total_pop
                hhi = (shares ** 2).sum() * 10000
                place_importance = surname_data['place_importance'].iloc[0]
                
                hhi_by_surname.append({
                    'surname_id': surname_id,
                    'hhi': hhi,
                    'place_importance': place_importance
                })
        
        hhi_df = pd.DataFrame(hhi_by_surname)
        
        # Correlation: place importance vs HHI
        if len(hhi_df) >= self.min_sample_size:
            corr_hhi, p_hhi = stats.pearsonr(hhi_df['place_importance'], hhi_df['hhi'])
        else:
            corr_hhi, p_hhi = None, None
        
        results = {
            'immigration_rate_correlation': {
                'n': len(immigration_totals),
                'r': float(corr_immig),
                'p_value': float(p_immig),
                'r_squared': float(corr_immig ** 2),
                'significant': p_immig < self.alpha,
                'interpretation': 'Higher place importance correlates with higher immigration' if corr_immig > 0 and p_immig < self.alpha else 'No significant correlation'
            },
            'settlement_clustering_correlation': {
                'n': len(hhi_df) if corr_hhi else 0,
                'r': float(corr_hhi) if corr_hhi else None,
                'p_value': float(p_hhi) if p_hhi else None,
                'r_squared': float(corr_hhi ** 2) if corr_hhi else None,
                'significant': p_hhi < self.alpha if p_hhi else False
            } if corr_hhi else None,
            'conclusion': f"Place importance {'significantly correlates' if p_immig < self.alpha else 'does not significantly correlate'} with immigration rate"
        }
        
        logger.info(f"H4 Results: r_immigration={corr_immig:.3f}, p={p_immig:.4f}")
        
        return results
    
    def analyze_cross_category_comparisons(self, surnames_df: pd.DataFrame,
                                          immigration_df: pd.DataFrame,
                                          settlement_df: pd.DataFrame) -> Dict:
        """H5: ANOVA comparing all 5 semantic categories."""
        # Merge immigration data
        merged_immig = immigration_df.merge(surnames_df, on='surname_id')
        immigration_totals = merged_immig.groupby('surname_id').agg({
            'count': 'sum',
            'semantic_category': 'first',
            'total_bearers': 'first'
        }).reset_index()
        immigration_totals['immigration_rate'] = immigration_totals['count'] / immigration_totals['total_bearers']
        
        # ANOVA on immigration rates
        categories = immigration_totals['semantic_category'].unique()
        groups = [immigration_totals[immigration_totals['semantic_category'] == cat]['immigration_rate'].values
                 for cat in categories]
        
        f_stat, p_value = stats.f_oneway(*groups)
        
        # Effect size (eta-squared)
        ss_between = sum(len(g) * (np.mean(g) - np.mean(immigration_totals['immigration_rate']))**2 for g in groups)
        ss_total = sum((immigration_totals['immigration_rate'] - np.mean(immigration_totals['immigration_rate']))**2)
        eta_squared = ss_between / ss_total if ss_total > 0 else 0
        
        # Pairwise comparisons with Bonferroni correction
        pairwise = []
        category_list = list(categories)
        for i in range(len(category_list)):
            for j in range(i+1, len(category_list)):
                cat1, cat2 = category_list[i], category_list[j]
                group1 = immigration_totals[immigration_totals['semantic_category'] == cat1]['immigration_rate']
                group2 = immigration_totals[immigration_totals['semantic_category'] == cat2]['immigration_rate']
                
                t_stat, p = stats.ttest_ind(group1, group2)
                cohens_d = self._calculate_cohens_d(group1, group2)
                
                pairwise.append({
                    'comparison': f"{cat1} vs {cat2}",
                    't_statistic': float(t_stat),
                    'p_value': float(p),
                    'bonferroni_significant': p < self.bonferroni_alpha,
                    'cohens_d': float(cohens_d)
                })
        
        # Descriptive stats by category
        descriptive = {}
        for cat in categories:
            cat_data = immigration_totals[immigration_totals['semantic_category'] == cat]['immigration_rate']
            descriptive[cat] = {
                'n': len(cat_data),
                'mean': float(cat_data.mean()),
                'median': float(cat_data.median()),
                'std': float(cat_data.std())
            }
        
        results = {
            'anova': {
                'f_statistic': float(f_stat),
                'p_value': float(p_value),
                'significant': p_value < self.alpha,
                'eta_squared': float(eta_squared),
                'interpretation': 'Significant differences across categories' if p_value < self.alpha else 'No significant differences'
            },
            'descriptive_by_category': descriptive,
            'pairwise_comparisons': pairwise,
            'conclusion': f"{'Significant' if p_value < self.alpha else 'No significant'} differences in immigration rates across semantic categories (F={f_stat:.2f}, p={p_value:.4f})"
        }
        
        logger.info(f"H5 Results: F={f_stat:.3f}, p={p_value:.4f}, η²={eta_squared:.3f}")
        
        return results
    
    def analyze_semantic_origin_interactions(self, surnames_df: pd.DataFrame,
                                            immigration_df: pd.DataFrame) -> Dict:
        """H6: Test for semantic category × origin country interaction effects."""
        # Merge data
        merged = immigration_df.merge(surnames_df, on='surname_id')
        immigration_totals = merged.groupby('surname_id').agg({
            'count': 'sum',
            'semantic_category': 'first',
            'origin_country': 'first',
            'total_bearers': 'first'
        }).reset_index()
        immigration_totals['immigration_rate'] = immigration_totals['count'] / immigration_totals['total_bearers']
        
        # Focus on major origins with multiple categories
        major_origins = ['Italian', 'English', 'German', 'Spanish']
        
        interaction_results = {}
        for origin in major_origins:
            origin_data = immigration_totals[immigration_totals['origin_country'] == origin]
            
            if len(origin_data) < 30:  # Need enough data
                continue
            
            # Compare categories within this origin
            categories_present = origin_data['semantic_category'].unique()
            if len(categories_present) >= 2:
                groups = [origin_data[origin_data['semantic_category'] == cat]['immigration_rate'].values
                         for cat in categories_present]
                
                try:
                    f_stat, p_value = stats.f_oneway(*groups)
                    
                    interaction_results[origin] = {
                        'n': len(origin_data),
                        'categories': list(categories_present),
                        'f_statistic': float(f_stat),
                        'p_value': float(p_value),
                        'significant': p_value < self.alpha,
                        'mean_by_category': {
                            cat: float(origin_data[origin_data['semantic_category'] == cat]['immigration_rate'].mean())
                            for cat in categories_present
                        }
                    }
                except:
                    continue
        
        results = {
            'by_origin_country': interaction_results,
            'conclusion': f"Tested semantic × origin interactions for {len(interaction_results)} major origin countries"
        }
        
        logger.info(f"H6 Results: Analyzed {len(interaction_results)} origin countries")
        
        return results
    
    def calculate_descriptive_statistics(self, surnames_df: pd.DataFrame,
                                        immigration_df: pd.DataFrame,
                                        settlement_df: pd.DataFrame) -> Dict:
        """Calculate comprehensive descriptive statistics."""
        stats_dict = {
            'by_semantic_category': {},
            'overall': {}
        }
        
        # Overall
        stats_dict['overall'] = {
            'total_surnames': len(surnames_df),
            'categories': surnames_df['semantic_category'].value_counts().to_dict()
        }
        
        # By category
        for category in surnames_df['semantic_category'].unique():
            cat_df = surnames_df[surnames_df['semantic_category'] == category]
            stats_dict['by_semantic_category'][category] = {
                'count': len(cat_df),
                'percentage': float(len(cat_df) / len(surnames_df) * 100),
                'mean_bearers': float(cat_df['total_bearers'].mean()) if 'total_bearers' in cat_df else None
            }
        
        return stats_dict
    
    def analyze_temporal_trends(self, immigration_df: pd.DataFrame,
                               settlement_df: pd.DataFrame) -> Dict:
        """Analyze temporal trends."""
        trends = {
            'immigration_by_decade': {},
            'settlement_dispersion_over_time': {}
        }
        
        # Immigration by decade
        by_decade = immigration_df.groupby('decade')['count'].sum()
        for decade, count in by_decade.items():
            trends['immigration_by_decade'][int(decade)] = int(count)
        
        # Dispersion over time
        by_year = settlement_df.groupby('year')['dispersion_score'].mean()
        for year, dispersion in by_year.items():
            trends['settlement_dispersion_over_time'][int(year)] = float(dispersion)
        
        return trends
    
    def _calculate_cohens_d(self, group1: pd.Series, group2: pd.Series) -> float:
        """Calculate Cohen's d effect size."""
        n1, n2 = len(group1), len(group2)
        var1, var2 = group1.var(), group2.var()
        pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
        d = (group1.mean() - group2.mean()) / pooled_std if pooled_std > 0 else 0
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
    
    def _generate_h1_conclusion(self, p_value: float, cohens_d: float,
                               toponymic: pd.DataFrame, non_toponymic: pd.DataFrame) -> str:
        """Generate conclusion for H1."""
        if p_value < self.alpha:
            diff = toponymic['immigration_rate'].mean() - non_toponymic['immigration_rate'].mean()
            direction = "higher" if diff > 0 else "lower"
            return f"Toponymic surnames show significantly {direction} immigration rates than non-toponymic surnames (p={p_value:.4f}, d={cohens_d:.3f})"
        else:
            return f"No significant difference in immigration rates between toponymic and non-toponymic surnames (p={p_value:.4f})"
    
    def _generate_h2_conclusion(self, p_value: float, cohens_d: float,
                               toponymic: pd.DataFrame, non_toponymic: pd.DataFrame) -> str:
        """Generate conclusion for H2."""
        if p_value < self.alpha:
            diff = toponymic['hhi'].mean() - non_toponymic['hhi'].mean()
            direction = "higher" if diff > 0 else "lower"
            return f"Toponymic surnames show significantly {direction} geographic clustering (HHI) than non-toponymic surnames (p={p_value:.4f}, d={cohens_d:.3f})"
        else:
            return f"No significant difference in geographic clustering between toponymic and non-toponymic surnames (p={p_value:.4f})"
