"""
Deep Linguistic Analyzer
Integrates all deep analysis modules for comprehensive name evaluation
"""

from analyzers.phonemic_analyzer import PhonemicAnalyzer
from analyzers.semantic_analyzer import SemanticAnalyzer
from analyzers.sound_symbolism_analyzer import SoundSymbolismAnalyzer
from analyzers.prosodic_analyzer import ProsodicAnalyzer
import logging

logger = logging.getLogger(__name__)


class DeepLinguisticAnalyzer:
    """Comprehensive deep linguistic analysis"""
    
    def __init__(self):
        self.phonemic = PhonemicAnalyzer()
        self.semantic = SemanticAnalyzer()
        self.sound_symbolism = SoundSymbolismAnalyzer()
        self.prosodic = ProsodicAnalyzer()
    
    def analyze(self, name):
        """
        Run all deep analyses on a name
        
        Returns: Comprehensive linguistic profile with 40+ metrics
        """
        try:
            phonemic_results = self.phonemic.analyze(name)
            semantic_results = self.semantic.analyze(name)
            symbolism_results = self.sound_symbolism.analyze(name)
            prosodic_results = self.prosodic.analyze(name)
            
            # Calculate composite deep score
            deep_score = self._calculate_deep_score(
                phonemic_results,
                semantic_results,
                symbolism_results,
                prosodic_results
            )
            
            # Generate insights
            insights = self._generate_insights(
                name,
                phonemic_results,
                semantic_results,
                symbolism_results,
                prosodic_results
            )
            
            return {
                'name': name,
                'deep_score': deep_score,
                'phonemic': phonemic_results,
                'semantic': semantic_results,
                'sound_symbolism': symbolism_results,
                'prosodic': prosodic_results,
                'insights': insights,
                'quality_breakdown': {
                    'phonemic_quality': phonemic_results['phonemic_quality'],
                    'semantic_quality': semantic_results['semantic_quality'],
                    'symbolism_quality': symbolism_results['sound_symbolism_quality'],
                    'prosodic_quality': prosodic_results['prosodic_quality']
                }
            }
        
        except Exception as e:
            logger.error(f"Deep analysis error for '{name}': {e}")
            return None
    
    def _calculate_deep_score(self, phonemic, semantic, symbolism, prosodic):
        """Calculate comprehensive deep linguistic score"""
        
        # Weighted combination of all factors
        score = (
            phonemic['phonemic_quality'] * 0.25 +
            semantic['semantic_quality'] * 0.25 +
            symbolism['sound_symbolism_quality'] * 0.20 +
            prosodic['prosodic_quality'] * 0.30
        )
        
        return round(score, 1)
    
    def _generate_insights(self, name, phonemic, semantic, symbolism, prosodic):
        """Generate human-readable insights about the name"""
        insights = []
        
        # Phonemic insights
        if phonemic['initial_is_plosive']:
            insights.append(f"Starts with plosive '{phonemic['initial_sound']}' - strong, memorable opening")
        
        if phonemic['has_alliteration']:
            insights.append("Uses alliteration - enhances memorability")
        
        if phonemic['phonotactic_score'] > 80:
            insights.append("Natural sound combinations - easy to pronounce")
        
        # Semantic insights
        if semantic['primary_metaphor'] != 'neutral':
            insights.append(f"Uses {semantic['primary_metaphor']} metaphor - clear conceptual association")
        
        if semantic['emotional_valence'] == 'positive':
            insights.append("Positive emotional associations - approachable")
        
        if semantic['imagery_strength'] > 60:
            insights.append("Strong visual imagery - highly memorable")
        
        # Sound symbolism insights
        if symbolism['bouba_kiki_type'] == 'kiki':
            insights.append("Sharp sound profile - signals precision/tech")
        elif symbolism['bouba_kiki_type'] == 'bouba':
            insights.append("Round sound profile - signals friendliness/approachability")
        
        if symbolism['speed_association'] == 'fast/dynamic':
            insights.append("Fast-sounding - connotes dynamism and energy")
        
        if symbolism['strength_perception'] == 'strong/authoritative':
            insights.append("Strong consonants - authoritative presence")
        
        # Prosodic insights
        if prosodic['stress_pattern'] == 'trochaic':
            insights.append("Trochaic rhythm - natural English stress pattern")
        
        if prosodic['flow_score'] > 80:
            insights.append("Excellent flow - smooth pronunciation")
        
        if prosodic['catchiness'] > 80:
            insights.append("Highly catchy - likely to spread virally")
        
        return insights
    
    def explain_score(self, name, deep_analysis):
        """Generate detailed explanation of why name scored as it did"""
        if not deep_analysis:
            return "Analysis failed"
        
        score = deep_analysis['deep_score']
        insights = deep_analysis['insights']
        
        explanation = f"{name} scores {score}/100.\n\n"
        
        if score >= 80:
            explanation += "This is an EXCELLENT name. "
        elif score >= 65:
            explanation += "This is a GOOD name. "
        elif score >= 50:
            explanation += "This is an AVERAGE name. "
        else:
            explanation += "This name has WEAKNESSES. "
        
        explanation += "\n\nKey factors:\n"
        for insight in insights[:5]:  # Top 5 insights
            explanation += f"• {insight}\n"
        
        breakdown = deep_analysis['quality_breakdown']
        explanation += f"\nQuality breakdown:\n"
        explanation += f"• Phonemic: {breakdown['phonemic_quality']:.1f}/100\n"
        explanation += f"• Semantic: {breakdown['semantic_quality']:.1f}/100\n"
        explanation += f"• Sound Symbolism: {breakdown['symbolism_quality']:.1f}/100\n"
        explanation += f"• Prosodic: {breakdown['prosodic_quality']:.1f}/100\n"
        
        return explanation

