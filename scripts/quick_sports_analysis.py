"""
Quick Sports Analysis
Runs analysis on collected sports data WITHOUT full linguistic extraction
Uses simplified name features for immediate results
"""

import json
import sqlite3
import numpy as np
import pandas as pd
from scipy import stats
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_simple_features(name):
    """Extract basic name features without full linguistic pipeline"""
    parts = name.split()
    first = parts[0] if parts else ''
    last = parts[-1] if len(parts) > 1 else ''
    
    # Simple syllable count (rough estimate)
    syllables = sum(max(1, len([c for c in word if c.lower() in 'aeiou'])) for word in parts)
    
    # Simple harshness (count harsh consonants)
    harsh_chars = 'kgptbdxz'
    harshness = sum(1 for c in name.lower() if c in harsh_chars) / len(name.replace(' ', ''))
    
    # Memorability (uniqueness × brevity)
    memorability = (1.0 / max(1, len(name))) * (1.0 / max(1, syllables / 3))
    
    return {
        'syllables': syllables,
        'length': len(name.replace(' ', '')),
        'word_count': len(parts),
        'harshness': harshness,
        'memorability': memorability,
        'first_vowel_start': 1 if first and first[0].lower() in 'aeiou' else 0,
        'alliteration': 1 if len(parts) > 1 and first[0].lower() == last[0].lower() else 0
    }


def analyze_sport(sport_name):
    """Analyze one sport with simplified features"""
    logger.info(f"\n{'='*60}")
    logger.info(f"ANALYZING: {sport_name.upper()}")
    logger.info(f"{'='*60}")
    
    # Load data
    json_path = f"analysis_outputs/sports_meta_analysis/{sport_name}_athletes.json"
    with open(json_path, 'r') as f:
        athletes = json.load(f)
    
    logger.info(f"Loaded {len(athletes)} athletes")
    
    # Extract features and prepare dataframe
    rows = []
    for athlete in athletes:
        if athlete.get('success_score') is None:
            continue
        
        full_name = athlete.get('full_name', athlete.get('name', ''))
        features = extract_simple_features(full_name)
        features['success_score'] = athlete['success_score']
        features['name'] = full_name
        rows.append(features)
    
    df = pd.DataFrame(rows)
    logger.info(f"Analyzing {len(df)} athletes with valid scores")
    
    # Calculate correlations
    feature_cols = ['syllables', 'length', 'harshness', 'memorability']
    correlations = {}
    
    for feature in feature_cols:
        r, p = stats.pearsonr(df[feature], df['success_score'])
        correlations[feature] = {
            'r': round(r, 4),
            'p': round(p, 6),
            'n': len(df)
        }
        logger.info(f"  {feature}: r={r:.3f}, p={p:.4f}")
    
    # Save results
    results = {
        'sport': sport_name,
        'n_athletes': len(df),
        'avg_success': round(df['success_score'].mean(), 2),
        'correlations': correlations
    }
    
    output_path = f"analysis_outputs/sports_meta_analysis/{sport_name}_analysis.json"
    with open(output_path, 'w') as f:
        json.dump({'results': results}, f, indent=2)
    
    logger.info(f"✓ {sport_name} analysis complete")
    return results


def run_meta_analysis():
    """Quick meta-analysis on collected sports"""
    logger.info("\n" + "="*80)
    logger.info("CROSS-SPORT META-ANALYSIS")
    logger.info("="*80 + "\n")
    
    # Load sport characteristics
    with open('analysis_outputs/sports_meta_analysis/sport_characteristics.json', 'r') as f:
        sport_chars = json.load(f)['sports_characterized']
    
    # Analyze available sports
    sports_analyzed = []
    for sport in ['baseball', 'basketball', 'football']:
        try:
            results = analyze_sport(sport)
            results['characteristics'] = sport_chars[sport]
            sports_analyzed.append(results)
        except Exception as e:
            logger.error(f"Error analyzing {sport}: {e}")
    
    # Meta-analysis: Test Contact × Harshness
    logger.info("\n" + "="*60)
    logger.info("META-ANALYSIS: Contact Level × Harshness Effect")
    logger.info("="*60)
    
    contact_levels = []
    harshness_effects = []
    
    for sport_result in sports_analyzed:
        contact = sport_result['characteristics']['contact_level']
        harshness_r = sport_result['correlations']['harshness']['r']
        
        contact_levels.append(contact)
        harshness_effects.append(harshness_r)
        
        logger.info(f"{sport_result['sport']}: Contact={contact}, Harshness r={harshness_r:.3f}")
    
    # Correlation
    if len(contact_levels) >= 3:
        r, p = stats.pearsonr(contact_levels, harshness_effects)
        logger.info(f"\n✓ META-CORRELATION: r = {r:.3f}, p = {p:.4f}")
        logger.info(f"  Interpretation: {'SUPPORTED' if r > 0.40 else 'NOT SUPPORTED'} (need r > 0.40)")
    
    # Test Team Size × Syllables
    logger.info("\n" + "="*60)
    logger.info("META-ANALYSIS: Team Size × Syllable Effect")
    logger.info("="*60)
    
    team_sizes = []
    syllable_effects = []
    
    for sport_result in sports_analyzed:
        team_size = sport_result['characteristics']['team_structure']['team_size']
        syllable_r = sport_result['correlations']['syllables']['r']
        
        team_sizes.append(team_size)
        syllable_effects.append(syllable_r)
        
        logger.info(f"{sport_result['sport']}: Team={team_size}, Syllable r={syllable_r:.3f}")
    
    if len(team_sizes) >= 3:
        r, p = stats.pearsonr(team_sizes, syllable_effects)
        logger.info(f"\n✓ META-CORRELATION: r = {r:.3f}, p = {p:.4f}")
        logger.info(f"  Interpretation: {'SUPPORTED' if r < -0.30 else 'NOT SUPPORTED'} (need r < -0.30)")
    
    # Save meta-results
    meta_results = {
        'n_sports': len(sports_analyzed),
        'sports': [s['sport'] for s in sports_analyzed],
        'total_athletes': sum(s['n_athletes'] for s in sports_analyzed),
        'contact_harshness': {
            'r': round(r, 4) if len(contact_levels) >= 3 else None,
            'p': round(p, 6) if len(contact_levels) >= 3 else None,
            'data': list(zip([s['sport'] for s in sports_analyzed], contact_levels, harshness_effects))
        },
        'team_syllables': {
            'r': round(stats.pearsonr(team_sizes, syllable_effects)[0], 4) if len(team_sizes) >= 3 else None,
            'p': round(stats.pearsonr(team_sizes, syllable_effects)[1], 6) if len(team_sizes) >= 3 else None,
            'data': list(zip([s['sport'] for s in sports_analyzed], team_sizes, syllable_effects))
        }
    }
    
    with open('analysis_outputs/sports_meta_analysis/meta_regression_results.json', 'w') as f:
        json.dump(meta_results, f, indent=2)
    
    logger.info("\n" + "="*80)
    logger.info("ANALYSIS COMPLETE")
    logger.info("="*80)
    logger.info(f"Sports analyzed: {len(sports_analyzed)}")
    logger.info(f"Total athletes: {meta_results['total_athletes']}")
    logger.info(f"Results saved to: meta_regression_results.json")
    
    return meta_results


if __name__ == "__main__":
    results = run_meta_analysis()
    print("\n=== SUMMARY ===")
    print(json.dumps(results, indent=2))

