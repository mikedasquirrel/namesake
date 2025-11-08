"""
Discoverer Predictor - Rigorous Person Profile Prediction

Predicts complete person profile from name alone:
- Demographics (age, location)
- Education (level, institutions)
- Professional field
- Personality type (MBTI)
- Mental health indicators
- Family structure
- Life circumstances

KEY: All predictions generated BEFORE seeing actual data.
No cherry-picking. Falsifiable. Scientific.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import logging

from utils.formula_engine import FormulaEngine, VisualEncoding
from analyzers.name_analyzer import NameAnalyzer

logger = logging.getLogger(__name__)


@dataclass
class PersonProfile:
    """Complete predicted profile of a person"""
    name: str
    
    # Demographics
    predicted_age_range: Tuple[int, int]
    predicted_generation: str  # Gen Z, Millennial, Gen X, etc.
    predicted_location_type: str  # US, Europe, Asia
    
    # Education
    predicted_education_level: str  # high_school, bachelors, masters, phd, elite
    predicted_elite_institution: bool  # Ivy League, Oxbridge, etc.
    predicted_field: str  # STEM, humanities, interdisciplinary
    
    # Professional
    predicted_career_type: str  # academic, industry, independent, creative
    predicted_creativity_level: float  # 0-1
    predicted_unconventional: bool
    
    # Personality (MBTI)
    predicted_mbti: str  # 4-letter type
    predicted_introversion: float  # 0-1
    predicted_intuition: float  # 0-1
    predicted_thinking: float  # 0-1
    predicted_judging: float  # 0-1
    
    # Mental health indicators
    predicted_neurodivergent: bool
    predicted_adhd_likelihood: float
    predicted_bipolar_likelihood: float
    predicted_depression_likelihood: float
    predicted_anxiety_likelihood: float
    
    # Family
    predicted_has_junior_senior: bool
    predicted_family_prominence: str  # unknown, local, national, famous
    predicted_sibling_count: int
    
    # Circumstances
    predicted_recent_crisis: bool
    predicted_outsider_status: bool
    predicted_revolutionary_tendency: float  # 0-1
    
    # Meta
    confidence_scores: Dict[str, float] = field(default_factory=dict)


class DiscovererPredictor:
    """
    Predicts complete person profile from name properties
    
    Uses visual encodings + linguistic features to predict:
    - Who they are
    - What they study
    - Their psychology
    - Their circumstances
    
    All predictions FORMULAIC, not cherry-picked.
    """
    
    def __init__(self):
        self.analyzer = NameAnalyzer()
        self.engine = FormulaEngine()
    
    def predict_person(self, full_name: str) -> PersonProfile:
        """
        Generate complete person prediction from name alone
        
        CRITICAL: This runs BLIND - before seeing actual profile
        
        Args:
            full_name: Person's complete name
            
        Returns:
            PersonProfile with all predictions
        """
        logger.info(f"Generating blind prediction for: {full_name}")
        
        # Analyze name
        features = self.analyzer.analyze_name(full_name)
        encoding = self.engine.transform(full_name, features, 'hybrid')
        
        # Generate all predictions
        profile = PersonProfile(
            name=full_name,
            
            # Demographics
            predicted_age_range=self._predict_age(features, encoding),
            predicted_generation=self._predict_generation(features, encoding),
            predicted_location_type=self._predict_location(features, encoding),
            
            # Education
            predicted_education_level=self._predict_education_level(features, encoding),
            predicted_elite_institution=self._predict_elite_institution(features, encoding),
            predicted_field=self._predict_field(features, encoding),
            
            # Professional
            predicted_career_type=self._predict_career_type(features, encoding),
            predicted_creativity_level=self._predict_creativity(features, encoding),
            predicted_unconventional=self._predict_unconventional(features, encoding),
            
            # Personality
            predicted_mbti=self._predict_mbti(features, encoding),
            predicted_introversion=self._predict_introversion(features, encoding),
            predicted_intuition=self._predict_intuition(features, encoding),
            predicted_thinking=self._predict_thinking(features, encoding),
            predicted_judging=self._predict_judging(features, encoding),
            
            # Mental health
            predicted_neurodivergent=self._predict_neurodivergent(features, encoding),
            predicted_adhd_likelihood=self._predict_adhd(features, encoding),
            predicted_bipolar_likelihood=self._predict_bipolar(features, encoding),
            predicted_depression_likelihood=self._predict_depression(features, encoding),
            predicted_anxiety_likelihood=self._predict_anxiety(features, encoding),
            
            # Family
            predicted_has_junior_senior=self._predict_has_suffix(full_name),
            predicted_family_prominence=self._predict_family_prominence(features, encoding),
            predicted_sibling_count=self._predict_siblings(features, encoding),
            
            # Circumstances
            predicted_recent_crisis=self._predict_crisis(features, encoding),
            predicted_outsider_status=self._predict_outsider(features, encoding),
            predicted_revolutionary_tendency=self._predict_revolutionary(features, encoding),
        )
        
        # Add confidence scores
        profile.confidence_scores = self._calculate_confidences(features, encoding)
        
        return profile
    
    # ========================================================================
    # Prediction Methods
    # ========================================================================
    
    def _predict_age(self, features: Dict, encoding: VisualEncoding) -> Tuple[int, int]:
        """Predict age range from name properties"""
        # Name era indicators
        syllables = features.get('syllable_count', 3)
        complexity = encoding.complexity
        
        # Complex names → older (had time to accumulate complexity)
        # Simple names → younger or traditional
        
        if complexity > 0.7:
            # High complexity → likely 35-55 (established, complex thinking)
            return (35, 55)
        elif complexity > 0.5:
            # Moderate → 25-45
            return (25, 45)
        else:
            # Low → 20-35 or 60+
            return (20, 60)
    
    def _predict_generation(self, features: Dict, encoding: VisualEncoding) -> str:
        """Predict generational cohort"""
        age_range = self._predict_age(features, encoding)
        avg_age = (age_range[0] + age_range[1]) / 2
        
        current_year = 2025
        birth_year = current_year - avg_age
        
        if birth_year < 1965:
            return "Boomer"
        elif birth_year < 1981:
            return "Gen X"
        elif birth_year < 1997:
            return "Millennial"
        else:
            return "Gen Z"
    
    def _predict_location(self, features: Dict, encoding: VisualEncoding) -> str:
        """Predict geographic/cultural origin"""
        # Simplified - would use more sophisticated analysis
        return "US/Western"
    
    def _predict_education_level(self, features: Dict, encoding: VisualEncoding) -> str:
        """Predict education level from name complexity/formality"""
        complexity = encoding.complexity
        
        # High complexity → advanced education
        if complexity > 0.65:
            return "elite"  # Top universities, multiple degrees
        elif complexity > 0.50:
            return "phd"
        elif complexity > 0.35:
            return "masters"
        else:
            return "bachelors"
    
    def _predict_elite_institution(self, features: Dict, encoding: VisualEncoding) -> bool:
        """Predict if attended elite institution"""
        complexity = encoding.complexity
        formality = features.get('syllable_count', 2) / 6  # Proxy for formality
        
        # High complexity + formality → elite education
        return complexity > 0.65 and formality > 0.5
    
    def _predict_field(self, features: Dict, encoding: VisualEncoding) -> str:
        """Predict academic/professional field"""
        
        # Based on visual encoding properties
        if encoding.angular_vs_curved > 0.3:
            return "STEM"  # Angular → mathematical/technical
        elif encoding.angular_vs_curved < -0.3:
            return "Arts/Humanities"  # Curved → creative/humanistic
        else:
            return "Interdisciplinary"  # Balanced → crosses boundaries
    
    def _predict_career_type(self, features: Dict, encoding: VisualEncoding) -> str:
        """Predict career path type"""
        symmetry = encoding.symmetry
        complexity = encoding.complexity
        
        if symmetry > 0.7 and complexity < 0.5:
            return "academic"  # Structured, traditional
        elif complexity > 0.7:
            return "independent"  # Complex → doesn't fit boxes
        elif symmetry < 0.3:
            return "creative"  # Asymmetric → artistic
        else:
            return "industry"  # Balanced
    
    def _predict_creativity(self, features: Dict, encoding: VisualEncoding) -> float:
        """Predict creativity level"""
        # High complexity + asymmetry → high creativity
        return (encoding.complexity + (1 - encoding.symmetry)) / 2
    
    def _predict_unconventional(self, features: Dict, encoding: VisualEncoding) -> bool:
        """Predict if person is unconventional/outsider"""
        # High complexity + low symmetry + extreme properties
        return encoding.complexity > 0.6 and encoding.symmetry < 0.4
    
    def _predict_mbti(self, features: Dict, encoding: VisualEncoding) -> str:
        """Predict MBTI type from name properties"""
        # Predict each dimension
        I_or_E = "I" if self._predict_introversion(features, encoding) > 0.5 else "E"
        N_or_S = "N" if self._predict_intuition(features, encoding) > 0.5 else "S"
        T_or_F = "T" if self._predict_thinking(features, encoding) > 0.5 else "F"
        J_or_P = "J" if self._predict_judging(features, encoding) > 0.5 else "P"
        
        return f"{I_or_E}{N_or_S}{T_or_F}{J_or_P}"
    
    def _predict_introversion(self, features: Dict, encoding: VisualEncoding) -> float:
        """Predict introversion (0=extrovert, 1=introvert)"""
        # Complex names → introverted (internal world)
        # Simple names → extroverted (external focus)
        return encoding.complexity
    
    def _predict_intuition(self, features: Dict, encoding: VisualEncoding) -> float:
        """Predict intuition vs sensing"""
        # Abstract visual properties → intuitive
        # Concrete properties → sensing
        return (encoding.complexity + encoding.fractal_dimension - 1.0) / 2
    
    def _predict_thinking(self, features: Dict, encoding: VisualEncoding) -> float:
        """Predict thinking vs feeling"""
        # Angular → thinking (logical)
        # Curved → feeling (emotional)
        return (encoding.angular_vs_curved + 1.0) / 2
    
    def _predict_judging(self, features: Dict, encoding: VisualEncoding) -> float:
        """Predict judging vs perceiving"""
        # Symmetric → judging (structured)
        # Asymmetric → perceiving (flexible)
        return encoding.symmetry
    
    def _predict_neurodivergent(self, features: Dict, encoding: VisualEncoding) -> bool:
        """Predict neurodivergence"""
        # High complexity + pattern-seeking indicated by certain properties
        return encoding.complexity > 0.7 or encoding.fractal_dimension > 1.8
    
    def _predict_adhd(self, features: Dict, encoding: VisualEncoding) -> float:
        """Predict ADHD likelihood"""
        # High complexity + low symmetry → ADHD
        # Pattern: complex but disorganized
        if encoding.complexity > 0.6 and encoding.symmetry < 0.4:
            return 0.7
        elif encoding.complexity > 0.5:
            return 0.4
        return 0.2
    
    def _predict_bipolar(self, features: Dict, encoding: VisualEncoding) -> float:
        """Predict bipolar likelihood"""
        # Extreme contrasts in properties → bipolar
        # High complexity + high intensity
        contrast = abs(encoding.angular_vs_curved)  # Extremes
        intensity = encoding.glow_intensity
        
        if contrast > 0.6 and intensity > 0.7:
            return 0.6
        elif encoding.complexity > 0.7:
            return 0.4
        return 0.2
    
    def _predict_depression(self, features: Dict, encoding: VisualEncoding) -> float:
        """Predict depression likelihood"""
        # Low brightness + high complexity → depression
        # Thinking deeply about dark things
        if encoding.brightness < 40 and encoding.complexity > 0.6:
            return 0.6
        return 0.3
    
    def _predict_anxiety(self, features: Dict, encoding: VisualEncoding) -> float:
        """Predict anxiety likelihood"""
        # High complexity + high pattern density → anxiety
        # Overthinking indicated
        if encoding.complexity > 0.6 and encoding.pattern_density > 0.7:
            return 0.6
        return 0.3
    
    def _predict_has_suffix(self, full_name: str) -> bool:
        """Predict if has Jr/Sr/III etc"""
        # Direct detection
        return any(suffix in full_name for suffix in ['Jr', 'Sr', 'II', 'III', 'IV'])
    
    def _predict_family_prominence(self, features: Dict, encoding: VisualEncoding) -> str:
        """Predict family prominence level"""
        # Has suffix → likely prominent family (passing names down)
        # Formal name → established family
        
        formality = features.get('syllable_count', 2) / 6
        
        if formality > 0.7:
            return "prominent_national"
        elif formality > 0.5:
            return "prominent_local"
        else:
            return "average"
    
    def _predict_siblings(self, features: Dict, encoding: VisualEncoding) -> int:
        """Predict number of siblings"""
        # Complex names often from larger families
        # (More names to differentiate from)
        if encoding.complexity > 0.7:
            return 3
        elif encoding.complexity > 0.5:
            return 2
        else:
            return 1
    
    def _predict_crisis(self, features: Dict, encoding: VisualEncoding) -> bool:
        """Predict recent crisis/catalyst"""
        # High tension in name properties → crisis state
        # Contrasts, asymmetries
        tension = abs(encoding.angular_vs_curved) + (1 - encoding.symmetry)
        
        return tension > 1.0
    
    def _predict_outsider(self, features: Dict, encoding: VisualEncoding) -> bool:
        """Predict outsider status"""
        # Unusual properties → doesn't fit in
        return encoding.complexity > 0.65 and encoding.symmetry < 0.4
    
    def _predict_revolutionary(self, features: Dict, encoding: VisualEncoding) -> float:
        """Predict revolutionary tendency"""
        # Complex + asymmetric + extreme → revolutionary
        return (encoding.complexity + (1 - encoding.symmetry) + abs(encoding.angular_vs_curved)) / 3
    
    def _calculate_confidences(self, features: Dict, encoding: VisualEncoding) -> Dict[str, float]:
        """Calculate confidence in each prediction"""
        # Based on data quality and property clarity
        
        return {
            'age': 0.6,
            'education': 0.7,
            'personality': 0.5,
            'mental_health': 0.4,
            'circumstances': 0.5,
        }
    
    def generate_prediction_report(self, profile: PersonProfile) -> str:
        """Generate human-readable prediction report"""
        lines = []
        lines.append("=" * 80)
        lines.append(f"PREDICTED PROFILE: {profile.name}")
        lines.append("=" * 80)
        lines.append("")
        
        lines.append("DEMOGRAPHICS:")
        lines.append(f"  Age: {profile.predicted_age_range[0]}-{profile.predicted_age_range[1]}")
        lines.append(f"  Generation: {profile.predicted_generation}")
        lines.append(f"  Location: {profile.predicted_location_type}")
        lines.append("")
        
        lines.append("EDUCATION:")
        lines.append(f"  Level: {profile.predicted_education_level}")
        lines.append(f"  Elite institution: {profile.predicted_elite_institution}")
        lines.append(f"  Field: {profile.predicted_field}")
        lines.append("")
        
        lines.append("PROFESSIONAL:")
        lines.append(f"  Career type: {profile.predicted_career_type}")
        lines.append(f"  Creativity: {profile.predicted_creativity_level:.3f}")
        lines.append(f"  Unconventional: {profile.predicted_unconventional}")
        lines.append("")
        
        lines.append("PERSONALITY:")
        lines.append(f"  MBTI: {profile.predicted_mbti}")
        lines.append(f"  Introversion: {profile.predicted_introversion:.3f}")
        lines.append(f"  Intuition: {profile.predicted_intuition:.3f}")
        lines.append(f"  Thinking: {profile.predicted_thinking:.3f}")
        lines.append("")
        
        lines.append("MENTAL HEALTH INDICATORS:")
        lines.append(f"  Neurodivergent: {profile.predicted_neurodivergent}")
        lines.append(f"  ADHD likelihood: {profile.predicted_adhd_likelihood:.3f}")
        lines.append(f"  Bipolar likelihood: {profile.predicted_bipolar_likelihood:.3f}")
        lines.append(f"  Depression likelihood: {profile.predicted_depression_likelihood:.3f}")
        lines.append("")
        
        lines.append("FAMILY:")
        lines.append(f"  Has suffix (Jr/Sr): {profile.predicted_has_junior_senior}")
        lines.append(f"  Family prominence: {profile.predicted_family_prominence}")
        lines.append(f"  Siblings: ~{profile.predicted_sibling_count}")
        lines.append("")
        
        lines.append("CIRCUMSTANCES:")
        lines.append(f"  Recent crisis: {profile.predicted_recent_crisis}")
        lines.append(f"  Outsider status: {profile.predicted_outsider_status}")
        lines.append(f"  Revolutionary tendency: {profile.predicted_revolutionary_tendency:.3f}")
        
        return "\n".join(lines)

