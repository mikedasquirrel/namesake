"""
Contextual Amplifiers
Apply multipliers based on game context (primetime, playoffs, rivalries, contract years)
Theory: High-attention situations amplify name effects
Expected Impact: +2-4% ROI
"""

from typing import Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ContextualAmplifiers:
    """Apply context-based multipliers to betting scores"""
    
    def __init__(self):
        """Initialize with context definitions"""
        self.context_multipliers = self._define_multipliers()
        self.rivalry_matchups = self._define_rivalries()
        self.market_sizes = self._define_market_sizes()
    
    def _define_multipliers(self) -> Dict:
        """Define multiplier values for each context type"""
        return {
            'primetime': {
                'memorability': 1.3,
                'harshness': 1.1,
                'overall': 1.2,
                'confidence_boost': 5,
                'rationale': 'Prime time games increase audience and name recognition'
            },
            'playoff': {
                'harshness': 1.5,
                'memorability': 1.3,
                'overall': 1.4,
                'confidence_boost': 10,
                'rationale': 'Pressure situations amplify harsh phonetic advantages'
            },
            'rivalry': {
                'all_features': 1.2,
                'overall': 1.2,
                'confidence_boost': 5,
                'rationale': 'Heightened attention increases all name effects'
            },
            'national_broadcast': {
                'memorability': 1.3,
                'overall': 1.15,
                'confidence_boost': 5,
                'rationale': 'Larger audience amplifies memorable names'
            },
            'contract_year': {
                'all_features': 1.2,
                'overall': 1.2,
                'confidence_boost': 8,
                'rationale': 'Legacy motivation peak, players at maximum intensity'
            },
            'rookie_season': {
                'memorability': 1.15,
                'overall': 1.1,
                'confidence_boost': 3,
                'rationale': 'Building recognition, names fresh in public consciousness'
            },
            'breakout': {
                'all_features': 1.15,
                'overall': 1.15,
                'confidence_boost': 10,
                'rationale': 'Momentum amplifies name recognition and performance'
            },
            'home_game': {
                'memorability': 1.1,
                'overall': 1.05,
                'confidence_boost': 2,
                'rationale': 'Home crowd amplifies name recognition'
            },
            'championship_game': {
                'harshness': 1.6,
                'memorability': 1.5,
                'overall': 1.5,
                'confidence_boost': 15,
                'rationale': 'Ultimate pressure situation, maximum attention'
            }
        }
    
    def _define_rivalries(self) -> Dict:
        """Define rivalry matchups by sport"""
        return {
            'football': [
                ('patriots', 'jets'), ('packers', 'bears'), ('cowboys', 'eagles'),
                ('steelers', 'ravens'), ('49ers', 'seahawks'), ('chiefs', 'raiders')
            ],
            'basketball': [
                ('lakers', 'celtics'), ('warriors', 'cavaliers'), ('heat', 'knicks'),
                ('bulls', 'pistons'), ('76ers', 'celtics')
            ],
            'baseball': [
                ('yankees', 'red sox'), ('dodgers', 'giants'), ('cubs', 'cardinals'),
                ('mets', 'phillies')
            ]
        }
    
    def _define_market_sizes(self) -> Dict:
        """Market size multipliers by city"""
        return {
            'New York': 1.5,
            'Los Angeles': 1.4,
            'Chicago': 1.3,
            'Houston': 1.25,
            'Philadelphia': 1.25,
            'Phoenix': 1.2,
            'San Antonio': 1.15,
            'Dallas': 1.3,
            'San Diego': 1.2,
            'San Jose': 1.2,
            'Miami': 1.25,
            'Boston': 1.3,
            'San Francisco': 1.3,
            'Seattle': 1.2,
            'Denver': 1.15,
            'Washington': 1.3,
            'Atlanta': 1.25,
            'Detroit': 1.2,
            # Smaller markets
            'Green Bay': 0.9,
            'Buffalo': 0.95,
            'Jacksonville': 0.9,
            'Sacramento': 1.0,
            # Default
            'default': 1.0
        }
    
    def detect_game_context(self, game_info: Dict) -> Dict:
        """
        Detect all applicable contexts for a game
        
        Args:
            game_info: Dict with game details
                Required: sport, date, teams
                Optional: is_primetime, is_playoff, broadcast_type, etc.
                
        Returns:
            Dict of detected contexts and their multipliers
        """
        contexts = {}
        
        # Primetime detection
        if game_info.get('is_primetime') or self._is_primetime_game(game_info):
            contexts['primetime'] = self.context_multipliers['primetime']
        
        # Playoff detection
        if game_info.get('is_playoff') or game_info.get('is_postseason'):
            contexts['playoff'] = self.context_multipliers['playoff']
        
        # Championship game
        if game_info.get('is_championship') or game_info.get('is_finals'):
            contexts['championship_game'] = self.context_multipliers['championship_game']
        
        # Rivalry detection
        if self._is_rivalry_game(game_info):
            contexts['rivalry'] = self.context_multipliers['rivalry']
        
        # National broadcast
        if game_info.get('is_national_broadcast') or game_info.get('broadcast_reach', 0) > 5000000:
            contexts['national_broadcast'] = self.context_multipliers['national_broadcast']
        
        # Home game
        if game_info.get('is_home_game'):
            contexts['home_game'] = self.context_multipliers['home_game']
        
        return contexts
    
    def detect_player_context(self, player_info: Dict) -> Dict:
        """
        Detect player-specific contexts
        
        Args:
            player_info: Dict with player details
                Optional: years_in_league, is_contract_year, performance_trend, etc.
                
        Returns:
            Dict of detected contexts
        """
        contexts = {}
        
        # Contract year
        if player_info.get('is_contract_year'):
            contexts['contract_year'] = self.context_multipliers['contract_year']
        
        # Rookie
        years_in_league = player_info.get('years_in_league', 999)
        if years_in_league <= 2:
            contexts['rookie_season'] = self.context_multipliers['rookie_season']
        
        # Breakout (performance trend > 20%)
        performance_trend = player_info.get('performance_trend', 0)
        if performance_trend > 0.2:
            contexts['breakout'] = self.context_multipliers['breakout']
        
        return contexts
    
    def apply_context_amplifiers(self, base_score: Dict, game_contexts: Dict,
                                 player_contexts: Dict) -> Dict:
        """
        Apply all context multipliers to a base score
        
        Args:
            base_score: Base betting score dict with overall_score, confidence, components
            game_contexts: Game contexts from detect_game_context()
            player_contexts: Player contexts from detect_player_context()
            
        Returns:
            Enhanced score with context multipliers applied
        """
        # Combine all contexts
        all_contexts = {**game_contexts, **player_contexts}
        
        if not all_contexts:
            # No contexts, return original
            return {
                **base_score,
                'contexts_applied': [],
                'total_multiplier': 1.0,
                'confidence_boost': 0
            }
        
        # Calculate combined multiplier
        total_multiplier = 1.0
        context_names = []
        confidence_boost = 0
        
        for context_name, context_def in all_contexts.items():
            overall_mult = context_def.get('overall', 1.0)
            total_multiplier *= overall_mult
            context_names.append(context_name)
            confidence_boost += context_def.get('confidence_boost', 0)
        
        # Cap multiplier at 3.0x for safety
        total_multiplier = min(total_multiplier, 3.0)
        
        # Apply to score
        amplified_score = base_score['overall_score'] * total_multiplier
        amplified_score = min(amplified_score, 100)  # Cap at 100
        
        # Apply confidence boost
        amplified_confidence = base_score['confidence'] + confidence_boost
        amplified_confidence = min(amplified_confidence, 95)  # Cap at 95%
        
        return {
            'base_score': base_score['overall_score'],
            'amplified_score': round(amplified_score, 2),
            'base_confidence': base_score['confidence'],
            'amplified_confidence': round(amplified_confidence, 2),
            'contexts_applied': context_names,
            'total_multiplier': round(total_multiplier, 3),
            'confidence_boost': confidence_boost,
            'context_details': {name: all_contexts[name]['rationale'] 
                              for name in context_names}
        }
    
    def _is_primetime_game(self, game_info: Dict) -> bool:
        """Detect if game is primetime based on time/day"""
        # Check if time is provided
        game_time = game_info.get('time') or game_info.get('start_time')
        if not game_time:
            return False
        
        # Convert to hour if needed
        if isinstance(game_time, str):
            try:
                hour = int(game_time.split(':')[0])
            except:
                return False
        else:
            hour = game_time
        
        # Primetime is typically 8pm-11pm
        return 20 <= hour <= 23
    
    def _is_rivalry_game(self, game_info: Dict) -> bool:
        """Check if teams are rivals"""
        sport = game_info.get('sport', '').lower()
        team1 = game_info.get('home_team', '').lower()
        team2 = game_info.get('away_team', '').lower()
        
        if not all([sport, team1, team2]):
            return False
        
        rivalries = self.rivalry_matchups.get(sport, [])
        
        for rival1, rival2 in rivalries:
            if (rival1 in team1 and rival2 in team2) or (rival2 in team1 and rival1 in team2):
                return True
        
        return False
    
    def get_market_multiplier(self, city: str) -> float:
        """Get market size multiplier for a city"""
        return self.market_sizes.get(city, self.market_sizes['default'])
    
    def get_context_summary(self, contexts: Dict) -> str:
        """Generate human-readable summary of contexts"""
        if not contexts:
            return "No special contexts detected"
        
        summary_parts = []
        for context_name in contexts.keys():
            emoji_map = {
                'primetime': '🌟',
                'playoff': '🏆',
                'rivalry': '⚔️',
                'national_broadcast': '📺',
                'contract_year': '💰',
                'rookie_season': '🆕',
                'breakout': '📈',
                'home_game': '🏠',
                'championship_game': '👑'
            }
            emoji = emoji_map.get(context_name, '✨')
            display_name = context_name.replace('_', ' ').title()
            summary_parts.append(f"{emoji} {display_name}")
        
        return " • ".join(summary_parts)


if __name__ == "__main__":
    # Test context amplifiers
    amplifiers = ContextualAmplifiers()
    
    # Test game context
    game_info = {
        'sport': 'football',
        'is_primetime': True,
        'is_playoff': True,
        'home_team': 'patriots',
        'away_team': 'jets'
    }
    
    game_contexts = amplifiers.detect_game_context(game_info)
    print(f"Detected game contexts: {list(game_contexts.keys())}")
    print(f"Summary: {amplifiers.get_context_summary(game_contexts)}")
    
    # Test player context
    player_info = {
        'is_contract_year': True,
        'years_in_league': 1
    }
    
    player_contexts = amplifiers.detect_player_context(player_info)
    print(f"\nDetected player contexts: {list(player_contexts.keys())}")
    
    # Test amplification
    base_score = {
        'overall_score': 70,
        'confidence': 65
    }
    
    amplified = amplifiers.apply_context_amplifiers(base_score, game_contexts, player_contexts)
    print(f"\nBase score: {amplified['base_score']}")
    print(f"Amplified score: {amplified['amplified_score']}")
    print(f"Multiplier: {amplified['total_multiplier']}×")
    print(f"Confidence boost: +{amplified['confidence_boost']}%")
    print(f"New confidence: {amplified['amplified_confidence']}%")

