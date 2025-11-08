"""
Formula Engine - The Heart of Nominative Visual Transformation

Transforms names into visual encodings using multiple competing mathematical formulas.
Each formula represents a different theory of how linguistic properties map to visual/symbolic space.

This is where we test: What is the mathematical structure of nominative determinism?
"""

import numpy as np
import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import hashlib
import json


@dataclass
class VisualEncoding:
    """Standardized visual representation of a name"""
    
    # Geometry
    shape_type: str  # heart/star/spiral/mandala/polygon/fractal
    complexity: float  # 0.0-1.0 (simple to complex)
    symmetry: float  # 0.0-1.0 (asymmetric to symmetric)
    angular_vs_curved: float  # -1.0 to 1.0 (curved to angular)
    
    # Color
    hue: float  # 0-360 degrees
    saturation: float  # 0-100
    brightness: float  # 0-100
    palette_family: str  # warm/cool/neutral
    
    # Spatial
    x: float  # Normalized -1.0 to 1.0
    y: float  # Normalized -1.0 to 1.0
    z: float  # Depth 0.0-1.0
    rotation: float  # 0-360 degrees
    
    # Texture
    glow_intensity: float  # 0.0-1.0
    fractal_dimension: float  # 1.0-2.0
    pattern_density: float  # 0.0-1.0
    
    # Metadata
    formula_id: str
    name: str
    secret_variable: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict())


class FormulaBase(ABC):
    """Abstract base class for all transformation formulas"""
    
    def __init__(self, formula_id: str, weights: Optional[Dict[str, float]] = None):
        self.formula_id = formula_id
        self.weights = weights or self.default_weights()
        
    @abstractmethod
    def default_weights(self) -> Dict[str, float]:
        """Default parameter weights for this formula"""
        pass
    
    @abstractmethod
    def transform(self, linguistic_features: Dict) -> VisualEncoding:
        """Transform linguistic features to visual encoding"""
        pass
    
    def get_weights(self) -> Dict[str, float]:
        """Get current weights"""
        return self.weights.copy()
    
    def set_weights(self, weights: Dict[str, float]):
        """Update weights"""
        self.weights.update(weights)
    
    def mutate(self, mutation_rate: float = 0.1) -> 'FormulaBase':
        """Create mutated copy of this formula"""
        new_weights = {}
        for key, value in self.weights.items():
            if np.random.random() < mutation_rate:
                # Mutate this weight by ±20%
                delta = value * np.random.uniform(-0.2, 0.2)
                new_weights[key] = np.clip(value + delta, 0.0, 2.0)
            else:
                new_weights[key] = value
        
        return self.__class__(
            formula_id=f"{self.formula_id}_mutated",
            weights=new_weights
        )
    
    @staticmethod
    def crossover(parent1: 'FormulaBase', parent2: 'FormulaBase') -> 'FormulaBase':
        """Breed two formulas to create offspring"""
        if type(parent1) != type(parent2):
            raise ValueError("Cannot crossover different formula types")
        
        new_weights = {}
        for key in parent1.weights.keys():
            # Randomly choose weight from either parent
            new_weights[key] = parent1.weights[key] if np.random.random() < 0.5 else parent2.weights[key]
        
        return parent1.__class__(
            formula_id=f"{parent1.formula_id}_x_{parent2.formula_id}",
            weights=new_weights
        )


class PhoneticFormula(FormulaBase):
    """
    Phonetic-dominant transformation
    Maps sound patterns to visual properties
    Theory: Names "sound" like what they represent
    """
    
    def default_weights(self) -> Dict[str, float]:
        return {
            'harshness_to_angular': 1.0,
            'vowel_ratio_to_curves': 1.0,
            'plosive_to_hue': 1.0,
            'smoothness_to_symmetry': 1.0,
            'complexity_to_fractal': 1.0,
            'power_to_brightness': 1.0,
        }
    
    def transform(self, features: Dict) -> VisualEncoding:
        name = features.get('name', 'Unknown')
        
        # Extract phonetic features
        harshness = features.get('harshness_score', 0.5)
        smoothness = features.get('smoothness_score', 0.5)
        vowel_ratio = features.get('vowel_ratio', 0.4)
        plosive_ratio = features.get('plosive_ratio', 0.2)
        phonetic_complexity = features.get('phonetic_complexity', 0.5)
        power_score = features.get('power_connotation_score', 0.0)
        
        # Geometry: Harshness creates angular shapes
        angular_vs_curved = (harshness - smoothness) * self.weights['harshness_to_angular']
        angular_vs_curved = np.clip(angular_vs_curved, -1.0, 1.0)
        
        # Shape type based on phonetic profile
        if angular_vs_curved > 0.5:
            shape_type = 'star'
        elif angular_vs_curved < -0.5:
            shape_type = 'spiral'
        else:
            shape_type = 'heart'
        
        complexity = phonetic_complexity * self.weights['complexity_to_fractal']
        symmetry = smoothness * self.weights['smoothness_to_symmetry']
        
        # Color: Plosives create warm colors, fricatives cool
        hue = (plosive_ratio * 30 + (1 - vowel_ratio) * 180) * self.weights['plosive_to_hue']
        hue = hue % 360
        
        saturation = 50 + (harshness * 50)
        brightness = 40 + (abs(power_score) / 100 * 60) * self.weights['power_to_brightness']
        
        palette_family = 'warm' if hue < 60 or hue > 300 else 'cool' if hue < 240 else 'neutral'
        
        # Spatial: Phonetic energy determines position
        x = (harshness - 0.5) * 2  # -1 to 1
        y = (vowel_ratio - 0.5) * 2
        z = phonetic_complexity
        rotation = (plosive_ratio * 360) % 360
        
        # Texture
        glow_intensity = smoothness
        fractal_dimension = 1.0 + phonetic_complexity
        pattern_density = harshness
        
        return VisualEncoding(
            shape_type=shape_type,
            complexity=complexity,
            symmetry=symmetry,
            angular_vs_curved=angular_vs_curved,
            hue=hue,
            saturation=saturation,
            brightness=brightness,
            palette_family=palette_family,
            x=x,
            y=y,
            z=z,
            rotation=rotation,
            glow_intensity=glow_intensity,
            fractal_dimension=fractal_dimension,
            pattern_density=pattern_density,
            formula_id=self.formula_id,
            name=name
        )


class SemanticFormula(FormulaBase):
    """
    Semantic-dominant transformation
    Maps meaning categories to symbolic forms
    Theory: Names mean what they represent
    """
    
    def default_weights(self) -> Dict[str, float]:
        return {
            'category_to_shape': 1.0,
            'meaning_to_hue': 1.0,
            'power_to_size': 1.0,
            'prestige_to_brightness': 1.0,
            'semantic_density': 1.0,
        }
    
    def transform(self, features: Dict) -> VisualEncoding:
        name = features.get('name', 'Unknown')
        
        # Semantic categories
        name_type = features.get('name_type', 'unknown')
        semantic_category = features.get('semantic_category', 'neutral')
        
        # Semantic scores
        authority_score = features.get('authority_score', 50) / 100
        prestige_score = features.get('prestige_score', 50) / 100
        power_score = features.get('power_connotation_score', 0) / 100
        
        # Geometry: Category determines shape
        category_shapes = {
            'animal': 'spiral',
            'tech': 'polygon',
            'mythological': 'star',
            'financial': 'mandala',
            'astronomical': 'spiral',
            'elemental': 'fractal',
            'religious': 'mandala',
            'geographic': 'polygon',
        }
        
        shape_type = 'heart'  # default
        for cat, shape in category_shapes.items():
            if cat in name_type.lower() or cat in semantic_category.lower():
                shape_type = shape
                break
        
        complexity = authority_score * self.weights['semantic_density']
        symmetry = prestige_score
        angular_vs_curved = power_score * 2 - 1  # -1 to 1
        
        # Color: Semantic meaning to hue
        semantic_hues = {
            'tech': 200,  # Blue
            'financial': 45,  # Gold
            'mythological': 280,  # Purple
            'animal': 120,  # Green
            'astronomical': 240,  # Deep blue
            'elemental': 15,  # Orange-red
            'religious': 300,  # Magenta
            'geographic': 180,  # Cyan
        }
        
        hue = 180  # default cyan
        for cat, h in semantic_hues.items():
            if cat in name_type.lower() or cat in semantic_category.lower():
                hue = h
                break
        
        hue = (hue * self.weights['meaning_to_hue']) % 360
        
        saturation = 40 + (authority_score * 60)
        brightness = 30 + (prestige_score * 70) * self.weights['prestige_to_brightness']
        
        palette_family = 'warm' if hue < 60 or hue > 300 else 'cool' if hue < 240 else 'neutral'
        
        # Spatial
        x = (authority_score - 0.5) * 2
        y = (prestige_score - 0.5) * 2
        z = complexity
        rotation = (hue * self.weights['category_to_shape']) % 360
        
        # Texture
        glow_intensity = prestige_score
        fractal_dimension = 1.0 + authority_score
        pattern_density = complexity
        
        return VisualEncoding(
            shape_type=shape_type,
            complexity=complexity,
            symmetry=symmetry,
            angular_vs_curved=angular_vs_curved,
            hue=hue,
            saturation=saturation,
            brightness=brightness,
            palette_family=palette_family,
            x=x,
            y=y,
            z=z,
            rotation=rotation,
            glow_intensity=glow_intensity,
            fractal_dimension=fractal_dimension,
            pattern_density=pattern_density,
            formula_id=self.formula_id,
            name=name
        )


class StructuralFormula(FormulaBase):
    """
    Structural-dominant transformation
    Maps syllables, symmetry, length to geometric patterns
    Theory: Names have structural patterns that predict outcomes
    """
    
    def default_weights(self) -> Dict[str, float]:
        return {
            'syllables_to_symmetry': 1.0,
            'length_to_complexity': 1.0,
            'structure_to_rotation': 1.0,
            'balance_to_position': 1.0,
        }
    
    def transform(self, features: Dict) -> VisualEncoding:
        name = features.get('name', 'Unknown')
        
        # Structural features
        syllables = features.get('syllable_count', 2)
        char_length = features.get('character_length', 5)
        word_count = features.get('word_count', 1)
        
        # Symmetry analysis
        name_str = name.lower()
        is_palindrome = name_str == name_str[::-1]
        
        # Calculate structural balance
        if len(name_str) > 0:
            first_half = name_str[:len(name_str)//2]
            second_half = name_str[len(name_str)//2:]
            balance = 1.0 - (abs(len(first_half) - len(second_half)) / len(name_str))
        else:
            balance = 0.5
        
        # Geometry: Structure determines shape
        if syllables == 1:
            shape_type = 'heart'
        elif syllables == 2:
            shape_type = 'mandala'
        elif syllables == 3:
            shape_type = 'star'
        else:
            shape_type = 'spiral'
        
        complexity = min(char_length / 15, 1.0) * self.weights['length_to_complexity']
        symmetry = (1.0 if is_palindrome else balance) * self.weights['syllables_to_symmetry']
        
        # Angular vs curved based on consonant/vowel structure
        vowel_ratio = features.get('vowel_ratio', 0.4)
        angular_vs_curved = (0.5 - vowel_ratio) * 2  # More vowels = more curved
        
        # Color: Structure to hue (golden ratio progression)
        golden_ratio = 1.618033988749
        hue = ((syllables * golden_ratio * 137.5) % 360) * self.weights['structure_to_rotation']
        
        saturation = 30 + (complexity * 70)
        brightness = 40 + (symmetry * 60)
        
        palette_family = 'warm' if hue < 60 or hue > 300 else 'cool' if hue < 240 else 'neutral'
        
        # Spatial: Structure creates position
        x = (syllables / 5 - 0.5) * 2 * self.weights['balance_to_position']
        x = np.clip(x, -1.0, 1.0)
        y = (word_count / 3 - 0.5) * 2
        y = np.clip(y, -1.0, 1.0)
        z = complexity
        rotation = (syllables * 72) % 360  # Pentagonal symmetry
        
        # Texture
        glow_intensity = symmetry
        fractal_dimension = 1.0 + (syllables / 5)
        pattern_density = complexity
        
        return VisualEncoding(
            shape_type=shape_type,
            complexity=complexity,
            symmetry=symmetry,
            angular_vs_curved=angular_vs_curved,
            hue=hue,
            saturation=saturation,
            brightness=brightness,
            palette_family=palette_family,
            x=x,
            y=y,
            z=z,
            rotation=rotation,
            glow_intensity=glow_intensity,
            fractal_dimension=fractal_dimension,
            pattern_density=pattern_density,
            formula_id=self.formula_id,
            name=name
        )


class FrequencyFormula(FormulaBase):
    """
    Frequency-based transformation
    Maps letter frequencies and n-grams to wave patterns
    Theory: Names have spectral signatures like music
    """
    
    def default_weights(self) -> Dict[str, float]:
        return {
            'frequency_to_hue': 1.0,
            'entropy_to_complexity': 1.0,
            'repetition_to_pattern': 1.0,
            'rhythm_to_rotation': 1.0,
        }
    
    def transform(self, features: Dict) -> VisualEncoding:
        name = features.get('name', 'Unknown')
        name_lower = name.lower()
        
        # Calculate letter frequencies
        letter_counts = {}
        for char in name_lower:
            if char.isalpha():
                letter_counts[char] = letter_counts.get(char, 0) + 1
        
        # Entropy (information density)
        total_chars = sum(letter_counts.values())
        if total_chars > 0:
            entropy = 0
            for count in letter_counts.values():
                p = count / total_chars
                if p > 0:
                    entropy -= p * math.log2(p)
            # Normalize by max possible entropy
            max_entropy = math.log2(min(total_chars, 26))
            if max_entropy > 0:
                entropy = entropy / max_entropy
            else:
                entropy = 0
        else:
            entropy = 0
        
        # Repetition score
        unique_chars = len(letter_counts)
        repetition = 1.0 - (unique_chars / max(total_chars, 1))
        
        # Calculate "dominant frequency" (most common letter's ASCII value)
        if letter_counts:
            dominant_char = max(letter_counts.items(), key=lambda x: x[1])[0]
            dominant_freq = ord(dominant_char) - ord('a')  # 0-25
        else:
            dominant_freq = 13
        
        # Geometry
        if entropy > 0.8:
            shape_type = 'fractal'
        elif repetition > 0.5:
            shape_type = 'spiral'
        else:
            shape_type = 'star'
        
        complexity = entropy * self.weights['entropy_to_complexity']
        symmetry = repetition * self.weights['repetition_to_pattern']
        angular_vs_curved = (entropy - 0.5) * 2  # High entropy = angular
        
        # Color: Frequency spectrum
        hue = (dominant_freq * 360 / 26) * self.weights['frequency_to_hue']
        hue = hue % 360
        
        saturation = 50 + (entropy * 50)
        brightness = 40 + (repetition * 60)
        
        palette_family = 'warm' if hue < 60 or hue > 300 else 'cool' if hue < 240 else 'neutral'
        
        # Spatial: Frequency space
        x = (dominant_freq / 26 - 0.5) * 2
        y = (entropy - 0.5) * 2
        z = complexity
        rotation = (dominant_freq * 13.846) % 360 * self.weights['rhythm_to_rotation']  # Magic number
        
        # Texture
        glow_intensity = entropy
        fractal_dimension = 1.0 + entropy
        pattern_density = repetition
        
        return VisualEncoding(
            shape_type=shape_type,
            complexity=complexity,
            symmetry=symmetry,
            angular_vs_curved=angular_vs_curved,
            hue=hue,
            saturation=saturation,
            brightness=brightness,
            palette_family=palette_family,
            x=x,
            y=y,
            z=z,
            rotation=rotation,
            glow_intensity=glow_intensity,
            fractal_dimension=fractal_dimension,
            pattern_density=pattern_density,
            formula_id=self.formula_id,
            name=name
        )


class NumerologicalFormula(FormulaBase):
    """
    Numerological transformation
    Maps character values to sacred geometry
    Theory: Names encode numerical patterns with cosmic significance
    """
    
    def default_weights(self) -> Dict[str, float]:
        return {
            'pythagorean_to_hue': 1.0,
            'golden_ratio_factor': 1.0,
            'fibonacci_influence': 1.0,
            'prime_pattern': 1.0,
        }
    
    def transform(self, features: Dict) -> VisualEncoding:
        name = features.get('name', 'Unknown')
        name_lower = name.lower()
        
        # Pythagorean numerology (A=1, B=2, ..., Z=26, reduce to 1-9)
        def reduce_to_single(n):
            while n > 9:
                n = sum(int(d) for d in str(n))
            return n
        
        char_sum = sum(ord(c) - ord('a') + 1 for c in name_lower if c.isalpha())
        pythagorean_number = reduce_to_single(char_sum)
        
        # Full sum (no reduction)
        full_sum = char_sum
        
        # Golden ratio relationship
        golden_ratio = 1.618033988749
        golden_phase = (full_sum * golden_ratio) % 1.0
        
        # Fibonacci proximity
        fib_sequence = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377]
        closest_fib = min(fib_sequence, key=lambda x: abs(x - full_sum))
        fib_proximity = 1.0 - min(abs(full_sum - closest_fib) / full_sum, 1.0) if full_sum > 0 else 0
        
        # Prime check
        def is_prime(n):
            if n < 2:
                return False
            for i in range(2, int(math.sqrt(n)) + 1):
                if n % i == 0:
                    return False
            return True
        
        prime_factor = 1.0 if is_prime(full_sum) else 0.5
        
        # Geometry: Numerological shapes
        shapes_by_number = {
            1: 'heart',      # Unity
            2: 'mandala',    # Duality
            3: 'star',       # Trinity
            4: 'polygon',    # Stability
            5: 'star',       # Human/pentagram
            6: 'mandala',    # Harmony
            7: 'fractal',    # Mystery
            8: 'mandala',    # Infinity
            9: 'spiral',     # Completion
        }
        shape_type = shapes_by_number.get(pythagorean_number, 'heart')
        
        complexity = (pythagorean_number / 9) * self.weights['fibonacci_influence']
        symmetry = golden_phase * self.weights['golden_ratio_factor']
        angular_vs_curved = (pythagorean_number / 9 - 0.5) * 2
        
        # Color: Golden angle and Pythagorean number
        golden_angle = 137.508  # degrees
        hue = (pythagorean_number * golden_angle) % 360 * self.weights['pythagorean_to_hue']
        
        saturation = 40 + (fib_proximity * 60)
        brightness = 30 + (prime_factor * 70)
        
        palette_family = 'warm' if hue < 60 or hue > 300 else 'cool' if hue < 240 else 'neutral'
        
        # Spatial: Sacred geometry positions
        x = math.cos(golden_phase * 2 * math.pi)
        y = math.sin(golden_phase * 2 * math.pi)
        z = fib_proximity
        rotation = (pythagorean_number * 40) % 360
        
        # Texture
        glow_intensity = prime_factor
        fractal_dimension = 1.0 + (pythagorean_number / 9)
        pattern_density = fib_proximity * self.weights['prime_pattern']
        
        return VisualEncoding(
            shape_type=shape_type,
            complexity=complexity,
            symmetry=symmetry,
            angular_vs_curved=angular_vs_curved,
            hue=hue,
            saturation=saturation,
            brightness=brightness,
            palette_family=palette_family,
            x=x,
            y=y,
            z=z,
            rotation=rotation,
            glow_intensity=glow_intensity,
            fractal_dimension=fractal_dimension,
            pattern_density=pattern_density,
            formula_id=self.formula_id,
            name=name
        )


class HybridFormula(FormulaBase):
    """
    Hybrid transformation
    Weighted combination of all other approaches
    Theory: Reality is multi-dimensional, truth emerges from synthesis
    """
    
    def __init__(self, formula_id: str = "hybrid", weights: Optional[Dict[str, float]] = None):
        super().__init__(formula_id, weights)
        
        # Initialize sub-formulas
        self.phonetic = PhoneticFormula("phonetic_sub")
        self.semantic = SemanticFormula("semantic_sub")
        self.structural = StructuralFormula("structural_sub")
        self.frequency = FrequencyFormula("frequency_sub")
        self.numerological = NumerologicalFormula("numerological_sub")
    
    def default_weights(self) -> Dict[str, float]:
        return {
            'phonetic_weight': 0.2,
            'semantic_weight': 0.2,
            'structural_weight': 0.2,
            'frequency_weight': 0.2,
            'numerological_weight': 0.2,
        }
    
    def transform(self, features: Dict) -> VisualEncoding:
        name = features.get('name', 'Unknown')
        
        # Get encodings from all sub-formulas
        encodings = {
            'phonetic': self.phonetic.transform(features),
            'semantic': self.semantic.transform(features),
            'structural': self.structural.transform(features),
            'frequency': self.frequency.transform(features),
            'numerological': self.numerological.transform(features),
        }
        
        # Weighted average of numerical properties
        def weighted_avg(attr):
            total = 0.0
            total_weight = 0.0
            for name, enc in encodings.items():
                weight = self.weights.get(f"{name}_weight", 0.2)
                total += getattr(enc, attr) * weight
                total_weight += weight
            return total / total_weight if total_weight > 0 else 0.0
        
        # Shape type: Vote by weight
        shape_votes = {}
        for name, enc in encodings.items():
            weight = self.weights.get(f"{name}_weight", 0.2)
            shape_votes[enc.shape_type] = shape_votes.get(enc.shape_type, 0) + weight
        shape_type = max(shape_votes.items(), key=lambda x: x[1])[0]
        
        # Palette: Vote by weight
        palette_votes = {}
        for name, enc in encodings.items():
            weight = self.weights.get(f"{name}_weight", 0.2)
            palette_votes[enc.palette_family] = palette_votes.get(enc.palette_family, 0) + weight
        palette_family = max(palette_votes.items(), key=lambda x: x[1])[0]
        
        return VisualEncoding(
            shape_type=shape_type,
            complexity=weighted_avg('complexity'),
            symmetry=weighted_avg('symmetry'),
            angular_vs_curved=weighted_avg('angular_vs_curved'),
            hue=weighted_avg('hue'),
            saturation=weighted_avg('saturation'),
            brightness=weighted_avg('brightness'),
            palette_family=palette_family,
            x=weighted_avg('x'),
            y=weighted_avg('y'),
            z=weighted_avg('z'),
            rotation=weighted_avg('rotation'),
            glow_intensity=weighted_avg('glow_intensity'),
            fractal_dimension=weighted_avg('fractal_dimension'),
            pattern_density=weighted_avg('pattern_density'),
            formula_id=self.formula_id,
            name=name
        )


class FormulaEngine:
    """
    Main engine for managing and applying transformation formulas
    """
    
    def __init__(self):
        self.formulas: Dict[str, FormulaBase] = {}
        self._register_default_formulas()
    
    def _register_default_formulas(self):
        """Register the 6 base formula types"""
        self.register_formula(PhoneticFormula("phonetic"))
        self.register_formula(SemanticFormula("semantic"))
        self.register_formula(StructuralFormula("structural"))
        self.register_formula(FrequencyFormula("frequency"))
        self.register_formula(NumerologicalFormula("numerological"))
        self.register_formula(HybridFormula("hybrid"))
    
    def register_formula(self, formula: FormulaBase):
        """Register a formula"""
        self.formulas[formula.formula_id] = formula
    
    def get_formula(self, formula_id: str) -> Optional[FormulaBase]:
        """Get formula by ID"""
        return self.formulas.get(formula_id)
    
    def list_formulas(self) -> List[str]:
        """List all registered formula IDs"""
        return list(self.formulas.keys())
    
    def transform(self, name: str, linguistic_features: Dict, formula_id: str = "hybrid") -> VisualEncoding:
        """
        Transform a name using specified formula
        
        Args:
            name: The name to transform
            linguistic_features: Dictionary of linguistic features
            formula_id: Which formula to use
            
        Returns:
            VisualEncoding object
        """
        formula = self.get_formula(formula_id)
        if not formula:
            raise ValueError(f"Unknown formula: {formula_id}")
        
        # Ensure name is in features
        linguistic_features['name'] = name
        
        return formula.transform(linguistic_features)
    
    def transform_all(self, name: str, linguistic_features: Dict) -> Dict[str, VisualEncoding]:
        """
        Transform using all registered formulas
        
        Returns:
            Dictionary mapping formula_id to VisualEncoding
        """
        linguistic_features['name'] = name
        results = {}
        
        for formula_id, formula in self.formulas.items():
            results[formula_id] = formula.transform(linguistic_features)
        
        return results
    
    def create_random_formula(self, base_type: str = "hybrid") -> FormulaBase:
        """Create a formula with random weights"""
        formula_classes = {
            'phonetic': PhoneticFormula,
            'semantic': SemanticFormula,
            'structural': StructuralFormula,
            'frequency': FrequencyFormula,
            'numerological': NumerologicalFormula,
            'hybrid': HybridFormula,
        }
        
        formula_class = formula_classes.get(base_type, HybridFormula)
        default_weights = formula_class("temp").default_weights()
        
        # Randomize weights
        random_weights = {
            key: np.random.uniform(0.1, 2.0)
            for key in default_weights.keys()
        }
        
        formula_id = f"{base_type}_random_{np.random.randint(10000)}"
        return formula_class(formula_id, random_weights)

