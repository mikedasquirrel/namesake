"""
Encryption Pattern Detector

Tests if transformation formulas exhibit encryption-like properties:
- Reversibility: Can we decode visual → name features?
- Information preservation: How much name information survives transformation?
- Collision resistance: Do different names produce different visuals?
- Avalanche effect: Do small name changes create large visual changes?
- Key-space analysis: How many distinct visuals are possible?

This reveals: Is the formula a natural encryption system?
"""

import numpy as np
import hashlib
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from collections import defaultdict
import logging
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors

from utils.formula_engine import FormulaEngine, VisualEncoding, FormulaBase

logger = logging.getLogger(__name__)


@dataclass
class ReversibilityTest:
    """Results of reversibility testing"""
    formula_id: str
    
    # Can we decode visual properties back to linguistic features?
    pca_reconstruction_accuracy: float  # 0-1
    nearest_neighbor_accuracy: float  # 0-1
    
    # How much information is preserved?
    information_preservation_score: float  # 0-1
    
    is_reversible: bool  # > 70% accuracy


@dataclass
class CollisionResistanceTest:
    """Results of collision resistance testing"""
    formula_id: str
    
    # Do different names produce different visuals?
    n_names_tested: int
    n_unique_visuals: int
    collision_rate: float  # 0-1 (lower is better)
    
    # Visual distance statistics
    mean_visual_distance: float
    min_visual_distance: float
    
    # Similar names (edit distance 1) should produce distinct visuals
    similar_names_divergence: float  # Average visual distance for edit-distance-1 names
    
    is_collision_resistant: bool  # < 5% collision rate


@dataclass
class AvalancheTest:
    """Results of avalanche effect testing"""
    formula_id: str
    
    # Do small changes in name create large changes in visual?
    n_name_pairs_tested: int
    
    # For single-character changes
    mean_visual_change: float  # 0-1
    avalanche_ratio: float  # visual_change / name_change (higher is better)
    
    # Should be > 0.5 (50%+ of visual properties change)
    is_avalanche_strong: bool


@dataclass
class KeySpaceAnalysis:
    """Analysis of visual encoding key space"""
    formula_id: str
    
    # Dimensionality of visual space
    effective_dimensions: int
    theoretical_key_space: float  # log10 of possible distinct visuals
    
    # Actual distribution
    entropy: float  # Shannon entropy of visual distribution
    uniformity_score: float  # 0-1, how evenly distributed
    
    # Clustering analysis
    n_clusters: int
    cluster_separation: float  # How distinct are clusters


@dataclass
class EncryptionProfile:
    """Complete encryption-like properties profile"""
    formula_id: str
    
    reversibility: ReversibilityTest
    collision_resistance: CollisionResistanceTest
    avalanche: AvalancheTest
    key_space: KeySpaceAnalysis
    
    # Overall score
    encryption_quality_score: float  # 0-1
    
    # Comparison to known algorithms
    similar_to_algorithm: Optional[str] = None
    similarity_explanation: str = ""
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


class EncryptionDetector:
    """
    Tests transformation formulas for encryption-like properties
    """
    
    def __init__(self):
        self.formula_engine = FormulaEngine()
        self.tolerance = 1e-6  # For detecting collisions
    
    def analyze_formula(self, formula_id: str,
                       test_names: List[str],
                       linguistic_features: Dict[str, Dict]) -> EncryptionProfile:
        """
        Complete encryption properties analysis
        
        Args:
            formula_id: Formula to test
            test_names: List of names to test
            linguistic_features: Dict mapping name to linguistic features
            
        Returns:
            EncryptionProfile with all test results
        """
        logger.info(f"Analyzing encryption properties of '{formula_id}'")
        logger.info(f"Testing on {len(test_names)} names")
        
        # Generate visual encodings
        visual_encodings = self._generate_encodings(
            formula_id, test_names, linguistic_features
        )
        
        # Run all tests
        reversibility = self._test_reversibility(
            formula_id, test_names, linguistic_features, visual_encodings
        )
        
        collision_resistance = self._test_collision_resistance(
            formula_id, test_names, visual_encodings
        )
        
        avalanche = self._test_avalanche_effect(
            formula_id, test_names, linguistic_features
        )
        
        key_space = self._analyze_key_space(
            formula_id, visual_encodings
        )
        
        # Calculate overall encryption quality score
        quality_score = self._calculate_encryption_quality(
            reversibility, collision_resistance, avalanche, key_space
        )
        
        # Compare to known encryption algorithms
        similar_algo, explanation = self._compare_to_algorithms(
            reversibility, collision_resistance, avalanche
        )
        
        profile = EncryptionProfile(
            formula_id=formula_id,
            reversibility=reversibility,
            collision_resistance=collision_resistance,
            avalanche=avalanche,
            key_space=key_space,
            encryption_quality_score=quality_score,
            similar_to_algorithm=similar_algo,
            similarity_explanation=explanation
        )
        
        return profile
    
    def _generate_encodings(self, formula_id: str, names: List[str],
                           linguistic_features: Dict[str, Dict]) -> Dict[str, VisualEncoding]:
        """Generate visual encodings for all names"""
        encodings = {}
        
        for name in names:
            features = linguistic_features.get(name, {})
            if not features:
                continue
            
            try:
                encoding = self.formula_engine.transform(name, features, formula_id)
                encodings[name] = encoding
            except Exception as e:
                logger.error(f"Error encoding {name}: {e}")
        
        return encodings
    
    def _test_reversibility(self, formula_id: str, names: List[str],
                           linguistic_features: Dict[str, Dict],
                           visual_encodings: Dict[str, VisualEncoding]) -> ReversibilityTest:
        """Test if we can decode visuals back to linguistic features"""
        logger.info("Testing reversibility...")
        
        # Extract visual feature matrix
        visual_matrix = []
        linguistic_matrix = []
        valid_names = []
        
        for name in names:
            if name not in visual_encodings or name not in linguistic_features:
                continue
            
            visual_encoding = visual_encodings[name]
            ling_features = linguistic_features[name]
            
            # Visual features as vector
            visual_vec = [
                visual_encoding.complexity,
                visual_encoding.symmetry,
                visual_encoding.angular_vs_curved,
                visual_encoding.hue / 360.0,  # Normalize
                visual_encoding.saturation / 100.0,
                visual_encoding.brightness / 100.0,
                visual_encoding.x,
                visual_encoding.y,
                visual_encoding.z,
                visual_encoding.glow_intensity,
                visual_encoding.fractal_dimension - 1.0,  # Normalize to 0-1
                visual_encoding.pattern_density,
            ]
            
            # Linguistic features as vector (sample)
            ling_vec = [
                ling_features.get('syllable_count', 2) / 10.0,
                ling_features.get('character_length', 5) / 20.0,
                ling_features.get('vowel_ratio', 0.4),
                ling_features.get('harshness_score', 0.5),
                ling_features.get('phonetic_complexity', 0.5),
            ]
            
            visual_matrix.append(visual_vec)
            linguistic_matrix.append(ling_vec)
            valid_names.append(name)
        
        if len(visual_matrix) < 10:
            logger.warning("Too few samples for reversibility test")
            return ReversibilityTest(
                formula_id=formula_id,
                pca_reconstruction_accuracy=0.0,
                nearest_neighbor_accuracy=0.0,
                information_preservation_score=0.0,
                is_reversible=False
            )
        
        visual_matrix = np.array(visual_matrix)
        linguistic_matrix = np.array(linguistic_matrix)
        
        # Test 1: PCA reconstruction
        # Can we reconstruct linguistic features from visual features using linear transformation?
        try:
            # Fit PCA to learn mapping
            pca = PCA(n_components=min(5, visual_matrix.shape[1]))
            visual_reduced = pca.fit_transform(visual_matrix)
            
            # Try to reconstruct linguistic features
            from sklearn.linear_model import LinearRegression
            
            reconstruction_errors = []
            for i in range(linguistic_matrix.shape[1]):
                model = LinearRegression()
                model.fit(visual_reduced, linguistic_matrix[:, i])
                predictions = model.predict(visual_reduced)
                error = np.mean(np.abs(predictions - linguistic_matrix[:, i]))
                reconstruction_errors.append(error)
            
            pca_accuracy = 1.0 - np.mean(reconstruction_errors)
            pca_accuracy = max(0.0, pca_accuracy)
            
        except Exception as e:
            logger.error(f"PCA reconstruction error: {e}")
            pca_accuracy = 0.0
        
        # Test 2: Nearest neighbor decoding
        # Can we identify the correct name from visual encoding?
        try:
            nbrs = NearestNeighbors(n_neighbors=1)
            nbrs.fit(visual_matrix)
            
            correct_matches = 0
            for i, visual_vec in enumerate(visual_matrix):
                distances, indices = nbrs.kneighbors([visual_vec])
                if indices[0][0] == i:
                    correct_matches += 1
            
            nn_accuracy = correct_matches / len(visual_matrix)
            
        except Exception as e:
            logger.error(f"Nearest neighbor error: {e}")
            nn_accuracy = 0.0
        
        # Information preservation: How much variance is captured?
        try:
            pca_full = PCA()
            pca_full.fit(visual_matrix)
            explained_variance = np.sum(pca_full.explained_variance_ratio_[:5])
            info_preservation = float(explained_variance)
        except:
            info_preservation = 0.5
        
        is_reversible = pca_accuracy > 0.7 or nn_accuracy > 0.7
        
        return ReversibilityTest(
            formula_id=formula_id,
            pca_reconstruction_accuracy=pca_accuracy,
            nearest_neighbor_accuracy=nn_accuracy,
            information_preservation_score=info_preservation,
            is_reversible=is_reversible
        )
    
    def _test_collision_resistance(self, formula_id: str, names: List[str],
                                   visual_encodings: Dict[str, VisualEncoding]) -> CollisionResistanceTest:
        """Test if different names produce different visuals"""
        logger.info("Testing collision resistance...")
        
        # Convert visuals to hashable tuples
        visual_hashes = {}
        visual_vectors = {}
        
        for name, encoding in visual_encodings.items():
            # Create hash of visual properties (rounded to avoid floating point issues)
            visual_tuple = (
                round(encoding.complexity, 4),
                round(encoding.symmetry, 4),
                round(encoding.angular_vs_curved, 4),
                round(encoding.hue, 2),
                round(encoding.saturation, 2),
                round(encoding.brightness, 2),
                round(encoding.x, 4),
                round(encoding.y, 4),
                round(encoding.z, 4),
            )
            
            visual_hash = hash(visual_tuple)
            visual_hashes[name] = visual_hash
            
            # Also store as vector for distance calculation
            visual_vectors[name] = np.array([
                encoding.complexity,
                encoding.symmetry,
                encoding.angular_vs_curved,
                encoding.hue / 360.0,
                encoding.saturation / 100.0,
                encoding.brightness / 100.0,
                encoding.x,
                encoding.y,
                encoding.z,
            ])
        
        # Count unique visuals
        n_unique = len(set(visual_hashes.values()))
        collision_rate = 1.0 - (n_unique / len(names))
        
        # Calculate visual distances
        distances = []
        for i, name1 in enumerate(names):
            if name1 not in visual_vectors:
                continue
            for name2 in names[i+1:]:
                if name2 not in visual_vectors:
                    continue
                dist = np.linalg.norm(visual_vectors[name1] - visual_vectors[name2])
                distances.append(dist)
        
        mean_distance = float(np.mean(distances)) if distances else 0.0
        min_distance = float(np.min(distances)) if distances else 0.0
        
        # Test similar names (edit distance 1)
        similar_pairs_distances = []
        for i, name1 in enumerate(names):
            if name1 not in visual_vectors:
                continue
            for name2 in names[i+1:]:
                if name2 not in visual_vectors:
                    continue
                # Calculate edit distance
                edit_dist = self._edit_distance(name1, name2)
                if edit_dist == 1:
                    visual_dist = np.linalg.norm(visual_vectors[name1] - visual_vectors[name2])
                    similar_pairs_distances.append(visual_dist)
        
        similar_divergence = float(np.mean(similar_pairs_distances)) if similar_pairs_distances else mean_distance
        
        is_resistant = collision_rate < 0.05
        
        return CollisionResistanceTest(
            formula_id=formula_id,
            n_names_tested=len(names),
            n_unique_visuals=n_unique,
            collision_rate=collision_rate,
            mean_visual_distance=mean_distance,
            min_visual_distance=min_distance,
            similar_names_divergence=similar_divergence,
            is_collision_resistant=is_resistant
        )
    
    def _test_avalanche_effect(self, formula_id: str, names: List[str],
                               linguistic_features: Dict[str, Dict]) -> AvalancheTest:
        """Test if small name changes create large visual changes"""
        logger.info("Testing avalanche effect...")
        
        visual_changes = []
        n_pairs = 0
        
        # Test first 100 names (for speed)
        test_names = names[:100]
        
        for name in test_names:
            if name not in linguistic_features:
                continue
            
            # Create slight variation
            variants = self._create_name_variants(name)
            
            for variant in variants:
                # Generate linguistic features for variant (simplified)
                variant_features = linguistic_features.get(name, {}).copy()
                # Slightly modify features
                for key in ['character_length', 'syllable_count']:
                    if key in variant_features:
                        variant_features[key] = len(variant)
                
                try:
                    original_visual = self.formula_engine.transform(
                        name, linguistic_features[name], formula_id
                    )
                    variant_visual = self.formula_engine.transform(
                        variant, variant_features, formula_id
                    )
                    
                    # Calculate visual change
                    visual_change = self._calculate_visual_difference(
                        original_visual, variant_visual
                    )
                    
                    visual_changes.append(visual_change)
                    n_pairs += 1
                    
                except Exception as e:
                    pass
        
        if not visual_changes:
            return AvalancheTest(
                formula_id=formula_id,
                n_name_pairs_tested=0,
                mean_visual_change=0.0,
                avalanche_ratio=0.0,
                is_avalanche_strong=False
            )
        
        mean_change = float(np.mean(visual_changes))
        
        # Avalanche ratio: visual change relative to name change
        # Single character change should cause ~50% visual property change
        avalanche_ratio = mean_change / 0.1  # Normalized
        
        is_strong = mean_change > 0.5
        
        return AvalancheTest(
            formula_id=formula_id,
            n_name_pairs_tested=n_pairs,
            mean_visual_change=mean_change,
            avalanche_ratio=avalanche_ratio,
            is_avalanche_strong=is_strong
        )
    
    def _analyze_key_space(self, formula_id: str,
                          visual_encodings: Dict[str, VisualEncoding]) -> KeySpaceAnalysis:
        """Analyze the space of possible visual encodings"""
        logger.info("Analyzing key space...")
        
        # Convert to matrix
        visual_matrix = []
        for encoding in visual_encodings.values():
            vec = [
                encoding.complexity,
                encoding.symmetry,
                encoding.angular_vs_curved,
                encoding.hue / 360.0,
                encoding.saturation / 100.0,
                encoding.brightness / 100.0,
                encoding.x,
                encoding.y,
                encoding.z,
                encoding.glow_intensity,
                (encoding.fractal_dimension - 1.0),
                encoding.pattern_density,
            ]
            visual_matrix.append(vec)
        
        visual_matrix = np.array(visual_matrix)
        
        # Effective dimensions (PCA)
        try:
            pca = PCA()
            pca.fit(visual_matrix)
            
            # Count dimensions that explain > 5% variance
            effective_dims = np.sum(pca.explained_variance_ratio_ > 0.05)
            
        except:
            effective_dims = 12
        
        # Theoretical key space (assuming 100 distinct values per dimension)
        theoretical_space = np.log10(100 ** effective_dims)
        
        # Shannon entropy
        try:
            # Discretize each dimension
            n_bins = 10
            discretized = np.floor(visual_matrix * n_bins).astype(int)
            
            # Calculate entropy for each dimension
            entropies = []
            for dim in range(discretized.shape[1]):
                values, counts = np.unique(discretized[:, dim], return_counts=True)
                probs = counts / counts.sum()
                entropy = -np.sum(probs * np.log2(probs + 1e-10))
                entropies.append(entropy)
            
            mean_entropy = float(np.mean(entropies))
            
        except:
            mean_entropy = 3.0  # Default
        
        # Uniformity: How evenly distributed are the encodings?
        try:
            from scipy.stats import chi2_contingency
            
            # Test uniformity in each dimension
            uniformity_scores = []
            for dim in range(visual_matrix.shape[1]):
                hist, _ = np.histogram(visual_matrix[:, dim], bins=10)
                expected = len(visual_matrix) / 10
                chi2 = np.sum((hist - expected) ** 2 / expected)
                # Convert to 0-1 score (lower chi2 = more uniform)
                uniformity = max(0, 1.0 - chi2 / 100)
                uniformity_scores.append(uniformity)
            
            uniformity_score = float(np.mean(uniformity_scores))
            
        except:
            uniformity_score = 0.5
        
        # Clustering
        try:
            from sklearn.cluster import KMeans
            
            n_clusters = min(10, len(visual_encodings) // 10)
            if n_clusters >= 2:
                kmeans = KMeans(n_clusters=n_clusters, random_state=42)
                labels = kmeans.fit_predict(visual_matrix)
                
                # Calculate separation (silhouette score)
                from sklearn.metrics import silhouette_score
                separation = float(silhouette_score(visual_matrix, labels))
            else:
                n_clusters = 1
                separation = 0.0
                
        except:
            n_clusters = 1
            separation = 0.0
        
        return KeySpaceAnalysis(
            formula_id=formula_id,
            effective_dimensions=int(effective_dims),
            theoretical_key_space=theoretical_space,
            entropy=mean_entropy,
            uniformity_score=uniformity_score,
            n_clusters=n_clusters,
            cluster_separation=separation
        )
    
    def _calculate_encryption_quality(self, reversibility: ReversibilityTest,
                                      collision: CollisionResistanceTest,
                                      avalanche: AvalancheTest,
                                      key_space: KeySpaceAnalysis) -> float:
        """Calculate overall encryption quality score"""
        
        # Good encryption should be:
        # - Hard to reverse (low reversibility)
        # - Collision resistant (high uniqueness)
        # - Strong avalanche effect
        # - Large key space
        
        irreversibility_score = 1.0 - reversibility.pca_reconstruction_accuracy
        collision_score = 1.0 - collision.collision_rate
        avalanche_score = min(1.0, avalanche.mean_visual_change)
        key_space_score = min(1.0, key_space.entropy / 4.0)  # Max entropy ~4
        
        quality = (
            irreversibility_score * 0.3 +
            collision_score * 0.3 +
            avalanche_score * 0.2 +
            key_space_score * 0.2
        )
        
        return quality
    
    def _compare_to_algorithms(self, reversibility: ReversibilityTest,
                               collision: CollisionResistanceTest,
                               avalanche: AvalancheTest) -> Tuple[Optional[str], str]:
        """Compare to known encryption/hashing algorithms"""
        
        # Hash function characteristics: irreversible, collision-resistant, strong avalanche
        if (not reversibility.is_reversible and 
            collision.is_collision_resistant and 
            avalanche.is_avalanche_strong):
            return "Cryptographic Hash (e.g., SHA-256)", \
                   "Exhibits strong one-way function properties with good avalanche effect"
        
        # Block cipher: reversible with key, strong avalanche
        if (reversibility.is_reversible and avalanche.is_avalanche_strong):
            return "Block Cipher (e.g., AES)", \
                   "Reversible transformation with strong diffusion properties"
        
        # Stream cipher: simpler transformation
        if reversibility.is_reversible and not avalanche.is_avalanche_strong:
            return "Stream Cipher", \
                   "Reversible but with weaker diffusion"
        
        # Weak hash: collisions present
        if not reversibility.is_reversible and not collision.is_collision_resistant:
            return "Weak Hash Function", \
                   "One-way but susceptible to collisions"
        
        # Simple encoding: reversible, weak avalanche
        return "Simple Encoding", \
               "More like a reversible encoding than encryption"
    
    def _create_name_variants(self, name: str) -> List[str]:
        """Create single-character variants of a name"""
        variants = []
        
        # Change one character
        for i in range(len(name)):
            if name[i].isalpha():
                # Replace with adjacent letter
                char_code = ord(name[i].lower())
                for delta in [-1, 1]:
                    new_code = char_code + delta
                    if ord('a') <= new_code <= ord('z'):
                        variant = name[:i] + chr(new_code) + name[i+1:]
                        variants.append(variant)
        
        return variants[:3]  # Return max 3 variants
    
    def _calculate_visual_difference(self, visual1: VisualEncoding,
                                     visual2: VisualEncoding) -> float:
        """Calculate normalized difference between two visual encodings"""
        
        differences = []
        
        # Numerical properties (0-1 range)
        differences.append(abs(visual1.complexity - visual2.complexity))
        differences.append(abs(visual1.symmetry - visual2.symmetry))
        differences.append(abs(visual1.angular_vs_curved - visual2.angular_vs_curved) / 2.0)
        differences.append(abs(visual1.hue - visual2.hue) / 360.0)
        differences.append(abs(visual1.saturation - visual2.saturation) / 100.0)
        differences.append(abs(visual1.brightness - visual2.brightness) / 100.0)
        differences.append(abs(visual1.x - visual2.x) / 2.0)
        differences.append(abs(visual1.y - visual2.y) / 2.0)
        differences.append(abs(visual1.z - visual2.z))
        differences.append(abs(visual1.glow_intensity - visual2.glow_intensity))
        differences.append(abs(visual1.fractal_dimension - visual2.fractal_dimension))
        differences.append(abs(visual1.pattern_density - visual2.pattern_density))
        
        # Categorical properties
        if visual1.shape_type != visual2.shape_type:
            differences.append(1.0)
        
        if visual1.palette_family != visual2.palette_family:
            differences.append(1.0)
        
        # Average difference
        return float(np.mean(differences))
    
    def _edit_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein edit distance"""
        if len(s1) < len(s2):
            return self._edit_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def export_profile(self, profile: EncryptionProfile, filepath: str):
        """Export encryption profile to file"""
        import json
        with open(filepath, 'w') as f:
            json.dump(profile.to_dict(), f, indent=2)
        
        logger.info(f"Encryption profile exported to {filepath}")
    
    def generate_report(self, profile: EncryptionProfile) -> str:
        """Generate human-readable report"""
        lines = []
        lines.append("=" * 80)
        lines.append(f"ENCRYPTION PROPERTIES ANALYSIS: {profile.formula_id}")
        lines.append("=" * 80)
        lines.append("")
        
        lines.append(f"Overall Encryption Quality: {profile.encryption_quality_score:.3f}")
        lines.append(f"Similar to: {profile.similar_to_algorithm}")
        lines.append(f"Explanation: {profile.similarity_explanation}")
        lines.append("")
        
        lines.append("REVERSIBILITY:")
        lines.append(f"  PCA Reconstruction: {profile.reversibility.pca_reconstruction_accuracy:.3f}")
        lines.append(f"  Nearest Neighbor: {profile.reversibility.nearest_neighbor_accuracy:.3f}")
        lines.append(f"  Information Preservation: {profile.reversibility.information_preservation_score:.3f}")
        lines.append(f"  Is Reversible: {profile.reversibility.is_reversible}")
        lines.append("")
        
        lines.append("COLLISION RESISTANCE:")
        lines.append(f"  Names Tested: {profile.collision_resistance.n_names_tested}")
        lines.append(f"  Unique Visuals: {profile.collision_resistance.n_unique_visuals}")
        lines.append(f"  Collision Rate: {profile.collision_resistance.collision_rate:.3f}")
        lines.append(f"  Is Collision Resistant: {profile.collision_resistance.is_collision_resistant}")
        lines.append("")
        
        lines.append("AVALANCHE EFFECT:")
        lines.append(f"  Pairs Tested: {profile.avalanche.n_name_pairs_tested}")
        lines.append(f"  Mean Visual Change: {profile.avalanche.mean_visual_change:.3f}")
        lines.append(f"  Avalanche Ratio: {profile.avalanche.avalanche_ratio:.3f}")
        lines.append(f"  Is Strong: {profile.avalanche.is_avalanche_strong}")
        lines.append("")
        
        lines.append("KEY SPACE:")
        lines.append(f"  Effective Dimensions: {profile.key_space.effective_dimensions}")
        lines.append(f"  Theoretical Key Space: 10^{profile.key_space.theoretical_key_space:.1f}")
        lines.append(f"  Entropy: {profile.key_space.entropy:.3f}")
        lines.append(f"  Uniformity: {profile.key_space.uniformity_score:.3f}")
        
        return "\n".join(lines)

