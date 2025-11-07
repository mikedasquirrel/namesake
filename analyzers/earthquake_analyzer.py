"""
Earthquake Location Name Phonetic Analyzer

Extends hurricane phonetic analysis framework to earthquake location names.
Analyzes how phonetic properties of location names (cities, regions, countries)
correlate with disaster outcomes.
"""

import pandas as pd
import numpy as np
from typing import Dict, List
import re


class EarthquakeLocationAnalyzer:
    """Analyzes phonetic properties of earthquake location names."""
    
    def __init__(self):
        # Phoneme classification (from hurricane analyzer)
        self.plosives = set('ptkbdg')
        self.fricatives = set('fvszʃʒθð')
        self.liquids = set('lr')
        self.nasals = set('mn')
        self.vowels = set('aeiouæɛɪɔʊəɜʌ')
        
    def analyze_location_name(self, name: str) -> Dict:
        """
        Comprehensive phonetic analysis of earthquake location name.
        
        Args:
            name: Location name (e.g., "Northridge", "Kobe", "Haiti")
            
        Returns:
            Dict with phonetic features
        """
        if not name or pd.isna(name):
            return self._empty_analysis()
        
        name_clean = name.lower().strip()
        
        # Remove common prefixes
        name_clean = re.sub(r'^(earthquake|quake|the)\s+', '', name_clean)
        
        # Basic metrics
        char_length = len(name_clean.replace(' ', ''))
        word_count = len(name_clean.split())
        
        # Phonetic features
        harshness = self._calculate_harshness(name_clean)
        smoothness = self._calculate_smoothness(name_clean)
        syllable_count = self._estimate_syllables(name_clean)
        memorability = self._calculate_memorability(name_clean, syllable_count)
        pronounceability = self._calculate_pronounceability(name_clean)
        
        # Geographic/cultural features
        cultural_familiarity = self._estimate_cultural_familiarity(name)
        semantic_valence = self._estimate_semantic_valence(name)
        naming_specificity = self._calculate_naming_specificity(name)
        
        return {
            'name': name,
            'name_clean': name_clean,
            'character_length': char_length,
            'word_count': word_count,
            'syllable_count': syllable_count,
            'phonetic_harshness': harshness,
            'phonetic_smoothness': smoothness,
            'memorability_score': memorability,
            'pronounceability_score': pronounceability,
            'cultural_familiarity': cultural_familiarity,
            'semantic_valence': semantic_valence,
            'naming_specificity': naming_specificity,
            'vowel_ratio': self._vowel_ratio(name_clean),
            'plosive_count': sum(1 for c in name_clean if c in self.plosives),
            'fricative_count': sum(1 for c in name_clean if c in self.fricatives)
        }
    
    def _calculate_harshness(self, name: str) -> float:
        """
        Calculate phonetic harshness score (0-100).
        
        Plosives, fricatives, and consonant clusters increase harshness.
        """
        if not name:
            return 0.0
        
        # Count harsh phonemes
        plosive_count = sum(1 for c in name if c in self.plosives)
        fricative_count = sum(1 for c in name if c in self.fricatives)
        
        # Consonant clusters (multiple consonants together)
        cluster_penalty = len(re.findall(r'[bcdfghjklmnpqrstvwxyz]{3,}', name)) * 10
        
        # Calculate harshness (0-100 scale)
        harshness = (plosive_count * 15) + (fricative_count * 10) + cluster_penalty
        
        return min(100.0, harshness)
    
    def _calculate_smoothness(self, name: str) -> float:
        """Calculate phonetic smoothness (liquids, nasals, vowels)."""
        if not name:
            return 0.0
        
        liquid_count = sum(1 for c in name if c in self.liquids)
        nasal_count = sum(1 for c in name if c in self.nasals)
        vowel_count = sum(1 for c in name if c in self.vowels)
        
        total_phonemes = len(name.replace(' ', ''))
        if total_phonemes == 0:
            return 0.0
        
        smoothness = ((liquid_count + nasal_count + vowel_count) / total_phonemes) * 100
        return min(100.0, smoothness)
    
    def _estimate_syllables(self, name: str) -> int:
        """Estimate syllable count using vowel cluster method."""
        if not name:
            return 0
        
        # Remove spaces
        name = name.replace(' ', '')
        
        # Count vowel groups
        syllables = len(re.findall(r'[aeiou]+', name, re.IGNORECASE))
        
        # Minimum 1 syllable if name exists
        return max(1, syllables)
    
    def _calculate_memorability(self, name: str, syllables: int) -> float:
        """
        Calculate memorability score (0-100).
        
        Higher scores = more memorable (shorter, distinctive, pronounceable).
        """
        if not name:
            return 0.0
        
        # Brevity bonus (shorter = more memorable)
        length = len(name.replace(' ', ''))
        brevity_score = max(0, 100 - (length * 5))
        
        # Syllable bonus (2-3 syllables optimal)
        if syllables in [2, 3]:
            syllable_bonus = 20
        elif syllables == 1:
            syllable_bonus = 10
        else:
            syllable_bonus = max(0, 20 - (syllables - 3) * 5)
        
        # Uniqueness (avoid common words)
        common_words = {'the', 'of', 'and', 'in', 'on', 'at', 'to', 'for', 'north', 'south', 'east', 'west'}
        uniqueness = 30 if name not in common_words else 0
        
        memorability = min(100.0, brevity_score + syllable_bonus + uniqueness)
        return memorability
    
    def _calculate_pronounceability(self, name: str) -> float:
        """
        Calculate pronounceability score (0-100).
        
        Based on phonotactic legality and consonant cluster complexity.
        """
        if not name:
            return 0.0
        
        # Penalize consonant clusters
        clusters = re.findall(r'[bcdfghjklmnpqrstvwxyz]{2,}', name)
        cluster_penalty = sum(len(c) - 1 for c in clusters) * 10
        
        # Bonus for vowel distribution
        vowel_positions = [i for i, c in enumerate(name) if c in self.vowels]
        if len(vowel_positions) > 1:
            avg_gap = np.mean(np.diff(vowel_positions)) if len(vowel_positions) > 1 else 10
            distribution_bonus = min(30, avg_gap * 3)
        else:
            distribution_bonus = 0
        
        pronounceability = max(0, min(100, 70 - cluster_penalty + distribution_bonus))
        return pronounceability
    
    def _estimate_cultural_familiarity(self, name: str) -> float:
        """
        Estimate cultural familiarity for US audience (0-100).
        
        Common US place names = high familiarity.
        """
        if not name:
            return 0.0
        
        name_lower = name.lower()
        
        # High familiarity (US major cities, common regions)
        high_familiarity = ['san francisco', 'los angeles', 'seattle', 'california', 
                           'alaska', 'washington', 'francisco', 'diego', 'jose']
        
        # Medium familiarity (other US places, major world cities)
        medium_familiarity = ['virginia', 'loma', 'northridge', 'anchorage', 'napa',
                             'japan', 'tokyo', 'mexico', 'chile']
        
        # Check for matches
        for term in high_familiarity:
            if term in name_lower:
                return 80.0
        
        for term in medium_familiarity:
            if term in name_lower:
                return 50.0
        
        # Default: low familiarity for international/unfamiliar
        return 20.0
    
    def _estimate_semantic_valence(self, name: str) -> float:
        """
        Estimate semantic valence (-1 to +1).
        
        Positive = tourism/beauty associations
        Negative = industrial/harsh associations
        """
        if not name:
            return 0.0
        
        name_lower = name.lower()
        
        # Positive associations (tourism, nature, beauty)
        positive_terms = ['san', 'santa', 'bay', 'valley', 'beach', 'lake', 'park']
        
        # Negative associations (industrial, harsh)
        negative_terms = ['bam', 'tangshan', 'kashmir']
        
        score = 0.0
        for term in positive_terms:
            if term in name_lower:
                score += 0.3
        
        for term in negative_terms:
            if term in name_lower:
                score -= 0.3
        
        return max(-1.0, min(1.0, score))
    
    def _calculate_naming_specificity(self, name: str) -> float:
        """
        Calculate naming specificity (0-100).
        
        Higher = more specific (city name vs country name).
        """
        if not name:
            return 0.0
        
        word_count = len(name.split())
        
        # More words = more specific ("Loma Prieta" vs "California")
        if word_count >= 2:
            return 80.0
        elif word_count == 1:
            # Check if it's a city (specific) vs country (general)
            if len(name) <= 10:  # Shorter names tend to be cities
                return 60.0
            else:
                return 40.0
        
        return 50.0
    
    def _vowel_ratio(self, name: str) -> float:
        """Calculate ratio of vowels to total characters."""
        if not name:
            return 0.0
        
        name_clean = name.replace(' ', '')
        if len(name_clean) == 0:
            return 0.0
        
        vowel_count = sum(1 for c in name_clean if c in self.vowels)
        return vowel_count / len(name_clean)
    
    def _empty_analysis(self) -> Dict:
        """Return empty analysis dict for missing names."""
        return {
            'name': None,
            'name_clean': None,
            'character_length': 0,
            'word_count': 0,
            'syllable_count': 0,
            'phonetic_harshness': 0,
            'phonetic_smoothness': 0,
            'memorability_score': 0,
            'pronounceability_score': 0,
            'cultural_familiarity': 0,
            'semantic_valence': 0,
            'naming_specificity': 0,
            'vowel_ratio': 0,
            'plosive_count': 0,
            'fricative_count': 0
        }
    
    def analyze_dataset(self, df: pd.DataFrame, name_column: str = 'name') -> pd.DataFrame:
        """
        Analyze all location names in a dataset.
        
        Args:
            df: DataFrame with earthquake data
            name_column: Column containing location names
            
        Returns:
            DataFrame with added phonetic feature columns
        """
        print(f"Analyzing {len(df)} earthquake location names...")
        
        analyses = []
        for idx, row in df.iterrows():
            name = row.get(name_column, '')
            analysis = self.analyze_location_name(name)
            analyses.append(analysis)
        
        # Create features dataframe
        features_df = pd.DataFrame(analyses)
        
        # Merge with original (drop duplicate name column)
        features_df = features_df.drop(columns=['name'], errors='ignore')
        result = pd.concat([df.reset_index(drop=True), features_df], axis=1)
        
        print(f"✓ Added {len(features_df.columns)} phonetic features")
        return result


def main():
    """Test earthquake analyzer on sample data."""
    analyzer = EarthquakeLocationAnalyzer()
    
    # Test cases
    test_names = [
        "Northridge",
        "Loma Prieta", 
        "San Francisco",
        "Haiti",
        "Kobe",
        "Tangshan",
        "Nepal",
        "Kashmir",
        "Christchurch"
    ]
    
    print("Testing Earthquake Location Name Analyzer")
    print("=" * 60)
    
    for name in test_names:
        result = analyzer.analyze_location_name(name)
        print(f"\n{name}:")
        print(f"  Harshness: {result['phonetic_harshness']:.1f}")
        print(f"  Memorability: {result['memorability_score']:.1f}")
        print(f"  Cultural Familiarity: {result['cultural_familiarity']:.1f}")
        print(f"  Syllables: {result['syllable_count']}")


if __name__ == '__main__':
    main()

