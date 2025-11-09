"""
Network Effects Analyzer
Teammate name pattern synergies and roster coherence
Theory: Name patterns of teammates interact
Expected Impact: +1-2% ROI from team chemistry insight
"""

from typing import Dict, List
import numpy as np
import logging

logger = logging.getLogger(__name__)


class NetworkEffectsAnalyzer:
    """Analyze roster-level name pattern interactions"""
    
    def __init__(self):
        """Initialize network analyzer"""
        pass
    
    def calculate_roster_coherence(self, roster_scores: List[float]) -> Dict:
        """
        Calculate roster name pattern coherence
        Theory: Teams with similar name patterns show better chemistry
        
        Args:
            roster_scores: List of player name scores
            
        Returns:
            Coherence analysis
        """
        if len(roster_scores) < 3:
            return {'error': 'Insufficient roster data'}
        
        mean_score = np.mean(roster_scores)
        variance = np.var(roster_scores)
        std_dev = np.std(roster_scores)
        
        # Low variance = high coherence (everyone similar)
        # High variance = low coherence (mismatched identities)
        
        if variance < 50:
            coherence = 'HIGH'
            multiplier = 1.15
            reasoning = 'Team has coherent name identity - chemistry bonus'
        elif variance < 150:
            coherence = 'MODERATE'
            multiplier = 1.05
            reasoning = 'Team shows moderate name coherence'
        elif variance < 300:
            coherence = 'LOW'
            multiplier = 1.0
            reasoning = 'Team has mixed name patterns - neutral'
        else:
            coherence = 'CHAOTIC'
            multiplier = 0.92
            reasoning = 'Team has wildly varying name patterns - potential identity issues'
        
        # Coherence score (0-100)
        coherence_score = max(0, 100 - (variance / 4))
        
        return {
            'roster_size': len(roster_scores),
            'mean_score': round(mean_score, 2),
            'variance': round(variance, 2),
            'std_dev': round(std_dev, 2),
            'coherence': coherence,
            'coherence_score': round(coherence_score, 2),
            'multiplier': multiplier,
            'reasoning': reasoning
        }
    
    def analyze_key_player_influence(self, key_player_score: float,
                                    roster_mean: float,
                                    position: str) -> Dict:
        """
        Analyze how key player's name affects team expectations
        Theory: QB/Star player names disproportionately affect team identity
        
        Args:
            key_player_score: Star player's name score
            roster_mean: Team average score
            position: Player position
            
        Returns:
            Influence analysis
        """
        # Position importance weights
        position_weights = {
            'QB': 3.0,      # Quarterback dominates team identity
            'PG': 2.0,      # Point guard leads
            'SP': 2.5,      # Starting pitcher
            'C': 1.8,       # Center (basketball)
            'RB': 1.5,      # Running back
            'WR': 1.3,      # Wide receiver
            'default': 1.0
        }
        
        position_weight = position_weights.get(position, position_weights['default'])
        
        # Calculate influence
        differential = key_player_score - roster_mean
        
        # Weighted influence
        influence_score = differential * position_weight
        
        # Classification
        if influence_score > 15:
            classification = 'DOMINANT_POSITIVE'
            team_multiplier = 1.20
            reasoning = f'Star {position} name dominance elevates entire team identity'
        elif influence_score > 8:
            classification = 'STRONG_POSITIVE'
            team_multiplier = 1.12
            reasoning = f'{position} provides strong positive name influence'
        elif influence_score < -15:
            classification = 'DOMINANT_NEGATIVE'
            team_multiplier = 0.88
            reasoning = f'Star {position} weak name drags down team perception'
        elif influence_score < -8:
            classification = 'STRONG_NEGATIVE'
            team_multiplier = 0.94
            reasoning = f'{position} weak name limits team potential'
        else:
            classification = 'NEUTRAL'
            team_multiplier = 1.0
            reasoning = f'{position} name aligned with team average'
        
        return {
            'position': position,
            'position_weight': position_weight,
            'key_player_score': key_player_score,
            'roster_mean': roster_mean,
            'differential': round(differential, 2),
            'influence_score': round(influence_score, 2),
            'classification': classification,
            'team_multiplier': team_multiplier,
            'reasoning': reasoning
        }
    
    def analyze_position_group_synergy(self, position_group_scores: Dict[str, List[float]]) -> Dict:
        """
        Analyze synergies within position groups
        Theory: Position groups with coherent names perform better
        
        Args:
            position_group_scores: Dict mapping position to list of scores
            
        Returns:
            Position group analysis
        """
        synergies = {}
        
        for position, scores in position_group_scores.items():
            if len(scores) < 2:
                continue
            
            variance = np.var(scores)
            mean = np.mean(scores)
            
            # Low variance in position group = synergy
            if variance < 80:
                synergy = 'HIGH'
                multiplier = 1.12
            elif variance < 200:
                synergy = 'MODERATE'
                multiplier = 1.05
            else:
                synergy = 'LOW'
                multiplier = 1.0
            
            synergies[position] = {
                'mean_score': round(mean, 2),
                'variance': round(variance, 2),
                'synergy': synergy,
                'multiplier': multiplier,
                'player_count': len(scores)
            }
        
        # Calculate overall position group coherence
        all_multipliers = [s['multiplier'] for s in synergies.values()]
        overall_multiplier = np.mean(all_multipliers) if all_multipliers else 1.0
        
        return {
            'position_groups': synergies,
            'overall_synergy_multiplier': round(overall_multiplier, 3),
            'groups_analyzed': len(synergies)
        }
    
    def analyze_rival_name_dynamics(self, team1_profile: Dict,
                                   team2_profile: Dict) -> Dict:
        """
        Analyze name pattern dynamics in rivalry matchups
        Theory: Opposing name profiles create psychological dynamics
        
        Args:
            team1_profile: Team 1 aggregate name data
            team2_profile: Team 2 aggregate name data
            
        Returns:
            Rivalry dynamics analysis
        """
        team1_harshness = team1_profile.get('mean_harshness', 50)
        team2_harshness = team2_profile.get('mean_harshness', 50)
        
        harshness_diff = team1_harshness - team2_harshness
        
        # Classify matchup
        if abs(harshness_diff) > 15:
            matchup_type = 'DOMINANT_CLASH'
            reasoning = 'One team phonetically dominates - clear identity advantage'
            advantage_multiplier = 1.18
        elif abs(harshness_diff) > 8:
            matchup_type = 'MODERATE_CLASH'
            reasoning = 'Moderate phonetic advantage - slight edge'
            advantage_multiplier = 1.10
        else:
            matchup_type = 'BALANCED_RIVALRY'
            reasoning = 'Phonetically balanced - pure talent matchup'
            advantage_multiplier = 1.0
        
        # Determine which team has advantage
        if harshness_diff > 0:
            advantage_team = 'team1'
        elif harshness_diff < 0:
            advantage_team = 'team2'
        else:
            advantage_team = 'none'
        
        return {
            'matchup_type': matchup_type,
            'team1_harshness': team1_harshness,
            'team2_harshness': team2_harshness,
            'harshness_differential': round(harshness_diff, 2),
            'advantage_team': advantage_team,
            'advantage_multiplier': advantage_multiplier,
            'reasoning': reasoning
        }


if __name__ == "__main__":
    # Test network effects
    analyzer = NetworkEffectsAnalyzer()
    
    print("="*80)
    print("NETWORK EFFECTS ANALYSIS")
    print("="*80)
    
    # Test 1: Roster coherence
    print("\n1. ROSTER COHERENCE")
    print("-" * 80)
    
    coherent_roster = [72, 75, 73, 71, 74]  # Low variance
    chaotic_roster = [85, 45, 72, 38, 91]   # High variance
    
    coherent = analyzer.calculate_roster_coherence(coherent_roster)
    print(f"Coherent roster: {coherent['coherence']}, Multiplier={coherent['multiplier']}")
    
    chaotic = analyzer.calculate_roster_coherence(chaotic_roster)
    print(f"Chaotic roster: {chaotic['coherence']}, Multiplier={chaotic['multiplier']}")
    
    # Test 2: Key player influence
    print("\n2. KEY PLAYER INFLUENCE")
    print("-" * 80)
    
    influence = analyzer.analyze_key_player_influence(
        key_player_score=88,
        roster_mean=65,
        position='QB'
    )
    print(f"QB Score: 88, Team Mean: 65")
    print(f"Classification: {influence['classification']}")
    print(f"Team Multiplier: {influence['team_multiplier']}")
    
    # Test 3: Rivalry dynamics
    print("\n3. RIVALRY DYNAMICS")
    print("-" * 80)
    
    rivalry = analyzer.analyze_rival_name_dynamics(
        team1_profile={'mean_harshness': 72},
        team2_profile={'mean_harshness': 54}
    )
    print(f"Team 1: 72 harshness, Team 2: 54 harshness")
    print(f"Matchup: {rivalry['matchup_type']}")
    print(f"Advantage: Team {rivalry['advantage_team']}")
    print(f"Multiplier: {rivalry['advantage_multiplier']}")
    
    print("\n" + "="*80)

