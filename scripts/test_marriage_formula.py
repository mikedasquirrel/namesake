#!/usr/bin/env python3
"""
Marriage Formula Test - SHOCKING RESULTS POSSIBLE

Tests if name compatibility predicts marriage success using celebrity data.
Can run IMMEDIATELY with no API keys required.

This is the reality-breaking experiment.
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.relationship_formulas import RelationshipFormulaEngine, RelationshipBatchAnalyzer
from tabulate import tabulate

# Celebrity marriage data (public knowledge, easily verifiable)
CELEBRITY_MARRIAGES = [
    # (name1, name2, status, years_together)
    
    # DIVORCED
    ('Brad Pitt', 'Jennifer Aniston', 'divorced', 5),
    ('Brad Pitt', 'Angelina Jolie', 'divorced', 12),
    ('Tom Cruise', 'Katie Holmes', 'divorced', 6),
    ('Kim Kardashian', 'Kanye West', 'divorced', 7),
    ('Johnny Depp', 'Amber Heard', 'divorced', 2),
    ('Ben Affleck', 'Jennifer Garner', 'divorced', 13),
    ('Britney Spears', 'Kevin Federline', 'divorced', 3),
    ('Tiger Woods', 'Elin Nordegren', 'divorced', 6),
    ('Arnold Schwarzenegger', 'Maria Shriver', 'divorced', 25),
    ('Bill Gates', 'Melinda Gates', 'divorced', 27),
    
    # STILL MARRIED (10+ years)
    ('Beyoncé Knowles', 'Shawn Carter', 'married', 15),  # Jay-Z
    ('Barack Obama', 'Michelle Obama', 'married', 31),
    ('Tom Hanks', 'Rita Wilson', 'married', 35),
    ('Denzel Washington', 'Pauletta Washington', 'married', 40),
    ('Will Smith', 'Jada Pinkett', 'married', 26),
    ('David Beckham', 'Victoria Beckham', 'married', 24),
    ('Ellen DeGeneres', 'Portia de Rossi', 'married', 15),
    ('Sarah Jessica Parker', 'Matthew Broderick', 'married', 27),
    ('Faith Hill', 'Tim McGraw', 'married', 27),
    ('Goldie Hawn', 'Kurt Russell', 'married', 40),  # Not legally married but together
]


def main():
    print("\n" + "=" * 70)
    print("MARRIAGE FORMULA TEST - CELEBRITY COUPLES")
    print("Testing if name compatibility predicts marriage success")
    print("=" * 70)
    
    engine = RelationshipFormulaEngine()
    batch_analyzer = RelationshipBatchAnalyzer()
    
    # Analyze all couples
    print("\nAnalyzing couples...")
    
    results_table = []
    
    for name1, name2, status, duration in CELEBRITY_MARRIAGES:
        try:
            relationship = engine.analyze_relationship(name1, name2)
            
            results_table.append([
                f"{name1} & {name2}"[:40],
                status,
                duration,
                f"{relationship.compatibility_score:.3f}",
                f"{relationship.distance_score:.3f}",
                f"{relationship.golden_ratio_proximity:.3f}",
                relationship.relationship_type
            ])
            
        except Exception as e:
            print(f"  Error analyzing {name1} & {name2}: {e}")
    
    # Display results
    print("\n" + tabulate(
        results_table,
        headers=['Couple', 'Status', 'Years', 'Compat', 'Distance', 'Golden φ', 'Type'],
        tablefmt='grid'
    ))
    
    # Run batch analysis
    print("\n" + "=" * 70)
    print("STATISTICAL ANALYSIS")
    print("=" * 70)
    
    batch_results = batch_analyzer.analyze_couples(CELEBRITY_MARRIAGES)
    
    print(f"\nSample Size:")
    print(f"  Divorced: {batch_results['n_divorced']}")
    print(f"  Still Married: {batch_results['n_married']}")
    
    print(f"\nMean Compatibility:")
    print(f"  Divorced: {batch_results['divorced_compatibility']:.3f}")
    print(f"  Still Married: {batch_results['married_compatibility']:.3f}")
    print(f"  Effect Size: {batch_results['compatibility_effect']:+.3f}")
    
    sig = batch_results['significance']
    print(f"\nStatistical Significance:")
    print(f"  T-statistic: {sig['t_statistic']:.3f}")
    print(f"  P-value: {sig['p_value']:.4f}")
    print(f"  Significant: {'YES' if sig['significant'] else 'NO'} (p < 0.05)")
    
    print(f"\n" + "=" * 70)
    print("CONCLUSION:")
    print("=" * 70)
    print(f"\n{batch_results['conclusion']}")
    
    if abs(batch_results['compatibility_effect']) > 0.1:
        print("\n" + "🔥" * 35)
        print("\n  IF THIS HOLDS WITH MORE DATA:")
        print("  → Marriage success is mathematically predictable from names")
        print("  → Partner choice follows deterministic patterns")
        print("  → Free will in relationships is questionable")
        print("\n" + "🔥" * 35)
    
    print("\n" + "=" * 70)
    print("To test with MORE data:")
    print("  1. Collect 1,000 marriage/divorce records")
    print("  2. Run full statistical analysis")
    print("  3. Build prediction model")
    print("  4. Launch /marriage-compatibility web tool")
    print("=" * 70)


if __name__ == '__main__':
    main()

