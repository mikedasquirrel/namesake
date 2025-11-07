"""Ship Collector

Collects historical ship data from multiple sources for nominative determinism analysis.
Tests whether geographically-tethered names (Florence, Boston) correlate with greater 
achievement compared to saint names, and whether semantic alignment (HMS Beagle → Darwin) 
exceeds chance.

Data Sources:
1. Wikipedia API - Historical ships with rich achievement data
2. Curated famous ships list - Bootstrap with well-documented vessels
3. Manual enrichment - HMS Beagle, Mayflower, Constitution, etc.

Target: 500-1000 ships across eras (Age of Sail, Steam Era, Modern)
Strategy: Stratified sampling by era, type, and nation
"""

import logging
import time
import json
import requests
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

from core.models import db, Ship, ShipAnalysis
from analyzers.name_analyzer import NameAnalyzer
from analyzers.phonemic_analyzer import PhonemicAnalyzer
from analyzers.semantic_analyzer import SemanticAnalyzer
from analyzers.advanced_analyzer import AdvancedAnalyzer

logger = logging.getLogger(__name__)


class ShipCollector:
    """Collect historical ship data from Wikipedia and other sources."""
    
    def __init__(self):
        """Initialize the collector with API connections and analyzers."""
        self.wikipedia_api_url = "https://en.wikipedia.org/w/api.php"
        
        # Geocoding for place names
        self.geolocator = Nominatim(user_agent="nominative_determinism_research")
        self.geocode_cache = {}
        
        # Rate limiting
        self.wikipedia_delay = 0.5  # Be respectful to Wikipedia
        self.geocode_delay = 1.0
        
        # Analyzers for linguistic analysis
        self.name_analyzer = NameAnalyzer()
        self.phonemic_analyzer = PhonemicAnalyzer()
        self.semantic_analyzer = SemanticAnalyzer()
        self.advanced_analyzer = AdvancedAnalyzer()
        
        # Place name databases for categorization
        self._load_place_names()
        self._load_saint_names()
        
    def _load_place_names(self):
        """Load database of geographic place names."""
        # Major cities, regions, and countries that commonly appear in ship names
        self.place_names = {
            # Major cities
            'london', 'paris', 'rome', 'berlin', 'madrid', 'vienna', 'athens',
            'florence', 'venice', 'naples', 'milan', 'boston', 'new york',
            'philadelphia', 'baltimore', 'richmond', 'charleston', 'savannah',
            'chicago', 'san francisco', 'los angeles', 'seattle', 'portland',
            'liverpool', 'manchester', 'bristol', 'glasgow', 'edinburgh',
            'sydney', 'melbourne', 'brisbane', 'wellington', 'auckland',
            'toronto', 'montreal', 'vancouver', 'quebec', 'halifax',
            'tokyo', 'kyoto', 'osaka', 'beijing', 'shanghai', 'hong kong',
            'delhi', 'mumbai', 'calcutta', 'madras', 'bombay',
            'cairo', 'alexandria', 'cape town', 'johannesburg',
            'rio', 'buenos aires', 'santiago', 'lima', 'havana',
            
            # US States
            'alabama', 'alaska', 'arizona', 'arkansas', 'california',
            'colorado', 'connecticut', 'delaware', 'florida', 'georgia',
            'hawaii', 'idaho', 'illinois', 'indiana', 'iowa', 'kansas',
            'kentucky', 'louisiana', 'maine', 'maryland', 'massachusetts',
            'michigan', 'minnesota', 'mississippi', 'missouri', 'montana',
            'nebraska', 'nevada', 'hampshire', 'jersey', 'mexico',
            'carolina', 'dakota', 'ohio', 'oklahoma', 'oregon',
            'pennsylvania', 'rhode island', 'tennessee', 'texas',
            'utah', 'vermont', 'virginia', 'washington', 'wisconsin', 'wyoming',
            
            # Countries/Nations
            'america', 'england', 'britain', 'scotland', 'wales', 'ireland',
            'france', 'spain', 'portugal', 'italy', 'germany', 'russia',
            'china', 'japan', 'india', 'australia', 'canada', 'brazil',
            
            # Regions
            'yorkshire', 'cornwall', 'devonshire', 'essex', 'kent',
            'normandy', 'brittany', 'bavaria', 'prussia', 'saxony',
            'tuscany', 'sicily', 'sardinia', 'corsica',
            
            # Rivers/Mountains/Landmarks
            'thames', 'seine', 'rhine', 'danube', 'nile', 'amazon',
            'alps', 'andes', 'himalayas', 'rockies',
        }
        
        # Cultural prestige scores (0-100) for major places
        self.place_prestige = {
            'rome': 95, 'paris': 92, 'london': 90, 'athens': 88, 'florence': 85,
            'venice': 83, 'vienna': 82, 'berlin': 80, 'madrid': 78,
            'new york': 85, 'boston': 75, 'philadelphia': 73, 'san francisco': 70,
            'edinburgh': 77, 'oxford': 76, 'cambridge': 76,
            'tokyo': 82, 'kyoto': 80, 'beijing': 85, 'shanghai': 78,
            'sydney': 75, 'melbourne': 72,
        }
    
    def _load_saint_names(self):
        """Load database of saint names commonly used for ships."""
        self.saint_names = {
            'mary', 'joseph', 'john', 'paul', 'peter', 'james', 'andrew',
            'george', 'michael', 'gabriel', 'christopher', 'francis',
            'anthony', 'patrick', 'nicholas', 'thomas', 'stephen',
            'catherine', 'margaret', 'elizabeth', 'anne', 'teresa',
            'barbara', 'agnes', 'cecilia', 'lucy', 'martha',
            'vincent', 'lawrence', 'sebastian', 'martin', 'louis',
            'rosa', 'clare', 'dominic', 'augustine', 'benedict',
        }
        
        # Common saint prefixes
        self.saint_prefixes = ['saint', 'st.', 'st', 'san', 'santa', 'santo', 'ste']
    
    def collect_bootstrap_ships(self) -> Dict:
        """Bootstrap collection with manually curated famous ships.
        
        These are ships with well-documented histories and clear outcomes,
        perfect for testing the nominative determinism hypothesis.
        
        Returns:
            Collection statistics
        """
        logger.info("="*70)
        logger.info("BOOTSTRAP: Collecting Famous Ships")
        logger.info("="*70)
        
        stats = {
            'ships_added': 0,
            'ships_updated': 0,
            'ships_analyzed': 0,
            'errors': 0
        }
        
        # Curated list of historically significant ships
        famous_ships = self._get_famous_ships_list()
        
        for ship_data in famous_ships:
            try:
                logger.info(f"Processing: {ship_data['name']}")
                
                # Check if exists
                existing = Ship.query.filter_by(name=ship_data['name']).first()
                
                if existing:
                    ship = existing
                    status = 'updated'
                else:
                    ship = Ship()
                    status = 'added'
                
                # Populate ship data
                self._populate_ship_from_dict(ship, ship_data)
                
                # Save ship
                if status == 'added':
                    db.session.add(ship)
                    stats['ships_added'] += 1
                else:
                    stats['ships_updated'] += 1
                
                db.session.commit()
                
                # Analyze ship name
                self._analyze_ship_name(ship)
                stats['ships_analyzed'] += 1
                
                logger.info(f"  ✓ {ship.name} ({status})")
                
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error processing {ship_data.get('name', 'Unknown')}: {e}")
                db.session.rollback()
                stats['errors'] += 1
        
        logger.info(f"\n{'='*70}")
        logger.info(f"Bootstrap complete: {stats['ships_added']} added, {stats['ships_updated']} updated")
        logger.info(f"{'='*70}\n")
        
        return stats
    
    def _get_famous_ships_list(self) -> List[Dict]:
        """Return manually curated list of famous ships with complete data."""
        return [
            # EXPLORATION & SCIENTIFIC SHIPS - Geographic Names
            {
                'name': 'Beagle',
                'full_designation': 'HMS Beagle',
                'prefix': 'HMS',
                'nation': 'United Kingdom',
                'ship_type': 'exploration',
                'ship_class': 'Cherokee-class brig-sloop',
                'launch_year': 1820,
                'decommission_year': 1870,
                'era': 'age_of_sail',
                'primary_purpose': 'Survey and exploration',
                'famous_voyages': json.dumps([
                    'First voyage: South America survey (1826-1830)',
                    'Second voyage: Darwin\'s voyage (1831-1836)',
                    'Third voyage: Australia survey (1837-1843)'
                ]),
                'scientific_contributions': json.dumps([
                    'Darwin\'s theory of evolution by natural selection',
                    'Extensive geological and biological specimen collection',
                    'Detailed hydrographic surveys',
                    'Foundation for "On the Origin of Species"'
                ]),
                'notable_crew_members': json.dumps([
                    'Charles Darwin (naturalist, 1831-1836)',
                    'Robert FitzRoy (captain)',
                    'John Clements Wickham (lieutenant)'
                ]),
                'major_discoveries': json.dumps([
                    'Galapagos finches variation',
                    'Geological formations supporting gradualism',
                    'Biogeographical patterns',
                    'Coral reef formation theory'
                ]),
                'historical_significance_score': 98.0,
                'major_events_count': 5,
                'home_port': 'Plymouth',
                'primary_theater': 'South America, Pacific, Australia',
                'tonnage': 235,
                'crew_size': 120,
                'data_completeness_score': 95.0,
                'wikipedia_url': 'https://en.wikipedia.org/wiki/HMS_Beagle'
            },
            {
                'name': 'Endeavour',
                'full_designation': 'HMS Endeavour',
                'prefix': 'HMS',
                'nation': 'United Kingdom',
                'ship_type': 'exploration',
                'launch_year': 1764,
                'decommission_year': 1778,
                'era': 'age_of_sail',
                'primary_purpose': 'Scientific exploration and discovery',
                'famous_voyages': json.dumps([
                    'First voyage: Transit of Venus and Pacific exploration (1768-1771)',
                    'Charting of New Zealand and eastern Australia'
                ]),
                'notable_crew_members': json.dumps([
                    'Captain James Cook',
                    'Joseph Banks (naturalist)',
                    'Daniel Solander (botanist)'
                ]),
                'major_discoveries': json.dumps([
                    'First European contact with eastern coastline of Australia',
                    'Charted New Zealand',
                    'Extensive botanical specimens',
                    'Transit of Venus observations'
                ]),
                'scientific_contributions': json.dumps([
                    '3,000+ plant specimens',
                    '1,000+ animal specimens',
                    'Astronomical observations',
                    'Cartographic achievements'
                ]),
                'historical_significance_score': 95.0,
                'major_events_count': 8,
                'home_port': 'Plymouth',
                'tonnage': 368,
                'crew_size': 94,
                'data_completeness_score': 92.0,
                'wikipedia_url': 'https://en.wikipedia.org/wiki/HMS_Endeavour'
            },
            {
                'name': 'Discovery',
                'full_designation': 'HMS Discovery',
                'prefix': 'HMS',
                'nation': 'United Kingdom',
                'ship_type': 'exploration',
                'launch_year': 1901,
                'decommission_year': 1979,
                'era': 'steam_era',
                'primary_purpose': 'Antarctic exploration',
                'famous_voyages': json.dumps([
                    'Discovery Expedition (1901-1904) - Scott\'s first Antarctic expedition',
                    'Multiple Antarctic relief missions',
                    'Arctic research voyages'
                ]),
                'notable_crew_members': json.dumps([
                    'Robert Falcon Scott (captain)',
                    'Ernest Shackleton',
                    'Edward Wilson (scientist)'
                ]),
                'major_discoveries': json.dumps([
                    'Discovery of Antarctic Plateau',
                    'Extensive magnetic measurements',
                    'Antarctic wildlife documentation',
                    'Geological specimens'
                ]),
                'historical_significance_score': 88.0,
                'major_events_count': 6,
                'tonnage': 1570,
                'crew_size': 47,
                'data_completeness_score': 90.0,
                'wikipedia_url': 'https://en.wikipedia.org/wiki/RRS_Discovery'
            },
            {
                'name': 'Resolution',
                'full_designation': 'HMS Resolution',
                'prefix': 'HMS',
                'nation': 'United Kingdom',
                'ship_type': 'exploration',
                'launch_year': 1771,
                'decommission_year': 1782,
                'era': 'age_of_sail',
                'primary_purpose': 'Pacific exploration',
                'famous_voyages': json.dumps([
                    'Second Cook voyage (1772-1775) - Antarctic Circle crossing',
                    'Third Cook voyage (1776-1780) - Pacific Northwest'
                ]),
                'notable_crew_members': json.dumps([
                    'Captain James Cook',
                    'William Bligh (sailing master)'
                ]),
                'major_discoveries': json.dumps([
                    'First crossing of Antarctic Circle',
                    'Discovery of numerous Pacific islands',
                    'Mapping of Pacific Northwest',
                    'Disproved existence of Terra Australis'
                ]),
                'historical_significance_score': 90.0,
                'major_events_count': 7,
                'tonnage': 462,
                'crew_size': 112,
                'data_completeness_score': 88.0,
                'wikipedia_url': 'https://en.wikipedia.org/wiki/HMS_Resolution_(1771)'
            },
            
            # SAINT-NAMED SHIPS (Control Group)
            {
                'name': 'Santa Maria',
                'full_designation': 'Santa María',
                'prefix': None,
                'nation': 'Spain',
                'ship_type': 'exploration',
                'launch_year': 1460,
                'decommission_year': 1492,
                'era': 'age_of_discovery',
                'primary_purpose': 'Transatlantic exploration',
                'famous_voyages': json.dumps([
                    'Columbus first voyage to Americas (1492)'
                ]),
                'notable_crew_members': json.dumps([
                    'Christopher Columbus (captain-general)'
                ]),
                'major_discoveries': json.dumps([
                    'European discovery of the Americas',
                    'Landing in the Bahamas'
                ]),
                'historical_significance_score': 96.0,
                'major_events_count': 3,
                'was_sunk': True,
                'sunk_year': 1492,
                'sunk_reason': 'Grounded on reef, Christmas Day',
                'sunk_location': 'Hispaniola coast',
                'tonnage': 108,
                'crew_size': 40,
                'data_completeness_score': 75.0,
                'wikipedia_url': 'https://en.wikipedia.org/wiki/Santa_Mar%C3%ADa_(ship)'
            },
            {
                'name': 'San Salvador',
                'full_designation': 'San Salvador',
                'prefix': None,
                'nation': 'Spain',
                'ship_type': 'exploration',
                'launch_year': 1541,
                'decommission_year': 1543,
                'era': 'age_of_discovery',
                'primary_purpose': 'Pacific exploration',
                'famous_voyages': json.dumps([
                    'Cabrillo expedition (1542-1543) - California coast'
                ]),
                'notable_crew_members': json.dumps([
                    'Juan Rodríguez Cabrillo (captain)'
                ]),
                'major_discoveries': json.dumps([
                    'First European exploration of California coast',
                    'Discovery of San Diego Bay'
                ]),
                'historical_significance_score': 72.0,
                'major_events_count': 3,
                'tonnage': 200,
                'crew_size': 65,
                'data_completeness_score': 70.0,
                'wikipedia_url': 'https://en.wikipedia.org/wiki/San_Salvador_(Cabrillo)'
            },
            
            # NAVAL WARSHIPS - Geographic Names
            {
                'name': 'Constitution',
                'full_designation': 'USS Constitution',
                'prefix': 'USS',
                'nation': 'United States',
                'ship_type': 'naval',
                'ship_class': 'Constitution-class frigate',
                'launch_year': 1797,
                'era': 'age_of_sail',
                'primary_purpose': 'Naval warfare',
                'famous_voyages': json.dumps([
                    'War of 1812',
                    'Barbary Wars',
                    'Mediterranean patrols'
                ]),
                'battles_participated': 33,
                'battles_won': 31,
                'ships_sunk': 5,
                'notable_achievements': json.dumps([
                    'Defeated HMS Guerriere (1812)',
                    'Defeated HMS Java (1812)',
                    'Never defeated in battle',
                    'Oldest commissioned warship still afloat'
                ]),
                'historical_significance_score': 94.0,
                'major_events_count': 12,
                'home_port': 'Boston',
                'tonnage': 2200,
                'crew_size': 450,
                'armament': '44 guns',
                'years_active': 226,
                'data_completeness_score': 95.0,
                'wikipedia_url': 'https://en.wikipedia.org/wiki/USS_Constitution'
            },
            {
                'name': 'Enterprise',
                'full_designation': 'USS Enterprise (CV-6)',
                'prefix': 'USS',
                'nation': 'United States',
                'ship_type': 'naval',
                'ship_class': 'Yorktown-class aircraft carrier',
                'launch_year': 1936,
                'decommission_year': 1947,
                'era': 'modern',
                'primary_purpose': 'Aircraft carrier operations',
                'battles_participated': 20,
                'battles_won': 18,
                'notable_achievements': json.dumps([
                    'Most decorated US ship of WWII',
                    '20 battle stars',
                    'Battle of Midway',
                    'Guadalcanal campaign',
                    'Philippine Sea',
                    'Leyte Gulf'
                ]),
                'historical_significance_score': 97.0,
                'major_events_count': 20,
                'tonnage': 19800,
                'crew_size': 2200,
                'years_active': 11,
                'data_completeness_score': 93.0,
                'wikipedia_url': 'https://en.wikipedia.org/wiki/USS_Enterprise_(CV-6)'
            },
            {
                'name': 'Victory',
                'full_designation': 'HMS Victory',
                'prefix': 'HMS',
                'nation': 'United Kingdom',
                'ship_type': 'naval',
                'ship_class': 'First-rate ship of the line',
                'launch_year': 1765,
                'era': 'age_of_sail',
                'primary_purpose': 'Naval warfare',
                'battles_participated': 15,
                'battles_won': 13,
                'famous_voyages': json.dumps([
                    'Battle of Trafalgar (1805)',
                    'French Revolutionary Wars',
                    'Napoleonic Wars'
                ]),
                'notable_crew_members': json.dumps([
                    'Admiral Horatio Nelson (flag)',
                    'Thomas Hardy (captain)'
                ]),
                'notable_achievements': json.dumps([
                    'Nelson\'s flagship at Trafalgar',
                    'Decisive victory over Franco-Spanish fleet',
                    'Oldest naval ship still in commission',
                    'British naval supremacy established'
                ]),
                'historical_significance_score': 98.0,
                'major_events_count': 15,
                'tonnage': 3500,
                'crew_size': 850,
                'armament': '104 guns',
                'years_active': 260,
                'data_completeness_score': 96.0,
                'wikipedia_url': 'https://en.wikipedia.org/wiki/HMS_Victory'
            },
            {
                'name': 'Arizona',
                'full_designation': 'USS Arizona (BB-39)',
                'prefix': 'USS',
                'nation': 'United States',
                'ship_type': 'naval',
                'ship_class': 'Pennsylvania-class battleship',
                'launch_year': 1915,
                'decommission_year': 1941,
                'era': 'modern',
                'primary_purpose': 'Naval warfare',
                'historical_significance_score': 92.0,
                'major_events_count': 2,
                'notable_achievements': json.dumps([
                    'Pearl Harbor attack symbol',
                    'Memorial and war graves',
                    'Catalyst for US WWII entry'
                ]),
                'was_sunk': True,
                'sunk_year': 1941,
                'sunk_reason': 'Japanese aerial attack at Pearl Harbor',
                'sunk_location': 'Pearl Harbor, Hawaii',
                'crew_casualties': 1177,
                'tonnage': 31400,
                'crew_size': 1731,
                'armament': '12x 14-inch guns',
                'years_active': 26,
                'data_completeness_score': 94.0,
                'wikipedia_url': 'https://en.wikipedia.org/wiki/USS_Arizona_(BB-39)'
            },
            
            # COMMERCIAL & PASSENGER SHIPS
            {
                'name': 'Titanic',
                'full_designation': 'RMS Titanic',
                'prefix': 'RMS',
                'nation': 'United Kingdom',
                'ship_type': 'passenger',
                'ship_class': 'Olympic-class ocean liner',
                'launch_year': 1911,
                'decommission_year': 1912,
                'era': 'steam_era',
                'primary_purpose': 'Transatlantic passenger service',
                'historical_significance_score': 95.0,
                'major_events_count': 1,
                'famous_voyages': json.dumps([
                    'Maiden voyage: Southampton to New York (April 10-15, 1912)'
                ]),
                'was_sunk': True,
                'sunk_year': 1912,
                'sunk_reason': 'Collision with iceberg',
                'sunk_location': 'North Atlantic, 41.73°N 49.95°W',
                'crew_casualties': 1517,
                'tonnage': 52310,
                'crew_size': 2224,
                'years_active': 1,
                'data_completeness_score': 98.0,
                'wikipedia_url': 'https://en.wikipedia.org/wiki/RMS_Titanic'
            },
            {
                'name': 'Mayflower',
                'full_designation': 'Mayflower',
                'prefix': None,
                'nation': 'England',
                'ship_type': 'commercial',
                'launch_year': 1609,
                'decommission_year': 1622,
                'era': 'age_of_sail',
                'primary_purpose': 'Cargo and passenger transport',
                'famous_voyages': json.dumps([
                    'Pilgrim voyage to Plymouth, Massachusetts (1620)'
                ]),
                'historical_significance_score': 94.0,
                'major_events_count': 2,
                'notable_achievements': json.dumps([
                    'Transported Pilgrims to New World',
                    'Foundation of Plymouth Colony',
                    'Mayflower Compact signed aboard',
                    'American colonial history symbol'
                ]),
                'tonnage': 180,
                'crew_size': 130,
                'years_active': 13,
                'data_completeness_score': 82.0,
                'wikipedia_url': 'https://en.wikipedia.org/wiki/Mayflower'
            },
            {
                'name': 'Bounty',
                'full_designation': 'HMS Bounty',
                'prefix': 'HMS',
                'nation': 'United Kingdom',
                'ship_type': 'naval',
                'launch_year': 1784,
                'decommission_year': 1790,
                'era': 'age_of_sail',
                'primary_purpose': 'Transport breadfruit from Tahiti',
                'famous_voyages': json.dumps([
                    'Breadfruit expedition to Tahiti (1787-1789)'
                ]),
                'notable_crew_members': json.dumps([
                    'Captain William Bligh',
                    'Fletcher Christian (master\'s mate)'
                ]),
                'major_events_count': 2,
                'notable_achievements': json.dumps([
                    'Famous mutiny (1789)',
                    'Captain Bligh\'s open boat navigation',
                    'Historical and cultural impact'
                ]),
                'historical_significance_score': 78.0,
                'was_sunk': True,
                'sunk_year': 1790,
                'sunk_reason': 'Burned by mutineers at Pitcairn Island',
                'tonnage': 215,
                'crew_size': 46,
                'years_active': 6,
                'data_completeness_score': 88.0,
                'wikipedia_url': 'https://en.wikipedia.org/wiki/HMS_Bounty'
            },
        ]
    
    def _populate_ship_from_dict(self, ship: Ship, data: Dict):
        """Populate Ship model from dictionary data with rich historical details."""
        ship.name = data['name']
        ship.full_designation = data.get('full_designation') or f"{data.get('prefix', '')} {data['name']}".strip()
        ship.prefix = data.get('prefix')
        ship.nation = data['nation']
        ship.ship_type = data['ship_type']
        ship.ship_class = data.get('ship_class')
        ship.launch_year = data.get('launch_year')
        ship.decommission_year = data.get('decommission_year')
        ship.era = data['era']
        ship.era_decade = (data.get('launch_year', 0) // 10) * 10 if data.get('launch_year') else None
        
        # Calculate years active
        if data.get('years_active'):
            ship.years_active = data['years_active']
        elif data.get('launch_year') and data.get('decommission_year'):
            ship.years_active = data['decommission_year'] - data['launch_year']
        elif data.get('launch_year') and not data.get('was_sunk'):
            ship.years_active = datetime.now().year - data['launch_year']
        
        # Achievement metrics
        ship.historical_significance_score = data.get('historical_significance_score', 50.0)
        ship.major_events_count = data.get('major_events_count', 0)
        
        # Battle data (for naval ships)
        ship.battles_participated = data.get('battles_participated', 0)
        ship.battles_won = data.get('battles_won', 0)
        ship.ships_sunk = data.get('ships_sunk', 0)
        
        # Rich historical data (serialize as JSON)
        if 'major_discoveries' in data:
            ship.major_discoveries = json.dumps(data['major_discoveries']) if isinstance(data['major_discoveries'], list) else data['major_discoveries']
        
        if 'famous_voyages' in data:
            ship.famous_voyages = json.dumps(data['famous_voyages']) if isinstance(data['famous_voyages'], list) else data['famous_voyages']
        
        if 'scientific_contributions' in data:
            ship.scientific_contributions = json.dumps(data['scientific_contributions']) if isinstance(data['scientific_contributions'], list) else data['scientific_contributions']
        
        if 'notable_crew_members' in data:
            ship.notable_crew_members = json.dumps(data['notable_crew_members']) if isinstance(data['notable_crew_members'], list) else data['notable_crew_members']
        
        if 'notable_achievements' in data:
            ship.notable_achievements = json.dumps(data['notable_achievements']) if isinstance(data['notable_achievements'], list) else data['notable_achievements']
        
        if 'awards_decorations' in data:
            ship.awards_decorations = json.dumps(data['awards_decorations']) if isinstance(data['awards_decorations'], list) else data['awards_decorations']
        
        # Mission data
        ship.primary_purpose = data.get('primary_purpose')
        ship.secondary_purposes = data.get('secondary_purposes')
        
        # Geographic data
        ship.home_port = data.get('home_port')
        ship.primary_theater = data.get('primary_theater')
        
        if 'regions_operated' in data:
            ship.regions_operated = json.dumps(data['regions_operated']) if isinstance(data['regions_operated'], list) else data['regions_operated']
        
        # Physical specifications
        ship.tonnage = data.get('tonnage')
        ship.crew_size = data.get('crew_size')
        ship.armament = data.get('armament')
        
        # Casualties
        ship.crew_casualties = data.get('crew_casualties', 0)
        
        # Failure tracking
        ship.was_sunk = data.get('was_sunk', False)
        ship.sunk_year = data.get('sunk_year')
        ship.sunk_reason = data.get('sunk_reason')
        ship.sunk_location = data.get('sunk_location')
        
        # Categorize name
        name_cat = self._categorize_ship_name(ship.name)
        ship.name_category = name_cat['category']
        ship.geographic_origin = name_cat.get('geographic_origin')
        
        # Geocode if geographic
        if name_cat['category'] == 'geographic' and name_cat.get('geographic_origin'):
            geocode_result = self._geocode_place(name_cat['geographic_origin'])
            if geocode_result:
                ship.geographic_lat = geocode_result['lat']
                ship.geographic_lon = geocode_result['lon']
                ship.place_type = geocode_result.get('type')
                ship.place_cultural_prestige_score = self._get_place_prestige(
                    name_cat['geographic_origin']
                )
        
        ship.data_completeness_score = data.get('data_completeness_score', 50.0)
        ship.primary_source = data.get('primary_source', 'Manual curation')
        ship.wikipedia_url = data.get('wikipedia_url')
    
    def _categorize_ship_name(self, name: str) -> Dict:
        """Categorize ship name into geographic/saint/monarch/virtue/etc.
        
        This is the core function for testing the geographic vs saint hypothesis.
        
        Args:
            name: Ship name (without prefix like HMS, USS)
            
        Returns:
            Dictionary with category and details
        """
        name_lower = name.lower().strip()
        
        # Check for saint names - EXPANDED DETECTION
        # Direct saint prefix check
        for prefix in self.saint_prefixes:
            if name_lower.startswith(prefix):
                return {
                    'category': 'saint',
                    'saint_name': name_lower.replace(prefix, '').strip(),
                    'geographic_origin': None
                }
        
        # Check for Portuguese São, Spanish/French patterns
        if name_lower.startswith('são ') or name_lower.startswith('sainte '):
            return {
                'category': 'saint',
                'saint_name': name_lower.split()[1] if len(name_lower.split()) > 1 else name_lower,
                'geographic_origin': None
            }
        
        # Check for saint name patterns even without prefix
        saint_indicators = ['nossa senhora', 'nuestra señora', 'santa maria', 'san miguel', 'são']
        if any(indicator in name_lower for indicator in saint_indicators):
            return {
                'category': 'saint',
                'saint_name': name_lower,
                'geographic_origin': None
            }
        
        # Check for geographic names
        for place in self.place_names:
            if place in name_lower:
                return {
                    'category': 'geographic',
                    'geographic_origin': place.title(),
                    'place_name': place
                }
        
        # Check for virtue names
        virtues = ['victory', 'enterprise', 'endeavour', 'resolution', 'discovery',
                   'courage', 'valiant', 'intrepid', 'defiance', 'triumph', 'glory',
                   'liberty', 'freedom', 'independence', 'vigilance', 'perseverance']
        if name_lower in virtues:
            return {
                'category': 'virtue',
                'virtue_name': name,
                'geographic_origin': None
            }
        
        # Check for mythological names
        mythological = ['zeus', 'athena', 'apollo', 'hercules', 'titan', 'olympus',
                       'poseidon', 'neptune', 'mars', 'mercury', 'jupiter', 'venus']
        if name_lower in mythological:
            return {
                'category': 'mythological',
                'mythological_name': name,
                'geographic_origin': None
            }
        
        # Check for animal names
        animals = ['beagle', 'eagle', 'falcon', 'hawk', 'wolf', 'bear', 'lion',
                  'tiger', 'leopard', 'panther', 'shark', 'dolphin', 'whale']
        if name_lower in animals:
            return {
                'category': 'animal',
                'animal_name': name,
                'geographic_origin': None
            }
        
        # Check for monarch names
        monarchs = ['queen', 'king', 'prince', 'princess', 'duke', 'duchess',
                   'elizabeth', 'victoria', 'george', 'william', 'charles', 'henry',
                   'mary', 'anne', 'edward', 'richard', 'james']
        if any(monarch in name_lower for monarch in monarchs):
            return {
                'category': 'monarch',
                'monarch_name': name,
                'geographic_origin': None
            }
        
        # Default to 'other'
        return {
            'category': 'other',
            'geographic_origin': None
        }
    
    def _geocode_place(self, place_name: str) -> Optional[Dict]:
        """Geocode a place name to lat/lon coordinates."""
        # Check cache first
        if place_name in self.geocode_cache:
            return self.geocode_cache[place_name]
        
        try:
            time.sleep(self.geocode_delay)
            location = self.geolocator.geocode(place_name)
            
            if location:
                result = {
                    'lat': location.latitude,
                    'lon': location.longitude,
                    'type': location.raw.get('type', 'unknown')
                }
                self.geocode_cache[place_name] = result
                return result
            
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            logger.warning(f"Geocoding failed for {place_name}: {e}")
        
        return None
    
    def _get_place_prestige(self, place_name: str) -> float:
        """Get cultural prestige score for a place name."""
        place_lower = place_name.lower()
        
        # Check predefined prestige scores
        for place, score in self.place_prestige.items():
            if place in place_lower:
                return score
        
        # Default prestige based on type
        if place_lower in self.place_names:
            # US states get moderate prestige
            us_states = {'california', 'texas', 'florida', 'new york', 'massachusetts'}
            if place_lower in us_states:
                return 65.0
            # Other major cities
            return 55.0
        
        return 50.0  # Default
    
    def _analyze_ship_name(self, ship: Ship):
        """Perform comprehensive linguistic analysis on ship name.
        
        Args:
            ship: Ship object to analyze
        """
        try:
            name = ship.name
            
            # Check if analysis exists
            existing = ShipAnalysis.query.filter_by(ship_id=ship.id).first()
            if existing:
                analysis = existing
            else:
                analysis = ShipAnalysis(ship_id=ship.id)
            
            # Standard name analysis
            name_metrics = self.name_analyzer.analyze_name(name)
            
            analysis.syllable_count = name_metrics.get('syllable_count', 0)
            analysis.character_length = name_metrics.get('character_length', 0)
            analysis.word_count = name_metrics.get('word_count', 0)
            analysis.phonetic_score = name_metrics.get('phonetic_score', 0)
            analysis.vowel_ratio = name_metrics.get('vowel_ratio', 0)
            analysis.consonant_clusters = name_metrics.get('consonant_clusters', 0)
            analysis.memorability_score = name_metrics.get('memorability_score', 0)
            analysis.pronounceability_score = name_metrics.get('pronounceability_score', 0)
            analysis.uniqueness_score = name_metrics.get('uniqueness_score', 0)
            analysis.name_type = name_metrics.get('name_type', 'Unknown')
            
            # Categorization
            name_cat = self._categorize_ship_name(name)
            analysis.name_category = name_cat['category']
            analysis.is_geographic_name = (name_cat['category'] == 'geographic')
            analysis.is_saint_name = (name_cat['category'] == 'saint')
            analysis.is_monarch_name = (name_cat['category'] == 'monarch')
            analysis.is_virtue_name = (name_cat['category'] == 'virtue')
            analysis.is_mythological_name = (name_cat['category'] == 'mythological')
            analysis.is_animal_name = (name_cat['category'] == 'animal')
            
            if name_cat.get('geographic_origin'):
                analysis.geographic_origin_name = name_cat['geographic_origin']
                analysis.geographic_specificity = self._get_geographic_specificity(
                    name_cat['geographic_origin']
                )
                analysis.geographic_cultural_importance = self._get_place_prestige(
                    name_cat['geographic_origin']
                )
            
            if name_cat.get('saint_name'):
                analysis.saint_name = name_cat['saint_name']
            
            # Phonemic analysis
            phonemic_results = self.phonemic_analyzer.analyze(name)
            analysis.harshness_score = phonemic_results.get('harshness_score', 0)
            analysis.softness_score = phonemic_results.get('softness_score', 0)
            analysis.plosive_ratio = phonemic_results.get('plosive_ratio', 0)
            analysis.fricative_ratio = phonemic_results.get('fricative_ratio', 0)
            analysis.voicing_ratio = phonemic_results.get('voicing_ratio', 0)
            analysis.phonosemantic_data = json.dumps(phonemic_results)
            
            # Semantic analysis
            semantic_results = self.semantic_analyzer.analyze(name)
            analysis.power_connotation_score = semantic_results.get('power_score', 0)
            analysis.prestige_score = semantic_results.get('prestige_score', 0)
            analysis.semantic_data = json.dumps(semantic_results)
            
            # Advanced analysis
            advanced_results = self.advanced_analyzer.analyze(name)
            analysis.authority_score = advanced_results.get('authority_score', 0)
            analysis.intellectual_sophistication_score = advanced_results.get('sophistication_score', 0)
            analysis.phonestheme_score = advanced_results.get('phonestheme_score', 0)
            analysis.vowel_brightness = advanced_results.get('vowel_brightness', 0)
            analysis.consonant_hardness = advanced_results.get('consonant_hardness', 0)
            
            # Calculate semantic alignment score
            alignment_result = self._calculate_semantic_alignment(ship)
            analysis.semantic_alignment_score = alignment_result['score']
            analysis.semantic_alignment_explanation = alignment_result['explanation']
            analysis.nominative_determinism_data = json.dumps(alignment_result.get('details', {}))
            
            # Save analysis
            if not existing:
                db.session.add(analysis)
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error analyzing ship name '{ship.name}': {e}")
            db.session.rollback()
    
    def _get_geographic_specificity(self, place_name: str) -> str:
        """Determine specificity of geographic name (city/region/country)."""
        place_lower = place_name.lower()
        
        # Major cities
        cities = {'london', 'paris', 'rome', 'berlin', 'vienna', 'boston', 'new york',
                 'philadelphia', 'san francisco', 'chicago', 'sydney', 'tokyo'}
        if place_lower in cities:
            return 'city'
        
        # Countries
        countries = {'america', 'england', 'france', 'spain', 'italy', 'germany',
                    'russia', 'china', 'japan', 'australia', 'canada'}
        if place_lower in countries:
            return 'country'
        
        # US States
        if any(state in place_lower for state in ['york', 'jersey', 'carolina', 'dakota', 'virginia']):
            return 'region'
        
        # Default
        return 'region'
    
    def _calculate_semantic_alignment(self, ship: Ship) -> Dict:
        """Calculate how well ship's name aligns with its achievements.
        
        This is the core nominative determinism test.
        
        Args:
            ship: Ship object with historical data
            
        Returns:
            Dictionary with alignment score and explanation
        """
        name = ship.name.lower()
        score = 50.0  # Baseline
        explanation_parts = []
        details = {}
        
        # Beagle case: animal name → carried naturalist → evolution theory
        if 'beagle' in name:
            if ship.notable_crew_members and 'darwin' in ship.notable_crew_members.lower():
                score += 40
                explanation_parts.append("Beagle (dog breed) → carried Darwin → natural selection theory (biological connection)")
                details['darwin_beagle_connection'] = True
            if ship.scientific_contributions and 'evolution' in ship.scientific_contributions.lower():
                score += 10
                explanation_parts.append("Scientific contributions to evolutionary theory")
        
        # Victory → actually victorious in battles
        if 'victory' in name and ship.battles_won and ship.battles_won > 10:
            score += 30
            explanation_parts.append(f"'Victory' name → {ship.battles_won} battles won")
            details['victory_battles_won'] = ship.battles_won
        
        # Enterprise → enterprising missions/achievements
        if 'enterprise' in name and ship.major_events_count and ship.major_events_count > 15:
            score += 25
            explanation_parts.append(f"'Enterprise' name → {ship.major_events_count} major accomplishments")
        
        # Endeavour → exploration endeavours
        if 'endeavour' in name or 'endeavor' in name:
            if ship.ship_type == 'exploration':
                score += 20
                explanation_parts.append("'Endeavour' name → exploration missions")
            if ship.major_discoveries:
                score += 15
                explanation_parts.append("Major discoveries made")
        
        # Discovery → actual discoveries
        if 'discovery' in name and ship.major_discoveries:
            discoveries = json.loads(ship.major_discoveries) if isinstance(ship.major_discoveries, str) else ship.major_discoveries
            if discoveries and len(discoveries) > 2:
                score += 30
                explanation_parts.append(f"'Discovery' name → {len(discoveries)} major discoveries")
                details['discoveries_count'] = len(discoveries)
        
        # Resolution → resolute missions
        if 'resolution' in name:
            if ship.famous_voyages:
                voyages = json.loads(ship.famous_voyages) if isinstance(ship.famous_voyages, str) else ship.famous_voyages
                if voyages and len(voyages) > 1:
                    score += 20
                    explanation_parts.append("'Resolution' name → multiple completed voyages")
        
        # Geographic names → operated in that region
        if ship.name_category == 'geographic' and ship.geographic_origin:
            # Check if ship operated in region matching its name
            if ship.primary_theater and ship.geographic_origin.lower() in ship.primary_theater.lower():
                score += 25
                explanation_parts.append(f"Named after {ship.geographic_origin}, operated in that region")
                details['geographic_theater_match'] = True
        
        # Constitution → long-lasting, constitutional strength
        if 'constitution' in name and ship.years_active and ship.years_active > 100:
            score += 35
            explanation_parts.append(f"'Constitution' name → {ship.years_active} years of service (constitutional longevity)")
        
        # Cap score at 100
        score = min(100, score)
        
        explanation = " | ".join(explanation_parts) if explanation_parts else "No significant semantic alignment detected"
        
        return {
            'score': round(score, 2),
            'explanation': explanation,
            'details': details
        }


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    from flask import Flask
    from core.config import Config
    
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        
        collector = ShipCollector()
        stats = collector.collect_bootstrap_ships()
        
        print("\n" + "="*70)
        print("COLLECTION COMPLETE")
        print("="*70)
        print(f"Ships added: {stats['ships_added']}")
        print(f"Ships updated: {stats['ships_updated']}")
        print(f"Ships analyzed: {stats['ships_analyzed']}")
        print(f"Errors: {stats['errors']}")
        print("="*70)

