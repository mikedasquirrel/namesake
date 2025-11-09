"""
Spatial Analysis Module
========================

Geographic spatial analysis for religious text adoption patterns.
Uses Moran's I, spatial autocorrelation, and geographically weighted regression.
"""

import logging
import numpy as np
from typing import Dict, List, Tuple
from scipy.spatial.distance import cdist

logger = logging.getLogger(__name__)


class SpatialAnalyzer:
    """Analyze spatial patterns in name and religious text adoption."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("SpatialAnalyzer initialized")
    
    def morans_i(self, values: np.ndarray, coordinates: np.ndarray, 
                threshold_distance: float = None) -> Dict:
        """
        Calculate Moran's I for spatial autocorrelation.
        
        Args:
            values: Values at each location
            coordinates: (lat, lon) coordinates for each location
            threshold_distance: Distance threshold for neighbors (km)
        
        Returns:
            Moran's I statistic and significance
        """
        n = len(values)
        
        # Calculate spatial weights (inverse distance)
        distances = cdist(coordinates, coordinates, metric='euclidean')
        
        if threshold_distance:
            weights = (distances < threshold_distance).astype(float)
            np.fill_diagonal(weights, 0)  # No self-neighbors
        else:
            # Inverse distance weighting
            weights = 1 / (distances + 0.1)  # +0.1 to avoid division by zero
            np.fill_diagonal(weights, 0)
        
        # Normalize weights
        row_sums = weights.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1  # Avoid division by zero
        W = weights / row_sums
        
        # Calculate Moran's I
        mean_val = np.mean(values)
        deviations = values - mean_val
        
        numerator = np.sum(W * np.outer(deviations, deviations))
        denominator = np.sum(deviations ** 2)
        
        if denominator == 0:
            return {'error': 'No variance in values'}
        
        I = (n / np.sum(weights)) * (numerator / denominator)
        
        # Expected value and variance (under null hypothesis of no spatial correlation)
        E_I = -1 / (n - 1)
        
        # Simplified variance calculation
        S1 = 0.5 * np.sum((W + W.T) ** 2)
        S2 = np.sum((W.sum(axis=0) + W.sum(axis=1)) ** 2)
        S3 = (np.sum(deviations ** 4) / n) / ((np.sum(deviations ** 2) / n) ** 2)
        
        var_I = ((n * S1 - n * S2 + 3 * np.sum(weights) ** 2) / 
                (np.sum(weights) ** 2 * (n ** 2 - 1)))
        
        # Z-score
        z_score = (I - E_I) / np.sqrt(var_I) if var_I > 0 else 0
        
        # P-value (two-tailed)
        from scipy import stats
        p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))
        
        return {
            'morans_i': float(I),
            'expected_i': float(E_I),
            'z_score': float(z_score),
            'p_value': float(p_value),
            'significant': p_value < 0.05,
            'interpretation': self._interpret_morans_i(I, p_value),
            'pattern': 'clustered' if I > 0 else 'dispersed' if I < 0 else 'random'
        }
    
    def hot_spot_analysis(self, values: np.ndarray, coordinates: np.ndarray) -> Dict:
        """
        Identify hot spots and cold spots (Getis-Ord Gi*).
        
        Args:
            values: Values at each location
            coordinates: (lat, lon) coordinates
        
        Returns:
            Hot spot statistics for each location
        """
        n = len(values)
        
        # Calculate distances
        distances = cdist(coordinates, coordinates, metric='euclidean')
        
        # Use inverse distance weighting
        weights = 1 / (distances + 0.1)
        np.fill_diagonal(weights, 0)
        
        # Calculate Gi* for each location
        gi_stars = []
        mean_val = np.mean(values)
        std_val = np.std(values)
        
        for i in range(n):
            w_i = weights[i]
            w_sum = np.sum(w_i)
            
            if w_sum == 0:
                gi_stars.append(0)
                continue
            
            # Gi* statistic
            numerator = np.sum(w_i * values) - mean_val * w_sum
            denominator = std_val * np.sqrt((n * np.sum(w_i ** 2) - w_sum ** 2) / (n - 1))
            
            gi_star = numerator / denominator if denominator > 0 else 0
            gi_stars.append(gi_star)
        
        gi_stars = np.array(gi_stars)
        
        # Classify hot/cold spots
        hot_spots = []
        cold_spots = []
        
        for i, gi in enumerate(gi_stars):
            if gi > 1.96:  # 95% confidence
                hot_spots.append({'index': i, 'gi_star': float(gi), 'value': float(values[i])})
            elif gi < -1.96:
                cold_spots.append({'index': i, 'gi_star': float(gi), 'value': float(values[i])})
        
        return {
            'method': 'Getis-Ord Gi*',
            'hot_spots': hot_spots,
            'cold_spots': cold_spots,
            'n_hot_spots': len(hot_spots),
            'n_cold_spots': len(cold_spots),
            'interpretation': f"Found {len(hot_spots)} hot spots and {len(cold_spots)} cold spots at 95% confidence"
        }
    
    def _interpret_morans_i(self, I: float, p_value: float) -> str:
        """Interpret Moran's I results."""
        if p_value >= 0.05:
            return f"No significant spatial autocorrelation (I={I:.3f}, p={p_value:.3f})"
        
        if I > 0:
            strength = "strong" if I > 0.5 else "moderate" if I > 0.3 else "weak"
            return f"Significant {strength} positive spatial clustering (I={I:.3f}, p={p_value:.4f})"
        else:
            strength = "strong" if I < -0.5 else "moderate" if I < -0.3 else "weak"
            return f"Significant {strength} spatial dispersion (I={I:.3f}, p={p_value:.4f})"
    
    def _simple_survival_estimate(self, data: List[Dict]) -> Dict:
        """Simple survival estimate without lifelines."""
        durations = [d['duration'] for d in data]
        events = [d.get('event', 1) for d in data]
        
        median_survival = float(np.median([d for d, e in zip(durations, events) if e == 1]))
        
        return {
            'method': 'Simple estimate',
            'median_survival': median_survival,
            'note': 'Install lifelines for full survival analysis'
        }


# Singleton
spatial_analyzer = SpatialAnalyzer()

