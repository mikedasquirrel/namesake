"""Hurricane Demographics Collection Orchestration Script

Orchestrates the full demographic data collection pipeline for hurricane analysis:
1. Geocode hurricane tracks to affected counties
2. Collect Census demographic baselines for affected areas
3. Collect FEMA Individual Assistance data
4. Collect NOAA Storm Events data (if available)

Usage:
    python scripts/collect_hurricane_demographics.py --hurricane AL092005  # Specific hurricane
    python scripts/collect_hurricane_demographics.py --year 2005           # All in year
    python scripts/collect_hurricane_demographics.py --all                 # All hurricanes
"""

import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app import app
from core.models import Hurricane, db
from collectors.hurricane_track_geocoder import HurricaneTrackGeocoder
from collectors.census_demographic_collector import CensusDemographicCollector
from collectors.fema_individual_assistance_collector import FEMAIndividualAssistanceCollector
from collectors.noaa_storm_events_demographic_collector import NOAAStormEventsCollector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hurricane_demographics_collection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def collect_for_hurricane(hurricane_id: str, census_api_key: str = None, 
                          noaa_token: str = None) -> dict:
    """
    Run full demographic collection pipeline for a single hurricane.
    
    Args:
        hurricane_id: Hurricane ID (e.g., 'AL092005')
        census_api_key: Census Bureau API key (optional)
        noaa_token: NOAA API token (optional)
    
    Returns:
        Results dict with statistics
    """
    logger.info(f"\n{'='*80}")
    logger.info(f"COLLECTING DEMOGRAPHICS FOR HURRICANE: {hurricane_id}")
    logger.info(f"{'='*80}\n")
    
    results = {
        'hurricane_id': hurricane_id,
        'steps': {},
        'success': False
    }
    
    try:
        with app.app_context():
            # Verify hurricane exists
            hurricane = Hurricane.query.get(hurricane_id)
            if not hurricane:
                logger.error(f"Hurricane {hurricane_id} not found in database")
                results['error'] = 'Hurricane not found'
                return results
            
            logger.info(f"Processing: {hurricane.name} ({hurricane.year})")
            
            # STEP 1: Geocode hurricane track to counties
            logger.info("\n--- STEP 1: Geocoding hurricane track to affected counties ---")
            geocoder = HurricaneTrackGeocoder()
            geocode_result = geocoder.geocode_hurricane_from_hurdat2(hurricane_id)
            results['steps']['geocoding'] = geocode_result
            
            if not geocode_result.get('success'):
                logger.warning("Geocoding failed or no counties identified")
            else:
                logger.info(f"✓ Identified {geocode_result.get('counties_affected', 0)} affected counties")
            
            # STEP 2: Collect Census demographics for affected counties
            logger.info("\n--- STEP 2: Collecting Census demographic data ---")
            census_collector = CensusDemographicCollector(api_key=census_api_key)
            
            # Get list of affected counties from geocoding step
            affected_counties = census_collector.get_hurricane_affected_counties(hurricane_id)
            
            if affected_counties:
                # Collect demographics for hurricane year (or closest available)
                census_year = hurricane.year if hurricane.year >= 2009 else 2010
                census_result = census_collector.collect_multiple_counties(
                    affected_counties,
                    year=census_year
                )
                results['steps']['census_demographics'] = census_result
                logger.info(f"✓ Collected demographics for {census_result.get('successful', 0)} counties")
            else:
                logger.warning("No affected counties to collect demographics for")
                results['steps']['census_demographics'] = {'skipped': True}
            
            # STEP 3: Collect FEMA Individual Assistance data
            logger.info("\n--- STEP 3: Collecting FEMA Individual Assistance data ---")
            fema_collector = FEMAIndividualAssistanceCollector()
            fema_result = fema_collector.collect_ia_for_hurricane(hurricane_id)
            results['steps']['fema_ia'] = fema_result
            
            if fema_result.get('success'):
                logger.info(f"✓ FEMA IA: {fema_result.get('total_ia_applications', 0):,} applications across "
                           f"{fema_result.get('counties_affected', 0)} counties")
            
            # STEP 4: Collect NOAA Storm Events data (if available)
            logger.info("\n--- STEP 4: Collecting NOAA Storm Events data ---")
            noaa_collector = NOAAStormEventsCollector(token=noaa_token)
            noaa_result = noaa_collector.collect_events_for_hurricane(hurricane_id)
            results['steps']['noaa_events'] = noaa_result
            
            if noaa_result.get('success'):
                logger.info(f"✓ NOAA Events: {noaa_result.get('events_found', 0)} events across "
                           f"{noaa_result.get('counties_with_data', 0)} counties")
            
            results['success'] = True
            
            logger.info(f"\n{'='*80}")
            logger.info(f"✅ DEMOGRAPHIC COLLECTION COMPLETE FOR {hurricane.name} ({hurricane.year})")
            logger.info(f"{'='*80}\n")
            
    except Exception as e:
        logger.error(f"Error in demographic collection pipeline: {e}", exc_info=True)
        results['error'] = str(e)
    
    return results


def collect_for_year(year: int, census_api_key: str = None, noaa_token: str = None) -> dict:
    """
    Collect demographics for all hurricanes in a specific year.
    
    Args:
        year: Hurricane year
        census_api_key: Census API key
        noaa_token: NOAA token
    
    Returns:
        Overall results dict
    """
    logger.info(f"\n{'#'*80}")
    logger.info(f"COLLECTING DEMOGRAPHICS FOR ALL HURRICANES IN {year}")
    logger.info(f"{'#'*80}\n")
    
    overall_results = {
        'year': year,
        'hurricanes_processed': 0,
        'successful': 0,
        'failed': 0,
        'hurricanes': []
    }
    
    with app.app_context():
        # Query hurricanes from this year with outcome data
        hurricanes = Hurricane.query.filter_by(year=year).filter(
            (Hurricane.deaths.isnot(None)) | (Hurricane.damage_usd.isnot(None))
        ).all()
        
        logger.info(f"Found {len(hurricanes)} hurricanes in {year} with outcome data\n")
        
        for hurricane in hurricanes:
            result = collect_for_hurricane(hurricane.id, census_api_key, noaa_token)
            
            overall_results['hurricanes'].append(result)
            overall_results['hurricanes_processed'] += 1
            
            if result.get('success'):
                overall_results['successful'] += 1
            else:
                overall_results['failed'] += 1
    
    logger.info(f"\n{'#'*80}")
    logger.info(f"✅ YEAR {year} COMPLETE: {overall_results['successful']}/{overall_results['hurricanes_processed']} successful")
    logger.info(f"{'#'*80}\n")
    
    return overall_results


def collect_for_all(census_api_key: str = None, noaa_token: str = None, limit: int = None) -> dict:
    """
    Collect demographics for all hurricanes in database (with outcome data).
    
    Args:
        census_api_key: Census API key
        noaa_token: NOAA token
        limit: Max number of hurricanes to process
    
    Returns:
        Overall results dict
    """
    logger.info(f"\n{'#'*80}")
    logger.info(f"COLLECTING DEMOGRAPHICS FOR ALL HURRICANES")
    logger.info(f"{'#'*80}\n")
    
    overall_results = {
        'hurricanes_processed': 0,
        'successful': 0,
        'failed': 0,
        'hurricanes': []
    }
    
    with app.app_context():
        # Query hurricanes with outcome data, prioritize recent
        query = Hurricane.query.filter(
            (Hurricane.deaths.isnot(None)) | (Hurricane.damage_usd.isnot(None))
        ).order_by(Hurricane.year.desc())
        
        if limit:
            query = query.limit(limit)
        
        hurricanes = query.all()
        
        logger.info(f"Found {len(hurricanes)} hurricanes with outcome data\n")
        
        for idx, hurricane in enumerate(hurricanes):
            logger.info(f"\n[{idx+1}/{len(hurricanes)}] Processing {hurricane.name} ({hurricane.year})")
            
            result = collect_for_hurricane(hurricane.id, census_api_key, noaa_token)
            
            overall_results['hurricanes'].append(result)
            overall_results['hurricanes_processed'] += 1
            
            if result.get('success'):
                overall_results['successful'] += 1
            else:
                overall_results['failed'] += 1
    
    logger.info(f"\n{'#'*80}")
    logger.info(f"✅ ALL HURRICANES COMPLETE: {overall_results['successful']}/{overall_results['hurricanes_processed']} successful")
    logger.info(f"{'#'*80}\n")
    
    return overall_results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Collect demographic data for hurricane analysis'
    )
    
    # Mode selection (mutually exclusive)
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('--hurricane', type=str, help='Hurricane ID (e.g., AL092005)')
    mode_group.add_argument('--year', type=int, help='Year (collect all hurricanes in year)')
    mode_group.add_argument('--all', action='store_true', help='Collect for all hurricanes')
    
    # API keys
    parser.add_argument('--census-key', type=str, help='Census Bureau API key')
    parser.add_argument('--noaa-token', type=str, help='NOAA API token')
    
    # Options
    parser.add_argument('--limit', type=int, help='Max hurricanes to process (for --all mode)')
    
    args = parser.parse_args()
    
    # Run appropriate collection mode
    if args.hurricane:
        results = collect_for_hurricane(args.hurricane, args.census_key, args.noaa_token)
    elif args.year:
        results = collect_for_year(args.year, args.census_key, args.noaa_token)
    elif args.all:
        results = collect_for_all(args.census_key, args.noaa_token, args.limit)
    
    # Print summary
    print("\n" + "="*80)
    print("COLLECTION SUMMARY")
    print("="*80)
    
    if args.hurricane:
        print(f"Hurricane: {results.get('hurricane_id')}")
        print(f"Success: {results.get('success')}")
    else:
        print(f"Hurricanes processed: {results.get('hurricanes_processed', 0)}")
        print(f"Successful: {results.get('successful', 0)}")
        print(f"Failed: {results.get('failed', 0)}")
    
    print("="*80)


if __name__ == '__main__':
    main()

