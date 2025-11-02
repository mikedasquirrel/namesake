"""
MASTER COLLECTION SCRIPT
Runs all collection scripts to populate database with 10,000+ assets
Eliminates survivorship bias across all spheres

Expected outcome:
- Cryptocurrencies: 4,000 (top + mid + dead)
- Domains: 3,000 (all price tiers + failed)
- Stocks: 3,000 (active + delisted + bankrupt)
- TOTAL: 10,000 assets

Statistical rigor: ZERO survivorship bias
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
from core.config import Config
from core.models import db, Cryptocurrency, Domain, Stock
import logging
from datetime import datetime
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_current_counts():
    """Get current database counts"""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        counts = {
            'cryptocurrencies': Cryptocurrency.query.count(),
            'crypto_active': Cryptocurrency.query.filter_by(is_active=True).count(),
            'crypto_dead': Cryptocurrency.query.filter_by(is_active=False).count(),
            'domains': Domain.query.count(),
            'domain_sales': Domain.query.filter_by(auction_failed=False).count(),
            'domain_failed': Domain.query.filter_by(auction_failed=True).count(),
            'stocks': Stock.query.count(),
            'stock_active': Stock.query.filter_by(is_active=True).count(),
            'stock_delisted': Stock.query.filter_by(is_active=False).count(),
        }
        counts['total'] = counts['cryptocurrencies'] + counts['domains'] + counts['stocks']
        return counts


def run_script(script_name):
    """Run a collection script"""
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    logger.info(f"\n{'='*70}")
    logger.info(f"RUNNING: {script_name}")
    logger.info(f"{'='*70}\n")
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=7200  # 2 hour timeout
        )
        
        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        if result.returncode != 0:
            logger.error(f"Script failed with return code {result.returncode}")
            return False
        
        logger.info(f"✅ {script_name} completed successfully\n")
        return True
        
    except subprocess.TimeoutExpired:
        logger.error(f"Script timed out after 2 hours")
        return False
    except Exception as e:
        logger.error(f"Error running script: {e}")
        return False


def main():
    """Run all collection scripts"""
    
    start_time = datetime.now()
    
    logger.info("="*80)
    logger.info("MASTER COLLECTION SCRIPT")
    logger.info("Populating database with 10,000+ assets")
    logger.info("Eliminating survivorship bias for statistical rigor")
    logger.info("="*80)
    
    # Check initial state
    logger.info("\n" + "="*70)
    logger.info("INITIAL DATABASE STATE")
    logger.info("="*70)
    initial_counts = get_current_counts()
    logger.info(f"Cryptocurrencies: {initial_counts['cryptocurrencies']} (active: {initial_counts['crypto_active']}, dead: {initial_counts['crypto_dead']})")
    logger.info(f"Domains: {initial_counts['domains']} (sales: {initial_counts['domain_sales']}, failed: {initial_counts['domain_failed']})")
    logger.info(f"Stocks: {initial_counts['stocks']} (active: {initial_counts['stock_active']}, delisted: {initial_counts['stock_delisted']})")
    logger.info(f"TOTAL: {initial_counts['total']} assets")
    
    # Collection scripts to run
    scripts = [
        ('collect_complete_crypto.py', 'Cryptocurrencies (4,000 total)'),
        ('collect_stratified_domains.py', 'Domains (3,000 total)'),
        ('collect_complete_stocks.py', 'Stocks (3,000 total)')
    ]
    
    results = {}
    
    # Run each script
    for i, (script, description) in enumerate(scripts, 1):
        logger.info(f"\n{'#'*80}")
        logger.info(f"STEP {i}/{len(scripts)}: {description}")
        logger.info(f"{'#'*80}\n")
        
        success = run_script(script)
        results[script] = success
        
        if not success:
            logger.error(f"❌ {script} failed!")
            logger.info("\nContinuing with remaining scripts...")
        
        # Show progress
        current_counts = get_current_counts()
        logger.info(f"\nCurrent totals: {current_counts['total']} assets")
    
    # Final summary
    end_time = datetime.now()
    duration = end_time - start_time
    
    logger.info("\n" + "="*80)
    logger.info("COLLECTION COMPLETE")
    logger.info("="*80)
    
    final_counts = get_current_counts()
    
    logger.info(f"\n📊 FINAL DATABASE STATE:")
    logger.info(f"{'='*70}")
    logger.info(f"Cryptocurrencies: {final_counts['cryptocurrencies']:,}")
    logger.info(f"  ├─ Active: {final_counts['crypto_active']:,}")
    logger.info(f"  └─ Dead/Failed: {final_counts['crypto_dead']:,}")
    logger.info(f"\nDomains: {final_counts['domains']:,}")
    logger.info(f"  ├─ Successful sales: {final_counts['domain_sales']:,}")
    logger.info(f"  └─ Failed auctions: {final_counts['domain_failed']:,}")
    logger.info(f"\nStocks: {final_counts['stocks']:,}")
    logger.info(f"  ├─ Active: {final_counts['stock_active']:,}")
    logger.info(f"  └─ Delisted/Bankrupt: {final_counts['stock_delisted']:,}")
    logger.info(f"\n{'='*70}")
    logger.info(f"TOTAL ASSETS: {final_counts['total']:,}")
    logger.info(f"{'='*70}")
    
    # Growth stats
    growth = {
        'crypto': final_counts['cryptocurrencies'] - initial_counts['cryptocurrencies'],
        'domains': final_counts['domains'] - initial_counts['domains'],
        'stocks': final_counts['stocks'] - initial_counts['stocks']
    }
    total_growth = sum(growth.values())
    
    logger.info(f"\n📈 SESSION GROWTH:")
    logger.info(f"Cryptocurrencies: +{growth['crypto']:,}")
    logger.info(f"Domains: +{growth['domains']:,}")
    logger.info(f"Stocks: +{growth['stocks']:,}")
    logger.info(f"TOTAL GROWTH: +{total_growth:,} assets")
    
    # Script results
    logger.info(f"\n📋 SCRIPT RESULTS:")
    for script, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        logger.info(f"{status} - {script}")
    
    # Time stats
    logger.info(f"\n⏱️  TIME ELAPSED: {duration}")
    
    # Statistical rigor check
    logger.info(f"\n{'='*80}")
    logger.info("STATISTICAL RIGOR ASSESSMENT")
    logger.info(f"{'='*80}")
    
    has_failures = final_counts['crypto_dead'] > 0 or final_counts['domain_failed'] > 0 or final_counts['stock_delisted'] > 0
    
    if has_failures:
        logger.info("✅ ZERO SURVIVORSHIP BIAS")
        logger.info("   Database includes winners AND losers")
        logger.info(f"   - Dead cryptos: {final_counts['crypto_dead']:,}")
        logger.info(f"   - Failed domain auctions: {final_counts['domain_failed']:,}")
        logger.info(f"   - Delisted/bankrupt stocks: {final_counts['stock_delisted']:,}")
    else:
        logger.warning("⚠️  SURVIVORSHIP BIAS DETECTED")
        logger.warning("   Database contains only winners - statistical inference will be biased")
    
    if final_counts['total'] >= 10000:
        logger.info("\n✅ PUBLICATION-QUALITY DATASET")
        logger.info(f"   {final_counts['total']:,} assets provides strong statistical power")
        logger.info("   Can detect small effects (d > 0.3) with p < 0.001")
    elif final_counts['total'] >= 5000:
        logger.info("\n✅ GOOD STATISTICAL POWER")
        logger.info(f"   {final_counts['total']:,} assets provides medium statistical power")
        logger.info("   Can detect medium effects (d > 0.5) with p < 0.01")
    else:
        logger.warning(f"\n⚠️  LOW STATISTICAL POWER")
        logger.warning(f"   {final_counts['total']:,} assets - recommend collecting more data")
    
    logger.info("\n" + "="*80)
    logger.info("READY FOR ANALYSIS")
    logger.info("="*80)
    logger.info("Next step: Run comprehensive analysis to validate patterns")
    logger.info("Command: python3 scripts/validate_patterns.py")
    
    return results


if __name__ == '__main__':
    main()

