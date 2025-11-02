import requests
import time
from datetime import datetime, timedelta
from core.config import Config
import logging

logger = logging.getLogger(__name__)


class CoinGeckoClient:
    """Client for CoinGecko API with rate limiting and error handling"""
    
    def __init__(self):
        self.base_url = Config.COINGECKO_API_BASE
        self.rate_limit = Config.COINGECKO_RATE_LIMIT
        self.last_request_time = 0
        self.min_request_interval = 60.0 / self.rate_limit  # seconds between requests
        
    def _rate_limited_request(self, endpoint, params=None):
        """Make rate-limited API request"""
        # Ensure we don't exceed rate limit
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.get(url, params=params, timeout=30)
            self.last_request_time = time.time()
            
            if response.status_code == 429:  # Rate limit exceeded
                logger.warning("Rate limit exceeded, waiting 60 seconds...")
                time.sleep(60)
                return self._rate_limited_request(endpoint, params)
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None
    
    def get_top_cryptocurrencies(self, limit=500):
        """
        Fetch top cryptocurrencies by market cap
        
        Args:
            limit: Number of cryptocurrencies to fetch
            
        Returns:
            List of cryptocurrency data dictionaries
        """
        all_cryptos = []
        per_page = 250  # CoinGecko max per page
        pages = (limit + per_page - 1) // per_page
        
        for page in range(1, pages + 1):
            logger.info(f"Fetching page {page}/{pages}...")
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': per_page,
                'page': page,
                'sparkline': False,
                'price_change_percentage': '24h,7d,30d,1y'
            }
            
            data = self._rate_limited_request('coins/markets', params)
            if data:
                all_cryptos.extend(data)
            
            if len(all_cryptos) >= limit:
                break
        
        return all_cryptos[:limit]
    
    def get_price_history(self, coin_id, days=365):
        """
        Get historical price data for a cryptocurrency
        
        Args:
            coin_id: CoinGecko coin ID
            days: Number of days of history (max 365 for free tier)
            
        Returns:
            Dictionary with price history and metadata
        """
        endpoint = f"coins/{coin_id}/market_chart"
        params = {
            'vs_currency': 'usd',
            'days': days,
            'interval': 'daily'
        }
        
        data = self._rate_limited_request(endpoint, params)
        if not data:
            return None
        
        # Parse price data
        prices = data.get('prices', [])
        market_caps = data.get('market_caps', [])
        volumes = data.get('total_volumes', [])
        
        history = []
        for i, (timestamp, price) in enumerate(prices):
            date = datetime.fromtimestamp(timestamp / 1000).date()
            history.append({
                'date': date,
                'price': price,
                'market_cap': market_caps[i][1] if i < len(market_caps) else None,
                'volume': volumes[i][1] if i < len(volumes) else None
            })
        
        return history
    
    def get_coin_details(self, coin_id):
        """
        Get detailed information about a specific cryptocurrency
        
        Args:
            coin_id: CoinGecko coin ID
            
        Returns:
            Dictionary with detailed coin data
        """
        endpoint = f"coins/{coin_id}"
        params = {
            'localization': False,
            'tickers': False,
            'community_data': False,
            'developer_data': False
        }
        
        return self._rate_limited_request(endpoint, params)
    
    def calculate_performance_metrics(self, price_history):
        """
        Calculate price performance metrics from historical data
        
        Args:
            price_history: List of price history dictionaries
            
        Returns:
            Dictionary with performance metrics
        """
        if not price_history or len(price_history) < 2:
            return {}
        
        current_price = price_history[-1]['price']
        metrics = {}
        
        # 30-day change
        if len(price_history) >= 30:
            price_30d_ago = price_history[-30]['price']
            if price_30d_ago > 0:
                metrics['price_30d_change'] = ((current_price - price_30d_ago) / price_30d_ago) * 100
        
        # 90-day change
        if len(price_history) >= 90:
            price_90d_ago = price_history[-90]['price']
            if price_90d_ago > 0:
                metrics['price_90d_change'] = ((current_price - price_90d_ago) / price_90d_ago) * 100
        
        # 1-year change
        if len(price_history) >= 365:
            price_1yr_ago = price_history[-365]['price']
            if price_1yr_ago > 0:
                metrics['price_1yr_change'] = ((current_price - price_1yr_ago) / price_1yr_ago) * 100
        
        # All-time high analysis
        all_prices = [p['price'] for p in price_history]
        ath_price = max(all_prices)
        if ath_price > 0:
            metrics['price_ath_change'] = ((current_price - ath_price) / ath_price) * 100
            metrics['ath'] = ath_price
            ath_index = all_prices.index(ath_price)
            metrics['ath_date'] = price_history[ath_index]['date']
        
        return metrics
    
    def ping(self):
        """Check API availability"""
        data = self._rate_limited_request('ping')
        return data is not None

