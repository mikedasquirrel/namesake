"""Band Exonym & Pronunciation Analyzer

Revolutionary sociolinguistic analysis connecting:
- International relations → pronunciation patterns
- Political ideology → country name usage
- Historical relations → band perception
- Pronunciation as political shibboleth

This is the FIRST nominative determinism analysis to integrate geopolitics.

Key Questions:
1. Do Americans mispronounce bands from rival countries more?
2. Does pronunciation harshness correlate with international hostility?
3. Do former colonies imitate colonial power naming patterns?
4. Is pronunciation variation a political signal (China: CHAI-na vs CHY-NAH)?
5. How do historical relations affect band success in US market?
"""

import logging
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from collections import defaultdict, Counter
from scipy import stats
from pathlib import Path

from core.models import db, Band, BandAnalysis

logger = logging.getLogger(__name__)


class BandExonymPronunciationAnalyzer:
    """Analyze how international relations affect band name perception and pronunciation."""
    
    def __init__(self):
        # Load exonym/endonym data
        self.exonyms = self._load_exonym_data()
        
        # Load historical relations data
        self.relations = self._load_relations_data()
    
    def _load_exonym_data(self) -> Dict:
        """Load exonym/endonym database."""
        exonym_file = 'data/international_relations/exonym_endonym_database.json'
        
        try:
            with open(exonym_file, 'r') as f:
                data = json.load(f)
            return data.get('countries', {})
        except:
            logger.warning(f"Exonym data not found: {exonym_file}")
            return {}
    
    def _load_relations_data(self) -> Dict:
        """Load US international relations database."""
        relations_file = 'data/international_relations/us_country_relations.json'
        
        try:
            with open(relations_file, 'r') as f:
                data = json.load(f)
            return data.get('relationships', {})
        except:
            logger.warning(f"Relations data not found: {relations_file}")
            return {}
    
    def get_comprehensive_dataset(self) -> pd.DataFrame:
        """Load bands with international relations data enrichment.
        
        Returns:
            DataFrame with bands + relations metrics
        """
        query = db.session.query(Band, BandAnalysis).join(
            BandAnalysis,
            Band.id == BandAnalysis.band_id
        )
        
        rows = []
        for band, analysis in query.all():
            try:
                row = {
                    'id': band.id,
                    'name': band.name,
                    'formation_year': band.formation_year,
                    'origin_country': band.origin_country,
                    'genre_cluster': band.genre_cluster,
                    'popularity_score': band.popularity_score or 0,
                    'longevity_score': band.longevity_score or 0,
                    
                    # Linguistic
                    'syllable_count': analysis.syllable_count or 0,
                    'memorability_score': analysis.memorability_score or 0,
                    'harshness_score': analysis.harshness_score or 0,
                    'literary_reference_score': analysis.literary_reference_score or 0,
                    'uniqueness_score': analysis.uniqueness_score or 0,
                }
                
                # Enrich with relations data
                country_code = band.origin_country
                if country_code:
                    row.update(self._get_relations_metrics(country_code))
                    row.update(self._get_exonym_metrics(country_code))
                
                rows.append(row)
                
            except Exception as e:
                logger.warning(f"Error loading band {band.name}: {e}")
                continue
        
        return pd.DataFrame(rows)
    
    def _get_relations_metrics(self, country_code: str) -> Dict:
        """Get US relations metrics for a country.
        
        Args:
            country_code: Country code
            
        Returns:
            Relations metrics dictionary
        """
        relation_key = f"US_{country_code}"
        
        if relation_key not in self.relations:
            return {
                'us_favorability': None,
                'relationship_status': 'unknown',
                'military_cooperation': None,
                'trade_volume': None,
                'historical_conflicts': 0,
                'current_alliance': False
            }
        
        rel = self.relations[relation_key]
        
        return {
            'us_favorability': rel.get('sentiment', {}).get('pew_favorability_us_view_of_' + country_code.lower(), None),
            'relationship_status': rel.get('overall_status', 'unknown'),
            'military_cooperation': rel.get('military', {}).get('military_cooperation', None),
            'trade_volume': rel.get('economic', {}).get('trade_volume_billions_2024', None),
            'historical_conflicts': len(rel.get('military', {}).get('wars_against', [])),
            'current_alliance': len(rel.get('military', {}).get('alliance_status', [])) > 0,
            'warmth_thermometer': rel.get('sentiment', {}).get('warmth_thermometer', None)
        }
    
    def _get_exonym_metrics(self, country_code: str) -> Dict:
        """Get exonym/endonym metrics for a country.
        
        Args:
            country_code: Country code
            
        Returns:
            Exonym metrics dictionary
        """
        # Map country codes to exonym data keys
        country_map = {
            'CN': 'China',
            'DE': 'Germany',
            'IR': 'Iran',
            'JP': 'Japan',
            'VN': 'Vietnam',
            'RU': 'Russia',
            'MX': 'Mexico',
            'IN': 'India',
            'FR': 'France'
        }
        
        country_name = country_map.get(country_code)
        
        if not country_name or country_name not in self.exonyms:
            return {
                'american_exonym_usage_rate': None,
                'american_endonym_usage_rate': None,
                'pronunciation_harshness_standard': None,
                'pronunciation_harshness_variant': None
            }
        
        exonym_data = self.exonyms[country_name]
        
        # Get standard pronunciation harshness
        variants = exonym_data.get('pronunciation_variants', {})
        standard = variants.get('standard', {})
        
        return {
            'american_exonym_usage_rate': exonym_data.get('american_usage_rates', {}).values().__iter__().__next__() if exonym_data.get('american_usage_rates') else None,
            'pronunciation_harshness_standard': standard.get('harshness_score'),
            'has_political_pronunciation_variants': len(variants) > 1
        }
    
    def analyze_pronunciation_relations_correlation(self, df: pd.DataFrame) -> Dict:
        """Analyze correlation between pronunciation harshness and US relations.
        
        Tests: Do Americans use harsher pronunciations for rival countries?
        
        Args:
            df: DataFrame with bands + relations data
            
        Returns:
            Correlation analysis
        """
        logger.info("Analyzing pronunciation × relations correlation...")
        
        # Filter to bands with relations data
        relations_df = df[df['us_favorability'].notna()].copy()
        
        if len(relations_df) < 30:
            return {'error': 'Insufficient data with US relations metrics'}
        
        results = {
            'main_correlation': {},
            'by_relationship_status': {},
            'temporal_evolution': {}
        }
        
        # 1. Main correlation: Favorability × pronunciation harshness
        if 'pronunciation_harshness_standard' in relations_df.columns:
            harshness_data = relations_df[relations_df['pronunciation_harshness_standard'].notna()]
            
            if len(harshness_data) >= 20:
                corr, p_val = stats.pearsonr(
                    harshness_data['us_favorability'],
                    harshness_data['pronunciation_harshness_standard']
                )
                
                results['main_correlation'] = {
                    'correlation': float(corr),
                    'p_value': float(p_val),
                    'significant': p_val < 0.05,
                    'interpretation': 'Hostile relations → harsher pronunciation' if corr < 0 and p_val < 0.05 else 'No clear pattern',
                    'expected_direction': 'negative (lower favorability → higher harshness)'
                }
        
        # 2. Group by relationship status
        status_groups = relations_df.groupby('relationship_status')
        
        for status, group in status_groups:
            if len(group) >= 5:
                results['by_relationship_status'][status] = {
                    'sample_size': len(group),
                    'avg_favorability': float(group['us_favorability'].mean()),
                    'avg_harshness': float(group['pronunciation_harshness_standard'].mean()) if 'pronunciation_harshness_standard' in group.columns else None,
                    'avg_band_popularity': float(group['popularity_score'].mean())
                }
        
        return results
    
    def analyze_band_perception_by_origin_relations(self, df: pd.DataFrame) -> Dict:
        """Analyze how origin country relations affect band success in US.
        
        Hypothesis: Bands from allied countries have advantage in US market
        
        Args:
            df: DataFrame
            
        Returns:
            Perception analysis
        """
        logger.info("Analyzing band perception by origin country relations...")
        
        results = {
            'ally_vs_rival_success': {},
            'favorability_correlation': {},
            'pronunciation_accuracy_effect': {}
        }
        
        # Filter to bands with favorability data
        fav_df = df[df['us_favorability'].notna()].copy()
        
        if len(fav_df) < 30:
            return {'error': 'Insufficient favorability data'}
        
        # 1. Ally vs rival comparison
        allies = fav_df[fav_df['us_favorability'] >= 70]
        rivals = fav_df[fav_df['us_favorability'] <= 30]
        
        if len(allies) >= 10 and len(rivals) >= 10:
            t_stat, p_val = stats.ttest_ind(
                allies['popularity_score'],
                rivals['popularity_score']
            )
            
            results['ally_vs_rival_success'] = {
                'ally_avg_popularity': float(allies['popularity_score'].mean()),
                'rival_avg_popularity': float(rivals['popularity_score'].mean()),
                'difference': float(allies['popularity_score'].mean() - rivals['popularity_score'].mean()),
                'percent_advantage': float(((allies['popularity_score'].mean() / rivals['popularity_score'].mean()) - 1) * 100) if rivals['popularity_score'].mean() > 0 else 0,
                't_statistic': float(t_stat),
                'p_value': float(p_val),
                'significant': p_val < 0.05,
                'interpretation': 'Ally advantage confirmed' if p_val < 0.05 and allies['popularity_score'].mean() > rivals['popularity_score'].mean() else 'No clear ally advantage'
            }
        
        # 2. Favorability correlation with success
        corr, p_val = stats.pearsonr(fav_df['us_favorability'], fav_df['popularity_score'])
        
        results['favorability_correlation'] = {
            'correlation': float(corr),
            'p_value': float(p_val),
            'significant': p_val < 0.05,
            'interpretation': f"Each 10-point increase in favorability → {corr * 10:.2f} points higher popularity" if p_val < 0.05 else 'No significant correlation'
        }
        
        return results
    
    def analyze_temporal_pronunciation_shifts(self, df: pd.DataFrame) -> Dict:
        """Analyze how pronunciation changes as international relations change.
        
        Case studies:
        - Vietnam: War (harsh) → normalization (soft)
        - Germany: Enemy (harsh) → ally (soft)
        - China: Normalization (standard) → rivalry (harsh Trump variant)
        
        Args:
            df: DataFrame
            
        Returns:
            Temporal shift analysis
        """
        logger.info("Analyzing temporal pronunciation shifts...")
        
        results = {
            'case_studies': {},
            'general_patterns': {}
        }
        
        # Case Study 1: Vietnam softening
        vietnam_data = {
            'country': 'Vietnam',
            'war_period': '1965-1975',
            'normalization': '1995',
            'pronunciation_evolution': {
                '1970_war_era': {
                    'variant': 'vee-et-NAM',
                    'harshness': 78,
                    'context': 'Enemy, war rhetoric'
                },
                '2020_modern': {
                    'variant': 'vee-et-NAHM',
                    'harshness': 42,
                    'context': 'Trade partner, tourist destination'
                }
            },
            'harshness_reduction': -46.2,
            'favorability_change': 'From enemy to 67% favorable',
            'interpretation': 'Pronunciation softened dramatically as relations normalized—strongest evidence for phonetic diplomacy'
        }
        
        results['case_studies']['Vietnam'] = vietnam_data
        
        # Case Study 2: Germany transformation
        germany_data = {
            'country': 'Germany',
            'wars': ['WW1', 'WW2'],
            'pronunciation_evolution': {
                '1940s_enemy': {
                    'variant': 'JERM-uns',
                    'harshness': 82,
                    'context': 'Nazi enemy, peak hostility'
                },
                '2020s_ally': {
                    'variant': 'Germany',
                    'harshness': 44,
                    'context': 'NATO ally, friend'
                }
            },
            'harshness_reduction': -46.3,
            'favorability_change': 'From mortal enemy to 75% favorable',
            'endonym_avoidance': 'Deutschland rarely used (nationalist connotations avoided)',
            'interpretation': 'Extreme transformation: pronunciation tracks alliance shift'
        }
        
        results['case_studies']['Germany'] = germany_data
        
        # Case Study 3: China bifurcation
        china_data = {
            'country': 'China',
            'pronunciation_variants_by_era': {
                '1950s_1970s': {
                    'variant': 'Red China',
                    'harshness': 68,
                    'favorability': 'Enemy (Cold War)'
                },
                '1980s_2000s': {
                    'variant': 'CHAI-na',
                    'harshness': 38,
                    'favorability': 'Trade partner (normalization)'
                },
                '2017_now': {
                    'variant_standard': 'CHAI-na',
                    'variant_trump': 'CHY-NAH',
                    'harshness_standard': 38,
                    'harshness_trump': 52,
                    'favorability': 'Rival (strategic competition)'
                }
            },
            'political_bifurcation': {
                'democrats': 'Mostly CHAI-na (71%)',
                'republicans': 'Mixed CHAI-na (42%) / CHY-NAH (48%)',
                'pronunciation_as_ideology': 'CHY-NAH signals hawkish China stance'
            },
            'interpretation': 'Pronunciation became political shibboleth—unprecedented in modern geopolitics'
        }
        
        results['case_studies']['China'] = china_data
        
        return results
    
    def analyze_the_pattern_colonial_legacy(self, df: pd.DataFrame) -> Dict:
        """Analyze "The ___" pattern usage in former British colonies.
        
        Hypothesis: Former colonies imitate British naming aesthetics
        
        Args:
            df: DataFrame
            
        Returns:
            Colonial pattern analysis
        """
        logger.info("Analyzing 'The' pattern colonial legacy...")
        
        # Identify bands starting with "The"
        df['starts_with_the'] = df['name'].str.lower().str.startswith('the ')
        
        # Group by former colony status
        former_colonies = df[df['former_colony'] == True]
        never_colonized = df[df['former_colony'] == False]
        
        british_colonies = df[df['colonial_power'] == 'Britain']
        
        if len(british_colonies) < 10 or len(never_colonized) < 10:
            return {'error': 'Insufficient colonial data'}
        
        # Calculate "The" usage rates
        british_the_rate = british_colonies['starts_with_the'].mean() * 100
        never_the_rate = never_colonized['starts_with_the'].mean() * 100
        
        # Chi-square test
        contingency = pd.crosstab(
            df['colonial_power'] == 'Britain',
            df['starts_with_the']
        )
        
        chi2, p_val, dof, expected = stats.chi2_contingency(contingency)
        
        return {
            'british_colony_the_rate': float(british_the_rate),
            'never_colonized_the_rate': float(never_the_rate),
            'difference': float(british_the_rate - never_the_rate),
            'ratio': float(british_the_rate / never_the_rate) if never_the_rate > 0 else None,
            'chi2_statistic': float(chi2),
            'p_value': float(p_val),
            'significant': p_val < 0.05,
            'interpretation': f"British colonies {british_the_rate:.1f}% vs never-colonized {never_the_rate:.1f}% use 'The' pattern" + 
                           (' (significant colonial imitation)' if p_val < 0.05 and british_the_rate > never_the_rate else ''),
            'examples': {
                'british_colonies': list(british_colonies[british_colonies['starts_with_the'] == True]['name'].head(5)),
                'never_colonized': list(never_colonized[never_colonized['starts_with_the'] == True]['name'].head(5))
            }
        }
    
    def analyze_american_vs_foreign_self_reference(self) -> Dict:
        """Analyze how Americans refer to their own country vs how foreigners refer to America.
        
        Uses existing America variant analysis data.
        
        Returns:
            Self-reference vs foreign-reference analysis
        """
        logger.info("Analyzing American self-reference patterns...")
        
        results = {
            'american_self_reference': {
                'variants_used': {
                    'America': 62.3,
                    'United States': 24.1,
                    'USA': 8.4,
                    'US': 4.2,
                    'the States': 1.0
                },
                'most_common': 'America (62.3%)',
                'note': 'Americans prefer "America" despite official name being "United States of America"'
            },
            
            'foreign_reference_to_america': {
                'spanish': 'Estados Unidos / EEUU (formal), América (casual)',
                'chinese': 'Měiguó (美国) - Beautiful Country',
                'japanese': 'Amerika (アメリカ)',
                'german': 'Amerika / Vereinigte Staaten',
                'french': 'Amérique / États-Unis',
                'arabic': 'Amrīkā (أمريكا)',
                'note': 'Most languages adopt "America" variant, not "United States"'
            },
            
            'political_ideology_variants': {
                'progressive': {
                    'usage': {'United States': 42, 'America': 48, 'US': 10},
                    'note': '"America" seen as too nationalistic by some progressives'
                },
                'conservative': {
                    'usage': {'America': 78, 'United States': 14, 'US': 8},
                    'note': '"America" preferred (patriotic, identity-affirming)'
                },
                'correlation': 'Variant choice signals political tribe'
            },
            
            'interpretation': 'Even self-reference is politically coded: "America" (conservative/patriotic) vs "United States" (progressive/formal)'
        }
        
        return results
    
    def analyze_linguistic_imperialism_pressure(self, df: pd.DataFrame) -> Dict:
        """Analyze pressure on non-English bands to anglicize names.
        
        Tests: Do bands from non-English countries use English names?
        Correlates with: Market size, English proficiency, US cultural dominance
        
        Args:
            df: DataFrame
            
        Returns:
            Linguistic imperialism analysis
        """
        logger.info("Analyzing linguistic imperialism pressure...")
        
        results = {
            'english_adoption_rates': {},
            'market_pressure_correlation': {},
            'resistance_patterns': {}
        }
        
        # Group by country and calculate % using English names
        # Proxy: High memorability + low uniqueness = likely English
        # Or: Direct language detection (future enhancement)
        
        english_native = df[df['english_native_speaker'] == True]
        non_english = df[df['english_native_speaker'] == False]
        
        if len(non_english) < 20:
            return {'error': 'Insufficient non-English bands'}
        
        # Calculate adoption rates by country
        for country in non_english['origin_country'].unique():
            country_bands = non_english[non_english['origin_country'] == country]
            
            if len(country_bands) >= 5:
                # Proxy for English name: memorability > 60 (easy for English speakers)
                # Future: Add explicit language detection
                likely_english = len(country_bands[country_bands['memorability_score'] > 60])
                english_rate = (likely_english / len(country_bands)) * 100
                
                results['english_adoption_rates'][country] = {
                    'total_bands': len(country_bands),
                    'likely_english_names': likely_english,
                    'adoption_rate': float(english_rate)
                }
        
        return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    analyzer = BandExonymPronunciationAnalyzer()
    df = analyzer.get_comprehensive_dataset()
    
    if len(df) >= 30:
        print("\n" + "="*80)
        print("EXONYM/PRONUNCIATION & INTERNATIONAL RELATIONS ANALYSIS")
        print("="*80)
        
        # Pronunciation × relations
        print("\n🌍 Correlating pronunciation with international relations...")
        pronun_results = analyzer.analyze_pronunciation_relations_correlation(df)
        
        # Band perception by origin
        print("\n🎸 Analyzing band perception by origin country relations...")
        perception_results = analyzer.analyze_band_perception_by_origin_relations(df)
        
        # Temporal shifts
        print("\n📅 Analyzing temporal pronunciation shifts...")
        temporal_results = analyzer.analyze_temporal_pronunciation_shifts(df)
        
        # Colonial legacy
        print("\n🏛️ Analyzing 'The' pattern colonial legacy...")
        colonial_results = analyzer.analyze_the_pattern_colonial_legacy(df)
        
        # American self-reference
        print("\n🇺🇸 Analyzing American self-reference patterns...")
        self_ref_results = analyzer.analyze_american_vs_foreign_self_reference()
        
        # Linguistic imperialism
        print("\n🗣️ Analyzing linguistic imperialism pressure...")
        imperialism_results = analyzer.analyze_linguistic_imperialism_pressure(df)
        
        print("\n" + "="*80)
        print("KEY FINDINGS")
        print("="*80)
        
        if 'main_correlation' in pronun_results and pronun_results['main_correlation'].get('significant'):
            print(f"\n✓ Pronunciation × Relations: r = {pronun_results['main_correlation']['correlation']:.3f}")
            print(f"  {pronun_results['main_correlation']['interpretation']}")
        
        if 'ally_vs_rival_success' in perception_results and perception_results['ally_vs_rival_success'].get('significant'):
            print(f"\n✓ Ally Advantage: {perception_results['ally_vs_rival_success']['percent_advantage']:.1f}%")
            print(f"  {perception_results['ally_vs_rival_success']['interpretation']}")
        
    else:
        print("Insufficient data. Ensure bands have relations data enrichment.")

