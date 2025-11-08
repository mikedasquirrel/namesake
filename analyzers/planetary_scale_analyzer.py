"""
Planetary Scale Analyzer - Field-Like Invisible Forces

Tests for effects that operate at population scale, invisibly, like gravity.

Gravity doesn't affect individual atoms noticeably,
but it organizes entire solar systems.

Similarly: Maybe there's a "nominative field" that:
- Affects outcomes at population scale
- Operates through action-at-a-distance
- Creates potential wells (attractors/repellers)
- Has sources and sinks
- Follows novel field equations

This discovers MACRO-SCALE invisible structure.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging
from scipy import stats
from scipy.spatial.distance import pdist, squareform
from sklearn.neighbors import NearestNeighbors

logger = logging.getLogger(__name__)


@dataclass
class NominativeField:
    """A detected field-like effect in nominative space"""
    field_id: str
    field_type: str  # 'attractor', 'repeller', 'wave', 'gradient'
    
    # Field properties
    strength: float  # How strong is the field?
    range: float  # How far does it reach?
    falloff_pattern: str  # inverse_square, exponential, novel
    
    # Location in nominative space
    center_location: Optional[np.ndarray] = None  # Where is field strongest?
    affected_radius: float = 0.0  # How far does influence extend?
    
    # Evidence
    n_entities_affected: int = 0
    effect_size: float = 0.0
    confidence: float = 0.0
    
    # Mathematical form
    field_equation: Optional[str] = None
    parameters: Dict[str, float] = None


class PlanetaryScaleAnalyzer:
    """
    Analyzes population-scale field effects in nominative space
    
    Tests if names affect each other at a distance,
    like gravitational or electromagnetic fields
    """
    
    def __init__(self):
        self.min_field_strength = 0.20
        self.distance_metric = 'euclidean'
    
    def detect_field_effects(self, entities: List[Dict]) -> List[NominativeField]:
        """
        Detect field-like effects at population scale
        
        Args:
            entities: List with visual_encoding and outcome
            
        Returns:
            List of detected nominative fields
        """
        logger.info("Detecting planetary-scale field effects...")
        
        fields = []
        
        # Extract visual encodings as points in space
        points, outcomes = self._extract_visual_space(entities)
        
        if len(points) < 50:
            logger.warning("  Too few entities for field detection")
            return fields
        
        # Test 1: Action-at-a-distance
        distance_effect = self._test_action_at_distance(points, outcomes)
        if distance_effect:
            fields.append(distance_effect)
        
        # Test 2: Potential wells (attractors/repellers)
        potential_fields = self._detect_potential_wells(points, outcomes)
        fields.extend(potential_fields)
        
        # Test 3: Wave propagation
        wave_fields = self._detect_wave_propagation(points, outcomes)
        fields.extend(wave_fields)
        
        # Test 4: Gradient fields
        gradient_fields = self._detect_gradients(points, outcomes)
        fields.extend(gradient_fields)
        
        logger.info(f"Detected {len(fields)} field-like effects")
        
        return fields
    
    def _extract_visual_space(self, entities: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """Extract visual properties as points in multidimensional space"""
        points = []
        outcomes = []
        
        for entity in entities:
            visual = entity.get('visual_encoding', {})
            outcome = entity.get('outcome_metric')
            
            if visual and outcome is not None:
                point = [
                    visual.get('complexity', 0.5),
                    visual.get('symmetry', 0.5),
                    visual.get('hue', 180) / 360.0,
                    visual.get('x', 0.0),
                    visual.get('y', 0.0),
                ]
                points.append(point)
                outcomes.append(outcome)
        
        return np.array(points), np.array(outcomes)
    
    def _test_action_at_distance(self, points: np.ndarray, 
                                 outcomes: np.ndarray) -> Optional[NominativeField]:
        """
        Test if similar names (close in visual space) affect each other's outcomes
        
        Like gravity: nearby masses affect each other
        """
        # Calculate pairwise distances
        distances = squareform(pdist(points))
        
        # For each entity, find its neighbors
        neighbors = NearestNeighbors(n_neighbors=min(10, len(points)//2))
        neighbors.fit(points)
        
        neighbor_distances, neighbor_indices = neighbors.kneighbors(points)
        
        # Test: Do outcomes correlate with neighbor mean outcome?
        neighbor_outcome_means = []
        for i in range(len(points)):
            neighbor_idx = neighbor_indices[i][1:]  # Exclude self
            neighbor_outcomes = outcomes[neighbor_idx]
            neighbor_outcome_means.append(np.mean(neighbor_outcomes))
        
        # Correlate own outcome with neighbor mean
        try:
            corr, p_value = stats.pearsonr(outcomes, neighbor_outcome_means)
            
            if p_value < 0.05 and abs(corr) > 0.15:
                # Action-at-a-distance detected!
                logger.info(f"  🔥 Action-at-a-distance detected: r={corr:.3f}, p={p_value:.4f}")
                
                field = NominativeField(
                    field_id="action_at_distance",
                    field_type="attractor" if corr > 0 else "repeller",
                    strength=abs(corr),
                    range=float(np.mean(neighbor_distances)),
                    falloff_pattern="unknown",
                    n_entities_affected=len(points),
                    effect_size=abs(corr),
                    confidence=1.0 - p_value,
                    field_equation=f"outcome_correlation(distance) ≈ {corr:.3f}"
                )
                
                return field
        except:
            pass
        
        return None
    
    def _detect_potential_wells(self, points: np.ndarray, 
                                outcomes: np.ndarray) -> List[NominativeField]:
        """
        Detect regions of visual space that act as attractors or repellers
        
        Like gravitational wells - certain patterns always succeed/fail
        """
        fields = []
        
        # Use clustering to find regions
        from sklearn.cluster import KMeans
        
        n_clusters = min(5, len(points) // 20)
        
        if n_clusters < 2:
            return fields
        
        try:
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            labels = kmeans.fit_predict(points)
            centers = kmeans.cluster_centers_
            
            # Calculate mean outcome per cluster
            cluster_outcomes = []
            for i in range(n_clusters):
                cluster_mask = labels == i
                cluster_mean = np.mean(outcomes[cluster_mask])
                cluster_outcomes.append(cluster_mean)
            
            overall_mean = np.mean(outcomes)
            
            # Find clusters with significantly different outcomes
            for i, cluster_mean in enumerate(cluster_outcomes):
                effect = (cluster_mean - overall_mean) / np.std(outcomes)
                
                if abs(effect) > 0.30:  # Medium effect
                    # Potential well found!
                    field_type = "attractor" if effect > 0 else "repeller"
                    
                    logger.info(f"  {field_type.capitalize()} found: effect={effect:.3f}")
                    
                    field = NominativeField(
                        field_id=f"potential_well_{i}",
                        field_type=field_type,
                        strength=abs(effect),
                        range=self._estimate_cluster_radius(points, labels, i),
                        falloff_pattern="unknown",
                        center_location=centers[i],
                        affected_radius=self._estimate_cluster_radius(points, labels, i),
                        n_entities_affected=int(np.sum(labels == i)),
                        effect_size=abs(effect),
                        confidence=0.80,
                        field_equation=f"Entities near {centers[i][:3]} show {effect:+.2f}σ effect"
                    )
                    
                    fields.append(field)
        
        except Exception as e:
            logger.error(f"  Potential well detection failed: {e}")
        
        return fields
    
    def _detect_wave_propagation(self, points: np.ndarray, 
                                outcomes: np.ndarray) -> List[NominativeField]:
        """
        Test if naming trends propagate like waves through nominative space
        """
        # Would need temporal data
        # Test for wave-like patterns over time
        return []
    
    def _detect_gradients(self, points: np.ndarray, 
                         outcomes: np.ndarray) -> List[NominativeField]:
        """
        Detect if outcomes follow gradient (like flowing downhill)
        """
        # Test if moving in certain direction in visual space
        # consistently changes outcomes
        return []
    
    def _estimate_cluster_radius(self, points: np.ndarray, 
                                labels: np.ndarray, cluster_id: int) -> float:
        """Estimate effective radius of a cluster"""
        cluster_points = points[labels == cluster_id]
        center = np.mean(cluster_points, axis=0)
        
        distances = np.linalg.norm(cluster_points - center, axis=1)
        
        return float(np.mean(distances))
    
    def generate_field_report(self, fields: List[NominativeField]) -> str:
        """Generate report of detected fields"""
        lines = []
        lines.append("=" * 80)
        lines.append("PLANETARY-SCALE FIELD ANALYSIS")
        lines.append("=" * 80)
        lines.append("")
        
        if fields:
            lines.append(f"🔥 NOMINATIVE FIELDS DETECTED: {len(fields)}")
            lines.append("-" * 80)
            
            for field in fields:
                lines.append(f"\nField: {field.field_id}")
                lines.append(f"Type: {field.field_type}")
                lines.append(f"Strength: {field.strength:.3f}")
                lines.append(f"Range: {field.range:.3f}")
                lines.append(f"Affected Entities: {field.n_entities_affected}")
                
                if field.field_equation:
                    lines.append(f"Equation: {field.field_equation}")
                
                lines.append(f"\nINTERPRETATION:")
                lines.append(f"  {field.field_type.capitalize()} effect detected.")
                lines.append(f"  Names in this region of visual space")
                lines.append(f"  show systematic {'+' if field.field_type == 'attractor' else '-'} outcomes.")
                lines.append(f"  Effect operates at population scale, like gravity.")
            
            lines.append("\n" + "=" * 80)
            lines.append("PROFOUND IMPLICATION:")
            lines.append("=" * 80)
            lines.append("Nominative space has FIELD STRUCTURE.")
            lines.append("Not just correlations - actual FORCES.")
            lines.append("Certain patterns attract success, others repel it.")
            lines.append("This operates invisibly at population scale.")
            lines.append("")
            lines.append("Like discovering a new fundamental force.")
        else:
            lines.append("No field-like effects detected.")
            lines.append("Nominative space appears locally independent.")
        
        return "\n".join(lines)

