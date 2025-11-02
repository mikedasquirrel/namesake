#!/usr/bin/env python3
"""
FAST BULK CRYPTOCURRENCY COLLECTION
Uses CoinGecko /markets endpoint to get 2,500+ cryptos in ONE BATCH
Includes ALL price data in the response - no individual API calls needed!

Total time: 5-10 minutes for 2,500 cryptos
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
from core.config import Config
from core.models import db, Cryptocurrency, PriceHistory, NameAnalysis
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

def bulk_collect_cryptos(target_count=2500):
    """Collect cryptos using batch markets endpoint - FAST!"""
    
    with app.app_context():
        logger.info("="*70)
        logger.info(f"FAST BULK COLLECTION - Target: {target_count} cryptocurrencies")
        logger.info("="*70)
        logger.info("Using CoinGecko /markets endpoint for INSTANT batch data")
        logger.info("Includes price changes in response - no individual calls needed!")
        logger.info("="*70 + "\n")
        
        cryptos_added = 0
        price_histories_added = 0
        per_page = 250  # Max allowed by CoinGecko
        pages_needed = (target_count // per_page) + 1
        
        for page in range(1, pages_needed + 1):
            logger.info(f"\n[Page {page}/{pages_needed}] Fetching {per_page} cryptocurrencies...")
            
            try:
                # GET COMPLETE DATA IN ONE CALL!
                markets = cg.get_coins_markets(
                    vs_currency='usd',
                    order='market_cap_desc',
                    per_page=per_page,
                    page=page,
                    sparkline=False,
                    price_change_percentage='24h,7d,30d,1y'  # Get all price changes!
                )
                
                if not markets:
                    logger.warning(f"No data returned for page {page}")
                    break
                
                logger.info(f"✅ Got {len(markets)} cryptos with COMPLETE data")
                
                # Process each cryptocurrency
                for coin in markets:
                    try:
                        coin_id = coin['id']
                        
                        # Create or update Cryptocurrency
                        crypto = Cryptocurrency.query.get(coin_id)
                        if not crypto:
                            crypto = Cryptocurrency(
                                id=coin_id,
                                name=coin['name'],
                                symbol=coin['symbol'].upper(),
                                rank=coin.get('market_cap_rank'),
                                market_cap=coin.get('market_cap'),
                                current_price=coin.get('current_price'),
                                total_volume=coin.get('total_volume'),
                                circulating_supply=coin.get('circulating_supply'),
                                max_supply=coin.get('max_supply'),
                                ath=coin.get('ath'),
                                ath_date=datetime.fromisoformat(coin['ath_date'].replace('Z', '+00:00')) if coin.get('ath_date') else None,
                                last_updated=datetime.utcnow()
                            )
                            db.session.add(crypto)
                            cryptos_added += 1
                        else:
                            # Update existing
                            crypto.rank = coin.get('market_cap_rank')
                            crypto.market_cap = coin.get('market_cap')
                            crypto.current_price = coin.get('current_price')
                            crypto.last_updated = datetime.utcnow()
                        
                        # Create PriceHistory from market data (INSTANT!)
                        # Check if already exists
                        existing_price = PriceHistory.query.filter_by(crypto_id=coin_id).first()
                        if not existing_price:
                            price_history = PriceHistory(
                                crypto_id=coin_id,
                                date=date.today(),
                                price=coin.get('current_price', 0),
                                market_cap=coin.get('market_cap'),
                                volume=coin.get('total_volume'),
                                price_30d_change=coin.get('price_change_percentage_30d_in_currency'),
                                price_90d_change=None,  # Not in markets endpoint
                                price_1yr_change=coin.get('price_change_percentage_1y_in_currency'),
                                price_ath_change=coin.get('ath_change_percentage')
                            )
                            db.session.add(price_history)
                            price_histories_added += 1
                        
                    except Exception as e:
                        logger.error(f"Error processing {coin.get('name', 'unknown')}: {e}")
                        continue
                
                # Commit this page
                db.session.commit()
                logger.info(f"  Cryptos: +{cryptos_added} | Price histories: +{price_histories_added}")
                
                # Check if we hit target
                total_now = Cryptocurrency.query.count()
                if total_now >= target_count:
                    logger.info(f"\n✅ TARGET REACHED: {total_now} cryptocurrencies!")
                    break
                
                # Rate limiting - be respectful
                time.sleep(2)  # 2 seconds between pages
                
            except Exception as e:
                logger.error(f"Error on page {page}: {e}")
                db.session.rollback()
                continue
        
        # Final stats
        final_crypto_count = Cryptocurrency.query.count()
        final_price_count = db.session.query(PriceHistory.crypto_id).distinct().count()
        
        logger.info("\n" + "="*70)
        logger.info("✅ BULK COLLECTION COMPLETE!")
        logger.info("="*70)
        logger.info(f"Cryptocurrencies: {final_crypto_count}")
        logger.info(f"With price data: {final_price_count}")
        logger.info(f"Added this session:")
        logger.info(f"  - Cryptos: {cryptos_added}")
        logger.info(f"  - Price histories: {price_histories_added}")
        logger.info("="*70)
        logger.info("\nNext step: Run name analysis")
        logger.info("Command: python3 populate_missing_data.py")
        logger.info("="*70 + "\n")

if __name__ == '__main__':
    bulk_collect_cryptos(target_count=2500)

