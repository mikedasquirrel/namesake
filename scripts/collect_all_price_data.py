#!/usr/bin/env python3
"""
Collect Price Data for ALL 3,500 Existing Cryptocurrencies
This populates PriceHistory for every crypto in the database
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
from core.config import Config
from core.models import db, Cryptocurrency, PriceHistory
from collectors.api_client import CoinGeckoClient
from datetime import datetime, date, timedelta
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def collect_price_history_for_crypto(crypto, api_client):
    """Collect price history for a single crypto"""
    try:
        # Check if already has price data
        existing = PriceHistory.query.filter_by(crypto_id=crypto.id).first()
        if existing:
            return False  # Already has data
        
        # Get historical data from CoinGecko
        coin_data = api_client.get_coin_details(crypto.id)
        if not coin_data:
            return False
        
        # Calculate performance metrics
        market_data = coin_data.get('market_data', {})
        
        price_30d = market_data.get('price_change_percentage_30d')
        price_90d = market_data.get('price_change_percentage_200d')  # Closest to 90d
        price_1yr = market_data.get('price_change_percentage_1y')
        
        current_price = market_data.get('current_price', {}).get('usd', 0)
        ath_price = market_data.get('ath', {}).get('usd', 0)
        
        # Calculate ATH change
        ath_change = ((current_price - ath_price) / ath_price * 100) if ath_price else None
        
        # Create price history record
        price_history = PriceHistory(
            crypto_id=crypto.id,
            date=date.today(),
            price=current_price,
            market_cap=market_data.get('market_cap', {}).get('usd'),
            volume=market_data.get('total_volume', {}).get('usd'),
            price_30d_change=price_30d,
            price_90d_change=price_90d,
            price_1yr_change=price_1yr,
            price_ath_change=ath_change
        )
        
        db.session.add(price_history)
        return True
        
    except Exception as e:
        logger.error(f"Error collecting price for {crypto.name}: {e}")
        return False


def main():
    with app.app_context():
        # Get all cryptos
        all_cryptos = Cryptocurrency.query.all()
        total = len(all_cryptos)
        
        logger.info("="*70)
        logger.info("COLLECTING PRICE DATA FOR ALL CRYPTOCURRENCIES")
        logger.info("="*70)
        logger.info(f"Total cryptocurrencies: {total}")
        logger.info(f"This will take approximately {int(total * 1.5 / 60)} minutes")
        logger.info("="*70 + "\n")
        
        api_client = CoinGeckoClient()
        
        added = 0
        skipped = 0
        errors = 0
        
        for i, crypto in enumerate(all_cryptos, 1):
            if i % 50 == 0:
                logger.info(f"Progress: {i}/{total} ({(i/total*100):.1f}%)")
                logger.info(f"  Added: {added}, Skipped: {skipped}, Errors: {errors}")
            
            success = collect_price_history_for_crypto(crypto, api_client)
            
            if success:
                added += 1
                # Commit every 10 to avoid losing progress
                if added % 10 == 0:
                    db.session.commit()
            elif success is False and PriceHistory.query.filter_by(crypto_id=crypto.id).first():
                skipped += 1
            else:
                errors += 1
            
            # Rate limiting - CoinGecko free tier allows ~50 calls/min
            time.sleep(1.2)  # ~50 calls per minute
        
        # Final commit
        db.session.commit()
        
        logger.info("\n" + "="*70)
        logger.info("✅ PRICE DATA COLLECTION COMPLETE")
        logger.info("="*70)
        logger.info(f"Price histories added: {added}")
        logger.info(f"Already had data: {skipped}")
        logger.info(f"Errors: {errors}")
        logger.info(f"Total processed: {total}")
        logger.info("="*70)
        
        # Verify
        cryptos_with_prices = db.session.query(PriceHistory.crypto_id).distinct().count()
        logger.info(f"\n✅ {cryptos_with_prices} cryptocurrencies now have price data")
        logger.info(f"Coverage: {(cryptos_with_prices/total*100):.1f}%")

if __name__ == '__main__':
    main()

