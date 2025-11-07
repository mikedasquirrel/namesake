"""
Formula Validation Framework

Empirically compares conservative vs revolutionary phonetic formula approaches
across all research domains using cross-validation.

This script will determine which approach (or hybrid) performs best.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
from sklearn.model_selection import KFold, cross_val_score
from sklearn.linear_model import Ridge, Lasso, ElasticNet
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error, roc_auc_score
from sklearn.preprocessing import StandardScaler
import json
from datetime import datetime

# Import Flask app for context
from app import app
from core.models import db, Cryptocurrency, NameAnalysis, PriceHistory, Band, Hurricane, HurricaneAnalysis
from analyzers.phonetic_base import get_analyzer as get_phonetic_analyzer
from analyzers.phonetic_composites import get_composite_analyzer
from analyzers.formula_manager import get_formula_manager, Domain
from analyzers.interaction_detector import InteractionDetector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FormulaValidator:
    """
    Validates phonetic formulas across domains.
    
    Compares:
    - Conservative: Simple linear combination of standardized features
    - Revolutionary: Hierarchical 4-level model with interactions
    """
    
    def __init__(self):
        self.phonetic_analyzer = get_phonetic_analyzer()
        self.composite_analyzer = get_composite_analyzer()
        self.formula_manager = get_formula_manager()
        self.interaction_detector = InteractionDetector()
        
        self.results = {
            'validation_date': datetime.now().isoformat(),
            'domains': {},
            'summary': {}
        }
    
    def validate_all_domains(self) -> Dict:
        """
        Run validation on all available domains.
        
        Returns complete validation results.
        """
        logger.info("="*70)
        logger.info("PHONETIC FORMULA VALIDATION")
        logger.info("Comparing Conservative vs Revolutionary Approaches")
        logger.info("="*70 + "\n")
        
        # Validate each domain
        self.validate_crypto()
        self.validate_hurricanes()
        # self.validate_bands()  # Would need band data loading
        # self.validate_mtg()    # Would need MTG data loading
        # self.validate_nba()    # Would need NBA data loading
        
        # Generate summary
        self.generate_summary()
        
        # Save results
        self.save_results()
        
        return self.results
    
    def validate_crypto(self):
        """Validate on cryptocurrency data."""
        logger.info("\n" + "="*70)
        logger.info("VALIDATING: CRYPTOCURRENCY")
        logger.info("="*70)
        
        try:
            # Load data
            df = self._load_crypto_data()
            
            if len(df) < 50:
                logger.warning(f"Insufficient crypto data: n={len(df)}")
                return
            
            logger.info(f"Loaded {len(df)} cryptocurrencies with complete data\n")
            
            # Extract phonetic features
            df = self._add_phonetic_features(df, 'name')
            
            # Define feature sets
            conservative_features = [
                'syllable_count', 'character_length', 'memorability_score',
                'uniqueness_score', 'euphony_score', 'pronounceability_score'
            ]
            
            revolutionary_features = conservative_features + [
                'harshness_score', 'smoothness_score', 'power_authority_score',
                'plosive_score', 'fricative_score', 'liquid_score',
                'vowel_frontness', 'cluster_complexity'
            ]
            
            outcome = 'performance'
            
            # Validate conservative approach
            logger.info("Testing CONSERVATIVE approach...")
            conservative_results = self._validate_approach(
                df, conservative_features, outcome, approach='conservative'
            )
            
            # Validate revolutionary approach (with interactions)
            logger.info("\nTesting REVOLUTIONARY approach...")
            revolutionary_results = self._validate_approach(
                df, revolutionary_features, outcome, approach='revolutionary',
                detect_interactions=True
            )
            
            # Compare
            comparison = self._compare_approaches(conservative_results, revolutionary_results)
            
            # Store results
            self.results['domains']['crypto'] = {
                'sample_size': len(df),
                'conservative': conservative_results,
                'revolutionary': revolutionary_results,
                'comparison': comparison,
                'winner': comparison['winner']
            }
            
            # Log results
            logger.info("\n" + "-"*70)
            logger.info("CRYPTO RESULTS:")
            logger.info(f"  Conservative R²: {conservative_results['cv_r2_mean']:.4f} ± {conservative_results['cv_r2_std']:.4f}")
            logger.info(f"  Revolutionary R²: {revolutionary_results['cv_r2_mean']:.4f} ± {revolutionary_results['cv_r2_std']:.4f}")
            logger.info(f"  Winner: {comparison['winner'].upper()}")
            logger.info(f"  Improvement: {comparison['improvement']:.1f}%")
            logger.info("-"*70)
        
        except Exception as e:
            logger.error(f"Error validating crypto: {e}")
            import traceback
            traceback.print_exc()
    
    def validate_hurricanes(self):
        """Validate on hurricane casualty data."""
        logger.info("\n" + "="*70)
        logger.info("VALIDATING: HURRICANES")
        logger.info("="*70)
        
        try:
            # Load data
            df = self._load_hurricane_data()
            
            if len(df) < 30:
                logger.warning(f"Insufficient hurricane data: n={len(df)}")
                return
            
            logger.info(f"Loaded {len(df)} hurricanes with casualty data\n")
            
            # Extract phonetic features
            df = self._add_phonetic_features(df, 'name')
            
            # Conservative features
            conservative_features = [
                'harshness_score', 'memorability_score', 'syllable_count',
                'power_authority_score'
            ]
            
            # Revolutionary features (add meteorological context)
            revolutionary_features = conservative_features + [
                'plosive_score', 'fricative_score', 'sibilant_score',
                'smoothness_score', 'voicing_ratio'
            ]
            
            # Outcome: log casualties (or binary has_casualties)
            if 'log_casualties' in df.columns:
                outcome = 'log_casualties'
            else:
                outcome = 'casualties'
            
            # Validate conservative
            logger.info("Testing CONSERVATIVE approach...")
            conservative_results = self._validate_approach(
                df, conservative_features, outcome, approach='conservative'
            )
            
            # Validate revolutionary
            logger.info("\nTesting REVOLUTIONARY approach...")
            revolutionary_results = self._validate_approach(
                df, revolutionary_features, outcome, approach='revolutionary',
                detect_interactions=True
            )
            
            # Compare
            comparison = self._compare_approaches(conservative_results, revolutionary_results)
            
            # Store results
            self.results['domains']['hurricanes'] = {
                'sample_size': len(df),
                'conservative': conservative_results,
                'revolutionary': revolutionary_results,
                'comparison': comparison,
                'winner': comparison['winner']
            }
            
            # Log results
            logger.info("\n" + "-"*70)
            logger.info("HURRICANE RESULTS:")
            logger.info(f"  Conservative R²: {conservative_results['cv_r2_mean']:.4f} ± {conservative_results['cv_r2_std']:.4f}")
            logger.info(f"  Revolutionary R²: {revolutionary_results['cv_r2_mean']:.4f} ± {revolutionary_results['cv_r2_std']:.4f}")
            logger.info(f"  Winner: {comparison['winner'].upper()}")
            logger.info(f"  Improvement: {comparison['improvement']:.1f}%")
            logger.info("-"*70)
        
        except Exception as e:
            logger.error(f"Error validating hurricanes: {e}")
            import traceback
            traceback.print_exc()
    
    def _load_crypto_data(self) -> pd.DataFrame:
        """Load cryptocurrency data with outcomes."""
        # Get latest prices
        latest_prices_subq = db.session.query(
            PriceHistory.crypto_id,
            db.func.max(PriceHistory.date).label('max_date')
        ).group_by(PriceHistory.crypto_id).subquery()
        
        query = db.session.query(
            Cryptocurrency, NameAnalysis, PriceHistory
        ).join(NameAnalysis, Cryptocurrency.id == NameAnalysis.crypto_id)\
         .join(PriceHistory, Cryptocurrency.id == PriceHistory.crypto_id)\
         .join(latest_prices_subq, db.and_(
             PriceHistory.crypto_id == latest_prices_subq.c.crypto_id,
             PriceHistory.date == latest_prices_subq.c.max_date
         ))
        
        data = []
        for crypto, analysis, price in query.all():
            if price.price_1yr_change is not None:
                data.append({
                    'name': crypto.name,
                    'performance': price.price_1yr_change,
                    'uniqueness_score': analysis.uniqueness_score or 50,
                })
        
        return pd.DataFrame(data)
    
    def _load_hurricane_data(self) -> pd.DataFrame:
        """Load hurricane data with casualties."""
        query = db.session.query(Hurricane, HurricaneAnalysis)\
            .join(HurricaneAnalysis, Hurricane.id == HurricaneAnalysis.hurricane_id)
        
        data = []
        for hurricane, analysis in query.all():
            if hurricane.deaths is not None and hurricane.deaths >= 0:
                data.append({
                    'name': hurricane.name,
                    'casualties': hurricane.deaths,
                    'log_casualties': np.log1p(hurricane.deaths),
                    'max_wind': hurricane.max_wind_mph or 0,
                    'category': hurricane.saffir_simpson_category or 0,
                })
        
        return pd.DataFrame(data)
    
    def _add_phonetic_features(self, df: pd.DataFrame, name_col: str) -> pd.DataFrame:
        """Add all phonetic features to dataframe."""
        logger.info("Extracting phonetic features...")
        
        all_names = df[name_col].tolist()
        
        for idx, row in df.iterrows():
            name = row[name_col]
            
            # Get comprehensive analysis
            analysis = self.composite_analyzer.analyze(name, all_names)
            
            # Add all features
            for key, value in analysis.items():
                if isinstance(value, (int, float, bool)):
                    df.at[idx, key] = value
        
        return df
    
    def _validate_approach(self, df: pd.DataFrame, feature_cols: List[str],
                          outcome_col: str, approach: str = 'conservative',
                          detect_interactions: bool = False) -> Dict:
        """
        Validate a specific approach using cross-validation.
        
        Returns validation metrics.
        """
        # Prepare data
        available_features = [f for f in feature_cols if f in df.columns]
        
        if not available_features:
            logger.error(f"No features available from {feature_cols}")
            return {'error': 'No features available'}
        
        X = df[available_features].fillna(df[available_features].median())
        y = df[outcome_col].fillna(df[outcome_col].median())
        
        # Standardize
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Cross-validation setup
        cv = KFold(n_splits=5, shuffle=True, random_state=42)
        
        # Models to test
        models = {
            'ridge': Ridge(alpha=1.0),
            'lasso': Lasso(alpha=0.1, max_iter=10000),
            'elastic_net': ElasticNet(alpha=0.1, l1_ratio=0.5, max_iter=10000),
        }
        
        # Add random forest for revolutionary approach
        if approach == 'revolutionary':
            models['random_forest'] = RandomForestRegressor(
                n_estimators=100, max_depth=5, random_state=42
            )
        
        # Evaluate each model
        model_results = {}
        best_score = -np.inf
        best_model = None
        
        for model_name, model in models.items():
            try:
                scores = cross_val_score(model, X_scaled, y, cv=cv, scoring='r2')
                
                model_results[model_name] = {
                    'cv_r2_mean': float(scores.mean()),
                    'cv_r2_std': float(scores.std()),
                    'cv_r2_scores': scores.tolist()
                }
                
                if scores.mean() > best_score:
                    best_score = scores.mean()
                    best_model = model_name
            
            except Exception as e:
                logger.debug(f"Error with {model_name}: {e}")
                continue
        
        # Interaction detection (if revolutionary)
        interactions = {}
        if detect_interactions:
            try:
                logger.info("  Detecting interactions...")
                interactions = self.interaction_detector.detect_all_interactions(
                    df, outcome_col, available_features
                )
            except Exception as e:
                logger.debug(f"Interaction detection failed: {e}")
        
        return {
            'approach': approach,
            'features_used': available_features,
            'n_features': len(available_features),
            'models': model_results,
            'best_model': best_model,
            'cv_r2_mean': model_results[best_model]['cv_r2_mean'] if best_model else 0,
            'cv_r2_std': model_results[best_model]['cv_r2_std'] if best_model else 0,
            'interactions_found': interactions.get('summary', {}) if interactions else {}
        }
    
    def _compare_approaches(self, conservative: Dict, revolutionary: Dict) -> Dict:
        """Compare two approaches and determine winner."""
        cons_r2 = conservative.get('cv_r2_mean', 0)
        rev_r2 = revolutionary.get('cv_r2_mean', 0)
        
        improvement = ((rev_r2 - cons_r2) / abs(cons_r2)) * 100 if cons_r2 != 0 else 0
        
        # Determine winner
        if rev_r2 > cons_r2 + 0.05:  # Revolutionary wins by >5% R²
            winner = 'revolutionary'
        elif cons_r2 > rev_r2 + 0.02:  # Conservative wins by >2% R²
            winner = 'conservative'
        else:
            winner = 'tie'
        
        return {
            'winner': winner,
            'conservative_r2': cons_r2,
            'revolutionary_r2': rev_r2,
            'improvement': improvement,
            'absolute_difference': rev_r2 - cons_r2
        }
    
    def generate_summary(self):
        """Generate cross-domain summary statistics."""
        if not self.results['domains']:
            logger.warning("No domain results to summarize")
            return
        
        domains = self.results['domains']
        
        # Count wins
        conservative_wins = sum(1 for d in domains.values() if d.get('winner') == 'conservative')
        revolutionary_wins = sum(1 for d in domains.values() if d.get('winner') == 'revolutionary')
        ties = sum(1 for d in domains.values() if d.get('winner') == 'tie')
        
        # Average improvements
        conservative_r2s = [d['conservative']['cv_r2_mean'] for d in domains.values() if 'conservative' in d]
        revolutionary_r2s = [d['revolutionary']['cv_r2_mean'] for d in domains.values() if 'revolutionary' in d]
        
        self.results['summary'] = {
            'total_domains_tested': len(domains),
            'conservative_wins': conservative_wins,
            'revolutionary_wins': revolutionary_wins,
            'ties': ties,
            'avg_conservative_r2': np.mean(conservative_r2s) if conservative_r2s else 0,
            'avg_revolutionary_r2': np.mean(revolutionary_r2s) if revolutionary_r2s else 0,
            'overall_winner': 'revolutionary' if revolutionary_wins > conservative_wins else 'conservative',
            'recommendation': self._generate_recommendation(conservative_wins, revolutionary_wins, ties)
        }
        
        # Log summary
        logger.info("\n" + "="*70)
        logger.info("VALIDATION SUMMARY")
        logger.info("="*70)
        logger.info(f"Domains tested: {len(domains)}")
        logger.info(f"Conservative wins: {conservative_wins}")
        logger.info(f"Revolutionary wins: {revolutionary_wins}")
        logger.info(f"Ties: {ties}")
        logger.info(f"Avg Conservative R²: {self.results['summary']['avg_conservative_r2']:.4f}")
        logger.info(f"Avg Revolutionary R²: {self.results['summary']['avg_revolutionary_r2']:.4f}")
        logger.info(f"\nOverall Winner: {self.results['summary']['overall_winner'].upper()}")
        logger.info(f"Recommendation: {self.results['summary']['recommendation']}")
        logger.info("="*70)
    
    def _generate_recommendation(self, cons_wins: int, rev_wins: int, ties: int) -> str:
        """Generate deployment recommendation."""
        if rev_wins > cons_wins + 1:
            return "Deploy REVOLUTIONARY approach across all domains"
        elif cons_wins > rev_wins + 1:
            return "Deploy CONSERVATIVE approach (simpler, more stable)"
        else:
            return "Deploy HYBRID approach (conservative for some domains, revolutionary for others)"
    
    def save_results(self, filename: str = 'formula_validation_results.json'):
        """Save validation results to JSON."""
        filepath = os.path.join(
            os.path.dirname(__file__), '..', 'analysis_outputs', filename
        )
        
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        logger.info(f"\nResults saved to: {filepath}")


def main():
    """Run complete validation."""
    # Create Flask application context
    with app.app_context():
        validator = FormulaValidator()
        results = validator.validate_all_domains()
        
        return results


if __name__ == '__main__':
    main()

