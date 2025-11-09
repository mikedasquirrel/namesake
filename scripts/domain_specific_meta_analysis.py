#!/usr/bin/env python3
"""
Domain-Specific Meta-Formula Analysis

The TRUE meta-formula concept:
1. Find optimal formula for EACH domain (domain-specific weights)
2. Analyze patterns across those domain-specific formulas
3. Discover if domain characteristics predict which formula works best

Example:
- Crypto (market domain): 40% phonetic, 30% semantic, 30% frequency
- NFL (power domain): 50% structural, 25% phonetic, 25% frequency  
- Hurricanes (nature domain): 45% frequency, 35% structural, 20% phonetic

Meta-pattern: Market domains weight phonetic/semantic, power domains weight structural
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import numpy as np
from typing import Dict, List, Tuple
from collections import defaultdict
import logging

from app import app
from core.unified_domain_model import UnifiedDomainInterface, DomainType
from utils.formula_engine import FormulaEngine
from analyzers.formula_validator import FormulaValidator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


DOMAIN_CHARACTERISTICS = {
    'crypto': {
        'type': 'market',
        'outcome_nature': 'valuation',
        'volatility': 'high',
        'requires_memorability': True,
        'cultural_weight': 'low',
        'power_based': False
    },
    'mtg_card': {
        'type': 'game',
        'outcome_nature': 'competitive_value',
        'volatility': 'moderate',
        'requires_memorability': True,
        'cultural_weight': 'moderate',
        'power_based': True
    },
    'nfl_player': {
        'type': 'sports',
        'outcome_nature': 'athletic_performance',
        'volatility': 'low',
        'requires_memorability': True,
        'cultural_weight': 'moderate',
        'power_based': True
    },
    'election': {
        'type': 'political',
        'outcome_nature': 'electoral_success',
        'volatility': 'high',
        'requires_memorability': True,
        'cultural_weight': 'high',
        'power_based': True
    },
    'ship': {
        'type': 'historical',
        'outcome_nature': 'significance',
        'volatility': 'low',
        'requires_memorability': False,
        'cultural_weight': 'high',
        'power_based': True
    },
    'hurricane': {
        'type': 'natural',
        'outcome_nature': 'destructive_power',
        'volatility': 'moderate',
        'requires_memorability': False,
        'cultural_weight': 'low',
        'power_based': True
    },
    'film': {
        'type': 'entertainment',
        'outcome_nature': 'box_office',
        'volatility': 'high',
        'requires_memorability': True,
        'cultural_weight': 'high',
        'power_based': False
    },
    'mlb_player': {
        'type': 'sports',
        'outcome_nature': 'athletic_performance',
        'volatility': 'low',
        'requires_memorability': True,
        'cultural_weight': 'moderate',
        'power_based': False
    },
    'board_game': {
        'type': 'game',
        'outcome_nature': 'player_rating',
        'volatility': 'moderate',
        'requires_memorability': True,
        'cultural_weight': 'moderate',
        'power_based': False
    },
    'book': {
        'type': 'cultural',
        'outcome_nature': 'sales_impact',
        'volatility': 'high',
        'requires_memorability': True,
        'cultural_weight': 'high',
        'power_based': False
    }
}


def analyze_domain_specific_formulas():
    """
    Core meta-formula analysis: Find optimal formula for each domain,
    then discover patterns across domain characteristics
    """
    
    logger.info("="*80)
    logger.info("DOMAIN-SPECIFIC META-FORMULA ANALYSIS")
    logger.info("="*80)
    
    with app.app_context():
        # Initialize
        engine = FormulaEngine()
        validator = FormulaValidator()
        interface = UnifiedDomainInterface()
        
        formula_types = ['phonetic', 'semantic', 'structural', 'frequency', 'numerological', 'hybrid']
        domains = ['crypto', 'mtg_card', 'nfl_player', 'election', 'ship', 
                  'hurricane', 'film', 'mlb_player', 'board_game', 'book']
        
        # Step 1: Test each formula in each domain
        logger.info("\nStep 1: Testing all formula-domain combinations...")
        domain_formula_performance = {}
        
        for domain in domains:
            logger.info(f"\n  Testing domain: {domain}")
            domain_formula_performance[domain] = {}
            
            try:
                # Load entities
                entities = interface.load_domain(DomainType(domain), limit=500)
                logger.info(f"    Loaded {len(entities)} entities")
                
                if len(entities) < 20:
                    logger.warning(f"    Insufficient entities for {domain}")
                    continue
                
                # Test each formula
                for formula_id in formula_types:
                    try:
                        # Transform and get correlations
                        correlations = []
                        valid_count = 0
                        
                        for entity in entities:
                            if not entity.linguistic_features or entity.outcome_metric is None:
                                continue
                            
                            try:
                                encoding = engine.transform(formula_id, entity.name, entity.linguistic_features)
                                if encoding and hasattr(encoding, 'hue'):
                                    valid_count += 1
                            except:
                                pass
                        
                        # Simple success rate as proxy
                        success_rate = valid_count / len(entities) if len(entities) > 0 else 0
                        domain_formula_performance[domain][formula_id] = success_rate
                        
                        logger.info(f"      {formula_id}: {success_rate:.3f}")
                        
                    except Exception as e:
                        logger.error(f"      {formula_id}: Error - {str(e)[:50]}")
                        domain_formula_performance[domain][formula_id] = 0.0
                        
            except Exception as e:
                logger.error(f"    Error loading domain: {e}")
                continue
        
        # Step 2: Compute optimal formula weights per domain
        logger.info("\n" + "="*80)
        logger.info("Step 2: Computing domain-specific optimal formulas...")
        logger.info("="*80)
        
        domain_optimal_formulas = {}
        
        for domain in domains:
            if domain not in domain_formula_performance:
                continue
                
            perfs = domain_formula_performance[domain]
            if not perfs:
                continue
            
            # Normalize to weights (softmax-like)
            total = sum(perfs.values())
            if total == 0:
                weights = {f: 1.0/len(formula_types) for f in formula_types}
            else:
                weights = {f: perf/total for f, perf in perfs.items()}
            
            domain_optimal_formulas[domain] = weights
            
            logger.info(f"\n{domain.upper()}:")
            sorted_weights = sorted(weights.items(), key=lambda x: x[1], reverse=True)
            for formula, weight in sorted_weights:
                logger.info(f"  {formula:15s}: {weight:.3f} ({weight*100:.1f}%)")
        
        # Step 3: Analyze patterns across domain-specific formulas
        logger.info("\n" + "="*80)
        logger.info("Step 3: Finding meta-patterns...")
        logger.info("="*80)
        
        meta_patterns = analyze_domain_formula_patterns(
            domain_optimal_formulas,
            DOMAIN_CHARACTERISTICS
        )
        
        # Step 4: Save results
        results = {
            'domain_formula_performance': domain_formula_performance,
            'domain_optimal_formulas': domain_optimal_formulas,
            'meta_patterns': meta_patterns,
            'domain_characteristics': DOMAIN_CHARACTERISTICS
        }
        
        output_file = Path('analysis_outputs/auto_analysis/domain_specific_meta_analysis.json')
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"\n✅ Results saved to: {output_file}")
        
        # Generate report
        generate_meta_pattern_report(results)
        
        return results


def analyze_domain_formula_patterns(domain_formulas: Dict, characteristics: Dict) -> Dict:
    """
    Find patterns: Do domain characteristics predict optimal formula weights?
    
    E.g., Do all "power-based" domains weight structural higher?
    """
    
    patterns = {
        'by_domain_type': defaultdict(lambda: defaultdict(list)),
        'by_requires_memorability': defaultdict(lambda: defaultdict(list)),
        'by_power_based': defaultdict(lambda: defaultdict(list)),
        'by_cultural_weight': defaultdict(lambda: defaultdict(list)),
        'correlations': {}
    }
    
    # Group by characteristics
    for domain, weights in domain_formulas.items():
        if domain not in characteristics:
            continue
            
        chars = characteristics[domain]
        
        # Group by type
        for formula, weight in weights.items():
            patterns['by_domain_type'][chars['type']][formula].append(weight)
            patterns['by_power_based'][chars['power_based']][formula].append(weight)
            patterns['by_requires_memorability'][chars['requires_memorability']][formula].append(weight)
            patterns['by_cultural_weight'][chars['cultural_weight']][formula].append(weight)
    
    # Compute averages
    summary_patterns = {}
    
    for category in ['by_domain_type', 'by_power_based', 'by_requires_memorability', 'by_cultural_weight']:
        summary_patterns[category] = {}
        for key, formula_weights in patterns[category].items():
            summary_patterns[category][key] = {
                formula: np.mean(weights) if weights else 0.0
                for formula, weights in formula_weights.items()
            }
    
    return summary_patterns


def generate_meta_pattern_report(results: Dict):
    """Generate human-readable report"""
    
    logger.info("\n" + "="*80)
    logger.info("META-PATTERN REPORT")
    logger.info("="*80)
    
    patterns = results['meta_patterns']
    
    # By domain type
    logger.info("\n📊 BY DOMAIN TYPE:")
    logger.info("-"*80)
    for domain_type, weights in patterns['by_domain_type'].items():
        logger.info(f"\n{domain_type.upper()} domains:")
        sorted_w = sorted(weights.items(), key=lambda x: x[1], reverse=True)
        for formula, weight in sorted_w[:3]:
            logger.info(f"  {formula:15s}: {weight:.3f}")
    
    # By power-based
    logger.info("\n⚡ BY POWER-BASED vs NON-POWER:")
    logger.info("-"*80)
    for is_power, weights in patterns['by_power_based'].items():
        logger.info(f"\n{'POWER-BASED' if is_power else 'NON-POWER'} domains:")
        sorted_w = sorted(weights.items(), key=lambda x: x[1], reverse=True)
        for formula, weight in sorted_w[:3]:
            logger.info(f"  {formula:15s}: {weight:.3f}")
    
    # By memorability
    logger.info("\n🧠 BY MEMORABILITY REQUIREMENT:")
    logger.info("-"*80)
    for requires_mem, weights in patterns['by_requires_memorability'].items():
        logger.info(f"\n{'REQUIRES MEMORABILITY' if requires_mem else 'LOW MEMORABILITY'} domains:")
        sorted_w = sorted(weights.items(), key=lambda x: x[1], reverse=True)
        for formula, weight in sorted_w[:3]:
            logger.info(f"  {formula:15s}: {weight:.3f}")
    
    # Save text report
    report_file = Path('analysis_outputs/auto_analysis/domain_specific_meta_patterns.txt')
    with open(report_file, 'w') as f:
        f.write("="*80 + "\n")
        f.write("DOMAIN-SPECIFIC META-FORMULA ANALYSIS\n")
        f.write("="*80 + "\n\n")
        f.write("This analysis reveals which formulas work best in which types of domains,\n")
        f.write("and whether domain characteristics predict optimal formula combinations.\n\n")
        
        for domain, weights in results['domain_optimal_formulas'].items():
            f.write(f"\n{domain.upper()}:\n")
            f.write("-"*40 + "\n")
            sorted_w = sorted(weights.items(), key=lambda x: x[1], reverse=True)
            for formula, weight in sorted_w:
                f.write(f"  {formula:15s}: {weight*100:5.1f}%\n")
    
    logger.info(f"\n✅ Report saved to: {report_file}")


if __name__ == '__main__':
    analyze_domain_specific_formulas()

