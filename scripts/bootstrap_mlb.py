"""Bootstrap MLB Data

Creates initial dataset with famous MLB players for immediate visual demonstration.
Covers all position groups, eras, and includes power hitters, pitchers (SP/RP/CL).
"""

import logging
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from core.models import MLBPlayer, MLBPlayerAnalysis
from collectors.mlb_collector import MLBCollector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Curated list of legendary MLB players across positions, eras, and styles
BOOTSTRAP_PLAYERS = [
    # LEGENDARY PITCHERS - Starters
    {'name': 'Sandy Koufax', 'id': 'koufasa01', 'position': 'P', 'group': 'Pitcher', 'role': 'SP', 'debut': 1955, 'wins': 165, 'era': 2.76, 'strikeouts': 2396, 'country': 'US', 'hof': True},
    {'name': 'Randy Johnson', 'id': 'johnsr05', 'position': 'P', 'group': 'Pitcher', 'role': 'SP', 'debut': 1988, 'wins': 303, 'era': 3.29, 'strikeouts': 4875, 'country': 'US', 'hof': True},
    {'name': 'Pedro Martinez', 'id': 'martipe02', 'position': 'P', 'group': 'Pitcher', 'role': 'SP', 'debut': 1992, 'wins': 219, 'era': 2.93, 'strikeouts': 3154, 'country': 'DR', 'hof': True},
    {'name': 'Clayton Kershaw', 'id': 'kershcl01', 'position': 'P', 'group': 'Pitcher', 'role': 'SP', 'debut': 2008, 'wins': 210, 'era': 2.48, 'strikeouts': 2908, 'country': 'US', 'hof': False},
    {'name': 'Greg Maddux', 'id': 'maddugr01', 'position': 'P', 'group': 'Pitcher', 'role': 'SP', 'debut': 1986, 'wins': 355, 'era': 3.16, 'strikeouts': 3371, 'country': 'US', 'hof': True},
    {'name': 'Roger Clemens', 'id': 'clemero02', 'position': 'P', 'group': 'Pitcher', 'role': 'SP', 'debut': 1984, 'wins': 354, 'era': 3.12, 'strikeouts': 4672, 'country': 'US', 'hof': False},
    {'name': 'Nolan Ryan', 'id': 'ryanno01', 'position': 'P', 'group': 'Pitcher', 'role': 'SP', 'debut': 1966, 'wins': 324, 'era': 3.19, 'strikeouts': 5714, 'country': 'US', 'hof': True},
    
    # CLOSERS - Shorter names hypothesis
    {'name': 'Mariano Rivera', 'id': 'riverma01', 'position': 'P', 'group': 'Pitcher', 'role': 'CL', 'debut': 1995, 'saves': 652, 'era': 2.21, 'strikeouts': 1173, 'country': 'PA', 'hof': True},
    {'name': 'Trevor Hoffman', 'id': 'hoffmtr01', 'position': 'P', 'group': 'Pitcher', 'role': 'CL', 'debut': 1993, 'saves': 601, 'era': 2.87, 'strikeouts': 1133, 'country': 'US', 'hof': True},
    {'name': 'Lee Smith', 'id': 'smithle02', 'position': 'P', 'group': 'Pitcher', 'role': 'CL', 'debut': 1980, 'saves': 478, 'era': 3.03, 'strikeouts': 1251, 'country': 'US', 'hof': True},
    {'name': 'Dennis Eckersley', 'id': 'eckerde01', 'position': 'P', 'group': 'Pitcher', 'role': 'CL', 'debut': 1975, 'saves': 390, 'era': 3.50, 'strikeouts': 2401, 'country': 'US', 'hof': True},
    
    # POWER HITTERS - Harsh names hypothesis
    {'name': 'Babe Ruth', 'id': 'ruthba01', 'position': 'RF', 'group': 'Outfield', 'debut': 1914, 'hr': 714, 'ba': .342, 'ops': 1.164, 'country': 'US', 'hof': True},
    {'name': 'Hank Aaron', 'id': 'aaronha01', 'position': 'RF', 'group': 'Outfield', 'debut': 1954, 'hr': 755, 'ba': .305, 'ops': .928, 'country': 'US', 'hof': True},
    {'name': 'Barry Bonds', 'id': 'bondsba01', 'position': 'LF', 'group': 'Outfield', 'debut': 1986, 'hr': 762, 'ba': .298, 'ops': 1.051, 'country': 'US', 'hof': False},
    {'name': 'Mark McGwire', 'id': 'mcgwima01', 'position': '1B', 'group': 'Infield', 'debut': 1986, 'hr': 583, 'ba': .263, 'ops': .982, 'country': 'US', 'hof': False},
    {'name': 'Giancarlo Stanton', 'id': 'stantmi03', 'position': 'RF', 'group': 'Outfield', 'debut': 2010, 'hr': 429, 'ba': .266, 'ops': .868, 'country': 'US', 'hof': False},
    
    # CONTACT HITTERS - Softer names
    {'name': 'Tony Gwynn', 'id': 'gwynnto01', 'position': 'RF', 'group': 'Outfield', 'debut': 1982, 'hr': 135, 'ba': .338, 'ops': .847, 'country': 'US', 'hof': True},
    {'name': 'Wade Boggs', 'id': 'boggswa01', 'position': '3B', 'group': 'Infield', 'debut': 1982, 'hr': 118, 'ba': .328, 'ops': .858, 'country': 'US', 'hof': True},
    {'name': 'Rod Carew', 'id': 'carewro01', 'position': '2B', 'group': 'Infield', 'debut': 1967, 'hr': 92, 'ba': .328, 'ops': .822, 'country': 'PA', 'hof': True},
    
    # MODERN STARS
    {'name': 'Mike Trout', 'id': 'troutmi01', 'position': 'CF', 'group': 'Outfield', 'debut': 2011, 'hr': 376, 'ba': .303, 'ops': 1.000, 'country': 'US', 'hof': False},
    {'name': 'Mookie Betts', 'id': 'bettsmo01', 'position': 'RF', 'group': 'Outfield', 'debut': 2014, 'hr': 247, 'ba': .295, 'ops': .883, 'country': 'US', 'hof': False},
    {'name': 'Aaron Judge', 'id': 'judgeaa01', 'position': 'RF', 'group': 'Outfield', 'debut': 2016, 'hr': 282, 'ba': .276, 'ops': .959, 'country': 'US', 'hof': False},
    
    # INFIELD LEGENDS
    {'name': 'Derek Jeter', 'id': 'jeterde01', 'position': 'SS', 'group': 'Infield', 'debut': 1995, 'hr': 260, 'ba': .310, 'ops': .817, 'country': 'US', 'hof': True},
    {'name': 'Cal Ripken Jr', 'id': 'ripkeca01', 'position': 'SS', 'group': 'Infield', 'debut': 1981, 'hr': 431, 'ba': .276, 'ops': .788, 'country': 'US', 'hof': True},
    {'name': 'Mike Schmidt', 'id': 'schmimi01', 'position': '3B', 'group': 'Infield', 'debut': 1972, 'hr': 548, 'ba': .267, 'ops': .908, 'country': 'US', 'hof': True},
    {'name': 'Ozzie Smith', 'id': 'smithoz01', 'position': 'SS', 'group': 'Infield', 'debut': 1978, 'hr': 28, 'ba': .262, 'ops': .666, 'country': 'US', 'hof': True},
    
    # CATCHERS
    {'name': 'Johnny Bench', 'id': 'benchjo01', 'position': 'C', 'group': 'Catcher', 'debut': 1967, 'hr': 389, 'ba': .267, 'ops': .817, 'country': 'US', 'hof': True},
    {'name': 'Yogi Berra', 'id': 'berrayo01', 'position': 'C', 'group': 'Catcher', 'debut': 1946, 'hr': 358, 'ba': .285, 'ops': .830, 'country': 'US', 'hof': True},
    {'name': 'Mike Piazza', 'id': 'piazzmi01', 'position': 'C', 'group': 'Catcher', 'debut': 1992, 'hr': 427, 'ba': .308, 'ops': .922, 'country': 'US', 'hof': True},
    {'name': 'Ivan Rodriguez', 'id': 'rodriiv01', 'position': 'C', 'group': 'Catcher', 'debut': 1991, 'hr': 311, 'ba': .296, 'ops': .798, 'country': 'PR', 'hof': True},
    
    # LATINO STARS - Internationalization hypothesis
    {'name': 'Roberto Clemente', 'id': 'clemero01', 'position': 'RF', 'group': 'Outfield', 'debut': 1955, 'hr': 240, 'ba': .317, 'ops': .834, 'country': 'PR', 'hof': True},
    {'name': 'Fernando Valenzuela', 'id': 'valenfernandez01', 'position': 'P', 'group': 'Pitcher', 'role': 'SP', 'debut': 1980, 'wins': 173, 'era': 3.54, 'strikeouts': 2074, 'country': 'MX', 'hof': False},
    {'name': 'Vladimir Guerrero', 'id': 'guerrvl01', 'position': 'RF', 'group': 'Outfield', 'debut': 1996, 'hr': 449, 'ba': .318, 'ops': .931, 'country': 'DR', 'hof': True},
    {'name': 'Albert Pujols', 'id': 'pujolal01', 'position': '1B', 'group': 'Infield', 'debut': 2001, 'hr': 703, 'ba': .297, 'ops': .916, 'country': 'DR', 'hof': False},
    
    # ASIAN STARS
    {'name': 'Ichiro Suzuki', 'id': 'suzukic01', 'position': 'RF', 'group': 'Outfield', 'debut': 2001, 'hr': 117, 'ba': .311, 'ops': .757, 'country': 'JP', 'hof': True},
    {'name': 'Shohei Ohtani', 'id': 'ohtansh01', 'position': 'P', 'group': 'Pitcher', 'role': 'SP', 'debut': 2018, 'hr': 171, 'ba': .274, 'ops': .925, 'wins': 38, 'strikeouts': 608, 'country': 'JP', 'hof': False},
    {'name': 'Hideki Matsui', 'id': 'matsuhi01', 'position': 'LF', 'group': 'Outfield', 'debut': 2003, 'hr': 175, 'ba': .282, 'ops': .817, 'country': 'JP', 'hof': False},
    
    # ADDITIONAL LEGENDS
    {'name': 'Willie Mays', 'id': 'mayswi01', 'position': 'CF', 'group': 'Outfield', 'debut': 1951, 'hr': 660, 'ba': .302, 'ops': .941, 'country': 'US', 'hof': True},
    {'name': 'Ted Williams', 'id': 'willia02', 'position': 'LF', 'group': 'Outfield', 'debut': 1939, 'hr': 521, 'ba': .344, 'ops': 1.116, 'country': 'US', 'hof': True},
    {'name': 'Joe DiMaggio', 'id': 'dimagjo01', 'position': 'CF', 'group': 'Outfield', 'debut': 1936, 'hr': 361, 'ba': .325, 'ops': .977, 'country': 'US', 'hof': True},
    {'name': 'Jackie Robinson', 'id': 'robinja02', 'position': '2B', 'group': 'Infield', 'debut': 1947, 'hr': 137, 'ba': .311, 'ops': .817, 'country': 'US', 'hof': True},
    {'name': 'Ken Griffey Jr', 'id': 'griffke02', 'position': 'CF', 'group': 'Outfield', 'debut': 1989, 'hr': 630, 'ba': .284, 'ops': .907, 'country': 'US', 'hof': True},
    {'name': 'Frank Thomas', 'id': 'thomafr04', 'position': 'DH', 'group': 'DH', 'debut': 1990, 'hr': 521, 'ba': .301, 'ops': .974, 'country': 'US', 'hof': True},
    {'name': 'David Ortiz', 'id': 'ortizda01', 'position': 'DH', 'group': 'DH', 'debut': 1997, 'hr': 541, 'ba': .286, 'ops': .931, 'country': 'DR', 'hof': True},
]


def bootstrap_data():
    """Insert bootstrap players into database with analysis."""
    with app.app_context():
        db.create_all()
        logger.info("✅ Database tables created")
        
        collector = MLBCollector()
        
        added_count = 0
        for player_data in BOOTSTRAP_PLAYERS:
            # Check if exists
            existing = MLBPlayer.query.filter_by(id=player_data['id']).first()
            if existing:
                logger.debug(f"Player exists: {player_data['name']}")
                continue
            
            # Determine era
            debut_year = player_data['debut']
            if debut_year < 1980:
                era_group = 'classic'
            elif debut_year < 2000:
                era_group = 'modern'
            else:
                era_group = 'contemporary'
            
            # Create player
            player = MLBPlayer(
                id=player_data['id'],
                name=player_data['name'],
                full_name=player_data['name'],
                position=player_data['position'],
                position_group=player_data['group'],
                pitcher_role=player_data.get('role'),
                debut_year=debut_year,
                years_active=15,  # Placeholder
                era_group=era_group,
                birth_country=player_data.get('country', 'US'),
                hof_inducted=player_data.get('hof', False)
            )
            
            # Add stats based on position
            if player_data['group'] == 'Pitcher':
                player.wins = player_data.get('wins', 0)
                player.era = player_data.get('era', 0)
                player.strikeouts = player_data.get('strikeouts', 0)
                player.saves = player_data.get('saves', 0)
            else:
                player.home_runs = player_data.get('hr', 0)
                player.batting_average = player_data.get('ba', 0)
                player.ops = player_data.get('ops', 0)
            
            db.session.add(player)
            db.session.flush()
            
            # Analyze name
            analysis_data = collector.analyze_player_name(player_data['name'], player_data['group'])
            analysis_data['player_id'] = player_data['id']
            
            analysis = MLBPlayerAnalysis(**analysis_data)
            db.session.add(analysis)
            
            added_count += 1
            logger.info(f"✅ Added: {player_data['name']} ({player_data['group']}, {debut_year})")
        
        db.session.commit()
        
        logger.info(f"\n🎉 Bootstrap complete: {added_count} players added")
        
        # Show summary
        total = MLBPlayer.query.count()
        logger.info(f"\n📈 Total MLB players: {total}")
        
        # By position
        for pos_group in ['Pitcher', 'Catcher', 'Infield', 'Outfield', 'DH']:
            count = MLBPlayer.query.filter_by(position_group=pos_group).count()
            logger.info(f"   {pos_group}: {count}")
        
        # By era
        for era in ['classic', 'modern', 'contemporary']:
            count = MLBPlayer.query.filter_by(era_group=era).count()
            logger.info(f"   {era}: {count}")
        
        # Sample players
        logger.info(f"\n⚾ Sample players:")
        samples = MLBPlayer.query.limit(10).all()
        for p in samples:
            logger.info(f"   - {p.name} ({p.position_group})")


if __name__ == "__main__":
    bootstrap_data()

