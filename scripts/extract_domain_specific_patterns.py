#!/usr/bin/env python3
"""
Extract Domain-Specific Meta-Formula Patterns from Existing Analysis

Uses the validation results from the 72K analysis to find:
1. Which formula works best in each domain
2. Optimal weight combinations per domain
3. Meta-patterns: Do domain characteristics predict formula preferences?
"""

import json
import numpy as np
from pathlib import Path
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


DOMAIN_CHARACTERISTICS = {
    'crypto': {'type': 'market', 'power_based': False, 'memorability_critical': True},
    'mtg_card': {'type': 'game', 'power_based': True, 'memorability_critical': True},
    'nfl_player': {'type': 'sports', 'power_based': True, 'memorability_critical': True},
    'election': {'type': 'political', 'power_based': True, 'memorability_critical': True},
    'ship': {'type': 'historical', 'power_based': True, 'memorability_critical': False},
    'hurricane': {'type': 'natural', 'power_based': True, 'memorability_critical': False},
    'film': {'type': 'entertainment', 'power_based': False, 'memorability_critical': True},
    'mlb_player': {'type': 'sports', 'power_based': False, 'memorability_critical': True},
    'board_game': {'type': 'game', 'power_based': False, 'memorability_critical': True},
    'book': {'type': 'cultural', 'power_based': False, 'memorability_critical': True}
}


def main():
    logger.info("="*80)
    logger.info("EXTRACTING DOMAIN-SPECIFIC META-FORMULA PATTERNS")
    logger.info("="*80)
    
    # Load latest analysis
    analysis_file = Path('analysis_outputs/auto_analysis/weekly_analysis_latest.json')
    
    if not analysis_file.exists():
        logger.error("No analysis results found!")
        return
    
    with open(analysis_file) as f:
        data = json.load(f)
    
    validations = data.get('validations', {})
    
    if not validations:
        logger.error("No validation results in analysis!")
        return
    
    # Extract domain performance for each formula
    logger.info("\nExtracting domain performances...")
    
    formula_domain_scores = {}  # formula -> domain -> best_correlation
    
    for formula_id, validation in validations.items():
        formula_domain_scores[formula_id] = {}
        domain_perfs = validation.get('domain_performances', {})
        
        for domain, perf in domain_perfs.items():
            best_corr = perf.get('best_correlation', 0)
            
            # Handle NaN
            if isinstance(best_corr, str) or (isinstance(best_corr, float) and np.isnan(best_corr)):
                best_corr = 0.0
            
            formula_domain_scores[formula_id][domain] = abs(float(best_corr))
    
    # Compute optimal weights for each domain
    logger.info("\n" + "="*80)
    logger.info("DOMAIN-SPECIFIC OPTIMAL FORMULAS")
    logger.info("="*80)
    
    domain_optimal_formulas = {}
    
    for domain in DOMAIN_CHARACTERISTICS.keys():
        logger.info(f"\n{domain.upper()}:")
        logger.info("-"*40)
        
        # Get all formula scores for this domain
        scores = {}
        for formula_id in formula_domain_scores.keys():
            score = formula_domain_scores[formula_id].get(domain, 0.0)
            scores[formula_id] = score
        
        # Normalize to weights (softmax-like with temperature)
        total = sum(scores.values())
        if total > 0:
            weights = {f: score/total for f, score in scores.items()}
        else:
            weights = {f: 1.0/len(scores) for f in scores.keys()}
        
        domain_optimal_formulas[domain] = weights
        
        # Display sorted by weight
        sorted_weights = sorted(weights.items(), key=lambda x: x[1], reverse=True)
        for formula, weight in sorted_weights:
            logger.info(f"  {formula:15s}: {weight*100:5.1f}% (r={scores[formula]:.3f})")
    
    # Analyze meta-patterns
    logger.info("\n" + "="*80)
    logger.info("META-PATTERNS ACROSS DOMAIN TYPES")
    logger.info("="*80)
    
    patterns = analyze_patterns(domain_optimal_formulas, DOMAIN_CHARACTERISTICS)
    
    # Save results
    output = {
        'formula_domain_scores': formula_domain_scores,
        'domain_optimal_formulas': domain_optimal_formulas,
        'meta_patterns': patterns,
        'domain_characteristics': DOMAIN_CHARACTERISTICS
    }
    
    output_file = Path('analysis_outputs/auto_analysis/true_domain_specific_meta.json')
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    logger.info(f"\n✅ Results saved to: {output_file}")
    
    # Generate human-readable report
    generate_report(output)


def analyze_patterns(domain_formulas, characteristics):
    """Find patterns in which formulas work where"""
    
    patterns = {}
    
    # Group by domain characteristics
    by_type = defaultdict(lambda: defaultdict(list))
    by_power = defaultdict(lambda: defaultdict(list))
    by_memorability = defaultdict(lambda: defaultdict(list))
    
    for domain, weights in domain_formulas.items():
        chars = characteristics[domain]
        
        for formula, weight in weights.items():
            by_type[chars['type']][formula].append(weight)
            by_power[chars['power_based']][formula].append(weight)
            by_memorability[chars['memorability_critical']][formula].append(weight)
    
    # Compute averages
    patterns['by_type'] = {
        domain_type: {formula: np.mean(weights) for formula, weights in formulas.items()}
        for domain_type, formulas in by_type.items()
    }
    
    patterns['by_power'] = {
        str(is_power): {formula: np.mean(weights) for formula, weights in formulas.items()}
        for is_power, formulas in by_power.items()
    }
    
    patterns['by_memorability'] = {
        str(requires_mem): {formula: np.mean(weights) for formula, weights in formulas.items()}
        for requires_mem, formulas in by_memorability.items()
    }
    
    return patterns


def generate_report(results):
    """Generate comprehensive meta-pattern report"""
    
    report_file = Path('analysis_outputs/auto_analysis/TRUE_META_FORMULA_REPORT.md')
    
    with open(report_file, 'w') as f:
        f.write("# Domain-Specific Meta-Formula Analysis\n\n")
        f.write("## The True Meta-Formula Concept\n\n")
        f.write("Each domain has an optimal formula combination. By analyzing these\n")
        f.write("optimal combinations, we discover meta-patterns: which types of domains\n")
        f.write("favor which types of formulas.\n\n")
        
        f.write("## Domain-Specific Optimal Formulas\n\n")
        
        for domain, weights in results['domain_optimal_formulas'].items():
            chars = results['domain_characteristics'][domain]
            f.write(f"### {domain.upper()}\n")
            f.write(f"**Type:** {chars['type']} | **Power-based:** {chars['power_based']} | ")
            f.write(f"**Memorability:** {chars['memorability_critical']}\n\n")
            
            sorted_weights = sorted(weights.items(), key=lambda x: x[1], reverse=True)
            f.write("```\n")
            for formula, weight in sorted_weights:
                stars = "★" * int(weight * 20) if weight > 0.05 else ""
                f.write(f"{formula:15s}: {weight*100:5.1f}% {stars}\n")
            f.write("```\n\n")
        
        f.write("## Meta-Patterns by Domain Characteristics\n\n")
        
        # By type
        f.write("### By Domain Type\n\n")
        for domain_type, weights in results['meta_patterns']['by_type'].items():
            f.write(f"**{domain_type.upper()} domains:**\n")
            sorted_w = sorted(weights.items(), key=lambda x: x[1], reverse=True)
            for formula, weight in sorted_w[:3]:
                f.write(f"- {formula}: {weight*100:.1f}%\n")
            f.write("\n")
        
        # By power
        f.write("### By Power-Based Nature\n\n")
        for is_power, weights in results['meta_patterns']['by_power'].items():
            label = "POWER-BASED" if is_power == "True" else "NON-POWER"
            f.write(f"**{label} domains:**\n")
            sorted_w = sorted(weights.items(), key=lambda x: x[1], reverse=True)
            for formula, weight in sorted_w[:3]:
                f.write(f"- {formula}: {weight*100:.1f}%\n")
            f.write("\n")
    
    logger.info(f"\n📄 Report saved to: {report_file}")


if __name__ == '__main__':
    main()

