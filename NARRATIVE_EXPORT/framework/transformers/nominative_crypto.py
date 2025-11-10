"""
Nominative Analysis Transformer for Crypto Domain

Analyzes how cryptocurrency names encode identity through:
- Semantic field distributions (technical, financial, conceptual)
- Technical morpheme presence
- Naming convention patterns
- Category marker usage

Hypothesis: Crypto names that signal technical sophistication and category
membership through strategic morpheme selection achieve higher market caps.

Author: Narrative Integration System
Date: November 2025
"""

import re
import numpy as np
from typing import List, Dict
from collections import Counter
from .base_transformer import TextNarrativeTransformer


class NominativeAnalysisTransformer(TextNarrativeTransformer):
    """Extract nominative analysis features from crypto names."""
    
    def __init__(self, n_semantic_fields: int = 10, track_categories: bool = True, 
                 crypto_specific: bool = True):
        """
        Initialize nominative analyzer.
        
        Args:
            n_semantic_fields: Number of semantic fields to track
            track_categories: Whether to track category markers
            crypto_specific: Use crypto-specific semantic fields
        """
        super().__init__(
            narrative_id="nominative_analysis",
            description="Analyzes naming patterns and semantic field distributions"
        )
        self.n_semantic_fields = n_semantic_fields
        self.track_categories = track_categories
        self.crypto_specific = crypto_specific
        
        # Define semantic fields for crypto
        self._init_semantic_fields()
    
    def _init_semantic_fields(self):
        """Initialize semantic field dictionaries."""
        if self.crypto_specific:
            self.semantic_fields = {
                'technical': ['bit', 'byte', 'chain', 'block', 'hash', 'crypto', 'digi', 'cyber', 'node', 'protocol'],
                'financial': ['coin', 'cash', 'money', 'gold', 'silver', 'asset', 'value', 'capital', 'bank', 'finance', 'pay'],
                'speed': ['fast', 'quick', 'instant', 'rapid', 'swift', 'speed', 'flash', 'lightning'],
                'security': ['safe', 'secure', 'vault', 'lock', 'shield', 'trust', 'guard'],
                'scale': ['mega', 'ultra', 'super', 'hyper', 'omni', 'max', 'infinity'],
                'innovation': ['neo', 'next', 'future', 'new', 'quantum', 'ai', 'smart'],
                'community': ['people', 'social', 'community', 'network', 'share', 'together'],
                'authority': ['king', 'royal', 'empire', 'master', 'supreme', 'prime'],
                'nature': ['earth', 'terra', 'ocean', 'stellar', 'cosmos', 'luna', 'sol', 'stellar'],
                'playful': ['doge', 'shib', 'inu', 'pepe', 'moon', 'rocket', 'baby', 'elon', 'meme']
            }
        else:
            # Generic semantic fields
            self.semantic_fields = {
                'motion': ['move', 'flow', 'run', 'go', 'travel'],
                'cognition': ['think', 'know', 'learn', 'mind', 'smart'],
                'emotion': ['love', 'happy', 'joy', 'feel', 'heart'],
                'power': ['strong', 'power', 'force', 'might'],
                'quality': ['good', 'best', 'great', 'prime', 'top']
            }
    
    def fit(self, X, y=None):
        """
        Learn semantic field distributions from training data.
        
        Args:
            X: List of narrative descriptions
            y: Labels (optional)
        
        Returns:
            self
        """
        self._validate_input(X)
        
        # Extract corpus-level statistics
        field_counts = Counter()
        total_docs = len(X)
        
        for text in X:
            text_lower = text.lower()
            for field_name, field_words in self.semantic_fields.items():
                if any(word in text_lower for word in field_words):
                    field_counts[field_name] += 1
        
        # Store metadata
        self.metadata['field_frequencies'] = {
            field: count / total_docs 
            for field, count in field_counts.items()
        }
        self.metadata['n_features'] = self._calculate_n_features()
        self.metadata['total_docs'] = total_docs
        self.metadata['feature_names'] = self._generate_feature_names()
        
        self.is_fitted_ = True
        return self
    
    def transform(self, X):
        """
        Transform texts to nominative features.
        
        Args:
            X: List of narrative descriptions
        
        Returns:
            numpy.ndarray: Feature matrix (n_samples, n_features)
        """
        self._validate_fitted()
        self._validate_input(X)
        
        features = []
        for text in X:
            doc_features = self._extract_document_features(text)
            features.append(doc_features)
        
        return np.array(features, dtype=np.float32)
    
    def _extract_document_features(self, text: str) -> List[float]:
        """Extract nominative features from single document."""
        text_lower = text.lower()
        doc_features = []
        
        # 1. Semantic field presence (binary for each field)
        for field_name in sorted(self.semantic_fields.keys()):
            field_words = self.semantic_fields[field_name]
            has_field = 1.0 if any(word in text_lower for word in field_words) else 0.0
            doc_features.append(has_field)
        
        # 2. Semantic field density (count / text length)
        for field_name in sorted(self.semantic_fields.keys()):
            field_words = self.semantic_fields[field_name]
            count = sum(1 for word in field_words if word in text_lower)
            density = count / (len(text_lower.split()) + 1)
            doc_features.append(density)
        
        # 3. Dominant semantic field (one-hot across fields)
        field_counts = {}
        for field_name, field_words in self.semantic_fields.items():
            field_counts[field_name] = sum(1 for word in field_words if word in text_lower)
        
        dominant_field = max(field_counts, key=field_counts.get) if max(field_counts.values()) > 0 else None
        
        for field_name in sorted(self.semantic_fields.keys()):
            is_dominant = 1.0 if field_name == dominant_field else 0.0
            doc_features.append(is_dominant)
        
        # 4. Semantic diversity (number of different fields present)
        n_fields_present = sum(1 for count in field_counts.values() if count > 0)
        semantic_diversity = n_fields_present / len(self.semantic_fields)
        doc_features.append(semantic_diversity)
        
        # 5. Technical vs non-technical ratio
        if 'technical' in self.semantic_fields and 'playful' in self.semantic_fields:
            tech_count = field_counts.get('technical', 0)
            playful_count = field_counts.get('playful', 0)
            total_count = tech_count + playful_count + 1
            tech_ratio = tech_count / total_count
            doc_features.append(tech_ratio)
        else:
            doc_features.append(0.0)
        
        # 6. Category consistency (are multiple fields from same category?)
        category_mapping = {
            'technical': 'tech',
            'financial': 'finance',
            'security': 'enterprise',
            'speed': 'performance',
            'innovation': 'future',
            'scale': 'ambition',
            'community': 'social',
            'authority': 'power',
            'nature': 'organic',
            'playful': 'meme'
        }
        
        categories_present = set(
            category_mapping.get(field, 'other')
            for field, count in field_counts.items()
            if count > 0
        )
        category_consistency = 1.0 / (len(categories_present) + 1)
        doc_features.append(category_consistency)
        
        # 7. Field co-occurrence patterns (technical + financial, technical + security, etc.)
        if field_counts.get('technical', 0) > 0 and field_counts.get('financial', 0) > 0:
            doc_features.append(1.0)
        else:
            doc_features.append(0.0)
        
        if field_counts.get('technical', 0) > 0 and field_counts.get('security', 0) > 0:
            doc_features.append(1.0)
        else:
            doc_features.append(0.0)
        
        if field_counts.get('playful', 0) > 0 and field_counts.get('community', 0) > 0:
            doc_features.append(1.0)
        else:
            doc_features.append(0.0)
        
        # 8. Overall sophistication score
        sophistication_fields = {'technical', 'financial', 'security', 'innovation'}
        playful_fields = {'playful', 'community'}
        
        soph_count = sum(field_counts.get(f, 0) for f in sophistication_fields)
        play_count = sum(field_counts.get(f, 0) for f in playful_fields)
        total = soph_count + play_count + 1
        
        sophistication_score = soph_count / total
        doc_features.append(sophistication_score)
        
        return doc_features
    
    def _calculate_n_features(self) -> int:
        """Calculate number of output features."""
        n_fields = len(self.semantic_fields)
        # field_presence (n) + field_density (n) + dominant_field (n) + 
        # diversity (1) + tech_ratio (1) + consistency (1) + 
        # cooccurrence (3) + sophistication (1)
        return n_fields * 3 + 7
    
    def _generate_feature_names(self) -> List[str]:
        """Generate feature names."""
        names = []
        
        # Field presence
        for field in sorted(self.semantic_fields.keys()):
            names.append(f"field_present_{field}")
        
        # Field density
        for field in sorted(self.semantic_fields.keys()):
            names.append(f"field_density_{field}")
        
        # Dominant field
        for field in sorted(self.semantic_fields.keys()):
            names.append(f"field_dominant_{field}")
        
        # Aggregate features
        names.extend([
            'semantic_diversity',
            'tech_playful_ratio',
            'category_consistency',
            'cooccur_tech_financial',
            'cooccur_tech_security',
            'cooccur_playful_community',
            'sophistication_score'
        ])
        
        return names
    
    def _generate_interpretation(self) -> str:
        """Generate interpretation of learned patterns."""
        field_freqs = self.metadata.get('field_frequencies', {})
        
        # Find most common fields
        top_fields = sorted(field_freqs.items(), key=lambda x: x[1], reverse=True)[:5]
        
        interpretation = f"Nominative Analysis of {self.metadata['total_docs']} cryptocurrencies:\n\n"
        interpretation += "Most common semantic fields:\n"
        for field, freq in top_fields:
            interpretation += f"  - {field}: {freq*100:.1f}% of names\n"
        
        interpretation += "\nInterpretation: "
        if field_freqs.get('technical', 0) > 0.3:
            interpretation += "Technical terminology dominates naming patterns, signaling legitimacy. "
        if field_freqs.get('playful', 0) > 0.2:
            interpretation += "Significant memetic/playful naming suggests retail community focus. "
        if field_freqs.get('financial', 0) > 0.25:
            interpretation += "Traditional financial terminology indicates institutional positioning. "
        
        return interpretation

