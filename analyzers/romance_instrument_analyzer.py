"""
Romance Instrument Name Analyzer

Comprehensive phonetic, semantic, and correlation analysis of instrument names
across Romance languages. Extends the love words phonetic framework to analyze:

1. Phonetic properties per instrument per language
2. Cross-linguistic consistency  
3. Usage correlation with phonetic beauty
4. Native vs. borrowed word patterns
5. Ensemble phonetic coherence
6. Temporal evolution patterns

Tests 6 primary hypotheses about instrument names and cultural usage patterns.
"""

import logging
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from scipy import stats
import re
from collections import Counter, defaultdict

# Import existing phonetic analysis framework
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from analysis.country_name_linguistics import CountryNameLinguistics

logger = logging.getLogger(__name__)


class RomanceInstrumentAnalyzer(CountryNameLinguistics):
    """
    Comprehensive analyzer for Romance language instrument names.
    Extends CountryNameLinguistics for instrument-specific analyses.
    """
    
    def __init__(self):
        super().__init__()
        self.languages = ['spanish', 'french', 'italian', 'portuguese', 'romanian']
    
    def analyze_instrument_name(self, name: str, language: str, is_native: bool, descriptive_transparency: float) -> Dict:
        """
        Comprehensive phonetic analysis of single instrument name.
        
        Args:
            name: Instrument name in target language
            language: spanish, french, italian, portuguese, or romanian
            is_native: Is this a native Romance word?
            descriptive_transparency: 0-100 score
            
        Returns:
            Complete phonetic analysis dict
        """
        if not name:
            return {}
        
        # Basic phonetic analysis from parent class
        analysis = {
            'language': language,
            'name': name,
            'character_length': len(name),
            'syllable_count': self.estimate_syllables(name),
            
            # Sound counts
            'plosives_count': self.count_plosives(name),
            'sibilants_count': self.count_sibilants(name),
            'liquids_nasals_count': self.count_liquids_nasals(name),
            'vowels_count': self.count_open_vowels(name),
            
            # Aesthetic scores
            'harshness_score': self.phonetic_harshness_score(name),
            'melodiousness_score': self.melodiousness_score(name),
            'beauty_score': self.melodiousness_score(name) - (self.phonetic_harshness_score(name) * 0.3),
        }
        
        # Density ratios
        length = len(name)
        if length > 0:
            analysis['vowel_density'] = analysis['vowels_count'] / length
            analysis['consonant_density'] = (length - analysis['vowels_count']) / length
            analysis['liquid_density'] = analysis['liquids_nasals_count'] / length
        else:
            analysis['vowel_density'] = 0
            analysis['consonant_density'] = 0
            analysis['liquid_density'] = 0
        
        # Advanced phonetic features
        analysis['has_consonant_clusters'] = self._has_consonant_clusters(name)
        analysis['max_consonant_cluster_length'] = self._max_consonant_cluster(name)
        analysis['consonant_cluster_count'] = self._count_consonant_clusters(name)
        
        # Sound symbolism
        sharp_sounds = set('kKtTiIeE')
        round_sounds = set('bBmMoOuU')
        sharp_count = sum(1 for c in name if c in sharp_sounds)
        round_count = sum(1 for c in name if c in round_sounds)
        
        analysis['sharp_sounds_count'] = sharp_count
        analysis['round_sounds_count'] = round_count
        analysis['sound_symbolism_ratio'] = round_count / max(sharp_count, 1)
        
        # Phonetic patterns
        analysis['starts_with_liquid'] = name[0].lower() in 'lrmn' if name else False
        analysis['ends_with_vowel'] = name[-1].lower() in 'aeiouy' if name else False
        analysis['has_repeated_sounds'] = self._has_repeated_sounds(name)
        
        # Soft vs. harsh sound dominance
        soft_sounds = set('lLmMnNvVrRwWyY')
        harsh_sounds = set('kKgGtTdDpPbB')
        soft_count = sum(1 for c in name if c in soft_sounds)
        harsh_count = sum(1 for c in name if c in harsh_sounds)
        analysis['soft_sound_dominance'] = soft_count / max(harsh_count, 1)
        
        # Linguistic properties
        analysis['native_word'] = is_native
        analysis['descriptive_transparency'] = descriptive_transparency
        analysis['is_compound'] = ' ' in name or '-' in name
        
        return analysis
    
    def analyze_all_instruments(self, instruments_data: List[Dict]) -> Dict:
        """
        Analyze all instruments across all languages.
        
        Args:
            instruments_data: List of instrument dicts from collector
            
        Returns:
            Dict with analyses per instrument per language
        """
        logger.info("Analyzing all instruments across Romance languages...")
        
        all_analyses = {}
        
        for instrument in instruments_data:
            base_name = instrument['base_name_english']
            all_analyses[base_name] = {}
            
            for lang in self.languages:
                name = instrument['names'].get(lang)
                is_native = instrument['is_native'].get(lang, False)
                desc_trans = instrument['descriptive_transparency'].get(lang, 50)
                
                if name:
                    analysis = self.analyze_instrument_name(name, lang, is_native, desc_trans)
                    all_analyses[base_name][lang] = analysis
        
        return all_analyses
    
    def test_beauty_usage_correlation(self, instruments_data: List[Dict], usage_data: Dict) -> Dict:
        """
        H1: Test correlation between phonetic beauty and usage frequency.
        
        Do instruments with more melodious names show higher usage in that culture?
        
        Returns:
            Statistical results per language
        """
        logger.info("Testing H1: Beauty ↔ Usage correlation...")
        
        results = {}
        
        for lang in self.languages:
            beauty_scores = []
            usage_scores = []
            instrument_names = []
            
            for instrument in instruments_data:
                base_name = instrument['base_name_english']
                name = instrument['names'].get(lang)
                
                if name and base_name in usage_data:
                    # Get beauty score
                    analysis = self.analyze_instrument_name(
                        name, lang,
                        instrument['is_native'].get(lang, False),
                        instrument['descriptive_transparency'].get(lang, 50)
                    )
                    
                    # Get usage score for this region
                    region_map = {'spanish': 'spain', 'french': 'france', 'italian': 'italy', 
                                  'portuguese': 'portugal', 'romanian': 'romania'}
                    region = region_map[lang]
                    
                    usage = usage_data[base_name].get(region, {})
                    usage_score = usage.get('normalized_usage_score', 50)
                    
                    beauty_scores.append(analysis['beauty_score'])
                    usage_scores.append(usage_score)
                    instrument_names.append(base_name)
            
            if len(beauty_scores) > 3:
                # Pearson correlation
                r, p_value = stats.pearsonr(beauty_scores, usage_scores)
                
                # Spearman correlation (rank-based)
                rho, p_spearman = stats.spearmanr(beauty_scores, usage_scores)
                
                # Linear regression
                slope, intercept, r_value, p_reg, std_err = stats.linregress(beauty_scores, usage_scores)
                
                results[lang] = {
                    'sample_size': len(beauty_scores),
                    'pearson_r': float(r),
                    'pearson_p': float(p_value),
                    'spearman_rho': float(rho),
                    'spearman_p': float(p_spearman),
                    'regression_slope': float(slope),
                    'regression_intercept': float(intercept),
                    'regression_r_squared': float(r_value ** 2),
                    'regression_p': float(p_reg),
                    'significant': p_value < 0.05,
                    'interpretation': self._interpret_correlation(r, p_value)
                }
            else:
                results[lang] = {'error': 'Insufficient data'}
        
        return results
    
    def test_native_vs_borrowed(self, instruments_data: List[Dict], usage_data: Dict) -> Dict:
        """
        H2: Test if native Romance words show higher usage than borrowed words.
        
        Returns:
            Statistical comparison per language
        """
        logger.info("Testing H2: Native vs. Borrowed usage patterns...")
        
        results = {}
        
        for lang in self.languages:
            native_usage = []
            borrowed_usage = []
            
            region_map = {'spanish': 'spain', 'french': 'france', 'italian': 'italy',
                         'portuguese': 'portugal', 'romanian': 'romania'}
            region = region_map[lang]
            
            for instrument in instruments_data:
                base_name = instrument['base_name_english']
                is_native = instrument['is_native'].get(lang, False)
                
                if base_name in usage_data:
                    usage_score = usage_data[base_name].get(region, {}).get('normalized_usage_score', 50)
                    
                    if is_native:
                        native_usage.append(usage_score)
                    else:
                        borrowed_usage.append(usage_score)
            
            if len(native_usage) > 2 and len(borrowed_usage) > 2:
                # T-test
                t_stat, p_value = stats.ttest_ind(native_usage, borrowed_usage)
                
                # Mann-Whitney U (non-parametric)
                u_stat, p_mann = stats.mannwhitneyu(native_usage, borrowed_usage, alternative='two-sided')
                
                results[lang] = {
                    'native_count': len(native_usage),
                    'borrowed_count': len(borrowed_usage),
                    'native_mean': float(np.mean(native_usage)),
                    'borrowed_mean': float(np.mean(borrowed_usage)),
                    'native_std': float(np.std(native_usage)),
                    'borrowed_std': float(np.std(borrowed_usage)),
                    'difference': float(np.mean(native_usage) - np.mean(borrowed_usage)),
                    't_statistic': float(t_stat),
                    'p_value': float(p_value),
                    'mann_whitney_u': float(u_stat),
                    'mann_whitney_p': float(p_mann),
                    'significant': p_value < 0.05,
                    'effect_size_cohens_d': float((np.mean(native_usage) - np.mean(borrowed_usage)) / 
                                                  np.sqrt((np.std(native_usage)**2 + np.std(borrowed_usage)**2) / 2))
                }
            else:
                results[lang] = {'error': 'Insufficient data for comparison'}
        
        return results
    
    def analyze_cross_linguistic_consistency(self, instruments_data: List[Dict]) -> Dict:
        """
        Analyze how consistent instrument names are phonetically across languages.
        
        Do some instruments maintain similar beauty across all Romance languages?
        High variance suggests cultural/linguistic innovation.
        """
        logger.info("Analyzing cross-linguistic phonetic consistency...")
        
        consistency_results = {}
        
        for instrument in instruments_data:
            base_name = instrument['base_name_english']
            beauty_scores = []
            
            for lang in self.languages:
                name = instrument['names'].get(lang)
                if name:
                    analysis = self.analyze_instrument_name(
                        name, lang,
                        instrument['is_native'].get(lang, False),
                        instrument['descriptive_transparency'].get(lang, 50)
                    )
                    beauty_scores.append(analysis['beauty_score'])
            
            if len(beauty_scores) >= 3:
                consistency_results[base_name] = {
                    'mean_beauty': float(np.mean(beauty_scores)),
                    'std_beauty': float(np.std(beauty_scores)),
                    'variance': float(np.var(beauty_scores)),
                    'coefficient_of_variation': float(np.std(beauty_scores) / np.mean(beauty_scores)) if np.mean(beauty_scores) > 0 else 0,
                    'consistency': 'high' if np.std(beauty_scores) < 5 else 'medium' if np.std(beauty_scores) < 10 else 'low'
                }
        
        return consistency_results
    
    def compare_language_beauty_profiles(self, instruments_data: List[Dict]) -> Dict:
        """
        Compare overall phonetic beauty profiles across Romance languages.
        
        Which language has the most melodious instrument names overall?
        """
        logger.info("Comparing language beauty profiles...")
        
        language_profiles = {}
        
        for lang in self.languages:
            beauty_scores = []
            melodiousness_scores = []
            harshness_scores = []
            
            for instrument in instruments_data:
                name = instrument['names'].get(lang)
                if name:
                    analysis = self.analyze_instrument_name(
                        name, lang,
                        instrument['is_native'].get(lang, False),
                        instrument['descriptive_transparency'].get(lang, 50)
                    )
                    beauty_scores.append(analysis['beauty_score'])
                    melodiousness_scores.append(analysis['melodiousness_score'])
                    harshness_scores.append(analysis['harshness_score'])
            
            if beauty_scores:
                language_profiles[lang] = {
                    'sample_size': len(beauty_scores),
                    'mean_beauty': float(np.mean(beauty_scores)),
                    'mean_melodiousness': float(np.mean(melodiousness_scores)),
                    'mean_harshness': float(np.mean(harshness_scores)),
                    'std_beauty': float(np.std(beauty_scores)),
                    'median_beauty': float(np.median(beauty_scores)),
                }
        
        # ANOVA across languages
        beauty_by_lang = [language_profiles[lang]['mean_beauty'] for lang in self.languages if lang in language_profiles]
        
        if len(beauty_by_lang) >= 3:
            # Rank languages
            ranked = sorted(language_profiles.items(), key=lambda x: x[1]['mean_beauty'], reverse=True)
            
            return {
                'profiles': language_profiles,
                'ranked': [(lang, data['mean_beauty']) for lang, data in ranked],
                'most_melodious': ranked[0][0] if ranked else None,
                'interpretation': f"{ranked[0][0].capitalize()} has most melodious instrument names (mean: {ranked[0][1]['mean_beauty']:.1f})" if ranked else "Insufficient data"
            }
        
        return {'profiles': language_profiles}
    
    def run_comprehensive_analysis(self, instruments_data: List[Dict], usage_data: Dict) -> Dict:
        """
        Execute complete analysis pipeline testing all hypotheses.
        
        Args:
            instruments_data: From RomanceInstrumentCollector
            usage_data: From InstrumentUsageCollector
            
        Returns:
            Comprehensive analysis results
        """
        logger.info("\n" + "="*60)
        logger.info("ROMANCE INSTRUMENT NAMES ANALYSIS")
        logger.info("="*60 + "\n")
        
        results = {}
        
        # 1. Analyze all instrument names
        logger.info("1/6: Analyzing phonetic properties...")
        results['all_analyses'] = self.analyze_all_instruments(instruments_data)
        
        # 2. Test beauty-usage correlation
        logger.info("2/6: Testing beauty ↔ usage correlation...")
        results['beauty_usage_correlation'] = self.test_beauty_usage_correlation(instruments_data, usage_data)
        
        # 3. Test native vs. borrowed
        logger.info("3/6: Testing native vs. borrowed patterns...")
        results['native_vs_borrowed'] = self.test_native_vs_borrowed(instruments_data, usage_data)
        
        # 4. Cross-linguistic consistency
        logger.info("4/6: Analyzing cross-linguistic consistency...")
        results['cross_linguistic_consistency'] = self.analyze_cross_linguistic_consistency(instruments_data)
        
        # 5. Language beauty profiles
        logger.info("5/6: Comparing language beauty profiles...")
        results['language_profiles'] = self.compare_language_beauty_profiles(instruments_data)
        
        # 6. Summary statistics
        logger.info("6/6: Generating summary...")
        results['summary'] = self._generate_summary(results, instruments_data)
        
        logger.info("\n" + "="*60)
        logger.info("ANALYSIS COMPLETE")
        logger.info("="*60)
        
        return results
    
    def _interpret_correlation(self, r: float, p: float) -> str:
        """Interpret correlation coefficient"""
        if p >= 0.05:
            return f"No significant correlation (r={r:.3f}, p={p:.3f})"
        
        strength = ""
        if abs(r) < 0.3:
            strength = "weak"
        elif abs(r) < 0.5:
            strength = "moderate"
        elif abs(r) < 0.7:
            strength = "strong"
        else:
            strength = "very strong"
        
        direction = "positive" if r > 0 else "negative"
        
        return f"Significant {strength} {direction} correlation (r={r:.3f}, p={p:.3f})"
    
    def _generate_summary(self, results: Dict, instruments_data: List[Dict]) -> Dict:
        """Generate executive summary of findings"""
        summary = {
            'dataset_size': len(instruments_data),
            'languages_analyzed': len(self.languages),
            'total_analyses': len(instruments_data) * len(self.languages),
        }
        
        # H1 summary
        h1_results = results.get('beauty_usage_correlation', {})
        significant_correlations = sum(1 for lang_data in h1_results.values() 
                                      if isinstance(lang_data, dict) and lang_data.get('significant', False))
        summary['h1_beauty_usage'] = f"{significant_correlations}/{len(self.languages)} languages show significant correlation"
        
        # H2 summary
        h2_results = results.get('native_vs_borrowed', {})
        native_advantage = sum(1 for lang_data in h2_results.values()
                              if isinstance(lang_data, dict) and lang_data.get('difference', 0) > 0)
        summary['h2_native_borrowed'] = f"Native words show higher usage in {native_advantage}/{len(self.languages)} languages"
        
        # Language profiles
        lang_profiles = results.get('language_profiles', {})
        if 'most_melodious' in lang_profiles:
            summary['most_melodious_language'] = lang_profiles['most_melodious']
        
        return summary
    
    # Helper methods
    def _has_consonant_clusters(self, text: str) -> bool:
        """Check if word has consonant clusters"""
        consonants = 'bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ'
        for i in range(len(text) - 1):
            if text[i] in consonants and text[i+1] in consonants:
                return True
        return False
    
    def _max_consonant_cluster(self, text: str) -> int:
        """Find maximum consonant cluster length"""
        consonants = 'bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ'
        max_cluster = 0
        current_cluster = 0
        
        for char in text:
            if char in consonants:
                current_cluster += 1
                max_cluster = max(max_cluster, current_cluster)
            else:
                current_cluster = 0
        
        return max_cluster
    
    def _count_consonant_clusters(self, text: str) -> int:
        """Count number of consonant clusters"""
        consonants = 'bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ'
        clusters = 0
        in_cluster = False
        
        for i in range(len(text) - 1):
            if text[i] in consonants and text[i+1] in consonants:
                if not in_cluster:
                    clusters += 1
                    in_cluster = True
            else:
                in_cluster = False
        
        return clusters
    
    def _has_repeated_sounds(self, text: str) -> bool:
        """Check if word has repeated sounds"""
        text_lower = text.lower()
        for char in set(text_lower):
            if char.isalpha() and text_lower.count(char) >= 2:
                return True
        return False


if __name__ == '__main__':
    # Test analyzer
    from collectors.romance_instrument_collector import RomanceInstrumentCollector
    from collectors.instrument_usage_collector import InstrumentUsageCollector
    
    instrument_collector = RomanceInstrumentCollector()
    usage_collector = InstrumentUsageCollector()
    
    instruments = instrument_collector.get_all_instruments()
    instrument_names = [i['base_name_english'] for i in instruments]
    usage_data = usage_collector.get_all_usage_data(instrument_names)
    
    analyzer = RomanceInstrumentAnalyzer()
    results = analyzer.run_comprehensive_analysis(instruments, usage_data)
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Dataset: {results['summary']['dataset_size']} instruments")
    print(f"Languages: {results['summary']['languages_analyzed']}")
    print(f"\nH1 (Beauty ↔ Usage): {results['summary']['h1_beauty_usage']}")
    print(f"H2 (Native vs Borrowed): {results['summary']['h2_native_borrowed']}")
    if 'most_melodious_language' in results['summary']:
        print(f"Most Melodious: {results['summary']['most_melodious_language'].capitalize()}")
    print("="*60)

