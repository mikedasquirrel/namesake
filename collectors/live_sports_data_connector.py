"""
Live Sports Data Connector
Connect to real-time sports data APIs for live betting recommendations
APIs: ESPN, The Odds API, SportsData.io, etc.
"""

import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
import json

logger = logging.getLogger(__name__)


class LiveSportsDataConnector:
    """Connect to live sports data sources"""
    
    def __init__(self, api_keys: Optional[Dict] = None):
        """
        Initialize live connector
        
        Args:
            api_keys: Dict with API keys for various services
                - 'odds_api': The Odds API key
                - 'espn': ESPN API (if needed)
                - 'sportsdata': SportsData.io key
        """
        self.api_keys = api_keys or {}
        self.base_urls = {
            'odds_api': 'https://api.the-odds-api.com/v4',
            'espn': 'http://site.api.espn.com/apis/site/v2/sports',
            'nfl_scores': 'https://site.api.espn.com/apis/site/v2/sports/football/nfl',
            'nba_scores': 'https://site.api.espn.com/apis/site/v2/sports/basketball/nba',
            'mlb_scores': 'https://site.api.espn.com/apis/site/v2/sports/baseball/mlb'
        }
        
        # Free APIs (no key needed)
        self.free_apis = ['espn', 'nfl_scores', 'nba_scores', 'mlb_scores']
    
    def get_todays_games(self, sport: str) -> List[Dict]:
        """
        Get today's games for a sport (uses free ESPN API)
        
        Args:
            sport: 'football', 'basketball', or 'baseball'
            
        Returns:
            List of today's games
        """
        sport_map = {
            'football': 'nfl_scores',
            'basketball': 'nba_scores',
            'baseball': 'mlb_scores'
        }
        
        api_key = sport_map.get(sport)
        if not api_key:
            return []
        
        try:
            url = f"{self.base_urls[api_key]}/scoreboard"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                games = self._parse_espn_scoreboard(data)
                logger.info(f"Loaded {len(games)} {sport} games from ESPN")
                return games
            else:
                logger.warning(f"ESPN API returned {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching games: {e}")
            return []
    
    def _parse_espn_scoreboard(self, data: Dict) -> List[Dict]:
        """Parse ESPN scoreboard JSON"""
        games = []
        
        events = data.get('events', [])
        
        for event in events:
            competitions = event.get('competitions', [])
            if not competitions:
                continue
            
            comp = competitions[0]
            competitors = comp.get('competitors', [])
            
            if len(competitors) >= 2:
                home_team = next((c for c in competitors if c.get('homeAway') == 'home'), None)
                away_team = next((c for c in competitors if c.get('homeAway') == 'away'), None)
                
                if home_team and away_team:
                    game_data = {
                        'game_id': event.get('id'),
                        'home_team': home_team.get('team', {}).get('displayName'),
                        'away_team': away_team.get('team', {}).get('displayName'),
                        'home_score': home_team.get('score'),
                        'away_score': away_team.get('score'),
                        'status': comp.get('status', {}).get('type', {}).get('name'),
                        'is_live': comp.get('status', {}).get('type', {}).get('state') == 'in',
                        'date': event.get('date'),
                        'venue': comp.get('venue', {}).get('fullName'),
                        'broadcast': comp.get('broadcasts', [{}])[0].get('names', [''])[0] if comp.get('broadcasts') else None
                    }
                    games.append(game_data)
        
        return games
    
    def get_betting_odds(self, sport: str, market: str = 'h2h') -> List[Dict]:
        """
        Get betting odds from The Odds API (requires API key)
        
        Args:
            sport: Sport key ('americanfootball_nfl', 'basketball_nba', etc.)
            market: Market type ('h2h', 'spreads', 'totals', 'player_props')
            
        Returns:
            List of odds for games
        """
        odds_api_key = self.api_keys.get('odds_api')
        
        if not odds_api_key:
            logger.warning("The Odds API key not provided - using mock data")
            return self._get_mock_odds(sport)
        
        try:
            url = f"{self.base_urls['odds_api']}/sports/{sport}/odds/"
            params = {
                'apiKey': odds_api_key,
                'regions': 'us',
                'markets': market,
                'oddsFormat': 'american'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Loaded odds for {len(data)} games")
                return data
            else:
                logger.warning(f"Odds API returned {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching odds: {e}")
            return []
    
    def _get_mock_odds(self, sport: str) -> List[Dict]:
        """Generate mock odds for demonstration"""
        # In production, this would be replaced with real API data
        mock_games = [
            {
                'home_team': 'Team A',
                'away_team': 'Team B',
                'home_odds': -150,
                'away_odds': 130,
                'spread_home': -3.5,
                'spread_odds': -110,
                'total': 47.5,
                'over_odds': -110,
                'under_odds': -110
            }
        ]
        
        logger.info("Using mock odds data (API key not provided)")
        return mock_games
    
    def get_player_props(self, sport: str, player_name: str) -> List[Dict]:
        """
        Get player prop lines (requires premium API or web scraping)
        
        Args:
            sport: Sport type
            player_name: Player name
            
        Returns:
            Available prop bets for player
        """
        # This would integrate with odds providers
        # For now, return structure for manual entry
        
        return {
            'player_name': player_name,
            'sport': sport,
            'available_props': [
                {
                    'prop_type': 'points',  # or 'rushing_yards', 'strikeouts', etc.
                    'line': 0,  # To be filled
                    'over_odds': -110,
                    'under_odds': -110,
                    'book': 'DraftKings'  # Which sportsbook
                }
            ],
            'note': 'Manual entry required or connect to premium API'
        }
    
    def get_live_scores(self, sport: str) -> List[Dict]:
        """Get live scores during games"""
        return self.get_todays_games(sport)
    
    def get_season_schedule(self, sport: str, year: int) -> List[Dict]:
        """
        Get full season schedule (for historical analysis)
        
        Args:
            sport: Sport type
            year: Season year
            
        Returns:
            Season schedule
        """
        sport_map = {
            'football': f"football/nfl/scoreboard?dates={year}",
            'basketball': f"basketball/nba/scoreboard?dates={year}",
            'baseball': f"baseball/mlb/scoreboard?dates={year}"
        }
        
        # Would query ESPN for full season
        # For now, return structure
        
        return {
            'sport': sport,
            'year': year,
            'note': 'Full season data available via ESPN API iteration'
        }


if __name__ == "__main__":
    # Test live connector
    connector = LiveSportsDataConnector()
    
    print("="*80)
    print("LIVE SPORTS DATA CONNECTOR")
    print("="*80)
    
    # Test getting today's games
    for sport in ['football', 'basketball', 'baseball']:
        print(f"\n{sport.upper()} - Today's Games:")
        print("-" * 80)
        
        games = connector.get_todays_games(sport)
        
        if games:
            for i, game in enumerate(games[:3], 1):
                print(f"{i}. {game['away_team']} @ {game['home_team']}")
                print(f"   Status: {game['status']}")
                if game.get('broadcast'):
                    print(f"   Broadcast: {game['broadcast']}")
        else:
            print("  No games today or API unavailable")
    
    print("\n" + "="*80)
    print("✅ LIVE CONNECTOR READY")
    print("="*80)
    print("\nFor full functionality, provide API keys:")
    print("  - The Odds API: https://the-odds-api.com (free tier: 500 requests/month)")
    print("  - ESPN API: Free, no key needed")

