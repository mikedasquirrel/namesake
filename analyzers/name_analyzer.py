import re
import json
from collections import Counter
import pyphen
import Levenshtein
from core.config import Config
import logging

logger = logging.getLogger(__name__)


class NameAnalyzer:
    """Comprehensive linguistic and phonetic analysis of cryptocurrency names"""
    
    def __init__(self):
        self.pyphen_dic = pyphen.Pyphen(lang='en_US')
        self.vowels = set('aeiouAEIOU')
        self.consonants = set('bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ')
        
        # Common word lists for categorization
        self.animal_words = {
            'dog', 'cat', 'fox', 'bear', 'lion', 'tiger', 'wolf', 'bird', 'eagle', 
            'hawk', 'shark', 'whale', 'dolphin', 'dragon', 'snake', 'rabbit', 'frog',
            'monkey', 'ape', 'gorilla', 'panda', 'koala', 'ant', 'bee', 'bat', 'rat',
            'mouse', 'shiba', 'inu', 'doge', 'pepe', 'floki'
        }
        
        self.tech_words = {
            'bit', 'byte', 'coin', 'token', 'chain', 'link', 'net', 'web', 'cyber',
            'digital', 'crypto', 'meta', 'data', 'node', 'protocol', 'smart', 'quantum',
            'nano', 'micro', 'tech', 'tron', 'matic', 'algo', 'dot', 'hash', 'block'
        }
        
        self.mythological_words = {
            'zeus', 'thor', 'odin', 'apollo', 'titan', 'olympus', 'atlas', 'phoenix',
            'dragon', 'griffin', 'hydra', 'medusa', 'oracle', 'hermes', 'hera', 'athena'
        }
        
        self.financial_words = {
            'gold', 'silver', 'dollar', 'euro', 'pound', 'cash', 'money', 'bank',
            'pay', 'swap', 'trade', 'exchange', 'finance', 'defi', 'yield', 'stake'
        }
        
        self.astronomical_words = {
            'star', 'moon', 'sun', 'cosmos', 'stellar', 'luna', 'solar', 'orbit',
            'galaxy', 'nebula', 'comet', 'meteor', 'astro', 'space', 'terra'
        }
        
        self.elemental_words = {
            'fire', 'water', 'earth', 'air', 'ice', 'storm', 'thunder', 'lightning',
            'flame', 'ocean', 'wind', 'stone', 'crystal', 'plasma'
        }
    
    def analyze_name(self, name, all_names=None):
        """
        Perform comprehensive analysis of a cryptocurrency name
        
        Args:
            name: The cryptocurrency name to analyze
            all_names: List of all cryptocurrency names for similarity comparison
            
        Returns:
            Dictionary with all analysis metrics
        """
        analysis = {}
        
        # Basic metrics
        analysis['character_length'] = len(name)
        analysis['word_count'] = len(re.findall(r'\w+', name))
        
        # Syllable analysis
        analysis['syllable_count'] = self._count_syllables(name)
        
        # Phonetic analysis
        analysis['phonetic_score'] = self._calculate_phonetic_score(name)
        analysis['vowel_ratio'] = self._calculate_vowel_ratio(name)
        analysis['consonant_clusters'] = self._count_consonant_clusters(name)
        
        # Memorability
        analysis['memorability_score'] = self._calculate_memorability(name)
        analysis['pronounceability_score'] = self._calculate_pronounceability(name)
        
        # Categorization
        analysis['name_type'], analysis['category_tags'] = self._categorize_name(name)
        
        # Character composition
        analysis['has_numbers'] = bool(re.search(r'\d', name))
        analysis['has_special_chars'] = bool(re.search(r'[^a-zA-Z0-9\s]', name))
        analysis['capital_pattern'] = self._analyze_capitalization(name)
        
        # Semantic analysis
        analysis['is_real_word'] = self._is_real_word(name)
        analysis['semantic_category'] = self._get_semantic_category(name)
        
        # Uniqueness metrics (requires comparison with other names)
        if all_names:
            similarity_metrics = self._calculate_uniqueness(name, all_names)
            analysis.update(similarity_metrics)
        else:
            analysis['uniqueness_score'] = None
            analysis['avg_similarity_distance'] = None
            analysis['closest_match'] = None
            analysis['closest_match_distance'] = None
        
        return analysis
    
    def _count_syllables(self, word):
        """Count syllables in a word using pyphen"""
        clean_word = re.sub(r'[^a-zA-Z]', '', word)
        if not clean_word:
            return 1
        
        hyphenated = self.pyphen_dic.inserted(clean_word.lower())
        syllables = len(hyphenated.split('-'))
        
        # Fallback: basic vowel counting if pyphen fails
        if syllables == 0:
            syllables = max(1, len(re.findall(r'[aeiou]+', clean_word.lower())))
        
        return syllables
    
    def _calculate_vowel_ratio(self, name):
        """Calculate ratio of vowels to total letters"""
        letters = re.sub(r'[^a-zA-Z]', '', name)
        if not letters:
            return 0.0
        
        vowel_count = sum(1 for c in letters if c in self.vowels)
        return vowel_count / len(letters)
    
    def _count_consonant_clusters(self, name):
        """Count consonant clusters (sequences of 2+ consonants)"""
        clean_name = re.sub(r'[^a-zA-Z]', '', name.lower())
        clusters = re.findall(r'[bcdfghjklmnpqrstvwxyz]{2,}', clean_name)
        return len(clusters)
    
    def _calculate_phonetic_score(self, name):
        """
        Calculate overall phonetic appeal (euphony)
        Based on vowel ratio, consonant clusters, and syllable rhythm
        Score: 0-100
        """
        vowel_ratio = self._calculate_vowel_ratio(name)
        consonant_clusters = self._count_consonant_clusters(name)
        syllables = self._count_syllables(name)
        length = len(re.sub(r'[^a-zA-Z]', '', name))
        
        # Ideal vowel ratio is around 0.4-0.5
        vowel_score = 100 * (1 - abs(0.45 - vowel_ratio) * 2)
        
        # Fewer consonant clusters = more euphonious
        cluster_penalty = min(consonant_clusters * 10, 40)
        
        # Moderate length and syllable count preferred
        if 3 <= length <= 7 and 1 <= syllables <= 3:
            length_bonus = 20
        else:
            length_bonus = 0
        
        score = max(0, min(100, vowel_score - cluster_penalty + length_bonus))
        return round(score, 2)
    
    def _calculate_memorability(self, name):
        """
        Calculate memorability score based on length, uniqueness, and phonetics
        Score: 0-100
        """
        length = len(name)
        syllables = self._count_syllables(name)
        has_numbers = bool(re.search(r'\d', name))
        
        # Optimal length: 4-8 characters
        if 4 <= length <= 8:
            length_score = 40
        elif 3 <= length <= 10:
            length_score = 25
        else:
            length_score = 10
        
        # Optimal syllables: 1-2
        if syllables <= 2:
            syllable_score = 30
        elif syllables == 3:
            syllable_score = 20
        else:
            syllable_score = 5
        
        # Numbers reduce memorability
        number_penalty = 15 if has_numbers else 0
        
        # Phonetic appeal contributes
        phonetic_component = self._calculate_phonetic_score(name) * 0.3
        
        score = length_score + syllable_score + phonetic_component - number_penalty
        return round(max(0, min(100, score)), 2)
    
    def _calculate_pronounceability(self, name):
        """
        Calculate how easy the name is to pronounce
        Score: 0-100
        """
        clean_name = re.sub(r'[^a-zA-Z]', '', name.lower())
        if not clean_name:
            return 0
        
        # Vowel spacing (should have vowels regularly distributed)
        vowel_positions = [i for i, c in enumerate(clean_name) if c in 'aeiou']
        if len(vowel_positions) < 2:
            spacing_score = 20
        else:
            gaps = [vowel_positions[i+1] - vowel_positions[i] for i in range(len(vowel_positions)-1)]
            avg_gap = sum(gaps) / len(gaps)
            # Ideal gap: 1-2 characters
            spacing_score = 40 * (1 / (1 + abs(avg_gap - 1.5)))
        
        # Consonant cluster penalty
        clusters = self._count_consonant_clusters(name)
        cluster_penalty = min(clusters * 15, 50)
        
        # Length consideration
        length_factor = 30 if 3 <= len(clean_name) <= 8 else 15
        
        # Starting with a vowel is generally easier
        starts_with_vowel = 10 if clean_name[0] in 'aeiou' else 0
        
        score = spacing_score + length_factor + starts_with_vowel - cluster_penalty
        return round(max(0, min(100, score)), 2)
    
    def _categorize_name(self, name):
        """
        Categorize the name into primary type and all applicable tags
        Returns: (primary_type, [tags])
        """
        name_lower = name.lower()
        tags = []
        
        # Check each category
        if any(word in name_lower for word in self.animal_words):
            tags.append('animal')
        
        if any(word in name_lower for word in self.tech_words):
            tags.append('tech')
        
        if any(word in name_lower for word in self.mythological_words):
            tags.append('mythological')
        
        if any(word in name_lower for word in self.financial_words):
            tags.append('financial')
        
        if any(word in name_lower for word in self.astronomical_words):
            tags.append('astronomical')
        
        if any(word in name_lower for word in self.elemental_words):
            tags.append('elemental')
        
        # Check for acronym (all caps, 2-5 letters)
        if name.isupper() and 2 <= len(name) <= 5 and name.isalpha():
            tags.append('acronym')
        
        # Check for numbers
        if re.search(r'\d', name):
            tags.append('numeric')
        
        # Check for portmanteau (mixed categories)
        if len(tags) >= 2:
            tags.append('portmanteau')
        
        # Check for invented/abstract
        if not tags or (len(tags) == 1 and tags[0] == 'numeric'):
            tags.append('invented')
        
        # Primary type is the first tag, or 'other' if none
        primary_type = tags[0] if tags else 'other'
        if not tags:
            tags = ['other']
        
        return primary_type, tags
    
    def _analyze_capitalization(self, name):
        """Analyze capitalization pattern"""
        if name.islower():
            return 'lowercase'
        elif name.isupper():
            return 'uppercase'
        elif re.match(r'^[A-Z][a-z]+(?:[A-Z][a-z]+)+$', name):
            return 'camelcase'
        elif any(c.isupper() for c in name) and any(c.islower() for c in name):
            return 'mixed'
        else:
            return 'lowercase'
    
    def _is_real_word(self, name):
        """Check if name is likely a real English word"""
        # Simple heuristic: common dictionary words
        common_words = {
            'bitcoin', 'ethereum', 'cardano', 'stellar', 'cosmos', 'avalanche',
            'polygon', 'solana', 'chain', 'link', 'maker', 'compound', 'curve'
        }
        return name.lower() in common_words
    
    def _get_semantic_category(self, name):
        """Get the semantic meaning category of the name"""
        name_lower = name.lower()
        
        if any(word in name_lower for word in self.animal_words):
            return 'animal_reference'
        elif any(word in name_lower for word in self.tech_words):
            return 'technology'
        elif any(word in name_lower for word in self.mythological_words):
            return 'mythology'
        elif any(word in name_lower for word in self.financial_words):
            return 'finance'
        elif any(word in name_lower for word in self.astronomical_words):
            return 'astronomy'
        elif any(word in name_lower for word in self.elemental_words):
            return 'nature'
        else:
            return 'abstract'
    
    def _calculate_uniqueness(self, name, all_names):
        """
        Calculate uniqueness metrics by comparing to all other names
        
        Returns dict with:
        - uniqueness_score: 0-100, higher = more unique
        - avg_similarity_distance: Average Levenshtein distance
        - closest_match: Name of most similar crypto
        - closest_match_distance: Distance to closest match
        """
        if not all_names or len(all_names) < 2:
            return {
                'uniqueness_score': 100,
                'avg_similarity_distance': None,
                'closest_match': None,
                'closest_match_distance': None
            }
        
        distances = []
        min_distance = float('inf')
        closest = None
        
        for other_name in all_names:
            if other_name.lower() == name.lower():
                continue
            
            distance = Levenshtein.distance(name.lower(), other_name.lower())
            distances.append(distance)
            
            if distance < min_distance:
                min_distance = distance
                closest = other_name
        
        if not distances:
            return {
                'uniqueness_score': 100,
                'avg_similarity_distance': None,
                'closest_match': None,
                'closest_match_distance': None
            }
        
        avg_distance = sum(distances) / len(distances)
        
        # Uniqueness score: normalized average distance
        # Typical max distance is around 10-15 for crypto names
        uniqueness_score = min(100, (avg_distance / 10) * 100)
        
        return {
            'uniqueness_score': round(uniqueness_score, 2),
            'avg_similarity_distance': round(avg_distance, 2),
            'closest_match': closest,
            'closest_match_distance': min_distance
        }
    
    def calculate_scarcity_metrics(self, name_type, all_analyses):
        """
        Calculate scarcity metrics for a name type within the full dataset
        
        Args:
            name_type: The primary name type
            all_analyses: List of all NameAnalysis objects
            
        Returns:
            Dict with name_type_count and name_type_percentile
        """
        type_counts = Counter(analysis.name_type for analysis in all_analyses)
        total_count = len(all_analyses)
        
        type_count = type_counts.get(name_type, 1)
        
        # Percentile: what percentage are more rare than this type
        rarer_count = sum(1 for count in type_counts.values() if count < type_count)
        percentile = (rarer_count / len(type_counts)) * 100 if type_counts else 50
        
        return {
            'name_type_count': type_count,
            'name_type_percentile': round(percentile, 2)
        }

