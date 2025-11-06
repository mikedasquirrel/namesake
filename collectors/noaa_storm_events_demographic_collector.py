"""NOAA Storm Events Demographic Collector

Collects county-level hurricane casualty and damage data from NOAA Storm Events Database.
Links outcomes to demographic data for demographic-specific impact analysis.

Data Source: NOAA National Centers for Environmental Information (NCEI)
API: https://www.ncdc.noaa.gov/stormevents/
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

import requests

from core.models import (
    Hurricane, HurricaneDemographicImpact, HurricaneGeography,
    GeographicDemographics, db
)

logger = logging.getLogger(__name__)


class NOAAStormEventsCollector:
    """Collect NOAA Storm Events data for hurricane impacts."""
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize collector.
        
        Args:
            token: NOAA NCEI API token (get free at https://www.ncdc.noaa.gov/cdo-web/token)
        """
        self.token = token
        self.base_url = "https://www.ncdc.noaa.gov/stormevents/csv"
        self.rate_limit_delay = 1.0 if token else 2.0
    
    def collect_events_for_hurricane(self, hurricane_id: str) -> Dict:
        """
        Collect Storm Events data for a specific hurricane.
        
        Args:
            hurricane_id: Hurricane ID
        
        Returns:
            Statistics dict
        """
        hurricane = Hurricane.query.get(hurricane_id)
        if not hurricane:
            logger.error(f"Hurricane {hurricane_id} not found")
            return {'success': False, 'error': 'Hurricane not found'}
        
        stats = {
            'hurricane_id': hurricane_id,
            'hurricane_name': hurricane.name,
            'year': hurricane.year,
            'events_found': 0,
            'counties_with_data': 0,
            'total_deaths': 0,
            'total_injuries': 0,
            'total_damage': 0.0,
            'success': False
        }
        
        try:
            # Get time window for this hurricane (±7 days from landfall)
            if not hurricane.landfall_date:
                logger.warning(f"No landfall date for {hurricane.name} ({hurricane.year})")
                # Use year as fallback
                start_date = datetime(hurricane.year, 1, 1).date()
                end_date = datetime(hurricane.year, 12, 31).date()
            else:
                start_date = hurricane.landfall_date - timedelta(days=7)
                end_date = hurricane.landfall_date + timedelta(days=14)  # Extended for indirect impacts
            
            # Fetch storm events
            events = self._fetch_storm_events(
                hurricane.name,
                start_date,
                end_date
            )
            
            stats['events_found'] = len(events)
            
            if not events:
                logger.info(f"No storm events found for {hurricane.name} ({hurricane.year})")
                stats['success'] = True
                return stats
            
            # Group events by county
            county_events = self._group_by_county(events)
            stats['counties_with_data'] = len(county_events)
            
            # Process each county's events
            for county_fips, county_data in county_events.items():
                self._process_county_events(hurricane_id, county_fips, county_data, stats)
            
            db.session.commit()
            
            stats['success'] = True
            logger.info(f"✅ NOAA events for {hurricane.name} ({hurricane.year}): "
                       f"{stats['events_found']} events across {stats['counties_with_data']} counties")
            
            return stats
            
        except Exception as e:
            logger.error(f"Error collecting NOAA events for {hurricane_id}: {e}")
            db.session.rollback()
            stats['error'] = str(e)
            return stats
    
    def _fetch_storm_events(self, storm_name: str, start_date, end_date) -> List[Dict]:
        """
        Fetch storm events from NOAA database.
        
        Note: NOAA Storm Events Database doesn't have a public REST API.
        Data is available as bulk CSV downloads by state/year.
        
        For a production system, would need to:
        1. Download and cache CSV files
        2. Parse locally
        3. Or use alternative data source
        
        This is a placeholder implementation showing the structure.
        
        Args:
            storm_name: Hurricane name
            start_date: Start date
            end_date: End date
        
        Returns:
            List of event dicts
        """
        # Placeholder - NOAA Storm Events requires CSV download and parsing
        # Real implementation would download state CSVs and parse
        
        logger.warning("NOAA Storm Events API not implemented - requires CSV download/parsing")
        logger.info(f"Would search for '{storm_name}' between {start_date} and {end_date}")
        
        # Return empty list - this would be populated from CSV parsing
        return []
    
    def _parse_storm_events_csv(self, csv_path: str, storm_name: str, 
                                 start_date, end_date) -> List[Dict]:
        """
        Parse NOAA Storm Events CSV file.
        
        CSV columns include:
        - BEGIN_DATE, END_DATE
        - STATE, STATE_FIPS, CZ_TYPE, CZ_FIPS (county zone)
        - EVENT_TYPE (Hurricane, Tropical Storm, etc.)
        - DEATHS_DIRECT, DEATHS_INDIRECT
        - INJURIES_DIRECT, INJURIES_INDIRECT
        - DAMAGE_PROPERTY, DAMAGE_CROPS
        - EVENT_NARRATIVE
        
        Args:
            csv_path: Path to downloaded CSV file
            storm_name: Hurricane name to filter
            start_date: Start date
            end_date: End date
        
        Returns:
            List of event dicts
        """
        import csv
        
        events = []
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    # Filter by event type
                    event_type = row.get('EVENT_TYPE', '')
                    if 'Hurricane' not in event_type and 'Tropical Storm' not in event_type:
                        continue
                    
                    # Filter by date range
                    try:
                        begin_date = datetime.strptime(row.get('BEGIN_DATE', ''), '%Y-%m-%d').date()
                        if begin_date < start_date or begin_date > end_date:
                            continue
                    except ValueError:
                        continue
                    
                    # Filter by storm name (check narrative)
                    narrative = row.get('EVENT_NARRATIVE', '').lower()
                    if storm_name.lower() not in narrative:
                        # Also check episode narrative
                        episode_narrative = row.get('EPISODE_NARRATIVE', '').lower()
                        if storm_name.lower() not in episode_narrative:
                            continue
                    
                    # Extract data
                    event = {
                        'state_fips': row.get('STATE_FIPS', ''),
                        'county_fips': row.get('CZ_FIPS', ''),
                        'cz_type': row.get('CZ_TYPE', ''),
                        'begin_date': begin_date,
                        'deaths_direct': int(row.get('DEATHS_DIRECT', 0) or 0),
                        'deaths_indirect': int(row.get('DEATHS_INDIRECT', 0) or 0),
                        'injuries_direct': int(row.get('INJURIES_DIRECT', 0) or 0),
                        'injuries_indirect': int(row.get('INJURIES_INDIRECT', 0) or 0),
                        'damage_property': self._parse_damage(row.get('DAMAGE_PROPERTY', '0')),
                        'damage_crops': self._parse_damage(row.get('DAMAGE_CROPS', '0')),
                    }
                    
                    events.append(event)
            
            return events
            
        except Exception as e:
            logger.error(f"Error parsing Storm Events CSV: {e}")
            return []
    
    def _parse_damage(self, damage_str: str) -> float:
        """
        Parse NOAA damage string (e.g., '10.00K', '1.50M', '0.50B').
        
        Args:
            damage_str: Damage string from CSV
        
        Returns:
            Damage in USD
        """
        if not damage_str or damage_str == '0':
            return 0.0
        
        try:
            # Remove any whitespace
            damage_str = damage_str.strip().upper()
            
            # Extract multiplier
            multipliers = {
                'K': 1_000,
                'M': 1_000_000,
                'B': 1_000_000_000
            }
            
            multiplier = 1.0
            for suffix, mult in multipliers.items():
                if damage_str.endswith(suffix):
                    multiplier = mult
                    damage_str = damage_str[:-1]
                    break
            
            value = float(damage_str)
            return value * multiplier
            
        except ValueError:
            return 0.0
    
    def _group_by_county(self, events: List[Dict]) -> Dict[str, Dict]:
        """
        Group storm events by county FIPS code.
        
        Args:
            events: List of event dicts
        
        Returns:
            Dict mapping county FIPS to aggregated data
        """
        county_data = {}
        
        for event in events:
            state_fips = event.get('state_fips', '')
            county_fips = event.get('county_fips', '')
            
            if not state_fips or not county_fips:
                continue
            
            # Handle zone type - only process county zones (CZ_TYPE == 'C')
            if event.get('cz_type') != 'C':
                continue
            
            # Create full FIPS code
            full_fips = f"{state_fips}{county_fips.zfill(3)}"
            
            if full_fips not in county_data:
                county_data[full_fips] = {
                    'fips': full_fips,
                    'state_fips': state_fips,
                    'county_fips': county_fips.zfill(3),
                    'events': [],
                    'total_deaths_direct': 0,
                    'total_deaths_indirect': 0,
                    'total_injuries_direct': 0,
                    'total_injuries_indirect': 0,
                    'total_damage': 0.0
                }
            
            # Add event and aggregate totals
            county_data[full_fips]['events'].append(event)
            county_data[full_fips]['total_deaths_direct'] += event.get('deaths_direct', 0)
            county_data[full_fips]['total_deaths_indirect'] += event.get('deaths_indirect', 0)
            county_data[full_fips]['total_injuries_direct'] += event.get('injuries_direct', 0)
            county_data[full_fips]['total_injuries_indirect'] += event.get('injuries_indirect', 0)
            county_data[full_fips]['total_damage'] += event.get('damage_property', 0) + event.get('damage_crops', 0)
        
        return county_data
    
    def _process_county_events(self, hurricane_id: str, county_fips: str, 
                                county_data: Dict, stats: Dict):
        """
        Process county-level storm events and create/update demographic impact records.
        
        Args:
            hurricane_id: Hurricane ID
            county_fips: County FIPS code
            county_data: Aggregated county event data
            stats: Statistics dict to update
        """
        try:
            # Get demographics for this county
            demographics = GeographicDemographics.query.filter_by(
                geographic_code=county_fips,
                geographic_level='county'
            ).order_by(GeographicDemographics.year.desc()).first()
            
            # Calculate totals
            total_deaths = county_data['total_deaths_direct'] + county_data['total_deaths_indirect']
            total_injuries = county_data['total_injuries_direct'] + county_data['total_injuries_indirect']
            total_damage = county_data['total_damage']
            
            # Check if aggregate record already exists
            existing = HurricaneDemographicImpact.query.filter_by(
                hurricane_id=hurricane_id,
                geographic_code=county_fips,
                geographic_level='county',
                demographic_category='total',
                demographic_value='all'
            ).first()
            
            population = demographics.total_population if demographics else None
            
            if existing:
                # Update existing record
                existing.deaths = total_deaths
                existing.injuries = total_injuries
                existing.damage_estimate_usd = total_damage
                existing.population_at_risk = population
                if population and total_deaths:
                    existing.death_rate_per_1000 = (total_deaths / population) * 1000
                
                # Merge data sources
                sources = existing.data_source.split(',') if existing.data_source else []
                if 'NOAA_STORM_EVENTS' not in sources:
                    sources.append('NOAA_STORM_EVENTS')
                existing.data_source = ','.join(sources)
                
            else:
                # Create new record
                impact = HurricaneDemographicImpact(
                    hurricane_id=hurricane_id,
                    geographic_code=county_fips,
                    geographic_level='county',
                    demographic_category='total',
                    demographic_value='all',
                    population_at_risk=population,
                    deaths=total_deaths,
                    injuries=total_injuries,
                    damage_estimate_usd=total_damage,
                    death_rate_per_1000=(total_deaths / population * 1000) if population and total_deaths else None,
                    data_source='NOAA_STORM_EVENTS',
                    confidence_level='high'  # NOAA data is authoritative
                )
                db.session.add(impact)
            
            # Update stats
            stats['total_deaths'] += total_deaths
            stats['total_injuries'] += total_injuries
            stats['total_damage'] += total_damage
            
        except Exception as e:
            logger.error(f"Error processing county events for {county_fips}: {e}")

