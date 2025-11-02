"""
Phonemic Analyzer
Deep analysis of individual sounds in names
"""

import re
import logging

logger = logging.getLogger(__name__)


class PhonemicAnalyzer:
    """Analyze phonemic characteristics of names"""
    
    def __init__(self):
        # Phoneme classifications
        self.plosives = set('ptkbdg')  # Stop consonants
        self.fricatives = set('fvszhθð')  # Friction consonants
        self.nasals = set('mn')
        self.liquids = set('lr')
        self.voiced_consonants = set('bdgvzmnlr')
        self.voiceless_consonants = set('ptkfshθ')
        
        # Vowel classifications
        self.front_vowels = set('ieæ')  # High energy, bright
        self.back_vowels = set('ouɔɑ')  # Low energy, dark
        self.high_vowels = set('iu')  # Small, fast associations
        self.low_vowels = set('æɑɔ')  # Large, slow associations
    
    def analyze(self, name):
        """
        Comprehensive phonemic analysis
        
        Returns: Dict with detailed phonemic metrics
        """
        name_lower = name.lower()
        
        # Count phoneme types
        plosive_count = sum(1 for c in name_lower if c in self.plosives)
        fricative_count = sum(1 for c in name_lower if c in self.fricatives)
        nasal_count = sum(1 for c in name_lower if c in self.nasals)
        liquid_count = sum(1 for c in name_lower if c in self.liquids)
        
        total_consonants = plosive_count + fricative_count + nasal_count + liquid_count
        
        # Consonant distribution
        plosive_ratio = plosive_count / total_consonants if total_consonants > 0 else 0
        fricative_ratio = fricative_count / total_consonants if total_consonants > 0 else 0
        
        # Voicing
        voiced_count = sum(1 for c in name_lower if c in self.voiced_consonants)
        voiceless_count = sum(1 for c in name_lower if c in self.voiceless_consonants)
        voicing_ratio = voiced_count / (voiced_count + voiceless_count) if (voiced_count + voiceless_count) > 0 else 0.5
        
        # Vowel analysis
        vowels = [c for c in name_lower if c in 'aeiou']
        front_vowel_count = sum(1 for v in vowels if v in 'ie')
        back_vowel_count = sum(1 for v in vowels if v in 'ou')
        
        vowel_frontness = front_vowel_count / len(vowels) if vowels else 0.5
        
        # Initial sound (very important for brand recall)
        initial_sound = name_lower[0] if name_lower else ''
        initial_is_plosive = initial_sound in self.plosives
        initial_is_fricative = initial_sound in self.fricatives
        initial_is_voiceless = initial_sound in self.voiceless_consonants
        
        # Alliteration detection (repeated initial sounds)
        words = name.split()
        has_alliteration = len(words) > 1 and len(set(w[0].lower() for w in words if w)) == 1
        
        # Consonant clustering (difficulty score)
        consonant_clusters = re.findall(r'[bcdfghjklmnpqrstvwxyz]{2,}', name_lower)
        max_cluster_length = max([len(c) for c in consonant_clusters]) if consonant_clusters else 0
        cluster_difficulty = min(100, max_cluster_length * 25)  # 0-100 scale
        
        # Phonotactic probability (how natural sound combinations are)
        # Simplified: penalize unusual clusters
        unusual_clusters = ['ht', 'pn', 'pt', 'tk', 'nm']
        unusual_count = sum(1 for uc in unusual_clusters if uc in name_lower)
        phonotactic_score = max(0, 100 - unusual_count * 20)
        
        return {
            'plosive_count': plosive_count,
            'fricative_count': fricative_count,
            'nasal_count': nasal_count,
            'liquid_count': liquid_count,
            'plosive_ratio': round(plosive_ratio, 3),
            'fricative_ratio': round(fricative_ratio, 3),
            'voicing_ratio': round(voicing_ratio, 3),
            'vowel_frontness': round(vowel_frontness, 3),
            'initial_sound': initial_sound,
            'initial_is_plosive': initial_is_plosive,
            'initial_is_fricative': initial_is_fricative,
            'initial_is_voiceless': initial_is_voiceless,
            'has_alliteration': has_alliteration,
            'max_cluster_length': max_cluster_length,
            'cluster_difficulty': cluster_difficulty,
            'phonotactic_score': phonotactic_score,
            'phonemic_quality': self._calculate_quality(plosive_ratio, fricative_ratio, voicing_ratio, vowel_frontness, cluster_difficulty, phonotactic_score)
        }
    
    def _calculate_quality(self, plosive_ratio, fricative_ratio, voicing_ratio, vowel_frontness, cluster_diff, phonotactic):
        """Calculate overall phonemic quality score"""
        score = 50  # Base
        
        # Plosives are memorable (especially initial)
        score += plosive_ratio * 20
        
        # Balanced voicing is good
        voicing_balance = 1 - abs(voicing_ratio - 0.5) * 2
        score += voicing_balance * 15
        
        # Front vowels are brighter/more energetic
        score += vowel_frontness * 10
        
        # Low cluster difficulty is better
        score += (100 - cluster_diff) * 0.05
        
        # High phonotactic probability is better
        score += phonotactic * 0.1
        
        return min(100, max(0, score))

