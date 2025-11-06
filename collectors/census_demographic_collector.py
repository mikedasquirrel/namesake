"""Census Demographic Data Collector

Fetches demographic data from the U.S. Census Bureau API for geographic areas
affected by hurricanes. Uses American Community Survey (ACS) 5-year estimates
for recent data and Decennial Census for historical baselines.

Data Sources:
- ACS 5-Year Estimates (2009-present): Detailed demographics
- Decennial Census (1950-2020): Historical baselines
- API Documentation: https://www.census.gov/data/developers/data-sets.html
"""

import logging
import time
from datetime import datetime
from typing import Dict, List, Optional
import json

import requests

from core.models import GeographicDemographics, db

logger = logging.getLogger(__name__)


class CensusDemographicCollector:
    """Collect demographic data from Census Bureau API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize collector with Census API key.
        
        Args:
            api_key: Census API key (get free key at https://api.census.gov/data/key_signup.html)
                    If None, will attempt to use without key (limited rate)
        """
        self.api_key = api_key
        self.base_url = "https://api.census.gov/data"
        self.rate_limit_delay = 0.5 if api_key else 1.0  # Slower without key
        
        # ACS 5-year estimates variable codes
        self.acs_variables = {
            # Population totals
            'total_population': 'B01003_001E',
            
            # Race (Hispanic/Latino is separate in Census)
            'white_alone': 'B02001_002E',
            'black_alone': 'B02001_003E',
            'native_alone': 'B02001_004E',
            'asian_alone': 'B02001_005E',
            'pacific_alone': 'B02001_006E',
            'other_race': 'B02001_007E',
            'multiracial': 'B02001_008E',
            'hispanic_latino': 'B03003_003E',
            
            # Age groups
            'age_under_18': 'B01001_003E,B01001_004E,B01001_005E,B01001_006E,B01001_027E,B01001_028E,B01001_029E,B01001_030E',  # Sum these
            'age_18_34': 'B01001_007E,B01001_008E,B01001_009E,B01001_010E,B01001_031E,B01001_032E,B01001_033E,B01001_034E',
            'age_35_49': 'B01001_011E,B01001_012E,B01001_035E,B01001_036E',
            'age_50_64': 'B01001_013E,B01001_014E,B01001_037E,B01001_038E',
            'age_65_74': 'B01001_015E,B01001_016E,B01001_039E,B01001_040E',
            'age_75_plus': 'B01001_017E,B01001_018E,B01001_019E,B01001_020E,B01001_021E,B01001_022E,B01001_023E,B01001_024E,B01001_025E,B01001_041E,B01001_042E,B01001_043E,B01001_044E,B01001_045E,B01001_046E,B01001_047E,B01001_048E,B01001_049E',
            
            # Income
            'median_income': 'B19013_001E',
            'poverty_rate': 'B17001_002E',  # Need to divide by total for rate
            
            # Education
            'bachelors_plus': 'B15003_022E,B15003_023E,B15003_024E,B15003_025E',  # Sum these
            
            # Housing
            'homeownership_units': 'B25003_002E',  # Owner-occupied
            'total_housing_units': 'B25003_001E',
            'median_home_value': 'B25077_001E',
        }
    
    def collect_county_demographics(self, state_fips: str, county_fips: str, year: int = 2020) -> Optional[Dict]:
        """
        Collect demographic data for a specific county.
        
        Args:
            state_fips: 2-digit state FIPS code (e.g., '12' for Florida)
            county_fips: 3-digit county FIPS code (e.g., '086' for Miami-Dade)
            year: Census year (2009-2022 for ACS, 1950/1960/.../2020 for Decennial)
        
        Returns:
            Demographics dict or None if failed
        """
        geographic_code = f"{state_fips}{county_fips}"
        
        try:
            # Use ACS 5-year for recent data (most detailed)
            if year >= 2009:
                data = self._fetch_acs_5yr_data(state_fips, county_fips, year)
            else:
                # Use decennial census for historical data (less detailed)
                data = self._fetch_decennial_data(state_fips, county_fips, year)
            
            if not data:
                logger.warning(f"No demographic data found for county {geographic_code} in {year}")
                return None
            
            # Store in database
            existing = GeographicDemographics.query.filter_by(
                geographic_code=geographic_code,
                geographic_level='county',
                year=year
            ).first()
            
            if existing:
                # Update existing record
                self._update_demographics(existing, data)
                logger.debug(f"Updated demographics for county {geographic_code} ({year})")
            else:
                # Create new record
                demo = GeographicDemographics(
                    geographic_code=geographic_code,
                    geographic_level='county',
                    year=year,
                    **data
                )
                db.session.add(demo)
                logger.debug(f"Added demographics for county {geographic_code} ({year})")
            
            db.session.commit()
            time.sleep(self.rate_limit_delay)
            
            return data
            
        except Exception as e:
            logger.error(f"Error collecting demographics for county {geographic_code} ({year}): {e}")
            db.session.rollback()
            return None
    
    def collect_multiple_counties(self, counties: List[tuple], year: int = 2020) -> Dict:
        """
        Collect demographics for multiple counties.
        
        Args:
            counties: List of (state_fips, county_fips) tuples
            year: Census year
        
        Returns:
            Statistics dict
        """
        stats = {
            'total_requested': len(counties),
            'successful': 0,
            'failed': 0,
            'skipped_existing': 0
        }
        
        logger.info(f"Collecting demographics for {len(counties)} counties (year {year})...")
        
        for idx, (state_fips, county_fips) in enumerate(counties):
            if idx > 0 and idx % 10 == 0:
                logger.info(f"  Progress: {idx}/{len(counties)} counties processed")
            
            # Check if already exists
            geographic_code = f"{state_fips}{county_fips}"
            existing = GeographicDemographics.query.filter_by(
                geographic_code=geographic_code,
                geographic_level='county',
                year=year
            ).first()
            
            if existing:
                stats['skipped_existing'] += 1
                continue
            
            result = self.collect_county_demographics(state_fips, county_fips, year)
            
            if result:
                stats['successful'] += 1
            else:
                stats['failed'] += 1
        
        logger.info(f"✅ Demographics collection complete: {stats['successful']} collected, "
                   f"{stats['skipped_existing']} skipped (already exists), {stats['failed']} failed")
        
        return stats
    
    def _fetch_acs_5yr_data(self, state_fips: str, county_fips: str, year: int) -> Optional[Dict]:
        """Fetch ACS 5-year estimate data."""
        # ACS 5-year datasets available: 2009-2022
        if year > 2022:
            year = 2022  # Use most recent available
        elif year < 2009:
            logger.warning(f"ACS 5-year not available for {year}, using decennial instead")
            return self._fetch_decennial_data(state_fips, county_fips, year)
        
        # Build variable list (limit to 50 vars per request due to API limits)
        var_list = ','.join([
            self.acs_variables['total_population'],
            self.acs_variables['white_alone'],
            self.acs_variables['black_alone'],
            self.acs_variables['native_alone'],
            self.acs_variables['asian_alone'],
            self.acs_variables['pacific_alone'],
            self.acs_variables['other_race'],
            self.acs_variables['multiracial'],
            self.acs_variables['hispanic_latino'],
            self.acs_variables['median_income'],
            self.acs_variables['poverty_rate'],
            self.acs_variables['median_home_value'],
        ])
        
        url = f"{self.base_url}/{year}/acs/acs5"
        params = {
            'get': var_list,
            'for': f'county:{county_fips}',
            'in': f'state:{state_fips}',
        }
        
        if self.api_key:
            params['key'] = self.api_key
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if len(data) < 2:  # Header + data row
                return None
            
            # Parse response (first row is headers, second is data)
            headers = data[0]
            values = data[1]
            
            # Create dict from headers and values
            result_dict = dict(zip(headers, values))
            
            # Extract and format demographics
            demographics = self._parse_acs_response(result_dict, year)
            
            return demographics
            
        except requests.exceptions.RequestException as e:
            logger.error(f"ACS API request failed for {state_fips}/{county_fips} ({year}): {e}")
            return None
        except Exception as e:
            logger.error(f"Error parsing ACS data: {e}")
            return None
    
    def _fetch_decennial_data(self, state_fips: str, county_fips: str, year: int) -> Optional[Dict]:
        """Fetch Decennial Census data (simplified - fewer variables available)."""
        # Round to nearest census year
        census_years = [1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020]
        year = min(census_years, key=lambda y: abs(y - year))
        
        if year < 2000:
            # Historical census data requires different approach (NHGIS)
            # For now, return None and log - would need separate implementation
            logger.warning(f"Historical census data ({year}) requires NHGIS integration - not yet implemented")
            return None
        
        # Use Decennial Census API (available for 2000, 2010, 2020)
        # Much simpler schema than ACS
        var_list = 'P001001'  # Total population
        
        if year == 2020:
            url = f"{self.base_url}/{year}/dec/pl"  # 2020 uses redistricting data
        else:
            url = f"{self.base_url}/{year}/dec/sf1"  # 2000/2010 use SF1
        
        params = {
            'get': var_list,
            'for': f'county:{county_fips}',
            'in': f'state:{state_fips}',
        }
        
        if self.api_key:
            params['key'] = self.api_key
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if len(data) < 2:
                return None
            
            total_pop = int(data[1][0]) if data[1][0] not in ['-', None] else None
            
            # Decennial has limited data - just population
            demographics = {
                'total_population': total_pop,
                'race_breakdown': json.dumps({}),  # Limited race data in decennial
                'income_breakdown': json.dumps({}),
                'age_breakdown': json.dumps({}),
                'median_income': None,
                'poverty_rate': None,
                'education_bachelors_plus_pct': None,
                'homeownership_rate': None,
                'median_home_value': None,
                'source': f'DECENNIAL_{year}'
            }
            
            return demographics
            
        except Exception as e:
            logger.error(f"Decennial census request failed: {e}")
            return None
    
    def _parse_acs_response(self, data: Dict, year: int) -> Dict:
        """Parse ACS API response into our schema."""
        def safe_int(val):
            """Safely convert to int, handling null/negative values."""
            if val in [None, '', '-', 'null']:
                return None
            try:
                v = int(float(val))
                return v if v >= 0 else None
            except (ValueError, TypeError):
                return None
        
        def safe_float(val):
            """Safely convert to float."""
            if val in [None, '', '-', 'null']:
                return None
            try:
                return float(val)
            except (ValueError, TypeError):
                return None
        
        # Extract values
        total_pop = safe_int(data.get(self.acs_variables['total_population']))
        
        # Race breakdown
        race_breakdown = {
            'white': safe_int(data.get(self.acs_variables['white_alone'])),
            'black': safe_int(data.get(self.acs_variables['black_alone'])),
            'native': safe_int(data.get(self.acs_variables['native_alone'])),
            'asian': safe_int(data.get(self.acs_variables['asian_alone'])),
            'pacific': safe_int(data.get(self.acs_variables['pacific_alone'])),
            'other': safe_int(data.get(self.acs_variables['other_race'])),
            'multiracial': safe_int(data.get(self.acs_variables['multiracial'])),
            'hispanic_latino': safe_int(data.get(self.acs_variables['hispanic_latino'])),
        }
        
        # Income
        median_income = safe_float(data.get(self.acs_variables['median_income']))
        poverty_count = safe_int(data.get(self.acs_variables['poverty_rate']))
        poverty_rate = (poverty_count / total_pop * 100) if total_pop and poverty_count else None
        
        # Housing
        owner_occupied = safe_int(data.get(self.acs_variables['homeownership_units']))
        total_housing = safe_int(data.get(self.acs_variables['total_housing_units']))
        homeownership_rate = (owner_occupied / total_housing * 100) if total_housing and owner_occupied else None
        median_home_value = safe_float(data.get(self.acs_variables['median_home_value']))
        
        # Note: Age groups and income quintiles would require multiple API calls
        # or more complex variable aggregation - implement if needed
        
        return {
            'total_population': total_pop,
            'race_breakdown': json.dumps(race_breakdown),
            'income_breakdown': json.dumps({}),  # TODO: Implement income distribution
            'age_breakdown': json.dumps({}),  # TODO: Implement age aggregation
            'median_income': median_income,
            'poverty_rate': poverty_rate,
            'education_bachelors_plus_pct': None,  # TODO: Calculate from education variables
            'homeownership_rate': homeownership_rate,
            'median_home_value': median_home_value,
            'source': f'ACS_5YR_{year}'
        }
    
    def _update_demographics(self, record: GeographicDemographics, data: Dict):
        """Update existing demographic record with new data."""
        for key, value in data.items():
            if hasattr(record, key):
                setattr(record, key, value)
    
    def get_hurricane_affected_counties(self, hurricane_id: str) -> List[tuple]:
        """
        Get list of counties affected by a hurricane (from HurricaneGeography table).
        
        Args:
            hurricane_id: Hurricane ID
        
        Returns:
            List of (state_fips, county_fips) tuples
        """
        from core.models import HurricaneGeography
        
        geographies = HurricaneGeography.query.filter_by(
            hurricane_id=hurricane_id,
            geographic_level='county'
        ).all()
        
        counties = []
        for geo in geographies:
            if geo.state_fips and geo.county_fips:
                counties.append((geo.state_fips, geo.county_fips))
        
        return counties

