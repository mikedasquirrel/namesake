#!/usr/bin/env python3
"""
Run comprehensive America variant and 50-country phonetic analysis.

This script performs:
1. N-gram analysis of America nomenclature variants (1900-2019)
2. Phonetic analysis of 50 countries for comparative beauty scoring
3. Generates visualizations and saves results to data/processed/america_variants/

Usage:
    python scripts/run_america_analysis.py
    python scripts/run_america_analysis.py --phonetics-only
    python scripts/run_america_analysis.py --skip-ngrams
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from analysis.america_variant_analysis import AmericaVariantAnalyzer
import argparse


def main():
    parser = argparse.ArgumentParser(
        description='Run comprehensive America variant analysis with 50-country phonetic comparison'
    )
    parser.add_argument(
        '--phonetics-only',
        action='store_true',
        help='Only run phonetic analysis, skip N-gram data fetching'
    )
    parser.add_argument(
        '--skip-ngrams',
        action='store_true',
        help='Skip N-gram analysis (faster, uses cached data if available)'
    )
    
    args = parser.parse_args()
    
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║         AMERICA VARIANT & 50-COUNTRY PHONETIC ANALYSIS           ║
║                                                                   ║
║  This analysis compares "America" against 50 countries from      ║
║  all continents using comprehensive phonetic scoring.            ║
║                                                                   ║
║  Output: data/processed/america_variants/                        ║
║          - country_phonetic_comparison.csv                       ║
║          - country_phonetic_comparison.png                       ║
║          - ngram_variant_usage.parquet                           ║
║          - variant_summary.csv                                   ║
╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    analyzer = AmericaVariantAnalyzer()
    
    if args.phonetics_only:
        print("\n▶ Running phonetic analysis only (50 countries)...\n")
        phonetic_df = analyzer.analyze_country_phonetics()
        
        # Print America's ranking
        america_row = phonetic_df[phonetic_df['name'] == 'America']
        if len(america_row) > 0:
            rank = america_row['beauty_rank'].values[0]
            score = america_row['beauty_score'].values[0]
            print(f"\n{'='*70}")
            print(f"✓ AMERICA RANKS #{rank} out of 50 countries")
            print(f"  Beauty Score: {score:.1f}/100")
            print(f"{'='*70}\n")
    else:
        include_phonetics = not args.skip_ngrams
        analyzer.run_pipeline(include_phonetics=include_phonetics)
    
    print(f"\n✅ Analysis complete!")
    print(f"\n📂 Results saved to: {analyzer.results_dir}")
    print(f"\n🌐 View results at: http://localhost:5000/america")
    print()


if __name__ == "__main__":
    main()

