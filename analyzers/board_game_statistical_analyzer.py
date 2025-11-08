"""Board Game Statistical Analyzer

Comprehensive statistical modeling for board game name analysis.
Implements cluster analysis, temporal evolution, cultural comparison, and success prediction.

Analyses:
1. Descriptive statistics by era and category
2. Cluster analysis (K-means on phonetic+semantic features)
3. Temporal evolution (naming conventions over time)
4. Cultural comparison (US vs Euro vs Japanese traditions)
5. Success prediction (name features → BGG rating)
6. Complexity correlation (name complexity ↔ game complexity)
"""

import logging
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, r2_score, mean_squared_error
from scipy import stats

from core.models import db, BoardGame, BoardGameAnalysis

logger = logging.getLogger(__name__)


class BoardGameStatisticalAnalyzer:
    """Comprehensive statistical analysis for board game nomenclature."""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.rating_model = None
        self.complexity_model = None
        self.clusters = None
    
    def get_comprehensive_dataset(self) -> pd.DataFrame:
        """Load all games with complete data.
        
        Returns:
            DataFrame with game and analysis data
        """
        query = db.session.query(BoardGame, BoardGameAnalysis).join(
            BoardGameAnalysis,
            BoardGame.id == BoardGameAnalysis.game_id
        )
        
        rows = []
        for game, analysis in query.all():
            try:
                row = {
                    # Metadata
                    'id': game.id,
                    'name': game.name,
                    'bgg_id': game.bgg_id,
                    'year_published': game.year_published,
                    'era': analysis.era,
                    'category': game.category,
                    'designer_nationality': game.designer_nationality,
                    'designer': game.designer,
                    
                    # Outcomes (dependent variables)
                    'bgg_rating': game.bgg_rating or 0,
                    'average_rating': game.average_rating or 0,
                    'num_ratings': game.num_ratings or 0,
                    'complexity_weight': game.complexity_weight or 0,
                    'ownership_count': game.ownership_count or 0,
                    'bgg_rank': game.bgg_rank or 99999,
                    
                    # Name structure (predictors)
                    'word_count': analysis.word_count or 0,
                    'syllable_count': analysis.syllable_count or 0,
                    'character_length': analysis.character_length or 0,
                    'contains_colon': analysis.contains_colon or False,
                    'contains_number': analysis.contains_number or False,
                    'contains_article': analysis.contains_article or False,
                    
                    # Phonetic features
                    'harshness_score': analysis.harshness_score or 50,
                    'smoothness_score': analysis.smoothness_score or 50,
                    'plosive_ratio': analysis.plosive_ratio or 0,
                    'fricative_ratio': analysis.fricative_ratio or 0,
                    'vowel_ratio': analysis.vowel_ratio or 0.4,
                    'consonant_cluster_density': analysis.consonant_cluster_density or 0,
                    'phonetic_complexity': analysis.phonetic_complexity or 0,
                    'sound_symbolism_score': analysis.sound_symbolism_score or 50,
                    'alliteration_score': analysis.alliteration_score or 0,
                    
                    # Semantic features
                    'name_type': analysis.name_type or 'abstract',
                    'memorability_score': analysis.memorability_score or 50,
                    'pronounceability_score': analysis.pronounceability_score or 50,
                    'semantic_transparency': analysis.semantic_transparency or 40,
                    
                    # Cultural
                    'is_fantasy_name': analysis.is_fantasy_name or False,
                    'is_latin_derived': analysis.is_latin_derived or False,
                    'is_compound_word': analysis.is_compound_word or False,
                    'primary_language': analysis.primary_language or 'en',
                    
                    # Clusters
                    'phonetic_cluster': analysis.phonetic_cluster,
                    'semantic_cluster': analysis.semantic_cluster,
                    'combined_cluster': analysis.combined_cluster,
                    
                    # Composite scores
                    'name_quality_score': analysis.name_quality_score or 50,
                    'cultural_alignment_score': analysis.cultural_alignment_score or 50,
                    'thematic_resonance': analysis.thematic_resonance or 40,
                }
                
                rows.append(row)
                
            except Exception as e:
                logger.warning(f"Error loading game {game.name}: {e}")
                continue
        
        df = pd.DataFrame(rows)
        logger.info(f"Loaded {len(df)} board games for analysis")
        return df
    
    def run_full_analysis(self) -> Dict:
        """Execute all 6 analysis modules.
        
        Returns:
            Dict with comprehensive results
        """
        logger.info("=== BOARD GAME STATISTICAL ANALYSIS ===")
        
        df = self.get_comprehensive_dataset()
        
        if len(df) < 100:
            logger.error("Insufficient data for analysis (need 100+)")
            return {'error': 'Insufficient data'}
        
        results = {}
        
        # Analysis 1: Descriptive Statistics
        logger.info("\n1. Running descriptive statistics...")
        results['descriptive'] = self.analyze_descriptive_statistics(df)
        
        # Analysis 2: Cluster Analysis
        logger.info("\n2. Running cluster analysis...")
        results['clusters'] = self.analyze_clusters(df)
        
        # Analysis 3: Temporal Evolution
        logger.info("\n3. Running temporal evolution...")
        results['temporal'] = self.analyze_temporal_evolution(df)
        
        # Analysis 4: Cultural Comparison
        logger.info("\n4. Running cultural comparison...")
        results['cultural'] = self.analyze_cultural_patterns(df)
        
        # Analysis 5: Success Prediction
        logger.info("\n5. Running success prediction...")
        results['success_prediction'] = self.predict_success(df)
        
        # Analysis 6: Complexity Correlation
        logger.info("\n6. Running complexity correlation...")
        results['complexity'] = self.analyze_complexity_correlation(df)
        
        results['sample_size'] = len(df)
        results['analysis_timestamp'] = datetime.now().isoformat()
        
        logger.info("\n=== ANALYSIS COMPLETE ===")
        return results
    
    def analyze_descriptive_statistics(self, df: pd.DataFrame) -> Dict:
        """Compute descriptive statistics by era and category.
        
        Args:
            df: Complete dataset
        
        Returns:
            Dict with descriptive stats
        """
        stats_dict = {
            'overall': {
                'mean_syllables': float(df['syllable_count'].mean()),
                'mean_words': float(df['word_count'].mean()),
                'mean_rating': float(df['bgg_rating'].mean()),
                'mean_complexity': float(df['complexity_weight'].mean()),
                'colon_percentage': float((df['contains_colon'].sum() / len(df)) * 100),
                'fantasy_names_percentage': float((df['is_fantasy_name'].sum() / len(df)) * 100)
            },
            'by_era': {},
            'by_category': {}
        }
        
        # By era
        for era in df['era'].unique():
            era_df = df[df['era'] == era]
            stats_dict['by_era'][era] = {
                'count': len(era_df),
                'mean_syllables': float(era_df['syllable_count'].mean()),
                'mean_rating': float(era_df['bgg_rating'].mean()),
                'mean_complexity': float(era_df['complexity_weight'].mean()),
                'mean_memorability': float(era_df['memorability_score'].mean())
            }
        
        # By category
        for category in df['category'].value_counts().head(10).index:
            cat_df = df[df['category'] == category]
            if len(cat_df) >= 10:
                stats_dict['by_category'][category] = {
                    'count': len(cat_df),
                    'mean_syllables': float(cat_df['syllable_count'].mean()),
                    'mean_rating': float(cat_df['bgg_rating'].mean())
                }
        
        return stats_dict
    
    def analyze_clusters(self, df: pd.DataFrame, n_clusters: int = 5) -> Dict:
        """Perform K-means clustering on name features.
        
        Args:
            df: Complete dataset
            n_clusters: Number of clusters to create
        
        Returns:
            Dict with cluster analysis results
        """
        # Select features for clustering
        feature_cols = [
            'syllable_count', 'word_count', 'harshness_score', 
            'memorability_score', 'phonetic_complexity', 'semantic_transparency'
        ]
        
        X = df[feature_cols].fillna(0)
        
        # Fit K-means
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        df['cluster'] = kmeans.fit_predict(X)
        
        # Calculate silhouette score
        silhouette = silhouette_score(X, df['cluster'])
        
        # Analyze each cluster
        cluster_profiles = {}
        for cluster_id in range(n_clusters):
            cluster_df = df[df['cluster'] == cluster_id]
            
            cluster_profiles[f'cluster_{cluster_id}'] = {
                'size': len(cluster_df),
                'percentage': float((len(cluster_df) / len(df)) * 100),
                'mean_rating': float(cluster_df['bgg_rating'].mean()),
                'mean_syllables': float(cluster_df['syllable_count'].mean()),
                'mean_memorability': float(cluster_df['memorability_score'].mean()),
                'mean_complexity': float(cluster_df['complexity_weight'].mean()),
                'example_games': cluster_df.nlargest(5, 'bgg_rating')['name'].tolist()
            }
        
        # Update database with cluster assignments
        for idx, row in df.iterrows():
            analysis = BoardGameAnalysis.query.filter_by(game_id=row['id']).first()
            if analysis:
                analysis.combined_cluster = int(row['cluster'])
        
        try:
            db.session.commit()
        except Exception as e:
            logger.error(f"Error updating clusters: {e}")
            db.session.rollback()
        
        return {
            'n_clusters': n_clusters,
            'silhouette_score': float(silhouette),
            'cluster_profiles': cluster_profiles
        }
    
    def analyze_temporal_evolution(self, df: pd.DataFrame) -> Dict:
        """Analyze how naming conventions evolved over time.
        
        Args:
            df: Complete dataset
        
        Returns:
            Dict with temporal analysis
        """
        temporal_stats = {}
        
        # By era
        eras_ordered = ['classic_1950_1979', 'golden_1980_1999', 
                       'modern_2000_2009', 'contemporary_2010_2024']
        
        for era in eras_ordered:
            era_df = df[df['era'] == era]
            if len(era_df) > 0:
                temporal_stats[era] = {
                    'count': len(era_df),
                    'mean_syllables': float(era_df['syllable_count'].mean()),
                    'mean_words': float(era_df['word_count'].mean()),
                    'mean_complexity': float(era_df['complexity_weight'].mean()),
                    'colon_percentage': float((era_df['contains_colon'].sum() / len(era_df)) * 100),
                    'fantasy_names': float((era_df['is_fantasy_name'].sum() / len(era_df)) * 100)
                }
        
        # Calculate trends
        if len(temporal_stats) >= 3:
            syllable_values = [temporal_stats[era]['mean_syllables'] for era in eras_ordered if era in temporal_stats]
            complexity_values = [temporal_stats[era]['mean_complexity'] for era in eras_ordered if era in temporal_stats]
            
            temporal_stats['trends'] = {
                'syllable_increase': float(syllable_values[-1] - syllable_values[0]),
                'complexity_increase': float(complexity_values[-1] - complexity_values[0]),
                'syllables_per_decade': float((syllable_values[-1] - syllable_values[0]) / len(syllable_values)) if len(syllable_values) > 1 else 0
            }
        
        # Statistical test for temporal trend
        if 'year_published' in df.columns and df['year_published'].notna().sum() > 50:
            # Correlation between year and syllable count
            valid_years = df[df['year_published'].notna()]
            corr, p_value = stats.pearsonr(valid_years['year_published'], 
                                          valid_years['syllable_count'])
            
            temporal_stats['year_syllable_correlation'] = {
                'r': float(corr),
                'p_value': float(p_value),
                'significant': p_value < 0.05
            }
        
        return temporal_stats
    
    def analyze_cultural_patterns(self, df: pd.DataFrame) -> Dict:
        """Compare naming patterns across cultural traditions.
        
        Args:
            df: Complete dataset
        
        Returns:
            Dict with cultural comparison results
        """
        cultural_stats = {}
        
        # Group by designer nationality
        top_nationalities = df['designer_nationality'].value_counts().head(5).index
        
        for nationality in top_nationalities:
            nat_df = df[df['designer_nationality'] == nationality]
            if len(nat_df) >= 10:
                cultural_stats[nationality] = {
                    'count': len(nat_df),
                    'mean_syllables': float(nat_df['syllable_count'].mean()),
                    'mean_words': float(nat_df['word_count'].mean()),
                    'mean_rating': float(nat_df['bgg_rating'].mean()),
                    'mean_complexity': float(nat_df['complexity_weight'].mean()),
                    'fantasy_names_pct': float((nat_df['is_fantasy_name'].sum() / len(nat_df)) * 100),
                    'abstract_names_pct': float((nat_df['name_type'] == 'abstract').sum() / len(nat_df) * 100)
                }
        
        # Statistical comparison: US vs DE (Euro) vs JP
        comparisons = {}
        if 'US' in cultural_stats and 'DE' in cultural_stats:
            us_df = df[df['designer_nationality'] == 'US']
            de_df = df[df['designer_nationality'] == 'DE']
            
            # T-test on syllable count
            t_stat, p_value = stats.ttest_ind(us_df['syllable_count'], de_df['syllable_count'])
            cohens_d = (us_df['syllable_count'].mean() - de_df['syllable_count'].mean()) / \
                       np.sqrt((us_df['syllable_count'].std()**2 + de_df['syllable_count'].std()**2) / 2)
            
            comparisons['us_vs_euro'] = {
                't_statistic': float(t_stat),
                'p_value': float(p_value),
                'cohens_d': float(cohens_d),
                'significant': p_value < 0.05,
                'interpretation': 'Euro games have more abstract names' if de_df['syllable_count'].mean() < us_df['syllable_count'].mean() else 'US games have simpler names'
            }
        
        return {
            'by_nationality': cultural_stats,
            'comparisons': comparisons
        }
    
    def predict_success(self, df: pd.DataFrame) -> Dict:
        """Build model to predict BGG rating from name features.
        
        Args:
            df: Complete dataset
        
        Returns:
            Dict with prediction results
        """
        # Filter to games with valid ratings
        df_valid = df[df['bgg_rating'] > 0].copy()
        
        if len(df_valid) < 100:
            return {'error': 'Insufficient data for prediction'}
        
        # Select features
        feature_cols = [
            'syllable_count', 'word_count', 'memorability_score',
            'phonetic_complexity', 'semantic_transparency', 
            'harshness_score', 'vowel_ratio', 'pronounceability_score'
        ]
        
        X = df_valid[feature_cols].fillna(0)
        y = df_valid['bgg_rating']
        
        # Control variables (if using multiple regression)
        # For now, just name features
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train Random Forest
        model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)
        
        train_r2 = r2_score(y_train, y_pred_train)
        test_r2 = r2_score(y_test, y_pred_test)
        
        # Feature importance
        importances = dict(zip(feature_cols, model.feature_importances_))
        sorted_importance = sorted(importances.items(), key=lambda x: x[1], reverse=True)
        
        # Simple correlations
        correlations = {}
        for col in feature_cols:
            if df_valid[col].std() > 0:
                r, p = stats.pearsonr(df_valid[col], df_valid['bgg_rating'])
                correlations[col] = {'r': float(r), 'p': float(p)}
        
        self.rating_model = model
        
        return {
            'train_r2': float(train_r2),
            'test_r2': float(test_r2),
            'rmse': float(np.sqrt(mean_squared_error(y_test, y_pred_test))),
            'feature_importance': {k: float(v) for k, v in sorted_importance},
            'correlations': correlations,
            'n_train': len(X_train),
            'n_test': len(X_test)
        }
    
    def analyze_complexity_correlation(self, df: pd.DataFrame) -> Dict:
        """Analyze correlation between name complexity and game complexity.
        
        Args:
            df: Complete dataset
        
        Returns:
            Dict with correlation analysis
        """
        # Filter to games with complexity data
        df_valid = df[df['complexity_weight'] > 0].copy()
        
        if len(df_valid) < 50:
            return {'error': 'Insufficient complexity data'}
        
        # Test H3: Name complexity correlates with game complexity
        name_complexity = df_valid['syllable_count'] + df_valid['word_count']
        game_complexity = df_valid['complexity_weight']
        
        # Pearson correlation
        r, p = stats.pearsonr(name_complexity, game_complexity)
        
        # By category
        category_corrs = {}
        for category in df_valid['category'].value_counts().head(5).index:
            cat_df = df_valid[df_valid['category'] == category]
            if len(cat_df) >= 10:
                cat_name_complexity = cat_df['syllable_count'] + cat_df['word_count']
                cat_game_complexity = cat_df['complexity_weight']
                r_cat, p_cat = stats.pearsonr(cat_name_complexity, cat_game_complexity)
                
                category_corrs[category] = {
                    'r': float(r_cat),
                    'p': float(p_cat),
                    'n': len(cat_df)
                }
        
        # Categorize games by complexity
        df_valid['complexity_category'] = pd.cut(
            df_valid['complexity_weight'],
            bins=[0, 2, 3, 4, 5],
            labels=['light', 'medium_light', 'medium_heavy', 'heavy']
        )
        
        complexity_by_cat = {}
        for comp_cat in ['light', 'medium_light', 'medium_heavy', 'heavy']:
            comp_df = df_valid[df_valid['complexity_category'] == comp_cat]
            if len(comp_df) > 0:
                complexity_by_cat[comp_cat] = {
                    'count': len(comp_df),
                    'mean_syllables': float(comp_df['syllable_count'].mean()),
                    'mean_words': float(comp_df['word_count'].mean())
                }
        
        return {
            'overall_correlation': {
                'r': float(r),
                'p_value': float(p),
                'significant': p < 0.05,
                'interpretation': 'Name complexity DOES correlate with game complexity' if p < 0.05 and r > 0.2 else 'Weak or no correlation'
            },
            'by_category': category_corrs,
            'by_complexity_level': complexity_by_cat,
            'n': len(df_valid)
        }
    
    def test_hypotheses(self, df: pd.DataFrame) -> Dict:
        """Test all 5 primary hypotheses.
        
        Args:
            df: Complete dataset
        
        Returns:
            Dict with hypothesis test results
        """
        results = {}
        
        # H1: Shorter names correlate with higher ratings
        r_h1, p_h1 = stats.pearsonr(df['syllable_count'], df['bgg_rating'])
        results['H1_brevity'] = {
            'hypothesis': 'Shorter names predict higher BGG ratings',
            'r': float(r_h1),
            'p_value': float(p_h1),
            'supported': p_h1 < 0.05 and r_h1 < -0.10,
            'effect_size': 'small' if abs(r_h1) < 0.3 else 'medium'
        }
        
        # H2: Euro-games more abstract than American
        if 'US' in df['designer_nationality'].values and 'DE' in df['designer_nationality'].values:
            us_abstract = (df[df['designer_nationality'] == 'US']['name_type'] == 'abstract').sum()
            de_abstract = (df[df['designer_nationality'] == 'DE']['name_type'] == 'abstract').sum()
            us_total = (df['designer_nationality'] == 'US').sum()
            de_total = (df['designer_nationality'] == 'DE').sum()
            
            us_pct = (us_abstract / us_total * 100) if us_total > 0 else 0
            de_pct = (de_abstract / de_total * 100) if de_total > 0 else 0
            
            results['H2_euro_abstraction'] = {
                'hypothesis': 'Euro-games have more abstract names than American games',
                'us_abstract_pct': float(us_pct),
                'euro_abstract_pct': float(de_pct),
                'difference': float(de_pct - us_pct),
                'supported': de_pct > us_pct + 10
            }
        
        # H3: Name complexity correlates with game complexity
        r_h3, p_h3 = stats.pearsonr(
            df['syllable_count'] + df['word_count'],
            df['complexity_weight']
        )
        results['H3_complexity_correlation'] = {
            'hypothesis': 'Name complexity correlates with game complexity',
            'r': float(r_h3),
            'p_value': float(p_h3),
            'supported': p_h3 < 0.05 and r_h3 > 0.20,
            'effect_size': 'medium' if r_h3 > 0.3 else 'small'
        }
        
        # H4: Contemporary games have longer names
        classic = df[df['era'] == 'classic_1950_1979']
        contemporary = df[df['era'] == 'contemporary_2010_2024']
        
        if len(classic) > 10 and len(contemporary) > 10:
            t_stat, p_h4 = stats.ttest_ind(contemporary['syllable_count'], classic['syllable_count'])
            cohens_d = (contemporary['syllable_count'].mean() - classic['syllable_count'].mean()) / \
                       np.sqrt((contemporary['syllable_count'].std()**2 + classic['syllable_count'].std()**2) / 2)
            
            results['H4_temporal_expansion'] = {
                'hypothesis': 'Contemporary games have longer names than classics',
                'classic_mean': float(classic['syllable_count'].mean()),
                'contemporary_mean': float(contemporary['syllable_count'].mean()),
                'difference': float(contemporary['syllable_count'].mean() - classic['syllable_count'].mean()),
                't_statistic': float(t_stat),
                'p_value': float(p_h4),
                'cohens_d': float(cohens_d),
                'supported': p_h4 < 0.05 and cohens_d > 0.3
            }
        
        # H5: Colon games form distinct cluster
        colon_games = df[df['contains_colon'] == True]
        no_colon_games = df[df['contains_colon'] == False]
        
        if len(colon_games) > 10:
            results['H5_colon_effect'] = {
                'hypothesis': 'Games with colons (expansions) form distinct naming cluster',
                'colon_count': len(colon_games),
                'colon_mean_syllables': float(colon_games['syllable_count'].mean()),
                'no_colon_mean_syllables': float(no_colon_games['syllable_count'].mean()),
                'difference': float(colon_games['syllable_count'].mean() - no_colon_games['syllable_count'].mean()),
                'supported': len(colon_games) > 0 and colon_games['syllable_count'].mean() > no_colon_games['syllable_count'].mean() + 1.0
            }
        
        return results
    
    def generate_summary_report(self) -> Dict:
        """Generate comprehensive summary report.
        
        Returns:
            Dict with complete analysis summary
        """
        df = self.get_comprehensive_dataset()
        
        if len(df) < 50:
            return {'error': 'Insufficient data for report', 'sample_size': len(df)}
        
        report = {
            'sample_size': len(df),
            'descriptive': self.analyze_descriptive_statistics(df),
            'clusters': self.analyze_clusters(df),
            'temporal': self.analyze_temporal_evolution(df),
            'cultural': self.analyze_cultural_patterns(df),
            'success_prediction': self.predict_success(df),
            'complexity': self.analyze_complexity_correlation(df),
            'hypotheses': self.test_hypotheses(df),
            'generated_at': datetime.now().isoformat()
        }
        
        return report


# Testing function
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    analyzer = BoardGameStatisticalAnalyzer()
    
    report = analyzer.generate_summary_report()
    print(json.dumps(report, indent=2))

