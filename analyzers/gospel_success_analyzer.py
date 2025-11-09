"""
Gospel Success Analyzer
=======================

Analyzes religious text composition and correlates with regional adoption success.
Examines how linguistic features (name complexity, accessibility) affect religious text adoption.
"""

import logging
import numpy as np
from typing import Dict, List, Optional
from scipy import stats
from collections import Counter, defaultdict

from core.models import db, ReligiousText, ReligiousTextSuccessMetrics, RegionalAdoptionAnalysis
from analyzers.acoustic_analyzer import acoustic_analyzer
from analyzers.phonetic_universals_analyzer import phonetic_universals_analyzer

logger = logging.getLogger(__name__)


class GospelSuccessAnalyzer:
    """Analyze gospel/religious text success patterns."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("GospelSuccessAnalyzer initialized")
    
    def analyze_text_composition(self, text_name: str, full_text: str, 
                                character_names: List[str]) -> Dict:
        """
        Analyze composition features of a religious text.
        
        Args:
            text_name: Name of text (e.g., "Gospel of Matthew")
            full_text: Complete text content
            character_names: List of character names in text
        
        Returns:
            Composition analysis
        """
        words = full_text.split()
        sentences = full_text.split('.')
        
        # Basic statistics
        total_words = len(words)
        total_characters = len(full_text)
        unique_names = len(set(character_names))
        
        # Linguistic complexity
        unique_words = len(set(w.lower() for w in words))
        lexical_diversity = unique_words / total_words if total_words > 0 else 0
        
        mean_word_length = np.mean([len(w) for w in words]) if words else 0
        mean_sentence_length = np.mean([len(s.split()) for s in sentences if s.strip()]) if sentences else 0
        
        # Name composition patterns
        name_analyses = []
        for name in character_names:
            try:
                acoustic = acoustic_analyzer.analyze(name)
                name_analyses.append({
                    'name': name,
                    'syllables': self._count_syllables(name),
                    'length': len(name),
                    'melodiousness': acoustic.get('overall', {}).get('melodiousness', 0.5),
                    'complexity': acoustic.get('overall', {}).get('phonetic_complexity', 0.5)
                })
            except Exception as e:
                self.logger.error(f"Error analyzing name {name}: {e}")
        
        mean_name_syllables = np.mean([n['syllables'] for n in name_analyses]) if name_analyses else 0
        mean_name_length = np.mean([n['length'] for n in name_analyses]) if name_analyses else 0
        mean_name_melodiousness = np.mean([n['melodiousness'] for n in name_analyses]) if name_analyses else 0
        mean_name_complexity = np.mean([n['complexity'] for n in name_analyses]) if name_analyses else 0
        
        return {
            'text_name': text_name,
            'text_stats': {
                'total_words': total_words,
                'total_characters': total_characters,
                'unique_names': unique_names,
                'unique_words': unique_words
            },
            'linguistic': {
                'lexical_diversity': float(lexical_diversity),
                'mean_word_length': float(mean_word_length),
                'mean_sentence_length': float(mean_sentence_length),
                'reading_level': float(mean_sentence_length * 0.1 + mean_word_length * 0.05)  # Simplified
            },
            'name_patterns': {
                'mean_syllables': float(mean_name_syllables),
                'mean_length': float(mean_name_length),
                'melodiousness': float(mean_name_melodiousness),
                'complexity': float(mean_name_complexity)
            },
            'name_analyses': name_analyses
        }
    
    def correlate_composition_with_success(self, religious_text_id: int) -> Dict:
        """
        Correlate text composition features with regional adoption success.
        
        Args:
            religious_text_id: ID of religious text
        
        Returns:
            Correlation analysis
        """
        # Get text
        text = ReligiousText.query.get(religious_text_id)
        if not text:
            return {'error': 'Text not found'}
        
        # Get success metrics
        metrics = ReligiousTextSuccessMetrics.query.filter_by(religious_text_id=religious_text_id).all()
        if not metrics:
            return {'error': 'No success metrics found'}
        
        # Extract features
        name_melodiousness = text.name_melodiousness or 0.5
        name_complexity = text.name_complexity or 0.5
        reading_level = text.reading_level or 10
        
        # Extract success scores
        success_scores = [m.percentage_of_population for m in metrics if m.percentage_of_population]
        
        if not success_scores:
            return {'error': 'No population data available'}
        
        mean_success = np.mean(success_scores)
        
        # Calculate correlations (simplified)
        correlations = {
            'name_melodiousness_effect': self._estimate_effect(name_melodiousness, mean_success),
            'name_complexity_effect': self._estimate_effect(1 - name_complexity, mean_success),  # Inverse
            'reading_level_effect': self._estimate_effect(1 / reading_level, mean_success),  # Inverse
        }
        
        return {
            'text_name': text.text_name,
            'success_metrics': {
                'mean_adoption_percentage': float(mean_success),
                'regions_analyzed': len(metrics),
                'max_adoption': float(max(success_scores)),
                'min_adoption': float(min(success_scores))
            },
            'composition_features': {
                'name_melodiousness': float(name_melodiousness),
                'name_complexity': float(name_complexity),
                'reading_level': float(reading_level)
            },
            'correlations': correlations,
            'interpretation': self._interpret_correlations(correlations)
        }
    
    def analyze_regional_adoption(self, religious_text_id: int, region: str,
                                 regional_data: Dict) -> Dict:
        """
        Analyze adoption success in a specific region.
        
        Args:
            religious_text_id: ID of religious text
            region: Geographic region
            regional_data: Regional characteristics
        
        Returns:
            Regional adoption analysis
        """
        text = ReligiousText.query.get(religious_text_id)
        if not text:
            return {'error': 'Text not found'}
        
        # Calculate linguistic compatibility
        name_accessibility = self._calculate_accessibility(text, regional_data)
        phonetic_compatibility = self._calculate_phonetic_compatibility(text, regional_data)
        
        # Cultural fit
        cultural_fit = self._calculate_cultural_fit(text, regional_data)
        
        # Overall adoption prediction
        predicted_success = (name_accessibility * 0.3 + 
                           phonetic_compatibility * 0.3 + 
                           cultural_fit * 0.4)
        
        return {
            'text_name': text.text_name,
            'region': region,
            'linguistic_factors': {
                'name_accessibility': float(name_accessibility),
                'phonetic_compatibility': float(phonetic_compatibility)
            },
            'cultural_fit': float(cultural_fit),
            'predicted_adoption_score': float(predicted_success),
            'recommendation': self._generate_recommendation(predicted_success)
        }
    
    def compare_gospels(self, gospel_ids: List[int]) -> Dict:
        """
        Compare multiple gospels/religious texts.
        
        Args:
            gospel_ids: List of religious text IDs
        
        Returns:
            Comparative analysis
        """
        texts = [ReligiousText.query.get(gid) for gid in gospel_ids]
        texts = [t for t in texts if t is not None]
        
        if not texts:
            return {'error': 'No texts found'}
        
        comparisons = []
        for text in texts:
            metrics = ReligiousTextSuccessMetrics.query.filter_by(religious_text_id=text.id).all()
            
            success_scores = [m.percentage_of_population for m in metrics if m.percentage_of_population]
            mean_success = np.mean(success_scores) if success_scores else 0
            
            comparisons.append({
                'text_name': text.text_name,
                'name_melodiousness': text.name_melodiousness or 0.5,
                'name_complexity': text.name_complexity or 0.5,
                'reading_level': text.reading_level or 10,
                'mean_adoption_percentage': float(mean_success),
                'regions_present': len(metrics)
            })
        
        # Rank by success
        comparisons.sort(key=lambda x: x['mean_adoption_percentage'], reverse=True)
        
        return {
            'comparison_count': len(comparisons),
            'texts': comparisons,
            'insights': self._generate_comparative_insights(comparisons)
        }
    
    # Helper methods
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in word (approximation)."""
        word = word.lower()
        vowels = 'aeiou'
        syllable_count = 0
        previous_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel
        
        # Adjust for silent 'e'
        if word.endswith('e'):
            syllable_count -= 1
        
        return max(syllable_count, 1)
    
    def _estimate_effect(self, feature_value: float, outcome_value: float) -> float:
        """Estimate effect of feature on outcome (simplified)."""
        # Simple correlation estimate
        return (feature_value * outcome_value) / 100.0
    
    def _interpret_correlations(self, correlations: Dict) -> str:
        """Interpret correlation results."""
        effects = []
        for feature, effect in correlations.items():
            if effect > 0.5:
                effects.append(f"Strong positive effect of {feature}")
            elif effect > 0.2:
                effects.append(f"Moderate effect of {feature}")
        
        if not effects:
            return "Limited correlation between composition and success"
        
        return "; ".join(effects)
    
    def _calculate_accessibility(self, text: ReligiousText, regional_data: Dict) -> float:
        """Calculate name accessibility for region."""
        name_complexity = text.name_complexity or 0.5
        reading_level = text.reading_level or 10
        
        # Lower complexity and reading level = higher accessibility
        accessibility = (1 - name_complexity) * 0.5 + (10 / reading_level) * 0.5
        
        return min(accessibility, 1.0)
    
    def _calculate_phonetic_compatibility(self, text: ReligiousText, regional_data: Dict) -> float:
        """Calculate phonetic compatibility with regional language."""
        # Simplified: assume moderate compatibility
        return 0.6
    
    def _calculate_cultural_fit(self, text: ReligiousText, regional_data: Dict) -> float:
        """Calculate cultural fit score."""
        # Simplified: based on tradition similarity
        return 0.7
    
    def _generate_recommendation(self, predicted_success: float) -> str:
        """Generate adoption recommendation."""
        if predicted_success > 0.7:
            return "High adoption potential - favorable linguistic and cultural fit"
        elif predicted_success > 0.4:
            return "Moderate adoption potential - some barriers exist"
        else:
            return "Low adoption potential - significant linguistic or cultural barriers"
    
    def _generate_comparative_insights(self, comparisons: List[Dict]) -> List[str]:
        """Generate insights from gospel comparison."""
        insights = []
        
        if comparisons:
            best = comparisons[0]
            insights.append(f"{best['text_name']} has highest adoption rate ({best['mean_adoption_percentage']:.1f}%)")
            
            # Check melodiousness correlation
            melodiousness_scores = [c['name_melodiousness'] for c in comparisons]
            success_scores = [c['mean_adoption_percentage'] for c in comparisons]
            
            if len(melodiousness_scores) > 1:
                corr = np.corrcoef(melodiousness_scores, success_scores)[0, 1]
                if abs(corr) > 0.5:
                    insights.append(f"Name melodiousness {'positively' if corr > 0 else 'negatively'} correlates with adoption (r={corr:.2f})")
        
        return insights


# Singleton
gospel_success_analyzer = GospelSuccessAnalyzer()

