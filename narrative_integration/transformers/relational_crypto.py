"""
Relational Value Transformer for Crypto Domain

Analyzes how crypto names create value through complementarity
and differentiation rather than similarity.

Features extracted:
- Internal complementarity (diversity within narrative)
- Relational density (connections to corpus)
- Synergy scores (non-linear interactions)
- Differentiation metrics
- Portfolio complementarity potential

Hypothesis: Successful cryptos differentiate through non-overlapping
semantic territory while maintaining category coherence.

Author: Narrative Integration System
Date: November 2025
"""

import numpy as np
from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .base_transformer import TextNarrativeTransformer


class RelationalValueTransformer(TextNarrativeTransformer):
    """Extract relational value and complementarity features."""
    
    def __init__(self, n_features: int = 100, complementarity_threshold: float = 0.3,
                 synergy_window: int = 3):
        """
        Initialize relational analyzer.
        
        Args:
            n_features: Number of TF-IDF features for similarity computation
            complementarity_threshold: Similarity threshold for complementarity
            synergy_window: Window size for synergy detection
        """
        super().__init__(
            narrative_id="relational_value",
            description="Analyzes complementarity and relational positioning"
        )
        self.n_features = n_features
        self.complementarity_threshold = complementarity_threshold
        self.synergy_window = synergy_window
        
        self.vectorizer = None
        self.corpus_vectors = None
    
    def fit(self, X, y=None):
        """
        Learn relational patterns from training data.
        
        Args:
            X: List of narrative descriptions
            y: Labels (optional)
        
        Returns:
            self
        """
        self._validate_input(X)
        
        # Create TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=self.n_features,
            ngram_range=(1, 2),
            stop_words='english'
        )
        
        # Fit and transform corpus
        self.corpus_vectors = self.vectorizer.fit_transform(X).toarray()
        
        # Store metadata
        self.metadata['n_features_output'] = self._calculate_n_features()
        self.metadata['total_docs'] = len(X)
        self.metadata['feature_names'] = self._generate_feature_names()
        
        self.is_fitted_ = True
        return self
    
    def transform(self, X):
        """
        Transform texts to relational features.
        
        Args:
            X: List of narrative descriptions
        
        Returns:
            numpy.ndarray: Feature matrix
        """
        self._validate_fitted()
        self._validate_input(X)
        
        # Transform to TF-IDF vectors
        doc_vectors = self.vectorizer.transform(X).toarray()
        
        features = []
        for i, doc_vec in enumerate(doc_vectors):
            doc_features = self._extract_document_features(doc_vec)
            features.append(doc_features)
        
        return np.array(features, dtype=np.float32)
    
    def _extract_document_features(self, doc_vector: np.ndarray) -> List[float]:
        """Extract relational features from document vector."""
        doc_features = []
        
        # 1. Internal complementarity (diversity within document)
        # Measured by entropy of TF-IDF weights
        nonzero_weights = doc_vector[doc_vector > 0]
        if len(nonzero_weights) > 0:
            weight_probs = nonzero_weights / np.sum(nonzero_weights)
            internal_diversity = -np.sum(weight_probs * np.log(weight_probs + 1e-10))
        else:
            internal_diversity = 0
        doc_features.append(internal_diversity)
        
        # 2. Relational density (average similarity to corpus)
        similarities = cosine_similarity([doc_vector], self.corpus_vectors)[0]
        avg_similarity = np.mean(similarities)
        doc_features.append(avg_similarity)
        
        # 3. Complementarity score (how many docs are complementary?)
        # Complementary = similar but not too similar (threshold)
        complementary_count = np.sum(
            (similarities > self.complementarity_threshold) & 
            (similarities < 0.8)
        )
        complementarity_score = complementary_count / len(self.corpus_vectors)
        doc_features.append(complementarity_score)
        
        # 4. Differentiation score (uniqueness)
        # Low similarity = high differentiation
        max_similarity = np.max(similarities)
        differentiation = 1.0 - max_similarity
        doc_features.append(differentiation)
        
        # 5. Niche positioning (similarity to only a few others)
        # Count docs with similarity > 0.5
        niche_connections = np.sum(similarities > 0.5)
        niche_score = 1.0 - (niche_connections / len(self.corpus_vectors))
        doc_features.append(niche_score)
        
        # 6. Synergy potential (non-linear interactions)
        # Documents with moderate similarity across many = high synergy
        moderate_sims = np.sum((similarities > 0.3) & (similarities < 0.7))
        synergy_score = moderate_sims / len(self.corpus_vectors)
        doc_features.append(synergy_score)
        
        # 7. Relational coherence (consistency of relationships)
        # Std of similarities (low std = consistent relationships)
        relationship_std = np.std(similarities)
        coherence = 1.0 / (1.0 + relationship_std)
        doc_features.append(coherence)
        
        # 8. Portfolio fit (potential for diversification)
        # High if different from most but similar to some
        diversity_cluster_size = np.sum((similarities > 0.4) & (similarities < 0.7))
        portfolio_fit = diversity_cluster_size / len(self.corpus_vectors)
        doc_features.append(portfolio_fit)
        
        # 9. Semantic reach (breadth of connections)
        # Count of non-zero connections
        reach = np.sum(similarities > 0.1)
        semantic_reach = reach / len(self.corpus_vectors)
        doc_features.append(semantic_reach)
        
        return doc_features
    
    def _calculate_n_features(self) -> int:
        """Calculate number of output features."""
        # internal_diversity (1) + relational_density (1) + complementarity (1) +
        # differentiation (1) + niche (1) + synergy (1) + coherence (1) +
        # portfolio_fit (1) + semantic_reach (1) = 9
        return 9
    
    def _generate_feature_names(self) -> List[str]:
        """Generate feature names."""
        return [
            'internal_complementarity',
            'relational_density',
            'complementarity_score',
            'differentiation_score',
            'niche_positioning',
            'synergy_potential',
            'relational_coherence',
            'portfolio_fit',
            'semantic_reach'
        ]
    
    def _generate_interpretation(self) -> str:
        """Generate interpretation of learned patterns."""
        interpretation = f"Relational Value Analysis of {self.metadata['total_docs']} cryptocurrencies:\n\n"
        interpretation += "Analyzing complementarity and differentiation patterns.\n\n"
        interpretation += "Key insights:\n"
        interpretation += "- Successful cryptos balance differentiation (uniqueness) with category coherence\n"
        interpretation += "- Complementarity matters: neither too similar nor too different from ecosystem\n"
        interpretation += "- Portfolio positioning: value through filling semantic gaps\n"
        interpretation += "- Synergy potential: moderate similarity across diverse set creates network effects\n"
        
        return interpretation

