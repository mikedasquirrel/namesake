"""
Relationship Formulas - Combine Two Names into Compatibility Scores

Tests the shocking hypothesis: Can we predict relationship outcomes 
(marriage success, divorce, parent-child patterns, pet compatibility)
from name mathematics alone?

This is where nominative determinism gets DEEP.
"""

import numpy as np
from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass
import math

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
    
    # Pattern type
    relationship_type: str  # harmonic/complementary/discordant
    
    # Individual encodings
    encoding1: VisualEncoding
    encoding2: VisualEncoding
    
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
                           formula_id: str = 'hybrid') -> RelationshipEncoding:
        """
        Analyze compatibility between two names
        
        Args:
            name1: First name
            name2: Second name
            formula_id: Which formula to use
            
        Returns:
            RelationshipEncoding with compatibility metrics
        """
        # Get individual encodings
        features1 = self.analyzer.analyze_name(name1)
        features2 = self.analyzer.analyze_name(name2)
        
        encoding1 = self.engine.transform(name1, features1, formula_id)
        encoding2 = self.engine.transform(name2, features2, formula_id)
        
        # Calculate relationship metrics
        compatibility = self._calculate_compatibility(encoding1, encoding2)
        distance = self._calculate_distance(encoding1, encoding2)
        resonance = self._calculate_resonance(encoding1, encoding2)
        balance = self._calculate_balance(encoding1, encoding2)
        golden_proximity = self._test_golden_ratio(encoding1, encoding2)
        color_harmony = self._test_color_harmony(encoding1, encoding2)
        complexity_balance = self._test_complexity_balance(encoding1, encoding2)
        symmetry_match = self._test_symmetry_match(encoding1, encoding2)
        
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
            relationship_type=rel_type,
            encoding1=encoding1,
            encoding2=encoding2
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

