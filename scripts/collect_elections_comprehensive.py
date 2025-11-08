#!/usr/bin/env python3
"""Comprehensive Election Data Collection Script

Collects election candidate data from multiple sources and performs linguistic analysis.

Usage:
    python scripts/collect_elections_comprehensive.py

Target:
    - Presidential: ~100 major candidates (1952-2024)
    - Senate: ~2,000 candidates (1950-2024)  
    - House: ~15,000 candidates (sample competitive races)
    - Gubernatorial: ~1,200 candidates (1950-2024)
    - State Legislature: ~5,000 competitive races (2000-2024)
    - Mayoral: ~500 major city candidates (2000-2024)

Author: Michael Smerconish
Date: November 2025
"""

import sys
import os
import logging
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from collectors.election_collector import ElectionCollector
from core.models import ElectionCandidate, RunningMateTicket, ElectionCandidateAnalysis

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('election_collection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Main collection routine."""
    logger.info("="*70)
    logger.info("ELECTION DATA COLLECTION - COMPREHENSIVE")
    logger.info("="*70)
    logger.info(f"Started: {datetime.now().isoformat()}")
    logger.info("")
    
    with app.app_context():
        # Create tables if they don't exist
        logger.info("Ensuring database tables exist...")
        db.create_all()
        
        # Initialize collector
        collector = ElectionCollector()
        
        # Check current state
        current_candidates = ElectionCandidate.query.count()
        current_tickets = RunningMateTicket.query.count()
        current_analyses = ElectionCandidateAnalysis.query.count()
        
        logger.info(f"Current database state:")
        logger.info(f"  - Candidates: {current_candidates}")
        logger.info(f"  - Tickets: {current_tickets}")
        logger.info(f"  - Analyses: {current_analyses}")
        logger.info("")
        
        # Collect data
        logger.info("Starting data collection...")
        logger.info("")
        
        results = collector.collect_all_available_data()
        
        logger.info("")
        logger.info("="*70)
        logger.info("COLLECTION COMPLETE")
        logger.info("="*70)
        logger.info("FEDERAL LEVEL:")
        logger.info(f"  Presidential: {results['presidential']}")
        logger.info(f"  Senate: {results['senate']}")
        logger.info(f"  House: {results.get('house', 0)}")
        logger.info("")
        logger.info("STATE LEVEL:")
        logger.info(f"  Gubernatorial: {results.get('gubernatorial', 0)}")
        logger.info(f"  State Administrative (AG, Controller, etc.): {results.get('state_administrative', 0)}")
        logger.info("")
        logger.info("LOCAL LEVEL - LAW ENFORCEMENT:")
        logger.info(f"  Sheriff: {results.get('sheriff', 0)}")
        logger.info(f"  District Attorney: {results.get('district_attorney', 0)}")
        logger.info("")
        logger.info("LOCAL LEVEL - EXECUTIVE/ADMINISTRATIVE:")
        logger.info(f"  Mayor: {results.get('mayor', 0)}")
        logger.info(f"  County Supervisor: {results.get('county_supervisor', 0)}")
        logger.info(f"  County Administrative (Clerk, Treasurer, Assessor, Coroner): {results.get('county_administrative', 0)}")
        logger.info("")
        logger.info(f"TOTAL CANDIDATES COLLECTED: {results['total']}")
        logger.info("")
        
        # Final database state
        final_candidates = ElectionCandidate.query.count()
        final_tickets = RunningMateTicket.query.count()
        final_analyses = ElectionCandidateAnalysis.query.count()
        
        logger.info(f"Final database state:")
        logger.info(f"  - Candidates: {final_candidates} (added {final_candidates - current_candidates})")
        logger.info(f"  - Tickets: {final_tickets} (added {final_tickets - current_tickets})")
        logger.info(f"  - Analyses: {final_analyses} (added {final_analyses - current_analyses})")
        logger.info("")
        
        # Summary statistics - ALL POSITIONS
        logger.info("="*70)
        logger.info("FINAL DATABASE STATE - ALL POSITION TYPES")
        logger.info("="*70)
        
        position_counts = {}
        all_positions = [
            'President', 'Vice President', 'Senate', 'House', 'Governor',
            'Sheriff', 'District Attorney', 'County Supervisor', 'Mayor',
            'State Controller', 'State Treasurer', 'State Auditor', 
            'Secretary of State', 'Attorney General',
            'County Clerk', 'County Treasurer', 'County Assessor', 'County Coroner'
        ]
        
        for pos in all_positions:
            count = ElectionCandidate.query.filter_by(position=pos).count()
            if count > 0:
                position_counts[pos] = count
        
        # Group by level
        federal_total = position_counts.get('President', 0) + position_counts.get('Vice President', 0) + \
                       position_counts.get('Senate', 0) + position_counts.get('House', 0)
        
        state_total = position_counts.get('Governor', 0) + \
                     position_counts.get('State Controller', 0) + position_counts.get('State Treasurer', 0) + \
                     position_counts.get('State Auditor', 0) + position_counts.get('Secretary of State', 0) + \
                     position_counts.get('Attorney General', 0)
        
        local_total = position_counts.get('Sheriff', 0) + position_counts.get('District Attorney', 0) + \
                     position_counts.get('County Supervisor', 0) + position_counts.get('Mayor', 0) + \
                     position_counts.get('County Clerk', 0) + position_counts.get('County Treasurer', 0) + \
                     position_counts.get('County Assessor', 0) + position_counts.get('County Coroner', 0)
        
        logger.info("FEDERAL LEVEL:")
        for pos in ['President', 'Vice President', 'Senate', 'House']:
            if pos in position_counts:
                logger.info(f"  - {pos}: {position_counts[pos]}")
        logger.info(f"  Federal Subtotal: {federal_total}")
        logger.info("")
        
        logger.info("STATE LEVEL:")
        for pos in ['Governor', 'State Controller', 'State Treasurer', 'State Auditor', 
                   'Secretary of State', 'Attorney General']:
            if pos in position_counts:
                logger.info(f"  - {pos}: {position_counts[pos]}")
        logger.info(f"  State Subtotal: {state_total}")
        logger.info("")
        
        logger.info("LOCAL LEVEL:")
        for pos in ['Sheriff', 'District Attorney', 'Mayor', 'County Supervisor',
                   'County Clerk', 'County Treasurer', 'County Assessor', 'County Coroner']:
            if pos in position_counts:
                logger.info(f"  - {pos}: {position_counts[pos]}")
        logger.info(f"  Local Subtotal: {local_total}")
        logger.info("")
        
        grand_total = federal_total + state_total + local_total
        logger.info(f"GRAND TOTAL: {grand_total} candidates")
        logger.info("")
        
        # Coverage analysis
        pres_count = position_counts.get('President', 0)
        if pres_count > 0:
            years = db.session.query(
                db.func.min(ElectionCandidate.election_year),
                db.func.max(ElectionCandidate.election_year)
            ).filter(ElectionCandidate.position == 'President').first()
            
            if years[0]:
                logger.info(f"Presidential coverage: {years[0]}-{years[1]} ({years[1] - years[0]} years)")
        
        # Position type breakdown
        logger.info("="*70)
        logger.info("POSITION TYPE ANALYSIS")
        logger.info("="*70)
        
        type_counts = db.session.query(
            ElectionCandidate.position_type,
            db.func.count(ElectionCandidate.id)
        ).filter(
            ElectionCandidate.position_type.isnot(None)
        ).group_by(ElectionCandidate.position_type).all()
        
        for pos_type, count in sorted(type_counts, key=lambda x: x[1], reverse=True):
            logger.info(f"  {pos_type}: {count} candidates")
        
        logger.info("")
        logger.info("Next steps:")
        logger.info("  1. Visit http://localhost:5000/elections to view dashboard")
        logger.info("  2. Visit http://localhost:5000/elections/findings for research findings")
        logger.info("  3. Visit http://localhost:5000/api/elections/analysis for statistical analysis")
        logger.info("")
        logger.info(f"Completed: {datetime.now().isoformat()}")
        logger.info("="*70)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n\nCollection interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n\nCollection failed with error: {str(e)}", exc_info=True)
        sys.exit(1)

