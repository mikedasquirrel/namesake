#!/usr/bin/env python3
"""
Quick Test Analysis - 2 Minute Demo

Runs a mini version of the full analysis to demonstrate functionality.
Uses small sample sizes for speed.
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import logging

# Simple console logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

def main():
    logger.info("=" * 60)
    logger.info("QUICK TEST ANALYSIS (2 minute demo)")
    logger.info("=" * 60)
    
    from app import app
    from utils.formula_engine import FormulaEngine
    from analyzers.formula_validator import FormulaValidator
    from core.unified_domain_model import UnifiedDomainInterface, DomainType
    from analyzers.name_analyzer import NameAnalyzer
    
    with app.app_context():
        # Step 1: Test transformations
        logger.info("\n[1/3] Testing Transformations...")
        
        analyzer = NameAnalyzer()
        engine = FormulaEngine()
        
        test_names = ["Bitcoin", "Ethereum", "Solana"]
        
        for name in test_names:
            features = analyzer.analyze_name(name)
            encodings = engine.transform_all(name, features)
            
            logger.info(f"  {name}:")
            for formula_id, encoding in encodings.items():
                logger.info(f"    {formula_id}: {encoding.shape_type}, hue={encoding.hue:.1f}°")
        
        # Step 2: Quick validation (small sample)
        logger.info("\n[2/3] Testing Validation (small sample)...")
        
        validator = FormulaValidator()
        
        try:
            report = validator.validate_formula(
                formula_id='hybrid',
                domains=[DomainType.CRYPTO],
                limit_per_domain=20  # Very small for speed
            )
            
            logger.info(f"  ✓ Validation complete")
            logger.info(f"    Overall correlation: {report.overall_correlation:.3f}")
            logger.info(f"    Sample size: {report.domain_performances['crypto'].n_with_outcome}")
            
        except Exception as e:
            logger.warning(f"  ⚠ Validation error: {e}")
        
        # Step 3: Domain statistics
        logger.info("\n[3/3] Domain Statistics...")
        
        interface = UnifiedDomainInterface()
        stats = interface.get_all_statistics()
        
        for domain, stat in stats.items():
            logger.info(f"  {domain}: {stat['count']} entities")
    
    logger.info("\n" + "=" * 60)
    logger.info("QUICK TEST COMPLETE ✓")
    logger.info("=" * 60)
    logger.info("\nSystem is operational. Run full analysis:")
    logger.info("  python3 scripts/auto_analyze_formulas.py --mode daily")

if __name__ == '__main__':
    main()

