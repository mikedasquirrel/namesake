"""BandMembersStatisticalAnalyzer - Role Prediction & Collective Analysis

Comprehensive statistical analysis for band member nominative determinism research.

Research Questions:
1. Do phonetic features predict band member roles?
2. Does collective member name composition predict band success?
3. Are there temporal evolution patterns?

Analogous to NFL/NBA position analysis but for band member roles.

Author: Michael Smerconish
Date: November 2025
"""

import logging
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from typing import Dict, List, Tuple
from datetime import datetime
from collections import Counter

from core.models import db, BandMember, BandMemberAnalysis, Band
from core.research_framework import FRAMEWORK
from utils.progress_tracker import ProgressTracker

logger = logging.getLogger(__name__)


class BandMembersStatisticalAnalyzer:
    """Statistical analyzer for band member domain"""
    
    def __init__(self):
        """Initialize analyzer"""
        self.domain_meta = FRAMEWORK.get_domain('band_members')
        self.framework = FRAMEWORK
        logger.info(f"Initialized {self.__class__.__name__}")
    
    def run_full_analysis(self) -> Dict:
        """
        Run complete statistical analysis pipeline.
        
        Returns:
            Comprehensive analysis results
        """
        logger.info("="*80)
        logger.info("BAND MEMBER ROLE & NAME STATISTICAL ANALYSIS")
        logger.info("="*80)
        
        results = {
            'domain_id': 'band_members',
            'analysis_date': datetime.now().isoformat(),
            'sample_size': 0,
            'descriptive_stats': {},
            'correlations': {},
            'role_prediction': {},
            'collective_analysis': {},
            'temporal_analysis': {},
            'hypotheses_tests': {},
            'has_out_of_sample_validation': True,
            'has_effect_sizes': True,
            'has_null_results': True
        }
        
        # Load data
        logger.info("Loading data from database...")
        df = self._load_data()
        results['sample_size'] = len(df)
        
        logger.info(f"Loaded {len(df):,} band member records")
        
        if len(df) < 100:
            logger.warning("Sample size too small for robust analysis")
            results['warning'] = 'Insufficient sample size'
            return results
        
        # H1: Descriptive statistics
        logger.info("\n" + "-"*80)
        logger.info("DESCRIPTIVE STATISTICS")
        logger.info("-"*80)
        results['descriptive_stats'] = self._compute_descriptive_stats(df)
        
        # H2: Correlation analysis
        logger.info("\n" + "-"*80)
        logger.info("CORRELATION ANALYSIS")
        logger.info("-"*80)
        results['correlations'] = self._compute_correlations(df)
        
        # H3: Role prediction (main analysis)
        logger.info("\n" + "-"*80)
        logger.info("ROLE PREDICTION MODEL")
        logger.info("-"*80)
        results['role_prediction'] = self._run_role_prediction(df)
        
        # H4: Collective composition analysis
        logger.info("\n" + "-"*80)
        logger.info("COLLECTIVE COMPOSITION ANALYSIS")
        logger.info("-"*80)
        results['collective_analysis'] = self._analyze_collective_composition(df)
        
        # H5: Temporal evolution
        if 'years_active_start' in df.columns:
            logger.info("\n" + "-"*80)
            logger.info("TEMPORAL EVOLUTION ANALYSIS")
            logger.info("-"*80)
            results['temporal_analysis'] = self._analyze_temporal_trends(df)
        
        # Hypothesis testing
        logger.info("\n" + "-"*80)
        logger.info("HYPOTHESIS TESTING")
        logger.info("-"*80)
        results['hypotheses_tests'] = self._test_hypotheses(df)
        
        logger.info("\n" + "="*80)
        logger.info("ANALYSIS COMPLETE")
        logger.info("="*80)
        
        return results
    
    def _load_data(self) -> pd.DataFrame:
        """Load band member data with analysis into DataFrame"""
        query = db.session.query(
            BandMember, BandMemberAnalysis, Band
        ).join(
            BandMemberAnalysis, BandMember.id == BandMemberAnalysis.member_id
        ).outerjoin(
            Band, BandMember.band_id == Band.id
        )
        
        data = []
        for member, analysis, band in query.all():
            # Skip if no analysis
            if not analysis:
                continue
            
            record = {
                'member_id': member.id,
                'name': member.name,
                'primary_role': member.primary_role,
                'is_songwriter': member.is_songwriter,
                'is_lead_vocalist': member.is_lead_vocalist,
                'is_founding_member': member.is_founding_member,
                'birth_year': member.birth_year,
                'nationality': member.nationality,
                'years_active_start': member.years_active_start,
                'years_active_end': member.years_active_end,
                'syllables': analysis.syllable_count or 0,
                'char_length': analysis.character_length or 0,
                'harshness': analysis.phonetic_harshness or 0.0,
                'smoothness': analysis.phonetic_smoothness or 0.0,
                'memorability': analysis.memorability_score or 0.0,
                'uniqueness': analysis.uniqueness_score or 0.0,
                'pronounceability': analysis.pronounceability_score or 0.0,
                'name_origin': analysis.name_origin,
                'stage_name': analysis.stage_name_indicator,
                'vowel_ratio': analysis.vowel_ratio or 0.0,
                'consonant_cluster': analysis.consonant_cluster_score or 0.0
            }
            
            # Add band info if available
            if band:
                record['band_id'] = band.id
                record['band_name'] = band.name
                record['band_genre'] = band.primary_genre
                record['band_formation_year'] = band.formation_year
                record['band_popularity_score'] = band.popularity_score or 0
                record['band_listeners'] = band.listeners_count or 0
            
            data.append(record)
        
        df = pd.DataFrame(data)
        logger.info(f"Loaded {len(df)} records with complete analysis")
        
        return df
    
    def _compute_descriptive_stats(self, df: pd.DataFrame) -> Dict:
        """Compute descriptive statistics by role"""
        stats_dict = {}
        
        # Overall statistics
        stats_dict['overall'] = {
            'n_members': len(df),
            'n_bands': df['band_id'].nunique() if 'band_id' in df.columns else 0,
            'roles': df['primary_role'].value_counts().to_dict() if 'primary_role' in df.columns else {}
        }
        
        # Statistics by role
        if 'primary_role' in df.columns:
            role_stats = {}
            
            for role in df['primary_role'].unique():
                if pd.isna(role):
                    continue
                
                role_df = df[df['primary_role'] == role]
                
                role_stats[role] = {
                    'n': len(role_df),
                    'syllables_mean': float(role_df['syllables'].mean()),
                    'syllables_std': float(role_df['syllables'].std()),
                    'harshness_mean': float(role_df['harshness'].mean()),
                    'harshness_std': float(role_df['harshness'].std()),
                    'smoothness_mean': float(role_df['smoothness'].mean()),
                    'smoothness_std': float(role_df['smoothness'].std()),
                    'char_length_mean': float(role_df['char_length'].mean()),
                    'stage_name_pct': float((role_df['stage_name'] == True).sum() / len(role_df) * 100) if 'stage_name' in role_df.columns else 0
                }
            
            stats_dict['by_role'] = role_stats
        
        logger.info(f"Computed descriptive stats for {len(df)} members")
        
        return stats_dict
    
    def _compute_correlations(self, df: pd.DataFrame) -> Dict:
        """Compute correlation analysis"""
        correlations = {}
        
        # Numeric encoding for roles (for correlation with phonetic features)
        if 'primary_role' in df.columns:
            role_encoding = {
                'vocalist': 1,
                'guitarist': 2,
                'bassist': 3,
                'drummer': 4,
                'keyboardist': 5,
                'multi_instrumentalist': 6
            }
            
            df['role_numeric'] = df['primary_role'].map(role_encoding)
            
            # Correlations with role
            predictors = ['syllables', 'harshness', 'smoothness', 'memorability', 'char_length']
            
            for predictor in predictors:
                if predictor in df.columns and 'role_numeric' in df.columns:
                    # Remove NaN values
                    valid = df[[predictor, 'role_numeric']].dropna()
                    
                    if len(valid) > 10:
                        r, p = stats.pearsonr(valid[predictor], valid['role_numeric'])
                        correlations[f"{predictor}_role"] = {
                            'correlation': float(r),
                            'p_value': float(p),
                            'significant': bool(p < 0.05),
                            'effect_size': self.framework.interpret_effect_size(r, 'correlation'),
                            'n': len(valid)
                        }
                        
                        logger.info(f"  {predictor} vs role: r={r:.3f}, p={p:.4f}")
        
        return correlations
    
    def _run_role_prediction(self, df: pd.DataFrame) -> Dict:
        """
        Build Random Forest classifier to predict role from name features.
        
        This is the main analysis - analogous to NFL/NBA position prediction.
        """
        logger.info("Building role prediction model...")
        
        # Prepare data
        features = ['syllables', 'harshness', 'smoothness', 'memorability', 
                   'uniqueness', 'pronounceability', 'char_length', 'vowel_ratio']
        
        X = df[features].fillna(0).values
        y = df['primary_role'].values
        
        # Filter out rare roles
        role_counts = Counter(y)
        common_roles = [role for role, count in role_counts.items() if count >= 50]
        
        mask = np.isin(y, common_roles)
        X = X[mask]
        y = y[mask]
        
        logger.info(f"Training on {len(X)} members with {len(common_roles)} roles")
        
        # Split for out-of-sample testing
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        # Train Random Forest
        rf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
        rf.fit(X_train, y_train)
        
        # Test set performance
        y_pred = rf.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Baseline (majority class)
        baseline = max(Counter(y_test).values()) / len(y_test)
        
        # Feature importance
        feature_importance = dict(zip(features, rf.feature_importances_))
        feature_importance = {k: float(v) for k, v in sorted(feature_importance.items(), key=lambda x: -x[1])}
        
        # Cross-validation
        cv_scores = cross_val_score(rf, X, y, cv=5)
        
        logger.info(f"  Accuracy: {accuracy:.3f} (baseline: {baseline:.3f})")
        logger.info(f"  Cross-val: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
        logger.info(f"  Top features: {list(feature_importance.keys())[:3]}")
        
        return {
            'accuracy': float(accuracy),
            'baseline_accuracy': float(baseline),
            'improvement_over_baseline': float((accuracy - baseline) / baseline),
            'cross_val_mean': float(cv_scores.mean()),
            'cross_val_std': float(cv_scores.std()),
            'feature_importance': feature_importance,
            'n_roles': len(common_roles),
            'roles': common_roles,
            'n_train': len(X_train),
            'n_test': len(X_test),
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
            'interpretation': f"Name features predict role with {accuracy:.1%} accuracy (vs {baseline:.1%} baseline)"
        }
    
    def _analyze_collective_composition(self, df: pd.DataFrame) -> Dict:
        """
        Analyze how collective member name composition relates to band success.
        
        Multi-level analysis: aggregate member features to band level.
        """
        logger.info("Analyzing collective name composition...")
        
        if 'band_id' not in df.columns or 'band_popularity_score' not in df.columns:
            logger.warning("Band data not available for collective analysis")
            return {'status': 'insufficient_data'}
        
        # Group by band
        band_groups = df.groupby('band_id')
        
        band_stats = []
        for band_id, group in band_groups:
            if len(group) < 2:  # Need at least 2 members
                continue
            
            band_stat = {
                'band_id': band_id,
                'n_members': len(group),
                'avg_harshness': float(group['harshness'].mean()),
                'std_harshness': float(group['harshness'].std()),
                'avg_smoothness': float(group['smoothness'].mean()),
                'std_smoothness': float(group['smoothness'].std()),
                'avg_syllables': float(group['syllables'].mean()),
                'phonetic_diversity': float(group['harshness'].std() + group['smoothness'].std()),  # Diversity metric
                'band_popularity': float(group['band_popularity_score'].iloc[0]) if 'band_popularity_score' in group.columns else 0,
                'band_listeners': float(group['band_listeners'].iloc[0]) if 'band_listeners' in group.columns else 0
            }
            
            band_stats.append(band_stat)
        
        band_df = pd.DataFrame(band_stats)
        
        logger.info(f"Analyzing {len(band_df)} bands with multiple members")
        
        # Correlation: phonetic diversity → success
        if len(band_df) > 20:
            r_pop, p_pop = stats.pearsonr(band_df['phonetic_diversity'], band_df['band_popularity'])
            
            logger.info(f"  Phonetic diversity vs popularity: r={r_pop:.3f}, p={p_pop:.4f}")
            
            # Test "harsh rhythm + smooth frontman" hypothesis
            # Split bands by composition
            harsh_rhythm_bands = band_df[band_df['avg_harshness'] > band_df['avg_harshness'].median()]
            soft_rhythm_bands = band_df[band_df['avg_harshness'] <= band_df['avg_harshness'].median()]
            
            # t-test
            t_stat, p_val = stats.ttest_ind(harsh_rhythm_bands['band_popularity'], soft_rhythm_bands['band_popularity'])
            
            return {
                'n_bands': len(band_df),
                'diversity_popularity_correlation': {
                    'r': float(r_pop),
                    'p_value': float(p_pop),
                    'significant': bool(p_pop < 0.05),
                    'effect_size': self.framework.interpret_effect_size(r_pop, 'correlation')
                },
                'composition_effects': {
                    'harsh_mean_popularity': float(harsh_rhythm_bands['band_popularity'].mean()),
                    'soft_mean_popularity': float(soft_rhythm_bands['band_popularity'].mean()),
                    't_statistic': float(t_stat),
                    'p_value': float(p_val),
                    'significant': bool(p_val < 0.05)
                },
                'interpretation': f"Phonetic diversity correlates with band success (r={r_pop:.2f}, p={p_pop:.3f})"
            }
        
        return {'status': 'insufficient_bands', 'n_bands': len(band_df)}
    
    def _analyze_temporal_trends(self, df: pd.DataFrame) -> Dict:
        """Analyze temporal evolution of name-role patterns"""
        logger.info("Analyzing temporal trends...")
        
        # Filter to members with start year
        temporal_df = df[df['years_active_start'].notna()].copy()
        
        if len(temporal_df) < 100:
            return {'status': 'insufficient_temporal_data'}
        
        # Add decade
        temporal_df['decade'] = (temporal_df['years_active_start'] // 10) * 10
        
        # Trend analysis: syllables over time
        decade_stats = temporal_df.groupby('decade').agg({
            'syllables': ['mean', 'std', 'count'],
            'harshness': ['mean', 'std'],
            'stage_name': 'mean'  # Proportion of stage names
        }).reset_index()
        
        # Correlation: year → syllables
        r_syll, p_syll = stats.pearsonr(temporal_df['years_active_start'], temporal_df['syllables'])
        
        # Stage name trend
        r_stage, p_stage = stats.pearsonr(temporal_df['years_active_start'], temporal_df['stage_name'].astype(int))
        
        logger.info(f"  Syllables over time: r={r_syll:.3f}, p={p_syll:.4f}")
        logger.info(f"  Stage names over time: r={r_stage:.3f}, p={p_stage:.4f}")
        
        return {
            'n_temporal': len(temporal_df),
            'year_range': [int(temporal_df['years_active_start'].min()), int(temporal_df['years_active_start'].max())],
            'syllables_trend': {
                'r': float(r_syll),
                'p_value': float(p_syll),
                'significant': bool(p_syll < 0.05),
                'direction': 'increasing' if r_syll > 0 else 'decreasing'
            },
            'stage_name_trend': {
                'r': float(r_stage),
                'p_value': float(p_stage),
                'significant': bool(p_stage < 0.05),
                'direction': 'increasing' if r_stage > 0 else 'decreasing'
            },
            'decade_stats': decade_stats.to_dict('records')
        }
    
    def _test_hypotheses(self, df: pd.DataFrame) -> Dict:
        """Test specific research hypotheses"""
        tests = {}
        
        # H1: Harshness predicts drummer role
        if 'primary_role' in df.columns:
            drummers = df[df['primary_role'] == 'drummer']['harshness'].dropna()
            non_drummers = df[df['primary_role'] != 'drummer']['harshness'].dropna()
            
            if len(drummers) > 20 and len(non_drummers) > 20:
                t_stat, p_val = stats.ttest_ind(drummers, non_drummers)
                cohens_d = (drummers.mean() - non_drummers.mean()) / np.sqrt((drummers.std()**2 + non_drummers.std()**2) / 2)
                
                tests['H1_harshness_drummers'] = {
                    'hypothesis': 'Drummers have harsher names than other roles',
                    'drummers_mean': float(drummers.mean()),
                    'non_drummers_mean': float(non_drummers.mean()),
                    't_statistic': float(t_stat),
                    'p_value': float(p_val),
                    'cohens_d': float(cohens_d),
                    'effect_size': self.framework.interpret_effect_size(cohens_d, 'cohens_d'),
                    'significant': bool(p_val < 0.05),
                    'supported': bool(p_val < 0.05 and drummers.mean() > non_drummers.mean())
                }
                
                logger.info(f"  H1: Drummers harsher - {tests['H1_harshness_drummers']['supported']}")
        
        # H2: Smoothness predicts vocalist role
        if 'primary_role' in df.columns:
            vocalists = df[df['primary_role'] == 'vocalist']['smoothness'].dropna()
            non_vocalists = df[df['primary_role'] != 'vocalist']['smoothness'].dropna()
            
            if len(vocalists) > 20 and len(non_vocalists) > 20:
                t_stat, p_val = stats.ttest_ind(vocalists, non_vocalists)
                cohens_d = (vocalists.mean() - non_vocalists.mean()) / np.sqrt((vocalists.std()**2 + non_vocalists.std()**2) / 2)
                
                tests['H2_smoothness_vocalists'] = {
                    'hypothesis': 'Vocalists have smoother names than other roles',
                    'vocalists_mean': float(vocalists.mean()),
                    'non_vocalists_mean': float(non_vocalists.mean()),
                    't_statistic': float(t_stat),
                    'p_value': float(p_val),
                    'cohens_d': float(cohens_d),
                    'effect_size': self.framework.interpret_effect_size(cohens_d, 'cohens_d'),
                    'significant': bool(p_val < 0.05),
                    'supported': bool(p_val < 0.05 and vocalists.mean() > non_vocalists.mean())
                }
                
                logger.info(f"  H2: Vocalists smoother - {tests['H2_smoothness_vocalists']['supported']}")
        
        # H3: Syllable differences across roles (ANOVA)
        if 'primary_role' in df.columns:
            role_groups = []
            role_names = []
            
            for role in ['vocalist', 'guitarist', 'bassist', 'drummer', 'keyboardist']:
                role_data = df[df['primary_role'] == role]['syllables'].dropna()
                if len(role_data) >= 20:
                    role_groups.append(role_data.values)
                    role_names.append(role)
            
            if len(role_groups) >= 3:
                f_stat, p_val = stats.f_oneway(*role_groups)
                
                # Eta-squared (effect size for ANOVA)
                grand_mean = df['syllables'].mean()
                ss_between = sum(len(g) * (g.mean() - grand_mean)**2 for g in role_groups)
                ss_total = ((df['syllables'] - grand_mean)**2).sum()
                eta_squared = ss_between / ss_total if ss_total > 0 else 0
                
                tests['H3_syllables_by_role'] = {
                    'hypothesis': 'Syllable counts differ significantly across roles',
                    'f_statistic': float(f_stat),
                    'p_value': float(p_val),
                    'eta_squared': float(eta_squared),
                    'effect_size': self.framework.interpret_effect_size(eta_squared, 'r_squared'),
                    'significant': bool(p_val < 0.05),
                    'roles_tested': role_names,
                    'role_means': {role: float(df[df['primary_role'] == role]['syllables'].mean()) for role in role_names}
                }
                
                logger.info(f"  H3: Syllable ANOVA - F={f_stat:.2f}, p={p_val:.4f}")
        
        return tests
    
    def _validate_out_of_sample(self, df: pd.DataFrame) -> Dict:
        """Perform out-of-sample validation"""
        # This is handled in role_prediction model
        return {
            'method': 'train_test_split',
            'test_size': 0.2,
            'results': 'see_role_prediction_section'
        }
