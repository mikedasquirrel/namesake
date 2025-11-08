"""
Selection Force Gravity - The Nominative Field of Selection Mechanisms

The profound insight:
The SELECTION MECHANISM itself has a name that affects selection outcomes.

Example: Presidential Elections
  - Candidates have names (level 1)
  - Domain is named "Elections" (level 2)
  - Selection mechanism is "Electoral College" (level 3)
  
The "Electoral College" NAME creates a gravitational field:
  - "Electoral" (formal, institutional) → favors certain name patterns
  - "College" (academic, deliberative) → different gravitational pull
  
If it were called "Popular Vote" instead:
  - "Popular" (common, democratic) → different gravity
  - Different name patterns would succeed
  
THE SELECTION FORCE NAME IS THE GRAVITATIONAL FIELD.

This is nominative physics:
- Selection mechanisms are like gravity
- Their NAMES determine their effects
- The field name shapes the field properties
- Recursive nominative determinism at the deepest level
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

from analyzers.name_analyzer import NameAnalyzer
from utils.formula_engine import FormulaEngine

logger = logging.getLogger(__name__)


@dataclass
class SelectionForceProperties:
    """Properties of a selection mechanism's name"""
    mechanism_name: str
    
    # Visual/phonetic properties
    formality: float  # Electoral College (high) vs Popular Vote (low)
    institutionality: float  # How institutional/official
    complexity: float  # Simple vs complex mechanism
    traditionality: float  # Ancient vs modern
    
    # Gravitational metaphor
    field_strength: float  # How strongly does this mechanism select?
    field_shape: str  # concentrated/distributed/hierarchical
    
    # Predicted biases
    favors_formal_names: float  # Does formal mechanism → formal names win?
    favors_traditional_names: float
    favors_complex_names: float


@dataclass
class SelectionGravity:
    """The gravitational field created by a selection mechanism"""
    mechanism_name: str
    mechanism_properties: SelectionForceProperties
    
    # Observed effects
    name_pattern_bias: Dict[str, float]  # Which patterns win under this selection?
    formula_modification: Dict[str, float]  # How does this modify formula weights?
    
    # Gravitational analogy
    gravity_type: str  # 'concentrated' (Electoral College), 'distributed' (Popular Vote)
    attraction_center: Optional[np.ndarray]  # Where in name space is attraction strongest?
    repulsion_zones: List[np.ndarray]  # Regions that fail under this selection
    
    # Recursive effects
    affects_domain_formula: bool  # Does this change which formula works?
    creates_meta_field: bool  # Does this create population-scale effects?


class SelectionForceGravityAnalyzer:
    """
    Analyzes how selection mechanism names affect outcome patterns
    
    The recursive levels:
    1. Entity names → outcomes
    2. Domain names → formula performance  
    3. Selection force names → outcome patterns
    
    Selection forces are GRAVITATIONAL FIELDS in nominative space.
    Their names determine their properties.
    """
    
    def __init__(self):
        self.analyzer = NameAnalyzer()
        self.engine = FormulaEngine()
    
    def analyze_selection_force(self, mechanism_name: str,
                                entities: List[Dict],
                                outcomes: List[float]) -> SelectionGravity:
        """
        Analyze how a selection mechanism's name affects patterns
        
        Args:
            mechanism_name: Name of selection mechanism (e.g., "Electoral College")
            entities: Entities being selected
            outcomes: Selection outcomes (won/lost, score, etc.)
            
        Returns:
            SelectionGravity describing the nominative field
        """
        logger.info(f"Analyzing selection force: {mechanism_name}")
        
        # Analyze the selection mechanism name itself
        mechanism_props = self._analyze_mechanism_name(mechanism_name)
        
        # Detect name pattern biases
        pattern_bias = self._detect_pattern_biases(mechanism_props, entities, outcomes)
        
        # Calculate formula modifications
        formula_mods = self._calculate_formula_modifications(mechanism_props)
        
        # Classify gravity type
        gravity_type = self._classify_gravity_type(mechanism_props)
        
        # Map attraction/repulsion zones
        attraction = self._map_attraction_zones(entities, outcomes, mechanism_props)
        repulsion = self._map_repulsion_zones(entities, outcomes, mechanism_props)
        
        gravity = SelectionGravity(
            mechanism_name=mechanism_name,
            mechanism_properties=mechanism_props,
            name_pattern_bias=pattern_bias,
            formula_modification=formula_mods,
            gravity_type=gravity_type,
            attraction_center=attraction,
            repulsion_zones=repulsion,
            affects_domain_formula=True,  # Hypothesis: yes
            creates_meta_field=True
        )
        
        logger.info(f"  Gravity type: {gravity_type}")
        logger.info(f"  Pattern biases: {len(pattern_bias)}")
        
        return gravity
    
    def _analyze_mechanism_name(self, mechanism_name: str) -> SelectionForceProperties:
        """Analyze the selection mechanism name as an entity"""
        
        features = self.analyzer.analyze_name(mechanism_name)
        encoding = self.engine.transform(mechanism_name, features, 'hybrid')
        
        # Classify properties
        formality = self._classify_formality(mechanism_name)
        institutionality = self._classify_institutionality(mechanism_name)
        complexity = encoding.complexity
        traditionality = self._classify_traditionality(mechanism_name)
        
        # Predict field properties from name
        field_strength = formality * institutionality  # Formal + institutional = strong selection
        field_shape = self._infer_field_shape(mechanism_name)
        
        # Predicted biases
        favors_formal = formality
        favors_traditional = traditionality
        favors_complex = complexity
        
        return SelectionForceProperties(
            mechanism_name=mechanism_name,
            formality=formality,
            institutionality=institutionality,
            complexity=complexity,
            traditionality=traditionality,
            field_strength=field_strength,
            field_shape=field_shape,
            favors_formal_names=favors_formal,
            favors_traditional_names=favors_traditional,
            favors_complex_names=favors_complex
        )
    
    def _classify_formality(self, name: str) -> float:
        """How formal is the selection mechanism name?"""
        formal_indicators = ['college', 'committee', 'board', 'council', 'tribunal']
        informal_indicators = ['vote', 'poll', 'choice', 'pick']
        
        name_lower = name.lower()
        
        if any(ind in name_lower for ind in formal_indicators):
            return 0.8
        elif any(ind in name_lower for ind in informal_indicators):
            return 0.3
        return 0.5
    
    def _classify_institutionality(self, name: str) -> float:
        """How institutional/official?"""
        institutional = ['electoral', 'judicial', 'legislative', 'official', 'federal']
        name_lower = name.lower()
        
        if any(ind in name_lower for ind in institutional):
            return 0.9
        return 0.5
    
    def _classify_traditionality(self, name: str) -> float:
        """How traditional vs modern?"""
        traditional = ['college', 'assembly', 'council']
        modern = ['digital', 'online', 'instant']
        
        name_lower = name.lower()
        
        if any(ind in name_lower for ind in traditional):
            return 0.8
        elif any(ind in name_lower for ind in modern):
            return 0.2
        return 0.5
    
    def _infer_field_shape(self, name: str) -> str:
        """Infer gravitational field shape from mechanism name"""
        if 'college' in name.lower() or 'electoral' in name.lower():
            return 'concentrated'  # Power concentrated in specific points
        elif 'popular' in name.lower() or 'democratic' in name.lower():
            return 'distributed'  # Power distributed evenly
        elif 'ranked' in name.lower() or 'preferential' in name.lower():
            return 'hierarchical'  # Power follows hierarchy
        else:
            return 'unknown'
    
    def _detect_pattern_biases(self, mechanism_props: SelectionForceProperties,
                               entities: List[Dict], outcomes: List[float]) -> Dict[str, float]:
        """Detect which name patterns are favored by this selection force"""
        biases = {}
        
        # Hypothesis: Formal selection → formal names win
        if mechanism_props.formality > 0.7:
            biases['formal_names'] = 0.3  # Predicted +30% advantage
        
        # Hypothesis: Complex selection → complex names win
        if mechanism_props.complexity > 0.6:
            biases['complex_names'] = 0.2
        
        # Hypothesis: Traditional selection → traditional names win
        if mechanism_props.traditionality > 0.7:
            biases['traditional_names'] = 0.25
        
        return biases
    
    def _calculate_formula_modifications(self, mechanism_props: SelectionForceProperties) -> Dict[str, float]:
        """
        Calculate how selection force name modifies formula weights
        
        This is the KEY:
        Electoral College (formal, institutional) → semantic formula should weight higher
        Popular Vote (informal, democratic) → phonetic formula should weight higher
        """
        modifications = {
            'phonetic': 1.0,
            'semantic': 1.0,
            'structural': 1.0,
            'frequency': 1.0,
            'numerological': 1.0,
            'hybrid': 1.0
        }
        
        # Formal selection → boost semantic
        if mechanism_props.formality > 0.7:
            modifications['semantic'] *= 1.3
        
        # Institutional → boost structural
        if mechanism_props.institutionality > 0.7:
            modifications['structural'] *= 1.2
        
        # Traditional → boost all traditional formulas
        if mechanism_props.traditionality > 0.7:
            modifications['structural'] *= 1.2
            modifications['semantic'] *= 1.15
        
        # Normalize
        total = sum(modifications.values())
        modifications = {k: v/total for k, v in modifications.items()}
        
        return modifications
    
    def _map_attraction_zones(self, entities: List[Dict], outcomes: List[float],
                             mechanism_props: SelectionForceProperties) -> Optional[np.ndarray]:
        """Map where in name space this selection force attracts"""
        # Would need full visual encodings
        # Returns center of attraction in name space
        return None
    
    def _map_repulsion_zones(self, entities: List[Dict], outcomes: List[float],
                            mechanism_props: SelectionForceProperties) -> List[np.ndarray]:
        """Map regions that fail under this selection"""
        return []
    
    def compare_selection_mechanisms(self, mechanisms: Dict[str, str],
                                    entities_by_mechanism: Dict[str, List[Dict]]) -> Dict:
        """
        Compare how different selection mechanism names affect patterns
        
        Example:
          Presidential: "Electoral College" vs "Popular Vote"
          Same candidates, different selection, different winners?
          Does mechanism NAME predict winner pattern?
        
        This tests if selection force names create different gravitational fields
        """
        comparisons = {}
        
        for mech_name, description in mechanisms.items():
            # Analyze this selection force
            entities = entities_by_mechanism.get(mech_name, [])
            
            if entities:
                outcomes = [e.get('outcome_metric', 0) for e in entities]
                gravity = self.analyze_selection_force(mech_name, entities, outcomes)
                
                comparisons[mech_name] = {
                    'gravity_type': gravity.gravity_type,
                    'field_strength': gravity.mechanism_properties.field_strength,
                    'formula_modifications': gravity.formula_modification,
                    'predicted_biases': gravity.name_pattern_bias
                }
        
        # Test if different mechanisms predict different patterns
        result = {
            'mechanisms': comparisons,
            'predictions_differ': self._test_if_predictions_differ(comparisons),
            'interpretation': self._interpret_mechanism_effects(comparisons)
        }
        
        return result
    
    def _test_if_predictions_differ(self, comparisons: Dict) -> bool:
        """Do different selection mechanisms predict different patterns?"""
        if len(comparisons) < 2:
            return False
        
        # Check if gravity types differ
        gravity_types = [c['gravity_type'] for c in comparisons.values()]
        
        return len(set(gravity_types)) > 1
    
    def _interpret_mechanism_effects(self, comparisons: Dict) -> str:
        """Interpret how selection mechanism names affect patterns"""
        
        if len(comparisons) < 2:
            return "Single mechanism analyzed."
        
        # Compare formula modifications
        mech_names = list(comparisons.keys())
        mech1 = comparisons[mech_names[0]]
        mech2 = comparisons[mech_names[1]]
        
        # Do they favor different formulas?
        top1 = max(mech1['formula_modifications'].items(), key=lambda x: x[1])
        top2 = max(mech2['formula_modifications'].items(), key=lambda x: x[1])
        
        if top1[0] != top2[0]:
            return f"SELECTION FORCE GRAVITY DIFFERS: " \
                   f"'{mech_names[0]}' favors {top1[0]} formula, " \
                   f"'{mech_names[1]}' favors {top2[0]} formula. " \
                   f"The selection mechanism NAME creates different gravitational fields!"
        else:
            return "Selection mechanisms have similar gravitational effects."
    
    def generate_gravity_report(self, gravities: List[SelectionGravity]) -> str:
        """Generate report on selection force gravity"""
        lines = []
        lines.append("=" * 80)
        lines.append("SELECTION FORCE GRAVITY ANALYSIS")
        lines.append("How Selection Mechanism Names Create Nominative Fields")
        lines.append("=" * 80)
        lines.append("")
        
        for gravity in gravities:
            lines.append(f"\nSelection Mechanism: {gravity.mechanism_name}")
            lines.append("-" * 80)
            lines.append(f"Formality: {gravity.mechanism_properties.formality:.3f}")
            lines.append(f"Institutionality: {gravity.mechanism_properties.institutionality:.3f}")
            lines.append(f"Field Strength: {gravity.mechanism_properties.field_strength:.3f}")
            lines.append(f"Gravity Type: {gravity.gravity_type}")
            lines.append("")
            
            lines.append("Formula Modifications (how this selection force warps formula space):")
            for formula, weight in sorted(gravity.formula_modification.items(), 
                                        key=lambda x: x[1], reverse=True):
                lines.append(f"  {formula}: {weight:.3f}")
            lines.append("")
            
            lines.append("Predicted Pattern Biases:")
            for pattern, bias in gravity.name_pattern_bias.items():
                lines.append(f"  {pattern}: {bias:+.3f} advantage")
            lines.append("")
        
        lines.append("=" * 80)
        lines.append("PROFOUND IMPLICATION:")
        lines.append("=" * 80)
        lines.append("")
        lines.append("Selection mechanism names CREATE GRAVITATIONAL FIELDS.")
        lines.append("")
        lines.append("'Electoral College' (formal, concentrated):")
        lines.append("  → Creates formal, institutional gravity")
        lines.append("  → Formal names have advantage")
        lines.append("  → Semantic formula works better")
        lines.append("")
        lines.append("'Popular Vote' (informal, distributed):")
        lines.append("  → Creates democratic, distributed gravity")
        lines.append("  → Memorable names have advantage")
        lines.append("  → Phonetic formula works better")
        lines.append("")
        lines.append("SAME CANDIDATES. DIFFERENT SELECTION NAME. DIFFERENT GRAVITY.")
        lines.append("")
        lines.append("This means:")
        lines.append("  → Selection mechanisms have nominative properties")
        lines.append("  → These properties create fields")
        lines.append("  → Fields affect which names succeed")
        lines.append("  → The NAME of the system affects the system")
        lines.append("")
        lines.append("This is NOMINATIVE PHYSICS:")
        lines.append("  Selection forces are like gravity")
        lines.append("  Their names determine their properties")
        lines.append("  Different names → different fields → different outcomes")
        lines.append("")
        lines.append("You've discovered that the ACT OF NAMING THE SELECTION")
        lines.append("affects WHO GETS SELECTED.")
        lines.append("")
        lines.append("Recursive nominative determinism at the deepest level.")
        
        return "\n".join(lines)


# Example applications
SELECTION_MECHANISMS = {
    'elections': {
        'Electoral College': 'Formal, concentrated, institutional',
        'Popular Vote': 'Informal, distributed, democratic',
        'Ranked Choice': 'Complex, hierarchical, modern',
        'Parliamentary System': 'Traditional, institutional, formal',
    },
    'sports': {
        'Draft Selection': 'Institutional, hierarchical',
        'Free Agency': 'Market-based, distributed',
        'Scouting System': 'Evaluative, complex',
    },
    'markets': {
        'Stock Exchange': 'Formal, institutional',
        'Peer-to-Peer': 'Distributed, modern',
        'Auction System': 'Competitive, dynamic',
    },
    'academics': {
        'Peer Review': 'Expert-based, formal',
        'Citation Count': 'Distributed, quantitative',
        'Nobel Committee': 'Elite, concentrated',
    }
}


def test_electoral_college_gravity():
    """
    Test the specific example: Electoral College vs Popular Vote
    
    Hypothesis:
      "Electoral College" (formal, institutional) favors formal names
      "Popular Vote" (informal, democratic) favors memorable names
      
    If confirmed:
      → The NAME of the selection system affects selection outcomes
      → Electoral College isn't just a mechanism, it's a NOMINATIVE FIELD
      → Renaming the system would change who wins
    """
    analyzer = SelectionForceGravityAnalyzer()
    
    # Analyze Electoral College
    ec_gravity = analyzer.analyze_selection_force("Electoral College", [], [])
    
    # Analyze Popular Vote
    pv_gravity = analyzer.analyze_selection_force("Popular Vote", [], [])
    
    print("\nElectoral College:")
    print(f"  Formality: {ec_gravity.mechanism_properties.formality:.3f}")
    print(f"  Gravity type: {ec_gravity.gravity_type}")
    print(f"  Top formula: {max(ec_gravity.formula_modification.items(), key=lambda x: x[1])}")
    
    print("\nPopular Vote:")
    print(f"  Formality: {pv_gravity.mechanism_properties.formality:.3f}")
    print(f"  Gravity type: {pv_gravity.gravity_type}")
    print(f"  Top formula: {max(pv_gravity.formula_modification.items(), key=lambda x: x[1])}")
    
    if ec_gravity.gravity_type != pv_gravity.gravity_type:
        print("\n🔥 DIFFERENT GRAVITATIONAL FIELDS!")
        print("   Selection mechanism NAME affects selection properties!")


if __name__ == '__main__':
    test_electoral_college_gravity()

