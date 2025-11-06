"""Demographic-Phonetic Analysis Script

Runs regressive proof claims D1-D4 testing whether hurricane name phonetic
features correlate with demographic-specific outcomes.

Claims:
- D1: Phonetic harshness differentially affects evacuation by income quintile
- D2: Memorable names improve outcomes across all demographics proportionally
- D3: Gender-coded names affect risk perception differently by demographic
- D4: Displacement rates vary by demographic and correlate with phonetic formulas

Usage:
    python scripts/analyze_demographic_phonetics.py --all-claims
    python scripts/analyze_demographic_phonetics.py --claim D1
    python scripts/analyze_demographic_phonetics.py --export results.json
"""

import sys
import argparse
import logging
from pathlib import Path
import json
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app import app
from analyzers.phonetic_demographic_correlator import PhoneticDemographicCorrelator
from analyzers.demographic_impact_analyzer import DemographicImpactAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_all_claims(export_path: str = None) -> dict:
    """
    Run all demographic-phonetic correlation claims (D1-D4).
    
    Args:
        export_path: Optional path to export results JSON
    
    Returns:
        Results dict
    """
    logger.info("\n" + "="*80)
    logger.info("DEMOGRAPHIC-PHONETIC CORRELATION ANALYSIS")
    logger.info("Testing Claims D1-D4")
    logger.info("="*80 + "\n")
    
    with app.app_context():
        correlator = PhoneticDemographicCorrelator()
        
        # Run all claims
        results = correlator.test_all_claims()
        
        if not results.get('success'):
            logger.error("Analysis failed")
            return results
        
        # Print summary
        print_results_summary(results)
        
        # Export if requested
        if export_path:
            export_results(results, export_path)
        
        return results


def run_single_claim(claim_id: str, export_path: str = None) -> dict:
    """
    Run a single claim test.
    
    Args:
        claim_id: Claim ID (D1, D2, D3, or D4)
        export_path: Optional export path
    
    Returns:
        Results dict
    """
    logger.info(f"\n{'='*80}")
    logger.info(f"Testing Claim {claim_id}")
    logger.info(f"{'='*80}\n")
    
    with app.app_context():
        correlator = PhoneticDemographicCorrelator()
        
        # Run all claims (individual extraction not currently supported)
        all_results = correlator.test_all_claims()
        
        if not all_results.get('success'):
            logger.error("Analysis failed")
            return all_results
        
        # Extract specific claim
        claim_result = all_results.get('claims', {}).get(claim_id)
        
        if not claim_result:
            logger.error(f"Claim {claim_id} not found")
            return {'success': False, 'error': f'Claim {claim_id} not found'}
        
        # Print results
        print_claim_result(claim_id, claim_result)
        
        # Export if requested
        if export_path:
            export_results({
                'claim': claim_id,
                'sample_size': all_results.get('sample_size'),
                'result': claim_result
            }, export_path)
        
        return claim_result


def run_comparative_analysis(export_path: str = None) -> dict:
    """
    Run comparative demographic impact analysis across hurricanes.
    
    Args:
        export_path: Optional export path
    
    Returns:
        Results dict
    """
    logger.info("\n" + "="*80)
    logger.info("COMPARATIVE DEMOGRAPHIC IMPACT ANALYSIS")
    logger.info("="*80 + "\n")
    
    with app.app_context():
        from core.models import Hurricane, HurricaneDemographicImpact
        
        # Get hurricanes with demographic data
        hurricane_ids = [
            h[0] for h in app.app_context().push() or
            Hurricane.query.join(HurricaneDemographicImpact).distinct(Hurricane.id).values(Hurricane.id)
        ]
        
        analyzer = DemographicImpactAnalyzer()
        
        # Compare across hurricanes
        comparison = analyzer.compare_across_hurricanes(hurricane_ids)
        
        # Print summary
        print_comparative_summary(comparison)
        
        # Export if requested
        if export_path:
            export_results(comparison, export_path)
        
        return comparison


def print_results_summary(results: dict):
    """Print formatted summary of all claims."""
    print("\n" + "="*80)
    print("ANALYSIS RESULTS SUMMARY")
    print("="*80)
    print(f"Sample Size: {results.get('sample_size', 0)} observations")
    print()
    
    claims = results.get('claims', {})
    
    for claim_id in ['D1', 'D2', 'D3', 'D4']:
        claim_result = claims.get(claim_id, {})
        print_claim_result(claim_id, claim_result)
        print()


def print_claim_result(claim_id: str, result: dict):
    """Print formatted result for a single claim."""
    print(f"\n--- CLAIM {claim_id} ---")
    print(f"Hypothesis: {result.get('hypothesis', 'N/A')}")
    print(f"Tested: {result.get('tested', False)}")
    
    if not result.get('tested'):
        print(f"Reason: {result.get('interpretation', 'Not tested')}")
        return
    
    print(f"Sample Size: {result.get('sample_size', 'N/A')}")
    
    # Print metrics
    if 'r2' in result:
        print(f"R² (in-sample): {result['r2']:.4f}")
    if 'cv_r2_mean' in result:
        print(f"R² (cross-validated): {result['cv_r2_mean']:.4f} ± {result.get('cv_r2_std', 0):.4f}")
    
    # Claim-specific metrics
    if claim_id == 'D1' and 'max_interaction_effect' in result:
        print(f"Max Interaction Effect: {result['max_interaction_effect']:.6f}")
    elif claim_id == 'D2' and 'memorability_coefficient' in result:
        print(f"Memorability Coefficient: {result['memorability_coefficient']:.6f}")
    elif claim_id == 'D3' and 'max_gender_interaction' in result:
        print(f"Max Gender Interaction: {result['max_gender_interaction']:.6f}")
    elif claim_id == 'D4' and 'phonetic_composite_coefficient' in result:
        print(f"Phonetic Composite Coefficient: {result['phonetic_composite_coefficient']:.6f}")
    
    # Significance and interpretation
    significant = result.get('significant', False)
    print(f"\nSignificant: {'✓ YES' if significant else '✗ NO'}")
    print(f"Interpretation: {result.get('interpretation', 'N/A')}")


def print_comparative_summary(comparison: dict):
    """Print comparative analysis summary."""
    print("\n" + "="*80)
    print("COMPARATIVE DEMOGRAPHIC IMPACT ANALYSIS")
    print("="*80)
    print(f"Hurricanes Analyzed: {comparison.get('hurricanes_analyzed', 0)}")
    print()
    
    consistent = comparison.get('consistent_disparities', {})
    
    for category, patterns in consistent.items():
        print(f"\n{category.upper()}:")
        for pattern in patterns:
            metric = pattern.get('metric')
            group = pattern.get('highest_impact_group')
            frequency = pattern.get('frequency', 0)
            total = pattern.get('total_hurricanes', 0)
            consistency = pattern.get('consistency_pct', 0)
            
            print(f"  {metric}: {group} most affected ({frequency}/{total} hurricanes, {consistency:.1f}% consistent)")


def export_results(results: dict, export_path: str):
    """Export results to JSON file."""
    output = {
        'analysis_date': datetime.now().isoformat(),
        'analysis_type': 'demographic_phonetic_correlation',
        'results': results
    }
    
    export_file = Path(export_path)
    export_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(export_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    logger.info(f"✅ Results exported to {export_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Analyze demographic-phonetic correlations in hurricane impacts'
    )
    
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('--all-claims', action='store_true',
                           help='Run all claims (D1-D4)')
    mode_group.add_argument('--claim', type=str, choices=['D1', 'D2', 'D3', 'D4'],
                           help='Run specific claim')
    mode_group.add_argument('--comparative', action='store_true',
                           help='Run comparative demographic analysis across hurricanes')
    
    parser.add_argument('--export', type=str, help='Export results to JSON file')
    
    args = parser.parse_args()
    
    # Run appropriate analysis
    if args.all_claims:
        results = run_all_claims(args.export)
    elif args.claim:
        results = run_single_claim(args.claim, args.export)
    elif args.comparative:
        results = run_comparative_analysis(args.export)
    
    # Print final status
    print("\n" + "="*80)
    if results.get('success', False):
        print("✅ ANALYSIS COMPLETE")
    else:
        print("❌ ANALYSIS FAILED")
        if 'error' in results:
            print(f"Error: {results['error']}")
    print("="*80 + "\n")


if __name__ == '__main__':
    main()

