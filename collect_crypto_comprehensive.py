#!/usr/bin/env python3
"""
Comprehensive Cryptocurrency Collection with Competitive Context
Collects 1000+ coins with launch dates, descriptions, and competitive cohorts
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask
from core.config import Config
from core.models import db, Cryptocurrency, NameAnalysis
from collectors.data_collector import DataCollector
from collectors.competitive_context_collector import CompetitiveContextCollector
from datetime import datetime
import logging
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    # Create Flask app with context
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        # Create tables
        db.create_all()
        logger.info("Database initialized")
        
        # Collect data
        logger.info("="*80)
        logger.info("CRYPTOCURRENCY COMPREHENSIVE COLLECTION")
        logger.info("="*80)
        logger.info("")
        logger.info("Target: 1,000 cryptocurrencies with competitive context")
        logger.info("Expected time: 15-20 minutes")
        logger.info("")
        
        collector = DataCollector()
        
        # Collect 1000 cryptos
        stats = collector.collect_all_data(1000)
        
        logger.info("")
        logger.info("="*80)
        logger.info("COLLECTION COMPLETE")
        logger.info("="*80)
        logger.info(f"Cryptocurrencies added: {stats['cryptocurrencies_added']}")
        logger.info(f"Cryptocurrencies updated: {stats['cryptocurrencies_updated']}")
        logger.info(f"Price histories: {stats['price_histories_added']}")
        logger.info(f"Name analyses: {stats['name_analyses_added']}")
        
        if stats['errors']:
            logger.warning(f"Errors: {len(stats['errors'])}")
        
        # Now add competitive context
        logger.info("")
        logger.info("="*80)
        logger.info("ADDING COMPETITIVE CONTEXT")
        logger.info("="*80)
        
        # Get all cryptos from database
        all_cryptos = Cryptocurrency.query.all()
        logger.info(f"Processing {len(all_cryptos)} cryptocurrencies for competitive context")
        
        # Convert to dicts for competitive context analysis
        crypto_dicts = []
        for crypto in all_cryptos:
            crypto_dict = {
                'id': crypto.id,
                'name': crypto.name,
                'symbol': crypto.symbol,
                'market_cap': crypto.market_cap or 0,
                'rank': crypto.rank or 999,
                'created_date': crypto.created_date,
                'outcome': crypto.market_cap or 0
            }
            
            # Get name analysis features
            if crypto.name_analysis:
                crypto_dict['harshness'] = getattr(crypto.name_analysis, 'harshness', 0)
                crypto_dict['syllables'] = getattr(crypto.name_analysis, 'syllable_count', 0)
                crypto_dict['length'] = getattr(crypto.name_analysis, 'name_length', 0)
                crypto_dict['memorability'] = getattr(crypto.name_analysis, 'memorability', 0)
            
            crypto_dicts.append(crypto_dict)
        
        # Add competitive context
        context_collector = CompetitiveContextCollector()
        enhanced_cryptos = context_collector.batch_collect_with_cohorts(
            crypto_dicts, 
            'crypto'
        )
        
        # Save enhanced data
        output_file = 'data/crypto_with_competitive_context.json'
        Path('data').mkdir(exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(enhanced_cryptos, f, indent=2, default=str)
        
        logger.info(f"Saved enhanced data to: {output_file}")
        
        # Quick statistics
        cohort_sizes = {}
        for crypto in enhanced_cryptos:
            cohort_key = crypto.get('competitive_context', {}).get('cohort_key', 'unknown')
            cohort_sizes[cohort_key] = cohort_sizes.get(cohort_key, 0) + 1
        
        logger.info(f"\nCohort distribution:")
        for cohort, size in sorted(cohort_sizes.items()):
            logger.info(f"  {cohort}: {size} coins")
        
        logger.info("")
        logger.info("="*80)
        logger.info("✅ COLLECTION COMPLETE WITH COMPETITIVE CONTEXT")
        logger.info("="*80)
        logger.info("")
        logger.info("Next steps:")
        logger.info("1. Run: python3 test_crypto_improvements.py")
        logger.info("2. See modeling improvements from competitive context")
        logger.info("")

if __name__ == '__main__':
    main()


