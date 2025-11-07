import re
import json
from collections import Counter
import pyphen
import Levenshtein
from core.config import Config
import logging

# Import new standardized phonetic analysis
from analyzers.phonetic_base import get_analyzer as get_phonetic_analyzer
from analyzers.phonetic_composites import get_composite_analyzer

logger = logging.getLogger(__name__)


class NameAnalyzer:
    """Comprehensive linguistic and phonetic analysis of cryptocurrency names"""
    
    def __init__(self):
        self.pyphen_dic = pyphen.Pyphen(lang='en_US')
        self.vowels = set('aeiouAEIOU')
        self.consonants = set('bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ')
        
        # New standardized analyzers
        self.phonetic_analyzer = get_phonetic_analyzer()
        self.composite_analyzer = get_composite_analyzer()
        
        # Common word lists for categorization
        self.animal_words = {
            'dog', 'cat', 'fox', 'bear', 'lion', 'tiger', 'wolf', 'bird', 'eagle', 
            'hawk', 'shark', 'whale', 'dolphin', 'dragon', 'snake', 'rabbit', 'frog',
            'monkey', 'ape', 'gorilla', 'panda', 'koala', 'ant', 'bee', 'bat', 'rat',
            'mouse', 'shiba', 'inu', 'doge', 'pepe', 'floki'
        }
        
        self.tech_words = {
            'bit', 'byte', 'coin', 'token', 'chain', 'link', 'net', 'web', 'cyber',
            'digital', 'crypto', 'meta', 'data', 'node', 'protocol', 'smart', 'quantum',
            'nano', 'micro', 'tech', 'tron', 'matic', 'algo', 'dot', 'hash', 'block'
        }
        
        self.mythological_words = {
            'zeus', 'thor', 'odin', 'apollo', 'titan', 'olympus', 'atlas', 'phoenix',
            'dragon', 'griffin', 'hydra', 'medusa', 'oracle', 'hermes', 'hera', 'athena'
        }
        
        self.financial_words = {
            'gold', 'silver', 'dollar', 'euro', 'pound', 'cash', 'money', 'bank',
            'pay', 'swap', 'trade', 'exchange', 'finance', 'defi', 'yield', 'stake'
        }
        
        self.astronomical_words = {
            'star', 'moon', 'sun', 'cosmos', 'stellar', 'luna', 'solar', 'orbit',
            'galaxy', 'nebula', 'comet', 'meteor', 'astro', 'space', 'terra'
        }
        
        self.elemental_words = {
            'fire', 'water', 'earth', 'air', 'ice', 'storm', 'thunder', 'lightning',
            'flame', 'ocean', 'wind', 'stone', 'crystal', 'plasma'
        }
    
    def analyze_name(self, name, all_names=None, use_standardized=True):
        """
        Perform comprehensive analysis of a cryptocurrency name
        
        Args:
            name: The cryptocurrency name to analyze
            all_names: List of all cryptocurrency names for similarity comparison
            use_standardized: If True, use new standardized phonetic analysis
            
        Returns:
            Dictionary with all analysis metrics
        """
        if use_standardized:
            # Use new standardized analysis
            return self.analyze_name_standardized(name, all_names)
        
        # Legacy analysis (for backward compatibility)
        analysis = {}
        
        # Basic metrics
        analysis['character_length'] = len(name)
        analysis['word_count'] = len(re.findall(r'\w+', name))
        
        # Syllable analysis
        analysis['syllable_count'] = self._count_syllables(name)
        
        # Phonetic analysis
        analysis['phonetic_score'] = self._calculate_phonetic_score(name)
        analysis['vowel_ratio'] = self._calculate_vowel_ratio(name)
        analysis['consonant_clusters'] = self._count_consonant_clusters(name)
        
        # Memorability
        analysis['memorability_score'] = self._calculate_memorability(name)
        analysis['pronounceability_score'] = self._calculate_pronounceability(name)
        
        # Categorization
        analysis['name_type'], analysis['category_tags'] = self._categorize_name(name)
        
        # Character composition
        analysis['has_numbers'] = bool(re.search(r'\d', name))
        analysis['has_special_chars'] = bool(re.search(r'[^a-zA-Z0-9\s]', name))
        analysis['capital_pattern'] = self._analyze_capitalization(name)
        
        # Semantic analysis
        analysis['is_real_word'] = self._is_real_word(name)
        analysis['semantic_category'] = self._get_semantic_category(name)
        
        # Uniqueness metrics (requires comparison with other names)
        if all_names:
            similarity_metrics = self._calculate_uniqueness(name, all_names)
            analysis.update(similarity_metrics)
        else:
            analysis['uniqueness_score'] = None
            analysis['avg_similarity_distance'] = None
            analysis['closest_match'] = None
            analysis['closest_match_distance'] = None
        
        return analysis
    
    def analyze_name_standardized(self, name, all_names=None):
        """
        NEW: Use standardized phonetic analysis.
        
        This method uses PhoneticBase and PhoneticComposites for consistent
        measurements across all domains.
        """
        # Get standardized phonetic analysis
        composite_analysis = self.composite_analyzer.analyze(name, all_names)
        
        # Add domain-specific metrics (crypto-specific)
        analysis = composite_analysis.copy()
        
        # Categorization (domain-specific)
        analysis['name_type'], analysis['category_tags'] = self._categorize_name(name)
        
        # Character composition
        analysis['has_numbers'] = bool(re.search(r'\d', name))
        analysis['has_special_chars'] = bool(re.search(r'[^a-zA-Z0-9\s]', name))
        analysis['capital_pattern'] = self._analyze_capitalization(name)
        
        # Semantic analysis
        analysis['is_real_word'] = self._is_real_word(name)
        analysis['semantic_category'] = self._get_semantic_category(name)
        analysis['word_count'] = len(re.findall(r'\w+', name))
        
        # Crypto-specific scores
        analysis['tech_credibility_score'] = self._calculate_tech_credibility(analysis)
        analysis['meme_potential_score'] = self._calculate_meme_potential(analysis)
        
        return analysis
    
    def _calculate_tech_credibility(self, analysis):
        """
        Crypto-specific: Calculate tech credibility score.
        
        Formula: blend of syllables + uniqueness - memorability
        (Tech names should sound sophisticated, not overly memorable)
        """
        syllable_component = (3 - min(analysis['syllable_count'], 3)) * 20  # Prefer 2-3 syllables
        uniqueness_component = analysis.get('uniqueness_score', 50) * 0.4
        memorability_penalty = analysis['memorability_score'] * 0.2  # High memorability = less tech credibility
        euphony_component = analysis['euphony_score'] * 0.3
        
        score = syllable_component + uniqueness_component + euphony_component - memorability_penalty
        return max(0.0, min(100.0, score))
    
    def _calculate_meme_potential(self, analysis):
        """
        Crypto-specific: Calculate meme potential score.
        
        Formula: animal tags × memorability × brevity
        """
        # Check for animal/meme words
        is_animal = 'animal' in analysis.get('category_tags', [])
        animal_bonus = 40 if is_animal else 0
        
        memorability_component = analysis['memorability_score'] * 0.4
        brevity_component = (100 - min(analysis['character_length'] * 10, 100)) * 0.3
        
        score = animal_bonus + memorability_component + brevity_component
        return max(0.0, min(100.0, score))
    
    def _count_syllables(self, word):
        """Count syllables in a word using pyphen"""
        clean_word = re.sub(r'[^a-zA-Z]', '', word)
        if not clean_word:
            return 1
        
        hyphenated = self.pyphen_dic.inserted(clean_word.lower())
        syllables = len(hyphenated.split('-'))
        
        # Fallback: basic vowel counting if pyphen fails
        if syllables == 0:
            syllables = max(1, len(re.findall(r'[aeiou]+', clean_word.lower())))
        
        return syllables
    
    def _calculate_vowel_ratio(self, name):
        """Calculate ratio of vowels to total letters"""
        letters = re.sub(r'[^a-zA-Z]', '', name)
        if not letters:
            return 0.0
        
        vowel_count = sum(1 for c in letters if c in self.vowels)
        return vowel_count / len(letters)
    
    def _count_consonant_clusters(self, name):
        """Count consonant clusters (sequences of 2+ consonants)"""
        clean_name = re.sub(r'[^a-zA-Z]', '', name.lower())
        clusters = re.findall(r'[bcdfghjklmnpqrstvwxyz]{2,}', clean_name)
        return len(clusters)
    
    def _calculate_phonetic_score(self, name):
        """
        Calculate overall phonetic appeal (euphony)
        Based on vowel ratio, consonant clusters, and syllable rhythm
        Score: 0-100
        """
        vowel_ratio = self._calculate_vowel_ratio(name)
        consonant_clusters = self._count_consonant_clusters(name)
        syllables = self._count_syllables(name)
        length = len(re.sub(r'[^a-zA-Z]', '', name))
        
        # Ideal vowel ratio is around 0.4-0.5
        vowel_score = 100 * (1 - abs(0.45 - vowel_ratio) * 2)
        
        # Fewer consonant clusters = more euphonious
        cluster_penalty = min(consonant_clusters * 10, 40)
        
        # Moderate length and syllable count preferred
        if 3 <= length <= 7 and 1 <= syllables <= 3:
            length_bonus = 20
        else:
            length_bonus = 0
        
        score = max(0, min(100, vowel_score - cluster_penalty + length_bonus))
        return round(score, 2)
    
    def _calculate_memorability(self, name):
        """
        Calculate memorability score based on length, uniqueness, and phonetics
        Score: 0-100
        """
        length = len(name)
        syllables = self._count_syllables(name)
        has_numbers = bool(re.search(r'\d', name))
        
        # Optimal length: 4-8 characters
        if 4 <= length <= 8:
            length_score = 40
        elif 3 <= length <= 10:
            length_score = 25
        else:
            length_score = 10
        
        # Optimal syllables: 1-2
        if syllables <= 2:
            syllable_score = 30
        elif syllables == 3:
            syllable_score = 20
        else:
            syllable_score = 5
        
        # Numbers reduce memorability
        number_penalty = 15 if has_numbers else 0
        
        # Phonetic appeal contributes
        phonetic_component = self._calculate_phonetic_score(name) * 0.3
        
        score = length_score + syllable_score + phonetic_component - number_penalty
        return round(max(0, min(100, score)), 2)
    
    def _calculate_pronounceability(self, name):
        """
        Calculate how easy the name is to pronounce
        Score: 0-100
        """
        clean_name = re.sub(r'[^a-zA-Z]', '', name.lower())
        if not clean_name:
            return 0
        
        # Vowel spacing (should have vowels regularly distributed)
        vowel_positions = [i for i, c in enumerate(clean_name) if c in 'aeiou']
        if len(vowel_positions) < 2:
            spacing_score = 20
        else:
            gaps = [vowel_positions[i+1] - vowel_positions[i] for i in range(len(vowel_positions)-1)]
            avg_gap = sum(gaps) / len(gaps)
            # Ideal gap: 1-2 characters
            spacing_score = 40 * (1 / (1 + abs(avg_gap - 1.5)))
        
        # Consonant cluster penalty
        clusters = self._count_consonant_clusters(name)
        cluster_penalty = min(clusters * 15, 50)
        
        # Length consideration
        length_factor = 30 if 3 <= len(clean_name) <= 8 else 15
        
        # Starting with a vowel is generally easier
        starts_with_vowel = 10 if clean_name[0] in 'aeiou' else 0
        
        score = spacing_score + length_factor + starts_with_vowel - cluster_penalty
        return round(max(0, min(100, score)), 2)
    
    def _categorize_name(self, name):
        """
        Categorize the name into primary type and all applicable tags
        Returns: (primary_type, [tags])
        """
        name_lower = name.lower()
        tags = []
        
        # Check each category
        if any(word in name_lower for word in self.animal_words):
            tags.append('animal')
        
        if any(word in name_lower for word in self.tech_words):
            tags.append('tech')
        
        if any(word in name_lower for word in self.mythological_words):
            tags.append('mythological')
        
        if any(word in name_lower for word in self.financial_words):
            tags.append('financial')
        
        if any(word in name_lower for word in self.astronomical_words):
            tags.append('astronomical')
        
        if any(word in name_lower for word in self.elemental_words):
            tags.append('elemental')
        
        # Check for acronym (all caps, 2-5 letters)
        if name.isupper() and 2 <= len(name) <= 5 and name.isalpha():
            tags.append('acronym')
        
        # Check for numbers
        if re.search(r'\d', name):
            tags.append('numeric')
        
        # Check for portmanteau (mixed categories)
        if len(tags) >= 2:
            tags.append('portmanteau')
        
        # Check for invented/abstract
        if not tags or (len(tags) == 1 and tags[0] == 'numeric'):
            tags.append('invented')
        
        # Primary type is the first tag, or 'other' if none
        primary_type = tags[0] if tags else 'other'
        if not tags:
            tags = ['other']
        
        return primary_type, tags
    
    def _analyze_capitalization(self, name):
        """Analyze capitalization pattern"""
        if name.islower():
            return 'lowercase'
        elif name.isupper():
            return 'uppercase'
        elif re.match(r'^[A-Z][a-z]+(?:[A-Z][a-z]+)+$', name):
            return 'camelcase'
        elif any(c.isupper() for c in name) and any(c.islower() for c in name):
            return 'mixed'
        else:
            return 'lowercase'
    
    def _is_real_word(self, name):
        """Check if name is likely a real English word"""
        # Simple heuristic: common dictionary words
        common_words = {
            'bitcoin', 'ethereum', 'cardano', 'stellar', 'cosmos', 'avalanche',
            'polygon', 'solana', 'chain', 'link', 'maker', 'compound', 'curve'
        }
        return name.lower() in common_words
    
    def _get_semantic_category(self, name):
        """Get the semantic meaning category of the name"""
        name_lower = name.lower()
        
        if any(word in name_lower for word in self.animal_words):
            return 'animal_reference'
        elif any(word in name_lower for word in self.tech_words):
            return 'technology'
        elif any(word in name_lower for word in self.mythological_words):
            return 'mythology'
        elif any(word in name_lower for word in self.financial_words):
            return 'finance'
        elif any(word in name_lower for word in self.astronomical_words):
            return 'astronomy'
        elif any(word in name_lower for word in self.elemental_words):
            return 'nature'
        else:
            return 'abstract'
    
    def _calculate_uniqueness(self, name, all_names):
        """
        Calculate uniqueness metrics by comparing to all other names
        
        Returns dict with:
        - uniqueness_score: 0-100, higher = more unique
        - avg_similarity_distance: Average Levenshtein distance
        - closest_match: Name of most similar crypto
        - closest_match_distance: Distance to closest match
        """
        if not all_names or len(all_names) < 2:
            return {
                'uniqueness_score': 100,
                'avg_similarity_distance': None,
                'closest_match': None,
                'closest_match_distance': None
            }
        
        distances = []
        min_distance = float('inf')
        closest = None
        
        for other_name in all_names:
            if other_name.lower() == name.lower():
                continue
            
            distance = Levenshtein.distance(name.lower(), other_name.lower())
            distances.append(distance)
            
            if distance < min_distance:
                min_distance = distance
                closest = other_name
        
        if not distances:
            return {
                'uniqueness_score': 100,
                'avg_similarity_distance': None,
                'closest_match': None,
                'closest_match_distance': None
            }
        
        avg_distance = sum(distances) / len(distances)
        
        # Uniqueness score: normalized average distance
        # Typical max distance is around 10-15 for crypto names
        uniqueness_score = min(100, (avg_distance / 10) * 100)
        
        return {
            'uniqueness_score': round(uniqueness_score, 2),
            'avg_similarity_distance': round(avg_distance, 2),
            'closest_match': closest,
            'closest_match_distance': min_distance
        }
    
    def calculate_scarcity_metrics(self, name_type, all_analyses):
        """
        Calculate scarcity metrics for a name type within the full dataset
        
        Args:
            name_type: The primary name type
            all_analyses: List of all NameAnalysis objects
            
        Returns:
            Dict with name_type_count and name_type_percentile
        """
        type_counts = Counter(analysis.name_type for analysis in all_analyses)
        total_count = len(all_analyses)
        
        type_count = type_counts.get(name_type, 1)
        
        # Percentile: what percentage are more rare than this type
        rarer_count = sum(1 for count in type_counts.values() if count < type_count)
        percentile = (rarer_count / len(type_counts)) * 100 if type_counts else 50
        
        return {
            'name_type_count': type_count,
            'name_type_percentile': round(percentile, 2)
        }
    
    def calculate_phonetic_harshness(self, name: str) -> float:
        """Calculate phonetic harshness for storm/aggressive context analysis.
        
        Plosives (hard stops): p, b, t, d, k, g = HIGH harshness
        Fricatives (friction): f, v, s, z, sh, th, ch = MEDIUM harshness
        Nasals/liquids: m, n, l, r = LOW harshness (soothing)
        Vowels: a, e, i, o, u = SOFT (negative harshness)
        
        Returns:
            Score 0-100 (higher = harsher/more aggressive sounding)
        """
        name_lower = name.lower()
        
        # Count phoneme types
        plosives = sum(name_lower.count(c) for c in 'pbtdkg')
        fricatives = sum(name_lower.count(c) for c in 'fvszx')
        # Add common digraphs
        fricatives += name_lower.count('sh') + name_lower.count('ch') + name_lower.count('th')
        
        nasals_liquids = sum(name_lower.count(c) for c in 'mnlr')
        vowels = sum(name_lower.count(c) for c in 'aeiou')
        
        total_chars = len(re.sub(r'[^a-zA-Z]', '', name))
        if total_chars == 0:
            return 50.0
        
        # Weighted harshness calculation
        harshness_raw = (
            (plosives / total_chars * 100 * 3.0) +  # Plosives = very harsh
            (fricatives / total_chars * 100 * 2.0) +  # Fricatives = medium harsh
            (nasals_liquids / total_chars * 100 * 0.5) -  # Nasals/liquids soften
            (vowels / total_chars * 100 * 1.5)  # Vowels significantly soften
        )
        
        # Normalize to 0-100 (centered at 50)
        normalized = max(0, min(100, harshness_raw + 50))
        return round(normalized, 2)
    
    def infer_gender_coding(self, name: str, context_year: int = None) -> str:
        """Infer gender coding of a name (for hurricane or general use).
        
        Args:
            name: The name to analyze
            context_year: Year context (for hurricane naming policy awareness)
        
        Returns:
            'male', 'female', 'neutral', or 'ambiguous'
        """
        name_lower = name.lower().strip()
        
        # Common male names
        male_indicators = {
            'andrew', 'bob', 'dennis', 'floyd', 'georges', 'hugo', 'ivan', 'michael',
            'dean', 'felix', 'gustav', 'ike', 'karl', 'otto', 'philippe', 'richard',
            'alex', 'bill', 'colin', 'don', 'earl', 'gaston', 'joaquin', 'larry',
            'marco', 'nate', 'omar', 'peter', 'rafael', 'sam', 'tony', 'victor',
            'barry', 'danny', 'fred', 'gordon', 'harvey', 'jose', 'lee', 'matthew',
            'ian', 'stan', 'vince', 'waldo'
        }
        
        # Common female names
        female_indicators = {
            'katrina', 'rita', 'emily', 'isabel', 'frances', 'jeanne', 'ophelia',
            'maria', 'irma', 'nora', 'grace', 'ida', 'fiona', 'nicole', 'lisa',
            'julia', 'bonnie', 'danielle', 'karen', 'sandy', 'erin', 'gabrielle',
            'hanna', 'josephine', 'laura', 'sally', 'bertha', 'dolly', 'alma',
            'andrea', 'cindy', 'edith', 'camille', 'betsy', 'agnes', 'belle'
        }
        
        # Direct match
        if name_lower in male_indicators:
            return 'male'
        if name_lower in female_indicators:
            return 'female'
        
        # Morphological heuristics
        if name_lower.endswith(('a', 'ia', 'ina', 'elle', 'ette', 'een', 'ine')):
            return 'female'
        elif name_lower.endswith(('o', 'us', 'er', 'on', 'en')):
            return 'male'
        
        # Length heuristic (very rough)
        if len(name_lower) <= 3:
            return 'neutral'
        
        return 'ambiguous'
    
    def calculate_sentiment_polarity(self, name: str) -> float:
        """Calculate sentiment polarity of a name.
        
        Returns:
            Float from -1.0 (very negative) to +1.0 (very positive)
        """
        name_lower = name.lower()
        
        # Positive semantic markers
        positive_words = {
            'belle', 'grace', 'hope', 'joy', 'star', 'sunny', 'happy', 'victor',
            'win', 'love', 'peace', 'bright', 'dawn', 'light', 'clear', 'calm'
        }
        
        # Negative semantic markers
        negative_words = {
            'bad', 'evil', 'doom', 'grim', 'dark', 'death', 'destroy', 'wreck',
            'hell', 'devil', 'chaos', 'rage', 'fury', 'disaster', 'doom'
        }
        
        # Count matches
        positive_hits = sum(1 for word in positive_words if word in name_lower)
        negative_hits = sum(1 for word in negative_words if word in name_lower)
        
        if positive_hits == 0 and negative_hits == 0:
            return 0.0  # Neutral
        
        # Calculate polarity
        total_hits = positive_hits + negative_hits
        polarity = (positive_hits - negative_hits) / total_hits
        
        return round(polarity, 2)
    
    def calculate_fantasy_score(self, name: str) -> float:
        """Calculate fantasy/medieval resonance (0-100).
        
        Used for MTG cards, fantasy novels, RPG characters.
        Detects constructed language patterns, archaic structures, epic naming conventions.
        """
        score = 50.0
        name_lower = name.lower()
        
        # Apostrophes/hyphens (constructed names: Llanowar, Ko'rish)
        if "'" in name or '-' in name:
            score += 15
        
        # Fantasy suffixes
        fantasy_suffixes = ['ax', 'or', 'ath', 'on', 'el', 'ar', 'us', 'os', 'ix', 'ur', 'og', 'an', 'il']
        if any(name_lower.endswith(suffix) for suffix in fantasy_suffixes):
            score += 20
        
        # Multiple capitals (camel-case legendary names)
        capitals = sum(1 for c in name if c.isupper())
        if capitals > 1 and len(name) > 1:
            score += 10
        
        # Archaic articles and titles
        archaic_patterns = ['the ', 'of the', 'lord of', 'master of', 'keeper of', 'bringer of']
        if any(name_lower.startswith(pattern) for pattern in archaic_patterns):
            score += 15
        
        # Long multi-word names (epic feel)
        word_count = len(name.split())
        if word_count >= 3:
            score += 10
        elif word_count == 4:
            score += 15
        
        # Rare letter combinations
        rare_combos = ['zz', 'kh', 'zh', 'xh', 'qx', "'s", "k'", 'thr', 'dhr']
        if any(combo in name_lower for combo in rare_combos):
            score += 10
        
        return round(min(100, max(0, score)), 2)
    
    def calculate_power_connotation(self, name: str) -> float:
        """Calculate aggressive vs. gentle semantic connotation (-100 to +100).
        
        Positive values = aggressive/destructive
        Negative values = gentle/nurturing
        Zero = neutral
        """
        name_lower = name.lower()
        
        aggressive_words = {
            'death', 'destroy', 'kill', 'dragon', 'wrath', 'annihilate', 'obliterate',
            'doom', 'rage', 'fury', 'slaughter', 'massacre', 'terminate', 'murder',
            'chaos', 'havoc', 'devastation', 'catastrophe', 'apocalypse', 'carnage',
            'butcher', 'slay', 'vanquish', 'crush', 'smash', 'demolish', 'strike',
            'blast', 'bolt', 'fire', 'burn', 'lightning', 'thunder', 'storm'
        }
        
        gentle_words = {
            'heal', 'peace', 'mend', 'serene', 'gentle', 'tranquil', 'calm', 'soothe',
            'nurture', 'harmony', 'blessing', 'grace', 'mercy', 'kindness', 'compassion',
            'life', 'growth', 'flourish', 'bloom', 'restore', 'renew', 'spring'
        }
        
        aggressive_hits = sum(1 for word in aggressive_words if word in name_lower)
        gentle_hits = sum(1 for word in gentle_words if word in name_lower)
        
        if aggressive_hits == 0 and gentle_hits == 0:
            return 0.0
        
        # Calculate polarity
        total = aggressive_hits + gentle_hits
        polarity = (aggressive_hits - gentle_hits) / total
        
        return round(polarity * 100, 2)
    
    def calculate_mythic_resonance(self, name: str, is_legendary: bool = False) -> float:
        """Calculate epic/legendary linguistic quality (0-100).
        
        Detects title words, epic scale, mythological references.
        Boosted for mechanically legendary items.
        """
        score = 40.0
        name_lower = name.lower()
        
        # Title words
        titles = {
            'lord', 'master', 'king', 'queen', 'emperor', 'empress', 'god', 'goddess',
            'champion', 'elder', 'ancient', 'primordial', 'eternal', 'prince', 'princess',
            'duke', 'baron', 'count', 'knight', 'sage', 'archon', 'avatar'
        }
        if any(title in name_lower for title in titles):
            score += 25
        
        # Epic scale words
        epic_scale = {
            'infinite', 'eternal', 'supreme', 'ultimate', 'primal', 'cosmic',
            'void', 'abyss', 'immortal', 'omnipotent', 'divine', 'celestial',
            'grand', 'great', 'mighty', 'legendary'
        }
        epic_hits = sum(1 for word in epic_scale if word in name_lower)
        score += min(epic_hits * 15, 30)
        
        # Mechanical legendary status (game designers thought it was epic)
        if is_legendary:
            score += 15
        
        # Syllable count (longer = more epic)
        syllables = self._count_syllables(name)
        if syllables >= 5:
            score += 15
        elif syllables >= 4:
            score += 10
        elif syllables >= 3:
            score += 5
        
        # Comma structure (legendary title format: "Name, the Title")
        if ',' in name:
            score += 10
        
        # Article "the" (The Scarab God, The Gitrog Monster)
        if name_lower.startswith('the '):
            score += 10
        
        return round(min(100, max(0, score)), 2)

