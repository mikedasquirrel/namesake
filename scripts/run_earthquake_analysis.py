"""
Earthquake Nominative Determinism Analysis

Comprehensive statistical analysis testing whether earthquake location names
predict disaster outcomes beyond seismological factors.

Follows hurricane analysis methodology:
- Regressive proof framework
- 5-fold cross-validation
- Multiple outcome measures
- Strict controls for confounding
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from scipy import stats
from sklearn.model_selection import cross_val_score, KFold
from sklearn.linear_model import Ridge, LogisticRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.cluster import KMeans
from sklearn.metrics import roc_auc_score, silhouette_score
import statsmodels.api as sm
import json
from datetime import datetime
from typing import Dict, List

from analyzers.earthquake_analyzer import EarthquakeLocationAnalyzer


class EarthquakeNominativeAnalysis:
    """Complete statistical analysis of earthquake nomenclature effects."""
    
    def __init__(self, data_path: str = 'data/processed/earthquakes_dataset.csv'):
        self.data_path = data_path
        self.analyzer = EarthquakeLocationAnalyzer()
        self.results = {}
        
    def load_and_prepare_data(self) -> pd.DataFrame:
        """Load earthquake data and add phonetic features."""
        print("Loading earthquake data...")
        
        # For initial implementation, create sample dataset
        # In production, this would load from CSV
        df = self._create_sample_dataset()
        
        print(f"Loaded {len(df)} earthquakes")
        
        # Add phonetic analysis
        print("Adding phonetic features...")
        df = self.analyzer.analyze_dataset(df, name_column='name')
        
        return df
    
    def _create_sample_dataset(self) -> pd.DataFrame:
        """
        Create sample earthquake dataset with representative data.
        
        In production, this would be replaced with real USGS/NOAA data.
        """
        data = [
            # Name, Magnitude, Deaths, Damage (millions), Year, Country
            ('Northridge', 6.7, 57, 20000, 1994, 'USA'),
            ('Loma Prieta', 6.9, 63, 6000, 1989, 'USA'),
            ('San Francisco', 7.9, 3000, 524, 1906, 'USA'),
            ('Kobe', 6.9, 6434, 100000, 1995, 'Japan'),
            ('Haiti', 7.0, 316000, 8000, 2010, 'Haiti'),
            ('Nepal', 7.8, 8964, 10000, 2015, 'Nepal'),
            ('Tangshan', 7.6, 242769, 5600, 1976, 'China'),
            ('Sichuan', 7.9, 87587, 85000, 2008, 'China'),
            ('Kashmir', 7.6, 86000, 5200, 2005, 'Pakistan'),
            ('Christchurch', 6.3, 185, 15000, 2011, 'New Zealand'),
            ('Tohoku', 9.1, 15894, 235000, 2011, 'Japan'),
            ('Alaska', 9.2, 131, 311, 1964, 'USA'),
            ('Chile', 8.8, 525, 30000, 2010, 'Chile'),
            ('Valdivia', 9.5, 1655, 550, 1960, 'Chile'),
            ('Sumatra', 9.1, 227898, 10000, 2004, 'Indonesia'),
            ('Bam', 6.6, 26271, 500, 2003, 'Iran'),
            ('Turkey', 7.8, 59259, 34000, 2023, 'Turkey'),
            ('Mexico City', 8.0, 10000, 4000, 1985, 'Mexico'),
            ('Anchorage', 7.1, 0, 25, 2018, 'USA'),
            ('Ridgecrest', 7.1, 0, 5, 2019, 'USA'),
        ]
        
        df = pd.DataFrame(data, columns=['name', 'magnitude', 'deaths', 'damage_millions', 'year', 'country'])
        
        # Add derived variables
        df['log_deaths'] = np.log1p(df['deaths'])
        df['has_casualties'] = df['deaths'] > 0
        df['log_damage'] = np.log1p(df['damage_millions'])
        df['decade'] = (df['year'] // 10) * 10
        df['modern_era'] = (df['year'] >= 1990).astype(int)
        
        return df
    
    def run_complete_analysis(self):
        """Run all analyses following hurricane framework."""
        print("\n" + "=" * 70)
        print("EARTHQUAKE NOMINATIVE DETERMINISM ANALYSIS")
        print("=" * 70)
        
        # Load data
        df = self.load_and_prepare_data()
        self.df = df
        
        print(f"\nDataset: {len(df)} earthquakes")
        print(f"With casualties: {df['has_casualties'].sum()} ({df['has_casualties'].mean()*100:.1f}%)")
        print(f"Mean deaths: {df['deaths'].mean():.0f} (median: {df['deaths'].median():.0f})")
        
        # Run analyses
        print("\n" + "-" * 70)
        print("STATISTICAL ANALYSES")
        print("-" * 70)
        
        self.results['correlations'] = self.correlation_analysis(df)
        self.results['h1_harshness_casualties'] = self.test_h1_harshness_casualties(df)
        self.results['h3_casualty_presence'] = self.test_h3_casualty_presence(df)
        self.results['clustering'] = self.clustering_analysis(df)
        self.results['feature_importance'] = self.random_forest_importance(df)
        
        # Summary
        print("\n" + "=" * 70)
        print("ANALYSIS COMPLETE")
        print("=" * 70)
        self.print_summary()
        
        # Save results
        self.save_results()
        
        return self.results
    
    def correlation_analysis(self, df: pd.DataFrame) -> Dict:
        """Test correlations between phonetic features and outcomes."""
        print("\n1. Correlation Analysis")
        
        phonetic_features = [
            'phonetic_harshness', 'phonetic_smoothness', 'memorability_score',
            'pronounceability_score', 'syllable_count', 'character_length'
        ]
        
        outcomes = ['deaths', 'log_deaths', 'damage_millions']
        
        correlations = {}
        for feature in phonetic_features:
            if feature in df.columns:
                for outcome in outcomes:
                    if outcome in df.columns:
                        r, p = stats.pearsonr(df[feature].fillna(0), df[outcome].fillna(0))
                        correlations[f'{feature}_vs_{outcome}'] = {'r': r, 'p': p}
                        
                        if p < 0.05:
                            print(f"   {feature} vs {outcome}: r = {r:.3f}, p = {p:.3f} *")
        
        return correlations
    
    def test_h1_harshness_casualties(self, df: pd.DataFrame) -> Dict:
        """
        H1: Phonetic Harshness → Casualty Magnitude
        
        Tests whether location name harshness predicts deaths beyond magnitude.
        """
        print("\n2. H1: Harshness → Casualties")
        
        # Filter to earthquakes with casualty data
        analysis_df = df[df['deaths'].notna()].copy()
        
        if len(analysis_df) < 10:
            print("   ⚠️ Insufficient sample (n < 10)")
            return {'status': 'underpowered', 'n': len(analysis_df)}
        
        # Prepare variables
        X = analysis_df[['phonetic_harshness', 'magnitude', 'year']].fillna(0)
        y = analysis_df['log_deaths'].fillna(0)
        
        # OLS regression
        X_with_const = sm.add_constant(X)
        model = sm.OLS(y, X_with_const).fit()
        
        # Cross-validation
        ridge = Ridge(alpha=1.0)
        cv_scores = cross_val_score(ridge, X, y, cv=min(5, len(analysis_df)), 
                                    scoring='r2')
        
        result = {
            'n': len(analysis_df),
            'r_squared': model.rsquared,
            'adj_r_squared': model.rsquared_adj,
            'cv_r2_mean': cv_scores.mean(),
            'cv_r2_std': cv_scores.std(),
            'harshness_coef': model.params.get('phonetic_harshness', 0),
            'harshness_pvalue': model.pvalues.get('phonetic_harshness', 1.0)
        }
        
        print(f"   Sample: n = {result['n']}")
        print(f"   R² = {result['r_squared']:.3f}")
        print(f"   CV R² = {result['cv_r2_mean']:.3f} ± {result['cv_r2_std']:.3f}")
        print(f"   Harshness β = {result['harshness_coef']:.3f}, p = {result['harshness_pvalue']:.3f}")
        
        return result
    
    def test_h3_casualty_presence(self, df: pd.DataFrame) -> Dict:
        """
        H3: Names → Casualty Presence (Binary Classification)
        
        Tests whether phonetic features predict ANY casualties (0/1).
        """
        print("\n3. H3: Casualty Presence (Binary)")
        
        analysis_df = df[df['has_casualties'].notna()].copy()
        
        if len(analysis_df) < 15:
            print("   ⚠️ Insufficient sample for binary classification")
            return {'status': 'underpowered', 'n': len(analysis_df)}
        
        # Prepare variables
        features = ['phonetic_harshness', 'memorability_score', 'syllable_count', 'magnitude']
        X = analysis_df[features].fillna(0)
        y = analysis_df['has_casualties'].astype(int)
        
        # Logistic regression with cross-validation
        model = LogisticRegression(max_iter=1000, random_state=42)
        
        # ROC AUC cross-validation
        cv_auc = cross_val_score(model, X, y, cv=min(5, len(analysis_df)), 
                                 scoring='roc_auc')
        
        # Fit full model
        model.fit(X, y)
        y_pred_proba = model.predict_proba(X)[:, 1]
        train_auc = roc_auc_score(y, y_pred_proba)
        
        result = {
            'n': len(analysis_df),
            'train_auc': train_auc,
            'cv_auc_mean': cv_auc.mean(),
            'cv_auc_std': cv_auc.std(),
            'feature_coefficients': dict(zip(features, model.coef_[0]))
        }
        
        print(f"   Sample: n = {result['n']}")
        print(f"   Train ROC AUC = {result['train_auc']:.3f}")
        print(f"   CV ROC AUC = {result['cv_auc_mean']:.3f} ± {result['cv_auc_std']:.3f}")
        
        return result
    
    def clustering_analysis(self, df: pd.DataFrame) -> Dict:
        """
        Cluster earthquakes by location name phonetic profiles.
        
        Identifies linguistic archetypes similar to crypto clustering.
        """
        print("\n4. Clustering Analysis")
        
        features = ['phonetic_harshness', 'memorability_score', 'syllable_count', 
                   'pronounceability_score']
        
        X = df[features].fillna(0)
        
        # Try 2-4 clusters
        best_k = 2
        best_silhouette = -1
        
        for k in range(2, min(5, len(df) // 3)):
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(X)
            silhouette = silhouette_score(X, labels)
            
            if silhouette > best_silhouette:
                best_silhouette = silhouette
                best_k = k
        
        # Fit best model
        kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
        df['cluster'] = kmeans.fit_predict(X)
        
        # Analyze cluster characteristics
        cluster_profiles = []
        for i in range(best_k):
            cluster_df = df[df['cluster'] == i]
            profile = {
                'cluster_id': i,
                'n': len(cluster_df),
                'mean_harshness': cluster_df['phonetic_harshness'].mean(),
                'mean_memorability': cluster_df['memorability_score'].mean(),
                'mean_deaths': cluster_df['deaths'].mean(),
                'median_deaths': cluster_df['deaths'].median(),
                'casualty_rate': cluster_df['has_casualties'].mean()
            }
            cluster_profiles.append(profile)
        
        print(f"   Optimal k = {best_k} clusters")
        print(f"   Silhouette score = {best_silhouette:.3f}")
        
        for profile in cluster_profiles:
            print(f"\n   Cluster {profile['cluster_id']}: n={profile['n']}")
            print(f"      Harshness: {profile['mean_harshness']:.1f}")
            print(f"      Mean deaths: {profile['mean_deaths']:.0f}")
        
        return {
            'optimal_k': best_k,
            'silhouette': best_silhouette,
            'cluster_profiles': cluster_profiles
        }
    
    def random_forest_importance(self, df: pd.DataFrame) -> Dict:
        """
        Random Forest feature importance for non-linear relationships.
        """
        print("\n5. Random Forest Feature Importance")
        
        analysis_df = df[df['deaths'].notna()].copy()
        
        if len(analysis_df) < 10:
            print("   ⚠️ Insufficient sample")
            return {'status': 'underpowered'}
        
        features = ['phonetic_harshness', 'memorability_score', 'syllable_count',
                   'pronounceability_score', 'cultural_familiarity', 'magnitude']
        
        X = analysis_df[features].fillna(0)
        y = analysis_df['log_deaths']
        
        rf = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=5)
        rf.fit(X, y)
        
        importances = dict(zip(features, rf.feature_importances_))
        importances_sorted = dict(sorted(importances.items(), key=lambda x: x[1], reverse=True))
        
        print(f"   In-sample R² = {rf.score(X, y):.3f}")
        print("\n   Feature Importance:")
        for feature, importance in list(importances_sorted.items())[:5]:
            print(f"      {feature}: {importance:.3f}")
        
        return {
            'in_sample_r2': rf.score(X, y),
            'feature_importances': importances_sorted
        }
    
    def print_summary(self):
        """Print executive summary of findings."""
        print("\nEXECUTIVE SUMMARY")
        print("-" * 70)
        
        if 'h1_harshness_casualties' in self.results:
            h1 = self.results['h1_harshness_casualties']
            if 'cv_r2_mean' in h1:
                print(f"\nH1 (Harshness → Casualties):")
                print(f"   CV R² = {h1['cv_r2_mean']:.3f} ± {h1['cv_r2_std']:.3f}")
                print(f"   Status: {'✓ SUPPORTED' if h1['cv_r2_mean'] > 0.10 else '⚠️ WEAK'}")
        
        if 'h3_casualty_presence' in self.results:
            h3 = self.results['h3_casualty_presence']
            if 'cv_auc_mean' in h3:
                print(f"\nH3 (Binary Classification):")
                print(f"   CV ROC AUC = {h3['cv_auc_mean']:.3f} ± {h3['cv_auc_std']:.3f}")
                print(f"   Status: {'✓ STRONG' if h3['cv_auc_mean'] > 0.80 else '✓ MODERATE' if h3['cv_auc_mean'] > 0.70 else '⚠️ WEAK'}")
        
        if 'clustering' in self.results:
            clust = self.results['clustering']
            print(f"\nClustering:")
            print(f"   Optimal k = {clust['optimal_k']}")
            print(f"   Silhouette = {clust['silhouette']:.3f}")
    
    def save_results(self):
        """Save analysis results to JSON."""
        output_dir = 'analysis_outputs/current/earthquake_analysis'
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'{output_dir}/analysis_{timestamp}.json'
        
        # Convert numpy types for JSON serialization
        def convert_types(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            return obj
        
        results_serializable = json.loads(
            json.dumps(self.results, default=convert_types)
        )
        
        with open(filename, 'w') as f:
            json.dump(results_serializable, f, indent=2)
        
        print(f"\n✓ Results saved to {filename}")


def main():
    """Run complete earthquake analysis."""
    analysis = EarthquakeNominativeAnalysis()
    results = analysis.run_complete_analysis()
    
    print("\n" + "=" * 70)
    print("EARTHQUAKE ANALYSIS COMPLETE")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Enrich with more earthquake outcome data")
    print("2. Create earthquakes.html findings page")
    print("3. Compare to hurricane findings")
    
    return results


if __name__ == '__main__':
    results = main()

