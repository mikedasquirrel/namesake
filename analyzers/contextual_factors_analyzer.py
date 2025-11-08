"""
Contextual Factors Analyzer

Accounts for EXTERNAL nominative factors that confound pure name effects:
- Family name context (parents, siblings, relatives)
- Cultural/ethnic naming conventions
- Historical era naming trends
- Geographic/regional patterns
- Socioeconomic proxies in names

This is critical for isolating TRUE nominative effects from social/cultural confounds.

The profound question:
"After controlling for family, culture, and history - does the NAME ITSELF still matter?"
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging
from scipy import stats
import re

logger = logging.getLogger(__name__)


@dataclass
class ContextualFactors:
    """External nominative context for an entity"""
    entity_name: str
    
    # Family context
    family_surname: Optional[str] = None
    parent_names: Optional[List[str]] = None
    sibling_names: Optional[List[str]] = None
    family_name_tradition: Optional[str] = None  # "continuation", "innovation", etc.
    
    # Cultural context
    cultural_origin: Optional[str] = None
    ethnicity: Optional[str] = None
    name_cultural_typicality: float = 0.5  # 0-1, how typical for that culture
    acculturation_score: float = 0.5  # If immigrant, how adapted to new culture
    
    # Historical context
    birth_era: Optional[str] = None
    era_name_popularity: float = 0.5  # 0-1, how popular was this name in that era
    generational_cohort: Optional[str] = None  # boomer, gen_x, millennial, gen_z
    
    # Geographic context
    birth_region: Optional[str] = None
    region_naming_pattern: Optional[str] = None
    urban_vs_rural: Optional[str] = None
    
    # Socioeconomic proxies
    name_socioeconomic_signal: float = 0.5  # Names signal class
    education_proxy: float = 0.5  # Traditional vs trendy
    
    # Linguistic environment
    primary_language: Optional[str] = None
    accent_pattern: Optional[str] = None
    language_family: Optional[str] = None  # Germanic, Romance, Slavic, etc.
    tonal_language: bool = False
    
    # Name choice intentionality
    chosen_vs_assigned: str = "assigned"  # "chosen" for stage names, trans names
    name_change_history: Optional[List[str]] = None


@dataclass
class ContextualAnalysisResult:
    """Result of contextual factor analysis"""
    
    # Raw effect (without controls)
    raw_correlation: float
    
    # Controlled effect (after partialing out context)
    controlled_correlation: float
    
    # What changed?
    context_contribution: float  # How much was context vs pure name
    
    # Which factors mattered most
    significant_confounds: List[str]
    
    # Interpretation
    is_pure_name_effect: bool  # True if effect persists after controls
    effect_is_cultural: bool  # True if disappears after cultural controls
    effect_is_familial: bool  # True if disappears after family controls
    effect_is_historical: bool  # True if disappears after era controls


class ContextualFactorsAnalyzer:
    """
    Analyzes nominative effects while controlling for contextual confounds
    
    This separates:
    - Pure name effects (intrinsic properties)
    - Family effects (inherited patterns)
    - Cultural effects (ethnic/regional conventions)
    - Historical effects (era-specific trends)
    - Linguistic effects (language structure)
    """
    
    def __init__(self):
        # Cultural name databases (simplified - would expand)
        self.cultural_patterns = self._load_cultural_patterns()
        self.era_patterns = self._load_era_patterns()
        self.family_patterns = {}  # Built from data
    
    def analyze_with_context(self, entities: List[Dict], 
                            outcomes: List[float],
                            visual_properties: List[Dict]) -> ContextualAnalysisResult:
        """
        Analyze nominative effects controlling for contextual factors
        
        Args:
            entities: List of entity data (with context)
            outcomes: List of outcome metrics
            visual_properties: List of visual encodings from formula
            
        Returns:
            ContextualAnalysisResult showing pure vs confounded effects
        """
        logger.info("Analyzing with contextual controls...")
        
        # Extract contextual factors for each entity
        contexts = [self._extract_context(entity) for entity in entities]
        
        # Calculate raw correlation (no controls)
        raw_corr = self._calculate_raw_correlation(visual_properties, outcomes)
        
        # Partial correlation (controlling for context)
        controlled_corr = self._partial_correlation(
            visual_properties, outcomes, contexts
        )
        
        # Identify significant confounds
        confounds = self._identify_confounds(contexts, outcomes)
        
        # Classify effect type
        context_contrib = abs(raw_corr - controlled_corr)
        
        is_pure = abs(controlled_corr) > 0.15  # Effect persists
        is_cultural = 'cultural_origin' in confounds
        is_familial = 'family_context' in confounds
        is_historical = 'birth_era' in confounds
        
        result = ContextualAnalysisResult(
            raw_correlation=raw_corr,
            controlled_correlation=controlled_corr,
            context_contribution=context_contrib,
            significant_confounds=confounds,
            is_pure_name_effect=is_pure,
            effect_is_cultural=is_cultural,
            effect_is_familial=is_familial,
            effect_is_historical=is_historical
        )
        
        logger.info(f"  Raw correlation: {raw_corr:.3f}")
        logger.info(f"  Controlled correlation: {controlled_corr:.3f}")
        logger.info(f"  Context contribution: {context_contrib:.3f}")
        
        return result
    
    def _extract_context(self, entity: Dict) -> ContextualFactors:
        """Extract contextual factors from entity data"""
        
        # Parse name for cultural signals
        name = entity.get('name', '')
        
        # Infer cultural origin from name patterns
        cultural_origin = self._infer_cultural_origin(name)
        
        # Infer era from entity metadata
        birth_year = entity.get('metadata', {}).get('year') or entity.get('metadata', {}).get('debut_year')
        era = self._classify_era(birth_year) if birth_year else None
        
        # Build context object
        context = ContextualFactors(
            entity_name=name,
            cultural_origin=cultural_origin,
            birth_era=era,
            generational_cohort=self._classify_generation(birth_year) if birth_year else None,
            primary_language=self._infer_language(name, cultural_origin),
            name_cultural_typicality=self._calculate_typicality(name, cultural_origin),
        )
        
        return context
    
    def _calculate_raw_correlation(self, visual_props: List[Dict], 
                                   outcomes: List[float]) -> float:
        """Calculate raw correlation without controls"""
        
        if not visual_props or not outcomes:
            return 0.0
        
        # Use first visual property as example (would do all in real implementation)
        prop_values = [p.get('hue', 0) for p in visual_props]
        
        try:
            corr, _ = stats.pearsonr(prop_values, outcomes)
            return corr
        except:
            return 0.0
    
    def _partial_correlation(self, visual_props: List[Dict],
                            outcomes: List[float],
                            contexts: List[ContextualFactors]) -> float:
        """
        Calculate partial correlation controlling for contextual factors
        
        This uses regression to remove variance explained by context,
        then correlates residuals
        """
        from sklearn.linear_model import LinearRegression
        
        # Build context feature matrix
        context_features = []
        for ctx in contexts:
            features = [
                1.0 if ctx.cultural_origin == 'Western' else 0.0,
                1.0 if ctx.cultural_origin == 'Eastern' else 0.0,
                1.0 if ctx.birth_era == 'modern' else 0.0,
                ctx.name_cultural_typicality,
            ]
            context_features.append(features)
        
        context_matrix = np.array(context_features)
        
        # Visual property values
        prop_values = np.array([p.get('hue', 0) for p in visual_props])
        outcomes_array = np.array(outcomes)
        
        try:
            # Regress visual properties on context
            model1 = LinearRegression()
            model1.fit(context_matrix, prop_values)
            prop_residuals = prop_values - model1.predict(context_matrix)
            
            # Regress outcomes on context
            model2 = LinearRegression()
            model2.fit(context_matrix, outcomes_array)
            outcome_residuals = outcomes_array - model2.predict(context_matrix)
            
            # Correlate residuals (this is the pure name effect)
            partial_corr, _ = stats.pearsonr(prop_residuals, outcome_residuals)
            
            return partial_corr
            
        except Exception as e:
            logger.error(f"Partial correlation failed: {e}")
            return 0.0
    
    def _identify_confounds(self, contexts: List[ContextualFactors],
                           outcomes: List[float]) -> List[str]:
        """Identify which contextual factors confound the relationship"""
        confounds = []
        
        # Test each context factor
        context_factors = {
            'cultural_origin': [ctx.cultural_origin for ctx in contexts],
            'birth_era': [ctx.birth_era for ctx in contexts],
            'cultural_typicality': [ctx.name_cultural_typicality for ctx in contexts],
        }
        
        for factor_name, factor_values in context_factors.items():
            # Convert to numeric if needed
            if isinstance(factor_values[0], str):
                # One-hot encode
                unique = list(set(factor_values))
                numeric = [unique.index(v) if v else 0 for v in factor_values]
            else:
                numeric = factor_values
            
            try:
                # Correlate with outcomes
                corr, p_value = stats.pearsonr(numeric, outcomes)
                
                if p_value < 0.05 and abs(corr) > 0.15:
                    confounds.append(factor_name)
                    logger.info(f"    Confound detected: {factor_name} (r={corr:.3f})")
            except:
                pass
        
        return confounds
    
    def _infer_cultural_origin(self, name: str) -> str:
        """Infer cultural origin from name patterns"""
        name_lower = name.lower()
        
        # Very simplified heuristics
        western_endings = ['son', 'sen', 'ton', 'man', 'er', 'son']
        eastern_endings = ['san', 'chan', 'kun', 'dao', 'ming']
        
        for ending in western_endings:
            if name_lower.endswith(ending):
                return 'Western'
        
        for ending in eastern_endings:
            if name_lower.endswith(ending):
                return 'Eastern'
        
        # Check for non-Latin characters
        if not all(ord(c) < 128 for c in name):
            return 'Non-Western'
        
        return 'Western'  # Default
    
    def _classify_era(self, year: Optional[int]) -> Optional[str]:
        """Classify historical era"""
        if not year:
            return None
        
        if year < 1950:
            return 'pre_modern'
        elif year < 1980:
            return 'mid_century'
        elif year < 2000:
            return 'late_century'
        elif year < 2010:
            return 'early_digital'
        else:
            return 'digital_native'
    
    def _classify_generation(self, year: Optional[int]) -> Optional[str]:
        """Classify generational cohort"""
        if not year:
            return None
        
        if year < 1946:
            return 'silent'
        elif year < 1965:
            return 'boomer'
        elif year < 1981:
            return 'gen_x'
        elif year < 1997:
            return 'millennial'
        else:
            return 'gen_z'
    
    def _infer_language(self, name: str, cultural_origin: Optional[str]) -> str:
        """Infer primary language from name and culture"""
        if cultural_origin == 'Eastern':
            return 'Asian'
        elif cultural_origin == 'Western':
            return 'English'
        else:
            return 'Other'
    
    def _calculate_typicality(self, name: str, cultural_origin: Optional[str]) -> float:
        """How typical is this name for its culture?"""
        # Simplified - would use actual frequency data
        return 0.5
    
    def _load_cultural_patterns(self) -> Dict:
        """Load known cultural naming patterns"""
        return {
            'Western': {
                'typical_endings': ['son', 'er', 'ton', 'ley'],
                'typical_syllables': [2, 3],
                'typical_length': [6, 8],
            },
            'Eastern': {
                'typical_endings': ['san', 'ming', 'jun'],
                'typical_syllables': [2, 3],
                'typical_length': [4, 7],
            },
        }
    
    def _load_era_patterns(self) -> Dict:
        """Load era-specific naming patterns"""
        return {
            'pre_modern': {'typical_names': ['John', 'Mary', 'James']},
            'digital_native': {'typical_names': ['Aiden', 'Emma', 'Liam']},
        }
    
    def generate_contextual_report(self, result: ContextualAnalysisResult) -> str:
        """Generate human-readable report"""
        lines = []
        lines.append("=" * 80)
        lines.append("CONTEXTUAL FACTORS ANALYSIS")
        lines.append("=" * 80)
        lines.append("")
        
        lines.append("EFFECT DECOMPOSITION:")
        lines.append("-" * 80)
        lines.append(f"Raw Correlation (no controls): r = {result.raw_correlation:.3f}")
        lines.append(f"Controlled Correlation (with controls): r = {result.controlled_correlation:.3f}")
        lines.append(f"Context Contribution: {result.context_contribution:.3f}")
        lines.append(f"Percent Explained by Context: {(result.context_contribution / abs(result.raw_correlation) * 100):.1f}%")
        lines.append("")
        
        lines.append("SIGNIFICANT CONFOUNDS:")
        lines.append("-" * 80)
        if result.significant_confounds:
            for confound in result.significant_confounds:
                lines.append(f"  • {confound}")
        else:
            lines.append("  None detected")
        lines.append("")
        
        lines.append("EFFECT CLASSIFICATION:")
        lines.append("-" * 80)
        if result.is_pure_name_effect:
            lines.append("  ✓ Pure name effect persists after controls")
            lines.append("    → Nominative determinism is REAL (not just proxy)")
        else:
            lines.append("  ✗ Effect disappears after controls")
            lines.append("    → Pattern is confounded by context")
        
        if result.effect_is_cultural:
            lines.append("  ⚠ Cultural confound detected")
            lines.append("    → Effect may be ethnic/regional, not pure name")
        
        if result.effect_is_familial:
            lines.append("  ⚠ Family confound detected")
            lines.append("    → Effect may be inherited, not intrinsic")
        
        if result.effect_is_historical:
            lines.append("  ⚠ Historical confound detected")
            lines.append("    → Effect may be generational, not timeless")
        
        return "\n".join(lines)


class AccentPhoneticAnalyzer:
    """
    Analyzes how ACCENT affects phonetic properties and outcomes
    
    Tests: Does accent change the nominative effect?
    """
    
    def __init__(self):
        self.accent_patterns = {
            'British': {'r_dropping': True, 'vowel_shift': 'high'},
            'American': {'r_dropping': False, 'vowel_shift': 'low'},
            'Australian': {'r_dropping': True, 'vowel_shift': 'high'},
            'Southern_US': {'drawl': True, 'vowel_lengthening': True},
        }
    
    def analyze_accent_effects(self, name: str, accent: str) -> Dict:
        """
        How does accent change name properties?
        
        Example:
          "Martha" in Boston (r-dropping) vs Texas (drawl)
          Different phonetic realization
          Different nominative effects?
        """
        # Get accent pattern
        pattern = self.accent_patterns.get(accent, {})
        
        # Modify phonetic analysis based on accent
        modifications = {
            'r_sound_present': not pattern.get('r_dropping', False),
            'vowel_length_multiplier': 1.5 if pattern.get('drawl') else 1.0,
            'harshness_modifier': -0.1 if pattern.get('vowel_shift') == 'high' else 0.0,
        }
        
        return {
            'accent': accent,
            'modifications': modifications,
            'interpretation': f"Accent '{accent}' modifies phonetic realization"
        }


class LanguageFamilyAnalyzer:
    """
    Analyzes how language STRUCTURE affects naming patterns
    
    Tests: Do tonal languages → different personality distributions?
    """
    
    LANGUAGE_FAMILIES = {
        'Germanic': {'tonal': False, 'inflected': True, 'word_order': 'SVO'},
        'Romance': {'tonal': False, 'inflected': True, 'word_order': 'SVO'},
        'Slavic': {'tonal': False, 'inflected': True, 'word_order': 'SVO'},
        'Sino-Tibetan': {'tonal': True, 'inflected': False, 'word_order': 'SVO'},
        'Japanese': {'tonal': False, 'inflected': True, 'word_order': 'SOV'},
        'Arabic': {'tonal': False, 'inflected': True, 'word_order': 'VSO'},
    }
    
    def analyze_language_effects(self, language_family: str, 
                                 personality_type: str) -> Dict:
        """
        Test if language structure predicts personality
        
        Hypothesis: Tonal languages → more F (feeling) in MBTI
                   Inflected languages → more J (judging)
        """
        family_props = self.LANGUAGE_FAMILIES.get(language_family, {})
        
        predictions = {}
        
        if family_props.get('tonal'):
            predictions['MBTI_F_probability'] = 0.65  # Tonal → feeling
        else:
            predictions['MBTI_T_probability'] = 0.55  # Non-tonal → thinking
        
        if family_props.get('inflected'):
            predictions['MBTI_J_probability'] = 0.60  # Inflected → judging
        else:
            predictions['MBTI_P_probability'] = 0.55  # Non-inflected → perceiving
        
        return {
            'language_family': language_family,
            'properties': family_props,
            'predictions': predictions,
            'hypothesis': "Language structure affects personality distribution"
        }


class DirectionalityAnalyzer:
    """
    Analyzes RTL vs LTR information encoding/loss
    
    The profound question: Does reading direction encode meaning?
    """
    
    def analyze_directionality(self, name: str, script: str = 'Latin') -> Dict:
        """
        Analyze how directionality affects visual encoding
        
        Args:
            name: The name to analyze
            script: Writing system (Latin, Arabic, Hebrew, etc.)
            
        Returns:
            Analysis of directional effects
        """
        # Determine native direction
        native_direction = 'LTR'
        if script in ['Arabic', 'Hebrew', 'Persian']:
            native_direction = 'RTL'
        
        # Analyze in native direction
        encoding_native = self._transform_directional(name, native_direction)
        
        # Analyze in opposite direction
        opposite_direction = 'RTL' if native_direction == 'LTR' else 'LTR'
        encoding_opposite = self._transform_directional(name, opposite_direction)
        
        # Calculate information loss
        loss = self._calculate_directional_loss(encoding_native, encoding_opposite)
        
        return {
            'name': name,
            'native_direction': native_direction,
            'encoding_native': encoding_native,
            'encoding_opposite': encoding_opposite,
            'information_loss': loss,
            'properties_lost': loss['properties_affected'],
            'interpretation': self._interpret_directional_loss(loss, native_direction)
        }
    
    def _transform_directional(self, name: str, direction: str) -> Dict:
        """Transform name with directional awareness"""
        # Simplified - would use actual formula engine with direction parameter
        
        if direction == 'RTL':
            # Reverse name for analysis
            name_reversed = name[::-1]
            # Visual flow direction affects properties
            flow_modifier = -1.0
        else:
            name_reversed = name
            flow_modifier = 1.0
        
        # Key properties that might differ by direction
        return {
            'flow_direction': flow_modifier,
            'visual_weight_distribution': 'right' if direction == 'LTR' else 'left',
            'power_orientation': 'forward' if direction == 'LTR' else 'backward',
            'authority_directionality': direction,
        }
    
    def _calculate_directional_loss(self, native: Dict, opposite: Dict) -> Dict:
        """Calculate what's lost when flipping direction"""
        
        properties_affected = []
        
        # Flow direction completely flips
        if native['flow_direction'] != opposite['flow_direction']:
            properties_affected.append('flow_direction')
        
        # Visual weight shifts
        if native['visual_weight_distribution'] != opposite['visual_weight_distribution']:
            properties_affected.append('visual_weight')
        
        # Power orientation reverses
        if native['power_orientation'] != opposite['power_orientation']:
            properties_affected.append('power_orientation')
        
        loss_percentage = len(properties_affected) / len(native) * 100
        
        return {
            'properties_affected': properties_affected,
            'loss_percentage': loss_percentage,
            'severity': 'high' if loss_percentage > 50 else 'moderate' if loss_percentage > 25 else 'low'
        }
    
    def _interpret_directional_loss(self, loss: Dict, native_direction: str) -> str:
        """Interpret what directional flip means"""
        if loss['severity'] == 'high':
            return f"{native_direction} names lose significant meaning when read opposite direction. " \
                   f"Directionality encodes {loss['loss_percentage']:.0f}% of name properties."
        elif loss['severity'] == 'moderate':
            return f"Some meaning lost in directional flip ({loss['loss_percentage']:.0f}%). " \
                   f"Direction matters but name survives translation."
        else:
            return "Minimal directional dependence. Name meaning is direction-independent."

