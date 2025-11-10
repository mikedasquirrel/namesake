"""
Semantic Narrative Transformer for Crypto Domain

Uses dimensionality reduction and clustering to reveal latent semantic
categories in cryptocurrency naming.

Features extracted:
- Semantic embeddings (LSA dimensions)
- Cluster membership (one-hot)
- Cluster distances
- Semantic coherence metrics
- Topic structure

Hypothesis: Semantic clustering reveals narrative categories (DeFi, memecoins,
enterprise blockchain) that predict market behavior and survival.

Author: Narrative Integration System
Date: November 2025
"""

import numpy as np
from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from .base_transformer import TextNarrativeTransformer


class SemanticNarrativeTransformer(TextNarrativeTransformer):
    """Extract semantic structure through LSA and clustering."""
    
    def __init__(self, n_components: int = 50, n_clusters: int = 10,
                 max_features: int = 5000):
        """
        Initialize semantic analyzer.
        
        Args:
            n_components: Number of LSA components (semantic dimensions)
            n_clusters: Number of clusters for categorization
            max_features: Max features for TF-IDF
        """
        super().__init__(
            narrative_id="semantic_narrative",
            description="Reveals latent semantic categories through dimensionality reduction and clustering"
        )
        self.n_components = n_components
        self.n_clusters = n_clusters
        self.max_features = max_features
        
        self.vectorizer = None
        self.lsa = None
        self.kmeans = None
        self.cluster_centers = None
    
    def fit(self, X, y=None):
        """
        Learn semantic structure from training data.
        
        Args:
            X: List of narrative descriptions
            y: Labels (optional)
        
        Returns:
            self
        """
        self._validate_input(X)
        
        # Step 1: TF-IDF vectorization
        self.vectorizer = TfidfVectorizer(
            max_features=self.max_features,
            ngram_range=(1, 2),
            stop_words='english',
            min_df=2
        )
        tfidf_matrix = self.vectorizer.fit_transform(X)
        
        # Step 2: LSA (dimensionality reduction)
        self.lsa = TruncatedSVD(n_components=self.n_components, random_state=42)
        lsa_embeddings = self.lsa.fit_transform(tfidf_matrix)
        
        # Step 3: K-Means clustering
        self.kmeans = KMeans(n_clusters=self.n_clusters, random_state=42, n_init=10)
        cluster_labels = self.kmeans.fit_predict(lsa_embeddings)
        self.cluster_centers = self.kmeans.cluster_centers_
        
        # Calculate clustering quality
        if len(X) > self.n_clusters:
            silhouette = silhouette_score(lsa_embeddings, cluster_labels)
        else:
            silhouette = 0.0
        
        # Analyze clusters
        cluster_sizes = np.bincount(cluster_labels, minlength=self.n_clusters)
        
        # Store metadata
        self.metadata['explained_variance'] = np.sum(self.lsa.explained_variance_ratio_)
        self.metadata['silhouette_score'] = float(silhouette)
        self.metadata['cluster_sizes'] = cluster_sizes.tolist()
        self.metadata['n_features_output'] = self._calculate_n_features()
        self.metadata['total_docs'] = len(X)
        self.metadata['feature_names'] = self._generate_feature_names()
        
        self.is_fitted_ = True
        return self
    
    def transform(self, X):
        """
        Transform texts to semantic features.
        
        Args:
            X: List of narrative descriptions
        
        Returns:
            numpy.ndarray: Feature matrix
        """
        self._validate_fitted()
        self._validate_input(X)
        
        # Transform through pipeline
        tfidf_matrix = self.vectorizer.transform(X)
        lsa_embeddings = self.lsa.transform(tfidf_matrix)
        cluster_labels = self.kmeans.predict(lsa_embeddings)
        
        features = []
        for i, embedding in enumerate(lsa_embeddings):
            doc_features = self._extract_document_features(
                embedding, cluster_labels[i], lsa_embeddings
            )
            features.append(doc_features)
        
        return np.array(features, dtype=np.float32)
    
    def _extract_document_features(self, embedding: np.ndarray, 
                                   cluster_label: int,
                                   all_embeddings: np.ndarray) -> List[float]:
        """Extract semantic features from document."""
        doc_features = []
        
        # 1. LSA embedding (semantic dimensions) - use top 20 components
        doc_features.extend(embedding[:20].tolist())
        
        # 2. Cluster membership (one-hot)
        cluster_onehot = np.zeros(self.n_clusters)
        cluster_onehot[cluster_label] = 1.0
        doc_features.extend(cluster_onehot.tolist())
        
        # 3. Distance to assigned cluster center
        cluster_center = self.cluster_centers[cluster_label]
        distance_to_center = np.linalg.norm(embedding - cluster_center)
        doc_features.append(distance_to_center)
        
        # 4. Distance to nearest other cluster
        other_cluster_distances = []
        for i, center in enumerate(self.cluster_centers):
            if i != cluster_label:
                dist = np.linalg.norm(embedding - center)
                other_cluster_distances.append(dist)
        min_other_distance = np.min(other_cluster_distances) if other_cluster_distances else 0
        doc_features.append(min_other_distance)
        
        # 5. Cluster separation (how far from nearest other cluster)
        if min_other_distance > 0:
            separation_ratio = min_other_distance / (distance_to_center + 1e-6)
        else:
            separation_ratio = 0
        doc_features.append(separation_ratio)
        
        # 6. Semantic coherence (within-cluster similarity)
        # Distance to centroid normalized
        max_distance_in_cluster = np.max([
            np.linalg.norm(emb - cluster_center)
            for emb in all_embeddings[self.kmeans.labels_ == cluster_label]
        ]) if np.sum(self.kmeans.labels_ == cluster_label) > 0 else 1.0
        
        coherence = 1.0 - (distance_to_center / (max_distance_in_cluster + 1e-6))
        doc_features.append(coherence)
        
        # 7. Semantic complexity (norm of embedding vector)
        complexity = np.linalg.norm(embedding)
        doc_features.append(complexity)
        
        # 8. Dominant semantic dimension (which LSA component is strongest)
        dominant_dim = np.argmax(np.abs(embedding))
        dominant_dim_normalized = dominant_dim / self.n_components
        doc_features.append(dominant_dim_normalized)
        
        # 9. Semantic spread (entropy of LSA weights)
        abs_weights = np.abs(embedding)
        if np.sum(abs_weights) > 0:
            weight_probs = abs_weights / np.sum(abs_weights)
            semantic_entropy = -np.sum(weight_probs * np.log(weight_probs + 1e-10))
        else:
            semantic_entropy = 0
        doc_features.append(semantic_entropy)
        
        return doc_features
    
    def _calculate_n_features(self) -> int:
        """Calculate number of output features."""
        # lsa_components (20) + cluster_onehot (n_clusters) + distances (3) +
        # coherence (1) + complexity (1) + dominant_dim (1) + entropy (1)
        return 20 + self.n_clusters + 7
    
    def _generate_feature_names(self) -> List[str]:
        """Generate feature names."""
        names = []
        
        # LSA components
        for i in range(20):
            names.append(f'semantic_dim_{i}')
        
        # Cluster membership
        for i in range(self.n_clusters):
            names.append(f'cluster_{i}')
        
        # Other features
        names.extend([
            'distance_to_cluster_center',
            'distance_to_nearest_other_cluster',
            'cluster_separation_ratio',
            'semantic_coherence',
            'semantic_complexity',
            'dominant_semantic_dimension',
            'semantic_entropy'
        ])
        
        return names
    
    def _generate_interpretation(self) -> str:
        """Generate interpretation of learned patterns."""
        explained_var = self.metadata.get('explained_variance', 0)
        silhouette = self.metadata.get('silhouette_score', 0)
        cluster_sizes = self.metadata.get('cluster_sizes', [])
        
        interpretation = f"Semantic Analysis of {self.metadata['total_docs']} cryptocurrencies:\n\n"
        interpretation += f"LSA captured {explained_var*100:.1f}% of variance in {self.n_components} dimensions.\n"
        interpretation += f"Clustering quality (silhouette score): {silhouette:.3f}\n\n"
        interpretation += f"Discovered {self.n_clusters} semantic clusters:\n"
        
        for i, size in enumerate(cluster_sizes):
            pct = 100 * size / sum(cluster_sizes) if sum(cluster_sizes) > 0 else 0
            interpretation += f"  Cluster {i}: {size} cryptos ({pct:.1f}%)\n"
        
        interpretation += "\nInterpretation: "
        if silhouette > 0.3:
            interpretation += "Strong cluster structure suggests distinct narrative categories. "
        interpretation += "Semantic positioning in latent space reveals market segmentation. "
        interpretation += "Clusters likely correspond to DeFi, memecoins, enterprise, etc. "
        
        return interpretation

