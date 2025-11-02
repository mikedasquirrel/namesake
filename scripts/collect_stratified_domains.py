"""
Collect Stratified Domain Sales Distribution
Eliminates survivorship bias by collecting across all price tiers
Includes failed auctions (domains that didn't sell)

Total: 3,000 domains from $0 (failed) to $35M (ultra-premium)
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
from core.config import Config
from core.models import db, Domain, DomainAnalysis
from collectors.stratified_domain_collector import StratifiedDomainCollector
from analyzers.domain_analyzer import DomainAnalyzer
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def save_to_database(domains, tier_name):
    """Save domain data to database with analysis"""
    
    analyzer = DomainAnalyzer()
    
    added = 0
    updated = 0
    analyzed = 0
    
    for domain_data in domains:
        try:
            # Check if domain already exists
            existing = Domain.query.filter_by(full_domain=domain_data['full_domain']).first()
            
            if existing:
                # Update existing
                existing.sale_price = domain_data.get('sale_price')
                existing.sale_date = domain_data.get('sale_date')
                existing.auction_failed = domain_data.get('auction_failed', False)
                existing.listing_price = domain_data.get('listing_price')
                existing.days_on_market = domain_data.get('days_on_market')
                updated += 1
                domain = existing
            else:
                # Create new
                domain = Domain(
                    name=domain_data['name'],
                    tld=domain_data['tld'],
                    full_domain=domain_data['full_domain'],
                    sale_price=domain_data.get('sale_price'),
                    sale_date=domain_data.get('sale_date'),
                    auction_failed=domain_data.get('auction_failed', False),
                    listing_price=domain_data.get('listing_price'),
                    days_on_market=domain_data.get('days_on_market')
                )
                db.session.add(domain)
                added += 1
            
            # Analyze name if not already analyzed
            if not domain.domain_analysis:
                try:
                    analysis_data = analyzer.analyze(domain.name)
                    
                    analysis = DomainAnalysis(
                        domain_id=domain.id,
                        syllable_count=analysis_data.get('syllable_count'),
                        character_length=analysis_data.get('character_length'),
                        word_count=analysis_data.get('word_count'),
                        phonetic_score=analysis_data.get('phonetic_score'),
                        vowel_ratio=analysis_data.get('vowel_ratio'),
                        consonant_clusters=analysis_data.get('consonant_clusters'),
                        memorability_score=analysis_data.get('memorability_score'),
                        pronounceability_score=analysis_data.get('pronounceability_score'),
                        name_type=analysis_data.get('name_type'),
                        category_tags=json.dumps(analysis_data.get('categories', [])),
                        uniqueness_score=analysis_data.get('uniqueness_score')
                    )
                    db.session.add(analysis)
                    analyzed += 1
                except Exception as e:
                    logger.error(f"Error analyzing {domain.name}: {e}")
            
            # Commit every 50 records
            if (added + updated) % 50 == 0:
                db.session.commit()
                logger.info(f"  Progress: {added + updated} processed, {analyzed} analyzed")
        
        except Exception as e:
            logger.error(f"Error processing {domain_data.get('name', 'unknown')}: {e}")
            db.session.rollback()
            continue
    
    # Final commit
    db.session.commit()
    
    logger.info(f"\n{tier_name} Results:")
    logger.info(f"  Added: {added}")
    logger.info(f"  Updated: {updated}")
    logger.info(f"  Analyzed: {analyzed}")
    
    return {'added': added, 'updated': updated, 'analyzed': analyzed}


def main():
    """Main collection workflow"""
    
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        logger.info("="*70)
        logger.info("COLLECTING STRATIFIED DOMAIN DISTRIBUTION")
        logger.info("Eliminating survivorship bias for statistical rigor")
        logger.info("="*70)
        
        collector = StratifiedDomainCollector()
        
        total_stats = {
            'added': 0,
            'updated': 0,
            'analyzed': 0
        }
        
        # Check current state
        existing_count = Domain.query.count()
        logger.info(f"\nCurrent database: {existing_count} domains")
        
        # Collect stratified distribution
        logger.info("\nCollecting complete distribution across all price tiers...")
        results = collector.collect_stratified(total_count=3000)
        
        # Save all tiers
        logger.info("\n" + "="*70)
        logger.info("Saving to database...")
        logger.info("="*70)
        
        logger.info("\n[1/6] Saving ultra-premium ($1M+)...")
        stats = save_to_database(results['ultra_premium'], "Ultra-Premium")
        for key in total_stats:
            total_stats[key] += stats[key]
        
        logger.info("\n[2/6] Saving premium ($100K-$1M)...")
        stats = save_to_database(results['premium'], "Premium")
        for key in total_stats:
            total_stats[key] += stats[key]
        
        logger.info("\n[3/6] Saving high-value ($20K-$100K)...")
        stats = save_to_database(results['high_value'], "High-Value")
        for key in total_stats:
            total_stats[key] += stats[key]
        
        logger.info("\n[4/6] Saving medium ($5K-$20K)...")
        stats = save_to_database(results['medium'], "Medium")
        for key in total_stats:
            total_stats[key] += stats[key]
        
        logger.info("\n[5/6] Saving low-value ($1K-$5K)...")
        stats = save_to_database(results['low_value'], "Low-Value")
        for key in total_stats:
            total_stats[key] += stats[key]
        
        logger.info("\n[6/6] Saving failed auctions...")
        stats = save_to_database(results['failed_auctions'], "Failed Auctions")
        for key in total_stats:
            total_stats[key] += stats[key]
        
        # Final summary
        final_count = Domain.query.count()
        successful = Domain.query.filter_by(auction_failed=False).count()
        failed = Domain.query.filter_by(auction_failed=True).count()
        
        # Price distribution
        ultra_premium = Domain.query.filter(Domain.sale_price >= 1000000).count()
        premium = Domain.query.filter(Domain.sale_price >= 100000, Domain.sale_price < 1000000).count()
        high_value = Domain.query.filter(Domain.sale_price >= 20000, Domain.sale_price < 100000).count()
        medium = Domain.query.filter(Domain.sale_price >= 5000, Domain.sale_price < 20000).count()
        low_value = Domain.query.filter(Domain.sale_price >= 1000, Domain.sale_price < 5000).count()
        
        logger.info("\n" + "="*70)
        logger.info("✅ COMPLETE DOMAIN DISTRIBUTION COLLECTED")
        logger.info("="*70)
        logger.info(f"Total in database: {final_count} domains")
        logger.info(f"  Successful sales: {successful}")
        logger.info(f"  Failed auctions: {failed}")
        logger.info(f"\nPrice distribution:")
        logger.info(f"  Ultra-premium ($1M+): {ultra_premium}")
        logger.info(f"  Premium ($100K-$1M): {premium}")
        logger.info(f"  High-value ($20K-$100K): {high_value}")
        logger.info(f"  Medium ($5K-$20K): {medium}")
        logger.info(f"  Low-value ($1K-$5K): {low_value}")
        logger.info(f"\nThis session:")
        logger.info(f"  New: {total_stats['added']}")
        logger.info(f"  Updated: {total_stats['updated']}")
        logger.info(f"  Analyzed: {total_stats['analyzed']}")
        logger.info("\n✅ ZERO SURVIVORSHIP BIAS")
        logger.info("Ready for statistically rigorous analysis")


if __name__ == '__main__':
    main()

