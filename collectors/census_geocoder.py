"""Census Geocoder and Population Controls

Geocode hurricane landfalls and join with Census data to get exposed population counts.
This is a crucial control variable - names might correlate with outcomes simply because
some storms hit more populated areas.

Data sources:
- Census Geocoding API
- Census population estimates (decennial + ACS)
"""

import logging
import time
from typing import Dict, Optional, Tuple

import requests

from core.models import Hurricane, db

logger = logging.getLogger(__name__)


class CensusGeocoder:
    """Geocode hurricane landfalls and enrich with population data."""
    
    def __init__(self):
        self.geocode_url = "https://geocoding.geo.census.gov/geocoder/geographies/address"
        self.pop_url = "https://api.census.gov/data"
        self.rate_limit_delay = 0.5
    
    def enrich_hurricane_population(self, hurricane_id: str) -> Dict:
        """Enrich hurricane with coastal population exposed.
        
        Args:
            hurricane_id: NOAA storm ID
        
        Returns:
            Enrichment statistics
        """
        hurricane = Hurricane.query.get(hurricane_id)
        if not hurricane:
            logger.warning(f"Hurricane {hurricane_id} not found")
            return {'success': False, 'error': 'Hurricane not found'}
        
        if not hurricane.landfall_location or not hurricane.landfall_state:
            logger.info(f"No landfall location for {hurricane.name} ({hurricane.year})")
            return {'success': True, 'enriched': False, 'reason': 'No landfall data'}
        
        try:
            # Geocode landfall location
            lat, lon = self._geocode_location(
                hurricane.landfall_location,
                hurricane.landfall_state
            )
            
            if not lat or not lon:
                logger.warning(f"Could not geocode {hurricane.landfall_location}, {hurricane.landfall_state}")
                return {'success': True, 'enriched': False, 'reason': 'Geocoding failed'}
            
            # Get population within 50-mile radius of landfall
            population = self._get_coastal_population(
                lat, lon,
                hurricane.year,
                radius_miles=50
            )
            
            if population:
                hurricane.coastal_population_exposed = population
                hurricane.last_updated = datetime.utcnow()
                db.session.commit()
                
                logger.info(f"✅ {hurricane.name} ({hurricane.year}): "
                          f"{population:,} exposed population at {hurricane.landfall_location}")
                
                return {
                    'success': True,
                    'enriched': True,
                    'population': population,
                    'lat': lat,
                    'lon': lon
                }
            else:
                return {'success': True, 'enriched': False, 'reason': 'No population data'}
        
        except Exception as e:
            logger.error(f"Error enriching population for {hurricane_id}: {e}")
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    def enrich_all_hurricanes(self, limit: Optional[int] = None) -> Dict:
        """Enrich all hurricanes with population controls.
        
        Args:
            limit: Max hurricanes to process
        
        Returns:
            Statistics
        """
        stats = {
            'total_hurricanes': 0,
            'enriched': 0,
            'skipped_no_landfall': 0,
            'skipped_geocode_failed': 0,
            'errors': 0
        }
        
        query = Hurricane.query.filter(
            Hurricane.landfall_location.isnot(None),
            Hurricane.landfall_state.isnot(None)
        ).order_by(
            Hurricane.coastal_population_exposed.is_(None).desc(),
            Hurricane.year.desc()
        )
        
        if limit:
            query = query.limit(limit)
        
        hurricanes = query.all()
        stats['total_hurricanes'] = len(hurricanes)
        
        logger.info(f"Starting Census enrichment for {len(hurricanes)} hurricanes...")
        
        for idx, hurricane in enumerate(hurricanes):
            if idx > 0 and idx % 10 == 0:
                logger.info(f"  Progress: {idx}/{len(hurricanes)} processed...")
                time.sleep(2)
            
            result = self.enrich_hurricane_population(hurricane.id)
            
            if result['success']:
                if result.get('enriched'):
                    stats['enriched'] += 1
                elif result.get('reason') == 'Geocoding failed':
                    stats['skipped_geocode_failed'] += 1
            else:
                stats['errors'] += 1
            
            time.sleep(self.rate_limit_delay)
        
        logger.info(f"\n{'='*60}")
        logger.info("✅ CENSUS ENRICHMENT COMPLETE")
        logger.info(f"{'='*60}")
        logger.info(f"Hurricanes processed: {stats['total_hurricanes']}")
        logger.info(f"Successfully enriched: {stats['enriched']}")
        logger.info(f"Geocoding failed: {stats['skipped_geocode_failed']}")
        logger.info(f"Errors: {stats['errors']}")
        
        return stats
    
    def _geocode_location(self, location: str, state: str) -> Tuple[Optional[float], Optional[float]]:
        """Geocode a location to lat/lon.
        
        Args:
            location: City or location name
            state: State name
        
        Returns:
            (latitude, longitude) or (None, None)
        """
        try:
            params = {
                'street': '',
                'city': location,
                'state': state,
                'benchmark': 'Public_AR_Current',
                'format': 'json'
            }
            
            response = requests.get(self.geocode_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('result', {}).get('addressMatches'):
                match = data['result']['addressMatches'][0]
                coords = match.get('coordinates', {})
                lat = coords.get('y')
                lon = coords.get('x')
                return (lat, lon)
            
            return (None, None)
        
        except Exception as e:
            logger.error(f"Geocoding error for {location}, {state}: {e}")
            return (None, None)
    
    def _get_coastal_population(
        self, 
        lat: float, 
        lon: float, 
        year: int,
        radius_miles: float = 50
    ) -> Optional[int]:
        """Get population within radius of coordinates.
        
        This is simplified - in reality would use Census TIGER/Line shapefiles
        and spatial queries. For now, estimate based on nearest county.
        
        Args:
            lat: Latitude
            lon: Longitude
            year: Storm year (for historical population)
            radius_miles: Radius to search
        
        Returns:
            Estimated population or None
        """
        try:
            # Simplified implementation - would need more sophisticated spatial analysis
            # For now, return a placeholder that could be manually filled
            # Real implementation would:
            # 1. Get county FIPS code from lat/lon
            # 2. Query Census API for that county's population in that year
            # 3. Potentially sum multiple counties within radius
            
            # This is a TODO for full implementation
            return None
        
        except Exception as e:
            logger.error(f"Population query error for ({lat}, {lon}): {e}")
            return None


from datetime import datetime

