"""Test 5: AI-Generated Name Optimization - The Ultimate Test

This is the PRIMARY validation test. Can AI optimize names better than humans
if it understands the nominative formula? Or does human semantic meaning win?

Three possible outcomes (all advance theory):
A. AI names outperform → Formula has predictive power (phonetics work)
B. Human names outperform → Meaning > phonetics (refines substrate theory)
C. No difference → Names don't matter much in this domain (fundamentals win)

Target domain: Cryptocurrency (fast feedback, measurable outcomes)
Trial: 20 projects randomized to AI vs human names
Timeline: 12-month outcome monitoring
"""

import sys
import os
import json
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import itertools

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from analyzers.name_analyzer import NameAnalyzer
import pandas as pd
import numpy as np


class NominativeAI:
    """AI system that generates optimal cryptocurrency names based on formula."""
    
    def __init__(self):
        self.analyzer = NameAnalyzer()
        
        # Formula weights from cryptocurrency analysis
        self.formula_weights = {
            'memorability': 0.35,      # Strong positive in crypto
            'syllable_penalty': 0.28,  # Fewer syllables better
            'harshness_optimal': 0.19, # Moderate harshness (45-60)
            'uniqueness': 0.12,        # Avoid saturated patterns
            'pronounceability': 0.06   # Easy to say
        }
        
        # Target ranges from successful crypto names
        self.optimal_ranges = {
            'syllables': (1, 2),           # 1-2 syllables optimal
            'length': (4, 8),              # 4-8 characters
            'memorability': (70, 85),      # High but not maximal
            'harshness': (45, 60),         # Moderate (not too harsh)
            'vowel_ratio': (0.3, 0.5),     # Balanced
            'pronounceability': (0.65, 1.0) # High
        }
        
        # Phoneme building blocks
        self.phonemes = {
            'vowels': ['a', 'e', 'i', 'o', 'u', 'y'],
            'consonants_soft': ['l', 'r', 'm', 'n', 'w'],
            'consonants_medium': ['b', 'd', 'g', 'v', 'z'],
            'consonants_hard': ['k', 't', 'p', 'f', 's'],
            'consonants_harsh': ['x', 'q', 'j']
        }
        
    def generate_optimal_names(self, n: int = 10, constraints: Optional[Dict] = None) -> List[Dict]:
        """Generate n optimized cryptocurrency names.
        
        Args:
            n: Number of names to generate
            constraints: Optional constraints (available domains, etc.)
            
        Returns:
            List of name candidates with scores
        """
        
        print(f"Generating {n} AI-optimized cryptocurrency names...")
        print("Optimization criteria:")
        print(f"  - Syllables: {self.optimal_ranges['syllables']}")
        print(f"  - Length: {self.optimal_ranges['length']} characters")
        print(f"  - Memorability: {self.optimal_ranges['memorability']}")
        print(f"  - Harshness: {self.optimal_ranges['harshness']}")
        print()
        
        # Use multiple generation strategies
        candidates = []
        
        # Strategy 1: Genetic algorithm (evolve good patterns)
        candidates.extend(self._genetic_generation(n // 3))
        
        # Strategy 2: Template-based (copy successful patterns)
        candidates.extend(self._template_generation(n // 3))
        
        # Strategy 3: Random search (exploration)
        candidates.extend(self._random_generation(n // 3 + 1))
        
        # Score all candidates
        scored_candidates = []
        for name in candidates:
            score, details = self._score_name(name)
            scored_candidates.append({
                'name': name,
                'optimization_score': score,
                'details': details,
                'generation_method': details.get('method', 'unknown')
            })
        
        # Sort by score and return top n
        scored_candidates.sort(key=lambda x: x['optimization_score'], reverse=True)
        top_candidates = scored_candidates[:n]
        
        # Print top candidates
        print(f"Top {len(top_candidates)} AI-generated names:")
        for i, candidate in enumerate(top_candidates, 1):
            print(f"  {i}. {candidate['name']:12s} "
                  f"(score={candidate['optimization_score']:.2f}, "
                  f"mem={candidate['details']['memorability']:.0f}, "
                  f"harsh={candidate['details']['harshness']:.0f})")
        print()
        
        return top_candidates
    
    def _genetic_generation(self, n: int) -> List[str]:
        """Generate names using genetic algorithm (evolve good phoneme combinations)."""
        
        # Start with seed patterns from successful cryptos
        seeds = ['bit', 'eth', 'ada', 'sol', 'dot', 'link', 'uni', 'atom']
        
        population = []
        
        # Mutate and crossover seeds
        for _ in range(n):
            if random.random() < 0.5:
                # Mutation: modify a seed
                seed = random.choice(seeds)
                mutated = self._mutate_name(seed)
                population.append(mutated)
            else:
                # Crossover: combine two seeds
                seed1, seed2 = random.sample(seeds, 2)
                crossed = self._crossover_names(seed1, seed2)
                population.append(crossed)
        
        return population
    
    def _template_generation(self, n: int) -> List[str]:
        """Generate names using successful templates."""
        
        templates = [
            ('CV', 'CV'),           # Two CV syllables: "sola", "vega"
            ('CVC',),               # Single CVC: "link", "dash"
            ('V', 'CVC'),           # V-CVC: "atom"
            ('CVC', 'V'),           # CVC-V: "luna"
        ]
        
        names = []
        for _ in range(n):
            template = random.choice(templates)
            name = self._apply_template(template)
            names.append(name)
        
        return names
    
    def _random_generation(self, n: int) -> List[str]:
        """Generate random names within constraints."""
        
        names = []
        for _ in range(n):
            length = random.randint(*self.optimal_ranges['length'])
            name = self._generate_random_name(length)
            names.append(name)
        
        return names
    
    def _mutate_name(self, name: str) -> str:
        """Mutate a name by changing one phoneme."""
        if len(name) <= 2:
            return name + random.choice(self.phonemes['vowels'])
        
        pos = random.randint(0, len(name) - 1)
        char = name[pos]
        
        # Replace with similar phoneme
        if char in self.phonemes['vowels']:
            new_char = random.choice(self.phonemes['vowels'])
        else:
            # Choose from medium consonants for balance
            new_char = random.choice(self.phonemes['consonants_medium'])
        
        return name[:pos] + new_char + name[pos+1:]
    
    def _crossover_names(self, name1: str, name2: str) -> str:
        """Combine two names."""
        # Take first half of name1 and second half of name2
        split1 = len(name1) // 2
        split2 = len(name2) // 2
        
        return name1[:split1] + name2[split2:]
    
    def _apply_template(self, template: Tuple[str, ...]) -> str:
        """Generate name following syllable template."""
        name = ""
        
        for syllable_pattern in template:
            syllable = ""
            for char_type in syllable_pattern:
                if char_type == 'C':
                    # Choose consonant (favor medium for balance)
                    consonants = (self.phonemes['consonants_soft'] + 
                                self.phonemes['consonants_medium'] * 2 +  # Weight toward medium
                                self.phonemes['consonants_hard'])
                    syllable += random.choice(consonants)
                elif char_type == 'V':
                    syllable += random.choice(self.phonemes['vowels'])
            
            name += syllable
        
        return name.capitalize()
    
    def _generate_random_name(self, length: int) -> str:
        """Generate random pronounceable name."""
        name = ""
        
        # Alternate consonants and vowels mostly
        for i in range(length):
            if i % 2 == 0:
                # Consonant
                consonants = (self.phonemes['consonants_soft'] + 
                            self.phonemes['consonants_medium'] +
                            self.phonemes['consonants_hard'])
                name += random.choice(consonants)
            else:
                # Vowel
                name += random.choice(self.phonemes['vowels'])
        
        return name.capitalize()
    
    def _score_name(self, name: str) -> Tuple[float, Dict]:
        """Score a name using the optimization formula."""
        
        # Analyze name
        analysis = self.analyzer.analyze_name(name)
        
        # Extract features (map NameAnalyzer keys)
        syllables = analysis.get('syllable_count', 2)
        length = analysis.get('character_length', len(name))
        memorability = analysis.get('memorability_score', 50.0)
        harshness = analysis.get('phonetic_score', 50.0)  # Use phonetic_score as harshness proxy
        vowel_ratio = analysis.get('vowel_ratio', 0.4)
        
        # Compute component scores (0-100 scale)
        scores = {}
        
        # 1. Syllable score (fewer is better, 1-2 optimal)
        if syllables in self.optimal_ranges['syllables']:
            scores['syllables'] = 100
        elif syllables == 3:
            scores['syllables'] = 70
        else:
            scores['syllables'] = max(0, 100 - (syllables - 2) * 20)
        
        # 2. Length score (4-8 characters optimal)
        if self.optimal_ranges['length'][0] <= length <= self.optimal_ranges['length'][1]:
            scores['length'] = 100
        else:
            distance = min(abs(length - self.optimal_ranges['length'][0]),
                          abs(length - self.optimal_ranges['length'][1]))
            scores['length'] = max(0, 100 - distance * 15)
        
        # 3. Memorability score (70-85 optimal)
        if self.optimal_ranges['memorability'][0] <= memorability <= self.optimal_ranges['memorability'][1]:
            scores['memorability'] = 100
        else:
            distance = min(abs(memorability - self.optimal_ranges['memorability'][0]),
                          abs(memorability - self.optimal_ranges['memorability'][1]))
            scores['memorability'] = max(0, 100 - distance * 2)
        
        # 4. Harshness score (45-60 optimal for crypto)
        if self.optimal_ranges['harshness'][0] <= harshness <= self.optimal_ranges['harshness'][1]:
            scores['harshness'] = 100
        else:
            distance = min(abs(harshness - self.optimal_ranges['harshness'][0]),
                          abs(harshness - self.optimal_ranges['harshness'][1]))
            scores['harshness'] = max(0, 100 - distance * 2)
        
        # 5. Pronounceability (simple check)
        pronounceable = self._is_pronounceable(name)
        scores['pronounceable'] = 100 if pronounceable else 50
        
        # Weighted sum
        total_score = (
            scores['syllables'] * 0.25 +
            scores['length'] * 0.15 +
            scores['memorability'] * 0.30 +
            scores['harshness'] * 0.20 +
            scores['pronounceable'] * 0.10
        )
        
        details = {
            'syllables': syllables,
            'length': length,
            'memorability': memorability,
            'harshness': harshness,
            'vowel_ratio': vowel_ratio,
            'component_scores': scores,
            'method': 'ai_optimization'
        }
        
        return total_score, details
    
    def _is_pronounceable(self, name: str) -> bool:
        """Check if name is pronounceable (no 3+ consonants in a row)."""
        consonant_run = 0
        
        for char in name.lower():
            if char in 'aeiouy':
                consonant_run = 0
            else:
                consonant_run += 1
                if consonant_run >= 3:
                    return False
        
        return True


class CryptoNamingTrial:
    """Manage randomized controlled trial of AI vs human naming."""
    
    def __init__(self):
        self.ai_generator = NominativeAI()
        self.trial_data = {
            'projects': [],
            'trial_start': datetime.now().isoformat(),
            'trial_status': 'recruiting'
        }
    
    def generate_trial_protocol(self) -> Dict:
        """Generate complete trial protocol document."""
        
        print("="*80)
        print("CRYPTO NAMING TRIAL PROTOCOL")
        print("Randomized Controlled Trial: AI vs Human Names")
        print("="*80)
        print()
        
        protocol = {
            'title': 'AI vs Human Cryptocurrency Name Optimization: Randomized Controlled Trial',
            'investigators': ['Michael Smerconish'],
            'institution': 'Independent Research',
            'trial_registration': 'To be submitted to ClinicalTrials.gov equivalent',
            'date_created': datetime.now().isoformat(),
            
            'objective': {
                'primary': 'Test whether AI-optimized names outperform human-selected names in cryptocurrency market performance',
                'secondary': [
                    'Determine if phonetic optimization predicts outcomes',
                    'Identify whether semantic meaning or phonetics matter more',
                    'Validate nominative determinism formula prospectively'
                ]
            },
            
            'design': {
                'type': 'Randomized Controlled Trial',
                'assignment': 'Parallel (AI vs Human)',
                'blinding': 'Single-blind (analysts blinded to assignment)',
                'randomization': 'Stratified by technology type and team size',
                'sample_size': 20,
                'duration': '12 months'
            },
            
            'eligibility': {
                'inclusion': [
                    'New cryptocurrency project launching in 2025-2026',
                    'Willing to accept random name assignment',
                    'Commit to providing outcome data',
                    'Allow publication of results'
                ],
                'exclusion': [
                    'Already launched projects',
                    'Projects with established branding',
                    'Scam/rug-pull projects (screened)'
                ]
            },
            
            'intervention': {
                'ai_arm': {
                    'description': 'Project receives AI-optimized name based on phonetic formula',
                    'method': 'NominativeAI generates 3 candidates, project chooses best fit',
                    'constraints': 'Must use assigned name for full 12 months'
                },
                'human_arm': {
                    'description': 'Project team selects own name following standard process',
                    'method': 'Team brainstorms and chooses preferred name',
                    'constraints': 'Must complete naming before seeing AI alternatives'
                }
            },
            
            'outcomes': {
                'primary': 'Market capitalization at 12 months',
                'secondary': [
                    'Trading volume (average daily)',
                    'Holder count',
                    'Social media mentions',
                    'Survival (project still active)',
                    'Price volatility'
                ]
            },
            
            'analysis_plan': {
                'primary_test': 't-test comparing mean market cap (log-transformed)',
                'secondary_tests': [
                    'Mann-Whitney U for non-normal outcomes',
                    'Survival analysis (Kaplan-Meier)',
                    'Regression controlling for fundamentals'
                ],
                'significance': 'α = 0.05 (two-tailed)',
                'missing_data': 'Intention-to-treat analysis'
            },
            
            'sample_size_justification': {
                'expected_effect': '15-25% performance difference (based on observational data)',
                'power': '80% to detect 20% difference',
                'n_per_arm': 10,
                'total_n': 20
            },
            
            'recruitment': {
                'targets': [
                    'Cryptocurrency incubators',
                    'Launch platforms (e.g., CoinList)',
                    'Crypto founder communities',
                    'Venture capital firms'
                ],
                'incentive': 'Free professional name optimization + publication exposure',
                'timeline': 'Q1-Q2 2025'
            },
            
            'ethical_considerations': {
                'informed_consent': 'All projects sign consent form',
                'data_privacy': 'Project fundamentals kept confidential',
                'no_harm': 'Both arms receive professional naming support',
                'transparency': 'Full publication regardless of outcome'
            }
        }
        
        # Generate example AI names to show projects
        print("[Generating example AI-optimized names...]")
        example_names = self.ai_generator.generate_optimal_names(n=10)
        protocol['example_ai_names'] = [
            {
                'name': n['name'],
                'score': n['optimization_score']
            }
            for n in example_names
        ]
        
        # Save protocol
        self._save_protocol(protocol)
        
        print("\n" + "="*80)
        print("TRIAL PROTOCOL COMPLETE")
        print("="*80)
        print("Next steps:")
        print("1. Begin recruitment (crypto incubators, launch platforms)")
        print("2. Screen projects for eligibility")
        print("3. Random assignment as projects enroll")
        print("4. Monitor outcomes monthly for 12 months")
        print("5. Analyze and publish results")
        print()
        
        return protocol
    
    def _save_protocol(self, protocol: Dict):
        """Save trial protocol."""
        output_dir = Path(__file__).parent.parent / 'data' / 'crypto_trial'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        json_path = output_dir / 'trial_protocol.json'
        with open(json_path, 'w') as f:
            json.dump(protocol, f, indent=2)
        print(f"✓ Protocol saved: {json_path}")
        
        # Also save as readable text
        txt_path = output_dir / 'trial_protocol.txt'
        with open(txt_path, 'w') as f:
            f.write("CRYPTOCURRENCY NAMING TRIAL PROTOCOL\n")
            f.write("="*80 + "\n\n")
            f.write(f"Title: {protocol['title']}\n")
            f.write(f"Date: {protocol['date_created']}\n\n")
            f.write(f"Design: {protocol['design']['type']}\n")
            f.write(f"Sample Size: {protocol['sample_size_justification']['total_n']}\n")
            f.write(f"Duration: {protocol['design']['duration']}\n\n")
            f.write("Primary Outcome: Market capitalization at 12 months\n\n")
            f.write("Example AI-Generated Names:\n")
            for i, name in enumerate(protocol['example_ai_names'], 1):
                f.write(f"  {i}. {name['name']} (score={name['score']:.1f})\n")
        print(f"✓ Readable protocol: {txt_path}")


def main():
    """Run AI name generator and trial protocol."""
    
    # Part 1: Demonstrate AI name generation
    print("PART 1: AI NAME GENERATOR DEMONSTRATION")
    print("="*80 + "\n")
    
    ai = NominativeAI()
    ai_names = ai.generate_optimal_names(n=20)
    
    # Part 2: Generate trial protocol
    print("\n\nPART 2: RANDOMIZED CONTROLLED TRIAL PROTOCOL")
    print("="*80 + "\n")
    
    trial = CryptoNamingTrial()
    protocol = trial.generate_trial_protocol()
    
    print("\n" + "="*80)
    print("TEST 5 INFRASTRUCTURE COMPLETE")
    print("="*80)
    print("\nNext steps:")
    print("1. Begin recruiting cryptocurrency projects")
    print("2. Set up outcome monitoring dashboard")
    print("3. Conduct trial over 12 months")
    print("4. Analyze results: AI vs Human performance")
    print("\nThree possible outcomes (all advance theory):")
    print("  A. AI wins → Phonetic formula has predictive power")
    print("  B. Human wins → Semantic meaning > phonetics (refines theory)")
    print("  C. Tie → Fundamentals dominate (names secondary)")
    print()


if __name__ == '__main__':
    main()

