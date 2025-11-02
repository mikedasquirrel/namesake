"""
Stock Market Data Collector
Collects S&P 500 company data for nominative determinism analysis
"""

import yfinance as yf
import pandas as pd
from datetime import datetime
import logging
import time

logger = logging.getLogger(__name__)


class StockCollector:
    """Collect stock market data"""
    
    def __init__(self):
        # S&P 500 tickers (partial list - most active/known companies)
        self.sp500_tickers = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK.B', 'UNH', 'XOM',
            'JNJ', 'JPM', 'V', 'PG', 'MA', 'HD', 'CVX', 'MRK', 'ABBV', 'PEP',
            'COST', 'AVGO', 'ADBE', 'CRM', 'MCD', 'CSCO', 'ACN', 'LIN', 'TMO', 'NFLX',
            'ABT', 'WMT', 'DHR', 'NKE', 'DIS', 'TXN', 'VZ', 'ORCL', 'COP', 'NEE',
            'CMCSA', 'PM', 'RTX', 'UPS', 'QCOM', 'INTU', 'HON', 'BMY', 'AMGN', 'LOW',
            'BA', 'SPGI', 'ELV', 'SBUX', 'IBM', 'GS', 'BLK', 'GILD', 'AMAT', 'CAT',
            'DE', 'MDLZ', 'ADP', 'LMT', 'ADI', 'BKNG', 'ISRG', 'MMC', 'TJX', 'VRTX',
            'CI', 'SYK', 'ZTS', 'AMT', 'PLD', 'MO', 'CB', 'SCHW', 'REGN', 'NOW',
            'TMUS', 'PGR', 'EOG', 'DUK', 'SO', 'BSX', 'ETN', 'ITW', 'GE', 'APD',
            'HCA', 'CSX', 'CL', 'USB', 'MMM', 'NSC', 'FI', 'WM', 'SLB', 'PNC',
            # Tech
            'INTC', 'AMD', 'SNAP', 'UBER', 'LYFT', 'SQ', 'SHOP', 'SPOT', 'ZM', 'DOCU',
            'TWLO', 'SNOW', 'CRWD', 'NET', 'DDOG', 'ZS', 'OKTA', 'MDB', 'TEAM', 'WDAY',
            # Finance
            'BAC', 'WFC', 'C', 'MS', 'AXP', 'COF', 'BK', 'STT', 'TFC', 'USB',
            # Consumer
            'KO', 'PEP', 'WMT', 'TGT', 'COST', 'HD', 'LOW', 'NKE', 'SBUX', 'MCD',
            # Healthcare
            'UNH', 'CVS', 'CI', 'HUM', 'ANTM', 'LLY', 'PFE', 'TMO', 'ABT', 'DHR',
            # Energy
            'XOM', 'CVX', 'COP', 'SLB', 'EOG', 'PSX', 'VLO', 'MPC', 'OXY', 'HAL',
            # More tech/growth
            'ROKU', 'PINS', 'ETSY', 'ABNB', 'DASH', 'COIN', 'RBLX', 'U', 'PLTR', 'SOFI',
            # Biotech
            'BIIB', 'VRTX', 'REGN', 'GILD', 'AMGN', 'ILMN', 'MRNA', 'BNTX', 'ALNY', 'SGEN',
            # Industrials
            'GE', 'CAT', 'DE', 'BA', 'LMT', 'RTX', 'HON', 'UPS', 'FDX', 'NSC',
            # Retail
            'AMZN', 'WMT', 'TGT', 'COST', 'HD', 'LOW', 'TJX', 'ROST', 'DG', 'DLTR',
            # Semiconductors
            'NVDA', 'AMD', 'INTC', 'QCOM', 'AVGO', 'TXN', 'ADI', 'MCHP', 'KLAC', 'LRCX',
            # Software
            'MSFT', 'ORCL', 'SAP', 'ADBE', 'CRM', 'NOW', 'INTU', 'ANSS', 'CDNS', 'SNPS',
            # Cloud
            'AMZN', 'MSFT', 'GOOGL', 'IBM', 'ORCL', 'SNOW', 'DDOG', 'MDB', 'NET', 'ESTC',
            # EV/Auto
            'TSLA', 'F', 'GM', 'RIVN', 'LCID', 'NIO', 'XPEV', 'LI', 'PLUG', 'BLNK',
            # Fintech
            'V', 'MA', 'PYPL', 'SQ', 'COIN', 'SOFI', 'AFRM', 'UPST', 'LC', 'NU',
            # E-commerce
            'AMZN', 'SHOP', 'MELI', 'EBAY', 'ETSY', 'W', 'CHWY', 'FTCH', 'CPNG', 'SE',
            # Streaming
            'NFLX', 'DIS', 'PARA', 'WBD', 'SPOT', 'ROKU', 'FUBO', 'DKNG', 'PENN', 'MGM',
            # Social Media
            'META', 'SNAP', 'PINS', 'TWTR', 'MTCH', 'BMBL', 'YELP', 'TRIP', 'GRPN', 'LFTR',
            # Cybersecurity
            'CRWD', 'ZS', 'PANW', 'FTNT', 'OKTA', 'DDOG', 'NET', 'S', 'TENB', 'RPD',
            # AI/ML
            'NVDA', 'GOOGL', 'MSFT', 'META', 'IBM', 'PLTR', 'AI', 'PATH', 'BBAI', 'SOUN',
            # Pharma
            'JNJ', 'PFE', 'MRK', 'ABBV', 'LLY', 'BMY', 'AMGN', 'GILD', 'BIIB', 'VRTX',
            # More variety
            'UBER', 'LYFT', 'DASH', 'ABNB', 'RBLX', 'HOOD', 'OPEN', 'COIN', 'MARA', 'RIOT'
        ]
        
        # Remove duplicates
        self.sp500_tickers = list(set(self.sp500_tickers))
    
    def collect_all_stocks(self):
        """Collect all available stock data"""
        logger.info(f"Collecting data for {len(self.sp500_tickers)} stocks...")
        
        stocks_data = []
        errors = 0
        
        for i, ticker in enumerate(self.sp500_tickers):
            try:
                if i % 50 == 0:
                    logger.info(f"Progress: {i}/{len(self.sp500_tickers)}")
                
                stock = yf.Ticker(ticker)
                info = stock.info
                hist = stock.history(period="5y")
                
                if len(hist) < 10:
                    continue
                
                # Calculate returns
                current_price = hist['Close'].iloc[-1] if len(hist) > 0 else 0
                price_1yr_ago = hist['Close'].iloc[-252] if len(hist) >= 252 else hist['Close'].iloc[0]
                price_5yr_ago = hist['Close'].iloc[0]
                
                return_1yr = ((current_price - price_1yr_ago) / price_1yr_ago * 100) if price_1yr_ago > 0 else 0
                return_5yr = ((current_price - price_5yr_ago) / price_5yr_ago * 100) if price_5yr_ago > 0 else 0
                
                stocks_data.append({
                    'ticker': ticker,
                    'company_name': info.get('longName', ticker),
                    'sector': info.get('sector', 'Unknown'),
                    'industry': info.get('industry', 'Unknown'),
                    'market_cap': info.get('marketCap', 0),
                    'current_price': current_price,
                    'return_1yr': return_1yr,
                    'return_5yr': return_5yr,
                    'employees': info.get('fullTimeEmployees', 0),
                    'founded_year': info.get('Founded', None)
                })
                
                time.sleep(0.1)  # Rate limiting
                
            except Exception as e:
                logger.warning(f"Error collecting {ticker}: {e}")
                errors += 1
                continue
        
        logger.info(f"Collected {len(stocks_data)} stocks ({errors} errors)")
        
        return stocks_data

