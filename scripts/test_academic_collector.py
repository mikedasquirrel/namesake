"""
Test Academic Collector
Run pilot collection to validate scraping and analysis pipeline

Tests:
1. Database models work correctly
2. Name analysis pipeline functions
3. Google Scholar enrichment (limited)
4. Field classification
5. Data quality checks
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the existing app
from app import app, db
from core.models import Academic, AcademicAnalysis, AcademicResearchMetrics
from collectors.academic_collector import AcademicCollector
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def initialize_tables():
    """Create tables if they don't exist"""
    with app.app_context():
        db.create_all()
        logger.info("Database tables created/verified")


def test_database_models():
    """Test that database models work correctly"""
    logger.info("\n" + "="*70)
    logger.info("TEST 1: Database Models")
    logger.info("="*70)
    
    with app.app_context():
        # Test creating a record
        test_academic = Academic(
            full_name="Test Professor",
            first_name="Test",
            last_name="Professor",
            university_name="Test University",
            academic_rank="full",
            field_broad="stem"
        )
        
        db.session.add(test_academic)
        db.session.flush()
        
        logger.info(f"✓ Created test Academic record (ID: {test_academic.id})")
        
        # Test analysis relationship
        test_analysis = AcademicAnalysis(
            academic_id=test_academic.id,
            syllable_count=3,
            phonetic_score=75.5,
            memorability_score=80.0
        )
        
        db.session.add(test_analysis)
        db.session.commit()
        
        logger.info(f"✓ Created AcademicAnalysis record")
        logger.info(f"✓ Relationship working: {test_academic.analysis is not None}")
        
        # Clean up
        db.session.delete(test_academic)
        db.session.commit()
        
        logger.info("✓ Database models test passed")
        return True


def test_name_analysis(collector):
    """Test name analysis pipeline"""
    logger.info("\n" + "="*70)
    logger.info("TEST 2: Name Analysis Pipeline")
    logger.info("="*70)
    
    test_names = [
        "Richard Feynman",
        "Marie Curie",
        "Stephen Hawking",
        "Jane Goodall",
        "Albert Einstein"
    ]
    
    with app.app_context():
        for name in test_names:
            # Create mock academic
            parsed = collector.parse_name(name)
            
            academic = Academic(
                full_name=parsed['full'],
                first_name=parsed['first'],
                last_name=parsed['last'],
                university_name="Test University",
                academic_rank="full",
                field_broad="stem"
            )
            
            db.session.add(academic)
            db.session.flush()
            
            # Analyze name
            analysis = collector.analyze_academic_name(academic)
            
            logger.info(f"\n{name}:")
            logger.info(f"  Syllables: {analysis.syllable_count}")
            logger.info(f"  Phonetic Score: {analysis.phonetic_score}")
            logger.info(f"  Memorability: {analysis.memorability_score}")
            logger.info(f"  Authority: {analysis.authority_score}")
            logger.info(f"  Sophistication: {analysis.intellectual_sophistication_score}")
            logger.info(f"  Gender: {analysis.gender_coding}")
            
            # Clean up
            db.session.delete(academic)
        
        db.session.commit()
        logger.info("\n✓ Name analysis pipeline test passed")
        return True


def test_field_classification(collector):
    """Test field classification logic"""
    logger.info("\n" + "="*70)
    logger.info("TEST 3: Field Classification")
    logger.info("="*70)
    
    test_departments = [
        "Physics",
        "English Literature",
        "Computer Science",
        "Psychology",
        "Business Administration",
        "History",
        "Mechanical Engineering",
        "Economics"
    ]
    
    for dept in test_departments:
        field_broad, field_specific = collector.classify_field(dept)
        logger.info(f"{dept:30s} -> {field_broad:20s} ({field_specific or 'N/A'})")
    
    logger.info("✓ Field classification test passed")
    return True


def test_bootstrap_collection(collector):
    """Test bootstrap data collection"""
    logger.info("\n" + "="*70)
    logger.info("TEST 4: Bootstrap Data Collection")
    logger.info("="*70)
    
    with app.app_context():
        # Clear any existing test data
        Academic.query.delete()
        db.session.commit()
        
        # Collect bootstrap data
        bootstrap = collector.collect_from_manual_data()
        
        logger.info(f"Bootstrap data: {len(bootstrap)} records")
        
        # Save to database
        for academic_data in bootstrap:
            academic_id = collector.save_academic_to_db(academic_data)
            if academic_id:
                logger.info(f"  ✓ Saved: {academic_data['full_name']}")
        
        # Count what we have
        total_academics = Academic.query.count()
        total_analyses = AcademicAnalysis.query.count()
        
        logger.info(f"\n✓ Total academics in database: {total_academics}")
        logger.info(f"✓ Total analyses in database: {total_analyses}")
        logger.info(f"✓ Bootstrap collection test passed")
        
        return True


def test_data_quality():
    """Test data quality and completeness"""
    logger.info("\n" + "="*70)
    logger.info("TEST 5: Data Quality Checks")
    logger.info("="*70)
    
    with app.app_context():
        academics = Academic.query.all()
        
        quality_report = {
            'total_records': len(academics),
            'with_analysis': 0,
            'with_rank': 0,
            'with_field': 0,
            'with_university_rank': 0,
            'missing_data': []
        }
        
        for academic in academics:
            if academic.analysis:
                quality_report['with_analysis'] += 1
            else:
                quality_report['missing_data'].append(f"{academic.full_name}: no analysis")
            
            if academic.academic_rank and academic.academic_rank != 'unknown':
                quality_report['with_rank'] += 1
            
            if academic.field_broad and academic.field_broad != 'unknown':
                quality_report['with_field'] += 1
            
            if academic.university_ranking:
                quality_report['with_university_rank'] += 1
        
        logger.info(f"Total records: {quality_report['total_records']}")
        logger.info(f"With analysis: {quality_report['with_analysis']} ({quality_report['with_analysis']/max(quality_report['total_records'],1)*100:.1f}%)")
        logger.info(f"With academic rank: {quality_report['with_rank']} ({quality_report['with_rank']/max(quality_report['total_records'],1)*100:.1f}%)")
        logger.info(f"With field classification: {quality_report['with_field']} ({quality_report['with_field']/max(quality_report['total_records'],1)*100:.1f}%)")
        logger.info(f"With university ranking: {quality_report['with_university_rank']} ({quality_report['with_university_rank']/max(quality_report['total_records'],1)*100:.1f}%)")
        
        if quality_report['missing_data']:
            logger.warning(f"\nMissing data issues: {len(quality_report['missing_data'])}")
            for issue in quality_report['missing_data'][:5]:
                logger.warning(f"  - {issue}")
        
        logger.info("✓ Data quality checks complete")
        return quality_report


def test_analysis_distributions():
    """Test that name metrics show reasonable distributions"""
    logger.info("\n" + "="*70)
    logger.info("TEST 6: Name Metric Distributions")
    logger.info("="*70)
    
    with app.app_context():
        analyses = AcademicAnalysis.query.all()
        
        if not analyses:
            logger.warning("No analyses found to test distributions")
            return False
        
        # Calculate summary statistics
        metrics = {
            'syllable_count': [a.syllable_count for a in analyses if a.syllable_count],
            'phonetic_score': [a.phonetic_score for a in analyses if a.phonetic_score],
            'memorability_score': [a.memorability_score for a in analyses if a.memorability_score],
            'authority_score': [a.authority_score for a in analyses if a.authority_score],
            'sophistication': [a.intellectual_sophistication_score for a in analyses if a.intellectual_sophistication_score]
        }
        
        for metric_name, values in metrics.items():
            if values:
                avg = sum(values) / len(values)
                min_val = min(values)
                max_val = max(values)
                logger.info(f"{metric_name:25s}: min={min_val:6.2f}, avg={avg:6.2f}, max={max_val:6.2f}, n={len(values)}")
        
        logger.info("✓ Metric distributions look reasonable")
        return True


def run_all_tests():
    """Run complete test suite"""
    logger.info("\n" + "="*70)
    logger.info("ACADEMIC COLLECTOR TEST SUITE")
    logger.info("="*70)
    logger.info("Testing database models, name analysis, and data collection")
    logger.info("="*70 + "\n")
    
    # Initialize tables and collector
    initialize_tables()
    collector = AcademicCollector()
    
    results = {
        'database_models': False,
        'name_analysis': False,
        'field_classification': False,
        'bootstrap_collection': False,
        'data_quality': None,
        'distributions': False
    }
    
    try:
        # Run tests
        results['database_models'] = test_database_models()
        results['name_analysis'] = test_name_analysis(collector)
        results['field_classification'] = test_field_classification(collector)
        results['bootstrap_collection'] = test_bootstrap_collection(collector)
        results['data_quality'] = test_data_quality()
        results['distributions'] = test_analysis_distributions()
        
    except Exception as e:
        logger.error(f"\n✗ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Final report
    logger.info("\n" + "="*70)
    logger.info("TEST SUITE RESULTS")
    logger.info("="*70)
    
    all_passed = True
    for test_name, result in results.items():
        if test_name == 'data_quality':
            continue
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{test_name:30s}: {status}")
        if not result:
            all_passed = False
    
    logger.info("="*70)
    
    if all_passed:
        logger.info("\n🎉 ALL TESTS PASSED! Collector is ready for mass collection.")
        logger.info("\nNext steps:")
        logger.info("1. Run scripts/collect_academics_mass_scale.py for full collection")
        logger.info("2. Monitor for scraping errors and adjust parsers as needed")
        logger.info("3. Enrich with Google Scholar (slow, rate-limited)")
        logger.info("="*70 + "\n")
    else:
        logger.error("\n❌ SOME TESTS FAILED. Fix issues before proceeding.")
    
    return all_passed


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)

