"""
Narrative Potential Transformer for Crypto Domain

Measures openness, possibility, and growth orientation in crypto narratives.

Features extracted:
- Future orientation (temporal markers)
- Possibility language (modal verbs, potential markers)
- Growth mindset indicators
- Innovation and disruption language
- Developmental arc positioning

Hypothesis: Cryptos with growth-oriented, possibility-rich narratives
attract more investment and achieve higher market caps.

Author: Narrative Integration System
Date: November 2025
"""

import re
import numpy as np
from typing import List
from .base_transformer import TextNarrativeTransformer


class NarrativePotentialTransformer(TextNarrativeTransformer):
    """Extract narrative potential features from crypto descriptions."""
    
    def __init__(self, track_modality: bool = True, track_flexibility: bool = True,
                 innovation_markers: bool = True):
        """
        Initialize narrative potential analyzer.
        
        Args:
            track_modality: Track possibility/modal language
            track_flexibility: Track narrative flexibility markers
            innovation_markers: Track innovation/disruption language
        """
        super().__init__(
            narrative_id="narrative_potential",
            description="Measures openness, growth orientation, and future potential in narratives"
        )
        self.track_modality = track_modality
        self.track_flexibility = track_flexibility
        self.innovation_markers = innovation_markers
        
        # Define marker sets
        self._init_markers()
    
    def _init_markers(self):
        """Initialize linguistic marker sets."""
        # Future orientation markers
        self.future_markers = [
            'will', 'future', 'next', 'coming', 'upcoming', 'tomorrow',
            'ahead', 'forward', 'evolving', 'emerging', 'becoming'
        ]
        
        # Possibility markers (modals)
        self.possibility_markers = [
            'can', 'could', 'may', 'might', 'possible', 'potentially',
            'opportunity', 'chance', 'promise', 'enable'
        ]
        
        # Growth markers
        self.growth_markers = [
            'grow', 'expand', 'scale', 'increase', 'rise', 'surge',
            'boost', 'enhance', 'improve', 'advance', 'progress'
        ]
        
        # Innovation markers
        self.innovation_markers_list = [
            'innovate', 'revolutionary', 'disrupt', 'breakthrough', 'pioneer',
            'cutting-edge', 'advanced', 'novel', 'new', 'next-gen', 'quantum'
        ]
        
        # Openness markers
        self.openness_markers = [
            'open', 'flexible', 'adapt', 'diverse', 'inclusive', 'accessible',
            'transparent', 'community', 'decentralized', 'distributed'
        ]
        
        # Development stage markers
        self.stage_markers = {
            'early': ['new', 'emerging', 'young', 'early', 'nascent', 'initial'],
            'developing': ['growing', 'developing', 'building', 'scaling'],
            'mature': ['established', 'mature', 'proven', 'stable'],
            'dominant': ['leader', 'dominant', 'major', 'leading', 'top', 'foundational']
        }
    
    def fit(self, X, y=None):
        """
        Learn narrative potential patterns from training data.
        
        Args:
            X: List of narrative descriptions
            y: Labels (optional)
        
        Returns:
            self
        """
        self._validate_input(X)
        
        # Calculate corpus statistics
        total_docs = len(X)
        future_count = 0
        possibility_count = 0
        growth_count = 0
        innovation_count = 0
        
        for text in X:
            text_lower = text.lower()
            if any(marker in text_lower for marker in self.future_markers):
                future_count += 1
            if any(marker in text_lower for marker in self.possibility_markers):
                possibility_count += 1
            if any(marker in text_lower for marker in self.growth_markers):
                growth_count += 1
            if any(marker in text_lower for marker in self.innovation_markers_list):
                innovation_count += 1
        
        # Store metadata
        self.metadata['corpus_stats'] = {
            'future_freq': future_count / total_docs,
            'possibility_freq': possibility_count / total_docs,
            'growth_freq': growth_count / total_docs,
            'innovation_freq': innovation_count / total_docs
        }
        self.metadata['n_features'] = self._calculate_n_features()
        self.metadata['total_docs'] = total_docs
        self.metadata['feature_names'] = self._generate_feature_names()
        
        self.is_fitted_ = True
        return self
    
    def transform(self, X):
        """
        Transform texts to narrative potential features.
        
        Args:
            X: List of narrative descriptions
        
        Returns:
            numpy.ndarray: Feature matrix
        """
        self._validate_fitted()
        self._validate_input(X)
        
        features = []
        for text in X:
            doc_features = self._extract_document_features(text)
            features.append(doc_features)
        
        return np.array(features, dtype=np.float32)
    
    def _extract_document_features(self, text: str) -> List[float]:
        """Extract narrative potential features from document."""
        text_lower = text.lower()
        words = text_lower.split()
        n_words = len(words) + 1
        
        doc_features = []
        
        # 1. Future orientation
        future_count = sum(1 for marker in self.future_markers if marker in text_lower)
        future_density = future_count / n_words
        has_future = 1.0 if future_count > 0 else 0.0
        doc_features.extend([future_density, has_future])
        
        # 2. Possibility language
        possibility_count = sum(1 for marker in self.possibility_markers if marker in text_lower)
        possibility_density = possibility_count / n_words
        has_possibility = 1.0 if possibility_count > 0 else 0.0
        doc_features.extend([possibility_density, has_possibility])
        
        # 3. Growth orientation
        growth_count = sum(1 for marker in self.growth_markers if marker in text_lower)
        growth_density = growth_count / n_words
        has_growth = 1.0 if growth_count > 0 else 0.0
        doc_features.extend([growth_density, has_growth])
        
        # 4. Innovation language
        innovation_count = sum(1 for marker in self.innovation_markers_list if marker in text_lower)
        innovation_density = innovation_count / n_words
        has_innovation = 1.0 if innovation_count > 0 else 0.0
        doc_features.extend([innovation_density, has_innovation])
        
        # 5. Openness
        openness_count = sum(1 for marker in self.openness_markers if marker in text_lower)
        openness_density = openness_count / n_words
        has_openness = 1.0 if openness_count > 0 else 0.0
        doc_features.extend([openness_density, has_openness])
        
        # 6. Development stage (one-hot)
        stage_scores = {}
        for stage, markers in self.stage_markers.items():
            stage_scores[stage] = sum(1 for marker in markers if marker in text_lower)
        
        dominant_stage = max(stage_scores, key=stage_scores.get) if max(stage_scores.values()) > 0 else 'unknown'
        
        for stage in ['early', 'developing', 'mature', 'dominant']:
            is_stage = 1.0 if stage == dominant_stage else 0.0
            doc_features.append(is_stage)
        
        # 7. Temporal breadth (uses both past and future)
        has_past = 1.0 if any(marker in text_lower for marker in ['historical', 'established', 'proven']) else 0.0
        temporal_breadth = has_past * has_future
        doc_features.append(temporal_breadth)
        
        # 8. Narrative momentum (combination of growth + future + innovation)
        momentum_score = (growth_density + future_density + innovation_density) / 3
        doc_features.append(momentum_score)
        
        # 9. Possibility richness (variety of possibility markers)
        possibility_variety = sum(1 for marker in self.possibility_markers if marker in text_lower)
        possibility_richness = possibility_variety / len(self.possibility_markers)
        doc_features.append(possibility_richness)
        
        # 10. Forward orientation score (composite)
        forward_score = (
            future_density * 0.3 +
            possibility_density * 0.2 +
            growth_density * 0.3 +
            innovation_density * 0.2
        )
        doc_features.append(forward_score)
        
        # 11. Developmental trajectory (early -> dominant progression implied)
        if dominant_stage in ['early', 'developing']:
            trajectory = 1.0  # Ascending
        elif dominant_stage == 'dominant':
            trajectory = 0.5  # Established
        else:
            trajectory = 0.0  # Unclear
        doc_features.append(trajectory)
        
        # 12. Flexibility indicators
        flexibility_markers = ['adapt', 'flexible', 'evolving', 'dynamic']
        flexibility_count = sum(1 for marker in flexibility_markers if marker in text_lower)
        flexibility_score = flexibility_count / len(flexibility_markers)
        doc_features.append(flexibility_score)
        
        return doc_features
    
    def _calculate_n_features(self) -> int:
        """Calculate number of output features."""
        # future (2) + possibility (2) + growth (2) + innovation (2) + openness (2) +
        # stage (4) + temporal_breadth (1) + momentum (1) + richness (1) +
        # forward_score (1) + trajectory (1) + flexibility (1) = 20
        return 20
    
    def _generate_feature_names(self) -> List[str]:
        """Generate feature names."""
        return [
            'future_density', 'has_future',
            'possibility_density', 'has_possibility',
            'growth_density', 'has_growth',
            'innovation_density', 'has_innovation',
            'openness_density', 'has_openness',
            'stage_early', 'stage_developing', 'stage_mature', 'stage_dominant',
            'temporal_breadth',
            'narrative_momentum',
            'possibility_richness',
            'forward_orientation',
            'developmental_trajectory',
            'flexibility_score'
        ]
    
    def _generate_interpretation(self) -> str:
        """Generate interpretation of learned patterns."""
        stats = self.metadata.get('corpus_stats', {})
        
        interpretation = f"Narrative Potential Analysis of {self.metadata['total_docs']} cryptocurrencies:\n\n"
        interpretation += f"Future orientation: {stats.get('future_freq', 0)*100:.1f}% of descriptions\n"
        interpretation += f"Possibility language: {stats.get('possibility_freq', 0)*100:.1f}% of descriptions\n"
        interpretation += f"Growth orientation: {stats.get('growth_freq', 0)*100:.1f}% of descriptions\n"
        interpretation += f"Innovation markers: {stats.get('innovation_freq', 0)*100:.1f}% of descriptions\n\n"
        
        interpretation += "Interpretation: "
        if stats.get('future_freq', 0) > 0.3:
            interpretation += "Strong future orientation suggests speculative narrative appeal. "
        if stats.get('innovation_freq', 0) > 0.2:
            interpretation += "Innovation language signals disruption potential. "
        if stats.get('growth_freq', 0) > 0.25:
            interpretation += "Growth-oriented narratives attract expansion-focused investors. "
        
        return interpretation

