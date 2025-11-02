#!/usr/bin/env python3
"""
FORCE cryptocurrency collection to 1,000
Runs until database actually has 1,000 cryptos
"""

import sys
sys.path.insert(0, '/Users/michaelsmerconish/Desktop/RandomCode/FlaskProject')

from flask import Flask
from core.config import Config
from core.models import db, Cryptocurrency, NameAnalysis
from pycoingecko import CoinGeckoAPI
from analyzers.name_analyzer import NameAnalyzer
from datetime import datetime
import time
import json

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

cg = CoinGeckoAPI()
name_analyzer = NameAnalyzer()

with app.app_context():
    start_count = Cryptocurrency.query.count()
    print(f"Starting with: {start_count} cryptos")
    print(f"Target: 1,000 cryptos")
    print(f"Need to collect: {1000 - start_count}")
    print("")
    
    # Get all existing IDs to avoid duplicates
    existing_ids = set(c.id for c in Cryptocurrency.query.all())
    
    added = 0
    
    # Loop through pages
    for page in range(1, 6):  # 5 pages × 250 = 1,250 (ensures we get 1,000)
        print(f"\nFetching page {page}...")
        
        try:
            markets = cg.get_coins_markets(
                vs_currency='usd',
                order='market_cap_desc',
                per_page=250,
                page=page,
                sparkline=False
            )
            
            if not markets:
                print(f"No data on page {page}")
                break
            
            print(f"Got {len(markets)} coins from page {page}")
            
            for coin in markets:
                coin_id = coin['id']
                
                if coin_id in existing_ids:
                    continue  # Skip existing
                
                # Create crypto
                crypto = Cryptocurrency(
                    id=coin_id,
                    name=coin['name'],
                    symbol=coin['symbol'].upper(),
                    rank=coin.get('market_cap_rank'),
                    market_cap=coin.get('market_cap'),
                    current_price=coin.get('current_price'),
                    total_volume=coin.get('total_volume'),
                    ath=coin.get('ath'),
                    ath_date=datetime.fromisoformat(coin['ath_date'].replace('Z', '+00:00')) if coin.get('ath_date') else None,
                    last_updated=datetime.utcnow()
                )
                
                db.session.add(crypto)
                existing_ids.add(coin_id)
                added += 1
                
                if added % 50 == 0:
                    db.session.commit()
                    current_total = Cryptocurrency.query.count()
                    print(f"  Progress: {added} new, {current_total} total")
            
            db.session.commit()
            current_total = Cryptocurrency.query.count()
            print(f"Page {page} complete - Total in DB: {current_total}")
            
            if current_total >= 1000:
                print(f"\n✅ TARGET REACHED: {current_total} cryptocurrencies")
                break
            
            time.sleep(1.5)  # Rate limiting
            
        except Exception as e:
            print(f"Error on page {page}: {e}")
            db.session.rollback()
            continue
    
    # Final count
    final_count = Cryptocurrency.query.count()
    print(f"\n{'='*70}")
    print(f"COLLECTION COMPLETE")
    print(f"{'='*70}")
    print(f"Started: {start_count}")
    print(f"Added: {added}")
    print(f"Final: {final_count}")
    print(f"{'='*70}")
    
    if final_count < 1000:
        print(f"\n⚠️  WARNING: Only got {final_count} cryptos (target was 1,000)")
    else:
        print(f"\n✅ SUCCESS: {final_count} cryptocurrencies in database")

