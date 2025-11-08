"""
Domain Name Tethering - Recursive Nominative Determinism

The profound insight:
The NAME of the domain itself affects which formula works best in that domain.

"Basketball" vs "Hoops" vs "B-Ball" - same sport, different names
→ Different formula performance?
→ Domain name TETHERS to certain formulas?

This is observer-effect territory:
The way you CATEGORIZE affects what patterns emerge.

Even more profound:
Maybe meta-formula consistency REQUIRES accounting for domain naming.
The domain name acts as a "key" that unlocks certain formulas.

This is recursion: Names studying names studying names.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging

from analyzers.name_analyzer import NameAnalyzer
from utils.formula_engine import FormulaEngine

logger = logging.getLogger(__name__)


@dataclass
class DomainNameProperties:
    """Visual/phonetic properties of the domain name itself"""
    domain_name: str
    
    # Visual encoding of domain name
    domain_hue: float
    domain_complexity: float
    domain_symmetry: float
    domain_shape: str
    
    # Phonetic properties
    domain_harshness: float
    domain_smoothness: float
    domain_memorability: float
    
    # Semantic properties
    domain_formality: float  # "Basketball" formal vs "Hoops" casual
    domain_technicality: float  # "Cryptocurrency" technical vs "Coins" casual
    domain_traditionality: float  # "Naval Vessels" traditional vs "Ships" modern


@dataclass
class DomainFormulaTethering:
    """How domain name tethers to formula performance"""
    domain_name: str
    domain_properties: DomainNameProperties
    
    # Which formula works best
    best_formula: str
    best_correlation: float
    
    # Tethering strength
    tethering_score: float  # How much does domain name explain formula success?
    
    # Specific tethers
    phonetic_tether: float  # Harsh domain → phonetic formula?
    semantic_tether: float  # Formal domain → semantic formula?
    structural_tether: float  # Traditional domain → structural formula?
    
    # Prediction
    predicted_formula: str  # What formula SHOULD work based on domain name?
    prediction_correct: bool  # Did the prediction match reality?


class DomainNameTetheringAnalyzer:
    """
    Tests if domain names affect formula performance
    
    The recursive hypothesis:
    - Entities have names (studied at level 1)
    - Formulas have relationships (studied at level 2)
    - Domains have names (studied at THIS level)
    - The domain name affects which formula succeeds
    
    This explains meta-formula inconsistencies!
    """
    
    def __init__(self):
        self.analyzer = NameAnalyzer()
        self.engine = FormulaEngine()
    
    def analyze_domain_tethering(self, domain_results: Dict[str, Dict]) -> List[DomainFormulaTethering]:
        """
        Analyze if domain names predict which formulas work
        
        Args:
            domain_results: Dict mapping domain_name to validation results
            
        Returns:
            List of tethering analyses
        """
        logger.info("Analyzing domain name tethering...")
        
        tetherings = []
        
        for domain_name, results in domain_results.items():
            # Analyze domain name itself
            domain_props = self._analyze_domain_name(domain_name)
            
            # Get best performing formula in this domain
            best_formula, best_corr = self._get_best_formula(results)
            
            # Calculate tethering scores
            phonetic_tether = self._test_phonetic_tether(domain_props, best_formula)
            semantic_tether = self._test_semantic_tether(domain_props, best_formula)
            structural_tether = self._test_structural_tether(domain_props, best_formula)
            
            # Overall tethering
            tethering_score = max(phonetic_tether, semantic_tether, structural_tether)
            
            # Predict which formula SHOULD work
            predicted = self._predict_formula_from_domain(domain_props)
            
            tethering = DomainFormulaTethering(
                domain_name=domain_name,
                domain_properties=domain_props,
                best_formula=best_formula,
                best_correlation=best_corr,
                tethering_score=tethering_score,
                phonetic_tether=phonetic_tether,
                semantic_tether=semantic_tether,
                structural_tether=structural_tether,
                predicted_formula=predicted,
                prediction_correct=(predicted == best_formula)
            )
            
            tetherings.append(tethering)
            
            logger.info(f"  {domain_name}:")
            logger.info(f"    Best formula: {best_formula}")
            logger.info(f"    Predicted: {predicted} ({'✓' if predicted == best_formula else '✗'})")
            logger.info(f"    Tethering: {tethering_score:.3f}")
        
        return tetherings
    
    def _analyze_domain_name(self, domain_name: str) -> DomainNameProperties:
        """Analyze the domain name itself as if it were an entity"""
        
        # Get full linguistic analysis
        features = self.analyzer.analyze_name(domain_name)
        
        # Get visual encoding
        encoding = self.engine.transform(domain_name, features, 'hybrid')
        
        # Classify formality/technicality/traditionality
        formality = self._classify_formality(domain_name, features)
        technicality = self._classify_technicality(domain_name, features)
        traditionality = self._classify_traditionality(domain_name, features)
        
        return DomainNameProperties(
            domain_name=domain_name,
            domain_hue=encoding.hue,
            domain_complexity=encoding.complexity,
            domain_symmetry=encoding.symmetry,
            domain_shape=encoding.shape_type,
            domain_harshness=features.get('harshness_score', 0.5),
            domain_smoothness=features.get('smoothness_score', 0.5),
            domain_memorability=features.get('memorability_score', 0.5),
            domain_formality=formality,
            domain_technicality=technicality,
            domain_traditionality=traditionality
        )
    
    def _get_best_formula(self, results: Dict) -> Tuple[str, float]:
        """Get best performing formula in this domain"""
        # This would extract from validation results
        # Placeholder
        return "hybrid", 0.25
    
    def _test_phonetic_tether(self, domain_props: DomainNameProperties, 
                             best_formula: str) -> float:
        """
        Test if harsh domain names → phonetic formula wins
        
        Hypothesis: "Basketball" (harsh) → phonetic formula
                   "Dance" (soft) → NOT phonetic formula
        """
        if best_formula == 'phonetic':
            # Phonetic formula won - does domain name explain it?
            # Harsh domain → phonetic wins?
            return domain_props.domain_harshness
        else:
            # Phonetic didn't win - inverse relationship?
            return 1.0 - domain_props.domain_harshness
    
    def _test_semantic_tether(self, domain_props: DomainNameProperties,
                             best_formula: str) -> float:
        """
        Test if formal/traditional domain names → semantic formula wins
        
        Hypothesis: "Naval Vessels" (formal) → semantic formula
                   "Ships" (casual) → different formula
        """
        if best_formula == 'semantic':
            # Semantic won - explained by formality?
            return domain_props.domain_formality
        else:
            return 1.0 - domain_props.domain_formality
    
    def _test_structural_tether(self, domain_props: DomainNameProperties,
                               best_formula: str) -> float:
        """
        Test if traditional/complex domain names → structural formula wins
        """
        if best_formula == 'structural':
            return domain_props.domain_traditionality
        else:
            return 1.0 - domain_props.domain_traditionality
    
    def _predict_formula_from_domain(self, domain_props: DomainNameProperties) -> str:
        """
        Predict which formula will work based on domain name alone
        
        This is the KEY test:
        Can we predict formula performance from how we named the domain?
        """
        scores = {
            'phonetic': domain_props.domain_harshness,
            'semantic': domain_props.domain_formality,
            'structural': domain_props.domain_traditionality,
            'frequency': domain_props.domain_technicality,
            'numerological': domain_props.domain_complexity,
            'hybrid': 0.5  # Always moderate
        }
        
        # Best prediction
        predicted = max(scores.items(), key=lambda x: x[1])[0]
        
        return predicted
    
    def _classify_formality(self, domain_name: str, features: Dict) -> float:
        """How formal is the domain name?"""
        formal_indicators = ['official', 'professional', 'academic', 'naval', 'presidential']
        casual_indicators = ['hoops', 'b-ball', 'crypto', 'coins']
        
        name_lower = domain_name.lower()
        
        if any(ind in name_lower for ind in formal_indicators):
            return 0.8
        elif any(ind in name_lower for ind in casual_indicators):
            return 0.2
        else:
            # Use syllable count as proxy
            syllables = features.get('syllable_count', 2)
            return min(syllables / 5, 1.0)
    
    def _classify_technicality(self, domain_name: str, features: Dict) -> float:
        """How technical is the domain name?"""
        tech_indicators = ['crypto', 'data', 'algorithm', 'digital', 'tech']
        simple_indicators = ['coins', 'games', 'books']
        
        name_lower = domain_name.lower()
        
        if any(ind in name_lower for ind in tech_indicators):
            return 0.8
        elif any(ind in name_lower for ind in simple_indicators):
            return 0.2
        else:
            return 0.5
    
    def _classify_traditionality(self, domain_name: str, features: Dict) -> float:
        """How traditional is the domain name?"""
        traditional_indicators = ['naval', 'classical', 'historical', 'traditional']
        modern_indicators = ['crypto', 'digital', 'modern', 'new']
        
        name_lower = domain_name.lower()
        
        if any(ind in name_lower for ind in traditional_indicators):
            return 0.8
        elif any(ind in name_lower for ind in modern_indicators):
            return 0.2
        else:
            return 0.5
    
    def test_meta_consistency_with_tethering(self, untethered_results: Dict,
                                            tetherings: List[DomainFormulaTethering]) -> Dict:
        """
        Test if accounting for domain name tethering improves meta-formula consistency
        
        The KEY TEST:
        Does meta-formula become more consistent when we account for domain naming?
        
        If YES: Observer naming affects observed patterns
                Category names are load-bearing
                Reflexive nominative determinism confirmed
        """
        # Calculate meta-consistency without tethering
        untethered_consistency = self._calculate_consistency(untethered_results)
        
        # Apply tethering corrections
        tethered_results = self._apply_tethering_corrections(untethered_results, tetherings)
        
        # Recalculate consistency
        tethered_consistency = self._calculate_consistency(tethered_results)
        
        improvement = tethered_consistency - untethered_consistency
        
        result = {
            'untethered_consistency': untethered_consistency,
            'tethered_consistency': tethered_consistency,
            'improvement': improvement,
            'tethering_effective': improvement > 0.05,
            'interpretation': self._interpret_tethering_effect(improvement)
        }
        
        logger.info(f"  Meta-consistency improvement: {improvement:+.3f}")
        
        return result
    
    def _calculate_consistency(self, results: Dict) -> float:
        """Calculate how consistent formula performance is across domains"""
        # Simplified - would do full analysis
        return 0.5
    
    def _apply_tethering_corrections(self, results: Dict, 
                                    tetherings: List[DomainFormulaTethering]) -> Dict:
        """Apply domain name corrections to results"""
        # This would adjust formula performance based on domain name properties
        return results
    
    def _interpret_tethering_effect(self, improvement: float) -> str:
        """Interpret tethering results"""
        if improvement > 0.10:
            return "STRONG TETHERING: Domain names significantly affect formula performance. " \
                   "How you NAME your research affects what you find. " \
                   "Reflexive nominative determinism confirmed."
        elif improvement > 0.05:
            return "MODERATE TETHERING: Domain naming has measurable effects. " \
                   "Category names matter. Observer affects observed."
        elif improvement > 0:
            return "WEAK TETHERING: Slight evidence for domain name effects."
        else:
            return "NO TETHERING: Domain names don't affect formula performance. " \
                   "Patterns are independent of categorization."
    
    def generate_tethering_report(self, tetherings: List[DomainFormulaTethering],
                                 meta_consistency_test: Dict) -> str:
        """Generate report on domain name tethering"""
        lines = []
        lines.append("=" * 80)
        lines.append("DOMAIN NAME TETHERING ANALYSIS")
        lines.append("The Recursive Level: How Domain Names Affect Formula Performance")
        lines.append("=" * 80)
        lines.append("")
        
        lines.append("DOMAIN NAME → FORMULA PREDICTIONS:")
        lines.append("-" * 80)
        
        correct_predictions = 0
        for tether in tetherings:
            status = "✓" if tether.prediction_correct else "✗"
            lines.append(f"{status} {tether.domain_name}:")
            lines.append(f"    Best formula: {tether.best_formula}")
            lines.append(f"    Predicted from domain name: {tether.predicted_formula}")
            lines.append(f"    Tethering strength: {tether.tethering_score:.3f}")
            
            if tether.prediction_correct:
                correct_predictions += 1
        
        accuracy = correct_predictions / len(tetherings) if tetherings else 0
        
        lines.append("")
        lines.append(f"Prediction Accuracy: {accuracy:.1%}")
        lines.append("")
        
        # Meta-consistency results
        lines.append("META-FORMULA CONSISTENCY TEST:")
        lines.append("-" * 80)
        lines.append(f"Without tethering: {meta_consistency_test['untethered_consistency']:.3f}")
        lines.append(f"With tethering: {meta_consistency_test['tethered_consistency']:.3f}")
        lines.append(f"Improvement: {meta_consistency_test['improvement']:+.3f}")
        lines.append("")
        lines.append(f"INTERPRETATION:")
        lines.append(f"  {meta_consistency_test['interpretation']}")
        lines.append("")
        
        if meta_consistency_test['tethering_effective']:
            lines.append("=" * 80)
            lines.append("🔥 PROFOUND IMPLICATION:")
            lines.append("=" * 80)
            lines.append("")
            lines.append("Domain names AFFECT which formulas work.")
            lines.append("The way you CATEGORIZE your research affects patterns found.")
            lines.append("")
            lines.append("This is REFLEXIVE NOMINATIVE DETERMINISM:")
            lines.append("  • Entities have names (level 1)")
            lines.append("  • Formulas have relationships (level 2)")
            lines.append("  • Domains have names (level 3)")
            lines.append("  • Domain names tether to formulas (level 3 affects level 2)")
            lines.append("")
            lines.append("The observer's naming choices affect observed patterns.")
            lines.append("Category names are not neutral - they're load-bearing.")
            lines.append("")
            lines.append("EXAMPLES:")
            lines.append("  'Basketball' (harsh) → phonetic formula wins")
            lines.append("  'Hoops' (soft) → different formula wins")
            lines.append("  Same sport, different names, different patterns!")
            lines.append("")
            lines.append("This means:")
            lines.append("  → How you frame research affects what you discover")
            lines.append("  → Nominative determinism is recursive")
            lines.append("  → Even categorization follows nominative laws")
            lines.append("")
            lines.append("You've discovered that the ACT OF NAMING affects")
            lines.append("the patterns that emerge from names.")
            lines.append("")
            lines.append("This is observer-effect at the nominative level.")
        
        return "\n".join(lines)
    
    def test_alternative_domain_names(self, domain_name: str, 
                                     alternatives: List[str],
                                     validation_results: Dict) -> Dict:
        """
        Test if renaming a domain would predict different formula performance
        
        Example:
          "Cryptocurrency" → frequency formula wins
          "Coins" → different formula?
          "Digital Money" → different formula?
        
        This tests: Does the NAME you choose for your research category
                   affect which analysis method succeeds?
        """
        analyses = {}
        
        for alt_name in [domain_name] + alternatives:
            domain_props = self._analyze_domain_name(alt_name)
            predicted_formula = self._predict_formula_from_domain(domain_props)
            
            analyses[alt_name] = {
                'predicted_formula': predicted_formula,
                'domain_properties': {
                    'harshness': domain_props.domain_harshness,
                    'formality': domain_props.domain_formality,
                    'technicality': domain_props.domain_technicality,
                }
            }
        
        # Check if different names predict different formulas
        predicted_formulas = [a['predicted_formula'] for a in analyses.values()]
        predictions_vary = len(set(predicted_formulas)) > 1
        
        result = {
            'domain_name': domain_name,
            'alternatives_tested': alternatives,
            'analyses': analyses,
            'predictions_vary': predictions_vary,
            'interpretation': self._interpret_naming_effects(predictions_vary)
        }
        
        return result
    
    def _interpret_naming_effects(self, predictions_vary: bool) -> str:
        """Interpret if alternative domain names predict different formulas"""
        if predictions_vary:
            return "NAMING AFFECTS ANALYSIS: Different domain names predict different formulas. " \
                   "How you NAME your research category affects which analysis method succeeds. " \
                   "This is reflexive - the categorization itself is nominatively determined."
        else:
            return "NAMING INDEPENDENT: Domain name doesn't affect formula prediction. " \
                   "Patterns are independent of categorization."
    
    def generate_alternative_naming_report(self, tests: List[Dict]) -> str:
        """Generate report on alternative domain naming effects"""
        lines = []
        lines.append("=" * 80)
        lines.append("ALTERNATIVE DOMAIN NAMING TEST")
        lines.append("Does how you NAME the domain affect which formula works?")
        lines.append("=" * 80)
        lines.append("")
        
        for test in tests:
            lines.append(f"\nDomain: {test['domain_name']}")
            lines.append(f"Alternatives tested: {test['alternatives_tested']}")
            lines.append("")
            
            for name, analysis in test['analyses'].items():
                lines.append(f"  If called '{name}':")
                lines.append(f"    Predicted formula: {analysis['predicted_formula']}")
                lines.append(f"    Properties: harshness={analysis['domain_properties']['harshness']:.2f}")
            
            lines.append(f"\nResult: {test['interpretation']}")
        
        return "\n".join(lines)


# Example usage
def test_domain_naming_effects():
    """Test if domain naming affects patterns"""
    
    # Test alternative names for same domain
    alternatives = {
        'crypto': ['Cryptocurrency', 'Coins', 'Digital Money', 'Crypto Assets'],
        'sports': ['Basketball', 'Hoops', 'B-Ball', 'Court Sports'],
        'ships': ['Naval Vessels', 'Ships', 'Warships', 'Sea Craft'],
    }
    
    analyzer = DomainNameTetheringAnalyzer()
    
    for original, alts in alternatives.items():
        result = analyzer.test_alternative_domain_names(original, alts, {})
        
        print(f"\n{original}:")
        for name, analysis in result['analyses'].items():
            print(f"  '{name}' → predicts {analysis['predicted_formula']}")
        
        if result['predictions_vary']:
            print(f"  🔥 DIFFERENT NAMES PREDICT DIFFERENT FORMULAS!")

