"""
Sound Symbolism Analyzer
Psychological associations with sounds (Bouba/Kiki effect, etc.)
"""

import logging

logger = logging.getLogger(__name__)


class SoundSymbolismAnalyzer:
    """Analyze sound-meaning associations"""
    
    def __init__(self):
        # Bouba/Kiki effect categories
        self.round_sounds = set('lmnr')  # Sonorants = round, soft
        self.sharp_sounds = set('ptkszfv')  # Obstruents = sharp, angular
        
        # Size symbolism
        self.small_sounds = set('ie')  # High front vowels = small
        self.large_sounds = set('oua')  # Low back vowels = large
        
        # Speed symbolism
        self.fast_consonants = set('ptkfszh')  # Voiceless = fast
        self.slow_consonants = set('bdgvzmnl')  # Voiced/sonorants = slow
        
        # Brightness
        self.bright_vowels = set('ie')  # Front = bright
        self.dark_vowels = set('ou')  # Back = dark
        
        # Strength
        self.strong_consonants = set('ptk')  # Voiceless plosives = strong
        self.weak_consonants = set('fvsh')  # Fricatives = weak
    
    def analyze(self, name):
        """Analyze sound symbolism"""
        name_lower = name.lower()
        
        # Bouba/Kiki score
        round_count = sum(1 for c in name_lower if c in self.round_sounds)
        sharp_count = sum(1 for c in name_lower if c in self.sharp_sounds)
        total_sounds = round_count + sharp_count
        
        if total_sounds > 0:
            roundness_score = (round_count / total_sounds) * 100
            sharpness_score = (sharp_count / total_sounds) * 100
        else:
            roundness_score = 50
            sharpness_score = 50
        
        # Determine bouba/kiki classification
        if roundness_score > 60:
            bouba_kiki = 'bouba'  # Round, soft, friendly
        elif sharpness_score > 60:
            bouba_kiki = 'kiki'  # Sharp, angular, precise
        else:
            bouba_kiki = 'balanced'
        
        # Size symbolism
        vowels = [c for c in name_lower if c in 'aeiou']
        small_vowel_count = sum(1 for v in vowels if v in self.small_sounds)
        large_vowel_count = sum(1 for v in vowels if v in self.large_sounds)
        
        if len(vowels) > 0:
            size_symbolism_score = (small_vowel_count / len(vowels)) * 100
        else:
            size_symbolism_score = 50
        
        if size_symbolism_score > 60:
            size_association = 'small/fast'
        elif size_symbolism_score < 40:
            size_association = 'large/slow'
        else:
            size_association = 'neutral'
        
        # Speed symbolism
        consonants = [c for c in name_lower if c.isalpha() and c not in 'aeiou']
        fast_count = sum(1 for c in consonants if c in self.fast_consonants)
        slow_count = sum(1 for c in consonants if c in self.slow_consonants)
        
        if len(consonants) > 0:
            speed_score = (fast_count / len(consonants)) * 100
        else:
            speed_score = 50
        
        if speed_score > 60:
            speed_association = 'fast/dynamic'
        elif speed_score < 40:
            speed_association = 'slow/steady'
        else:
            speed_association = 'moderate'
        
        # Brightness
        bright_count = sum(1 for v in vowels if v in self.bright_vowels)
        dark_count = sum(1 for v in vowels if v in self.dark_vowels)
        
        if len(vowels) > 0:
            brightness_score = (bright_count / len(vowels)) * 100
        else:
            brightness_score = 50
        
        if brightness_score > 60:
            brightness = 'bright/energetic'
        elif brightness_score < 40:
            brightness = 'dark/serious'
        else:
            brightness = 'neutral'
        
        # Strength symbolism
        strong_count = sum(1 for c in consonants if c in self.strong_consonants)
        
        if len(consonants) > 0:
            strength_score = (strong_count / len(consonants)) * 100
        else:
            strength_score = 50
        
        if strength_score > 60:
            strength_perception = 'strong/authoritative'
        elif strength_score < 40:
            strength_perception = 'soft/approachable'
        else:
            strength_perception = 'balanced'
        
        return {
            'bouba_kiki_type': bouba_kiki,
            'roundness_score': round(roundness_score, 1),
            'sharpness_score': round(sharpness_score, 1),
            'size_association': size_association,
            'size_symbolism_score': round(size_symbolism_score, 1),
            'speed_association': speed_association,
            'speed_score': round(speed_score, 1),
            'brightness': brightness,
            'brightness_score': round(brightness_score, 1),
            'strength_perception': strength_perception,
            'strength_score': round(strength_score, 1),
            'sound_symbolism_quality': self._calculate_symbolism_quality(bouba_kiki, size_association, speed_association)
        }
    
    def _calculate_symbolism_quality(self, bouba_kiki, size, speed):
        """Calculate overall sound symbolism effectiveness"""
        score = 50
        
        # Sharp sounds good for tech
        if bouba_kiki == 'kiki':
            score += 15
        
        # Small/fast associations modern/dynamic
        if 'fast' in speed or 'small' in size:
            score += 10
        
        return min(100, score)

