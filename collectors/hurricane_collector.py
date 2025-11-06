"""Hurricane Data Collector

Collects hurricane data from NOAA HURDAT2 database and NOAA Storm Events Database.
Focuses on named storms with landfall to test nominative determinism effects on outcomes.
"""

import csv
import logging
import re
from datetime import datetime
from io import StringIO
from typing import Dict, List, Optional

import requests

from analyzers.name_analyzer import NameAnalyzer
from core.models import Hurricane, HurricaneAnalysis, db

logger = logging.getLogger(__name__)


class HurricaneCollector:
    """Collect and analyze hurricane data from NOAA sources."""
    
    def __init__(self):
        self.analyzer = NameAnalyzer()
        self.hurdat2_atlantic_url = "https://www.nhc.noaa.gov/data/hurdat/hurdat2-1851-2023-051124.txt"
        self.hurdat2_pacific_url = "https://www.nhc.noaa.gov/data/hurdat/hurdat2-nepac-1949-2023-051124.txt"
        
        # CPI adjustment factors (2023 baseline)
        self.cpi_adjustments = self._load_cpi_data()
    
    def collect_all_hurricanes(self, min_year=1950, require_landfall=True, min_category=None):
        """Collect hurricanes from HURDAT2 database with outcome data.
        
        Args:
            min_year: Minimum year (earlier data often incomplete)
            require_landfall: Only include storms that made landfall
            min_category: Minimum Saffir-Simpson category (None = include tropical storms)
        
        Returns:
            Collection statistics
        """
        stats = {
            'requested_min_year': min_year,
            'storms_processed': 0,
            'storms_added': 0,
            'storms_updated': 0,
            'skipped_no_name': 0,
            'skipped_no_landfall': 0,
            'skipped_year': 0,
            'skipped_category': 0,
            'errors': 0
        }
        
        try:
            # Collect Atlantic basin
            logger.info("Fetching Atlantic basin hurricanes...")
            atlantic_storms = self._fetch_hurdat2_data(self.hurdat2_atlantic_url, 'AL')
            stats['storms_processed'] += len(atlantic_storms)
            
            # Collect Pacific basin
            logger.info("Fetching Pacific basin hurricanes...")
            pacific_storms = self._fetch_hurdat2_data(self.hurdat2_pacific_url, 'EP')
            stats['storms_processed'] += len(pacific_storms)
            
            all_storms = atlantic_storms + pacific_storms
            logger.info(f"Retrieved {len(all_storms)} total storms from HURDAT2")
            
            # Collect all storm names for uniqueness analysis
            all_storm_names = [s['name'] for s in all_storms if s.get('name')]
            
            # Process and save each storm
            for storm in all_storms:
                try:
                    # Apply filters
                    if not storm.get('name') or storm['name'] in ('UNNAMED', 'UNKNOWN'):
                        stats['skipped_no_name'] += 1
                        continue
                    
                    if storm.get('year', 0) < min_year:
                        stats['skipped_year'] += 1
                        continue
                    
                    if require_landfall and not storm.get('landfall_flag'):
                        stats['skipped_no_landfall'] += 1
                        continue
                    
                    if min_category is not None:
                        cat = storm.get('saffir_simpson_category')
                        if cat is None or cat < min_category:
                            stats['skipped_category'] += 1
                            continue
                    
                    # Check if storm already exists
                    existing = Hurricane.query.get(storm['id'])
                    
                    if existing:
                        # Update existing
                        self._update_hurricane(existing, storm)
                        stats['storms_updated'] += 1
                        hurricane_record = existing
                    else:
                        # Create new
                        hurricane_record = self._create_hurricane(storm)
                        stats['storms_added'] += 1
                    
                    db.session.flush()
                    
                    # Create or update analysis
                    self._analyze_hurricane_name(hurricane_record, all_storm_names)
                    
                except Exception as e:
                    logger.error(f"Error processing storm {storm.get('id', 'unknown')}: {e}")
                    stats['errors'] += 1
                    db.session.rollback()
                    continue
            
            db.session.commit()
            stats['total_in_db'] = Hurricane.query.count()
            
            logger.info(f"✅ Hurricane collection complete: {stats['storms_added']} added, {stats['storms_updated']} updated")
            return stats
        
        except Exception as e:
            logger.error(f"Hurricane collection error: {e}")
            db.session.rollback()
            stats['error'] = str(e)
            return stats
    
    def _fetch_hurdat2_data(self, url: str, basin_code: str) -> List[Dict]:
        """Fetch and parse HURDAT2 format data."""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            storms = []
            current_storm = None
            
            lines = response.text.strip().split('\n')
            
            for line in lines:
                # Header line format: AL092005,KATRINA,33
                if re.match(r'^[A-Z]{2}\d+', line):
                    if current_storm:
                        storms.append(current_storm)
                    
                    parts = [p.strip() for p in line.split(',')]
                    storm_id = parts[0]
                    name = parts[1] if len(parts) > 1 else 'UNNAMED'
                    
                    # Extract year from ID (last 4 digits)
                    year_match = re.search(r'(\d{4})$', storm_id)
                    year = int(year_match.group(1)) if year_match else None
                    
                    current_storm = {
                        'id': storm_id,
                        'name': name,
                        'year': year,
                        'basin': basin_code,
                        'max_wind_kts': 0,
                        'min_pressure_mb': 9999,
                        'landfall_flag': False,
                        'landfall_date': None,
                        'landfall_state': None,
                        'data_points': []
                    }
                else:
                    # Data line format: date, time, record_id, status, lat, lon, wind, pressure, ...
                    if current_storm:
                        parts = [p.strip() for p in line.split(',')]
                        if len(parts) >= 8:
                            try:
                                wind_kts = int(parts[6]) if parts[6] and parts[6] != '-999' else 0
                                pressure_mb = int(parts[7]) if parts[7] and parts[7] != '-999' else 9999
                                
                                # Track maximum intensity
                                if wind_kts > current_storm['max_wind_kts']:
                                    current_storm['max_wind_kts'] = wind_kts
                                if pressure_mb < current_storm['min_pressure_mb'] and pressure_mb > 0:
                                    current_storm['min_pressure_mb'] = pressure_mb
                                
                                # Check for landfall indicator (status = 'L' or 'LF')
                                status = parts[3].strip()
                                if 'L' in status:
                                    current_storm['landfall_flag'] = True
                                    if not current_storm['landfall_date']:
                                        date_str = parts[0]
                                        current_storm['landfall_date'] = datetime.strptime(date_str, '%Y%m%d').date()
                            except (ValueError, IndexError):
                                continue
            
            # Don't forget last storm
            if current_storm:
                storms.append(current_storm)
            
            # Calculate Saffir-Simpson category and convert knots to mph
            for storm in storms:
                wind_kts = storm['max_wind_kts']
                storm['max_wind_mph'] = int(wind_kts * 1.151) if wind_kts else None
                storm['saffir_simpson_category'] = self._wind_to_category(wind_kts)
            
            logger.info(f"Parsed {len(storms)} storms from {basin_code} basin")
            return storms
        
        except Exception as e:
            logger.error(f"HURDAT2 fetch error for {basin_code}: {e}")
            return []
    
    def _wind_to_category(self, wind_kts: int) -> Optional[int]:
        """Convert max sustained wind to Saffir-Simpson category."""
        if wind_kts < 64:
            return None  # Tropical storm or depression
        elif wind_kts < 83:
            return 1
        elif wind_kts < 96:
            return 2
        elif wind_kts < 113:
            return 3
        elif wind_kts < 137:
            return 4
        else:
            return 5
    
    def _create_hurricane(self, storm_data: Dict) -> Hurricane:
        """Create new Hurricane record."""
        hurricane = Hurricane(
            id=storm_data['id'],
            name=storm_data['name'],
            year=storm_data['year'],
            basin=storm_data['basin'],
            max_wind_mph=storm_data.get('max_wind_mph'),
            max_wind_kts=storm_data.get('max_wind_kts'),
            min_pressure_mb=storm_data.get('min_pressure_mb') if storm_data.get('min_pressure_mb', 9999) < 9999 else None,
            saffir_simpson_category=storm_data.get('saffir_simpson_category'),
            landfall_date=storm_data.get('landfall_date'),
            landfall_state=storm_data.get('landfall_state')
        )
        db.session.add(hurricane)
        return hurricane
    
    def _update_hurricane(self, hurricane: Hurricane, storm_data: Dict):
        """Update existing Hurricane record."""
        hurricane.max_wind_mph = storm_data.get('max_wind_mph')
        hurricane.max_wind_kts = storm_data.get('max_wind_kts')
        hurricane.min_pressure_mb = storm_data.get('min_pressure_mb') if storm_data.get('min_pressure_mb', 9999) < 9999 else None
        hurricane.saffir_simpson_category = storm_data.get('saffir_simpson_category')
        hurricane.landfall_date = storm_data.get('landfall_date')
        hurricane.landfall_state = storm_data.get('landfall_state')
    
    def _analyze_hurricane_name(self, hurricane: Hurricane, all_names: List[str]):
        """Analyze hurricane name with standard + hurricane-specific metrics."""
        # Get standard name analysis
        standard_analysis = self.analyzer.analyze_name(hurricane.name, all_names)
        
        # Calculate hurricane-specific metrics
        harshness_score = self._calculate_phonetic_harshness(hurricane.name)
        gender = self._infer_gender_coding(hurricane.name, hurricane.year)
        sentiment = self._calculate_sentiment_polarity(hurricane.name)
        alpha_pos = ord(hurricane.name[0].upper()) - ord('A') + 1 if hurricane.name else None
        
        # Check if analysis already exists
        existing_analysis = HurricaneAnalysis.query.filter_by(hurricane_id=hurricane.id).first()
        
        if existing_analysis:
            # Update
            existing_analysis.syllable_count = standard_analysis.get('syllable_count')
            existing_analysis.character_length = standard_analysis.get('character_length')
            existing_analysis.word_count = standard_analysis.get('word_count')
            existing_analysis.phonetic_score = standard_analysis.get('phonetic_score')
            existing_analysis.vowel_ratio = standard_analysis.get('vowel_ratio')
            existing_analysis.memorability_score = standard_analysis.get('memorability_score')
            existing_analysis.pronounceability_score = standard_analysis.get('pronounceability_score')
            existing_analysis.uniqueness_score = standard_analysis.get('uniqueness_score')
            existing_analysis.name_type = standard_analysis.get('name_type')
            existing_analysis.phonetic_harshness_score = harshness_score
            existing_analysis.gender_coded = gender
            existing_analysis.sentiment_polarity = sentiment
            existing_analysis.alphabetical_position = alpha_pos
        else:
            # Create new
            analysis = HurricaneAnalysis(
                hurricane_id=hurricane.id,
                syllable_count=standard_analysis.get('syllable_count'),
                character_length=standard_analysis.get('character_length'),
                word_count=standard_analysis.get('word_count'),
                phonetic_score=standard_analysis.get('phonetic_score'),
                vowel_ratio=standard_analysis.get('vowel_ratio'),
                memorability_score=standard_analysis.get('memorability_score'),
                pronounceability_score=standard_analysis.get('pronounceability_score'),
                uniqueness_score=standard_analysis.get('uniqueness_score'),
                name_type=standard_analysis.get('name_type'),
                phonetic_harshness_score=harshness_score,
                gender_coded=gender,
                sentiment_polarity=sentiment,
                alphabetical_position=alpha_pos
            )
            db.session.add(analysis)
    
    def _calculate_phonetic_harshness(self, name: str) -> float:
        """Calculate phonetic harshness based on consonant types.
        
        Plosives (hard stops): p, b, t, d, k, g = HIGH harshness
        Fricatives (friction): f, v, s, z, sh, th = MEDIUM harshness
        Nasals/liquids: m, n, l, r = LOW harshness
        Vowels: a, e, i, o, u = SOFT (negative harshness)
        
        Returns score 0-100 (higher = harsher, more aggressive sounding)
        """
        name_lower = name.lower()
        
        plosives = sum(name_lower.count(c) for c in 'pbtdkg')
        fricatives = sum(name_lower.count(c) for c in 'fvsz')
        nasals = sum(name_lower.count(c) for c in 'mnlr')
        vowels = sum(name_lower.count(c) for c in 'aeiou')
        
        total_chars = len(re.sub(r'[^a-zA-Z]', '', name))
        if total_chars == 0:
            return 50.0
        
        # Weighted scoring
        harshness_score = (
            (plosives * 100 / total_chars * 3.0) +  # Plosives heavily weighted
            (fricatives * 100 / total_chars * 2.0) +  # Fricatives medium weight
            (nasals * 100 / total_chars * 0.5) -  # Nasals reduce harshness
            (vowels * 100 / total_chars * 1.0)  # Vowels soften
        )
        
        # Normalize to 0-100 range
        normalized = max(0, min(100, harshness_score + 50))
        return round(normalized, 2)
    
    def _infer_gender_coding(self, name: str, year: int) -> str:
        """Infer gender coding of hurricane name.
        
        Pre-1979: All female names
        1979+: Alternating male/female (determined by alphabetical position in season)
        """
        if year < 1979:
            return 'female'
        
        # Common gendered names for classification
        male_names = {
            'andrew', 'bob', 'dennis', 'floyd', 'georges', 'hugo', 'ivan', 'michael',
            'wilma', 'dean', 'felix', 'gustav', 'ike', 'karl', 'otto', 'philippe',
            'richard', 'tomas', 'vince', 'alex', 'bill', 'colin', 'don', 'earl',
            'gaston', 'hernan', 'joaquin', 'larry', 'marco', 'nate', 'omar', 'peter',
            'rafael', 'sam', 'tony', 'victor', 'waldo', 'barry', 'chantal', 'danny',
            'fred', 'gordon', 'harvey', 'jose', 'lee', 'matthew', 'newton', 'ian'
        }
        
        female_names = {
            'katrina', 'rita', 'wilma', 'emily', 'isabel', 'frances', 'jeanne',
            'charley', 'ophelia', 'maria', 'irma', 'nora', 'grace', 'ida', 'fiona',
            'nicole', 'lisa', 'julia', 'bonnie', 'danielle', 'earl', 'karen',
            'sandy', 'erin', 'gabrielle', 'hanna', 'josephine', 'laura', 'sally',
            'bertha', 'cristobal', 'dolly', 'edouard', 'alma', 'andrea', 'cindy'
        }
        
        name_lower = name.lower()
        
        if name_lower in male_names:
            return 'male'
        elif name_lower in female_names:
            return 'female'
        else:
            # Use ending heuristic
            if name_lower.endswith(('a', 'e', 'ie', 'y', 'ette', 'ine')):
                return 'female'
            elif name_lower.endswith(('o', 'us', 'er', 'on')):
                return 'male'
            else:
                return 'ambiguous'
    
    def _calculate_sentiment_polarity(self, name: str) -> float:
        """Calculate sentiment polarity of name.
        
        Returns: -1.0 (very negative) to +1.0 (very positive)
        """
        name_lower = name.lower()
        
        positive_words = {'belle', 'grace', 'hope', 'joy', 'star', 'sunny', 'happy', 'victor', 'win'}
        negative_words = {'bad', 'evil', 'doom', 'grim', 'dark', 'death', 'destroy', 'wreck'}
        
        positive_count = sum(1 for word in positive_words if word in name_lower)
        negative_count = sum(1 for word in negative_words if word in name_lower)
        
        if positive_count == 0 and negative_count == 0:
            return 0.0  # Neutral
        
        # Simple sentiment score
        score = (positive_count - negative_count) / max(positive_count + negative_count, 1)
        return round(score, 2)
    
    def enrich_with_outcome_data(self, storm_id: str, deaths: int = None, injuries: int = None, 
                                  damage_usd: float = None, damage_year: int = None,
                                  fema_aid: float = None):
        """Manually enrich a hurricane with outcome data.
        
        Args:
            storm_id: NOAA storm ID
            deaths: Casualty count
            injuries: Injury count
            damage_usd: Damage in USD (will be inflation-adjusted)
            damage_year: Year of damage estimate
            fema_aid: FEMA disaster aid total
        """
        try:
            hurricane = Hurricane.query.get(storm_id)
            if not hurricane:
                logger.error(f"Hurricane {storm_id} not found")
                return False
            
            hurricane.deaths = deaths
            hurricane.injuries = injuries
            
            if damage_usd and damage_year:
                # Adjust to 2023 dollars
                adjusted_damage = self._adjust_for_inflation(damage_usd, damage_year)
                hurricane.damage_usd = adjusted_damage
                hurricane.damage_usd_year = damage_year
            
            hurricane.fema_aid_usd = fema_aid
            
            db.session.commit()
            logger.info(f"✅ Enriched {hurricane.name} ({hurricane.year}) with outcome data")
            return True
        
        except Exception as e:
            logger.error(f"Error enriching storm {storm_id}: {e}")
            db.session.rollback()
            return False
    
    def _adjust_for_inflation(self, amount: float, year: int) -> float:
        """Adjust dollar amount to 2023 baseline using CPI."""
        if year not in self.cpi_adjustments:
            # Use linear interpolation or nearest year
            logger.warning(f"No CPI data for {year}, using nearest year approximation")
            nearest_year = min(self.cpi_adjustments.keys(), key=lambda y: abs(y - year))
            year = nearest_year
        
        multiplier = self.cpi_adjustments.get(2023, 1.0) / self.cpi_adjustments.get(year, 1.0)
        return amount * multiplier
    
    def _load_cpi_data(self) -> Dict[int, float]:
        """Load CPI adjustment factors (simplified - using approximate values)."""
        # CPI-U Annual averages (1950-2023, baseline 2023 = 100)
        # Real implementation would fetch from BLS API
        return {
            1950: 24.1, 1960: 29.6, 1970: 38.8, 1980: 82.4, 1990: 130.7,
            2000: 172.2, 2005: 195.3, 2010: 218.1, 2015: 237.0, 2020: 258.8,
            2021: 271.0, 2022: 292.7, 2023: 304.7
        }
    
    def bootstrap_major_hurricanes(self):
        """Bootstrap database with well-documented major hurricanes and outcome data."""
        logger.info("Bootstrapping major hurricanes with known outcome data...")
        
        # Well-documented major hurricanes with verified casualty/damage data
        major_storms = [
            {
                'name': 'Katrina', 'year': 2005, 'deaths': 1833, 'injuries': None,
                'damage_usd': 125000000000, 'fema_aid': 120500000000,
                'notes': 'Category 5, New Orleans flooding'
            },
            {
                'name': 'Andrew', 'year': 1992, 'deaths': 65, 'injuries': None,
                'damage_usd': 27300000000, 'fema_aid': 1400000000,
                'notes': 'Category 5, South Florida'
            },
            {
                'name': 'Maria', 'year': 2017, 'deaths': 2975, 'injuries': None,
                'damage_usd': 91610000000, 'fema_aid': 23000000000,
                'notes': 'Category 5, Puerto Rico devastation'
            },
            {
                'name': 'Harvey', 'year': 2017, 'deaths': 68, 'injuries': None,
                'damage_usd': 125000000000, 'fema_aid': 13000000000,
                'notes': 'Category 4, Houston flooding'
            },
            {
                'name': 'Irma', 'year': 2017, 'deaths': 134, 'injuries': None,
                'damage_usd': 77160000000, 'fema_aid': 4800000000,
                'notes': 'Category 5, Florida Keys'
            },
            {
                'name': 'Sandy', 'year': 2012, 'deaths': 233, 'injuries': None,
                'damage_usd': 70200000000, 'fema_aid': 16000000000,
                'notes': 'Post-tropical, New York/New Jersey'
            },
            {
                'name': 'Ike', 'year': 2008, 'deaths': 195, 'injuries': None,
                'damage_usd': 38000000000, 'fema_aid': 2600000000,
                'notes': 'Category 4, Texas/Louisiana'
            },
            {
                'name': 'Wilma', 'year': 2005, 'deaths': 52, 'injuries': None,
                'damage_usd': 29400000000, 'fema_aid': 800000000,
                'notes': 'Category 5, lowest pressure on record'
            },
            {
                'name': 'Ivan', 'year': 2004, 'deaths': 92, 'injuries': None,
                'damage_usd': 26100000000, 'fema_aid': 1800000000,
                'notes': 'Category 5, Alabama/Florida'
            },
            {
                'name': 'Charley', 'year': 2004, 'deaths': 35, 'injuries': None,
                'damage_usd': 16900000000, 'fema_aid': 1100000000,
                'notes': 'Category 4, Southwest Florida'
            },
            {
                'name': 'Rita', 'year': 2005, 'deaths': 120, 'injuries': None,
                'damage_usd': 23700000000, 'fema_aid': 1500000000,
                'notes': 'Category 5, Texas/Louisiana'
            },
            {
                'name': 'Hugo', 'year': 1989, 'deaths': 61, 'injuries': None,
                'damage_usd': 10000000000, 'fema_aid': 1500000000,
                'notes': 'Category 5, South Carolina'
            },
            {
                'name': 'Michael', 'year': 2018, 'deaths': 74, 'injuries': None,
                'damage_usd': 25100000000, 'fema_aid': 1600000000,
                'notes': 'Category 5, Florida Panhandle'
            },
            {
                'name': 'Florence', 'year': 2018, 'deaths': 53, 'injuries': None,
                'damage_usd': 24200000000, 'fema_aid': 1200000000,
                'notes': 'Category 4, Carolinas'
            },
            {
                'name': 'Camille', 'year': 1969, 'deaths': 259, 'injuries': None,
                'damage_usd': 1420000000, 'fema_aid': None,
                'notes': 'Category 5, Mississippi'
            },
        ]
        
        enriched_count = 0
        for storm in major_storms:
            # Find storm in database by name and year
            hurricane = Hurricane.query.filter_by(name=storm['name'].upper(), year=storm['year']).first()
            
            if hurricane:
                success = self.enrich_with_outcome_data(
                    hurricane.id,
                    deaths=storm['deaths'],
                    injuries=storm['injuries'],
                    damage_usd=storm['damage_usd'],
                    damage_year=storm['year'],
                    fema_aid=storm.get('fema_aid')
                )
                if success:
                    enriched_count += 1
            else:
                logger.warning(f"Could not find {storm['name']} ({storm['year']}) in database")
        
        logger.info(f"✅ Bootstrapped {enriched_count} major hurricanes with outcome data")
        return {'enriched': enriched_count, 'total_attempted': len(major_storms)}

