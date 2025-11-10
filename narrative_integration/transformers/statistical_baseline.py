"""
Statistical Transformer (TF-IDF Baseline)

Pure frequency-based statistical approach without narrative interpretation.
Serves as baseline for comparison with narrative transformers.

Features extracted:
- TF-IDF vectors (term frequency-inverse document frequency)
- No semantic analysis
- No narrative hypothesis

Purpose: Test whether narrative features outperform simple statistics (H1).

Author: Narrative Integration System
Date: November 2025
"""

import numpy as np
from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
from .base_transformer import TextNarrativeTransformer


class StatisticalTransformer(TextNarrativeTransformer):
    """TF-IDF baseline without narrative interpretation."""
    
    def __init__(self, max_features: int = 1000, ngram_range: tuple = (1, 2),
                 min_df: int = 2, max_df: float = 0.8):
        """
        Initialize statistical transformer.
        
        Args:
            max_features: Maximum number of features
            ngram_range: N-gram range for features
            min_df: Minimum document frequency
            max_df: Maximum document frequency
        """
        super().__init__(
            narrative_id="statistical_baseline",
            description="TF-IDF baseline without narrative interpretation"
        )
        self.max_features = max_features
        self.ngram_range = ngram_range
        self.min_df = min_df
        self.max_df = max_df
        
        self.vectorizer = None
    
    def fit(self, X, y=None):
        """
        Fit TF-IDF vectorizer.
        
        Args:
            X: List of narrative descriptions
            y: Labels (optional)
        
        Returns:
            self
        """
        self._validate_input(X)
        
        # Create and fit vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=self.max_features,
            ngram_range=self.ngram_range,
            min_df=self.min_df,
            max_df=self.max_df,
            stop_words='english'
        )
        
        self.vectorizer.fit(X)
        
        # Store metadata
        feature_names = self.vectorizer.get_feature_names_out()
        self.metadata['n_features'] = len(feature_names)
        self.metadata['total_docs'] = len(X)
        self.metadata['vocabulary_size'] = len(feature_names)
        self.metadata['feature_names'] = list(feature_names)
        self.metadata['top_features'] = list(feature_names[:20])  # Store top 20
        
        self.is_fitted_ = True
        return self
    
    def transform(self, X):
        """
        Transform texts to TF-IDF features.
        
        Args:
            X: List of narrative descriptions
        
        Returns:
            numpy.ndarray: TF-IDF feature matrix
        """
        self._validate_fitted()
        self._validate_input(X)
        
        # Transform to TF-IDF
        tfidf_matrix = self.vectorizer.transform(X).toarray()
        
        return tfidf_matrix.astype(np.float32)
    
    def get_feature_names(self) -> List[str]:
        """Get feature names (TF-IDF terms)."""
        self._validate_fitted()
        return self.metadata['feature_names']
    
    def _generate_interpretation(self) -> str:
        """Generate interpretation."""
        vocab_size = self.metadata.get('vocabulary_size', 0)
        top_features = self.metadata.get('top_features', [])
        
        interpretation = f"Statistical Baseline Analysis of {self.metadata['total_docs']} cryptocurrencies:\n\n"
        interpretation += f"Vocabulary size: {vocab_size} terms\n"
        interpretation += f"Feature type: TF-IDF (no narrative interpretation)\n\n"
        interpretation += "Top 20 terms by frequency:\n"
        for i, term in enumerate(top_features, 1):
            interpretation += f"  {i:2d}. {term}\n"
        
        interpretation += "\nInterpretation: Pure statistical baseline. "
        interpretation += "No narrative hypothesis encoded. "
        interpretation += "Serves as comparison point for narrative transformers (H1 test). "
        
        return interpretation

