"""MTG Constructed Language Analyzer

Analyzes sophisticated constructed language patterns in MTG card names,
detecting linguistic archetypes (Elvish, Phyrexian, Draconic, etc.) and
measuring morphological complexity.

Goes beyond simple apostrophe counting to detect:
- Phonotactic patterns specific to MTG's fictional languages
- Morphological structures (agglutination, compounding)
- Cross-linguistic borrowing
- Orthographic conventions
"""

import logging
import re
from typing import Dict, List, Set, Tuple

logger = logging.getLogger(__name__)


class MTGConstructedLanguageAnalyzer:
    """Analyzes constructed language sophistication in MTG card names."""
    
    def __init__(self):
        # Elvish/Llanowar patterns (fluid, natural, vowel-harmonic)
        self.elvish_patterns = {
            'phonotactics': {
                'preferred_clusters': ['ll', 'th', 'dh', 'lv', 'rw'],
                'vowel_harmony': True,
                'liquid_heavy': True,
                'soft_consonants': ['l', 'n', 'r', 'v', 'w', 'th'],
            },
            'morphology': {
                'suffixes': ['wen', 'iel', 'ath', 'orn', 'iel', 'dir'],
                'prefixes': ['el', 'gal', 'lin'],
                'infixes': False,
            },
            'orthography': {
                'apostrophe_rare': True,
                'double_consonants': ['ll'],
                'diacritics': False,
            },
        }
        
        # Phyrexian patterns (harsh, mechanical, aggressive)
        self.phyrexian_patterns = {
            'phonotactics': {
                'preferred_clusters': ['xx', 'xh', 'kk', 'zz', 'vr', 'kr'],
                'harsh_consonants': ['k', 'x', 'z', 'g', 'v'],
                'glottal_stops': ["'"],
                'dark_vowels': ['u', 'o', 'a'],
            },
            'morphology': {
                'suffixes': ['vor', 'ex', 'rex', 'xis', 'ath'],
                'prefixes': ['vor', 'kher', 'rag'],
                'agglutination': True,
            },
            'orthography': {
                'apostrophe_common': True,
                'x_heavy': True,
                'double_harsh': ['xx', 'kk'],
            },
        }
        
        # Draconic patterns (gravitas, low vowels, long syllables)
        self.draconic_patterns = {
            'phonotactics': {
                'preferred_clusters': ['dr', 'gr', 'kr', 'th', 'gh'],
                'low_vowels': ['a', 'o', 'au'],
                'guttural': ['k', 'g', 'r', 'kh', 'gh'],
                'long_syllables': True,
            },
            'morphology': {
                'suffixes': ['ath', 'or', 'ax', 'ar', 'on'],
                'prefixes': ['drak', 'kor', 'ath'],
                'titles': ['the', 'ur-', 'ancient'],
            },
            'orthography': {
                'hyphens_common': True,
                'capitals_mid_word': False,
            },
        }
        
        # Thran/Ancient patterns (archaeological, formal, Latinate)
        self.ancient_patterns = {
            'phonotactics': {
                'latinate_clusters': ['ct', 'pt', 'mn', 'gn'],
                'formal_endings': ['us', 'um', 'is', 'os'],
            },
            'morphology': {
                'suffixes': ['us', 'um', 'is', 'ius', 'eum'],
                'prefixes': ['prae', 'neo', 'proto'],
                'compound_heavy': True,
            },
            'orthography': {
                'classical': True,
                'ae_ligature_implied': True,
            },
        }
        
        # Japanese-inspired (Kamigawa)
        self.japanese_patterns = {
            'phonotactics': {
                'cv_structure': True,  # Consonant-vowel alternation
                'no_clusters': True,
                'final_vowels': ['a', 'i', 'u', 'e', 'o'],
                'palatals': ['y', 'sh', 'ch'],
            },
            'morphology': {
                'suffixes': ['ko', 'ka', 'mi', 'no', 'ji'],
                'prefixes': ['kami', 'kiri', 'oni'],
                'honorifics': ['o-', '-san', '-sama'],
            },
            'orthography': {
                'simple': True,
                'no_apostrophes': True,
            },
        }
        
        # Cross-linguistic borrowing detection
        self.etymology_markers = {
            'latin': {
                'patterns': ['us$', 'um$', 'is$', 'ae', 'ius$'],
                'roots': ['corpus', 'magnus', 'rex', 'lux', 'nox'],
            },
            'greek': {
                'patterns': ['ph', 'th', 'ch', 'ps', 'os$', 'on$'],
                'roots': ['theos', 'logos', 'phobos', 'psyche'],
            },
            'sanskrit': {
                'patterns': ['dh', 'bh', 'ksh', 'ya', 'ma'],
                'roots': ['brahm', 'dev', 'asura', 'yama'],
            },
            'norse': {
                'patterns': ['dr', 'vr', 'thr', 'heimr', 'gard'],
                'roots': ['thor', 'odin', 'heim', 'ragnar'],
            },
            'celtic': {
                'patterns': ['ll', 'dh', 'bh', 'ch'],
                'roots': ['caith', 'llanowar', 'brigid'],
            },
        }
    
    def analyze_constructed_language(self, name: str, set_code: str = None,
                                     card_type: str = None) -> Dict:
        """Comprehensive constructed language analysis.
        
        Args:
            name: Card name
            set_code: Set code (to infer plane/world)
            card_type: Card type (legendary creatures more likely to have constructed lang)
            
        Returns:
            Dict with language archetype scores and morphological metrics
        """
        name_lower = name.lower()
        
        # Detect language archetypes
        elvish_score = self._detect_elvish(name, name_lower)
        phyrexian_score = self._detect_phyrexian(name, name_lower)
        draconic_score = self._detect_draconic(name, name_lower)
        ancient_score = self._detect_ancient(name, name_lower)
        japanese_score = self._detect_japanese(name, name_lower)
        
        # Morphological complexity analysis
        morphological_complexity = self._analyze_morphology(name, name_lower)
        
        # Phonotactic sophistication
        phonotactic_score = self._analyze_phonotactics(name_lower)
        
        # Orthographic conventions
        orthographic_sophistication = self._analyze_orthography(name)
        
        # Etymology detection
        etymology = self._detect_etymology(name_lower)
        
        # Overall constructed language score
        is_constructed = any([
            elvish_score > 60,
            phyrexian_score > 60,
            draconic_score > 60,
            ancient_score > 60,
            japanese_score > 60,
            "'" in name,
            re.search(r'[a-z]{2,}-[a-z]', name_lower),
        ])
        
        # Sophistication score (how linguistically creative)
        sophistication = self._calculate_sophistication(
            name, name_lower,
            elvish_score, phyrexian_score, draconic_score,
            ancient_score, japanese_score,
            morphological_complexity, phonotactic_score
        )
        
        return {
            # Language archetype scores (0-100)
            'elvish_score': round(elvish_score, 2),
            'phyrexian_score': round(phyrexian_score, 2),
            'draconic_score': round(draconic_score, 2),
            'ancient_thran_score': round(ancient_score, 2),
            'japanese_kamigawa_score': round(japanese_score, 2),
            
            # Dominant archetype
            'dominant_archetype': self._get_dominant_archetype(
                elvish_score, phyrexian_score, draconic_score,
                ancient_score, japanese_score
            ),
            
            # Morphological metrics
            'morphological_complexity': morphological_complexity,
            'phonotactic_sophistication': round(phonotactic_score, 2),
            'orthographic_sophistication': round(orthographic_sophistication, 2),
            
            # Etymology
            'etymological_roots': etymology,
            'cross_linguistic_borrowing': len(etymology) > 1,
            
            # Summary
            'is_constructed_language': is_constructed,
            'overall_sophistication': round(sophistication, 2),
            
            # Specific features
            'has_apostrophe': "'" in name,
            'has_hyphen': '-' in name,
            'has_unusual_clusters': self._has_unusual_clusters(name_lower),
            'vowel_harmony_present': self._has_vowel_harmony(name_lower),
        }
    
    def _detect_elvish(self, name: str, name_lower: str) -> float:
        """Detect Elvish linguistic patterns."""
        score = 0.0
        
        # Liquid-heavy (l, r, w)
        liquids = sum(1 for c in name_lower if c in 'lrw')
        if liquids > 0:
            score += min((liquids / len(name_lower)) * 100, 40)
        
        # Double 'll'
        if 'll' in name_lower:
            score += 20
        
        # Soft consonants dominance
        soft_cons = sum(1 for c in name_lower if c in 'lnrvwth')
        total_cons = sum(1 for c in name_lower if c not in 'aeiou ')
        if total_cons > 0:
            soft_ratio = soft_cons / total_cons
            score += soft_ratio * 30
        
        # Elvish suffixes
        elvish_suffixes = ['wen', 'iel', 'ath', 'orn', 'dir', 'ath']
        if any(name_lower.endswith(suffix) for suffix in elvish_suffixes):
            score += 20
        
        # Elvish prefixes
        if any(name_lower.startswith(pre) for pre in ['el', 'gal', 'lin']):
            score += 15
        
        # Vowel harmony (rough check)
        if self._has_vowel_harmony(name_lower):
            score += 15
        
        return min(100, score)
    
    def _detect_phyrexian(self, name: str, name_lower: str) -> float:
        """Detect Phyrexian linguistic patterns (harsh, mechanical)."""
        score = 0.0
        
        # X, K, Z heavy
        harsh_letters = sum(1 for c in name_lower if c in 'xkz')
        if harsh_letters > 0:
            score += min(harsh_letters * 25, 50)
        
        # Apostrophe (glottal stop)
        if "'" in name:
            score += 20
        
        # Double harsh consonants
        if any(pattern in name_lower for pattern in ['xx', 'kk', 'zz']):
            score += 25
        
        # Phyrexian suffixes
        if any(name_lower.endswith(s) for s in ['vor', 'ex', 'rex', 'xis', 'ath']):
            score += 20
        
        # Harsh clusters
        harsh_clusters = ['xh', 'kh', 'vr', 'kr', 'zr']
        if any(cluster in name_lower for cluster in harsh_clusters):
            score += 15
        
        # Dark vowels (u, o)
        vowels = [c for c in name_lower if c in 'aeiou']
        if vowels:
            dark_ratio = sum(1 for v in vowels if v in 'uo') / len(vowels)
            score += dark_ratio * 20
        
        return min(100, score)
    
    def _detect_draconic(self, name: str, name_lower: str) -> float:
        """Detect Draconic patterns (gravitas, guttural)."""
        score = 0.0
        
        # Guttural consonants (k, g, r)
        gutturals = sum(1 for c in name_lower if c in 'kgr')
        if gutturals > 0:
            score += min((gutturals / max(len(name_lower), 1)) * 100, 35)
        
        # Low vowels (a, o)
        vowels = [c for c in name_lower if c in 'aeiou']
        if vowels:
            low_ratio = sum(1 for v in vowels if v in 'ao') / len(vowels)
            score += low_ratio * 30
        
        # Draconic suffixes
        if any(name_lower.endswith(s) for s in ['ath', 'or', 'ax', 'ar', 'on']):
            score += 20
        
        # Title words (Ur-, Ancient, Elder)
        if any(title in name for title in ['Ur-', 'Ancient', 'Elder', 'Primal']):
            score += 25
        
        # Long name (draconic names tend to be imposing)
        if len(name) > 12:
            score += 15
        
        # Hyphenated (e.g., Ur-Dragon)
        if '-' in name:
            score += 10
        
        return min(100, score)
    
    def _detect_ancient(self, name: str, name_lower: str) -> float:
        """Detect Ancient/Thran/Latinate patterns."""
        score = 0.0
        
        # Latin endings
        latin_endings = ['us', 'um', 'is', 'os', 'ius', 'eum']
        if any(name_lower.endswith(ending) for ending in latin_endings):
            score += 30
        
        # Classical clusters
        classical = ['ct', 'pt', 'mn', 'gn', 'ae', 'ph', 'th']
        cluster_count = sum(1 for c in classical if c in name_lower)
        score += min(cluster_count * 15, 40)
        
        # Compound structure (multiple meaningful roots)
        if len(name.split()) > 2 or len(re.findall(r'[A-Z][a-z]+', name)) > 1:
            score += 20
        
        # Formal register (capital-heavy proper nouns)
        if name[0].isupper() and sum(1 for c in name if c.isupper()) > 1:
            score += 15
        
        return min(100, score)
    
    def _detect_japanese(self, name: str, name_lower: str) -> float:
        """Detect Japanese-inspired (Kamigawa) patterns."""
        score = 0.0
        
        # CV structure (consonant-vowel alternation)
        cv_pattern = re.findall(r'[bcdfghjklmnpqrstvwxyz][aeiou]', name_lower)
        if len(cv_pattern) > len(name_lower) / 3:
            score += 30
        
        # Ends in vowel
        if name_lower and name_lower[-1] in 'aeiou':
            score += 20
        
        # Japanese suffixes
        jp_suffixes = ['ko', 'ka', 'mi', 'no', 'ji', 'to', 'ke']
        if any(name_lower.endswith(s) for s in jp_suffixes):
            score += 25
        
        # Japanese prefixes
        if any(name_lower.startswith(p) for p in ['kami', 'kiri', 'oni', 'yuki']):
            score += 25
        
        # No consonant clusters (Japanese phonology)
        clusters = re.findall(r'[bcdfghjklmnpqrstvwxyz]{2,}', name_lower)
        if not clusters:
            score += 20
        
        # Palatal consonants
        if any(p in name_lower for p in ['sh', 'ch', 'y']):
            score += 10
        
        return min(100, score)
    
    def _analyze_morphology(self, name: str, name_lower: str) -> Dict:
        """Analyze morphological complexity."""
        # Word count
        words = name.split()
        word_count = len(words)
        
        # Compound detection
        is_compound = word_count > 2 or '-' in name
        
        # Affixation detection
        has_prefix = any(name_lower.startswith(p) for p in [
            'un', 're', 'pre', 'anti', 'super', 'mega', 'ultra'
        ])
        
        has_suffix = any(name_lower.endswith(s) for s in [
            'er', 'or', 'ist', 'ian', 'ness', 'tion', 'ment'
        ])
        
        # Agglutination (multiple meaningful parts stuck together)
        morpheme_count = word_count
        if '-' in name:
            morpheme_count += name.count('-')
        if "'" in name:
            morpheme_count += name.count("'")
        
        # Derivational complexity
        derived_from_verb = any(name_lower.endswith(s) for s in ['ing', 'ed', 'er'])
        
        return {
            'word_count': word_count,
            'morpheme_count': morpheme_count,
            'is_compound': is_compound,
            'has_prefix': has_prefix,
            'has_suffix': has_suffix,
            'agglutination_degree': min(morpheme_count * 25, 100),
            'derivational_complexity': 50 if (has_prefix or has_suffix or derived_from_verb) else 0,
        }
    
    def _analyze_phonotactics(self, name_lower: str) -> float:
        """Analyze phonotactic sophistication."""
        score = 0.0
        
        # Unusual consonant clusters
        if self._has_unusual_clusters(name_lower):
            score += 40
        
        # Vowel-consonant balance
        vowels = sum(1 for c in name_lower if c in 'aeiou')
        consonants = sum(1 for c in name_lower if c.isalpha() and c not in 'aeiou')
        if consonants > 0:
            vc_ratio = vowels / consonants
            # Ideal ratio around 0.6-0.8
            if 0.4 <= vc_ratio <= 1.0:
                score += 30
        
        # Syllable structure complexity
        syllable_complexity = len(re.findall(r'[aeiou]+', name_lower))
        score += min(syllable_complexity * 5, 30)
        
        return min(100, score)
    
    def _analyze_orthography(self, name: str) -> float:
        """Analyze orthographic sophistication."""
        score = 0.0
        
        # Special characters
        if "'" in name:
            score += 25
        if '-' in name:
            score += 20
        
        # Capitalization patterns
        caps = sum(1 for c in name if c.isupper())
        if caps > 1:
            score += 15
        
        # Length (longer names can be more sophisticated)
        score += min(len(name) * 2, 40)
        
        return min(100, score)
    
    def _detect_etymology(self, name_lower: str) -> List[str]:
        """Detect etymological roots."""
        detected = []
        
        for language, markers in self.etymology_markers.items():
            # Check patterns
            for pattern in markers['patterns']:
                if re.search(pattern, name_lower):
                    detected.append(language)
                    break
            
            # Check roots
            if language not in detected:
                for root in markers['roots']:
                    if root in name_lower:
                        detected.append(language)
                        break
        
        return list(set(detected))
    
    def _get_dominant_archetype(self, elvish: float, phyrexian: float,
                                draconic: float, ancient: float, japanese: float) -> str:
        """Get dominant language archetype."""
        scores = {
            'elvish': elvish,
            'phyrexian': phyrexian,
            'draconic': draconic,
            'ancient_thran': ancient,
            'japanese_kamigawa': japanese,
        }
        
        max_score = max(scores.values())
        if max_score < 40:
            return 'common_english'
        
        return max(scores, key=scores.get)
    
    def _calculate_sophistication(self, name: str, name_lower: str,
                                  elvish: float, phyrexian: float, draconic: float,
                                  ancient: float, japanese: float,
                                  morphology: Dict, phonotactics: float) -> float:
        """Calculate overall linguistic sophistication."""
        # Average of archetype scores
        archetype_avg = (elvish + phyrexian + draconic + ancient + japanese) / 5
        
        # Morphological weight
        morphology_score = morphology['agglutination_degree']
        
        # Combine
        sophistication = (archetype_avg * 0.4 + morphology_score * 0.3 + phonotactics * 0.3)
        
        # Bonus for special features
        if "'" in name:
            sophistication += 10
        if '-' in name:
            sophistication += 5
        if self._has_unusual_clusters(name_lower):
            sophistication += 10
        
        return min(100, sophistication)
    
    def _has_unusual_clusters(self, name_lower: str) -> bool:
        """Check for unusual consonant clusters."""
        unusual = ['xh', 'kh', 'zh', 'thr', 'shr', 'vr', 'vl', 'kl', 'zr', 'xx', 'kk', 'zz']
        return any(cluster in name_lower for cluster in unusual)
    
    def _has_vowel_harmony(self, name_lower: str) -> bool:
        """Check for vowel harmony (crude check)."""
        vowels = [c for c in name_lower if c in 'aeiou']
        if len(vowels) < 2:
            return False
        
        # Front vowels (i, e) vs back vowels (u, o, a)
        front = sum(1 for v in vowels if v in 'ie')
        back = sum(1 for v in vowels if v in 'uoa')
        
        # If >75% are front or back, there's harmony
        if front / len(vowels) > 0.75 or back / len(vowels) > 0.75:
            return True
        
        return False

