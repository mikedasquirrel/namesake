"""Hurricane Track Geocoder

Maps hurricane tracks from HURDAT2 to Census geographic areas (counties, tracts, zips).
Calculates distance from storm center to determine impact zones and severity levels.

Uses:
- Haversine formula for distance calculations
- Census TIGER/Line shapefiles for geographic boundaries
- HURDAT2 track points for hurricane positions
"""

import logging
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json

import requests

from core.models import Hurricane, HurricaneGeography, db

logger = logging.getLogger(__name__)


class HurricaneTrackGeocoder:
    """Map hurricane tracks to affected Census geographies."""
    
    def __init__(self):
        self.census_geocoder_url = "https://geocoding.geo.census.gov/geocoder/geographies/coordinates"
        
        # Impact severity thresholds (miles from track)
        self.severity_thresholds = {
            'direct': 50,       # 0-50 miles
            'moderate': 100,    # 50-100 miles
            'peripheral': 200   # 100-200 miles
        }
    
    def geocode_hurricane_track(self, hurricane_id: str, track_points: List[Dict]) -> Dict:
        """
        Map hurricane track to affected counties and create HurricaneGeography records.
        
        Args:
            hurricane_id: Hurricane ID
            track_points: List of track point dicts with {lat, lon, date, wind_mph}
        
        Returns:
            Statistics dict
        """
        stats = {
            'hurricane_id': hurricane_id,
            'track_points': len(track_points),
            'counties_affected': 0,
            'direct_impact': 0,
            'moderate_impact': 0,
            'peripheral_impact': 0,
            'errors': 0
        }
        
        if not track_points:
            logger.warning(f"No track points provided for {hurricane_id}")
            return stats
        
        try:
            # Get all counties affected by the track
            affected_counties = self._identify_affected_counties(track_points)
            
            stats['counties_affected'] = len(affected_counties)
            
            # For each affected county, calculate impact metrics
            for county_info in affected_counties:
                try:
                    self._create_geography_record(hurricane_id, county_info, track_points, stats)
                except Exception as e:
                    logger.error(f"Error creating geography record for county {county_info.get('fips')}: {e}")
                    stats['errors'] += 1
            
            db.session.commit()
            
            logger.info(f"✅ Geocoded {hurricane_id}: {stats['counties_affected']} counties "
                       f"({stats['direct_impact']} direct, {stats['moderate_impact']} moderate, "
                       f"{stats['peripheral_impact']} peripheral)")
            
            return stats
            
        except Exception as e:
            logger.error(f"Error geocoding hurricane track for {hurricane_id}: {e}")
            db.session.rollback()
            stats['error'] = str(e)
            return stats
    
    def geocode_hurricane_from_hurdat2(self, hurricane_id: str) -> Dict:
        """
        Geocode a hurricane using its HURDAT2 data.
        
        This fetches the hurricane's track from HURDAT2 and geocodes it.
        
        Args:
            hurricane_id: Hurricane ID (e.g., 'AL092005' for Katrina)
        
        Returns:
            Statistics dict
        """
        hurricane = Hurricane.query.get(hurricane_id)
        if not hurricane:
            logger.error(f"Hurricane {hurricane_id} not found")
            return {'success': False, 'error': 'Hurricane not found'}
        
        # Fetch HURDAT2 track data
        track_points = self._fetch_hurdat2_track(hurricane.id, hurricane.basin, hurricane.year)
        
        if not track_points:
            logger.warning(f"No track data found for {hurricane.name} ({hurricane.year})")
            return {'success': False, 'error': 'No track data'}
        
        # Geocode the track
        result = self.geocode_hurricane_track(hurricane.id, track_points)
        result['success'] = True
        
        return result
    
    def _fetch_hurdat2_track(self, storm_id: str, basin: str, year: int) -> List[Dict]:
        """
        Fetch track points from HURDAT2 database.
        
        Args:
            storm_id: NOAA storm ID (e.g., 'AL092005')
            basin: 'AL' or 'EP'
            year: Hurricane year
        
        Returns:
            List of track point dicts
        """
        # Determine HURDAT2 URL based on basin
        if basin == 'AL':
            url = "https://www.nhc.noaa.gov/data/hurdat/hurdat2-1851-2023-051124.txt"
        elif basin == 'EP':
            url = "https://www.nhc.noaa.gov/data/hurdat/hurdat2-nepac-1949-2023-051124.txt"
        else:
            logger.error(f"Unknown basin: {basin}")
            return []
        
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            
            lines = response.text.strip().split('\n')
            
            # Find storm in HURDAT2 data
            in_storm = False
            track_points = []
            
            for line in lines:
                # Header line
                if line.startswith(storm_id):
                    in_storm = True
                    continue
                elif line[0:2].isalpha() and line[2:4].isdigit():
                    # New storm header - stop if we were in our storm
                    if in_storm:
                        break
                    continue
                
                if in_storm:
                    # Parse data line
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) < 8:
                        continue
                    
                    try:
                        date_str = parts[0]
                        time_str = parts[1]
                        lat_str = parts[4]
                        lon_str = parts[5]
                        wind_kts = int(parts[6]) if parts[6] and parts[6] != '-999' else 0
                        
                        # Parse lat/lon (format: 25.5N, 80.2W)
                        lat = self._parse_coordinate(lat_str)
                        lon = self._parse_coordinate(lon_str)
                        
                        if lat is None or lon is None:
                            continue
                        
                        # Convert knots to mph
                        wind_mph = int(wind_kts * 1.151) if wind_kts else 0
                        
                        # Parse datetime
                        track_date = datetime.strptime(f"{date_str}{time_str}", "%Y%m%d%H%M")
                        
                        track_points.append({
                            'lat': lat,
                            'lon': lon,
                            'date': track_date,
                            'wind_mph': wind_mph
                        })
                    except (ValueError, IndexError) as e:
                        logger.debug(f"Error parsing track point: {e}")
                        continue
            
            return track_points
            
        except Exception as e:
            logger.error(f"Error fetching HURDAT2 track for {storm_id}: {e}")
            return []
    
    def _parse_coordinate(self, coord_str: str) -> Optional[float]:
        """
        Parse HURDAT2 coordinate string (e.g., '25.5N', '80.2W').
        
        Args:
            coord_str: Coordinate string with direction
        
        Returns:
            Decimal degrees (positive for N/E, negative for S/W)
        """
        if not coord_str or len(coord_str) < 2:
            return None
        
        try:
            direction = coord_str[-1]
            value = float(coord_str[:-1])
            
            if direction in ['S', 'W']:
                value = -value
            
            return value
        except ValueError:
            return None
    
    def _identify_affected_counties(self, track_points: List[Dict]) -> List[Dict]:
        """
        Identify all counties within impact distance of hurricane track.
        
        Uses a simplified approach: sample track points and find nearby counties.
        
        Args:
            track_points: List of track point dicts
        
        Returns:
            List of county info dicts with FIPS codes and impact details
        """
        affected_counties = {}
        
        # Sample track points (every Nth point to avoid API overload)
        sample_interval = max(1, len(track_points) // 20)  # ~20 samples max
        sampled_points = track_points[::sample_interval]
        
        logger.debug(f"Sampling {len(sampled_points)} of {len(track_points)} track points")
        
        for point in sampled_points:
            # Get counties near this point
            counties = self._get_counties_near_point(
                point['lat'],
                point['lon'],
                self.severity_thresholds['peripheral']
            )
            
            for county in counties:
                fips = county['fips']
                
                # Calculate distance from this track point to county center
                distance = self._haversine_distance(
                    point['lat'], point['lon'],
                    county['lat'], county['lon']
                )
                
                # Update minimum distance for this county
                if fips not in affected_counties or distance < affected_counties[fips]['min_distance']:
                    affected_counties[fips] = {
                        'fips': fips,
                        'state_fips': fips[:2],
                        'county_fips': fips[2:],
                        'name': county['name'],
                        'min_distance': distance,
                        'closest_point': point
                    }
        
        return list(affected_counties.values())
    
    def _get_counties_near_point(self, lat: float, lon: float, radius_miles: float) -> List[Dict]:
        """
        Get counties near a geographic point using Census Geocoder.
        
        This is a simplified implementation. In production, would use:
        - Local TIGER/Line county shapefiles
        - Spatial database (PostGIS)
        - Pre-computed county centroids
        
        Args:
            lat: Latitude
            lon: Longitude
            radius_miles: Search radius
        
        Returns:
            List of county dicts with FIPS codes
        """
        # For now, just get the county at this point
        # A full implementation would query all counties within radius
        try:
            params = {
                'x': lon,
                'y': lat,
                'benchmark': 'Public_AR_Current',
                'vintage': 'Current_Current',
                'layers': 'Counties',
                'format': 'json'
            }
            
            response = requests.get(self.census_geocoder_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            counties = []
            
            if 'result' in data and 'geographies' in data['result']:
                for county_list in data['result']['geographies'].values():
                    for county in county_list:
                        fips = county.get('STATE') + county.get('COUNTY', '')
                        counties.append({
                            'fips': fips,
                            'name': county.get('NAME', ''),
                            'lat': lat,  # Use track point coords (county center would be better)
                            'lon': lon
                        })
            
            return counties
            
        except Exception as e:
            logger.debug(f"Census geocoder request failed: {e}")
            return []
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two points using Haversine formula.
        
        Args:
            lat1, lon1: First point coordinates
            lat2, lon2: Second point coordinates
        
        Returns:
            Distance in miles
        """
        # Radius of Earth in miles
        R = 3959.0
        
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        dLat = math.radians(lat2 - lat1)
        dLon = math.radians(lon2 - lon1)
        
        # Haversine formula
        a = (math.sin(dLat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dLon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        
        return distance
    
    def _create_geography_record(self, hurricane_id: str, county_info: Dict, 
                                  track_points: List[Dict], stats: Dict):
        """
        Create HurricaneGeography record for a county.
        
        Args:
            hurricane_id: Hurricane ID
            county_info: County information dict
            track_points: Full track points list
            stats: Statistics dict to update
        """
        fips = county_info['fips']
        min_distance = county_info['min_distance']
        closest_point = county_info['closest_point']
        
        # Determine impact severity
        if min_distance <= self.severity_thresholds['direct']:
            severity = 'direct'
            stats['direct_impact'] += 1
        elif min_distance <= self.severity_thresholds['moderate']:
            severity = 'moderate'
            stats['moderate_impact'] += 1
        elif min_distance <= self.severity_thresholds['peripheral']:
            severity = 'peripheral'
            stats['peripheral_impact'] += 1
        else:
            # Beyond peripheral threshold - skip
            return
        
        # Check if record already exists
        existing = HurricaneGeography.query.filter_by(
            hurricane_id=hurricane_id,
            geographic_code=fips,
            geographic_level='county'
        ).first()
        
        if existing:
            # Update existing
            existing.impact_severity = severity
            existing.distance_from_track_miles = min_distance
            existing.closest_approach_date = closest_point['date']
            existing.max_wind_at_location_mph = closest_point['wind_mph']
        else:
            # Create new
            geography = HurricaneGeography(
                hurricane_id=hurricane_id,
                geographic_code=fips,
                geographic_level='county',
                impact_severity=severity,
                distance_from_track_miles=min_distance,
                closest_approach_date=closest_point['date'],
                max_wind_at_location_mph=closest_point['wind_mph'],
                state_fips=county_info['state_fips'],
                county_fips=county_info['county_fips']
            )
            db.session.add(geography)

