"""MTG Phonosemantic Alignment Analyzer

Analyzes sophisticated sound-symbolism patterns in MTG card names,
mapping phonetic features to mechanical and thematic card properties.

Theory: Different phonemes carry inherent connotations that align with
MTG color philosophy and card mechanics (harsh sounds for damage,
soft sounds for healing, etc.)
"""

import logging
from typing import Dict, List, Tuple
import re

logger = logging.getLogger(__name__)


class MTGPhonosemanticAnalyzer:
    """Analyzes phonosemantic alignment between card names and mechanics."""
    
    def __init__(self):
        # Phoneme categories with IPA-like classifications
        self.phoneme_categories = {
            # Harsh/Aggressive sounds
            'plosives': ['k', 'g', 't', 'd', 'p', 'b'],  # Sudden stops
            'harsh_fricatives': ['x', 'kh', 'gh'],  # Guttural friction
            'sibilants': ['s', 'z', 'sh', 'zh'],  # Hissing sounds
            
            # Soft/Gentle sounds
            'liquids': ['l', 'r'],  # Flowing continuants
            'nasals': ['m', 'n', 'ng'],  # Resonant sounds
            'glides': ['w', 'y', 'j'],  # Smooth transitions
            
            # Intermediate
            'fricatives': ['f', 'v', 'th'],  # Softer friction
            'affricates': ['ch', 'j'],  # Combined stops
        }
        
        # Vowel classifications
        self.vowel_categories = {
            'high_front': ['i', 'ee', 'ea'],  # Bright, sharp (blue/white)
            'high_back': ['u', 'oo', 'ou'],  # Dark, deep (black)
            'mid': ['e', 'o'],  # Neutral
            'low': ['a', 'aa', 'ah'],  # Open, powerful (red/green)
            'diphthongs': ['ai', 'ei', 'oi', 'au', 'ou'],  # Complex
        }
        
        # Color identity phonetic signatures
        self.color_phonetics = {
            'R': {  # Red - aggressive, explosive
                'preferred_consonants': ['k', 'g', 'r', 'x', 'z'],
                'preferred_vowels': ['a', 'o'],  # Open, loud
                'phonetic_quality': 'harsh_explosive',
                'stress_pattern': 'strong_initial',
            },
            'U': {  # Blue - cerebral, flowing
                'preferred_consonants': ['s', 'l', 'n', 'th'],
                'preferred_vowels': ['i', 'e', 'ee'],  # Bright, precise
                'phonetic_quality': 'sibilant_flowing',
                'stress_pattern': 'distributed',
            },
            'B': {  # Black - dark, ominous
                'preferred_consonants': ['d', 'g', 'v', 'z', 'th'],
                'preferred_vowels': ['u', 'o', 'a'],  # Dark, deep
                'phonetic_quality': 'voiced_dark',
                'stress_pattern': 'final_heavy',
            },
            'G': {  # Green - natural, organic
                'preferred_consonants': ['l', 'r', 'm', 'n', 'w'],
                'preferred_vowels': ['o', 'a', 'ou'],  # Rounded, natural
                'phonetic_quality': 'liquid_resonant',
                'stress_pattern': 'flowing',
            },
            'W': {  # White - pure, protective
                'preferred_consonants': ['l', 'm', 'n', 'w', 's'],
                'preferred_vowels': ['i', 'e', 'a'],  # Clear, bright
                'phonetic_quality': 'soft_aspirated',
                'stress_pattern': 'gentle',
            },
        }
        
        # Mechanical-phonetic correlations
        self.mechanic_phonetics = {
            'damage': ['k', 't', 'x', 'g', 'z'],  # Sharp, sudden
            'healing': ['l', 'm', 'n', 'w'],  # Soft, flowing
            'destruction': ['d', 'k', 'r', 'x'],  # Harsh stops
            'creation': ['b', 'l', 'n', 'm'],  # Soft builds
            'counter': ['s', 'n', 't', 'c'],  # Precise, blocking
            'draw': ['l', 'r', 'w'],  # Flowing, continuous
            'sacrifice': ['k', 'd', 'g', 'v'],  # Dark, harsh
            'protection': ['w', 'l', 'm', 'sh'],  # Soft, shielding
        }
    
    def analyze_card_phonetics(self, name: str, color_identity: str = None,
                               card_type: str = None, oracle_text: str = None) -> Dict:
        """Comprehensive phonosemantic analysis of MTG card name.
        
        Args:
            name: Card name
            color_identity: Color(s) - e.g., 'R', 'UB', 'GW'
            card_type: Card type line
            oracle_text: Card text (to infer mechanics)
            
        Returns:
            Dict with phonosemantic scores and alignments
        """
        name_lower = name.lower()
        
        # Basic phonetic decomposition
        consonants, vowels = self._extract_phonemes(name_lower)
        
        # Calculate core phonetic scores
        harshness_score = self._calculate_harshness(name_lower, consonants)
        softness_score = self._calculate_softness(name_lower, consonants)
        sibilance_score = self._calculate_sibilance(name_lower, consonants)
        resonance_score = self._calculate_resonance(name_lower, consonants)
        
        # Voiced/voiceless ratio (voiced = more aggressive/dark)
        voiced_ratio = self._calculate_voiced_ratio(consonants)
        
        # Vowel quality analysis
        vowel_brightness = self._calculate_vowel_brightness(vowels)
        vowel_openness = self._calculate_vowel_openness(vowels)
        
        # Stress and rhythm
        stress_pattern = self._detect_stress_pattern(name)
        phonological_weight = self._calculate_phonological_weight(name)
        
        # Color identity alignment (if provided)
        color_alignment = {}
        if color_identity:
            color_alignment = self._analyze_color_alignment(
                name_lower, consonants, vowels, color_identity
            )
        
        # Mechanic alignment (if oracle text provided)
        mechanic_alignment = {}
        if oracle_text:
            mechanic_alignment = self._analyze_mechanic_alignment(
                name_lower, consonants, oracle_text
            )
        
        # Phonetic complexity
        consonant_cluster_complexity = self._calculate_cluster_complexity(name_lower)
        phonotactic_rarity = self._calculate_phonotactic_rarity(name_lower)
        
        return {
            # Core phonetic dimensions (0-100)
            'harshness_score': round(harshness_score, 2),
            'softness_score': round(softness_score, 2),
            'sibilance_score': round(sibilance_score, 2),
            'resonance_score': round(resonance_score, 2),
            
            # Consonant quality
            'voiced_consonant_ratio': round(voiced_ratio, 2),
            'plosive_concentration': self._count_category(consonants, 'plosives') / max(len(consonants), 1),
            'liquid_concentration': self._count_category(consonants, 'liquids') / max(len(consonants), 1),
            'nasal_concentration': self._count_category(consonants, 'nasals') / max(len(consonants), 1),
            
            # Vowel quality
            'vowel_brightness': round(vowel_brightness, 2),
            'vowel_openness': round(vowel_openness, 2),
            'vowel_complexity': len(set(vowels)) / max(len(vowels), 1),
            
            # Rhythm and weight
            'stress_pattern': stress_pattern,
            'phonological_weight': round(phonological_weight, 2),
            'consonant_cluster_complexity': round(consonant_cluster_complexity, 2),
            'phonotactic_rarity': round(phonotactic_rarity, 2),
            
            # Alignment scores
            'color_alignment': color_alignment,
            'mechanic_alignment': mechanic_alignment,
            
            # Summary scores
            'aggressive_phonetic_profile': round((harshness_score + sibilance_score + voiced_ratio) / 3, 2),
            'gentle_phonetic_profile': round((softness_score + resonance_score + (100 - harshness_score)) / 3, 2),
        }
    
    def _extract_phonemes(self, name: str) -> Tuple[List[str], List[str]]:
        """Extract consonants and vowels from name."""
        vowels_set = set('aeiou')
        consonants = []
        vowels = []
        
        # Clean name
        clean = re.sub(r'[^a-z]', '', name)
        
        for char in clean:
            if char in vowels_set:
                vowels.append(char)
            else:
                consonants.append(char)
        
        return consonants, vowels
    
    def _calculate_harshness(self, name: str, consonants: List[str]) -> float:
        """Calculate harshness score (0-100) based on plosives and harsh fricatives."""
        if not consonants:
            return 0.0
        
        score = 0.0
        
        # Plosive concentration (k, g, t, d, p, b)
        plosive_count = sum(1 for c in consonants if c in self.phoneme_categories['plosives'])
        score += (plosive_count / len(consonants)) * 50
        
        # Harsh sounds (x, z, hard consonant clusters)
        harsh_count = sum(1 for c in ['x', 'z', 'q'] if c in name)
        score += harsh_count * 15
        
        # Double consonants (harsher feel)
        double_consonants = len(re.findall(r'([bcdfghjklmnpqrstvwxz])\1', name))
        score += double_consonants * 10
        
        # Initial hard consonants
        if name and name[0] in ['k', 'g', 't', 'd', 'x', 'z']:
            score += 10
        
        return min(100, score)
    
    def _calculate_softness(self, name: str, consonants: List[str]) -> float:
        """Calculate softness score (0-100) based on liquids, nasals, glides."""
        if not consonants:
            return 50.0
        
        score = 0.0
        
        # Liquid concentration (l, r)
        liquid_count = sum(1 for c in consonants if c in self.phoneme_categories['liquids'])
        score += (liquid_count / len(consonants)) * 40
        
        # Nasal concentration (m, n)
        nasal_count = sum(1 for c in consonants if c in self.phoneme_categories['nasals'])
        score += (nasal_count / len(consonants)) * 40
        
        # Glide/semivowel presence (w, y)
        glide_count = sum(1 for c in ['w', 'y'] if c in name)
        score += glide_count * 10
        
        # Ends in soft consonants
        if name and name[-1] in ['l', 'n', 'm', 'w']:
            score += 15
        
        return min(100, score)
    
    def _calculate_sibilance(self, name: str, consonants: List[str]) -> float:
        """Calculate sibilance score (hissing sounds: s, z, sh, zh)."""
        if not consonants:
            return 0.0
        
        sibilant_count = sum(1 for c in consonants if c in self.phoneme_categories['sibilants'])
        sibilant_count += name.count('sh') + name.count('zh')
        
        score = (sibilant_count / max(len(consonants), 1)) * 100
        
        # Initial 's' is particularly sibilant
        if name.startswith('s'):
            score += 15
        
        return min(100, score)
    
    def _calculate_resonance(self, name: str, consonants: List[str]) -> float:
        """Calculate resonance score (nasals + vowels create resonance)."""
        if not name:
            return 0.0
        
        # Nasal concentration
        nasal_count = sum(1 for c in consonants if c in self.phoneme_categories['nasals'])
        nasal_ratio = nasal_count / max(len(consonants), 1)
        
        # Vowel ratio (more vowels = more resonance)
        vowel_count = sum(1 for c in name if c in 'aeiou')
        vowel_ratio = vowel_count / len(name)
        
        score = (nasal_ratio * 50) + (vowel_ratio * 50)
        
        return min(100, score)
    
    def _calculate_voiced_ratio(self, consonants: List[str]) -> float:
        """Calculate ratio of voiced consonants (b, d, g, v, z, etc.)."""
        if not consonants:
            return 50.0
        
        voiced = ['b', 'd', 'g', 'v', 'z', 'j', 'm', 'n', 'l', 'r', 'w', 'y']
        voiced_count = sum(1 for c in consonants if c in voiced)
        
        return (voiced_count / len(consonants)) * 100
    
    def _calculate_vowel_brightness(self, vowels: List[str]) -> float:
        """Calculate vowel brightness (i, e = bright; u, o = dark)."""
        if not vowels:
            return 50.0
        
        bright_vowels = ['i', 'e']
        dark_vowels = ['u', 'o']
        
        bright_count = sum(1 for v in vowels if v in bright_vowels)
        dark_count = sum(1 for v in vowels if v in dark_vowels)
        
        # Score: 100 = very bright, 0 = very dark, 50 = neutral
        if bright_count + dark_count == 0:
            return 50.0
        
        return (bright_count / (bright_count + dark_count)) * 100
    
    def _calculate_vowel_openness(self, vowels: List[str]) -> float:
        """Calculate vowel openness (a = most open, i/u = most closed)."""
        if not vowels:
            return 50.0
        
        openness_map = {'a': 100, 'o': 70, 'e': 50, 'i': 20, 'u': 20}
        
        total_openness = sum(openness_map.get(v, 50) for v in vowels)
        return total_openness / len(vowels)
    
    def _detect_stress_pattern(self, name: str) -> str:
        """Detect likely stress pattern (simplified)."""
        words = name.split()
        if not words:
            return 'unknown'
        
        # Simple heuristic: longer words tend to have initial stress
        avg_word_length = sum(len(w) for w in words) / len(words)
        
        if avg_word_length <= 4:
            return 'monosyllabic_simple'
        elif avg_word_length <= 7:
            return 'initial_stress'
        else:
            return 'distributed_stress'
    
    def _calculate_phonological_weight(self, name: str) -> float:
        """Calculate overall phonological weight/complexity."""
        score = 0.0
        
        # Syllable count proxy (very rough)
        vowel_groups = len(re.findall(r'[aeiou]+', name.lower()))
        score += min(vowel_groups * 15, 60)
        
        # Consonant clusters
        clusters = len(re.findall(r'[bcdfghjklmnpqrstvwxz]{2,}', name.lower()))
        score += clusters * 10
        
        # Overall length
        score += min(len(name) * 2, 40)
        
        return min(100, score)
    
    def _calculate_cluster_complexity(self, name: str) -> float:
        """Calculate consonant cluster complexity."""
        clusters = re.findall(r'[bcdfghjklmnpqrstvwxz]{2,}', name)
        
        if not clusters:
            return 0.0
        
        # Weight by cluster length
        complexity = sum((len(c) - 1) * 20 for c in clusters)
        
        # Rare clusters (e.g., 'thr', 'spl') add extra complexity
        rare_patterns = ['thr', 'shr', 'spl', 'str', 'scr', 'spr']
        for pattern in rare_patterns:
            if pattern in name:
                complexity += 15
        
        return min(100, complexity)
    
    def _calculate_phonotactic_rarity(self, name: str) -> float:
        """Calculate how rare/unusual the phonotactic patterns are."""
        score = 0.0
        
        # Rare letter combinations
        rare_combos = ['xh', 'kh', 'zh', 'qx', 'zz', 'kk', 'qq']
        for combo in rare_combos:
            if combo in name:
                score += 20
        
        # Apostrophes (constructed language marker)
        score += name.count("'") * 15
        
        # Unusual initial clusters
        if name and len(name) > 1:
            initial = name[:2]
            if initial in ['kh', 'zh', 'xh', 'vl', 'vr', 'tl']:
                score += 20
        
        return min(100, score)
    
    def _count_category(self, consonants: List[str], category: str) -> int:
        """Count consonants in a specific category."""
        if category not in self.phoneme_categories:
            return 0
        
        category_set = set(self.phoneme_categories[category])
        return sum(1 for c in consonants if c in category_set)
    
    def _analyze_color_alignment(self, name: str, consonants: List[str],
                                 vowels: List[str], color_identity: str) -> Dict:
        """Analyze how well name aligns with color identity phonetics."""
        alignments = {}
        
        # Analyze each color in identity
        for color in color_identity:
            if color not in self.color_phonetics:
                continue
            
            profile = self.color_phonetics[color]
            score = 0.0
            
            # Check preferred consonants
            preferred_cons = profile['preferred_consonants']
            consonant_match = sum(1 for c in consonants if c in preferred_cons)
            score += (consonant_match / max(len(consonants), 1)) * 50
            
            # Check preferred vowels
            preferred_vow = profile['preferred_vowels']
            vowel_match = sum(1 for v in vowels if v in preferred_vow)
            score += (vowel_match / max(len(vowels), 1)) * 50
            
            alignments[color] = {
                'alignment_score': round(score, 2),
                'phonetic_quality': profile['phonetic_quality'],
                'consonant_match_rate': round((consonant_match / max(len(consonants), 1)) * 100, 2),
                'vowel_match_rate': round((vowel_match / max(len(vowels), 1)) * 100, 2),
            }
        
        # Calculate overall multi-color alignment
        if len(alignments) > 1:
            avg_alignment = sum(a['alignment_score'] for a in alignments.values()) / len(alignments)
            alignments['overall'] = round(avg_alignment, 2)
        elif len(alignments) == 1:
            alignments['overall'] = list(alignments.values())[0]['alignment_score']
        else:
            alignments['overall'] = 0.0
        
        return alignments
    
    def _analyze_mechanic_alignment(self, name: str, consonants: List[str],
                                    oracle_text: str) -> Dict:
        """Analyze alignment between name phonetics and card mechanics."""
        oracle_lower = oracle_text.lower()
        alignments = {}
        
        for mechanic, preferred_phonemes in self.mechanic_phonetics.items():
            # Check if card has this mechanic (simple keyword matching)
            if mechanic in oracle_lower or self._has_mechanic_keyword(mechanic, oracle_lower):
                # Calculate phoneme alignment
                phoneme_match = sum(1 for c in consonants if c in preferred_phonemes)
                score = (phoneme_match / max(len(consonants), 1)) * 100
                
                alignments[mechanic] = {
                    'alignment_score': round(score, 2),
                    'present': True,
                    'phoneme_match_count': phoneme_match,
                }
        
        return alignments
    
    def _has_mechanic_keyword(self, mechanic: str, oracle_text: str) -> bool:
        """Check if oracle text contains mechanic keywords."""
        keyword_map = {
            'damage': ['damage', 'deals', 'destroy'],
            'healing': ['gain', 'life', 'heal'],
            'destruction': ['destroy', 'exile', 'sacrifice'],
            'creation': ['create', 'token', 'put onto'],
            'counter': ['counter target'],
            'draw': ['draw'],
            'sacrifice': ['sacrifice'],
            'protection': ['prevent', 'protection', 'indestructible'],
        }
        
        keywords = keyword_map.get(mechanic, [])
        return any(kw in oracle_text for kw in keywords)

