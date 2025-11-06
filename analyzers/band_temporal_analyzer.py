"""Band Temporal Analyzer

Analyzes linguistic patterns across musical decades (1950s-2020s).
Tests hypotheses about naming evolution over time.

Key Questions:
- Do band names get shorter/simpler over time?
- Peak of memorability/fantasy in 1970s prog rock?
- Harshness spikes in punk (70s), metal (80s), grunge (90s) eras?
- Era-specific linguistic formulas?
"""

import logging
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

from core.models import db, Band, BandAnalysis

logger = logging.getLogger(__name__)


class BandTemporalAnalyzer:
    """Analyze temporal evolution of band name linguistics."""
    
    def __init__(self):
        self.decades = [1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020]
    
    def get_comprehensive_dataset(self) -> pd.DataFrame:
        """Load all bands with linguistic analysis into DataFrame.
        
        Returns:
            DataFrame with band data and analysis
        """
        query = db.session.query(Band, BandAnalysis).join(
            BandAnalysis,
            Band.id == BandAnalysis.band_id
        ).filter(
            Band.formation_decade.isnot(None)
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
                    'is_active': band.is_active,
                    'years_active': band.years_active,
                    
                    # Popularity metrics
                    'listeners_count': band.listeners_count or 0,
                    'play_count': band.play_count or 0,
                    'popularity_score': band.popularity_score or 0,
                    'longevity_score': band.longevity_score or 0,
                    'cross_generational_appeal': band.cross_generational_appeal,
                    
                    # Standard linguistic metrics
                    'syllable_count': analysis.syllable_count,
                    'character_length': analysis.character_length,
                    'word_count': analysis.word_count,
                    'phonetic_score': analysis.phonetic_score,
                    'vowel_ratio': analysis.vowel_ratio,
                    'memorability_score': analysis.memorability_score,
                    'pronounceability_score': analysis.pronounceability_score,
                    'uniqueness_score': analysis.uniqueness_score,
                    'name_type': analysis.name_type,
                    
                    # Band-specific metrics
                    'fantasy_score': analysis.fantasy_score,
                    'power_connotation_score': analysis.power_connotation_score,
                    'harshness_score': analysis.harshness_score,
                    'softness_score': analysis.softness_score,
                    'abstraction_score': analysis.abstraction_score,
                    'literary_reference_score': analysis.literary_reference_score,
                    
                    # Temporal/geographic
                    'temporal_cohort': analysis.temporal_cohort,
                    'geographic_cluster': analysis.geographic_cluster,
                }
                
                rows.append(row)
                
            except Exception as e:
                logger.warning(f"Error loading band {band.name}: {e}")
                continue
        
        df = pd.DataFrame(rows)
        logger.info(f"Loaded {len(df)} bands with complete analysis")
        
        return df
    
    def analyze_temporal_evolution(self, df: pd.DataFrame) -> Dict:
        """Analyze how linguistic features evolve across decades.
        
        Args:
            df: DataFrame with band data
            
        Returns:
            Dictionary with temporal analysis results
        """
        logger.info("Analyzing temporal evolution of band names...")
        
        results = {
            'decade_profiles': {},
            'trend_analysis': {},
            'hypothesis_tests': {},
            'era_archetypes': {}
        }
        
        # 1. Decade-by-decade profiles
        for decade in self.decades:
            decade_data = df[df['formation_decade'] == decade]
            
            if len(decade_data) == 0:
                continue
            
            profile = self._compute_decade_profile(decade_data)
            results['decade_profiles'][f"{decade}s"] = profile
        
        # 2. Trend analysis (regression over time)
        results['trend_analysis'] = self._analyze_trends(df)
        
        # 3. Hypothesis testing
        results['hypothesis_tests'] = self._test_hypotheses(df)
        
        # 4. Era archetypes (clustering within decades)
        results['era_archetypes'] = self._identify_era_archetypes(df)
        
        return results
    
    def _compute_decade_profile(self, decade_data: pd.DataFrame) -> Dict:
        """Compute linguistic profile for a decade.
        
        Args:
            decade_data: DataFrame filtered to one decade
            
        Returns:
            Decade profile statistics
        """
        profile = {
            'sample_size': len(decade_data),
            'decade': decade_data['formation_decade'].iloc[0] if len(decade_data) > 0 else None,
        }
        
        # Linguistic metrics (mean, std, median)
        metrics = [
            'syllable_count', 'character_length', 'word_count',
            'memorability_score', 'pronounceability_score', 'uniqueness_score',
            'fantasy_score', 'power_connotation_score', 'harshness_score',
            'softness_score', 'abstraction_score', 'literary_reference_score',
            'phonetic_score', 'vowel_ratio'
        ]
        
        for metric in metrics:
            if metric in decade_data.columns:
                values = decade_data[metric].dropna()
                if len(values) > 0:
                    profile[f"{metric}_mean"] = float(values.mean())
                    profile[f"{metric}_std"] = float(values.std())
                    profile[f"{metric}_median"] = float(values.median())
        
        # Genre distribution
        genre_counts = decade_data['genre_cluster'].value_counts()
        profile['top_genres'] = genre_counts.head(5).to_dict()
        
        # Success metrics
        if 'popularity_score' in decade_data.columns:
            profile['avg_popularity'] = float(decade_data['popularity_score'].mean())
            profile['avg_longevity'] = float(decade_data['longevity_score'].mean())
        
        # Most common name types
        name_types = decade_data['name_type'].value_counts()
        profile['name_type_distribution'] = name_types.head(5).to_dict()
        
        return profile
    
    def _analyze_trends(self, df: pd.DataFrame) -> Dict:
        """Analyze trends in linguistic features over time.
        
        Uses linear regression to identify increasing/decreasing trends.
        
        Args:
            df: DataFrame with all bands
            
        Returns:
            Trend analysis results
        """
        trends = {}
        
        metrics_to_test = [
            'syllable_count',
            'character_length',
            'word_count',
            'memorability_score',
            'fantasy_score',
            'harshness_score',
            'abstraction_score',
            'uniqueness_score'
        ]
        
        for metric in metrics_to_test:
            if metric not in df.columns:
                continue
            
            # Prepare data (remove nulls)
            valid_data = df[['formation_year', metric]].dropna()
            
            if len(valid_data) < 10:
                continue
            
            X = valid_data['formation_year'].values.reshape(-1, 1)
            y = valid_data[metric].values
            
            # Linear regression
            slope, intercept, r_value, p_value, std_err = stats.linregress(X.flatten(), y)
            
            # Calculate predicted values for 1950 and 2020
            pred_1950 = slope * 1950 + intercept
            pred_2020 = slope * 2020 + intercept
            percent_change = ((pred_2020 - pred_1950) / pred_1950) * 100 if pred_1950 != 0 else 0
            
            trends[metric] = {
                'slope': float(slope),
                'r_squared': float(r_value ** 2),
                'p_value': float(p_value),
                'significant': p_value < 0.05,
                'direction': 'increasing' if slope > 0 else 'decreasing',
                'value_1950': float(pred_1950),
                'value_2020': float(pred_2020),
                'percent_change': float(percent_change)
            }
        
        return trends
    
    def _test_hypotheses(self, df: pd.DataFrame) -> Dict:
        """Test specific hypotheses about temporal patterns.
        
        Args:
            df: DataFrame with all bands
            
        Returns:
            Hypothesis test results
        """
        hypotheses = {}
        
        # H1: Syllable count decline (1950s vs 2020s)
        bands_1950s = df[df['formation_decade'] == 1950]['syllable_count'].dropna()
        bands_2020s = df[df['formation_decade'] == 2020]['syllable_count'].dropna()
        
        if len(bands_1950s) > 0 and len(bands_2020s) > 0:
            t_stat, p_value = stats.ttest_ind(bands_1950s, bands_2020s)
            hypotheses['H1_syllable_decline'] = {
                'hypothesis': 'Band names become shorter over time (fewer syllables)',
                'mean_1950s': float(bands_1950s.mean()),
                'mean_2020s': float(bands_2020s.mean()),
                'difference': float(bands_1950s.mean() - bands_2020s.mean()),
                't_statistic': float(t_stat),
                'p_value': float(p_value),
                'supported': p_value < 0.05 and bands_1950s.mean() > bands_2020s.mean(),
                'effect_size': float(abs(bands_1950s.mean() - bands_2020s.mean()) / bands_1950s.std())
            }
        
        # H2: Memorability peak in 1970s (prog rock era)
        bands_1970s = df[df['formation_decade'] == 1970]['memorability_score'].dropna()
        other_decades = df[df['formation_decade'] != 1970]['memorability_score'].dropna()
        
        if len(bands_1970s) > 0 and len(other_decades) > 0:
            t_stat, p_value = stats.ttest_ind(bands_1970s, other_decades)
            hypotheses['H2_memorability_peak_1970s'] = {
                'hypothesis': 'Memorability peaks in 1970s (prog rock era)',
                'mean_1970s': float(bands_1970s.mean()),
                'mean_other_decades': float(other_decades.mean()),
                'difference': float(bands_1970s.mean() - other_decades.mean()),
                't_statistic': float(t_stat),
                'p_value': float(p_value),
                'supported': p_value < 0.05 and bands_1970s.mean() > other_decades.mean()
            }
        
        # H3: Fantasy score peak in 1970s
        bands_1970s_fantasy = df[df['formation_decade'] == 1970]['fantasy_score'].dropna()
        other_decades_fantasy = df[df['formation_decade'] != 1970]['fantasy_score'].dropna()
        
        if len(bands_1970s_fantasy) > 0 and len(other_decades_fantasy) > 0:
            t_stat, p_value = stats.ttest_ind(bands_1970s_fantasy, other_decades_fantasy)
            hypotheses['H3_fantasy_peak_1970s'] = {
                'hypothesis': 'Fantasy/mythological names peak in 1970s',
                'mean_1970s': float(bands_1970s_fantasy.mean()),
                'mean_other_decades': float(other_decades_fantasy.mean()),
                't_statistic': float(t_stat),
                'p_value': float(p_value),
                'supported': p_value < 0.05 and bands_1970s_fantasy.mean() > other_decades_fantasy.mean()
            }
        
        # H4: Harshness spike in metal era (1980s)
        bands_1980s = df[df['formation_decade'] == 1980]['harshness_score'].dropna()
        other_decades_harsh = df[df['formation_decade'] != 1980]['harshness_score'].dropna()
        
        if len(bands_1980s) > 0 and len(other_decades_harsh) > 0:
            t_stat, p_value = stats.ttest_ind(bands_1980s, other_decades_harsh)
            hypotheses['H4_harshness_spike_1980s'] = {
                'hypothesis': 'Harshness spikes in 1980s (metal era)',
                'mean_1980s': float(bands_1980s.mean()),
                'mean_other_decades': float(other_decades_harsh.mean()),
                't_statistic': float(t_stat),
                'p_value': float(p_value),
                'supported': p_value < 0.05 and bands_1980s.mean() > other_decades_harsh.mean()
            }
        
        # H5: Abstraction increases over time (simple → abstract)
        early_era = df[df['formation_decade'] <= 1970]['abstraction_score'].dropna()
        modern_era = df[df['formation_decade'] >= 2000]['abstraction_score'].dropna()
        
        if len(early_era) > 0 and len(modern_era) > 0:
            t_stat, p_value = stats.ttest_ind(early_era, modern_era)
            hypotheses['H5_abstraction_increase'] = {
                'hypothesis': 'Names become more abstract over time (≤1970 vs ≥2000)',
                'mean_early': float(early_era.mean()),
                'mean_modern': float(modern_era.mean()),
                't_statistic': float(t_stat),
                'p_value': float(p_value),
                'supported': p_value < 0.05 and modern_era.mean() > early_era.mean()
            }
        
        return hypotheses
    
    def _identify_era_archetypes(self, df: pd.DataFrame) -> Dict:
        """Identify archetypal name patterns within each decade.
        
        Uses clustering to find distinct naming styles per era.
        
        Args:
            df: DataFrame with all bands
            
        Returns:
            Era archetypes by decade
        """
        archetypes = {}
        
        feature_cols = [
            'syllable_count', 'character_length', 'memorability_score',
            'fantasy_score', 'harshness_score', 'abstraction_score'
        ]
        
        for decade in self.decades:
            decade_data = df[df['formation_decade'] == decade].copy()
            
            if len(decade_data) < 20:  # Need minimum sample
                continue
            
            # Prepare features
            features = decade_data[feature_cols].fillna(0)
            
            if len(features) < 20:
                continue
            
            # Standardize
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(features)
            
            # Cluster (k=3 for simplicity)
            try:
                kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
                clusters = kmeans.fit_predict(features_scaled)
                
                decade_data['cluster'] = clusters
                
                # Compute cluster profiles
                cluster_profiles = []
                for cluster_id in range(3):
                    cluster_data = decade_data[decade_data['cluster'] == cluster_id]
                    
                    profile = {
                        'cluster_id': int(cluster_id),
                        'size': len(cluster_data),
                        'percentage': float(len(cluster_data) / len(decade_data) * 100),
                        'example_bands': cluster_data['name'].head(5).tolist(),
                        'avg_syllables': float(cluster_data['syllable_count'].mean()),
                        'avg_memorability': float(cluster_data['memorability_score'].mean()),
                        'avg_fantasy': float(cluster_data['fantasy_score'].mean()),
                        'avg_harshness': float(cluster_data['harshness_score'].mean()),
                    }
                    
                    # Assign archetype name
                    profile['archetype_name'] = self._name_archetype(profile)
                    
                    cluster_profiles.append(profile)
                
                # Calculate silhouette score
                silhouette = silhouette_score(features_scaled, clusters)
                
                archetypes[f"{decade}s"] = {
                    'clusters': cluster_profiles,
                    'silhouette_score': float(silhouette),
                    'quality': 'good' if silhouette > 0.3 else 'fair' if silhouette > 0.2 else 'poor'
                }
                
            except Exception as e:
                logger.warning(f"Error clustering {decade}s: {e}")
                continue
        
        return archetypes
    
    def _name_archetype(self, profile: Dict) -> str:
        """Assign descriptive name to cluster archetype.
        
        Args:
            profile: Cluster profile statistics
            
        Returns:
            Archetype name
        """
        syllables = profile['avg_syllables']
        memorability = profile['avg_memorability']
        fantasy = profile['avg_fantasy']
        harshness = profile['avg_harshness']
        
        # Simple heuristic classification
        if syllables < 2.5 and memorability > 60:
            return "Punchy & Memorable"
        elif fantasy > 60:
            return "Mythological/Epic"
        elif harshness > 60:
            return "Aggressive/Harsh"
        elif syllables > 3.5:
            return "Complex/Literary"
        elif memorability < 40:
            return "Abstract/Obscure"
        else:
            return "Balanced/Mainstream"
    
    def compare_decades(self, df: pd.DataFrame, decade1: int, decade2: int) -> Dict:
        """Compare linguistic profiles between two decades.
        
        Args:
            df: DataFrame with all bands
            decade1: First decade (e.g., 1970)
            decade2: Second decade (e.g., 2010)
            
        Returns:
            Comparison results
        """
        data1 = df[df['formation_decade'] == decade1]
        data2 = df[df['formation_decade'] == decade2]
        
        if len(data1) == 0 or len(data2) == 0:
            return {'error': 'Insufficient data for comparison'}
        
        comparison = {
            'decade1': decade1,
            'decade2': decade2,
            'sample_size_1': len(data1),
            'sample_size_2': len(data2),
            'metrics': {}
        }
        
        metrics = [
            'syllable_count', 'character_length', 'memorability_score',
            'fantasy_score', 'harshness_score', 'abstraction_score'
        ]
        
        for metric in metrics:
            if metric not in data1.columns or metric not in data2.columns:
                continue
            
            values1 = data1[metric].dropna()
            values2 = data2[metric].dropna()
            
            if len(values1) > 0 and len(values2) > 0:
                mean1 = values1.mean()
                mean2 = values2.mean()
                
                t_stat, p_value = stats.ttest_ind(values1, values2)
                
                comparison['metrics'][metric] = {
                    f'mean_{decade1}s': float(mean1),
                    f'mean_{decade2}s': float(mean2),
                    'difference': float(mean2 - mean1),
                    'percent_change': float(((mean2 - mean1) / mean1) * 100) if mean1 != 0 else 0,
                    'p_value': float(p_value),
                    'significant': p_value < 0.05
                }
        
        return comparison


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    analyzer = BandTemporalAnalyzer()
    df = analyzer.get_comprehensive_dataset()
    
    if len(df) > 0:
        results = analyzer.analyze_temporal_evolution(df)
        
        # Print summary
        print("\n" + "="*60)
        print("TEMPORAL EVOLUTION ANALYSIS")
        print("="*60)
        
        print("\nDecade Profiles:")
        for decade, profile in results['decade_profiles'].items():
            print(f"\n{decade}:")
            print(f"  Sample size: {profile['sample_size']}")
            print(f"  Avg syllables: {profile.get('syllable_count_mean', 0):.2f}")
            print(f"  Avg memorability: {profile.get('memorability_score_mean', 0):.2f}")
            print(f"  Top genre: {list(profile['top_genres'].keys())[0] if profile['top_genres'] else 'N/A'}")
        
        print("\n\nTrend Analysis (1950-2020):")
        for metric, trend in results['trend_analysis'].items():
            if trend['significant']:
                print(f"\n{metric}:")
                print(f"  Direction: {trend['direction']}")
                print(f"  Change: {trend['percent_change']:.1f}%")
                print(f"  R²: {trend['r_squared']:.3f}")
                print(f"  p-value: {trend['p_value']:.4f}")
    else:
        print("No bands found in database. Run band_collector.py first.")

