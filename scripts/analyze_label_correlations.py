"""
Label Nominative Correlation Analysis
Test hypotheses about label nominative effects on outcomes

Purpose: Validate label nominative framework with statistical analysis
Expected Findings: 20-40 significant correlations across teams, venues, ensembles
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from core.models import (LabelNominativeProfile, TeamProfile, VenueProfile,
                          LabelCorrelationAnalysis, NFLPlayer, NBAPlayer, MLBPlayer)
import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import pearsonr, spearmanr
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def analyze_team_harshness_home_advantage():
    """
    Hypothesis: Harsh team names correlate with home field advantage
    Expected: r=0.15-0.25, p<0.05
    """
    logger.info("\n" + "="*80)
    logger.info("ANALYSIS 1: Team Harshness → Home Field Advantage")
    logger.info("="*80)
    
    teams = TeamProfile.query.join(LabelNominativeProfile).all()
    
    data = []
    for team in teams:
        if team.label_profile and team.home_advantage_score:
            data.append({
                'team_name': team.team_full_name,
                'sport': team.sport,
                'harshness': team.label_profile.harshness,
                'home_advantage': team.home_advantage_score,
                'team_aggression': team.team_aggression_score
            })
    
    if len(data) < 10:
        logger.warning(f"⚠️  Insufficient data: {len(data)} teams with home advantage scores")
        logger.info("    Run populate scripts and add home advantage data to analyze")
        return None
    
    df = pd.DataFrame(data)
    
    # Correlation: Team harshness vs home advantage
    r, p = pearsonr(df['harshness'], df['home_advantage'])
    
    logger.info(f"\nSample size: n={len(df)}")
    logger.info(f"Correlation: r={r:.3f}, p={p:.4f}")
    
    if p < 0.05:
        logger.info(f"✅ SIGNIFICANT! Harsh team names predict home advantage")
        interpretation = f"Harsh team names correlate with {r:.1%} stronger home advantage (p={p:.4f})"
    else:
        logger.info(f"❌ Not significant (p={p:.4f})")
        interpretation = f"No significant correlation found (r={r:.3f}, p={p:.4f})"
    
    # Effect size (Cohen's d)
    median_harsh = df['harshness'].median()
    harsh_teams = df[df['harshness'] > median_harsh]['home_advantage']
    soft_teams = df[df['harshness'] <= median_harsh]['home_advantage']
    
    if len(harsh_teams) > 0 and len(soft_teams) > 0:
        cohens_d = (harsh_teams.mean() - soft_teams.mean()) / df['home_advantage'].std()
        logger.info(f"Effect size (Cohen's d): {cohens_d:.3f}")
    else:
        cohens_d = 0
    
    # Save to database
    analysis = LabelCorrelationAnalysis(
        label_type='team',
        feature_name='harshness',
        outcome_variable='home_advantage',
        correlation_coefficient=r,
        p_value=p,
        sample_size=len(df),
        effect_size=cohens_d,
        is_significant=(p < 0.05),
        interpretation=interpretation
    )
    db.session.add(analysis)
    db.session.commit()
    
    return {'r': r, 'p': p, 'n': len(df), 'd': cohens_d}


def analyze_venue_intimidation_visitor_performance():
    """
    Hypothesis: Intimidating venue names correlate with visiting team underperformance
    Expected: r=0.10-0.20, p<0.05
    """
    logger.info("\n" + "="*80)
    logger.info("ANALYSIS 2: Venue Intimidation → Visitor Performance")
    logger.info("="*80)
    
    venues = VenueProfile.query.join(LabelNominativeProfile).all()
    
    data = []
    for venue in venues:
        if venue.label_profile and venue.home_team_win_pct:
            data.append({
                'venue_name': venue.venue_name,
                'sport': venue.sport,
                'intimidation': venue.venue_intimidation,
                'home_win_pct': venue.home_team_win_pct,
                'venue_prestige': venue.venue_prestige
            })
    
    if len(data) < 10:
        logger.warning(f"⚠️  Insufficient data: {len(data)} venues with performance data")
        logger.info("    Add venue performance data to analyze")
        return None
    
    df = pd.DataFrame(data)
    
    # Correlation: Venue intimidation vs home win %
    r, p = pearsonr(df['intimidation'], df['home_win_pct'])
    
    logger.info(f"\nSample size: n={len(df)}")
    logger.info(f"Correlation: r={r:.3f}, p={p:.4f}")
    
    if p < 0.05:
        logger.info(f"✅ SIGNIFICANT! Intimidating venues predict home wins")
        interpretation = f"Intimidating venue names correlate with {r:.1%} higher home win rate (p={p:.4f})"
    else:
        logger.info(f"❌ Not significant (p={p:.4f})")
        interpretation = f"No significant correlation found (r={r:.3f}, p={p:.4f})"
    
    # Effect size
    median_intim = df['intimidation'].median()
    harsh_venues = df[df['intimidation'] > median_intim]['home_win_pct']
    soft_venues = df[df['intimidation'] <= median_intim]['home_win_pct']
    
    if len(harsh_venues) > 0 and len(soft_venues) > 0:
        cohens_d = (harsh_venues.mean() - soft_venues.mean()) / df['home_win_pct'].std()
        logger.info(f"Effect size (Cohen's d): {cohens_d:.3f}")
    else:
        cohens_d = 0
    
    # Save
    analysis = LabelCorrelationAnalysis(
        label_type='venue',
        feature_name='intimidation',
        outcome_variable='home_win_pct',
        correlation_coefficient=r,
        p_value=p,
        sample_size=len(df),
        effect_size=cohens_d,
        is_significant=(p < 0.05),
        interpretation=interpretation
    )
    db.session.add(analysis)
    db.session.commit()
    
    return {'r': r, 'p': p, 'n': len(df), 'd': cohens_d}


def analyze_team_memorability_media_coverage():
    """
    Hypothesis: Memorable team names get more media coverage
    Expected: r=0.20-0.30, p<0.01
    """
    logger.info("\n" + "="*80)
    logger.info("ANALYSIS 3: Team Memorability → Media Coverage")
    logger.info("="*80)
    
    teams = TeamProfile.query.join(LabelNominativeProfile).all()
    
    data = []
    for team in teams:
        if team.label_profile:
            # Note: Would need actual media coverage data
            # For now, use market size as proxy
            market_score = {'large': 90, 'medium': 60, 'small': 40}.get(team.market_size, 50)
            
            data.append({
                'team_name': team.team_full_name,
                'memorability': team.label_profile.memorability,
                'market_proxy': market_score
            })
    
    if len(data) < 10:
        logger.warning(f"⚠️  Insufficient data: {len(data)} teams")
        return None
    
    df = pd.DataFrame(data)
    
    r, p = pearsonr(df['memorability'], df['market_proxy'])
    
    logger.info(f"\nSample size: n={len(df)}")
    logger.info(f"Correlation: r={r:.3f}, p={p:.4f}")
    logger.info("    Note: Using market size as media coverage proxy")
    
    interpretation = f"Team memorability correlation with market presence: r={r:.3f}, p={p:.4f}"
    
    analysis = LabelCorrelationAnalysis(
        label_type='team',
        feature_name='memorability',
        outcome_variable='media_coverage_proxy',
        correlation_coefficient=r,
        p_value=p,
        sample_size=len(df),
        is_significant=(p < 0.05),
        interpretation=interpretation
    )
    db.session.add(analysis)
    db.session.commit()
    
    return {'r': r, 'p': p, 'n': len(df)}


def analyze_label_phonetic_patterns():
    """
    Exploratory: Analyze phonetic patterns across label types
    """
    logger.info("\n" + "="*80)
    logger.info("ANALYSIS 4: Label Phonetic Pattern Summary")
    logger.info("="*80)
    
    # Get all labels by type
    label_types = ['team', 'venue', 'prop', 'play']
    
    summary = []
    for label_type in label_types:
        labels = LabelNominativeProfile.query.filter_by(
            label_type=label_type,
            domain='sports'
        ).all()
        
        if len(labels) > 0:
            harshness_vals = [l.harshness for l in labels if l.harshness]
            memorability_vals = [l.memorability for l in labels if l.memorability]
            power_phoneme_vals = [l.power_phoneme_count for l in labels if l.power_phoneme_count]
            
            summary.append({
                'label_type': label_type,
                'count': len(labels),
                'mean_harshness': np.mean(harshness_vals) if harshness_vals else 0,
                'std_harshness': np.std(harshness_vals) if harshness_vals else 0,
                'mean_memorability': np.mean(memorability_vals) if memorability_vals else 0,
                'mean_power_phonemes': np.mean(power_phoneme_vals) if power_phoneme_vals else 0
            })
    
    logger.info("\nLabel Type Phonetic Profiles:")
    logger.info(f"{'Type':<15} {'Count':<10} {'Harshness':<15} {'Memorability':<15} {'Power Phonemes':<15}")
    logger.info("-" * 70)
    
    for s in summary:
        logger.info(
            f"{s['label_type']:<15} "
            f"{s['count']:<10} "
            f"{s['mean_harshness']:<15.1f} "
            f"{s['mean_memorability']:<15.1f} "
            f"{s['mean_power_phonemes']:<15.1f}"
        )
    
    return summary


def main():
    """Main analysis execution"""
    with app.app_context():
        logger.info("="*80)
        logger.info("LABEL NOMINATIVE CORRELATION ANALYSIS")
        logger.info("="*80)
        logger.info("\nTesting key hypotheses about label nominative effects\n")
        
        results = {}
        
        try:
            # Analysis 1: Team harshness → Home advantage
            results['team_harshness'] = analyze_team_harshness_home_advantage()
            
            # Analysis 2: Venue intimidation → Visitor performance
            results['venue_intimidation'] = analyze_venue_intimidation_visitor_performance()
            
            # Analysis 3: Team memorability → Media coverage
            results['team_memorability'] = analyze_team_memorability_media_coverage()
            
            # Analysis 4: Phonetic patterns
            results['phonetic_patterns'] = analyze_label_phonetic_patterns()
            
            # Summary
            logger.info("\n" + "="*80)
            logger.info("ANALYSIS COMPLETE - SUMMARY")
            logger.info("="*80)
            
            saved_analyses = LabelCorrelationAnalysis.query.all()
            logger.info(f"\nTotal analyses saved: {len(saved_analyses)}")
            
            significant = [a for a in saved_analyses if a.is_significant]
            logger.info(f"Significant findings: {len(significant)}")
            
            if significant:
                logger.info("\n✅ Significant Correlations Found:")
                for analysis in significant:
                    logger.info(f"  • {analysis.label_type} {analysis.feature_name} → {analysis.outcome_variable}")
                    logger.info(f"    r={analysis.correlation_coefficient:.3f}, p={analysis.p_value:.4f}, n={analysis.sample_size}")
            
            logger.info("\n" + "="*80)
            logger.info("NEXT STEPS:")
            logger.info("="*80)
            logger.info("1. Add actual performance data (home advantage, visitor stats)")
            logger.info("2. Collect more teams/venues for larger sample sizes")
            logger.info("3. Run ensemble interaction analysis (next script)")
            logger.info("4. Integrate significant findings into prediction formula\n")
            
        except Exception as e:
            logger.error(f"❌ Error during analysis: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            raise


if __name__ == "__main__":
    main()

