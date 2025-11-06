"""
Stock Market Data Collector
Collects S&P 500 company data for nominative determinism analysis
"""

import yfinance as yf
import pandas as pd
from datetime import datetime
import logging
import math
import time

from analyzers.name_analyzer import NameAnalyzer
from core.models import db, Stock, StockAnalysis

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
        self.sp500_tickers = list(dict.fromkeys(self.sp500_tickers))
        self.analyzer = NameAnalyzer()
    
    def collect_all_stocks(self, tickers=None, require_history_days=252, batch_commit=25):
        """Collect stock data, persist to the database, and return a summary."""
        tickers_to_process = tickers or self.sp500_tickers
        tickers_to_process = [t.strip().upper() for t in tickers_to_process if t]
        tickers_to_process = list(dict.fromkeys(tickers_to_process))
        summary = {
            'requested': len(tickers_to_process),
            'processed': 0,
            'added': 0,
            'updated': 0,
            'skipped_history': 0,
            'skipped_missing_info': 0,
            'errors': 0
        }
        all_company_names = [name for (name,) in db.session.query(Stock.company_name).all() if name]
        for idx, ticker in enumerate(tickers_to_process, start=1):
            try:
                summary['processed'] += 1
                if idx % 50 == 1:
                    logger.info("Progress: %s/%s", idx - 1, len(tickers_to_process))
                stock = yf.Ticker(ticker)
                info = stock.info or {}
                hist = stock.history(period="5y")
                if hist.empty or len(hist.dropna(subset=['Close'])) < require_history_days:
                    summary['skipped_history'] += 1
                    continue
                hist = hist.dropna(subset=['Close'])
                current_price = float(hist['Close'].iloc[-1])
                price_1yr_index = max(len(hist) - require_history_days, 0)
                price_1yr_ago = float(hist['Close'].iloc[price_1yr_index])
                price_5yr_ago = float(hist['Close'].iloc[0])
                if not all(math.isfinite(val) for val in (current_price, price_1yr_ago, price_5yr_ago)):
                    summary['skipped_history'] += 1
                    continue
                if price_1yr_ago <= 0 or price_5yr_ago <= 0:
                    summary['skipped_history'] += 1
                    continue
                return_1yr = ((current_price - price_1yr_ago) / price_1yr_ago) * 100
                return_5yr = ((current_price - price_5yr_ago) / price_5yr_ago) * 100
                company_name = info.get('longName') or info.get('shortName') or ticker
                market_cap = info.get('marketCap')
                if not company_name or market_cap is None:
                    summary['skipped_missing_info'] += 1
                    continue
                existing = Stock.query.filter_by(ticker=ticker).first()
                if existing:
                    existing.company_name = company_name
                    existing.sector = info.get('sector', existing.sector)
                    existing.industry = info.get('industry', existing.industry)
                    existing.market_cap = float(market_cap)
                    existing.current_price = current_price
                    existing.return_1yr = return_1yr
                    existing.return_5yr = return_5yr
                    existing.founded_year = info.get('foundedYear') or existing.founded_year
                    stock_record = existing
                    summary['updated'] += 1
                else:
                    stock_record = Stock(
                        ticker=ticker,
                        company_name=company_name,
                        sector=info.get('sector'),
                        industry=info.get('industry'),
                        market_cap=float(market_cap),
                        current_price=current_price,
                        return_1yr=return_1yr,
                        return_5yr=return_5yr,
                        founded_year=info.get('foundedYear'),
                        is_active=True
                    )
                    db.session.add(stock_record)
                    summary['added'] += 1
                db.session.flush()
                name_analysis = self.analyzer.analyze_name(company_name, all_company_names or None)
                ticker_analysis = self.analyzer.analyze_name(ticker)
                stock_analysis = StockAnalysis.query.filter_by(stock_id=stock_record.id).first()
                if stock_analysis:
                    stock_analysis.syllable_count = name_analysis.get('syllable_count')
                    stock_analysis.character_length = name_analysis.get('character_length')
                    stock_analysis.memorability_score = name_analysis.get('memorability_score')
                    stock_analysis.uniqueness_score = name_analysis.get('uniqueness_score')
                    stock_analysis.name_type = name_analysis.get('name_type')
                    stock_analysis.ticker_length = len(ticker)
                    stock_analysis.ticker_pronounceability = ticker_analysis.get('pronounceability_score')
                else:
                    stock_analysis = StockAnalysis(
                        stock_id=stock_record.id,
                        syllable_count=name_analysis.get('syllable_count'),
                        character_length=name_analysis.get('character_length'),
                        memorability_score=name_analysis.get('memorability_score'),
                        uniqueness_score=name_analysis.get('uniqueness_score'),
                        name_type=name_analysis.get('name_type'),
                        ticker_length=len(ticker),
                        ticker_pronounceability=ticker_analysis.get('pronounceability_score')
                    )
                    db.session.add(stock_analysis)
                if company_name not in all_company_names:
                    all_company_names.append(company_name)
                if summary['processed'] % batch_commit == 0:
                    db.session.commit()
                    logger.info("Committed %s records", summary['processed'])
                time.sleep(0.1)
            except Exception as exc:
                summary['errors'] += 1
                logger.warning("Error collecting %s: %s", ticker, exc)
                db.session.rollback()
                time.sleep(0.1)
                continue
        db.session.commit()
        logger.info(
            "Collected %s stocks (%s added, %s updated)",
            summary['processed'],
            summary['added'],
            summary['updated']
        )
        return summary

