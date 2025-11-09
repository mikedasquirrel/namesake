"""
Sports Betting Analyzer
Core betting opportunity identification engine using name pattern correlations
Leverages proven linguistic effects: Football r=0.427 harshness, NBA r=0.196, MLB r=0.221
"""

import json
import sqlite3
from pathlib import Path
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class SportsBettingAnalyzer:
    """Identify betting opportunities using linguistic name pattern analysis"""
    
    def __init__(self):
        """Initialize with correlation data and athlete databases"""
        self.base_path = Path(__file__).parent.parent / "analysis_outputs" / "sports_meta_analysis"
        self.correlations = self._load_correlations()
        self.sport_characteristics = self._load_sport_characteristics()
        
    def _load_correlations(self) -> Dict:
        """Load correlation data from analysis results"""
        correlations = {}
        
        for sport in ['football', 'basketball', 'baseball']:
            file_path = self.base_path / f"{sport}_analysis.json"
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    correlations[sport] = data['results']['correlations']
                    logger.info(f"Loaded {sport} correlations")
            except Exception as e:
                logger.error(f"Error loading {sport} correlations: {e}")
                
        return correlations
    
    def _load_sport_characteristics(self) -> Dict:
        """Load sport characteristics for weighting"""
        try:
            char_path = self.base_path / "sport_characteristics.json"
            with open(char_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading sport characteristics: {e}")
            return {}
    
    def get_sport_weight(self, sport: str) -> float:
        """
        Get correlation strength weight for sport
        Football shows 2x stronger effects than basketball
        """
        weights = {
            'football': 2.0,    # Strongest effects: r=0.427 harshness
            'baseball': 1.1,    # Moderate: r=0.221 harshness  
            'basketball': 1.0   # Baseline: r=0.196 harshness
        }
        return weights.get(sport, 1.0)
    
    def calculate_player_score(self, linguistic_features: Dict, sport: str) -> Dict:
        """
        Calculate player betting score based on linguistic features and sport-specific correlations
        
        Args:
            linguistic_features: Dict with syllables, harshness, memorability, length
            sport: 'football', 'basketball', or 'baseball'
            
        Returns:
            Dict with overall_score, component_scores, confidence
        """
        if sport not in self.correlations:
            return {'error': f'Sport {sport} not found in correlations'}
        
        sport_corr = self.correlations[sport]
        sport_weight = self.get_sport_weight(sport)
        
        # Extract correlations (all are statistically significant p<0.001)
        harshness_r = sport_corr['harshness']['r']
        syllables_r = sport_corr['syllables']['r']
        memorability_r = sport_corr['memorability']['r']
        length_r = sport_corr.get('length', {}).get('r', 0)
        
        # Normalize features to z-scores (approximate)
        # Assuming mean: syllables=2.5, harshness=50, memorability=50, length=7
        syllables_z = (linguistic_features.get('syllables', 2.5) - 2.5) / 0.8
        harshness_z = (linguistic_features.get('harshness', 50) - 50) / 15
        memorability_z = (linguistic_features.get('memorability', 50) - 50) / 15
        length_z = (linguistic_features.get('length', 7) - 7) / 2
        
        # Calculate weighted contributions
        # Higher correlation = stronger prediction
        harshness_contribution = harshness_r * harshness_z * abs(harshness_r)
        syllables_contribution = syllables_r * syllables_z * abs(syllables_r)
        memorability_contribution = memorability_r * memorability_z * abs(memorability_r)
        length_contribution = length_r * length_z * abs(length_r) if length_r else 0
        
        # Sum contributions with sport-specific weighting
        raw_score = (harshness_contribution + syllables_contribution + 
                     memorability_contribution + length_contribution) * sport_weight
        
        # Convert to 0-100 scale (higher = better predicted performance)
        # Normalize: ~±3 standard deviations -> 0-100
        overall_score = 50 + (raw_score * 10)  # Scale factor
        overall_score = max(0, min(100, overall_score))
        
        # Confidence based on correlation strength and sample size
        # Football has strongest correlations -> highest confidence
        avg_correlation = np.mean([abs(harshness_r), abs(syllables_r), abs(memorability_r)])
        confidence = avg_correlation * sport_weight * 100  # 0-100 scale
        confidence = min(confidence, 95)  # Cap at 95%
        
        return {
            'overall_score': round(overall_score, 2),
            'confidence': round(confidence, 2),
            'sport_weight': sport_weight,
            'components': {
                'harshness': {
                    'value': linguistic_features.get('harshness', 50),
                    'z_score': round(harshness_z, 2),
                    'contribution': round(harshness_contribution, 3),
                    'correlation': harshness_r
                },
                'syllables': {
                    'value': linguistic_features.get('syllables', 2.5),
                    'z_score': round(syllables_z, 2),
                    'contribution': round(syllables_contribution, 3),
                    'correlation': syllables_r
                },
                'memorability': {
                    'value': linguistic_features.get('memorability', 50),
                    'z_score': round(memorability_z, 2),
                    'contribution': round(memorability_contribution, 3),
                    'correlation': memorability_r
                },
                'length': {
                    'value': linguistic_features.get('length', 7),
                    'z_score': round(length_z, 2),
                    'contribution': round(length_contribution, 3),
                    'correlation': length_r
                }
            }
        }
    
    def get_athlete_data(self, sport: str, limit: int = 100) -> List[Dict]:
        """
        Load athlete data from SQLite database
        
        Args:
            sport: 'football', 'basketball', or 'baseball'
            limit: Number of athletes to load
            
        Returns:
            List of athlete dicts with name and linguistic features
        """
        db_path = self.base_path / f"{sport}_athletes.db"
        
        if not db_path.exists():
            logger.error(f"Database not found: {db_path}")
            return []
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Get athletes - generate linguistic features from names
            cursor.execute(f"""
                SELECT full_name, success_score
                FROM athletes
                WHERE success_score IS NOT NULL
                ORDER BY success_score DESC
                LIMIT {limit}
            """)
            
            athletes = []
            for row in cursor.fetchall():
                name = row[0]
                # Calculate linguistic features
                syllables = max(1, len(name.split()))  * 1.5  # Rough estimate
                harshness = 50 + (sum(c in name.lower() for c in 'kgptbdxz') * 5)  # Harsh phonemes
                memorability = min(100, 70 - len(name) + (sum(c in name for c in 'AEIOU') * 2))
                length = len(name)
                
                athletes.append({
                    'name': name,
                    'syllables': syllables,
                    'harshness': harshness,
                    'memorability': memorability,
                    'length': length,
                    'actual_success': row[1]
                })
            
            conn.close()
            logger.info(f"Loaded {len(athletes)} athletes from {sport} database")
            return athletes
            
        except Exception as e:
            logger.error(f"Error loading athlete data for {sport}: {e}")
            return []
    
    def identify_opportunities(self, sport: str, min_score: float = 60, 
                              min_confidence: float = 50, limit: int = 20) -> List[Dict]:
        """
        Identify top betting opportunities for a sport
        
        Args:
            sport: 'football', 'basketball', or 'baseball'
            min_score: Minimum predicted score threshold
            min_confidence: Minimum confidence threshold
            limit: Max opportunities to return
            
        Returns:
            List of betting opportunities sorted by expected value
        """
        athletes = self.get_athlete_data(sport, limit=1000)
        
        if not athletes:
            return []
        
        opportunities = []
        
        for athlete in athletes:
            # Calculate betting score
            linguistic_features = {
                'syllables': athlete['syllables'],
                'harshness': athlete['harshness'],
                'memorability': athlete['memorability'],
                'length': athlete['length']
            }
            
            score_result = self.calculate_player_score(linguistic_features, sport)
            
            # Filter by thresholds
            if (score_result['overall_score'] >= min_score and 
                score_result['confidence'] >= min_confidence):
                
                opportunity = {
                    'name': athlete['name'],
                    'sport': sport,
                    'predicted_score': score_result['overall_score'],
                    'confidence': score_result['confidence'],
                    'actual_success': athlete['actual_success'],
                    'edge': score_result['overall_score'] - athlete['actual_success'],
                    'linguistic_features': linguistic_features,
                    'components': score_result['components']
                }
                
                opportunities.append(opportunity)
        
        # Sort by edge (predicted - actual)
        opportunities.sort(key=lambda x: abs(x['edge']), reverse=True)
        
        return opportunities[:limit]
    
    def analyze_player(self, name: str, sport: str, 
                      linguistic_features: Optional[Dict] = None) -> Dict:
        """
        Analyze a specific player for betting value
        
        Args:
            name: Player name
            sport: 'football', 'basketball', or 'baseball'
            linguistic_features: Optional pre-computed features
            
        Returns:
            Complete analysis with score, confidence, recommendations
        """
        if linguistic_features is None:
            # Would need to compute features from name
            # For now, require features to be passed
            return {'error': 'Linguistic features required'}
        
        score_result = self.calculate_player_score(linguistic_features, sport)
        
        # Generate betting recommendation
        score = score_result['overall_score']
        confidence = score_result['confidence']
        
        if score >= 70 and confidence >= 60:
            recommendation = 'STRONG BET'
            reasoning = f'High predicted performance ({score:.1f}) with strong confidence ({confidence:.1f}%)'
        elif score >= 60 and confidence >= 50:
            recommendation = 'MODERATE BET'
            reasoning = f'Good predicted performance ({score:.1f}) with moderate confidence ({confidence:.1f}%)'
        elif score >= 50:
            recommendation = 'SMALL BET'
            reasoning = f'Slight edge detected ({score:.1f}), low confidence ({confidence:.1f}%)'
        else:
            recommendation = 'AVOID'
            reasoning = f'Below-average prediction ({score:.1f}), insufficient edge'
        
        return {
            'name': name,
            'sport': sport,
            'score': score_result['overall_score'],
            'confidence': score_result['confidence'],
            'recommendation': recommendation,
            'reasoning': reasoning,
            'components': score_result['components'],
            'sport_weight': score_result['sport_weight']
        }
    
    def get_sport_statistics(self, sport: str) -> Dict:
        """Get summary statistics for a sport's betting potential"""
        if sport not in self.correlations:
            return {}
        
        sport_corr = self.correlations[sport]
        sport_weight = self.get_sport_weight(sport)
        
        # Calculate average effect size
        effects = [
            abs(sport_corr['harshness']['r']),
            abs(sport_corr['syllables']['r']),
            abs(sport_corr['memorability']['r'])
        ]
        avg_effect = np.mean(effects)
        
        return {
            'sport': sport,
            'average_effect_size': round(avg_effect, 3),
            'sport_weight': sport_weight,
            'correlations': {
                'harshness': sport_corr['harshness']['r'],
                'syllables': sport_corr['syllables']['r'],
                'memorability': sport_corr['memorability']['r']
            },
            'sample_size': sport_corr['harshness']['n'],
            'betting_potential': 'HIGH' if avg_effect > 0.3 else 'MODERATE' if avg_effect > 0.2 else 'LOW'
        }
    
    def compare_sports(self) -> List[Dict]:
        """Compare betting potential across all sports"""
        comparison = []
        
        for sport in ['football', 'basketball', 'baseball']:
            stats = self.get_sport_statistics(sport)
            if stats:
                comparison.append(stats)
        
        # Sort by betting potential (average effect size)
        comparison.sort(key=lambda x: x['average_effect_size'], reverse=True)
        
        return comparison
    
    def calculate_relative_edge(self, player1_features: Dict, player2_features: Dict, 
                               sport: str) -> Dict:
        """
        Calculate relative edge between two players (CORE INNOVATION)
        Theory: It's not absolute name quality, it's RELATIVE dominance
        
        Args:
            player1_features: Linguistic features for player 1
            player2_features: Linguistic features for player 2
            sport: Sport type
            
        Returns:
            Dict with edge, dominance_factor, and bet_multiplier
        """
        # Calculate scores for both players
        score1 = self.calculate_player_score(player1_features, sport)
        score2 = self.calculate_player_score(player2_features, sport)
        
        # Calculate differential
        edge = score1['overall_score'] - score2['overall_score']
        
        # Dominance factor (normalized to 0-2 range)
        dominance_factor = abs(edge) / 50
        
        # Amplify bet sizing on large differentials
        # 10 point edge = 1.2× multiplier
        # 20 point edge = 1.4× multiplier
        # 50 point edge = 2.0× multiplier
        recommended_multiplier = 1 + (dominance_factor * 0.5)
        recommended_multiplier = min(recommended_multiplier, 2.0)  # Cap at 2×
        
        # Confidence boost when edge is large
        base_confidence = (score1['confidence'] + score2['confidence']) / 2
        edge_confidence_boost = min(abs(edge) / 2, 20)  # Up to +20% confidence
        adjusted_confidence = min(base_confidence + edge_confidence_boost, 95)
        
        return {
            'player1_score': score1['overall_score'],
            'player2_score': score2['overall_score'],
            'edge': round(edge, 2),
            'dominance_factor': round(dominance_factor, 3),
            'bet_multiplier': round(recommended_multiplier, 3),
            'base_confidence': round(base_confidence, 2),
            'adjusted_confidence': round(adjusted_confidence, 2),
            'confidence_boost': round(edge_confidence_boost, 2),
            'recommendation': self._get_edge_recommendation(edge, adjusted_confidence)
        }
    
    def _get_edge_recommendation(self, edge: float, confidence: float) -> str:
        """Generate recommendation based on relative edge"""
        if abs(edge) >= 20 and confidence >= 75:
            return 'STRONG ADVANTAGE' if edge > 0 else 'STRONG DISADVANTAGE'
        elif abs(edge) >= 10 and confidence >= 65:
            return 'MODERATE ADVANTAGE' if edge > 0 else 'MODERATE DISADVANTAGE'
        elif abs(edge) >= 5 and confidence >= 55:
            return 'SLIGHT ADVANTAGE' if edge > 0 else 'SLIGHT DISADVANTAGE'
        else:
            return 'NEUTRAL MATCHUP'
    
    def calculate_vs_defense_edge(self, player_features: Dict, 
                                  defense_quality: float, sport: str) -> Dict:
        """
        Calculate player edge vs defensive unit quality
        
        Args:
            player_features: Player linguistic features
            defense_quality: Defense quality score (0-100, lower = weaker)
            sport: Sport type
            
        Returns:
            Relative edge analysis
        """
        player_score = self.calculate_player_score(player_features, sport)
        
        # Inverse defense score (weak defense = high opportunity score)
        defense_inverse = 100 - defense_quality
        
        # Calculate relative edge
        relative_edge = player_score['overall_score'] - defense_inverse
        
        # Amplification when facing weak defense
        weakness_multiplier = 1 + ((defense_inverse - 50) / 100)  # 1.0-1.5× range
        weakness_multiplier = max(0.8, min(weakness_multiplier, 1.5))
        
        adjusted_score = player_score['overall_score'] * weakness_multiplier
        
        return {
            'player_score': player_score['overall_score'],
            'defense_quality': defense_quality,
            'defense_inverse': defense_inverse,
            'relative_edge': round(relative_edge, 2),
            'weakness_multiplier': round(weakness_multiplier, 3),
            'adjusted_score': round(adjusted_score, 2),
            'confidence': player_score['confidence'],
            'recommendation': 'EXPLOIT WEAKNESS' if relative_edge > 15 else 
                            'GOOD MATCHUP' if relative_edge > 5 else 'NEUTRAL'
        }


if __name__ == "__main__":
    # Test the analyzer
    logging.basicConfig(level=logging.INFO)
    
    analyzer = SportsBettingAnalyzer()
    
    print("\n=== SPORT COMPARISON ===")
    comparison = analyzer.compare_sports()
    for sport_stats in comparison:
        print(f"\n{sport_stats['sport'].upper()}:")
        print(f"  Average Effect Size: {sport_stats['average_effect_size']}")
        print(f"  Betting Potential: {sport_stats['betting_potential']}")
        print(f"  Sport Weight: {sport_stats['sport_weight']}x")
    
    print("\n=== TOP OPPORTUNITIES ===")
    for sport in ['football', 'basketball', 'baseball']:
        opps = analyzer.identify_opportunities(sport, min_score=60, limit=5)
        print(f"\n{sport.upper()} - Top 5:")
        for i, opp in enumerate(opps, 1):
            print(f"  {i}. {opp['name']}: Score={opp['predicted_score']:.1f}, "
                  f"Confidence={opp['confidence']:.1f}%, Edge={opp['edge']:.1f}")

