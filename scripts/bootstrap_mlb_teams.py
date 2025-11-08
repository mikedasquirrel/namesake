"""Bootstrap MLB Teams Data

Creates all 30 MLB teams with complete 3-layer analysis:
- Layer 1: Team name linguistics
- Layer 2: City name linguistics  
- Layer 3: Roster amalgamation (using existing 44 players)
"""

import logging
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from core.models import MLBTeam, MLBTeamAnalysis, MLBPlayer
from collectors.mlb_team_collector import MLBTeamCollector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# All 30 MLB Teams (2024 season)
MLB_TEAMS_DATA = [
    # AL East
    {'id': 'NYY', 'name': 'Yankees', 'city': 'New York', 'state': 'NY', 'league': 'AL', 'division': 'AL East', 'founded': 1901, 'ws_titles': 27, 'wins': 95, 'losses': 67},
    {'id': 'BOS', 'name': 'Red Sox', 'city': 'Boston', 'state': 'MA', 'league': 'AL', 'division': 'AL East', 'founded': 1901, 'ws_titles': 9, 'wins': 78, 'losses': 84},
    {'id': 'TB', 'name': 'Rays', 'city': 'Tampa Bay', 'state': 'FL', 'league': 'AL', 'division': 'AL East', 'founded': 1998, 'ws_titles': 0, 'wins': 80, 'losses': 82},
    {'id': 'TOR', 'name': 'Blue Jays', 'city': 'Toronto', 'state': 'ON', 'league': 'AL', 'division': 'AL East', 'founded': 1977, 'ws_titles': 2, 'wins': 74, 'losses': 88},
    {'id': 'BAL', 'name': 'Orioles', 'city': 'Baltimore', 'state': 'MD', 'league': 'AL', 'division': 'AL East', 'founded': 1901, 'ws_titles': 3, 'wins': 91, 'losses': 71},
    
    # AL Central
    {'id': 'CLE', 'name': 'Guardians', 'city': 'Cleveland', 'state': 'OH', 'league': 'AL', 'division': 'AL Central', 'founded': 1901, 'ws_titles': 2, 'wins': 92, 'losses': 69},
    {'id': 'MIN', 'name': 'Twins', 'city': 'Minneapolis', 'state': 'MN', 'league': 'AL', 'division': 'AL Central', 'founded': 1901, 'ws_titles': 3, 'wins': 82, 'losses': 80},
    {'id': 'KC', 'name': 'Royals', 'city': 'Kansas City', 'state': 'MO', 'league': 'AL', 'division': 'AL Central', 'founded': 1969, 'ws_titles': 2, 'wins': 56, 'losses': 106},
    {'id': 'DET', 'name': 'Tigers', 'city': 'Detroit', 'state': 'MI', 'league': 'AL', 'division': 'AL Central', 'founded': 1901, 'ws_titles': 4, 'wins': 77, 'losses': 85},
    {'id': 'CWS', 'name': 'White Sox', 'city': 'Chicago', 'state': 'IL', 'league': 'AL', 'division': 'AL Central', 'founded': 1901, 'ws_titles': 3, 'wins': 41, 'losses': 121},
    
    # AL West
    {'id': 'HOU', 'name': 'Astros', 'city': 'Houston', 'state': 'TX', 'league': 'AL', 'division': 'AL West', 'founded': 1962, 'ws_titles': 2, 'wins': 88, 'losses': 73},
    {'id': 'SEA', 'name': 'Mariners', 'city': 'Seattle', 'state': 'WA', 'league': 'AL', 'division': 'AL West', 'founded': 1977, 'ws_titles': 0, 'wins': 85, 'losses': 77},
    {'id': 'TEX', 'name': 'Rangers', 'city': 'Texas', 'state': 'TX', 'league': 'AL', 'division': 'AL West', 'founded': 1961, 'ws_titles': 1, 'wins': 78, 'losses': 84},
    {'id': 'LAA', 'name': 'Angels', 'city': 'Los Angeles', 'state': 'CA', 'league': 'AL', 'division': 'AL West', 'founded': 1961, 'ws_titles': 1, 'wins': 63, 'losses': 99},
    {'id': 'OAK', 'name': 'Athletics', 'city': 'Oakland', 'state': 'CA', 'league': 'AL', 'division': 'AL West', 'founded': 1901, 'ws_titles': 9, 'wins': 69, 'losses': 93},
    
    # NL East
    {'id': 'ATL', 'name': 'Braves', 'city': 'Atlanta', 'state': 'GA', 'league': 'NL', 'division': 'NL East', 'founded': 1871, 'ws_titles': 4, 'wins': 89, 'losses': 73},
    {'id': 'PHI', 'name': 'Phillies', 'city': 'Philadelphia', 'state': 'PA', 'league': 'NL', 'division': 'NL East', 'founded': 1883, 'ws_titles': 2, 'wins': 95, 'losses': 67},
    {'id': 'NYM', 'name': 'Mets', 'city': 'New York', 'state': 'NY', 'league': 'NL', 'division': 'NL East', 'founded': 1962, 'ws_titles': 2, 'wins': 89, 'losses': 73},
    {'id': 'MIA', 'name': 'Marlins', 'city': 'Miami', 'state': 'FL', 'league': 'NL', 'division': 'NL East', 'founded': 1993, 'ws_titles': 2, 'wins': 62, 'losses': 100},
    {'id': 'WSH', 'name': 'Nationals', 'city': 'Washington', 'state': 'DC', 'league': 'NL', 'division': 'NL East', 'founded': 1969, 'ws_titles': 1, 'wins': 71, 'losses': 91},
    
    # NL Central
    {'id': 'MIL', 'name': 'Brewers', 'city': 'Milwaukee', 'state': 'WI', 'league': 'NL', 'division': 'NL Central', 'founded': 1969, 'ws_titles': 0, 'wins': 93, 'losses': 69},
    {'id': 'CHC', 'name': 'Cubs', 'city': 'Chicago', 'state': 'IL', 'league': 'NL', 'division': 'NL Central', 'founded': 1876, 'ws_titles': 3, 'wins': 83, 'losses': 79},
    {'id': 'STL', 'name': 'Cardinals', 'city': 'St. Louis', 'state': 'MO', 'league': 'NL', 'division': 'NL Central', 'founded': 1882, 'ws_titles': 11, 'wins': 83, 'losses': 79},
    {'id': 'CIN', 'name': 'Reds', 'city': 'Cincinnati', 'state': 'OH', 'league': 'NL', 'division': 'NL Central', 'founded': 1882, 'ws_titles': 5, 'wins': 77, 'losses': 85},
    {'id': 'PIT', 'name': 'Pirates', 'city': 'Pittsburgh', 'state': 'PA', 'league': 'NL', 'division': 'NL Central', 'founded': 1882, 'ws_titles': 5, 'wins': 76, 'losses': 86},
    
    # NL West
    {'id': 'LAD', 'name': 'Dodgers', 'city': 'Los Angeles', 'state': 'CA', 'league': 'NL', 'division': 'NL West', 'founded': 1883, 'ws_titles': 7, 'wins': 98, 'losses': 64},
    {'id': 'SD', 'name': 'Padres', 'city': 'San Diego', 'state': 'CA', 'league': 'NL', 'division': 'NL West', 'founded': 1969, 'ws_titles': 0, 'wins': 93, 'losses': 69},
    {'id': 'ARI', 'name': 'Diamondbacks', 'city': 'Phoenix', 'state': 'AZ', 'league': 'NL', 'division': 'NL West', 'founded': 1998, 'ws_titles': 1, 'wins': 89, 'losses': 73},
    {'id': 'SF', 'name': 'Giants', 'city': 'San Francisco', 'state': 'CA', 'league': 'NL', 'division': 'NL West', 'founded': 1883, 'ws_titles': 8, 'wins': 80, 'losses': 82},
    {'id': 'COL', 'name': 'Rockies', 'city': 'Denver', 'state': 'CO', 'league': 'NL', 'division': 'NL West', 'founded': 1993, 'ws_titles': 0, 'wins': 61, 'losses': 101},
]


def bootstrap_teams():
    """Insert all 30 MLB teams with 3-layer analysis."""
    with app.app_context():
        db.create_all()
        logger.info("✅ Database tables created")
        
        collector = MLBTeamCollector()
        
        added_count = 0
        for team_data in MLB_TEAMS_DATA:
            # Check if exists
            existing = MLBTeam.query.filter_by(id=team_data['id']).first()
            if existing:
                logger.debug(f"Team exists: {team_data['name']}")
                continue
            
            # Create team
            team = MLBTeam(
                id=team_data['id'],
                name=team_data['name'],
                full_name=f"{team_data['city']} {team_data['name']}",
                city=team_data['city'],
                state=team_data['state'],
                league=team_data['league'],
                division=team_data['division'],
                founded_year=team_data['founded'],
                wins_season=team_data['wins'],
                losses_season=team_data['losses'],
                win_percentage=team_data['wins'] / (team_data['wins'] + team_data['losses']),
                world_series_titles=team_data['ws_titles'],
                playoff_appearances=team_data['ws_titles'] * 2,  # Rough estimate
                market_size_rank=15  # Placeholder
            )
            
            db.session.add(team)
            db.session.flush()
            
            # Perform 3-layer analysis
            analysis = collector.analyze_team_complete(team)
            db.session.add(analysis)
            
            added_count += 1
            logger.info(f"✅ Added: {team.full_name} (composite: {analysis.composite_linguistic_score:.1f})")
        
        db.session.commit()
        
        logger.info(f"\n🎉 Bootstrap complete: {added_count} teams added")
        
        # Show summary
        total = MLBTeam.query.count()
        logger.info(f"\n⚾ Total MLB teams: {total}")
        
        # By league
        al = MLBTeam.query.filter_by(league='AL').count()
        nl = MLBTeam.query.filter_by(league='NL').count()
        logger.info(f"   AL: {al}")
        logger.info(f"   NL: {nl}")
        
        # Top 5 by composite score
        logger.info(f"\n🏆 Top 5 by Composite Linguistic Score:")
        top_teams = db.session.query(MLBTeam, MLBTeamAnalysis).join(
            MLBTeamAnalysis,
            MLBTeam.id == MLBTeamAnalysis.team_id
        ).order_by(MLBTeamAnalysis.composite_linguistic_score.desc()).limit(5).all()
        
        for team, analysis in top_teams:
            logger.info(f"   {team.full_name}: {analysis.composite_linguistic_score:.1f} (Win%: {team.win_percentage:.3f})")
        
        # City prestige hierarchy
        logger.info(f"\n🌆 Top 5 by City Prestige:")
        top_cities = db.session.query(MLBTeam, MLBTeamAnalysis).join(
            MLBTeamAnalysis,
            MLBTeam.id == MLBTeamAnalysis.team_id
        ).order_by(MLBTeamAnalysis.city_prestige_score.desc()).limit(5).all()
        
        for team, analysis in top_cities:
            logger.info(f"   {team.city}: {analysis.city_prestige_score:.1f}")


if __name__ == "__main__":
    bootstrap_teams()

