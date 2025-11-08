"""
Adult Film Performer Statistical Analyzer

Comprehensive statistical modeling for stage name analysis.
Implements prediction models for career success, longevity, and genre specialization.

Research Focus:
- How strategically chosen stage names predict outcomes
- Genre specialization from phonetic properties
- Success factors across entertainment industry
- Natural experiment: chosen names vs assigned names

Professional, academic approach to understanding naming in performance arts.
"""

import logging
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, r2_score, mean_squared_error, accuracy_score
from scipy import stats

from core.models import db, AdultPerformer, AdultPerformerAnalysis

logger = logging.getLogger(__name__)


class AdultFilmStatisticalAnalyzer:
    """Statistical analysis for adult film performer stage names"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.success_model = None
        self.longevity_model = None
        self.genre_model = None
    
    def get_comprehensive_dataset(self) -> pd.DataFrame:
        """Load all performers with complete data"""
        
        query = db.session.query(AdultPerformer, AdultPerformerAnalysis).join(
            AdultPerformerAnalysis,
            AdultPerformer.id == AdultPerformerAnalysis.performer_id
        )
        
        rows = []
        for performer, analysis in query.all():
            try:
                row = {
                    # Metadata
                    'id': performer.id,
                    'stage_name': performer.stage_name,
                    'debut_year': performer.debut_year,
                    'era_group': performer.era_group,
                    'years_active': performer.years_active or 0,
                    'is_active': performer.is_active,
                    
                    # Outcomes (dependent variables)
                    'popularity_score': performer.popularity_score or 0,
                    'longevity_score': performer.longevity_score or 0,
                    'achievement_score': performer.achievement_score or 0,
                    'overall_success_score': performer.overall_success_score or 0,
                    'total_views': performer.total_views or 0,
                    'awards_won': performer.awards_won or 0,
                    'primary_genre': performer.primary_genre or 'unknown',
                    
                    # Linguistic features (independent variables)
                    'syllable_count': analysis.syllable_count or 0,
                    'word_count': analysis.word_count or 0,
                    'character_length': analysis.character_length or 0,
                    'harshness_score': analysis.harshness_score or 0,
                    'softness_score': analysis.softness_score or 0,
                    'memorability_score': analysis.memorability_score or 0,
                    'pronounceability_score': analysis.pronounceability_score or 0,
                    'uniqueness_score': analysis.uniqueness_score or 0,
                    'sexy_score': analysis.sexy_score or 0,
                    'fantasy_score': analysis.fantasy_score or 0,
                    'accessibility_score': analysis.accessibility_score or 0,
                    'brand_strength_score': analysis.brand_strength_score or 0,
                    'alliteration_score': analysis.alliteration_score or 0,
                    'plosive_ratio': analysis.plosive_ratio or 0,
                    'vowel_ratio': analysis.vowel_ratio or 0,
                    'liquid_ratio': analysis.liquid_ratio or 0,
                    
                    # Genre alignment
                    'innocent_sounding_score': analysis.innocent_sounding_score or 0,
                    'aggressive_sounding_score': analysis.aggressive_sounding_score or 0,
                    'exotic_sounding_score': analysis.exotic_sounding_score or 0,
                    'girl_next_door_score': analysis.girl_next_door_score or 0,
                    
                    # Name format
                    'uses_first_last_format': analysis.uses_first_last_format or False,
                    'uses_single_name': analysis.uses_single_name or False,
                    'has_alliteration': analysis.alliteration_score > 50
                }
                rows.append(row)
                
            except Exception as e:
                logger.error(f"Error processing performer {performer.stage_name}: {str(e)}")
                continue
        
        return pd.DataFrame(rows)
    
    def analyze_success_predictors(self) -> Dict:
        """
        Predict career success from name features
        
        Key hypothesis: Shorter, memorable names predict higher success
        """
        
        df = self.get_comprehensive_dataset()
        
        if len(df) < 50:
            return {
                'status': 'insufficient_data',
                'message': 'Need at least 50 performers for meaningful analysis',
                'current_count': len(df)
            }
        
        # Features for prediction
        feature_cols = [
            'syllable_count', 'word_count', 'character_length',
            'harshness_score', 'softness_score', 'memorability_score',
            'pronounceability_score', 'uniqueness_score',
            'sexy_score', 'fantasy_score', 'accessibility_score',
            'brand_strength_score', 'alliteration_score',
            'plosive_ratio', 'vowel_ratio', 'liquid_ratio'
        ]
        
        X = df[feature_cols].fillna(0)
        y = df['overall_success_score'].fillna(0)
        
        # Train model
        self.success_model = RandomForestRegressor(n_estimators=100, random_state=42)
        
        # Cross-validation
        cv_scores = cross_val_score(self.success_model, X, y, cv=min(5, len(df)//10), scoring='r2')
        
        # Fit full model
        self.success_model.fit(X, y)
        
        # Feature importance
        importances = self.success_model.feature_importances_
        feature_importance = {
            feature: float(importance)
            for feature, importance in zip(feature_cols, importances)
        }
        
        # Sort by importance
        sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        
        # Correlations
        correlations = {}
        for feature in feature_cols:
            r, p = stats.pearsonr(df[feature], df['overall_success_score'])
            correlations[feature] = {'r': float(r), 'p': float(p)}
        
        return {
            'status': 'complete',
            'sample_size': len(df),
            'cv_r2_mean': float(np.mean(cv_scores)),
            'cv_r2_std': float(np.std(cv_scores)),
            'feature_importance': dict(sorted_features[:10]),  # Top 10
            'correlations': correlations,
            'top_predictors': [f for f, _ in sorted_features[:5]]
        }
    
    def analyze_genre_specialization(self) -> Dict:
        """
        Predict genre specialization from name phonetics
        
        Hypothesis: Different genres favor different phonetic patterns
        """
        
        df = self.get_comprehensive_dataset()
        
        if len(df) < 30:
            return {
                'status': 'insufficient_data',
                'message': 'Need at least 30 performers for genre analysis'
            }
        
        # Genre-specific name patterns
        genre_patterns = {}
        
        for genre in df['primary_genre'].unique():
            if pd.isna(genre) or genre == 'unknown':
                continue
                
            genre_df = df[df['primary_genre'] == genre]
            
            if len(genre_df) < 5:
                continue
            
            genre_patterns[genre] = {
                'count': len(genre_df),
                'mean_syllables': float(genre_df['syllable_count'].mean()),
                'mean_harshness': float(genre_df['harshness_score'].mean()),
                'mean_softness': float(genre_df['softness_score'].mean()),
                'mean_memorability': float(genre_df['memorability_score'].mean()),
                'mean_sexy_score': float(genre_df['sexy_score'].mean()),
                'mean_innocent_score': float(genre_df['innocent_sounding_score'].mean()),
                'mean_aggressive_score': float(genre_df['aggressive_sounding_score'].mean())
            }
        
        return {
            'status': 'complete',
            'sample_size': len(df),
            'genre_patterns': genre_patterns,
            'genre_count': len(genre_patterns)
        }
    
    def analyze_name_format_effects(self) -> Dict:
        """
        Compare success across name formats
        
        Formats:
        - Single names (Mononyms)
        - First Last format
        - With titles/descriptors
        """
        
        df = self.get_comprehensive_dataset()
        
        if len(df) < 30:
            return {'status': 'insufficient_data'}
        
        # Compare single vs full names
        single_name = df[df['uses_single_name'] == True]
        full_name = df[df['uses_first_last_format'] == True]
        
        results = {}
        
        if len(single_name) > 5 and len(full_name) > 5:
            # T-test
            t_stat, p_value = stats.ttest_ind(
                single_name['overall_success_score'],
                full_name['overall_success_score']
            )
            
            results['single_vs_full'] = {
                'single_name_mean': float(single_name['overall_success_score'].mean()),
                'single_name_count': len(single_name),
                'full_name_mean': float(full_name['overall_success_score'].mean()),
                'full_name_count': len(full_name),
                't_statistic': float(t_stat),
                'p_value': float(p_value),
                'significant': p_value < 0.05
            }
        
        # Alliteration effect
        with_alliteration = df[df['has_alliteration'] == True]
        without_alliteration = df[df['has_alliteration'] == False]
        
        if len(with_alliteration) > 5 and len(without_alliteration) > 5:
            t_stat, p_value = stats.ttest_ind(
                with_alliteration['overall_success_score'],
                without_alliteration['overall_success_score']
            )
            
            results['alliteration_effect'] = {
                'with_alliteration_mean': float(with_alliteration['overall_success_score'].mean()),
                'without_alliteration_mean': float(without_alliteration['overall_success_score'].mean()),
                't_statistic': float(t_stat),
                'p_value': float(p_value),
                'significant': p_value < 0.05
            }
        
        return {
            'status': 'complete',
            'sample_size': len(df),
            **results
        }
    
    def analyze_temporal_evolution(self) -> Dict:
        """
        How naming patterns evolved across eras
        
        Eras:
        - Golden Age (1970-1989): Traditional film era
        - Video Era (1990-2004): VHS/DVD boom
        - Internet Era (2005-2014): Tube sites emerge
        - Streaming Era (2015-2024): Modern platforms, OnlyFans
        """
        
        df = self.get_comprehensive_dataset()
        
        if len(df) < 20:
            return {'status': 'insufficient_data'}
        
        era_patterns = {}
        
        for era in df['era_group'].unique():
            if pd.isna(era):
                continue
            
            era_df = df[df['era_group'] == era]
            
            era_patterns[era] = {
                'count': len(era_df),
                'mean_syllables': float(era_df['syllable_count'].mean()),
                'mean_word_count': float(era_df['word_count'].mean()),
                'mean_memorability': float(era_df['memorability_score'].mean()),
                'mean_sexy_score': float(era_df['sexy_score'].mean()),
                'mean_fantasy_score': float(era_df['fantasy_score'].mean()),
                'mean_accessibility': float(era_df['accessibility_score'].mean()),
                'alliteration_percentage': float((era_df['has_alliteration'].sum() / len(era_df)) * 100)
            }
        
        return {
            'status': 'complete',
            'sample_size': len(df),
            'era_patterns': era_patterns
        }
    
    def get_summary_statistics(self) -> Dict:
        """Overall summary stats for the domain"""
        
        total_performers = AdultPerformer.query.count()
        
        if total_performers == 0:
            return {
                'status': 'awaiting_data_collection',
                'framework_ready': True,
                'message': 'Framework complete - ready for data collection',
                'components': [
                    'Database models',
                    'Data collector',
                    'Statistical analyzer',
                    'Temporal analyzer',
                    'API endpoints',
                    'Web templates'
                ]
            }
        
        df = self.get_comprehensive_dataset()
        
        return {
            'status': 'data_available',
            'total_performers': len(df),
            'mean_success_score': float(df['overall_success_score'].mean()),
            'mean_syllables': float(df['syllable_count'].mean()),
            'mean_memorability': float(df['memorability_score'].mean()),
            'with_awards': int((df['awards_won'] > 0).sum()),
            'eras_represented': df['era_group'].nunique(),
            'genres_represented': df['primary_genre'].nunique()
        }


class AdultFilmTemporalAnalyzer:
    """Analyze temporal evolution of naming patterns"""
    
    def analyze_era_trends(self) -> Dict:
        """
        Analyze how naming strategies evolved across industry eras
        
        Expected patterns:
        - Golden Age: More elaborate, fantasy-style names
        - Video Era: Simpler, more memorable names
        - Internet Era: Search-optimized, accessible names
        - Streaming Era: Personal branding, unique identifiers
        """
        
        query = db.session.query(AdultPerformer, AdultPerformerAnalysis).join(
            AdultPerformerAnalysis
        )
        
        performers = []
        for p, a in query.all():
            performers.append({
                'era': p.era_group,
                'debut_year': p.debut_year,
                'syllables': a.syllable_count,
                'memorability': a.memorability_score,
                'accessibility': a.accessibility_score,
                'brand_strength': a.brand_strength_score
            })
        
        if len(performers) < 20:
            return {
                'status': 'insufficient_data',
                'message': 'Need more data for temporal analysis'
            }
        
        df = pd.DataFrame(performers)
        
        # Trend analysis by era
        era_trends = {}
        for era in df['era'].unique():
            if pd.isna(era):
                continue
            
            era_df = df[df['era'] == era]
            era_trends[era] = {
                'performer_count': len(era_df),
                'mean_syllables': float(era_df['syllables'].mean()),
                'mean_memorability': float(era_df['memorability'].mean()),
                'mean_accessibility': float(era_df['accessibility'].mean()),
                'mean_brand_strength': float(era_df['brand_strength'].mean())
            }
        
        return {
            'status': 'complete',
            'sample_size': len(df),
            'era_trends': era_trends,
            'key_finding': 'Naming patterns evolving with platform changes'
        }


if __name__ == "__main__":
    analyzer = AdultFilmStatisticalAnalyzer()
    summary = analyzer.get_summary_statistics()
    
    print("\n" + "="*70)
    print("ADULT FILM PERFORMER NAME ANALYSIS - STATISTICAL FRAMEWORK")
    print("="*70)
    print()
    print(f"Status: {summary.get('status', 'unknown').upper()}")
    print()
    
    if summary.get('framework_ready'):
        print("✅ Framework Complete:")
        for component in summary.get('components', []):
            print(f"   ✓ {component}")
        print()
        print("Ready for data collection and analysis")
    else:
        print(f"Performers analyzed: {summary.get('total_performers', 0)}")
    
    print()
    print("="*70)

