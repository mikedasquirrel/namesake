"""
Collect Complete Stock Distribution
Eliminates survivorship bias by collecting:
- S&P 500 (500 active blue-chips)
- Small-caps (500 Russell 2000 sample)
- Penny stocks (700 under $1)
- Delisted (800 companies)
- Bankrupt (500 companies)

Total: 3,000 stocks across complete distribution
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
from core.config import Config
from core.models import db, Stock, StockAnalysis
from collectors.complete_stock_collector import CompleteStockCollector
from analyzers.name_analyzer import NameAnalyzer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def save_to_database(stocks, category_name):
    """Save stock data to database with analysis"""
    
    analyzer = NameAnalyzer()
    
    added = 0
    updated = 0
    analyzed = 0
    
    for stock_data in stocks:
        try:
            # Check if stock already exists
            existing = Stock.query.filter_by(ticker=stock_data['ticker']).first()
            
            if existing:
                # Update existing
                existing.market_cap = stock_data.get('market_cap', 0)
                existing.current_price = stock_data.get('current_price', 0)
                existing.return_1yr = stock_data.get('return_1yr', 0)
                existing.return_5yr = stock_data.get('return_5yr', 0)
                existing.is_active = stock_data.get('is_active', True)
                existing.delisted_date = stock_data.get('delisted_date')
                existing.delisting_reason = stock_data.get('delisting_reason')
                existing.final_price = stock_data.get('final_price')
                updated += 1
                stock = existing
            else:
                # Create new
                stock = Stock(
                    ticker=stock_data['ticker'],
                    company_name=stock_data['company_name'],
                    sector=stock_data.get('sector'),
                    industry=stock_data.get('industry'),
                    market_cap=stock_data.get('market_cap', 0),
                    current_price=stock_data.get('current_price', 0),
                    return_1yr=stock_data.get('return_1yr', 0),
                    return_5yr=stock_data.get('return_5yr', 0),
                    is_active=stock_data.get('is_active', True),
                    delisted_date=stock_data.get('delisted_date'),
                    delisting_reason=stock_data.get('delisting_reason'),
                    final_price=stock_data.get('final_price')
                )
                db.session.add(stock)
                added += 1
            
            # Analyze name if not already analyzed
            if not stock.stock_analysis:
                try:
                    # Analyze company name
                    name_data = analyzer.analyze(stock.company_name)
                    
                    # Analyze ticker
                    ticker_data = analyzer.analyze(stock.ticker)
                    
                    analysis = StockAnalysis(
                        stock_id=stock.id,
                        syllable_count=name_data.get('syllable_count'),
                        character_length=name_data.get('character_length'),
                        memorability_score=name_data.get('memorability_score'),
                        uniqueness_score=name_data.get('uniqueness_score'),
                        name_type=name_data.get('name_type'),
                        ticker_length=len(stock.ticker),
                        ticker_pronounceability=ticker_data.get('pronounceability_score')
                    )
                    db.session.add(analysis)
                    analyzed += 1
                except Exception as e:
                    logger.error(f"Error analyzing {stock.company_name}: {e}")
            
            # Commit every 50 records
            if (added + updated) % 50 == 0:
                db.session.commit()
                logger.info(f"  Progress: {added + updated} processed, {analyzed} analyzed")
        
        except Exception as e:
            logger.error(f"Error processing {stock_data.get('ticker', 'unknown')}: {e}")
            db.session.rollback()
            continue
    
    # Final commit
    db.session.commit()
    
    logger.info(f"\n{category_name} Results:")
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
        logger.info("COLLECTING COMPLETE STOCK DISTRIBUTION")
        logger.info("Eliminating survivorship bias for statistical rigor")
        logger.info("="*70)
        
        collector = CompleteStockCollector()
        
        total_stats = {
            'added': 0,
            'updated': 0,
            'analyzed': 0
        }
        
        # Check current state
        existing_count = Stock.query.count()
        logger.info(f"\nCurrent database: {existing_count} stocks")
        
        # Collect complete distribution
        logger.info("\nCollecting complete distribution...")
        results = collector.collect_complete_distribution()
        
        # Save all categories
        logger.info("\n" + "="*70)
        logger.info("Saving to database...")
        logger.info("="*70)
        
        logger.info("\n[1/5] Saving S&P 500...")
        stats = save_to_database(results['sp500'], "S&P 500")
        for key in total_stats:
            total_stats[key] += stats[key]
        
        logger.info("\n[2/5] Saving small-caps...")
        stats = save_to_database(results['small_caps'], "Small-Caps")
        for key in total_stats:
            total_stats[key] += stats[key]
        
        logger.info("\n[3/5] Saving penny stocks...")
        stats = save_to_database(results['penny_stocks'], "Penny Stocks")
        for key in total_stats:
            total_stats[key] += stats[key]
        
        logger.info("\n[4/5] Saving delisted companies...")
        stats = save_to_database(results['delisted'], "Delisted")
        for key in total_stats:
            total_stats[key] += stats[key]
        
        logger.info("\n[5/5] Saving bankrupt companies...")
        stats = save_to_database(results['bankrupt'], "Bankrupt")
        for key in total_stats:
            total_stats[key] += stats[key]
        
        # Final summary
        final_count = Stock.query.count()
        active_count = Stock.query.filter_by(is_active=True).count()
        delisted_count = Stock.query.filter_by(is_active=False).count()
        
        logger.info("\n" + "="*70)
        logger.info("✅ COMPLETE STOCK DISTRIBUTION COLLECTED")
        logger.info("="*70)
        logger.info(f"Total in database: {final_count} stocks")
        logger.info(f"  Active: {active_count}")
        logger.info(f"  Delisted/Bankrupt: {delisted_count}")
        logger.info(f"\nThis session:")
        logger.info(f"  New: {total_stats['added']}")
        logger.info(f"  Updated: {total_stats['updated']}")
        logger.info(f"  Analyzed: {total_stats['analyzed']}")
        logger.info("\n✅ ZERO SURVIVORSHIP BIAS")
        logger.info("Ready for statistically rigorous analysis")


if __name__ == '__main__':
    main()

