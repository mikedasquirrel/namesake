"""
Media Attention Analyzer
Track real-time media buzz and popularity metrics
Theory: Actual mentions > theoretical memorability
Expected Impact: +4-6% ROI
"""

import logging
from typing import Dict, Optional
import math

logger = logging.getLogger(__name__)


class MediaAttentionAnalyzer:
    """Analyze media attention and popularity metrics"""
    
    def __init__(self):
        """Initialize analyzer"""
        self.market_sizes = self._load_market_sizes()
    
    def _load_market_sizes(self) -> Dict:
        """Load market size multipliers"""
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
            'Minneapolis': 1.15,
            'Tampa': 1.15,
            'Portland': 1.1,
            'Las Vegas': 1.2,
            'Nashville': 1.1,
            'Austin': 1.15,
            # Smaller markets
            'Green Bay': 0.9,
            'Buffalo': 0.95,
            'Jacksonville': 0.9,
            'Sacramento': 1.0,
            'Milwaukee': 1.05,
            'Cincinnati': 1.0,
            'Cleveland': 1.05,
            'Pittsburgh': 1.1,
            'Kansas City': 1.0,
            'Indianapolis': 1.0,
            'Columbus': 1.05,
            # Default
            'default': 1.0
        }
    
    def get_google_trends_score(self, player_name: str, timeframe: str = 'now 7-d') -> Optional[float]:
        """
        Get Google Trends score for a player
        Returns None if pytrends not available (graceful degradation)
        
        Args:
            player_name: Player name to search
            timeframe: Time range for trends
            
        Returns:
            Normalized score 0-100 or None
        """
        try:
            from pytrends.request import TrendReq
            
            pytrends = TrendReq(hl='en-US', tz=360)
            pytrends.build_payload([player_name], timeframe=timeframe)
            trend_data = pytrends.interest_over_time()
            
            if trend_data.empty or player_name not in trend_data.columns:
                return None
            
            # Get average interest over time period
            avg_interest = trend_data[player_name].mean()
            
            return float(avg_interest)
            
        except ImportError:
            logger.info("pytrends not installed, skipping Google Trends analysis")
            return None
        except Exception as e:
            logger.warning(f"Error getting Google Trends data: {e}")
            return None
    
    def get_market_size_multiplier(self, team_city: str) -> float:
        """
        Get market size multiplier for team's city
        
        Args:
            team_city: City name
            
        Returns:
            Multiplier (0.9 - 1.5)
        """
        return self.market_sizes.get(team_city, self.market_sizes['default'])
    
    def estimate_media_buzz(self, player_name: str, team_city: Optional[str] = None,
                           recent_performance: Optional[str] = None) -> Dict:
        """
        Estimate overall media buzz for a player
        
        Args:
            player_name: Player name
            team_city: Team's city (for market size proxy)
            recent_performance: 'hot', 'cold', or None
            
        Returns:
            Media buzz analysis
        """
        # Try Google Trends first
        trends_score = self.get_google_trends_score(player_name)
        
        # Market size proxy
        market_multiplier = 1.0
        if team_city:
            market_multiplier = self.get_market_size_multiplier(team_city)
        
        # Performance buzz
        performance_multiplier = 1.0
        if recent_performance == 'hot':
            performance_multiplier = 1.3
        elif recent_performance == 'cold':
            performance_multiplier = 0.8
        
        # Calculate composite buzz score
        if trends_score is not None:
            # Have actual data, weight it heavily
            base_buzz = trends_score
            method = 'google_trends'
        else:
            # Use proxies
            base_buzz = 50  # Baseline
            method = 'market_proxy'
        
        # Apply multipliers
        adjusted_buzz = base_buzz * market_multiplier * performance_multiplier
        adjusted_buzz = min(adjusted_buzz, 100)  # Cap at 100
        
        return {
            'player_name': player_name,
            'buzz_score': round(adjusted_buzz, 2),
            'method': method,
            'components': {
                'base_score': round(base_buzz, 2) if trends_score is not None else None,
                'market_multiplier': round(market_multiplier, 2),
                'performance_multiplier': round(performance_multiplier, 2)
            },
            'team_city': team_city,
            'market_size_tier': self._get_market_tier(market_multiplier)
        }
    
    def _get_market_tier(self, multiplier: float) -> str:
        """Classify market size tier"""
        if multiplier >= 1.3:
            return 'LARGE'
        elif multiplier >= 1.1:
            return 'MEDIUM'
        elif multiplier >= 0.95:
            return 'SMALL'
        else:
            return 'TINY'
    
    def adjust_memorability_for_buzz(self, base_memorability: float, 
                                    buzz_score: float) -> Dict:
        """
        Adjust theoretical memorability based on actual media buzz
        Formula: adjusted = base × (1 + log(buzz) / 10)
        
        Args:
            base_memorability: Theoretical memorability score
            buzz_score: Media buzz score (0-100)
            
        Returns:
            Adjusted memorability with breakdown
        """
        if buzz_score <= 0:
            buzz_adjustment = 0
        else:
            # Log scale to prevent extreme adjustments
            buzz_adjustment = math.log(buzz_score + 1) / 10
        
        adjusted_memorability = base_memorability * (1 + buzz_adjustment)
        adjusted_memorability = min(adjusted_memorability, 100)  # Cap at 100
        
        return {
            'base_memorability': round(base_memorability, 2),
            'buzz_score': round(buzz_score, 2),
            'buzz_adjustment': round(buzz_adjustment, 3),
            'adjusted_memorability': round(adjusted_memorability, 2),
            'boost_percentage': round((adjusted_memorability - base_memorability) / base_memorability * 100, 1)
        }
    
    def get_fantasy_ownership_proxy(self, player_tier: str) -> float:
        """
        Estimate fantasy ownership as popularity proxy
        
        Args:
            player_tier: 'elite', 'starter', 'flex', 'bench', 'deep'
            
        Returns:
            Estimated ownership percentage
        """
        ownership_map = {
            'elite': 90,      # Stars owned everywhere
            'starter': 60,    # Solid starters
            'flex': 35,       # Flex plays
            'bench': 15,      # Bench stashes
            'deep': 5         # Deep league only
        }
        
        return ownership_map.get(player_tier, 25)
    
    def analyze_name_hype_vs_substance(self, linguistic_features: Dict,
                                      buzz_score: float) -> Dict:
        """
        Detect when high buzz doesn't match name quality (overvalued)
        Or low buzz with strong name quality (undervalued)
        
        Args:
            linguistic_features: Name linguistic features
            buzz_score: Media buzz score
            
        Returns:
            Hype analysis
        """
        # Calculate name quality composite
        harshness = linguistic_features.get('harshness', 50)
        memorability = linguistic_features.get('memorability', 50)
        name_quality = (harshness + memorability) / 2
        
        # Compare to buzz
        hype_differential = buzz_score - name_quality
        
        # Classify
        if hype_differential > 20:
            classification = 'OVERHYPED'
            betting_signal = 'FADE'
            reasoning = 'High buzz but weak name fundamentals'
        elif hype_differential < -20:
            classification = 'UNDERHYPED'
            betting_signal = 'TARGET'
            reasoning = 'Strong name quality but low buzz (value play)'
        else:
            classification = 'FAIR VALUE'
            betting_signal = 'NEUTRAL'
            reasoning = 'Buzz matches name quality'
        
        return {
            'name_quality': round(name_quality, 2),
            'buzz_score': round(buzz_score, 2),
            'hype_differential': round(hype_differential, 2),
            'classification': classification,
            'betting_signal': betting_signal,
            'reasoning': reasoning
        }


if __name__ == "__main__":
    # Test media attention analyzer
    logging.basicConfig(level=logging.INFO)
    
    analyzer = MediaAttentionAnalyzer()
    
    # Test market multiplier
    print("=== MARKET SIZE MULTIPLIERS ===")
    cities = ['New York', 'Los Angeles', 'Green Bay', 'Buffalo']
    for city in cities:
        mult = analyzer.get_market_size_multiplier(city)
        print(f"{city}: {mult}x")
    
    # Test buzz estimation
    print("\n=== MEDIA BUZZ ESTIMATION ===")
    buzz = analyzer.estimate_media_buzz(
        player_name="Patrick Mahomes",
        team_city="Kansas City",
        recent_performance="hot"
    )
    print(f"Player: {buzz['player_name']}")
    print(f"Buzz Score: {buzz['buzz_score']}")
    print(f"Method: {buzz['method']}")
    print(f"Market Tier: {buzz['market_size_tier']}")
    
    # Test memorability adjustment
    print("\n=== MEMORABILITY ADJUSTMENT ===")
    adjusted = analyzer.adjust_memorability_for_buzz(
        base_memorability=70,
        buzz_score=85
    )
    print(f"Base: {adjusted['base_memorability']}")
    print(f"Adjusted: {adjusted['adjusted_memorability']}")
    print(f"Boost: +{adjusted['boost_percentage']}%")
    
    # Test hype analysis
    print("\n=== HYPE VS SUBSTANCE ===")
    hype_analysis = analyzer.analyze_name_hype_vs_substance(
        linguistic_features={'harshness': 65, 'memorability': 85},
        buzz_score=90
    )
    print(f"Classification: {hype_analysis['classification']}")
    print(f"Signal: {hype_analysis['betting_signal']}")
    print(f"Reasoning: {hype_analysis['reasoning']}")

