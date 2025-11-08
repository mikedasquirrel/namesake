"""
Initialize Marriage Study Database

Sets up database tables and populates with baseline data.
Run this FIRST before collecting actual marriage data.
"""

import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
from datetime import datetime

from core.models import db
from core.marriage_models import (
    MarriedCouple, MarriageAnalysis, ChildName,
    DivorceBaseline, CelebrityMarriage, PredictionLock
)
from app import app  # Import Flask app to get db context

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def initialize_database():
    """Create all marriage study tables"""
    logger.info("=" * 80)
    logger.info("INITIALIZING MARRIAGE STUDY DATABASE")
    logger.info("=" * 80)
    
    with app.app_context():
        # Create tables
        logger.info("\nCreating database tables...")
        
        # Check if tables already exist
        inspector = db.inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        if 'married_couples' in existing_tables:
            logger.warning("Tables already exist. Skipping creation.")
            logger.info("To reset: drop tables manually and re-run.")
            return False
        
        # Create all tables
        db.create_all()
        
        logger.info("✓ Tables created:")
        logger.info("  - married_couples")
        logger.info("  - marriage_analyses")
        logger.info("  - child_names")
        logger.info("  - divorce_baselines")
        logger.info("  - celebrity_marriages")
        logger.info("  - prediction_locks")
        
        return True


def populate_baseline_data():
    """Populate divorce baseline statistics"""
    logger.info("\n" + "=" * 80)
    logger.info("POPULATING BASELINE DIVORCE STATISTICS")
    logger.info("=" * 80)
    
    with app.app_context():
        from collectors.marriage_collector import MarriageCollector
        
        collector = MarriageCollector()
        
        logger.info("\nCollecting baseline statistics from CDC/Census...")
        baselines = collector.collect_baseline_statistics()
        
        logger.info(f"✓ Generated {len(baselines)} baseline records")
        
        # Save to database
        for baseline in baselines:
            db.session.add(baseline)
        
        db.session.commit()
        
        logger.info("✓ Baseline data saved to database")
        
        # Show sample
        logger.info("\nSample baselines:")
        sample = db.session.query(DivorceBaseline).limit(5).all()
        for s in sample:
            logger.info(f"  {s.marriage_year_start}-{s.marriage_year_end} | Age {s.age_bracket} | {s.geographic_region}: "
                       f"Divorce rate = {s.divorce_rate:.1%}, "
                       f"Duration = {s.median_marriage_duration:.1f} years")


def generate_sample_data(n_samples: int = 100):
    """Generate sample marriage data for testing"""
    logger.info("\n" + "=" * 80)
    logger.info(f"GENERATING {n_samples} SAMPLE COUPLES FOR TESTING")
    logger.info("=" * 80)
    
    with app.app_context():
        from collectors.marriage_collector import MarriageCollector
        
        collector = MarriageCollector()
        
        logger.info("\nGenerating sample couples...")
        couples = collector.collect_sample(target_size=n_samples, stratify_by_era=True)
        
        logger.info(f"✓ Generated {len(couples)} sample couples")
        
        # Save to database
        for couple in couples:
            db.session.add(couple)
        
        db.session.commit()
        
        logger.info("✓ Sample data saved to database")
        
        # Show statistics
        total = db.session.query(MarriedCouple).count()
        divorced = db.session.query(MarriedCouple).filter_by(is_divorced=True).count()
        
        logger.info(f"\nDatabase statistics:")
        logger.info(f"  Total couples: {total}")
        logger.info(f"  Divorced: {divorced} ({divorced/total*100:.1f}%)")
        logger.info(f"  Still married: {total-divorced} ({(total-divorced)/total*100:.1f}%)")
        
        # Show sample couples
        logger.info("\nSample couples:")
        samples = db.session.query(MarriedCouple).limit(5).all()
        for s in samples:
            status = "Divorced" if s.is_divorced else "Married"
            logger.info(f"  {s.partner1_first} & {s.partner2_first}: "
                       f"{status}, {s.marriage_duration_years:.1f} years, "
                       f"Married {s.marriage_year}")


def analyze_sample_data():
    """Run analysis on sample data"""
    logger.info("\n" + "=" * 80)
    logger.info("ANALYZING SAMPLE DATA")
    logger.info("=" * 80)
    
    with app.app_context():
        from analyzers.relationship_compatibility_analyzer import RelationshipCompatibilityAnalyzer
        
        analyzer = RelationshipCompatibilityAnalyzer(db.session)
        
        # Get couples without analysis
        couples = db.session.query(MarriedCouple).filter(
            ~db.session.query(MarriageAnalysis).filter(
                MarriageAnalysis.couple_id == MarriedCouple.id
            ).exists()
        ).limit(50).all()
        
        logger.info(f"\nAnalyzing {len(couples)} couples...")
        
        analyzed = 0
        for i, couple in enumerate(couples):
            try:
                analysis = analyzer.analyze_couple(couple, include_children=False)
                db.session.add(analysis)
                analyzed += 1
                
                if (i + 1) % 10 == 0:
                    logger.info(f"  Processed {i + 1}/{len(couples)} couples...")
            
            except Exception as e:
                logger.error(f"Error analyzing couple {couple.id}: {e}")
        
        db.session.commit()
        
        logger.info(f"✓ Analyzed {analyzed} couples")
        
        # Show sample results
        logger.info("\nSample analysis results:")
        analyses = db.session.query(MarriageAnalysis).join(MarriedCouple).limit(5).all()
        
        for analysis in analyses:
            couple = analysis.couple
            logger.info(f"\n  {couple.partner1_first} & {couple.partner2_first}:")
            logger.info(f"    Compatibility: {analysis.compatibility_score:.3f}")
            logger.info(f"    Phonetic Distance: {analysis.phonetic_distance:.3f}")
            logger.info(f"    Golden Ratio Proximity: {analysis.golden_ratio_proximity:.3f}")
            logger.info(f"    Vowel Harmony: {analysis.vowel_harmony:.3f}")
            logger.info(f"    Relationship Type: {analysis.relationship_type}")
            logger.info(f"    Relative Success: {analysis.relative_success_score:.2f}" 
                       if analysis.relative_success_score else "    Relative Success: N/A")


def show_statistics():
    """Show database statistics"""
    logger.info("\n" + "=" * 80)
    logger.info("DATABASE STATISTICS")
    logger.info("=" * 80)
    
    with app.app_context():
        # Couples
        n_couples = db.session.query(MarriedCouple).count()
        n_divorced = db.session.query(MarriedCouple).filter_by(is_divorced=True).count()
        n_analyzed = db.session.query(MarriageAnalysis).count()
        n_baselines = db.session.query(DivorceBaseline).count()
        
        logger.info(f"\nCouples:")
        logger.info(f"  Total: {n_couples}")
        logger.info(f"  Divorced: {n_divorced} ({n_divorced/n_couples*100:.1f}%)" if n_couples > 0 else "  Divorced: 0")
        logger.info(f"  Still married: {n_couples - n_divorced}")
        logger.info(f"  Analyzed: {n_analyzed}")
        
        logger.info(f"\nBaseline Data:")
        logger.info(f"  Divorce baselines: {n_baselines}")
        
        # Show compatibility distribution
        if n_analyzed > 0:
            import numpy as np
            analyses = db.session.query(MarriageAnalysis).all()
            
            compat_scores = [a.compatibility_score for a in analyses if a.compatibility_score is not None]
            phone_distances = [a.phonetic_distance for a in analyses if a.phonetic_distance is not None]
            golden_scores = [a.golden_ratio_proximity for a in analyses if a.golden_ratio_proximity is not None]
            
            if compat_scores:
                logger.info(f"\nName Metrics Distribution:")
                logger.info(f"  Compatibility: μ={np.mean(compat_scores):.3f}, σ={np.std(compat_scores):.3f}")
                logger.info(f"  Phonetic Distance: μ={np.mean(phone_distances):.3f}, σ={np.std(phone_distances):.3f}")
                logger.info(f"  Golden Ratio Proximity: μ={np.mean(golden_scores):.3f}, σ={np.std(golden_scores):.3f}")


def main():
    """Main initialization sequence"""
    logger.info("\n" + "=" * 80)
    logger.info("MARRIAGE STUDY INITIALIZATION")
    logger.info("=" * 80)
    logger.info(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Initialize database
    tables_created = initialize_database()
    
    if not tables_created:
        logger.info("\nDatabase already initialized.")
        logger.info("Skipping to data generation...")
    
    # Step 2: Populate baselines
    populate_baseline_data()
    
    # Step 3: Generate sample data
    generate_sample_data(n_samples=100)
    
    # Step 4: Analyze sample
    analyze_sample_data()
    
    # Step 5: Show statistics
    show_statistics()
    
    logger.info("\n" + "=" * 80)
    logger.info("INITIALIZATION COMPLETE")
    logger.info("=" * 80)
    logger.info("\nNext steps:")
    logger.info("  1. Review sample data: python scripts/view_marriage_data.py")
    logger.info("  2. Run blind test: python scripts/run_marriage_blind_test.py")
    logger.info("  3. Run full analysis: python scripts/run_marriage_analysis.py")
    logger.info(f"\nEnd Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.error(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

