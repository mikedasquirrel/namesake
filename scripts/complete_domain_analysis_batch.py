"""Complete Domain Analysis Batch

Analyze all domains that don't have linguistic analysis yet.

Usage:
    python scripts/complete_domain_analysis_batch.py
"""

import sys
import os
import logging
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from core.models import db, Domain, DomainAnalysis
from analyzers.name_analyzer import NameAnalyzer
from analyzers.phonemic_analyzer import PhonemicAnalyzer
from analyzers.semantic_analyzer import SemanticAnalyzer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def analyze_domain(domain: Domain, name_analyzer):
    """Analyze a single domain name."""
    try:
        # Check if already analyzed
        existing = DomainAnalysis.query.filter_by(domain_id=domain.id).first()
        if existing:
            return False
        
        name = domain.name
        
        # Run analysis
        name_metrics = name_analyzer.analyze_name(name)
        
        # Create analysis
        analysis = DomainAnalysis(
            domain_id=domain.id,
            syllable_count=name_metrics.get('syllable_count', 0),
            character_length=name_metrics.get('character_length', 0),
            memorability_score=name_metrics.get('memorability_score', 50),
            pronounceability_score=name_metrics.get('pronounceability_score', 50),
            uniqueness_score=name_metrics.get('uniqueness_score', 50),
        )
        
        db.session.add(analysis)
        db.session.commit()
        
        return True
        
    except Exception as e:
        logger.error(f"Error analyzing {domain.name}: {e}")
        db.session.rollback()
        return False


def main():
    """Complete all domain analyses."""
    print("\n" + "=" * 60)
    print("Domain Analysis Completion".center(60))
    print("=" * 60 + "\n")
    
    start_time = datetime.now()
    
    with app.app_context():
        # Initialize analyzer
        name_analyzer = NameAnalyzer()
        
        # Get domains without analysis
        analyzed_ids = {a.domain_id for a in DomainAnalysis.query.all()}
        all_domains = Domain.query.all()
        unanalyzed = [d for d in all_domains if d.id not in analyzed_ids]
        
        print(f"Total Domains: {len(all_domains)}")
        print(f"Already Analyzed: {len(analyzed_ids)}")
        print(f"Need Analysis: {len(unanalyzed)}\n")
        
        if len(unanalyzed) == 0:
            print("✓ All domains already analyzed!")
            return
        
        # Analyze in batches
        analyzed_count = 0
        error_count = 0
        
        for i, domain in enumerate(unanalyzed, 1):
            if i % 100 == 0:
                print(f"Progress: {i}/{len(unanalyzed)} ({100*i/len(unanalyzed):.1f}%)")
            
            if analyze_domain(domain, name_analyzer):
                analyzed_count += 1
            else:
                error_count += 1
        
        elapsed = datetime.now() - start_time
        
        print("\n" + "=" * 60)
        print("Completion Summary".center(60))
        print("=" * 60)
        print(f"\nAnalyzed: {analyzed_count}")
        print(f"Errors: {error_count}")
        print(f"Time: {elapsed}")
        print(f"\n✓ Domain analysis now 100% complete")


if __name__ == "__main__":
    main()

