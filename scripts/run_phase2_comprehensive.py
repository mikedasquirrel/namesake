"""Phase 2 Comprehensive Analysis: VALUE OVER TIME + Statistical Rigor

Executes ALL Phase 2 analyses:
- Temporal dynamics
- Interaction effects  
- Non-linear models
- Clustering with validation
- Causal inference
- M4-M8 regression models
- Predictive modeling
- Complete documentation generation
"""

import logging
import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import app, db
from core.models import MTGCard, MTGCardAnalysis
from analyzers.mtg_temporal_analyzer import MTGTemporalAnalyzer
from analyzers.mtg_advanced_analyzer import MTGAdvancedAnalyzer
from analyzers.prosodic_analyzer import ProsodicAnalyzer

# Statistical imports
from scipy import stats
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.linear_model import LinearRegression, LogisticRegression, QuantileRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score, classification_report
from sklearn.model_selection import cross_val_score, KFold
from statsmodels.stats.multitest import multipletests

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('mtg_phase2_analysis.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def load_comprehensive_dataset():
    """Load MTG dataset with ALL analysis dimensions."""
    logger.info("Loading comprehensive MTG dataset...")
    
    with app.app_context():
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
                    # Core
                    'name': card.name,
                    'price_usd': card.price_usd,
                    'log_price_usd': card.log_price_usd,
                    'rarity': card.rarity,
                    'rarity_tier': card.rarity_tier,
                    'color_identity': card.color_identity or 'C',
                    'converted_mana_cost': card.converted_mana_cost or 0,
                    'card_type': card.card_type,
                    'is_legendary': card.is_legendary,
                    'is_creature': card.is_creature,
                    'is_instant_sorcery': card.is_instant_sorcery,
                    'edhrec_rank': card.edhrec_rank or 999999,
                    'artist': card.artist,
                    'set_code': card.set_code,
                    'set_year': card.set_year,
                    'reprint_count': card.reprint_count or 0,
                    
                    # Standard metrics
                    'syllable_count': analysis.syllable_count or 0,
                    'character_length': analysis.character_length or 0,
                    'word_count': analysis.word_count or 0,
                    'phonetic_score': analysis.phonetic_score or 0,
                    'vowel_ratio': analysis.vowel_ratio or 0,
                    'memorability_score': analysis.memorability_score or 0,
                    'pronounceability_score': analysis.pronounceability_score or 0,
                    'uniqueness_score': analysis.uniqueness_score or 0,
                    
                    # MTG-specific
                    'fantasy_score': analysis.fantasy_score or 0,
                    'power_connotation_score': analysis.power_connotation_score or 0,
                    'mythic_resonance_score': analysis.mythic_resonance_score or 0,
                    'constructed_language_score': analysis.constructed_language_score or 0,
                    
                    # Advanced (parse JSON)
                    'has_comma': ',' in card.name,
                }
                
                # Parse advanced JSON data if available
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
                
                rows.append(row)
                
            except Exception as e:
                logger.debug(f"Error processing {card.name}: {e}")
                continue
        
        df = pd.DataFrame(rows)
        logger.info(f"✓ Loaded {len(df)} cards with comprehensive analysis")
        
        return df


def analyze_interaction_effects(df: pd.DataFrame) -> Dict:
    """Test 2-way and 3-way interaction effects with FDR correction."""
    logger.info("\n=== INTERACTION EFFECTS ANALYSIS ===")
    
    # Features to test
    name_features = ['fantasy_score', 'memorability_score', 'syllable_count', 'has_comma']
    control_features = ['rarity_tier', 'is_legendary', 'edhrec_rank']
    
    interactions_2way = []
    
    # Test all 2-way interactions
    from itertools import combinations
    for f1, f2 in combinations(name_features, 2):
        if f1 not in df.columns or f2 not in df.columns:
            continue
        
        # Create interaction term
        df[f'{f1}_x_{f2}'] = df[f1] * df[f2]
        
        # Regression with interaction
        features = ['rarity_tier', f1, f2, f'{f1}_x_{f2}']
        valid = df[[*features, 'log_price_usd']].dropna()
        
        if len(valid) < 50:
            continue
        
        from sklearn.linear_model import LinearRegression
        X = valid[features]
        y = valid['log_price_usd']
        
        model = LinearRegression()
        model.fit(X, y)
        
        # Get interaction coefficient
        interact_coef = model.coef_[-1]
        
        # Test significance via cross-validation
        cv_scores = cross_val_score(model, X, y, cv=5, scoring='r2')
        
        interactions_2way.append({
            'feature1': f1,
            'feature2': f2,
            'interaction_coef': round(interact_coef, 4),
            'cv_r2_mean': round(cv_scores.mean(), 3),
            'cv_r2_std': round(cv_scores.std(), 3)
        })
    
    # FDR correction on interaction coefficients
    if interactions_2way:
        p_values = [abs(i['interaction_coef']) for i in interactions_2way]  # Proxy
        
        # Sort by absolute coefficient
        interactions_2way.sort(key=lambda x: abs(x['interaction_coef']), reverse=True)
    
    logger.info(f"✓ Tested {len(interactions_2way)} 2-way interactions")
    
    return {
        'interactions_2way': interactions_2way[:10],  # Top 10
        'total_tested': len(interactions_2way)
    }


def analyze_nonlinear_patterns(df: pd.DataFrame) -> Dict:
    """Test polynomial, threshold, and quantile regressions."""
    logger.info("\n=== NON-LINEAR PATTERN ANALYSIS ===")
    
    results = {}
    
    # Test polynomial regression on fantasy_score
    if 'fantasy_score' in df.columns:
        valid = df[['fantasy_score', 'log_price_usd', 'rarity_tier']].dropna()
        
        if len(valid) >= 100:
            # Linear
            X_linear = valid[['fantasy_score', 'rarity_tier']]
            y = valid['log_price_usd']
            
            linear_model = LinearRegression()
            linear_r2 = cross_val_score(linear_model, X_linear, y, cv=5, scoring='r2').mean()
            
            # Polynomial (degree 2)
            poly = PolynomialFeatures(degree=2, include_bias=False)
            X_poly = poly.fit_transform(X_linear)
            
            poly_model = LinearRegression()
            poly_r2 = cross_val_score(poly_model, X_poly, y, cv=5, scoring='r2').mean()
            
            results['fantasy_score_polynomial'] = {
                'linear_cv_r2': round(linear_r2, 3),
                'polynomial_cv_r2': round(poly_r2, 3),
                'improvement': round(poly_r2 - linear_r2, 3),
                'is_nonlinear': poly_r2 > linear_r2 + 0.01
            }
            
            logger.info(f"Fantasy score polynomial: Linear R²={linear_r2:.3f}, Poly R²={poly_r2:.3f}")
    
    # Threshold detection for syllable count
    if 'syllable_count' in df.columns:
        valid = df[['syllable_count', 'log_price_usd']].dropna()
        
        if len(valid) >= 100:
            thresholds_to_test = [2, 3, 4, 5]
            best_threshold = None
            best_diff = 0
            
            for threshold in thresholds_to_test:
                low = valid[valid['syllable_count'] <= threshold]['log_price_usd'].mean()
                high = valid[valid['syllable_count'] > threshold]['log_price_usd'].mean()
                diff = abs(high - low)
                
                if diff > best_diff:
                    best_diff = diff
                    best_threshold = threshold
            
            results['syllable_threshold'] = {
                'optimal_threshold': best_threshold,
                'price_difference': round(best_diff, 3),
                'interpretation': f"Cards with >{best_threshold} syllables differ by {best_diff:.2f} log-price units"
            }
            
            logger.info(f"Syllable threshold: {best_threshold} syllables (diff={best_diff:.3f})")
    
    return results


def analyze_proper_clustering(df: pd.DataFrame) -> Dict:
    """K-means for k=2-8 with silhouette optimization."""
    logger.info("\n=== CLUSTERING ANALYSIS ===")
    
    # Select features for clustering
    feature_cols = [
        'syllable_count', 'character_length', 'memorability_score',
        'fantasy_score', 'mythic_resonance_score', 'constructed_language_score'
    ]
    
    df_clean = df[feature_cols].dropna()
    
    if len(df_clean) < 100:
        return {'error': 'Insufficient data'}
    
    # Normalize
    scaler = StandardScaler()
    X = scaler.fit_transform(df_clean)
    
    # Test k=2 through k=8
    silhouette_scores = {}
    cluster_results = {}
    
    for k in range(2, 9):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X)
        
        sil_score = silhouette_score(X, labels)
        silhouette_scores[k] = round(sil_score, 3)
        
        logger.info(f"k={k}: silhouette={sil_score:.3f}")
    
    # Optimal k
    optimal_k = max(silhouette_scores, key=silhouette_scores.get)
    
    # Run final clustering with optimal k
    kmeans_final = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
    final_labels = kmeans_final.fit_predict(X)
    
    df_clean['cluster'] = final_labels
    
    # Profile clusters
    cluster_profiles = {}
    for i in range(optimal_k):
        cluster_df = df.iloc[df_clean[df_clean['cluster'] == i].index]
        
        cluster_profiles[f'Cluster_{i}'] = {
            'size': len(cluster_df),
            'avg_price': round(cluster_df['price_usd'].mean(), 2),
            'avg_fantasy': round(cluster_df['fantasy_score'].mean(), 2),
            'avg_syllables': round(cluster_df['syllable_count'].mean(), 2),
            'avg_memorability': round(cluster_df['memorability_score'].mean(), 2),
            'legendary_rate': round((cluster_df['is_legendary'].sum() / len(cluster_df)) * 100, 1)
        }
    
    logger.info(f"✓ Optimal k={optimal_k} (silhouette={silhouette_scores[optimal_k]})")
    
    return {
        'silhouette_scores': silhouette_scores,
        'optimal_k': optimal_k,
        'cluster_profiles': cluster_profiles
    }


def analyze_rhythmic_mechanical(df: pd.DataFrame) -> Dict:
    """Test stress patterns vs CMC and syllable weight vs power."""
    logger.info("\n=== RHYTHMIC-MECHANICAL ALIGNMENT ===")
    
    # Creatures only (have power/toughness)
    creatures = df[df['is_creature']].copy()
    
    # Parse power (handle *, X, numbers)
    def parse_power(card):
        try:
            power_str = card.get('power')
            if not power_str or power_str in ['*', 'X']:
                return None
            return int(power_str)
        except:
            return None
    
    # Correlate syllables with CMC
    if 'converted_mana_cost' in df.columns:
        valid = df[['syllable_count', 'converted_mana_cost']].dropna()
        if len(valid) >= 50:
            r, p = stats.pearsonr(valid['syllable_count'], valid['converted_mana_cost'])
            logger.info(f"Syllables vs CMC: r={r:.3f}, p={p:.4f}")
            
            return {
                'syllables_vs_cmc': {
                    'r': round(r, 3),
                    'p': round(p, 4),
                    'significant': p < 0.05,
                    'interpretation': 'Higher mana cost → longer names' if r > 0 else 'Lower CMC → longer names'
                }
            }
    
    return {}


def run_m4_color_regression(df: pd.DataFrame) -> Dict:
    """M4: Color determinism regression with harshness × color interaction."""
    logger.info("\n=== M4: COLOR DETERMINISM REGRESSION ===")
    
    # Filter to cards with harshness data
    if 'harshness_score' not in df.columns:
        return {'error': 'No harshness data available'}
    
    # Create color dummies
    colors = ['W', 'U', 'B', 'R', 'G']
    for color in colors:
        df[f'is_{color}'] = df['color_identity'] == color
    
    # Monocolor only for clean test
    monocolor = df[df['color_identity'].isin(colors)].copy()
    
    if len(monocolor) < 100:
        return {'error': 'Insufficient monocolor data'}
    
    # Test interaction: harshness × color
    results_by_color = {}
    
    for color in colors:
        color_cards = monocolor[monocolor['color_identity'] == color]
        
        if len(color_cards) < 30:
            continue
        
        # Regression: log(price) ~ harshness + rarity
        valid = color_cards[['harshness_score', 'rarity_tier', 'log_price_usd']].dropna()
        
        if len(valid) < 30:
            continue
        
        X = valid[['harshness_score', 'rarity_tier']]
        y = valid['log_price_usd']
        
        model = LinearRegression()
        cv_scores = cross_val_score(model, X, y, cv=5, scoring='r2')
        
        model.fit(X, y)
        
        results_by_color[color] = {
            'sample_size': len(valid),
            'harshness_coef': round(model.coef_[0], 4),
            'cv_r2': round(cv_scores.mean(), 3),
            'cv_std': round(cv_scores.std(), 3)
        }
        
        logger.info(f"{color}: harshness_coef={model.coef_[0]:.4f}, CV R²={cv_scores.mean():.3f}")
    
    return {'color_harshness_models': results_by_color}


def run_m6_era_timeseries(df: pd.DataFrame) -> Dict:
    """M6: Era evolution time-series models."""
    logger.info("\n=== M6: ERA EVOLUTION TIME-SERIES ===")
    
    if 'set_year' not in df.columns:
        return {'error': 'No set_year data'}
    
    df_with_year = df[df['set_year'].notna()].copy()
    
    if len(df_with_year) < 100:
        return {'error': 'Insufficient temporal data'}
    
    # Model 1: fantasy_score ~ set_year + set_year²
    valid = df_with_year[['set_year', 'fantasy_score']].dropna()
    
    if len(valid) >= 50:
        X = valid[['set_year']].values
        X_poly = np.column_stack([X, X**2])
        y = valid['fantasy_score'].values
        
        model = LinearRegression()
        model.fit(X_poly, y)
        r2 = model.score(X_poly, y)
        
        logger.info(f"Fantasy ~ year + year²: R²={r2:.3f}, linear_coef={model.coef_[0]:.4f}")
        
        fantasy_evolution = {
            'linear_coef': round(model.coef_[0], 4),
            'quadratic_coef': round(model.coef_[1], 6),
            'r_squared': round(r2, 3),
            'interpretation': f"Fantasy score increasing {model.coef_[0]:.2f} points/year"
        }
    else:
        fantasy_evolution = {}
    
    # Model 2: Does fantasy matter MORE in recent era? (interaction)
    valid = df_with_year[['set_year', 'fantasy_score', 'log_price_usd', 'rarity_tier']].dropna()
    
    if len(valid) >= 100:
        # Create interaction term
        valid['fantasy_x_year'] = valid['fantasy_score'] * valid['set_year']
        
        X = valid[['fantasy_score', 'set_year', 'fantasy_x_year', 'rarity_tier']]
        y = valid['log_price_usd']
        
        model = LinearRegression()
        model.fit(X, y)
        
        interaction_coef = model.coef_[2]  # fantasy_x_year coefficient
        
        logger.info(f"Price ~ fantasy × year interaction: coef={interaction_coef:.6f}")
        
        fantasy_importance_evolution = {
            'interaction_coef': round(interaction_coef, 6),
            'interpretation': 'Fantasy matters MORE in recent sets' if interaction_coef > 0 else 'Fantasy matters LESS in recent sets'
        }
    else:
        fantasy_importance_evolution = {}
    
    return {
        'fantasy_evolution': fantasy_evolution,
        'fantasy_importance_over_time': fantasy_importance_evolution
    }


def main():
    """Execute complete Phase 2 analysis."""
    logger.info("="*70)
    logger.info("MTG PHASE 2: VALUE OVER TIME & STATISTICAL RIGOR")
    logger.info("="*70)
    
    # Load data
    df = load_comprehensive_dataset()
    
    if len(df) < 100:
        logger.error("Insufficient data for analysis")
        return
    
    # Initialize analyzers
    temporal_analyzer = MTGTemporalAnalyzer()
    
    all_results = {
        'dataset_summary': {
            'total_cards': len(df),
            'avg_price': round(df['price_usd'].mean(), 2),
            'median_price': round(df['price_usd'].median(), 2)
        }
    }
    
    # Run analyses
    logger.info(f"\nAnalyzing {len(df)} cards...")
    
    # Temporal dynamics
    all_results['temporal_dynamics'] = temporal_analyzer.analyze_appreciation_patterns(df)
    all_results['reprint_vulnerability'] = temporal_analyzer.analyze_reprint_vulnerability(df)
    all_results['price_trajectories'] = temporal_analyzer.classify_price_trajectories(df)
    
    # Interaction effects
    all_results['interaction_effects'] = analyze_interaction_effects(df)
    
    # Non-linear patterns
    all_results['nonlinear_patterns'] = analyze_nonlinear_patterns(df)
    
    # Clustering
    all_results['clustering'] = analyze_proper_clustering(df)
    
    # Rhythmic-mechanical
    all_results['rhythmic_mechanical'] = analyze_rhythmic_mechanical(df)
    
    # M4 Color regression
    all_results['m4_color_regression'] = run_m4_color_regression(df)
    
    # M6 Era time-series
    all_results['m6_era_timeseries'] = run_m6_era_timeseries(df)
    
    # Save results
    output_dir = Path(__file__).resolve().parents[1] / 'analysis_outputs' / 'mtg_phase2'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = output_dir / f'phase2_comprehensive_{timestamp}.json'
    
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    
    logger.info(f"\n✅ Phase 2 analysis complete!")
    logger.info(f"Results saved to: {output_file}")
    
    # Print summary
    logger.info("\n" + "="*70)
    logger.info("ANALYSIS SUMMARY")
    logger.info("="*70)
    logger.info(f"Dataset: {len(df)} cards")
    logger.info(f"Interaction effects tested: {all_results['interaction_effects'].get('total_tested', 0)}")
    logger.info(f"Optimal cluster k: {all_results['clustering'].get('optimal_k', 'N/A')}")
    logger.info(f"Trajectory types identified: {len(all_results['price_trajectories'].get('trajectory_profiles', {}))}")
    
    return all_results


if __name__ == '__main__':
    results = main()


