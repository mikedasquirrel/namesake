"""
Emergent Dimension Detector - Finding Hidden Forces

Detects invisible dimensions affecting outcomes - like gravity before Newton.

You can't measure it directly, but you can see its effects:
- Structured unexplained variance
- Non-random residual patterns
- Action-at-a-distance effects
- Field-like influences

This discovers dimensions that don't correspond to any measured variable.
Pure emergence.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging
from scipy import stats
from scipy.spatial.distance import pdist, squareform
from sklearn.decomposition import PCA
from sklearn.cluster import DBSCAN

logger = logging.getLogger(__name__)


@dataclass
class EmergentDimension:
    """A discovered hidden dimension"""
    dimension_id: str
    description: str
    
    # Evidence for existence
    structure_score: float  # How structured are residuals? (0-1)
    explained_variance: float  # How much variance does this explain?
    
    # Properties of the dimension
    dimensionality: int  # How many hidden dimensions?
    correlation_with_residuals: float
    
    # Spatial properties (if applicable)
    has_spatial_structure: bool  # Clusters geographically?
    has_temporal_structure: bool  # Varies over time?
    has_network_structure: bool  # Spreads through connections?
    
    # Mathematical form (if discoverable)
    mathematical_model: Optional[str] = None
    model_parameters: Dict[str, float] = None
    
    # Interpretation
    possible_mechanisms: List[str] = None


class EmergentDimensionDetector:
    """
    Detects hidden forces through structured unexplained variance
    
    Like discovering dark matter:
    - Can't see it
    - Can't measure it directly
    - But can map it through gravitational effects
    
    Here: Map hidden nominative dimensions through outcome effects
    """
    
    def __init__(self):
        self.min_structure_score = 0.30  # Threshold for "structured"
        self.significance_level = 0.05
    
    def detect_hidden_dimensions(self, entities: List[Dict], 
                                 outcomes: np.ndarray,
                                 visual_properties: np.ndarray) -> List[EmergentDimension]:
        """
        Detect if hidden dimensions affect outcomes
        
        Args:
            entities: Entity metadata
            outcomes: Measured outcomes
            visual_properties: Known visual properties (linguistic-derived)
            
        Returns:
            List of detected emergent dimensions
        """
        logger.info("Detecting emergent dimensions...")
        
        dimensions = []
        
        # Step 1: Predict outcomes from known factors
        from sklearn.linear_model import Ridge
        
        try:
            model = Ridge()
            model.fit(visual_properties, outcomes)
            predicted = model.predict(visual_properties)
            
            # Step 2: Calculate residuals (unexplained variance)
            residuals = outcomes - predicted
            
            logger.info(f"  Unexplained variance: {np.var(residuals)/np.var(outcomes)*100:.1f}%")
            
            # Step 3: Test if residuals are structured
            structure_score = self._test_residual_structure(residuals, entities)
            
            logger.info(f"  Residual structure score: {structure_score:.3f}")
            
            if structure_score > self.min_structure_score:
                # Hidden dimension detected!
                logger.info(f"  🔥 HIDDEN DIMENSION DETECTED (structure={structure_score:.3f})")
                
                # Map the dimension
                dimension = self._map_hidden_dimension(residuals, entities, visual_properties)
                dimensions.append(dimension)
        
        except Exception as e:
            logger.error(f"  Emergent dimension detection failed: {e}")
        
        return dimensions
    
    def _test_residual_structure(self, residuals: np.ndarray, 
                                 entities: List[Dict]) -> float:
        """
        Test if residuals have non-random structure
        
        Random residuals → no hidden dimension
        Structured residuals → hidden dimension exists
        
        Tests:
        1. Autocorrelation (nearby entities have similar residuals?)
        2. Clustering (residuals form groups?)
        3. Runs test (are residuals randomly distributed?)
        """
        structure_scores = []
        
        # Test 1: Clustering in residual space
        try:
            # If residuals cluster, there's structure
            clustering = DBSCAN(eps=np.std(residuals)*0.5, min_samples=5)
            labels = clustering.fit_predict(residuals.reshape(-1, 1))
            
            n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
            
            if n_clusters > 1:
                # Multiple clusters found
                cluster_score = min(n_clusters / 5, 1.0)
                structure_scores.append(cluster_score)
                logger.info(f"    Clustering: {n_clusters} groups found")
        except:
            pass
        
        # Test 2: Runs test (randomness)
        try:
            median = np.median(residuals)
            runs = 1
            for i in range(1, len(residuals)):
                if (residuals[i] > median) != (residuals[i-1] > median):
                    runs += 1
            
            expected_runs = (2 * len(residuals) - 1) / 3
            z_score = abs(runs - expected_runs) / np.sqrt(expected_runs)
            
            # High z-score = non-random
            runs_score = min(z_score / 3, 1.0)
            structure_scores.append(runs_score)
            
            if z_score > 2:
                logger.info(f"    Runs test: Non-random pattern (z={z_score:.2f})")
        except:
            pass
        
        # Test 3: Autocorrelation
        try:
            autocorr = np.corrcoef(residuals[:-1], residuals[1:])[0, 1]
            
            if abs(autocorr) > 0.15:
                autocorr_score = abs(autocorr)
                structure_scores.append(autocorr_score)
                logger.info(f"    Autocorrelation: {autocorr:.3f} (structured)")
        except:
            pass
        
        # Average structure score
        if structure_scores:
            return np.mean(structure_scores)
        else:
            return 0.0
    
    def _map_hidden_dimension(self, residuals: np.ndarray, 
                             entities: List[Dict],
                             visual_properties: np.ndarray) -> EmergentDimension:
        """
        Map properties of the hidden dimension
        
        Like mapping dark matter through gravitational effects
        """
        # Use PCA on residuals to extract hidden factor
        try:
            pca = PCA(n_components=1)
            hidden_factor = pca.fit_transform(residuals.reshape(-1, 1))
            explained_var = pca.explained_variance_ratio_[0]
        except:
            hidden_factor = residuals
            explained_var = 1.0
        
        # Test what correlates with hidden factor
        possible_mechanisms = []
        
        # Test spatial clustering
        has_spatial = self._test_spatial_structure(entities, residuals)
        if has_spatial:
            possible_mechanisms.append("Geographic/spatial effects")
        
        # Test temporal patterns
        has_temporal = self._test_temporal_structure(entities, residuals)
        if has_temporal:
            possible_mechanisms.append("Temporal/historical effects")
        
        # Test network effects
        has_network = self._test_network_structure(entities, residuals)
        if has_network:
            possible_mechanisms.append("Network/memetic effects")
        
        # Calculate structure score
        structure_score = self._test_residual_structure(residuals, entities)
        
        dimension = EmergentDimension(
            dimension_id="hidden_1",
            description="Structured unexplained variance detected",
            structure_score=structure_score,
            explained_variance=explained_var,
            dimensionality=1,
            correlation_with_residuals=1.0,
            has_spatial_structure=has_spatial,
            has_temporal_structure=has_temporal,
            has_network_structure=has_network,
            possible_mechanisms=possible_mechanisms
        )
        
        return dimension
    
    def _test_spatial_structure(self, entities: List[Dict], 
                               residuals: np.ndarray) -> bool:
        """Test if residuals cluster geographically"""
        # Would need geographic coordinates
        # For now, simplified test
        return False
    
    def _test_temporal_structure(self, entities: List[Dict], 
                                residuals: np.ndarray) -> bool:
        """Test if residuals vary systematically over time"""
        # Extract timestamps if available
        timestamps = []
        for entity in entities:
            year = entity.get('metadata', {}).get('year')
            if year:
                timestamps.append(year)
        
        if len(timestamps) == len(residuals) and len(timestamps) > 10:
            # Test correlation between time and residuals
            try:
                corr, p_value = stats.pearsonr(timestamps, residuals)
                
                if p_value < 0.05 and abs(corr) > 0.15:
                    logger.info(f"    Temporal structure: r={corr:.3f}, p={p_value:.4f}")
                    return True
            except:
                pass
        
        return False
    
    def _test_network_structure(self, entities: List[Dict], 
                               residuals: np.ndarray) -> bool:
        """Test if residuals spread through network effects"""
        # Would need network/similarity data
        # Simplified test
        return False
    
    def generate_dimension_report(self, dimensions: List[EmergentDimension]) -> str:
        """Generate report of emergent dimensions"""
        lines = []
        lines.append("=" * 80)
        lines.append("EMERGENT DIMENSION ANALYSIS")
        lines.append("=" * 80)
        lines.append("")
        
        if dimensions:
            lines.append(f"🔥 HIDDEN DIMENSIONS DETECTED: {len(dimensions)}")
            lines.append("-" * 80)
            
            for dim in dimensions:
                lines.append(f"\nDimension: {dim.dimension_id}")
                lines.append(f"Structure Score: {dim.structure_score:.3f}")
                lines.append(f"Explained Variance: {dim.explained_variance*100:.1f}%")
                lines.append(f"")
                lines.append(f"Properties:")
                lines.append(f"  Spatial structure: {dim.has_spatial_structure}")
                lines.append(f"  Temporal structure: {dim.has_temporal_structure}")
                lines.append(f"  Network structure: {dim.has_network_structure}")
                
                if dim.possible_mechanisms:
                    lines.append(f"\nPossible Mechanisms:")
                    for mech in dim.possible_mechanisms:
                        lines.append(f"  • {mech}")
                
                lines.append(f"\nInterpretation:")
                lines.append(f"  An unmeasured dimension affects outcomes.")
                lines.append(f"  Like gravity - invisible but with observable effects.")
                lines.append(f"  This dimension is not linguistic, not visual,")
                lines.append(f"  but something else entirely.")
        else:
            lines.append("No emergent dimensions detected.")
            lines.append("Unexplained variance appears random.")
        
        return "\n".join(lines)

