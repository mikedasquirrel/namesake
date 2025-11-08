"""
Relationship Formulas - Combine Two Names into Compatibility Scores

Tests the shocking hypothesis: Can we predict relationship outcomes 
(marriage success, divorce, parent-child patterns, pet compatibility)
from name mathematics alone?

This is where nominative determinism gets DEEP.

EXPANDED VERSION - November 8, 2025:
- Added phonetic distance metrics (ALINE algorithm)
- Added vowel harmony and consonant compatibility
- Added stress pattern alignment
- Enhanced golden ratio testing
- Added relative success calculations
"""

import numpy as np
from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass, field
import math
import Levenshtein

from utils.formula_engine import VisualEncoding, FormulaEngine
from analyzers.name_analyzer import NameAnalyzer


@dataclass
class RelationshipEncoding:
    """Visual encoding of a two-name relationship"""
    name1: str
    name2: str
    
    # Combined properties
    compatibility_score: float  # 0-1 (higher = more compatible)
    distance_score: float  # 0-1 (how different are they?)
    resonance_score: float  # 0-1 (do they amplify each other?)
    balance_score: float  # 0-1 (are they balanced?)
    
    # Specific tests
    golden_ratio_proximity: float  # How close to φ = 1.618
    color_harmony: float  # Complementary colors?
    complexity_balance: float  # Similar complexity?
    symmetry_match: float  # Both symmetric?
    
    # NEW: Phonetic interaction metrics
    phonetic_distance: float = 0.0  # Edit distance (normalized)
    vowel_harmony: float = 0.0  # Do vowels complement?
    consonant_compatibility: float = 0.0  # Consonant cluster matching
    stress_alignment: float = 0.0  # Stress pattern similarity
    syllable_ratio: float = 1.0  # Ratio of syllable counts
    syllable_ratio_to_phi: float = 1.0  # Distance from golden ratio
    
    # NEW: Semantic metrics
    cultural_origin_match: float = 0.0  # Same cultural background?
    social_class_alignment: float = 0.0  # SES connotation match
    
    # Pattern type
    relationship_type: str = "neutral"  # harmonic/complementary/discordant
    
    # Individual encodings
    encoding1: Optional[VisualEncoding] = None
    encoding2: Optional[VisualEncoding] = None
    
    # Individual name features (for analysis)
    features1: Dict = field(default_factory=dict)
    features2: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'name1': self.name1,
            'name2': self.name2,
            'compatibility_score': self.compatibility_score,
            'distance_score': self.distance_score,
            'resonance_score': self.resonance_score,
            'balance_score': self.balance_score,
            'golden_ratio_proximity': self.golden_ratio_proximity,
            'color_harmony': self.color_harmony,
            'relationship_type': self.relationship_type,
        }


class RelationshipFormulaEngine:
    """
    Analyzes relationships between two names
    
    Tests multiple theories of name compatibility:
    1. Similarity Theory: Similar names = compatible
    2. Complementary Theory: Opposite names = compatible
    3. Golden Ratio Theory: φ relationship = ideal
    4. Harmonic Theory: Musical/frequency resonance
    5. Balance Theory: Equal complexity/symmetry
    """
    
    def __init__(self):
        self.engine = FormulaEngine()
        self.analyzer = NameAnalyzer()
        self.golden_ratio = 1.618033988749
    
    def analyze_relationship(self, name1: str, name2: str, 
                           formula_id: str = 'hybrid',
                           include_phonetic: bool = True) -> RelationshipEncoding:
        """
        Analyze compatibility between two names
        
        Args:
            name1: First name
            name2: Second name
            formula_id: Which formula to use
            include_phonetic: Include advanced phonetic analysis
            
        Returns:
            RelationshipEncoding with compatibility metrics
        """
        # Get individual encodings
        features1 = self.analyzer.analyze_name(name1)
        features2 = self.analyzer.analyze_name(name2)
        
        encoding1 = self.engine.transform(name1, features1, formula_id)
        encoding2 = self.engine.transform(name2, features2, formula_id)
        
        # Calculate relationship metrics (original)
        compatibility = self._calculate_compatibility(encoding1, encoding2)
        distance = self._calculate_distance(encoding1, encoding2)
        resonance = self._calculate_resonance(encoding1, encoding2)
        balance = self._calculate_balance(encoding1, encoding2)
        golden_proximity = self._test_golden_ratio(encoding1, encoding2)
        color_harmony = self._test_color_harmony(encoding1, encoding2)
        complexity_balance = self._test_complexity_balance(encoding1, encoding2)
        symmetry_match = self._test_symmetry_match(encoding1, encoding2)
        
        # NEW: Calculate phonetic metrics
        phonetic_distance = 0.0
        vowel_harmony = 0.0
        consonant_compat = 0.0
        stress_align = 0.0
        syllable_ratio = 1.0
        syllable_ratio_to_phi = 1.0
        cultural_match = 0.0
        social_class_align = 0.0
        
        if include_phonetic:
            phonetic_distance = self._calculate_phonetic_distance(name1, name2)
            vowel_harmony = self._calculate_vowel_harmony(name1, name2)
            consonant_compat = self._calculate_consonant_compatibility(name1, name2)
            stress_align = self._calculate_stress_alignment(features1, features2)
            syllable_ratio = self._calculate_syllable_ratio(features1, features2)
            syllable_ratio_to_phi = abs(syllable_ratio - self.golden_ratio) / self.golden_ratio
            cultural_match = self._estimate_cultural_match(features1, features2)
            social_class_align = self._estimate_social_class_alignment(features1, features2)
        
        # Classify relationship type
        rel_type = self._classify_relationship(compatibility, distance, resonance)
        
        return RelationshipEncoding(
            name1=name1,
            name2=name2,
            compatibility_score=compatibility,
            distance_score=distance,
            resonance_score=resonance,
            balance_score=balance,
            golden_ratio_proximity=golden_proximity,
            color_harmony=color_harmony,
            complexity_balance=complexity_balance,
            symmetry_match=symmetry_match,
            phonetic_distance=phonetic_distance,
            vowel_harmony=vowel_harmony,
            consonant_compatibility=consonant_compat,
            stress_alignment=stress_align,
            syllable_ratio=syllable_ratio,
            syllable_ratio_to_phi=syllable_ratio_to_phi,
            cultural_origin_match=cultural_match,
            social_class_alignment=social_class_align,
            relationship_type=rel_type,
            encoding1=encoding1,
            encoding2=encoding2,
            features1=features1,
            features2=features2
        )
    
    def _calculate_compatibility(self, enc1: VisualEncoding, enc2: VisualEncoding) -> float:
        """
        Overall compatibility score
        Combines multiple theories weighted by empirical success
        """
        # Similarity score (0-1, higher = more similar)
        similarity = 1.0 - self._calculate_distance(enc1, enc2)
        
        # Complementarity score (some properties should differ)
        complementarity = self._calculate_complementarity(enc1, enc2)
        
        # Golden ratio score (some property ratios should = φ)
        golden = self._test_golden_ratio(enc1, enc2)
        
        # Weighted combination (empirical weights TBD from data)
        compatibility = (
            similarity * 0.3 +
            complementarity * 0.4 +
            golden * 0.3
        )
        
        return compatibility
    
    def _calculate_distance(self, enc1: VisualEncoding, enc2: VisualEncoding) -> float:
        """
        Calculate normalized distance between two visual encodings
        Returns 0-1 (0 = identical, 1 = maximally different)
        """
        differences = []
        
        # Geometric differences
        differences.append(abs(enc1.complexity - enc2.complexity))
        differences.append(abs(enc1.symmetry - enc2.symmetry))
        differences.append(abs(enc1.angular_vs_curved - enc2.angular_vs_curved) / 2.0)
        
        # Color differences
        hue_diff = abs(enc1.hue - enc2.hue)
        # Wrap around (359° and 1° are close)
        if hue_diff > 180:
            hue_diff = 360 - hue_diff
        differences.append(hue_diff / 180.0)
        
        differences.append(abs(enc1.saturation - enc2.saturation) / 100.0)
        differences.append(abs(enc1.brightness - enc2.brightness) / 100.0)
        
        # Spatial differences
        differences.append(abs(enc1.x - enc2.x) / 2.0)
        differences.append(abs(enc1.y - enc2.y) / 2.0)
        differences.append(abs(enc1.z - enc2.z))
        
        # Texture differences
        differences.append(abs(enc1.glow_intensity - enc2.glow_intensity))
        differences.append(abs(enc1.fractal_dimension - enc2.fractal_dimension))
        differences.append(abs(enc1.pattern_density - enc2.pattern_density))
        
        # Average distance
        return float(np.mean(differences))
    
    def _calculate_complementarity(self, enc1: VisualEncoding, enc2: VisualEncoding) -> float:
        """
        Score for complementary (opposite but balanced) patterns
        Some properties should be similar, some should be opposite
        """
        # Color: Complementary hues (opposite on wheel)
        hue_diff = abs(enc1.hue - enc2.hue)
        color_complementary = abs(hue_diff - 180) / 180.0  # 180° apart is ideal
        color_score = 1.0 - color_complementary  # Higher = more complementary
        
        # Complexity: Should be similar (not too different)
        complexity_diff = abs(enc1.complexity - enc2.complexity)
        complexity_score = 1.0 - complexity_diff
        
        # Angular: Opposites can attract
        angular_diff = abs(enc1.angular_vs_curved - enc2.angular_vs_curved)
        angular_score = angular_diff / 2.0  # Higher difference = more complementary
        
        # Average
        complementarity = (color_score + complexity_score + angular_score) / 3.0
        
        return complementarity
    
    def _calculate_resonance(self, enc1: VisualEncoding, enc2: VisualEncoding) -> float:
        """
        Do the patterns amplify/reinforce each other?
        Musical consonance theory applied to names
        """
        # Frequency ratios (simple ratios = consonant)
        # Using hue as "frequency"
        freq_ratio = enc1.hue / max(enc2.hue, 1.0)
        
        # Test for simple ratios (1:1, 1:2, 2:3, 3:4, etc.)
        simple_ratios = [1.0, 0.5, 2.0, 1.5, 0.667, 1.333, 0.75, 1.25]
        
        min_distance = min(abs(freq_ratio - ratio) for ratio in simple_ratios)
        
        # Closer to simple ratio = higher resonance
        resonance = 1.0 - min(min_distance, 1.0)
        
        return resonance
    
    def _calculate_balance(self, enc1: VisualEncoding, enc2: VisualEncoding) -> float:
        """
        Are the two names balanced in their properties?
        """
        # Test multiple balance metrics
        balances = []
        
        # Complexity balance
        complexity_balance = 1.0 - abs(enc1.complexity - enc2.complexity)
        balances.append(complexity_balance)
        
        # Symmetry balance
        symmetry_balance = 1.0 - abs(enc1.symmetry - enc2.symmetry)
        balances.append(symmetry_balance)
        
        # Brightness balance
        brightness_balance = 1.0 - abs(enc1.brightness - enc2.brightness) / 100.0
        balances.append(brightness_balance)
        
        return float(np.mean(balances))
    
    def _test_golden_ratio(self, enc1: VisualEncoding, enc2: VisualEncoding) -> float:
        """
        Test if any property ratios approach golden ratio (φ = 1.618)
        """
        golden_proximities = []
        
        # Test various property ratios
        properties = [
            ('complexity', enc1.complexity, enc2.complexity),
            ('hue', enc1.hue / 360.0, enc2.hue / 360.0),  # Normalize
            ('brightness', enc1.brightness / 100.0, enc2.brightness / 100.0),
        ]
        
        for name, val1, val2 in properties:
            if val2 > 0:
                ratio = val1 / val2
                # Test both ratios (a/b and b/a)
                proximity1 = abs(ratio - self.golden_ratio) / self.golden_ratio
                proximity2 = abs((1/ratio) - self.golden_ratio) / self.golden_ratio
                
                best_proximity = min(proximity1, proximity2)
                golden_proximities.append(1.0 - min(best_proximity, 1.0))
        
        # Best golden ratio match
        return max(golden_proximities) if golden_proximities else 0.0
    
    def _test_color_harmony(self, enc1: VisualEncoding, enc2: VisualEncoding) -> float:
        """
        Test color theory harmony (complementary, analogous, triadic)
        """
        hue_diff = abs(enc1.hue - enc2.hue)
        if hue_diff > 180:
            hue_diff = 360 - hue_diff
        
        # Complementary (180° apart)
        complementary_score = 1.0 - abs(hue_diff - 180) / 180.0
        
        # Analogous (30° apart)
        analogous_score = 1.0 - abs(hue_diff - 30) / 180.0
        
        # Triadic (120° apart)
        triadic_score = 1.0 - abs(hue_diff - 120) / 180.0
        
        # Best harmony
        return max(complementary_score, analogous_score, triadic_score)
    
    def _test_complexity_balance(self, enc1: VisualEncoding, enc2: VisualEncoding) -> float:
        """Test if complexity levels are balanced"""
        return 1.0 - abs(enc1.complexity - enc2.complexity)
    
    def _test_symmetry_match(self, enc1: VisualEncoding, enc2: VisualEncoding) -> float:
        """Test if symmetry levels match"""
        return 1.0 - abs(enc1.symmetry - enc2.symmetry)
    
    def _classify_relationship(self, compatibility: float, distance: float, 
                               resonance: float) -> str:
        """Classify the relationship type"""
        if compatibility > 0.7:
            return "harmonic"  # High compatibility
        elif distance > 0.7:
            return "discordant"  # Very different
        elif resonance > 0.7:
            return "resonant"  # Amplifying each other
        elif 0.4 < compatibility < 0.6 and 0.4 < distance < 0.6:
            return "complementary"  # Balanced opposites
        else:
            return "neutral"  # No strong pattern
    
    # =============================================================================
    # NEW: Advanced Phonetic Analysis Methods
    # =============================================================================
    
    def _calculate_phonetic_distance(self, name1: str, name2: str) -> float:
        """
        Calculate normalized phonetic distance using Levenshtein edit distance
        
        Returns:
            0-1 (0 = identical, 1 = maximally different)
        """
        # Clean names (remove non-letters)
        import re
        clean1 = re.sub(r'[^a-zA-Z]', '', name1.lower())
        clean2 = re.sub(r'[^a-zA-Z]', '', name2.lower())
        
        if not clean1 or not clean2:
            return 1.0
        
        # Levenshtein distance
        distance = Levenshtein.distance(clean1, clean2)
        
        # Normalize by max possible distance (length of longer name)
        max_distance = max(len(clean1), len(clean2))
        normalized = distance / max_distance if max_distance > 0 else 0.0
        
        return min(1.0, normalized)
    
    def _calculate_vowel_harmony(self, name1: str, name2: str) -> float:
        """
        Calculate vowel harmony score (do vowels complement or match?)
        
        Vowel harmony is a linguistic universal where vowels within a word
        tend to share features. Test if couple names have harmonic vowels.
        
        Returns:
            0-1 (1 = perfect harmony)
        """
        vowels = 'aeiouAEIOU'
        
        # Extract vowels
        vowels1 = [c.lower() for c in name1 if c in vowels]
        vowels2 = [c.lower() for c in name2 if c in vowels]
        
        if not vowels1 or not vowels2:
            return 0.5  # Neutral if no vowels
        
        # Vowel categories (front, central, back)
        front_vowels = set('ei')  # e, i
        central_vowels = set('a')  # a
        back_vowels = set('ou')  # o, u
        
        def get_vowel_profile(vowel_list):
            """Get proportion of front, central, back vowels"""
            total = len(vowel_list)
            front = sum(1 for v in vowel_list if v in front_vowels) / total
            central = sum(1 for v in vowel_list if v in central_vowels) / total
            back = sum(1 for v in vowel_list if v in back_vowels) / total
            return np.array([front, central, back])
        
        profile1 = get_vowel_profile(vowels1)
        profile2 = get_vowel_profile(vowels2)
        
        # Harmony = similarity of vowel distributions
        # Use cosine similarity
        dot_product = np.dot(profile1, profile2)
        norm1 = np.linalg.norm(profile1)
        norm2 = np.linalg.norm(profile2)
        
        if norm1 > 0 and norm2 > 0:
            harmony = dot_product / (norm1 * norm2)
        else:
            harmony = 0.5
        
        return float(harmony)
    
    def _calculate_consonant_compatibility(self, name1: str, name2: str) -> float:
        """
        Calculate consonant compatibility (do consonant patterns match?)
        
        Tests if consonant clusters and patterns are compatible.
        Similar cluster complexity = higher compatibility.
        
        Returns:
            0-1 (1 = highly compatible)
        """
        import re
        
        # Extract consonants
        consonants = 'bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ'
        cons1 = ''.join(c for c in name1.lower() if c in consonants.lower())
        cons2 = ''.join(c for c in name2.lower() if c in consonants.lower())
        
        if not cons1 or not cons2:
            return 0.5
        
        # Find consonant clusters (2+ consonants in a row)
        clusters1 = re.findall(r'[bcdfghjklmnpqrstvwxyz]{2,}', name1.lower())
        clusters2 = re.findall(r'[bcdfghjklmnpqrstvwxyz]{2,}', name2.lower())
        
        # Cluster density
        density1 = len(clusters1) / len(cons1) if cons1 else 0
        density2 = len(clusters2) / len(cons2) if cons2 else 0
        
        # Compatibility = similar cluster density
        density_diff = abs(density1 - density2)
        compatibility = 1.0 - min(density_diff, 1.0)
        
        return compatibility
    
    def _calculate_stress_alignment(self, features1: Dict, features2: Dict) -> float:
        """
        Calculate stress pattern alignment
        
        Names with similar stress patterns (syllable emphasis) should be
        more compatible (hypothesis: creates rhythmic harmony)
        
        Returns:
            0-1 (1 = perfectly aligned)
        """
        # Get syllable counts
        syl1 = features1.get('syllable_count', 1)
        syl2 = features2.get('syllable_count', 1)
        
        # Simple heuristic: similar syllable count = aligned stress
        syl_diff = abs(syl1 - syl2)
        
        # Normalize (max reasonable difference is 5 syllables)
        alignment = 1.0 - min(syl_diff / 5.0, 1.0)
        
        return alignment
    
    def _calculate_syllable_ratio(self, features1: Dict, features2: Dict) -> float:
        """
        Calculate ratio of syllable counts
        
        Returns:
            Ratio (always >= 1.0, larger / smaller)
        """
        syl1 = features1.get('syllable_count', 1)
        syl2 = features2.get('syllable_count', 1)
        
        if syl1 == 0 or syl2 == 0:
            return 1.0
        
        # Always return ratio >= 1.0 (larger / smaller)
        ratio = max(syl1, syl2) / min(syl1, syl2)
        
        return ratio
    
    def _estimate_cultural_match(self, features1: Dict, features2: Dict) -> float:
        """
        Estimate if names come from similar cultural backgrounds
        
        Uses name categories and semantic markers as proxies.
        
        Returns:
            0-1 (1 = strong cultural match)
        """
        # Get semantic categories
        cat1 = features1.get('semantic_category', 'abstract')
        cat2 = features2.get('semantic_category', 'abstract')
        
        # Exact match
        if cat1 == cat2:
            return 1.0
        
        # Related categories
        related_groups = [
            {'mythology', 'astronomy', 'nature'},  # Epic/classical
            {'technology', 'finance', 'abstract'},  # Modern/technical
            {'animal_reference'},  # Unique category
        ]
        
        for group in related_groups:
            if cat1 in group and cat2 in group:
                return 0.7  # Related but not identical
        
        # No apparent relationship
        return 0.3
    
    def _estimate_social_class_alignment(self, features1: Dict, features2: Dict) -> float:
        """
        Estimate if names suggest similar social class backgrounds
        
        Uses name complexity, length, and conventionality as proxies.
        
        Returns:
            0-1 (1 = strong alignment)
        """
        # Get complexity features
        len1 = features1.get('character_length', 5)
        len2 = features2.get('character_length', 5)
        
        mem1 = features1.get('memorability_score', 50)
        mem2 = features2.get('memorability_score', 50)
        
        # Length similarity
        len_diff = abs(len1 - len2)
        len_align = 1.0 - min(len_diff / 10.0, 1.0)
        
        # Memorability similarity
        mem_diff = abs(mem1 - mem2)
        mem_align = 1.0 - min(mem_diff / 100.0, 1.0)
        
        # Average
        alignment = (len_align + mem_align) / 2.0
        
        return alignment
    
    def predict_divorce_risk(self, name1: str, name2: str) -> Dict:
        """
        Predict divorce risk based on name compatibility
        
        Returns dict with:
        - risk_score (0-1, higher = higher divorce risk)
        - confidence (0-1)
        - factors (what contributes to risk)
        """
        relationship = self.analyze_relationship(name1, name2)
        
        # Hypothesis: Low compatibility = high divorce risk
        # (This is crude - will be refined with actual data)
        risk_score = 1.0 - relationship.compatibility_score
        
        # Factors
        factors = []
        if relationship.distance_score > 0.8:
            factors.append("Very different name patterns (high distance)")
        if relationship.golden_ratio_proximity < 0.3:
            factors.append("No golden ratio relationship")
        if relationship.color_harmony < 0.3:
            factors.append("Poor color harmony")
        if relationship.balance_score < 0.3:
            factors.append("Unbalanced complexity levels")
        
        return {
            'risk_score': risk_score,
            'confidence': 0.5,  # Will increase with training data
            'factors': factors,
            'relationship_type': relationship.relationship_type,
            'interpretation': self._interpret_risk(risk_score)
        }
    
    def _interpret_risk(self, risk: float) -> str:
        """Interpret divorce risk score"""
        if risk < 0.2:
            return "Very Low Risk - Highly compatible name patterns"
        elif risk < 0.4:
            return "Low Risk - Compatible patterns"
        elif risk < 0.6:
            return "Moderate Risk - Neutral patterns"
        elif risk < 0.8:
            return "High Risk - Incompatible patterns"
        else:
            return "Very High Risk - Highly discordant patterns"
    
    def predict_child_name_pattern(self, parent1_name: str, parent2_name: str) -> Dict:
        """
        Predict visual properties of child name from parent names
        
        Tests: Do parents unconsciously blend their name formulas?
        """
        # Get parent encodings
        features1 = self.analyzer.analyze_name(parent1_name)
        features2 = self.analyzer.analyze_name(parent2_name)
        
        enc1 = self.engine.transform(parent1_name, features1, 'hybrid')
        enc2 = self.engine.transform(parent2_name, features2, 'hybrid')
        
        # Predict child pattern (blend of parents)
        predicted_child = {
            'hue': (enc1.hue + enc2.hue) / 2.0,
            'complexity': (enc1.complexity + enc2.complexity) / 2.0,
            'symmetry': (enc1.symmetry + enc2.symmetry) / 2.0,
            'angular_vs_curved': (enc1.angular_vs_curved + enc2.angular_vs_curved) / 2.0,
        }
        
        # Test for dominant/recessive patterns
        # (If mother's harshness > father's, child tends toward mother?)
        
        return {
            'predicted_properties': predicted_child,
            'inheritance_model': 'blended',
            'confidence': 0.5,  # Will increase with training data
        }
    
    def analyze_pet_compatibility(self, owner_name: str, pet_name: str) -> Dict:
        """
        Analyze owner-pet name relationship
        
        Tests: Do people project identity onto pets?
        """
        relationship = self.analyze_relationship(owner_name, pet_name)
        
        # Hypotheses to test:
        # 1. Compensation: Harsh owner → soft pet name
        # 2. Extension: Similar patterns (identity extension)
        # 3. Completion: Pet name fills gaps in owner pattern
        
        owner_enc = relationship.encoding1
        pet_enc = relationship.encoding2
        
        # Compensation test
        is_compensatory = (
            (owner_enc.angular_vs_curved > 0.5 and pet_enc.angular_vs_curved < -0.5) or
            (owner_enc.angular_vs_curved < -0.5 and pet_enc.angular_vs_curved > 0.5)
        )
        
        # Extension test
        is_extension = relationship.distance_score < 0.3  # Very similar
        
        # Completion test (approaches golden ratio)
        is_completion = relationship.golden_ratio_proximity > 0.7
        
        pattern = 'compensatory' if is_compensatory else 'extension' if is_extension else 'completion' if is_completion else 'neutral'
        
        return {
            'pattern_type': pattern,
            'similarity': 1.0 - relationship.distance_score,
            'projection_score': relationship.compatibility_score,
            'interpretation': self._interpret_pet_pattern(pattern)
        }
    
    def _interpret_pet_pattern(self, pattern: str) -> str:
        """Interpret pet naming pattern"""
        interpretations = {
            'compensatory': "Pet name compensates for owner traits (seeking balance)",
            'extension': "Pet name extends owner identity (projection)",
            'completion': "Pet name completes owner pattern (golden ratio seeking)",
            'neutral': "No clear pattern detected"
        }
        return interpretations.get(pattern, "Unknown pattern")


# =============================================================================
# Batch Relationship Analysis
# =============================================================================

class RelationshipBatchAnalyzer:
    """Analyze relationships in bulk for research"""
    
    def __init__(self):
        self.engine = RelationshipFormulaEngine()
    
    def analyze_couples(self, couples: List[Tuple[str, str, str, int]]) -> Dict:
        """
        Analyze marriage/divorce dataset
        
        Args:
            couples: List of (name1, name2, status, duration) tuples
                    status: 'divorced' or 'married'
                    duration: years together
        
        Returns:
            Statistical analysis of patterns
        """
        divorced = []
        married = []
        
        for name1, name2, status, duration in couples:
            relationship = self.engine.analyze_relationship(name1, name2)
            
            data = {
                'names': (name1, name2),
                'encoding': relationship,
                'duration': duration
            }
            
            if status == 'divorced':
                divorced.append(data)
            else:
                married.append(data)
        
        # Calculate statistics
        divorced_compatibility = np.mean([d['encoding'].compatibility_score for d in divorced])
        married_compatibility = np.mean([m['encoding'].compatibility_score for m in married])
        
        divorced_distance = np.mean([d['encoding'].distance_score for d in divorced])
        married_distance = np.mean([m['encoding'].distance_score for m in married])
        
        divorced_golden = np.mean([d['encoding'].golden_ratio_proximity for d in divorced])
        married_golden = np.mean([m['encoding'].golden_ratio_proximity for m in married])
        
        # Effect sizes
        compatibility_effect = married_compatibility - divorced_compatibility
        distance_effect = divorced_distance - married_distance
        golden_effect = married_golden - divorced_golden
        
        return {
            'n_divorced': len(divorced),
            'n_married': len(married),
            'divorced_compatibility': divorced_compatibility,
            'married_compatibility': married_compatibility,
            'compatibility_effect': compatibility_effect,
            'significance': self._test_significance(divorced, married, 'compatibility_score'),
            'conclusion': self._interpret_marriage_results(compatibility_effect, distance_effect, golden_effect)
        }
    
    def _test_significance(self, group1: List, group2: List, property: str) -> Dict:
        """Test statistical significance of difference"""
        from scipy import stats
        
        values1 = [item['encoding'].__dict__[property] for item in group1]
        values2 = [item['encoding'].__dict__[property] for item in group2]
        
        t_stat, p_value = stats.ttest_ind(values1, values2)
        
        return {
            't_statistic': t_stat,
            'p_value': p_value,
            'significant': p_value < 0.05
        }
    
    def _interpret_marriage_results(self, compat_effect: float, dist_effect: float, golden_effect: float) -> str:
        """Interpret the results"""
        if compat_effect > 0.1 and golden_effect > 0.1:
            return "SHOCKING: Married couples have significantly higher compatibility and golden ratio proximity. Name mathematics predicts marriage success!"
        elif compat_effect < -0.1:
            return "UNEXPECTED: Divorced couples actually had higher compatibility. Similarity may predict boredom?"
        elif abs(compat_effect) < 0.05:
            return "NO PATTERN: Name compatibility doesn't predict marriage outcomes."
        else:
            return "WEAK PATTERN: Slight evidence for name compatibility effects."

