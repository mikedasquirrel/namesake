"""
Novel Pattern Discovery - Finding NEW Mathematical Structures

Discovers patterns from data rather than testing for known constants.

Like Newton discovering gravity - he didn't search for F=ma,
he observed effects and DERIVED the formula.

This system:
1. Finds CONSISTENT patterns (even if not φ, π, Fibonacci)
2. Discovers novel ratios, progressions, geometric forms
3. Maps emergent structures
4. Reports what IS, not what we expect

"What pattern emerges?" not "Does the golden ratio appear?"
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
import logging
from scipy import stats
from scipy.optimize import curve_fit
from sklearn.cluster import DBSCAN

logger = logging.getLogger(__name__)


@dataclass
class NovelPattern:
    """A discovered mathematical pattern"""
    pattern_type: str  # 'ratio', 'progression', 'power_law', 'periodic', 'geometric'
    description: str
    
    # Pattern parameters
    parameters: Dict[str, float]  # The discovered constants
    
    # Evidence
    occurrence_rate: float  # How often does this appear?
    consistency_score: float  # How consistent is it?
    confidence: float  # Statistical confidence
    
    # Context
    where_found: List[str]  # Which formulas/domains show this
    examples: List[str] = field(default_factory=list)
    
    # Significance
    is_novel: bool = True  # True if doesn't match known constants
    mathematical_form: Optional[str] = None  # If derivable formula


class NovelPatternDiscovery:
    """
    Discovers NEW mathematical patterns without presupposing what they should be
    """
    
    # Known constants (to check if pattern is truly novel)
    KNOWN_CONSTANTS = {
        'golden_ratio': 1.618033988749,
        'pi': 3.141592653590,
        'e': 2.718281828459,
        'sqrt_2': 1.414213562373,
        'sqrt_3': 1.732050807569,
        'sqrt_5': 2.236067977500,
        'golden_angle': 137.507764,
        'phi_squared': 2.618033988749,
        'silver_ratio': 2.414213562373,
    }
    
    def __init__(self):
        self.tolerance = 0.02  # 2% tolerance for matching
        self.min_consistency = 0.70  # 70% occurrence for valid pattern
    
    def discover_all_patterns(self, data: Dict) -> List[NovelPattern]:
        """
        Discover all mathematical patterns in data
        
        Args:
            data: Dictionary of analysis results
            
        Returns:
            List of NovelPattern objects (both known and novel)
        """
        logger.info("Discovering mathematical patterns...")
        
        patterns = []
        
        # 1. Discover ratio patterns
        ratio_patterns = self._discover_ratio_patterns(data)
        patterns.extend(ratio_patterns)
        
        # 2. Discover progression patterns
        progression_patterns = self._discover_progressions(data)
        patterns.extend(progression_patterns)
        
        # 3. Discover power law patterns
        power_patterns = self._discover_power_laws(data)
        patterns.extend(power_patterns)
        
        # 4. Discover periodic patterns
        periodic_patterns = self._discover_periodicity(data)
        patterns.extend(periodic_patterns)
        
        # 5. Discover geometric patterns
        geometric_patterns = self._discover_geometric_forms(data)
        patterns.extend(geometric_patterns)
        
        logger.info(f"Discovered {len(patterns)} total patterns")
        logger.info(f"  Novel patterns: {len([p for p in patterns if p.is_novel])}")
        logger.info(f"  Known patterns: {len([p for p in patterns if not p.is_novel])}")
        
        return patterns
    
    def _discover_ratio_patterns(self, data: Dict) -> List[NovelPattern]:
        """
        Find consistent ratios in data (not just testing for φ)
        
        Method:
        1. Calculate all possible ratios
        2. Find which ratios appear consistently
        3. Report WHATEVER ratio emerges (even if it's 1.742 or 2.331)
        """
        patterns = []
        
        # Extract numeric sequences
        sequences = self._extract_numeric_sequences(data)
        
        for seq_name, values in sequences.items():
            if len(values) < 3:
                continue
            
            # Calculate consecutive ratios
            ratios = []
            for i in range(len(values) - 1):
                if values[i+1] != 0:
                    ratio = values[i] / values[i+1]
                    ratios.append(ratio)
            
            if not ratios:
                continue
            
            # Find if ratios are consistent
            mean_ratio = np.mean(ratios)
            std_ratio = np.std(ratios)
            
            # Consistent if low variance
            if std_ratio / mean_ratio < 0.15:  # CV < 15%
                # We found a consistent ratio!
                
                # Check if it's novel
                is_novel = not any(
                    abs(mean_ratio - const) / const < self.tolerance
                    for const in self.KNOWN_CONSTANTS.values()
                )
                
                pattern = NovelPattern(
                    pattern_type='ratio',
                    description=f"Consistent ratio in {seq_name}: {mean_ratio:.4f}",
                    parameters={'ratio': mean_ratio, 'std': std_ratio},
                    occurrence_rate=1.0 - (std_ratio / mean_ratio),
                    consistency_score=1.0 - (std_ratio / mean_ratio),
                    confidence=0.95 if std_ratio / mean_ratio < 0.10 else 0.80,
                    where_found=[seq_name],
                    is_novel=is_novel,
                    mathematical_form=f"r = {mean_ratio:.6f}"
                )
                
                patterns.append(pattern)
                
                if is_novel:
                    logger.info(f"  🔥 NOVEL RATIO discovered in {seq_name}: {mean_ratio:.4f}")
                else:
                    # Check which known constant it matches
                    for name, value in self.KNOWN_CONSTANTS.items():
                        if abs(mean_ratio - value) / value < self.tolerance:
                            logger.info(f"  Known pattern ({name}) found in {seq_name}: {mean_ratio:.4f}")
                            break
        
        return patterns
    
    def _discover_progressions(self, data: Dict) -> List[NovelPattern]:
        """
        Discover if sequences follow novel progression rules
        
        Not just: Is it Fibonacci?
        But: What progression DOES it follow?
        """
        patterns = []
        
        sequences = self._extract_numeric_sequences(data)
        
        for seq_name, values in sequences.items():
            if len(values) < 4:
                continue
            
            # Test for arithmetic progression
            diffs = np.diff(values)
            if np.std(diffs) / (np.mean(np.abs(diffs)) + 1e-10) < 0.15:
                # Arithmetic progression found
                pattern = NovelPattern(
                    pattern_type='progression',
                    description=f"Arithmetic progression in {seq_name}",
                    parameters={'difference': float(np.mean(diffs))},
                    occurrence_rate=0.95,
                    consistency_score=1.0 - np.std(diffs) / (np.mean(np.abs(diffs)) + 1e-10),
                    confidence=0.90,
                    where_found=[seq_name],
                    is_novel=False,  # Arithmetic is known
                    mathematical_form=f"a_n = a_0 + {np.mean(diffs):.4f}*n"
                )
                patterns.append(pattern)
            
            # Test for geometric progression
            if all(v > 0 for v in values):
                ratios = [values[i+1]/values[i] for i in range(len(values)-1)]
                if np.std(ratios) / np.mean(ratios) < 0.15:
                    # Geometric progression found
                    mean_ratio = np.mean(ratios)
                    
                    pattern = NovelPattern(
                        pattern_type='progression',
                        description=f"Geometric progression in {seq_name}",
                        parameters={'ratio': float(mean_ratio)},
                        occurrence_rate=0.95,
                        consistency_score=1.0 - np.std(ratios) / np.mean(ratios),
                        confidence=0.90,
                        where_found=[seq_name],
                        is_novel=not self._is_known_constant(mean_ratio),
                        mathematical_form=f"a_n = a_0 * {mean_ratio:.4f}^n"
                    )
                    patterns.append(pattern)
                    
                    if pattern.is_novel:
                        logger.info(f"  🔥 NOVEL geometric progression: ratio={mean_ratio:.4f}")
        
        return patterns
    
    def _discover_power_laws(self, data: Dict) -> List[NovelPattern]:
        """
        Discover if relationships follow power laws: y = ax^b
        
        Find the ACTUAL exponent (might not be 2, might be 1.73 or 2.48)
        """
        patterns = []
        
        # Would need paired x,y data
        # Test various relationships for power law fits
        # Report discovered exponents (novel or known)
        
        return patterns
    
    def _discover_periodicity(self, data: Dict) -> List[NovelPattern]:
        """
        Discover periodic patterns
        
        Not just: sine wave
        But: What IS the period? What's the form?
        """
        patterns = []
        
        sequences = self._extract_numeric_sequences(data)
        
        for seq_name, values in sequences.items():
            if len(values) < 10:
                continue
            
            # FFT to find dominant frequencies
            fft = np.fft.fft(values - np.mean(values))
            frequencies = np.fft.fftfreq(len(values))
            power = np.abs(fft) ** 2
            
            # Find dominant frequency
            dominant_idx = np.argmax(power[1:len(power)//2]) + 1
            dominant_freq = abs(frequencies[dominant_idx])
            
            if dominant_freq > 0:
                period = 1.0 / dominant_freq
                
                # Check if periodic pattern is strong
                if power[dominant_idx] > np.mean(power) * 5:
                    pattern = NovelPattern(
                        pattern_type='periodic',
                        description=f"Periodic oscillation in {seq_name}",
                        parameters={'period': float(period), 'frequency': float(dominant_freq)},
                        occurrence_rate=0.80,
                        consistency_score=float(power[dominant_idx] / np.sum(power)),
                        confidence=0.75,
                        where_found=[seq_name],
                        is_novel=True,  # Specific period is always novel
                        mathematical_form=f"Oscillates with period={period:.2f}"
                    )
                    patterns.append(pattern)
                    
                    logger.info(f"  Periodic pattern found: period={period:.2f}")
        
        return patterns
    
    def _discover_geometric_forms(self, data: Dict) -> List[NovelPattern]:
        """
        Discover if data points form geometric shapes in space
        
        Not testing for known shapes, but discovering WHAT shape they form
        """
        patterns = []
        
        # Would need multidimensional point data
        # Use techniques like:
        # - Hull analysis (convex, concave, fractal?)
        # - Symmetry detection (what symmetry group?)
        # - Topology (holes, genus, etc.)
        # - Manifold learning (what manifold?)
        
        return patterns
    
    def _extract_numeric_sequences(self, data: Dict) -> Dict[str, List[float]]:
        """Extract numeric sequences from analysis data"""
        sequences = {}
        
        # Formula performance sequence
        if 'validations' in data:
            formulas = ['phonetic', 'semantic', 'structural', 'frequency', 'numerological', 'hybrid']
            correlations = []
            for f in formulas:
                if f in data['validations']:
                    corr = data['validations'][f].get('overall_correlation', 0)
                    correlations.append(abs(corr))
            
            if correlations:
                sequences['formula_correlations'] = correlations
        
        # Evolution fitness sequences
        if 'evolutions' in data:
            for formula, evolution in data['evolutions'].items():
                generations = evolution.get('generations', [])
                if generations:
                    fitnesses = [g.get('best_fitness', 0) for g in generations]
                    sequences[f'{formula}_fitness'] = fitnesses
        
        # Parameter weight sequences
        if 'convergences' in data:
            for formula, convergence in data['convergences'].items():
                params = convergence.get('optimal_parameters', {})
                if params:
                    weights = list(params.values())
                    sequences[f'{formula}_weights'] = weights
        
        return sequences
    
    def _is_known_constant(self, value: float) -> bool:
        """Check if value matches a known mathematical constant"""
        for const in self.KNOWN_CONSTANTS.values():
            if abs(value - const) / const < self.tolerance:
                return True
        return False
    
    def generate_pattern_report(self, patterns: List[NovelPattern]) -> str:
        """Generate report of discovered patterns"""
        lines = []
        lines.append("=" * 80)
        lines.append("NOVEL PATTERN DISCOVERY REPORT")
        lines.append("=" * 80)
        lines.append("")
        
        # Separate novel from known
        novel = [p for p in patterns if p.is_novel]
        known = [p for p in patterns if not p.is_novel]
        
        if novel:
            lines.append(f"🔥 NOVEL PATTERNS DISCOVERED: {len(novel)}")
            lines.append("-" * 80)
            for pattern in novel:
                lines.append(f"\nType: {pattern.pattern_type}")
                lines.append(f"Description: {pattern.description}")
                lines.append(f"Parameters: {pattern.parameters}")
                lines.append(f"Consistency: {pattern.consistency_score:.3f}")
                lines.append(f"Confidence: {pattern.confidence:.3f}")
                if pattern.mathematical_form:
                    lines.append(f"Formula: {pattern.mathematical_form}")
            lines.append("")
        
        if known:
            lines.append(f"\nKNOWN PATTERNS FOUND: {len(known)}")
            lines.append("-" * 80)
            for pattern in known:
                lines.append(f"  • {pattern.description}")
            lines.append("")
        
        if not patterns:
            lines.append("No consistent mathematical patterns discovered.")
            lines.append("Data may be too noisy or sample too small.")
        
        return "\n".join(lines)

