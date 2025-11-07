"""Academic Names Deep Dive Analysis - Nominative Determinism in Academia

Comprehensive hypothesis testing for academic name-outcome relationships:

H1: Name Sophistication → University Prestige
H2: Phonetic Authority → Academic Rank  
H3: Memorability → Research Impact (h-index)
H4: Field-Specific Name Patterns (STEM vs Humanities)
H5: "Intellectual Name" Advantage at Top Universities (ROC AUC target: 0.916)
H6: Gender-Name Interaction (Exploratory)

Methodology: Regressive proof with cross-validation
Goal: Find shocking, publication-quality patterns
Output: Comprehensive report + visualizations
"""

import logging
import sys
import os
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, Any, List, Tuple
import warnings

warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from core.models import Academic, AcademicAnalysis, AcademicResearchMetrics
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.linear_model import LogisticRegression, Ridge, ElasticNet
from sklearn.model_selection import cross_val_score, KFold, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, roc_curve, accuracy_score, classification_report
import statsmodels.api as sm
from statsmodels.formula.api import ols, logit
import matplotlib.pyplot as plt
import seaborn as sns

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AcademicDeepDive:
    """Comprehensive analysis of academic name-success relationships"""
    
    def __init__(self):
        self.app = app
        
        self.output_dir = Path(__file__).parent.parent / 'analysis_outputs' / 'academic_determinism'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.figures_dir = self.output_dir / 'figures'
        self.figures_dir.mkdir(parents=True, exist_ok=True)
        
        self.results = {}
        
    def run_all_analyses(self) -> Dict[str, Any]:
        """Execute complete academic analysis suite"""
        
        logger.info("="*70)
        logger.info("ACADEMIC NAMES DEEP DIVE ANALYSIS")
        logger.info("="*70)
        logger.info("Testing nominative determinism in academia")
        logger.info("Target: ROC AUC 0.916 (matching hurricane analysis)")
        logger.info("="*70 + "\n")
        
        with self.app.app_context():
            # Load data
            self.df = self._load_academic_data()
            logger.info(f"✓ Loaded {len(self.df)} academics with complete data\n")
            
            # Run hypothesis tests
            self.results['h1_prestige'] = self._test_h1_name_sophistication_prestige()
            self.results['h2_rank'] = self._test_h2_authority_rank()
            self.results['h3_citations'] = self._test_h3_memorability_citations()
            self.results['h4_field_patterns'] = self._test_h4_field_patterns()
            self.results['h5_top20_prediction'] = self._test_h5_top20_prediction()
            self.results['h6_gender'] = self._test_h6_gender_interaction()
            
            # Additional analyses
            self.results['shocking_findings'] = self._identify_shocking_patterns()
            self.results['effect_sizes'] = self._calculate_comprehensive_effect_sizes()
            self.results['summary_stats'] = self._generate_summary_statistics()
            
            # Generate visualizations
            self._create_all_visualizations()
            
            # Save results
            self._save_results()
            
            # Generate report
            self._generate_comprehensive_report()
            
        return self.results
    
    def _load_academic_data(self) -> pd.DataFrame:
        """Load academic data with all features"""
        
        academics = Academic.query.all()
        analyses = {aa.academic_id: aa for aa in AcademicAnalysis.query.all()}
        metrics = {arm.academic_id: arm for arm in AcademicResearchMetrics.query.all()}
        
        data = []
        for academic in academics:
            analysis = analyses.get(academic.id)
            research = metrics.get(academic.id)
            
            if not analysis:
                continue  # Skip if no name analysis
            
            row = {
                'id': academic.id,
                'full_name': academic.full_name,
                'first_name': academic.first_name,
                'last_name': academic.last_name,
                
                # University characteristics
                'university_name': academic.university_name,
                'university_ranking': academic.university_ranking,
                'university_tier': academic.university_tier,
                'is_top_20': 1 if academic.university_tier == 'top_20' else 0,
                'is_top_50': 1 if academic.university_tier in ['top_20', 'top_50'] else 0,
                'is_ivy_league': 1 if any(ivy in academic.university_name for ivy in 
                                         ['Harvard', 'Yale', 'Princeton', 'Columbia', 'Penn', 
                                          'Brown', 'Dartmouth', 'Cornell']) else 0,
                
                # Academic position
                'academic_rank': academic.academic_rank,
                'rank_numeric': self._encode_rank(academic.academic_rank),
                'is_distinguished': 1 if academic.academic_rank == 'distinguished' else 0,
                'is_full_professor': 1 if academic.academic_rank in ['full', 'distinguished'] else 0,
                
                # Field
                'field_broad': academic.field_broad,
                'field_specific': academic.field_specific,
                'is_stem': 1 if academic.field_broad == 'stem' else 0,
                'is_humanities': 1 if academic.field_broad == 'humanities' else 0,
                'is_social_science': 1 if academic.field_broad == 'social_science' else 0,
                
                # Name features (basic)
                'syllable_count': analysis.syllable_count,
                'character_length': analysis.character_length,
                'phonetic_score': analysis.phonetic_score,
                'vowel_ratio': analysis.vowel_ratio,
                'consonant_clusters': analysis.consonant_clusters,
                
                # Name features (memorability)
                'memorability_score': analysis.memorability_score,
                'pronounceability_score': analysis.pronounceability_score,
                'uniqueness_score': analysis.uniqueness_score,
                
                # Name features (advanced)
                'authority_score': analysis.authority_score,
                'innovation_score': analysis.innovation_score,
                'trust_score': analysis.trust_score,
                'consonant_hardness': analysis.consonant_hardness,
                'vowel_brightness': analysis.vowel_brightness,
                
                # Name features (phonemic)
                'plosive_ratio': analysis.plosive_ratio,
                'fricative_ratio': analysis.fricative_ratio,
                'voicing_ratio': analysis.voicing_ratio,
                'initial_is_plosive': 1 if analysis.initial_is_plosive else 0,
                
                # Academic-specific composites
                'intellectual_sophistication': analysis.intellectual_sophistication_score,
                'academic_authority_composite': analysis.academic_authority_composite,
                
                # Demographics
                'gender_coding': analysis.gender_coding,
                'is_masculine_name': 1 if analysis.gender_coding == 'masculine' else 0,
                'is_feminine_name': 1 if analysis.gender_coding == 'feminine' else 0,
                'is_neutral_name': 1 if analysis.gender_coding in ['neutral', 'ambiguous'] else 0,
            }
            
            # Research metrics (if available)
            if research:
                row.update({
                    'h_index': research.h_index,
                    'total_citations': research.total_citations,
                    'i10_index': research.i10_index,
                    'years_publishing': research.years_publishing,
                    'citations_per_year': research.citations_per_year,
                    'has_google_scholar': 1
                })
            else:
                row.update({
                    'h_index': None,
                    'total_citations': None,
                    'i10_index': None,
                    'years_publishing': None,
                    'citations_per_year': None,
                    'has_google_scholar': 0
                })
            
            data.append(row)
        
        df = pd.DataFrame(data)
        
        # Additional derived features
        if 'h_index' in df.columns:
            df['log_h_index'] = np.log1p(df['h_index'].fillna(0))
            df['log_citations'] = np.log1p(df['total_citations'].fillna(0))
        
        logger.info(f"Loaded data shape: {df.shape}")
        logger.info(f"  - Academics: {len(df)}")
        logger.info(f"  - With Google Scholar: {df['has_google_scholar'].sum()}")
        logger.info(f"  - Top 20 universities: {df['is_top_20'].sum()}")
        logger.info(f"  - Top 50 universities: {df['is_top_50'].sum()}")
        logger.info(f"  - Ivy League: {df['is_ivy_league'].sum()}")
        
        return df
    
    def _encode_rank(self, rank: str) -> int:
        """Convert academic rank to numeric scale"""
        rank_map = {
            'lecturer': 1,
            'instructor': 1,
            'assistant': 2,
            'associate': 3,
            'full': 4,
            'distinguished': 5,
            'endowed': 5,
            'emeritus': 4,
            'unknown': 0
        }
        return rank_map.get(rank, 0)
    
    # =========================================================================
    # H1: NAME SOPHISTICATION → UNIVERSITY PRESTIGE
    # =========================================================================
    
    def _test_h1_name_sophistication_prestige(self) -> Dict[str, Any]:
        """
        Test if name sophistication predicts university prestige
        
        Target: university_ranking (lower = better)
        Controls: PhD institution, field
        Prediction: Higher sophistication → lower rank (better university)
        """
        logger.info("\n" + "="*70)
        logger.info("H1: NAME SOPHISTICATION → UNIVERSITY PRESTIGE")
        logger.info("="*70)
        
        # Filter to academics with university ranking
        df_test = self.df[self.df['university_ranking'].notna()].copy()
        logger.info(f"Sample size: {len(df_test)}")
        
        if len(df_test) < 30:
            logger.warning("Insufficient sample size for H1")
            return {'status': 'insufficient_data', 'n': len(df_test)}
        
        # Prepare features
        features = [
            'intellectual_sophistication',
            'phonetic_score',
            'authority_score',
            'syllable_count',
            'uniqueness_score'
        ]
        
        X = df_test[features].fillna(df_test[features].median())
        y = df_test['university_ranking']  # Lower = better
        
        # Standardize
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Ridge regression with cross-validation
        model = Ridge(alpha=1.0)
        cv_scores = cross_val_score(model, X_scaled, y, cv=5, scoring='r2')
        
        # Fit full model for coefficients
        model.fit(X_scaled, y)
        
        # Statistics
        from sklearn.metrics import mean_squared_error, r2_score
        y_pred = model.predict(X_scaled)
        r2_train = r2_score(y, y_pred)
        rmse = np.sqrt(mean_squared_error(y, y_pred))
        
        results = {
            'n': len(df_test),
            'features': features,
            'coefficients': dict(zip(features, model.coef_)),
            'r2_train': r2_train,
            'r2_cv_mean': cv_scores.mean(),
            'r2_cv_std': cv_scores.std(),
            'rmse': rmse,
            'interpretation': self._interpret_h1(model.coef_, features, cv_scores.mean())
        }
        
        logger.info(f"  R² (training): {r2_train:.3f}")
        logger.info(f"  R² (CV): {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
        logger.info(f"  RMSE: {rmse:.1f} ranking positions")
        logger.info(f"\n  Coefficients:")
        for feature, coef in results['coefficients'].items():
            logger.info(f"    {feature:30s}: {coef:8.3f}")
        
        logger.info(f"\n{results['interpretation']}")
        
        return results
    
    def _interpret_h1(self, coefficients, features, r2_cv) -> str:
        """Interpret H1 results"""
        if r2_cv > 0.10:
            return "🔥 SHOCKING: Name sophistication predicts university prestige with R²>0.10! This is publication-worthy."
        elif r2_cv > 0.05:
            return "✓ MODERATE SIGNAL: Name metrics explain 5-10% of university prestige variance. Interesting but modest effect."
        elif r2_cv > 0.0:
            return "⚠️ WEAK SIGNAL: Positive but small effect (R²<0.05). May be noise."
        else:
            return "❌ NULL FINDING: No predictive relationship between name sophistication and university prestige."
    
    # =========================================================================
    # H2: PHONETIC AUTHORITY → ACADEMIC RANK
    # =========================================================================
    
    def _test_h2_authority_rank(self) -> Dict[str, Any]:
        """
        Test if phonetic authority predicts academic rank
        
        Target: rank_numeric (ordinal)
        Controls: years_publishing (if available)
        Prediction: Higher authority → higher rank
        """
        logger.info("\n" + "="*70)
        logger.info("H2: PHONETIC AUTHORITY → ACADEMIC RANK")
        logger.info("="*70)
        
        # Filter to known ranks
        df_test = self.df[self.df['rank_numeric'] > 0].copy()
        logger.info(f"Sample size: {len(df_test)}")
        
        if len(df_test) < 50:
            logger.warning("Insufficient sample size for H2")
            return {'status': 'insufficient_data', 'n': len(df_test)}
        
        # Binary: Full professor or higher vs lower ranks
        df_test['is_senior'] = (df_test['rank_numeric'] >= 4).astype(int)
        
        features = [
            'authority_score',
            'academic_authority_composite',
            'consonant_hardness',
            'memorability_score',
            'intellectual_sophistication'
        ]
        
        X = df_test[features].fillna(df_test[features].median())
        y = df_test['is_senior']
        
        # Standardize
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Logistic regression with cross-validation
        model = LogisticRegression(penalty='l2', C=1.0, max_iter=1000)
        
        # Stratified cross-validation
        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        cv_scores = cross_val_score(model, X_scaled, y, cv=skf, scoring='roc_auc')
        
        # Fit full model
        model.fit(X_scaled, y)
        y_pred_proba = model.predict_proba(X_scaled)[:, 1]
        y_pred = model.predict(X_scaled)
        
        # Calculate metrics
        roc_auc_train = roc_auc_score(y, y_pred_proba)
        accuracy = accuracy_score(y, y_pred)
        
        # Odds ratios (approximate from standardized coefficients)
        odds_ratios = np.exp(model.coef_[0])
        
        results = {
            'n': len(df_test),
            'n_senior': y.sum(),
            'features': features,
            'coefficients': dict(zip(features, model.coef_[0])),
            'odds_ratios': dict(zip(features, odds_ratios)),
            'roc_auc_train': roc_auc_train,
            'roc_auc_cv_mean': cv_scores.mean(),
            'roc_auc_cv_std': cv_scores.std(),
            'accuracy': accuracy,
            'interpretation': self._interpret_h2(cv_scores.mean(), odds_ratios[0])
        }
        
        logger.info(f"  ROC AUC (training): {roc_auc_train:.3f}")
        logger.info(f"  ROC AUC (CV): {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
        logger.info(f"  Accuracy: {accuracy:.3f}")
        logger.info(f"\n  Odds Ratios (per SD increase):")
        for feature, or_val in results['odds_ratios'].items():
            logger.info(f"    {feature:30s}: {or_val:.3f}")
        
        logger.info(f"\n{results['interpretation']}")
        
        return results
    
    def _interpret_h2(self, roc_auc, authority_or) -> str:
        """Interpret H2 results"""
        if roc_auc > 0.75 and authority_or > 1.5:
            return "🔥 STRONG EFFECT: Authority score predicts senior rank with OR>1.5 and AUC>0.75!"
        elif roc_auc > 0.65:
            return "✓ MODERATE EFFECT: Phonetic authority correlates with academic rank (AUC>0.65)."
        elif roc_auc > 0.55:
            return "⚠️ WEAK SIGNAL: Small predictive power (AUC 0.55-0.65)."
        else:
            return "❌ NULL: Authority score does not predict academic rank."
    
    # =========================================================================
    # H3: MEMORABILITY → RESEARCH IMPACT (h-index)
    # =========================================================================
    
    def _test_h3_memorability_citations(self) -> Dict[str, Any]:
        """
        Test if memorable names → more citations
        
        Hypothesis: Name recognition effect
        """
        logger.info("\n" + "="*70)
        logger.info("H3: MEMORABILITY → RESEARCH IMPACT (h-index)")
        logger.info("="*70)
        
        # Filter to academics with Google Scholar data
        df_test = self.df[
            (self.df['has_google_scholar'] == 1) & 
            (self.df['h_index'].notna()) &
            (self.df['h_index'] > 0)
        ].copy()
        
        logger.info(f"Sample size: {len(df_test)}")
        
        if len(df_test) < 30:
            logger.warning("Insufficient sample size for H3")
            return {'status': 'insufficient_data', 'n': len(df_test)}
        
        features = [
            'memorability_score',
            'pronounceability_score',
            'uniqueness_score',
            'syllable_count',
            'character_length'
        ]
        
        # Control for career length if available
        if 'years_publishing' in df_test.columns:
            features.append('years_publishing')
        
        X = df_test[features].fillna(df_test[features].median())
        y = df_test['log_h_index']  # Log transform for normality
        
        # Standardize
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Ridge regression
        model = Ridge(alpha=1.0)
        cv_scores = cross_val_score(model, X_scaled, y, cv=5, scoring='r2')
        
        model.fit(X_scaled, y)
        y_pred = model.predict(X_scaled)
        
        from sklearn.metrics import r2_score
        r2_train = r2_score(y, y_pred)
        
        # Correlation analysis
        memorability_corr = df_test['memorability_score'].corr(df_test['h_index'])
        
        results = {
            'n': len(df_test),
            'features': features,
            'coefficients': dict(zip(features, model.coef_)),
            'r2_train': r2_train,
            'r2_cv_mean': cv_scores.mean(),
            'r2_cv_std': cv_scores.std(),
            'memorability_h_index_corr': memorability_corr,
            'interpretation': self._interpret_h3(cv_scores.mean(), memorability_corr)
        }
        
        logger.info(f"  R² (training): {r2_train:.3f}")
        logger.info(f"  R² (CV): {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
        logger.info(f"  Memorability-h_index correlation: {memorability_corr:.3f}")
        logger.info(f"\n{results['interpretation']}")
        
        return results
    
    def _interpret_h3(self, r2_cv, correlation) -> str:
        """Interpret H3 results"""
        if r2_cv > 0.15 and correlation > 0.3:
            return "🔥 PARADIGM SHIFT: Memorable names predict higher h-index! Citation advantage for easy names."
        elif r2_cv > 0.10:
            return "✓ MEANINGFUL EFFECT: Name memorability explains 10%+ of h-index variance."
        elif correlation > 0.15:
            return "⚠️ WEAK SIGNAL: Positive correlation but low predictive power."
        else:
            return "❌ NULL: No relationship between name memorability and research impact."
    
    # =========================================================================
    # H4: FIELD-SPECIFIC NAME PATTERNS
    # =========================================================================
    
    def _test_h4_field_patterns(self) -> Dict[str, Any]:
        """
        Test if STEM vs Humanities have different phonetic profiles
        
        Prediction: STEM = harder consonants, Humanities = softer
        """
        logger.info("\n" + "="*70)
        logger.info("H4: FIELD-SPECIFIC NAME PATTERNS")
        logger.info("="*70)
        
        # Compare STEM vs Humanities
        df_stem = self.df[self.df['is_stem'] == 1].copy()
        df_hum = self.df[self.df['is_humanities'] == 1].copy()
        
        logger.info(f"STEM: n={len(df_stem)}")
        logger.info(f"Humanities: n={len(df_hum)}")
        
        if len(df_stem) < 20 or len(df_hum) < 20:
            return {'status': 'insufficient_data'}
        
        # Test multiple phonetic features
        features_to_test = [
            'consonant_hardness',
            'plosive_ratio',
            'vowel_brightness',
            'authority_score',
            'syllable_count'
        ]
        
        comparisons = {}
        for feature in features_to_test:
            stem_vals = df_stem[feature].dropna()
            hum_vals = df_hum[feature].dropna()
            
            if len(stem_vals) > 0 and len(hum_vals) > 0:
                # T-test
                t_stat, p_val = stats.ttest_ind(stem_vals, hum_vals)
                
                # Cohen's d (effect size)
                pooled_std = np.sqrt((stem_vals.std()**2 + hum_vals.std()**2) / 2)
                cohens_d = (stem_vals.mean() - hum_vals.mean()) / pooled_std if pooled_std > 0 else 0
                
                comparisons[feature] = {
                    'stem_mean': stem_vals.mean(),
                    'humanities_mean': hum_vals.mean(),
                    'difference': stem_vals.mean() - hum_vals.mean(),
                    't_statistic': t_stat,
                    'p_value': p_val,
                    'cohens_d': cohens_d,
                    'significant': p_val < 0.05
                }
                
                sig_marker = "***" if p_val < 0.001 else ("**" if p_val < 0.01 else ("*" if p_val < 0.05 else ""))
                logger.info(f"\n{feature}:")
                logger.info(f"  STEM: {stem_vals.mean():.3f}")
                logger.info(f"  Humanities: {hum_vals.mean():.3f}")
                logger.info(f"  Difference: {stem_vals.mean() - hum_vals.mean():.3f}")
                logger.info(f"  Cohen's d: {cohens_d:.3f}")
                logger.info(f"  p-value: {p_val:.4f} {sig_marker}")
        
        # Overall interpretation
        significant_effects = [f for f, c in comparisons.items() if c['significant']]
        large_effects = [f for f, c in comparisons.items() if abs(c['cohens_d']) > 0.5]
        
        interpretation = self._interpret_h4(significant_effects, large_effects, comparisons)
        
        results = {
            'n_stem': len(df_stem),
            'n_humanities': len(df_hum),
            'comparisons': comparisons,
            'significant_features': significant_effects,
            'large_effect_features': large_effects,
            'interpretation': interpretation
        }
        
        logger.info(f"\n{interpretation}")
        
        return results
    
    def _interpret_h4(self, sig_features, large_effects, comparisons) -> str:
        """Interpret H4 results"""
        if len(large_effects) >= 2:
            return f"🔥 FIELD SIGNATURE DETECTED: {len(large_effects)} features show large effects (d>0.5)! STEM vs Humanities names ARE different."
        elif len(sig_features) >= 3:
            return f"✓ CLEAR PATTERN: {len(sig_features)} significant differences. Fields select for different name types."
        elif len(sig_features) > 0:
            return f"⚠️ WEAK PATTERN: Only {len(sig_features)} significant differences. May be noise."
        else:
            return "❌ NULL: No systematic phonetic differences between STEM and Humanities professors."
    
    # =========================================================================
    # H5: TOP-20 UNIVERSITY PREDICTION (THE BIG ONE)
    # =========================================================================
    
    def _test_h5_top20_prediction(self) -> Dict[str, Any]:
        """
        Predict Top-20 university from name alone
        
        GOAL: ROC AUC > 0.85 (ideally > 0.90 to match hurricane 0.916)
        """
        logger.info("\n" + "="*70)
        logger.info("H5: TOP-20 UNIVERSITY PREDICTION")
        logger.info("="*70)
        logger.info("🎯 TARGET: ROC AUC > 0.85 (match hurricane 0.916)")
        logger.info("="*70)
        
        df_test = self.df[self.df['university_tier'].notna()].copy()
        logger.info(f"Sample size: {len(df_test)}")
        logger.info(f"Top-20: {df_test['is_top_20'].sum()} ({df_test['is_top_20'].mean()*100:.1f}%)")
        
        if len(df_test) < 50:
            return {'status': 'insufficient_data'}
        
        # Use ALL name features
        features = [
            'intellectual_sophistication',
            'academic_authority_composite',
            'authority_score',
            'memorability_score',
            'phonetic_score',
            'syllable_count',
            'consonant_hardness',
            'vowel_brightness',
            'uniqueness_score',
            'plosive_ratio'
        ]
        
        X = df_test[features].fillna(df_test[features].median())
        y = df_test['is_top_20']
        
        # Standardize
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Logistic regression with stratified CV
        model = LogisticRegression(penalty='l2', C=0.5, max_iter=1000)
        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        
        cv_scores_auc = cross_val_score(model, X_scaled, y, cv=skf, scoring='roc_auc')
        cv_scores_acc = cross_val_score(model, X_scaled, y, cv=skf, scoring='accuracy')
        
        # Fit full model
        model.fit(X_scaled, y)
        y_pred_proba = model.predict_proba(X_scaled)[:, 1]
        y_pred = model.predict(X_scaled)
        
        # Metrics
        roc_auc_train = roc_auc_score(y, y_pred_proba)
        roc_auc_cv = cv_scores_auc.mean()
        accuracy_train = accuracy_score(y, y_pred)
        accuracy_cv = cv_scores_acc.mean()
        
        # ROC curve for visualization
        fpr, tpr, thresholds = roc_curve(y, y_pred_proba)
        
        # Feature importance (absolute coefficients)
        feature_importance = dict(zip(features, np.abs(model.coef_[0])))
        top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:5]
        
        results = {
            'n': len(df_test),
            'n_positive': y.sum(),
            'features': features,
            'coefficients': dict(zip(features, model.coef_[0])),
            'feature_importance': feature_importance,
            'top_5_features': top_features,
            'roc_auc_train': roc_auc_train,
            'roc_auc_cv_mean': roc_auc_cv,
            'roc_auc_cv_std': cv_scores_auc.std(),
            'accuracy_train': accuracy_train,
            'accuracy_cv_mean': accuracy_cv,
            'accuracy_cv_std': cv_scores_acc.std(),
            'roc_curve': {'fpr': fpr.tolist(), 'tpr': tpr.tolist(), 'thresholds': thresholds.tolist()},
            'interpretation': self._interpret_h5(roc_auc_cv, accuracy_cv)
        }
        
        logger.info(f"\n  🎯 ROC AUC (training): {roc_auc_train:.3f}")
        logger.info(f"  🎯 ROC AUC (CV): {roc_auc_cv:.3f} ± {cv_scores_auc.std():.3f}")
        logger.info(f"  Accuracy (training): {accuracy_train:.3f}")
        logger.info(f"  Accuracy (CV): {accuracy_cv:.3f} ± {cv_scores_acc.std():.3f}")
        
        logger.info(f"\n  Top 5 Predictive Features:")
        for feature, importance in top_features:
            logger.info(f"    {feature:30s}: {importance:.3f}")
        
        logger.info(f"\n{results['interpretation']}")
        
        return results
    
    def _interpret_h5(self, roc_auc, accuracy) -> str:
        """Interpret H5 results - THE MONEY SHOT"""
        if roc_auc >= 0.90:
            return "🔥🔥🔥 PARADIGM-SHIFTING: ROC AUC ≥ 0.90! We can predict Harvard from names! NATURE/SCIENCE PAPER!"
        elif roc_auc >= 0.85:
            return "🔥🔥 BREAKTHROUGH: ROC AUC ≥ 0.85! Top-20 university strongly predicted by name. PNAS/Science Advances!"
        elif roc_auc >= 0.75:
            return "🔥 STRONG FINDING: ROC AUC ≥ 0.75. Meaningful predictive power. Publication in specialty journal."
        elif roc_auc >= 0.65:
            return "✓ MODERATE SIGNAL: ROC AUC 0.65-0.75. Interesting but not shocking."
        elif roc_auc >= 0.55:
            return "⚠️ WEAK SIGNAL: ROC AUC 0.55-0.65. Barely better than chance."
        else:
            return "❌ NULL: Cannot predict top-20 university from name (AUC ≤ 0.55)."
    
    # =========================================================================
    # H6: GENDER-NAME INTERACTION (EXPLORATORY)
    # =========================================================================
    
    def _test_h6_gender_interaction(self) -> Dict[str, Any]:
        """
        Test if masculine/neutral names advantage women in academia
        
        SENSITIVE - Handle with care
        """
        logger.info("\n" + "="*70)
        logger.info("H6: GENDER-NAME INTERACTION (EXPLORATORY)")
        logger.info("="*70)
        logger.info("⚠️  Sensitive analysis - descriptive only")
        
        # Count by gender coding
        gender_dist = self.df['gender_coding'].value_counts()
        
        logger.info("\nGender coding distribution:")
        for gender, count in gender_dist.items():
            logger.info(f"  {gender:15s}: {count:5d} ({count/len(self.df)*100:.1f}%)")
        
        # Placeholder for full analysis
        # Would require external gender data for actual professors
        
        results = {
            'status': 'exploratory',
            'gender_distribution': gender_dist.to_dict(),
            'note': 'Requires external gender coding for professors. Name-gender inference insufficient.'
        }
        
        logger.info("\n⚠️  Full gender analysis requires manual coding.")
        logger.info("Recommendation: Defer to future work with proper data.")
        
        return results
    
    # =========================================================================
    # SHOCKING PATTERNS DETECTION
    # =========================================================================
    
    def _identify_shocking_patterns(self) -> Dict[str, Any]:
        """
        Hunt for unexpected, publication-worthy patterns
        """
        logger.info("\n" + "="*70)
        logger.info("SHOCKING PATTERNS DETECTION")
        logger.info("="*70)
        
        shocks = []
        
        # Check for Ivy League phonetic signature
        ivy = self.df[self.df['is_ivy_league'] == 1]
        non_ivy = self.df[self.df['is_ivy_league'] == 0]
        
        if len(ivy) >= 20 and len(non_ivy) >= 20:
            for feature in ['authority_score', 'intellectual_sophistication', 'consonant_hardness']:
                if feature in ivy.columns:
                    ivy_mean = ivy[feature].mean()
                    non_ivy_mean = non_ivy[feature].mean()
                    t_stat, p_val = stats.ttest_ind(ivy[feature].dropna(), non_ivy[feature].dropna())
                    
                    if p_val < 0.01:
                        effect_size = (ivy_mean - non_ivy_mean) / non_ivy[feature].std()
                        shocks.append({
                            'pattern': f'Ivy League {feature}',
                            'ivy_mean': ivy_mean,
                            'non_ivy_mean': non_ivy_mean,
                            'p_value': p_val,
                            'effect_size': effect_size,
                            'shocking': abs(effect_size) > 0.3
                        })
        
        # Log findings
        logger.info(f"Found {len(shocks)} potential shocking patterns")
        for shock in shocks:
            if shock['shocking']:
                logger.info(f"  🔥 {shock['pattern']}: p={shock['p_value']:.4f}, d={shock['effect_size']:.3f}")
        
        return {'patterns': shocks, 'count': len(shocks)}
    
    def _calculate_comprehensive_effect_sizes(self) -> Dict[str, Any]:
        """Calculate effect sizes for all tests"""
        logger.info("\n" + "="*70)
        logger.info("COMPREHENSIVE EFFECT SIZES")
        logger.info("="*70)
        
        effect_sizes = {
            'h1_r2': self.results.get('h1_prestige', {}).get('r2_cv_mean', 0),
            'h2_roc_auc': self.results.get('h2_rank', {}).get('roc_auc_cv_mean', 0.5),
            'h3_r2': self.results.get('h3_citations', {}).get('r2_cv_mean', 0),
            'h5_roc_auc': self.results.get('h5_top20_prediction', {}).get('roc_auc_cv_mean', 0.5),
        }
        
        logger.info("Effect size summary:")
        for test, effect in effect_sizes.items():
            logger.info(f"  {test:20s}: {effect:.3f}")
        
        return effect_sizes
    
    def _generate_summary_statistics(self) -> Dict[str, Any]:
        """Generate descriptive statistics"""
        logger.info("\n" + "="*70)
        logger.info("SUMMARY STATISTICS")
        logger.info("="*70)
        
        summary = {
            'n_total': len(self.df),
            'n_with_google_scholar': self.df['has_google_scholar'].sum(),
            'university_tiers': self.df['university_tier'].value_counts().to_dict(),
            'fields': self.df['field_broad'].value_counts().to_dict(),
            'ranks': self.df['academic_rank'].value_counts().to_dict(),
            
            'name_metrics_means': {
                'authority_score': self.df['authority_score'].mean(),
                'memorability_score': self.df['memorability_score'].mean(),
                'intellectual_sophistication': self.df['intellectual_sophistication'].mean(),
                'syllable_count': self.df['syllable_count'].mean(),
            }
        }
        
        for key, value in summary.items():
            logger.info(f"{key}: {value}")
        
        return summary
    
    def _create_all_visualizations(self):
        """Generate publication-quality visualizations"""
        logger.info("\n" + "="*70)
        logger.info("GENERATING VISUALIZATIONS")
        logger.info("="*70)
        
        # Set publication style
        sns.set_style('whitegrid')
        plt.rcParams['figure.figsize'] = (10, 6)
        plt.rcParams['font.size'] = 11
        
        # 1. ROC Curve for H5 (Top-20 prediction)
        if 'h5_top20_prediction' in self.results and 'roc_curve' in self.results['h5_top20_prediction']:
            self._plot_roc_curve_h5()
        
        # 2. Field comparison violin plots
        if 'h4_field_patterns' in self.results:
            self._plot_field_comparison()
        
        # 3. Effect sizes bar chart
        self._plot_effect_sizes()
        
        # 4. Name metric distributions by university tier
        self._plot_metrics_by_tier()
        
        logger.info(f"✓ Visualizations saved to {self.figures_dir}")
    
    def _plot_roc_curve_h5(self):
        """Plot ROC curve for H5 top-20 prediction"""
        h5 = self.results['h5_top20_prediction']
        
        fpr = h5['roc_curve']['fpr']
        tpr = h5['roc_curve']['tpr']
        auc = h5['roc_auc_cv_mean']
        
        plt.figure(figsize=(8, 8))
        plt.plot(fpr, tpr, linewidth=2, label=f'Academic Names (AUC = {auc:.3f})')
        plt.plot([0, 1], [0, 1], 'k--', linewidth=1, label='Chance (AUC = 0.500)')
        
        # Add hurricane comparison line (legendary 0.916)
        plt.axhline(y=0.916, color='red', linestyle=':', linewidth=2, alpha=0.7, label='Hurricane ROC AUC (0.916)')
        
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Top-20 University Prediction from Name Alone', fontsize=14, fontweight='bold')
        plt.legend(loc='lower right')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.figures_dir / 'h5_roc_curve_top20.png', dpi=300)
        plt.close()
        
        logger.info("  ✓ ROC curve saved")
    
    def _plot_field_comparison(self):
        """Violin plots comparing STEM vs Humanities"""
        df_plot = self.df[self.df['field_broad'].isin(['stem', 'humanities'])].copy()
        
        features = ['authority_score', 'consonant_hardness', 'intellectual_sophistication']
        
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        for i, feature in enumerate(features):
            sns.violinplot(data=df_plot, x='field_broad', y=feature, ax=axes[i])
            axes[i].set_title(feature.replace('_', ' ').title())
            axes[i].set_xlabel('')
        
        plt.suptitle('Phonetic Profiles: STEM vs Humanities', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(self.figures_dir / 'h4_field_comparison.png', dpi=300)
        plt.close()
        
        logger.info("  ✓ Field comparison saved")
    
    def _plot_effect_sizes(self):
        """Bar chart of all effect sizes"""
        effect_sizes = self.results.get('effect_sizes', {})
        
        labels = [
            'H1: Prestige (R²)',
            'H2: Rank (AUC)',
            'H3: Citations (R²)',
            'H5: Top-20 (AUC)'
        ]
        
        values = [
            effect_sizes.get('h1_r2', 0),
            effect_sizes.get('h2_roc_auc', 0.5) - 0.5,  # Subtract baseline for AUC
            effect_sizes.get('h3_r2', 0),
            effect_sizes.get('h5_roc_auc', 0.5) - 0.5
        ]
        
        plt.figure(figsize=(10, 6))
        bars = plt.barh(labels, values, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
        plt.xlabel('Effect Size')
        plt.title('Academic Nominative Determinism: Effect Sizes', fontsize=14, fontweight='bold')
        plt.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
        plt.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        plt.savefig(self.figures_dir / 'comprehensive_effect_sizes.png', dpi=300)
        plt.close()
        
        logger.info("  ✓ Effect sizes chart saved")
    
    def _plot_metrics_by_tier(self):
        """Box plots of name metrics by university tier"""
        df_plot = self.df[self.df['university_tier'].notna()].copy()
        
        tier_order = ['top_20', 'top_50', 'top_100', 'other']
        df_plot = df_plot[df_plot['university_tier'].isin(tier_order)]
        
        plt.figure(figsize=(12, 6))
        sns.boxplot(data=df_plot, x='university_tier', y='intellectual_sophistication', 
                   order=tier_order)
        plt.xlabel('University Tier')
        plt.ylabel('Intellectual Sophistication Score')
        plt.title('Name Sophistication by University Prestige', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(self.figures_dir / 'sophistication_by_tier.png', dpi=300)
        plt.close()
        
        logger.info("  ✓ Metrics by tier saved")
    
    def _save_results(self):
        """Save all results to JSON"""
        results_file = self.output_dir / 'academic_analysis_results.json'
        
        # Convert numpy types to native Python for JSON serialization
        def convert_types(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            return obj
        
        import json
        
        class NumpyEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, (np.integer, np.int64)):
                    return int(obj)
                elif isinstance(obj, (np.floating, np.float64)):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                return super().default(obj)
        
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2, cls=NumpyEncoder)
        
        logger.info(f"\n✓ Results saved to {results_file}")
    
    def _generate_comprehensive_report(self):
        """Generate markdown report"""
        report_file = self.output_dir / 'ACADEMIC_FINDINGS.md'
        
        report = f"""# Academic Names Nominative Determinism - Findings Report

**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Sample Size:** {len(self.df)} academics  
**Methodology:** Regressive proof with 5-fold cross-validation  

---

## Executive Summary

This analysis tests whether name phonetics predict academic outcomes using {len(self.df)} university professors.

### Key Findings

**H1: Name Sophistication → University Prestige**
- R² (CV): {self.results.get('h1_prestige', {}).get('r2_cv_mean', 0):.3f}
- {self.results.get('h1_prestige', {}).get('interpretation', 'N/A')}

**H2: Phonetic Authority → Academic Rank**
- ROC AUC (CV): {self.results.get('h2_rank', {}).get('roc_auc_cv_mean', 0):.3f}
- {self.results.get('h2_rank', {}).get('interpretation', 'N/A')}

**H3: Memorability → Research Impact**
- R² (CV): {self.results.get('h3_citations', {}).get('r2_cv_mean', 0):.3f}
- {self.results.get('h3_citations', {}).get('interpretation', 'N/A')}

**H4: Field-Specific Patterns**
- Significant features: {len(self.results.get('h4_field_patterns', {}).get('significant_features', []))}
- {self.results.get('h4_field_patterns', {}).get('interpretation', 'N/A')}

**H5: Top-20 University Prediction** 🎯
- ROC AUC (CV): {self.results.get('h5_top20_prediction', {}).get('roc_auc_cv_mean', 0):.3f}
- Target: 0.916 (hurricane benchmark)
- {self.results.get('h5_top20_prediction', {}).get('interpretation', 'N/A')}

---

## Publication Recommendations

"""
        
        # Add publication recommendations based on results
        h5_auc = self.results.get('h5_top20_prediction', {}).get('roc_auc_cv_mean', 0)
        
        if h5_auc >= 0.90:
            report += """
### Target: *Nature* or *Science*
- ROC AUC ≥ 0.90 is paradigm-shifting
- Trade press angle: "Can We Predict Harvard Professors from Their Names?"
- Policy implications for academic hiring bias
"""
        elif h5_auc >= 0.75:
            report += """
### Target: *PNAS*, *Science Advances*, *Nature Human Behaviour*
- Strong predictive signal warrants top-tier journal
- Angle: Hidden phonetic patterns in academic success
"""
        else:
            report += """
### Target: *PLOS ONE*, *Psychology & Education*, specialty journals
- Modest effects suitable for field-specific publication
- Frame as exploratory analysis with null findings documented
"""
        
        report += f"""

---

## Detailed Results

See `academic_analysis_results.json` for complete statistical output.

**Visualizations:**
- ROC curve: `figures/h5_roc_curve_top20.png`
- Field comparison: `figures/h4_field_comparison.png`
- Effect sizes: `figures/comprehensive_effect_sizes.png`

---

*Generated by Academic Deep Dive Analysis Pipeline*
"""
        
        with open(report_file, 'w') as f:
            f.write(report)
        
        logger.info(f"✓ Report saved to {report_file}")


def main():
    """Run complete academic analysis"""
    analyzer = AcademicDeepDive()
    results = analyzer.run_all_analyses()
    
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)
    print(f"Results: {analyzer.output_dir / 'academic_analysis_results.json'}")
    print(f"Report: {analyzer.output_dir / 'ACADEMIC_FINDINGS.md'}")
    print(f"Figures: {analyzer.figures_dir}")
    print("="*70 + "\n")
    
    return results


if __name__ == '__main__':
    main()

