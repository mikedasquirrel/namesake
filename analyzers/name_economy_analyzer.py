"""
Name Economy Analyzer - Competitive Dynamics & Relative Positioning

CRITICAL INSIGHT: Names don't exist in isolation. Their value depends on:
1. Scarcity/abundance within sphere (if everyone is short, short loses advantage)
2. Relative differentiation from competitors
3. Cross-sphere spillover (crypto borrows from tech, bands from mythology)
4. Pattern saturation (overuse degrades effectiveness)
5. Brand positioning economy

This is the missing piece: economic interdependence of naming.
"""

import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Optional, Tuple
from collections import Counter
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


class NameEconomyAnalyzer:
    """
    Analyzes competitive dynamics and relative positioning of names.
    
    Key Concept: A name's value is not absolute, but relative to the
    naming economy it operates within.
    """
    
    def __init__(self):
        self.scaler = StandardScaler()
    
    def analyze_name_economy(self, name: str, phonetic_features: Dict,
                             all_names_data: List[Dict],
                             sphere: str = 'generic') -> Dict:
        """
        Complete economic analysis of a name's competitive position.
        
        Args:
            name: Target name to analyze
            phonetic_features: Phonetic analysis of target name
            all_names_data: List of dicts with {'name': str, 'phonetic_features': dict, 'outcome': float}
            sphere: Domain context
            
        Returns:
            Economic positioning metrics
        """
        if len(all_names_data) < 10:
            return self._empty_economy()
        
        # Extract features and outcomes
        names = [d['name'] for d in all_names_data]
        all_features = [d['phonetic_features'] for d in all_names_data]
        outcomes = [d.get('outcome', 50) for d in all_names_data]
        
        # 1. Scarcity Analysis
        scarcity_metrics = self.calculate_scarcity_value(
            phonetic_features, all_features
        )
        
        # 2. Relative Differentiation
        differentiation = self.calculate_differentiation_advantage(
            phonetic_features, all_features, outcomes
        )
        
        # 3. Pattern Saturation
        saturation = self.calculate_pattern_saturation(
            phonetic_features, all_features, sphere
        )
        
        # 4. Competitive Positioning
        positioning = self.calculate_competitive_position(
            phonetic_features, all_features, outcomes
        )
        
        # 5. Cross-Sphere Spillover
        spillover = self.estimate_cross_sphere_influence(
            phonetic_features, sphere
        )
        
        # 6. Brand Economy Score (composite)
        brand_economy_score = self.calculate_brand_economy_score(
            scarcity_metrics, differentiation, saturation, positioning
        )
        
        return {
            'scarcity_metrics': scarcity_metrics,
            'differentiation': differentiation,
            'saturation': saturation,
            'positioning': positioning,
            'cross_sphere_spillover': spillover,
            'brand_economy_score': brand_economy_score,
            'summary': self._generate_summary(
                scarcity_metrics, differentiation, saturation, positioning
            )
        }
    
    def calculate_scarcity_value(self, target_features: Dict,
                                 all_features: List[Dict]) -> Dict:
        """
        Calculate scarcity value: how rare/common is this phonetic profile?
        
        Key Insight: If 80% of names are short, being short is not an advantage.
        Scarcity creates value through differentiation.
        """
        # Define key dimensions for clustering
        dimension_keys = [
            'syllable_count', 'harshness_score', 'memorability_score',
            'character_length', 'plosive_score', 'euphony_score'
        ]
        
        # Extract dimensions
        target_vector = np.array([target_features.get(k, 50) for k in dimension_keys])
        all_vectors = np.array([
            [f.get(k, 50) for k in dimension_keys] for f in all_features
        ])
        
        # Calculate distance to all other names
        distances = np.linalg.norm(all_vectors - target_vector, axis=1)
        
        # Scarcity metrics
        avg_distance = np.mean(distances)
        min_distance = np.min(distances[distances > 0]) if np.sum(distances > 0) > 0 else 0
        
        # Find "neighbors" (similar names)
        threshold = np.percentile(distances, 25)  # Bottom quartile
        n_neighbors = np.sum(distances < threshold)
        
        # Scarcity score: higher distance = more scarce = more valuable
        # But too scarce = weird/unnatural
        optimal_distance = np.percentile(distances, 75)
        scarcity_score = 100 * (1 - abs(avg_distance - optimal_distance) / optimal_distance)
        
        return {
            'avg_distance': round(float(avg_distance), 2),
            'min_distance': round(float(min_distance), 2),
            'n_neighbors': int(n_neighbors),
            'neighbor_density': round(n_neighbors / len(all_features) * 100, 1),
            'scarcity_score': round(float(scarcity_score), 2),
            'interpretation': self._interpret_scarcity(scarcity_score, n_neighbors)
        }
    
    def calculate_differentiation_advantage(self, target_features: Dict,
                                           all_features: List[Dict],
                                           outcomes: List[float]) -> Dict:
        """
        Calculate differentiation advantage: are you different in ways that matter?
        
        Key Insight: Being different is only valuable if the difference correlates
        with success. Random differentiation is noise.
        """
        # Find which features correlate with success
        dimension_keys = list(target_features.keys())
        
        feature_correlations = {}
        for key in dimension_keys:
            if key in ['name', 'category_tags']:
                continue
            
            try:
                values = [f.get(key, 50) for f in all_features]
                if len(set(values)) > 1:  # Has variation
                    corr, p_val = stats.pearsonr(values, outcomes)
                    if p_val < 0.10:  # Weakly significant
                        feature_correlations[key] = corr
            except:
                continue
        
        # Calculate differentiation on SUCCESS-CORRELATED dimensions only
        if not feature_correlations:
            return {
                'strategic_differentiation_score': 50.0,
                'top_differentiators': [],
                'interpretation': 'No clear success patterns in naming economy'
            }
        
        # For each important feature, measure how different target is from average
        differentiations = {}
        for key, corr in feature_correlations.items():
            avg_value = np.mean([f.get(key, 50) for f in all_features])
            target_value = target_features.get(key, 50)
            
            # Difference in direction of success
            if corr > 0:
                # Positive correlation: being higher is good
                diff_score = (target_value - avg_value) / 100 * 100
            else:
                # Negative correlation: being lower is good
                diff_score = (avg_value - target_value) / 100 * 100
            
            differentiations[key] = {
                'correlation': round(corr, 3),
                'avg_market': round(avg_value, 1),
                'target_value': round(target_value, 1),
                'strategic_diff': round(diff_score, 1)
            }
        
        # Overall strategic differentiation score
        strategic_diffs = [d['strategic_diff'] for d in differentiations.values()]
        strategic_score = 50 + np.mean(strategic_diffs) * 0.5  # Center at 50
        
        # Top differentiators
        top_diff = sorted(differentiations.items(), 
                         key=lambda x: abs(x[1]['strategic_diff']),
                         reverse=True)[:5]
        
        return {
            'strategic_differentiation_score': round(float(strategic_score), 2),
            'feature_differentiations': differentiations,
            'top_differentiators': [
                {
                    'feature': k,
                    'strategic_advantage': v['strategic_diff'],
                    'interpretation': self._interpret_diff(k, v)
                }
                for k, v in top_diff
            ],
            'interpretation': self._interpret_strategic_diff(strategic_score)
        }
    
    def calculate_pattern_saturation(self, target_features: Dict,
                                    all_features: List[Dict],
                                    sphere: str) -> Dict:
        """
        Calculate pattern saturation: is this pattern overused?
        
        Key Insight: Optimal patterns lose effectiveness as they saturate.
        First movers win, late adopters face diminishing returns.
        
        Examples:
        - Crypto 2017: "coin" suffix everywhere → lost meaning
        - Bands 1960s: "The ___" peaked → died → revived 2000s
        - MTG: Draconic names 29% → still working but nearing saturation
        """
        # Define pattern signatures
        patterns = self._extract_pattern_signatures(target_features)
        
        # Count pattern usage across all names
        pattern_counts = {}
        for pattern_name, pattern_fn in patterns.items():
            count = sum(1 for f in all_features if pattern_fn(f))
            frequency = count / len(all_features)
            pattern_counts[pattern_name] = {
                'count': count,
                'frequency': round(frequency, 3),
                'target_has': pattern_fn(target_features)
            }
        
        # Saturation thresholds (sphere-specific)
        saturation_thresholds = {
            'crypto': 0.15,      # 15%+ = saturated
            'band': 0.10,        # 10%+ = saturated
            'mtg': 0.20,         # 20%+ = saturated (larger pool)
            'hurricane': 0.30,   # Limited pool, higher tolerance
            'generic': 0.15
        }
        
        threshold = saturation_thresholds.get(sphere, 0.15)
        
        # Calculate saturation penalties
        saturated_patterns = []
        total_saturation_penalty = 0.0
        
        for pattern_name, data in pattern_counts.items():
            if data['target_has'] and data['frequency'] > threshold:
                # Saturation penalty formula
                excess = data['frequency'] - threshold
                penalty = (excess / threshold) * 0.5  # Up to 50% penalty at 2× threshold
                total_saturation_penalty += penalty
                
                saturated_patterns.append({
                    'pattern': pattern_name,
                    'frequency': data['frequency'],
                    'threshold': threshold,
                    'saturation_ratio': round(data['frequency'] / threshold, 2),
                    'penalty': round(penalty, 3)
                })
        
        # Overall saturation score (inverse of penalty)
        saturation_score = max(0, 100 - total_saturation_penalty * 100)
        
        return {
            'saturation_score': round(saturation_score, 2),
            'saturated_patterns': saturated_patterns,
            'pattern_counts': pattern_counts,
            'interpretation': self._interpret_saturation(saturation_score, saturated_patterns)
        }
    
    def calculate_competitive_position(self, target_features: Dict,
                                      all_features: List[Dict],
                                      outcomes: List[float]) -> Dict:
        """
        Calculate competitive position: where does this name rank?
        
        Uses clustering to identify strategic positioning groups.
        """
        if len(all_features) < 20:
            return {'position': 'unknown', 'cluster': -1}
        
        # Standardize features for clustering
        dimension_keys = [
            'syllable_count', 'harshness_score', 'memorability_score',
            'character_length', 'euphony_score'
        ]
        
        X = np.array([[f.get(k, 50) for k in dimension_keys] for f in all_features])
        X_scaled = self.scaler.fit_transform(X)
        
        # Optimal number of clusters (3-5)
        n_clusters = min(5, max(3, len(all_features) // 30))
        
        try:
            # Cluster names into strategic groups
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(X_scaled)
            
            # Assign target to cluster
            target_vector = np.array([[target_features.get(k, 50) for k in dimension_keys]])
            target_scaled = self.scaler.transform(target_vector)
            target_cluster = kmeans.predict(target_scaled)[0]
            
            # Analyze cluster performance
            cluster_outcomes = {}
            for c in range(n_clusters):
                cluster_mask = clusters == c
                cluster_outcomes[c] = {
                    'mean_outcome': np.mean([outcomes[i] for i, m in enumerate(cluster_mask) if m]),
                    'count': np.sum(cluster_mask),
                    'std_outcome': np.std([outcomes[i] for i, m in enumerate(cluster_mask) if m])
                }
            
            # Rank clusters by performance
            cluster_ranks = sorted(cluster_outcomes.items(),
                                 key=lambda x: x[1]['mean_outcome'],
                                 reverse=True)
            
            target_rank = [i for i, (c, _) in enumerate(cluster_ranks) if c == target_cluster][0] + 1
            
            return {
                'cluster_id': int(target_cluster),
                'cluster_rank': f"{target_rank}/{n_clusters}",
                'cluster_performance': round(cluster_outcomes[target_cluster]['mean_outcome'], 2),
                'market_avg_performance': round(np.mean(outcomes), 2),
                'competitive_advantage': round(
                    cluster_outcomes[target_cluster]['mean_outcome'] - np.mean(outcomes), 2
                ),
                'cluster_size': int(cluster_outcomes[target_cluster]['count']),
                'market_share': round(cluster_outcomes[target_cluster]['count'] / len(all_features) * 100, 1),
                'interpretation': self._interpret_position(
                    target_rank, n_clusters,
                    cluster_outcomes[target_cluster]['mean_outcome'],
                    np.mean(outcomes)
                )
            }
        
        except Exception as e:
            logger.error(f"Clustering failed: {e}")
            return {'position': 'error', 'cluster': -1}
    
    def estimate_cross_sphere_influence(self, target_features: Dict,
                                       sphere: str) -> Dict:
        """
        Estimate cross-sphere spillover effects.
        
        Key Insight: Naming conventions travel across domains.
        - Crypto borrowed from tech (Bitcoin, Ethereum)
        - Bands borrow from mythology (Led Zeppelin, Megadeth)
        - MTG creates fantasy conventions others copy
        """
        spillover_patterns = {
            'tech_influence': {
                'patterns': ['bit', 'byte', 'chain', 'link', 'protocol', 'smart'],
                'source_spheres': ['tech', 'crypto'],
                'target_spheres': ['all']
            },
            'mythological_influence': {
                'patterns': ['thor', 'zeus', 'titan', 'dragon', 'phoenix'],
                'source_spheres': ['mythology', 'mtg'],
                'target_spheres': ['band', 'crypto', 'ship']
            },
            'geographical_influence': {
                'patterns': ['places', 'cities', 'regions'],
                'source_spheres': ['geography'],
                'target_spheres': ['hurricane', 'ship', 'earthquake']
            },
            'animal_meme_influence': {
                'patterns': ['dog', 'cat', 'shiba', 'inu', 'pepe'],
                'source_spheres': ['internet_culture'],
                'target_spheres': ['crypto']
            }
        }
        
        # Detect which patterns target name uses
        name_lower = target_features.get('name', '').lower() if 'name' in target_features else ''
        
        detected_influences = []
        for influence_type, data in spillover_patterns.items():
            for pattern in data['patterns']:
                if pattern in name_lower:
                    detected_influences.append({
                        'type': influence_type,
                        'pattern': pattern,
                        'source_spheres': data['source_spheres'],
                        'cross_domain_strength': 'high' if sphere in data['target_spheres'] or 'all' in data['target_spheres'] else 'moderate'
                    })
        
        # Spillover score
        spillover_score = len(detected_influences) * 20 if detected_influences else 0
        
        return {
            'spillover_score': min(100, spillover_score),
            'detected_influences': detected_influences,
            'interpretation': self._interpret_spillover(detected_influences, sphere)
        }
    
    def calculate_brand_economy_score(self, scarcity: Dict, differentiation: Dict,
                                     saturation: Dict, positioning: Dict) -> float:
        """
        Calculate composite brand economy score.
        
        Formula: weighted combination of economic factors
        """
        weights = {
            'scarcity': 0.25,
            'strategic_diff': 0.35,
            'saturation': 0.30,
            'position': 0.10
        }
        
        components = {
            'scarcity': scarcity.get('scarcity_score', 50),
            'strategic_diff': differentiation.get('strategic_differentiation_score', 50),
            'saturation': saturation.get('saturation_score', 50),
            'position': positioning.get('competitive_advantage', 0) + 50  # Center at 50
        }
        
        score = sum(weights[k] * components[k] for k in weights.keys())
        
        return round(score, 2)
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _extract_pattern_signatures(self, features: Dict) -> Dict:
        """Extract pattern signatures for saturation detection."""
        return {
            'monosyllabic': lambda f: f.get('syllable_count', 2) == 1,
            'short_name': lambda f: f.get('character_length', 10) <= 5,
            'very_memorable': lambda f: f.get('memorability_score', 50) > 75,
            'harsh': lambda f: f.get('harshness_score', 50) > 70,
            'smooth': lambda f: f.get('smoothness_score', 50) > 70,
            'high_euphony': lambda f: f.get('euphony_score', 50) > 75,
            'has_numbers': lambda f: f.get('has_numbers', False),
        }
    
    def _interpret_scarcity(self, score: float, n_neighbors: int) -> str:
        """Interpret scarcity score."""
        if score > 75:
            return f"Highly distinctive phonetic profile ({n_neighbors} similar names) - strong differentiation"
        elif score > 50:
            return f"Moderately unique ({n_neighbors} similar names) - good positioning"
        else:
            return f"Common phonetic profile ({n_neighbors} similar names) - crowded space"
    
    def _interpret_diff(self, feature: str, data: Dict) -> str:
        """Interpret single feature differentiation."""
        adv = data['strategic_diff']
        if abs(adv) < 5:
            return "Similar to market average"
        elif adv > 0:
            return f"Above market average (advantage: +{abs(adv):.1f}%)"
        else:
            return f"Below market average (disadvantage: {adv:.1f}%)"
    
    def _interpret_strategic_diff(self, score: float) -> str:
        """Interpret overall strategic differentiation."""
        if score > 70:
            return "Strongly differentiated on success-correlated dimensions"
        elif score > 55:
            return "Moderately differentiated in strategically valuable ways"
        elif score > 45:
            return "Neutral positioning - similar to market average"
        else:
            return "Differentiated in wrong directions - disadvantaged vs market"
    
    def _interpret_saturation(self, score: float, saturated: List[Dict]) -> str:
        """Interpret saturation analysis."""
        if not saturated:
            return "No saturated patterns detected - fresh positioning"
        elif score > 70:
            return f"Mild saturation ({len(saturated)} patterns) - still effective"
        elif score > 50:
            return f"Moderate saturation ({len(saturated)} patterns) - diminishing returns"
        else:
            return f"High saturation ({len(saturated)} patterns) - pattern fatigue"
    
    def _interpret_position(self, rank: int, total: int, cluster_perf: float,
                           market_avg: float) -> str:
        """Interpret competitive position."""
        if rank == 1:
            adv = cluster_perf - market_avg
            return f"Top-performing cluster (rank 1/{total}) with +{adv:.1f} advantage"
        elif rank <= total // 2:
            return f"Above-average cluster (rank {rank}/{total})"
        else:
            return f"Below-average cluster (rank {rank}/{total})"
    
    def _interpret_spillover(self, influences: List[Dict], sphere: str) -> str:
        """Interpret cross-sphere spillover."""
        if not influences:
            return "No detected cross-sphere influences - domain-native name"
        else:
            types = [i['type'] for i in influences]
            return f"Cross-sphere influences detected: {', '.join(types)}"
    
    def _generate_summary(self, scarcity: Dict, diff: Dict, 
                         saturation: Dict, position: Dict) -> str:
        """Generate natural language summary."""
        parts = []
        
        # Scarcity
        if scarcity['scarcity_score'] > 70:
            parts.append("distinctive positioning")
        elif scarcity['scarcity_score'] < 40:
            parts.append("crowded segment")
        
        # Differentiation
        if diff['strategic_differentiation_score'] > 65:
            parts.append("strategically differentiated")
        elif diff['strategic_differentiation_score'] < 45:
            parts.append("strategically disadvantaged")
        
        # Saturation
        if saturation['saturation_score'] < 60:
            parts.append("facing pattern saturation")
        
        # Position
        if 'competitive_advantage' in position and position['competitive_advantage'] > 5:
            parts.append("above-market performance cluster")
        
        if not parts:
            return "Neutral market positioning"
        
        return "Name has: " + ", ".join(parts)
    
    def _empty_economy(self) -> Dict:
        """Return empty economy analysis."""
        return {
            'scarcity_metrics': {'scarcity_score': 50, 'interpretation': 'Insufficient data'},
            'differentiation': {'strategic_differentiation_score': 50},
            'saturation': {'saturation_score': 50, 'saturated_patterns': []},
            'positioning': {'position': 'unknown'},
            'cross_sphere_spillover': {'spillover_score': 0, 'detected_influences': []},
            'brand_economy_score': 50.0,
            'summary': 'Insufficient market data for economic analysis'
        }


# Convenience function
def analyze_name_in_economy(name: str, phonetic_features: Dict,
                            all_names_data: List[Dict],
                            sphere: str = 'generic') -> Dict:
    """Quick economic analysis."""
    analyzer = NameEconomyAnalyzer()
    return analyzer.analyze_name_economy(name, phonetic_features, all_names_data, sphere)

