"""Quasi-Experimental Analysis: 1979 Gender Policy Change

Natural experiment: WMO changed hurricane naming from all-female to alternating
male/female in 1979. If Jung et al. (2014) finding is real (female names → more deaths),
we should see discontinuity at 1979.

Tests:
1. Regression discontinuity: casualties ~ year (looking for break at 1979)
2. Pre/post comparison: mean casualties pre-1979 vs. post-1979
3. Interaction term: gender × post1979 indicator
"""

import logging
import sys
import os
from pathlib import Path
import json
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
from core.config import Config
from core.models import db, Hurricane, HurricaneAnalysis
from scipy import stats
import statsmodels.api as sm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_1979_analysis():
    """Run quasi-experimental analysis around 1979 policy change."""
    
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        logger.info("Running 1979 gender policy change analysis...")
        
        # Load data
        df = load_hurricane_data()
        
        if df.empty:
            logger.error("No hurricane data available")
            return
        
        logger.info(f"Loaded {len(df)} hurricanes from {df['year'].min()} to {df['year'].max()}")
        
        results = {
            'descriptive_stats': get_descriptive_stats(df),
            'regression_discontinuity': run_regression_discontinuity(df),
            'pre_post_comparison': run_pre_post_comparison(df),
            'interaction_test': run_interaction_test(df),
            'jung_replication': replicate_jung_et_al(df)
        }
        
        # Save results
        output_dir = Path(__file__).parent.parent / 'analysis_outputs' / 'quasi_experimental'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / 'gender_1979_analysis.json'
        with output_file.open('w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"\n{'='*60}")
        logger.info("✅ 1979 ANALYSIS COMPLETE")
        logger.info(f"{'='*60}")
        logger.info(f"Results saved to: {output_file}")
        
        # Print summary
        print_analysis_summary(results)
        
        return results


def load_hurricane_data():
    """Load hurricane data with name analysis."""
    query = db.session.query(Hurricane, HurricaneAnalysis).join(
        HurricaneAnalysis, Hurricane.id == HurricaneAnalysis.hurricane_id
    ).filter(Hurricane.year >= 1950)  # Start at 1950 for data quality
    
    rows = []
    for hurricane, analysis in query.all():
        rows.append({
            'name': hurricane.name,
            'year': hurricane.year,
            'deaths': hurricane.deaths or 0,
            'deaths_direct': hurricane.deaths_direct or 0,
            'deaths_indirect': hurricane.deaths_indirect or 0,
            'damage_usd': hurricane.damage_usd or 0,
            'category': hurricane.saffir_simpson_category or 0,
            'max_wind_mph': hurricane.max_wind_mph,
            'gender_coded': analysis.gender_coded,
            'phonetic_harshness': analysis.phonetic_harshness_score,
            'memorability': analysis.memorability_score,
            'post_1979': int(hurricane.year >= 1979),
            'gender_male': int(analysis.gender_coded == 'male') if analysis.gender_coded else 0,
            'gender_female': int(analysis.gender_coded == 'female') if analysis.gender_coded else 0,
        })
    
    return pd.DataFrame(rows)


def get_descriptive_stats(df):
    """Get descriptive statistics by era and gender."""
    stats = {}
    
    # Pre-1979 (all female)
    pre_1979 = df[df['year'] < 1979]
    stats['pre_1979'] = {
        'n_storms': len(pre_1979),
        'mean_deaths': float(pre_1979['deaths'].mean()),
        'median_deaths': float(pre_1979['deaths'].median()),
        'total_deaths': int(pre_1979['deaths'].sum()),
        'storms_with_casualties': int((pre_1979['deaths'] > 0).sum())
    }
    
    # Post-1979 (alternating)
    post_1979 = df[df['year'] >= 1979]
    stats['post_1979'] = {
        'n_storms': len(post_1979),
        'mean_deaths': float(post_1979['deaths'].mean()),
        'median_deaths': float(post_1979['deaths'].median()),
        'total_deaths': int(post_1979['deaths'].sum()),
        'storms_with_casualties': int((post_1979['deaths'] > 0).sum()),
        'n_male': int(post_1979['gender_male'].sum()),
        'n_female': int(post_1979['gender_female'].sum())
    }
    
    # Post-1979: Male vs. Female
    post_male = post_1979[post_1979['gender_male'] == 1]
    post_female = post_1979[post_1979['gender_female'] == 1]
    
    stats['post_1979_male'] = {
        'n_storms': len(post_male),
        'mean_deaths': float(post_male['deaths'].mean()) if len(post_male) > 0 else 0,
        'median_deaths': float(post_male['deaths'].median()) if len(post_male) > 0 else 0
    }
    
    stats['post_1979_female'] = {
        'n_storms': len(post_female),
        'mean_deaths': float(post_female['deaths'].mean()) if len(post_female) > 0 else 0,
        'median_deaths': float(post_female['deaths'].median()) if len(post_female) > 0 else 0
    }
    
    return stats


def run_regression_discontinuity(df):
    """Test for discontinuity in casualties at 1979."""
    # Simple regression discontinuity design
    # Model: deaths ~ year + post_1979_indicator + year×post_1979
    
    df_rd = df.copy()
    df_rd['year_centered'] = df_rd['year'] - 1979
    df_rd['log_deaths'] = np.log1p(df_rd['deaths'])
    
    # Drop rows without category data
    df_rd = df_rd[df_rd['category'] > 0].copy()
    
    X = sm.add_constant(df_rd[['year_centered', 'post_1979', 'category', 'max_wind_mph']])
    y = df_rd['log_deaths']
    
    try:
        model = sm.OLS(y, X, missing='drop').fit()
        
        return {
            'r_squared': float(model.rsquared),
            'post_1979_coef': float(model.params.get('post_1979', 0)),
            'post_1979_pvalue': float(model.pvalues.get('post_1979', 1)),
            'interpretation': 'Significant jump at 1979' if model.pvalues.get('post_1979', 1) < 0.05 else 'No discontinuity detected'
        }
    except Exception as e:
        logger.error(f"RD analysis failed: {e}")
        return {'error': str(e)}


def run_pre_post_comparison(df):
    """Simple pre/post-1979 comparison with t-test."""
    pre = df[df['year'] < 1979]['deaths']
    post = df[df['year'] >= 1979]['deaths']
    
    # T-test
    t_stat, p_value = stats.ttest_ind(pre, post, equal_var=False)
    
    # Mann-Whitney U (non-parametric, more robust for skewed data)
    u_stat, u_p_value = stats.mannwhitneyu(pre, post, alternative='two-sided')
    
    return {
        't_test': {
            't_statistic': float(t_stat),
            'p_value': float(p_value),
            'significant': p_value < 0.05
        },
        'mann_whitney': {
            'u_statistic': float(u_stat),
            'p_value': float(u_p_value),
            'significant': u_p_value < 0.05
        },
        'effect_size': {
            'pre_mean': float(pre.mean()),
            'post_mean': float(post.mean()),
            'difference': float(post.mean() - pre.mean()),
            'percent_change': float((post.mean() - pre.mean()) / pre.mean() * 100) if pre.mean() > 0 else None
        }
    }


def run_interaction_test(df):
    """Test gender × post_1979 interaction (Jung et al. claim)."""
    # Only post-1979 data (when we have gender variation)
    df_post = df[df['year'] >= 1979].copy()
    df_post = df_post[df_post['category'] > 0].copy()  # Drop storms without category
    
    # Create interaction term
    df_post['gender_male_x_year'] = df_post['gender_male'] * (df_post['year'] - 1979)
    df_post['log_deaths'] = np.log1p(df_post['deaths'])
    
    X = sm.add_constant(df_post[[
        'gender_male', 
        'category', 
        'max_wind_mph',
        'year'
    ]])
    y = df_post['log_deaths']
    
    try:
        model = sm.OLS(y, X, missing='drop').fit()
        
        return {
            'r_squared': float(model.rsquared),
            'gender_male_coef': float(model.params.get('gender_male', 0)),
            'gender_male_pvalue': float(model.pvalues.get('gender_male', 1)),
            'interpretation': 'Male names DECREASE deaths' if model.params.get('gender_male', 0) < 0 and model.pvalues.get('gender_male', 1) < 0.05 
                             else 'Male names INCREASE deaths' if model.params.get('gender_male', 0) > 0 and model.pvalues.get('gender_male', 1) < 0.05
                             else 'No significant gender effect',
            'jung_et_al_compatible': model.params.get('gender_male', 0) < 0  # Jung found female (not male) increased deaths
        }
    except Exception as e:
        logger.error(f"Interaction test failed: {e}")
        return {'error': str(e)}


def replicate_jung_et_al(df):
    """Attempt to replicate Jung et al. (2014) finding."""
    # Jung et al. claimed: controlling for damage, female names → more deaths
    # Our test: does gender predict deaths after controlling for intensity?
    
    df_rep = df[(df['year'] >= 1979) & (df['category'] > 0)].copy()
    df_rep['log_deaths'] = np.log1p(df_rep['deaths'])
    df_rep['log_damage'] = np.log1p(df_rep['damage_usd'])
    
    X = sm.add_constant(df_rep[[
        'gender_female',  # Jung et al. used gender as female=1
        'category',
        'max_wind_mph',
        'log_damage'
    ]])
    y = df_rep['log_deaths']
    
    try:
        model = sm.OLS(y, X, missing='drop').fit()
        
        female_coef = model.params.get('gender_female', 0)
        female_p = model.pvalues.get('gender_female', 1)
        
        return {
            'r_squared': float(model.rsquared),
            'female_coef': float(female_coef),
            'female_pvalue': float(female_p),
            'sample_size': int(model.nobs),
            'replicates_jung': (female_coef > 0 and female_p < 0.05),
            'interpretation': 'Female names predict MORE deaths (supports Jung)' if (female_coef > 0 and female_p < 0.05)
                             else 'Female names predict FEWER deaths (contradicts Jung)' if (female_coef < 0 and female_p < 0.05)
                             else 'No significant gender effect (Jung does not replicate)'
        }
    except Exception as e:
        logger.error(f"Jung replication failed: {e}")
        return {'error': str(e)}


def print_analysis_summary(results):
    """Print summary of quasi-experimental findings."""
    print("\n" + "="*60)
    print("1979 GENDER POLICY CHANGE ANALYSIS")
    print("="*60)
    
    desc = results.get('descriptive_stats', {})
    print("\nDESCRIPTIVE STATISTICS:")
    print(f"  Pre-1979 (all female): {desc.get('pre_1979', {}).get('n_storms', 0)} storms, "
          f"{desc.get('pre_1979', {}).get('mean_deaths', 0):.1f} mean deaths")
    print(f"  Post-1979 (alternating): {desc.get('post_1979', {}).get('n_storms', 0)} storms, "
          f"{desc.get('post_1979', {}).get('mean_deaths', 0):.1f} mean deaths")
    
    post_male = desc.get('post_1979_male', {})
    post_female = desc.get('post_1979_female', {})
    print(f"    Male names: {post_male.get('n_storms', 0)} storms, {post_male.get('mean_deaths', 0):.1f} mean deaths")
    print(f"    Female names: {post_female.get('n_storms', 0)} storms, {post_female.get('mean_deaths', 0):.1f} mean deaths")
    
    print("\nREGRESSION DISCONTINUITY:")
    rd = results.get('regression_discontinuity', {})
    print(f"  {rd.get('interpretation', 'N/A')}")
    print(f"  Post-1979 coefficient: {rd.get('post_1979_coef', 0):.3f} (p={rd.get('post_1979_pvalue', 1):.3f})")
    
    print("\nPRE/POST COMPARISON:")
    comp = results.get('pre_post_comparison', {})
    effect = comp.get('effect_size', {})
    print(f"  Change: {effect.get('difference', 0):.1f} deaths ({effect.get('percent_change', 0):.1f}%)")
    print(f"  T-test p-value: {comp.get('t_test', {}).get('p_value', 1):.3f}")
    
    print("\nJUNG ET AL. (2014) REPLICATION:")
    jung = results.get('jung_replication', {})
    print(f"  {jung.get('interpretation', 'N/A')}")
    print(f"  Female coefficient: {jung.get('female_coef', 0):.3f} (p={jung.get('female_pvalue', 1):.3f})")
    print(f"  Replicates Jung finding: {jung.get('replicates_jung', False)}")


if __name__ == '__main__':
    run_1979_analysis()

