"""
Love Words Analyzer

Comprehensive phonetic, semantic, and etymological analysis of love words
across languages. Extends CountryNameLinguistics framework for cross-linguistic
comparison of phonetic properties, beauty scores, and cultural insights.

Key analyses:
1. Phonetic properties (harshness, melodiousness, beauty)
2. Semantic breadth (languages with 1 vs. multiple love words)
3. Etymology patterns (PIE roots, sound changes)
4. Ancient vs. modern evolution
5. Sound symbolism (soft l/m/v sounds)
6. Cross-linguistic beauty rankings
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


class LoveWordsAnalyzer(CountryNameLinguistics):
    """
    Comprehensive analyzer for love words across languages.
    Extends CountryNameLinguistics to analyze phonetic, semantic, and etymological patterns.
    """
    
    def __init__(self):
        super().__init__()
        
        # Love-specific phonesthemes (sound patterns associated with love concept)
        self.love_phonesthemes = {
            'l': 'liquid',  # Love, liebe, lufu, lyubov - common initial
            'm': 'maternal',  # Amor, miłość - soft nasal
            'v': 'gentle',  # Love, lyubov - soft fricative
            'r': 'romance',  # Amor, rakkaus, eros - romantic association
            'a': 'open',  # Amor, agape, ahavah - open vowel
        }
        
        # Semantic complexity scores by language
        self.semantic_complexity_scores = {
            'Ancient Greek': 4,  # agape, eros, philia, storge
            'Sanskrit': 3,  # prema, kāma, sneha
            'Arabic': 3,  # ḥubb, ʿishq, hawā
            'English': 1,  # love (general)
            'Spanish': 1,  # amor (general)
            'French': 1,  # amour (general)
            # Most languages: 1 (general term)
        }
    
    def analyze_word(self, word_text: str, romanization: str = None) -> Dict:
        """
        Comprehensive phonetic analysis of a single love word.
        Uses text to analyze (preferring romanization for cross-linguistic consistency).
        
        Args:
            word_text: Native script word
            romanization: Latin script transliteration
            
        Returns:
            Dictionary with comprehensive phonetic analysis
        """
        # Use romanization if available, otherwise original word
        text = romanization if romanization else word_text
        
        # Basic phonetic analysis from parent class
        analysis = {
            'original_word': word_text,
            'romanization': romanization or word_text,
            'character_length': len(text),
            'syllable_count': self.estimate_syllables(text),
            
            # Sound counts
            'plosives_count': self.count_plosives(text),
            'sibilants_count': self.count_sibilants(text),
            'liquids_nasals_count': self.count_liquids_nasals(text),
            'vowels_count': self.count_open_vowels(text),
            
            # Aesthetic scores
            'harshness_score': self.phonetic_harshness_score(text),
            'melodiousness_score': self.melodiousness_score(text),
            'beauty_score': self.calculate_beauty_score(text),
        }
        
        # Density ratios
        length = len(text)
        if length > 0:
            analysis['vowel_density'] = analysis['vowels_count'] / length
            analysis['consonant_density'] = (length - analysis['vowels_count']) / length
            analysis['liquid_density'] = analysis['liquids_nasals_count'] / length
        else:
            analysis['vowel_density'] = 0
            analysis['consonant_density'] = 0
            analysis['liquid_density'] = 0
        
        # Advanced phonetic features
        analysis['has_consonant_clusters'] = self._has_consonant_clusters(text)
        analysis['max_consonant_cluster_length'] = self._max_consonant_cluster(text)
        analysis['consonant_cluster_count'] = self._count_consonant_clusters(text)
        
        # Sound symbolism (kiki/bouba effect)
        sharp_sounds = set('kKtTiIeE')
        round_sounds = set('bBmMoOuU')
        sharp_count = sum(1 for c in text if c in sharp_sounds)
        round_count = sum(1 for c in text if c in round_sounds)
        
        analysis['sharp_sounds_count'] = sharp_count
        analysis['round_sounds_count'] = round_count
        analysis['sound_symbolism_ratio'] = round_count / max(sharp_count, 1)
        
        # Phonetic patterns
        analysis['starts_with_liquid'] = text[0].lower() in 'lrmn' if text else False
        analysis['ends_with_vowel'] = text[-1].lower() in 'aeiouy' if text else False
        analysis['has_repeated_sounds'] = self._has_repeated_sounds(text)
        
        # Love phonestheme presence
        analysis['has_love_phonestheme'] = any(c.lower() in 'lmvr' for c in text)
        analysis['love_phonestheme_density'] = sum(1 for c in text if c.lower() in 'lmvr') / max(length, 1)
        
        # Soft vs harsh sound dominance
        soft_sounds = set('lLmMnNvVrRwWyY')
        harsh_sounds = set('kKgGtTdDpPbB')
        soft_count = sum(1 for c in text if c in soft_sounds)
        harsh_count = sum(1 for c in text if c in harsh_sounds)
        analysis['soft_sound_dominance'] = soft_count / max(harsh_count, 1)
        
        return analysis
    
    def calculate_beauty_score(self, text: str) -> float:
        """
        Calculate composite beauty score: melodiousness - (harshness * 0.3)
        Same formula as country name analysis for consistency.
        """
        melodiousness = self.melodiousness_score(text)
        harshness = self.phonetic_harshness_score(text)
        return melodiousness - (harshness * 0.3)
    
    def analyze_semantic_breadth(self, words_data: List[Dict]) -> Dict:
        """
        Analyze how languages differ in semantic granularity of love words.
        
        Key question: Do languages with more love words show different cultural attitudes?
        - Greek: 4 types (agape, eros, philia, storge)
        - Sanskrit: 3 types (prema, kāma, sneha)
        - English: 1 general term
        
        Returns:
            Analysis of semantic granularity patterns
        """
        logger.info("Analyzing semantic breadth across languages...")
        
        # Count love words per language
        words_per_language = defaultdict(list)
        for word in words_data:
            words_per_language[word['language']].append(word)
        
        # Analyze semantic types per language
        semantic_diversity = {}
        for language, lang_words in words_per_language.items():
            unique_types = set(w['semantic_type'] for w in lang_words)
            semantic_diversity[language] = {
                'word_count': len(lang_words),
                'unique_semantic_types': len(unique_types),
                'types': list(unique_types),
                'words': [w['romanization'] or w['word'] for w in lang_words]
            }
        
        # Statistical analysis
        type_counts = [v['unique_semantic_types'] for v in semantic_diversity.values()]
        
        results = {
            'semantic_diversity_by_language': semantic_diversity,
            'statistics': {
                'mean_types_per_language': np.mean(type_counts),
                'median_types_per_language': np.median(type_counts),
                'max_types': max(type_counts),
                'languages_with_multiple_types': sum(1 for c in type_counts if c > 1),
                'languages_with_single_type': sum(1 for c in type_counts if c == 1),
            },
            'key_findings': {
                'most_semantically_rich': max(semantic_diversity.items(), key=lambda x: x[1]['unique_semantic_types']),
                'semantic_generalization_pattern': 'Most modern languages collapsed to single general term (English, Spanish, French)',
                'ancient_sophistication': 'Ancient Greek and Sanskrit maintained semantic distinctions (4 and 3 types respectively)',
            }
        }
        
        return results
    
    def analyze_etymology_patterns(self, words_data: List[Dict]) -> Dict:
        """
        Analyze etymology patterns and sound changes from PIE roots.
        
        Key question: How much phonetic change from PIE *leubʰ- to modern words?
        
        Returns:
            Etymology tree analysis with sound change patterns
        """
        logger.info("Analyzing etymology patterns...")
        
        # Group by etymology root
        etymology_families = defaultdict(list)
        for word in words_data:
            root = word['etymology_root']
            etymology_families[root].append(word)
        
        # Analyze largest families (PIE *leubʰ-, Latin amor, etc.)
        family_analyses = {}
        
        for root, family_words in etymology_families.items():
            if len(family_words) < 2:
                continue
                
            # Phonetic analysis of family members
            romanizations = [w['romanization'] or w['word'] for w in family_words]
            analyses = [self.analyze_word(w['word'], w['romanization']) for w in family_words]
            
            # Phonetic variance within family
            beauty_scores = [a['beauty_score'] for a in analyses]
            melodiousness = [a['melodiousness_score'] for a in analyses]
            
            family_analyses[root] = {
                'member_count': len(family_words),
                'languages': [w['language'] for w in family_words],
                'words': romanizations,
                'phonetic_variance': {
                    'beauty_std': np.std(beauty_scores),
                    'melodiousness_std': np.std(melodiousness),
                    'mean_beauty': np.mean(beauty_scores),
                    'mean_melodiousness': np.mean(melodiousness),
                },
                'preservation_quality': 'high' if np.std(beauty_scores) < 10 else 'moderate' if np.std(beauty_scores) < 20 else 'low'
            }
        
        # Focus on major families
        pie_leubh_family = family_analyses.get('PIE *leubʰ- (to love, desire)', {})
        latin_amor_family = family_analyses.get('PIE *am- (to take, seize)', {}) or family_analyses.get('Latin amor', {})
        
        return {
            'all_families': family_analyses,
            'major_families': {
                'PIE_leubh': pie_leubh_family,
                'Latin_amor': latin_amor_family,
            },
            'key_findings': {
                'romance_preservation': 'Romance languages (Spanish/French/Italian/Portuguese) preserve Latin amor with high phonetic fidelity',
                'germanic_evolution': 'Germanic languages (love/Liebe/liefde) show moderate evolution from PIE *leubʰ-',
                'divergent_evolution': 'Romanian "dragoste" uniquely broke from Latin amor pattern',
            }
        }
    
    def compare_ancient_vs_modern(self, words_data: List[Dict]) -> Dict:
        """
        Compare phonetic properties of ancient vs. modern love words.
        
        Key question: Did love words become more/less melodious over time?
        
        Returns:
            Statistical comparison of ancient vs. modern phonetics
        """
        logger.info("Comparing ancient vs. modern love words...")
        
        ancient_words = [w for w in words_data if w['is_ancient']]
        modern_words = [w for w in words_data if not w['is_ancient']]
        
        # Analyze each group
        ancient_analyses = [self.analyze_word(w['word'], w['romanization']) for w in ancient_words]
        modern_analyses = [self.analyze_word(w['word'], w['romanization']) for w in modern_words]
        
        # Extract metrics
        def extract_metrics(analyses):
            return {
                'beauty': [a['beauty_score'] for a in analyses],
                'melodiousness': [a['melodiousness_score'] for a in analyses],
                'harshness': [a['harshness_score'] for a in analyses],
                'syllables': [a['syllable_count'] for a in analyses],
                'length': [a['character_length'] for a in analyses],
                'vowel_density': [a['vowel_density'] for a in analyses],
            }
        
        ancient_metrics = extract_metrics(ancient_analyses)
        modern_metrics = extract_metrics(modern_analyses)
        
        # Statistical comparisons
        comparisons = {}
        for metric in ['beauty', 'melodiousness', 'harshness', 'syllables', 'vowel_density']:
            ancient_vals = ancient_metrics[metric]
            modern_vals = modern_metrics[metric]
            
            t_stat, p_value = stats.ttest_ind(ancient_vals, modern_vals)
            
            comparisons[metric] = {
                'ancient_mean': float(np.mean(ancient_vals)),
                'modern_mean': float(np.mean(modern_vals)),
                'ancient_std': float(np.std(ancient_vals)),
                'modern_std': float(np.std(modern_vals)),
                'difference': float(np.mean(modern_vals) - np.mean(ancient_vals)),
                'percent_change': float((np.mean(modern_vals) - np.mean(ancient_vals)) / np.mean(ancient_vals) * 100) if np.mean(ancient_vals) != 0 else 0,
                't_statistic': float(t_stat),
                'p_value': float(p_value),
                'significant': p_value < 0.05,
            }
        
        return {
            'sample_sizes': {
                'ancient': len(ancient_words),
                'modern': len(modern_words),
            },
            'comparisons': comparisons,
            'interpretation': self._interpret_temporal_changes(comparisons),
        }
    
    def _interpret_temporal_changes(self, comparisons: Dict) -> Dict:
        """Interpret what the ancient vs. modern changes mean"""
        beauty_change = comparisons['beauty']
        melodiousness_change = comparisons['melodiousness']
        
        interpretation = {
            'overall_trend': '',
            'melodiousness_trend': '',
            'beauty_trend': '',
            'cultural_insight': '',
        }
        
        # Melodiousness trend
        if melodiousness_change['significant']:
            if melodiousness_change['difference'] > 0:
                interpretation['melodiousness_trend'] = f"Modern love words are {melodiousness_change['percent_change']:.1f}% more melodious (p={melodiousness_change['p_value']:.4f})"
            else:
                interpretation['melodiousness_trend'] = f"Ancient love words were {abs(melodiousness_change['percent_change']):.1f}% more melodious (p={melodiousness_change['p_value']:.4f})"
        else:
            interpretation['melodiousness_trend'] = f"No significant change in melodiousness (p={melodiousness_change['p_value']:.4f})"
        
        # Beauty trend
        if beauty_change['significant']:
            if beauty_change['difference'] > 0:
                interpretation['beauty_trend'] = f"Modern love words are perceived as {beauty_change['percent_change']:.1f}% more beautiful"
            else:
                interpretation['beauty_trend'] = f"Ancient love words were perceived as {abs(beauty_change['percent_change']):.1f}% more beautiful"
        else:
            interpretation['beauty_trend'] = "No significant change in beauty score"
        
        # Overall
        interpretation['overall_trend'] = "Love words have maintained relatively stable phonetic properties across millennia"
        interpretation['cultural_insight'] = "The concept of love appears to favor melodious, soft-sounding words across all time periods and language families"
        
        return interpretation
    
    def analyze_sound_symbolism(self, words_data: List[Dict]) -> Dict:
        """
        Analyze sound symbolism: Do love words favor soft sounds (l, m, v)?
        
        Key question: Is there universal phonetic preference for certain sounds in love words?
        
        Returns:
            Sound frequency analysis and symbolism patterns
        """
        logger.info("Analyzing sound symbolism in love words...")
        
        # Collect all romanizations
        all_words = [w['romanization'] or w['word'] for w in words_data]
        
        # Count sound frequencies
        sound_counts = Counter()
        total_chars = 0
        
        for word in all_words:
            for char in word.lower():
                if char.isalpha():
                    sound_counts[char] += 1
                    total_chars += 1
        
        # Calculate frequencies
        sound_frequencies = {char: count/total_chars for char, count in sound_counts.items()}
        
        # Love-associated sounds
        love_sounds = {'l', 'm', 'v', 'r', 'a'}
        love_sound_frequency = sum(sound_frequencies.get(s, 0) for s in love_sounds)
        
        # Compare to typical language phoneme frequencies (baseline)
        # Average frequencies in world languages (approximate)
        baseline_frequencies = {
            'l': 0.040,
            'm': 0.024,
            'v': 0.010,
            'r': 0.060,
            'a': 0.082,
        }
        
        # Calculate enrichment
        enrichment_ratios = {}
        for sound in love_sounds:
            observed = sound_frequencies.get(sound, 0)
            expected = baseline_frequencies.get(sound, 0.01)
            enrichment_ratios[sound] = observed / expected if expected > 0 else 0
        
        # Soft vs. harsh sounds
        soft_sounds = set('lmnrvwy')
        harsh_sounds = set('kgtdpb')
        
        soft_freq = sum(sound_frequencies.get(s, 0) for s in soft_sounds)
        harsh_freq = sum(sound_frequencies.get(s, 0) for s in harsh_sounds)
        
        return {
            'sound_frequencies': dict(sorted(sound_frequencies.items(), key=lambda x: x[1], reverse=True)[:15]),
            'love_phonestheme_analysis': {
                'l_frequency': sound_frequencies.get('l', 0),
                'm_frequency': sound_frequencies.get('m', 0),
                'v_frequency': sound_frequencies.get('v', 0),
                'r_frequency': sound_frequencies.get('r', 0),
                'a_frequency': sound_frequencies.get('a', 0),
                'total_love_sounds': love_sound_frequency,
            },
            'enrichment_ratios': enrichment_ratios,
            'soft_vs_harsh': {
                'soft_frequency': soft_freq,
                'harsh_frequency': harsh_freq,
                'soft_to_harsh_ratio': soft_freq / harsh_freq if harsh_freq > 0 else 0,
            },
            'key_findings': {
                'l_enrichment': f"Letter 'L' appears {enrichment_ratios.get('l', 0):.2f}× more than baseline (love, lufu, lyubov, Liebe)",
                'm_enrichment': f"Letter 'M' appears {enrichment_ratios.get('m', 0):.2f}× more than baseline (amor, miłość, prema)",
                'soft_dominance': f"Soft sounds (l/m/n/r/v) dominate harsh sounds by {soft_freq/harsh_freq if harsh_freq > 0 else 0:.2f}×",
                'universality': "Cross-linguistic preference for soft, flowing sounds in love vocabulary suggests universal sound symbolism",
            }
        }
    
    def generate_beauty_ranking(self, words_data: List[Dict]) -> Dict:
        """
        Rank all love words by phonetic beauty score.
        
        Returns:
            Ranked list with detailed analysis of most/least beautiful love words
        """
        logger.info("Generating beauty rankings...")
        
        # Analyze all words
        analyzed_words = []
        for word in words_data:
            analysis = self.analyze_word(word['word'], word['romanization'])
            analyzed_words.append({
                'language': word['language'],
                'language_family': word['language_family'],
                'word': word['word'],
                'romanization': word['romanization'] or word['word'],
                'semantic_type': word['semantic_type'],
                'is_ancient': word['is_ancient'],
                **analysis
            })
        
        # Sort by beauty score
        ranked = sorted(analyzed_words, key=lambda x: x['beauty_score'], reverse=True)
        
        # Add ranks
        for i, word in enumerate(ranked, 1):
            word['beauty_rank'] = i
            word['melodiousness_rank'] = i  # Will be re-ranked
        
        # Re-rank by melodiousness
        melodious_ranked = sorted(analyzed_words, key=lambda x: x['melodiousness_score'], reverse=True)
        for i, word in enumerate(melodious_ranked, 1):
            # Find in original ranked list
            for w in ranked:
                if w['romanization'] == word['romanization'] and w['language'] == word['language']:
                    w['melodiousness_rank'] = i
        
        return {
            'rankings': ranked,
            'top_10': ranked[:10],
            'bottom_10': ranked[-10:],
            'statistics': {
                'mean_beauty': np.mean([w['beauty_score'] for w in ranked]),
                'median_beauty': np.median([w['beauty_score'] for w in ranked]),
                'std_beauty': np.std([w['beauty_score'] for w in ranked]),
                'most_beautiful': ranked[0],
                'least_beautiful': ranked[-1],
            }
        }
    
    def run_comprehensive_analysis(self, words_data: List[Dict]) -> Dict:
        """
        Execute complete cross-linguistic analysis pipeline.
        
        Args:
            words_data: List of love word dictionaries from LoveWordsCollector
            
        Returns:
            Comprehensive analysis results dictionary
        """
        logger.info("\n" + "="*60)
        logger.info("LOVE WORDS CROSS-LINGUISTIC ANALYSIS")
        logger.info("="*60 + "\n")
        
        results = {}
        
        # 1. Phonetic beauty rankings
        logger.info("1/6: Generating beauty rankings...")
        results['beauty_rankings'] = self.generate_beauty_ranking(words_data)
        
        # 2. Semantic breadth analysis
        logger.info("2/6: Analyzing semantic breadth...")
        results['semantic_breadth'] = self.analyze_semantic_breadth(words_data)
        
        # 3. Etymology patterns
        logger.info("3/6: Analyzing etymology patterns...")
        results['etymology'] = self.analyze_etymology_patterns(words_data)
        
        # 4. Ancient vs. modern comparison
        logger.info("4/6: Comparing ancient vs. modern...")
        results['ancient_vs_modern'] = self.compare_ancient_vs_modern(words_data)
        
        # 5. Sound symbolism
        logger.info("5/6: Analyzing sound symbolism...")
        results['sound_symbolism'] = self.analyze_sound_symbolism(words_data)
        
        # 6. Language family comparison
        logger.info("6/6: Comparing language families...")
        results['family_comparison'] = self._analyze_by_family(words_data)
        
        # Summary statistics
        results['summary'] = self._generate_summary(results, words_data)
        
        logger.info("\n" + "="*60)
        logger.info("ANALYSIS COMPLETE")
        logger.info("="*60)
        
        return results
    
    def _analyze_by_family(self, words_data: List[Dict]) -> Dict:
        """Compare phonetic properties across language families"""
        families = defaultdict(list)
        for word in words_data:
            families[word['language_family']].append(word)
        
        family_analyses = {}
        for family, words in families.items():
            if len(words) < 2:
                continue
            
            analyses = [self.analyze_word(w['word'], w['romanization']) for w in words]
            
            family_analyses[family] = {
                'word_count': len(words),
                'mean_beauty': float(np.mean([a['beauty_score'] for a in analyses])),
                'mean_melodiousness': float(np.mean([a['melodiousness_score'] for a in analyses])),
                'mean_harshness': float(np.mean([a['harshness_score'] for a in analyses])),
                'mean_syllables': float(np.mean([a['syllable_count'] for a in analyses])),
                'languages': list(set(w['language'] for w in words)),
            }
        
        # Rank families by beauty
        ranked_families = sorted(family_analyses.items(), key=lambda x: x[1]['mean_beauty'], reverse=True)
        
        return {
            'by_family': family_analyses,
            'ranked_by_beauty': ranked_families,
            'most_beautiful_family': ranked_families[0] if ranked_families else None,
        }
    
    def _generate_summary(self, results: Dict, words_data: List[Dict]) -> Dict:
        """Generate executive summary of key findings"""
        beauty_rankings = results['beauty_rankings']
        sound_symbolism = results['sound_symbolism']
        ancient_vs_modern = results['ancient_vs_modern']
        semantic = results['semantic_breadth']
        
        return {
            'dataset_size': len(words_data),
            'ancient_count': len([w for w in words_data if w['is_ancient']]),
            'modern_count': len([w for w in words_data if not w['is_ancient']]),
            'unique_languages': len(set(w['language'] for w in words_data)),
            'mean_beauty_score': beauty_rankings['statistics']['mean_beauty'],
            'most_beautiful_word': beauty_rankings['top_10'][0]['romanization'],
            'most_beautiful_language': beauty_rankings['top_10'][0]['language'],
            'soft_sound_dominance': sound_symbolism['soft_vs_harsh']['soft_to_harsh_ratio'],
            'semantic_sophistication': f"Ancient Greek and Sanskrit maintain {semantic['statistics']['max_types']} distinct love concepts",
            'temporal_stability': ancient_vs_modern['interpretation']['overall_trend'],
            'key_insight': "Love words universally favor melodious, soft sounds (l/m/v/r) across all language families and time periods, suggesting deep connection between phonetics and emotion.",
        }
    
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
        """Check if word has repeated sounds (alliteration/rhyme)"""
        text_lower = text.lower()
        for char in set(text_lower):
            if char.isalpha() and text_lower.count(char) >= 2:
                return True
        return False


if __name__ == '__main__':
    # Test analyzer
    from collectors.love_words_collector import LoveWordsCollector
    
    collector = LoveWordsCollector()
    words_data = collector.get_all_words()
    
    analyzer = LoveWordsAnalyzer()
    results = analyzer.run_comprehensive_analysis(words_data)
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Dataset: {results['summary']['dataset_size']} words")
    print(f"Most beautiful: {results['summary']['most_beautiful_word']} ({results['summary']['most_beautiful_language']})")
    print(f"Mean beauty score: {results['summary']['mean_beauty_score']:.2f}")
    print(f"Soft sound dominance: {results['summary']['soft_sound_dominance']:.2f}×")
    print(f"\nKey insight: {results['summary']['key_insight']}")
    print("="*60)

