"""
Formula Validator - Cross-Domain Testing System

Tests transformation formulas across all research domains to determine:
1. Which visual properties correlate with outcomes
2. Which formulas predict best in which domains
3. Cross-domain consistency of formula performance
4. Statistical significance of correlations

This is where we discover: Does the formula capture real nominative patterns?
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from scipy import stats
from scipy.stats import pearsonr, spearmanr
import logging
import json
from datetime import datetime

from utils.formula_engine import FormulaEngine, VisualEncoding, FormulaBase
try:
    from core.unified_domain_model_extended import ExtendedDomainInterface, ExtendedDomainType, UnifiedDomainEntity
    DomainInterface = ExtendedDomainInterface
    DomainType = ExtendedDomainType
except ImportError:
    from core.unified_domain_model import UnifiedDomainInterface, DomainType, UnifiedDomainEntity
    DomainInterface = UnifiedDomainInterface

logger = logging.getLogger(__name__)


@dataclass
class CorrelationResult:
    """Result of correlation test between visual property and outcome"""
    visual_property: str
    outcome_metric: str
    correlation_coefficient: float
    p_value: float
    sample_size: int
    is_significant: bool  # p < 0.05
    effect_size: str  # small/medium/large/none


@dataclass
class FormulaPerformance:
    """Performance metrics for a formula in a specific domain"""
    formula_id: str
    domain: str
    
    # Overall correlation with outcomes
    best_correlation: float
    best_property: str
    
    # All property correlations
    property_correlations: Dict[str, CorrelationResult] = field(default_factory=dict)
    
    # Prediction accuracy
    binary_accuracy: Optional[float] = None  # For success/failure prediction
    rmse: Optional[float] = None  # For continuous outcomes
    
    # Sample size
    n_entities: int = 0
    n_with_outcome: int = 0
    
    # Statistical summary
    significant_properties: List[str] = field(default_factory=list)
    mean_correlation: float = 0.0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        result = asdict(self)
        # Convert CorrelationResult objects
        result['property_correlations'] = {
            k: asdict(v) for k, v in self.property_correlations.items()
        }
        return result


@dataclass
class CrossDomainReport:
    """Comprehensive report of formula performance across all domains"""
    formula_id: str
    timestamp: str
    
    # Performance by domain
    domain_performances: Dict[str, FormulaPerformance] = field(default_factory=dict)
    
    # Cross-domain metrics
    overall_correlation: float = 0.0
    consistency_score: float = 0.0  # How consistent across domains
    best_domain: Optional[str] = None
    worst_domain: Optional[str] = None
    
    # Universal patterns
    universal_properties: List[str] = field(default_factory=list)  # Significant across domains
    domain_specific_properties: Dict[str, List[str]] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        result = asdict(self)
        result['domain_performances'] = {
            k: v.to_dict() for k, v in self.domain_performances.items()
        }
        return result


class FormulaValidator:
    """
    Validates transformation formulas across domains
    """
    
    def __init__(self):
        self.formula_engine = FormulaEngine()
        self.domain_interface = DomainInterface()
        
        # Visual properties to test for correlation
        self.visual_properties = [
            'complexity', 'symmetry', 'angular_vs_curved',
            'hue', 'saturation', 'brightness',
            'x', 'y', 'z', 'rotation',
            'glow_intensity', 'fractal_dimension', 'pattern_density'
        ]
    
    def validate_formula(self, formula_id: str, 
                        domains: Optional[List] = None,
                        limit_per_domain: Optional[int] = None) -> CrossDomainReport:
        """
        Validate a formula across domains
        
        Args:
            formula_id: ID of formula to test
            domains: Which domains to test (None = all)
            limit_per_domain: Max entities per domain
            
        Returns:
            CrossDomainReport with full analysis
        """
        if domains is None:
            try:
                domains = list(DomainType)
            except:
                domains = ['crypto', 'election', 'ship', 'board_game', 'mlb_player']
        
        # Convert strings to enum if needed
        domain_enums = []
        for d in domains:
            if isinstance(d, str):
                try:
                    domain_enums.append(DomainType(d))
                except:
                    logger.warning(f"Unknown domain string: {d}")
            else:
                domain_enums.append(d)
        domains = domain_enums
        
        logger.info(f"Validating formula '{formula_id}' across {len(domains)} domains")
        
        report = CrossDomainReport(
            formula_id=formula_id,
            timestamp=datetime.now().isoformat()
        )
        
        # Test in each domain
        for domain in domains:
            logger.info(f"Testing in {domain.value}...")
            
            try:
                performance = self._test_formula_in_domain(
                    formula_id, domain, limit_per_domain
                )
                report.domain_performances[domain.value] = performance
            except Exception as e:
                logger.error(f"Error testing {domain.value}: {e}")
        
        # Compute cross-domain metrics
        self._compute_cross_domain_metrics(report)
        
        return report
    
    def _test_formula_in_domain(self, formula_id: str, domain: DomainType,
                                limit: Optional[int] = None) -> FormulaPerformance:
        """Test formula performance in a single domain"""
        
        # Load entities
        entities = self.domain_interface.load_domain(domain, limit=limit)
        
        if not entities:
            logger.warning(f"No entities loaded from {domain.value}")
            return FormulaPerformance(
                formula_id=formula_id,
                domain=domain.value,
                best_correlation=0.0,
                best_property="none"
            )
        
        logger.info(f"Loaded {len(entities)} entities from {domain.value}")
        
        # Transform all entities using formula
        for entity in entities:
            if not entity.linguistic_features:
                continue
            
            try:
                visual_encoding = self.formula_engine.transform(
                    entity.name,
                    entity.linguistic_features,
                    formula_id
                )
                entity.visual_encoding = visual_encoding.to_dict()
                entity.formula_id = formula_id
            except Exception as e:
                logger.error(f"Error transforming {entity.name}: {e}")
        
        # Filter to entities with both visual encoding and outcome
        valid_entities = [
            e for e in entities
            if e.visual_encoding is not None and e.outcome_metric is not None
        ]
        
        logger.info(f"Testing correlations on {len(valid_entities)} entities with outcomes")
        
        if len(valid_entities) < 10:
            logger.warning(f"Too few valid entities ({len(valid_entities)}) for reliable correlation")
            return FormulaPerformance(
                formula_id=formula_id,
                domain=domain.value,
                best_correlation=0.0,
                best_property="none",
                n_entities=len(entities),
                n_with_outcome=len(valid_entities)
            )
        
        # Test correlation for each visual property
        property_correlations = {}
        
        for prop in self.visual_properties:
            result = self._test_property_correlation(valid_entities, prop)
            if result:
                property_correlations[prop] = result
        
        # Find best correlation
        best_corr = 0.0
        best_prop = "none"
        
        if property_correlations:
            best_prop = max(property_correlations.items(), 
                          key=lambda x: abs(x[1].correlation_coefficient))
            best_corr = best_prop[1].correlation_coefficient
            best_prop = best_prop[0]
        
        # Calculate prediction accuracy for binary outcomes
        binary_accuracy = None
        if all(e.is_successful is not None for e in valid_entities):
            binary_accuracy = self._calculate_binary_accuracy(
                valid_entities, best_prop
            )
        
        # Calculate RMSE for continuous outcomes
        rmse = self._calculate_rmse(valid_entities, best_prop)
        
        # Identify significant properties
        significant = [
            prop for prop, result in property_correlations.items()
            if result.is_significant
        ]
        
        # Mean correlation strength
        mean_corr = np.mean([
            abs(r.correlation_coefficient) 
            for r in property_correlations.values()
        ]) if property_correlations else 0.0
        
        performance = FormulaPerformance(
            formula_id=formula_id,
            domain=domain.value,
            best_correlation=best_corr,
            best_property=best_prop,
            property_correlations=property_correlations,
            binary_accuracy=binary_accuracy,
            rmse=rmse,
            n_entities=len(entities),
            n_with_outcome=len(valid_entities),
            significant_properties=significant,
            mean_correlation=mean_corr
        )
        
        return performance
    
    def _test_property_correlation(self, entities: List[UnifiedDomainEntity],
                                  property_name: str) -> Optional[CorrelationResult]:
        """Test correlation between a visual property and outcome metric"""
        
        # Extract values
        visual_values = []
        outcome_values = []
        
        for entity in entities:
            if not entity.visual_encoding or entity.outcome_metric is None:
                continue
            
            visual_val = entity.visual_encoding.get(property_name)
            if visual_val is None:
                continue
            
            visual_values.append(visual_val)
            outcome_values.append(entity.outcome_metric)
        
        if len(visual_values) < 10:
            return None
        
        # Calculate Pearson correlation
        try:
            corr_coef, p_value = pearsonr(visual_values, outcome_values)
        except Exception as e:
            logger.error(f"Error calculating correlation for {property_name}: {e}")
            return None
        
        # Determine effect size
        abs_corr = abs(corr_coef)
        if abs_corr < 0.1:
            effect_size = "none"
        elif abs_corr < 0.3:
            effect_size = "small"
        elif abs_corr < 0.5:
            effect_size = "medium"
        else:
            effect_size = "large"
        
        return CorrelationResult(
            visual_property=property_name,
            outcome_metric="outcome",
            correlation_coefficient=corr_coef,
            p_value=p_value,
            sample_size=len(visual_values),
            is_significant=p_value < 0.05,
            effect_size=effect_size
        )
    
    def _calculate_binary_accuracy(self, entities: List[UnifiedDomainEntity],
                                   property_name: str) -> float:
        """Calculate prediction accuracy for binary success/failure"""
        
        # Use visual property as predictor
        visual_values = []
        success_values = []
        
        for entity in entities:
            if not entity.visual_encoding or entity.is_successful is None:
                continue
            
            visual_val = entity.visual_encoding.get(property_name)
            if visual_val is None:
                continue
            
            visual_values.append(visual_val)
            success_values.append(1 if entity.is_successful else 0)
        
        if len(visual_values) < 10:
            return 0.0
        
        # Use median split as threshold
        threshold = np.median(visual_values)
        predictions = [1 if v > threshold else 0 for v in visual_values]
        
        # Calculate accuracy
        correct = sum(p == s for p, s in zip(predictions, success_values))
        accuracy = correct / len(predictions)
        
        return accuracy
    
    def _calculate_rmse(self, entities: List[UnifiedDomainEntity],
                       property_name: str) -> Optional[float]:
        """Calculate RMSE for continuous outcome prediction"""
        
        visual_values = []
        outcome_values = []
        
        for entity in entities:
            if not entity.visual_encoding or entity.outcome_metric is None:
                continue
            
            visual_val = entity.visual_encoding.get(property_name)
            if visual_val is None:
                continue
            
            visual_values.append(visual_val)
            outcome_values.append(entity.outcome_metric)
        
        if len(visual_values) < 10:
            return None
        
        # Simple linear prediction: scale visual values to outcome range
        visual_array = np.array(visual_values)
        outcome_array = np.array(outcome_values)
        
        # Normalize visual values
        if visual_array.std() > 0:
            visual_norm = (visual_array - visual_array.mean()) / visual_array.std()
        else:
            visual_norm = visual_array
        
        # Scale to outcome range
        predictions = visual_norm * outcome_array.std() + outcome_array.mean()
        
        # Calculate RMSE
        rmse = np.sqrt(np.mean((predictions - outcome_array) ** 2))
        
        return float(rmse)
    
    def _compute_cross_domain_metrics(self, report: CrossDomainReport):
        """Compute cross-domain summary metrics"""
        
        if not report.domain_performances:
            return
        
        performances = list(report.domain_performances.values())
        
        # Overall correlation: mean of best correlations
        correlations = [abs(p.best_correlation) for p in performances]
        report.overall_correlation = float(np.mean(correlations))
        
        # Consistency: standard deviation of correlations (lower = more consistent)
        if len(correlations) > 1:
            std_corr = np.std(correlations)
            # Convert to 0-1 score (1 = perfect consistency)
            report.consistency_score = max(0, 1.0 - std_corr)
        else:
            report.consistency_score = 1.0
        
        # Best and worst domains
        if performances:
            best_perf = max(performances, key=lambda p: abs(p.best_correlation))
            worst_perf = min(performances, key=lambda p: abs(p.best_correlation))
            report.best_domain = best_perf.domain
            report.worst_domain = worst_perf.domain
        
        # Universal properties: significant in multiple domains
        property_counts = {}
        for perf in performances:
            for prop in perf.significant_properties:
                property_counts[prop] = property_counts.get(prop, 0) + 1
        
        # Universal if significant in >= 50% of domains
        threshold = len(performances) / 2
        report.universal_properties = [
            prop for prop, count in property_counts.items()
            if count >= threshold
        ]
        
        # Domain-specific properties
        for perf in performances:
            domain_specific = [
                prop for prop in perf.significant_properties
                if prop not in report.universal_properties
            ]
            if domain_specific:
                report.domain_specific_properties[perf.domain] = domain_specific
    
    def compare_formulas(self, formula_ids: List[str],
                        domains: Optional[List[DomainType]] = None,
                        limit_per_domain: Optional[int] = None) -> Dict[str, CrossDomainReport]:
        """
        Compare multiple formulas across domains
        
        Returns:
            Dictionary mapping formula_id to CrossDomainReport
        """
        results = {}
        
        for formula_id in formula_ids:
            logger.info(f"\n{'='*60}")
            logger.info(f"Testing formula: {formula_id}")
            logger.info(f"{'='*60}")
            
            report = self.validate_formula(formula_id, domains, limit_per_domain)
            results[formula_id] = report
        
        return results
    
    def rank_formulas(self, reports: Dict[str, CrossDomainReport]) -> List[Tuple[str, float]]:
        """
        Rank formulas by overall performance
        
        Returns:
            List of (formula_id, score) tuples, sorted best to worst
        """
        scores = []
        
        for formula_id, report in reports.items():
            # Composite score: correlation strength + consistency
            score = report.overall_correlation * 0.7 + report.consistency_score * 0.3
            scores.append((formula_id, score))
        
        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        
        return scores
    
    def export_results(self, report: CrossDomainReport, filepath: str):
        """Export validation results to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(report.to_dict(), f, indent=2)
        
        logger.info(f"Results exported to {filepath}")
    
    def generate_summary_report(self, reports: Dict[str, CrossDomainReport]) -> str:
        """Generate human-readable summary of formula comparison"""
        
        lines = []
        lines.append("=" * 80)
        lines.append("FORMULA VALIDATION SUMMARY")
        lines.append("=" * 80)
        lines.append("")
        
        # Rank formulas
        rankings = self.rank_formulas(reports)
        
        lines.append("OVERALL RANKINGS:")
        lines.append("-" * 80)
        for i, (formula_id, score) in enumerate(rankings, 1):
            report = reports[formula_id]
            lines.append(f"{i}. {formula_id}")
            lines.append(f"   Score: {score:.3f}")
            lines.append(f"   Mean Correlation: {report.overall_correlation:.3f}")
            lines.append(f"   Consistency: {report.consistency_score:.3f}")
            lines.append(f"   Best Domain: {report.best_domain}")
            lines.append(f"   Universal Properties: {', '.join(report.universal_properties) if report.universal_properties else 'None'}")
            lines.append("")
        
        # Domain-by-domain comparison
        lines.append("\nDOMAIN-BY-DOMAIN COMPARISON:")
        lines.append("-" * 80)
        
        domains = set()
        for report in reports.values():
            domains.update(report.domain_performances.keys())
        
        for domain in sorted(domains):
            lines.append(f"\n{domain.upper()}:")
            
            domain_results = []
            for formula_id, report in reports.items():
                if domain in report.domain_performances:
                    perf = report.domain_performances[domain]
                    domain_results.append((
                        formula_id,
                        abs(perf.best_correlation),
                        perf.best_property
                    ))
            
            domain_results.sort(key=lambda x: x[1], reverse=True)
            
            for formula_id, corr, prop in domain_results:
                lines.append(f"  {formula_id}: r={corr:.3f} (via {prop})")
        
        return "\n".join(lines)

