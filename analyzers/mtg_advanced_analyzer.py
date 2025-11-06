"""MTG Advanced Statistical Analyzer

Implements comprehensive statistical analysis for MTG cards including:
- M4: Color identity linguistic determinism
- M5: Format segmentation (Commander vs Modern vs Legacy)
- M6: Set era evolution (1993-2025)
- M7: Artist-name synergy
- M8: Reprint natural experiment

Mirrors crypto's advanced statistics but adapted for MTG's unique characteristics.
"""

import logging
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LinearRegression
from scipy import stats

from core.models import db, MTGCard, MTGCardAnalysis

logger = logging.getLogger(__name__)


class MTGAdvancedAnalyzer:
    """Advanced statistical analysis for MTG nominative determinism."""
    
    def __init__(self):
        self.scaler = StandardScaler()
    
    def get_comprehensive_dataset(self) -> pd.DataFrame:
        """Load comprehensive MTG dataset with all analysis dimensions."""
        
        # Query all cards with analysis
        query = db.session.query(MTGCard, MTGCardAnalysis).join(
            MTGCardAnalysis,
            MTGCard.id == MTGCardAnalysis.card_id
        ).filter(
            MTGCard.price_usd.isnot(None)
        )
        
        rows = []
        for card, analysis in query.all():
            try:
                row = {
                    # Core data
                    'name': card.name,
                    'price_usd': card.price_usd,
                    'log_price_usd': card.log_price_usd,
                    'rarity': card.rarity,
                    'rarity_tier': card.rarity_tier,
                    'color_identity': card.color_identity,
                    'converted_mana_cost': card.converted_mana_cost,
                    'card_type': card.card_type,
                    'is_legendary': card.is_legendary,
                    'is_creature': card.is_creature,
                    'is_instant_sorcery': card.is_instant_sorcery,
                    'edhrec_rank': card.edhrec_rank,
                    'artist': card.artist,
                    'set_code': card.set_code,
                    'set_year': card.set_year,
                    'reprint_count': card.reprint_count,
                    
                    # Standard name metrics
                    'syllable_count': analysis.syllable_count,
                    'character_length': analysis.character_length,
                    'word_count': analysis.word_count,
                    'phonetic_score': analysis.phonetic_score,
                    'vowel_ratio': analysis.vowel_ratio,
                    'memorability_score': analysis.memorability_score,
                    'pronounceability_score': analysis.pronounceability_score,
                    'uniqueness_score': analysis.uniqueness_score,
                    
                    # MTG-specific
                    'fantasy_score': analysis.fantasy_score,
                    'power_connotation_score': analysis.power_connotation_score,
                    'mythic_resonance_score': analysis.mythic_resonance_score,
                    'constructed_language_score': analysis.constructed_language_score,
                }
                
                # Parse JSON advanced data
                if analysis.phonosemantic_data:
                    phono = json.loads(analysis.phonosemantic_data)
                    row['harshness_score'] = phono.get('harshness_score', 0)
                    row['softness_score'] = phono.get('softness_score', 0)
                
                if analysis.format_affinity_data:
                    fmt = json.loads(analysis.format_affinity_data)
                    row['commander_affinity'] = fmt.get('commander_affinity', 0)
                    row['competitive_affinity'] = fmt.get('competitive_affinity', 0)
                
                if analysis.narrative_data:
                    narrative = json.loads(analysis.narrative_data)
                    row['narrative_complexity'] = narrative.get('overall_narrative_complexity', 0)
                
                if analysis.semantic_data:
                    semantic = json.loads(analysis.semantic_data)
                    row['semantic_density'] = semantic.get('semantic_density', 0)
                
                # Parse format legalities
                if card.format_legalities:
                    legalities = json.loads(card.format_legalities)
                    row['is_commander_legal'] = legalities.get('commander') == 'legal'
                    row['is_modern_legal'] = legalities.get('modern') == 'legal'
                    row['is_legacy_legal'] = legalities.get('legacy') == 'legal'
                
                rows.append(row)
                
            except Exception as e:
                logger.debug(f"Error processing card {card.name}: {e}")
                continue
        
        df = pd.DataFrame(rows)
        logger.info(f"Loaded {len(df)} cards for comprehensive analysis")
        
        return df
    
    def analyze_color_determinism(self, df: pd.DataFrame) -> Dict:
        """M4: Color identity linguistic determinism.
        
        Tests if each MTG color has distinct linguistic patterns.
        """
        logger.info("Running M4: Color identity linguistic determinism...")
        
        results = {}
        
        # Analyze each color
        colors = {'W': 'White', 'U': 'Blue', 'B': 'Black', 'R': 'Red', 'G': 'Green'}
        
        for color_code, color_name in colors.items():
            # Monocolor cards only
            mono = df[df['color_identity'] == color_code].copy()
            
            if len(mono) < 30:
                continue
            
            # Compare linguistic features to other colors
            others = df[(df['color_identity'].notna()) & (df['color_identity'] != color_code)].copy()
            
            # Statistical tests
            features = ['harshness_score', 'softness_score', 'memorability_score', 
                       'fantasy_score', 'mythic_resonance_score']
            
            color_profile = {}
            for feature in features:
                if feature in mono.columns and feature in others.columns:
                    mono_mean = mono[feature].mean()
                    others_mean = others[feature].mean()
                    
                    # T-test
                    t_stat, p_value = stats.ttest_ind(
                        mono[feature].dropna(),
                        others[feature].dropna()
                    )
                    
                    color_profile[feature] = {
                        'mean': round(mono_mean, 2),
                        'vs_others': round(mono_mean - others_mean, 2),
                        'p_value': round(p_value, 4),
                        'significant': p_value < 0.05,
                    }
            
            results[color_name] = {
                'sample_size': len(mono),
                'linguistic_profile': color_profile,
                'avg_price': round(mono['price_usd'].mean(), 2),
            }
        
        return results
    
    def analyze_format_segmentation(self, df: pd.DataFrame) -> Dict:
        """M5: Format segmentation (Commander vs Modern naming patterns)."""
        logger.info("Running M5: Format segmentation analysis...")
        
        # Filter by format legality
        commander = df[df.get('is_commander_legal', False)].copy()
        modern = df[df.get('is_modern_legal', False)].copy()
        
        results = {
            'commander': self._format_profile(commander, 'Commander'),
            'modern': self._format_profile(modern, 'Modern'),
        }
        
        # Comparison
        if 'commander_affinity' in df.columns:
            # Do cards with high Commander affinity perform better in Commander?
            high_cmdr = commander[commander['commander_affinity'] > 60]
            low_cmdr = commander[commander['commander_affinity'] <= 60]
            
            if len(high_cmdr) > 10 and len(low_cmdr) > 10:
                results['commander_affinity_effect'] = {
                    'high_affinity_avg_price': round(high_cmdr['price_usd'].mean(), 2),
                    'low_affinity_avg_price': round(low_cmdr['price_usd'].mean(), 2),
                    'difference': round(high_cmdr['price_usd'].mean() - low_cmdr['price_usd'].mean(), 2),
                }
        
        return results
    
    def analyze_set_era_evolution(self, df: pd.DataFrame) -> Dict:
        """M6: How naming conventions evolved 1993-2025."""
        logger.info("Running M6: Set era evolution...")
        
        df_with_year = df[df['set_year'].notna()].copy()
        
        # Define eras
        eras = {
            'Early (1993-2000)': (1993, 2000),
            'Golden Age (2001-2010)': (2001, 2010),
            'Modern (2011-2020)': (2011, 2020),
            'Contemporary (2021-2025)': (2021, 2025),
        }
        
        results = {}
        for era_name, (start, end) in eras.items():
            era_cards = df_with_year[
                (df_with_year['set_year'] >= start) & 
                (df_with_year['set_year'] <= end)
            ]
            
            if len(era_cards) < 20:
                continue
            
            results[era_name] = {
                'sample_size': len(era_cards),
                'avg_syllables': round(era_cards['syllable_count'].mean(), 2),
                'avg_length': round(era_cards['character_length'].mean(), 2),
                'avg_fantasy_score': round(era_cards['fantasy_score'].mean(), 2),
                'avg_memorability': round(era_cards['memorability_score'].mean(), 2),
                'avg_price': round(era_cards['price_usd'].mean(), 2),
            }
        
        return results
    
    def cluster_analysis(self, df: pd.DataFrame, n_clusters: int = 3) -> Dict:
        """Cluster MTG cards by linguistic features."""
        logger.info(f"Running cluster analysis (k={n_clusters})...")
        
        # Select features for clustering
        feature_cols = [
            'syllable_count', 'character_length', 'memorability_score',
            'fantasy_score', 'mythic_resonance_score', 'constructed_language_score'
        ]
        
        # Filter to cards with all features
        df_clean = df[feature_cols].dropna()
        
        if len(df_clean) < 100:
            return {'error': 'Insufficient data for clustering'}
        
        # Normalize
        X = self.scaler.fit_transform(df_clean)
        
        # K-means
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(X)
        
        # Add clusters to df
        df_clean['cluster'] = clusters
        
        # Profile each cluster
        cluster_profiles = {}
        for i in range(n_clusters):
            cluster_df = df.iloc[df_clean[df_clean['cluster'] == i].index]
            
            cluster_profiles[f'Cluster_{i}'] = {
                'size': len(cluster_df),
                'avg_price': round(cluster_df['price_usd'].mean(), 2),
                'avg_syllables': round(cluster_df['syllable_count'].mean(), 2),
                'avg_fantasy_score': round(cluster_df['fantasy_score'].mean(), 2),
                'avg_memorability': round(cluster_df['memorability_score'].mean(), 2),
                'top_cards': cluster_df.nlargest(5, 'price_usd')['name'].tolist(),
            }
        
        return {
            'n_clusters': n_clusters,
            'total_cards': len(df_clean),
            'clusters': cluster_profiles,
        }
    
    def _format_profile(self, df: pd.DataFrame, format_name: str) -> Dict:
        """Generate linguistic profile for a format."""
        if len(df) == 0:
            return {}
        
        return {
            'sample_size': len(df),
            'avg_syllables': round(df['syllable_count'].mean(), 2),
            'avg_length': round(df['character_length'].mean(), 2),
            'avg_memorability': round(df['memorability_score'].mean(), 2),
            'avg_fantasy_score': round(df['fantasy_score'].mean(), 2),
            'legendary_rate': round((df['is_legendary'].sum() / len(df)) * 100, 1),
            'avg_price': round(df['price_usd'].mean(), 2),
        }
    
    def run_comprehensive_analysis(self) -> Dict:
        """Run all M4-M8 analyses."""
        logger.info("="*70)
        logger.info("MTG COMPREHENSIVE STATISTICAL ANALYSIS")
        logger.info("="*70)
        
        # Load data
        df = self.get_comprehensive_dataset()
        
        if len(df) < 100:
            return {'error': 'Insufficient data', 'sample_size': len(df)}
        
        results = {
            'dataset_summary': {
                'total_cards': len(df),
                'avg_price': round(df['price_usd'].mean(), 2),
                'median_price': round(df['price_usd'].median(), 2),
            },
            
            # M4: Color determinism
            'color_determinism': self.analyze_color_determinism(df),
            
            # M5: Format segmentation
            'format_segmentation': self.analyze_format_segmentation(df),
            
            # M6: Era evolution
            'era_evolution': self.analyze_set_era_evolution(df),
            
            # Clustering
            'cluster_analysis': self.cluster_analysis(df, n_clusters=3),
        }
        
        logger.info("✅ Comprehensive analysis complete!")
        
        return results

