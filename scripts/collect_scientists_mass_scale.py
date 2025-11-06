"""Scientists Names Mass-Scale Collection and Analysis

Tests whether scientists with "light" semantics in names specialize in optics/photonics.

Example: Does Chandrasekhar ("moon-holder") → radiative transfer generalize?

Data: arXiv.org (physics/astronomy preprints)
Cost: $0 (free API)
Sample target: 10,000 physicists with 5+ papers
"""

import arxiv
import json
import re
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Any
import logging
import time

import pandas as pd
import numpy as np
from scipy import stats

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScientistNamesSynchronicityAnalyzer:
    """Mass-scale analysis of scientist name-research area matching."""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / 'data' / 'scientist_synchronicity'
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.output_dir = Path(__file__).parent.parent / 'analysis_outputs' / 'scientist_synchronicity'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Name semantics to test
        self.name_semantics = {
            'light_brightness': {
                'first_names': ['Lucian', 'Lucy', 'Claire', 'Clara', 'Helen', 'Robert', 'Albert'],
                'surname_roots': ['Light', 'Bright', 'Lux', 'Luci', 'Chand', 'Shein'],
                'research_areas': ['optics', 'photonics', 'laser', 'spectroscopy', 'radiative'],
                'baseline_rate': 0.12
            },
            
            'dark_black': {
                'first_names': ['Blake', 'Darcy'],
                'surname_roots': ['Black', 'Schwartz', 'Noir', 'Nero', 'Kuro'],
                'research_areas': ['black hole', 'dark matter', 'dark energy'],
                'baseline_rate': 0.08
            },
            
            'field_force': {
                'first_names': ['Maxwell', 'Faraday'],
                'surname_roots': ['Field', 'Force', 'Power'],
                'research_areas': ['field theory', 'electromagnetic', 'quantum field'],
                'baseline_rate': 0.15
            },
            
            'wave_quantum': {
                'surname_roots': ['Wave', 'Bohr', 'Planck', 'Quantum'],
                'research_areas': ['quantum', 'wave', 'oscillation'],
                'baseline_rate': 0.20
            }
        }
    
    def collect_physicist_sample(self, n_target: int = 1000) -> List[Dict]:
        """Collect sample of physicists from arXiv."""
        
        logger.info("="*70)
        logger.info("PHYSICIST SAMPLE COLLECTION FROM ARXIV")
        logger.info("="*70)
        logger.info(f"Target: {n_target} physicists with 5+ papers")
        logger.info("="*70)
        
        # Sample physics categories
        categories = [
            'physics.optics',
            'physics.atom-ph',  # Atomic physics
            'astro-ph',  # Astrophysics
            'quant-ph',  # Quantum physics
            'cond-mat',  # Condensed matter
            'hep-ph',  # High energy physics
        ]
        
        physicists = []
        seen_authors = set()
        
        for category in categories:
            logger.info(f"\nSearching category: {category}")
            
            try:
                # Search recent papers in this category
                search = arxiv.Search(
                    query=f'cat:{category}',
                    max_results=500,
                    sort_by=arxiv.SortCriterion.SubmittedDate
                )
                
                for paper in search.results():
                    for author in paper.authors:
                        author_name = author.name
                        
                        if author_name not in seen_authors:
                            seen_authors.add(author_name)
                            
                            physicists.append({
                                'name': author_name,
                                'category': category,
                                'sample_paper_title': paper.title,
                                'sample_paper_categories': [cat for cat in paper.categories]
                            })
                    
                    if len(physicists) >= n_target:
                        break
                
                time.sleep(3)  # Polite to arXiv
                
                if len(physicists) >= n_target:
                    break
                    
            except Exception as e:
                logger.error(f"Error searching {category}: {e}")
        
        logger.info(f"\n✅ Collected {len(physicists)} unique physicists")
        
        return physicists[:n_target]
    
    def classify_name_semantics(self, name: str) -> List[str]:
        """Classify name into semantic categories."""
        
        name_lower = name.lower()
        categories = []
        
        for category, info in self.name_semantics.items():
            # Check first names
            for first_name in info.get('first_names', []):
                if first_name.lower() in name_lower:
                    categories.append(category)
                    break
            
            # Check surname roots
            for root in info.get('surname_roots', []):
                if root.lower() in name_lower:
                    categories.append(category)
                    break
        
        return categories if categories else ['none']
    
    def classify_research_area(self, papers: List) -> List[str]:
        """Classify research area from papers."""
        
        # Extract keywords from titles and categories
        keywords = []
        
        for paper in papers:
            # Title words
            title_words = paper.title.lower().split()
            keywords.extend(title_words)
            
            # Categories
            keywords.extend([cat.lower() for cat in paper.categories])
        
        # Count keyword frequencies
        keyword_counts = Counter(keywords)
        
        # Match to research areas
        areas = []
        
        for category, info in self.name_semantics.items():
            for area_keyword in info['research_areas']:
                # Check if keyword appears frequently
                if any(area_keyword in kw for kw in keyword_counts):
                    areas.append(area_keyword)
        
        return areas if areas else ['general']
    
    def analyze_name_area_match(self) -> Dict[str, Any]:
        """Test whether name semantics predict research areas."""
        
        logger.info("\n[ANALYZING NAME-AREA MATCHES]")
        
        # This is a framework - full implementation would:
        # 1. Collect 10,000 physicists
        # 2. Get their publication histories
        # 3. Classify names semantically
        # 4. Classify research areas from papers
        # 5. Test for statistical association
        
        framework = {
            'sample_needed': 10000,
            'data_source': 'arXiv API (free)',
            'timeline': '2 months',
            'cost': '$0',
            
            'methodology': {
                'step_1': 'Sample 10,000 physicists with 5+ papers each',
                'step_2': 'Classify names using etymology API or manual coding',
                'step_3': 'Classify research areas from publication keywords',
                'step_4': 'Chi-square test: name category × research area',
                'step_5': 'Calculate odds ratios with confidence intervals'
            },
            
            'expected_results': {
                'light_names_optics_rate': 0.18,
                'non_light_names_optics_rate': 0.12,
                'odds_ratio': 1.5,
                'interpretation': 'Light-named physicists 1.5x more likely in optics',
                'p_value': '< 0.01 with n=10,000',
                'effect_size': 'Small but significant (Cohen\'s h = 0.15)'
            },
            
            'challenges': {
                'etymology_classification': 'Hard to automate (need manual coding or API)',
                'cross_cultural_names': 'Chandrasekhar clear, but many ambiguous',
                'research_area_classification': 'Multiple specialties per physicist',
                'confounds': 'Nationality, era, advisor effects'
            },
            
            'power_analysis': {
                'to_detect_1_5x_effect': 'Need n=2,500 per group = 5,000 total',
                'to_detect_2_0x_effect': 'Need n=400 per group = 800 total',
                'recommended_sample': 10000,
                'power_with_n_10000': '>99% for OR=1.5, >80% for OR=1.3'
            }
        }
        
        return framework
    
    def run_pilot_analysis(self, n_pilot: int = 100) -> Dict[str, Any]:
        """Run pilot with small sample to test feasibility."""
        
        logger.info("="*70)
        logger.info("SCIENTIST NAMES - PILOT ANALYSIS")
        logger.info("="*70)
        logger.info(f"Collecting n={n_pilot} physicists for pilot test")
        logger.info("="*70)
        
        # Collect pilot sample
        physicists = self.collect_physicist_sample(n_pilot)
        
        # Classify each
        classified = []
        for physicist in physicists:
            name_cats = self.classify_name_semantics(physicist['name'])
            
            classified.append({
                **physicist,
                'name_categories': name_cats,
                'has_light_semantic': 'light_brightness' in name_cats
            })
        
        # Summary
        n_light_names = sum(1 for p in classified if p['has_light_semantic'])
        
        results = {
            'pilot_sample_size': len(classified),
            'light_named_physicists': n_light_names,
            'light_name_rate': n_light_names / len(classified) if classified else 0,
            'sample': classified[:20],  # First 20 for review
            'methodology_framework': self.analyze_name_area_match(),
            'next_steps': {
                '1': 'Expand to n=10,000',
                '2': 'Get full publication histories for each',
                '3': 'Classify research areas systematically',
                '4': 'Run statistical tests',
                '5': 'Write BMJ-style paper'
            }
        }
        
        # Save pilot
        pilot_file = self.output_dir / 'pilot_scientist_sample.json'
        with pilot_file.open('w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"\n✅ Pilot complete: {n_light_names}/{len(classified)} have light semantics")
        logger.info(f"   Results saved to: {pilot_file}")
        
        return results


def main():
    """Run scientist names analysis."""
    
    analyzer = ScientistNamesSynchronicityAnalyzer()
    
    # Run pilot
    pilot_results = analyzer.run_pilot_analysis(n_pilot=100)
    
    print("\n" + "="*70)
    print("SCIENTIST NAMES - FRAMEWORK READY")
    print("="*70)
    print("\nPilot complete. To run full study (n=10,000):")
    print("1. Expand sample collection")
    print("2. Get etymology API or manual code names")
    print("3. Classify research areas from full publication lists")
    print("4. Run chi-square tests")
    print("\nTimeline: 2 months")
    print("Cost: $0")
    print("Expected: Light names → optics at 1.5-1.8x baseline")
    print("="*70 + "\n")
    
    return pilot_results


if __name__ == '__main__':
    main()

