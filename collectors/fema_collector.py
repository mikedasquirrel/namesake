"""FEMA Disaster Declarations Collector

Scrapes FEMA disaster declarations to get federal aid totals per hurricane.
Data Source: https://www.fema.gov/openfema-data-page/disaster-declarations-summaries-v2

Focus on:
- Total FEMA aid obligated
- Affected counties
- Disaster declaration dates
"""

import logging
import time
from datetime import datetime
from typing import Dict, List, Optional

import requests

from core.models import Hurricane, db

logger = logging.getLogger(__name__)


class FEMACollector:
    """Collect FEMA disaster aid data for hurricanes."""
    
    def __init__(self):
        self.base_url = "https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries"
        self.rate_limit_delay = 0.3  # Be respectful
    
    def enrich_hurricane_fema_aid(self, hurricane_id: str) -> Dict:
        """Enrich a single hurricane with FEMA aid data.
        
        Args:
            hurricane_id: NOAA storm ID
        
        Returns:
            Enrichment statistics
        """
        hurricane = Hurricane.query.get(hurricane_id)
        if not hurricane:
            logger.warning(f"Hurricane {hurricane_id} not found")
            return {'success': False, 'error': 'Hurricane not found'}
        
        try:
            # Search FEMA API for this storm
            declarations = self._fetch_fema_declarations(hurricane.name, hurricane.year)
            
            if not declarations:
                logger.info(f"No FEMA declarations found for {hurricane.name} ({hurricane.year})")
                return {'success': True, 'declarations_found': 0, 'enriched': False}
            
            # Aggregate aid across all declarations
            total_aid = sum(d.get('totalObligatedAmountPa', 0) or 0 for d in declarations)
            affected_counties = len(set(d.get('designatedArea', '') for d in declarations if d.get('designatedArea')))
            
            # Update hurricane record
            hurricane.fema_aid_usd = total_aid if total_aid > 0 else None
            hurricane.last_updated = datetime.utcnow()
            
            db.session.commit()
            
            logger.info(f"✅ FEMA aid for {hurricane.name} ({hurricane.year}): "
                       f"${total_aid:,.0f} across {affected_counties} counties")
            
            return {
                'success': True,
                'declarations_found': len(declarations),
                'enriched': True,
                'total_aid_usd': total_aid,
                'affected_counties': affected_counties
            }
        
        except Exception as e:
            logger.error(f"Error enriching FEMA data for {hurricane_id}: {e}")
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    def enrich_all_hurricanes(self, limit: Optional[int] = None) -> Dict:
        """Enrich all hurricanes with FEMA data.
        
        Args:
            limit: Max hurricanes to process
        
        Returns:
            Statistics
        """
        stats = {
            'total_hurricanes': 0,
            'enriched': 0,
            'skipped_no_data': 0,
            'errors': 0,
            'total_declarations': 0,
            'total_aid_usd': 0.0
        }
        
        # Prioritize hurricanes without FEMA data, recent first
        query = Hurricane.query.order_by(
            Hurricane.fema_aid_usd.is_(None).desc(),
            Hurricane.year.desc()
        )
        
        if limit:
            query = query.limit(limit)
        
        hurricanes = query.all()
        stats['total_hurricanes'] = len(hurricanes)
        
        logger.info(f"Starting FEMA enrichment for {len(hurricanes)} hurricanes...")
        
        for idx, hurricane in enumerate(hurricanes):
            if idx > 0 and idx % 5 == 0:
                logger.info(f"  Progress: {idx}/{len(hurricanes)} processed...")
                time.sleep(2)  # Extra pause
            
            result = self.enrich_hurricane_fema_aid(hurricane.id)
            
            if result['success']:
                if result.get('enriched'):
                    stats['enriched'] += 1
                    stats['total_declarations'] += result.get('declarations_found', 0)
                    stats['total_aid_usd'] += result.get('total_aid_usd', 0.0)
                else:
                    stats['skipped_no_data'] += 1
            else:
                stats['errors'] += 1
            
            time.sleep(self.rate_limit_delay)
        
        logger.info(f"\n{'='*60}")
        logger.info("✅ FEMA ENRICHMENT COMPLETE")
        logger.info(f"{'='*60}")
        logger.info(f"Hurricanes processed: {stats['total_hurricanes']}")
        logger.info(f"Successfully enriched: {stats['enriched']}")
        logger.info(f"No FEMA data: {stats['skipped_no_data']}")
        logger.info(f"Total FEMA aid found: ${stats['total_aid_usd']:,.0f}")
        
        return stats
    
    def _fetch_fema_declarations(self, storm_name: str, year: int) -> List[Dict]:
        """Fetch FEMA disaster declarations for a hurricane.
        
        Args:
            storm_name: Hurricane name
            year: Year of storm
        
        Returns:
            List of declaration records
        """
        try:
            # FEMA OpenFEMA API parameters
            params = {
                '$filter': f"fyDeclared eq {year} and incidentType eq 'Hurricane'",
                '$select': 'disasterNumber,declarationTitle,designatedArea,totalObligatedAmountPa,declarationDate',
                '$orderby': 'disasterNumber',
                '$top': 1000
            }
            
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Filter declarations matching storm name
            declarations = []
            for record in data.get('DisasterDeclarationsSummaries', []):
                title = record.get('declarationTitle', '').lower()
                if storm_name.lower() in title or f'hurricane {storm_name.lower()}' in title:
                    declarations.append(record)
            
            return declarations
        
        except requests.exceptions.RequestException as e:
            logger.error(f"FEMA API request failed for {storm_name} ({year}): {e}")
            return []
        except Exception as e:
            logger.error(f"Error parsing FEMA data for {storm_name}: {e}")
            return []



