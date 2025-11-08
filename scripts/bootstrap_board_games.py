"""Bootstrap Board Games Data

Creates initial dataset with well-known games for immediate visual demonstration.
This provides data for the dashboard while full BGG collection is refined.
"""

import logging
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from core.models import BoardGame, BoardGameAnalysis
from collectors.board_game_collector import BoardGameCollector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Curated list of influential board games with known data
BOOTSTRAP_GAMES = [
    # Classic Era (1950-1979)
    {'name': 'Monopoly', 'bgg_id': 1406, 'year': 1935, 'rating': 4.4, 'complexity': 1.7, 'category': 'Economic', 'designer': 'Charles Darrow', 'nationality': 'US'},
    {'name': 'Risk', 'bgg_id': 181, 'year': 1959, 'rating': 5.6, 'complexity': 2.1, 'category': 'War Game', 'designer': 'Albert Lamorisse', 'nationality': 'FR'},
    {'name': 'Stratego', 'bgg_id': 1917, 'year': 1961, 'rating': 5.9, 'complexity': 2.0, 'category': 'War Game', 'designer': 'Jacques Johan Mogendorff', 'nationality': 'NL'},
    {'name': 'Diplomacy', 'bgg_id': 483, 'year': 1959, 'rating': 7.2, 'complexity': 2.5, 'category': 'Strategy', 'designer': 'Allan B. Calhamer', 'nationality': 'US'},
    {'name': 'Acquire', 'bgg_id': 5, 'year': 1964, 'rating': 7.2, 'complexity': 2.4, 'category': 'Economic', 'designer': 'Sid Sackson', 'nationality': 'US'},
    {'name': 'Cosmic Encounter', 'bgg_id': 39463, 'year': 1977, 'rating': 7.1, 'complexity': 2.6, 'category': 'Sci-Fi', 'designer': 'Bill Eberle', 'nationality': 'US'},
    
    # Golden Age (1980-1999)
    {'name': 'Sherlock Holmes Consulting Detective', 'bgg_id': 2511, 'year': 1981, 'rating': 7.6, 'complexity': 2.7, 'category': 'Deduction', 'designer': 'Gary Grady', 'nationality': 'US'},
    {'name': 'Dune', 'bgg_id': 283155, 'year': 1979, 'rating': 7.6, 'complexity': 3.7, 'category': 'Strategy', 'designer': 'Bill Eberle', 'nationality': 'US'},
    {'name': 'El Grande', 'bgg_id': 93, 'year': 1995, 'rating': 7.7, 'complexity': 3.1, 'category': 'Strategy', 'designer': 'Wolfgang Kramer', 'nationality': 'DE'},
    {'name': 'Catan', 'bgg_id': 13, 'year': 1995, 'rating': 7.1, 'complexity': 2.3, 'category': 'Strategy', 'designer': 'Klaus Teuber', 'nationality': 'DE'},
    {'name': 'Carcassonne', 'bgg_id': 822, 'year': 2000, 'rating': 7.4, 'complexity': 1.9, 'category': 'Strategy', 'designer': 'Klaus-Jürgen Wrede', 'nationality': 'DE'},
    {'name': 'Tikal', 'bgg_id': 54, 'year': 1999, 'rating': 7.3, 'complexity': 3.0, 'category': 'Strategy', 'designer': 'Wolfgang Kramer', 'nationality': 'DE'},
    {'name': 'Tigris & Euphrates', 'bgg_id': 42, 'year': 1997, 'rating': 7.6, 'complexity': 3.5, 'category': 'Abstract', 'designer': 'Reiner Knizia', 'nationality': 'DE'},
    
    # Modern Era (2000-2009)
    {'name': 'Puerto Rico', 'bgg_id': 3076, 'year': 2002, 'rating': 7.9, 'complexity': 3.3, 'category': 'Strategy', 'designer': 'Andreas Seyfarth', 'nationality': 'DE'},
    {'name': 'Ticket to Ride', 'bgg_id': 9209, 'year': 2004, 'rating': 7.4, 'complexity': 1.9, 'category': 'Family', 'designer': 'Alan R. Moon', 'nationality': 'US'},
    {'name': 'Pandemic', 'bgg_id': 30549, 'year': 2008, 'rating': 7.6, 'complexity': 2.4, 'category': 'Cooperative', 'designer': 'Matt Leacock', 'nationality': 'US'},
    {'name': 'Dominion', 'bgg_id': 36218, 'year': 2008, 'rating': 7.6, 'complexity': 2.4, 'category': 'Card Game', 'designer': 'Donald X. Vaccarino', 'nationality': 'US'},
    {'name': 'Agricola', 'bgg_id': 31260, 'year': 2007, 'rating': 7.9, 'complexity': 3.6, 'category': 'Strategy', 'designer': 'Uwe Rosenberg', 'nationality': 'DE'},
    {'name': 'Power Grid', 'bgg_id': 2651, 'year': 2004, 'rating': 7.8, 'complexity': 3.3, 'category': 'Economic', 'designer': 'Friedemann Friese', 'nationality': 'DE'},
    {'name': 'Race for the Galaxy', 'bgg_id': 28143, 'year': 2007, 'rating': 7.7, 'complexity': 3.0, 'category': 'Sci-Fi', 'designer': 'Thomas Lehmann', 'nationality': 'US'},
    {'name': 'Through the Ages', 'bgg_id': 25613, 'year': 2006, 'rating': 8.1, 'complexity': 4.4, 'category': 'Civilization', 'designer': 'Vlaada Chvátil', 'nationality': 'CZ'},
    
    # Contemporary Era (2010-2024)
    {'name': 'Wingspan', 'bgg_id': 266192, 'year': 2019, 'rating': 8.0, 'complexity': 2.4, 'category': 'Strategy', 'designer': 'Elizabeth Hargrave', 'nationality': 'US'},
    {'name': 'Azul', 'bgg_id': 230802, 'year': 2017, 'rating': 7.8, 'complexity': 1.8, 'category': 'Abstract', 'designer': 'Michael Kiesling', 'nationality': 'DE'},
    {'name': 'Scythe', 'bgg_id': 169786, 'year': 2016, 'rating': 8.1, 'complexity': 3.4, 'category': 'Strategy', 'designer': 'Jamey Stegmaier', 'nationality': 'US'},
    {'name': 'Terraforming Mars', 'bgg_id': 167791, 'year': 2016, 'rating': 8.4, 'complexity': 3.2, 'category': 'Strategy', 'designer': 'Jacob Fryxelius', 'nationality': 'SE'},
    {'name': 'Gloomhaven', 'bgg_id': 174430, 'year': 2017, 'rating': 8.7, 'complexity': 3.9, 'category': 'Adventure', 'designer': 'Isaac Childres', 'nationality': 'US'},
    {'name': 'Brass: Birmingham', 'bgg_id': 224517, 'year': 2018, 'rating': 8.6, 'complexity': 3.9, 'category': 'Economic', 'designer': 'Martin Wallace', 'nationality': 'GB'},
    {'name': '7 Wonders', 'bgg_id': 68448, 'year': 2010, 'rating': 7.7, 'complexity': 2.3, 'category': 'Strategy', 'designer': 'Antoine Bauza', 'nationality': 'FR'},
    {'name': 'Spirit Island', 'bgg_id': 162886, 'year': 2017, 'rating': 8.3, 'complexity': 4.0, 'category': 'Strategy', 'designer': 'R. Eric Reuss', 'nationality': 'US'},
    {'name': 'Everdell', 'bgg_id': 199792, 'year': 2018, 'rating': 7.9, 'complexity': 2.8, 'category': 'Strategy', 'designer': 'James A. Wilson', 'nationality': 'US'},
    {'name': 'Cascadia', 'bgg_id': 295947, 'year': 2021, 'rating': 7.9, 'complexity': 1.9, 'category': 'Strategy', 'designer': 'Randy Flynn', 'nationality': 'US'},
    {'name': 'Splendor', 'bgg_id': 148228, 'year': 2014, 'rating': 7.4, 'complexity': 1.8, 'category': 'Strategy', 'designer': 'Marc André', 'nationality': 'FR'},
    {'name': 'Codenames', 'bgg_id': 178900, 'year': 2015, 'rating': 7.6, 'complexity': 1.3, 'category': 'Party', 'designer': 'Vlaada Chvátil', 'nationality': 'CZ'},
    {'name': 'Kingdomino', 'bgg_id': 204583, 'year': 2016, 'rating': 7.3, 'complexity': 1.2, 'category': 'Family', 'designer': 'Bruno Cathala', 'nationality': 'FR'},
    
    # Additional notable games
    {'name': 'Root', 'bgg_id': 237182, 'year': 2018, 'rating': 8.0, 'complexity': 3.7, 'category': 'War Game', 'designer': 'Cole Wehrle', 'nationality': 'US'},
    {'name': 'Ark Nova', 'bgg_id': 342942, 'year': 2021, 'rating': 8.5, 'complexity': 3.7, 'category': 'Strategy', 'designer': 'Mathias Wigge', 'nationality': 'DE'},
    {'name': 'Lost Ruins of Arnak', 'bgg_id': 312484, 'year': 2020, 'rating': 8.1, 'complexity': 2.9, 'category': 'Adventure', 'designer': 'Mín & Elwen', 'nationality': 'CZ'},
]


def bootstrap_data():
    """Insert bootstrap games into database with analysis."""
    with app.app_context():
        db.create_all()
        logger.info("✅ Database tables created")
        
        collector = BoardGameCollector()
        
        added_count = 0
        for game_data in BOOTSTRAP_GAMES:
            # Check if exists
            existing = BoardGame.query.filter_by(name=game_data['name']).first()
            if existing:
                logger.debug(f"Game exists: {game_data['name']}")
                continue
            
            # Create game
            game = BoardGame(
                name=game_data['name'],
                bgg_id=game_data['bgg_id'],
                year_published=game_data['year'],
                bgg_rating=game_data['rating'],
                average_rating=game_data['rating'],
                num_ratings=1000,  # Placeholder
                complexity_weight=game_data['complexity'],
                category=game_data['category'],
                designer=game_data['designer'],
                designer_nationality=game_data['nationality'],
                min_players=2,
                max_players=4,
                playing_time=60
            )
            
            db.session.add(game)
            db.session.flush()
            
            # Determine era
            year = game_data['year']
            if year < 1980:
                era = 'classic_1950_1979'
            elif year < 2000:
                era = 'golden_1980_1999'
            elif year < 2010:
                era = 'modern_2000_2009'
            else:
                era = 'contemporary_2010_2024'
            
            # Analyze name
            analysis_data = collector._analyze_game_name(game_data['name'], era)
            analysis_data['game_id'] = game.id
            
            analysis = BoardGameAnalysis(**analysis_data)
            db.session.add(analysis)
            
            added_count += 1
            logger.info(f"✅ Added: {game_data['name']} ({game_data['year']})")
        
        db.session.commit()
        
        logger.info(f"\n🎉 Bootstrap complete: {added_count} games added")
        
        # Run cluster analysis
        logger.info("\n📊 Running cluster analysis...")
        from analyzers.board_game_statistical_analyzer import BoardGameStatisticalAnalyzer
        analyzer = BoardGameStatisticalAnalyzer()
        
        df = analyzer.get_comprehensive_dataset()
        if len(df) >= 20:
            cluster_results = analyzer.analyze_clusters(df, n_clusters=4)
            logger.info(f"✅ Clusters created (silhouette: {cluster_results['silhouette_score']:.3f})")
        
        # Show summary
        total = BoardGame.query.count()
        logger.info(f"\n📈 Total games in database: {total}")
        
        # By era
        for era in ['classic_1950_1979', 'golden_1980_1999', 'modern_2000_2009', 'contemporary_2010_2024']:
            count = BoardGameAnalysis.query.filter_by(era=era).count()
            logger.info(f"   {era}: {count}")


if __name__ == "__main__":
    bootstrap_data()

