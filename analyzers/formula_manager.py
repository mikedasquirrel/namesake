"""
Formula Manager - Hierarchical Formula System

Implements the 4-level compositional model for nominative determinism:
Level 1: Phonetic Primitives (universal measurements)
Level 2: Domain-Contextualized Score (weighted for sphere)
Level 3: Predetermined Feature Integration (fundamentals + interactions)
Level 4: Outcome Prediction (link function)

This is the "revolutionary" architecture that allows sophisticated
context-dependent weighting with non-linear interactions.
"""

import numpy as np
import logging
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from analyzers.phonetic_base import get_analyzer as get_phonetic_analyzer
from analyzers.phonetic_composites import get_composite_analyzer
from analyzers.name_economy_analyzer import NameEconomyAnalyzer
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


class Domain(Enum):
    """Supported research domains."""
    CRYPTO = "crypto"
    HURRICANE = "hurricane"
    MTG = "mtg"
    BAND = "band"
    NBA = "nba"
    NFL = "nfl"
    MENTAL_HEALTH = "mental_health"
    AMERICA = "america"
    EARTHQUAKE = "earthquake"
    SHIP = "ship"
    GENERIC = "generic"


class LinkFunction(Enum):
    """Link functions for outcome transformation."""
    IDENTITY = "identity"  # Linear regression
    LOGIT = "logit"  # Binary classification
    SOFTMAX = "softmax"  # Multiclass
    LOG = "log"  # Log-linear


class FormulaManager:
    """
    Manages hierarchical formula system across all domains.
    
    Provides both conservative (simple linear) and revolutionary (4-level)
    approaches for each domain.
    """
    
    def __init__(self):
        self.phonetic_analyzer = get_phonetic_analyzer()
        self.composite_analyzer = get_composite_analyzer()
        self.economy_analyzer = NameEconomyAnalyzer()
        
        # Learned weights per domain (to be populated from validation)
        self.domain_weights = self._initialize_domain_weights()
        
        # Congruence matrices (context alignment multipliers)
        self.congruence_matrices = self._initialize_congruence_matrices()
        
        # Saturation penalties (pattern overuse detection)
        self.saturation_thresholds = self._initialize_saturation_thresholds()
        
        # Scalers for standardization
        self.scalers = {}
    
    def _initialize_domain_weights(self) -> Dict[Domain, Dict]:
        """
        Initialize domain-specific weights for phonetic features.
        
        These are starting weights; optimal values learned during validation.
        """
        return {
            Domain.CRYPTO: {
                'plosive_score': -0.15,
                'fricative_score': -0.10,
                'liquid_score': 0.20,
                'nasal_score': 0.15,
                'voicing_ratio': 0.05,
                'cluster_complexity': -0.25,
                'syllable_count': -0.35,  # Brevity strongly valued
                'memorability_score': -0.30,  # NEGATIVE: sophisticated > memorable
                'euphony_score': 0.15,
                'uniqueness': 0.20,
            },
            Domain.HURRICANE: {
                'plosive_score': 0.40,  # Harshness predicts casualties
                'fricative_score': 0.25,
                'sibilant_score': 0.20,
                'liquid_score': -0.15,
                'memorability_score': 0.25,  # Positive: memorable = taken seriously
                'harshness_score': 0.50,  # Primary predictor
                'power_authority_score': 0.30,
            },
            Domain.MTG: {
                'plosive_score': 0.25,
                'harshness_score': 0.30,  # Red/Black cards
                'smoothness_score': 0.15,  # White/Green cards
                'memorability_score': 0.35,  # POSITIVE: tournament recall
                'syllable_count': -0.20,  # Brevity aids recall
                'euphony_score': 0.20,
                'power_authority_score': 0.25,  # Legendary gravitas
            },
            Domain.BAND: {
                'harshness_score': 0.00,  # Genre-dependent (handled by congruence)
                'memorability_score': 0.40,
                'syllable_count': -0.30,  # Monosyllabic advantage
                'euphony_score': 0.20,
                'uniqueness': 0.25,
            },
            Domain.NBA: {
                'harshness_score': 0.20,  # Position-dependent
                'smoothness_score': 0.10,
                'memorability_score': 0.25,  # Announcer-friendliness
                'pronounceability_score': 0.30,
                'syllable_count': 0.05,  # International trend
            },
            Domain.NFL: {
                'harshness_score': 0.25,
                'power_authority_score': 0.30,
                'memorability_score': 0.20,
                'pronounceability_score': 0.25,
            },
            Domain.MENTAL_HEALTH: {
                'harshness_score': -0.35,  # Stigma penalty
                'smoothness_score': 0.25,
                'memorability_score': 0.40,  # Adherence critical
                'pronounceability_score': 0.45,  # Clinical accessibility
                'euphony_score': 0.20,
            },
            Domain.AMERICA: {
                'harshness_score': 0.30,  # Nationalism correlation
                'memorability_score': 0.35,
                'power_authority_score': 0.25,
                'syllable_count': -0.15,
            },
        }
    
    def _initialize_congruence_matrices(self) -> Dict[Domain, Dict]:
        """
        Initialize congruence multipliers for context alignment.
        
        Example: harsh name × metal genre = high congruence (2.0×)
                 harsh name × folk genre = low congruence (0.5×)
        """
        return {
            Domain.BAND: {
                'metal': {'harshness_score': 2.0, 'smoothness_score': 0.5},
                'folk': {'harshness_score': 0.5, 'smoothness_score': 2.0},
                'pop': {'memorability_score': 1.5, 'syllable_count': 1.3},
                'rock': {'harshness_score': 1.3, 'memorability_score': 1.2},
                'indie': {'uniqueness': 1.8, 'euphony_score': 1.4},
            },
            Domain.MTG: {
                'R': {'harshness_score': 1.8, 'plosive_score': 1.6},  # Red
                'U': {'smoothness_score': 1.5, 'sibilant_score': 1.4},  # Blue
                'B': {'harshness_score': 1.7, 'voicing_ratio': 1.5},  # Black
                'G': {'smoothness_score': 1.6, 'nasal_score': 1.4},  # Green
                'W': {'euphony_score': 1.5, 'smoothness_score': 1.4},  # White
            },
            Domain.NBA: {
                'center': {'harshness_score': 1.6, 'power_authority_score': 1.5},
                'guard': {'smoothness_score': 1.3, 'memorability_score': 1.4},
                'forward': {'balanced': 1.0},
            },
        }
    
    def _initialize_saturation_thresholds(self) -> Dict[Domain, Dict]:
        """
        Initialize saturation detection thresholds.
        
        When a pattern becomes overused, its effectiveness decays.
        """
        return {
            Domain.CRYPTO: {
                'pattern_threshold': 0.15,  # If >15% of coins share pattern, penalty
                'decay_rate': 0.5,  # 50% effectiveness decay at saturation
            },
            Domain.BAND: {
                'pattern_threshold': 0.10,
                'decay_rate': 0.6,
            },
            Domain.MTG: {
                'pattern_threshold': 0.20,  # More tolerance (larger card pool)
                'decay_rate': 0.4,
            },
        }
    
    # ========================================================================
    # LEVEL 1: PHONETIC PRIMITIVES (Universal)
    # ========================================================================
    
    def extract_primitives(self, name: str, all_names: Optional[List[str]] = None) -> Dict:
        """
        Level 1: Extract universal phonetic primitives.
        
        Returns:
            P_vector: Dictionary of fundamental phonetic measurements
        """
        # Get both base and composite measurements
        composites = self.composite_analyzer.analyze(name, all_names)
        
        return composites  # Already includes base measurements
    
    # ========================================================================
    # LEVEL 2: DOMAIN-CONTEXTUALIZED SCORE
    # ========================================================================
    
    def calculate_domain_score(self, primitives: Dict, domain: Domain, 
                               context: Optional[Dict] = None,
                               economy_data: Optional[List[Dict]] = None) -> float:
        """
        Level 2: Calculate domain-specific weighted score.
        
        Formula: S_domain = weighted_sum(P_vector) × congruence × (1 - saturation) × economy_factor
        
        CRITICAL UPDATE: Now includes economic interdependence!
        Names don't exist in isolation - their value depends on competitive positioning.
        
        Args:
            primitives: Phonetic primitives from Level 1
            domain: Target domain
            context: Optional context (genre, color, position, etc.)
            economy_data: Optional list of competitor names for economic analysis
            
        Returns:
            Domain-contextualized score (0-100)
        """
        weights = self.domain_weights.get(domain, self.domain_weights[Domain.GENERIC])
        
        # Weighted sum of primitives
        weighted_sum = 0.0
        feature_count = 0
        
        for feature, weight in weights.items():
            if feature in primitives:
                weighted_sum += primitives[feature] * weight
                feature_count += 1
        
        # Normalize by number of features
        if feature_count > 0:
            base_score = (weighted_sum / feature_count) * 50 + 50  # Center at 50
        else:
            base_score = 50.0
        
        # Apply congruence multiplier (if context provided)
        congruence_multiplier = self._calculate_congruence(
            primitives, domain, context
        )
        
        # NEW: Economic positioning factor
        economy_factor = self._calculate_economy_factor(
            primitives, domain, economy_data
        )
        
        # Apply saturation penalty (now handled within economy analysis)
        saturation_penalty = self._calculate_saturation_penalty(
            primitives, domain, context
        )
        
        # UPDATED FORMULA: Include economic interdependence
        domain_score = (base_score * congruence_multiplier * 
                       (1 - saturation_penalty) * economy_factor)
        
        return max(0.0, min(100.0, domain_score))
    
    def _calculate_congruence(self, primitives: Dict, domain: Domain, 
                             context: Optional[Dict]) -> float:
        """
        Calculate context-congruence multiplier.
        
        Returns multiplier (typically 0.5 to 2.0)
        """
        if not context or domain not in self.congruence_matrices:
            return 1.0
        
        congruence_matrix = self.congruence_matrices[domain]
        
        # Get context key (genre, color, position, etc.)
        context_key = context.get('genre') or context.get('color') or context.get('position')
        
        if not context_key or context_key not in congruence_matrix:
            return 1.0
        
        # Apply context-specific multipliers
        multipliers = congruence_matrix[context_key]
        avg_multiplier = 1.0
        count = 0
        
        for feature, multiplier in multipliers.items():
            if feature in primitives and primitives[feature] > 50:  # Feature is prominent
                avg_multiplier += (multiplier - 1.0) * (primitives[feature] / 100)
                count += 1
        
        return avg_multiplier if count > 0 else 1.0
    
    def _calculate_economy_factor(self, primitives: Dict, domain: Domain,
                                  economy_data: Optional[List[Dict]]) -> float:
        """
        Calculate economic positioning factor (0.5 to 1.5).
        
        This is THE KEY INSIGHT: Names don't exist in isolation.
        Their value depends on competitive dynamics and relative positioning.
        
        Returns multiplier based on:
        - Scarcity (rare patterns = valuable)
        - Strategic differentiation (different in ways that matter)
        - Saturation (overused patterns lose value)
        - Competitive position (which cluster are you in?)
        """
        if not economy_data or len(economy_data) < 10:
            return 1.0  # Neutral if no market data
        
        try:
            # Perform economic analysis
            name = primitives.get('name', 'unknown')
            economy_analysis = self.economy_analyzer.analyze_name_economy(
                name, primitives, economy_data, domain.value
            )
            
            # Extract brand economy score (0-100)
            brand_economy = economy_analysis['brand_economy_score']
            
            # Convert to multiplier (0.5 to 1.5)
            # 100 = 1.5×, 50 = 1.0×, 0 = 0.5×
            economy_multiplier = 0.5 + (brand_economy / 100)
            
            logger.debug(f"Economy factor for '{name}': {economy_multiplier:.2f}× "
                        f"(brand_economy={brand_economy:.1f})")
            
            return economy_multiplier
        
        except Exception as e:
            logger.debug(f"Economy analysis failed: {e}")
            return 1.0  # Neutral on error
    
    def _calculate_saturation_penalty(self, primitives: Dict, domain: Domain,
                                     context: Optional[Dict]) -> float:
        """
        Calculate saturation penalty (0.0 to 1.0).
        
        NOTE: Saturation is now primarily handled in economy_factor.
        This method kept for backward compatibility.
        
        Returns penalty fraction (0 = no penalty, 1 = full penalty)
        """
        if domain not in self.saturation_thresholds or not context:
            return 0.0
        
        # Minimal saturation check (detailed analysis in economy_factor)
        return 0.0
    
    # ========================================================================
    # LEVEL 3: PREDETERMINED FEATURE INTEGRATION
    # ========================================================================
    
    def integrate_fundamentals(self, domain_score: float, fundamentals: Dict,
                               primitives: Dict) -> Dict:
        """
        Level 3: Integrate phonetic score with predetermined features.
        
        Formula: N_score = α×S_domain + β×fundamentals + γ×interactions
        
        Args:
            domain_score: Score from Level 2
            fundamentals: Domain-specific control variables
            primitives: Phonetic primitives (for interactions)
            
        Returns:
            Dictionary with integrated score and components
        """
        # Default mixing coefficients (can be learned)
        alpha = 0.35  # Phonetic weight
        beta = 0.50   # Fundamentals weight
        gamma = 0.15  # Interactions weight
        
        # Fundamental score (normalize to 0-100)
        fundamental_score = self._normalize_fundamentals(fundamentals)
        
        # Interaction effects
        interaction_score = self._calculate_interactions(
            domain_score, fundamentals, primitives
        )
        
        # Combined score
        n_score = (alpha * domain_score + 
                   beta * fundamental_score + 
                   gamma * interaction_score)
        
        return {
            'n_score': n_score,
            'domain_score': domain_score,
            'fundamental_score': fundamental_score,
            'interaction_score': interaction_score,
            'components': {
                'phonetic': alpha * domain_score,
                'fundamentals': beta * fundamental_score,
                'interactions': gamma * interaction_score,
            }
        }
    
    def _normalize_fundamentals(self, fundamentals: Dict) -> float:
        """Normalize fundamental features to 0-100 scale."""
        if not fundamentals:
            return 50.0
        
        # Domain-specific normalization (would be learned)
        # For now, simple average
        values = list(fundamentals.values())
        numeric_values = [v for v in values if isinstance(v, (int, float))]
        
        if not numeric_values:
            return 50.0
        
        return np.mean(numeric_values)
    
    def _calculate_interactions(self, domain_score: float, fundamentals: Dict,
                               primitives: Dict) -> float:
        """
        Calculate interaction effects.
        
        Examples:
        - Hurricane: harshness × wind_speed
        - Band: memorability × decade
        - MTG: harshness × CMC
        """
        # Placeholder: Domain-specific interactions would be defined here
        # For now, return simple product of domain_score and fundamental mean
        
        if not fundamentals:
            return domain_score
        
        fundamental_score = self._normalize_fundamentals(fundamentals)
        
        # Simple multiplicative interaction
        interaction = (domain_score / 100) * (fundamental_score / 100) * 100
        
        return interaction
    
    # ========================================================================
    # LEVEL 4: OUTCOME PREDICTION
    # ========================================================================
    
    def predict_outcome(self, n_score: float, link_function: LinkFunction,
                       **kwargs) -> Any:
        """
        Level 4: Transform integrated score to outcome prediction.
        
        Args:
            n_score: Integrated score from Level 3
            link_function: Transformation function
            **kwargs: Additional parameters for link function
            
        Returns:
            Predicted outcome (type depends on link function)
        """
        if link_function == LinkFunction.IDENTITY:
            # Linear regression (continuous outcome)
            return n_score
        
        elif link_function == LinkFunction.LOGIT:
            # Binary classification (probability)
            # Logit: p = 1 / (1 + exp(-z))
            z = (n_score - 50) / 10  # Center and scale
            probability = 1 / (1 + np.exp(-z))
            return probability
        
        elif link_function == LinkFunction.LOG:
            # Log-linear (for positive continuous outcomes)
            return np.exp(n_score / 20)  # Scale adjustment
        
        elif link_function == LinkFunction.SOFTMAX:
            # Multiclass (requires multiple scores)
            scores = kwargs.get('scores', [n_score])
            exp_scores = np.exp(scores)
            probabilities = exp_scores / np.sum(exp_scores)
            return probabilities
        
        else:
            return n_score
    
    # ========================================================================
    # COMPLETE HIERARCHICAL ANALYSIS
    # ========================================================================
    
    def analyze_hierarchical(self, name: str, domain: Domain,
                            context: Optional[Dict] = None,
                            fundamentals: Optional[Dict] = None,
                            link_function: LinkFunction = LinkFunction.IDENTITY,
                            all_names: Optional[List[str]] = None,
                            economy_data: Optional[List[Dict]] = None) -> Dict:
        """
        Complete 4-level hierarchical analysis.
        
        Args:
            name: Name to analyze
            domain: Target domain
            context: Optional context (genre, color, etc.)
            fundamentals: Optional predetermined features
            link_function: Outcome transformation function
            all_names: Optional list for uniqueness calculation
            economy_data: Optional list of competitor data for economic positioning
            
        Returns:
            Complete analysis with all 4 levels
        """
        # Level 1: Extract primitives
        primitives = self.extract_primitives(name, all_names)
        primitives['name'] = name  # Add name for economy analysis
        
        # Level 2: Domain-contextualized score (NOW WITH ECONOMY!)
        domain_score = self.calculate_domain_score(primitives, domain, context, economy_data)
        
        # Level 3: Integrate fundamentals
        if fundamentals is None:
            fundamentals = {}
        
        integration = self.integrate_fundamentals(domain_score, fundamentals, primitives)
        
        # Level 4: Outcome prediction
        outcome = self.predict_outcome(
            integration['n_score'],
            link_function
        )
        
        return {
            'name': name,
            'domain': domain.value,
            'level_1_primitives': primitives,
            'level_2_domain_score': domain_score,
            'level_3_integration': integration,
            'level_4_outcome': outcome,
            'context': context,
            'fundamentals': fundamentals,
        }
    
    # ========================================================================
    # CONSERVATIVE APPROACH (for comparison)
    # ========================================================================
    
    def analyze_conservative(self, name: str, domain: Domain,
                            all_names: Optional[List[str]] = None) -> Dict:
        """
        Conservative approach: Simple linear combination of standardized features.
        
        No context, no interactions, just weighted sum of base features.
        """
        primitives = self.extract_primitives(name, all_names)
        weights = self.domain_weights.get(domain, self.domain_weights[Domain.GENERIC])
        
        # Simple weighted sum
        score = 0.0
        feature_count = 0
        
        for feature, weight in weights.items():
            if feature in primitives:
                score += primitives[feature] * weight
                feature_count += 1
        
        # Normalize
        if feature_count > 0:
            score = (score / feature_count) * 50 + 50
        else:
            score = 50.0
        
        return {
            'name': name,
            'domain': domain.value,
            'approach': 'conservative',
            'score': max(0.0, min(100.0, score)),
            'primitives': primitives,
        }
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def detect_domain(self, **kwargs) -> Domain:
        """
        Auto-detect domain from context clues.
        
        Args:
            **kwargs: Context clues (has_wind_speed, has_cmc, has_genre, etc.)
            
        Returns:
            Detected domain
        """
        if kwargs.get('has_wind_speed') or kwargs.get('is_storm'):
            return Domain.HURRICANE
        elif kwargs.get('has_cmc') or kwargs.get('has_color'):
            return Domain.MTG
        elif kwargs.get('has_genre') or kwargs.get('is_music'):
            return Domain.BAND
        elif kwargs.get('has_market_cap') or kwargs.get('is_crypto'):
            return Domain.CRYPTO
        elif kwargs.get('has_position') or kwargs.get('is_nba'):
            return Domain.NBA
        elif kwargs.get('is_nfl'):
            return Domain.NFL
        elif kwargs.get('is_drug') or kwargs.get('is_diagnosis'):
            return Domain.MENTAL_HEALTH
        else:
            return Domain.GENERIC
    
    def update_weights(self, domain: Domain, new_weights: Dict):
        """Update learned weights for a domain."""
        if domain in self.domain_weights:
            self.domain_weights[domain].update(new_weights)
        else:
            self.domain_weights[domain] = new_weights
        
        logger.info(f"Updated weights for {domain.value}")
    
    def get_feature_importance(self, domain: Domain) -> List[Tuple[str, float]]:
        """
        Get feature importance ranking for a domain.
        
        Returns:
            List of (feature, weight) tuples sorted by absolute weight
        """
        weights = self.domain_weights.get(domain, {})
        importance = [(feat, abs(weight)) for feat, weight in weights.items()]
        importance.sort(key=lambda x: x[1], reverse=True)
        return importance


# Module-level singleton
_formula_manager = None

def get_formula_manager() -> FormulaManager:
    """Get singleton FormulaManager instance."""
    global _formula_manager
    if _formula_manager is None:
        _formula_manager = FormulaManager()
    return _formula_manager

