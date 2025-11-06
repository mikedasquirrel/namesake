"""Band Statistical Analyzer

Comprehensive statistical modeling for band name success prediction.
Implements clustering, regression, and feature importance analysis.

Models:
- Success prediction: linguistic features → popularity/longevity
- Era-specific formulas: what works in each decade
- Genre-specific patterns: metal vs pop vs electronic naming
- Cross-sphere validation: bands as cultural longevity test
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

from core.models import db, Band, BandAnalysis

logger = logging.getLogger(__name__)


class BandStatisticalAnalyzer:
    """Comprehensive statistical analysis for band name success prediction."""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.success_model = None
        self.longevity_model = None
    
    def get_comprehensive_dataset(self) -> pd.DataFrame:
        """Load all bands with complete data.
        
        Returns:
            DataFrame with band and analysis data
        """
        query = db.session.query(Band, BandAnalysis).join(
            BandAnalysis,
            Band.id == BandAnalysis.band_id
        )
        
        rows = []
        for band, analysis in query.all():
            try:
                row = {
                    # Metadata
                    'id': band.id,
                    'name': band.name,
                    'formation_year': band.formation_year,
                    'formation_decade': band.formation_decade,
                    'origin_country': band.origin_country,
                    'genre_cluster': band.genre_cluster,
                    'is_active': band.is_active,
                    'years_active': band.years_active or 0,
                    
                    # Outcomes (dependent variables)
                    'popularity_score': band.popularity_score or 0,
                    'longevity_score': band.longevity_score or 0,
                    'cross_generational_appeal': band.cross_generational_appeal or False,
                    'listeners_count': band.listeners_count or 0,
                    
                    # Linguistic features (predictors)
                    'syllable_count': analysis.syllable_count or 0,
                    'character_length': analysis.character_length or 0,
                    'word_count': analysis.word_count or 0,
                    'memorability_score': analysis.memorability_score or 0,
                    'pronounceability_score': analysis.pronounceability_score or 0,
                    'uniqueness_score': analysis.uniqueness_score or 0,
                    'fantasy_score': analysis.fantasy_score or 0,
                    'power_connotation_score': analysis.power_connotation_score or 0,
                    'harshness_score': analysis.harshness_score or 0,
                    'softness_score': analysis.softness_score or 0,
                    'abstraction_score': analysis.abstraction_score or 0,
                    'literary_reference_score': analysis.literary_reference_score or 0,
                    'phonetic_score': analysis.phonetic_score or 0,
                    'vowel_ratio': analysis.vowel_ratio or 0,
                    
                    # Contextual
                    'temporal_cohort': analysis.temporal_cohort,
                    'geographic_cluster': analysis.geographic_cluster,
                }
                
                rows.append(row)
                
            except Exception as e:
                logger.warning(f"Error loading band {band.name}: {e}")
                continue
        
        df = pd.DataFrame(rows)
        logger.info(f"Loaded {len(df)} bands for statistical analysis")
        
        return df
    
    def analyze_success_predictors(self, df: pd.DataFrame) -> Dict:
        """Analyze which linguistic features predict success.
        
        Args:
            df: DataFrame with band data
            
        Returns:
            Success prediction analysis results
        """
        logger.info("Analyzing success predictors...")
        
        results = {
            'popularity_model': {},
            'longevity_model': {},
            'cross_generational_model': {},
            'feature_importance': {},
            'genre_specific_formulas': {},
            'era_specific_formulas': {}
        }
        
        # Define feature columns
        feature_cols = [
            'syllable_count', 'character_length', 'word_count',
            'memorability_score', 'pronounceability_score', 'uniqueness_score',
            'fantasy_score', 'power_connotation_score', 'harshness_score',
            'softness_score', 'abstraction_score', 'literary_reference_score',
            'phonetic_score', 'vowel_ratio'
        ]
        
        # Prepare data
        df_clean = df[feature_cols + ['popularity_score', 'longevity_score']].dropna()
        
        if len(df_clean) < 50:
            logger.warning("Insufficient data for statistical modeling")
            return results
        
        X = df_clean[feature_cols]
        
        # 1. Popularity prediction
        y_popularity = df_clean['popularity_score']
        results['popularity_model'] = self._train_regression_model(
            X, y_popularity, 'Popularity', feature_cols
        )
        
        # 2. Longevity prediction
        y_longevity = df_clean['longevity_score']
        results['longevity_model'] = self._train_regression_model(
            X, y_longevity, 'Longevity', feature_cols
        )
        
        # 3. Cross-generational appeal (classification)
        df_appeal = df[feature_cols + ['cross_generational_appeal']].dropna()
        if len(df_appeal) >= 50 and df_appeal['cross_generational_appeal'].sum() > 10:
            X_appeal = df_appeal[feature_cols]
            y_appeal = df_appeal['cross_generational_appeal'].astype(int)
            results['cross_generational_model'] = self._train_classification_model(
                X_appeal, y_appeal, 'Cross-Generational Appeal', feature_cols
            )
        
        # 4. Combined feature importance
        results['feature_importance'] = self._analyze_feature_importance(
            results['popularity_model'],
            results['longevity_model'],
            feature_cols
        )
        
        # 5. Genre-specific formulas
        results['genre_specific_formulas'] = self._analyze_genre_formulas(df, feature_cols)
        
        # 6. Era-specific formulas
        results['era_specific_formulas'] = self._analyze_era_formulas(df, feature_cols)
        
        return results
    
    def _train_regression_model(self, X: pd.DataFrame, y: pd.Series, 
                                 target_name: str, feature_names: List[str]) -> Dict:
        """Train Random Forest regression model.
        
        Args:
            X: Feature matrix
            y: Target variable
            target_name: Name of target (for logging)
            feature_names: List of feature names
            
        Returns:
            Model results
        """
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train model
        model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        r2 = r2_score(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        # Cross-validation
        cv_scores = cross_val_score(model, X, y, cv=5, scoring='r2')
        
        # Feature importance
        feature_importance = dict(zip(feature_names, model.feature_importances_))
        top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'target': target_name,
            'r2_score': float(r2),
            'rmse': float(rmse),
            'cv_mean': float(cv_scores.mean()),
            'cv_std': float(cv_scores.std()),
            'sample_size': len(X),
            'top_features': [{'feature': f, 'importance': float(imp)} for f, imp in top_features],
            'all_feature_importance': {k: float(v) for k, v in feature_importance.items()}
        }
    
    def _train_classification_model(self, X: pd.DataFrame, y: pd.Series,
                                     target_name: str, feature_names: List[str]) -> Dict:
        """Train Random Forest classification model.
        
        Args:
            X: Feature matrix
            y: Target variable (binary)
            target_name: Name of target
            feature_names: List of feature names
            
        Returns:
            Model results
        """
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Train model
        model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
        model.fit(X_train, y_train)
        
        # Evaluate
        accuracy = model.score(X_test, y_test)
        
        # Cross-validation
        cv_scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
        
        # Feature importance
        feature_importance = dict(zip(feature_names, model.feature_importances_))
        top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'target': target_name,
            'accuracy': float(accuracy),
            'cv_mean': float(cv_scores.mean()),
            'cv_std': float(cv_scores.std()),
            'sample_size': len(X),
            'positive_class_count': int(y.sum()),
            'top_features': [{'feature': f, 'importance': float(imp)} for f, imp in top_features]
        }
    
    def _analyze_feature_importance(self, popularity_model: Dict, 
                                     longevity_model: Dict,
                                     feature_names: List[str]) -> Dict:
        """Analyze combined feature importance across models.
        
        Args:
            popularity_model: Popularity prediction results
            longevity_model: Longevity prediction results
            feature_names: List of features
            
        Returns:
            Combined importance rankings
        """
        combined_importance = {}
        
        # Average importance across models
        for feature in feature_names:
            pop_imp = popularity_model.get('all_feature_importance', {}).get(feature, 0)
            lon_imp = longevity_model.get('all_feature_importance', {}).get(feature, 0)
            
            combined_importance[feature] = {
                'popularity_importance': float(pop_imp),
                'longevity_importance': float(lon_imp),
                'average_importance': float((pop_imp + lon_imp) / 2),
                'max_importance': float(max(pop_imp, lon_imp))
            }
        
        # Rank by average importance
        ranked = sorted(combined_importance.items(), 
                       key=lambda x: x[1]['average_importance'],
                       reverse=True)
        
        return {
            'ranked_features': [
                {'feature': f, **stats} for f, stats in ranked
            ],
            'top_5_universal': [f for f, _ in ranked[:5]]
        }
    
    def _analyze_genre_formulas(self, df: pd.DataFrame, feature_cols: List[str]) -> Dict:
        """Analyze genre-specific success formulas.
        
        Args:
            df: DataFrame with all data
            feature_cols: Feature columns
            
        Returns:
            Genre-specific formulas
        """
        formulas = {}
        
        major_genres = ['rock', 'metal', 'pop', 'punk', 'electronic']
        
        for genre in major_genres:
            genre_data = df[df['genre_cluster'] == genre]
            
            if len(genre_data) < 20:
                continue
            
            # Correlations with success
            correlations = {}
            for feature in feature_cols:
                if feature in genre_data.columns and 'popularity_score' in genre_data.columns:
                    corr, p_value = stats.pearsonr(
                        genre_data[feature].fillna(0),
                        genre_data['popularity_score'].fillna(0)
                    )
                    
                    if not np.isnan(corr):
                        correlations[feature] = {
                            'correlation': float(corr),
                            'p_value': float(p_value),
                            'significant': p_value < 0.05
                        }
            
            # Top correlates
            sig_correlations = {k: v for k, v in correlations.items() if v['significant']}
            top_correlates = sorted(sig_correlations.items(),
                                   key=lambda x: abs(x[1]['correlation']),
                                   reverse=True)[:5]
            
            formulas[genre] = {
                'sample_size': len(genre_data),
                'avg_popularity': float(genre_data['popularity_score'].mean()),
                'top_success_predictors': [
                    {
                        'feature': f,
                        'correlation': c['correlation'],
                        'direction': 'positive' if c['correlation'] > 0 else 'negative'
                    }
                    for f, c in top_correlates
                ],
                'genre_profile': {
                    feature: float(genre_data[feature].mean())
                    for feature in feature_cols
                    if feature in genre_data.columns
                }
            }
        
        return formulas
    
    def _analyze_era_formulas(self, df: pd.DataFrame, feature_cols: List[str]) -> Dict:
        """Analyze era-specific success formulas.
        
        Args:
            df: DataFrame with all data
            feature_cols: Feature columns
            
        Returns:
            Era-specific formulas
        """
        formulas = {}
        
        decades = [1960, 1970, 1980, 1990, 2000, 2010]
        
        for decade in decades:
            era_data = df[df['formation_decade'] == decade]
            
            if len(era_data) < 20:
                continue
            
            # Correlations with success
            correlations = {}
            for feature in feature_cols:
                if feature in era_data.columns and 'popularity_score' in era_data.columns:
                    valid_data = era_data[[feature, 'popularity_score']].dropna()
                    
                    if len(valid_data) < 10:
                        continue
                    
                    corr, p_value = stats.pearsonr(
                        valid_data[feature],
                        valid_data['popularity_score']
                    )
                    
                    if not np.isnan(corr):
                        correlations[feature] = {
                            'correlation': float(corr),
                            'p_value': float(p_value)
                        }
            
            # Top correlates
            sig_correlations = {k: v for k, v in correlations.items() if v.get('p_value', 1) < 0.05}
            top_correlates = sorted(sig_correlations.items(),
                                   key=lambda x: abs(x[1]['correlation']),
                                   reverse=True)[:5]
            
            formulas[f"{decade}s"] = {
                'sample_size': len(era_data),
                'success_formula': [
                    {'feature': f, 'correlation': float(c['correlation'])}
                    for f, c in top_correlates
                ] if top_correlates else []
            }
        
        return formulas
    
    def cluster_bands(self, df: pd.DataFrame, n_clusters: int = 5) -> Dict:
        """Cluster bands by linguistic profile.
        
        Args:
            df: DataFrame with band data
            n_clusters: Number of clusters
            
        Returns:
            Clustering results
        """
        logger.info(f"Clustering bands into {n_clusters} groups...")
        
        feature_cols = [
            'syllable_count', 'character_length', 'memorability_score',
            'fantasy_score', 'harshness_score', 'abstraction_score'
        ]
        
        # Prepare data
        df_clean = df[feature_cols + ['name', 'popularity_score', 'formation_decade']].dropna()
        
        if len(df_clean) < n_clusters * 5:
            return {'error': 'Insufficient data for clustering'}
        
        X = df_clean[feature_cols]
        
        # Standardize
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Cluster
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(X_scaled)
        
        df_clean['cluster'] = clusters
        
        # Compute cluster profiles
        cluster_profiles = []
        for cluster_id in range(n_clusters):
            cluster_data = df_clean[df_clean['cluster'] == cluster_id]
            
            profile = {
                'cluster_id': int(cluster_id),
                'size': len(cluster_data),
                'percentage': float(len(cluster_data) / len(df_clean) * 100),
                'avg_popularity': float(cluster_data['popularity_score'].mean()),
                'example_bands': cluster_data.nlargest(10, 'popularity_score')['name'].tolist(),
                'linguistic_profile': {
                    feature: float(cluster_data[feature].mean())
                    for feature in feature_cols
                },
                'decade_distribution': cluster_data['formation_decade'].value_counts().to_dict()
            }
            
            # Name the cluster
            profile['cluster_name'] = self._name_cluster(profile['linguistic_profile'])
            
            cluster_profiles.append(profile)
        
        # Calculate silhouette score
        silhouette = silhouette_score(X_scaled, clusters)
        
        return {
            'n_clusters': n_clusters,
            'silhouette_score': float(silhouette),
            'quality': 'good' if silhouette > 0.3 else 'fair' if silhouette > 0.2 else 'poor',
            'clusters': cluster_profiles
        }
    
    def _name_cluster(self, profile: Dict) -> str:
        """Assign descriptive name to cluster.
        
        Args:
            profile: Cluster linguistic profile
            
        Returns:
            Cluster name
        """
        syllables = profile.get('syllable_count', 0)
        memorability = profile.get('memorability_score', 0)
        fantasy = profile.get('fantasy_score', 0)
        harshness = profile.get('harshness_score', 0)
        abstraction = profile.get('abstraction_score', 0)
        
        # Classification heuristics
        if syllables < 2.5 and memorability > 65:
            return "Punchy & Iconic"
        elif fantasy > 65:
            return "Mythological/Epic"
        elif harshness > 65:
            return "Aggressive/Edgy"
        elif abstraction > 60:
            return "Abstract/Experimental"
        elif syllables > 3.5:
            return "Literary/Complex"
        else:
            return "Mainstream/Balanced"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    analyzer = BandStatisticalAnalyzer()
    df = analyzer.get_comprehensive_dataset()
    
    if len(df) > 50:
        # Run success prediction analysis
        success_results = analyzer.analyze_success_predictors(df)
        
        print("\n" + "="*60)
        print("SUCCESS PREDICTION ANALYSIS")
        print("="*60)
        
        print("\nPopularity Model:")
        pop_model = success_results['popularity_model']
        print(f"  R² Score: {pop_model.get('r2_score', 0):.3f}")
        print(f"  CV Score: {pop_model.get('cv_mean', 0):.3f} ± {pop_model.get('cv_std', 0):.3f}")
        print("\n  Top Predictors:")
        for feat in pop_model.get('top_features', [])[:5]:
            print(f"    {feat['feature']}: {feat['importance']:.3f}")
        
        print("\n\nLongevity Model:")
        lon_model = success_results['longevity_model']
        print(f"  R² Score: {lon_model.get('r2_score', 0):.3f}")
        print(f"  CV Score: {lon_model.get('cv_mean', 0):.3f} ± {lon_model.get('cv_std', 0):.3f}")
        
        # Run clustering
        cluster_results = analyzer.cluster_bands(df, n_clusters=5)
        
        print("\n\n" + "="*60)
        print("CLUSTERING ANALYSIS")
        print("="*60)
        print(f"\nSilhouette Score: {cluster_results.get('silhouette_score', 0):.3f}")
        print(f"Quality: {cluster_results.get('quality', 'N/A')}")
        
        for cluster in cluster_results.get('clusters', []):
            print(f"\n{cluster['cluster_name']} (n={cluster['size']}):")
            print(f"  Avg popularity: {cluster['avg_popularity']:.1f}")
            print(f"  Examples: {', '.join(cluster['example_bands'][:3])}")
    else:
        print("Insufficient data. Run band_collector.py to collect bands first.")

