#!/usr/bin/env python3
"""
COMPLETE 1-YEAR DATA COLLECTION
Aggressively collect 1-year price data for ALL cryptos
Target: 2,500+ cryptos with complete 1-year performance data
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
from core.config import Config
from core.models import db, Cryptocurrency, PriceHistory
from pycoingecko import CoinGeckoAPI
from datetime import datetime, date
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

cg = CoinGeckoAPI()

def main():
    with app.app_context():
        logger.info("="*70)
        logger.info("COMPLETE 1-YEAR DATA COLLECTION")
        logger.info("Target: 2,500+ cryptos with verified 1-year price data")
        logger.info("="*70 + "\n")
        
        # Get current state
        all_price_records = PriceHistory.query.all()
        logger.info(f"Current PriceHistory records: {len(all_price_records)}")
        
        # How many need 1yr data
        need_1yr = [p for p in all_price_records if p.price_1yr_change is None]
        logger.info(f"Need 1yr data: {len(need_1yr)} records")
        logger.info(f"Already have 1yr: {len(all_price_records) - len(need_1yr)}")
        logger.info("="*70 + "\n")
        
        # Strategy: Re-fetch using markets endpoint with explicit 1y parameter
        logger.info("Strategy: Re-fetching top 3,000 with explicit 1y price change request")
        logger.info("This should populate most missing 1yr data\n")
        
        updated = 0
        added_1yr = 0
        
        # Fetch in batches
        for page in range(1, 13):  # 12 pages * 250 = 3,000 cryptos
            logger.info(f"[Page {page}/12] Fetching top cryptos...")
            
            try:
                # EXPLICIT REQUEST for 1-year price change
                markets = cg.get_coins_markets(
                    vs_currency='usd',
                    order='market_cap_desc',
                    per_page=250,
                    page=page,
                    sparkline=False,
                    price_change_percentage='1y'  # EXPLICIT 1-year request
                )
                
                if not markets:
                    logger.warning(f"No data on page {page}")
                    break
                
                for coin in markets:
                    coin_id = coin['id']
                    
                    # Find existing PriceHistory
                    price_record = PriceHistory.query.filter_by(crypto_id=coin_id).first()
                    
                    if price_record:
                        # Update with 1yr data if we got it
                        price_1yr = coin.get('price_change_percentage_1y_in_currency')
                        if price_1yr is not None and price_record.price_1yr_change is None:
                            price_record.price_1yr_change = price_1yr
                            added_1yr += 1
                        
                        # Also update current price
                        price_record.price = coin.get('current_price', price_record.price)
                        price_record.market_cap = coin.get('market_cap', price_record.market_cap)
                        updated += 1
                    else:
                        # Create new if crypto exists in our database
                        if Cryptocurrency.query.get(coin_id):
                            price_record = PriceHistory(
                                crypto_id=coin_id,
                                date=date.today(),
                                price=coin.get('current_price', 0),
                                market_cap=coin.get('market_cap'),
                                volume=coin.get('total_volume'),
                                price_30d_change=coin.get('price_change_percentage_30d_in_currency'),
                                price_1yr_change=coin.get('price_change_percentage_1y_in_currency'),
                                price_ath_change=coin.get('ath_change_percentage')
                            )
                            db.session.add(price_record)
                            if price_record.price_1yr_change is not None:
                                added_1yr += 1
                
                # Commit this batch
                db.session.commit()
                logger.info(f"  Updated: {updated} | Added 1yr data: {added_1yr}")
                
                time.sleep(2)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Error on page {page}: {e}")
                db.session.rollback()
                continue
        
        # Final stats
        final_with_1yr = db.session.query(PriceHistory.crypto_id).filter(
            PriceHistory.price_1yr_change.isnot(None)
        ).distinct().count()
        
        logger.info("\n" + "="*70)
        logger.info("✅ COMPLETE!")
        logger.info("="*70)
        logger.info(f"Updated records: {updated}")
        logger.info(f"Added 1yr data: {added_1yr}")
        logger.info(f"Total cryptos with 1yr data: {final_with_1yr}")
        logger.info("="*70)
        logger.info(f"\n✅ SUCCESS: {final_with_1yr} cryptocurrencies ready for analysis!")
        logger.info("="*70 + "\n")

if __name__ == '__main__':
    main()

