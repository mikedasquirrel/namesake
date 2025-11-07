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
        logger.info(f"Presidential candidates collected: {results['presidential']}")
        logger.info(f"Senate candidates collected: {results['senate']}")
        logger.info(f"Total candidates collected: {results['total']}")
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
        
        # Summary statistics
        presidential_count = ElectionCandidate.query.filter_by(position='President').count()
        senate_count = ElectionCandidate.query.filter_by(position='Senate').count()
        vp_count = ElectionCandidate.query.filter_by(position='Vice President').count()
        
        logger.info("Position breakdown:")
        logger.info(f"  - Presidential: {presidential_count}")
        logger.info(f"  - Vice Presidential: {vp_count}")
        logger.info(f"  - Senate: {senate_count}")
        logger.info("")
        
        # Coverage analysis
        if presidential_count > 0:
            years = db.session.query(
                db.func.min(ElectionCandidate.election_year),
                db.func.max(ElectionCandidate.election_year)
            ).filter(ElectionCandidate.position == 'President').first()
            
            if years[0]:
                logger.info(f"Presidential coverage: {years[0]}-{years[1]} ({years[1] - years[0] + 1} years)")
        
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

