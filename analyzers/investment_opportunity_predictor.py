"""
Investment Opportunity Predictor
Formulaic prediction of crypto investment value using narrative advantage framework

Combines:
- Absolute narrative features (tech sophistication, memorability)
- Relative competitive positioning (vs cohort)
- Market context (saturation, timing)
- Narrative gaps (missing story elements)
"""

import numpy as np
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class InvestmentOpportunityPredictor:
    """
    Predict investment opportunity score for cryptocurrencies
    Uses narrative advantage framework with competitive context
    """
    
    def __init__(self):
        self.weights = {
            # Absolute features (30% weight)
            'tech_sophistication': 0.10,
            'memorability': 0.08,
            'seriousness': 0.07,
            'pronounceability': 0.05,
            
            # Relative features (40% weight) - MORE IMPORTANT
            'relative_tech_score': 0.15,
            'competitive_differentiation': 0.12,
            'positioning_clarity': 0.08,
            'narrative_novelty': 0.05,
            
            # Market context (20% weight)
            'market_saturation': -0.10,  # Negative (crowded = bad)
            'timing_score': 0.06,
            'genre_saturation': -0.04,
            
            # Story coherence (10% weight)
            'name_description_fit': 0.05,
            'story_completeness': 0.05
        }
    
    def predict_opportunity(self, 
                          coin_data: Dict,
                          cohort_data: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Predict investment opportunity for a coin
        
        Args:
            coin_data: Dict with coin info (name, market_cap, etc.)
            cohort_data: Optional list of competitors in same cohort
        
        Returns:
            {
                'opportunity_score': float (0-100),
                'confidence': float (0-100),
                'narrative_strength': float (0-100),
                'competitive_position': str,
                'key_strengths': List[str],
                'narrative_gaps': List[Dict],  # Missing elements
                'recommendation': str
            }
        """
        logger.info(f"Analyzing investment opportunity: {coin_data.get('name', 'Unknown')}")
        
        # Extract features
        features = self._extract_all_features(coin_data, cohort_data)
        
        # Calculate weighted score
        opportunity_score = self._calculate_weighted_score(features)
        
        # Analyze narrative gaps
        gaps = self._identify_narrative_gaps(features, coin_data)
        
        # Determine competitive position
        position = self._classify_competitive_position(features, cohort_data)
        
        # Identify strengths
        strengths = self._identify_strengths(features)
        
        # Calculate confidence
        confidence = self._calculate_confidence(features, cohort_data)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(
            opportunity_score, 
            confidence, 
            gaps, 
            position
        )
        
        return {
            'opportunity_score': round(opportunity_score, 2),
            'confidence': round(confidence, 2),
            'narrative_strength': round(features.get('narrative_strength', 50), 2),
            'competitive_position': position,
            'key_strengths': strengths[:3],  # Top 3
            'narrative_gaps': gaps,
            'recommendation': recommendation,
            'features_analyzed': features
        }
    
    def _extract_all_features(self, 
                             coin_data: Dict,
                             cohort_data: Optional[List[Dict]]) -> Dict:
        """Extract complete feature set"""
        
        name = coin_data.get('name', '')
        
        features = {
            # Absolute features
            'tech_sophistication': self._measure_tech_sophistication(name),
            'memorability': self._measure_memorability(name),
            'seriousness': self._classify_seriousness_score(name),
            'pronounceability': self._measure_pronounceability(name),
            
            # Story completeness
            'has_tagline': 'tagline' in coin_data and bool(coin_data['tagline']),
            'has_description': 'description' in coin_data and bool(coin_data['description']),
            'has_categories': 'categories' in coin_data and bool(coin_data['categories']),
        }
        
        # Add relative features if cohort provided
        if cohort_data and len(cohort_data) > 1:
            features.update(self._calculate_relative_features(coin_data, cohort_data))
        else:
            # Use competitive_context if available
            competitive_context = coin_data.get('competitive_context', {})
            if competitive_context:
                features.update({
                    'relative_tech_score': 0.0,  # Would calculate from cohort_stats
                    'competitive_differentiation': 50.0,
                    'market_saturation': competitive_context.get('market_saturation', 0.5) * 100,
                })
        
        # Calculate composite scores
        features['narrative_strength'] = (
            features['tech_sophistication'] * 0.3 +
            features['memorability'] * 0.3 +
            features['seriousness'] * 0.2 +
            features['pronounceability'] * 0.2
        )
        
        features['story_completeness'] = self._measure_story_completeness(features)
        
        return features
    
    def _measure_tech_sophistication(self, name: str) -> float:
        """
        Measure technical sophistication signaling (0-100)
        Technical morphemes = higher score
        """
        tech_morphemes = ['bit', 'byte', 'crypto', 'coin', 'chain', 'block', 
                         'digi', 'cyber', 'tech', 'net', 'protocol']
        
        name_lower = name.lower()
        count = sum(1 for morph in tech_morphemes if morph in name_lower)
        
        # Each morpheme adds 25 points, cap at 100
        return min(count * 25, 100)
    
    def _measure_memorability(self, name: str) -> float:
        """Measure memorability (0-100)"""
        # Shorter + unique = more memorable
        length_score = max(0, 100 - (len(name) - 4) * 10)
        
        # Single word bonus
        word_count = len(name.split())
        word_score = 100 if word_count == 1 else 70
        
        return (length_score + word_score) / 2
    
    def _classify_seriousness_score(self, name: str) -> float:
        """
        Classify seriousness vs humor (0-100)
        100 = very serious, 0 = joke
        """
        humor_words = ['doge', 'meme', 'baby', 'moon', 'safe', 'shiba', 
                       'inu', 'pepe', 'wojak', 'chad', 'elon']
        serious_words = ['bitcoin', 'ether', 'protocol', 'network', 'finance']
        
        name_lower = name.lower()
        
        humor_count = sum(1 for word in humor_words if word in name_lower)
        serious_count = sum(1 for word in serious_words if word in name_lower)
        
        if humor_count > 0:
            return 20  # Joke token
        elif serious_count > 0:
            return 90  # Serious project
        else:
            return 60  # Neutral
    
    def _measure_pronounceability(self, name: str) -> float:
        """Measure how easy to pronounce (0-100)"""
        # Simple heuristic: consonant clusters reduce pronounceability
        difficult_clusters = ['tch', 'dge', 'phr', 'sch', 'xz']
        
        name_lower = name.lower()
        has_difficult = any(cluster in name_lower for cluster in difficult_clusters)
        
        if has_difficult:
            return 40
        elif len(name) <= 6:
            return 90
        elif len(name) <= 10:
            return 70
        else:
            return 50
    
    def _calculate_relative_features(self, 
                                     coin_data: Dict, 
                                     cohort: List[Dict]) -> Dict:
        """Calculate features relative to competitive cohort"""
        
        name = coin_data.get('name', '')
        my_tech = self._measure_tech_sophistication(name)
        
        # Calculate cohort means
        cohort_tech = [self._measure_tech_sophistication(c.get('name', '')) for c in cohort]
        mean_tech = np.mean(cohort_tech)
        
        # Relative positioning
        relative_tech = my_tech - mean_tech
        
        # Differentiation: how different from competitors?
        my_features = np.array([
            my_tech,
            self._measure_memorability(name),
            self._classify_seriousness_score(name)
        ])
        
        cohort_features = np.array([
            [self._measure_tech_sophistication(c.get('name', '')),
             self._measure_memorability(c.get('name', '')),
             self._classify_seriousness_score(c.get('name', ''))]
            for c in cohort
        ])
        
        # Distance from cohort mean
        cohort_mean = np.mean(cohort_features, axis=0)
        differentiation = np.linalg.norm(my_features - cohort_mean)
        
        return {
            'relative_tech_score': relative_tech,
            'competitive_differentiation': min(differentiation * 10, 100),
            'positioning_clarity': 75.0,  # Would calculate from feature clustering
            'narrative_novelty': self._measure_novelty(name, cohort),
            'market_saturation': (len(cohort) / 1000) * 100  # Normalize to 0-100
        }
    
    def _measure_novelty(self, name: str, cohort: List[Dict]) -> float:
        """
        How novel/unique is this narrative vs competitors? (0-100)
        """
        # Simple: check how many cohort members have similar names
        name_words = set(name.lower().split())
        
        similar_count = 0
        for competitor in cohort:
            comp_name = competitor.get('name', '')
            comp_words = set(comp_name.lower().split())
            
            # If significant overlap, consider similar
            overlap = name_words & comp_words
            if len(overlap) > 0:
                similar_count += 1
        
        # Fewer similar = more novel
        similarity_ratio = similar_count / len(cohort) if cohort else 0
        return (1 - similarity_ratio) * 100
    
    def _measure_story_completeness(self, features: Dict) -> float:
        """
        How complete is the story? (0-100)
        Checks for presence of key narrative elements
        """
        elements = [
            features.get('tech_sophistication', 0) > 20,
            features.get('memorability', 0) > 40,
            features.get('has_tagline', False),
            features.get('has_description', False),
            features.get('has_categories', False)
        ]
        
        return (sum(elements) / len(elements)) * 100
    
    def _calculate_weighted_score(self, features: Dict) -> float:
        """Calculate final opportunity score using weights"""
        
        score = 0.0
        
        for feature_name, weight in self.weights.items():
            value = features.get(feature_name, 50)  # Default to neutral 50
            score += weight * value
        
        # Normalize to 0-100
        score = max(0, min(100, score))
        
        return score
    
    def _identify_narrative_gaps(self, 
                                 features: Dict,
                                 coin_data: Dict) -> List[Dict]:
        """
        Identify missing or weak narrative elements
        Returns list of gaps with recommendations
        """
        gaps = []
        
        # Check tech sophistication
        if features.get('tech_sophistication', 0) < 30:
            gaps.append({
                'element': 'Technical Signaling',
                'current_score': features.get('tech_sophistication', 0),
                'issue': 'Name lacks technical morphemes (bit, crypto, chain, protocol)',
                'fix': 'Consider rebrand with technical prefix/suffix',
                'impact': 'HIGH',
                'example': f'"{coin_data.get("name")}" → "BitName" or "NameProtocol"'
            })
        
        # Check memorability
        if features.get('memorability', 0) < 40:
            gaps.append({
                'element': 'Memorability',
                'current_score': features.get('memorability', 0),
                'issue': 'Name too long or complex',
                'fix': 'Shorten name or create memorable ticker',
                'impact': 'MEDIUM',
                'example': f'Reduce from {len(coin_data.get("name", ""))} characters to <8'
            })
        
        # Check seriousness
        if features.get('seriousness', 60) < 40:
            gaps.append({
                'element': 'Seriousness Framing',
                'current_score': features.get('seriousness', 60),
                'issue': 'Name signals joke/meme (limits institutional capital)',
                'fix': 'Either lean into meme positioning OR rebrand for seriousness',
                'impact': 'HIGH',
                'example': 'Meme: community-driven. Serious: enterprise partnerships'
            })
        
        # Check competitive differentiation
        if features.get('competitive_differentiation', 50) < 30:
            gaps.append({
                'element': 'Competitive Differentiation',
                'current_score': features.get('competitive_differentiation', 50),
                'issue': 'Too similar to existing coins in cohort',
                'fix': 'Emphasize unique narrative angle',
                'impact': 'HIGH',
                'example': 'Market saturated - need clear positioning vs competitors'
            })
        
        # Check story completeness
        if not features.get('has_tagline', False):
            gaps.append({
                'element': 'Tagline',
                'current_score': 0,
                'issue': 'Missing compressed story (tagline)',
                'fix': 'Add clear tagline on CMC/website',
                'impact': 'MEDIUM',
                'example': 'Bitcoin: "Digital Gold" | Ethereum: "World Computer"'
            })
        
        if not features.get('has_description', False):
            gaps.append({
                'element': 'Description',
                'current_score': 0,
                'issue': 'Missing narrative summary',
                'fix': 'Write 2-3 sentence story on CMC',
                'impact': 'MEDIUM',
                'example': 'Explain value prop in narrative terms, not just tech specs'
            })
        
        if not features.get('has_categories', False):
            gaps.append({
                'element': 'Categories',
                'current_score': 0,
                'issue': 'Missing genre classification',
                'fix': 'Add categories: DeFi, NFT, L1, L2, etc.',
                'impact': 'MEDIUM',
                'example': 'Clear genre = easier for investors to evaluate fit'
            })
        
        # Sort by impact
        impact_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
        gaps.sort(key=lambda x: impact_order.get(x['impact'], 3))
        
        return gaps
    
    def _classify_competitive_position(self, 
                                      features: Dict,
                                      cohort: Optional[List[Dict]]) -> str:
        """
        Classify competitive position
        Returns: Dominant, Strong, Average, Weak, Very Weak
        """
        score = features.get('competitive_differentiation', 50)
        relative_tech = features.get('relative_tech_score', 0)
        
        if score > 75 and relative_tech > 20:
            return 'Dominant' # Clear leader in narrative space
        elif score > 60 and relative_tech > 10:
            return 'Strong'  # Well-positioned
        elif score > 40:
            return 'Average'  # Middle of pack
        elif score > 25:
            return 'Weak'  # Struggling to differentiate
        else:
            return 'Very Weak'  # Lost in crowd
    
    def _identify_strengths(self, features: Dict) -> List[str]:
        """Identify top strengths"""
        strengths = []
        
        if features.get('tech_sophistication', 0) > 70:
            strengths.append('Strong technical signaling')
        
        if features.get('memorability', 0) > 75:
            strengths.append('Highly memorable name')
        
        if features.get('seriousness', 60) > 80:
            strengths.append('Serious/institutional framing')
        
        if features.get('competitive_differentiation', 50) > 65:
            strengths.append('Well-differentiated vs competitors')
        
        if features.get('relative_tech_score', 0) > 15:
            strengths.append('More sophisticated than cohort average')
        
        if features.get('narrative_novelty', 50) > 70:
            strengths.append('Novel narrative angle')
        
        if features.get('story_completeness', 50) > 80:
            strengths.append('Complete story across all elements')
        
        return strengths if strengths else ['No major strengths identified']
    
    def _calculate_confidence(self, 
                             features: Dict,
                             cohort: Optional[List[Dict]]) -> float:
        """
        Calculate confidence in prediction (0-100)
        Higher when we have complete data and clear patterns
        """
        confidence = 50.0  # Base
        
        # More complete data = higher confidence
        if features.get('has_tagline', False):
            confidence += 10
        if features.get('has_description', False):
            confidence += 10
        if features.get('has_categories', False):
            confidence += 10
        
        # Cohort data available = higher confidence
        if cohort and len(cohort) > 50:
            confidence += 15
        
        # Clear positioning = higher confidence
        if features.get('competitive_differentiation', 50) > 60:
            confidence += 5
        
        return min(confidence, 100)
    
    def _generate_recommendation(self, 
                                 score: float,
                                 confidence: float,
                                 gaps: List[Dict],
                                 position: str) -> str:
        """Generate investment recommendation"""
        
        if score >= 75:
            rec = "STRONG BUY" if confidence > 70 else "BUY"
            reason = "Excellent narrative positioning, strong competitive differentiation"
        
        elif score >= 60:
            rec = "BUY" if confidence > 60 else "CONSIDER"
            reason = "Good narrative elements, above-average positioning"
        
        elif score >= 45:
            rec = "HOLD" if confidence > 50 else "WEAK HOLD"
            reason = "Average positioning, limited differentiation"
        
        elif score >= 30:
            rec = "AVOID"
            reason = "Weak narrative, poor competitive position"
        
        else:
            rec = "STRONG AVOID"
            reason = "Very weak narrative with major gaps"
        
        # Add gap context
        if len(gaps) >= 3:
            reason += f". {len(gaps)} major narrative gaps identified"
        
        return f"{rec}: {reason}"
    
    def batch_predict(self, coins: List[Dict]) -> List[Dict]:
        """
        Predict opportunities for multiple coins
        Automatically uses cohort for relative analysis
        """
        logger.info(f"Batch predicting {len(coins)} coins...")
        
        results = []
        for coin in coins:
            try:
                prediction = self.predict_opportunity(coin, cohort_data=coins)
                prediction['coin_name'] = coin.get('name')
                prediction['market_cap'] = coin.get('market_cap', 0)
                results.append(prediction)
            except Exception as e:
                logger.error(f"Error predicting {coin.get('name', 'unknown')}: {e}")
                continue
        
        # Sort by opportunity score
        results.sort(key=lambda x: x['opportunity_score'], reverse=True)
        
        logger.info(f"Completed {len(results)} predictions")
        return results


class NarrativeGapAnalyzer:
    """
    Identifies most valuable missing narrative element
    Tells you what to add/fix to maximize story impact
    """
    
    def analyze_gaps(self, coin_data: Dict, cohort_data: Optional[List[Dict]] = None) -> Dict:
        """
        Identify THE MOST VALUABLE missing element
        
        Returns priority-ranked gaps with:
        - What's missing
        - Why it matters
        - How to fix it
        - Expected impact
        """
        predictor = InvestmentOpportunityPredictor()
        
        # Get current prediction
        current = predictor.predict_opportunity(coin_data, cohort_data)
        current_score = current['opportunity_score']
        gaps = current['narrative_gaps']
        
        # Simulate fixing each gap
        gap_values = []
        for gap in gaps:
            # Estimate improvement from fixing this gap
            if gap['impact'] == 'HIGH':
                estimated_improvement = 15
            elif gap['impact'] == 'MEDIUM':
                estimated_improvement = 8
            else:
                estimated_improvement = 3
            
            gap['estimated_improvement'] = estimated_improvement
            gap['new_score_if_fixed'] = current_score + estimated_improvement
            gap_values.append(gap)
        
        # Sort by estimated improvement
        gap_values.sort(key=lambda x: x['estimated_improvement'], reverse=True)
        
        # Identify THE most valuable gap
        if gap_values:
            most_valuable = gap_values[0]
            
            return {
                'current_score': current_score,
                'most_valuable_gap': most_valuable,
                'all_gaps': gap_values,
                'quick_fix': most_valuable['fix'],
                'expected_new_score': most_valuable['new_score_if_fixed'],
                'improvement': most_valuable['estimated_improvement']
            }
        else:
            return {
                'current_score': current_score,
                'most_valuable_gap': None,
                'all_gaps': [],
                'message': 'No major gaps identified - narrative is complete'
            }


# =============================================================================
# Convenience Functions
# =============================================================================

def predict_investment(coin_name: str, 
                      market_cap: float = None,
                      cohort: List[Dict] = None) -> Dict:
    """
    Quick prediction for a coin
    
    Usage:
        result = predict_investment('Bitcoin')
        result = predict_investment('NewCoin', cohort=similar_coins)
    """
    coin_data = {
        'name': coin_name,
        'market_cap': market_cap
    }
    
    predictor = InvestmentOpportunityPredictor()
    return predictor.predict_opportunity(coin_data, cohort)


def find_missing_element(coin_name: str) -> Dict:
    """
    Find most valuable missing narrative element
    
    Usage:
        gap_analysis = find_missing_element('MyCoin')
        print(f"Fix: {gap_analysis['quick_fix']}")
        print(f"Impact: +{gap_analysis['improvement']} points")
    """
    coin_data = {'name': coin_name}
    analyzer = NarrativeGapAnalyzer()
    return analyzer.analyze_gaps(coin_data)

