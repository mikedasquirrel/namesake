"""
Phonetic Composite Scores - Standardized Derived Measurements

This module provides higher-level composite scores built from PhoneticBase primitives.
These composites are standardized across all domains but can be weighted differently.

Composites include:
- Harshness (aggressive, forceful sound)
- Smoothness (melodious, flowing sound)
- Memorability (ease of recall)
- Power/Authority (commanding presence)
- Euphony (aesthetic beauty)
"""

import re
import logging
from typing import Dict, Optional
from analyzers.phonetic_base import PhoneticBase, get_analyzer
import Levenshtein

logger = logging.getLogger(__name__)


class PhoneticComposites:
    """
    Standardized composite scores derived from phonetic primitives.
    
    All composites are normalized to 0-100 scale.
    Formulas are research-informed and validated across multiple domains.
    """
    
    def __init__(self, phonetic_base: Optional[PhoneticBase] = None):
        """
        Initialize with optional custom PhoneticBase analyzer.
        
        Args:
            phonetic_base: Optional PhoneticBase instance (creates new if None)
        """
        self.phonetic_base = phonetic_base or get_analyzer()
    
    def analyze(self, name: str, all_names: Optional[list] = None) -> Dict:
        """
        Complete composite analysis of a name.
        
        Args:
            name: The name to analyze
            all_names: Optional list of all names for uniqueness calculation
            
        Returns:
            Dictionary with all composite scores (0-100 scale)
        """
        # Get base phonetic analysis
        base = self.phonetic_base.analyze(name)
        
        # Calculate composites
        harshness = self.calculate_harshness(base, name)
        smoothness = self.calculate_smoothness(base, name)
        memorability = self.calculate_memorability(base, name, all_names)
        power_authority = self.calculate_power_authority(base, name)
        euphony = self.calculate_euphony(base)
        pronounceability = self.calculate_pronounceability(base, name)
        
        # Additional useful composites
        aggressive_profile = self.calculate_aggressive_profile(base, name)
        gentle_profile = self.calculate_gentle_profile(base, name)
        
        return {
            # === Primary Composites ===
            'harshness_score': round(harshness, 2),
            'smoothness_score': round(smoothness, 2),
            'memorability_score': round(memorability, 2),
            'power_authority_score': round(power_authority, 2),
            'euphony_score': round(euphony, 2),
            'pronounceability_score': round(pronounceability, 2),
            
            # === Phonetic Profiles ===
            'aggressive_phonetic_profile': round(aggressive_profile, 2),
            'gentle_phonetic_profile': round(gentle_profile, 2),
            
            # === Derived Insights ===
            'harshness_smoothness_balance': round(harshness - smoothness, 2),
            'memorability_pronounceability_balance': round(memorability - pronounceability, 2),
            
            # Include base measurements for reference
            **base
        }
    
    def calculate_harshness(self, base: Dict, name: str) -> float:
        """
        Calculate phonetic harshness (0-100).
        
        Formula: 0.5×plosives + 0.3×fricatives + 0.2×voicing - 0.2×vowel_smoothness
        
        High harshness = aggressive, forceful, attention-grabbing
        Used in: hurricanes (threat perception), bands (genre matching), MTG (damage spells)
        """
        name_lower = name.lower()
        
        # Core components
        plosive_component = base['plosive_score'] * 0.5
        fricative_component = base['fricative_score'] * 0.3
        
        # Voicing (voiced consonants sound harsher/darker)
        voicing_component = (base['voicing_ratio'] - 50) / 50 * 20  # Center at 50, scale to ±20
        
        # Vowel smoothness (more open vowels soften the harshness)
        vowel_smoothness = (base['vowel_openness'] / 100) * base['vowel_ratio'] * 100
        vowel_penalty = vowel_smoothness * 0.2
        
        # Positional bonuses (initial/final harsh sounds amplify perception)
        position_bonus = 0
        if base['initial_is_plosive']:
            position_bonus += 10
        if name_lower and name_lower[-1] in 'kgtdx':
            position_bonus += 5
        
        # Sibilance adds edge
        sibilant_bonus = base['sibilant_score'] * 0.15
        
        score = (plosive_component + fricative_component + voicing_component + 
                 position_bonus + sibilant_bonus - vowel_penalty)
        
        return max(0.0, min(100.0, score))
    
    def calculate_smoothness(self, base: Dict, name: str) -> float:
        """
        Calculate phonetic smoothness (0-100).
        
        Formula: 0.4×liquids + 0.4×nasals + 0.2×vowel_openness
        
        High smoothness = melodious, flowing, accessible
        Used in: bands (folk/pop), mental health (clinical accessibility), MTG (healing spells)
        """
        name_lower = name.lower()
        
        # Core flow components
        liquid_component = base['liquid_score'] * 0.4
        nasal_component = base['nasal_score'] * 0.4
        
        # Vowel quality (open, flowing vowels)
        vowel_component = base['vowel_openness'] * 0.2
        
        # Glides add smoothness
        glide_bonus = base['glide_score'] * 0.15
        
        # Positional features (soft endings)
        position_bonus = 0
        if base['final_is_liquid'] or base['final_is_nasal']:
            position_bonus += 10
        if name_lower and name_lower[-1] in 'aeiou':
            position_bonus += 8
        
        # Cluster complexity penalty (hard to pronounce = less smooth)
        cluster_penalty = base['cluster_complexity'] * 0.15
        
        score = (liquid_component + nasal_component + vowel_component + 
                 glide_bonus + position_bonus - cluster_penalty)
        
        return max(0.0, min(100.0, score))
    
    def calculate_memorability(self, base: Dict, name: str, all_names: Optional[list] = None) -> float:
        """
        Calculate memorability score (0-100).
        
        Formula: f(syllables, length, pronounceability, uniqueness)
        
        High memorability = easy to recall, distinctive
        Used in: ALL DOMAINS (but sign varies: positive in MTG/bands, negative in crypto)
        """
        syllables = base['syllable_count']
        length = base['character_length']
        
        # Optimal length: 4-8 characters
        if 4 <= length <= 8:
            length_score = 40
        elif 3 <= length <= 10:
            length_score = 25
        else:
            length_score = max(0, 40 - abs(length - 6) * 5)
        
        # Optimal syllables: 1-2 (working memory limit)
        if syllables <= 2:
            syllable_score = 35
        elif syllables == 3:
            syllable_score = 25
        else:
            syllable_score = max(0, 35 - (syllables - 2) * 8)
        
        # Phonetic quality contribution (easier to process = more memorable)
        phonetic_component = (base['phonotactic_score'] / 100) * 15
        
        # Initial plosive = attention-grabbing
        initial_bonus = 10 if base['initial_is_plosive'] else 0
        
        # Uniqueness (if available)
        uniqueness_bonus = 0
        if all_names:
            uniqueness = self._calculate_uniqueness(name, all_names)
            uniqueness_bonus = (uniqueness / 100) * 10
        
        score = length_score + syllable_score + phonetic_component + initial_bonus + uniqueness_bonus
        
        return max(0.0, min(100.0, score))
    
    def calculate_power_authority(self, base: Dict, name: str) -> float:
        """
        Calculate power/authority connotation (0-100).
        
        Formula: 0.35×harshness + 0.25×plosive_concentration + 0.2×low_vowels + 0.2×length
        
        High power = commanding, authoritative, dominant
        Used in: ships (historical significance), bands (metal), NBA (power positions)
        """
        # Use harshness as foundation
        harshness = self.calculate_harshness(base, name)
        harshness_component = harshness * 0.35
        
        # Plosive concentration (explosive power)
        plosive_component = base['plosive_score'] * 0.25
        
        # Low/back vowels (deeper, more powerful sound)
        back_vowel_component = (100 - base['vowel_frontness']) * 0.2
        
        # Length (longer names can sound more authoritative)
        length = base['character_length']
        if 6 <= length <= 10:
            length_component = 20
        elif length > 10:
            length_component = 25
        else:
            length_component = length * 2
        
        # Phonological weight (substantial presence)
        weight_component = base['phonological_weight'] * 0.1
        
        score = (harshness_component + plosive_component + back_vowel_component + 
                 length_component + weight_component)
        
        return max(0.0, min(100.0, score))
    
    def calculate_euphony(self, base: Dict) -> float:
        """
        Calculate euphony/beauty score (0-100).
        
        Formula: 0.4×vowel_ratio + 0.3×liquid_ratio - 0.3×cluster_complexity
        
        High euphony = aesthetically pleasing, harmonious
        Used in: bands (pop/indie), crypto (brand appeal), mental health (positive valence)
        """
        # Vowel richness (ideal ~40-50%)
        vowel_ratio = base['vowel_ratio']
        vowel_component = 100 * (1 - abs(0.45 - vowel_ratio) * 2)
        vowel_component = max(0, vowel_component) * 0.4
        
        # Liquid sounds (flowing beauty)
        liquid_ratio = base['liquid_count'] / max(base['consonant_count'], 1)
        liquid_component = liquid_ratio * 100 * 0.3
        
        # Cluster penalty (awkward = not beautiful)
        cluster_penalty = base['cluster_complexity'] * 0.3
        
        # Phonotactic bonus (natural combinations)
        natural_bonus = base['phonotactic_score'] * 0.2
        
        score = vowel_component + liquid_component + natural_bonus - cluster_penalty
        
        return max(0.0, min(100.0, score))
    
    def calculate_pronounceability(self, base: Dict, name: str) -> float:
        """
        Calculate pronounceability (0-100).
        
        High pronounceability = easy to say, natural sound patterns
        Used in: mental health (adherence), crypto (adoption), bands (radio play)
        """
        name_lower = name.lower()
        name_alpha = re.sub(r'[^a-z]', '', name_lower)
        
        if not name_alpha:
            return 0.0
        
        # Vowel spacing (regular distribution is easier)
        vowel_positions = [i for i, c in enumerate(name_alpha) if c in 'aeiou']
        
        if len(vowel_positions) < 2:
            spacing_score = 20
        else:
            gaps = [vowel_positions[i+1] - vowel_positions[i] for i in range(len(vowel_positions)-1)]
            avg_gap = sum(gaps) / len(gaps)
            # Ideal gap: 1-2 characters between vowels
            spacing_score = 40 * (1 / (1 + abs(avg_gap - 1.5)))
        
        # Cluster penalty
        cluster_penalty = base['cluster_complexity'] * 0.5
        
        # Length factor
        length = base['character_length']
        length_score = 30 if 3 <= length <= 8 else max(0, 30 - abs(length - 5.5) * 3)
        
        # Phonotactic naturalness
        natural_component = base['phonotactic_score'] * 0.3
        
        # Initial vowel bonus (easier to start)
        initial_vowel_bonus = 10 if name_alpha and name_alpha[0] in 'aeiou' else 0
        
        score = spacing_score + length_score + natural_component + initial_vowel_bonus - cluster_penalty
        
        return max(0.0, min(100.0, score))
    
    def calculate_aggressive_profile(self, base: Dict, name: str) -> float:
        """
        Calculate overall aggressive phonetic profile (0-100).
        Composite of harshness, plosives, and voicing.
        """
        harshness = self.calculate_harshness(base, name)
        sibilance = base['sibilant_score']
        voicing = base['voicing_ratio']
        
        # Aggressive = harsh + sibilant + voiced
        return (harshness * 0.5 + sibilance * 0.3 + voicing * 0.2)
    
    def calculate_gentle_profile(self, base: Dict, name: str) -> float:
        """
        Calculate overall gentle phonetic profile (0-100).
        Composite of smoothness, liquids/nasals, and euphony.
        """
        smoothness = self.calculate_smoothness(base, name)
        euphony = self.calculate_euphony(base)
        voicing_softness = 100 - abs(base['voicing_ratio'] - 50)  # Balance is gentle
        
        return (smoothness * 0.4 + euphony * 0.3 + voicing_softness * 0.3)
    
    def _calculate_uniqueness(self, name: str, all_names: list) -> float:
        """
        Calculate uniqueness via Levenshtein distance (0-100).
        Higher = more unique/distinctive.
        """
        if not all_names or len(all_names) < 2:
            return 100.0
        
        distances = []
        name_lower = name.lower()
        
        for other_name in all_names:
            if other_name.lower() == name_lower:
                continue
            
            distance = Levenshtein.distance(name_lower, other_name.lower())
            distances.append(distance)
        
        if not distances:
            return 100.0
        
        avg_distance = sum(distances) / len(distances)
        # Normalize: typical max distance is ~10-15 for names
        uniqueness = min(100.0, (avg_distance / 10) * 100)
        
        return uniqueness
    
    def get_phonetic_summary(self, name: str) -> str:
        """
        Generate human-readable phonetic summary.
        
        Returns a text description of the name's phonetic character.
        """
        analysis = self.analyze(name)
        
        # Determine dominant characteristics
        characteristics = []
        
        if analysis['harshness_score'] > 70:
            characteristics.append("harsh/aggressive")
        elif analysis['harshness_score'] > 50:
            characteristics.append("moderately harsh")
        
        if analysis['smoothness_score'] > 70:
            characteristics.append("smooth/flowing")
        
        if analysis['memorability_score'] > 75:
            characteristics.append("highly memorable")
        elif analysis['memorability_score'] < 40:
            characteristics.append("difficult to remember")
        
        if analysis['euphony_score'] > 70:
            characteristics.append("euphonious/beautiful")
        
        if analysis['pronounceability_score'] < 40:
            characteristics.append("difficult to pronounce")
        
        if not characteristics:
            characteristics.append("phonetically neutral")
        
        summary = f"'{name}' is {', '.join(characteristics)}."
        
        # Add syllable/length context
        summary += f" It has {analysis['syllable_count']} syllable(s) and {analysis['character_length']} characters."
        
        return summary


# Module-level convenience functions
_composite_analyzer = None

def get_composite_analyzer() -> PhoneticComposites:
    """Get singleton PhoneticComposites instance."""
    global _composite_analyzer
    if _composite_analyzer is None:
        _composite_analyzer = PhoneticComposites()
    return _composite_analyzer


def analyze_composites(name: str, all_names: Optional[list] = None) -> Dict:
    """Convenience function for quick composite analysis."""
    return get_composite_analyzer().analyze(name, all_names)


def get_phonetic_summary(name: str) -> str:
    """Convenience function for phonetic summary."""
    return get_composite_analyzer().get_phonetic_summary(name)

