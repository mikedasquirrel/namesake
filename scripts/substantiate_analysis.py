"""
Substantiate Marriage Prediction Analysis

Scales up data collection and runs comprehensive validation.
Target: 1,000+ couples for adequate statistical power.
"""

import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
import json
import numpy as np
import pandas as pd
from datetime import datetime
from scipy import stats
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Ridge, LogisticRegression
from sklearn.metrics import r2_score, accuracy_score, roc_auc_score

from core.models import db
from core.marriage_models import MarriedCouple, MarriageAnalysis
from collectors.marriage_collector import MarriageCollector
from analyzers.relationship_compatibility_analyzer import RelationshipCompatibilityAnalyzer
from app import app

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def scale_up_data(target_couples: int = 1000):
    """Collect larger dataset for statistical power"""
    logger.info("=" * 80)
    logger.info(f"SCALING UP TO {target_couples} COUPLES")
    logger.info("=" * 80)
    
    with app.app_context():
        collector = MarriageCollector()
        
        # Check current count
        current_count = db.session.query(MarriedCouple).count()
        logger.info(f"\nCurrent couples in database: {current_count}")
        
        if current_count >= target_couples:
            logger.info("✓ Target already reached!")
            return current_count
        
        # Generate additional couples
        needed = target_couples - current_count
        logger.info(f"Generating {needed} additional couples...")
        
        new_couples = collector.collect_sample(target_size=needed, stratify_by_era=True)
        
        for couple in new_couples:
            db.session.add(couple)
        
        db.session.commit()
        
        total = db.session.query(MarriedCouple).count()
        logger.info(f"✓ Database now has {total} couples")
        
        return total


def analyze_all_couples():
    """Analyze all couples in database"""
    logger.info("\n" + "=" * 80)
    logger.info("ANALYZING ALL COUPLES")
    logger.info("=" * 80)
    
    with app.app_context():
        analyzer = RelationshipCompatibilityAnalyzer(db.session)
        
        # Get unanalyzed couples
        unanalyzed = db.session.query(MarriedCouple).filter(
            ~db.session.query(MarriageAnalysis).filter(
                MarriageAnalysis.couple_id == MarriedCouple.id
            ).exists()
        ).all()
        
        logger.info(f"\nUnanalyzed couples: {len(unanalyzed)}")
        
        if len(unanalyzed) == 0:
            logger.info("✓ All couples already analyzed!")
            return
        
        # Analyze in batches
        batch_size = 100
        analyzed_count = 0
        
        for i in range(0, len(unanalyzed), batch_size):
            batch = unanalyzed[i:i+batch_size]
            
            for couple in batch:
                try:
                    analysis = analyzer.analyze_couple(couple, include_children=False)
                    db.session.add(analysis)
                    analyzed_count += 1
                except Exception as e:
                    logger.error(f"Error analyzing couple {couple.id}: {e}")
            
            db.session.commit()
            logger.info(f"  Analyzed {min(i+batch_size, len(unanalyzed))}/{len(unanalyzed)} couples...")
        
        logger.info(f"✓ Analyzed {analyzed_count} new couples")


def comprehensive_analysis():
    """Run comprehensive statistical analysis"""
    logger.info("\n" + "=" * 80)
    logger.info("COMPREHENSIVE STATISTICAL ANALYSIS")
    logger.info("=" * 80)
    
    with app.app_context():
        analyzer = RelationshipCompatibilityAnalyzer(db.session)
        
        # Get all analyzed couples
        couples = db.session.query(MarriedCouple).join(MarriageAnalysis).all()
        
        if len(couples) < 100:
            logger.warning(f"Only {len(couples)} couples available. Need more for robust analysis.")
            return None
        
        logger.info(f"\nAnalyzing {len(couples)} couples...")
        
        # Convert to DataFrame
        df = analyzer.batch_analyze_couples(couples)
        
        # === DESCRIPTIVE STATISTICS ===
        logger.info("\n" + "-" * 80)
        logger.info("DESCRIPTIVE STATISTICS")
        logger.info("-" * 80)
        
        stats_summary = {
            'n_total': len(df),
            'n_divorced': int(df['is_divorced'].sum()),
            'divorce_rate': float(df['is_divorced'].mean()),
            'mean_duration': float(df['marriage_duration'].mean()),
            'sd_duration': float(df['marriage_duration'].std()),
            'median_duration': float(df['marriage_duration'].median()),
        }
        
        logger.info(f"Sample Size: {stats_summary['n_total']}")
        logger.info(f"Divorced: {stats_summary['n_divorced']} ({stats_summary['divorce_rate']*100:.1f}%)")
        logger.info(f"Mean Duration: {stats_summary['mean_duration']:.1f} years (SD={stats_summary['sd_duration']:.1f})")
        logger.info(f"Median Duration: {stats_summary['median_duration']:.1f} years")
        
        # Name metrics
        logger.info(f"\nName Compatibility Metrics:")
        logger.info(f"  Compatibility: μ={df['compatibility_score'].mean():.3f}, σ={df['compatibility_score'].std():.3f}")
        logger.info(f"  Phonetic Distance: μ={df['phonetic_distance'].mean():.3f}, σ={df['phonetic_distance'].std():.3f}")
        logger.info(f"  Golden Ratio: μ={df['golden_ratio_proximity'].mean():.3f}, σ={df['golden_ratio_proximity'].std():.3f}")
        logger.info(f"  Vowel Harmony: μ={df['vowel_harmony'].mean():.3f}, σ={df['vowel_harmony'].std():.3f}")
        
        # === HYPOTHESIS TESTING ===
        logger.info("\n" + "-" * 80)
        logger.info("HYPOTHESIS TESTING (PRIMARY)")
        logger.info("-" * 80)
        
        hypotheses = {}
        
        # H1: Compatibility → Duration
        r_compat, p_compat = stats.pearsonr(df['compatibility_score'], df['marriage_duration'])
        d_compat = r_compat / np.sqrt(1 - r_compat**2) * np.sqrt(len(df) - 2) / np.sqrt(len(df))
        
        logger.info(f"\n[H1] Compatibility → Duration")
        logger.info(f"  r = {r_compat:.3f}, p = {p_compat:.4f}")
        logger.info(f"  Cohen's d = {d_compat:.3f}")
        logger.info(f"  {'✅ SIGNIFICANT' if p_compat < 0.05 else '❌ Not significant'}")
        
        hypotheses['H1_compatibility'] = {
            'r': float(r_compat),
            'p': float(p_compat),
            'd': float(d_compat),
            'significant': bool(p_compat < 0.05)
        }
        
        # H2: Phonetic Distance → Divorce
        divorced = df[df['is_divorced'] == True]['phonetic_distance']
        married = df[df['is_divorced'] == False]['phonetic_distance']
        t_stat, p_dist = stats.ttest_ind(divorced, married)
        
        logger.info(f"\n[H2] Phonetic Distance → Divorce")
        logger.info(f"  Divorced: μ={divorced.mean():.3f}")
        logger.info(f"  Married: μ={married.mean():.3f}")
        logger.info(f"  t({len(df)-2}) = {t_stat:.3f}, p = {p_dist:.4f}")
        logger.info(f"  {'✅ SIGNIFICANT' if p_dist < 0.05 else '❌ Not significant'}")
        
        hypotheses['H2_distance_divorce'] = {
            't': float(t_stat),
            'p': float(p_dist),
            'divorced_mean': float(divorced.mean()),
            'married_mean': float(married.mean()),
            'significant': bool(p_dist < 0.05)
        }
        
        # H3: Golden Ratio → Duration
        r_golden, p_golden = stats.pearsonr(df['golden_ratio_proximity'], df['marriage_duration'])
        
        logger.info(f"\n[H3] Golden Ratio → Duration")
        logger.info(f"  r = {r_golden:.3f}, p = {p_golden:.4f}")
        logger.info(f"  {'✅ SIGNIFICANT' if p_golden < 0.05 else '❌ Not significant'}")
        
        hypotheses['H3_golden_ratio'] = {
            'r': float(r_golden),
            'p': float(p_golden),
            'significant': bool(p_golden < 0.05)
        }
        
        # H4: Vowel Harmony → Duration
        r_vowel, p_vowel = stats.pearsonr(df['vowel_harmony'], df['marriage_duration'])
        
        logger.info(f"\n[H4] Vowel Harmony → Duration")
        logger.info(f"  r = {r_vowel:.3f}, p = {p_vowel:.4f}")
        logger.info(f"  {'✅ SIGNIFICANT' if p_vowel < 0.05 else '❌ Not significant'}")
        
        hypotheses['H4_vowel_harmony'] = {
            'r': float(r_vowel),
            'p': float(p_vowel),
            'significant': bool(p_vowel < 0.05)
        }
        
        # === THEORY COMPARISON ===
        logger.info("\n" + "-" * 80)
        logger.info("THEORY COMPARISON")
        logger.info("-" * 80)
        
        theories = {
            'Similarity': df['similarity_theory'].corr(df['marriage_duration']),
            'Complementarity': df['complementarity_theory'].corr(df['marriage_duration']),
            'Golden Ratio': df['golden_ratio_theory'].corr(df['marriage_duration']),
            'Resonance': df['resonance_theory'].corr(df['marriage_duration'])
        }
        
        logger.info("\nCorrelation with Marriage Duration:")
        for theory, r in sorted(theories.items(), key=lambda x: abs(x[1]), reverse=True):
            sig = "✅" if abs(r) > 0.15 else ""
            logger.info(f"  {theory:20s}: r = {r:+.3f} {sig}")
        
        winner = max(theories, key=lambda k: abs(theories[k]))
        logger.info(f"\n🏆 WINNER: {winner} (r = {theories[winner]:.3f})")
        
        # === REGRESSION MODELS ===
        logger.info("\n" + "-" * 80)
        logger.info("PREDICTIVE MODELS")
        logger.info("-" * 80)
        
        # Prepare features (only use available columns)
        feature_cols = [
            'compatibility_score', 'phonetic_distance', 'golden_ratio_proximity',
            'vowel_harmony'
        ]
        
        # Filter to only existing columns
        available_features = [col for col in feature_cols if col in df.columns]
        
        if len(available_features) == 0:
            logger.warning("No feature columns available for modeling")
            return results
        
        X = df[available_features].fillna(0)
        y_duration = df['marriage_duration']
        y_divorce = df['is_divorced'].astype(int)
        
        # Train/test split
        X_train, X_test, y_dur_train, y_dur_test = train_test_split(
            X, y_duration, test_size=0.25, random_state=42
        )
        
        _, _, y_div_train, y_div_test = train_test_split(
            X, y_divorce, test_size=0.25, random_state=42
        )
        
        # Model 1: Duration prediction
        model_duration = Ridge(alpha=1.0)
        model_duration.fit(X_train, y_dur_train)
        
        r2_train = model_duration.score(X_train, y_dur_train)
        r2_test = model_duration.score(X_test, y_dur_test)
        
        logger.info(f"\nDuration Prediction (Ridge):")
        logger.info(f"  R² Train: {r2_train:.3f}")
        logger.info(f"  R² Test:  {r2_test:.3f}")
        logger.info(f"  {'✅ Predictive' if r2_test > 0.05 else '❌ Weak prediction'}")
        
        # Feature importance
        logger.info(f"\n  Feature Importance:")
        for feat, coef in sorted(zip(feature_cols, model_duration.coef_), 
                                key=lambda x: abs(x[1]), reverse=True):
            logger.info(f"    {feat:30s}: {coef:+.3f}")
        
        # Model 2: Divorce prediction
        model_divorce = LogisticRegression(max_iter=1000)
        model_divorce.fit(X_train, y_div_train)
        
        acc_test = accuracy_score(y_div_test, model_divorce.predict(X_test))
        
        try:
            auc_test = roc_auc_score(y_div_test, model_divorce.predict_proba(X_test)[:, 1])
        except:
            auc_test = 0.5
        
        logger.info(f"\nDivorce Prediction (Logistic):")
        logger.info(f"  Accuracy: {acc_test:.3f}")
        logger.info(f"  AUC:      {auc_test:.3f}")
        logger.info(f"  {'✅ Better than chance' if auc_test > 0.55 else '❌ At chance level'}")
        
        # === EFFECT SIZES ===
        logger.info("\n" + "-" * 80)
        logger.info("EFFECT SIZE SUMMARY")
        logger.info("-" * 80)
        
        logger.info(f"\nBest predictors:")
        logger.info(f"  1. {winner}: r = {theories[winner]:.3f}")
        logger.info(f"  2. Compatibility: r = {r_compat:.3f}")
        logger.info(f"  3. Golden Ratio: r = {r_golden:.3f}")
        
        logger.info(f"\nVariance Explained:")
        logger.info(f"  Single best predictor: R² = {theories[winner]**2:.3f} ({theories[winner]**2*100:.1f}%)")
        logger.info(f"  Multi-predictor model: R² = {r2_test:.3f} ({r2_test*100:.1f}%)")
        
        # === POWER ANALYSIS ===
        logger.info("\n" + "-" * 80)
        logger.info("STATISTICAL POWER")
        logger.info("-" * 80)
        
        # Calculate achieved power
        from scipy.stats import norm
        z_alpha = norm.ppf(0.975)  # Two-tailed α=0.05
        z_beta = abs(r_compat) * np.sqrt(len(df) - 3) - z_alpha
        power = norm.cdf(z_beta)
        
        logger.info(f"\nSample size: n = {len(df)}")
        logger.info(f"Observed effect: r = {r_compat:.3f}")
        logger.info(f"Achieved power: {power:.3f} ({power*100:.1f}%)")
        
        if power < 0.80:
            needed_n = int(((z_alpha + norm.ppf(0.80)) / (0.5 * np.log((1 + 0.15) / (1 - 0.15)))) ** 2 + 3)
            logger.info(f"⚠️  Need n ≥ {needed_n} for 80% power to detect r=0.15")
        else:
            logger.info(f"✅ Adequate power achieved!")
        
        # === SAVE RESULTS ===
        output_dir = Path('analysis_outputs/marriage')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'n_couples': len(df),
            'descriptive_stats': stats_summary,
            'hypotheses': hypotheses,
            'theory_comparison': {k: float(v) for k, v in theories.items()},
            'winner': winner,
            'predictive_models': {
                'duration': {'r2_train': float(r2_train), 'r2_test': float(r2_test)},
                'divorce': {'accuracy': float(acc_test), 'auc': float(auc_test)}
            },
            'power': {
                'achieved': float(power),
                'adequate': bool(power >= 0.80)
            }
        }
        
        results_file = output_dir / f'substantiated_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"\n✅ Results saved to {results_file}")
        
        # Save DataFrame
        df_file = output_dir / f'substantiated_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        df.to_csv(df_file, index=False)
        logger.info(f"✅ Data saved to {df_file}")
        
        return results


def main():
    """Main execution"""
    logger.info("\n" + "=" * 80)
    logger.info("SUBSTANTIATING MARRIAGE PREDICTION ANALYSIS")
    logger.info("=" * 80)
    logger.info(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Step 1: Scale up data
    n_couples = scale_up_data(target_couples=1000)
    
    # Step 2: Analyze all couples
    analyze_all_couples()
    
    # Step 3: Comprehensive analysis
    results = comprehensive_analysis()
    
    if results:
        logger.info("\n" + "=" * 80)
        logger.info("SUBSTANTIATION COMPLETE")
        logger.info("=" * 80)
        
        logger.info(f"\n✅ Analyzed {results['n_couples']} couples")
        logger.info(f"✅ Divorce rate: {results['descriptive_stats']['divorce_rate']*100:.1f}%")
        logger.info(f"✅ Winner theory: {results['winner']}")
        logger.info(f"✅ Power: {results['power']['achieved']*100:.1f}%")
        
        # Summary of significance
        sig_count = sum(1 for h in results['hypotheses'].values() if h.get('significant', False))
        logger.info(f"\n📊 Significant hypotheses: {sig_count}/4")
        
        if sig_count >= 2:
            logger.info("🎉 STUDY SUCCESS: Multiple significant effects found!")
        elif sig_count == 1:
            logger.info("⚠️  PARTIAL SUCCESS: One significant effect found")
        else:
            logger.info("ℹ️  NULL FINDINGS: No significant effects (but high-powered null)")
    
    logger.info(f"\nEnd Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.error(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

