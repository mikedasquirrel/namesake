"""
Narrative Feature Extraction
Extracts universal and context-specific story elements from entity names

Based on Narrative Advantage Framework:
- Universal features apply to all domains
- Context-specific features vary by domain
- Features capture signaling, selection, and recursion components
"""

import re
from typing import Dict, List, Any, Optional
import numpy as np


class NarrativeFeatureExtractor:
    """
    Extract narrative features (story elements) from names
    Combines universal phonetic features with context-specific variables
    """
    
    def __init__(self):
        """Initialize feature extractor with reference data"""
        self._init_phonetic_data()
        self._init_context_data()
    
    def _init_phonetic_data(self):
        """Initialize phonetic analysis tools"""
        self.harsh_consonants = set('kgptbdxz')
        self.vowels = set('aeiouy')
        
        # Common name lists (abbreviated - would load from file in production)
        self.common_names = {'john', 'mary', 'james', 'patricia', 'michael', 'jennifer'}
    
    def _init_context_data(self):
        """Initialize context-specific reference data"""
        # Technical morphemes for crypto
        self.tech_morphemes = ['bit', 'byte', 'crypto', 'coin', 'chain', 'block', 'digi', 'cyber']
        
        # Genre words for bands
        self.metal_words = ['death', 'metal', 'iron', 'black', 'dark', 'blood']
        self.folk_words = ['fleet', 'fleet', 'willow', 'mountain', 'river', 'wind']
        
        # Position words for sports
        self.power_words = ['tank', 'rock', 'steel', 'iron', 'bull', 'beast']
        self.speed_words = ['flash', 'lightning', 'swift', 'rocket', 'jet']
    
    # =============================================================================
    # UNIVERSAL FEATURES (All Domains)
    # =============================================================================
    
    def extract_universal_features(self, name: str) -> Dict[str, Any]:
        """
        Extract features that apply across all domains
        
        These are baseline narrative elements:
        - Phonetic properties
        - Length/complexity
        - Memorability
        """
        return {
            'length': len(name),
            'syllables': self.count_syllables(name),
            'harsh_consonants': self.count_harsh_consonants(name),
            'has_harsh_sounds': self.has_harsh_sounds(name),
            'vowel_ratio': self.calculate_vowel_ratio(name),
            'memorability': self.calculate_memorability(name),
            'complexity': self.calculate_complexity(name),
            'uniqueness': self.estimate_uniqueness(name)
        }
    
    def count_syllables(self, word: str) -> int:
        """
        Count syllables (simple heuristic)
        
        For production, use pyphen library:
        import pyphen
        dic = pyphen.Pyphen(lang='en')
        return len(dic.inserted(word).split('-'))
        """
        word = word.lower()
        count = 0
        vowel = False
        
        for char in word:
            if char in self.vowels:
                if not vowel:
                    count += 1
                    vowel = True
            else:
                vowel = False
        
        return max(1, count)
    
    def count_harsh_consonants(self, word: str) -> int:
        """Count harsh consonants (k, g, p, t, b, d, x, z)"""
        return sum(1 for char in word.lower() if char in self.harsh_consonants)
    
    def has_harsh_sounds(self, word: str) -> bool:
        """Binary: contains harsh consonants?"""
        return any(char in word.lower() for char in self.harsh_consonants)
    
    def calculate_vowel_ratio(self, word: str) -> float:
        """Ratio of vowels to total letters"""
        if not word:
            return 0.0
        vowel_count = sum(1 for char in word.lower() if char in self.vowels)
        return vowel_count / len(word)
    
    def calculate_memorability(self, word: str) -> float:
        """
        Memorability score (0-1)
        Shorter + fewer syllables = more memorable
        """
        length_score = max(0, 1 - (len(word) - 3) / 10)
        syllable_score = max(0, 1 - (self.count_syllables(word) - 1) / 5)
        return (length_score + syllable_score) / 2
    
    def calculate_complexity(self, word: str) -> float:
        """
        Complexity score (0-1)
        Based on length, syllables, and rare letters
        """
        length_complexity = min(1.0, len(word) / 15)
        syllable_complexity = min(1.0, self.count_syllables(word) / 5)
        
        # Rare letters (q, x, z, etc)
        rare_letters = set('qxzjkv')
        rare_count = sum(1 for char in word.lower() if char in rare_letters)
        rare_complexity = min(1.0, rare_count / 3)
        
        return (length_complexity + syllable_complexity + rare_complexity) / 3
    
    def estimate_uniqueness(self, word: str) -> float:
        """
        Uniqueness score (0-1)
        Higher = more unique/distinctive
        """
        # Check against common names (simplified)
        if word.lower() in self.common_names:
            return 0.2
        
        # Length as proxy for uniqueness
        if len(word) < 4:
            return 0.4
        elif len(word) > 10:
            return 0.9
        else:
            return 0.6
    
    # =============================================================================
    # HURRICANES: Danger Narrative Variables
    # =============================================================================
    
    def extract_hurricane_features(self, name: str, **context) -> Dict[str, Any]:
        """
        Extract hurricane-specific narrative features
        
        Context params:
        - historical_deaths: int (deaths from previous storm with same name)
        - year: int (for checking reuse)
        """
        features = {
            'name_familiarity': self.calculate_name_familiarity(name),
            'gender_association': self.classify_gender(name),
            'pronunciation_ease': self.calculate_pronunciation_ease(name),
            'historical_context': context.get('historical_deaths', 0) > 0,
            'previous_deaths': context.get('historical_deaths', 0)
        }
        
        # Danger amplifiers
        features['danger_score'] = self.calculate_danger_score(name, features)
        
        return features
    
    def calculate_name_familiarity(self, name: str) -> float:
        """
        How familiar is this as a person name? (0-1)
        In production, lookup SSA name frequency
        """
        if name.lower() in self.common_names:
            return 1.0
        elif len(name) < 4:
            return 0.3
        else:
            return 0.5
    
    def classify_gender(self, name: str) -> str:
        """
        Classify name gender (Male/Female/Neutral)
        In production, use gender-guesser library or SSA data
        """
        # Simplified heuristic
        male_endings = ['o', 'n', 'r', 'd', 'k']
        female_endings = ['a', 'e', 'y', 'ia', 'ina']
        
        name_lower = name.lower()
        
        if any(name_lower.endswith(ending) for ending in female_endings):
            return 'Female'
        elif any(name_lower.endswith(ending) for ending in male_endings):
            return 'Male'
        else:
            return 'Neutral'
    
    def calculate_pronunciation_ease(self, name: str) -> float:
        """
        How easy to pronounce? (0-1, higher = easier)
        Based on phonotactic probability
        """
        # Simplified: short + common letters = easy
        if len(name) <= 4:
            return 0.9
        elif len(name) <= 7:
            return 0.7
        else:
            return 0.5
    
    def calculate_danger_score(self, name: str, features: Dict) -> float:
        """
        Combined danger narrative score
        Harsh sounds + historical context + gender bias
        """
        score = 0.0
        
        # Harsh sounds amplify danger
        if features.get('harsh_consonants', 0) > 0:
            score += 0.3
        
        # Historical deaths amplify
        if features.get('previous_deaths', 0) > 100:
            score += 0.4
        
        # Familiarity makes it feel "real"
        score += features.get('name_familiarity', 0) * 0.3
        
        return min(1.0, score)
    
    # =============================================================================
    # CRYPTOCURRENCIES: Technology Sophistication Signals
    # =============================================================================
    
    def extract_crypto_features(self, name: str, **context) -> Dict[str, Any]:
        """
        Extract crypto-specific narrative features
        
        Context params:
        - whitepaper_text: str (for coherence analysis)
        - launch_date: datetime
        """
        features = {
            'technical_morpheme_count': self.count_technical_morphemes(name),
            'seriousness_classification': self.classify_seriousness(name),
            'ecosystem_reference': self.detect_ecosystem_reference(name),
            'pronounceability': self.calculate_pronounceability(name),
            'real_word_vs_invented': self.classify_word_type(name)
        }
        
        # Technology sophistication score
        features['tech_sophistication'] = self.calculate_tech_sophistication(name, features)
        
        return features
    
    def count_technical_morphemes(self, name: str) -> int:
        """Count presence of technical morphemes"""
        name_lower = name.lower()
        return sum(1 for morpheme in self.tech_morphemes if morpheme in name_lower)
    
    def classify_seriousness(self, name: str) -> str:
        """Classify as Serious/Mixed/Joke"""
        humor_words = ['doge', 'meme', 'joke', 'fun', 'lol', 'moon', 'safe']
        
        name_lower = name.lower()
        if any(word in name_lower for word in humor_words):
            return 'Joke'
        elif self.count_technical_morphemes(name) >= 2:
            return 'Serious'
        else:
            return 'Mixed'
    
    def detect_ecosystem_reference(self, name: str) -> Optional[str]:
        """Detect reference to major ecosystem"""
        name_lower = name.lower()
        
        if 'bitcoin' in name_lower or 'btc' in name_lower:
            return 'Bitcoin'
        elif 'ether' in name_lower or 'eth' in name_lower:
            return 'Ethereum'
        elif 'doge' in name_lower:
            return 'Dogecoin'
        else:
            return None
    
    def calculate_pronounceability(self, name: str) -> float:
        """
        How easy to pronounce? (0-1)
        Based on consonant clusters and length
        """
        # Check for difficult consonant clusters
        difficult_clusters = ['tch', 'dge', 'ght', 'sch', 'phr']
        has_difficult = any(cluster in name.lower() for cluster in difficult_clusters)
        
        if has_difficult:
            return 0.4
        elif len(name) <= 6:
            return 0.9
        elif len(name) <= 10:
            return 0.7
        else:
            return 0.5
    
    def classify_word_type(self, name: str) -> str:
        """Real word, Hybrid, or Invented"""
        # Simplified - in production, use dictionary API
        common_words = ['stellar', 'civic', 'storm', 'coin', 'chain']
        
        if name.lower() in common_words:
            return 'Real'
        elif any(morph in name.lower() for morph in self.tech_morphemes):
            return 'Hybrid'
        else:
            return 'Invented'
    
    def calculate_tech_sophistication(self, name: str, features: Dict) -> float:
        """
        Combined technology sophistication score
        """
        score = 0.0
        
        # Technical morphemes boost sophistication
        score += features['technical_morpheme_count'] * 0.2
        
        # Serious framing boosts
        if features['seriousness_classification'] == 'Serious':
            score += 0.3
        elif features['seriousness_classification'] == 'Joke':
            score -= 0.3
        
        # Ecosystem reference boosts
        if features['ecosystem_reference']:
            score += 0.2
        
        return max(0.0, min(1.0, score))
    
    # =============================================================================
    # SPORTS: Persona Construction Variables
    # =============================================================================
    
    def extract_sports_features(self, name: str, position: str = None, **context) -> Dict[str, Any]:
        """
        Extract sports-specific narrative features
        
        Params:
        - position: str (QB, RB, WR, etc for NFL; PG, SG, SF, PF, C for NBA)
        - sport: str (nba, nfl, mlb)
        """
        sport = context.get('sport', 'nba')
        
        features = {
            'position': position,
            'sport': sport,
            'position_congruence': self.calculate_position_congruence(name, position, sport),
            'nickname_potential': self.calculate_nickname_potential(name),
            'marketability': self.calculate_marketability(name),
            'cultural_heritage_signal': self.estimate_heritage_strength(name)
        }
        
        # Persona score
        features['persona_strength'] = self.calculate_persona_strength(name, features)
        
        return features
    
    def calculate_position_congruence(self, name: str, position: Optional[str], sport: str) -> float:
        """
        How well does name fit position archetype? (0-1)
        """
        if not position:
            return 0.5
        
        name_lower = name.lower()
        
        # NFL position archetypes
        if sport == 'nfl':
            if position in ['DT', 'DE', 'LB']:  # Contact positions
                has_power = any(word in name_lower for word in self.power_words)
                is_harsh = self.has_harsh_sounds(name)
                return 0.8 if (has_power or is_harsh) else 0.4
            
            elif position in ['WR', 'CB', 'RB']:  # Speed positions
                has_speed = any(word in name_lower for word in self.speed_words)
                is_short = len(name) <= 5
                return 0.8 if (has_speed or is_short) else 0.5
        
        # NBA position archetypes
        elif sport == 'nba':
            if position == 'C':  # Centers
                is_strong = self.has_harsh_sounds(name) or len(name) >= 7
                return 0.7 if is_strong else 0.4
            elif position in ['PG', 'SG']:  # Guards
                is_quick = len(name) <= 6
                return 0.7 if is_quick else 0.5
        
        return 0.5  # Neutral if unclear
    
    def calculate_nickname_potential(self, name: str) -> float:
        """
        How good is this name for generating nicknames? (0-1)
        """
        # Short names get easy nicknames
        if len(name) <= 4:
            return 0.8
        
        # Names with clear syllable breaks
        if self.count_syllables(name) >= 2:
            return 0.7
        
        # Unique names are memorable
        if self.estimate_uniqueness(name) > 0.7:
            return 0.6
        
        return 0.4
    
    def calculate_marketability(self, name: str) -> float:
        """
        Combined marketability score (0-1)
        Memorability + uniqueness + pronounceability
        """
        memo = self.calculate_memorability(name)
        unique = self.estimate_uniqueness(name)
        pronounce = self.calculate_pronunciation_ease(name)
        
        return (memo + unique + pronounce) / 3
    
    def estimate_heritage_strength(self, name: str) -> float:
        """
        How strongly does name signal cultural heritage? (0-1)
        In production, use name origin databases
        """
        # Simplified: longer/complex names suggest strong heritage
        if len(name) > 12:
            return 0.9
        elif len(name) > 8:
            return 0.7
        else:
            return 0.4
    
    def calculate_persona_strength(self, name: str, features: Dict) -> float:
        """
        Combined persona narrative strength
        """
        score = 0.0
        
        # Position fit matters
        score += features.get('position_congruence', 0.5) * 0.4
        
        # Marketability matters
        score += features.get('marketability', 0.5) * 0.3
        
        # Nickname potential
        score += features.get('nickname_potential', 0.5) * 0.3
        
        return min(1.0, score)
    
    # =============================================================================
    # META-LEVEL: Complete Extraction
    # =============================================================================
    
    def extract_all_features(self, name: str, domain: str, **context) -> Dict[str, Any]:
        """
        Extract complete feature set for any domain
        
        Params:
        - name: str (entity name)
        - domain: str (hurricanes, crypto, nba, nfl, etc)
        - **context: domain-specific parameters
        
        Returns:
        - Dict with universal + domain-specific features
        """
        # Start with universal features
        features = {
            'name': name,
            'domain': domain,
            **self.extract_universal_features(name)
        }
        
        # Add domain-specific features
        if domain == 'hurricanes':
            features.update(self.extract_hurricane_features(name, **context))
        
        elif domain == 'crypto':
            features.update(self.extract_crypto_features(name, **context))
        
        elif domain in ['nba', 'nfl', 'mlb']:
            features.update(self.extract_sports_features(name, **context))
        
        # Calculate composite scores
        features['genre_congruence'] = self._calculate_genre_congruence(features, domain)
        features['story_coherence'] = self._calculate_story_coherence(features, domain)
        
        return features
    
    def _calculate_genre_congruence(self, features: Dict, domain: str) -> float:
        """
        How well do features fit domain expectations?
        """
        if domain == 'hurricanes':
            # Harsh sounds appropriate for danger context
            harsh_score = features.get('harsh_consonants', 0) / 3
            return min(1.0, harsh_score)
        
        elif domain == 'crypto':
            # Technical sophistication appropriate
            return features.get('tech_sophistication', 0.5)
        
        elif domain in ['nba', 'nfl']:
            # Position congruence
            return features.get('position_congruence', 0.5)
        
        else:
            return 0.5  # Neutral for unmapped domains
    
    def _calculate_story_coherence(self, features: Dict, domain: str) -> float:
        """
        Do all story elements align coherently?
        """
        # Coherence = genre fit + complexity match + context appropriateness
        genre = features.get('genre_congruence', 0.5)
        complexity = features.get('complexity', 0.5)
        
        # Simple heuristic: high genre fit + appropriate complexity
        if domain in ['hurricanes', 'crypto']:
            # Simple names work well
            simple_bonus = 1.0 - complexity
            return (genre + simple_bonus) / 2
        else:
            return genre


# =============================================================================
# Convenience Functions
# =============================================================================

def extract_narrative_features(name: str, domain: str, **context) -> Dict[str, Any]:
    """
    Convenience function for extracting narrative features
    
    Usage:
        features = extract_narrative_features('Katrina', 'hurricanes', historical_deaths=1833)
        features = extract_narrative_features('Bitcoin', 'crypto')
        features = extract_narrative_features('LeBron', 'nba', position='SF')
    """
    extractor = NarrativeFeatureExtractor()
    return extractor.extract_all_features(name, domain, **context)


def batch_extract_features(entities: List[Dict], domain: str) -> List[Dict]:
    """
    Extract features for multiple entities
    
    Params:
    - entities: List of dicts with 'name' key and optional context keys
    - domain: str
    
    Returns:
    - List of feature dicts
    """
    extractor = NarrativeFeatureExtractor()
    results = []
    
    for entity in entities:
        name = entity['name']
        context = {k: v for k, v in entity.items() if k != 'name'}
        features = extractor.extract_all_features(name, domain, **context)
        results.append(features)
    
    return results

