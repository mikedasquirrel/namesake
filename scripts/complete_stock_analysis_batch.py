"""Complete Stock Analysis Batch

Analyze all stocks that don't have linguistic analysis yet.
Stocks are already in DB, just need to run analyzers.

Usage:
    python scripts/complete_stock_analysis_batch.py
"""

import sys
import os
import logging
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from core.models import db, Stock, StockAnalysis
from analyzers.name_analyzer import NameAnalyzer
from analyzers.phonemic_analyzer import PhonemicAnalyzer
from analyzers.semantic_analyzer import SemanticAnalyzer
from analyzers.sound_symbolism_analyzer import SoundSymbolismAnalyzer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def analyze_stock(stock: Stock, name_analyzer):
    """Analyze a single stock name."""
    try:
        # Check if already analyzed
        existing = StockAnalysis.query.filter_by(stock_id=stock.id).first()
        if existing:
            return False
        
        # Use company name for analysis
        name = stock.name if hasattr(stock, 'name') else (stock.company_name if hasattr(stock, 'company_name') else str(stock.id))
        ticker = stock.ticker if hasattr(stock, 'ticker') else (stock.symbol if hasattr(stock, 'symbol') else '')
        
        # Run analysis
        name_metrics = name_analyzer.analyze_name(name)
        ticker_metrics = name_analyzer.analyze_name(ticker) if ticker else {}
        
        # Create analysis
        analysis = StockAnalysis(
            stock_id=stock.id,
            syllable_count=name_metrics.get('syllable_count', 0),
            character_length=name_metrics.get('character_length', 0),
            memorability_score=name_metrics.get('memorability_score', 50),
            uniqueness_score=name_metrics.get('uniqueness_score', 50),
            name_type=name_metrics.get('name_type', 'Unknown'),
            ticker_length=len(ticker) if ticker else 0,
            ticker_pronounceability=ticker_metrics.get('pronounceability_score', 50) if ticker else 50,
        )
        
        db.session.add(analysis)
        db.session.commit()
        
        return True
        
    except Exception as e:
        logger.error(f"Error analyzing stock {stock.id}: {e}")
        db.session.rollback()
        return False


def main():
    """Complete all stock analyses."""
    print("\n" + "=" * 60)
    print("Stock Analysis Completion".center(60))
    print("=" * 60 + "\n")
    
    start_time = datetime.now()
    
    with app.app_context():
        # Initialize analyzer
        name_analyzer = NameAnalyzer()
        
        # Get stocks without analysis
        analyzed_ids = {a.stock_id for a in StockAnalysis.query.all()}
        all_stocks = Stock.query.all()
        unanalyzed = [s for s in all_stocks if s.id not in analyzed_ids]
        
        print(f"Total Stocks: {len(all_stocks)}")
        print(f"Already Analyzed: {len(analyzed_ids)}")
        print(f"Need Analysis: {len(unanalyzed)}\n")
        
        if len(unanalyzed) == 0:
            print("✓ All stocks already analyzed!")
            return
        
        # Analyze in batches
        analyzed_count = 0
        error_count = 0
        
        for i, stock in enumerate(unanalyzed, 1):
            if i % 100 == 0:
                print(f"Progress: {i}/{len(unanalyzed)} ({100*i/len(unanalyzed):.1f}%)")
            
            if analyze_stock(stock, name_analyzer):
                analyzed_count += 1
            else:
                error_count += 1
        
        elapsed = datetime.now() - start_time
        
        print("\n" + "=" * 60)
        print("Completion Summary".center(60))
        print("=" * 60)
        print(f"\nAnalyzed: {analyzed_count}")
        print(f"Errors: {error_count}")
        print(f"Time: {elapsed}")
        total_analyzed = len(analyzed_ids) + analyzed_count
        print(f"\n✓ Stock analysis now {100*total_analyzed/len(all_stocks):.1f}% complete")


if __name__ == "__main__":
    main()

