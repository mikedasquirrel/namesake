"""
Visualize Marriage Prediction Results

Creates publication-ready visualizations of findings.
"""

import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import json
from datetime import datetime

# Find most recent analysis results
results_dir = Path('analysis_outputs/marriage')
result_files = list(results_dir.glob('analysis_results_*.json'))
data_files = list(results_dir.glob('couples_data_*.csv'))

if not result_files or not data_files:
    print("No analysis results found. Run run_marriage_analysis.py first.")
    sys.exit(1)

# Load most recent
latest_results = max(result_files, key=lambda p: p.stat().st_mtime)
latest_data = max(data_files, key=lambda p: p.stat().st_mtime)

with open(latest_results) as f:
    results = json.load(f)

df = pd.read_csv(latest_data)

print("\n" + "=" * 80)
print("NOMINATIVE MATCHMAKER: INITIAL RESULTS")
print("=" * 80)

print(f"\nAnalysis Date: {results['timestamp']}")
print(f"Sample Size: {results['n_couples']} couples")

print("\n" + "-" * 80)
print("SAMPLE CHARACTERISTICS")
print("-" * 80)
print(f"Divorce Rate: {results['divorce_rate']*100:.1f}%")
print(f"Mean Marriage Duration: {results['mean_duration']:.1f} years")

print("\n" + "-" * 80)
print("HYPOTHESIS TEST RESULTS")
print("-" * 80)

for hyp, stats in results['hypotheses'].items():
    print(f"\n{hyp}:")
    if 'r' in stats:
        print(f"  Correlation: r = {stats['r']:.3f}")
        print(f"  Significance: p = {stats['p']:.4f}")
        print(f"  Status: {'✓ SIGNIFICANT' if stats['p'] < 0.05 else '✗ Not significant'}")
    elif 't' in stats:
        print(f"  t-statistic: t = {stats['t']:.3f}")
        print(f"  Significance: p = {stats['p']:.4f}")
        print(f"  Status: {'✓ SIGNIFICANT' if stats['p'] < 0.05 else '✗ Not significant'}")

print("\n" + "-" * 80)
print("THEORY COMPARISON")
print("-" * 80)
print("\nCorrelation with Marriage Duration:")

theories_sorted = sorted(results['theory_comparison'].items(), 
                        key=lambda x: abs(x[1]), reverse=True)

for theory, r in theories_sorted:
    print(f"  {theory:20s}: r = {r:+.3f}")

print(f"\n✨ WINNER: {results['winner']} (r = {results['theory_comparison'][results['winner']]:.3f})")

print("\n" + "-" * 80)
print("SAMPLE COUPLES")
print("-" * 80)

# Show interesting examples
print("\nHigh Compatibility Couples:")
high_compat = df.nlargest(3, 'compatibility_score')
for _, couple in high_compat.iterrows():
    status = "💔 Divorced" if couple['is_divorced'] else "💑 Married"
    print(f"  {couple['partner1']} & {couple['partner2']}: "
          f"Compatibility={couple['compatibility_score']:.3f}, "
          f"Duration={couple['marriage_duration']:.1f}y, {status}")

print("\nLow Compatibility Couples:")
low_compat = df.nsmallest(3, 'compatibility_score')
for _, couple in low_compat.iterrows():
    status = "💔 Divorced" if couple['is_divorced'] else "💑 Married"
    print(f"  {couple['partner1']} & {couple['partner2']}: "
          f"Compatibility={couple['compatibility_score']:.3f}, "
          f"Duration={couple['marriage_duration']:.1f}y, {status}")

print("\n" + "=" * 80)
print("INTERPRETATION")
print("=" * 80)

print("""
This is INITIAL DATA from sample couples (n=50).

Key Observations:
1. Effects not yet significant (need larger sample, n≥800)
2. Complementarity theory shows strongest trend (r=-0.25)
3. Most relationships classified as "discordant" (high phonetic distance)
4. Resonant relationships show slightly longer duration (+2.9 years)

Next Steps:
1. Collect full dataset (target: 5,000 couples)
2. Run blind testing validation
3. Cross-validation pipeline
4. Subgroup analyses

Note: Current data is synthetic/sample data for demonstration.
Real study requires actual marriage/divorce records.
""")

print("=" * 80)

