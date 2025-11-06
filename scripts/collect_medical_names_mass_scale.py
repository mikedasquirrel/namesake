"""Medical Names Mass-Scale Collection and Analysis

Tests whether doctors choose specialties matching surnames at scale.

Example: Do doctors named "Hart" specialize in Cardiology at 2x baseline rate?

Data: NPI (National Provider Identifier) database - ~1 million U.S. physicians
Cost: $0 (public data)
Sample target: 40,000 physicians across 8 specialties
"""

import csv
import json
import requests
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any
import logging

import pandas as pd
import numpy as np
from scipy import stats

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MedicalNamesSynchronicityAnalyzer:
    """Mass-scale analysis of physician name-specialty matching."""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / 'data' / 'medical_synchronicity'
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.output_dir = Path(__file__).parent.parent / 'analysis_outputs' / 'medical_synchronicity'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Define surname-specialty matches to test
        self.matches_to_test = {
            'cardiology': {
                'surnames': ['Hart', 'Heart', 'Herz', 'Coeur', 'Cardiac'],
                'baseline_rate': 0.08,  # 8% of doctors are cardiologists
                'specialty_codes': ['207RC0000X', '207RA0000X']  # NPI taxonomy codes
            },
            
            'hematology': {
                'surnames': ['Blood', 'Blut', 'Sang', 'Sangre', 'Hema'],
                'baseline_rate': 0.005,  # 0.5% (rare specialty)
                'specialty_codes': ['207RH0000X']
            },
            
            'neurology': {
                'surnames': ['Brain', 'Mind', 'Head', 'Kopf', 'Neuro'],
                'baseline_rate': 0.03,  # 3%
                'specialty_codes': ['204D00000X', '2084N0400X']
            },
            
            'orthopedics': {
                'surnames': ['Bone', 'Bones', 'Skelton', 'Skeleton', 'Os'],
                'baseline_rate': 0.04,  # 4%
                'specialty_codes': ['207X00000X', '207XS0114X']
            },
            
            'pain_medicine': {
                'surnames': ['Payne', 'Pain', 'Hurt', 'Ache', 'Dolor'],
                'baseline_rate': 0.01,  # 1%
                'specialty_codes': ['208VP0000X']
            },
            
            'surgery': {
                'surnames': ['Slaughter', 'Butcher', 'Cutting', 'Sharp', 'Blade'],
                'baseline_rate': 0.10,  # 10%
                'specialty_codes': ['208600000X', '2086S0122X']
            },
            
            'dermatology': {
                'surnames': ['Skin', 'Haut', 'Piel', 'Hyde', 'Derm'],
                'baseline_rate': 0.03,  # 3%
                'specialty_codes': ['207N00000X']
            },
            
            'ophthalmology': {
                'surnames': ['Eye', 'Eyes', 'Seher', 'Vision', 'Sight'],
                'baseline_rate': 0.02,  # 2%
                'specialty_codes': ['207W00000X']
            }
        }
    
    def download_npi_data(self) -> str:
        """Download NPI database (large file ~8GB)."""
        
        logger.info("="*70)
        logger.info("NPI DATABASE DOWNLOAD")
        logger.info("="*70)
        logger.info("Note: Full NPI database is ~8GB")
        logger.info("Alternative: Use NPI API for targeted searches")
        logger.info("="*70)
        
        # NPI Registry API (free, no key needed)
        npi_api_url = "https://npiregistry.cms.hhs.gov/api/"
        
        instructions = {
            'method_1_api': {
                'description': 'Use NPI API for surname searches',
                'url': 'https://npiregistry.cms.hhs.gov/api/',
                'rate_limit': '5 requests/second',
                'advantage': 'No download needed, targeted searches',
                'disadvantage': 'Slower for mass searches'
            },
            
            'method_2_bulk': {
                'description': 'Download full NPI database',
                'url': 'https://download.cms.gov/nppes/NPI_Files.zip',
                'size': '~8GB zipped, ~50GB unzipped',
                'advantage': 'Complete data, fast analysis',
                'disadvantage': 'Large download, storage needed'
            },
            
            'method_3_sample': {
                'description': 'Use Doximity physician directory (requires account)',
                'advantage': 'Cleaner data, verified physicians',
                'disadvantage': 'May require institutional access'
            },
            
            'recommended': 'Start with API searches for specific surnames (Method 1)'
        }
        
        # Save instructions
        instructions_file = self.data_dir / 'npi_data_sources.json'
        with instructions_file.open('w') as f:
            json.dump(instructions, f, indent=2)
        
        logger.info(f"Data source instructions saved to: {instructions_file}")
        
        return "See npi_data_sources.json for download options"
    
    def search_surname_via_api(self, surname: str, specialty_codes: List[str] = None, 
                               max_results: int = 200) -> List[Dict]:
        """Search NPI API for physicians with specific surname."""
        
        url = "https://npiregistry.cms.hhs.gov/api/"
        
        params = {
            'version': '2.1',
            'last_name': surname,
            'limit': max_results
        }
        
        if specialty_codes:
            params['taxonomy_description'] = specialty_codes[0]
        
        try:
            logger.info(f"Searching for physicians named {surname}...")
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            results = data.get('results', [])
            
            logger.info(f"  Found {len(results)} physicians named {surname}")
            
            return results
            
        except Exception as e:
            logger.error(f"API search failed: {e}")
            return []
    
    def analyze_surname_specialty_match(self, surname: str, specialty: str, 
                                       specialty_info: Dict) -> Dict[str, Any]:
        """Test whether surname predicts specialty above baseline."""
        
        logger.info(f"\nTesting: {surname} → {specialty}")
        
        # Search for all physicians with this surname
        all_with_surname = self.search_surname_via_api(surname, max_results=200)
        
        if not all_with_surname:
            return {'status': 'no_data', 'surname': surname}
        
        # Count how many are in target specialty
        in_specialty = 0
        for physician in all_with_surname:
            taxonomies = physician.get('taxonomies', [])
            for tax in taxonomies:
                if tax.get('code') in specialty_info['specialty_codes']:
                    in_specialty += 1
                    break
        
        n_total = len(all_with_surname)
        observed_rate = in_specialty / n_total if n_total > 0 else 0
        expected_rate = specialty_info['baseline_rate']
        
        # Binomial test
        from scipy.stats import binom_test
        
        expected_count = n_total * expected_rate
        p_value = binom_test(in_specialty, n_total, expected_rate, alternative='greater')
        
        # Odds ratio
        odds_observed = observed_rate / (1 - observed_rate) if observed_rate < 1 else None
        odds_baseline = expected_rate / (1 - expected_rate)
        odds_ratio = odds_observed / odds_baseline if odds_observed else None
        
        result = {
            'surname': surname,
            'specialty': specialty,
            'n_total_physicians': n_total,
            'n_in_specialty': in_specialty,
            'observed_rate': observed_rate,
            'expected_rate': expected_rate,
            'expected_count': expected_count,
            'odds_ratio': odds_ratio,
            'p_value': p_value,
            'significant': p_value < 0.05,
            'interpretation': self._interpret_result(surname, specialty, observed_rate, expected_rate, p_value)
        }
        
        logger.info(f"  Observed: {in_specialty}/{n_total} ({observed_rate:.1%}) vs Expected: {expected_rate:.1%}")
        logger.info(f"  Odds ratio: {odds_ratio:.2f}" if odds_ratio else "  Odds ratio: undefined")
        logger.info(f"  p-value: {p_value:.4f} {'✓ SIGNIFICANT' if p_value < 0.05 else ''}")
        
        return result
    
    def _interpret_result(self, surname: str, specialty: str, observed: float, 
                         expected: float, p_value: float) -> str:
        """Generate interpretation of result."""
        
        if p_value >= 0.05:
            return f"No evidence that '{surname}' predicts {specialty}"
        
        fold_increase = observed / expected if expected > 0 else 0
        
        if fold_increase > 3.0:
            return f"STRONG: '{surname}' → {specialty} at {fold_increase:.1f}x baseline (p < {p_value:.4f})"
        elif fold_increase > 2.0:
            return f"MODERATE: '{surname}' → {specialty} at {fold_increase:.1f}x baseline (p < {p_value:.4f})"
        elif fold_increase > 1.3:
            return f"WEAK: '{surname}' → {specialty} at {fold_increase:.1f}x baseline (p < {p_value:.4f})"
        else:
            return f"Minimal effect: {fold_increase:.1f}x baseline"
    
    def run_full_analysis(self) -> Dict[str, Any]:
        """Test all surname-specialty matches."""
        
        logger.info("="*70)
        logger.info("MEDICAL NAMES MASS-SCALE ANALYSIS")
        logger.info("="*70)
        logger.info("Testing: Do doctors choose specialties matching surnames?")
        logger.info("Sample: Up to 40,000 physicians via NPI API")
        logger.info("="*70)
        
        # Download instructions
        self.download_npi_data()
        
        results = {}
        
        # Test each surname-specialty match
        for specialty, info in self.matches_to_test.items():
            specialty_results = []
            
            for surname in info['surnames']:
                result = self.analyze_surname_specialty_match(surname, specialty, info)
                specialty_results.append(result)
            
            results[specialty] = specialty_results
        
        # Meta-analysis
        results['meta_analysis'] = self._meta_analyze_results(results)
        
        # Save
        self._save_results(results)
        self._generate_report(results)
        
        return results
    
    def _meta_analyze_results(self, results: Dict) -> Dict[str, Any]:
        """Meta-analyze across all tests."""
        
        all_tests = []
        for specialty, tests in results.items():
            if specialty == 'meta_analysis':
                continue
            for test in tests:
                if test.get('odds_ratio'):
                    all_tests.append(test)
        
        if not all_tests:
            return {'status': 'no_valid_tests'}
        
        # Calculate summary statistics
        odds_ratios = [t['odds_ratio'] for t in all_tests if t.get('odds_ratio')]
        p_values = [t['p_value'] for t in all_tests]
        significant_tests = sum(1 for t in all_tests if t.get('significant'))
        
        return {
            'total_tests': len(all_tests),
            'significant_tests': significant_tests,
            'pct_significant': significant_tests / len(all_tests) * 100,
            'median_odds_ratio': float(np.median(odds_ratios)) if odds_ratios else None,
            'mean_odds_ratio': float(np.mean(odds_ratios)) if odds_ratios else None,
            'median_p_value': float(np.median(p_values)),
            'interpretation': self._interpret_meta(significant_tests, len(all_tests), 
                                                  np.median(odds_ratios) if odds_ratios else None)
        }
    
    def _interpret_meta(self, n_sig: int, n_total: int, median_or: float) -> str:
        """Interpret meta-analytic findings."""
        
        pct_sig = n_sig / n_total * 100 if n_total > 0 else 0
        
        if pct_sig > 60 and median_or and median_or > 2.0:
            return f"STRONG EVIDENCE: {pct_sig:.0f}% of tests significant, median OR = {median_or:.1f}x. Physicians DO choose specialties matching surnames."
        elif pct_sig > 40 and median_or and median_or > 1.5:
            return f"MODERATE EVIDENCE: {pct_sig:.0f}% significant, median OR = {median_or:.1f}x. Pattern exists but weaker than anecdotes."
        elif pct_sig > 25:
            return f"WEAK EVIDENCE: {pct_sig:.0f}% significant. Some matching but not robust."
        else:
            return f"NO EVIDENCE: Only {pct_sig:.0f}% significant. Anecdotes don't generalize."
    
    def _save_results(self, results: Dict):
        """Save results to JSON."""
        
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.output_dir / f'medical_mass_scale_{timestamp}.json'
        
        with output_file.open('w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"\n{'='*70}")
        logger.info(f"✅ Results saved to: {output_file}")
        logger.info(f"{'='*70}")
    
    def _generate_report(self, results: Dict):
        """Generate publication-ready report."""
        
        print("\n" + "="*70)
        print("MEDICAL NAMES SYNCHRONICITY - MASS-SCALE RESULTS")
        print("="*70)
        
        meta = results.get('meta_analysis', {})
        
        print(f"\nTOTAL TESTS: {meta.get('total_tests', 0)}")
        print(f"SIGNIFICANT: {meta.get('significant_tests', 0)} ({meta.get('pct_significant', 0):.0f}%)")
        print(f"MEDIAN ODDS RATIO: {meta.get('median_odds_ratio', 0):.2f}x")
        
        print(f"\nINTERPRETATION:")
        print(f"  {meta.get('interpretation', 'N/A')}")
        
        print("\n" + "="*70)
        print("TOP MATCHES:")
        print("="*70)
        
        # Find strongest matches
        all_results = []
        for specialty, tests in results.items():
            if specialty == 'meta_analysis':
                continue
            for test in tests:
                if test.get('odds_ratio') and test.get('odds_ratio') > 1.0:
                    all_results.append(test)
        
        # Sort by odds ratio
        all_results.sort(key=lambda x: x.get('odds_ratio', 0), reverse=True)
        
        for i, result in enumerate(all_results[:10], 1):
            print(f"\n{i}. {result['surname']} → {result['specialty']}")
            print(f"   Observed: {result['observed_rate']:.1%} vs Expected: {result['expected_rate']:.1%}")
            print(f"   Odds Ratio: {result['odds_ratio']:.2f}x")
            print(f"   p-value: {result['p_value']:.4f}")
        
        print("\n" + "="*70 + "\n")


def main():
    """Run medical names mass-scale analysis."""
    
    analyzer = MedicalNamesSynchronicityAnalyzer()
    
    print("\n" + "="*70)
    print("MEDICAL NAMES MASS-SCALE COLLECTION")
    print("="*70)
    print("\nThis script will test the Dr. Chopp phenomenon at scale.")
    print("\nOptions:")
    print("1. Use NPI API (free, slower, targeted)")
    print("2. Download full NPI database (free, 8GB, fast analysis)")
    print("3. Manual sample from Doximity (institutional access needed)")
    print("\nRecommended: Start with API for proof-of-concept")
    print("="*70)
    
    # Run analysis
    results = analyzer.run_full_analysis()
    
    return results


if __name__ == '__main__':
    main()

