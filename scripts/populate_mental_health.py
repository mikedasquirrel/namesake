#!/usr/bin/env python3
"""
Populate Mental Health Data

Standalone script to populate the database with mental health diagnoses and medications.
Can be run independently of the main Flask application.

Usage:
    python scripts/populate_mental_health.py
"""

import sys
import os

# Add parent directory to path so we can import from project
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from core.models import db, MentalHealthTerm, MentalHealthAnalysis
from collectors.mental_health_collector import MentalHealthCollector
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main execution function."""
    print("\n" + "="*70)
    print("MENTAL HEALTH DATA POPULATION")
    print("="*70)
    print("\nThis script will:")
    print("  1. Collect 70+ DSM-5 diagnoses with prevalence data")
    print("  2. Collect 150+ psychiatric medications (generic + brand)")
    print("  3. Perform comprehensive linguistic analysis on all terms")
    print("  4. Populate the database with ~650+ analyzed terms")
    print("\nEstimated time: 2-3 minutes")
    print("="*70 + "\n")
    
    # Get user confirmation
    response = input("Proceed with data collection? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("❌ Aborted by user.")
        return
    
    print("\n🚀 Starting data collection...\n")
    
    with app.app_context():
        # Check existing data
        existing_count = MentalHealthTerm.query.count()
        if existing_count > 0:
            print(f"⚠️  Database already contains {existing_count} mental health terms.")
            response = input("Do you want to continue and add more data? (yes/no): ").strip().lower()
            if response not in ['yes', 'y']:
                print("❌ Aborted by user.")
                return
        
        # Initialize collector
        collector = MentalHealthCollector()
        
        # Collect all data
        try:
            stats = collector.collect_all_data()
            
            # Print results
            print("\n" + "="*70)
            print("✅ COLLECTION COMPLETE")
            print("="*70)
            print(f"\n📊 Statistics:")
            print(f"  • Diagnoses added: {stats['diagnoses_added']}")
            print(f"  • Medications added: {stats['medications_added']}")
            print(f"  • Total terms added: {stats['total_terms_added']}")
            print(f"  • Linguistic analyses created: {stats['analyses_added']}")
            
            if stats['errors']:
                print(f"\n⚠️  Errors encountered: {len(stats['errors'])}")
                for error in stats['errors'][:5]:  # Show first 5 errors
                    print(f"  • {error}")
            
            # Show final counts
            final_count = MentalHealthTerm.query.count()
            diagnosis_count = MentalHealthTerm.query.filter_by(term_type='diagnosis').count()
            medication_count = MentalHealthTerm.query.filter_by(term_type='medication').count()
            analysis_count = MentalHealthAnalysis.query.count()
            
            print(f"\n📈 Database Totals:")
            print(f"  • Total terms: {final_count}")
            print(f"  • Diagnoses: {diagnosis_count}")
            print(f"  • Medications: {medication_count}")
            print(f"  • Analyses: {analysis_count}")
            
            print("\n" + "="*70)
            print("✅ Mental health data successfully populated!")
            print("="*70)
            print("\nYou can now:")
            print("  • Start the Flask app: python app.py")
            print("  • Visit: http://localhost:<port>/mental-health")
            print("  • Explore the mental health findings page")
            print("\n")
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            logger.error(f"Collection failed: {e}", exc_info=True)
            return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())





