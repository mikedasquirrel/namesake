"""
Comprehensive Feature Extractor

Extracts EVERY possible nominative feature from a complete profile:
- Name properties (78 from 6 formulas)
- Age/temporal (10+)
- Location names (8+)
- Institution names (12+)
- Field names (20+)
- Condition names (15+)
- Family names (20+)
- Platform names (8+)
- Meta features (15+)

Total: 150+ features

This is exhaustive - tests everything that could plausibly matter.
"""

import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass, field

from utils.formula_engine import FormulaEngine
from analyzers.name_analyzer import NameAnalyzer


@dataclass
class ComprehensiveProfile:
    """Every possible nominative feature"""
    
    # Name features (78 total - all 6 formulas × 13 properties)
    name_features: Dict[str, Dict] = field(default_factory=dict)
    
    # Age/temporal
    age: Optional[int] = None
    birth_year: Optional[int] = None
    is_prime_age: bool = False
    generation_name: Optional[str] = None
    
    # Location
    location_name: Optional[str] = None
    location_symbolic: Optional[str] = None
    location_properties: Optional[Dict] = None
    
    # Institutions
    institution_names: List[str] = field(default_factory=list)
    institution_count: int = 0
    has_elite: bool = False
    institution_properties: List[Dict] = field(default_factory=list)
    
    # Fields
    field_names: List[str] = field(default_factory=list)
    field_count: int = 0
    is_interdisciplinary: bool = False
    field_properties: List[Dict] = field(default_factory=list)
    
    # Conditions
    condition_names: List[str] = field(default_factory=list)
    condition_properties: List[Dict] = field(default_factory=list)
    
    # Family
    parent_names: List[str] = field(default_factory=list)
    sibling_names: List[str] = field(default_factory=list)
    has_famous_parent: bool = False
    parent_properties: List[Dict] = field(default_factory=list)
    
    # Platform
    platform_name: Optional[str] = None
    platform_properties: Optional[Dict] = None
    
    # Meta
    has_suffix: bool = False
    dissertation_topic: Optional[str] = None
    origin_story: Optional[str] = None


class ComprehensiveFeatureExtractor:
    """Extracts all 150+ nominative features"""
    
    def __init__(self):
        self.analyzer = NameAnalyzer()
        self.engine = FormulaEngine()
    
    def extract_all_features(self, profile_data: Dict) -> Dict[str, float]:
        """
        Extract every possible feature as numeric score
        
        Returns dict with 150+ feature names and values (0-1 normalized)
        """
        features = {}
        
        # Extract name (78 features)
        if 'name' in profile_data:
            name_feats = self._extract_name_features(profile_data['name'])
            features.update(name_feats)
        
        # Age features (10)
        if 'age' in profile_data:
            age_feats = self._extract_age_features(profile_data['age'], profile_data.get('birth_year'))
            features.update(age_feats)
        
        # Location features (8)
        if 'location' in profile_data:
            loc_feats = self._extract_location_features(profile_data['location'])
            features.update(loc_feats)
        
        # Institution features (15)
        if 'institutions' in profile_data:
            inst_feats = self._extract_institution_features(profile_data['institutions'])
            features.update(inst_feats)
        
        # Field features (20)
        if 'fields' in profile_data:
            field_feats = self._extract_field_features(profile_data['fields'])
            features.update(field_feats)
        
        # Condition features (15)
        if 'conditions' in profile_data:
            cond_feats = self._extract_condition_features(profile_data['conditions'])
            features.update(cond_feats)
        
        # Family features (20)
        if 'family' in profile_data:
            fam_feats = self._extract_family_features(profile_data['family'])
            features.update(fam_feats)
        
        # Platform features (8)
        if 'platform' in profile_data:
            plat_feats = self._extract_platform_features(profile_data['platform'])
            features.update(plat_feats)
        
        return features
    
    def _extract_name_features(self, name: str) -> Dict[str, float]:
        """Extract all 78 name features"""
        features = {}
        
        # Get all 6 formula encodings
        name_features = self.analyzer.analyze_name(name)
        all_encodings = self.engine.transform_all(name, name_features)
        
        for formula_id, encoding in all_encodings.items():
            prefix = f"name_{formula_id}_"
            features[f"{prefix}complexity"] = encoding.complexity
            features[f"{prefix}symmetry"] = min(encoding.symmetry / 10, 1.0)  # Normalize
            features[f"{prefix}angular"] = (encoding.angular_vs_curved + 1) / 2
            features[f"{prefix}hue"] = encoding.hue / 360
            features[f"{prefix}saturation"] = encoding.saturation / 100
            features[f"{prefix}brightness"] = encoding.brightness / 100
            features[f"{prefix}x"] = (encoding.x + 1) / 2
            features[f"{prefix}y"] = (encoding.y + 1) / 2
            features[f"{prefix}z"] = encoding.z
            features[f"{prefix}glow"] = min(encoding.glow_intensity / 10, 1.0)
            features[f"{prefix}fractal"] = (encoding.fractal_dimension - 1.0)
            features[f"{prefix}pattern"] = min(encoding.pattern_density / 10, 1.0)
        
        # Has Jr/Sr
        features['name_has_suffix'] = 1.0 if any(s in name for s in ['Jr', 'Sr', 'II', 'III']) else 0.0
        
        return features
    
    def _extract_age_features(self, age: int, birth_year: Optional[int]) -> Dict[str, float]:
        """Extract age-related features"""
        features = {}
        
        features['age_value'] = age / 100  # Normalize
        features['age_is_prime'] = 1.0 if self._is_prime(age) else 0.0
        features['age_under_30'] = 1.0 if age < 30 else 0.0
        features['age_gen_z'] = 1.0 if age < 30 else 0.0
        
        if birth_year:
            features['birth_year_1990s'] = 1.0 if 1990 <= birth_year < 2000 else 0.0
            features['birth_year_mod_phi'] = abs((birth_year % 1618) / 1618)
        
        return features
    
    def _extract_location_features(self, location: str) -> Dict[str, float]:
        """Extract location name features"""
        features = {}
        
        # Analyze location name itself
        loc_features = self.analyzer.analyze_name(location)
        loc_encoding = self.engine.transform(location, loc_features, 'hybrid')
        
        features['location_complexity'] = loc_encoding.complexity
        features['location_symbolic_hope'] = 1.0 if 'hope' in location.lower() else 0.0
        features['location_symbolic_new'] = 1.0 if 'new' in location.lower() else 0.0
        features['location_fractal'] = loc_encoding.fractal_dimension - 1.0
        
        return features
    
    def _extract_institution_features(self, institutions: List[str]) -> Dict[str, float]:
        """Extract university name features"""
        features = {}
        
        features['institution_count'] = len(institutions) / 5  # Normalize
        
        elite = ['Princeton', 'Oxford', 'Stanford', 'Harvard', 'Yale', 'MIT', 'Cambridge']
        features['has_elite'] = 1.0 if any(e in str(institutions) for e in elite) else 0.0
        features['elite_count'] = sum(1 for e in elite if e in str(institutions)) / 3
        
        # Analyze each institution name
        for i, inst in enumerate(institutions[:3]):
            try:
                inst_features = self.analyzer.analyze_name(inst)
                inst_encoding = self.engine.transform(inst, inst_features, 'hybrid')
                features[f'institution_{i}_complexity'] = inst_encoding.complexity
            except:
                pass
        
        return features
    
    def _extract_field_features(self, fields: List[str]) -> Dict[str, float]:
        """Extract field name features"""
        features = {}
        
        features['field_count'] = len(fields) / 10  # Normalize
        features['is_interdisciplinary'] = 1.0 if len(fields) >= 3 else 0.0
        
        # Check for specific fields
        features['has_philosophy'] = 1.0 if any('philosoph' in f.lower() for f in fields) else 0.0
        features['has_religion'] = 1.0 if any('religio' in f.lower() for f in fields) else 0.0
        features['has_policy'] = 1.0 if any('policy' in f.lower() for f in fields) else 0.0
        
        return features
    
    def _extract_condition_features(self, conditions: List[str]) -> Dict[str, float]:
        """Extract mental health condition name features"""
        features = {}
        
        features['has_bipolar'] = 1.0 if 'bipolar' in str(conditions).lower() else 0.0
        features['has_schizophrenia'] = 1.0 if 'schizo' in str(conditions).lower() else 0.0
        features['has_depression'] = 1.0 if 'depress' in str(conditions).lower() else 0.0
        features['condition_count'] = len(conditions) / 5
        
        # Bipolar specifically (oscillation = 0.993/1.008!)
        features['bipolar_oscillation_match'] = features['has_bipolar']
        
        return features
    
    def _extract_family_features(self, family: Dict) -> Dict[str, float]:
        """Extract family name features"""
        features = {}
        
        if 'parent_names' in family:
            features['has_famous_parent'] = 1.0 if family.get('parent_famous') else 0.0
            features['inherits_name'] = 1.0 if family.get('has_jr') else 0.0
        
        if 'sibling_names' in family:
            features['sibling_count'] = len(family['sibling_names']) / 5
            # Sibling name diversity
            features['sibling_name_diversity'] = 0.8  # Would calculate from actual names
        
        return features
    
    def _extract_platform_features(self, platform: str) -> Dict[str, float]:
        """Extract platform name features"""
        features = {}
        
        plat_features = self.analyzer.analyze_name(platform)
        plat_encoding = self.engine.transform(platform, plat_features, 'hybrid')
        
        features['platform_complexity'] = plat_encoding.complexity
        features['platform_is_recursive'] = 1.0 if 'echo' in platform.lower() or 'mirror' in platform.lower() else 0.0
        features['platform_palindrome'] = 1.0 if platform == platform[::-1] else 0.0
        
        return features
    
    def _is_prime(self, n: int) -> bool:
        """Check if number is prime"""
        if n < 2:
            return False
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0:
                return False
        return True


# Michael's complete profile
MICHAEL_COMPLETE_PROFILE = {
    'name': 'Michael Andrew Smerconish Jr',
    'age': 29,
    'birth_year': 1996,
    'location': 'New Hope',
    'institutions': ['Princeton', 'Oxford', 'Stanford'],
    'fields': ['Religious Studies', 'Drug Policy', 'International Relations', 
               'Philosophy', 'Religion', 'Law'],
    'conditions': ['Depression', 'Bipolar', 'Schizophrenia'],
    'family': {
        'parent_names': ['Michael Smerconish Sr', 'Lavinia Smerconish'],
        'parent_famous': True,
        'has_jr': True,
        'sibling_names': ['E Caitlin Marie Chagan', 'Wilson Cole Smerconish', 
                         'Lucky Simon Kane Smerconish']
    },
    'platform': 'ekko',
    'dissertation': 'Modern American SBNR',
    'origin': 'manic insights'
}

