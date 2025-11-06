"""MTG Format-Specific Linguistic Analyzer

Analyzes linguistic markers that correlate with different competitive formats.

Theory: Commander/EDH cards have more epic, verbose naming while competitive
formats (Modern, Legacy, Vintage) favor terse, efficient names. Casual vs
competitive naming strategies differ systematically.
"""

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class MTGFormatAnalyzer:
    """Analyzes format-specific linguistic markers in card names."""
    
    def __init__(self):
        # Commander/EDH linguistic markers
        self.commander_markers = {
            'epic_titles': ['lord', 'master', 'elder', 'ancient', 'king', 'queen', 
                          'emperor', 'god', 'primordial'],
            'legendary_epithets': True,  # Comma-separated titles
            'long_names': True,  # 3+ words
            'fantasy_vocabulary': ['eternal', 'infinite', 'supreme', 'ultimate'],
            'narrative_complexity': 'high',
            'avg_syllables': (4, 7),  # Range
            'avg_length': (15, 35),  # Characters
        }
        
        # Modern/Legacy markers (competitive constructed)
        self.competitive_markers = {
            'terse_names': True,  # 1-2 words
            'mechanical_efficiency': ['bolt', 'snap', 'push', 'path'],
            'simple_descriptors': True,
            'avg_syllables': (2, 4),
            'avg_length': (8, 18),
        }
        
        # Vintage markers (older, classic naming)
        self.vintage_markers = {
            'archaic_language': ['mox', 'lotus', 'timetwister', 'ancestral'],
            'simple_structure': True,
            'iconic_brevity': True,
            'avg_syllables': (2, 3),
            'avg_length': (6, 14),
        }
        
        # Standard markers (current, trendy)
        self.standard_markers = {
            'modern_fantasy': True,
            'planeswalker_names': True,  # Character-focused
            'set_themed': True,
            'avg_syllables': (3, 5),
            'avg_length': (10, 22),
        }
        
        # Limited/Draft markers (splashy, memorable)
        self.limited_markers = {
            'memorable': True,
            'flavorful': True,
            'creature_focused': True,
            'avg_syllables': (3, 5),
            'avg_length': (12, 24),
        }
    
    def analyze_format_linguistic_markers(self, name: str, format_legalities: Dict = None,
                                         card_type: str = None, is_legendary: bool = False,
                                         converted_mana_cost: float = None) -> Dict:
        """Analyze format-specific linguistic characteristics.
        
        Args:
            name: Card name
            format_legalities: Dict of format -> legal/banned/restricted
            card_type: Card type line
            is_legendary: Whether legendary
            converted_mana_cost: CMC
            
        Returns:
            Dict with format affinity scores and predictions
        """
        # Basic metrics
        word_count = len(name.split())
        char_length = len(name)
        syllable_count = self._estimate_syllables(name)
        has_comma = ',' in name
        
        # Calculate format affinity scores
        commander_score = self._calculate_commander_affinity(
            name, word_count, char_length, syllable_count, has_comma,
            is_legendary, card_type
        )
        
        competitive_score = self._calculate_competitive_affinity(
            name, word_count, char_length, syllable_count,
            converted_mana_cost, card_type
        )
        
        vintage_score = self._calculate_vintage_affinity(
            name, word_count, char_length, syllable_count
        )
        
        limited_score = self._calculate_limited_affinity(
            name, word_count, char_length, syllable_count
        )
        
        # Determine primary format affinity
        scores = {
            'commander': commander_score,
            'competitive_constructed': competitive_score,
            'vintage': vintage_score,
            'limited': limited_score,
        }
        
        primary_affinity = max(scores, key=scores.get)
        
        # Naming strategy classification
        naming_strategy = self._classify_naming_strategy(
            word_count, char_length, syllable_count, has_comma, is_legendary
        )
        
        # Multiplayer signaling (Commander-specific)
        multiplayer_signaling = self._analyze_multiplayer_signaling(
            name, is_legendary, card_type
        )
        
        return {
            # Format affinity scores (0-100)
            'commander_affinity': round(commander_score, 2),
            'competitive_affinity': round(competitive_score, 2),
            'vintage_affinity': round(vintage_score, 2),
            'limited_affinity': round(limited_score, 2),
            
            # Primary affinity
            'primary_format_affinity': primary_affinity,
            'format_affinity_scores': {k: round(v, 2) for k, v in scores.items()},
            
            # Naming strategy
            'naming_strategy': naming_strategy,
            'is_epic_naming': naming_strategy in ['epic_legendary', 'narrative_complex'],
            'is_efficient_naming': naming_strategy in ['competitive_terse', 'vintage_iconic'],
            
            # Multiplayer signals
            'multiplayer_signaling': multiplayer_signaling,
            
            # Metrics
            'word_count': word_count,
            'character_length': char_length,
            'estimated_syllables': syllable_count,
            'has_epithet_structure': has_comma,
        }
    
    def _calculate_commander_affinity(self, name: str, words: int, chars: int,
                                      syllables: int, has_comma: bool,
                                      is_legendary: bool, card_type: str) -> float:
        """Calculate Commander/EDH format affinity."""
        score = 0.0
        name_lower = name.lower()
        
        # Legendary status (huge boost)
        if is_legendary:
            score += 30
        
        # Epic title markers
        title_count = sum(1 for title in self.commander_markers['epic_titles'] 
                         if title in name_lower)
        score += min(title_count * 20, 40)
        
        # Comma-separated epithet structure
        if has_comma:
            score += 25
        
        # Length metrics (Commander favors longer, more epic names)
        if 15 <= chars <= 35:
            score += 20
        elif chars > 35:
            score += 10
        
        # Syllable count (4-7 optimal for epic feel)
        if 4 <= syllables <= 7:
            score += 15
        elif syllables > 7:
            score += 10
        
        # Multi-word names (narrative complexity)
        if words >= 3:
            score += 15
        
        # Fantasy vocabulary
        fantasy_count = sum(1 for word in self.commander_markers['fantasy_vocabulary']
                          if word in name_lower)
        score += fantasy_count * 10
        
        return min(100, score)
    
    def _calculate_competitive_affinity(self, name: str, words: int, chars: int,
                                       syllables: int, cmc: float,
                                       card_type: str) -> float:
        """Calculate competitive constructed (Modern/Legacy) affinity."""
        score = 0.0
        name_lower = name.lower()
        
        # Terse names (1-2 words)
        if words <= 2:
            score += 30
        elif words == 3:
            score += 10
        
        # Efficient length (8-18 characters)
        if 8 <= chars <= 18:
            score += 25
        
        # Moderate syllables (2-4)
        if 2 <= syllables <= 4:
            score += 20
        
        # Low CMC (competitive cards are efficient)
        if cmc is not None:
            if cmc <= 2:
                score += 20
            elif cmc <= 4:
                score += 10
        
        # Mechanical efficiency markers
        if any(marker in name_lower for marker in self.competitive_markers['mechanical_efficiency']):
            score += 15
        
        # Instant/sorcery (competitive formats love spells)
        if card_type and ('instant' in card_type.lower() or 'sorcery' in card_type.lower()):
            score += 15
        
        return min(100, score)
    
    def _calculate_vintage_affinity(self, name: str, words: int, chars: int,
                                    syllables: int) -> float:
        """Calculate Vintage format affinity (classic, iconic names)."""
        score = 0.0
        name_lower = name.lower()
        
        # Very short, iconic names
        if words == 1 and 4 <= chars <= 10:
            score += 40
        elif words <= 2 and chars <= 14:
            score += 25
        
        # Low syllable count (iconic brevity)
        if syllables <= 3:
            score += 30
        
        # Archaic language markers
        if any(marker in name_lower for marker in self.vintage_markers['archaic_language']):
            score += 30
        
        # Simple, memorable structure
        if words <= 2 and syllables <= 3:
            score += 20
        
        return min(100, score)
    
    def _calculate_limited_affinity(self, name: str, words: int, chars: int,
                                    syllables: int) -> float:
        """Calculate Limited/Draft format affinity."""
        score = 50.0  # Baseline (most cards are draftable)
        
        # Moderate length (memorable but not epic)
        if 12 <= chars <= 24:
            score += 20
        
        # Moderate complexity (3-5 syllables)
        if 3 <= syllables <= 5:
            score += 20
        
        # 2-3 word names (flavorful but not overly complex)
        if 2 <= words <= 3:
            score += 15
        
        return min(100, score)
    
    def _classify_naming_strategy(self, words: int, chars: int, syllables: int,
                                  has_comma: bool, is_legendary: bool) -> str:
        """Classify overall naming strategy."""
        if has_comma and is_legendary:
            return 'epic_legendary'
        elif words >= 4 or chars >= 30:
            return 'narrative_complex'
        elif words <= 2 and chars <= 12:
            return 'competitive_terse'
        elif words == 1 and chars <= 8:
            return 'vintage_iconic'
        elif words == 2 or words == 3:
            return 'standard_descriptive'
        else:
            return 'casual_flavorful'
    
    def _analyze_multiplayer_signaling(self, name: str, is_legendary: bool,
                                      card_type: str) -> Dict:
        """Analyze multiplayer/Commander social signaling in name."""
        name_lower = name.lower()
        
        # Multiplayer keywords
        multiplayer_keywords = ['group', 'each', 'all', 'everyone', 'council', 'monarch']
        has_multiplayer_keyword = any(kw in name_lower for kw in multiplayer_keywords)
        
        # Political/social vocabulary
        political_words = ['alliance', 'treaty', 'pact', 'council', 'assembly', 'vote']
        has_political = any(word in name_lower for word in political_words)
        
        # Commander-specific tropes
        commander_tropes = ['commander', 'general', 'warlord', 'chieftain']
        has_commander_trope = any(trope in name_lower for trope in commander_tropes)
        
        # Calculate multiplayer signal strength
        signal_strength = 0.0
        if is_legendary:
            signal_strength += 30
        if has_multiplayer_keyword:
            signal_strength += 25
        if has_political:
            signal_strength += 20
        if has_commander_trope:
            signal_strength += 25
        
        return {
            'signal_strength': round(min(100, signal_strength), 2),
            'has_multiplayer_keywords': has_multiplayer_keyword,
            'has_political_vocabulary': has_political,
            'has_commander_tropes': has_commander_trope,
            'is_multiplayer_focused': signal_strength > 50,
        }
    
    def _estimate_syllables(self, word: str) -> int:
        """Rough syllable estimation."""
        word = word.lower()
        count = 0
        vowels = 'aeiouy'
        previous_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                count += 1
            previous_was_vowel = is_vowel
        
        # Adjust for silent e
        if word.endswith('e'):
            count -= 1
        
        # Minimum 1 syllable
        if count == 0:
            count = 1
        
        return count

