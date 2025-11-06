"""Band Geographic Analyzer

Analyzes linguistic patterns across geographic regions.
Tests hypotheses about regional naming styles.

Key Questions:
- UK bands favor mythological/literary references?
- US bands favor simplicity/directness?
- Nordic metal: harsh phonetics?
- Regional archetypes (Seattle grunge, Manchester sound)?
"""

import logging
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from collections import defaultdict, Counter
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

from core.models import db, Band, BandAnalysis

logger = logging.getLogger(__name__)


class BandGeographicAnalyzer:
    """Analyze geographic patterns in band name linguistics."""
    
    def __init__(self):
        # Major music regions to analyze
        self.major_countries = ['US', 'GB', 'CA', 'AU', 'DE', 'SE', 'NO', 'FI']
        self.us_regions = ['US_West', 'US_Northeast', 'US_South', 'US_Midwest']
        self.uk_regions = ['UK_London', 'UK_Manchester', 'UK_Liverpool']
    
    def get_comprehensive_dataset(self) -> pd.DataFrame:
        """Load all bands with geographic and linguistic data.
        
        Returns:
            DataFrame with band data
        """
        query = db.session.query(Band, BandAnalysis).join(
            BandAnalysis,
            Band.id == BandAnalysis.band_id
        ).filter(
            Band.origin_country.isnot(None)
        )
        
        rows = []
        for band, analysis in query.all():
            try:
                row = {
                    # Band metadata
                    'id': band.id,
                    'name': band.name,
                    'formation_year': band.formation_year,
                    'formation_decade': band.formation_decade,
                    'origin_country': band.origin_country,
                    'origin_country_name': band.origin_country_name,
                    'origin_city': band.origin_city,
                    'primary_genre': band.primary_genre,
                    'genre_cluster': band.genre_cluster,
                    
                    # Popularity
                    'popularity_score': band.popularity_score or 0,
                    'longevity_score': band.longevity_score or 0,
                    
                    # Linguistic metrics
                    'syllable_count': analysis.syllable_count,
                    'character_length': analysis.character_length,
                    'word_count': analysis.word_count,
                    'memorability_score': analysis.memorability_score,
                    'pronounceability_score': analysis.pronounceability_score,
                    'uniqueness_score': analysis.uniqueness_score,
                    'fantasy_score': analysis.fantasy_score,
                    'power_connotation_score': analysis.power_connotation_score,
                    'harshness_score': analysis.harshness_score,
                    'softness_score': analysis.softness_score,
                    'abstraction_score': analysis.abstraction_score,
                    'literary_reference_score': analysis.literary_reference_score,
                    'geographic_cluster': analysis.geographic_cluster,
                }
                
                rows.append(row)
                
            except Exception as e:
                logger.warning(f"Error loading band {band.name}: {e}")
                continue
        
        df = pd.DataFrame(rows)
        logger.info(f"Loaded {len(df)} bands for geographic analysis")
        
        return df
    
    def analyze_geographic_patterns(self, df: pd.DataFrame) -> Dict:
        """Analyze linguistic patterns by geography.
        
        Args:
            df: DataFrame with band data
            
        Returns:
            Geographic analysis results
        """
        logger.info("Analyzing geographic patterns...")
        
        results = {
            'country_profiles': {},
            'regional_profiles': {},
            'country_comparisons': {},
            'hypothesis_tests': {},
            'regional_archetypes': {}
        }
        
        # 1. Country profiles
        for country in self.major_countries:
            country_data = df[df['origin_country'] == country]
            if len(country_data) >= 10:
                profile = self._compute_country_profile(country_data, country)
                results['country_profiles'][country] = profile
        
        # 2. US regional profiles
        us_data = df[df['origin_country'] == 'US']
        for region in self.us_regions:
            region_data = us_data[us_data['geographic_cluster'] == region]
            if len(region_data) >= 10:
                profile = self._compute_regional_profile(region_data, region)
                results['regional_profiles'][region] = profile
        
        # 3. UK regional profiles
        uk_data = df[df['origin_country'] == 'GB']
        for region in self.uk_regions:
            region_data = uk_data[uk_data['geographic_cluster'] == region]
            if len(region_data) >= 10:
                profile = self._compute_regional_profile(region_data, region)
                results['regional_profiles'][region] = profile
        
        # 4. Country comparisons
        results['country_comparisons']['US_vs_UK'] = self._compare_countries(df, 'US', 'GB')
        results['country_comparisons']['US_vs_Nordic'] = self._compare_regions(
            df[df['origin_country'] == 'US'],
            df[df['geographic_cluster'] == 'Nordic'],
            'US', 'Nordic'
        )
        
        # 5. Hypothesis tests
        results['hypothesis_tests'] = self._test_geographic_hypotheses(df)
        
        # 6. Regional archetypes
        results['regional_archetypes'] = self._identify_regional_archetypes(df)
        
        return results
    
    def _compute_country_profile(self, country_data: pd.DataFrame, country_code: str) -> Dict:
        """Compute linguistic profile for a country.
        
        Args:
            country_data: DataFrame filtered to one country
            country_code: Country code (e.g., 'US')
            
        Returns:
            Country profile statistics
        """
        profile = {
            'country_code': country_code,
            'country_name': country_data['origin_country_name'].iloc[0] if len(country_data) > 0 else country_code,
            'sample_size': len(country_data),
        }
        
        # Linguistic metrics
        metrics = [
            'syllable_count', 'character_length', 'word_count',
            'memorability_score', 'uniqueness_score',
            'fantasy_score', 'harshness_score', 'softness_score',
            'abstraction_score', 'literary_reference_score'
        ]
        
        for metric in metrics:
            if metric in country_data.columns:
                values = country_data[metric].dropna()
                if len(values) > 0:
                    profile[f"{metric}_mean"] = float(values.mean())
                    profile[f"{metric}_median"] = float(values.median())
                    profile[f"{metric}_std"] = float(values.std())
        
        # Genre distribution
        genre_counts = country_data['genre_cluster'].value_counts()
        profile['top_genres'] = genre_counts.head(5).to_dict()
        
        # Decade distribution
        decade_counts = country_data['formation_decade'].value_counts()
        profile['decade_distribution'] = decade_counts.to_dict()
        
        # Most representative bands (high popularity)
        top_bands = country_data.nlargest(5, 'popularity_score')
        profile['representative_bands'] = top_bands['name'].tolist()
        
        return profile
    
    def _compute_regional_profile(self, region_data: pd.DataFrame, region_name: str) -> Dict:
        """Compute profile for a specific region (e.g., US_West).
        
        Args:
            region_data: DataFrame filtered to one region
            region_name: Region identifier
            
        Returns:
            Regional profile
        """
        profile = {
            'region': region_name,
            'sample_size': len(region_data),
        }
        
        metrics = [
            'syllable_count', 'memorability_score', 'fantasy_score',
            'harshness_score', 'abstraction_score'
        ]
        
        for metric in metrics:
            if metric in region_data.columns:
                values = region_data[metric].dropna()
                if len(values) > 0:
                    profile[f"{metric}_mean"] = float(values.mean())
        
        # Top genres
        genre_counts = region_data['genre_cluster'].value_counts()
        profile['top_genres'] = genre_counts.head(3).to_dict()
        
        # Top cities
        if 'origin_city' in region_data.columns:
            city_counts = region_data['origin_city'].value_counts()
            profile['top_cities'] = city_counts.head(5).to_dict()
        
        # Example bands
        profile['example_bands'] = region_data['name'].head(10).tolist()
        
        return profile
    
    def _compare_countries(self, df: pd.DataFrame, country1: str, country2: str) -> Dict:
        """Compare linguistic profiles between two countries.
        
        Args:
            df: DataFrame with all bands
            country1: First country code
            country2: Second country code
            
        Returns:
            Comparison results
        """
        data1 = df[df['origin_country'] == country1]
        data2 = df[df['origin_country'] == country2]
        
        if len(data1) == 0 or len(data2) == 0:
            return {'error': 'Insufficient data'}
        
        comparison = {
            'country1': country1,
            'country2': country2,
            'sample_size_1': len(data1),
            'sample_size_2': len(data2),
            'metrics': {}
        }
        
        metrics = [
            'syllable_count', 'memorability_score', 'fantasy_score',
            'harshness_score', 'literary_reference_score', 'abstraction_score'
        ]
        
        for metric in metrics:
            if metric not in data1.columns or metric not in data2.columns:
                continue
            
            values1 = data1[metric].dropna()
            values2 = data2[metric].dropna()
            
            if len(values1) > 5 and len(values2) > 5:
                mean1 = values1.mean()
                mean2 = values2.mean()
                
                t_stat, p_value = stats.ttest_ind(values1, values2)
                
                comparison['metrics'][metric] = {
                    f'mean_{country1}': float(mean1),
                    f'mean_{country2}': float(mean2),
                    'difference': float(mean2 - mean1),
                    'percent_difference': float(((mean2 - mean1) / mean1) * 100) if mean1 != 0 else 0,
                    'p_value': float(p_value),
                    'significant': p_value < 0.05,
                    f'{country2}_higher': mean2 > mean1
                }
        
        return comparison
    
    def _compare_regions(self, data1: pd.DataFrame, data2: pd.DataFrame, 
                        region1: str, region2: str) -> Dict:
        """Compare two regions.
        
        Args:
            data1: DataFrame for region 1
            data2: DataFrame for region 2
            region1: Region 1 name
            region2: Region 2 name
            
        Returns:
            Comparison results
        """
        if len(data1) == 0 or len(data2) == 0:
            return {'error': 'Insufficient data'}
        
        comparison = {
            'region1': region1,
            'region2': region2,
            'sample_size_1': len(data1),
            'sample_size_2': len(data2),
            'metrics': {}
        }
        
        metrics = ['syllable_count', 'memorability_score', 'fantasy_score', 'harshness_score']
        
        for metric in metrics:
            if metric in data1.columns and metric in data2.columns:
                values1 = data1[metric].dropna()
                values2 = data2[metric].dropna()
                
                if len(values1) > 5 and len(values2) > 5:
                    t_stat, p_value = stats.ttest_ind(values1, values2)
                    
                    comparison['metrics'][metric] = {
                        f'mean_{region1}': float(values1.mean()),
                        f'mean_{region2}': float(values2.mean()),
                        'difference': float(values2.mean() - values1.mean()),
                        'p_value': float(p_value),
                        'significant': p_value < 0.05
                    }
        
        return comparison
    
    def _test_geographic_hypotheses(self, df: pd.DataFrame) -> Dict:
        """Test specific geographic hypotheses.
        
        Args:
            df: DataFrame with all bands
            
        Returns:
            Hypothesis test results
        """
        hypotheses = {}
        
        # H1: UK bands have higher fantasy/literary scores
        uk_bands = df[df['origin_country'] == 'GB']['fantasy_score'].dropna()
        us_bands = df[df['origin_country'] == 'US']['fantasy_score'].dropna()
        
        if len(uk_bands) > 10 and len(us_bands) > 10:
            t_stat, p_value = stats.ttest_ind(uk_bands, us_bands)
            hypotheses['H1_UK_fantasy_premium'] = {
                'hypothesis': 'UK bands favor mythological/fantasy names more than US',
                'mean_UK': float(uk_bands.mean()),
                'mean_US': float(us_bands.mean()),
                'difference': float(uk_bands.mean() - us_bands.mean()),
                'percent_premium': float(((uk_bands.mean() - us_bands.mean()) / us_bands.mean()) * 100),
                't_statistic': float(t_stat),
                'p_value': float(p_value),
                'supported': p_value < 0.05 and uk_bands.mean() > us_bands.mean()
            }
        
        # H2: UK bands have higher literary reference scores
        uk_literary = df[df['origin_country'] == 'GB']['literary_reference_score'].dropna()
        us_literary = df[df['origin_country'] == 'US']['literary_reference_score'].dropna()
        
        if len(uk_literary) > 10 and len(us_literary) > 10:
            t_stat, p_value = stats.ttest_ind(uk_literary, us_literary)
            hypotheses['H2_UK_literary_premium'] = {
                'hypothesis': 'UK bands have more literary references than US',
                'mean_UK': float(uk_literary.mean()),
                'mean_US': float(us_literary.mean()),
                't_statistic': float(t_stat),
                'p_value': float(p_value),
                'supported': p_value < 0.05 and uk_literary.mean() > us_literary.mean()
            }
        
        # H3: Nordic metal bands have higher harshness
        nordic_bands = df[df['geographic_cluster'] == 'Nordic']
        nordic_metal = nordic_bands[nordic_bands['genre_cluster'] == 'metal']['harshness_score'].dropna()
        other_metal = df[(df['geographic_cluster'] != 'Nordic') & 
                        (df['genre_cluster'] == 'metal')]['harshness_score'].dropna()
        
        if len(nordic_metal) > 5 and len(other_metal) > 10:
            t_stat, p_value = stats.ttest_ind(nordic_metal, other_metal)
            hypotheses['H3_Nordic_metal_harshness'] = {
                'hypothesis': 'Nordic metal bands have harsher names',
                'mean_Nordic': float(nordic_metal.mean()),
                'mean_Other': float(other_metal.mean()),
                't_statistic': float(t_stat),
                'p_value': float(p_value),
                'supported': p_value < 0.05 and nordic_metal.mean() > other_metal.mean()
            }
        
        # H4: US bands favor shorter, punchier names
        uk_syllables = df[df['origin_country'] == 'GB']['syllable_count'].dropna()
        us_syllables = df[df['origin_country'] == 'US']['syllable_count'].dropna()
        
        if len(uk_syllables) > 10 and len(us_syllables) > 10:
            t_stat, p_value = stats.ttest_ind(us_syllables, uk_syllables)
            hypotheses['H4_US_brevity'] = {
                'hypothesis': 'US bands favor shorter names (fewer syllables)',
                'mean_US': float(us_syllables.mean()),
                'mean_UK': float(uk_syllables.mean()),
                't_statistic': float(t_stat),
                'p_value': float(p_value),
                'supported': p_value < 0.05 and us_syllables.mean() < uk_syllables.mean()
            }
        
        # H5: Seattle (US_West grunge) has higher harshness
        seattle_bands = df[df['geographic_cluster'] == 'US_West']
        seattle_grunge = seattle_bands[seattle_bands['genre_cluster'].isin(['grunge', 'alternative'])]['harshness_score'].dropna()
        other_grunge = df[(df['geographic_cluster'] != 'US_West') & 
                         (df['genre_cluster'].isin(['grunge', 'alternative']))]['harshness_score'].dropna()
        
        if len(seattle_grunge) > 5 and len(other_grunge) > 5:
            t_stat, p_value = stats.ttest_ind(seattle_grunge, other_grunge)
            hypotheses['H5_Seattle_grunge_harshness'] = {
                'hypothesis': 'Seattle/US_West grunge bands have harsher names',
                'mean_Seattle': float(seattle_grunge.mean()),
                'mean_Other': float(other_grunge.mean()),
                't_statistic': float(t_stat),
                'p_value': float(p_value),
                'supported': p_value < 0.05 and seattle_grunge.mean() > other_grunge.mean()
            }
        
        return hypotheses
    
    def _identify_regional_archetypes(self, df: pd.DataFrame) -> Dict:
        """Identify archetypal naming patterns by region.
        
        Args:
            df: DataFrame with all bands
            
        Returns:
            Regional archetypes
        """
        archetypes = {}
        
        # Analyze major regions
        regions_to_analyze = {
            'US': df[df['origin_country'] == 'US'],
            'UK': df[df['origin_country'] == 'GB'],
            'Nordic': df[df['geographic_cluster'] == 'Nordic'],
            'Germany': df[df['origin_country'] == 'DE']
        }
        
        for region_name, region_data in regions_to_analyze.items():
            if len(region_data) < 20:
                continue
            
            archetype = {
                'region': region_name,
                'sample_size': len(region_data),
                'linguistic_signature': {},
                'genre_specialization': {},
                'notable_patterns': []
            }
            
            # Compute z-scores relative to global mean
            global_means = {
                'fantasy_score': df['fantasy_score'].mean(),
                'harshness_score': df['harshness_score'].mean(),
                'literary_reference_score': df['literary_reference_score'].mean(),
                'abstraction_score': df['abstraction_score'].mean(),
                'syllable_count': df['syllable_count'].mean()
            }
            
            for metric, global_mean in global_means.items():
                if metric in region_data.columns:
                    regional_mean = region_data[metric].mean()
                    regional_std = df[metric].std()
                    
                    if regional_std > 0:
                        z_score = (regional_mean - global_mean) / regional_std
                        
                        archetype['linguistic_signature'][metric] = {
                            'mean': float(regional_mean),
                            'z_score': float(z_score),
                            'distinctive': abs(z_score) > 0.5
                        }
            
            # Genre specialization
            genre_counts = region_data['genre_cluster'].value_counts()
            total_bands = len(region_data)
            
            for genre, count in genre_counts.head(3).items():
                percentage = (count / total_bands) * 100
                archetype['genre_specialization'][genre] = {
                    'count': int(count),
                    'percentage': float(percentage)
                }
            
            # Notable patterns (high z-scores)
            for metric, sig in archetype['linguistic_signature'].items():
                if sig['distinctive']:
                    direction = 'higher' if sig['z_score'] > 0 else 'lower'
                    archetype['notable_patterns'].append(
                        f"{metric.replace('_', ' ').title()}: {direction} than average (z={sig['z_score']:.2f})"
                    )
            
            archetypes[region_name] = archetype
        
        return archetypes
    
    def create_geographic_heatmap_data(self, df: pd.DataFrame) -> Dict:
        """Create data for geographic visualization.
        
        Args:
            df: DataFrame with all bands
            
        Returns:
            Heatmap data for visualization
        """
        heatmap_data = {}
        
        # Count bands by country
        country_counts = df['origin_country'].value_counts()
        
        for country, count in country_counts.items():
            country_data = df[df['origin_country'] == country]
            
            heatmap_data[country] = {
                'count': int(count),
                'avg_popularity': float(country_data['popularity_score'].mean()),
                'avg_memorability': float(country_data['memorability_score'].mean()),
                'avg_fantasy': float(country_data['fantasy_score'].mean()),
                'top_genre': country_data['genre_cluster'].mode()[0] if len(country_data) > 0 else 'Unknown'
            }
        
        return heatmap_data


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    analyzer = BandGeographicAnalyzer()
    df = analyzer.get_comprehensive_dataset()
    
    if len(df) > 0:
        results = analyzer.analyze_geographic_patterns(df)
        
        print("\n" + "="*60)
        print("GEOGRAPHIC PATTERN ANALYSIS")
        print("="*60)
        
        print("\nCountry Profiles:")
        for country, profile in results['country_profiles'].items():
            print(f"\n{country} ({profile['country_name']}):")
            print(f"  Sample size: {profile['sample_size']}")
            print(f"  Avg fantasy score: {profile.get('fantasy_score_mean', 0):.2f}")
            print(f"  Avg harshness: {profile.get('harshness_score_mean', 0):.2f}")
            print(f"  Top genre: {list(profile['top_genres'].keys())[0] if profile['top_genres'] else 'N/A'}")
        
        print("\n\nHypothesis Tests:")
        for hyp_name, hyp in results['hypothesis_tests'].items():
            print(f"\n{hyp_name}:")
            print(f"  {hyp['hypothesis']}")
            print(f"  Supported: {hyp['supported']}")
            if 'p_value' in hyp:
                print(f"  p-value: {hyp['p_value']:.4f}")
    else:
        print("No bands found. Run band_collector.py first.")

