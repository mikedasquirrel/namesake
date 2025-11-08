"""
Convergence Analyzer - Extract Mathematical Invariants

Analyzes evolved formulas to discover:
1. What mathematical properties do successful formulas share?
2. Are there universal constants (golden ratio, primes, etc.)?
3. Which parameters matter most across domains?
4. What is the "signature" of an optimal formula?

This reveals: The mathematical structure of nominative determinism itself.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from scipy import stats
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import pdist
import logging
import json

from analyzers.formula_evolution import EvolutionHistory, Individual
from utils.formula_engine import FormulaBase

logger = logging.getLogger(__name__)


@dataclass
class ParameterAnalysis:
    """Analysis of a specific parameter across formulas"""
    parameter_name: str
    
    # Statistical properties
    mean: float
    median: float
    std: float
    min_val: float
    max_val: float
    
    # Correlation with fitness
    fitness_correlation: float
    correlation_p_value: float
    
    # Significance
    is_significant: bool  # p < 0.05
    importance_rank: Optional[int] = None


@dataclass
class MathematicalInvariant:
    """A discovered mathematical pattern or constant"""
    invariant_type: str  # 'ratio', 'constant', 'pattern', 'relationship'
    description: str
    value: Optional[float] = None
    formula: Optional[str] = None
    
    # Evidence strength
    occurrence_rate: float = 0.0  # How often this appears in top formulas
    consistency_score: float = 0.0  # How consistent the value is
    
    # Examples
    example_formulas: List[str] = field(default_factory=list)


@dataclass
class ConvergenceSignature:
    """The mathematical signature of converged formulas"""
    formula_type: str
    
    # Key parameters and their optimal values
    optimal_parameters: Dict[str, float] = field(default_factory=dict)
    parameter_importance: Dict[str, float] = field(default_factory=dict)
    
    # Mathematical invariants discovered
    invariants: List[MathematicalInvariant] = field(default_factory=list)
    
    # Relationships between parameters
    parameter_correlations: Dict[Tuple[str, str], float] = field(default_factory=dict)
    
    # Universal vs domain-specific
    universal_patterns: List[str] = field(default_factory=list)
    domain_specific_patterns: Dict[str, List[str]] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        result = asdict(self)
        # Convert tuple keys to strings
        result['parameter_correlations'] = {
            f"{k[0]}_vs_{k[1]}": v 
            for k, v in self.parameter_correlations.items()
        }
        return result


class ConvergenceAnalyzer:
    """
    Analyzes converged formulas to extract mathematical invariants
    """
    
    # Known mathematical constants to test for
    MATHEMATICAL_CONSTANTS = {
        'golden_ratio': 1.618033988749,
        'phi': 1.618033988749,
        'pi': 3.141592653590,
        'e': 2.718281828459,
        'sqrt_2': 1.414213562373,
        'sqrt_3': 1.732050807569,
        'sqrt_5': 2.236067977500,
        'golden_angle': 137.507764,  # degrees
    }
    
    FIBONACCI_NUMBERS = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610]
    PRIME_NUMBERS = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71]
    
    def __init__(self):
        self.tolerance = 0.05  # 5% tolerance for matching constants
    
    def analyze_evolution(self, history: EvolutionHistory,
                         top_n: int = 10) -> ConvergenceSignature:
        """
        Analyze an evolution history to extract convergence signature
        
        Args:
            history: Evolution history to analyze
            top_n: Number of top individuals to analyze
            
        Returns:
            ConvergenceSignature with discovered patterns
        """
        logger.info(f"Analyzing convergence for {history.formula_type} formulas")
        
        signature = ConvergenceSignature(formula_type=history.formula_type)
        
        # Get top performing individuals from final generation
        if not history.generations:
            logger.warning("No generations in history")
            return signature
        
        final_generation = history.generations[-1]
        top_individuals = sorted(
            final_generation.individuals,
            key=lambda x: x.fitness,
            reverse=True
        )[:top_n]
        
        logger.info(f"Analyzing top {len(top_individuals)} individuals")
        
        # Extract parameter values and fitnesses
        parameter_data = self._extract_parameter_data(top_individuals)
        
        # Analyze each parameter
        parameter_analyses = {}
        for param_name, values in parameter_data['parameters'].items():
            analysis = self._analyze_parameter(
                param_name,
                values,
                parameter_data['fitnesses']
            )
            parameter_analyses[param_name] = analysis
        
        # Rank parameters by importance
        sorted_params = sorted(
            parameter_analyses.items(),
            key=lambda x: abs(x[1].fitness_correlation),
            reverse=True
        )
        
        for rank, (param_name, analysis) in enumerate(sorted_params, 1):
            analysis.importance_rank = rank
            if analysis.is_significant:
                signature.parameter_importance[param_name] = abs(analysis.fitness_correlation)
        
        # Calculate optimal parameter values (from top performers)
        for param_name, values in parameter_data['parameters'].items():
            signature.optimal_parameters[param_name] = float(np.median(values))
        
        # Discover mathematical invariants
        signature.invariants = self._discover_invariants(
            parameter_data['parameters'],
            top_individuals
        )
        
        # Analyze parameter relationships
        signature.parameter_correlations = self._analyze_parameter_relationships(
            parameter_data['parameters']
        )
        
        # Identify universal patterns
        signature.universal_patterns = self._identify_universal_patterns(
            parameter_analyses,
            signature.invariants
        )
        
        logger.info(f"Found {len(signature.invariants)} mathematical invariants")
        logger.info(f"Identified {len(signature.universal_patterns)} universal patterns")
        
        return signature
    
    def _extract_parameter_data(self, individuals: List[Individual]) -> Dict:
        """Extract parameter values and fitnesses from individuals"""
        fitnesses = []
        parameters = {}
        
        for individual in individuals:
            fitnesses.append(individual.fitness)
            
            weights = individual.formula.get_weights()
            for param_name, param_value in weights.items():
                if param_name not in parameters:
                    parameters[param_name] = []
                parameters[param_name].append(param_value)
        
        return {
            'fitnesses': np.array(fitnesses),
            'parameters': {k: np.array(v) for k, v in parameters.items()}
        }
    
    def _analyze_parameter(self, param_name: str, values: np.ndarray,
                          fitnesses: np.ndarray) -> ParameterAnalysis:
        """Analyze a single parameter"""
        
        # Calculate statistics
        mean_val = float(np.mean(values))
        median_val = float(np.median(values))
        std_val = float(np.std(values))
        min_val = float(np.min(values))
        max_val = float(np.max(values))
        
        # Correlation with fitness
        if len(values) > 2 and std_val > 0:
            corr_coef, p_value = stats.pearsonr(values, fitnesses)
        else:
            corr_coef = 0.0
            p_value = 1.0
        
        is_significant = p_value < 0.05
        
        return ParameterAnalysis(
            parameter_name=param_name,
            mean=mean_val,
            median=median_val,
            std=std_val,
            min_val=min_val,
            max_val=max_val,
            fitness_correlation=corr_coef,
            correlation_p_value=p_value,
            is_significant=is_significant
        )
    
    def _discover_invariants(self, parameters: Dict[str, np.ndarray],
                            individuals: List[Individual]) -> List[MathematicalInvariant]:
        """Discover mathematical invariants in the formulas"""
        invariants = []
        
        # Test 1: Check for mathematical constants
        for param_name, values in parameters.items():
            median_val = np.median(values)
            
            for const_name, const_val in self.MATHEMATICAL_CONSTANTS.items():
                if self._is_close(median_val, const_val):
                    occurrence = np.mean([
                        self._is_close(v, const_val) for v in values
                    ])
                    
                    if occurrence > 0.5:  # More than 50% of formulas
                        invariant = MathematicalInvariant(
                            invariant_type='constant',
                            description=f"{param_name} converges to {const_name}",
                            value=const_val,
                            occurrence_rate=occurrence,
                            consistency_score=1.0 - float(np.std(values) / median_val) if median_val > 0 else 0,
                            example_formulas=[ind.formula.formula_id for ind in individuals[:3]]
                        )
                        invariants.append(invariant)
        
        # Test 2: Check for Fibonacci numbers
        for param_name, values in parameters.items():
            median_val = np.median(values)
            
            for fib in self.FIBONACCI_NUMBERS:
                if self._is_close(median_val, fib, tolerance=0.1):
                    occurrence = np.mean([
                        any(self._is_close(v, f, tolerance=0.1) for f in self.FIBONACCI_NUMBERS)
                        for v in values
                    ])
                    
                    if occurrence > 0.4:
                        invariant = MathematicalInvariant(
                            invariant_type='pattern',
                            description=f"{param_name} follows Fibonacci sequence",
                            value=float(fib),
                            occurrence_rate=occurrence,
                            example_formulas=[ind.formula.formula_id for ind in individuals[:3]]
                        )
                        invariants.append(invariant)
                        break
        
        # Test 3: Check for simple ratios between parameters
        param_names = list(parameters.keys())
        for i, name1 in enumerate(param_names):
            for name2 in param_names[i+1:]:
                values1 = parameters[name1]
                values2 = parameters[name2]
                
                # Avoid division by zero
                valid_indices = values2 != 0
                if not np.any(valid_indices):
                    continue
                
                ratios = values1[valid_indices] / values2[valid_indices]
                median_ratio = np.median(ratios)
                
                # Check if ratio is close to a simple fraction or constant
                for const_name, const_val in self.MATHEMATICAL_CONSTANTS.items():
                    if self._is_close(median_ratio, const_val):
                        occurrence = np.mean([
                            self._is_close(r, const_val) for r in ratios
                        ])
                        
                        if occurrence > 0.5:
                            invariant = MathematicalInvariant(
                                invariant_type='ratio',
                                description=f"{name1}/{name2} ≈ {const_name}",
                                value=const_val,
                                formula=f"{name1}/{name2}",
                                occurrence_rate=occurrence,
                                consistency_score=1.0 - float(np.std(ratios) / median_ratio) if median_ratio > 0 else 0
                            )
                            invariants.append(invariant)
        
        # Test 4: Check for parameter sums/products
        if len(param_names) >= 2:
            # Check if sum of certain parameters is constant
            all_values = [parameters[name] for name in param_names]
            
            # Try different combinations
            for i in range(len(param_names)):
                for j in range(i+1, len(param_names)):
                    sums = parameters[param_names[i]] + parameters[param_names[j]]
                    median_sum = np.median(sums)
                    
                    if np.std(sums) < 0.1 * median_sum and median_sum > 0:  # Low variance
                        invariant = MathematicalInvariant(
                            invariant_type='relationship',
                            description=f"{param_names[i]} + {param_names[j]} ≈ constant",
                            value=median_sum,
                            formula=f"{param_names[i]} + {param_names[j]}",
                            consistency_score=1.0 - float(np.std(sums) / median_sum)
                        )
                        invariants.append(invariant)
        
        return invariants
    
    def _is_close(self, value: float, target: float, tolerance: Optional[float] = None) -> bool:
        """Check if value is close to target within tolerance"""
        if tolerance is None:
            tolerance = self.tolerance
        
        if target == 0:
            return abs(value) < tolerance
        
        relative_diff = abs(value - target) / abs(target)
        return relative_diff < tolerance
    
    def _analyze_parameter_relationships(self, parameters: Dict[str, np.ndarray]) -> Dict[Tuple[str, str], float]:
        """Analyze correlations between parameters"""
        correlations = {}
        
        param_names = list(parameters.keys())
        
        for i, name1 in enumerate(param_names):
            for name2 in param_names[i+1:]:
                values1 = parameters[name1]
                values2 = parameters[name2]
                
                if len(values1) > 2:
                    try:
                        corr, _ = stats.pearsonr(values1, values2)
                        if abs(corr) > 0.5:  # Moderate to strong correlation
                            correlations[(name1, name2)] = float(corr)
                    except:
                        pass
        
        return correlations
    
    def _identify_universal_patterns(self, parameter_analyses: Dict[str, ParameterAnalysis],
                                     invariants: List[MathematicalInvariant]) -> List[str]:
        """Identify patterns that appear universal"""
        universal = []
        
        # Parameters with strong fitness correlation
        for param_name, analysis in parameter_analyses.items():
            if analysis.is_significant and abs(analysis.fitness_correlation) > 0.5:
                universal.append(f"Parameter '{param_name}' strongly predicts fitness (r={analysis.fitness_correlation:.3f})")
        
        # High-occurrence invariants
        for invariant in invariants:
            if invariant.occurrence_rate > 0.7:  # 70%+ occurrence
                universal.append(invariant.description)
        
        return universal
    
    def compare_formula_types(self, histories: Dict[str, EvolutionHistory]) -> Dict[str, Any]:
        """
        Compare convergence across different formula types
        
        Returns comprehensive comparison
        """
        logger.info(f"Comparing convergence across {len(histories)} formula types")
        
        signatures = {}
        for formula_type, history in histories.items():
            signatures[formula_type] = self.analyze_evolution(history)
        
        comparison = {
            'formula_types': list(signatures.keys()),
            'signatures': {k: v.to_dict() for k, v in signatures.items()},
            'cross_type_analysis': {}
        }
        
        # Find parameters that are important across multiple types
        all_important_params = {}
        for formula_type, sig in signatures.items():
            for param, importance in sig.parameter_importance.items():
                if param not in all_important_params:
                    all_important_params[param] = []
                all_important_params[param].append((formula_type, importance))
        
        # Universal parameters (important in multiple formula types)
        universal_params = {
            param: types
            for param, types in all_important_params.items()
            if len(types) >= 2
        }
        
        comparison['cross_type_analysis']['universal_parameters'] = {
            param: [{'type': t, 'importance': i} for t, i in types]
            for param, types in universal_params.items()
        }
        
        # Find common invariants
        all_invariants = []
        for sig in signatures.values():
            all_invariants.extend([inv.description for inv in sig.invariants])
        
        from collections import Counter
        invariant_counts = Counter(all_invariants)
        
        common_invariants = [
            inv for inv, count in invariant_counts.items()
            if count >= 2
        ]
        
        comparison['cross_type_analysis']['common_invariants'] = common_invariants
        
        return comparison
    
    def export_analysis(self, signature: ConvergenceSignature, filepath: str):
        """Export convergence analysis to file"""
        with open(filepath, 'w') as f:
            json.dump(signature.to_dict(), f, indent=2)
        
        logger.info(f"Convergence analysis exported to {filepath}")
    
    def generate_report(self, signature: ConvergenceSignature) -> str:
        """Generate human-readable report of convergence analysis"""
        lines = []
        lines.append("=" * 80)
        lines.append(f"CONVERGENCE ANALYSIS: {signature.formula_type.upper()}")
        lines.append("=" * 80)
        lines.append("")
        
        # Optimal parameters
        lines.append("OPTIMAL PARAMETER VALUES:")
        lines.append("-" * 80)
        
        sorted_params = sorted(
            signature.optimal_parameters.items(),
            key=lambda x: signature.parameter_importance.get(x[0], 0),
            reverse=True
        )
        
        for param, value in sorted_params:
            importance = signature.parameter_importance.get(param, 0)
            lines.append(f"  {param}: {value:.4f} (importance: {importance:.3f})")
        
        # Mathematical invariants
        if signature.invariants:
            lines.append("\nMATHEMATICAL INVARIANTS DISCOVERED:")
            lines.append("-" * 80)
            
            for inv in signature.invariants:
                lines.append(f"  Type: {inv.invariant_type}")
                lines.append(f"  Description: {inv.description}")
                if inv.value:
                    lines.append(f"  Value: {inv.value:.6f}")
                lines.append(f"  Occurrence Rate: {inv.occurrence_rate:.1%}")
                lines.append("")
        
        # Universal patterns
        if signature.universal_patterns:
            lines.append("\nUNIVERSAL PATTERNS:")
            lines.append("-" * 80)
            for pattern in signature.universal_patterns:
                lines.append(f"  • {pattern}")
        
        return "\n".join(lines)

