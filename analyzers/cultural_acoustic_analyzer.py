"""
Culture-Specific Acoustic Analysis
===================================

Analyzes names in their CULTURAL CONTEXT - what sounds harsh/melodious/typical varies by culture.

Key Insight: "Beautiful" in English ≠ "Beautiful" in Arabic ≠ "Beautiful" in Japanese

Implementations:
- Language-family phonotactics (Semitic, Indo-European, Sino-Tibetan, etc.)
- Culture-specific aesthetic preferences
- Era-appropriate phonetic norms
- Social class markers in naming
"""

import logging
import numpy as np
from typing import Dict, Optional, List

from analyzers.acoustic_analyzer import acoustic_analyzer

logger = logging.getLogger(__name__)


class CulturalAcousticAnalyzer:
    """Analyze acoustic properties in cultural context."""
    
    # Culture-specific phonetic preferences
    CULTURAL_AESTHETICS = {
        '1st_century_judea': {
            'language_family': 'semitic',
            'preferred_sounds': ['l', 'n', 'm', 'a', 'i'],  # Soft sonorants
            'avoided_sounds': ['p', 'x', 'f'],  # Less common in Aramaic
            'typical_syllables': [2, 3],  # Most names 2-3 syllables
            'melodiousness_baseline': 0.55,  # What's "normal" melodiousness
            'harsh_tolerance': 0.6,  # Culture accepts moderate harshness
        },
        'ancient_greece': {
            'language_family': 'hellenic',
            'preferred_sounds': ['s', 'n', 'r', 'o', 'a'],
            'avoided_sounds': ['w', 'h'],
            'typical_syllables': [3, 4],  # Greek names often longer
            'melodiousness_baseline': 0.62,
            'harsh_tolerance': 0.5,
        },
        'roman_empire': {
            'language_family': 'italic',
            'preferred_sounds': ['s', 'r', 'i', 'u'],
            'avoided_sounds': ['th', 'kh'],
            'typical_syllables': [2, 3],
            'melodiousness_baseline': 0.58,
            'harsh_tolerance': 0.65,  # Romans liked powerful sounds
        },
        'medieval_europe': {
            'language_family': 'germanic_romance_mix',
            'preferred_sounds': ['r', 'l', 'n', 'a', 'e'],
            'avoided_sounds': [],
            'typical_syllables': [2, 3],
            'melodiousness_baseline': 0.60,
            'harsh_tolerance': 0.7,  # Warrior culture
        },
        'russian_19th_century': {
            'language_family': 'slavic',
            'preferred_sounds': ['l', 'v', 'a', 'i', 'y'],
            'avoided_sounds': ['h'],
            'typical_syllables': [3, 4],  # Russian names often longer
            'melodiousness_baseline': 0.57,
            'harsh_tolerance': 0.55,
        },
        'modern_anglo': {
            'language_family': 'germanic',
            'preferred_sounds': ['r', 'l', 'n', 'm'],
            'avoided_sounds': ['x', 'q'],
            'typical_syllables': [2, 3],
            'melodiousness_baseline': 0.63,  # Modern preference for melodious
            'harsh_tolerance': 0.45,  # Less tolerance for harsh
        },
    }
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("CulturalAcousticAnalyzer initialized")
    
    def analyze_in_context(self, name: str, cultural_context: str) -> Dict:
        """
        Analyze name in specific cultural context.
        
        Args:
            name: Name to analyze
            cultural_context: Cultural context key
        
        Returns:
            Culture-relative acoustic analysis
        """
        # Get universal analysis first
        universal = acoustic_analyzer.analyze(name)
        
        # Get cultural norms
        norms = self.CULTURAL_AESTHETICS.get(cultural_context, {})
        
        if not norms:
            return {
                'error': f'Unknown cultural context: {cultural_context}',
                'universal_analysis': universal
            }
        
        # Calculate culture-relative scores
        culture_relative = self._calculate_culture_relative(name, universal, norms)
        
        # Detect cultural outliers
        outliers = self._detect_cultural_outliers(name, universal, norms)
        
        return {
            'name': name,
            'cultural_context': cultural_context,
            'universal': {
                'melodiousness': universal['overall']['melodiousness'],
                'harshness': universal['harshness']['overall_score'],
                'complexity': universal['overall']['phonetic_complexity']
            },
            'culture_relative': culture_relative,
            'cultural_outliers': outliers,
            'interpretation': self._interpret_cultural_fit(culture_relative, outliers)
        }
    
    def _calculate_culture_relative(self, name: str, universal: Dict, norms: Dict) -> Dict:
        """Calculate culture-relative acoustic scores."""
        universal_melodious = universal['overall']['melodiousness']
        universal_harsh = universal['harshness']['overall_score']
        
        baseline_melodious = norms.get('melodiousness_baseline', 0.5)
        
        # Culture-relative melodiousness (how much above/below cultural norm)
        relative_melodious = universal_melodious - baseline_melodious
        
        # Adjust for cultural harsh tolerance
        harsh_tolerance = norms.get('harsh_tolerance', 0.5)
        acceptable_harsh = universal_harsh < harsh_tolerance
        
        # Count typical vs atypical syllables
        phonemes = self._extract_phonemes(name)
        syllable_count = self._estimate_syllables(name)
        typical_syllables = norms.get('typical_syllables', [2, 3])
        
        syllable_typical = syllable_count in typical_syllables
        
        # Preferred sound frequency
        preferred = norms.get('preferred_sounds', [])
        avoided = norms.get('avoided_sounds', [])
        
        phoneme_list = list(name.lower())
        preferred_count = sum(1 for p in phoneme_list if p in preferred)
        avoided_count = sum(1 for p in phoneme_list if p in avoided)
        
        cultural_fit_score = (
            (preferred_count / len(phoneme_list) if phoneme_list else 0) * 0.4 +
            (1 - avoided_count / len(phoneme_list) if phoneme_list else 1) * 0.3 +
            (1 if syllable_typical else 0.5) * 0.3
        )
        
        return {
            'relative_melodiousness': float(relative_melodious),
            'culturally_melodious': universal_melodious > baseline_melodious,
            'acceptable_harshness': acceptable_harsh,
            'syllable_typical': syllable_typical,
            'syllable_count': syllable_count,
            'cultural_fit_score': float(cultural_fit_score),
            'fit_category': 'high' if cultural_fit_score > 0.7 else 'medium' if cultural_fit_score > 0.5 else 'low'
        }
    
    def _detect_cultural_outliers(self, name: str, universal: Dict, norms: Dict) -> Dict:
        """Detect if name is culturally unusual."""
        outliers = []
        
        # Syllable outlier?
        syllable_count = self._estimate_syllables(name)
        typical = norms.get('typical_syllables', [2, 3])
        
        if syllable_count < min(typical) - 1:
            outliers.append(f"Unusually short ({syllable_count} syllables)")
        elif syllable_count > max(typical) + 1:
            outliers.append(f"Unusually long ({syllable_count} syllables)")
        
        # Melodiousness outlier?
        melodious = universal['overall']['melodiousness']
        baseline = norms.get('melodiousness_baseline', 0.5)
        
        if abs(melodious - baseline) > 0.25:  # >2 SD (assuming SD~0.12)
            if melodious > baseline:
                outliers.append("Exceptionally melodious for culture")
            else:
                outliers.append("Exceptionally harsh for culture")
        
        return {
            'is_outlier': len(outliers) > 0,
            'outlier_reasons': outliers,
            'outlier_count': len(outliers)
        }
    
    def _interpret_cultural_fit(self, culture_relative: Dict, outliers: Dict) -> str:
        """Interpret cultural fit."""
        fit_score = culture_relative['cultural_fit_score']
        is_outlier = outliers['is_outlier']
        
        if fit_score > 0.7 and not is_outlier:
            return "Culturally typical name—fits phonetic and frequency norms well"
        elif fit_score > 0.5:
            return "Moderately typical—some unusual features but acceptable"
        elif is_outlier:
            return f"Cultural outlier—{'; '.join(outliers['outlier_reasons'])}"
        else:
            return "Culturally atypical name—doesn't match expected patterns"
    
    def _extract_phonemes(self, name: str) -> List[str]:
        """Extract simplified phonemes."""
        return list(name.lower().replace(' ', ''))
    
    def _estimate_syllables(self, name: str) -> int:
        """Estimate syllable count."""
        name = name.lower()
        vowels = 'aeiou'
        count = 0
        previous_was_vowel = False
        
        for char in name:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                count += 1
            previous_was_vowel = is_vowel
        
        # Adjust for silent e
        if name.endswith('e') and count > 1:
            count -= 1
        
        return max(count, 1)


# Singleton
cultural_acoustic_analyzer = CulturalAcousticAnalyzer()

