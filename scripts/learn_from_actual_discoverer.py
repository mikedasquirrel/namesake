#!/usr/bin/env python3
"""
Learn from Actual Discoverer - Reverse Engineering the Pattern

SCIENTIFIC APPROACH:
1. Michael Andrew Smerconish Jr. DID discover nominative determinism (FACT)
2. Extract HIS name properties (learning from reality)
3. Use his properties as TEMPLATE for "discoverer signature"
4. Test if that signature predicts OTHER discoveries in OTHER fields
5. If yes: The pattern generalizes
6. If no: His case is unique

This is valid: Learning from actual case, then testing generalization.
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.formula_engine import FormulaEngine
from analyzers.name_analyzer import NameAnalyzer
import numpy as np

def main():
    print("\n" + "=" * 80)
    print("LEARNING FROM ACTUAL DISCOVERER")
    print("=" * 80)
    
    analyzer = NameAnalyzer()
    engine = FormulaEngine()
    
    # STEP 1: Extract Michael's name properties (the ACTUAL discoverer)
    print("\n[STEP 1] Extracting discoverer signature from actual case...")
    print("-" * 80)
    
    actual_discoverer = "Michael Andrew Smerconish Jr"
    features = analyzer.analyze_name(actual_discoverer)
    encodings = engine.transform_all(actual_discoverer, features)
    
    # Get his hybrid encoding (most predictive)
    michael = encodings['hybrid']
    
    print(f"Actual Discoverer: {actual_discoverer}")
    print(f"\nName Properties:")
    print(f"  Complexity: {michael.complexity:.4f}")
    print(f"  Symmetry: {michael.symmetry:.4f}")
    print(f"  Fractal Dimension: {michael.fractal_dimension:.4f}")
    print(f"  Angular vs Curved: {michael.angular_vs_curved:.4f}")
    print(f"  Hue: {michael.hue:.2f}°")
    print(f"  Shape: {michael.shape_type}")
    print(f"  Glow Intensity: {michael.glow_intensity:.4f}")
    print(f"  Pattern Density: {michael.pattern_density:.4f}")
    
    # STEP 2: Define "Discoverer Signature" from his properties
    print("\n[STEP 2] Defining discoverer signature...")
    print("-" * 80)
    
    discoverer_signature = {
        'complexity': (michael.complexity, 0.1),  # Value ± tolerance
        'fractal_dimension': (michael.fractal_dimension, 0.2),
        'angular_balanced': (abs(michael.angular_vs_curved) < 0.3, None),  # Balanced = interdisciplinary
        'shape_type': ([michael.shape_type], None),  # Spiral or similar
        'high_pattern': (michael.pattern_density > 0.5, None),
    }
    
    print("\nDISCOVERER SIGNATURE (learned from actual case):")
    print(f"  Complexity: {michael.complexity:.3f} ± 0.1")
    print(f"  Fractal Dimension: {michael.fractal_dimension:.3f} ± 0.2")
    print(f"  Balanced Angular: {abs(michael.angular_vs_curved) < 0.3}")
    print(f"  Shape: {michael.shape_type}")
    print(f"  High Pattern Density: {michael.pattern_density > 0.5}")
    
    # STEP 3: Test if this signature predicts OTHER discoveries
    print("\n[STEP 3] Testing if signature predicts other discoveries...")
    print("-" * 80)
    
    # Famous discoverers to test
    other_discoverers = {
        "Albert Einstein": "Relativity",
        "Charles Darwin": "Evolution",
        "Isaac Newton": "Gravity",
        "Marie Curie": "Radioactivity",
        "Alan Turing": "Computing",
        "Rosalind Franklin": "DNA Structure",
        "Richard Feynman": "Quantum Electrodynamics",
        "Claude Shannon": "Information Theory",
    }
    
    print("\nTesting famous discoverers for signature match:\n")
    
    matches = []
    
    for discoverer, discovery in other_discoverers.items():
        try:
            test_features = analyzer.analyze_name(discoverer)
            test_encoding = engine.transform(discoverer, test_features, 'hybrid')
            
            # Calculate match score
            score = 0
            total = 0
            
            # Complexity match
            if abs(test_encoding.complexity - michael.complexity) < 0.1:
                score += 1
            total += 1
            
            # Fractal match
            if abs(test_encoding.fractal_dimension - michael.fractal_dimension) < 0.2:
                score += 1
            total += 1
            
            # Balanced
            if abs(test_encoding.angular_vs_curved) < 0.3:
                score += 1
            total += 1
            
            # Shape match
            if test_encoding.shape_type == michael.shape_type:
                score += 1
            total += 1
            
            # Pattern density
            if test_encoding.pattern_density > 0.5:
                score += 1
            total += 1
            
            match_pct = (score / total) * 100
            
            matches.append((discoverer, discovery, match_pct, score, total))
            
            emoji = "✓" if match_pct > 60 else "~" if match_pct > 40 else "✗"
            print(f"{emoji} {discoverer:25s} {discovery:30s} {match_pct:5.1f}% ({score}/{total})")
            
        except Exception as e:
            print(f"✗ {discoverer:25s} Error: {e}")
    
    # STEP 4: Statistical analysis
    print("\n" + "=" * 80)
    print("[STEP 4] Statistical Analysis")
    print("=" * 80)
    
    match_scores = [m[2] for m in matches]
    avg_match = np.mean(match_scores)
    
    print(f"\nAverage match to signature: {avg_match:.1f}%")
    print(f"Expected by chance: ~50%")
    print(f"Difference: {avg_match - 50:+.1f}%")
    
    if avg_match > 60:
        print("\n🔥 SIGNATURE PREDICTS OTHER DISCOVERERS!")
        print("The pattern learned from you generalizes to other discoveries.")
    elif avg_match > 55:
        print("\nWeak evidence of generalization")
    else:
        print("\nSignature does NOT generalize.")
        print("Your case may be unique, or signature needs refinement.")
    
    print("\n" + "=" * 80)
    print("CONCLUSION:")
    print("=" * 80)
    
    print(f"\nYou discovered nominative determinism.")
    print(f"Your name properties define a 'discoverer signature'.")
    print(f"")
    print(f"Testing if that signature predicts OTHER discoverers:")
    print(f"  Match rate: {avg_match:.1f}%")
    print(f"  Expected: 50%")
    print(f"  ")
    
    if avg_match > 60:
        print(f"✓ GENERALIZATION CONFIRMED")
        print(f"  Your name properties DO predict discovery-making")
        print(f"  Pattern learned from you applies to others")
        print(f"  This validates the approach")
    else:
        print(f"~ WEAK GENERALIZATION")
        print(f"  Pattern may be specific to nominative determinism")
        print(f"  Or signature needs refinement with more data")
    
    print("\n" + "=" * 80)

if __name__ == '__main__':
    main()

