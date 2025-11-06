"""GDELT Media Mention Collector

Collects pre-landfall and post-landfall media mentions for hurricanes from GDELT.
Tests the hypothesis that phonetically harsh names → more media coverage → better prep.

GDELT: Global Database of Events, Language, and Tone
API: https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Optional

import requests

from core.models import Hurricane, db

logger = logging.getLogger(__name__)


class GDELTCollector:
    """Collect media mention counts from GDELT for hurricanes."""
    
    def __init__(self):
        self.api_url = "https://api.gdeltproject.org/api/v2/doc/doc"
        self.rate_limit_delay = 1.0  # Be very respectful to GDELT
    
    def enrich_hurricane_media_mentions(self, hurricane_id: str) -> Dict:
        """Enrich hurricane with pre/post-landfall media mentions.
        
        Args:
            hurricane_id: NOAA storm ID
        
        Returns:
            Enrichment statistics
        """
        hurricane = Hurricane.query.get(hurricane_id)
        if not hurricane:
            logger.warning(f"Hurricane {hurricane_id} not found")
            return {'success': False, 'error': 'Hurricane not found'}
        
        if not hurricane.landfall_date:
            logger.info(f"No landfall date for {hurricane.name} ({hurricane.year})")
            return {'success': True, 'enriched': False, 'reason': 'No landfall date'}
        
        try:
            # Query GDELT for 7 days before landfall
            pre_mentions = self._get_mention_count(
                hurricane.name,
                hurricane.landfall_date - timedelta(days=7),
                hurricane.landfall_date
            )
            
            # Query GDELT for 7 days after landfall
            post_mentions = self._get_mention_count(
                hurricane.name,
                hurricane.landfall_date,
                hurricane.landfall_date + timedelta(days=7)
            )
            
            # Update hurricane record
            hurricane.media_mentions_prelandfall = pre_mentions
            hurricane.media_mentions_postlandfall = post_mentions
            hurricane.last_updated = datetime.utcnow()
            
            db.session.commit()
            
            logger.info(f"✅ {hurricane.name} ({hurricane.year}): "
                       f"{pre_mentions} pre-landfall mentions, "
                       f"{post_mentions} post-landfall mentions")
            
            return {
                'success': True,
                'enriched': True,
                'pre_mentions': pre_mentions,
                'post_mentions': post_mentions
            }
        
        except Exception as e:
            logger.error(f"Error enriching GDELT for {hurricane_id}: {e}")
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    def enrich_all_hurricanes(self, limit: Optional[int] = None) -> Dict:
        """Enrich all hurricanes with media mention counts.
        
        Args:
            limit: Max hurricanes to process
        
        Returns:
            Statistics
        """
        stats = {
            'total_hurricanes': 0,
            'enriched': 0,
            'skipped_no_landfall': 0,
            'errors': 0,
            'total_pre_mentions': 0,
            'total_post_mentions': 0
        }
        
        # Only process storms with landfall dates, recent first
        query = Hurricane.query.filter(
            Hurricane.landfall_date.isnot(None)
        ).order_by(
            Hurricane.media_mentions_prelandfall.is_(None).desc(),
            Hurricane.year.desc()
        )
        
        if limit:
            query = query.limit(limit)
        
        hurricanes = query.all()
        stats['total_hurricanes'] = len(hurricanes)
        
        logger.info(f"Starting GDELT enrichment for {len(hurricanes)} hurricanes...")
        logger.info("⚠️  This will be slow - GDELT rate limits are strict")
        
        for idx, hurricane in enumerate(hurricanes):
            if idx > 0 and idx % 5 == 0:
                logger.info(f"  Progress: {idx}/{len(hurricanes)} processed...")
                time.sleep(5)  # Extra pause every 5 requests
            
            result = self.enrich_hurricane_media_mentions(hurricane.id)
            
            if result['success']:
                if result.get('enriched'):
                    stats['enriched'] += 1
                    stats['total_pre_mentions'] += result.get('pre_mentions', 0)
                    stats['total_post_mentions'] += result.get('post_mentions', 0)
                else:
                    stats['skipped_no_landfall'] += 1
            else:
                stats['errors'] += 1
            
            time.sleep(self.rate_limit_delay)
        
        logger.info(f"\n{'='*60}")
        logger.info("✅ GDELT ENRICHMENT COMPLETE")
        logger.info(f"{'='*60}")
        logger.info(f"Hurricanes processed: {stats['total_hurricanes']}")
        logger.info(f"Successfully enriched: {stats['enriched']}")
        logger.info(f"Total pre-landfall mentions: {stats['total_pre_mentions']:,}")
        logger.info(f"Total post-landfall mentions: {stats['total_post_mentions']:,}")
        
        return stats
    
    def _get_mention_count(
        self, 
        storm_name: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> int:
        """Get count of media mentions for a storm in date range.
        
        Args:
            storm_name: Hurricane name
            start_date: Start of search window
            end_date: End of search window
        
        Returns:
            Number of mentions
        """
        try:
            # Format dates for GDELT API (YYYYMMDDHHMMSS)
            start_str = start_date.strftime('%Y%m%d000000')
            end_str = end_date.strftime('%Y%m%d235959')
            
            # GDELT Doc API parameters
            params = {
                'query': f'hurricane {storm_name}',
                'mode': 'timelineinfo',
                'maxrecords': '1',  # We just need the count
                'format': 'json',
                'startdatetime': start_str,
                'enddatetime': end_str
            }
            
            response = requests.get(self.api_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract article count from timeline
            if 'timeline' in data and len(data['timeline']) > 0:
                # Sum up all article counts in the timeline
                total_count = sum(
                    entry.get('artcount', 0) 
                    for entry in data['timeline']
                )
                return total_count
            
            return 0
        
        except requests.exceptions.RequestException as e:
            logger.error(f"GDELT API error for {storm_name} ({start_date.date()}): {e}")
            return 0
        except Exception as e:
            logger.error(f"Error parsing GDELT data for {storm_name}: {e}")
            return 0



