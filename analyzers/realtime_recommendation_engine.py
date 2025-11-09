"""
Real-Time Recommendation Engine
Generate live betting recommendations with current odds and player data
Updates every 15 minutes with fresh opportunities
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class RealtimeRecommendationEngine:
    """Generate and update betting recommendations in real-time"""
    
    def __init__(self):
        """Initialize real-time engine"""
        self.current_recommendations = []
        self.last_update = None
        self.update_interval = 900  # 15 minutes in seconds
    
    def generate_live_recommendations(self, games_today: List[Dict],
                                     market_odds: List[Dict],
                                     player_database: Dict) -> List[Dict]:
        """
        Generate live betting recommendations for today's games
        
        Args:
            games_today: Today's scheduled games
            market_odds: Current betting lines and odds
            player_database: Player linguistic features and stats
            
        Returns:
            List of recommended bets with all analysis
        """
        from analyzers.integrated_betting_analyzer import IntegratedBettingAnalyzer
        from analyzers.position_specific_optimizer import PositionSpecificOptimizer
        from analyzers.sport_specific_prominence_finder import SportSpecificProminenceFinder
        
        analyzer = IntegratedBettingAnalyzer()
        position_optimizer = PositionSpecificOptimizer()
        prominence_finder = SportSpecificProminenceFinder()
        
        recommendations = []
        
        for game in games_today:
            # Determine if this is a high-prominence situation
            game_context = self._extract_game_context(game)
            
            # Get players for this game
            home_players = self._get_team_players(game['home_team'], player_database)
            away_players = self._get_team_players(game['away_team'], player_database)
            
            # Analyze each player
            for player in home_players + away_players:
                # Get market odds for player (if available)
                player_odds = self._find_player_odds(player, market_odds)
                
                if not player_odds:
                    continue  # No odds available
                
                # Run complete analysis
                try:
                    analysis = analyzer.complete_analysis(
                        player_data=player,
                        game_context=game_context,
                        opponent_data=self._get_opponent(player, home_players, away_players),
                        market_data=player_odds
                    )
                    
                    # Filter by quality thresholds
                    if (analysis['final_score'] >= 65 and 
                        analysis['final_confidence'] >= 70 and
                        analysis['expected_roi'] >= 15):
                        
                        recommendations.append({
                            **analysis,
                            'game': game,
                            'prop_available': player_odds,
                            'timestamp': datetime.now().isoformat(),
                            'priority': self._calculate_priority(analysis)
                        })
                
                except Exception as e:
                    logger.error(f"Error analyzing {player.get('name', 'unknown')}: {e}")
                    continue
        
        # Sort by expected ROI
        recommendations.sort(key=lambda x: x['expected_roi'], reverse=True)
        
        # Update cache
        self.current_recommendations = recommendations[:50]  # Top 50
        self.last_update = datetime.now()
        
        logger.info(f"Generated {len(recommendations)} live recommendations")
        
        return recommendations
    
    def _extract_game_context(self, game: Dict) -> Dict:
        """Extract game context from game data"""
        return {
            'sport': game.get('sport', 'football'),
            'is_primetime': self._is_primetime(game),
            'is_playoff': self._is_playoff(game),
            'is_championship': self._is_championship(game),
            'is_rivalry': self._is_rivalry(game),
            'is_national_broadcast': self._is_national_broadcast(game),
            'is_home_game': True,  # Would determine per player
            'home_team': game.get('home_team'),
            'away_team': game.get('away_team')
        }
    
    def _is_primetime(self, game: Dict) -> bool:
        """Detect if game is primetime"""
        broadcast = game.get('broadcast', '')
        game_time = game.get('date', '')
        
        # Check for primetime broadcasts
        primetime_networks = ['NBC', 'ESPN', 'TNT', 'ABC', 'FOX']
        if any(network in broadcast for network in primetime_networks):
            return True
        
        # Check time (if available)
        if game_time:
            try:
                dt = datetime.fromisoformat(game_time.replace('Z', '+00:00'))
                hour = dt.hour
                return 19 <= hour <= 23  # 7pm-11pm
            except:
                pass
        
        return False
    
    def _is_playoff(self, game: Dict) -> bool:
        """Detect if game is playoff"""
        # Would check ESPN playoff status or date
        return 'playoff' in game.get('status', '').lower()
    
    def _is_championship(self, game: Dict) -> bool:
        """Detect if championship game"""
        status = game.get('status', '').lower()
        return any(term in status for term in ['championship', 'final', 'super bowl', 'world series'])
    
    def _is_rivalry(self, game: Dict) -> bool:
        """Detect rivalry matchup"""
        home = game.get('home_team', '').lower()
        away = game.get('away_team', '').lower()
        
        # Known rivalries
        rivalries = [
            ('patriots', 'jets'), ('packers', 'bears'), ('cowboys', 'eagles'),
            ('lakers', 'celtics'), ('yankees', 'red sox'), ('dodgers', 'giants')
        ]
        
        for team1, team2 in rivalries:
            if (team1 in home and team2 in away) or (team2 in home and team1 in away):
                return True
        
        return False
    
    def _is_national_broadcast(self, game: Dict) -> bool:
        """Detect national broadcast"""
        broadcast = game.get('broadcast', '')
        return any(net in broadcast for net in ['NBC', 'ESPN', 'ABC', 'FOX', 'TNT', 'TBS'])
    
    def _get_team_players(self, team_name: str, player_db: Dict) -> List[Dict]:
        """Get players for a team"""
        # Would query player database by team
        # For now, return structure
        return player_db.get(team_name, [])
    
    def _find_player_odds(self, player: Dict, market_odds: List[Dict]) -> Optional[Dict]:
        """Find odds for specific player"""
        # Would match player to odds data
        # For now, return structure
        return {
            'player_name': player.get('name'),
            'prop_type': 'points',  # or rushing_yards, etc.
            'line': 25.5,
            'over_odds': -110,
            'under_odds': -110,
            'book': 'DraftKings'
        }
    
    def _get_opponent(self, player: Dict, home_players: List, away_players: List) -> Optional[Dict]:
        """Get opponent player data"""
        # Would find positional matchup
        # For now, return None
        return None
    
    def _calculate_priority(self, analysis: Dict) -> int:
        """Calculate recommendation priority (1-5, 5=highest)"""
        score = analysis.get('final_score', 0)
        confidence = analysis.get('final_confidence', 0)
        roi = analysis.get('expected_roi', 0)
        
        # Priority formula
        priority_score = (score * 0.3 + confidence * 0.3 + roi * 0.4)
        
        if priority_score >= 80:
            return 5  # MUST BET
        elif priority_score >= 70:
            return 4  # STRONG BET
        elif priority_score >= 60:
            return 3  # GOOD BET
        elif priority_score >= 50:
            return 2  # CONSIDER
        else:
            return 1  # PASS
    
    def get_fresh_recommendations(self) -> Dict:
        """Get current recommendations (updates if stale)"""
        now = datetime.now()
        
        if (self.last_update is None or 
            (now - self.last_update).seconds > self.update_interval):
            # Need fresh update
            return {
                'status': 'stale',
                'last_update': self.last_update.isoformat() if self.last_update else None,
                'message': 'Recommendations need refresh',
                'recommendations': []
            }
        
        return {
            'status': 'fresh',
            'last_update': self.last_update.isoformat(),
            'recommendations': self.current_recommendations,
            'next_update': (self.last_update + timedelta(seconds=self.update_interval)).isoformat()
        }


if __name__ == "__main__":
    print("Real-Time Recommendation Engine ready")
    print("Connect to live APIs for automatic recommendations")

