"""
Advanced Linguistic Analysis Engine
20+ new dimensions for deep name analysis
"""

import re
from collections import Counter
import math


class AdvancedAnalyzer:
    """Advanced linguistic and psychological analysis of cryptocurrency names"""
    
    def __init__(self):
        # Sound symbolism phonesthemes
        self.phonesthemes = {
            'gl-': ('light', 'gleam'),
            'sn-': ('nose', 'snout'),
            'sl-': ('slip', 'slide'),
            'gr-': ('rough', 'grasp'),
            'fl-': ('flow', 'flutter'),
            'cr-': ('break', 'crash'),
            'sp-': ('point', 'spray'),
            'tw-': ('twist', 'twin'),
            'sw-': ('sweep', 'swift'),
            'br-': ('break', 'bright')
        }
        
        # Vowel emotional mapping
        self.vowel_emotions = {
            'i': 'bright',  # High front vowel = brightness, smallness
            'e': 'moderate_bright',
            'a': 'open',  # Open vowel = largeness, openness
            'o': 'round',  # Rounded = roundness, fullness
            'u': 'dark'  # Back vowel = darkness, depth
        }
        
        # Cultural power words
        self.power_words = {
            'dragon': 'mythical_power',
            'titan': 'strength',
            'samurai': 'honor',
            'phoenix': 'rebirth',
            'infinity': 'endless',
            'quantum': 'advanced',
            'stellar': 'celestial',
            'terra': 'earth',
            'luna': 'moon',
            'sol': 'sun',
            'cosmos': 'universe',
            'nexus': 'connection',
            'apex': 'peak',
            'alpha': 'first',
            'omega': 'last',
            'meta': 'beyond',
            'ultra': 'extreme',
            'hyper': 'intense',
            'mega': 'large',
            'giga': 'massive'
        }
        
        # Psychological triggers
        self.psych_triggers = {
            'trust': ['safe', 'secure', 'trust', 'stable', 'solid'],
            'innovation': ['new', 'next', 'future', 'quantum', 'meta', 'ultra'],
            'luxury': ['gold', 'diamond', 'platinum', 'royal', 'elite'],
            'community': ['people', 'social', 'share', 'together', 'united'],
            'urgency': ['now', 'fast', 'instant', 'rapid', 'speed'],
            'power': ['titan', 'dragon', 'apex', 'supreme', 'dominant']
        }
    
    def analyze(self, name, existing_names=None):
        """
        Perform comprehensive advanced analysis
        
        Returns dict with 20+ new metrics
        """
        analysis = {}
        
        name_lower = name.lower()
        
        # 1. Sound Symbolism
        analysis['phonestheme_score'] = self._analyze_phonesthemes(name_lower)
        analysis['phonestheme_type'] = self._get_phonestheme_type(name_lower)
        
        # 2. Vowel Emotion Mapping
        analysis['vowel_brightness'] = self._calculate_vowel_brightness(name_lower)
        analysis['vowel_emotion_profile'] = self._get_vowel_emotion_profile(name_lower)
        
        # 3. Consonant Hardness/Softness
        analysis['consonant_hardness'] = self._calculate_consonant_hardness(name_lower)
        
        # 4. Rhythmic Pattern
        analysis['rhythmic_pattern'] = self._analyze_rhythm(name_lower)
        analysis['rhythm_score'] = self._score_rhythm(analysis['rhythmic_pattern'])
        
        # 5. Alliteration & Assonance
        analysis['alliteration_score'] = self._detect_alliteration(name_lower)
        analysis['assonance_score'] = self._detect_assonance(name_lower)
        
        # 6. Cultural Power Words
        analysis['power_word_count'] = self._count_power_words(name_lower)
        analysis['power_word_types'] = self._identify_power_words(name_lower)
        
        # 7. Psychological Impact
        analysis['authority_score'] = self._calculate_authority(name_lower)
        analysis['innovation_score'] = self._calculate_innovation(name_lower)
        analysis['trust_score'] = self._calculate_trust(name_lower)
        analysis['luxury_score'] = self._calculate_luxury(name_lower)
        analysis['urgency_score'] = self._calculate_urgency(name_lower)
        analysis['community_score'] = self._calculate_community(name_lower)
        
        # 8. Visual & Typography
        analysis['visual_symmetry'] = self._calculate_visual_symmetry(name)
        analysis['letter_complexity'] = self._calculate_letter_complexity(name)
        analysis['logo_friendliness'] = self._calculate_logo_friendliness(name)
        
        # 9. Semantic Positioning
        analysis['tech_modernity_score'] = self._calculate_tech_modernity(name_lower)
        analysis['nature_tech_spectrum'] = self._position_nature_tech(name_lower)
        analysis['abstract_concrete_spectrum'] = self._position_abstract_concrete(name_lower)
        analysis['currency_distance'] = self._calculate_currency_distance(name_lower)
        
        # 10. Advanced Pattern Recognition
        analysis['repetition_pattern'] = self._analyze_repetition(name_lower)
        analysis['letter_diversity'] = self._calculate_letter_diversity(name)
        
        return analysis
    
    def _analyze_phonesthemes(self, name):
        """Detect sound symbolism patterns"""
        score = 0
        for phonestheme in self.phonesthemes.keys():
            if name.startswith(phonestheme):
                score += 10
        return min(100, score)
    
    def _get_phonestheme_type(self, name):
        """Identify specific phonestheme type"""
        for phonestheme, (meaning, _) in self.phonesthemes.items():
            if name.startswith(phonestheme):
                return meaning
        return 'none'
    
    def _calculate_vowel_brightness(self, name):
        """Calculate overall vowel brightness (0-100)"""
        vowels = [c for c in name if c in 'aeiou']
        if not vowels:
            return 50
        
        brightness_map = {'i': 100, 'e': 75, 'a': 50, 'o': 25, 'u': 0}
        avg_brightness = sum(brightness_map.get(v, 50) for v in vowels) / len(vowels)
        return round(avg_brightness, 2)
    
    def _get_vowel_emotion_profile(self, name):
        """Get dominant vowel emotion"""
        vowels = [c for c in name if c in 'aeiou']
        if not vowels:
            return 'neutral'
        
        emotion_counts = Counter(self.vowel_emotions.get(v, 'neutral') for v in vowels)
        return emotion_counts.most_common(1)[0][0]
    
    def _calculate_consonant_hardness(self, name):
        """Calculate consonant hardness (0-100)"""
        hard_consonants = set('kptgdbcq')
        soft_consonants = set('lmnrsfvwyz')
        
        consonants = [c for c in name if c.isalpha() and c not in 'aeiou']
        if not consonants:
            return 50
        
        hard_count = sum(1 for c in consonants if c in hard_consonants)
        soft_count = sum(1 for c in consonants if c in soft_consonants)
        
        if hard_count + soft_count == 0:
            return 50
        
        hardness = (hard_count / (hard_count + soft_count)) * 100
        return round(hardness, 2)
    
    def _analyze_rhythm(self, name):
        """Analyze rhythmic pattern (syllable stress)"""
        # Simplified: detect alternating patterns
        vowel_positions = [i for i, c in enumerate(name) if c in 'aeiou']
        
        if len(vowel_positions) < 2:
            return 'monotone'
        
        gaps = [vowel_positions[i+1] - vowel_positions[i] for i in range(len(vowel_positions)-1)]
        avg_gap = sum(gaps) / len(gaps)
        
        if avg_gap < 2:
            return 'rapid'
        elif avg_gap > 3:
            return 'slow'
        else:
            return 'moderate'
    
    def _score_rhythm(self, pattern):
        """Score rhythmic appeal (0-100)"""
        scores = {'moderate': 80, 'rapid': 60, 'slow': 40, 'monotone': 20}
        return scores.get(pattern, 50)
    
    def _detect_alliteration(self, name):
        """Detect alliteration (repeated initial consonants)"""
        words = re.findall(r'[a-z]+', name)
        if len(words) < 2:
            return 0
        
        initials = [w[0] for w in words if w]
        if len(set(initials)) < len(initials):
            return 100
        return 0
    
    def _detect_assonance(self, name):
        """Detect assonance (repeated vowel sounds)"""
        vowels = [c for c in name if c in 'aeiou']
        if len(vowels) < 2:
            return 0
        
        most_common = Counter(vowels).most_common(1)[0][1]
        assonance = (most_common / len(vowels)) * 100
        return round(assonance, 2)
    
    def _count_power_words(self, name):
        """Count power words in name"""
        count = 0
        for power_word in self.power_words.keys():
            if power_word in name:
                count += 1
        return count
    
    def _identify_power_words(self, name):
        """Identify specific power words"""
        found = []
        for power_word, word_type in self.power_words.items():
            if power_word in name:
                found.append(word_type)
        return found if found else ['none']
    
    def _calculate_authority(self, name):
        """Calculate authority/trust score"""
        authority_signals = ['trust', 'safe', 'secure', 'prime', 'pro', 'master', 'expert']
        score = sum(30 for signal in authority_signals if signal in name)
        
        # Longer names often perceived as more authoritative
        if len(name) > 8:
            score += 20
        
        return min(100, score)
    
    def _calculate_innovation(self, name):
        """Calculate innovation perception"""
        innovation_signals = ['new', 'next', 'future', 'quantum', 'meta', 'ultra', 'neo', 'x', 'ai']
        score = sum(25 for signal in innovation_signals if signal in name)
        
        # Presence of numbers or special chars
        if re.search(r'\d', name):
            score += 15
        
        return min(100, score)
    
    def _calculate_trust(self, name):
        """Calculate trust signals"""
        trust_words = self.psych_triggers['trust']
        score = sum(30 for word in trust_words if word in name)
        
        # Familiarity (real words) increase trust
        common_roots = ['bit', 'coin', 'cash', 'pay', 'bank']
        if any(root in name for root in common_roots):
            score += 25
        
        return min(100, score)
    
    def _calculate_luxury(self, name):
        """Calculate luxury positioning"""
        luxury_words = self.psych_triggers['luxury']
        score = sum(35 for word in luxury_words if word in name)
        return min(100, score)
    
    def _calculate_urgency(self, name):
        """Calculate urgency/FOMO triggers"""
        urgency_words = self.psych_triggers['urgency']
        score = sum(30 for word in urgency_words if word in name)
        return min(100, score)
    
    def _calculate_community(self, name):
        """Calculate community belonging cues"""
        community_words = self.psych_triggers['community']
        score = sum(30 for word in community_words if word in name)
        return min(100, score)
    
    def _calculate_visual_symmetry(self, name):
        """Calculate visual symmetry (0-100)"""
        # Check if palindrome or near-palindrome
        reversed_name = name[::-1].lower()
        name_lower = name.lower()
        
        # Perfect palindrome
        if name_lower == reversed_name:
            return 100
        
        # Calculate character-wise similarity
        matches = sum(1 for a, b in zip(name_lower, reversed_name) if a == b)
        symmetry = (matches / len(name)) * 100
        
        return round(symmetry, 2)
    
    def _calculate_letter_complexity(self, name):
        """Calculate visual complexity of letters"""
        # Complex letters: MWQKXZ (many strokes/angles)
        # Simple letters: IOCTL (few strokes)
        complex_letters = set('MWQKXZNHBRmwqkxznhbr')
        simple_letters = set('IOCTLioctl')
        
        complexity_score = 0
        for char in name:
            if char in complex_letters:
                complexity_score += 2
            elif char in simple_letters:
                complexity_score += 0.5
            else:
                complexity_score += 1
        
        # Normalize to 0-100
        max_complexity = len(name) * 2
        normalized = (complexity_score / max_complexity) * 100
        return round(normalized, 2)
    
    def _calculate_logo_friendliness(self, name):
        """Calculate logo design friendliness"""
        score = 100
        
        # Penalize very long names
        if len(name) > 10:
            score -= 30
        elif len(name) > 7:
            score -= 15
        
        # Penalize numbers and special chars
        if re.search(r'\d', name):
            score -= 10
        if re.search(r'[^a-zA-Z0-9]', name):
            score -= 15
        
        # Reward distinctiveness (unique first letter)
        if name[0].upper() in 'XZQK':
            score += 10
        
        return max(0, min(100, score))
    
    def _calculate_tech_modernity(self, name):
        """Calculate technology modernity score"""
        tech_signals = ['bit', 'byte', 'chain', 'link', 'net', 'web', 'cyber', 
                       'digital', 'crypto', 'meta', 'quantum', 'nano', 'ai', 'ml']
        
        score = sum(20 for signal in tech_signals if signal in name)
        
        # Shortened forms indicate modernity
        if len(name) <= 4 and name.isalpha():
            score += 25
        
        return min(100, score)
    
    def _position_nature_tech(self, name):
        """Position on nature-tech spectrum (-100 to 100)"""
        nature_words = ['terra', 'luna', 'sol', 'star', 'moon', 'sun', 'earth', 
                       'water', 'fire', 'wind', 'tree', 'leaf']
        tech_words = ['bit', 'byte', 'chain', 'link', 'net', 'cyber', 'digital', 
                     'quantum', 'nano', 'tech']
        
        nature_score = sum(20 for word in nature_words if word in name)
        tech_score = sum(20 for word in tech_words if word in name)
        
        # -100 = pure nature, +100 = pure tech
        spectrum = tech_score - nature_score
        return max(-100, min(100, spectrum))
    
    def _position_abstract_concrete(self, name):
        """Position on abstract-concrete spectrum (-100 to 100)"""
        concrete_words = ['coin', 'cash', 'gold', 'silver', 'dollar', 'money', 'pay']
        abstract_words = ['infinity', 'cosmos', 'nexus', 'aether', 'void', 'quantum']
        
        concrete_score = sum(20 for word in concrete_words if word in name)
        abstract_score = sum(20 for word in abstract_words if word in name)
        
        # -100 = concrete, +100 = abstract
        spectrum = abstract_score - concrete_score
        return max(-100, min(100, spectrum))
    
    def _calculate_currency_distance(self, name):
        """Calculate conceptual distance from traditional currency (0-100)"""
        currency_words = ['coin', 'cash', 'money', 'dollar', 'pay', 'bank', 'currency']
        
        # Higher score = more distant from traditional currency concepts
        if any(word in name for word in currency_words):
            return 0
        
        # Check for financial tech words
        fintech_words = ['swap', 'trade', 'exchange', 'defi', 'finance']
        if any(word in name for word in fintech_words):
            return 40
        
        # Everything else is quite distant
        return 80
    
    def _analyze_repetition(self, name):
        """Analyze letter repetition patterns"""
        letter_counts = Counter(name.lower())
        
        if not letter_counts:
            return 'none'
        
        max_repetition = max(letter_counts.values())
        
        if max_repetition >= 3:
            return 'high'
        elif max_repetition == 2:
            return 'moderate'
        else:
            return 'low'
    
    def _calculate_letter_diversity(self, name):
        """Calculate letter diversity (0-100)"""
        if not name:
            return 0
        
        unique_letters = len(set(name.lower()))
        total_letters = len([c for c in name if c.isalpha()])
        
        if total_letters == 0:
            return 0
        
        diversity = (unique_letters / total_letters) * 100
        return round(diversity, 2)

