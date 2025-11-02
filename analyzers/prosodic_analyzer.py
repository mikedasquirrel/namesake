"""
Prosodic Analyzer
Rhythm, stress patterns, and flow analysis
"""

import re
import logging

logger = logging.getLogger(__name__)


class ProsodicAnalyzer:
    """Analyze prosodic characteristics (rhythm, stress, flow)"""
    
    def analyze(self, name):
        """Analyze rhythm and flow patterns"""
        
        # Detect stress pattern (simplified)
        stress_pattern = self._detect_stress_pattern(name)
        
        # Rhythm regularity
        rhythm_score = self._calculate_rhythm_regularity(name)
        
        # Flow score (ease of pronunciation)
        flow_score = self._calculate_flow(name)
        
        # Vowel harmony (do vowels match?)
        harmony_score = self._calculate_vowel_harmony(name)
        
        # Catchiness (rhythm + flow + harmony)
        catchiness = (rhythm_score + flow_score + harmony_score) / 3
        
        # Sing-ability (can you chant it?)
        singability = self._calculate_singability(name, rhythm_score, flow_score)
        
        return {
            'stress_pattern': stress_pattern,
            'rhythm_regularity': round(rhythm_score, 1),
            'flow_score': round(flow_score, 1),
            'vowel_harmony': round(harmony_score, 1),
            'catchiness': round(catchiness, 1),
            'singability': round(singability, 1),
            'prosodic_quality': round((rhythm_score + flow_score + catchiness) / 3, 1)
        }
    
    def _detect_stress_pattern(self, name):
        """Detect if trochaic (STROng-weak) or iambic (weak-STROng)"""
        # Simplified: check if first syllable tends to be stressed
        # In English, words often start with stress (trochaic)
        
        # Heuristic: longer first syllable = likely stressed
        words = name.split()
        if not words:
            return 'unknown'
        
        first_word = words[0].lower()
        
        # Common trochaic patterns
        trochaic_patterns = ['apple', 'google', 'facebook', 'bitcoin', 'stellar']
        if any(first_word.startswith(p[:3]) for p in trochaic_patterns):
            return 'trochaic'
        
        # Common iambic patterns
        iambic_patterns = ['about', 'around', 'between', 'beyond']
        if any(first_word.startswith(p[:3]) for p in iambic_patterns):
            return 'iambic'
        
        # Default: assume trochaic (most common in English)
        return 'trochaic'
    
    def _calculate_rhythm_regularity(self, name):
        """Calculate how regular the rhythm is"""
        # Count syllables in each word
        words = name.split()
        if len(words) <= 1:
            return 80  # Single words have regular rhythm
        
        syllable_counts = [self._count_syllables(word) for word in words]
        
        # Regular rhythm = similar syllable counts
        if len(set(syllable_counts)) == 1:
            return 100  # Perfect regularity
        
        # Calculate variance
        avg = sum(syllable_counts) / len(syllable_counts)
        variance = sum((s - avg) ** 2 for s in syllable_counts) / len(syllable_counts)
        
        # Low variance = high regularity
        regularity = max(0, 100 - variance * 30)
        
        return regularity
    
    def _count_syllables(self, word):
        """Simple syllable counter"""
        word = word.lower()
        vowels = 'aeiouy'
        syllable_count = 0
        previous_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel
        
        # Adjust for silent e
        if word.endswith('e'):
            syllable_count = max(1, syllable_count - 1)
        
        return max(1, syllable_count)
    
    def _calculate_flow(self, name):
        """Calculate pronunciation flow/smoothness"""
        name_lower = name.lower()
        
        # Consonant clusters reduce flow
        clusters = re.findall(r'[bcdfghjklmnpqrstvwxyz]{3,}', name_lower)
        cluster_penalty = len(clusters) * 15
        
        # Vowel-consonant alternation increases flow
        alternation_score = self._calculate_alternation(name_lower)
        
        # Length affects flow (very long = harder to say smoothly)
        length_penalty = max(0, (len(name) - 10) * 2)
        
        flow = 100 - cluster_penalty + alternation_score - length_penalty
        
        return max(0, min(100, flow))
    
    def _calculate_alternation(self, name):
        """Calculate vowel-consonant alternation"""
        if len(name) < 2:
            return 0
        
        alternations = 0
        for i in range(len(name) - 1):
            curr_is_vowel = name[i] in 'aeiou'
            next_is_vowel = name[i+1] in 'aeiou'
            if curr_is_vowel != next_is_vowel:
                alternations += 1
        
        # More alternation = smoother flow
        alternation_ratio = alternations / (len(name) - 1)
        return alternation_ratio * 30
    
    def _calculate_vowel_harmony(self, name):
        """Calculate vowel harmony (do vowels match in quality?)"""
        vowels = [c for c in name.lower() if c in 'aeiou']
        
        if len(vowels) <= 1:
            return 80  # Single vowel = harmonious
        
        # Check if all front or all back
        front = sum(1 for v in vowels if v in 'ie')
        back = sum(1 for v in vowels if v in 'ou')
        
        if front == len(vowels) or back == len(vowels):
            return 100  # Perfect harmony
        
        # Partial harmony
        dominant = max(front, back)
        harmony = (dominant / len(vowels)) * 100
        
        return harmony
    
    def _calculate_singability(self, name, rhythm, flow):
        """Can you chant/sing this name easily?"""
        # Simple formula: rhythm + flow + bonus for short names
        base = (rhythm + flow) / 2
        
        # Short names easier to chant
        if len(name) <= 6:
            base += 10
        
        return min(100, base)

