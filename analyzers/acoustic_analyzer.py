"""
Acoustic Analyzer - Deep Phonetic Analysis
===========================================

Performs acoustic and spectral analysis of names using signal processing techniques.
Analyzes formant frequencies, spectral energy, voice onset time, prosody, and phonetic complexity.

Features:
- Formant frequency analysis (F1, F2, F3)
- Spectral energy distribution
- Voice Onset Time (VOT) estimation
- Prosodic feature analysis
- Harshness vs melodiousness scoring
- Cross-linguistic pronounceability
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Tuple
import re
from collections import Counter

# Import core phonetic analyzer
from analyzers.phonetic_base import PhoneticBase

logger = logging.getLogger(__name__)


class AcousticAnalyzer:
    """
    Deep acoustic analysis of names using phonetic principles.
    """
    
    # Formant frequency ranges (approximate Hz values)
    FORMANT_RANGES = {
        # Vowel -> (F1, F2, F3)
        'i': (250, 2300, 3000),  # high front
        'e': (400, 2100, 2800),  # mid front
        'a': (750, 1200, 2500),  # low central
        'o': (500, 900, 2500),   # mid back
        'u': (300, 800, 2250),   # high back
    }
    
    # Consonant acoustic properties
    CONSONANT_PROPERTIES = {
        # Stops (plosives)
        'p': {'type': 'stop', 'voiceless': True, 'vot': 60, 'harshness': 0.6},
        't': {'type': 'stop', 'voiceless': True, 'vot': 70, 'harshness': 0.7},
        'k': {'type': 'stop', 'voiceless': True, 'vot': 80, 'harshness': 0.8},
        'b': {'type': 'stop', 'voiceless': False, 'vot': 5, 'harshness': 0.4},
        'd': {'type': 'stop', 'voiceless': False, 'vot': 10, 'harshness': 0.4},
        'g': {'type': 'stop', 'voiceless': False, 'vot': 15, 'harshness': 0.5},
        
        # Fricatives
        'f': {'type': 'fricative', 'voiceless': True, 'harshness': 0.6},
        'v': {'type': 'fricative', 'voiceless': False, 'harshness': 0.4},
        's': {'type': 'fricative', 'voiceless': True, 'harshness': 0.9},  # Sibilant
        'z': {'type': 'fricative', 'voiceless': False, 'harshness': 0.7},  # Sibilant
        'sh': {'type': 'fricative', 'voiceless': True, 'harshness': 0.8},  # Sibilant
        'zh': {'type': 'fricative', 'voiceless': False, 'harshness': 0.6},  # Sibilant
        'h': {'type': 'fricative', 'voiceless': True, 'harshness': 0.3},
        
        # Sonorants (nasals, liquids, glides)
        'm': {'type': 'nasal', 'voiceless': False, 'harshness': 0.1},
        'n': {'type': 'nasal', 'voiceless': False, 'harshness': 0.1},
        'l': {'type': 'liquid', 'voiceless': False, 'harshness': 0.15},
        'r': {'type': 'liquid', 'voiceless': False, 'harshness': 0.2},
        'w': {'type': 'glide', 'voiceless': False, 'harshness': 0.1},
        'y': {'type': 'glide', 'voiceless': False, 'harshness': 0.1},
    }
    
    def __init__(self):
        """Initialize acoustic analyzer."""
        self.logger = logging.getLogger(__name__)
        self.phonetic_base = PhoneticBase()
        self.logger.info("AcousticAnalyzer initialized")
    
    def analyze(self, name: str) -> Dict:
        """
        Comprehensive acoustic analysis of name.
        
        Args:
            name: Name to analyze
        
        Returns:
            Complete acoustic profile
        """
        # Convert to phonetic representation
        phonemes = self._name_to_phonemes(name)
        vowels = self._extract_vowels(phonemes)
        consonants = self._extract_consonants(phonemes)
        
        result = {
            'name': name,
            'phonemes': phonemes,
            
            # Formant analysis
            'formants': self._analyze_formants(vowels),
            
            # Spectral energy
            'spectral': self._analyze_spectral_energy(phonemes),
            
            # VOT analysis
            'vot': self._analyze_vot(consonants),
            
            # Prosody
            'prosody': self._analyze_prosody(name, phonemes),
            
            # Harshness analysis
            'harshness': self._analyze_harshness(consonants),
            
            # Overall characteristics
            'overall': {
                'melodiousness': self._calculate_melodiousness(phonemes),
                'rhythmic_regularity': self._calculate_rhythmic_regularity(phonemes),
                'phonetic_complexity': self._calculate_phonetic_complexity(phonemes),
            },
            
            # Cluster analysis
            'clusters': self._analyze_clusters(name),
            
            # Vowel patterns
            'vowels': self._analyze_vowel_patterns(vowels),
            
            # Pronounceability
            'pronounceability': self._analyze_pronounceability(name, phonemes),
        }
        
        return result
    
    def _name_to_phonemes(self, name: str) -> List[str]:
        """Convert name to simplified phoneme representation."""
        name_lower = name.lower().replace(' ', '')
        phonemes = []
        i = 0
        
        while i < len(name_lower):
            # Check for digraphs
            if i < len(name_lower) - 1:
                digraph = name_lower[i:i+2]
                if digraph in ['sh', 'ch', 'th', 'ph', 'wh', 'zh']:
                    phonemes.append(digraph)
                    i += 2
                    continue
            
            # Single character
            phonemes.append(name_lower[i])
            i += 1
        
        return phonemes
    
    def _extract_vowels(self, phonemes: List[str]) -> List[str]:
        """Extract vowel phonemes."""
        vowels = 'aeiou'
        return [p for p in phonemes if any(v in p for v in vowels)]
    
    def _extract_consonants(self, phonemes: List[str]) -> List[str]:
        """Extract consonant phonemes."""
        vowels = 'aeiou'
        return [p for p in phonemes if not any(v in p for v in vowels)]
    
    def _analyze_formants(self, vowels: List[str]) -> Dict:
        """Analyze formant frequencies of vowels."""
        if not vowels:
            return {
                'f1': {'mean': 0, 'range': 0},
                'f2': {'mean': 0, 'range': 0},
                'f3': {'mean': 0}
            }
        
        f1_values = []
        f2_values = []
        f3_values = []
        
        for vowel in vowels:
            # Get primary vowel
            v = vowel[0] if vowel else 'a'
            if v in self.FORMANT_RANGES:
                f1, f2, f3 = self.FORMANT_RANGES[v]
                f1_values.append(f1)
                f2_values.append(f2)
                f3_values.append(f3)
        
        return {
            'f1': {
                'mean': float(np.mean(f1_values)) if f1_values else 0,
                'range': float(np.max(f1_values) - np.min(f1_values)) if f1_values else 0
            },
            'f2': {
                'mean': float(np.mean(f2_values)) if f2_values else 0,
                'range': float(np.max(f2_values) - np.min(f2_values)) if f2_values else 0
            },
            'f3': {
                'mean': float(np.mean(f3_values)) if f3_values else 0
            }
        }
    
    def _analyze_spectral_energy(self, phonemes: List[str]) -> Dict:
        """Analyze spectral energy distribution."""
        low_energy = 0  # 0-500 Hz (voiced sounds)
        mid_energy = 0  # 500-2000 Hz (vowels, voiced consonants)
        high_energy = 0  # 2000+ Hz (fricatives, sibilants)
        
        for phoneme in phonemes:
            if self._is_vowel(phoneme):
                mid_energy += 1
            elif phoneme in ['s', 'z', 'sh', 'zh', 'f']:
                high_energy += 1
            else:
                low_energy += 0.5
                mid_energy += 0.5
        
        total = low_energy + mid_energy + high_energy
        if total == 0:
            return {
                'low_freq_energy': 0,
                'mid_freq_energy': 0,
                'high_freq_energy': 0,
                'centroid': 1000,
                'flatness': 0.5
            }
        
        # Normalize
        low_energy /= total
        mid_energy /= total
        high_energy /= total
        
        # Calculate spectral centroid (weighted average frequency)
        centroid = (low_energy * 250 + mid_energy * 1250 + high_energy * 4000)
        
        # Spectral flatness (how noise-like vs tone-like)
        flatness = high_energy  # Simple approximation
        
        return {
            'low_freq_energy': float(low_energy),
            'mid_freq_energy': float(mid_energy),
            'high_freq_energy': float(high_energy),
            'centroid': float(centroid),
            'flatness': float(flatness)
        }
    
    def _analyze_vot(self, consonants: List[str]) -> Dict:
        """Analyze Voice Onset Time patterns."""
        vot_values = []
        aspirated_count = 0
        
        for consonant in consonants:
            if consonant in self.CONSONANT_PROPERTIES:
                props = self.CONSONANT_PROPERTIES[consonant]
                if 'vot' in props:
                    vot_values.append(props['vot'])
                    if props['vot'] > 30:  # Aspirated threshold
                        aspirated_count += 1
        
        return {
            'mean': float(np.mean(vot_values)) if vot_values else 0,
            'variance': float(np.var(vot_values)) if vot_values else 0,
            'aspirated_stops': aspirated_count
        }
    
    def _analyze_prosody(self, name: str, phonemes: List[str]) -> Dict:
        """Analyze prosodic features."""
        # Syllable count (approximation)
        vowel_groups = self._get_vowel_groups(phonemes)
        syllable_count = len(vowel_groups)
        
        # Stress pattern (simple heuristic: first syllable stressed in English)
        stress_pattern = 'initial' if syllable_count > 1 else 'monosyllabic'
        
        # Syllable duration (uniform for simplicity)
        syllable_duration_mean = 1.0 / syllable_count if syllable_count > 0 else 1.0
        
        # Pitch contour (based on phoneme sequence)
        pitch_contour = 'falling' if self._has_falling_pattern(phonemes) else 'flat'
        
        return {
            'stress_pattern': stress_pattern,
            'syllable_duration_mean': float(syllable_duration_mean),
            'syllable_duration_variance': 0.1,
            'pitch_contour': pitch_contour
        }
    
    def _analyze_harshness(self, consonants: List[str]) -> Dict:
        """Analyze acoustic harshness vs softness."""
        harshness_scores = []
        
        sibilant_count = 0
        plosive_count = 0
        fricative_count = 0
        sonorant_count = 0
        
        for consonant in consonants:
            if consonant in self.CONSONANT_PROPERTIES:
                props = self.CONSONANT_PROPERTIES[consonant]
                harshness_scores.append(props.get('harshness', 0.5))
                
                if consonant in ['s', 'z', 'sh', 'zh']:
                    sibilant_count += 1
                if props.get('type') == 'stop':
                    plosive_count += 1
                if props.get('type') == 'fricative':
                    fricative_count += 1
                if props.get('type') in ['nasal', 'liquid', 'glide']:
                    sonorant_count += 1
        
        total_cons = len(consonants) if consonants else 1
        
        return {
            'overall_score': float(np.mean(harshness_scores)) if harshness_scores else 0.5,
            'sibilance': float(sibilant_count / total_cons),
            'plosive_density': float(plosive_count / total_cons),
            'fricative_density': float(fricative_count / total_cons),
            'sonorant_density': float(sonorant_count / total_cons)
        }
    
    def _calculate_melodiousness(self, phonemes: List[str]) -> float:
        """Calculate overall melodiousness score (0-1)."""
        if not phonemes:
            return 0.5
        
        # Factors that increase melodiousness:
        # - More vowels
        # - More sonorants
        # - Fewer harsh consonants
        # - Alternating V-C pattern
        
        vowel_ratio = sum(1 for p in phonemes if self._is_vowel(p)) / len(phonemes)
        sonorant_ratio = sum(1 for p in phonemes if self._is_sonorant(p)) / len(phonemes)
        alternation_score = self._calculate_alternation_score(phonemes)
        
        melodiousness = (vowel_ratio * 0.4 + sonorant_ratio * 0.3 + alternation_score * 0.3)
        
        return float(min(melodiousness, 1.0))
    
    def _calculate_rhythmic_regularity(self, phonemes: List[str]) -> float:
        """Calculate rhythmic regularity (0-1)."""
        # Check for regular CV (consonant-vowel) alternation
        if len(phonemes) < 2:
            return 0.5
        
        alternations = 0
        for i in range(len(phonemes) - 1):
            is_vowel_curr = self._is_vowel(phonemes[i])
            is_vowel_next = self._is_vowel(phonemes[i + 1])
            if is_vowel_curr != is_vowel_next:
                alternations += 1
        
        max_alternations = len(phonemes) - 1
        regularity = alternations / max_alternations if max_alternations > 0 else 0
        
        return float(regularity)
    
    def _calculate_phonetic_complexity(self, phonemes: List[str]) -> float:
        """Calculate phonetic complexity (0-1)."""
        if not phonemes:
            return 0
        
        # Complexity factors:
        # - Consonant clusters
        # - Rare phonemes
        # - Long sequences
        
        cluster_count = self._count_clusters(phonemes)
        unique_phonemes = len(set(phonemes))
        
        complexity = min((cluster_count * 0.2 + unique_phonemes * 0.05), 1.0)
        
        return float(complexity)
    
    def _analyze_clusters(self, name: str) -> Dict:
        """Analyze consonant clusters."""
        phonemes = self._name_to_phonemes(name)
        
        has_initial = False
        has_final = False
        max_cluster = 0
        
        # Check initial cluster
        i = 0
        initial_cons_count = 0
        while i < len(phonemes) and not self._is_vowel(phonemes[i]):
            initial_cons_count += 1
            i += 1
        
        if initial_cons_count >= 2:
            has_initial = True
            max_cluster = max(max_cluster, initial_cons_count)
        
        # Check final cluster
        i = len(phonemes) - 1
        final_cons_count = 0
        while i >= 0 and not self._is_vowel(phonemes[i]):
            final_cons_count += 1
            i -= 1
        
        if final_cons_count >= 2:
            has_final = True
            max_cluster = max(max_cluster, final_cons_count)
        
        complexity = min(max_cluster / 3.0, 1.0)
        
        return {
            'initial': has_initial,
            'final': has_final,
            'max_size': max_cluster,
            'complexity': float(complexity)
        }
    
    def _analyze_vowel_patterns(self, vowels: List[str]) -> Dict:
        """Analyze vowel sequence patterns."""
        if not vowels:
            return {
                'sequence_pattern': 'none',
                'diphthong_count': 0,
                'harmony': 0.0
            }
        
        # Detect diphthongs (two vowels together)
        diphthong_count = 0
        for i in range(len(vowels) - 1):
            if self._is_diphthong(vowels[i], vowels[i+1]):
                diphthong_count += 1
        
        # Vowel harmony (similarity of vowels)
        harmony = self._calculate_vowel_harmony(vowels)
        
        return {
            'sequence_pattern': self._describe_vowel_pattern(vowels),
            'diphthong_count': diphthong_count,
            'harmony': float(harmony)
        }
    
    def _analyze_pronounceability(self, name: str, phonemes: List[str]) -> Dict:
        """Analyze cross-linguistic pronounceability."""
        # Simplified pronounceability scoring
        # Based on phonotactic constraints of different languages
        
        cluster_complexity = self._analyze_clusters(name)['complexity']
        unique_phonemes = len(set(phonemes))
        
        # English: allows complex clusters
        english_ease = 1.0 - (cluster_complexity * 0.3)
        
        # Spanish: prefers simpler clusters
        spanish_ease = 1.0 - (cluster_complexity * 0.5)
        
        # Mandarin: minimal clusters
        mandarin_ease = 1.0 - (cluster_complexity * 0.8)
        
        # Arabic: moderate clusters
        arabic_ease = 1.0 - (cluster_complexity * 0.4)
        
        # Hindi: moderate complexity
        hindi_ease = 1.0 - (cluster_complexity * 0.4)
        
        universal = np.mean([english_ease, spanish_ease, mandarin_ease, arabic_ease, hindi_ease])
        
        return {
            'english': float(max(english_ease, 0)),
            'spanish': float(max(spanish_ease, 0)),
            'mandarin': float(max(mandarin_ease, 0)),
            'arabic': float(max(arabic_ease, 0)),
            'hindi': float(max(hindi_ease, 0)),
            'universal': float(universal)
        }
    
    # Helper methods
    
    def _is_vowel(self, phoneme: str) -> bool:
        """Check if phoneme is a vowel."""
        return any(v in phoneme.lower() for v in 'aeiou')
    
    def _is_sonorant(self, phoneme: str) -> bool:
        """Check if phoneme is a sonorant (nasal, liquid, glide)."""
        return phoneme in ['m', 'n', 'l', 'r', 'w', 'y']
    
    def _get_vowel_groups(self, phonemes: List[str]) -> List[List[str]]:
        """Group vowels into syllable nuclei."""
        groups = []
        current_group = []
        
        for p in phonemes:
            if self._is_vowel(p):
                current_group.append(p)
            else:
                if current_group:
                    groups.append(current_group)
                    current_group = []
        
        if current_group:
            groups.append(current_group)
        
        return groups
    
    def _has_falling_pattern(self, phonemes: List[str]) -> bool:
        """Check if phoneme sequence has falling pitch pattern."""
        # Simplified: if ends with sonorant or vowel, likely falling
        if phonemes:
            last = phonemes[-1]
            return self._is_vowel(last) or self._is_sonorant(last)
        return False
    
    def _calculate_alternation_score(self, phonemes: List[str]) -> float:
        """Calculate V-C alternation score."""
        if len(phonemes) < 2:
            return 0.5
        
        alternations = 0
        for i in range(len(phonemes) - 1):
            if self._is_vowel(phonemes[i]) != self._is_vowel(phonemes[i+1]):
                alternations += 1
        
        return alternations / (len(phonemes) - 1)
    
    def _count_clusters(self, phonemes: List[str]) -> int:
        """Count consonant clusters."""
        cluster_count = 0
        in_cluster = False
        cluster_size = 0
        
        for p in phonemes:
            if not self._is_vowel(p):
                cluster_size += 1
                if cluster_size >= 2:
                    in_cluster = True
            else:
                if in_cluster:
                    cluster_count += 1
                in_cluster = False
                cluster_size = 0
        
        if in_cluster:
            cluster_count += 1
        
        return cluster_count
    
    def _is_diphthong(self, v1: str, v2: str) -> bool:
        """Check if two vowels form a diphthong."""
        # Common diphthongs
        diphthongs = [('a', 'i'), ('a', 'u'), ('e', 'i'), ('o', 'i'), ('o', 'u')]
        pair = (v1[0] if v1 else '', v2[0] if v2 else '')
        return pair in diphthongs
    
    def _calculate_vowel_harmony(self, vowels: List[str]) -> float:
        """Calculate vowel harmony (similarity)."""
        if len(vowels) < 2:
            return 1.0
        
        # Count unique vowels
        unique = len(set(v[0] if v else '' for v in vowels))
        
        # More unique = less harmony
        harmony = 1.0 - (unique / 5.0)  # 5 basic vowels
        
        return max(harmony, 0.0)
    
    def _describe_vowel_pattern(self, vowels: List[str]) -> str:
        """Describe vowel sequence pattern."""
        if not vowels:
            return 'none'
        if len(vowels) == 1:
            return 'single'
        if len(set(vowels)) == 1:
            return 'repeated'
        return 'varied'


# Create singleton
acoustic_analyzer = AcousticAnalyzer()

