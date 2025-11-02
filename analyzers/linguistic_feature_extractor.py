"""
Linguistic Feature Extractor

Computes advanced linguistic features for cryptocurrency names including:
- Phonetic patterns (CV sequences, n-grams, sound types)
- Linguistic structure (morphology, etymology, word formation)
- Psychological dimensions (sound symbolism, emotional valence)
- Structural patterns (letter positions, symmetry, repetition)
"""

import re
import json
from collections import Counter
import logging

logger = logging.getLogger(__name__)


class LinguisticFeatureExtractor:
    """
    Extract deep linguistic features from cryptocurrency names
    """
    
    def __init__(self):
        # Phonetic categories
        self.vowels = set('aeiouAEIOU')
        self.consonants = set('bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ')
        
        # Hard vs soft sounds
        self.hard_sounds = set('kKtTpPbBdDgG')  # Plosives
        self.soft_sounds = set('sSfFvVhHmMnNlLrR')  # Fricatives, nasals, liquids
        
        # Sound symbolism (kiki/bouba effect)
        self.sharp_sounds = set('kKtTiIeE')  # Associated with angular/sharp
        self.round_sounds = set('bBmMoOuU')  # Associated with round/soft
        
        # Emotional valence
        self.positive_sounds = set('lLmMnNsSzZ')  # Generally perceived as pleasant
        self.power_sounds = set('kKxXqQgGrR')  # Associated with strength/power
        
        # Common prefixes and suffixes in crypto
        self.crypto_prefixes = [
            'bit', 'coin', 'chain', 'block', 'crypto', 'digi', 'cyber', 
            'meta', 'neo', 'poly', 'multi', 'uni', 'super', 'hyper'
        ]
        self.crypto_suffixes = [
            'coin', 'token', 'swap', 'finance', 'cash', 'pay', 'link',
            'chain', 'net', 'network', 'protocol'
        ]
        
        # Etymology hints
        self.latin_roots = ['terra', 'luna', 'sol', 'aqua', 'omni', 'multi', 'uni']
        self.greek_roots = ['crypto', 'poly', 'meta', 'neo', 'auto', 'tele', 'photo']
        self.tech_roots = ['bit', 'byte', 'cyber', 'digi', 'nano', 'micro', 'mega']
        
    def extract_all_features(self, name):
        """
        Extract all linguistic features for a name
        
        Returns:
            Dict with comprehensive linguistic features
        """
        name_clean = name.strip()
        name_lower = name_clean.lower()
        
        features = {}
        
        # Phonetic patterns
        features['phonetic'] = self._extract_phonetic_features(name_clean)
        
        # Linguistic structure
        features['structure'] = self._extract_structural_features(name_clean)
        
        # Psychological dimensions
        features['psychological'] = self._extract_psychological_features(name_clean)
        
        # Positional patterns
        features['positional'] = self._extract_positional_features(name_clean)
        
        # N-gram analysis
        features['ngrams'] = self._extract_ngram_features(name_lower)
        
        # Morphological analysis
        features['morphology'] = self._extract_morphological_features(name_lower)
        
        # Symmetry and patterns
        features['symmetry'] = self._extract_symmetry_features(name_lower)
        
        return features
    
    # =============================================================================
    # PHONETIC PATTERNS
    # =============================================================================
    
    def _extract_phonetic_features(self, name):
        """Extract phonetic pattern features"""
        features = {}
        
        # CV pattern (Consonant-Vowel sequence)
        cv_pattern = self._get_cv_pattern(name)
        features['cv_pattern'] = cv_pattern
        features['cv_pattern_length'] = len(cv_pattern)
        
        # Pattern complexity
        features['cv_transitions'] = self._count_cv_transitions(cv_pattern)
        features['cv_repetition_score'] = self._calculate_pattern_repetition(cv_pattern)
        
        # Hard vs soft sound ratio
        hard_count = sum(1 for c in name if c in self.hard_sounds)
        soft_count = sum(1 for c in name if c in self.soft_sounds)
        total_consonants = hard_count + soft_count
        
        features['hard_sound_ratio'] = round(hard_count / total_consonants, 3) if total_consonants > 0 else 0
        features['soft_sound_ratio'] = round(soft_count / total_consonants, 3) if total_consonants > 0 else 0
        features['sound_balance'] = round(abs(hard_count - soft_count) / max(total_consonants, 1), 3)
        
        # Consonant clusters
        features['max_consonant_cluster'] = self._max_consonant_cluster_size(name)
        features['max_vowel_cluster'] = self._max_vowel_cluster_size(name)
        features['total_clusters'] = self._count_clusters(name)
        
        # Phoneme diversity
        unique_sounds = len(set(name.lower()))
        features['phoneme_diversity'] = round(unique_sounds / len(name), 3) if len(name) > 0 else 0
        
        return features
    
    def _get_cv_pattern(self, name):
        """Get consonant-vowel pattern (e.g., 'Bitcoin' -> 'CVCCVVC')"""
        pattern = []
        for char in name:
            if char in self.vowels:
                pattern.append('V')
            elif char in self.consonants:
                pattern.append('C')
        return ''.join(pattern)
    
    def _count_cv_transitions(self, cv_pattern):
        """Count transitions between consonants and vowels"""
        if len(cv_pattern) < 2:
            return 0
        transitions = sum(1 for i in range(len(cv_pattern)-1) 
                         if cv_pattern[i] != cv_pattern[i+1])
        return transitions
    
    def _calculate_pattern_repetition(self, cv_pattern):
        """Calculate how repetitive the CV pattern is"""
        if len(cv_pattern) < 2:
            return 0
        
        # Look for repeated subsequences
        max_repeat_score = 0
        for length in range(2, len(cv_pattern)//2 + 1):
            for i in range(len(cv_pattern) - length):
                substring = cv_pattern[i:i+length]
                count = cv_pattern.count(substring)
                if count > 1:
                    score = count * length
                    max_repeat_score = max(max_repeat_score, score)
        
        return max_repeat_score
    
    def _max_consonant_cluster_size(self, name):
        """Find maximum consecutive consonant sequence"""
        current = 0
        maximum = 0
        for char in name:
            if char in self.consonants:
                current += 1
                maximum = max(maximum, current)
            else:
                current = 0
        return maximum
    
    def _max_vowel_cluster_size(self, name):
        """Find maximum consecutive vowel sequence"""
        current = 0
        maximum = 0
        for char in name:
            if char in self.vowels:
                current += 1
                maximum = max(maximum, current)
            else:
                current = 0
        return maximum
    
    def _count_clusters(self, name):
        """Count total number of consonant/vowel clusters"""
        if not name:
            return 0
        
        clusters = 1
        prev_type = 'V' if name[0] in self.vowels else 'C' if name[0] in self.consonants else 'O'
        
        for char in name[1:]:
            curr_type = 'V' if char in self.vowels else 'C' if char in self.consonants else 'O'
            if curr_type != prev_type and curr_type != 'O':
                clusters += 1
            prev_type = curr_type
        
        return clusters
    
    # =============================================================================
    # STRUCTURAL FEATURES
    # =============================================================================
    
    def _extract_structural_features(self, name):
        """Extract structural/compositional features"""
        features = {}
        
        # Letter frequency analysis
        letter_freq = Counter(name.lower())
        features['unique_letters'] = len(letter_freq)
        features['max_letter_frequency'] = max(letter_freq.values()) if letter_freq else 0
        
        # Repetition patterns
        features['has_doubled_letters'] = int(bool(re.search(r'([a-zA-Z])\1', name)))
        features['has_tripled_letters'] = int(bool(re.search(r'([a-zA-Z])\1{2}', name)))
        
        # Character type composition
        features['alpha_ratio'] = round(sum(c.isalpha() for c in name) / len(name), 3) if name else 0
        features['digit_ratio'] = round(sum(c.isdigit() for c in name) / len(name), 3) if name else 0
        features['special_char_ratio'] = round(sum(not c.isalnum() for c in name) / len(name), 3) if name else 0
        
        # Case patterns
        features['uppercase_ratio'] = round(sum(c.isupper() for c in name) / len(name), 3) if name else 0
        features['has_camelcase'] = int(bool(re.search(r'[a-z][A-Z]', name)))
        features['all_caps'] = int(name.isupper() and name.isalpha())
        features['all_lowercase'] = int(name.islower() and name.isalpha())
        
        return features
    
    # =============================================================================
    # PSYCHOLOGICAL DIMENSIONS
    # =============================================================================
    
    def _extract_psychological_features(self, name):
        """Extract psychological/perceptual features"""
        features = {}
        
        # Sound symbolism (kiki/bouba effect)
        sharp_count = sum(1 for c in name if c in self.sharp_sounds)
        round_count = sum(1 for c in name if c in self.round_sounds)
        total_symbolic = sharp_count + round_count
        
        features['sharp_sound_ratio'] = round(sharp_count / len(name), 3) if name else 0
        features['round_sound_ratio'] = round(round_count / len(name), 3) if name else 0
        features['symbolism_balance'] = round(abs(sharp_count - round_count) / max(total_symbolic, 1), 3)
        features['symbolism_type'] = 'sharp' if sharp_count > round_count else 'round' if round_count > sharp_count else 'balanced'
        
        # Emotional valence
        positive_count = sum(1 for c in name if c in self.positive_sounds)
        features['positive_sound_ratio'] = round(positive_count / len(name), 3) if name else 0
        
        # Power/strength dimension
        power_count = sum(1 for c in name if c in self.power_sounds)
        features['power_sound_ratio'] = round(power_count / len(name), 3) if name else 0
        
        # Overall phonetic affect
        features['phonetic_affect_score'] = round(
            (features['positive_sound_ratio'] * 0.5 + 
             features['power_sound_ratio'] * 0.3 +
             features['round_sound_ratio'] * 0.2), 3
        )
        
        # Brand archetype hints
        features['archetype'] = self._infer_brand_archetype(name, features)
        
        return features
    
    def _infer_brand_archetype(self, name, features):
        """Infer likely brand archetype based on phonetic features"""
        name_lower = name.lower()
        
        # Simple heuristics
        if features['power_sound_ratio'] > 0.3 or any(word in name_lower for word in ['king', 'titan', 'master', 'lord']):
            return 'ruler'
        elif features['sharp_sound_ratio'] > 0.4 or any(word in name_lower for word in ['tech', 'bit', 'cyber', 'digi']):
            return 'innovator'
        elif features['positive_sound_ratio'] > 0.3 or any(word in name_lower for word in ['safe', 'trust', 'care']):
            return 'caregiver'
        elif any(word in name_lower for word in ['hero', 'save', 'guard', 'shield']):
            return 'hero'
        else:
            return 'neutral'
    
    # =============================================================================
    # POSITIONAL FEATURES
    # =============================================================================
    
    def _extract_positional_features(self, name):
        """Extract position-specific features"""
        features = {}
        
        if not name:
            return features
        
        name_alpha = ''.join(c for c in name if c.isalpha())
        
        if name_alpha:
            # First letter
            features['first_letter'] = name_alpha[0].lower()
            features['first_letter_vowel'] = int(name_alpha[0] in self.vowels)
            features['first_letter_hard'] = int(name_alpha[0] in self.hard_sounds)
            
            # Last letter
            features['last_letter'] = name_alpha[-1].lower()
            features['last_letter_vowel'] = int(name_alpha[-1] in self.vowels)
            features['last_letter_soft'] = int(name_alpha[-1] in self.soft_sounds)
            
            # Endings analysis
            features['ends_with_vowel'] = features['last_letter_vowel']
            features['ends_with_consonant'] = 1 - features['last_letter_vowel']
            
            # Common ending patterns
            name_lower = name_alpha.lower()
            features['ends_with_er'] = int(name_lower.endswith('er'))
            features['ends_with_ly'] = int(name_lower.endswith('ly'))
            features['ends_with_y'] = int(name_lower.endswith('y'))
            features['ends_with_o'] = int(name_lower.endswith('o'))
            features['ends_with_a'] = int(name_lower.endswith('a'))
        
        return features
    
    # =============================================================================
    # N-GRAM FEATURES
    # =============================================================================
    
    def _extract_ngram_features(self, name):
        """Extract n-gram (bigram, trigram) features"""
        features = {}
        
        # Bigrams (2-letter sequences)
        bigrams = [name[i:i+2] for i in range(len(name)-1)]
        features['unique_bigrams'] = len(set(bigrams))
        features['bigram_diversity'] = round(len(set(bigrams)) / max(len(bigrams), 1), 3)
        
        # Most common bigrams
        if bigrams:
            bigram_counts = Counter(bigrams)
            most_common = bigram_counts.most_common(3)
            features['most_common_bigram'] = most_common[0][0] if most_common else ''
            features['bigram_max_frequency'] = most_common[0][1] if most_common else 0
        
        # Trigrams (3-letter sequences)
        trigrams = [name[i:i+3] for i in range(len(name)-2)]
        features['unique_trigrams'] = len(set(trigrams))
        features['trigram_diversity'] = round(len(set(trigrams)) / max(len(trigrams), 1), 3)
        
        # Common crypto n-grams
        crypto_ngrams = ['bit', 'coin', 'chain', 'swap', 'link', 'eth', 'doge']
        features['has_crypto_ngram'] = int(any(ng in name for ng in crypto_ngrams))
        
        return features
    
    # =============================================================================
    # MORPHOLOGICAL FEATURES
    # =============================================================================
    
    def _extract_morphological_features(self, name):
        """Extract morphological/word formation features"""
        features = {}
        
        name_lower = name.lower()
        
        # Prefix detection
        has_prefix = False
        detected_prefix = None
        for prefix in self.crypto_prefixes:
            if name_lower.startswith(prefix):
                has_prefix = True
                detected_prefix = prefix
                break
        
        features['has_crypto_prefix'] = int(has_prefix)
        features['detected_prefix'] = detected_prefix
        
        # Suffix detection
        has_suffix = False
        detected_suffix = None
        for suffix in self.crypto_suffixes:
            if name_lower.endswith(suffix):
                has_suffix = True
                detected_suffix = suffix
                break
        
        features['has_crypto_suffix'] = int(has_suffix)
        features['detected_suffix'] = detected_suffix
        
        # Etymology hints
        etymology = []
        if any(root in name_lower for root in self.latin_roots):
            etymology.append('latin')
        if any(root in name_lower for root in self.greek_roots):
            etymology.append('greek')
        if any(root in name_lower for root in self.tech_roots):
            etymology.append('tech')
        
        features['etymology_hints'] = etymology
        features['has_classical_etymology'] = int('latin' in etymology or 'greek' in etymology)
        features['has_tech_etymology'] = int('tech' in etymology)
        
        # Word formation type
        features['formation_type'] = self._infer_word_formation(name_lower)
        
        # Compound word detection
        features['likely_compound'] = int(has_prefix and has_suffix)
        
        return features
    
    def _infer_word_formation(self, name):
        """Infer how the word was likely formed"""
        # Simple heuristics
        if any(char.isdigit() for char in name):
            return 'alphanumeric'
        elif len(name) <= 4 and name.isupper():
            return 'acronym'
        elif any(root in name for root in self.crypto_prefixes + self.crypto_suffixes):
            return 'compound'
        elif len(set(name)) < len(name) * 0.5:  # High letter repetition
            return 'repetitive'
        else:
            return 'invented'
    
    # =============================================================================
    # SYMMETRY FEATURES
    # =============================================================================
    
    def _extract_symmetry_features(self, name):
        """Extract symmetry and pattern features"""
        features = {}
        
        name_lower = name.lower()
        name_alpha = ''.join(c for c in name_lower if c.isalpha())
        
        # Palindrome detection
        features['is_palindrome'] = int(name_alpha == name_alpha[::-1])
        
        # Partial palindrome (first half mirrors second half)
        if len(name_alpha) >= 4:
            mid = len(name_alpha) // 2
            first_half = name_alpha[:mid]
            second_half = name_alpha[-mid:][::-1]
            similarity = sum(a == b for a, b in zip(first_half, second_half)) / mid
            features['palindrome_similarity'] = round(similarity, 3)
        else:
            features['palindrome_similarity'] = 0
        
        # Symmetry in CV pattern
        cv_pattern = self._get_cv_pattern(name)
        if cv_pattern:
            features['cv_palindrome'] = int(cv_pattern == cv_pattern[::-1])
        else:
            features['cv_palindrome'] = 0
        
        # Repetitive structure
        features['has_repetitive_structure'] = int(self._has_repetitive_structure(name_lower))
        
        # Visual balance (similar number of ascenders/descenders)
        ascenders = sum(1 for c in name_lower if c in 'bdfhklt')
        descenders = sum(1 for c in name_lower if c in 'gjpqy')
        features['visual_balance'] = round(1 - abs(ascenders - descenders) / max(len(name_alpha), 1), 3)
        
        return features
    
    def _has_repetitive_structure(self, name):
        """Check if name has repetitive structure (e.g., ABAB pattern)"""
        if len(name) < 4:
            return False
        
        # Check for ABAB pattern
        if len(name) >= 4 and len(name) % 2 == 0:
            mid = len(name) // 2
            if name[:mid] == name[mid:]:
                return True
        
        # Check for repeated sequences of length 2-4
        for length in range(2, min(5, len(name)//2 + 1)):
            for i in range(len(name) - 2*length + 1):
                if name[i:i+length] == name[i+length:i+2*length]:
                    return True
        
        return False
    
    # =============================================================================
    # SUMMARY FEATURES
    # =============================================================================
    
    def get_summary_features(self, name):
        """
        Get summary feature vector for statistical analysis
        
        Returns:
            Dict with numeric features suitable for regression/clustering
        """
        all_features = self.extract_all_features(name)
        
        # Flatten to numeric features only
        summary = {}
        
        # Phonetic
        summary['cv_pattern_length'] = all_features['phonetic']['cv_pattern_length']
        summary['cv_transitions'] = all_features['phonetic']['cv_transitions']
        summary['hard_sound_ratio'] = all_features['phonetic']['hard_sound_ratio']
        summary['soft_sound_ratio'] = all_features['phonetic']['soft_sound_ratio']
        summary['max_consonant_cluster'] = all_features['phonetic']['max_consonant_cluster']
        summary['phoneme_diversity'] = all_features['phonetic']['phoneme_diversity']
        
        # Structural
        summary['unique_letters'] = all_features['structure']['unique_letters']
        summary['has_doubled_letters'] = all_features['structure']['has_doubled_letters']
        summary['has_camelcase'] = all_features['structure']['has_camelcase']
        
        # Psychological
        summary['sharp_sound_ratio'] = all_features['psychological']['sharp_sound_ratio']
        summary['round_sound_ratio'] = all_features['psychological']['round_sound_ratio']
        summary['power_sound_ratio'] = all_features['psychological']['power_sound_ratio']
        summary['phonetic_affect_score'] = all_features['psychological']['phonetic_affect_score']
        
        # Positional
        if 'first_letter_vowel' in all_features['positional']:
            summary['first_letter_vowel'] = all_features['positional']['first_letter_vowel']
            summary['last_letter_vowel'] = all_features['positional']['last_letter_vowel']
            summary['ends_with_vowel'] = all_features['positional']['ends_with_vowel']
        
        # N-grams
        summary['bigram_diversity'] = all_features['ngrams']['bigram_diversity']
        summary['trigram_diversity'] = all_features['ngrams']['trigram_diversity']
        summary['has_crypto_ngram'] = all_features['ngrams']['has_crypto_ngram']
        
        # Morphology
        summary['has_crypto_prefix'] = all_features['morphology']['has_crypto_prefix']
        summary['has_crypto_suffix'] = all_features['morphology']['has_crypto_suffix']
        summary['has_classical_etymology'] = all_features['morphology']['has_classical_etymology']
        
        # Symmetry
        summary['is_palindrome'] = all_features['symmetry']['is_palindrome']
        summary['palindrome_similarity'] = all_features['symmetry']['palindrome_similarity']
        summary['visual_balance'] = all_features['symmetry']['visual_balance']
        
        return summary

