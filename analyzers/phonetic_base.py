"""
PhoneticBase - Unified Phonetic Analysis Foundation

This module provides standardized phonetic measurements across all research domains.
The same measurements are used everywhere, but weighted differently per domain.

Key Innovation: Consistency in measurement, flexibility in interpretation.
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
import pyphen

logger = logging.getLogger(__name__)


class PhoneticBase:
    """
    Unified phonetic analysis providing standardized measurements.
    
    All phonetic scores are normalized to 0-100 scale for consistency.
    Domain-specific analyzers use these base measurements with custom weights.
    """
    
    def __init__(self):
        # Initialize syllable counter
        self.pyphen_dic = pyphen.Pyphen(lang='en_US')
        
        # Phoneme classifications (IPA-informed, orthographic approximations)
        self.plosives = set('ptkbdg')  # Stop consonants (explosive release)
        self.fricatives = set('fvszxh')  # Continuous friction
        self.sibilants = set('sz')  # Subset of fricatives (hissing)
        self.liquids = set('lr')  # Flow continuants
        self.nasals = set('mn')  # Nasal resonance
        self.glides = set('wy')  # Semivowels
        
        # Voicing classification
        self.voiced_consonants = set('bdgvzjmnlrwy')
        self.voiceless_consonants = set('ptkfshθ')
        
        # Vowel classifications
        self.front_vowels = set('ie')  # Bright, high energy
        self.back_vowels = set('ou')  # Dark, low energy
        self.open_vowels = set('a')  # Maximum aperture
        self.close_vowels = set('iu')  # Minimum aperture
        self.all_vowels = set('aeiou')
        
        # Digraphs and special combinations
        self.digraphs = {
            'sh': 'fricative_sibilant',
            'ch': 'affricate',
            'th': 'fricative',
            'ph': 'fricative',
            'gh': 'fricative',
            'ng': 'nasal',
        }
        
        # Rare/unusual combinations (phonotactic rarity)
        self.rare_clusters = [
            'xh', 'kh', 'zh', 'qx', 'zz', 'kk', 'qq',
            'tl', 'vl', 'vr', 'pn', 'pt', 'tk', 'nm'
        ]
    
    def analyze(self, name: str) -> Dict:
        """
        Complete phonetic analysis of a name.
        
        Args:
            name: The name to analyze
            
        Returns:
            Dictionary with all standardized phonetic measurements (0-100 scale)
        """
        if not name or not isinstance(name, str):
            return self._empty_analysis()
        
        name_clean = name.strip()
        name_lower = name_clean.lower()
        
        # Remove non-alphabetic characters for phonetic analysis
        name_alpha = re.sub(r'[^a-zA-Z]', '', name_lower)
        
        if not name_alpha:
            return self._empty_analysis()
        
        # Extract basic components
        consonants, vowels = self._extract_phonemes(name_alpha)
        syllable_count = self._count_syllables(name_clean)
        
        # === PRIMITIVE MEASUREMENTS (Level 1) ===
        
        # Consonant type concentrations
        plosive_score = self._calculate_plosive_score(name_alpha, consonants)
        fricative_score = self._calculate_fricative_score(name_alpha, consonants)
        sibilant_score = self._calculate_sibilant_score(name_alpha, consonants)
        liquid_score = self._calculate_liquid_score(consonants)
        nasal_score = self._calculate_nasal_score(consonants)
        glide_score = self._calculate_glide_score(name_alpha)
        
        # Voicing analysis
        voicing_ratio = self._calculate_voicing_ratio(consonants)
        
        # Vowel quality analysis
        vowel_frontness = self._calculate_vowel_frontness(vowels)
        vowel_openness = self._calculate_vowel_openness(vowels)
        vowel_complexity = self._calculate_vowel_complexity(vowels)
        
        # Cluster complexity
        cluster_complexity = self._calculate_cluster_complexity(name_alpha)
        max_cluster_length = self._calculate_max_cluster_length(name_alpha)
        
        # Phonotactic probability (naturalness)
        phonotactic_score = self._calculate_phonotactic_score(name_alpha)
        
        # Stress patterns (simplified)
        stress_pattern = self._detect_stress_pattern(name_clean, syllable_count)
        
        # Positional features (initial/final sound importance)
        initial_features = self._analyze_initial_sound(name_alpha)
        final_features = self._analyze_final_sound(name_alpha)
        
        # Phonological weight
        phonological_weight = self._calculate_phonological_weight(
            syllable_count, len(name_alpha), cluster_complexity
        )
        
        return {
            # === Core Consonant Scores ===
            'plosive_score': round(plosive_score, 2),
            'fricative_score': round(fricative_score, 2),
            'sibilant_score': round(sibilant_score, 2),
            'liquid_score': round(liquid_score, 2),
            'nasal_score': round(nasal_score, 2),
            'glide_score': round(glide_score, 2),
            
            # === Voicing ===
            'voicing_ratio': round(voicing_ratio, 2),
            'voiced_consonant_ratio': round(voicing_ratio, 2),  # Alias for compatibility
            
            # === Vowel Quality ===
            'vowel_frontness': round(vowel_frontness, 2),
            'vowel_openness': round(vowel_openness, 2),
            'vowel_complexity': round(vowel_complexity, 2),
            'vowel_count': len(vowels),
            'vowel_ratio': round(len(vowels) / len(name_alpha), 3) if name_alpha else 0,
            
            # === Complexity Metrics ===
            'cluster_complexity': round(cluster_complexity, 2),
            'max_cluster_length': max_cluster_length,
            'phonotactic_score': round(phonotactic_score, 2),
            'phonological_weight': round(phonological_weight, 2),
            
            # === Positional Features ===
            'initial_is_plosive': initial_features['is_plosive'],
            'initial_is_fricative': initial_features['is_fricative'],
            'initial_is_voiced': initial_features['is_voiced'],
            'initial_sound': initial_features['sound'],
            'final_is_liquid': final_features['is_liquid'],
            'final_is_nasal': final_features['is_nasal'],
            'final_sound': final_features['sound'],
            
            # === Structural ===
            'syllable_count': syllable_count,
            'character_length': len(name_alpha),
            'stress_pattern': stress_pattern,
            
            # === Raw counts (for transparency) ===
            'consonant_count': len(consonants),
            'plosive_count': sum(1 for c in consonants if c in self.plosives),
            'fricative_count': sum(1 for c in consonants if c in self.fricatives),
            'liquid_count': sum(1 for c in consonants if c in self.liquids),
            'nasal_count': sum(1 for c in consonants if c in self.nasals),
        }
    
    def _extract_phonemes(self, name: str) -> Tuple[List[str], List[str]]:
        """Extract consonants and vowels from name."""
        consonants = [c for c in name if c not in self.all_vowels]
        vowels = [v for v in name if v in self.all_vowels]
        return consonants, vowels
    
    def _count_syllables(self, name: str) -> int:
        """Count syllables using pyphen with fallback."""
        clean_name = re.sub(r'[^a-zA-Z]', '', name)
        if not clean_name:
            return 1
        
        try:
            hyphenated = self.pyphen_dic.inserted(clean_name.lower())
            syllables = len(hyphenated.split('-'))
            
            # Fallback if pyphen fails
            if syllables == 0:
                syllables = max(1, len(re.findall(r'[aeiou]+', clean_name.lower())))
            
            return syllables
        except:
            # Emergency fallback: count vowel groups
            return max(1, len(re.findall(r'[aeiou]+', clean_name.lower())))
    
    def _calculate_plosive_score(self, name: str, consonants: List[str]) -> float:
        """
        Calculate plosive concentration (0-100).
        Plosives: p, t, k, b, d, g (explosive stops)
        """
        if not consonants:
            return 0.0
        
        plosive_count = sum(1 for c in consonants if c in self.plosives)
        base_score = (plosive_count / len(consonants)) * 100
        
        # Positional weighting: initial plosives are more salient
        if name and name[0] in self.plosives:
            base_score += 15
        
        # Final plosives (abrupt endings)
        if name and name[-1] in self.plosives:
            base_score += 10
        
        return min(100.0, base_score)
    
    def _calculate_fricative_score(self, name: str, consonants: List[str]) -> float:
        """
        Calculate fricative concentration (0-100).
        Fricatives: f, v, s, z, x, h (continuous friction)
        """
        if not consonants:
            return 0.0
        
        fricative_count = sum(1 for c in consonants if c in self.fricatives)
        
        # Add digraph fricatives
        fricative_count += name.count('sh') + name.count('th') + name.count('ph')
        
        base_score = (fricative_count / len(consonants)) * 100
        
        # Initial fricatives (attention-grabbing)
        if name and name[0] in self.fricatives:
            base_score += 10
        
        return min(100.0, base_score)
    
    def _calculate_sibilant_score(self, name: str, consonants: List[str]) -> float:
        """
        Calculate sibilant concentration (0-100).
        Sibilants: s, z (hissing sounds)
        """
        if not consonants:
            return 0.0
        
        sibilant_count = sum(1 for c in consonants if c in self.sibilants)
        sibilant_count += name.count('sh') + name.count('zh')
        
        base_score = (sibilant_count / len(consonants)) * 100
        
        # Initial 's' is particularly prominent
        if name.startswith('s'):
            base_score += 20
        
        return min(100.0, base_score)
    
    def _calculate_liquid_score(self, consonants: List[str]) -> float:
        """
        Calculate liquid concentration (0-100).
        Liquids: l, r (flowing continuants)
        """
        if not consonants:
            return 0.0
        
        liquid_count = sum(1 for c in consonants if c in self.liquids)
        return (liquid_count / len(consonants)) * 100
    
    def _calculate_nasal_score(self, consonants: List[str]) -> float:
        """
        Calculate nasal concentration (0-100).
        Nasals: m, n (+ ng digraph)
        """
        if not consonants:
            return 0.0
        
        nasal_count = sum(1 for c in consonants if c in self.nasals)
        return (nasal_count / len(consonants)) * 100
    
    def _calculate_glide_score(self, name: str) -> float:
        """
        Calculate glide/semivowel presence (0-100).
        Glides: w, y (smooth transitions)
        """
        glide_count = sum(1 for c in name if c in self.glides)
        # Normalize by name length (glides are relatively rare)
        return min(100.0, (glide_count / max(len(name), 1)) * 200)
    
    def _calculate_voicing_ratio(self, consonants: List[str]) -> float:
        """
        Calculate ratio of voiced consonants (0-100).
        100 = all voiced, 0 = all voiceless, 50 = balanced
        """
        if not consonants:
            return 50.0
        
        voiced_count = sum(1 for c in consonants if c in self.voiced_consonants)
        return (voiced_count / len(consonants)) * 100
    
    def _calculate_vowel_frontness(self, vowels: List[str]) -> float:
        """
        Calculate vowel frontness (0-100).
        100 = front vowels (i, e - bright), 0 = back vowels (u, o - dark)
        """
        if not vowels:
            return 50.0
        
        front_count = sum(1 for v in vowels if v in self.front_vowels)
        back_count = sum(1 for v in vowels if v in self.back_vowels)
        
        if front_count + back_count == 0:
            return 50.0  # Neutral (only 'a')
        
        return (front_count / (front_count + back_count)) * 100
    
    def _calculate_vowel_openness(self, vowels: List[str]) -> float:
        """
        Calculate vowel openness (0-100).
        100 = open vowels (a), 0 = close vowels (i, u)
        """
        if not vowels:
            return 50.0
        
        openness_map = {'a': 100, 'o': 70, 'e': 50, 'i': 20, 'u': 20}
        total_openness = sum(openness_map.get(v, 50) for v in vowels)
        
        return total_openness / len(vowels)
    
    def _calculate_vowel_complexity(self, vowels: List[str]) -> float:
        """
        Calculate vowel diversity/complexity (0-100).
        More unique vowels = higher complexity
        """
        if not vowels:
            return 0.0
        
        unique_vowels = len(set(vowels))
        return (unique_vowels / 5) * 100  # 5 possible vowels
    
    def _calculate_cluster_complexity(self, name: str) -> float:
        """
        Calculate consonant cluster complexity (0-100).
        Based on number and length of consonant clusters.
        """
        clusters = re.findall(r'[bcdfghjklmnpqrstvwxyz]{2,}', name)
        
        if not clusters:
            return 0.0
        
        # Weight by cluster length (longer = more complex)
        complexity = sum((len(c) - 1) * 25 for c in clusters)
        
        # Bonus for rare clusters
        for rare in self.rare_clusters:
            if rare in name:
                complexity += 15
        
        return min(100.0, complexity)
    
    def _calculate_max_cluster_length(self, name: str) -> int:
        """Find longest consonant cluster."""
        clusters = re.findall(r'[bcdfghjklmnpqrstvwxyz]{2,}', name)
        return max([len(c) for c in clusters]) if clusters else 0
    
    def _calculate_phonotactic_score(self, name: str) -> float:
        """
        Calculate phonotactic probability (0-100).
        High score = natural, common combinations
        Low score = unusual, rare combinations
        """
        score = 100.0
        
        # Penalize rare clusters
        for rare in self.rare_clusters:
            if rare in name:
                score -= 20
        
        # Penalize unusual initial clusters
        if len(name) >= 2:
            initial_cluster = name[:2]
            if initial_cluster in ['kh', 'zh', 'xh', 'vl', 'vr', 'tl', 'pn']:
                score -= 15
        
        # Penalize repeated consonants (except common ones like 'll', 'ss')
        repeated = re.findall(r'([bcdfghjkmpqtvwxz])\1', name)
        score -= len(repeated) * 10
        
        # Apostrophes indicate constructed/borrowed words
        score -= name.count("'") * 15
        
        return max(0.0, score)
    
    def _detect_stress_pattern(self, name: str, syllable_count: int) -> str:
        """
        Detect likely stress pattern (simplified heuristic).
        
        Returns: 'monosyllabic', 'initial_stress', 'final_stress', or 'distributed'
        """
        if syllable_count == 1:
            return 'monosyllabic'
        elif syllable_count == 2:
            # English tends toward initial stress in 2-syllable words
            return 'initial_stress'
        elif syllable_count >= 3:
            # Longer words distribute stress
            return 'distributed'
        else:
            return 'unknown'
    
    def _analyze_initial_sound(self, name: str) -> Dict:
        """Analyze initial sound characteristics."""
        if not name:
            return {
                'sound': '',
                'is_plosive': False,
                'is_fricative': False,
                'is_voiced': False
            }
        
        initial = name[0]
        return {
            'sound': initial,
            'is_plosive': initial in self.plosives,
            'is_fricative': initial in self.fricatives,
            'is_voiced': initial in self.voiced_consonants
        }
    
    def _analyze_final_sound(self, name: str) -> Dict:
        """Analyze final sound characteristics."""
        if not name:
            return {
                'sound': '',
                'is_liquid': False,
                'is_nasal': False
            }
        
        final = name[-1]
        return {
            'sound': final,
            'is_liquid': final in self.liquids,
            'is_nasal': final in self.nasals
        }
    
    def _calculate_phonological_weight(self, syllables: int, length: int, 
                                      cluster_complexity: float) -> float:
        """
        Calculate overall phonological weight/complexity (0-100).
        Combines syllable count, length, and cluster complexity.
        """
        syllable_component = min(syllables * 15, 50)
        length_component = min(length * 2, 30)
        cluster_component = cluster_complexity * 0.2
        
        return min(100.0, syllable_component + length_component + cluster_component)
    
    def _empty_analysis(self) -> Dict:
        """Return empty analysis for invalid input."""
        return {
            'plosive_score': 0.0,
            'fricative_score': 0.0,
            'sibilant_score': 0.0,
            'liquid_score': 0.0,
            'nasal_score': 0.0,
            'glide_score': 0.0,
            'voicing_ratio': 50.0,
            'voiced_consonant_ratio': 50.0,
            'vowel_frontness': 50.0,
            'vowel_openness': 50.0,
            'vowel_complexity': 0.0,
            'vowel_count': 0,
            'vowel_ratio': 0.0,
            'cluster_complexity': 0.0,
            'max_cluster_length': 0,
            'phonotactic_score': 50.0,
            'phonological_weight': 0.0,
            'initial_is_plosive': False,
            'initial_is_fricative': False,
            'initial_is_voiced': False,
            'initial_sound': '',
            'final_is_liquid': False,
            'final_is_nasal': False,
            'final_sound': '',
            'syllable_count': 0,
            'character_length': 0,
            'stress_pattern': 'unknown',
            'consonant_count': 0,
            'plosive_count': 0,
            'fricative_count': 0,
            'liquid_count': 0,
            'nasal_count': 0,
        }


# Module-level convenience functions
_analyzer = None

def get_analyzer() -> PhoneticBase:
    """Get singleton PhoneticBase instance."""
    global _analyzer
    if _analyzer is None:
        _analyzer = PhoneticBase()
    return _analyzer


def analyze_name(name: str) -> Dict:
    """Convenience function for quick phonetic analysis."""
    return get_analyzer().analyze(name)

