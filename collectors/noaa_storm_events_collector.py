"""NOAA Storm Events Database Collector

Automated collection of hurricane casualty and damage data from NOAA API.
API Documentation: https://www.ncdc.noaa.gov/stormevents/

Focus on avoidable devastation metrics:
- Direct vs. indirect deaths
- Injuries
- Displaced persons
- Property damage
- Power outages
"""

import logging
import time
from datetime import datetime
from typing import Dict, List, Optional

import requests

from core.models import Hurricane, db

logger = logging.getLogger(__name__)


class NOAAStormEventsCollector:
    """Collect hurricane outcome data from NOAA Storm Events Database."""
    
    def __init__(self):
        self.base_url = "https://www.ncei.noaa.gov/access/services/data/v1"
        self.dataset = "storm-events"
        self.rate_limit_delay = 0.5  # Be respectful to NOAA servers
    
    def enrich_hurricane_outcomes(self, hurricane_id: str) -> Dict:
        """Enrich a single hurricane with NOAA Storm Events data.
        
        Args:
            hurricane_id: NOAA storm ID (e.g., 'AL092005' for Katrina)
        
        Returns:
            Dictionary with enrichment statistics
        """
        hurricane = Hurricane.query.get(hurricane_id)
        if not hurricane:
            logger.warning(f"Hurricane {hurricane_id} not found in database")
            return {'success': False, 'error': 'Hurricane not found'}
        
        try:
            # Query NOAA API for this storm
            events = self._fetch_storm_events(hurricane.name, hurricane.year, hurricane.landfall_state)
            
            if not events:
                logger.info(f"No NOAA Storm Events data found for {hurricane.name} ({hurricane.year})")
                return {'success': True, 'events_found': 0, 'enriched': False}
            
            # Aggregate outcomes across all events for this storm
            outcomes = self._aggregate_outcomes(events)
            
            # Update hurricane record
            hurricane.deaths_direct = outcomes.get('deaths_direct')
            hurricane.deaths_indirect = outcomes.get('deaths_indirect')
            hurricane.deaths = outcomes.get('deaths_total')
            hurricane.injuries = outcomes.get('injuries')
            hurricane.damage_usd = outcomes.get('damage_usd')
            hurricane.homes_destroyed = outcomes.get('homes_destroyed')
            hurricane.homes_damaged = outcomes.get('homes_damaged')
            hurricane.power_outages_peak = outcomes.get('power_outages')
            hurricane.last_updated = datetime.utcnow()
            
            db.session.commit()
            
            logger.info(f"✅ Enriched {hurricane.name} ({hurricane.year}): "
                       f"{outcomes.get('deaths_total', 0)} deaths, "
                       f"{outcomes.get('injuries', 0)} injuries, "
                       f"${outcomes.get('damage_usd', 0):,.0f} damage")
            
            return {
                'success': True,
                'events_found': len(events),
                'enriched': True,
                'outcomes': outcomes
            }
        
        except Exception as e:
            logger.error(f"Error enriching {hurricane_id}: {e}")
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    def enrich_all_hurricanes(self, limit: Optional[int] = None) -> Dict:
        """Enrich all hurricanes in database with NOAA data.
        
        Args:
            limit: Maximum number of hurricanes to enrich (for testing)
        
        Returns:
            Statistics dictionary
        """
        stats = {
            'total_hurricanes': 0,
            'enriched': 0,
            'skipped_no_data': 0,
            'errors': 0,
            'total_events': 0
        }
        
        # Get all hurricanes, prioritize those without outcome data
        query = Hurricane.query.order_by(
            Hurricane.deaths.is_(None).desc(),
            Hurricane.year.desc()
        )
        
        if limit:
            query = query.limit(limit)
        
        hurricanes = query.all()
        stats['total_hurricanes'] = len(hurricanes)
        
        logger.info(f"Starting NOAA enrichment for {len(hurricanes)} hurricanes...")
        
        for idx, hurricane in enumerate(hurricanes):
            if idx > 0 and idx % 10 == 0:
                logger.info(f"  Progress: {idx}/{len(hurricanes)} hurricanes processed...")
                time.sleep(2)  # Extra pause every 10 requests
            
            result = self.enrich_hurricane_outcomes(hurricane.id)
            
            if result['success']:
                if result.get('enriched'):
                    stats['enriched'] += 1
                    stats['total_events'] += result.get('events_found', 0)
                else:
                    stats['skipped_no_data'] += 1
            else:
                stats['errors'] += 1
            
            time.sleep(self.rate_limit_delay)
        
        logger.info(f"\n{'='*60}")
        logger.info("✅ NOAA ENRICHMENT COMPLETE")
        logger.info(f"{'='*60}")
        logger.info(f"Total hurricanes processed: {stats['total_hurricanes']}")
        logger.info(f"Successfully enriched: {stats['enriched']}")
        logger.info(f"No data available: {stats['skipped_no_data']}")
        logger.info(f"Errors: {stats['errors']}")
        logger.info(f"Total storm events found: {stats['total_events']}")
        
        return stats
    
    def _fetch_storm_events(self, storm_name: str, year: int, state: Optional[str] = None) -> List[Dict]:
        """Fetch storm events from NOAA API.
        
        Args:
            storm_name: Hurricane name (e.g., 'Katrina')
            year: Year of storm
            state: Landfall state (optional, for filtering)
        
        Returns:
            List of event dictionaries
        """
        try:
            # NOAA Storm Events API parameters
            params = {
                'dataset': 'storm-events',
                'dataTypes': 'details',
                'stations': '',
                'startDate': f'{year}-01-01',
                'endDate': f'{year}-12-31',
                'boundingBox': '',  # Could add geographic bounds
                'format': 'json'
            }
            
            # Note: NOAA API might not support direct filtering by storm name
            # May need to fetch all hurricane events for that year and filter locally
            
            response = requests.get(f"{self.base_url}", params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Filter events matching this storm name
            events = []
            for event in data.get('results', []):
                # Check if event mentions storm name in description
                event_name = event.get('EPISODE_NARRATIVE', '') + event.get('EVENT_NARRATIVE', '')
                if storm_name.lower() in event_name.lower():
                    events.append(event)
            
            return events
        
        except requests.exceptions.RequestException as e:
            logger.error(f"NOAA API request failed for {storm_name} ({year}): {e}")
            return []
        except Exception as e:
            logger.error(f"Error parsing NOAA data for {storm_name}: {e}")
            return []
    
    def _aggregate_outcomes(self, events: List[Dict]) -> Dict:
        """Aggregate outcomes across multiple storm events.
        
        Args:
            events: List of NOAA storm event records
        
        Returns:
            Dictionary with aggregated outcomes
        """
        outcomes = {
            'deaths_direct': 0,
            'deaths_indirect': 0,
            'deaths_total': 0,
            'injuries': 0,
            'damage_usd': 0.0,
            'homes_destroyed': 0,
            'homes_damaged': 0,
            'power_outages': 0
        }
        
        for event in events:
            # Deaths
            deaths_direct = event.get('DEATHS_DIRECT', 0) or 0
            deaths_indirect = event.get('DEATHS_INDIRECT', 0) or 0
            outcomes['deaths_direct'] += deaths_direct
            outcomes['deaths_indirect'] += deaths_indirect
            
            # Injuries
            outcomes['injuries'] += event.get('INJURIES_DIRECT', 0) or 0
            outcomes['injuries'] += event.get('INJURIES_INDIRECT', 0) or 0
            
            # Damage (convert from string format like "$1.5M" to float)
            damage_property = self._parse_damage(event.get('DAMAGE_PROPERTY', '0'))
            damage_crops = self._parse_damage(event.get('DAMAGE_CROPS', '0'))
            outcomes['damage_usd'] += damage_property + damage_crops
        
        outcomes['deaths_total'] = outcomes['deaths_direct'] + outcomes['deaths_indirect']
        
        return outcomes
    
    def _parse_damage(self, damage_str: str) -> float:
        """Parse NOAA damage string to float USD.
        
        Args:
            damage_str: Damage string like '1.5M', '250K', '5.0B'
        
        Returns:
            Damage in USD as float
        """
        if not damage_str or damage_str == '0':
            return 0.0
        
        try:
            damage_str = str(damage_str).upper().strip()
            
            # Remove any currency symbols or commas
            damage_str = damage_str.replace('$', '').replace(',', '')
            
            # Parse multiplier
            multiplier = 1
            if 'K' in damage_str:
                multiplier = 1_000
                damage_str = damage_str.replace('K', '')
            elif 'M' in damage_str:
                multiplier = 1_000_000
                damage_str = damage_str.replace('M', '')
            elif 'B' in damage_str:
                multiplier = 1_000_000_000
                damage_str = damage_str.replace('B', '')
            
            # Convert to float
            value = float(damage_str) * multiplier
            return value
        
        except (ValueError, AttributeError) as e:
            logger.warning(f"Could not parse damage string '{damage_str}': {e}")
            return 0.0



