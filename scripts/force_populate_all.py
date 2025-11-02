#!/usr/bin/env python3
"""
FORCE POPULATE ALL - Get price data for ALL 3,500 existing cryptos
Uses batch markets endpoint to populate PriceHistory for everything
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
        logger.info("FORCE POPULATE ALL CRYPTOS WITH PRICE DATA")
        logger.info("="*70 + "\n")
        
        # Get all cryptos that need price data
        all_cryptos = Cryptocurrency.query.all()
        crypto_ids = {c.id: c for c in all_cryptos}
        
        existing_price_ids = set(p.crypto_id for p in PriceHistory.query.all())
        needed = [cid for cid in crypto_ids.keys() if cid not in existing_price_ids]
        
        logger.info(f"Total cryptos: {len(all_cryptos)}")
        logger.info(f"Already have price data: {len(existing_price_ids)}")
        logger.info(f"NEED price data: {len(needed)}")
        logger.info("="*70 + "\n")
        
        # Collect in batches using markets endpoint
        added = 0
        per_page = 250
        pages = 20  # Get top 5,000 cryptos to cover all 3,500
        
        for page in range(1, pages + 1):
            logger.info(f"[Page {page}/{pages}] Fetching...")
            
            try:
                markets = cg.get_coins_markets(
                    vs_currency='usd',
                    order='market_cap_desc',
                    per_page=per_page,
                    page=page,
                    sparkline=False,
                    price_change_percentage='1y'
                )
                
                if not markets:
                    break
                
                for coin in markets:
                    coin_id = coin['id']
                    
                    # Skip if already has price data
                    if coin_id in existing_price_ids:
                        continue
                    
                    # Skip if not in our database
                    if coin_id not in crypto_ids:
                        continue
                    
                    # Create PriceHistory
                    price_history = PriceHistory(
                        crypto_id=coin_id,
                        date=date.today(),
                        price=coin.get('current_price', 0),
                        market_cap=coin.get('market_cap'),
                        volume=coin.get('total_volume'),
                        price_30d_change=coin.get('price_change_percentage_30d_in_currency'),
                        price_1yr_change=coin.get('price_change_percentage_1y_in_currency'),
                        price_ath_change=coin.get('ath_change_percentage')
                    )
                    
                    db.session.add(price_history)
                    added += 1
                    existing_price_ids.add(coin_id)
                
                db.session.commit()
                logger.info(f"  Added {added} price histories so far...")
                
                time.sleep(1.5)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Error on page {page}: {e}")
                db.session.rollback()
        
        # Final count
        final_count = db.session.query(PriceHistory.crypto_id).distinct().count()
        
        logger.info("\n" + "="*70)
        logger.info("✅ COMPLETE!")
        logger.info("="*70)
        logger.info(f"Price histories added: {added}")
        logger.info(f"Total with price data: {final_count}")
        logger.info(f"Coverage: {(final_count/len(all_cryptos)*100):.1f}%")
        logger.info("="*70 + "\n")

if __name__ == '__main__':
    main()

