"""FEMA Individual Assistance Applications Collector

Collects FEMA Individual Assistance (IA) application data as a proxy for
hurricane displacement and demographic impact. IA applications indicate
individuals/households that experienced significant displacement or damage.

Data Source: https://www.fema.gov/openfema-data-page/fema-web-disaster-summaries-v1
API Endpoint: https://www.fema.gov/api/open/v1/FemaWebDisasterSummaries
"""

import logging
import time
from datetime import datetime
from typing import Dict, List, Optional
import json

import requests

from core.models import Hurricane, HurricaneDemographicImpact, GeographicDemographics, db

logger = logging.getLogger(__name__)


class FEMAIndividualAssistanceCollector:
    """Collect FEMA Individual Assistance application data for hurricanes."""
    
    def __init__(self):
        self.base_url = "https://www.fema.gov/api/open/v1"
        self.disaster_summaries_endpoint = f"{self.base_url}/FemaWebDisasterSummaries"
        self.housing_assistance_endpoint = f"{self.base_url}/HousingAssistanceOwners"
        self.rate_limit_delay = 0.5
    
    def collect_ia_for_hurricane(self, hurricane_id: str) -> Dict:
        """
        Collect Individual Assistance data for a specific hurricane.
        
        Args:
            hurricane_id: Hurricane ID (e.g., 'AL092005' for Katrina)
        
        Returns:
            Statistics dict
        """
        hurricane = Hurricane.query.get(hurricane_id)
        if not hurricane:
            logger.error(f"Hurricane {hurricane_id} not found in database")
            return {'success': False, 'error': 'Hurricane not found'}
        
        stats = {
            'hurricane_id': hurricane_id,
            'hurricane_name': hurricane.name,
            'year': hurricane.year,
            'declarations_found': 0,
            'counties_affected': 0,
            'total_ia_applications': 0,
            'total_ia_approved': 0,
            'total_aid_approved_usd': 0.0,
            'success': False
        }
        
        try:
            # Search for disaster declarations matching this hurricane
            declarations = self._fetch_disaster_declarations(hurricane.name, hurricane.year)
            
            if not declarations:
                logger.info(f"No FEMA declarations found for {hurricane.name} ({hurricane.year})")
                stats['success'] = True
                return stats
            
            stats['declarations_found'] = len(declarations)
            
            # For each declaration, get county-level IA data
            for declaration in declarations:
                disaster_number = declaration.get('disasterNumber')
                
                if not disaster_number:
                    continue
                
                # Fetch IA data by county for this disaster
                county_data = self._fetch_ia_by_county(disaster_number)
                
                for county_record in county_data:
                    self._process_county_ia_data(hurricane_id, county_record, stats)
                
                time.sleep(self.rate_limit_delay)
            
            stats['success'] = True
            logger.info(f"✅ FEMA IA data for {hurricane.name} ({hurricane.year}): "
                       f"{stats['total_ia_applications']:,} applications across "
                       f"{stats['counties_affected']} counties")
            
            return stats
            
        except Exception as e:
            logger.error(f"Error collecting FEMA IA for {hurricane_id}: {e}")
            stats['error'] = str(e)
            return stats
    
    def collect_ia_for_all_hurricanes(self, limit: Optional[int] = None) -> Dict:
        """
        Collect IA data for all hurricanes in database.
        
        Args:
            limit: Max hurricanes to process
        
        Returns:
            Overall statistics
        """
        overall_stats = {
            'hurricanes_processed': 0,
            'successful': 0,
            'failed': 0,
            'total_applications': 0,
            'total_aid_usd': 0.0
        }
        
        # Query hurricanes with outcome data (deaths or damage)
        query = Hurricane.query.filter(
            (Hurricane.deaths.isnot(None)) | (Hurricane.damage_usd.isnot(None))
        ).order_by(Hurricane.year.desc())
        
        if limit:
            query = query.limit(limit)
        
        hurricanes = query.all()
        overall_stats['hurricanes_processed'] = len(hurricanes)
        
        logger.info(f"Collecting FEMA IA data for {len(hurricanes)} hurricanes...")
        
        for idx, hurricane in enumerate(hurricanes):
            if idx > 0 and idx % 5 == 0:
                logger.info(f"  Progress: {idx}/{len(hurricanes)} hurricanes processed")
                time.sleep(2)  # Extra pause
            
            result = self.collect_ia_for_hurricane(hurricane.id)
            
            if result.get('success'):
                overall_stats['successful'] += 1
                overall_stats['total_applications'] += result.get('total_ia_applications', 0)
                overall_stats['total_aid_usd'] += result.get('total_aid_approved_usd', 0.0)
            else:
                overall_stats['failed'] += 1
        
        logger.info(f"\n{'='*60}")
        logger.info("✅ FEMA IA COLLECTION COMPLETE")
        logger.info(f"{'='*60}")
        logger.info(f"Hurricanes processed: {overall_stats['hurricanes_processed']}")
        logger.info(f"Successful: {overall_stats['successful']}")
        logger.info(f"Total IA applications: {overall_stats['total_applications']:,}")
        logger.info(f"Total aid approved: ${overall_stats['total_aid_usd']:,.0f}")
        
        return overall_stats
    
    def _fetch_disaster_declarations(self, storm_name: str, year: int) -> List[Dict]:
        """
        Fetch FEMA disaster declarations for a hurricane.
        
        Args:
            storm_name: Hurricane name
            year: Year of hurricane
        
        Returns:
            List of disaster declaration records
        """
        try:
            # Filter by year and incident type
            params = {
                '$filter': f"declarationDate ge '{year}-01-01T00:00:00.000Z' and "
                          f"declarationDate le '{year}-12-31T23:59:59.999Z' and "
                          f"incidentType eq 'Hurricane'",
                '$orderby': 'disasterNumber',
                '$top': 1000
            }
            
            response = requests.get(self.disaster_summaries_endpoint, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Filter by storm name in title
            declarations = []
            for record in data.get('FemaWebDisasterSummaries', []):
                title = record.get('declarationTitle', '').lower()
                if storm_name.lower() in title or f'hurricane {storm_name.lower()}' in title:
                    declarations.append(record)
            
            return declarations
            
        except requests.exceptions.RequestException as e:
            logger.error(f"FEMA API request failed for {storm_name} ({year}): {e}")
            return []
        except Exception as e:
            logger.error(f"Error parsing FEMA declaration data: {e}")
            return []
    
    def _fetch_ia_by_county(self, disaster_number: str) -> List[Dict]:
        """
        Fetch Individual Assistance data by county for a disaster.
        
        Note: The Housing Assistance endpoint provides county-level breakdowns.
        
        Args:
            disaster_number: FEMA disaster number (e.g., '1603')
        
        Returns:
            List of county-level IA records
        """
        try:
            params = {
                '$filter': f"disasterNumber eq {disaster_number}",
                '$select': 'county,state,validRegistrations,ihpApproved,haApproved,'
                          'totalApprovedIhpAmount,totalInspected,totalDamage',
                '$top': 5000  # Get all counties
            }
            
            response = requests.get(self.housing_assistance_endpoint, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            records = data.get('HousingAssistanceOwners', [])
            
            # Group by county (API may return multiple records per county)
            county_aggregated = {}
            for record in records:
                county_name = record.get('county', '').strip()
                state_code = record.get('state', '').strip()
                key = f"{state_code}_{county_name}"
                
                if key not in county_aggregated:
                    county_aggregated[key] = {
                        'county': county_name,
                        'state': state_code,
                        'disaster_number': disaster_number,
                        'valid_registrations': 0,
                        'ihp_approved': 0,
                        'ha_approved': 0,
                        'total_approved_amount': 0.0,
                        'total_inspected': 0,
                        'total_damage': 0.0
                    }
                
                # Aggregate counts and amounts
                county_aggregated[key]['valid_registrations'] += int(record.get('validRegistrations', 0) or 0)
                county_aggregated[key]['ihp_approved'] += int(record.get('ihpApproved', 0) or 0)
                county_aggregated[key]['ha_approved'] += int(record.get('haApproved', 0) or 0)
                county_aggregated[key]['total_approved_amount'] += float(record.get('totalApprovedIhpAmount', 0) or 0)
                county_aggregated[key]['total_inspected'] += int(record.get('totalInspected', 0) or 0)
                county_aggregated[key]['total_damage'] += float(record.get('totalDamage', 0) or 0)
            
            return list(county_aggregated.values())
            
        except requests.exceptions.RequestException as e:
            logger.error(f"FEMA IA API request failed for disaster {disaster_number}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error parsing FEMA IA data: {e}")
            return []
    
    def _process_county_ia_data(self, hurricane_id: str, county_data: Dict, stats: Dict):
        """
        Process county-level IA data and create demographic impact records.
        
        This creates aggregate records for the county (will be disaggregated
        by demographics in later enrichment step).
        
        Args:
            hurricane_id: Hurricane ID
            county_data: County IA data from FEMA
            stats: Statistics dict to update
        """
        try:
            county_name = county_data.get('county')
            state_code = county_data.get('state')
            
            if not county_name or not state_code:
                return
            
            # Look up county FIPS code from state/county name
            # This would require a state/county lookup table - for now, log and skip
            # In production, would use Census geocoder or FIPS lookup table
            geographic_code = self._lookup_county_fips(state_code, county_name)
            
            if not geographic_code:
                logger.debug(f"Could not find FIPS code for {county_name}, {state_code}")
                return
            
            # Get demographics for this county (to estimate demographic breakdown)
            demographics = GeographicDemographics.query.filter_by(
                geographic_code=geographic_code,
                geographic_level='county'
            ).order_by(GeographicDemographics.year.desc()).first()
            
            if not demographics:
                logger.debug(f"No demographic data found for county {geographic_code}")
                # Still create aggregate record
                demographics = None
            
            # Create aggregate county-level record (all demographics combined)
            # Later, enrichment script will disaggregate by race/income/age
            applications = county_data.get('valid_registrations', 0)
            approved = county_data.get('ihp_approved', 0)
            aid_amount = county_data.get('total_approved_amount', 0.0)
            
            # Check if record already exists
            existing = HurricaneDemographicImpact.query.filter_by(
                hurricane_id=hurricane_id,
                geographic_code=geographic_code,
                geographic_level='county',
                demographic_category='total',
                demographic_value='all'
            ).first()
            
            population = demographics.total_population if demographics else None
            
            if existing:
                # Update existing
                existing.fema_applications = applications
                existing.fema_aid_received_usd = aid_amount
                existing.population_at_risk = population
                if population and applications:
                    existing.fema_application_rate = applications / population
            else:
                # Create new
                impact = HurricaneDemographicImpact(
                    hurricane_id=hurricane_id,
                    geographic_code=geographic_code,
                    geographic_level='county',
                    demographic_category='total',
                    demographic_value='all',
                    population_at_risk=population,
                    fema_applications=applications,
                    fema_aid_received_usd=aid_amount,
                    fema_application_rate=applications / population if population and applications else None,
                    data_source=f"FEMA_IA_{county_data.get('disaster_number')}",
                    confidence_level='medium'
                )
                db.session.add(impact)
            
            db.session.commit()
            
            # Update stats
            stats['counties_affected'] += 1
            stats['total_ia_applications'] += applications
            stats['total_ia_approved'] += approved
            stats['total_aid_approved_usd'] += aid_amount
            
        except Exception as e:
            logger.error(f"Error processing county IA data: {e}")
            db.session.rollback()
    
    def _lookup_county_fips(self, state_code: str, county_name: str) -> Optional[str]:
        """
        Look up county FIPS code from state abbreviation and county name.
        
        This is a simplified implementation - in production would use
        a comprehensive FIPS lookup table or Census geocoding API.
        
        Args:
            state_code: State abbreviation (e.g., 'FL')
            county_name: County name (e.g., 'Miami-Dade')
        
        Returns:
            5-digit FIPS code or None
        """
        # Simplified state FIPS mapping (partial)
        state_fips_map = {
            'AL': '01', 'AK': '02', 'AZ': '04', 'AR': '05', 'CA': '06',
            'CO': '08', 'CT': '09', 'DE': '10', 'FL': '12', 'GA': '13',
            'HI': '15', 'ID': '16', 'IL': '17', 'IN': '18', 'IA': '19',
            'KS': '20', 'KY': '21', 'LA': '22', 'ME': '23', 'MD': '24',
            'MA': '25', 'MI': '26', 'MN': '27', 'MS': '28', 'MO': '29',
            'MT': '30', 'NE': '31', 'NV': '32', 'NH': '33', 'NJ': '34',
            'NM': '35', 'NY': '36', 'NC': '37', 'ND': '38', 'OH': '39',
            'OK': '40', 'OR': '41', 'PA': '42', 'RI': '44', 'SC': '45',
            'SD': '46', 'TN': '47', 'TX': '48', 'UT': '49', 'VT': '50',
            'VA': '51', 'WA': '53', 'WV': '54', 'WI': '55', 'WY': '56',
            'PR': '72', 'VI': '78', 'AS': '60', 'GU': '66', 'MP': '69'
        }
        
        state_fips = state_fips_map.get(state_code.upper())
        
        if not state_fips:
            return None
        
        # For complete implementation, would query a county lookup table
        # For now, return None to indicate need for geocoding
        # The hurricane_track_geocoder will create the proper FIPS mappings
        
        return None  # Placeholder - needs full FIPS county table

