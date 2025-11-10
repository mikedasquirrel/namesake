"""
Ensemble Narrative Transformer for Crypto Domain

Analyzes how crypto names gain meaning through co-occurrence patterns
and network positioning within the cryptocurrency ecosystem.

Features extracted:
- Co-occurrence density with major cryptos
- Network centrality metrics
- Diversity indices (Shannon entropy)
- Ensemble coherence
- Ecosystem positioning

Hypothesis: Cryptos that are well-integrated into the ecosystem through
semantic and narrative connections show better survival and performance.

Author: Narrative Integration System
Date: November 2025
"""

import numpy as np
from typing import List, Dict, Set
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer
from .base_transformer import TextNarrativeTransformer


class EnsembleNarrativeTransformer(TextNarrativeTransformer):
    """Extract ensemble and network effects features."""
    
    def __init__(self, n_top_terms: int = 50, min_cooccurrence: int = 2,
                 network_metrics: bool = True, diversity_metrics: bool = True):
        """
        Initialize ensemble analyzer.
        
        Args:
            n_top_terms: Number of top terms to track for co-occurrence
            min_cooccurrence: Minimum co-occurrence threshold
            network_metrics: Compute network centrality metrics
            diversity_metrics: Compute diversity indices
        """
        super().__init__(
            narrative_id="ensemble_narrative",
            description="Analyzes network effects and ecosystem positioning"
        )
        self.n_top_terms = n_top_terms
        self.min_cooccurrence = min_cooccurrence
        self.network_metrics = network_metrics
        self.diversity_metrics = diversity_metrics
        
        self.vectorizer = None
        self.top_terms = None
        self.cooccurrence_matrix = None
    
    def fit(self, X, y=None):
        """
        Learn co-occurrence patterns and network structure.
        
        Args:
            X: List of narrative descriptions
            y: Labels (optional)
        
        Returns:
            self
        """
        self._validate_input(X)
        
        # Extract vocabulary with CountVectorizer
        self.vectorizer = CountVectorizer(
            max_features=self.n_top_terms,
            ngram_range=(1, 2),
            min_df=self.min_cooccurrence,
            stop_words='english'
        )
        
        term_matrix = self.vectorizer.fit_transform(X)
        self.top_terms = self.vectorizer.get_feature_names_out()
        
        # Compute co-occurrence matrix
        # Co-occurrence = terms appearing in same document
        self.cooccurrence_matrix = (term_matrix.T @ term_matrix).toarray()
        np.fill_diagonal(self.cooccurrence_matrix, 0)  # Remove self-cooccurrence
        
        # Store metadata
        self.metadata['n_terms'] = len(self.top_terms)
        self.metadata['total_docs'] = len(X)
        self.metadata['top_terms'] = list(self.top_terms[:20])  # Store top 20 for interpretation
        self.metadata['n_features'] = self._calculate_n_features()
        self.metadata['feature_names'] = self._generate_feature_names()
        
        self.is_fitted_ = True
        return self
    
    def transform(self, X):
        """
        Transform texts to ensemble features.
        
        Args:
            X: List of narrative descriptions
        
        Returns:
            numpy.ndarray: Feature matrix
        """
        self._validate_fitted()
        self._validate_input(X)
        
        # Transform to term matrix
        term_matrix = self.vectorizer.transform(X).toarray()
        
        features = []
        for i, text in enumerate(X):
            doc_features = self._extract_document_features(text, term_matrix[i])
            features.append(doc_features)
        
        return np.array(features, dtype=np.float32)
    
    def _extract_document_features(self, text: str, term_vector: np.ndarray) -> List[float]:
        """Extract ensemble features from document."""
        doc_features = []
        
        # 1. Ensemble size (number of tracked terms present)
        ensemble_size = np.sum(term_vector > 0)
        doc_features.append(ensemble_size / len(self.top_terms))  # Normalized
        
        # 2. Co-occurrence density
        # Average co-occurrence with all terms
        if ensemble_size > 0:
            present_term_indices = np.where(term_vector > 0)[0]
            cooccur_scores = []
            for idx in present_term_indices:
                cooccur_scores.append(np.sum(self.cooccurrence_matrix[idx]))
            avg_cooccurrence = np.mean(cooccur_scores) if cooccur_scores else 0
        else:
            avg_cooccurrence = 0
        doc_features.append(avg_cooccurrence / (self.metadata['total_docs'] + 1))
        
        # 3. Shannon diversity (term distribution entropy)
        if ensemble_size > 0:
            term_counts = term_vector[term_vector > 0]
            term_probs = term_counts / np.sum(term_counts)
            shannon_entropy = -np.sum(term_probs * np.log(term_probs + 1e-10))
        else:
            shannon_entropy = 0
        doc_features.append(shannon_entropy)
        
        # 4. Network centrality (how connected are the document's terms?)
        if ensemble_size > 1:
            present_indices = np.where(term_vector > 0)[0]
            submatrix = self.cooccurrence_matrix[np.ix_(present_indices, present_indices)]
            centrality = np.mean(np.sum(submatrix, axis=1))
        else:
            centrality = 0
        doc_features.append(centrality / (self.metadata['total_docs'] + 1))
        
        # 5. Ensemble coherence (how much do terms co-occur with each other?)
        if ensemble_size > 1:
            present_indices = np.where(term_vector > 0)[0]
            coherence_scores = []
            for i, idx1 in enumerate(present_indices):
                for idx2 in present_indices[i+1:]:
                    coherence_scores.append(self.cooccurrence_matrix[idx1, idx2])
            coherence = np.mean(coherence_scores) if coherence_scores else 0
        else:
            coherence = 0
        doc_features.append(coherence / (self.metadata['total_docs'] + 1))
        
        # 6. Ecosystem breadth (term diversity across semantic categories)
        # Categories: technical, financial, community, etc.
        tech_terms = ['bit', 'chain', 'block', 'crypto', 'token', 'protocol']
        finance_terms = ['coin', 'cash', 'finance', 'bank', 'pay', 'value']
        community_terms = ['social', 'community', 'people', 'network']
        
        text_lower = text.lower()
        categories_present = 0
        if any(term in text_lower for term in tech_terms):
            categories_present += 1
        if any(term in text_lower for term in finance_terms):
            categories_present += 1
        if any(term in text_lower for term in community_terms):
            categories_present += 1
        
        ecosystem_breadth = categories_present / 3.0
        doc_features.append(ecosystem_breadth)
        
        # 7. Major crypto connection (mentions of top cryptos)
        major_cryptos = ['bitcoin', 'ethereum', 'btc', 'eth', 'solana', 'cardano']
        has_major_connection = 1.0 if any(crypto in text_lower for crypto in major_cryptos) else 0.0
        doc_features.append(has_major_connection)
        
        # 8. Term rarity score (uses rare vs common terms)
        if ensemble_size > 0:
            # Approximate rarity by position in top terms (earlier = more common)
            present_terms = [self.top_terms[i] for i in range(len(term_vector)) if term_vector[i] > 0]
            rarity_scores = []
            for term in present_terms:
                term_idx = np.where(self.top_terms == term)[0]
                if len(term_idx) > 0:
                    rarity = term_idx[0] / len(self.top_terms)  # Later terms = rarer
                    rarity_scores.append(rarity)
            avg_rarity = np.mean(rarity_scores) if rarity_scores else 0.5
        else:
            avg_rarity = 0.5
        doc_features.append(avg_rarity)
        
        # 9. Ecosystem positioning (early vs late stage terminology)
        early_terms = ['new', 'emerging', 'innovative', 'next', 'future']
        late_terms = ['established', 'dominant', 'leader', 'major', 'foundational']
        
        early_count = sum(1 for term in early_terms if term in text_lower)
        late_count = sum(1 for term in late_terms if term in text_lower)
        
        if early_count + late_count > 0:
            positioning = late_count / (early_count + late_count)
        else:
            positioning = 0.5
        doc_features.append(positioning)
        
        return doc_features
    
    def _calculate_n_features(self) -> int:
        """Calculate number of output features."""
        # ensemble_size (1) + cooccurrence_density (1) + shannon_diversity (1) +
        # centrality (1) + coherence (1) + ecosystem_breadth (1) +
        # major_connection (1) + rarity (1) + positioning (1) = 9
        return 9
    
    def _generate_feature_names(self) -> List[str]:
        """Generate feature names."""
        return [
            'ensemble_size',
            'cooccurrence_density',
            'shannon_diversity',
            'network_centrality',
            'ensemble_coherence',
            'ecosystem_breadth',
            'major_crypto_connection',
            'term_rarity_score',
            'ecosystem_positioning'
        ]
    
    def _generate_interpretation(self) -> str:
        """Generate interpretation of learned patterns."""
        top_terms = self.metadata.get('top_terms', [])
        
        interpretation = f"Ensemble Analysis of {self.metadata['total_docs']} cryptocurrencies:\n\n"
        interpretation += f"Tracked {self.metadata['n_terms']} top terms for co-occurrence analysis.\n\n"
        interpretation += "Most common terms in ecosystem:\n"
        for i, term in enumerate(top_terms[:10], 1):
            interpretation += f"  {i}. {term}\n"
        
        interpretation += "\nInterpretation: "
        interpretation += "Network effects matter in crypto. "
        interpretation += "Coins that connect to ecosystem leaders (Bitcoin, Ethereum) and use "
        interpretation += "coherent terminology clusters show better integration. "
        interpretation += "Diversity in semantic positioning can signal broader appeal. "
        
        return interpretation

