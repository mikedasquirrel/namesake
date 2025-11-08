"""MLB Team Collector

Collects MLB team data with 3-layer linguistic analysis:
1. Team Name Linguistics (Yankees, Dodgers, Red Sox)
2. City Name Linguistics (New York, Los Angeles, Boston)
3. Roster Amalgamation (aggregate of all 25 players' name features)

Creates composite linguistic profiles for all 30 MLB teams.
"""

import logging
import json
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional

from core.models import db, MLBTeam, MLBTeamAnalysis, MLBPlayer, MLBPlayerAnalysis
from analyzers.name_analyzer import NameAnalyzer
from analyzers.phonemic_analyzer import PhonemicAnalyzer

logger = logging.getLogger(__name__)


class MLBTeamCollector:
    """Collect and analyze MLB teams with 3-layer linguistic framework."""
    
    def __init__(self):
        """Initialize the collector."""
        self.name_analyzer = NameAnalyzer()
        self.phonemic_analyzer = PhonemicAnalyzer()
        
        # City prestige tiers (based on market size, cultural significance)
        self.city_prestige = {
            'New York': 95,
            'Los Angeles': 92,
            'Chicago': 88,
            'Boston': 87,
            'San Francisco': 85,
            'Philadelphia': 82,
            'Washington': 80,
            'Houston': 78,
            'Atlanta': 76,
            'San Diego': 75,
            'Seattle': 74,
            'St. Louis': 72,
            'Minneapolis': 70,
            'Denver': 68,
            'Phoenix': 67,
            'Detroit': 66,
            'Miami': 65,
            'Toronto': 64,
            'Baltimore': 62,
            'Cincinnati': 60,
            'Cleveland': 59,
            'Milwaukee': 58,
            'Pittsburgh': 57,
            'Kansas City': 55,
            'Tampa Bay': 50,
            'Oakland': 48
        }
        
        # Team name types
        self.team_name_types = {
            'Yankees': 'Regional',
            'Red Sox': 'Color',
            'Dodgers': 'Occupation',
            'Giants': 'Physical',
            'Cubs': 'Animal',
            'White Sox': 'Color',
            'Cardinals': 'Animal',
            'Braves': 'Historical',
            'Tigers': 'Animal',
            'Athletics': 'Occupation',
            'Mets': 'Regional',
            'Pirates': 'Occupation',
            'Phillies': 'Regional',
            'Angels': 'Religious',
            'Astros': 'Scientific',
            'Orioles': 'Animal',
            'Twins': 'Physical',
            'Brewers': 'Occupation',
            'Mariners': 'Occupation',
            'Rays': 'Natural',
            'Royals': 'Historical',
            'Blue Jays': 'Animal',
            'Padres': 'Religious',
            'Rangers': 'Occupation',
            'Guardians': 'Occupation',
            'Diamondbacks': 'Animal',
            'Rockies': 'Natural',
            'Marlins': 'Animal',
            'Nationals': 'Regional',
            'Reds': 'Color'
        }
    
    def analyze_team_name(self, team_name: str) -> Dict:
        """Analyze team name linguistics (Layer 1).
        
        Args:
            team_name: Team name (e.g., "Yankees", "Red Sox")
        
        Returns:
            Dict with team name features
        """
        analysis = {}
        
        # Syllable count
        try:
            analysis['team_name_syllables'] = self.name_analyzer.count_syllables(team_name)
        except:
            analysis['team_name_syllables'] = len(team_name.split()) * 2
        
        analysis['team_name_character_length'] = len(team_name)
        
        # Memorability
        memorability = 50.0
        if analysis['team_name_syllables'] <= 2:
            memorability += 25
        elif analysis['team_name_syllables'] <= 3:
            memorability += 15
        analysis['team_name_memorability'] = min(100, memorability)
        
        # Phonetic features
        try:
            phonetic = self.phonemic_analyzer.analyze(team_name)
            analysis['team_name_harshness'] = phonetic.get('harshness_score', 50.0)
            analysis['team_name_power_score'] = phonetic.get('harshness_score', 50.0)
        except:
            analysis['team_name_harshness'] = 50.0
            analysis['team_name_power_score'] = 50.0
        
        # Prestige (based on historical success associations)
        prestige_map = {
            'Yankees': 95, 'Dodgers': 90, 'Red Sox': 88, 'Cardinals': 85,
            'Giants': 82, 'Braves': 80
        }
        analysis['team_name_prestige'] = prestige_map.get(team_name, 70.0)
        
        # Type classification
        analysis['team_name_type'] = self.team_name_types.get(team_name, 'Other')
        analysis['team_name_semantic_category'] = analysis['team_name_type']
        
        return analysis
    
    def analyze_city_name(self, city: str) -> Dict:
        """Analyze city name linguistics (Layer 2).
        
        Args:
            city: City name (e.g., "New York", "Los Angeles")
        
        Returns:
            Dict with city features
        """
        analysis = {}
        
        # Syllable count
        try:
            analysis['city_syllables'] = self.name_analyzer.count_syllables(city)
        except:
            analysis['city_syllables'] = len(city.split()) * 2
        
        analysis['city_character_length'] = len(city)
        
        # Prestige score (predefined)
        analysis['city_prestige_score'] = self.city_prestige.get(city, 60.0)
        
        # Market tier
        if analysis['city_prestige_score'] >= 85:
            analysis['city_market_tier'] = 'Major'
        elif analysis['city_prestige_score'] >= 70:
            analysis['city_market_tier'] = 'Mid'
        else:
            analysis['city_market_tier'] = 'Small'
        
        # Memorability
        memorability = 60.0
        if analysis['city_syllables'] <= 3:
            memorability += 20
        if city in ['New York', 'Boston', 'Chicago']:
            memorability += 15
        analysis['city_memorability'] = min(100, memorability)
        
        # Phonetic authority
        analysis['city_phonetic_authority'] = analysis['city_prestige_score']  # Correlated
        
        # Vowel ratio
        vowels = sum(1 for c in city.lower() if c in 'aeiou')
        total_letters = sum(1 for c in city if c.isalpha())
        analysis['city_vowel_ratio'] = vowels / total_letters if total_letters > 0 else 0.4
        
        return analysis
    
    def calculate_roster_amalgamation(self, team_id: str) -> Dict:
        """Calculate roster composite features (Layer 3).
        
        Aggregates all players' name features on the team roster.
        
        Args:
            team_id: Team ID
        
        Returns:
            Dict with roster amalgamation features
        """
        # Get all players on team
        players = MLBPlayer.query.filter_by(team_id=team_id).all()
        
        if not players:
            logger.warning(f"No players found for team {team_id}")
            return self._empty_roster_analysis()
        
        # Get analyses
        analyses = []
        for player in players:
            if player.analysis:
                analyses.append(player.analysis)
        
        if not analyses:
            logger.warning(f"No analyzed players for team {team_id}")
            return self._empty_roster_analysis()
        
        roster_data = {}
        
        # Basic aggregates
        roster_data['roster_size'] = len(analyses)
        
        syllables = [a.syllable_count for a in analyses if a.syllable_count]
        if syllables:
            roster_data['roster_mean_syllables'] = float(np.mean(syllables))
            roster_data['roster_syllable_stddev'] = float(np.std(syllables))
            roster_data['roster_max_syllables'] = int(max(syllables))
            roster_data['roster_min_syllables'] = int(min(syllables))
        else:
            roster_data['roster_mean_syllables'] = 3.0
            roster_data['roster_syllable_stddev'] = 0.5
            roster_data['roster_max_syllables'] = 4
            roster_data['roster_min_syllables'] = 2
        
        # Phonetic features
        harshness = [a.harshness_score for a in analyses if a.harshness_score]
        if harshness:
            roster_data['roster_mean_harshness'] = float(np.mean(harshness))
            roster_data['roster_harshest_player'] = float(max(harshness))
            roster_data['roster_softest_player'] = float(min(harshness))
        else:
            roster_data['roster_mean_harshness'] = 50.0
            roster_data['roster_harshest_player'] = 60.0
            roster_data['roster_softest_player'] = 40.0
        
        memorability = [a.memorability_score for a in analyses if a.memorability_score]
        roster_data['roster_mean_memorability'] = float(np.mean(memorability)) if memorability else 50.0
        
        power = [a.power_connotation_score for a in analyses if a.power_connotation_score]
        roster_data['roster_mean_power_score'] = float(np.mean(power)) if power else 50.0
        
        # Roster harmony (low diversity = high harmony)
        if roster_data['roster_syllable_stddev'] > 0:
            harmony = 100 - (roster_data['roster_syllable_stddev'] * 15)
            roster_data['roster_harmony_score'] = max(0, min(100, harmony))
        else:
            roster_data['roster_harmony_score'] = 100.0
        
        # Phonetic diversity
        if harshness:
            roster_data['roster_phonetic_diversity'] = float(np.std(harshness))
        else:
            roster_data['roster_phonetic_diversity'] = 10.0
        
        # International composition
        origins = [a.name_origin for a in analyses if a.name_origin]
        if origins:
            total = len(origins)
            roster_data['roster_latino_percentage'] = (origins.count('Latino') / total) * 100
            roster_data['roster_asian_percentage'] = (origins.count('Asian') / total) * 100
            roster_data['roster_anglo_percentage'] = (origins.count('Anglo') / total) * 100
            roster_data['roster_international_percentage'] = ((origins.count('Latino') + origins.count('Asian')) / total) * 100
        else:
            roster_data['roster_latino_percentage'] = 30.0  # MLB average
            roster_data['roster_asian_percentage'] = 5.0
            roster_data['roster_anglo_percentage'] = 65.0
            roster_data['roster_international_percentage'] = 35.0
        
        return roster_data
    
    def _empty_roster_analysis(self) -> Dict:
        """Return empty roster analysis when no players available."""
        return {
            'roster_size': 0,
            'roster_mean_syllables': 3.0,
            'roster_mean_harshness': 50.0,
            'roster_mean_memorability': 50.0,
            'roster_mean_power_score': 50.0,
            'roster_syllable_stddev': 0.5,
            'roster_harmony_score': 75.0,
            'roster_phonetic_diversity': 10.0,
            'roster_international_percentage': 35.0,
            'roster_anglo_percentage': 65.0,
            'roster_latino_percentage': 30.0,
            'roster_asian_percentage': 5.0,
            'roster_max_syllables': 4,
            'roster_min_syllables': 2,
            'roster_harshest_player': 60.0,
            'roster_softest_player': 40.0
        }
    
    def calculate_composite_scores(self, team_analysis: Dict, city_analysis: Dict, 
                                   roster_analysis: Dict) -> Dict:
        """Calculate composite scores from all 3 layers.
        
        Weighting: Team Name 30%, City 20%, Roster 50%
        
        Args:
            team_analysis: Layer 1 features
            city_analysis: Layer 2 features
            roster_analysis: Layer 3 features
        
        Returns:
            Dict with composite scores
        """
        composite = {}
        
        # Composite linguistic score (weighted sum of key features)
        team_score = (team_analysis['team_name_memorability'] + 
                     team_analysis['team_name_prestige']) / 2
        city_score = (city_analysis['city_prestige_score'] + 
                     city_analysis['city_memorability']) / 2
        roster_score = (roster_analysis['roster_mean_memorability'] + 
                       roster_analysis['roster_harmony_score']) / 2
        
        composite['composite_linguistic_score'] = (
            team_score * 0.30 +
            city_score * 0.20 +
            roster_score * 0.50
        )
        
        # Composite memorability
        composite['composite_memorability'] = (
            team_analysis['team_name_memorability'] * 0.30 +
            city_analysis['city_memorability'] * 0.20 +
            roster_analysis['roster_mean_memorability'] * 0.50
        )
        
        # Composite prestige
        composite['composite_prestige'] = (
            team_analysis['team_name_prestige'] * 0.30 +
            city_analysis['city_prestige_score'] * 0.20 +
            (70.0) * 0.50  # Roster doesn't have prestige, use neutral
        )
        
        # Composite power
        composite['composite_power'] = (
            team_analysis['team_name_power_score'] * 0.30 +
            (60.0) * 0.20 +  # Cities don't have power
            roster_analysis['roster_mean_power_score'] * 0.50
        )
        
        # Composite harmony (team-roster cohesion)
        composite['composite_harmony'] = roster_analysis['roster_harmony_score']
        
        return composite
    
    def collect_all_teams(self) -> Dict:
        """Collect and analyze all 30 MLB teams.
        
        Returns:
            Dict with collection statistics
        """
        logger.info("=== MLB TEAM COLLECTION: 30 Teams ===")
        
        added_count = 0
        errors = 0
        
        # This will be populated by bootstrap script with actual team data
        logger.info("Team collection framework ready")
        logger.info("Run bootstrap_mlb_teams.py to populate all 30 teams")
        
        return {
            'added': added_count,
            'errors': errors,
            'timestamp': datetime.now().isoformat()
        }
    
    def analyze_team_complete(self, team: MLBTeam) -> MLBTeamAnalysis:
        """Perform complete 3-layer analysis for a team.
        
        Args:
            team: MLBTeam model instance
        
        Returns:
            MLBTeamAnalysis instance
        """
        # Layer 1: Team Name
        team_name_analysis = self.analyze_team_name(team.name)
        
        # Layer 2: City Name
        city_analysis = self.analyze_city_name(team.city)
        
        # Layer 3: Roster Amalgamation
        roster_analysis = self.calculate_roster_amalgamation(team.id)
        
        # Composite Scores
        composite_scores = self.calculate_composite_scores(
            team_name_analysis,
            city_analysis,
            roster_analysis
        )
        
        # Combine all layers
        complete_analysis = {
            **team_name_analysis,
            **city_analysis,
            **roster_analysis,
            **composite_scores,
            'team_id': team.id,
            'roster_season': 2024  # Current season
        }
        
        return MLBTeamAnalysis(**complete_analysis)
    
    def get_collection_status(self) -> Dict:
        """Get current collection status.
        
        Returns:
            Dict with counts and statistics
        """
        total_teams = MLBTeam.query.count()
        analyzed_teams = MLBTeamAnalysis.query.count()
        
        # By league
        al_teams = MLBTeam.query.filter_by(league='AL').count()
        nl_teams = MLBTeam.query.filter_by(league='NL').count()
        
        # Top by composite score
        top_teams = db.session.query(MLBTeam, MLBTeamAnalysis).join(
            MLBTeamAnalysis,
            MLBTeam.id == MLBTeamAnalysis.team_id
        ).order_by(MLBTeamAnalysis.composite_linguistic_score.desc()).limit(5).all()
        
        top_names = [team.full_name for team, analysis in top_teams]
        
        return {
            'total_teams': total_teams,
            'analyzed_teams': analyzed_teams,
            'al_teams': al_teams,
            'nl_teams': nl_teams,
            'top_composite_teams': top_names,
            'timestamp': datetime.now().isoformat()
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    collector = MLBTeamCollector()
    status = collector.get_collection_status()
    print(f"MLB Teams Collection Status: {status}")


