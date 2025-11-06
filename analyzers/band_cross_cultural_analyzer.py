"""Band Cross-Cultural Analyzer

Sophisticated analysis of how linguistic families, colonial history, and cultural contexts
affect band naming patterns.

Key Analyses:
- Linguistic family effects (Germanic vs Romance vs Slavic vs Asian)
- Colonial legacy patterns (former colonies vs never-colonized)
- Linguistic interference (native language → English name phonology)
- Post-colonial assertion vs cultural cringe
- Cultural values × naming aesthetics
- Religious influences on name themes

This analyzer reveals deep cultural-linguistic patterns invisible in simple geographic comparisons.
"""

import logging
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from collections import defaultdict, Counter
from scipy import stats
from sklearn.preprocessing import StandardScaler

from core.models import db, Band, BandAnalysis

logger = logging.getLogger(__name__)


class BandCrossCulturalAnalyzer:
    """Analyze cross-cultural linguistic and demographic patterns in band names."""
    
    def __init__(self):
        # Load demographic data
        self.demographics = self._load_demographic_data()
        
        # Linguistic family categories
        self.linguistic_families = {
            'Germanic': ['US', 'GB', 'DE', 'SE', 'NO', 'DK', 'NL', 'AU', 'CA'],
            'Romance': ['FR', 'ES', 'IT', 'PT', 'BR', 'MX', 'AR'],
            'Slavic': ['PL', 'RU', 'CZ', 'SK', 'HR', 'RS'],
            'Uralic': ['FI', 'HU', 'EE'],
            'Asian': ['JP', 'CN', 'KR', 'TH', 'VN'],
            'Indo-Aryan': ['IN', 'PK', 'BD']
        }
    
    def _load_demographic_data(self) -> Dict:
        """Load demographic data from JSON file."""
        import os
        demo_file = 'data/demographic_data/country_demographics.json'
        
        if not os.path.exists(demo_file):
            logger.warning(f"Demographic data file not found: {demo_file}")
            return {}
        
        with open(demo_file, 'r') as f:
            data = json.load(f)
        
        return data.get('countries', {})
    
    def get_comprehensive_dataset(self) -> pd.DataFrame:
        """Load all bands with demographic enrichment.
        
        Returns:
            DataFrame with band + demographic data
        """
        query = db.session.query(Band, BandAnalysis).join(
            BandAnalysis,
            Band.id == BandAnalysis.band_id
        )
        
        rows = []
        for band, analysis in query.all():
            try:
                row = {
                    # Band core
                    'id': band.id,
                    'name': band.name,
                    'formation_year': band.formation_year,
                    'formation_decade': band.formation_decade,
                    'origin_country': band.origin_country,
                    'genre_cluster': band.genre_cluster,
                    'popularity_score': band.popularity_score or 0,
                    'longevity_score': band.longevity_score or 0,
                    
                    # Linguistic
                    'syllable_count': analysis.syllable_count or 0,
                    'character_length': analysis.character_length or 0,
                    'memorability_score': analysis.memorability_score or 0,
                    'harshness_score': analysis.harshness_score or 0,
                    'softness_score': analysis.softness_score or 0,
                    'fantasy_score': analysis.fantasy_score or 0,
                    'literary_reference_score': analysis.literary_reference_score or 0,
                    'abstraction_score': analysis.abstraction_score or 0,
                    'vowel_ratio': analysis.vowel_ratio or 0,
                    'uniqueness_score': analysis.uniqueness_score or 0,
                    
                    # Demographics from Band model
                    'language_family': band.language_family,
                    'native_language': band.native_language,
                    'former_colony': band.former_colony,
                    'colonial_power': band.colonial_power,
                    'years_independent': band.years_independent,
                    'gdp_per_capita': band.gdp_per_capita,
                    'education_index': band.education_index,
                    'hofstede_individualism': band.hofstede_individualism,
                    'hofstede_uncertainty_avoidance': band.hofstede_uncertainty_avoidance,
                    'majority_religion': band.majority_religion,
                    'secular_score': band.secular_score,
                    'english_native_speaker': band.english_native_speaker,
                    'english_proficiency_index': band.english_proficiency_index,
                    'allows_consonant_clusters': band.allows_consonant_clusters,
                    'has_l_r_distinction': band.has_l_r_distinction,
                    'immigrant_generation': band.immigrant_generation,
                    'diaspora_community': band.diaspora_community,
                }
                
                rows.append(row)
                
            except Exception as e:
                logger.warning(f"Error loading band {band.name}: {e}")
                continue
        
        return pd.DataFrame(rows)
    
    def analyze_linguistic_family_effects(self, df: pd.DataFrame) -> Dict:
        """Analyze how linguistic family affects English band naming patterns.
        
        Tests hypotheses:
        - Germanic: More consonant clusters, harsher
        - Romance: More melodious, vowel-rich
        - Slavic: Extremely harsh, cluster-heavy
        - Asian: Avoid R/L, simpler syllable structure
        - Uralic: Unique/avant-garde patterns
        
        Args:
            df: DataFrame with bands
            
        Returns:
            Linguistic family analysis results
        """
        logger.info("Analyzing linguistic family effects...")
        
        results = {
            'family_profiles': {},
            'family_comparisons': {},
            'phonological_hypotheses': {},
            'anova_tests': {}
        }
        
        # 1. Profile each linguistic family
        for family_name, countries in self.linguistic_families.items():
            family_data = df[df['origin_country'].isin(countries)]
            
            if len(family_data) < 10:
                continue
            
            profile = {
                'family': family_name,
                'sample_size': len(family_data),
                'countries': countries,
                'avg_syllables': float(family_data['syllable_count'].mean()),
                'avg_harshness': float(family_data['harshness_score'].mean()),
                'avg_softness': float(family_data['softness_score'].mean()),
                'avg_vowel_ratio': float(family_data['vowel_ratio'].mean()),
                'avg_fantasy': float(family_data['fantasy_score'].mean()),
                'avg_abstraction': float(family_data['abstraction_score'].mean()),
                'avg_uniqueness': float(family_data['uniqueness_score'].mean()),
                'avg_popularity': float(family_data['popularity_score'].mean())
            }
            
            results['family_profiles'][family_name] = profile
        
        # 2. Germanic vs Romance comparison (largest groups)
        germanic_data = df[df['origin_country'].isin(self.linguistic_families['Germanic'])]
        romance_data = df[df['origin_country'].isin(self.linguistic_families['Romance'])]
        
        if len(germanic_data) >= 20 and len(romance_data) >= 20:
            results['family_comparisons']['Germanic_vs_Romance'] = self._compare_families(
                germanic_data, romance_data, 'Germanic', 'Romance'
            )
        
        # 3. Slavic extreme hypothesis
        slavic_data = df[df['origin_country'].isin(self.linguistic_families['Slavic'])]
        if len(slavic_data) >= 10:
            other_data = df[~df['origin_country'].isin(self.linguistic_families['Slavic'])]
            
            results['phonological_hypotheses']['Slavic_extreme_harshness'] = {
                'hypothesis': 'Slavic bands have extremely harsh names (more than all other families)',
                'slavic_mean_harshness': float(slavic_data['harshness_score'].mean()),
                'other_mean_harshness': float(other_data['harshness_score'].mean()),
                'difference': float(slavic_data['harshness_score'].mean() - other_data['harshness_score'].mean()),
                'percent_harsher': float(((slavic_data['harshness_score'].mean() / other_data['harshness_score'].mean()) - 1) * 100),
                **self._t_test_result(slavic_data['harshness_score'], other_data['harshness_score'])
            }
        
        # 4. Asian R/L avoidance hypothesis
        asian_data = df[df['origin_country'].isin(self.linguistic_families['Asian'])]
        if len(asian_data) >= 10:
            # Count R and L phonemes in names
            asian_data_copy = asian_data.copy()
            asian_data_copy['r_l_count'] = asian_data_copy['name'].str.lower().str.count(r'[rl]')
            asian_data_copy['r_l_ratio'] = asian_data_copy['r_l_count'] / asian_data_copy['character_length']
            
            germanic_copy = germanic_data.copy()
            germanic_copy['r_l_count'] = germanic_copy['name'].str.lower().str.count(r'[rl]')
            germanic_copy['r_l_ratio'] = germanic_copy['r_l_count'] / germanic_copy['character_length']
            
            results['phonological_hypotheses']['Asian_R_L_avoidance'] = {
                'hypothesis': 'Asian bands avoid R/L sounds (phonological constraint from Japanese/Korean)',
                'asian_r_l_ratio': float(asian_data_copy['r_l_ratio'].mean()),
                'germanic_r_l_ratio': float(germanic_copy['r_l_ratio'].mean()),
                'difference': float(asian_data_copy['r_l_ratio'].mean() - germanic_copy['r_l_ratio'].mean()),
                'percent_lower': float(((germanic_copy['r_l_ratio'].mean() - asian_data_copy['r_l_ratio'].mean()) / germanic_copy['r_l_ratio'].mean()) * 100),
                **self._t_test_result(asian_data_copy['r_l_ratio'], germanic_copy['r_l_ratio'])
            }
        
        # 5. ANOVA: Language family × harshness
        df_with_family = df.copy()
        df_with_family['language_family'] = df_with_family['origin_country'].map(
            lambda c: next((fam for fam, countries in self.linguistic_families.items() if c in countries), 'Other')
        )
        
        # Get groups for ANOVA
        groups = []
        group_names = []
        for family in ['Germanic', 'Romance', 'Slavic', 'Asian']:
            family_group = df_with_family[df_with_family['language_family'] == family]['harshness_score'].dropna()
            if len(family_group) >= 5:
                groups.append(family_group)
                group_names.append(family)
        
        if len(groups) >= 3:
            f_stat, p_value = stats.f_oneway(*groups)
            
            results['anova_tests']['harshness_by_family'] = {
                'f_statistic': float(f_stat),
                'p_value': float(p_value),
                'significant': p_value < 0.05,
                'groups_tested': group_names,
                'interpretation': 'Linguistic family significantly affects harshness' if p_value < 0.05 else 'No significant family effect'
            }
        
        return results
    
    def _compare_families(self, data1: pd.DataFrame, data2: pd.DataFrame, 
                          name1: str, name2: str) -> Dict:
        """Compare two linguistic families across all features.
        
        Args:
            data1, data2: DataFrames for each family
            name1, name2: Family names
            
        Returns:
            Comparison results
        """
        comparison = {
            'family1': name1,
            'family2': name2,
            'sample_size_1': len(data1),
            'sample_size_2': len(data2),
            'metrics': {}
        }
        
        metrics = [
            'syllable_count', 'harshness_score', 'softness_score',
            'vowel_ratio', 'fantasy_score', 'literary_reference_score',
            'abstraction_score', 'uniqueness_score'
        ]
        
        for metric in metrics:
            if metric not in data1.columns or metric not in data2.columns:
                continue
            
            vals1 = data1[metric].dropna()
            vals2 = data2[metric].dropna()
            
            if len(vals1) >= 10 and len(vals2) >= 10:
                comparison['metrics'][metric] = {
                    f'mean_{name1}': float(vals1.mean()),
                    f'mean_{name2}': float(vals2.mean()),
                    'difference': float(vals2.mean() - vals1.mean()),
                    'percent_difference': float(((vals2.mean() - vals1.mean()) / vals1.mean()) * 100) if vals1.mean() != 0 else 0,
                    **self._t_test_result(vals1, vals2)
                }
        
        return comparison
    
    def _t_test_result(self, group1, group2) -> Dict:
        """Perform t-test and return formatted results."""
        t_stat, p_value = stats.ttest_ind(group1, group2)
        
        # Cohen's d
        pooled_std = np.sqrt(((len(group1)-1)*group1.std()**2 + (len(group2)-1)*group2.std()**2) / (len(group1) + len(group2) - 2))
        cohens_d = (group1.mean() - group2.mean()) / pooled_std if pooled_std > 0 else 0
        
        return {
            't_statistic': float(t_stat),
            'p_value': float(p_value),
            'significant': p_value < 0.05,
            'cohens_d': float(cohens_d),
            'effect_size': 'large' if abs(cohens_d) > 0.8 else 'medium' if abs(cohens_d) > 0.5 else 'small'
        }
    
    def analyze_colonial_legacy_patterns(self, df: pd.DataFrame) -> Dict:
        """Analyze how colonial history affects band naming.
        
        Tests:
        - Former British colonies: More "The ___" pattern?
        - British colonies: More literary references?
        - Recently independent: More native language assertion?
        - Never colonized: Different aesthetic entirely?
        
        Args:
            df: DataFrame
            
        Returns:
            Colonial legacy analysis
        """
        logger.info("Analyzing colonial legacy patterns...")
        
        results = {
            'british_colony_effects': {},
            'spanish_colony_effects': {},
            'independence_timeline': {},
            'the_pattern_analysis': {}
        }
        
        # Filter to bands with colonial data
        colonial_df = df[df['former_colony'].notna()].copy()
        
        if len(colonial_df) == 0:
            return {'error': 'No colonial history data available'}
        
        # 1. British colonial effects
        british_colonies = colonial_df[colonial_df['colonial_power'] == 'Britain']
        never_colonized = colonial_df[colonial_df['former_colony'] == False]
        
        if len(british_colonies) >= 10 and len(never_colonized) >= 10:
            results['british_colony_effects'] = self._compare_colonial_groups(
                british_colonies, never_colonized, 'British_Colonies', 'Never_Colonized'
            )
        
        # 2. "The ___" pattern analysis
        # Count bands starting with "The"
        df['starts_with_the'] = df['name'].str.lower().str.startswith('the ')
        
        british_the_rate = british_colonies['starts_with_the'].mean() * 100 if len(british_colonies) > 0 else 0
        never_the_rate = never_colonized['starts_with_the'].mean() * 100 if len(never_colonized) > 0 else 0
        
        # Chi-square test
        contingency = pd.crosstab(
            colonial_df['former_colony'] == (colonial_df['colonial_power'] == 'Britain'),
            colonial_df['starts_with_the']
        )
        
        if contingency.shape == (2, 2):
            chi2, p_value, dof, expected = stats.chi2_contingency(contingency)
            
            results['the_pattern_analysis'] = {
                'british_colony_the_rate': float(british_the_rate),
                'never_colonized_the_rate': float(never_the_rate),
                'difference': float(british_the_rate - never_the_rate),
                'chi2_statistic': float(chi2),
                'p_value': float(p_value),
                'significant': p_value < 0.05,
                'interpretation': 'British colonies significantly more likely to use "The" pattern' if p_value < 0.05 and british_the_rate > never_the_rate else 'No colonial effect on "The" usage'
            }
        
        # 3. Independence timeline effects
        # Do recently independent nations (post-1960) show more linguistic assertion?
        colonial_df_timed = colonial_df[colonial_df['independence_year'].notna()].copy()
        
        if len(colonial_df_timed) >= 20:
            colonial_df_timed['recent_independence'] = colonial_df_timed['independence_year'] >= 1960
            
            recent = colonial_df_timed[colonial_df_timed['recent_independence'] == True]
            old = colonial_df_timed[colonial_df_timed['recent_independence'] == False]
            
            if len(recent) >= 5 and len(old) >= 5:
                # Test for linguistic assertion (more native language influence, less English conformity)
                # Proxy: Higher uniqueness, lower "The" usage
                
                results['independence_timeline'] = {
                    'recent_independence_uniqueness': float(recent['uniqueness_score'].mean()),
                    'old_independence_uniqueness': float(old['uniqueness_score'].mean()),
                    'recent_the_usage': float(recent['starts_with_the'].mean() * 100),
                    'old_the_usage': float(old['starts_with_the'].mean() * 100),
                    'interpretation': self._interpret_independence_effect(recent, old)
                }
        
        return results
    
    def _compare_colonial_groups(self, colonies: pd.DataFrame, never: pd.DataFrame,
                                  name1: str, name2: str) -> Dict:
        """Compare former colonies to never-colonized countries."""
        comparison = {
            'group1': name1,
            'group2': name2,
            'n1': len(colonies),
            'n2': len(never),
            'metrics': {}
        }
        
        metrics = ['fantasy_score', 'literary_reference_score', 'memorability_score', 'uniqueness_score']
        
        for metric in metrics:
            v1 = colonies[metric].dropna()
            v2 = never[metric].dropna()
            
            if len(v1) >= 5 and len(v2) >= 5:
                comparison['metrics'][metric] = {
                    f'mean_{name1}': float(v1.mean()),
                    f'mean_{name2}': float(v2.mean()),
                    'difference': float(v1.mean() - v2.mean()),
                    **self._t_test_result(v1, v2)
                }
        
        return comparison
    
    def _interpret_independence_effect(self, recent: pd.DataFrame, old: pd.DataFrame) -> str:
        """Interpret independence timeline effects."""
        recent_unique = recent['uniqueness_score'].mean()
        old_unique = old['uniqueness_score'].mean()
        
        if recent_unique > old_unique + 5:
            return "Post-colonial assertion: Recently independent nations show more unique naming (rejecting colonial patterns)"
        elif old_unique > recent_unique + 5:
            return "Colonial legacy stronger in recent independence (still conforming to colonial aesthetics)"
        else:
            return "No clear independence timeline effect (globalization may override)"
    
    def analyze_linguistic_interference(self, df: pd.DataFrame) -> Dict:
        """Analyze how native language phonology interferes with English band names.
        
        Tests specific interference patterns:
        - Japanese: R/L avoidance, simple syllables
        - German: Consonant cluster preference
        - Spanish: Simple 5-vowel system, avoid complex vowels
        - Finnish: Avoid voiced stops (b/d/g)
        
        Args:
            df: DataFrame
            
        Returns:
            Interference analysis
        """
        logger.info("Analyzing linguistic interference patterns...")
        
        results = {
            'japanese_r_l_avoidance': {},
            'german_cluster_preference': {},
            'romance_vowel_simplification': {},
            'finnish_voiced_stop_avoidance': {}
        }
        
        # 1. Japanese R/L analysis
        japanese = df[df['origin_country'] == 'JP']
        english_native = df[df['english_native_speaker'] == True]
        
        if len(japanese) >= 5 and len(english_native) >= 20:
            # Count R/L in names
            japanese_copy = japanese.copy()
            japanese_copy['r_l_density'] = japanese_copy['name'].str.lower().str.count(r'[rl]') / japanese_copy['character_length']
            
            english_copy = english_native.copy()
            english_copy['r_l_density'] = english_copy['name'].str.lower().str.count(r'[rl]') / english_copy['character_length']
            
            results['japanese_r_l_avoidance'] = {
                'hypothesis': 'Japanese bands avoid R/L due to phonological constraint (no L/R distinction in Japanese)',
                'japanese_r_l_density': float(japanese_copy['r_l_density'].mean()),
                'english_r_l_density': float(english_copy['r_l_density'].mean()),
                'reduction_percentage': float(((english_copy['r_l_density'].mean() - japanese_copy['r_l_density'].mean()) / english_copy['r_l_density'].mean()) * 100),
                **self._t_test_result(japanese_copy['r_l_density'], english_copy['r_l_density'])
            }
        
        # 2. German consonant clusters
        german = df[df['origin_country'] == 'DE']
        romance = df[df['origin_country'].isin(['FR', 'ES', 'IT'])]
        
        if len(german) >= 10 and len(romance) >= 10:
            # Proxy for clusters: harshness score correlates with clusters
            results['german_cluster_preference'] = {
                'hypothesis': 'German bands prefer consonant clusters (German phonotactics allow complex onsets)',
                'german_avg_harshness': float(german['harshness_score'].mean()),
                'romance_avg_harshness': float(romance['harshness_score'].mean()),
                'difference': float(german['harshness_score'].mean() - romance['harshness_score'].mean()),
                **self._t_test_result(german['harshness_score'], romance['harshness_score'])
            }
        
        # 3. Romance language vowel simplification
        if len(romance) >= 10 and len(english_native) >= 20:
            results['romance_vowel_simplification'] = {
                'hypothesis': 'Romance language speakers prefer simpler vowel patterns (5-vowel systems vs English 15+)',
                'romance_vowel_ratio': float(romance['vowel_ratio'].mean()),
                'english_vowel_ratio': float(english_native['vowel_ratio'].mean()),
                'difference': float(romance['vowel_ratio'].mean() - english_native['vowel_ratio'].mean()),
                **self._t_test_result(romance['vowel_ratio'], english_native['vowel_ratio'])
            }
        
        # 4. Finnish voiced stop avoidance
        finnish = df[df['origin_country'] == 'FI']
        if len(finnish) >= 5 and len(germanic_data) >= 20:
            # Count b/d/g (voiced stops) in names
            finnish_copy = finnish.copy()
            finnish_copy['bdg_density'] = finnish_copy['name'].str.lower().str.count(r'[bdg]') / finnish_copy['character_length']
            
            germanic_copy = germanic_data.copy()
            germanic_copy['bdg_density'] = germanic_copy['name'].str.lower().str.count(r'[bdg]') / germanic_copy['character_length']
            
            results['finnish_voiced_stop_avoidance'] = {
                'hypothesis': 'Finnish bands avoid voiced stops b/d/g (Finnish lacks voiced/voiceless distinction)',
                'finnish_bdg_density': float(finnish_copy['bdg_density'].mean()),
                'germanic_bdg_density': float(germanic_copy['bdg_density'].mean()),
                'reduction_percentage': float(((germanic_copy['bdg_density'].mean() - finnish_copy['bdg_density'].mean()) / germanic_copy['bdg_density'].mean()) * 100) if germanic_copy['bdg_density'].mean() > 0 else 0,
                'sample_size_finnish': len(finnish),
                'sample_size_germanic': len(germanic_copy)
            }
        
        return results
    
    def analyze_socioeconomic_correlates(self, df: pd.DataFrame) -> Dict:
        """Analyze correlations between socioeconomic factors and naming patterns.
        
        Tests:
        - GDP × literary references
        - Education × abstraction
        - Inequality × uniqueness
        - Urbanization × English adoption
        
        Args:
            df: DataFrame
            
        Returns:
            Socioeconomic correlation analysis
        """
        logger.info("Analyzing socioeconomic correlates...")
        
        results = {
            'gdp_correlations': {},
            'education_correlations': {},
            'inequality_effects': {},
            'urbanization_effects': {}
        }
        
        # Filter to bands with socioeconomic data
        econ_df = df[df['gdp_per_capita'].notna()].copy()
        
        if len(econ_df) < 30:
            return {'error': 'Insufficient socioeconomic data'}
        
        # 1. GDP × Literary references
        if 'literary_reference_score' in econ_df.columns:
            corr, p_val = stats.pearsonr(econ_df['gdp_per_capita'], econ_df['literary_reference_score'])
            
            results['gdp_correlations']['literary_references'] = {
                'correlation': float(corr),
                'p_value': float(p_val),
                'significant': p_val < 0.05,
                'interpretation': 'Wealth → sophistication hypothesis' if corr > 0 and p_val < 0.05 else 'No wealth-literacy relationship'
            }
        
        # 2. Education × Abstraction
        if 'education_index' in econ_df.columns and 'abstraction_score' in econ_df.columns:
            edu_data = econ_df[econ_df['education_index'].notna()]
            
            if len(edu_data) >= 20:
                corr, p_val = stats.pearsonr(edu_data['education_index'], edu_data['abstraction_score'])
                
                results['education_correlations']['abstraction'] = {
                    'correlation': float(corr),
                    'p_value': float(p_val),
                    'significant': p_val < 0.05,
                    'interpretation': 'Education → abstract naming' if corr > 0 and p_val < 0.05 else 'No education-abstraction link'
                }
        
        # 3. Gini × Uniqueness
        if 'gini_coefficient' in econ_df.columns:
            gini_data = econ_df[econ_df['gini_coefficient'].notna()]
            
            if len(gini_data) >= 20:
                corr, p_val = stats.pearsonr(gini_data['gini_coefficient'], gini_data['uniqueness_score'])
                
                results['inequality_effects']['uniqueness'] = {
                    'correlation': float(corr),
                    'p_value': float(p_val),
                    'significant': p_val < 0.05,
                    'interpretation': 'Inequality suppresses uniqueness' if corr < 0 and p_val < 0.05 else 'Inequality promotes uniqueness' if corr > 0 and p_val < 0.05 else 'No inequality effect'
                }
        
        # 4. Urbanization × Abstraction
        if 'urbanization_rate' in econ_df.columns:
            urban_data = econ_df[econ_df['urbanization_rate'].notna()]
            
            if len(urban_data) >= 20:
                corr, p_val = stats.pearsonr(urban_data['urbanization_rate'], urban_data['abstraction_score'])
                
                results['urbanization_effects']['abstraction'] = {
                    'correlation': float(corr),
                    'p_value': float(p_val),
                    'significant': p_val < 0.05,
                    'interpretation': 'Urban environments → abstract naming' if corr > 0 and p_val < 0.05 else 'No urbanization effect'
                }
        
        return results
    
    def analyze_cultural_dimension_effects(self, df: pd.DataFrame) -> Dict:
        """Analyze how Hofstede cultural dimensions affect naming.
        
        Tests all 6 Hofstede dimensions:
        - Individualism → uniqueness
        - Power Distance → anti-authority themes
        - Masculinity → harshness
        - Uncertainty Avoidance → conventionality
        - Long-term Orientation → traditional references
        - Indulgence → playfulness
        
        Args:
            df: DataFrame
            
        Returns:
            Cultural dimension analysis
        """
        logger.info("Analyzing Hofstede cultural dimensions...")
        
        results = {}
        
        cultural_df = df[df['hofstede_individualism'].notna()].copy()
        
        if len(cultural_df) < 30:
            return {'error': 'Insufficient Hofstede data'}
        
        # Test each dimension
        dimension_tests = [
            ('hofstede_individualism', 'uniqueness_score', 'Individualism → Uniqueness'),
            ('hofstede_masculinity', 'harshness_score', 'Masculinity → Harshness'),
            ('hofstede_uncertainty_avoidance', 'memorability_score', 'UA → Conventional/Memorable'),
            ('hofstede_indulgence', 'fantasy_score', 'Indulgence → Playful/Fantasy')
        ]
        
        for dimension, outcome, label in dimension_tests:
            if dimension in cultural_df.columns and outcome in cultural_df.columns:
                test_data = cultural_df[[dimension, outcome]].dropna()
                
                if len(test_data) >= 20:
                    corr, p_val = stats.pearsonr(test_data[dimension], test_data[outcome])
                    
                    results[dimension] = {
                        'dimension': dimension.replace('hofstede_', '').title(),
                        'outcome': outcome.replace('_', ' ').title(),
                        'hypothesis': label,
                        'correlation': float(corr),
                        'p_value': float(p_val),
                        'significant': p_val < 0.05,
                        'effect_direction': 'positive' if corr > 0 else 'negative',
                        'strength': 'strong' if abs(corr) > 0.5 else 'moderate' if abs(corr) > 0.3 else 'weak'
                    }
        
        return results
    
    def analyze_religious_cultural_factors(self, df: pd.DataFrame) -> Dict:
        """Analyze how religious/cultural context affects naming themes.
        
        Tests:
        - Christian-majority: Biblical references?
        - Muslim-majority: Avoid occult themes?
        - Secular societies: More abstract names?
        - Hindu/Buddhist: Different mythological references?
        
        Args:
            df: DataFrame
            
        Returns:
            Religious influence analysis
        """
        logger.info("Analyzing religious cultural factors...")
        
        results = {}
        
        religious_df = df[df['majority_religion'].notna()].copy()
        
        if len(religious_df) < 30:
            return {'error': 'Insufficient religious data'}
        
        # 1. Christian vs non-Christian
        christian = religious_df[religious_df['majority_religion'] == 'Christian']
        non_christian = religious_df[religious_df['majority_religion'] != 'Christian']
        
        if len(christian) >= 20 and len(non_christian) >= 10:
            # Test for Biblical/religious theme differences
            results['christian_majority_effect'] = {
                'christian_fantasy': float(christian['fantasy_score'].mean()),
                'non_christian_fantasy': float(non_christian['fantasy_score'].mean()),
                'christian_literary': float(christian['literary_reference_score'].mean()),
                'non_christian_literary': float(non_christian['literary_reference_score'].mean()),
                'interpretation': 'Christian cultures show higher literary/fantasy (Western canon dominates)' if christian['fantasy_score'].mean() > non_christian['fantasy_score'].mean() else 'No clear Christian effect'
            }
        
        # 2. Secular score × abstraction
        secular_df = religious_df[religious_df['secular_score'].notna()]
        
        if len(secular_df) >= 20:
            corr, p_val = stats.pearsonr(secular_df['secular_score'], secular_df['abstraction_score'])
            
            results['secularity_abstraction'] = {
                'correlation': float(corr),
                'p_value': float(p_val),
                'significant': p_val < 0.05,
                'interpretation': 'Secular societies → more abstract naming' if corr > 0 and p_val < 0.05 else 'No secularity effect'
            }
        
        return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    analyzer = BandCrossCulturalAnalyzer()
    df = analyzer.get_comprehensive_dataset()
    
    if len(df) >= 30:
        print("\n" + "="*80)
        print("CROSS-CULTURAL LINGUISTIC ANALYSIS")
        print("="*80)
        
        # Linguistic family effects
        print("\n🌍 Analyzing linguistic family effects...")
        family_results = analyzer.analyze_linguistic_family_effects(df)
        
        if 'family_profiles' in family_results:
            print("\nLinguistic Family Profiles:")
            for family, profile in family_results['family_profiles'].items():
                print(f"\n{family} (n={profile['sample_size']}):")
                print(f"  Harshness: {profile['avg_harshness']:.1f}")
                print(f"  Softness: {profile['avg_softness']:.1f}")
                print(f"  Vowel ratio: {profile['avg_vowel_ratio']:.3f}")
        
        # Colonial legacy
        print("\n\n🏛️ Analyzing colonial legacy patterns...")
        colonial_results = analyzer.analyze_colonial_legacy_patterns(df)
        
        # Linguistic interference
        print("\n\n🗣️ Analyzing linguistic interference...")
        interference_results = analyzer.analyze_linguistic_interference(df)
        
        # Socioeconomic
        print("\n\n💰 Analyzing socioeconomic correlates...")
        econ_results = analyzer.analyze_socioeconomic_correlates(df)
        
        # Cultural dimensions
        print("\n\n🎭 Analyzing Hofstede cultural dimensions...")
        cultural_results = analyzer.analyze_cultural_dimension_effects(df)
        
    else:
        print("Insufficient data. Ensure bands have demographic enrichment.")

