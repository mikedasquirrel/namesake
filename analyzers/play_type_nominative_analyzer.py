"""
Play-Type Nominative Analyzer
BREAKTHROUGH: Play names themselves have nominative influence
Theory: "Spider 2 Y Banana" ≠ "Four Verticals" - different name patterns, different success
Expected Impact: +2-4% ROI from play-level analysis
"""

from typing import Dict, List, Optional
import numpy as np
import logging

logger = logging.getLogger(__name__)


class PlayTypeNominativeAnalyzer:
    """Analyze nominative influence of play names and schemes"""
    
    def __init__(self):
        """Initialize play-type analyzer"""
        self.play_patterns = self._define_play_patterns()
        self.scheme_characteristics = self._define_scheme_characteristics()
    
    def _define_play_patterns(self) -> Dict:
        """
        Define play name patterns and their characteristics
        Hypothesis: Play names follow same nominative principles
        """
        return {
            # FOOTBALL PLAY TYPES
            'power_runs': {
                'examples': ['Power I', 'Counter Trey', 'Iso', 'Dive', 'Blast'],
                'characteristics': {
                    'harshness': 75,  # Heavy plosives
                    'syllables': 1.5,  # Very short
                    'memorability': 60,  # Moderate
                    'aggression_score': 90
                },
                'expected_success': 'High in goal line, short yardage',
                'nominative_hypothesis': 'Harsh, short play names for power situations'
            },
            'speed_plays': {
                'examples': ['Jet Sweep', 'Fly', 'Stretch', 'Zoom', 'Flash'],
                'characteristics': {
                    'harshness': 55,  # Moderate (fricatives)
                    'syllables': 1.3,  # Short
                    'memorability': 75,  # High (vivid imagery)
                    'aggression_score': 70
                },
                'expected_success': 'Outside runs, speed matchups',
                'nominative_hypothesis': 'Fast-sounding names for speed plays'
            },
            'precision_passes': {
                'examples': ['Slant', 'Curl', 'Post', 'Corner', 'Seam'],
                'characteristics': {
                    'harshness': 65,  # Moderate-high
                    'syllables': 1.0,  # Very short
                    'memorability': 65,  # Moderate-high
                    'aggression_score': 60
                },
                'expected_success': 'Timing routes, precision throws',
                'nominative_hypothesis': 'Precise, short names for precision plays'
            },
            'trick_plays': {
                'examples': ['Flea Flicker', 'Statue of Liberty', 'Philly Special', 'Fumblerooski'],
                'characteristics': {
                    'harshness': 50,  # Lower
                    'syllables': 3.5,  # Longer (descriptive)
                    'memorability': 95,  # Very high (memorable events)
                    'aggression_score': 40
                },
                'expected_success': 'Surprise situations, high risk',
                'nominative_hypothesis': 'Memorable names for memorable plays'
            },
            
            # BASKETBALL PLAYS
            'pick_and_roll': {
                'examples': ['Pick and Roll', 'Spain Pick', 'Horns', 'Pistol'],
                'characteristics': {
                    'harshness': 70,  # Heavy plosives (Pick, Pistol)
                    'syllables': 2.0,  # Moderate
                    'memorability': 75,  # High
                    'aggression_score': 60
                },
                'expected_success': 'Half-court offense',
                'nominative_hypothesis': 'Clear, memorable names for coordinated plays'
            },
            'isolation_plays': {
                'examples': ['Iso', 'Clear Out', 'Give and Go'],
                'characteristics': {
                    'harshness': 60,  # Moderate
                    'syllables': 1.5,  # Short
                    'memorability': 70,  # High
                    'aggression_score': 80
                },
                'expected_success': 'Star player isolation',
                'nominative_hypothesis': 'Simple names for one-on-one plays'
            },
            
            # BASEBALL PLAYS
            'fastball': {
                'examples': ['Four-Seam', 'Heater', 'Cheese', 'Gas'],
                'characteristics': {
                    'harshness': 75,  # Heavy fricatives/plosives
                    'syllables': 1.0,  # Very short
                    'memorability': 80,  # High (vivid)
                    'aggression_score': 85
                },
                'expected_success': 'Power pitching',
                'nominative_hypothesis': 'Harsh, fast-sounding names for fastballs'
            },
            'breaking_balls': {
                'examples': ['Curve', 'Slider', 'Cutter', 'Slurve'],
                'characteristics': {
                    'harshness': 65,  # Moderate (sibilants)
                    'syllables': 1.5,  # Short
                    'memorability': 70,  # Moderate-high
                    'aggression_score': 60
                },
                'expected_success': 'Deception, off-speed',
                'nominative_hypothesis': 'Smooth sounds for breaking movement'
            }
        }
    
    def _define_scheme_characteristics(self) -> Dict:
        """Define offensive/defensive scheme name patterns"""
        return {
            # FOOTBALL SCHEMES
            'west_coast': {
                'full_name': 'West Coast Offense',
                'characteristics': {
                    'syllables': 4,
                    'harshness': 55,  # Moderate (soft "west")
                    'memorability': 85,  # Very high (geographic)
                    'complexity': 8  # High complexity
                },
                'philosophy': 'Precision passing, timing routes',
                'qb_preference': 'Accuracy over power → Lower harshness'
            },
            'air_raid': {
                'full_name': 'Air Raid Offense',
                'characteristics': {
                    'syllables': 3,
                    'harshness': 70,  # High (harsh "r" and "d")
                    'memorability': 90,  # Very high (vivid imagery)
                    'complexity': 6  # Moderate
                },
                'philosophy': 'Vertical passing, speed',
                'qb_preference': 'Arm strength, aggression → Higher harshness'
            },
            'run_and_shoot': {
                'full_name': 'Run and Shoot',
                'characteristics': {
                    'syllables': 3,
                    'harshness': 75,  # High (plosives + fricatives)
                    'memorability': 85,  # High
                    'complexity': 7
                },
                'philosophy': 'Improvisational passing',
                'qb_preference': 'Creativity, memorability important'
            }
        }
    
    def analyze_play_name(self, play_name: str, play_type: str) -> Dict:
        """
        Analyze nominative characteristics of a play name
        
        Args:
            play_name: Name of the play
            play_type: Type category
            
        Returns:
            Play name analysis
        """
        # Calculate linguistic features
        syllables = max(1, len(play_name.split())) * 1.5
        harshness = 50 + (sum(c in play_name.lower() for c in 'kgptbdxz') * 5)
        memorability = min(100, 70 - len(play_name) / 2 + (sum(c in play_name for c in 'AEIOU') * 3))
        
        # Get expected pattern for type
        expected_pattern = self.play_patterns.get(play_type, {}).get('characteristics', {})
        
        # Calculate match score
        if expected_pattern:
            match_score = self._calculate_pattern_match(
                {'syllables': syllables, 'harshness': harshness, 'memorability': memorability},
                expected_pattern
            )
        else:
            match_score = 50
        
        return {
            'play_name': play_name,
            'play_type': play_type,
            'linguistic_features': {
                'syllables': syllables,
                'harshness': harshness,
                'memorability': memorability
            },
            'expected_pattern': expected_pattern,
            'match_score': round(match_score, 2),
            'prediction': 'SUCCESS' if match_score > 65 else 'MODERATE' if match_score > 50 else 'POOR',
            'reasoning': self._generate_reasoning(match_score, play_type)
        }
    
    def _calculate_pattern_match(self, actual: Dict, expected: Dict) -> float:
        """Calculate how well play name matches expected pattern"""
        deviations = []
        
        for feature in ['syllables', 'harshness', 'memorability']:
            if feature in expected and feature in actual:
                expected_val = expected[feature]
                actual_val = actual[feature]
                # Normalized deviation
                deviation = abs(actual_val - expected_val) / expected_val if expected_val > 0 else 0
                deviations.append(deviation)
        
        if not deviations:
            return 50
        
        # Average match (0 deviation = 100 score)
        avg_deviation = np.mean(deviations)
        match_score = 100 - (avg_deviation * 100)
        match_score = max(0, min(100, match_score))
        
        return match_score
    
    def _generate_reasoning(self, match_score: float, play_type: str) -> str:
        """Generate reasoning for play name prediction"""
        if match_score > 75:
            return f"Play name perfectly matches {play_type} pattern - high success probability"
        elif match_score > 60:
            return f"Play name aligns with {play_type} expectations - good success probability"
        elif match_score > 40:
            return f"Play name moderately fits {play_type} - average success"
        else:
            return f"Play name mismatches {play_type} pattern - lower success probability"
    
    def player_play_synergy(self, player_features: Dict, play_type: str) -> Dict:
        """
        Analyze synergy between player name and play type
        Theory: Harsh-named RBs excel at power runs, memorable-named WRs excel at timing routes
        
        Args:
            player_features: Player linguistic features
            play_type: Type of play
            
        Returns:
            Synergy analysis
        """
        play_pattern = self.play_patterns.get(play_type, {}).get('characteristics', {})
        
        if not play_pattern:
            return {'error': f'Unknown play type: {play_type}'}
        
        # Calculate feature alignment
        player_harshness = player_features.get('harshness', 50)
        player_memorability = player_features.get('memorability', 50)
        player_syllables = player_features.get('syllables', 2.5)
        
        play_harshness = play_pattern.get('harshness', 50)
        play_memorability = play_pattern.get('memorability', 50)
        play_syllables = play_pattern.get('syllables', 2.5)
        
        # Calculate alignment scores
        harshness_alignment = 1 - abs(player_harshness - play_harshness) / 100
        memorability_alignment = 1 - abs(player_memorability - play_memorability) / 100
        syllable_alignment = 1 - abs(player_syllables - play_syllables) / 5
        
        # Overall synergy
        synergy_score = (harshness_alignment + memorability_alignment + syllable_alignment) / 3 * 100
        
        # Synergy multiplier
        if synergy_score > 75:
            multiplier = 1.20
            classification = 'EXCELLENT SYNERGY'
        elif synergy_score > 60:
            multiplier = 1.10
            classification = 'GOOD SYNERGY'
        elif synergy_score > 40:
            multiplier = 1.0
            classification = 'NEUTRAL'
        else:
            multiplier = 0.92
            classification = 'POOR SYNERGY'
        
        return {
            'player_features': player_features,
            'play_type': play_type,
            'play_pattern': play_pattern,
            'synergy_score': round(synergy_score, 2),
            'classification': classification,
            'multiplier': multiplier,
            'reasoning': f"{classification}: Player name patterns {'align with' if synergy_score > 60 else 'mismatch'} {play_type} characteristics"
        }


if __name__ == "__main__":
    # Test play-type analyzer
    analyzer = PlayTypeNominativeAnalyzer()
    
    print("="*80)
    print("PLAY-TYPE NOMINATIVE ANALYSIS")
    print("="*80)
    
    # Test play name analysis
    print("\n1. PLAY NAME ANALYSIS")
    print("-" * 80)
    
    plays = [
        ("Power I", "power_runs"),
        ("Jet Sweep", "speed_plays"),
        ("Spider 2 Y Banana", "trick_plays")
    ]
    
    for play_name, play_type in plays:
        result = analyzer.analyze_play_name(play_name, play_type)
        print(f"\n{play_name}:")
        print(f"  Type: {play_type}")
        print(f"  Harshness: {result['linguistic_features']['harshness']}")
        print(f"  Match Score: {result['match_score']}")
        print(f"  Prediction: {result['prediction']}")
    
    # Test player-play synergy
    print("\n2. PLAYER-PLAY SYNERGY")
    print("-" * 80)
    
    # Harsh-named RB + Power run = synergy
    harsh_rb = {'harshness': 78, 'memorability': 60, 'syllables': 2}
    synergy = analyzer.player_play_synergy(harsh_rb, 'power_runs')
    print(f"\nHarsh RB (78) + Power Run:")
    print(f"  Synergy: {synergy['synergy_score']}")
    print(f"  Classification: {synergy['classification']}")
    print(f"  Multiplier: {synergy['multiplier']}×")
    
    # Memorable WR + Timing route
    memorable_wr = {'harshness': 62, 'memorability': 85, 'syllables': 2}
    synergy2 = analyzer.player_play_synergy(memorable_wr, 'precision_passes')
    print(f"\nMemorable WR (85) + Precision Pass:")
    print(f"  Synergy: {synergy2['synergy_score']}")
    print(f"  Multiplier: {synergy2['multiplier']}×")
    
    print("\n" + "="*80)

