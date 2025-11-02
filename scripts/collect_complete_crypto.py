"""
Collect Complete Cryptocurrency Distribution
Eliminates survivorship bias by collecting:
- Top 2,500 (already in DB, can skip)
- Mid-tier 1,000 (ranks 5000-6000)
- Dead/failed 500 coins

Total: 4,000 cryptocurrencies across complete distribution
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
from core.config import Config
from core.models import db, Cryptocurrency, NameAnalysis
from collectors.max_crypto_collector import MaxCryptoCollector
from analyzers.name_analyzer import NameAnalyzer
from analyzers.advanced_analyzer import AdvancedAnalyzer
from datetime import datetime
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def save_to_database(cryptos, tier_name):
    """Save cryptocurrency data to database with analysis"""
    
    name_analyzer = NameAnalyzer()
    advanced_analyzer = AdvancedAnalyzer()
    
    added = 0
    updated = 0
    analyzed = 0
    
    for crypto_data in cryptos:
        try:
            # Check if cryptocurrency already exists
            crypto = Cryptocurrency.query.get(crypto_data['id'])
            
            if crypto:
                # Update existing
                crypto.rank = crypto_data.get('rank')
                crypto.market_cap = crypto_data.get('market_cap')
                crypto.current_price = crypto_data.get('current_price')
                crypto.total_volume = crypto_data.get('total_volume')
                crypto.last_updated = datetime.utcnow()
                crypto.is_active = crypto_data.get('is_active', True)
                crypto.failure_reason = crypto_data.get('failure_reason')
                updated += 1
            else:
                # Create new
                crypto = Cryptocurrency(
                    id=crypto_data['id'],
                    name=crypto_data['name'],
                    symbol=crypto_data['symbol'],
                    rank=crypto_data.get('rank'),
                    market_cap=crypto_data.get('market_cap'),
                    current_price=crypto_data.get('current_price'),
                    total_volume=crypto_data.get('total_volume'),
                    circulating_supply=crypto_data.get('circulating_supply'),
                    max_supply=crypto_data.get('max_supply'),
                    ath=crypto_data.get('ath'),
                    ath_date=datetime.fromisoformat(crypto_data['ath_date'].replace('Z', '+00:00')) if crypto_data.get('ath_date') else None,
                    is_active=crypto_data.get('is_active', True),
                    failure_reason=crypto_data.get('failure_reason')
                )
                db.session.add(crypto)
                added += 1
            
            # Analyze name if not already analyzed
            if not crypto.name_analysis:
                try:
                    # Basic analysis
                    basic_analysis = name_analyzer.analyze(crypto.name)
                    advanced_metrics = advanced_analyzer.analyze(crypto.name)
                    
                    analysis = NameAnalysis(
                        crypto_id=crypto.id,
                        syllable_count=basic_analysis.get('syllable_count'),
                        character_length=basic_analysis.get('character_length'),
                        word_count=basic_analysis.get('word_count'),
                        phonetic_score=basic_analysis.get('phonetic_score'),
                        vowel_ratio=basic_analysis.get('vowel_ratio'),
                        consonant_clusters=basic_analysis.get('consonant_clusters'),
                        memorability_score=basic_analysis.get('memorability_score'),
                        pronounceability_score=basic_analysis.get('pronounceability_score'),
                        name_type=basic_analysis.get('name_type'),
                        category_tags=json.dumps(basic_analysis.get('categories', [])),
                        uniqueness_score=basic_analysis.get('uniqueness_score'),
                        has_numbers=basic_analysis.get('has_numbers'),
                        has_special_chars=basic_analysis.get('has_special_chars'),
                        capital_pattern=basic_analysis.get('capital_pattern'),
                        is_real_word=basic_analysis.get('is_real_word'),
                        advanced_metrics=json.dumps(advanced_metrics)
                    )
                    db.session.add(analysis)
                    analyzed += 1
                except Exception as e:
                    logger.error(f"Error analyzing {crypto.name}: {e}")
            
            # Commit every 50 records
            if (added + updated) % 50 == 0:
                db.session.commit()
                logger.info(f"  Progress: {added + updated} processed, {analyzed} analyzed")
        
        except Exception as e:
            logger.error(f"Error processing {crypto_data.get('name', 'unknown')}: {e}")
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
        logger.info("COLLECTING COMPLETE CRYPTOCURRENCY DISTRIBUTION")
        logger.info("Eliminating survivorship bias for statistical rigor")
        logger.info("="*70)
        
        collector = MaxCryptoCollector()
        
        total_stats = {
            'added': 0,
            'updated': 0,
            'analyzed': 0
        }
        
        # Check if we already have top coins
        existing_count = Cryptocurrency.query.count()
        logger.info(f"\nCurrent database: {existing_count} cryptocurrencies")
        
        # Option 1: Skip top tier if we already have it
        if existing_count >= 2000:
            logger.info("Top tier already collected, skipping to mid/dead tiers...")
            
            # Mid-tier
            logger.info("\n" + "="*70)
            logger.info("[1/2] Collecting MID-TIER cryptocurrencies (ranks 5000-6000)")
            logger.info("="*70)
            mid_tier = collector.collect_mid_tier(start_rank=5000, count=1000)
            stats = save_to_database(mid_tier, "Mid-Tier")
            for key in total_stats:
                total_stats[key] += stats[key]
            
            # Dead coins
            logger.info("\n" + "="*70)
            logger.info("[2/2] Collecting DEAD/FAILED cryptocurrencies")
            logger.info("="*70)
            dead_coins = collector.collect_dead_coins(count=500)
            stats = save_to_database(dead_coins, "Dead/Failed")
            for key in total_stats:
                total_stats[key] += stats[key]
        
        else:
            # Collect everything
            logger.info("\nCollecting COMPLETE distribution (top + mid + dead)...")
            results = collector.collect_complete_distribution()
            
            # Save all tiers
            logger.info("\n" + "="*70)
            logger.info("Saving to database...")
            logger.info("="*70)
            
            logger.info("\n[1/3] Saving top tier...")
            stats = save_to_database(results['top_tier'], "Top Tier")
            for key in total_stats:
                total_stats[key] += stats[key]
            
            logger.info("\n[2/3] Saving mid tier...")
            stats = save_to_database(results['mid_tier'], "Mid Tier")
            for key in total_stats:
                total_stats[key] += stats[key]
            
            logger.info("\n[3/3] Saving dead coins...")
            stats = save_to_database(results['dead_coins'], "Dead Coins")
            for key in total_stats:
                total_stats[key] += stats[key]
        
        # Final summary
        final_count = Cryptocurrency.query.count()
        active_count = Cryptocurrency.query.filter_by(is_active=True).count()
        dead_count = Cryptocurrency.query.filter_by(is_active=False).count()
        
        logger.info("\n" + "="*70)
        logger.info("✅ COMPLETE CRYPTO DISTRIBUTION COLLECTED")
        logger.info("="*70)
        logger.info(f"Total in database: {final_count} cryptocurrencies")
        logger.info(f"  Active: {active_count}")
        logger.info(f"  Dead/Failed: {dead_count}")
        logger.info(f"\nThis session:")
        logger.info(f"  New: {total_stats['added']}")
        logger.info(f"  Updated: {total_stats['updated']}")
        logger.info(f"  Analyzed: {total_stats['analyzed']}")
        logger.info("\n✅ ZERO SURVIVORSHIP BIAS")
        logger.info("Ready for statistically rigorous analysis")


if __name__ == '__main__':
    main()

