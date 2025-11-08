"""MLB Statistical Analyzer

Comprehensive statistical modeling for MLB player name analysis.
Implements position prediction, pitcher analysis, power analysis, and temporal evolution.

Analyses:
1. Position prediction (name → P/C/IF/OF)
2. Pitcher analysis (SP vs RP vs CL patterns)
3. Power analysis (harshness ↔ home runs)
4. Temporal evolution (1950s → 2024)
5. Internationalization (pre/post-1990)
6. Closer effect (memorability for 9th inning)
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime

from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import accuracy_score, classification_report, r2_score
from scipy import stats

from core.models import db, MLBPlayer, MLBPlayerAnalysis

logger = logging.getLogger(__name__)


class MLBStatisticalAnalyzer:
    """Comprehensive statistical analysis for MLB player names."""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.position_model = None
        self.power_model = None
    
    def get_comprehensive_dataset(self) -> pd.DataFrame:
        """Load all players with complete data.
        
        Returns:
            DataFrame with player and analysis data
        """
        query = db.session.query(MLBPlayer, MLBPlayerAnalysis).join(
            MLBPlayerAnalysis,
            MLBPlayer.id == MLBPlayerAnalysis.player_id
        )
        
        rows = []
        for player, analysis in query.all():
            try:
                row = {
                    'id': player.id,
                    'name': player.name,
                    'position': player.position,
                    'position_group': player.position_group,
                    'pitcher_role': player.pitcher_role,
                    'debut_year': player.debut_year,
                    'era_group': player.era_group,
                    'home_runs': player.home_runs or 0,
                    'batting_average': player.batting_average or 0,
                    'era': player.era or 0,
                    'strikeouts': player.strikeouts or 0,
                    'saves': player.saves or 0,
                    'birth_country': player.birth_country,
                    'syllable_count': analysis.syllable_count or 0,
                    'word_count': analysis.word_count or 0,
                    'harshness_score': analysis.harshness_score or 50,
                    'power_connotation_score': analysis.power_connotation_score or 50,
                    'memorability_score': analysis.memorability_score or 50,
                    'phonetic_complexity': analysis.phonetic_complexity or 50,
                    'name_origin': analysis.name_origin,
                    'position_cluster': analysis.position_cluster,
                }
                rows.append(row)
            except Exception as e:
                logger.warning(f"Error loading player {player.name}: {e}")
                continue
        
        df = pd.DataFrame(rows)
        logger.info(f"Loaded {len(df)} MLB players for analysis")
        return df
    
    def run_full_analysis(self) -> Dict:
        """Execute all 6 analysis modules.
        
        Returns:
            Dict with comprehensive results
        """
        logger.info("=== MLB STATISTICAL ANALYSIS ===")
        
        df = self.get_comprehensive_dataset()
        
        if len(df) < 20:
            logger.error("Insufficient data for analysis (need 20+)")
            return {'error': 'Insufficient data', 'sample_size': len(df)}
        
        results = {}
        
        # Analysis 1: Position Prediction
        logger.info("\n1. Position prediction...")
        results['position_prediction'] = self.predict_position(df)
        
        # Analysis 2: Pitcher Analysis
        logger.info("\n2. Pitcher analysis...")
        results['pitcher'] = self.analyze_pitchers(df)
        
        # Analysis 3: Power Analysis
        logger.info("\n3. Power hitter analysis...")
        results['power'] = self.analyze_power_hitters(df)
        
        # Analysis 4: Temporal Evolution
        logger.info("\n4. Temporal evolution...")
        results['temporal'] = self.analyze_temporal_evolution(df)
        
        # Analysis 5: Internationalization
        logger.info("\n5. Internationalization...")
        results['internationalization'] = self.analyze_internationalization(df)
        
        # Analysis 6: Closer Effect
        logger.info("\n6. Closer effect...")
        results['closer_effect'] = self.analyze_closer_effect(df)
        
        results['sample_size'] = len(df)
        results['timestamp'] = datetime.now().isoformat()
        
        logger.info("\n=== ANALYSIS COMPLETE ===")
        return results
    
    def predict_position(self, df: pd.DataFrame) -> Dict:
        """Build model to predict position group from name features.
        
        Args:
            df: Complete dataset
        
        Returns:
            Dict with prediction results
        """
        df_valid = df[df['position_group'].notna()].copy()
        
        if len(df_valid) < 20:
            return {'error': 'Insufficient data'}
        
        feature_cols = ['syllable_count', 'harshness_score', 'memorability_score', 
                       'phonetic_complexity', 'power_connotation_score']
        
        X = df_valid[feature_cols].fillna(50)
        y = df_valid['position_group']
        
        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train model
        model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Feature importance
        importances = dict(zip(feature_cols, model.feature_importances_))
        
        self.position_model = model
        
        return {
            'accuracy': float(accuracy),
            'n_train': len(X_train),
            'n_test': len(X_test),
            'feature_importance': {k: float(v) for k, v in sorted(importances.items(), key=lambda x: x[1], reverse=True)}
        }
    
    def analyze_pitchers(self, df: pd.DataFrame) -> Dict:
        """Analyze pitcher naming patterns (SP vs RP vs CL).
        
        Args:
            df: Complete dataset
        
        Returns:
            Dict with pitcher analysis
        """
        pitchers = df[df['position_group'] == 'Pitcher'].copy()
        non_pitchers = df[df['position_group'] != 'Pitcher'].copy()
        
        if len(pitchers) < 5 or len(non_pitchers) < 5:
            return {'error': 'Insufficient pitcher data'}
        
        # H1: Pitchers have longer names
        t_stat, p_value = stats.ttest_ind(pitchers['syllable_count'], non_pitchers['syllable_count'])
        cohens_d = (pitchers['syllable_count'].mean() - non_pitchers['syllable_count'].mean()) / \
                   np.sqrt((pitchers['syllable_count'].std()**2 + non_pitchers['syllable_count'].std()**2) / 2)
        
        results = {
            'pitcher_mean_syllables': float(pitchers['syllable_count'].mean()),
            'non_pitcher_mean_syllables': float(non_pitchers['syllable_count'].mean()),
            'difference': float(pitchers['syllable_count'].mean() - non_pitchers['syllable_count'].mean()),
            'p_value': float(p_value),
            'cohens_d': float(cohens_d),
            'h1_supported': p_value < 0.05 and cohens_d > 0.3
        }
        
        # By pitcher role (if data available)
        if pitchers['pitcher_role'].notna().sum() > 10:
            by_role = {}
            for role in pitchers['pitcher_role'].unique():
                if pd.notna(role):
                    role_df = pitchers[pitchers['pitcher_role'] == role]
                    if len(role_df) >= 3:
                        by_role[role] = {
                            'count': len(role_df),
                            'mean_syllables': float(role_df['syllable_count'].mean()),
                            'mean_memorability': float(role_df['memorability_score'].mean())
                        }
            results['by_role'] = by_role
        
        return results
    
    def analyze_power_hitters(self, df: pd.DataFrame) -> Dict:
        """Analyze harshness correlation with home run totals.
        
        Args:
            df: Complete dataset
        
        Returns:
            Dict with power analysis
        """
        # Filter to position players with HR data
        hitters = df[(df['position_group'] != 'Pitcher') & (df['home_runs'] > 0)].copy()
        
        if len(hitters) < 10:
            return {'error': 'Insufficient hitter data'}
        
        # H2: Harshness correlates with power
        r, p_value = stats.pearsonr(hitters['harshness_score'], hitters['home_runs'])
        
        # Categorize by power level
        hr_median = hitters['home_runs'].median()
        power_hitters = hitters[hitters['home_runs'] > hr_median]
        contact_hitters = hitters[hitters['home_runs'] <= hr_median]
        
        # Compare harshness
        if len(power_hitters) >= 5 and len(contact_hitters) >= 5:
            t_stat, p_power = stats.ttest_ind(power_hitters['harshness_score'], 
                                             contact_hitters['harshness_score'])
            cohens_d = (power_hitters['harshness_score'].mean() - contact_hitters['harshness_score'].mean()) / \
                      np.sqrt((power_hitters['harshness_score'].std()**2 + contact_hitters['harshness_score'].std()**2) / 2)
        else:
            p_power = 1.0
            cohens_d = 0.0
        
        return {
            'correlation': {'r': float(r), 'p_value': float(p_value)},
            'power_hitters_harshness': float(power_hitters['harshness_score'].mean()) if len(power_hitters) > 0 else 0,
            'contact_hitters_harshness': float(contact_hitters['harshness_score'].mean()) if len(contact_hitters) > 0 else 0,
            'difference': float(power_hitters['harshness_score'].mean() - contact_hitters['harshness_score'].mean()) if len(power_hitters) > 0 and len(contact_hitters) > 0 else 0,
            'p_value': float(p_power),
            'cohens_d': float(cohens_d),
            'h2_supported': p_value < 0.05 and r > 0.15
        }
    
    def analyze_temporal_evolution(self, df: pd.DataFrame) -> Dict:
        """Analyze naming convention changes over time.
        
        Args:
            df: Complete dataset
        
        Returns:
            Dict with temporal analysis
        """
        df_valid = df[df['debut_year'].notna()].copy()
        
        if len(df_valid) < 20:
            return {'error': 'Insufficient temporal data'}
        
        # By era
        by_era = {}
        for era in ['classic', 'modern', 'contemporary']:
            era_df = df_valid[df_valid['era_group'] == era]
            if len(era_df) > 0:
                by_era[era] = {
                    'count': len(era_df),
                    'mean_syllables': float(era_df['syllable_count'].mean()),
                    'mean_harshness': float(era_df['harshness_score'].mean())
                }
        
        # Correlation with year
        r, p_value = stats.pearsonr(df_valid['debut_year'], df_valid['syllable_count'])
        
        return {
            'by_era': by_era,
            'year_syllable_correlation': {
                'r': float(r),
                'p_value': float(p_value),
                'trend': 'increasing' if r > 0 else 'decreasing'
            }
        }
    
    def analyze_internationalization(self, df: pd.DataFrame) -> Dict:
        """Analyze impact of international players on name diversity.
        
        Args:
            df: Complete dataset
        
        Returns:
            Dict with internationalization analysis
        """
        df_valid = df[df['debut_year'].notna()].copy()
        
        if len(df_valid) < 20:
            return {'error': 'Insufficient data'}
        
        # Pre/post-1990 comparison (H4)
        pre_1990 = df_valid[df_valid['debut_year'] < 1990]
        post_1990 = df_valid[df_valid['debut_year'] >= 1990]
        
        if len(pre_1990) >= 5 and len(post_1990) >= 5:
            t_stat, p_value = stats.ttest_ind(post_1990['syllable_count'], pre_1990['syllable_count'])
            cohens_d = (post_1990['syllable_count'].mean() - pre_1990['syllable_count'].mean()) / \
                      np.sqrt((post_1990['syllable_count'].std()**2 + pre_1990['syllable_count'].std()**2) / 2)
            
            results = {
                'pre_1990_syllables': float(pre_1990['syllable_count'].mean()),
                'post_1990_syllables': float(post_1990['syllable_count'].mean()),
                'difference': float(post_1990['syllable_count'].mean() - pre_1990['syllable_count'].mean()),
                'p_value': float(p_value),
                'cohens_d': float(cohens_d),
                'h4_supported': p_value < 0.05 and cohens_d > 0.5
            }
        else:
            results = {'error': 'Insufficient temporal data for comparison'}
        
        # By origin
        by_origin = {}
        for origin in df['name_origin'].unique():
            if pd.notna(origin):
                origin_df = df[df['name_origin'] == origin]
                if len(origin_df) >= 3:
                    by_origin[origin] = {
                        'count': len(origin_df),
                        'mean_syllables': float(origin_df['syllable_count'].mean())
                    }
        
        results['by_origin'] = by_origin
        
        return results
    
    def analyze_closer_effect(self, df: pd.DataFrame) -> Dict:
        """Test if closers have shorter, more memorable names.
        
        Args:
            df: Complete dataset
        
        Returns:
            Dict with closer analysis
        """
        closers = df[df['pitcher_role'] == 'CL']
        starters = df[df['pitcher_role'] == 'SP']
        
        if len(closers) < 3 or len(starters) < 3:
            return {'error': 'Insufficient pitcher role data'}
        
        # H5: Closers shorter than starters
        t_stat, p_value = stats.ttest_ind(closers['syllable_count'], starters['syllable_count'])
        
        return {
            'closer_mean_syllables': float(closers['syllable_count'].mean()),
            'starter_mean_syllables': float(starters['syllable_count'].mean()),
            'difference': float(closers['syllable_count'].mean() - starters['syllable_count'].mean()),
            'closer_memorability': float(closers['memorability_score'].mean()),
            'starter_memorability': float(starters['memorability_score'].mean()),
            'p_value': float(p_value),
            'h5_supported': p_value < 0.05 and closers['syllable_count'].mean() < starters['syllable_count'].mean()
        }
    
    def test_all_hypotheses(self, df: pd.DataFrame) -> Dict:
        """Test all 5 primary hypotheses.
        
        Args:
            df: Complete dataset
        
        Returns:
            Dict with hypothesis results
        """
        full_results = self.run_full_analysis()
        
        hypotheses = {
            'H1': {
                'hypothesis': 'Pitchers have longer names than position players',
                'supported': full_results.get('pitcher', {}).get('h1_supported', False),
                'effect_size': full_results.get('pitcher', {}).get('cohens_d', 0)
            },
            'H2': {
                'hypothesis': 'Power hitters have harsher names',
                'supported': full_results.get('power', {}).get('h2_supported', False),
                'correlation': full_results.get('power', {}).get('correlation', {}).get('r', 0)
            },
            'H3': {
                'hypothesis': 'Position prediction accuracy 60-65%',
                'supported': full_results.get('position_prediction', {}).get('accuracy', 0) >= 0.60,
                'accuracy': full_results.get('position_prediction', {}).get('accuracy', 0)
            },
            'H4': {
                'hypothesis': 'Post-1990 names longer due to internationalization',
                'supported': full_results.get('internationalization', {}).get('h4_supported', False),
                'difference': full_results.get('internationalization', {}).get('difference', 0)
            },
            'H5': {
                'hypothesis': 'Closers have shorter names than starters',
                'supported': full_results.get('closer_effect', {}).get('h5_supported', False),
                'difference': full_results.get('closer_effect', {}).get('difference', 0)
            }
        }
        
        return hypotheses
    
    def generate_summary_report(self) -> Dict:
        """Generate comprehensive summary report.
        
        Returns:
            Dict with complete analysis
        """
        df = self.get_comprehensive_dataset()
        
        if len(df) < 10:
            return {'error': 'Insufficient data', 'sample_size': len(df)}
        
        report = {
            'sample_size': len(df),
            'full_analysis': self.run_full_analysis(),
            'hypotheses': self.test_all_hypotheses(df),
            'generated_at': datetime.now().isoformat()
        }
        
        return report


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    analyzer = MLBStatisticalAnalyzer()
    report = analyzer.generate_summary_report()
    print(f"Analysis complete: {report.get('sample_size', 0)} players")

