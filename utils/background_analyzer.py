"""
Background Analyzer - Pre-Compute All Analysis for Instant Page Loads
Computes and stores all expensive analysis so pages load in <100ms
"""

import json
import time
import logging
from datetime import datetime
import numpy as np
from scipy.stats import pearsonr, spearmanr
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error

from core.models import db, Cryptocurrency, NameAnalysis, PriceHistory, PreComputedStats

logger = logging.getLogger(__name__)


class BackgroundAnalyzer:
    """Pre-compute and store all analysis results"""
    
    def compute_and_store_all(self):
        """
        Compute ALL expensive analysis and store in database
        Pages will just read from PreComputedStats table = INSTANT
        """
        logger.info("="*70)
        logger.info("STARTING BACKGROUND ANALYSIS")
        logger.info("Pre-computing all expensive statistics...")
        logger.info("="*70)
        
        results = {}
        
        # Compute each type
        results['advanced_stats'] = self.compute_advanced_stats()
        results['empirical_validation'] = self.compute_empirical_validation()
        results['patterns'] = self.compute_patterns()
        
        logger.info("\n" + "="*70)
        logger.info("✅ ALL ANALYSIS PRE-COMPUTED")
        logger.info("="*70)
        for stat_type, result in results.items():
            logger.info(f"{stat_type}: {result['status']}")
        
        return results
    
    def compute_advanced_stats(self):
        """Compute advanced crypto stats"""
        start_time = time.time()
        
        try:
            logger.info("\n[1/3] Computing advanced stats...")
            
            # Get data (same logic as endpoint)
            latest_prices = db.session.query(
                PriceHistory.crypto_id,
                db.func.max(PriceHistory.date).label('max_date')
            ).group_by(PriceHistory.crypto_id).subquery()
            
            query = db.session.query(
                Cryptocurrency, NameAnalysis, PriceHistory
            ).join(NameAnalysis, Cryptocurrency.id == NameAnalysis.crypto_id)\
             .join(PriceHistory, Cryptocurrency.id == PriceHistory.crypto_id)\
             .join(latest_prices, db.and_(
                 PriceHistory.crypto_id == latest_prices.c.crypto_id,
                 PriceHistory.date == latest_prices.c.max_date
             ))
            
            metrics = {
                'syllables': [],
                'length': [],
                'memorability': [],
                'uniqueness': [],
                'phonetic': [],
                'return_1yr': [],
                'rank': [],
                'market_cap': []
            }
            
            for crypto, analysis, price in query.all():
                # USE ONLY REAL 1-YEAR DATA
                if price.price_1yr_change is None:
                    continue
                
                metrics['syllables'].append(analysis.syllable_count or 0)
                metrics['length'].append(analysis.character_length or 0)
                metrics['memorability'].append(analysis.memorability_score or 0)
                metrics['uniqueness'].append(analysis.uniqueness_score or 0)
                metrics['phonetic'].append(analysis.phonetic_score or 0)
                metrics['return_1yr'].append(price.price_1yr_change)
                metrics['rank'].append(crypto.rank or 9999)
                metrics['market_cap'].append(crypto.market_cap or 0)
            
            # Calculate stats (same as endpoint logic)
            def calc_stats(data):
                if not data:
                    return {}
                arr = np.array(data)
                return {
                    'mean': round(float(np.mean(arr)), 2),
                    'median': round(float(np.median(arr)), 2),
                    'std': round(float(np.std(arr)), 2),
                    'q25': round(float(np.percentile(arr, 25)), 2),
                    'q75': round(float(np.percentile(arr, 75)), 2),
                    'min': round(float(np.min(arr)), 2),
                    'max': round(float(np.max(arr)), 2),
                    'count': len(data)
                }
            
            # Performance by rank tier
            rank_tiers = {
                'Top 100': [r for r, ret in zip(metrics['rank'], metrics['return_1yr']) if r <= 100],
                '101-500': [r for r, ret in zip(metrics['rank'], metrics['return_1yr']) if 100 < r <= 500],
                '501-1000': [r for r, ret in zip(metrics['rank'], metrics['return_1yr']) if 500 < r <= 1000],
                '1000+': [r for r, ret in zip(metrics['rank'], metrics['return_1yr']) if r > 1000]
            }
            
            tier_performance = {}
            for tier_name, ranks in rank_tiers.items():
                tier_returns = [metrics['return_1yr'][i] for i, r in enumerate(metrics['rank']) if r in ranks]
                if tier_returns:
                    tier_performance[tier_name] = {
                        'count': len(tier_returns),
                        'avg_return': round(float(np.mean(tier_returns)), 2),
                        'median_return': round(float(np.median(tier_returns)), 2),
                        'winners': len([r for r in tier_returns if r > 0]),
                        'losers': len([r for r in tier_returns if r < 0])
                    }
            
            # Correlations
            correlations = {}
            test_metrics = ['syllables', 'length', 'memorability', 'uniqueness', 'phonetic']
            for metric in test_metrics:
                if len(metrics[metric]) > 10 and len(metrics['return_1yr']) > 10:
                    try:
                        corr, p_val = pearsonr(metrics[metric], metrics['return_1yr'])
                        correlations[metric] = {
                            'correlation': round(float(corr), 3),
                            'p_value': round(float(p_val), 4),
                            'significant': bool(p_val < 0.05),
                            'sample_size': len(metrics[metric])
                        }
                    except:
                        correlations[metric] = {'error': 'calculation_failed'}
            
            # Length distribution
            length_distribution = {}
            for length in set(metrics['length']):
                if length > 0:
                    length_group = [metrics['return_1yr'][i] for i, l in enumerate(metrics['length']) if l == length]
                    if len(length_group) >= 5:
                        length_distribution[int(length)] = {
                            'count': len(length_group),
                            'avg_return': round(float(np.mean(length_group)), 2),
                            'median_return': round(float(np.median(length_group)), 2)
                        }
            
            result = {
                'sample_size': len(metrics['return_1yr']),
                'overall_stats': {
                    'syllables': calc_stats(metrics['syllables']),
                    'length': calc_stats(metrics['length']),
                    'memorability': calc_stats(metrics['memorability']),
                    'uniqueness': calc_stats(metrics['uniqueness']),
                    'return_1yr': calc_stats(metrics['return_1yr'])
                },
                'tier_performance': tier_performance,
                'correlations': correlations,
                'length_distribution': dict(sorted(length_distribution.items())[:15]),
                'statistical_power': {
                    'detectable_effect_size': round(2.8 / np.sqrt(len(metrics['return_1yr'])), 3) if metrics['return_1yr'] else 0,
                    'confidence': 'HIGH' if len(metrics['return_1yr']) > 1000 else 'MEDIUM'
                }
            }
            
            # Store in database
            duration = time.time() - start_time
            self._store_result('advanced_stats', result, len(metrics['return_1yr']), duration)
            
            logger.info(f"✅ Advanced stats computed (N={len(metrics['return_1yr'])}) in {duration:.1f}s")
            return {'status': 'success', 'sample_size': len(metrics['return_1yr']), 'duration': duration}
            
        except Exception as e:
            logger.error(f"Error computing advanced stats: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def compute_empirical_validation(self):
        """Compute empirical validation"""
        start_time = time.time()
        
        try:
            logger.info("\n[2/3] Computing empirical validation...")
            
            # Get data
            latest_prices = db.session.query(
                PriceHistory.crypto_id,
                db.func.max(PriceHistory.date).label('max_date')
            ).group_by(PriceHistory.crypto_id).subquery()
            
            query = db.session.query(
                Cryptocurrency, NameAnalysis, PriceHistory
            ).join(NameAnalysis, Cryptocurrency.id == NameAnalysis.crypto_id)\
             .join(PriceHistory, Cryptocurrency.id == PriceHistory.crypto_id)\
             .join(latest_prices, db.and_(
                 PriceHistory.crypto_id == latest_prices.c.crypto_id,
                 PriceHistory.date == latest_prices.c.max_date
             ))
            
            data = []
            for crypto, analysis, price in query.all():
                if price.price_1yr_change is None:
                    continue
                
                data.append({
                    'syllables': analysis.syllable_count or 0,
                    'length': analysis.character_length or 0,
                    'memorability': analysis.memorability_score or 0,
                    'uniqueness': analysis.uniqueness_score or 0,
                    'phonetic': analysis.phonetic_score or 0,
                    'pronounceability': analysis.pronounceability_score or 0,
                    'performance': price.price_1yr_change
                })
            
            if len(data) < 100:
                return {'status': 'insufficient_data', 'sample_size': len(data)}
            
            # Convert to arrays
            X_features = ['syllables', 'length', 'memorability', 'uniqueness', 'phonetic', 'pronounceability']
            X = np.array([[d[f] for f in X_features] for d in data])
            y = np.array([d['performance'] for d in data])
            
            # Correlation analysis
            correlations = {}
            for i, feature in enumerate(X_features):
                feature_vals = X[:, i]
                r_pearson, p_pearson = pearsonr(feature_vals, y)
                r_spearman, p_spearman = spearmanr(feature_vals, y)
                
                correlations[feature] = {
                    'pearson_r': round(float(r_pearson), 4),
                    'pearson_p': round(float(p_pearson), 6),
                    'spearman_r': round(float(r_spearman), 4),
                    'spearman_p': round(float(p_spearman), 6),
                    'significant': bool(p_pearson < 0.01),
                    'strength': 'strong' if abs(r_pearson) > 0.3 else ('moderate' if abs(r_pearson) > 0.1 else 'weak'),
                    'interpretation': f"{'Positive' if r_pearson > 0 else 'Negative'} {'significant' if p_pearson < 0.01 else 'non-significant'} correlation"
                }
            
            # Regression
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            model = LinearRegression()
            model.fit(X_train, y_train)
            
            y_train_pred = model.predict(X_train)
            r2_train = r2_score(y_train, y_train_pred)
            
            y_test_pred = model.predict(X_test)
            r2_test = r2_score(y_test, y_test_pred)
            rmse_test = np.sqrt(mean_squared_error(y_test, y_test_pred))
            
            regression = {
                'r_squared_train': round(float(r2_train), 4),
                'r_squared_test': round(float(r2_test), 4),
                'rmse_test': round(float(rmse_test), 2),
                'feature_coefficients': {
                    feature: round(float(coef), 4) 
                    for feature, coef in zip(X_features, model.coef_)
                },
                'intercept': round(float(model.intercept_), 2),
                'interpretation': f"Name characteristics explain {round(r2_test * 100, 1)}% of performance variance (out-of-sample)",
                'sample_sizes': {
                    'train': int(len(X_train)),
                    'test': int(len(X_test))
                }
            }
            
            # Pattern validation (simplified)
            patterns_tested = 0
            patterns_significant = 0
            
            for syllable_count in range(1, 6):
                mask_train = X_train[:, 0] == syllable_count
                mask_test = X_test[:, 0] == syllable_count
                
                if mask_train.sum() >= 20 and mask_test.sum() >= 10:
                    patterns_tested += 1
                    train_perf = y_train[mask_train].mean()
                    test_perf = y_test[mask_test].mean()
                    
                    if (train_perf > y_train.mean() and test_perf > y_test.mean()) or \
                       (train_perf < y_train.mean() and test_perf < y_test.mean()):
                        patterns_significant += 1
            
            pattern_validation = {
                'total_patterns_tested': int(patterns_tested),
                'patterns_validated': int(patterns_significant),
                'validation_rate': round(float(patterns_significant / patterns_tested if patterns_tested > 0 else 0), 3),
                'interpretation': f"{patterns_significant}/{patterns_tested} patterns validated out-of-sample"
            }
            
            # Predictive power
            y_test_binary = (y_test > 0).astype(int)
            y_test_pred_binary = (y_test_pred > 0).astype(int)
            
            accuracy = (y_test_binary == y_test_pred_binary).mean()
            baseline = max(y_test_binary.mean(), 1 - y_test_binary.mean())
            improvement = (accuracy - baseline) / baseline if baseline > 0 else 0
            
            predictive_power = {
                'out_of_sample_accuracy': round(float(accuracy), 3),
                'baseline_accuracy': round(float(baseline), 3),
                'improvement_over_baseline': round(float(improvement), 3),
                'winners_correctly_predicted': int((y_test_binary * y_test_pred_binary).sum()),
                'total_winners': int(y_test_binary.sum()),
                'interpretation': f"{round(improvement * 100, 1)}% better than random guessing"
            }
            
            # Conclusion
            evidence_count = 0
            if correlations['memorability']['significant']: evidence_count += 1
            if correlations['uniqueness']['significant']: evidence_count += 1
            if r2_test > 0.05: evidence_count += 1
            if pattern_validation['validation_rate'] > 0.5: evidence_count += 1
            if accuracy > baseline * 1.05: evidence_count += 1
            
            validation_strength = 'STRONG' if evidence_count >= 4 else ('MODERATE' if evidence_count >= 3 else 'WEAK')
            
            result = {
                'hypothesis': 'Name characteristics predict cryptocurrency performance',
                'sample_size': len(data),
                'validation_strength': validation_strength,
                'evidence_count': f"{evidence_count}/5 criteria met",
                'correlations': correlations,
                'regression_model': regression,
                'pattern_validation': pattern_validation,
                'predictive_power': predictive_power,
                'conclusion': f"{validation_strength} statistical evidence supports nominative determinism in cryptocurrency markets",
                'statistical_rigor': {
                    'out_of_sample_testing': True,
                    'bonferroni_corrected': False,
                    'confidence_level': 0.99,
                    'significance_threshold': 0.01
                },
                'timestamp': datetime.now().isoformat()
            }
            
            # Store in database
            duration = time.time() - start_time
            self._store_result('empirical_validation', result, len(data), duration)
            
            logger.info(f"✅ Empirical validation computed (N={len(data)}) in {duration:.1f}s")
            return {'status': 'success', 'sample_size': len(data), 'duration': duration}
            
        except Exception as e:
            logger.error(f"Error computing empirical validation: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {'status': 'error', 'error': str(e)}
    
    def compute_patterns(self):
        """Compute pattern discovery"""
        start_time = time.time()
        
        try:
            logger.info("\n[3/3] Computing pattern discovery...")
            
            # Import here to avoid circular dependency
            from analyzers.pattern_discovery import PatternDiscovery
            pattern_discovery = PatternDiscovery()
            
            patterns_result = pattern_discovery.discover_all_patterns()
            
            # Store in database
            duration = time.time() - start_time
            self._store_result('patterns', patterns_result, patterns_result.get('total_coins', 0), duration)
            
            logger.info(f"✅ Patterns computed ({len(patterns_result.get('patterns', []))} patterns) in {duration:.1f}s")
            return {'status': 'success', 'patterns': len(patterns_result.get('patterns', [])), 'duration': duration}
            
        except Exception as e:
            logger.error(f"Error computing patterns: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _store_result(self, stat_type, result, sample_size, duration):
        """Store result in PreComputedStats table"""
        try:
            # Mark old results as not current
            PreComputedStats.query.filter_by(stat_type=stat_type, is_current=True).update({'is_current': False})
            
            # Create new result
            precomputed = PreComputedStats(
                stat_type=stat_type,
                data_json=json.dumps(result),
                sample_size=sample_size,
                computed_at=datetime.utcnow(),
                computation_duration=duration,
                is_current=True
            )
            
            db.session.add(precomputed)
            db.session.commit()
            
            logger.info(f"  Stored {stat_type} in database")
            
        except Exception as e:
            logger.error(f"Error storing {stat_type}: {e}")
            db.session.rollback()
    
    def get_precomputed(self, stat_type):
        """Get pre-computed result (instant!)"""
        try:
            result = PreComputedStats.query.filter_by(
                stat_type=stat_type,
                is_current=True
            ).first()
            
            if result:
                return json.loads(result.data_json)
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving {stat_type}: {e}")
            return None

