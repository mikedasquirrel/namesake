"""
Phonetic Universals Analyzer
============================

Analyzes cross-linguistic phonetic universal patterns and sound symbolism.
Tests Bouba/Kiki effect, size symbolism, and other universal sound-meaning associations.
"""

import logging
import numpy as np
from typing import Dict, List
from collections import Counter

logger = logging.getLogger(__name__)


class PhoneticUniversalsAnalyzer:
    """Analyze universal phonetic patterns across languages."""
    
    # Bouba/Kiki associations
    ROUNDED_PHONEMES = ['b', 'm', 'w', 'o', 'u']  # Round/soft sounds
    ANGULAR_PHONEMES = ['k', 't', 'p', 'i', 'e']  # Angular/sharp sounds
    
    # Size symbolism
    SMALL_PHONEMES = ['i', 'e', 't', 'p', 'k']  # High frequency = small
    LARGE_PHONEMES = ['o', 'u', 'a', 'b', 'g']  # Low frequency = large
    
    # Speed/motion symbolism
    FAST_PHONEMES = ['s', 'z', 'f', 'v', 'sh']  # Fricatives = speed
    SLOW_PHONEMES = ['m', 'n', 'l']  # Sonorants = slowness
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("PhoneticUniversalsAnalyzer initialized")
    
    def analyze(self, name: str) -> Dict:
        """Complete phonetic universals analysis."""
        phonemes = self._name_to_phonemes(name.lower())
        
        return {
            'name': name,
            'bouba_kiki': self._analyze_bouba_kiki(phonemes),
            'size_symbolism': self._analyze_size_symbolism(phonemes),
            'speed_symbolism': self._analyze_speed_symbolism(phonemes),
            'emotional_valence': self._analyze_emotional_valence(phonemes),
            'phoneme_ratios': self._analyze_phoneme_ratios(phonemes),
            'semantic_associations': self._analyze_semantic_associations(phonemes),
            'language_families': self._analyze_language_fit(phonemes),
            'universals': self._check_universal_violations(phonemes),
            'iconicity': self._analyze_iconicity(name, phonemes)
        }
    
    def _name_to_phonemes(self, name: str) -> List[str]:
        """Convert name to phoneme list."""
        return list(name.replace(' ', ''))
    
    def _analyze_bouba_kiki(self, phonemes: List[str]) -> Dict:
        """Analyze Bouba/Kiki effect."""
        rounded_count = sum(1 for p in phonemes if p in self.ROUNDED_PHONEMES)
        angular_count = sum(1 for p in phonemes if p in self.ANGULAR_PHONEMES)
        
        total = len(phonemes)
        if total == 0:
            return {'score': 0, 'roundness': 0.5, 'angularity': 0.5}
        
        roundness = rounded_count / total
        angularity = angular_count / total
        
        # Score: -1 (angular/kiki) to +1 (round/bouba)
        score = roundness - angularity
        
        return {
            'score': float(score),
            'roundness': float(roundness),
            'angularity': float(angularity)
        }
    
    def _analyze_size_symbolism(self, phonemes: List[str]) -> Dict:
        """Analyze size sound symbolism."""
        small_count = sum(1 for p in phonemes if p in self.SMALL_PHONEMES)
        large_count = sum(1 for p in phonemes if p in self.LARGE_PHONEMES)
        
        total = len(phonemes)
        if total == 0:
            return {'score': 0, 'high_vowel_freq': 0, 'low_vowel_freq': 0}
        
        # Score: -1 (small) to +1 (large)
        score = (large_count - small_count) / total
        
        high_vowels = sum(1 for p in phonemes if p in ['i', 'e'])
        low_vowels = sum(1 for p in phonemes if p in ['a', 'o', 'u'])
        
        return {
            'score': float(score),
            'high_vowel_freq': float(high_vowels / total),
            'low_vowel_freq': float(low_vowels / total)
        }
    
    def _analyze_speed_symbolism(self, phonemes: List[str]) -> Dict:
        """Analyze speed/motion symbolism."""
        fast_count = sum(1 for p in phonemes if p in self.FAST_PHONEMES)
        slow_count = sum(1 for p in phonemes if p in self.SLOW_PHONEMES)
        
        total = len(phonemes)
        if total == 0:
            return {'score': 0, 'fricative_freq': 0, 'stop_freq': 0}
        
        score = (fast_count - slow_count) / total
        
        fricatives = sum(1 for p in phonemes if p in ['s', 'z', 'f', 'v', 'sh'])
        stops = sum(1 for p in phonemes if p in ['p', 't', 'k', 'b', 'd', 'g'])
        
        return {
            'score': float(score),
            'fricative_freq': float(fricatives / total),
            'stop_freq': float(stops / total)
        }
    
    def _analyze_emotional_valence(self, phonemes: List[str]) -> Dict:
        """Analyze universal emotional valence."""
        positive_phonemes = ['m', 'n', 'l', 'w', 'a', 'o']  # Soft, sonorant
        negative_phonemes = ['k', 't', 'p', 's', 'z']  # Harsh, voiceless
        
        pos_count = sum(1 for p in phonemes if p in positive_phonemes)
        neg_count = sum(1 for p in phonemes if p in negative_phonemes)
        
        total = len(phonemes)
        if total == 0:
            return {'universal': 0, 'pleasantness': 0.5, 'harshness': 0.5}
        
        valence = (pos_count - neg_count) / total
        pleasantness = pos_count / total
        harshness = neg_count / total
        
        return {
            'universal': float(valence),
            'pleasantness': float(pleasantness),
            'harshness': float(harshness)
        }
    
    def _analyze_phoneme_ratios(self, phonemes: List[str]) -> Dict:
        """Analyze phoneme type ratios."""
        total = len(phonemes)
        if total == 0:
            return {'sonorant': 0, 'voiceless': 0, 'front_vowel': 0, 'back_vowel': 0}
        
        sonorants = sum(1 for p in phonemes if p in ['m', 'n', 'l', 'r', 'w', 'y'])
        voiceless = sum(1 for p in phonemes if p in ['p', 't', 'k', 'f', 's', 'sh', 'h'])
        front_vowels = sum(1 for p in phonemes if p in ['i', 'e'])
        back_vowels = sum(1 for p in phonemes if p in ['o', 'u'])
        
        return {
            'sonorant': float(sonorants / total),
            'voiceless': float(voiceless / total),
            'front_vowel': float(front_vowels / total),
            'back_vowel': float(back_vowels / total)
        }
    
    def _analyze_semantic_associations(self, phonemes: List[str]) -> Dict:
        """Analyze semantic associations (brightness, hardness, etc.)."""
        # Brightness: front vowels + high frequency consonants
        bright_phonemes = ['i', 'e', 's', 't', 'p']
        dark_phonemes = ['u', 'o', 'b', 'g']
        
        # Hardness: stops
        hard_phonemes = ['k', 't', 'p', 'g', 'd', 'b']
        soft_phonemes = ['m', 'n', 'l', 'w']
        
        total = len(phonemes)
        if total == 0:
            return {'brightness': 0, 'hardness': 0, 'wetness': 0}
        
        brightness = (sum(1 for p in phonemes if p in bright_phonemes) - 
                     sum(1 for p in phonemes if p in dark_phonemes)) / total
        
        hardness = (sum(1 for p in phonemes if p in hard_phonemes) - 
                   sum(1 for p in phonemes if p in soft_phonemes)) / total
        
        # Wetness: liquids
        wetness = sum(1 for p in phonemes if p in ['l', 'r', 'w']) / total
        
        return {
            'brightness': float(brightness),
            'hardness': float(hardness),
            'wetness': float(wetness)
        }
    
    def _analyze_language_fit(self, phonemes: List[str]) -> Dict:
        """Analyze fit to different language family phonologies."""
        # Simplified patterns
        return {
            'germanic': self._check_germanic_fit(phonemes),
            'romance': self._check_romance_fit(phonemes),
            'slavic': self._check_slavic_fit(phonemes),
            'sinitic': self._check_sinitic_fit(phonemes),
            'semitic': self._check_semitic_fit(phonemes)
        }
    
    def _check_germanic_fit(self, phonemes: List[str]) -> float:
        """Check fit to Germanic phonology (allows complex clusters)."""
        # Germanic allows initial and final clusters
        has_clusters = any(phonemes[i:i+2] for i in range(len(phonemes)-1) 
                          if all(p not in 'aeiou' for p in phonemes[i:i+2]))
        return 0.8 if has_clusters else 0.5
    
    def _check_romance_fit(self, phonemes: List[str]) -> float:
        """Check fit to Romance phonology (prefers CV structure)."""
        # Romance prefers alternating CV
        alternations = sum(1 for i in range(len(phonemes)-1) 
                          if (phonemes[i] in 'aeiou') != (phonemes[i+1] in 'aeiou'))
        return alternations / (len(phonemes) - 1) if len(phonemes) > 1 else 0.5
    
    def _check_slavic_fit(self, phonemes: List[str]) -> float:
        """Check fit to Slavic phonology (complex clusters OK)."""
        return 0.7  # Simplified
    
    def _check_sinitic_fit(self, phonemes: List[str]) -> float:
        """Check fit to Chinese phonology (minimal clusters, tone-based)."""
        # Penalize clusters
        has_clusters = any(phonemes[i:i+2] for i in range(len(phonemes)-1) 
                          if all(p not in 'aeiou' for p in phonemes[i:i+2]))
        return 0.3 if has_clusters else 0.8
    
    def _check_semitic_fit(self, phonemes: List[str]) -> float:
        """Check fit to Semitic phonology (root-pattern morphology)."""
        # Semitic has pharyngeal and emphatic consonants
        return 0.6  # Simplified
    
    def _check_universal_violations(self, phonemes: List[str]) -> Dict:
        """Check for phonotactic universal violations."""
        violations = []
        
        # Universal: No language starts words with 'ng'
        if phonemes and phonemes[0:2] == ['n', 'g']:
            violations.append("Initial 'ng' cluster (universal violation)")
        
        # Most languages avoid three+ consonant clusters
        for i in range(len(phonemes)-2):
            if all(p not in 'aeiou' for p in phonemes[i:i+3]):
                violations.append("Triple consonant cluster")
                break
        
        rarity = len(violations) / 10.0  # Normalize
        
        return {
            'violates': len(violations) > 0,
            'violations': violations,
            'rarity': float(min(rarity, 1.0))
        }
    
    def _analyze_iconicity(self, name: str, phonemes: List[str]) -> Dict:
        """Analyze iconicity (form-meaning transparency)."""
        # Simple heuristics
        onomatopoeia = 0.0
        if any(p in phonemes for p in ['z', 's', 'sh', 'f']):  # Sound-like
            onomatopoeia = 0.3
        
        # Overall iconicity
        iconicity = onomatopoeia
        
        return {
            'onomatopoeia': float(onomatopoeia),
            'overall': float(iconicity)
        }


# Singleton
phonetic_universals_analyzer = PhoneticUniversalsAnalyzer()

