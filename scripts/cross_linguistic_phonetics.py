"""Test 1-Alt: Cross-Linguistic Phonetic Analysis

This script tests whether nominative effects TRANSFORM (not disappear) across languages.
If language is substrate, effects should shift based on linguistic context.

Tests hurricane names in 4 linguistic contexts:
1. English (original analysis)
2. Spanish (Mexico, Caribbean)
3. Tagalog (Philippines)
4. Japanese (Japan)

**Hypothesis:** Phonetic valence shifts with linguistic context
- Same phoneme has different "harshness" in different languages
- Effects persist but transform predictably
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
from core.config import Config
from core.models import db, Hurricane
import pandas as pd
import numpy as np
from scipy import stats


class CrossLinguisticPhoneticAnalyzer:
    """Analyze how phonetic features transform across languages."""
    
    def __init__(self):
        self.app = Flask(__name__)
        self.app.config.from_object(Config)
        db.init_app(self.app)
        
        # Phonetic feature mappings by language
        self.phonetic_systems = {
            'english': {
                'harsh_consonants': ['k', 't', 'p', 'sh', 'ch'],
                'soft_consonants': ['l', 'r', 'm', 'n', 'w'],
                'threatening_clusters': ['kr', 'tr', 'str'],
                'melodic_vowels': ['a', 'o', 'i'],
                'cultural_harshness_multiplier': 1.0
            },
            'spanish': {
                'harsh_consonants': ['j', 'rr', 'x'],  # jota, rolled r are harsh in Spanish
                'soft_consonants': ['l', 'n', 'ñ', 'y'],
                'threatening_clusters': ['gr', 'tr', 'br'],
                'melodic_vowels': ['a', 'e', 'i', 'o'],  # All vowels melodic
                'cultural_harshness_multiplier': 0.85  # Generally softer perception
            },
            'tagalog': {
                'harsh_consonants': ['k', 'g', 't'],
                'soft_consonants': ['l', 'm', 'n', 'ng'],
                'threatening_clusters': ['gl', 'kl'],
                'melodic_vowels': ['a', 'i', 'o'],
                'cultural_harshness_multiplier': 0.75  # Softer language overall
            },
            'japanese': {
                'harsh_consonants': ['k', 'g', 'z'],
                'soft_consonants': ['n', 'm', 'r', 'y', 'w'],
                'threatening_clusters': [],  # Japanese has no consonant clusters
                'melodic_vowels': ['a', 'i', 'u', 'e', 'o'],  # All vowels
                'cultural_harshness_multiplier': 0.65  # Very soft phonology
            }
        }
        
    def run_cross_linguistic_analysis(self) -> Dict:
        """Execute cross-linguistic hurricane name analysis."""
        
        print("="*80)
        print("CROSS-LINGUISTIC PHONETIC ANALYSIS")
        print("Test 1-Alt: Do Effects Transform Across Languages?")
        print("="*80)
        print()
        
        with self.app.app_context():
            # Get hurricane data
            print("[1/5] Loading hurricane casualty data...")
            hurricanes = self._load_hurricane_data()
            
            # Analyze in each language context
            print("\n[2/5] Computing phonetic features in 4 languages...")
            results = {}
            for lang in ['english', 'spanish', 'tagalog', 'japanese']:
                print(f"\n   Analyzing in {lang.title()} context...")
                results[lang] = self._analyze_in_language(hurricanes, lang)
            
            # Compare across languages
            print("\n[3/5] Comparing effects across languages...")
            comparison = self._cross_language_comparison(results)
            
            # Test transformation hypothesis
            print("\n[4/5] Testing transformation hypothesis...")
            hypothesis_test = self._test_transformation_hypothesis(results)
            
            # Generate report
            print("\n[5/5] Generating cross-linguistic report...")
            final_results = {
                'by_language': results,
                'comparison': comparison,
                'hypothesis_test': hypothesis_test,
                'conclusion': self._generate_conclusion(hypothesis_test)
            }
            
            self._save_results(final_results)
        
        print("\n" + "="*80)
        print("CROSS-LINGUISTIC ANALYSIS COMPLETE")
        print("="*80)
        
        return final_results
    
    def _load_hurricane_data(self) -> pd.DataFrame:
        """Load hurricanes with casualty data."""
        hurricanes = Hurricane.query.filter(
            Hurricane.year >= 1950,
            Hurricane.deaths.isnot(None)
        ).all()
        
        data = []
        for h in hurricanes:
            data.append({
                'name': h.name,
                'year': h.year,
                'deaths': h.deaths or 0,
                'log_deaths': np.log1p(h.deaths or 0),
                'has_casualties': 1 if (h.deaths and h.deaths > 0) else 0,
                'max_wind_mph': h.max_wind_mph or 100,
                'category': h.saffir_simpson_category or 2
            })
        
        df = pd.DataFrame(data)
        print(f"   Loaded {len(df)} hurricanes with casualty data")
        return df
    
    def _analyze_in_language(self, df: pd.DataFrame, language: str) -> Dict:
        """Analyze hurricane names through linguistic lens."""
        
        phonetic_system = self.phonetic_systems[language]
        
        # Compute language-specific harshness for each hurricane
        harshness_scores = []
        for name in df['name']:
            score = self._compute_harshness(name, phonetic_system)
            harshness_scores.append(score)
        
        df_lang = df.copy()
        df_lang[f'harshness_{language}'] = harshness_scores
        
        # Test correlation with casualties
        valid = df_lang[df_lang['deaths'] > 0].copy()
        
        if len(valid) < 15:
            return {
                'language': language,
                'n': len(valid),
                'status': 'insufficient_data'
            }
        
        # Correlation with log deaths
        corr, pval = stats.pearsonr(
            valid[f'harshness_{language}'],
            valid['log_deaths']
        )
        
        # Mean harshness comparison
        high_casualty = valid[valid['deaths'] > valid['deaths'].median()]
        low_casualty = valid[valid['deaths'] <= valid['deaths'].median()]
        
        mean_high = high_casualty[f'harshness_{language}'].mean()
        mean_low = low_casualty[f'harshness_{language}'].mean()
        diff = mean_high - mean_low
        
        # t-test
        t_stat, t_pval = stats.ttest_ind(
            high_casualty[f'harshness_{language}'],
            low_casualty[f'harshness_{language}']
        )
        
        result = {
            'language': language,
            'n': int(len(valid)),
            'correlation': float(corr),
            'pvalue': float(pval),
            'mean_harshness_high_casualty': float(mean_high),
            'mean_harshness_low_casualty': float(mean_low),
            'difference': float(diff),
            't_statistic': float(t_stat),
            't_pvalue': float(t_pval),
            'significant': bool(pval < 0.05),
            'effect_direction': 'positive' if corr > 0 else 'negative'
        }
        
        print(f"      r = {corr:.3f}, p = {pval:.4f}")
        
        return result
    
    def _compute_harshness(self, name: str, phonetic_system: Dict) -> float:
        """Compute language-specific harshness score."""
        name_lower = name.lower()
        score = 50.0  # Base score
        
        # Count harsh consonants (language-specific)
        for consonant in phonetic_system['harsh_consonants']:
            count = name_lower.count(consonant)
            score += count * 10
        
        # Count soft consonants (reduce harshness)
        for consonant in phonetic_system['soft_consonants']:
            count = name_lower.count(consonant)
            score -= count * 5
        
        # Check for threatening clusters
        for cluster in phonetic_system['threatening_clusters']:
            if cluster in name_lower:
                score += 15
        
        # Vowel ratio (more vowels = softer)
        vowels = sum(name_lower.count(v) for v in phonetic_system['melodic_vowels'])
        vowel_ratio = vowels / len(name) if len(name) > 0 else 0
        score -= vowel_ratio * 20
        
        # Apply cultural multiplier
        score *= phonetic_system['cultural_harshness_multiplier']
        
        # Normalize to 0-100
        score = max(0, min(100, score))
        
        return score
    
    def _cross_language_comparison(self, results: Dict) -> Dict:
        """Compare effects across languages."""
        
        # Extract correlations
        correlations = {}
        for lang, result in results.items():
            if result.get('correlation'):
                correlations[lang] = result['correlation']
        
        if len(correlations) < 3:
            return {'status': 'insufficient_languages'}
        
        # Test if correlations differ significantly
        # Convert correlations to z-scores (Fisher transformation)
        z_scores = {lang: np.arctanh(r) for lang, r in correlations.items()}
        
        # Compare English to other languages
        comparisons = {}
        if 'english' in z_scores:
            for lang, z in z_scores.items():
                if lang != 'english':
                    z_diff = abs(z - z_scores['english'])
                    # Approximate p-value for z-score difference
                    p = 2 * (1 - stats.norm.cdf(abs(z_diff)))
                    comparisons[f'english_vs_{lang}'] = {
                        'z_difference': float(z_diff),
                        'pvalue': float(p),
                        'significantly_different': bool(p < 0.05)
                    }
        
        return {
            'correlations_by_language': correlations,
            'mean_correlation': float(np.mean(list(correlations.values()))),
            'std_correlation': float(np.std(list(correlations.values()))),
            'cross_language_comparisons': comparisons,
            'correlation_range': [float(min(correlations.values())), 
                                 float(max(correlations.values()))]
        }
    
    def _test_transformation_hypothesis(self, results: Dict) -> Dict:
        """Test if effects transform (not disappear) across languages."""
        
        # Count languages with significant effects
        significant_count = sum(
            1 for r in results.values() 
            if r.get('significant', False)
        )
        total_count = sum(
            1 for r in results.values()
            if r.get('correlation') is not None
        )
        
        # Test if proportion significant > chance
        if total_count > 0:
            prop_significant = significant_count / total_count
            # Binomial test against null (p=0.05 by chance)
            try:
                from scipy.stats import binomtest
                binom_result = binomtest(significant_count, total_count, 0.05, alternative='greater')
                binom_p = binom_result.pvalue
            except ImportError:
                from scipy.stats import binom_test
                binom_p = binom_test(significant_count, total_count, 0.05, alternative='greater')
        else:
            prop_significant = 0
            binom_p = 1.0
        
        # Check if all effects in same direction (even if magnitudes differ)
        effects = [r.get('effect_direction') for r in results.values() if r.get('effect_direction')]
        consistent_direction = len(set(effects)) == 1 if effects else False
        
        # Hypothesis outcomes
        if prop_significant > 0.5 and consistent_direction:
            conclusion = "TRANSFORMATION: Effects persist across languages in same direction"
            interpretation = "Supports substrate claim: phonetic effects universal but context-modulated"
        elif prop_significant > 0.5:
            conclusion = "MIXED: Effects persist but directions vary"
            interpretation = "Partial support: phonetics matter but cultural context flips valence"
        else:
            conclusion = "LANGUAGE-SPECIFIC: Effects don't replicate cross-linguistically"
            interpretation = "English-specific effects: weakens universal substrate claim"
        
        return {
            'significant_languages': int(significant_count),
            'total_languages': int(total_count),
            'proportion_significant': float(prop_significant),
            'binomial_pvalue': float(binom_p),
            'consistent_direction': bool(consistent_direction),
            'conclusion': conclusion,
            'interpretation': interpretation,
            'hypothesis_supported': bool(prop_significant > 0.5)
        }
    
    def _generate_conclusion(self, hypothesis_test: Dict) -> str:
        """Generate final conclusion."""
        if hypothesis_test['hypothesis_supported']:
            return ("✓ CROSS-LINGUISTIC EFFECTS CONFIRMED: Nominative patterns persist across "
                   "languages, supporting universal substrate claim with cultural modulation.")
        else:
            return ("✗ ENGLISH-SPECIFIC EFFECTS: Patterns don't replicate cross-linguistically, "
                   "suggesting cultural construction rather than universal substrate.")
    
    def _save_results(self, results: Dict):
        """Save cross-linguistic analysis results."""
        output_dir = Path(__file__).parent.parent / 'data' / 'cross_linguistic'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save JSON
        json_path = output_dir / 'cross_linguistic_results.json'
        with open(json_path, 'w') as f:
            json.dump({
                'analysis': 'Cross-Linguistic Phonetic Effects',
                'date': datetime.now().isoformat(),
                'languages': ['English', 'Spanish', 'Tagalog', 'Japanese'],
                'results': results
            }, f, indent=2)
        
        print(f"\n✓ Results saved: {json_path}")


def main():
    """Run cross-linguistic analysis."""
    analyzer = CrossLinguisticPhoneticAnalyzer()
    results = analyzer.run_cross_linguistic_analysis()
    
    # Print summary
    print("\nSUMMARY:")
    print(f"  Conclusion: {results['conclusion']}")
    if 'hypothesis_test' in results:
        print(f"  Interpretation: {results['hypothesis_test']['interpretation']}")


if __name__ == '__main__':
    main()

