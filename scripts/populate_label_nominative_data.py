"""
Populate Label Nominative Data
Extract and analyze team names, venues, and other labels from existing database

Purpose: Populate LabelNominativeProfile tables with comprehensive feature extraction
Priority: Teams and venues first (immediate betting impact)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from core.models import (LabelNominativeProfile, TeamProfile, VenueProfile, 
                          PropTypeProfile, NFLPlayer, NBAPlayer, MLBPlayer)
from analyzers.label_nominative_extractor import LabelNominativeExtractor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# TEAM DATA - All Major Sports
# ============================================================================

NFL_TEAMS = [
    # AFC East
    ("Buffalo Bills", "Buffalo", "AFC", "East"),
    ("Miami Dolphins", "Miami", "AFC", "East"),
    ("New England Patriots", "New England", "AFC", "East"),
    ("New York Jets", "New York", "AFC", "East"),
    # AFC North
    ("Baltimore Ravens", "Baltimore", "AFC", "North"),
    ("Cincinnati Bengals", "Cincinnati", "AFC", "North"),
    ("Cleveland Browns", "Cleveland", "AFC", "North"),
    ("Pittsburgh Steelers", "Pittsburgh", "AFC", "North"),
    # AFC South
    ("Houston Texans", "Houston", "AFC", "South"),
    ("Indianapolis Colts", "Indianapolis", "AFC", "South"),
    ("Jacksonville Jaguars", "Jacksonville", "AFC", "South"),
    ("Tennessee Titans", "Tennessee", "AFC", "South"),
    # AFC West
    ("Denver Broncos", "Denver", "AFC", "West"),
    ("Kansas City Chiefs", "Kansas City", "AFC", "West"),
    ("Las Vegas Raiders", "Las Vegas", "AFC", "West"),
    ("Los Angeles Chargers", "Los Angeles", "AFC", "West"),
    # NFC East
    ("Dallas Cowboys", "Dallas", "NFC", "East"),
    ("New York Giants", "New York", "NFC", "East"),
    ("Philadelphia Eagles", "Philadelphia", "NFC", "East"),
    ("Washington Commanders", "Washington", "NFC", "East"),
    # NFC North
    ("Chicago Bears", "Chicago", "NFC", "North"),
    ("Detroit Lions", "Detroit", "NFC", "North"),
    ("Green Bay Packers", "Green Bay", "NFC", "North"),
    ("Minnesota Vikings", "Minnesota", "NFC", "North"),
    # NFC South
    ("Atlanta Falcons", "Atlanta", "NFC", "South"),
    ("Carolina Panthers", "Carolina", "NFC", "South"),
    ("New Orleans Saints", "New Orleans", "NFC", "South"),
    ("Tampa Bay Buccaneers", "Tampa Bay", "NFC", "South"),
    # NFC West
    ("Arizona Cardinals", "Arizona", "NFC", "West"),
    ("Los Angeles Rams", "Los Angeles", "NFC", "West"),
    ("San Francisco 49ers", "San Francisco", "NFC", "West"),
    ("Seattle Seahawks", "Seattle", "NFC", "West"),
]

NBA_TEAMS = [
    # Eastern Conference - Atlantic
    ("Boston Celtics", "Boston", "Eastern", "Atlantic"),
    ("Brooklyn Nets", "Brooklyn", "Eastern", "Atlantic"),
    ("New York Knicks", "New York", "Eastern", "Atlantic"),
    ("Philadelphia 76ers", "Philadelphia", "Eastern", "Atlantic"),
    ("Toronto Raptors", "Toronto", "Eastern", "Atlantic"),
    # Eastern Conference - Central
    ("Chicago Bulls", "Chicago", "Eastern", "Central"),
    ("Cleveland Cavaliers", "Cleveland", "Eastern", "Central"),
    ("Detroit Pistons", "Detroit", "Eastern", "Central"),
    ("Indiana Pacers", "Indiana", "Eastern", "Central"),
    ("Milwaukee Bucks", "Milwaukee", "Eastern", "Central"),
    # Eastern Conference - Southeast
    ("Atlanta Hawks", "Atlanta", "Eastern", "Southeast"),
    ("Charlotte Hornets", "Charlotte", "Eastern", "Southeast"),
    ("Miami Heat", "Miami", "Eastern", "Southeast"),
    ("Orlando Magic", "Orlando", "Eastern", "Southeast"),
    ("Washington Wizards", "Washington", "Eastern", "Southeast"),
    # Western Conference - Northwest
    ("Denver Nuggets", "Denver", "Western", "Northwest"),
    ("Minnesota Timberwolves", "Minnesota", "Western", "Northwest"),
    ("Oklahoma City Thunder", "Oklahoma City", "Western", "Northwest"),
    ("Portland Trail Blazers", "Portland", "Western", "Northwest"),
    ("Utah Jazz", "Utah", "Western", "Northwest"),
    # Western Conference - Pacific
    ("Golden State Warriors", "Golden State", "Western", "Pacific"),
    ("Los Angeles Clippers", "Los Angeles", "Western", "Pacific"),
    ("Los Angeles Lakers", "Los Angeles", "Western", "Pacific"),
    ("Phoenix Suns", "Phoenix", "Western", "Pacific"),
    ("Sacramento Kings", "Sacramento", "Western", "Pacific"),
    # Western Conference - Southwest
    ("Dallas Mavericks", "Dallas", "Western", "Southwest"),
    ("Houston Rockets", "Houston", "Western", "Southwest"),
    ("Memphis Grizzlies", "Memphis", "Western", "Southwest"),
    ("New Orleans Pelicans", "New Orleans", "Western", "Southwest"),
    ("San Antonio Spurs", "San Antonio", "Western", "Southwest"),
]

MLB_TEAMS = [
    # American League - East
    ("Baltimore Orioles", "Baltimore", "AL", "East"),
    ("Boston Red Sox", "Boston", "AL", "East"),
    ("New York Yankees", "New York", "AL", "East"),
    ("Tampa Bay Rays", "Tampa Bay", "AL", "East"),
    ("Toronto Blue Jays", "Toronto", "AL", "East"),
    # American League - Central
    ("Chicago White Sox", "Chicago", "AL", "Central"),
    ("Cleveland Guardians", "Cleveland", "AL", "Central"),
    ("Detroit Tigers", "Detroit", "AL", "Central"),
    ("Kansas City Royals", "Kansas City", "AL", "Central"),
    ("Minnesota Twins", "Minnesota", "AL", "Central"),
    # American League - West
    ("Houston Astros", "Houston", "AL", "West"),
    ("Los Angeles Angels", "Los Angeles", "AL", "West"),
    ("Oakland Athletics", "Oakland", "AL", "West"),
    ("Seattle Mariners", "Seattle", "AL", "West"),
    ("Texas Rangers", "Texas", "AL", "West"),
    # National League - East
    ("Atlanta Braves", "Atlanta", "NL", "East"),
    ("Miami Marlins", "Miami", "NL", "East"),
    ("New York Mets", "New York", "NL", "East"),
    ("Philadelphia Phillies", "Philadelphia", "NL", "East"),
    ("Washington Nationals", "Washington", "NL", "East"),
    # National League - Central
    ("Chicago Cubs", "Chicago", "NL", "Central"),
    ("Cincinnati Reds", "Cincinnati", "NL", "Central"),
    ("Milwaukee Brewers", "Milwaukee", "NL", "Central"),
    ("Pittsburgh Pirates", "Pittsburgh", "NL", "Central"),
    ("St. Louis Cardinals", "St. Louis", "NL", "Central"),
    # National League - West
    ("Arizona Diamondbacks", "Arizona", "NL", "West"),
    ("Colorado Rockies", "Colorado", "NL", "West"),
    ("Los Angeles Dodgers", "Los Angeles", "NL", "West"),
    ("San Diego Padres", "San Diego", "NL", "West"),
    ("San Francisco Giants", "San Francisco", "NL", "West"),
]


# ============================================================================
# VENUE DATA - Major Stadiums/Arenas
# ============================================================================

NFL_VENUES = [
    ("Lambeau Field", "Green Bay", "WI", "grass", 81441, True),
    ("Arrowhead Stadium", "Kansas City", "MO", "grass", 76416, True),
    ("Soldier Field", "Chicago", "IL", "grass", 61500, True),
    ("AT&T Stadium", "Arlington", "TX", "turf", 80000, False),
    ("MetLife Stadium", "East Rutherford", "NJ", "turf", 82500, True),
    ("Gillette Stadium", "Foxborough", "MA", "turf", 65878, True),
    ("Raymond James Stadium", "Tampa", "FL", "grass", 65618, True),
    ("Mercedes-Benz Stadium", "Atlanta", "GA", "turf", 71000, False),
    ("US Bank Stadium", "Minneapolis", "MN", "turf", 66860, False),
    ("Levi's Stadium", "Santa Clara", "CA", "grass", 68500, True),
    ("Lincoln Financial Field", "Philadelphia", "PA", "grass", 69796, True),
    ("Empower Field at Mile High", "Denver", "CO", "grass", 76125, True),
    ("M&T Bank Stadium", "Baltimore", "MD", "grass", 71008, True),
    ("Highmark Stadium", "Orchard Park", "NY", "turf", 71608, True),
]

NBA_VENUES = [
    ("Madison Square Garden", "New York", "NY", "hardwood", 19812, False),
    ("TD Garden", "Boston", "MA", "hardwood", 19156, False),
    ("United Center", "Chicago", "IL", "hardwood", 20917, False),
    ("Chase Center", "San Francisco", "CA", "hardwood", 18064, False),
    ("Crypto.com Arena", "Los Angeles", "CA", "hardwood", 19060, False),
    ("Ball Arena", "Denver", "CO", "hardwood", 19520, False),
    ("American Airlines Center", "Dallas", "TX", "hardwood", 19200, False),
    ("Barclays Center", "Brooklyn", "NY", "hardwood", 17732, False),
]

MLB_VENUES = [
    ("Fenway Park", "Boston", "MA", "grass", 37755, True),
    ("Yankee Stadium", "Bronx", "NY", "grass", 46537, True),
    ("Wrigley Field", "Chicago", "IL", "grass", 41649, True),
    ("Dodger Stadium", "Los Angeles", "CA", "grass", 56000, True),
    ("Oracle Park", "San Francisco", "CA", "grass", 41915, True),
    ("Coors Field", "Denver", "CO", "grass", 50144, True),
    ("Camden Yards", "Baltimore", "MD", "grass", 45971, True),
    ("PNC Park", "Pittsburgh", "PA", "grass", 38362, True),
]


# ============================================================================
# PROP TYPES - Standardized Taxonomy
# ============================================================================

PROP_TYPES = {
    'football': [
        ("Passing Yards", "passing", 60, 75, False, False),
        ("Passing Touchdowns", "passing", 70, 80, False, False),
        ("Rushing Yards", "rushing", 80, 40, True, True),
        ("Rushing Touchdowns", "rushing", 85, 35, True, True),
        ("Receiving Yards", "receiving", 65, 65, False, True),
        ("Receiving Touchdowns", "receiving", 70, 60, False, False),
        ("Receptions", "receiving", 50, 70, False, False),
        ("Tackles", "defense", 90, 50, True, False),
        ("Sacks", "defense", 95, 45, True, False),
        ("Interceptions", "defense", 75, 85, False, False),
    ],
    'basketball': [
        ("Points", "scoring", 65, 70, False, False),
        ("Rebounds", "rebounding", 75, 55, True, False),
        ("Assists", "passing", 50, 80, False, False),
        ("Three-Pointers Made", "shooting", 55, 90, False, False),
        ("Blocks", "defense", 80, 60, True, False),
        ("Steals", "defense", 70, 75, False, True),
    ],
    'baseball': [
        ("Hits", "batting", 60, 70, False, False),
        ("Home Runs", "batting", 85, 60, True, False),
        ("RBIs", "batting", 65, 65, False, False),
        ("Stolen Bases", "baserunning", 50, 80, False, True),
        ("Strikeouts", "pitching", 80, 85, True, False),
        ("Wins", "pitching", 70, 75, False, False),
        ("Earned Runs", "pitching", 75, 70, False, False),
    ]
}


def populate_team_names():
    """Extract and populate team nominative profiles"""
    logger.info("="*80)
    logger.info("POPULATING TEAM NOMINATIVE PROFILES")
    logger.info("="*80)
    
    extractor = LabelNominativeExtractor()
    
    teams_data = [
        ('NFL', 'football', NFL_TEAMS),
        ('NBA', 'basketball', NBA_TEAMS),
        ('MLB', 'baseball', MLB_TEAMS),
    ]
    
    total_teams = 0
    
    for league, sport, teams in teams_data:
        logger.info(f"\nProcessing {league} teams...")
        
        for team_name, city, conference, division in teams:
            # Extract nominative features
            features = extractor.extract_label_features(team_name, 'team', {'sport': sport})
            
            # Create or update label nominative profile
            profile = LabelNominativeProfile.query.filter_by(
                label_text=team_name,
                label_type='team',
                domain='sports'
            ).first()
            
            if not profile:
                profile = LabelNominativeProfile(
                    label_text=team_name,
                    label_type='team',
                    domain='sports',
                    sport=sport
                )
            
            # Set base linguistic features
            profile.syllables = features.get('syllables')
            profile.length = features.get('length')
            profile.harshness = features.get('harshness')
            profile.memorability = features.get('memorability')
            profile.pronounceability = features.get('pronounceability')
            profile.uniqueness = features.get('uniqueness')
            profile.vowel_ratio = features.get('vowel_ratio')
            profile.consonant_clusters = features.get('consonant_clusters')
            profile.first_letter_harsh = features.get('first_letter_harsh', False)
            profile.last_letter_harsh = features.get('last_letter_harsh', False)
            
            # Set phonetic features
            profile.plosive_count = features.get('plosive_count')
            profile.fricative_count = features.get('fricative_count')
            profile.liquid_count = features.get('liquid_count')
            profile.nasal_count = features.get('nasal_count')
            profile.front_vowel_count = features.get('front_vowel_count')
            profile.back_vowel_count = features.get('back_vowel_count')
            profile.power_phoneme_count = features.get('power_phoneme_count')
            profile.speed_phoneme_count = features.get('speed_phoneme_count')
            profile.soft_phoneme_count = features.get('soft_phoneme_count')
            profile.power_phoneme_ratio = features.get('power_phoneme_ratio')
            profile.speed_phoneme_ratio = features.get('speed_phoneme_ratio')
            profile.soft_phoneme_ratio = features.get('soft_phoneme_ratio')
            profile.initial_consonant_strength = features.get('initial_consonant_strength')
            profile.final_consonant_strength = features.get('final_consonant_strength')
            profile.sonority_score = features.get('sonority_score')
            profile.consonant_harmony = features.get('consonant_harmony')
            profile.vowel_harmony = features.get('vowel_harmony')
            
            # Set semantic features
            profile.word_count = features.get('word_count')
            profile.contains_numbers = features.get('contains_numbers', False)
            profile.has_acronym = features.get('has_acronym', False)
            profile.is_compound = features.get('is_compound', False)
            profile.prestige_indicator = features.get('prestige_indicator', False)
            profile.power_semantic = features.get('power_semantic', False)
            profile.speed_semantic = features.get('speed_semantic', False)
            profile.has_geographic = features.get('has_geographic', False)
            profile.has_color = features.get('has_color', False)
            profile.is_animal = features.get('is_animal', False)
            
            # Store team-specific features as JSON
            team_specific = {
                'team_aggression_score': features.get('team_aggression_score', 50),
                'team_tradition_score': features.get('team_tradition_score', 50),
                'geographic_prominence': features.get('team_geographic_strength', 50)
            }
            profile.set_specific_features(team_specific)
            
            db.session.add(profile)
            db.session.flush()  # Get the ID
            
            # Create TeamProfile entry
            team_profile = TeamProfile.query.filter_by(
                team_name=team_name,
                sport=sport,
                league=league
            ).first()
            
            if not team_profile:
                team_profile = TeamProfile(
                    team_name=team_name.split()[-1],  # Just nickname
                    team_city=city,
                    team_full_name=team_name,
                    sport=sport,
                    league=league,
                    conference=conference,
                    division=division,
                    label_profile_id=profile.id,
                    team_aggression_score=team_specific['team_aggression_score'],
                    team_tradition_score=team_specific['team_tradition_score'],
                    geographic_prominence=team_specific['geographic_prominence']
                )
                db.session.add(team_profile)
            
            total_teams += 1
            
            if total_teams % 10 == 0:
                logger.info(f"  Processed {total_teams} teams...")
                db.session.commit()
    
    db.session.commit()
    logger.info(f"\n✅ Successfully populated {total_teams} team profiles")


def populate_venue_names():
    """Extract and populate venue nominative profiles"""
    logger.info("\n" + "="*80)
    logger.info("POPULATING VENUE NOMINATIVE PROFILES")
    logger.info("="*80)
    
    extractor = LabelNominativeExtractor()
    
    venues_data = [
        ('football', NFL_VENUES),
        ('basketball', NBA_VENUES),
        ('baseball', MLB_VENUES),
    ]
    
    total_venues = 0
    
    for sport, venues in venues_data:
        logger.info(f"\nProcessing {sport} venues...")
        
        for venue_name, city, state, surface, capacity, is_outdoor in venues:
            # Extract nominative features
            features = extractor.extract_label_features(venue_name, 'venue', {'sport': sport})
            
            # Create or update label nominative profile
            profile = LabelNominativeProfile.query.filter_by(
                label_text=venue_name,
                label_type='venue',
                domain='sports'
            ).first()
            
            if not profile:
                profile = LabelNominativeProfile(
                    label_text=venue_name,
                    label_type='venue',
                    domain='sports',
                    sport=sport
                )
            
            # Set all features (same pattern as teams)
            profile.syllables = features.get('syllables')
            profile.length = features.get('length')
            profile.harshness = features.get('harshness')
            profile.memorability = features.get('memorability')
            profile.pronounceability = features.get('pronounceability')
            profile.uniqueness = features.get('uniqueness')
            profile.vowel_ratio = features.get('vowel_ratio')
            profile.consonant_clusters = features.get('consonant_clusters')
            profile.first_letter_harsh = features.get('first_letter_harsh', False)
            profile.last_letter_harsh = features.get('last_letter_harsh', False)
            
            # Phonetic features
            profile.plosive_count = features.get('plosive_count')
            profile.fricative_count = features.get('fricative_count')
            profile.power_phoneme_count = features.get('power_phoneme_count')
            profile.speed_phoneme_count = features.get('speed_phoneme_count')
            profile.power_phoneme_ratio = features.get('power_phoneme_ratio')
            profile.initial_consonant_strength = features.get('initial_consonant_strength')
            profile.final_consonant_strength = features.get('final_consonant_strength')
            profile.sonority_score = features.get('sonority_score')
            
            # Semantic features
            profile.word_count = features.get('word_count')
            profile.prestige_indicator = features.get('prestige_indicator', False)
            profile.has_geographic = features.get('has_geographic', False)
            
            # Venue-specific features
            venue_specific = {
                'venue_prestige': features.get('venue_prestige', 50),
                'venue_intimidation': features.get('venue_intimidation', 50),
                'venue_memorability': features.get('memorability', 50)
            }
            profile.set_specific_features(venue_specific)
            
            db.session.add(profile)
            db.session.flush()
            
            # Create VenueProfile entry
            venue_profile = VenueProfile.query.filter_by(venue_name=venue_name).first()
            
            if not venue_profile:
                venue_profile = VenueProfile(
                    venue_name=venue_name,
                    city=city,
                    state=state,
                    sport=sport,
                    label_profile_id=profile.id,
                    venue_prestige=venue_specific['venue_prestige'],
                    venue_intimidation=venue_specific['venue_intimidation'],
                    venue_memorability=venue_specific['venue_memorability'],
                    surface_type=surface,
                    capacity=capacity,
                    is_outdoor=is_outdoor
                )
                db.session.add(venue_profile)
            
            total_venues += 1
    
    db.session.commit()
    logger.info(f"\n✅ Successfully populated {total_venues} venue profiles")


def populate_prop_types():
    """Extract and populate prop type nominative profiles"""
    logger.info("\n" + "="*80)
    logger.info("POPULATING PROP TYPE NOMINATIVE PROFILES")
    logger.info("="*80)
    
    extractor = LabelNominativeExtractor()
    total_props = 0
    
    for sport, props in PROP_TYPES.items():
        logger.info(f"\nProcessing {sport} prop types...")
        
        for prop_name, category, intensity, precision, power_ind, speed_ind in props:
            # Extract nominative features
            features = extractor.extract_label_features(prop_name, 'prop', {'sport': sport})
            
            # Create label nominative profile
            profile = LabelNominativeProfile.query.filter_by(
                label_text=prop_name,
                label_type='prop',
                domain='sports'
            ).first()
            
            if not profile:
                profile = LabelNominativeProfile(
                    label_text=prop_name,
                    label_type='prop',
                    domain='sports',
                    sport=sport
                )
            
            # Set features
            profile.syllables = features.get('syllables')
            profile.length = features.get('length')
            profile.harshness = features.get('harshness')
            profile.memorability = features.get('memorability')
            profile.power_phoneme_count = features.get('power_phoneme_count')
            profile.speed_phoneme_count = features.get('speed_phoneme_count')
            profile.power_phoneme_ratio = features.get('power_phoneme_ratio')
            
            # Prop-specific features
            prop_specific = {
                'prop_action_intensity': features.get('prop_action_intensity', intensity),
                'prop_precision_demand': features.get('prop_precision_demand', precision)
            }
            profile.set_specific_features(prop_specific)
            
            db.session.add(profile)
            db.session.flush()
            
            # Create PropTypeProfile
            prop_profile = PropTypeProfile.query.filter_by(prop_type_name=prop_name).first()
            
            if not prop_profile:
                prop_profile = PropTypeProfile(
                    prop_type_name=prop_name,
                    sport=sport,
                    prop_category=category,
                    label_profile_id=profile.id,
                    prop_action_intensity=intensity,
                    prop_precision_demand=precision,
                    prop_power_indicator=power_ind,
                    prop_speed_indicator=speed_ind
                )
                db.session.add(prop_profile)
            
            total_props += 1
    
    db.session.commit()
    logger.info(f"\n✅ Successfully populated {total_props} prop type profiles")


def main():
    """Main execution function"""
    with app.app_context():
        logger.info("="*80)
        logger.info("LABEL NOMINATIVE DATA POPULATION")
        logger.info("="*80)
        logger.info("\nThis script will populate:")
        logger.info("  - Team names (92 teams across NFL/NBA/MLB)")
        logger.info("  - Venue names (30+ major stadiums/arenas)")
        logger.info("  - Prop types (standardized taxonomy)")
        logger.info("\nWith comprehensive nominative feature extraction\n")
        
        try:
            # Create tables if they don't exist
            db.create_all()
            logger.info("✅ Database tables ready\n")
            
            # Populate teams (highest priority)
            populate_team_names()
            
            # Populate venues
            populate_venue_names()
            
            # Populate prop types
            populate_prop_types()
            
            logger.info("\n" + "="*80)
            logger.info("DATA POPULATION COMPLETE!")
            logger.info("="*80)
            logger.info("\nLabel nominative profiles created for:")
            
            team_count = LabelNominativeProfile.query.filter_by(label_type='team').count()
            venue_count = LabelNominativeProfile.query.filter_by(label_type='venue').count()
            prop_count = LabelNominativeProfile.query.filter_by(label_type='prop').count()
            
            logger.info(f"  - Teams: {team_count}")
            logger.info(f"  - Venues: {venue_count}")
            logger.info(f"  - Prop Types: {prop_count}")
            logger.info(f"  - TOTAL: {team_count + venue_count + prop_count}")
            
            logger.info("\n✅ Ready for ensemble interaction analysis")
            logger.info("✅ Ready for correlation analysis")
            logger.info("✅ Ready for betting system integration\n")
            
        except Exception as e:
            logger.error(f"❌ Error during population: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            raise


if __name__ == "__main__":
    main()

