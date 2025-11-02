"""
Semantic Analyzer
Deep meaning and metaphor analysis
"""

import logging

logger = logging.getLogger(__name__)


class SemanticAnalyzer:
    """Analyze semantic characteristics of names"""
    
    def __init__(self):
        # Metaphor categories
        self.power_words = {'titan', 'apex', 'peak', 'summit', 'prime', 'ultimate', 'supreme', 'max', 'mega', 'ultra'}
        self.journey_words = {'path', 'way', 'route', 'journey', 'quest', 'voyage', 'trek', 'passage'}
        self.growth_words = {'grow', 'rise', 'ascend', 'evolve', 'expand', 'scale', 'surge', 'bloom'}
        self.speed_words = {'fast', 'quick', 'rapid', 'swift', 'instant', 'flash', 'dash', 'bolt', 'rush'}
        self.tech_words = {'tech', 'digital', 'cyber', 'data', 'cloud', 'net', 'web', 'bit', 'byte', 'code'}
        self.natural_words = {'sun', 'moon', 'star', 'ocean', 'mountain', 'river', 'earth', 'sky', 'wind', 'fire'}
        
        # Emotional valence indicators
        self.positive_words = {'joy', 'happy', 'bright', 'light', 'smile', 'sweet', 'love', 'good', 'great', 'best'}
        self.negative_words = {'dark', 'shadow', 'doom', 'pain', 'bad', 'evil', 'hate', 'fear', 'sad'}
        
        # Concrete vs abstract
        self.concrete_words = {'apple', 'lion', 'river', 'mountain', 'star', 'car', 'house', 'tree', 'bird'}
        self.abstract_words = {'wisdom', 'truth', 'justice', 'freedom', 'peace', 'hope', 'faith', 'dream'}
    
    def analyze(self, name):
        """Comprehensive semantic analysis"""
        name_lower = name.lower()
        
        # Detect metaphor types
        is_power = any(word in name_lower for word in self.power_words)
        is_journey = any(word in name_lower for word in self.journey_words)
        is_growth = any(word in name_lower for word in self.growth_words)
        is_speed = any(word in name_lower for word in self.speed_words)
        is_tech = any(word in name_lower for word in self.tech_words)
        is_natural = any(word in name_lower for word in self.natural_words)
        
        # Determine primary metaphor
        metaphors = []
        if is_power: metaphors.append('power')
        if is_journey: metaphors.append('journey')
        if is_growth: metaphors.append('growth')
        if is_speed: metaphors.append('speed')
        if is_tech: metaphors.append('tech')
        if is_natural: metaphors.append('natural')
        
        primary_metaphor = metaphors[0] if metaphors else 'neutral'
        
        # Emotional valence
        positive_count = sum(1 for word in self.positive_words if word in name_lower)
        negative_count = sum(1 for word in self.negative_words if word in name_lower)
        
        if positive_count > negative_count:
            emotional_valence = 'positive'
            valence_score = min(100, 50 + positive_count * 10)
        elif negative_count > positive_count:
            emotional_valence = 'negative'
            valence_score = max(0, 50 - negative_count * 10)
        else:
            emotional_valence = 'neutral'
            valence_score = 50
        
        # Concrete vs abstract
        is_concrete = any(word in name_lower for word in self.concrete_words)
        is_abstract = any(word in name_lower for word in self.abstract_words)
        
        if is_concrete:
            concreteness = 'concrete'
            concreteness_score = 75
        elif is_abstract:
            concreteness = 'abstract'
            concreteness_score = 25
        else:
            concreteness = 'neutral'
            concreteness_score = 50
        
        # Imagery strength (does it evoke visual images?)
        imagery_words = self.natural_words | self.concrete_words
        imagery_count = sum(1 for word in imagery_words if word in name_lower)
        imagery_strength = min(100, imagery_count * 30)
        
        # Concept complexity (word difficulty)
        avg_word_length = len(name) / max(1, len(name.split()))
        complexity_score = min(100, avg_word_length * 8)
        
        return {
            'primary_metaphor': primary_metaphor,
            'metaphor_types': metaphors,
            'is_power_metaphor': is_power,
            'is_journey_metaphor': is_journey,
            'is_growth_metaphor': is_growth,
            'is_speed_metaphor': is_speed,
            'is_tech_oriented': is_tech,
            'is_natural_theme': is_natural,
            'emotional_valence': emotional_valence,
            'valence_score': valence_score,
            'concreteness': concreteness,
            'concreteness_score': concreteness_score,
            'imagery_strength': imagery_strength,
            'concept_complexity': complexity_score,
            'semantic_quality': self._calculate_semantic_quality(metaphors, valence_score, imagery_strength)
        }
    
    def _calculate_semantic_quality(self, metaphors, valence, imagery):
        """Calculate overall semantic quality"""
        score = 50
        
        # Having clear metaphors is good
        score += len(metaphors) * 10
        
        # Positive valence generally better
        score += (valence - 50) * 0.3
        
        # Strong imagery helps memorability
        score += imagery * 0.2
        
        return min(100, max(0, score))

