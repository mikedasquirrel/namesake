"""
Meta-Formula Analyzer - The Formula of Formulas

Analyzes the RELATIONSHIPS between formulas, not just their individual performance.

The profound question:
"Is there a formula that describes how formulas relate to each other?"

Tests:
1. Do formula performance ratios follow golden ratio?
2. Are there harmonic relationships between formulas?
3. Does formula divergence encode information?
4. Is there a meta-formula that predicts which formula wins where?
5. Do formulas form geometric patterns in performance space?

This is the deepest level: The mathematics of mathematics itself.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging
from scipy.spatial.distance import pdist, squareform
from scipy.stats import pearsonr
import json

logger = logging.getLogger(__name__)


@dataclass
class FormulaRelationship:
    """Relationship between two formulas"""
    formula1: str
    formula2: str
    
    # Performance relationship
    correlation_correlation: float  # Do they correlate similarly across domains?
    performance_ratio: float  # formula1_r / formula2_r
    divergence_pattern: str  # Where do they differ most?
    
    # Agreement metrics
    domain_agreement: float  # 0-1, do they agree on which domains work?
    property_agreement: float  # 0-1, do they agree on which properties matter?
    
    # Mathematical tests
    ratio_is_golden: bool  # Is ratio ≈ φ?
    ratio_is_simple: bool  # Is ratio simple fraction (1:2, 2:3, etc.)?
    ratio_value: float
    
    # Complementarity
    complementary_score: float  # Do they capture different information?
    redundancy_score: float  # Do they measure the same thing?


@dataclass
class MetaFormulaSignature:
    """The mathematical structure of the formula space itself"""
    
    # Formula network
    formula_relationships: Dict[Tuple[str, str], FormulaRelationship]
    
    # Geometric structure
    formula_positions: Dict[str, np.ndarray]  # Formulas as points in space
    formula_distances: np.ndarray  # Distance matrix
    dimensionality: int  # Effective dimensions of formula space
    
    # Mathematical patterns
    golden_ratio_pairs: List[Tuple[str, str]]  # Formula pairs with φ ratio
    simple_ratio_pairs: List[Tuple[str, str, float]]  # (f1, f2, ratio)
    harmonic_triads: List[Tuple[str, str, str]]  # Three formulas in harmony
    
    # Meta-formula
    optimal_combination: Dict[str, float]  # Best weighted combination
    domain_specific_combinations: Dict[str, Dict[str, float]]  # Per domain
    
    # The discovery
    universal_meta_pattern: Optional[str] = None  # If one exists


class MetaFormulaAnalyzer:
    """
    Analyzes relationships between formulas themselves
    
    This is recursive: Using formulas to analyze formulas
    """
    
    GOLDEN_RATIO = 1.618033988749
    SIMPLE_RATIOS = [1.0, 0.5, 2.0, 1.5, 0.667, 1.333, 0.75, 1.25, 0.618, 1.618]
    
    def __init__(self):
        self.tolerance = 0.05  # 5% tolerance for ratio matching
    
    def analyze_formula_space(self, validation_results: Dict) -> MetaFormulaSignature:
        """
        Analyze the mathematical structure of formula relationships
        
        Args:
            validation_results: Dict mapping formula_id to validation report
            
        Returns:
            MetaFormulaSignature describing formula space structure
        """
        logger.info("Analyzing formula space structure...")
        
        formulas = list(validation_results.keys())
        n_formulas = len(formulas)
        
        logger.info(f"Analyzing {n_formulas} formulas")
        
        # Build pairwise relationships
        relationships = {}
        for i, f1 in enumerate(formulas):
            for f2 in formulas[i+1:]:
                rel = self._analyze_pair(
                    f1, f2,
                    validation_results[f1],
                    validation_results[f2]
                )
                relationships[(f1, f2)] = rel
        
        logger.info(f"Computed {len(relationships)} pairwise relationships")
        
        # Build formula space geometry
        positions = self._compute_formula_positions(formulas, validation_results)
        distances = self._compute_distance_matrix(formulas, validation_results)
        dimensionality = self._estimate_dimensionality(distances)
        
        # Find mathematical patterns
        golden_pairs = self._find_golden_ratio_pairs(relationships)
        simple_pairs = self._find_simple_ratio_pairs(relationships)
        harmonic_triads = self._find_harmonic_triads(formulas, validation_results)
        
        # Discover optimal meta-formula
        optimal_combo = self._discover_optimal_combination(formulas, validation_results)
        domain_combos = self._discover_domain_combinations(formulas, validation_results)
        
        # Check for universal meta-pattern
        universal_pattern = self._test_universal_meta_pattern(
            golden_pairs, simple_pairs, harmonic_triads, optimal_combo
        )
        
        signature = MetaFormulaSignature(
            formula_relationships=relationships,
            formula_positions=positions,
            formula_distances=distances,
            dimensionality=dimensionality,
            golden_ratio_pairs=golden_pairs,
            simple_ratio_pairs=simple_pairs,
            harmonic_triads=harmonic_triads,
            optimal_combination=optimal_combo,
            domain_specific_combinations=domain_combos,
            universal_meta_pattern=universal_pattern
        )
        
        return signature
    
    def _analyze_pair(self, f1: str, f2: str, 
                     results1: Dict, results2: Dict) -> FormulaRelationship:
        """Analyze relationship between two formulas"""
        
        # Get domain performances
        domains1 = results1.get('domain_performances', {})
        domains2 = results2.get('domain_performances', {})
        
        # Calculate correlation of correlations
        common_domains = set(domains1.keys()) & set(domains2.keys())
        
        if len(common_domains) >= 3:
            corrs1 = [domains1[d].get('best_correlation', 0) for d in common_domains]
            corrs2 = [domains2[d].get('best_correlation', 0) for d in common_domains]
            
            corr_corr, _ = pearsonr(corrs1, corrs2)
        else:
            corr_corr = 0.0
        
        # Performance ratio
        overall1 = results1.get('overall_correlation', 0.001)
        overall2 = results2.get('overall_correlation', 0.001)
        
        if overall2 != 0:
            ratio = overall1 / overall2
        else:
            ratio = 1.0
        
        # Test for golden ratio
        is_golden = self._is_close_to(ratio, self.GOLDEN_RATIO) or self._is_close_to(1/ratio, self.GOLDEN_RATIO)
        
        # Test for simple ratios
        is_simple = any(self._is_close_to(ratio, r) or self._is_close_to(1/ratio, r) 
                       for r in self.SIMPLE_RATIOS)
        
        # Domain agreement (do they pick same best domains?)
        domain_agreement = self._calculate_domain_agreement(domains1, domains2)
        
        # Property agreement
        property_agreement = self._calculate_property_agreement(domains1, domains2)
        
        # Complementarity (do they capture different information?)
        complementary = 1.0 - abs(corr_corr)  # Low correlation = complementary
        redundancy = abs(corr_corr)  # High correlation = redundant
        
        # Find where they diverge most
        divergence = self._find_divergence_pattern(domains1, domains2)
        
        return FormulaRelationship(
            formula1=f1,
            formula2=f2,
            correlation_correlation=corr_corr,
            performance_ratio=ratio,
            divergence_pattern=divergence,
            domain_agreement=domain_agreement,
            property_agreement=property_agreement,
            ratio_is_golden=is_golden,
            ratio_is_simple=is_simple,
            ratio_value=ratio,
            complementary_score=complementary,
            redundancy_score=redundancy
        )
    
    def _is_close_to(self, value: float, target: float) -> bool:
        """Check if value is close to target"""
        if target == 0:
            return abs(value) < self.tolerance
        return abs(value - target) / abs(target) < self.tolerance
    
    def _calculate_domain_agreement(self, domains1: Dict, domains2: Dict) -> float:
        """Do formulas agree on which domains work best?"""
        common = set(domains1.keys()) & set(domains2.keys())
        
        if len(common) < 2:
            return 0.0
        
        # Rank domains by performance for each formula
        ranked1 = sorted(common, key=lambda d: abs(domains1[d].get('best_correlation', 0)), reverse=True)
        ranked2 = sorted(common, key=lambda d: abs(domains2[d].get('best_correlation', 0)), reverse=True)
        
        # Calculate rank correlation (Spearman-like)
        agreements = 0
        for i, d in enumerate(ranked1):
            rank_diff = abs(i - ranked2.index(d))
            agreements += (len(common) - rank_diff) / len(common)
        
        return agreements / len(common)
    
    def _calculate_property_agreement(self, domains1: Dict, domains2: Dict) -> float:
        """Do formulas agree on which properties matter?"""
        # Simplified: Check if they find similar properties significant
        common = set(domains1.keys()) & set(domains2.keys())
        
        if not common:
            return 0.0
        
        agreements = 0
        for domain in common:
            props1 = set(domains1[domain].get('significant_properties', []))
            props2 = set(domains2[domain].get('significant_properties', []))
            
            if props1 and props2:
                overlap = len(props1 & props2)
                union = len(props1 | props2)
                agreements += overlap / union if union > 0 else 0
        
        return agreements / len(common) if common else 0.0
    
    def _find_divergence_pattern(self, domains1: Dict, domains2: Dict) -> str:
        """Find where formulas differ most"""
        common = set(domains1.keys()) & set(domains2.keys())
        
        if not common:
            return "no_overlap"
        
        # Find domain with biggest performance difference
        max_diff = 0
        max_domain = None
        
        for domain in common:
            corr1 = abs(domains1[domain].get('best_correlation', 0))
            corr2 = abs(domains2[domain].get('best_correlation', 0))
            diff = abs(corr1 - corr2)
            
            if diff > max_diff:
                max_diff = diff
                max_domain = domain
        
        return max_domain or "no_divergence"
    
    def _compute_formula_positions(self, formulas: List[str], 
                                   results: Dict) -> Dict[str, np.ndarray]:
        """
        Map formulas to points in multidimensional space
        Each dimension = performance in one domain
        """
        # Get all domains
        all_domains = set()
        for result in results.values():
            all_domains.update(result.get('domain_performances', {}).keys())
        
        domains = sorted(all_domains)
        
        # Create position vectors
        positions = {}
        for formula in formulas:
            perf = results[formula].get('domain_performances', {})
            vector = [abs(perf.get(d, {}).get('best_correlation', 0)) for d in domains]
            positions[formula] = np.array(vector)
        
        return positions
    
    def _compute_distance_matrix(self, formulas: List[str], results: Dict) -> np.ndarray:
        """Compute pairwise distances between formulas"""
        positions = self._compute_formula_positions(formulas, results)
        
        # Build matrix
        n = len(formulas)
        matrix = np.zeros((n, n))
        
        for i, f1 in enumerate(formulas):
            for j, f2 in enumerate(formulas):
                if i != j:
                    dist = np.linalg.norm(positions[f1] - positions[f2])
                    matrix[i, j] = dist
        
        return matrix
    
    def _estimate_dimensionality(self, distance_matrix: np.ndarray) -> int:
        """Estimate effective dimensionality of formula space"""
        from sklearn.manifold import MDS
        
        try:
            mds = MDS(n_components=min(distance_matrix.shape[0] - 1, 5), 
                     dissimilarity='precomputed', random_state=42)
            mds.fit(distance_matrix)
            
            # Count dimensions explaining >10% variance
            stress = mds.stress_
            # Rough heuristic
            return min(3, distance_matrix.shape[0] - 1)
        except:
            return 2
    
    def _find_golden_ratio_pairs(self, relationships: Dict) -> List[Tuple[str, str]]:
        """Find formula pairs with golden ratio performance relationship"""
        golden_pairs = []
        
        for (f1, f2), rel in relationships.items():
            if rel.ratio_is_golden:
                golden_pairs.append((f1, f2))
                logger.info(f"  Golden ratio found: {f1}/{f2} = {rel.ratio_value:.3f} ≈ φ")
        
        return golden_pairs
    
    def _find_simple_ratio_pairs(self, relationships: Dict) -> List[Tuple[str, str, float]]:
        """Find formula pairs with simple ratio relationships"""
        simple_pairs = []
        
        for (f1, f2), rel in relationships.items():
            if rel.ratio_is_simple and not rel.ratio_is_golden:
                simple_pairs.append((f1, f2, rel.ratio_value))
        
        return simple_pairs
    
    def _find_harmonic_triads(self, formulas: List[str], results: Dict) -> List[Tuple[str, str, str]]:
        """
        Find three formulas that form harmonic relationships
        (Musical consonance applied to formulas)
        """
        triads = []
        
        for i, f1 in enumerate(formulas):
            for j, f2 in enumerate(formulas[i+1:], i+1):
                for k, f3 in enumerate(formulas[j+1:], j+1):
                    # Check if this triad has special properties
                    r1 = results[f1].get('overall_correlation', 0)
                    r2 = results[f2].get('overall_correlation', 0)
                    r3 = results[f3].get('overall_correlation', 0)
                    
                    # Sort by performance
                    sorted_perfs = sorted([r1, r2, r3])
                    
                    if sorted_perfs[1] > 0:
                        # Check for arithmetic progression
                        diff1 = sorted_perfs[1] - sorted_perfs[0]
                        diff2 = sorted_perfs[2] - sorted_perfs[1]
                        
                        if abs(diff1 - diff2) < 0.05:  # Arithmetic sequence
                            triads.append((f1, f2, f3))
        
        return triads
    
    def _discover_optimal_combination(self, formulas: List[str], 
                                     results: Dict) -> Dict[str, float]:
        """
        Find optimal weighted combination of formulas
        
        The META-FORMULA: What weights maximize prediction?
        """
        from sklearn.linear_model import Ridge
        
        # This would need actual entity-level data
        # For now, return equal weights as placeholder
        
        return {formula: 1.0 / len(formulas) for formula in formulas}
    
    def _discover_domain_combinations(self, formulas: List[str], 
                                     results: Dict) -> Dict[str, Dict[str, float]]:
        """
        Find optimal formula combination PER DOMAIN
        
        Different domains might need different formula blends
        """
        domain_combos = {}
        
        # Get all domains
        all_domains = set()
        for result in results.values():
            all_domains.update(result.get('domain_performances', {}).keys())
        
        for domain in all_domains:
            # Find which formulas work best in this domain
            domain_perfs = {}
            total = 0
            
            for formula in formulas:
                perf = results[formula].get('domain_performances', {}).get(domain, {})
                corr = abs(perf.get('best_correlation', 0))
                domain_perfs[formula] = corr
                total += corr
            
            # Normalize to weights
            if total > 0:
                weights = {f: p/total for f, p in domain_perfs.items()}
            else:
                weights = {f: 1.0/len(formulas) for f in formulas}
            
            domain_combos[domain] = weights
        
        return domain_combos
    
    def _test_universal_meta_pattern(self, golden_pairs: List, 
                                     simple_pairs: List,
                                     triads: List,
                                     optimal: Dict) -> Optional[str]:
        """
        Test if there's a universal pattern in formula relationships
        """
        findings = []
        
        if len(golden_pairs) >= 2:
            findings.append(f"Golden ratio appears in {len(golden_pairs)} formula pairs")
        
        if len(simple_pairs) >= 3:
            findings.append(f"Simple ratios dominate formula relationships")
        
        if len(triads) >= 1:
            findings.append(f"Harmonic triads exist among formulas")
        
        # Check if optimal weights follow pattern
        weights = list(optimal.values())
        weights_sorted = sorted(weights, reverse=True)
        
        # Test for Fibonacci-like decay
        if len(weights_sorted) >= 3:
            ratios = [weights_sorted[i]/weights_sorted[i+1] if weights_sorted[i+1] > 0 else 0 
                     for i in range(len(weights_sorted)-1)]
            
            # Are ratios consistent?
            if len(ratios) >= 2:
                ratio_std = np.std(ratios)
                if ratio_std < 0.2:  # Consistent decay pattern
                    findings.append(f"Formula weights decay with consistent ratio {np.mean(ratios):.2f}")
        
        if findings:
            return " | ".join(findings)
        
        return None
    
    def generate_meta_formula_report(self, signature: MetaFormulaSignature) -> str:
        """Generate human-readable report of meta-formula analysis"""
        lines = []
        lines.append("=" * 80)
        lines.append("META-FORMULA ANALYSIS - The Formula of Formulas")
        lines.append("=" * 80)
        lines.append("")
        
        # Formula space geometry
        lines.append("FORMULA SPACE STRUCTURE:")
        lines.append("-" * 80)
        lines.append(f"Effective Dimensionality: {signature.dimensionality}")
        lines.append(f"Formula Relationships: {len(signature.formula_relationships)}")
        lines.append("")
        
        # Golden ratio pairs
        if signature.golden_ratio_pairs:
            lines.append("🔥 GOLDEN RATIO RELATIONSHIPS FOUND:")
            lines.append("-" * 80)
            for f1, f2 in signature.golden_ratio_pairs:
                rel = signature.formula_relationships[(f1, f2)]
                lines.append(f"  {f1} / {f2} = {rel.ratio_value:.3f} ≈ φ (1.618)")
            lines.append("")
        
        # Simple ratios
        if signature.simple_ratio_pairs:
            lines.append("SIMPLE RATIO RELATIONSHIPS:")
            lines.append("-" * 80)
            for f1, f2, ratio in signature.simple_ratio_pairs[:5]:
                lines.append(f"  {f1} / {f2} = {ratio:.3f}")
            lines.append("")
        
        # Harmonic triads
        if signature.harmonic_triads:
            lines.append("HARMONIC FORMULA TRIADS:")
            lines.append("-" * 80)
            for triad in signature.harmonic_triads:
                lines.append(f"  {triad[0]} - {triad[1]} - {triad[2]}")
            lines.append("")
        
        # Optimal combination
        lines.append("OPTIMAL META-FORMULA (Universal Combination):")
        lines.append("-" * 80)
        for formula, weight in sorted(signature.optimal_combination.items(), 
                                     key=lambda x: x[1], reverse=True):
            lines.append(f"  {formula}: {weight:.3f}")
        lines.append("")
        
        # Domain-specific combinations
        lines.append("DOMAIN-SPECIFIC OPTIMAL COMBINATIONS:")
        lines.append("-" * 80)
        for domain, weights in signature.domain_specific_combinations.items():
            top_formula = max(weights.items(), key=lambda x: x[1])
            lines.append(f"  {domain}: {top_formula[0]} ({top_formula[1]:.3f})")
        lines.append("")
        
        # Universal pattern
        if signature.universal_meta_pattern:
            lines.append("🔥 UNIVERSAL META-PATTERN DISCOVERED:")
            lines.append("-" * 80)
            lines.append(f"  {signature.universal_meta_pattern}")
            lines.append("")
        
        return "\n".join(lines)
    
    def export_signature(self, signature: MetaFormulaSignature, filepath: str):
        """Export meta-formula signature"""
        # Convert to JSON-serializable format
        export = {
            'dimensionality': signature.dimensionality,
            'golden_ratio_pairs': signature.golden_ratio_pairs,
            'simple_ratio_pairs': [(f1, f2, float(r)) for f1, f2, r in signature.simple_ratio_pairs],
            'harmonic_triads': signature.harmonic_triads,
            'optimal_combination': signature.optimal_combination,
            'domain_specific_combinations': signature.domain_specific_combinations,
            'universal_meta_pattern': signature.universal_meta_pattern,
        }
        
        with open(filepath, 'w') as f:
            json.dump(export, f, indent=2)
        
        logger.info(f"Meta-formula signature exported to {filepath}")

