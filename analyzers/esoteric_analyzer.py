"""
Esoteric Analysis Engine
Numerology, archetypes, frequencies, chaos theory - taking the radical theory seriously
"""

import re
import math
from collections import Counter
from datetime import datetime


class EsotericAnalyzer:
    """Unconventional but systematic analysis methods"""
    
    def __init__(self):
        # Pythagorean number system (A=1, B=2, etc.)
        self.pythagorean = {chr(i): (i - 64) % 9 or 9 for i in range(65, 91)}
        self.pythagorean.update({chr(i): (i - 96) % 9 or 9 for i in range(97, 123)})
        
        # Chaldean number system (different values)
        self.chaldean = {
            'a': 1, 'i': 1, 'j': 1, 'q': 1, 'y': 1,
            'b': 2, 'k': 2, 'r': 2,
            'c': 3, 'g': 3, 'l': 3, 's': 3,
            'd': 4, 'm': 4, 't': 4,
            'e': 5, 'h': 5, 'n': 5, 'x': 5,
            'u': 6, 'v': 6, 'w': 6,
            'o': 7, 'z': 7,
            'f': 8, 'p': 8
        }
        
        # Jungian archetypes
        self.archetypes = {
            'hero': ['hero', 'warrior', 'champion', 'titan', 'victory'],
            'sage': ['wise', 'oracle', 'prophet', 'truth', 'knowledge'],
            'explorer': ['quest', 'journey', 'discover', 'frontier', 'new'],
            'rebel': ['rebel', 'revolution', 'break', 'chaos', 'punk'],
            'magician': ['magic', 'transform', 'quantum', 'alchemy', 'wizard'],
            'ruler': ['king', 'queen', 'empire', 'throne', 'crown', 'supreme'],
            'creator': ['create', 'make', 'build', 'forge', 'craft'],
            'caregiver': ['care', 'safe', 'protect', 'secure', 'trust'],
            'jester': ['fun', 'play', 'meme', 'doge', 'shib'],
            'everyman': ['people', 'folk', 'common', 'community', 'social'],
            'lover': ['love', 'passion', 'heart', 'desire'],
            'innocent': ['pure', 'simple', 'basic', 'clean', 'white']
        }
        
        # Phonetic frequency base values (Hz) - simplified
        self.base_frequencies = {
            'a': 440, 'b': 493, 'c': 523, 'd': 587, 'e': 659,
            'f': 698, 'g': 784, 'h': 880, 'i': 988, 'j': 1046,
            'k': 1174, 'l': 1318, 'm': 1396, 'n': 1568, 'o': 1760,
            'p': 1975, 'q': 2093, 'r': 2349, 's': 2637, 't': 2793,
            'u': 3136, 'v': 3520, 'w': 3951, 'x': 4186, 'y': 4698, 'z': 5274
        }
        
        # Solfeggio frequencies (Hz) - ancient scale
        self.solfeggio = [174, 285, 396, 417, 528, 639, 741, 852, 963]
    
    def analyze(self, name, launch_date=None):
        """
        Perform esoteric analysis
        
        Args:
            name: Cryptocurrency name
            launch_date: Optional datetime of launch
            
        Returns:
            Dict with esoteric metrics
        """
        analysis = {}
        
        # 1. Numerological Analysis
        analysis['pythagorean_value'] = self._calculate_pythagorean(name)
        analysis['pythagorean_reduced'] = self._reduce_to_single(analysis['pythagorean_value'])
        analysis['chaldean_value'] = self._calculate_chaldean(name)
        analysis['chaldean_reduced'] = self._reduce_to_single(analysis['chaldean_value'])
        analysis['is_master_number'] = self._is_master_number(analysis['pythagorean_value'])
        analysis['numerology_interpretation'] = self._interpret_number(analysis['pythagorean_reduced'])
        
        # 2. Phonetic Frequency Analysis
        analysis['average_frequency'] = self._calculate_average_frequency(name)
        analysis['frequency_range'] = self._calculate_frequency_range(name)
        analysis['harmonic_ratio'] = self._calculate_harmonic_ratio(name)
        analysis['solfeggio_alignment'] = self._calculate_solfeggio_alignment(
            analysis['average_frequency']
        )
        
        # 3. Archetypal Pattern Matching
        analysis['primary_archetype'] = self._identify_archetype(name)
        analysis['archetype_strength'] = self._calculate_archetype_strength(name)
        analysis['archetype_multiplicity'] = self._count_archetypes(name)
        
        # 4. Temporal Correlations (if launch date provided)
        if launch_date:
            analysis['launch_numerology'] = self._analyze_launch_date(launch_date)
            analysis['name_date_synergy'] = self._calculate_synergy(
                analysis['pythagorean_reduced'],
                analysis['launch_numerology']
            )
        else:
            analysis['launch_numerology'] = None
            analysis['name_date_synergy'] = None
        
        # 5. Chaos & Complexity
        analysis['entropy'] = self._calculate_entropy(name)
        analysis['fractal_dimension'] = self._estimate_fractal_dimension(name)
        analysis['complexity_index'] = self._calculate_complexity(name)
        analysis['self_similarity'] = self._measure_self_similarity(name)
        
        # 6. Letter-Number Patterns
        analysis['digit_sum'] = self._sum_digits_in_name(name)
        analysis['letter_number_ratio'] = self._letter_number_ratio(name)
        
        # 7. Symmetry & Balance
        analysis['energetic_balance'] = self._calculate_energetic_balance(name)
        analysis['yin_yang_ratio'] = self._calculate_yin_yang(name)
        
        return analysis
    
    def _calculate_pythagorean(self, name):
        """Calculate Pythagorean numerology value"""
        return sum(self.pythagorean.get(c, 0) for c in name if c.isalpha())
    
    def _calculate_chaldean(self, name):
        """Calculate Chaldean numerology value"""
        return sum(self.chaldean.get(c.lower(), 0) for c in name if c.isalpha())
    
    def _reduce_to_single(self, number):
        """Reduce number to single digit (except master numbers)"""
        if number in [11, 22, 33]:  # Master numbers
            return number
        
        while number > 9:
            number = sum(int(d) for d in str(number))
        
        return number
    
    def _is_master_number(self, number):
        """Check if number is a master number"""
        return number in [11, 22, 33]
    
    def _interpret_number(self, number):
        """Interpret numerology number meaning"""
        interpretations = {
            1: 'leadership_innovation',
            2: 'balance_partnership',
            3: 'creativity_expression',
            4: 'stability_foundation',
            5: 'change_freedom',
            6: 'harmony_responsibility',
            7: 'wisdom_spirituality',
            8: 'power_abundance',
            9: 'completion_humanitarianism',
            11: 'illumination_intuition',
            22: 'master_builder',
            33: 'master_teacher'
        }
        return interpretations.get(number, 'unknown')
    
    def _calculate_average_frequency(self, name):
        """Calculate average phonetic frequency in Hz"""
        frequencies = [self.base_frequencies.get(c.lower(), 0) 
                      for c in name if c.isalpha()]
        
        if not frequencies:
            return 0
        
        return round(sum(frequencies) / len(frequencies), 2)
    
    def _calculate_frequency_range(self, name):
        """Calculate range of frequencies"""
        frequencies = [self.base_frequencies.get(c.lower(), 0) 
                      for c in name if c.isalpha()]
        
        if not frequencies:
            return 0
        
        return max(frequencies) - min(frequencies)
    
    def _calculate_harmonic_ratio(self, name):
        """Calculate harmonic ratio (golden ratio approximation)"""
        if len(name) < 2:
            return 0
        
        # Use letter frequencies to approximate harmonics
        avg_freq = self._calculate_average_frequency(name)
        
        # Golden ratio = 1.618
        # Calculate how close the name's structure is to golden proportions
        golden = 1.618
        
        # Compare vowel/consonant ratio to golden ratio
        vowels = sum(1 for c in name if c.lower() in 'aeiou')
        consonants = sum(1 for c in name if c.isalpha() and c.lower() not in 'aeiou')
        
        if consonants == 0:
            return 0
        
        ratio = vowels / consonants if consonants > 0 else 0
        proximity_to_golden = abs(ratio - golden) / golden
        
        # Convert to 0-100 score (closer = higher)
        return round((1 - proximity_to_golden) * 100, 2)
    
    def _calculate_solfeggio_alignment(self, frequency):
        """Calculate alignment with solfeggio frequencies"""
        if frequency == 0:
            return 0
        
        # Find closest solfeggio frequency
        closest = min(self.solfeggio, key=lambda x: abs(x - frequency))
        
        # Calculate alignment (closer = higher score)
        distance = abs(frequency - closest)
        max_distance = max(self.solfeggio) - min(self.solfeggio)
        
        alignment = (1 - distance / max_distance) * 100
        return round(alignment, 2)
    
    def _identify_archetype(self, name):
        """Identify primary Jungian archetype"""
        name_lower = name.lower()
        
        archetype_scores = {}
        for archetype, keywords in self.archetypes.items():
            score = sum(20 for keyword in keywords if keyword in name_lower)
            if score > 0:
                archetype_scores[archetype] = score
        
        if not archetype_scores:
            return 'unknown'
        
        return max(archetype_scores.items(), key=lambda x: x[1])[0]
    
    def _calculate_archetype_strength(self, name):
        """Calculate strength of archetypal association (0-100)"""
        name_lower = name.lower()
        
        total_score = 0
        for keywords in self.archetypes.values():
            total_score += sum(20 for keyword in keywords if keyword in name_lower)
        
        return min(100, total_score)
    
    def _count_archetypes(self, name):
        """Count how many archetypes are present"""
        name_lower = name.lower()
        
        count = 0
        for keywords in self.archetypes.values():
            if any(keyword in name_lower for keyword in keywords):
                count += 1
        
        return count
    
    def _analyze_launch_date(self, launch_date):
        """Analyze numerology of launch date"""
        if not launch_date:
            return None
        
        # Sum all digits in the date
        date_str = launch_date.strftime('%Y%m%d')
        total = sum(int(d) for d in date_str)
        
        return self._reduce_to_single(total)
    
    def _calculate_synergy(self, name_number, date_number):
        """Calculate synergy between name and launch date numbers"""
        if date_number is None:
            return None
        
        # Perfect match
        if name_number == date_number:
            return 100
        
        # Complementary numbers (add to 10)
        if name_number + date_number == 10:
            return 90
        
        # Similar vibration (within 2)
        diff = abs(name_number - date_number)
        if diff <= 2:
            return 70
        
        # Moderate synergy
        if diff <= 4:
            return 50
        
        # Low synergy
        return 30
    
    def _calculate_entropy(self, name):
        """Calculate Shannon entropy of the name"""
        if not name:
            return 0
        
        # Count character frequencies
        counter = Counter(name.lower())
        length = len(name)
        
        # Calculate Shannon entropy
        entropy = 0
        for count in counter.values():
            probability = count / length
            if probability > 0:
                entropy -= probability * math.log2(probability)
        
        # Normalize to 0-100
        max_entropy = math.log2(length) if length > 1 else 1
        normalized = (entropy / max_entropy) * 100 if max_entropy > 0 else 0
        
        return round(normalized, 2)
    
    def _estimate_fractal_dimension(self, name):
        """Estimate fractal dimension using box-counting approximation"""
        if len(name) < 2:
            return 1.0
        
        # Use character repetition patterns as proxy
        unique_chars = len(set(name.lower()))
        total_chars = len(name)
        
        if total_chars <= 1:
            return 1.0
        
        # Fractal dimension approximation
        dimension = math.log(unique_chars) / math.log(total_chars)
        
        return round(dimension, 3)
    
    def _calculate_complexity(self, name):
        """Calculate overall complexity index (0-100)"""
        if not name:
            return 0
        
        # Combine multiple complexity factors
        factors = []
        
        # Length complexity
        length_score = min(100, (len(name) / 15) * 100)
        factors.append(length_score)
        
        # Character diversity
        unique_ratio = len(set(name.lower())) / len(name)
        factors.append(unique_ratio * 100)
        
        # Case mixing
        has_upper = any(c.isupper() for c in name)
        has_lower = any(c.islower() for c in name)
        case_score = 50 if has_upper and has_lower else 25
        factors.append(case_score)
        
        # Special characters
        has_special = bool(re.search(r'[^a-zA-Z0-9]', name))
        special_score = 30 if has_special else 0
        factors.append(special_score)
        
        # Average all factors
        complexity = sum(factors) / len(factors)
        
        return round(complexity, 2)
    
    def _measure_self_similarity(self, name):
        """Measure self-similarity (repetition patterns)"""
        if len(name) < 2:
            return 0
        
        name_lower = name.lower()
        
        # Check for repeating substrings
        max_similarity = 0
        
        for length in range(2, len(name_lower) // 2 + 1):
            for i in range(len(name_lower) - length + 1):
                substring = name_lower[i:i+length]
                count = name_lower.count(substring)
                
                if count > 1:
                    similarity = (count * length) / len(name_lower) * 100
                    max_similarity = max(max_similarity, similarity)
        
        return round(max_similarity, 2)
    
    def _sum_digits_in_name(self, name):
        """Sum all digits found in the name"""
        digits = [int(c) for c in name if c.isdigit()]
        return sum(digits)
    
    def _letter_number_ratio(self, name):
        """Calculate ratio of letters to numbers"""
        letters = sum(1 for c in name if c.isalpha())
        numbers = sum(1 for c in name if c.isdigit())
        
        if numbers == 0:
            return 1000 if letters > 0 else 0  # Use large number instead of infinity
        
        return round(letters / numbers, 2)
    
    def _calculate_energetic_balance(self, name):
        """Calculate energetic balance using numerology"""
        # Even numbers = yin (receptive), Odd numbers = yang (active)
        pythagorean = self._calculate_pythagorean(name)
        
        # Count even vs odd letter values
        even_sum = 0
        odd_sum = 0
        
        for c in name:
            if c.isalpha():
                value = self.pythagorean.get(c, 0)
                if value % 2 == 0:
                    even_sum += value
                else:
                    odd_sum += value
        
        total = even_sum + odd_sum
        if total == 0:
            return 50  # Perfect balance
        
        # Return percentage of yang energy (odd)
        balance = (odd_sum / total) * 100
        return round(balance, 2)
    
    def _calculate_yin_yang(self, name):
        """Calculate yin/yang ratio (receptive vs active energy)"""
        # Yin letters (rounded, soft): o, c, s, u, g, q
        # Yang letters (sharp, angular): a, k, v, w, x, y, z, i, l, t
        
        yin_letters = set('ocsugq')
        yang_letters = set('akvwxyzilt')
        
        yin_count = sum(1 for c in name.lower() if c in yin_letters)
        yang_count = sum(1 for c in name.lower() if c in yang_letters)
        
        total = yin_count + yang_count
        if total == 0:
            return 50
        
        # Return percentage of yang
        ratio = (yang_count / total) * 100
        return round(ratio, 2)

