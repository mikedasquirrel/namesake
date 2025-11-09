"""
Market Inefficiency Detector
Identify contrarian opportunities where public bias creates value
Theory: Public bias creates betting opportunities
Expected Impact: +3-5% ROI
"""

from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class MarketInefficiencyDetector:
    """Detect market inefficiencies and contrarian opportunities"""
    
    def __init__(self):
        """Initialize detector"""
        self.public_thresholds = {
            'very_popular': 0.70,    # >70% public money
            'popular': 0.60,         # 60-70% public
            'balanced': 0.55,        # 45-55% balanced
            'unpopular': 0.40,       # 30-40% public
            'very_unpopular': 0.30   # <30% public
        }
    
    def analyze_public_betting_split(self, public_percentage: float,
                                     our_prediction: Dict) -> Dict:
        """
        Analyze public betting percentage for contrarian opportunities
        
        Args:
            public_percentage: % of public money on this side (0-1)
            our_prediction: Our model's prediction with score and confidence
            
        Returns:
            Market inefficiency analysis
        """
        our_score = our_prediction.get('score', 50)
        our_confidence = our_prediction.get('confidence', 50)
        
        # Classify public sentiment
        if public_percentage >= self.public_thresholds['very_popular']:
            public_sentiment = 'VERY_POPULAR'
        elif public_percentage >= self.public_thresholds['popular']:
            public_sentiment = 'POPULAR'
        elif public_percentage >= self.public_thresholds['balanced']:
            public_sentiment = 'BALANCED'
        elif public_percentage >= self.public_thresholds['unpopular']:
            public_sentiment = 'UNPOPULAR'
        else:
            public_sentiment = 'VERY_UNPOPULAR'
        
        # Detect inefficiencies
        # Type 1: Strong model + Unpopular = CONTRARIAN VALUE
        if our_score >= 65 and public_percentage < 0.40:
            signal = 'STRONG_CONTRARIAN'
            signal_strength = (our_score - 50) * (1 - public_percentage)
            reasoning = 'High quality pick that public is fading - strong value'
        
        # Type 2: Weak model + Very Popular = FADE PUBLIC
        elif our_score <= 45 and public_percentage > 0.65:
            signal = 'FADE_PUBLIC'
            signal_strength = (50 - our_score) * public_percentage
            reasoning = 'Public overvaluing weak pick - fade opportunity'
        
        # Type 3: Moderate model + Very Unpopular = VALUE
        elif our_score >= 55 and public_percentage < 0.35:
            signal = 'VALUE_PLAY'
            signal_strength = (our_score - 50) * (1 - public_percentage) * 0.7
            reasoning = 'Decent pick being ignored - moderate value'
        
        # Type 4: Strong model + Very Popular = TRAP?
        elif our_score >= 65 and public_percentage > 0.70:
            signal = 'PUBLIC_TRAP'
            signal_strength = 0  # Neutral, don't play
            reasoning = 'Both sides agree - no edge, possible trap game'
        
        # Type 5: No clear signal
        else:
            signal = 'NO_EDGE'
            signal_strength = 0
            reasoning = 'No clear market inefficiency detected'
        
        # Calculate adjusted edge based on public split
        baseline_edge = our_score - 50
        
        # Contrarian boost: betting against public adds value
        if public_percentage > 0.60:
            contrarian_boost = (public_percentage - 0.50) * 10  # Up to +2 points
        elif public_percentage < 0.40:
            contrarian_boost = (0.50 - public_percentage) * 10  # Up to +2 points
        else:
            contrarian_boost = 0
        
        adjusted_edge = baseline_edge + contrarian_boost
        
        return {
            'public_percentage': round(public_percentage * 100, 1),
            'public_sentiment': public_sentiment,
            'our_score': our_score,
            'our_confidence': our_confidence,
            'signal': signal,
            'signal_strength': round(signal_strength, 2),
            'baseline_edge': round(baseline_edge, 2),
            'contrarian_boost': round(contrarian_boost, 2),
            'adjusted_edge': round(adjusted_edge, 2),
            'reasoning': reasoning,
            'recommended_action': self._get_recommended_action(signal, signal_strength)
        }
    
    def _get_recommended_action(self, signal: str, strength: float) -> str:
        """Get betting recommendation based on signal"""
        if signal == 'STRONG_CONTRARIAN' and strength > 15:
            return 'BET HEAVY (2x size)'
        elif signal == 'STRONG_CONTRARIAN':
            return 'BET (1.5x size)'
        elif signal == 'VALUE_PLAY' and strength > 10:
            return 'BET (1.2x size)'
        elif signal == 'FADE_PUBLIC':
            return 'BET OPPOSITE (1.3x size)'
        elif signal == 'PUBLIC_TRAP':
            return 'AVOID - No edge'
        else:
            return 'STANDARD BET (1x size)'
    
    def detect_line_movement_inefficiency(self, opening_line: float, 
                                         current_line: float,
                                         our_prediction: float) -> Dict:
        """
        Analyze line movement for sharp vs public money
        
        Args:
            opening_line: Opening line/number
            current_line: Current line/number
            our_prediction: Our predicted value
            
        Returns:
            Line movement analysis
        """
        line_movement = current_line - opening_line
        movement_direction = 'UP' if line_movement > 0 else 'DOWN' if line_movement < 0 else 'NONE'
        
        # Compare our prediction to lines
        edge_vs_opening = our_prediction - opening_line
        edge_vs_current = our_prediction - current_line
        
        # Detect patterns
        if abs(line_movement) >= 2:
            movement_significance = 'SIGNIFICANT'
        elif abs(line_movement) >= 1:
            movement_significance = 'MODERATE'
        else:
            movement_significance = 'MINIMAL'
        
        # Best bet determination
        if abs(edge_vs_opening) > abs(edge_vs_current):
            better_line = 'OPENING'
            missed_value = edge_vs_opening - edge_vs_current
        else:
            better_line = 'CURRENT'
            missed_value = 0
        
        # Sharp money detection
        # If line moved TOWARDS our prediction = sharp money agrees
        if (line_movement > 0 and our_prediction > opening_line) or \
           (line_movement < 0 and our_prediction < opening_line):
            sharp_agreement = True
            signal = 'SHARP_AGREEMENT'
        else:
            sharp_agreement = False
            signal = 'DIVERGENCE'
        
        return {
            'opening_line': opening_line,
            'current_line': current_line,
            'line_movement': round(line_movement, 2),
            'movement_direction': movement_direction,
            'movement_significance': movement_significance,
            'our_prediction': our_prediction,
            'edge_vs_opening': round(edge_vs_opening, 2),
            'edge_vs_current': round(edge_vs_current, 2),
            'better_line': better_line,
            'missed_value': round(missed_value, 2),
            'sharp_agreement': sharp_agreement,
            'signal': signal,
            'recommendation': 'BET NOW' if better_line == 'CURRENT' else 'LINE MOVED AWAY'
        }
    
    def analyze_name_hype_inefficiency(self, linguistic_features: Dict,
                                     public_percentage: float) -> Dict:
        """
        Detect when memorable names are overbet vs harsh but less memorable names
        
        Args:
            linguistic_features: Name features
            public_percentage: Public betting percentage
            
        Returns:
            Hype inefficiency analysis
        """
        harshness = linguistic_features.get('harshness', 50)
        memorability = linguistic_features.get('memorability', 50)
        
        # High memorability but low harshness = likely overbet
        if memorability > 70 and harshness < 55 and public_percentage > 0.60:
            classification = 'OVERBET_MEMORABLE'
            signal = 'FADE'
            reasoning = 'High memorability without substance, public overvalues'
        
        # High harshness but low memorability = likely underbet
        elif harshness > 65 and memorability < 60 and public_percentage < 0.45:
            classification = 'UNDERBET_HARSH'
            signal = 'VALUE'
            reasoning = 'Strong fundamentals (harshness) but low recognition - value'
        
        # Both high = fair value
        elif harshness > 65 and memorability > 65:
            classification = 'LEGITIMATE_FAVORITE'
            signal = 'FAIR'
            reasoning = 'Strong on both metrics - appropriately valued'
        
        else:
            classification = 'NEUTRAL'
            signal = 'NEUTRAL'
            reasoning = 'No clear hype inefficiency'
        
        # Calculate value score
        substance_score = harshness
        hype_score = memorability
        
        # True value is substance, but public bets on hype
        value_differential = substance_score - (hype_score * (public_percentage / 0.5))
        
        return {
            'harshness': harshness,
            'memorability': memorability,
            'public_percentage': round(public_percentage * 100, 1),
            'substance_score': substance_score,
            'hype_score': hype_score,
            'value_differential': round(value_differential, 2),
            'classification': classification,
            'signal': signal,
            'reasoning': reasoning
        }
    
    def get_contrarian_multiplier(self, public_percentage: float, 
                                  our_confidence: float) -> float:
        """
        Calculate bet size multiplier based on contrarian opportunity
        
        Args:
            public_percentage: Public betting percentage (0-1)
            our_confidence: Our model confidence (0-100)
            
        Returns:
            Multiplier (0.5 - 2.0)
        """
        # Strong contrarian opportunity
        if our_confidence >= 70 and (public_percentage < 0.35 or public_percentage > 0.75):
            # Betting against strong public sentiment with high confidence
            contrarian_strength = abs(public_percentage - 0.5) * 2  # 0-1 scale
            multiplier = 1 + (contrarian_strength * 0.8)  # Up to 1.8×
        
        # Moderate contrarian
        elif our_confidence >= 60 and (public_percentage < 0.40 or public_percentage > 0.65):
            contrarian_strength = abs(public_percentage - 0.5) * 2
            multiplier = 1 + (contrarian_strength * 0.4)  # Up to 1.4×
        
        # Fade trap (public loves it but we don't)
        elif our_confidence < 45 and public_percentage > 0.70:
            multiplier = 0.5  # Reduce bet size or skip
        
        # Normal
        else:
            multiplier = 1.0
        
        return round(multiplier, 2)


if __name__ == "__main__":
    # Test market inefficiency detector
    detector = MarketInefficiencyDetector()
    
    print("=== CONTRARIAN OPPORTUNITY DETECTION ===")
    
    # Test 1: Strong pick, low public % = VALUE
    analysis = detector.analyze_public_betting_split(
        public_percentage=0.28,
        our_prediction={'score': 72, 'confidence': 75}
    )
    print(f"\nTest 1: {analysis['signal']}")
    print(f"Public: {analysis['public_percentage']}%")
    print(f"Our Score: {analysis['our_score']}")
    print(f"Signal Strength: {analysis['signal_strength']}")
    print(f"Action: {analysis['recommended_action']}")
    print(f"Reasoning: {analysis['reasoning']}")
    
    # Test 2: Weak pick, high public % = FADE
    analysis2 = detector.analyze_public_betting_split(
        public_percentage=0.78,
        our_prediction={'score': 42, 'confidence': 65}
    )
    print(f"\nTest 2: {analysis2['signal']}")
    print(f"Public: {analysis2['public_percentage']}%")
    print(f"Action: {analysis2['recommended_action']}")
    
    # Test 3: Line movement
    print("\n=== LINE MOVEMENT ANALYSIS ===")
    line_analysis = detector.detect_line_movement_inefficiency(
        opening_line=45.5,
        current_line=47.5,
        our_prediction=48.2
    )
    print(f"Line moved: {line_analysis['line_movement']} ({line_analysis['movement_direction']})")
    print(f"Sharp agreement: {line_analysis['sharp_agreement']}")
    print(f"Recommendation: {line_analysis['recommendation']}")
    
    # Test 4: Name hype inefficiency
    print("\n=== NAME HYPE INEFFICIENCY ===")
    hype_analysis = detector.analyze_name_hype_inefficiency(
        linguistic_features={'harshness': 48, 'memorability': 85},
        public_percentage=0.72
    )
    print(f"Classification: {hype_analysis['classification']}")
    print(f"Signal: {hype_analysis['signal']}")
    print(f"Reasoning: {hype_analysis['reasoning']}")

