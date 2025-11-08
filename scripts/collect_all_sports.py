"""
Master script to collect all sports data for meta-analysis
Coordinates collection across all 7 sports
"""

import sys
import json
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from collectors.unified_sports_collector import get_collector

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def collect_all_sports():
    """
    Coordinate collection across all sports
    This is a master orchestration script
    """
    
    sports_config = {
        'soccer': {'target': 5000, 'priority': 1, 'estimated_time_hours': 48},
        'tennis': {'target': 2500, 'priority': 2, 'estimated_time_hours': 36},
        'boxing_mma': {'target': 3000, 'priority': 3, 'estimated_time_hours': 48},
        'basketball': {'target': 2000, 'priority': 4, 'estimated_time_hours': 12},
        'football': {'target': 2000, 'priority': 5, 'estimated_time_hours': 12},
        'baseball': {'target': 2000, 'priority': 6, 'estimated_time_hours': 24},
        'cricket': {'target': 2000, 'priority': 7, 'estimated_time_hours': 48}
    }
    
    total_target = sum(s['target'] for s in sports_config.values())
    total_hours = sum(s['estimated_time_hours'] for s in sports_config.values())
    
    logger.info("="*80)
    logger.info("SPORTS META-ANALYSIS DATA COLLECTION")
    logger.info("="*80)
    logger.info(f"Total target athletes: {total_target:,}")
    logger.info(f"Estimated collection time: {total_hours} hours ({total_hours/24:.1f} days)")
    logger.info(f"Sports to collect: {len(sports_config)}")
    logger.info("")
    
    results = {}
    
    for sport, config in sorted(sports_config.items(), key=lambda x: x[1]['priority']):
        logger.info(f"\n{'='*60}")
        logger.info(f"COLLECTING: {sport.upper()}")
        logger.info(f"Target: {config['target']:,} athletes")
        logger.info(f"Estimated time: {config['estimated_time_hours']} hours")
        logger.info(f"{'='*60}\n")
        
        try:
            collector = get_collector(sport)
            
            # Check existing data
            existing = collector.get_collected_count()
            logger.info(f"Existing data: {existing:,} athletes")
            
            if existing >= config['target']:
                logger.info(f"✓ {sport} already has sufficient data")
                results[sport] = {'status': 'complete', 'count': existing}
                continue
            
            # Collect data
            logger.info(f"Starting collection for {sport}...")
            collector.collect()
            
            # Validate
            validation = collector.validate_data()
            results[sport] = {
                'status': 'collected',
                'count': validation['total_athletes'],
                'validation': validation
            }
            
            # Export to JSON
            json_file = collector.export_to_json()
            results[sport]['json_file'] = json_file
            
            logger.info(f"✓ {sport} collection complete: {validation['total_athletes']:,} athletes")
            
        except Exception as e:
            logger.error(f"✗ Error collecting {sport}: {e}")
            results[sport] = {'status': 'error', 'error': str(e)}
    
    # Final summary
    logger.info("\n" + "="*80)
    logger.info("COLLECTION SUMMARY")
    logger.info("="*80)
    
    total_collected = sum(r.get('count', 0) for r in results.values())
    successful = sum(1 for r in results.values() if r['status'] in ['complete', 'collected'])
    
    logger.info(f"Sports processed: {len(results)}")
    logger.info(f"Successful collections: {successful}/{len(results)}")
    logger.info(f"Total athletes collected: {total_collected:,}")
    logger.info(f"Target achieved: {(total_collected/total_target*100):.1f}%")
    
    # Save summary
    summary_file = 'analysis_outputs/sports_meta_analysis/collection_summary.json'
    with open(summary_file, 'w') as f:
        json.dump({
            'collection_date': str(Path(__file__).stat().st_mtime),
            'target_total': total_target,
            'collected_total': total_collected,
            'sports': results
        }, f, indent=2)
    
    logger.info(f"\nSummary saved to: {summary_file}")
    logger.info("="*80)
    
    return results


if __name__ == "__main__":
    collect_all_sports()

