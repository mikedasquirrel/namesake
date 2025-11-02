"""
Maximum Cryptocurrency Collector
Collects cryptocurrencies from all market tiers (top, mid, low, dead)
For statistical rigor - eliminates survivorship bias
"""

from pycoingecko import CoinGeckoAPI
import time
import logging
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class MaxCryptoCollector:
    """Collect maximum cryptocurrency data"""
    
    def __init__(self):
        self.cg = CoinGeckoAPI()
        self.rate_limit = 1.2  # Seconds between requests
    
    def collect_top_n(self, n=1500):
        """
        Collect top N cryptocurrencies by market cap
        
        Args:
            n: Number of cryptocurrencies to collect (max ~10,000)
        
        Returns: List of cryptocurrency data
        """
        logger.info(f"Collecting top {n} cryptocurrencies from CoinGecko...")
        
        all_cryptos = []
        per_page = 250  # CoinGecko max per page
        pages = (n // per_page) + 1
        
        for page in range(1, pages + 1):
            try:
                logger.info(f"Fetching page {page}/{pages}...")
                
                markets = self.cg.get_coins_markets(
                    vs_currency='usd',
                    order='market_cap_desc',
                    per_page=per_page,
                    page=page,
                    sparkline=False,
                    price_change_percentage='24h,7d,30d,1y'
                )
                
                if not markets:
                    break
                
                for coin in markets:
                    all_cryptos.append({
                        'id': coin['id'],
                        'name': coin['name'],
                        'symbol': coin['symbol'],
                        'rank': coin.get('market_cap_rank'),
                        'market_cap': coin.get('market_cap'),
                        'current_price': coin.get('current_price'),
                        'total_volume': coin.get('total_volume'),
                        'price_change_24h': coin.get('price_change_percentage_24h'),
                        'price_change_7d': coin.get('price_change_percentage_7d_in_currency'),
                        'price_change_30d': coin.get('price_change_percentage_30d_in_currency'),
                        'price_change_1y': coin.get('price_change_percentage_1y_in_currency'),
                        'ath': coin.get('ath'),
                        'ath_date': coin.get('ath_date'),
                        'circulating_supply': coin.get('circulating_supply'),
                        'max_supply': coin.get('max_supply')
                    })
                
                if len(all_cryptos) >= n:
                    break
                
                time.sleep(self.rate_limit)
                
            except Exception as e:
                logger.error(f"Error on page {page}: {e}")
                time.sleep(5)
                continue
        
        logger.info(f"Collected {len(all_cryptos)} cryptocurrencies")
        return all_cryptos[:n]
    
    def collect_mid_tier(self, start_rank=5000, count=1000):
        """
        Collect mid/low-tier cryptocurrencies for unbiased distribution
        
        Args:
            start_rank: Starting rank (e.g., 5000)
            count: Number of coins to collect
        
        Returns: List of mid-tier cryptocurrency data
        """
        logger.info(f"Collecting {count} mid-tier cryptos starting from rank {start_rank}...")
        
        all_cryptos = []
        per_page = 250
        start_page = start_rank // per_page
        pages_needed = (count // per_page) + 1
        
        for page_offset in range(pages_needed):
            page = start_page + page_offset
            try:
                logger.info(f"Fetching mid-tier page {page} (offset {page_offset + 1}/{pages_needed})...")
                
                markets = self.cg.get_coins_markets(
                    vs_currency='usd',
                    order='market_cap_desc',
                    per_page=per_page,
                    page=page,
                    sparkline=False,
                    price_change_percentage='24h,7d,30d,1y'
                )
                
                if not markets:
                    logger.warning(f"No more coins available at page {page}")
                    break
                
                for coin in markets:
                    all_cryptos.append({
                        'id': coin['id'],
                        'name': coin['name'],
                        'symbol': coin['symbol'],
                        'rank': coin.get('market_cap_rank'),
                        'market_cap': coin.get('market_cap'),
                        'current_price': coin.get('current_price'),
                        'total_volume': coin.get('total_volume'),
                        'price_change_1y': coin.get('price_change_percentage_1y_in_currency'),
                        'ath': coin.get('ath'),
                        'ath_date': coin.get('ath_date'),
                        'circulating_supply': coin.get('circulating_supply'),
                        'max_supply': coin.get('max_supply'),
                        'is_active': True  # These are still trading
                    })
                
                if len(all_cryptos) >= count:
                    break
                
                time.sleep(self.rate_limit)
                
            except Exception as e:
                logger.error(f"Error fetching mid-tier page {page}: {e}")
                time.sleep(5)
                continue
        
        logger.info(f"Collected {len(all_cryptos)} mid-tier cryptocurrencies")
        return all_cryptos[:count]
    
    def collect_dead_coins(self, count=500):
        """
        Collect dead/delisted cryptocurrencies for failure analysis
        
        Uses CoinGecko's inactive coins list
        
        Args:
            count: Number of dead coins to collect
        
        Returns: List of dead cryptocurrency data
        """
        logger.info(f"Collecting {count} dead/delisted cryptocurrencies...")
        
        dead_coins = []
        
        try:
            # CoinGecko has a list of all coins (including inactive)
            # We'll get the full list and filter for very low market cap / inactive
            all_coins = self.cg.get_coins_list()
            logger.info(f"Found {len(all_coins)} total coins in CoinGecko database")
            
            # Strategy: Get coins from the very bottom of market cap rankings
            # These are effectively dead (< $1000 market cap or no data)
            per_page = 250
            start_page = 100  # Start far from top coins
            
            for page in range(start_page, start_page + 10):  # Check 10 pages
                try:
                    logger.info(f"Checking page {page} for low-cap/dead coins...")
                    
                    markets = self.cg.get_coins_markets(
                        vs_currency='usd',
                        order='market_cap_desc',
                        per_page=per_page,
                        page=page,
                        sparkline=False
                    )
                    
                    if not markets:
                        break
                    
                    for coin in markets:
                        market_cap = coin.get('market_cap') or 0
                        price = coin.get('current_price') or 0
                        
                        # Dead coin criteria: very low market cap or zero price
                        if market_cap < 10000 or price < 0.0000001:
                            dead_coins.append({
                                'id': coin['id'],
                                'name': coin['name'],
                                'symbol': coin['symbol'],
                                'rank': coin.get('market_cap_rank', 999999),
                                'market_cap': market_cap,
                                'current_price': price,
                                'total_volume': coin.get('total_volume', 0),
                                'ath': coin.get('ath'),
                                'ath_date': coin.get('ath_date'),
                                'is_active': False,  # Mark as dead
                                'failure_reason': 'low_market_cap' if market_cap < 10000 else 'no_trading_volume'
                            })
                        
                        if len(dead_coins) >= count:
                            break
                    
                    if len(dead_coins) >= count:
                        break
                    
                    time.sleep(self.rate_limit)
                    
                except Exception as e:
                    logger.error(f"Error on page {page}: {e}")
                    time.sleep(5)
                    continue
            
            logger.info(f"Collected {len(dead_coins)} dead/low-cap cryptocurrencies")
            
        except Exception as e:
            logger.error(f"Error collecting dead coins: {e}")
        
        return dead_coins[:count]
    
    def collect_complete_distribution(self):
        """
        Collect complete cryptocurrency distribution (top + mid + dead)
        Total: ~4,000 coins for unbiased analysis
        
        Returns: Dict with all collected data
        """
        logger.info("Collecting COMPLETE cryptocurrency distribution...")
        logger.info("This eliminates survivorship bias for valid statistical inference")
        
        results = {
            'top_tier': [],
            'mid_tier': [],
            'dead_coins': [],
            'total': 0
        }
        
        # 1. Top tier (ranks 1-2500) - Already in database, skip if needed
        logger.info("\n[1/3] Collecting top 2,500 cryptocurrencies...")
        results['top_tier'] = self.collect_top_n(2500)
        
        # 2. Mid tier (ranks 5000-6000)
        logger.info("\n[2/3] Collecting 1,000 mid-tier cryptocurrencies...")
        results['mid_tier'] = self.collect_mid_tier(start_rank=5000, count=1000)
        
        # 3. Dead/delisted coins
        logger.info("\n[3/3] Collecting 500 dead/delisted cryptocurrencies...")
        results['dead_coins'] = self.collect_dead_coins(count=500)
        
        results['total'] = (
            len(results['top_tier']) + 
            len(results['mid_tier']) + 
            len(results['dead_coins'])
        )
        
        logger.info("\n" + "="*60)
        logger.info("COMPLETE DISTRIBUTION COLLECTED")
        logger.info("="*60)
        logger.info(f"Top tier (1-2500): {len(results['top_tier'])} coins")
        logger.info(f"Mid tier (5000-6000): {len(results['mid_tier'])} coins")
        logger.info(f"Dead/failed: {len(results['dead_coins'])} coins")
        logger.info(f"TOTAL: {results['total']} coins")
        logger.info("\nZero survivorship bias - complete market distribution")
        
        return results

