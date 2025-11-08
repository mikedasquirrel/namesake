#!/usr/bin/env python3
"""
Run Meta-Formula Analysis on Current Data

Don't wait for tomorrow - analyze formula relationships NOW
using existing cryptocurrency + other domain data.
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("\n" + "=" * 70)
    logger.info("META-FORMULA ANALYSIS - Running on Current Data")
    logger.info("=" * 70)
    
    from app import app
    from analyzers.formula_validator import FormulaValidator
    from analyzers.meta_formula_analyzer import MetaFormulaAnalyzer
    from core.unified_domain_model_extended import ExtendedDomainType
    
    with app.app_context():
        # Step 1: Quick validation of all formulas
        logger.info("\n[1/2] Validating formulas on small sample...")
        
        validator = FormulaValidator()
        
        # Test all 6 formulas on crypto (fast, large dataset)
        formulas = ['phonetic', 'semantic', 'structural', 'frequency', 'numerological', 'hybrid']
        
        validation_results = {}
        
        for formula in formulas:
            logger.info(f"  Testing {formula}...")
            
            try:
                report = validator.validate_formula(
                    formula,
                    domains=[ExtendedDomainType.CRYPTO],
                    limit_per_domain=100  # Small sample for speed
                )
                
                validation_results[formula] = report.to_dict()
                logger.info(f"    r = {report.overall_correlation:.3f}")
                
            except Exception as e:
                logger.error(f"    Error: {e}")
        
        # Step 2: Meta-analysis
        logger.info("\n[2/2] Analyzing formula relationships...")
        
        meta_analyzer = MetaFormulaAnalyzer()
        signature = meta_analyzer.analyze_formula_space(validation_results)
        
        # Generate report
        report = meta_analyzer.generate_meta_formula_report(signature)
        
        print("\n" + "=" * 70)
        print(report)
        print("=" * 70)
        
        # Key findings
        print("\n🔥 KEY FINDINGS:")
        print("─" * 70)
        
        if signature.golden_ratio_pairs:
            print(f"✓ Golden ratio found in {len(signature.golden_ratio_pairs)} formula pairs!")
            for f1, f2 in signature.golden_ratio_pairs:
                rel = signature.formula_relationships[(f1, f2)]
                print(f"  {f1}/{f2} = {rel.ratio_value:.3f} ≈ φ")
        else:
            print("✗ No golden ratio relationships detected")
        
        if signature.universal_meta_pattern:
            print(f"\n✓ Universal meta-pattern: {signature.universal_meta_pattern}")
        
        print("\n" + "=" * 70)
        print("Analysis complete. Full report saved to:")
        print("  analysis_outputs/auto_analysis/meta_formula_analysis.txt")
        print("=" * 70)

if __name__ == '__main__':
    main()

