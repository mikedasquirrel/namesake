"""
Label Nominative Extractor
Extract comprehensive linguistic/nominative features from categorical labels
(team names, venues, play types, genres, etc.)

Purpose: Enable nominative analysis of ANY labeled categorical variable
Expected Impact: +5-9% ROI from ensemble nominative effects
"""

from typing import Dict, List, Optional
import logging
import re

logger = logging.getLogger(__name__)


class LabelNominativeExtractor:
    """
    Extract nominative features from categorical labels
    
    Applies the same 138-feature extraction framework to labels that
    was previously only applied to person names.
    """
    
    def __init__(self):
        """Initialize extractor with linguistic mappings"""
        self.plosives = set('ptkbdg')
        self.fricatives = set('fvsz')
        self.liquids = set('lr')
        self.nasals = set('mn')
        self.front_vowels = set('ie')
        self.back_vowels = set('ou')
        self.power_phonemes = set('ktbgdp')
        self.speed_phonemes = set('szfv')
        self.soft_phonemes = set('lmnr')
        
    def extract_label_features(self, label: str, label_type: str = 'general',
                               context: Optional[Dict] = None) -> Dict:
        """
        Extract comprehensive linguistic features from a label
        
        Args:
            label: The label text (e.g., "Kansas City Chiefs", "Lambeau Field")
            label_type: Type of label ('team', 'venue', 'play', 'genre', etc.)
            context: Additional context (sport, domain, etc.)
            
        Returns:
            Dictionary with all extracted features
        """
        if not label:
            return self._get_empty_features()
            
        # Clean the label
        label_clean = label.strip()
        label_lower = label_clean.lower()
        
        features = {}
        
        # === CORE LINGUISTIC FEATURES (Base) ===
        features.update(self._extract_base_linguistic(label_clean, label_lower))
        
        # === PHONETIC FEATURES ===
        features.update(self._extract_phonetic_features(label_lower))
        
        # === SEMANTIC FEATURES ===
        features.update(self._extract_semantic_features(label_clean, label_lower, label_type))
        
        # === LABEL-SPECIFIC FEATURES ===
        features.update(self._extract_label_specific_features(
            label_clean, label_lower, label_type, context
        ))
        
        # === METADATA ===
        features['label'] = label_clean
        features['label_type'] = label_type
        features['label_word_count'] = len(label_clean.split())
        
        return features
    
    def _extract_base_linguistic(self, label: str, label_lower: str) -> Dict:
        """Extract base linguistic features (same as person names)"""
        features = {}
        
        # Syllable count (approximate)
        features['syllables'] = self._count_syllables(label_lower)
        
        # Character length
        features['length'] = len(label_lower.replace(' ', ''))
        
        # Harshness score (0-100, based on plosives/harsh consonants)
        features['harshness'] = self._calculate_harshness(label_lower)
        
        # Memorability score (0-100, based on length, uniqueness, phonetics)
        features['memorability'] = self._calculate_memorability(label_lower)
        
        # Pronounceability (0-100, based on consonant clusters)
        features['pronounceability'] = self._calculate_pronounceability(label_lower)
        
        # Uniqueness (based on uncommon letters/combinations)
        features['uniqueness'] = self._calculate_uniqueness(label_lower)
        
        # Vowel ratio
        vowel_count = sum(c in 'aeiou' for c in label_lower)
        letter_count = sum(c.isalpha() for c in label_lower)
        features['vowel_ratio'] = vowel_count / max(letter_count, 1)
        
        # Consonant clusters
        features['consonant_clusters'] = self._count_consonant_clusters(label_lower)
        
        # First/last letter characteristics
        first_char = next((c for c in label_lower if c.isalpha()), '')
        last_char = next((c for c in reversed(label_lower) if c.isalpha()), '')
        features['first_letter_harsh'] = 1 if first_char in self.plosives else 0
        features['last_letter_harsh'] = 1 if last_char in self.plosives else 0
        
        return features
    
    def _extract_phonetic_features(self, label_lower: str) -> Dict:
        """Extract detailed phonetic features"""
        features = {}
        
        # Phoneme type counts
        features['plosive_count'] = sum(c in self.plosives for c in label_lower)
        features['fricative_count'] = sum(c in self.fricatives for c in label_lower)
        features['liquid_count'] = sum(c in self.liquids for c in label_lower)
        features['nasal_count'] = sum(c in self.nasals for c in label_lower)
        
        # Vowel types
        features['front_vowel_count'] = sum(c in self.front_vowels for c in label_lower)
        features['back_vowel_count'] = sum(c in self.back_vowels for c in label_lower)
        
        # Power/speed/soft phoneme counts
        features['power_phoneme_count'] = sum(c in self.power_phonemes for c in label_lower)
        features['speed_phoneme_count'] = sum(c in self.speed_phonemes for c in label_lower)
        features['soft_phoneme_count'] = sum(c in self.soft_phonemes for c in label_lower)
        
        # Phonetic ratios
        total_phonemes = max(sum(c.isalpha() for c in label_lower), 1)
        features['power_phoneme_ratio'] = features['power_phoneme_count'] / total_phonemes
        features['speed_phoneme_ratio'] = features['speed_phoneme_count'] / total_phonemes
        features['soft_phoneme_ratio'] = features['soft_phoneme_count'] / total_phonemes
        
        # Phonetic balance
        features['plosive_to_fricative_ratio'] = (features['plosive_count'] / 
                                                  max(features['fricative_count'], 1))
        
        # Consonant/vowel balance
        consonant_count = total_phonemes - sum(c in 'aeiou' for c in label_lower)
        features['consonant_to_vowel_ratio'] = consonant_count / max(features.get('vowel_ratio', 0.4) * total_phonemes, 1)
        
        # Initial/final consonant strength
        features['initial_consonant_strength'] = self._initial_strength(label_lower)
        features['final_consonant_strength'] = self._final_strength(label_lower)
        
        # Sonority (melodic vs harsh)
        features['sonority_score'] = self._calculate_sonority(label_lower)
        
        # Harmony scores
        features['consonant_harmony'] = self._consonant_harmony(label_lower)
        features['vowel_harmony'] = self._vowel_harmony(label_lower)
        
        return features
    
    def _extract_semantic_features(self, label: str, label_lower: str, label_type: str) -> Dict:
        """Extract semantic/meaning-based features"""
        features = {}
        
        # Word count
        words = label.split()
        features['word_count'] = len(words)
        
        # Has numbers
        features['contains_numbers'] = 1 if any(c.isdigit() for c in label) else 0
        
        # All caps words (like acronyms)
        features['has_acronym'] = 1 if any(w.isupper() and len(w) > 1 for w in words) else 0
        
        # Compound nature (multi-word)
        features['is_compound'] = 1 if len(words) > 1 else 0
        
        # Prestige indicators (for venues, awards, etc.)
        prestige_words = {'field', 'stadium', 'arena', 'palace', 'center', 'garden', 
                         'championship', 'cup', 'trophy', 'award', 'bowl'}
        features['prestige_indicator'] = 1 if any(w.lower() in prestige_words for w in words) else 0
        
        # Power/aggression indicators (for teams, plays)
        power_words = {'killer', 'crusher', 'thunder', 'lightning', 'storm', 'blitz',
                      'raiders', 'warriors', 'chiefs', 'steelers', 'ravens', 'bears',
                      'tigers', 'lions', 'eagles', 'hawks', 'power', 'bomb', 'smash'}
        features['power_semantic'] = 1 if any(w.lower() in power_words for w in words) else 0
        
        # Speed indicators
        speed_words = {'jet', 'rocket', 'flash', 'quick', 'rapid', 'fast', 'sweep', 
                      'sprint', 'dash'}
        features['speed_semantic'] = 1 if any(w.lower() in speed_words for w in words) else 0
        
        # Geographic indicators (for teams/venues)
        features['has_geographic'] = 1 if self._has_geographic_term(words) else 0
        
        # Color/visual descriptors
        color_words = {'red', 'blue', 'green', 'gold', 'silver', 'black', 'white', 
                      'purple', 'orange', 'yellow', 'brown', 'pink'}
        features['has_color'] = 1 if any(w.lower() in color_words for w in words) else 0
        
        # Animalistic (teams often use animals)
        animal_words = {'bears', 'lions', 'tigers', 'eagles', 'hawks', 'ravens', 
                       'falcons', 'dolphins', 'rams', 'panthers', 'jaguars', 'broncos',
                       'colts', 'wolves', 'coyotes', 'sharks'}
        features['is_animal'] = 1 if any(w.lower() in animal_words for w in words) else 0
        
        return features
    
    def _extract_label_specific_features(self, label: str, label_lower: str,
                                        label_type: str, context: Optional[Dict]) -> Dict:
        """Extract features specific to label type"""
        features = {}
        
        if label_type == 'team':
            features.update(self._team_specific_features(label, label_lower))
        elif label_type == 'venue':
            features.update(self._venue_specific_features(label, label_lower))
        elif label_type == 'play':
            features.update(self._play_specific_features(label, label_lower))
        elif label_type == 'prop':
            features.update(self._prop_specific_features(label, label_lower))
        elif label_type == 'genre':
            features.update(self._genre_specific_features(label, label_lower))
        elif label_type == 'instrument':
            features.update(self._instrument_specific_features(label, label_lower))
        else:
            # Generic label features
            features['label_specificity'] = 50  # Default
        
        return features
    
    def _team_specific_features(self, label: str, label_lower: str) -> Dict:
        """Features specific to team names"""
        return {
            'team_aggression_score': self._calculate_team_aggression(label_lower),
            'team_tradition_score': self._calculate_team_tradition(label_lower),
            'team_geographic_strength': self._geographic_prominence(label),
        }
    
    def _venue_specific_features(self, label: str, label_lower: str) -> Dict:
        """Features specific to venue names"""
        return {
            'venue_prestige': self._calculate_venue_prestige(label_lower),
            'venue_intimidation': self._calculate_venue_intimidation(label_lower),
            'venue_memorability': self._calculate_memorability(label_lower),
        }
    
    def _play_specific_features(self, label: str, label_lower: str) -> Dict:
        """Features specific to play/formation names"""
        return {
            'play_complexity': len(label.split()),  # Complex plays have longer names
            'play_power_indicator': 1 if any(w in label_lower for w in ['power', 'iso', 'smash', 'blast']) else 0,
            'play_speed_indicator': 1 if any(w in label_lower for w in ['jet', 'sweep', 'quick', 'fast']) else 0,
            'play_trick_indicator': 1 if any(w in label_lower for w in ['spider', 'flea', 'hook', 'lateral']) else 0,
        }
    
    def _prop_specific_features(self, label: str, label_lower: str) -> Dict:
        """Features specific to prop type names"""
        return {
            'prop_action_intensity': self._calculate_action_intensity(label_lower),
            'prop_precision_demand': self._calculate_precision_demand(label_lower),
        }
    
    def _genre_specific_features(self, label: str, label_lower: str) -> Dict:
        """Features specific to genre names"""
        return {
            'genre_intensity': self._calculate_genre_intensity(label_lower),
            'genre_complexity': len(label_lower),  # Proxy for sophistication
        }
    
    def _instrument_specific_features(self, label: str, label_lower: str) -> Dict:
        """Features specific to instrument names"""
        return {
            'instrument_harshness': self._calculate_harshness(label_lower),
            'instrument_complexity': self._calculate_memorability(label_lower),
        }
    
    # === HELPER CALCULATION METHODS ===
    
    def _count_syllables(self, text: str) -> int:
        """Approximate syllable count"""
        text = text.lower().replace(' ', '')
        vowels = 'aeiou'
        count = 0
        previous_was_vowel = False
        
        for char in text:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                count += 1
            previous_was_vowel = is_vowel
        
        # Adjust for silent e
        if text.endswith('e'):
            count -= 1
        
        return max(count, 1)
    
    def _calculate_harshness(self, text: str) -> float:
        """Calculate harshness score (0-100)"""
        if not text:
            return 50
            
        letter_count = sum(c.isalpha() for c in text)
        if letter_count == 0:
            return 50
            
        harsh_consonants = 'ktbgdp'
        harsh_count = sum(c in harsh_consonants for c in text)
        
        # Additional harshness from consonant clusters
        cluster_bonus = self._count_consonant_clusters(text) * 5
        
        harshness = (harsh_count / letter_count) * 80 + cluster_bonus
        
        return min(harshness, 100)
    
    def _calculate_memorability(self, text: str) -> float:
        """Calculate memorability score (0-100)"""
        if not text:
            return 50
            
        score = 50  # Base
        
        # Short names more memorable
        length = len(text.replace(' ', ''))
        if length <= 5:
            score += 20
        elif length <= 8:
            score += 10
        elif length > 15:
            score -= 15
        
        # Repetition increases memorability
        if len(set(text.lower())) < len(text) * 0.6:
            score += 10
        
        # Alliteration
        words = text.split()
        if len(words) > 1:
            first_letters = [w[0].lower() for w in words if w]
            if len(first_letters) != len(set(first_letters)):
                score += 15  # Alliteration bonus
        
        # Rhythmic (even syllables)
        syllables = self._count_syllables(text)
        if syllables % 2 == 0:
            score += 5
        
        return min(max(score, 0), 100)
    
    def _calculate_pronounceability(self, text: str) -> float:
        """Calculate pronounceability (0-100)"""
        if not text:
            return 50
            
        score = 100
        
        # Penalize consonant clusters
        clusters = self._count_consonant_clusters(text)
        score -= clusters * 10
        
        # Penalize very long words
        words = text.split()
        for word in words:
            if len(word) > 12:
                score -= 15
        
        # Reward good vowel distribution
        vowel_ratio = sum(c in 'aeiou' for c in text) / max(len(text), 1)
        if 0.3 <= vowel_ratio <= 0.5:
            score += 10
        
        return min(max(score, 0), 100)
    
    def _calculate_uniqueness(self, text: str) -> float:
        """Calculate uniqueness score (0-100)"""
        if not text:
            return 50
            
        # Unique letters ratio
        unique_ratio = len(set(text.lower())) / max(len(text), 1)
        
        # Uncommon letters bonus
        uncommon = 'qxzjkw'
        uncommon_count = sum(c in uncommon for c in text.lower())
        
        uniqueness = (unique_ratio * 60) + (uncommon_count * 10)
        
        return min(uniqueness, 100)
    
    def _count_consonant_clusters(self, text: str) -> int:
        """Count consonant clusters (2+ consonants together)"""
        vowels = set('aeiou')
        clusters = 0
        in_cluster = False
        cluster_length = 0
        
        for char in text.lower():
            if char.isalpha():
                if char not in vowels:
                    cluster_length += 1
                    if cluster_length >= 2:
                        if not in_cluster:
                            clusters += 1
                            in_cluster = True
                else:
                    in_cluster = False
                    cluster_length = 0
        
        return clusters
    
    def _initial_strength(self, text: str) -> float:
        """Strength of initial consonant (0-100)"""
        first_char = next((c for c in text if c.isalpha()), '')
        if first_char in self.plosives:
            return 85
        elif first_char in self.fricatives:
            return 70
        elif first_char in 'aeiou':
            return 40
        else:
            return 55
    
    def _final_strength(self, text: str) -> float:
        """Strength of final consonant (0-100)"""
        last_char = next((c for c in reversed(text) if c.isalpha()), '')
        if last_char in self.plosives:
            return 85
        elif last_char in self.fricatives:
            return 70
        elif last_char in 'aeiou':
            return 40
        else:
            return 55
    
    def _calculate_sonority(self, text: str) -> float:
        """Calculate sonority (melodic vs harsh) (0-100)"""
        sonorants = sum(c in 'mnlrwy' for c in text)
        obstruents = sum(c in 'ptkbdgfvsz' for c in text)
        
        total = sonorants + obstruents
        if total == 0:
            return 50
            
        # Higher = more harsh/obstruent, Lower = more melodic/sonorant
        return (obstruents / total) * 100
    
    def _consonant_harmony(self, text: str) -> float:
        """Consonant harmony score (0-100)"""
        plosives = sum(c in self.plosives for c in text)
        fricatives = sum(c in self.fricatives for c in text)
        
        if plosives > fricatives * 2:
            return 75  # Plosive-harmonic
        elif fricatives > plosives * 2:
            return 65  # Fricative-harmonic
        else:
            return 50  # Mixed
    
    def _vowel_harmony(self, text: str) -> float:
        """Vowel harmony score (0-100)"""
        front = sum(c in self.front_vowels for c in text)
        back = sum(c in self.back_vowels for c in text)
        
        if front > back * 2 or back > front * 2:
            return 70  # Harmonic
        else:
            return 50  # Neutral
    
    def _has_geographic_term(self, words: List[str]) -> bool:
        """Check if contains geographic terms"""
        geographic = {'city', 'bay', 'new', 'san', 'los', 'st', 'saint', 'lake',
                     'golden', 'atlantic', 'pacific', 'north', 'south', 'east', 'west'}
        return any(w.lower() in geographic for w in words)
    
    def _calculate_team_aggression(self, text: str) -> float:
        """Calculate team aggression score (0-100)"""
        aggressive_terms = ['killer', 'crusher', 'thunder', 'lightning', 'raiders',
                           'warriors', 'chiefs', 'steelers', 'ravens', 'bears', 'tigers']
        
        score = 50
        for term in aggressive_terms:
            if term in text:
                score += 20
                break
        
        # Add harshness component
        score += (self._calculate_harshness(text) - 50) * 0.5
        
        return min(score, 100)
    
    def _calculate_team_tradition(self, text: str) -> float:
        """Calculate team tradition score (0-100)"""
        traditional_terms = ['green', 'bay', 'red', 'sox', 'yankees', 'dodgers',
                            'celtics', 'lakers', 'bruins', 'original']
        
        score = 50
        for term in traditional_terms:
            if term in text:
                score += 15
                break
        
        return min(score, 100)
    
    def _geographic_prominence(self, text: str) -> float:
        """Calculate geographic prominence (0-100)"""
        major_cities = ['new york', 'los angeles', 'chicago', 'boston', 'san francisco',
                       'philadelphia', 'dallas', 'miami', 'atlanta', 'washington']
        
        text_lower = text.lower()
        for city in major_cities:
            if city in text_lower:
                return 90
        
        return 50
    
    def _calculate_venue_prestige(self, text: str) -> float:
        """Calculate venue prestige (0-100)"""
        prestige_terms = ['field', 'stadium', 'arena', 'center', 'garden', 'park',
                         'bowl', 'coliseum', 'palace']
        
        score = 50
        for term in prestige_terms:
            if term in text:
                score += 10
        
        # Named after people/legends increases prestige
        if any(c.isupper() for c in text[1:]):  # Multiple capital letters
            score += 15
        
        return min(score, 100)
    
    def _calculate_venue_intimidation(self, text: str) -> float:
        """Calculate venue intimidation factor (0-100)"""
        intimidating = ['arrowhead', 'death valley', 'pit', 'swamp', 'steel']
        
        score = self._calculate_harshness(text)  # Base on harshness
        
        for term in intimidating:
            if term in text.lower():
                score += 20
                break
        
        return min(score, 100)
    
    def _calculate_action_intensity(self, text: str) -> float:
        """Calculate action intensity for prop types (0-100)"""
        high_intensity = ['tackles', 'sacks', 'blocks', 'strikeouts', 'hits', 'dunks']
        low_intensity = ['assists', 'passes', 'catches']
        
        text_lower = text.lower()
        
        if any(term in text_lower for term in high_intensity):
            return 80
        elif any(term in text_lower for term in low_intensity):
            return 40
        else:
            return 60
    
    def _calculate_precision_demand(self, text: str) -> float:
        """Calculate precision demand for prop types (0-100)"""
        high_precision = ['passing', 'field goal', 'three point', 'accuracy', 'percentage']
        low_precision = ['rushing', 'tackles', 'rebounds']
        
        text_lower = text.lower()
        
        if any(term in text_lower for term in high_precision):
            return 85
        elif any(term in text_lower for term in low_precision):
            return 40
        else:
            return 60
    
    def _calculate_genre_intensity(self, text: str) -> float:
        """Calculate genre intensity (0-100)"""
        intense_genres = ['metal', 'punk', 'hardcore', 'death', 'black', 'thrash',
                         'horror', 'thriller', 'action']
        mellow_genres = ['ambient', 'folk', 'jazz', 'classical', 'romance']
        
        if any(g in text for g in intense_genres):
            return 85
        elif any(g in text for g in mellow_genres):
            return 30
        else:
            return 60
    
    def _get_empty_features(self) -> Dict:
        """Return empty/default features"""
        return {
            'syllables': 2,
            'length': 5,
            'harshness': 50,
            'memorability': 50,
            'pronounceability': 50,
            'uniqueness': 50,
            'vowel_ratio': 0.4,
            'label': '',
            'label_type': 'unknown'
        }
    
    def extract_multiple_labels(self, labels: List[str], label_type: str,
                               context: Optional[Dict] = None) -> List[Dict]:
        """
        Extract features from multiple labels
        
        Args:
            labels: List of label strings
            label_type: Type of labels
            context: Optional context
            
        Returns:
            List of feature dictionaries
        """
        return [self.extract_label_features(label, label_type, context) 
                for label in labels]


if __name__ == "__main__":
    # Test the extractor
    extractor = LabelNominativeExtractor()
    
    print("="*80)
    print("LABEL NOMINATIVE EXTRACTOR - Test Run")
    print("="*80)
    
    # Test various label types
    test_labels = [
        ("Kansas City Chiefs", "team"),
        ("Lambeau Field", "venue"),
        ("Spider 2 Y Banana", "play"),
        ("Rushing yards", "prop"),
        ("Death Metal", "genre"),
        ("Drums", "instrument"),
    ]
    
    for label, label_type in test_labels:
        print(f"\n{'='*80}")
        print(f"Label: {label} (Type: {label_type})")
        print(f"{'='*80}")
        
        features = extractor.extract_label_features(label, label_type)
        
        print(f"  Syllables: {features['syllables']}")
        print(f"  Length: {features['length']}")
        print(f"  Harshness: {features['harshness']:.1f}")
        print(f"  Memorability: {features['memorability']:.1f}")
        print(f"  Pronounceability: {features['pronounceability']:.1f}")
        print(f"  Power Phonemes: {features['power_phoneme_count']}")
        print(f"  Speed Phonemes: {features['speed_phoneme_count']}")
        
        # Type-specific features
        if 'team_aggression_score' in features:
            print(f"  Team Aggression: {features['team_aggression_score']:.1f}")
        if 'venue_intimidation' in features:
            print(f"  Venue Intimidation: {features['venue_intimidation']:.1f}")
        if 'play_complexity' in features:
            print(f"  Play Complexity: {features['play_complexity']}")
    
    print(f"\n{'='*80}")
    print("EXTRACTION COMPLETE")
    print("="*80)

