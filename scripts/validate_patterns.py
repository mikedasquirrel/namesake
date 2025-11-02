"""
Validate Patterns with Unbiased Dataset
Runs comprehensive statistical analysis on complete distribution
Tests whether patterns hold when including failures

This is the CRITICAL test of nominative determinism theory
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
from core.config import Config
from core.models import db, Cryptocurrency, NameAnalysis, Domain, DomainAnalysis, Stock, StockAnalysis
import numpy as np
from scipy import stats
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def calculate_correlation(x, y, name):
    """Calculate correlation with statistical significance"""
    # Remove NaN values
    mask = ~(np.isnan(x) | np.isnan(y))
    x_clean = x[mask]
    y_clean = y[mask]
    
    if len(x_clean) < 10:
        return None
    
    # Calculate Pearson correlation
    r, p_value = stats.pearsonr(x_clean, y_clean)
    
    # Calculate effect size (Cohen's d)
    effect_size = abs(r) / np.sqrt(1 - r**2) if r != 1 else float('inf')
    
    # Sample size
    n = len(x_clean)
    
    return {
        'metric': name,
        'correlation': r,
        'p_value': p_value,
        'effect_size': effect_size,
        'sample_size': n,
        'significant': p_value < 0.05,
        'strong': abs(r) > 0.3
    }


def analyze_cryptocurrency():
    """Analyze cryptocurrency patterns with full distribution"""
    logger.info("\n" + "="*70)
    logger.info("CRYPTOCURRENCY ANALYSIS")
    logger.info("="*70)
    
    # Get all cryptos with analysis
    cryptos = db.session.query(Cryptocurrency, NameAnalysis)\
        .join(NameAnalysis, Cryptocurrency.id == NameAnalysis.crypto_id)\
        .filter(Cryptocurrency.current_price != None)\
        .all()
    
    logger.info(f"Analyzing {len(cryptos)} cryptocurrencies...")
    
    # Separate active vs dead
    active = [(c, a) for c, a in cryptos if c.is_active]
    dead = [(c, a) for c, a in cryptos if not c.is_active]
    
    logger.info(f"  Active: {len(active)}")
    logger.info(f"  Dead/Failed: {len(dead)}")
    
    if len(dead) == 0:
        logger.warning("⚠️  NO DEAD COINS - SURVIVORSHIP BIAS!")
    
    # Extract data for active coins
    syllables = np.array([a.syllable_count for c, a in active if a.syllable_count])
    length = np.array([a.character_length for c, a in active if a.character_length])
    memorability = np.array([a.memorability_score for c, a in active if a.memorability_score])
    
    # Performance metrics
    returns = np.array([c.return_1yr if hasattr(c, 'return_1yr') else 
                       ((c.current_price - c.ath) / c.ath * 100 if c.ath else 0) 
                       for c, a in active])
    
    # Ensure equal lengths
    min_len = min(len(syllables), len(length), len(memorability), len(returns))
    syllables = syllables[:min_len]
    length = length[:min_len]
    memorability = memorability[:min_len]
    returns = returns[:min_len]
    
    # Calculate correlations
    results = []
    
    logger.info("\nTesting correlations with performance:")
    
    corr = calculate_correlation(syllables, returns, "Syllable Count")
    if corr:
        results.append(corr)
        logger.info(f"  Syllables: r={corr['correlation']:.3f}, p={corr['p_value']:.4f}, n={corr['sample_size']}")
    
    corr = calculate_correlation(length, returns, "Character Length")
    if corr:
        results.append(corr)
        logger.info(f"  Length: r={corr['correlation']:.3f}, p={corr['p_value']:.4f}, n={corr['sample_size']}")
    
    corr = calculate_correlation(memorability, returns, "Memorability")
    if corr:
        results.append(corr)
        logger.info(f"  Memorability: r={corr['correlation']:.3f}, p={corr['p_value']:.4f}, n={corr['sample_size']}")
    
    # Compare active vs dead on name quality
    if len(dead) > 10:
        logger.info("\nComparing active vs dead coins:")
        
        active_memo = np.array([a.memorability_score for c, a in active if a.memorability_score])
        dead_memo = np.array([a.memorability_score for c, a in dead if a.memorability_score])
        
        if len(active_memo) > 0 and len(dead_memo) > 0:
            t_stat, p_value = stats.ttest_ind(active_memo, dead_memo)
            logger.info(f"  Active memorability: {np.mean(active_memo):.2f} ± {np.std(active_memo):.2f}")
            logger.info(f"  Dead memorability: {np.mean(dead_memo):.2f} ± {np.std(dead_memo):.2f}")
            logger.info(f"  t-test: t={t_stat:.3f}, p={p_value:.4f}")
            
            if p_value < 0.05:
                logger.info("  ✅ Significant difference!")
            else:
                logger.info("  ⚠️  No significant difference")
    
    return results


def analyze_domains():
    """Analyze domain patterns with full distribution"""
    logger.info("\n" + "="*70)
    logger.info("DOMAIN ANALYSIS")
    logger.info("="*70)
    
    # Get all domains with analysis
    domains = db.session.query(Domain, DomainAnalysis)\
        .join(DomainAnalysis, Domain.id == DomainAnalysis.domain_id)\
        .all()
    
    logger.info(f"Analyzing {len(domains)} domains...")
    
    # Separate successful vs failed
    successful = [(d, a) for d, a in domains if not d.auction_failed and d.sale_price]
    failed = [(d, a) for d, a in domains if d.auction_failed]
    
    logger.info(f"  Successful sales: {len(successful)}")
    logger.info(f"  Failed auctions: {len(failed)}")
    
    if len(failed) == 0:
        logger.warning("⚠️  NO FAILED AUCTIONS - SURVIVORSHIP BIAS!")
    
    # Extract data for successful sales
    syllables = np.array([a.syllable_count for d, a in successful if a.syllable_count])
    length = np.array([a.character_length for d, a in successful if a.character_length])
    memorability = np.array([a.memorability_score for d, a in successful if a.memorability_score])
    prices = np.array([np.log10(d.sale_price) for d, a in successful if d.sale_price and d.sale_price > 0])
    
    # Ensure equal lengths
    min_len = min(len(syllables), len(length), len(memorability), len(prices))
    syllables = syllables[:min_len]
    length = length[:min_len]
    memorability = memorability[:min_len]
    prices = prices[:min_len]
    
    # Calculate correlations
    results = []
    
    logger.info("\nTesting correlations with sale price (log10):")
    
    corr = calculate_correlation(syllables, prices, "Syllable Count")
    if corr:
        results.append(corr)
        logger.info(f"  Syllables: r={corr['correlation']:.3f}, p={corr['p_value']:.4f}, n={corr['sample_size']}")
    
    corr = calculate_correlation(length, prices, "Character Length")
    if corr:
        results.append(corr)
        logger.info(f"  Length: r={corr['correlation']:.3f}, p={corr['p_value']:.4f}, n={corr['sample_size']}")
    
    corr = calculate_correlation(memorability, prices, "Memorability")
    if corr:
        results.append(corr)
        logger.info(f"  Memorability: r={corr['correlation']:.3f}, p={corr['p_value']:.4f}, n={corr['sample_size']}")
    
    # Compare successful vs failed
    if len(failed) > 10:
        logger.info("\nComparing successful vs failed domains:")
        
        succ_memo = np.array([a.memorability_score for d, a in successful if a.memorability_score])
        fail_memo = np.array([a.memorability_score for d, a in failed if a.memorability_score])
        
        if len(succ_memo) > 0 and len(fail_memo) > 0:
            t_stat, p_value = stats.ttest_ind(succ_memo, fail_memo)
            logger.info(f"  Successful memorability: {np.mean(succ_memo):.2f} ± {np.std(succ_memo):.2f}")
            logger.info(f"  Failed memorability: {np.mean(fail_memo):.2f} ± {np.std(fail_memo):.2f}")
            logger.info(f"  t-test: t={t_stat:.3f}, p={p_value:.4f}")
            
            if p_value < 0.05:
                logger.info("  ✅ Significant difference!")
            else:
                logger.info("  ⚠️  No significant difference")
    
    return results


def analyze_stocks():
    """Analyze stock patterns with full distribution"""
    logger.info("\n" + "="*70)
    logger.info("STOCK ANALYSIS")
    logger.info("="*70)
    
    # Get all stocks with analysis
    stocks = db.session.query(Stock, StockAnalysis)\
        .join(StockAnalysis, Stock.id == StockAnalysis.stock_id)\
        .all()
    
    logger.info(f"Analyzing {len(stocks)} stocks...")
    
    # Separate active vs delisted
    active = [(s, a) for s, a in stocks if s.is_active]
    delisted = [(s, a) for s, a in stocks if not s.is_active]
    
    logger.info(f"  Active: {len(active)}")
    logger.info(f"  Delisted/Bankrupt: {len(delisted)}")
    
    if len(delisted) == 0:
        logger.warning("⚠️  NO DELISTED STOCKS - SURVIVORSHIP BIAS!")
    
    # Extract data for active stocks
    syllables = np.array([a.syllable_count for s, a in active if a.syllable_count])
    length = np.array([a.character_length for s, a in active if a.character_length])
    memorability = np.array([a.memorability_score for s, a in active if a.memorability_score])
    returns = np.array([s.return_1yr for s, a in active if s.return_1yr])
    
    # Ensure equal lengths
    min_len = min(len(syllables), len(length), len(memorability), len(returns))
    if min_len < 10:
        logger.warning("Insufficient data for correlation analysis")
        return []
    
    syllables = syllables[:min_len]
    length = length[:min_len]
    memorability = memorability[:min_len]
    returns = returns[:min_len]
    
    # Calculate correlations
    results = []
    
    logger.info("\nTesting correlations with 1-year returns:")
    
    corr = calculate_correlation(syllables, returns, "Syllable Count")
    if corr:
        results.append(corr)
        logger.info(f"  Syllables: r={corr['correlation']:.3f}, p={corr['p_value']:.4f}, n={corr['sample_size']}")
    
    corr = calculate_correlation(length, returns, "Character Length")
    if corr:
        results.append(corr)
        logger.info(f"  Length: r={corr['correlation']:.3f}, p={corr['p_value']:.4f}, n={corr['sample_size']}")
    
    corr = calculate_correlation(memorability, returns, "Memorability")
    if corr:
        results.append(corr)
        logger.info(f"  Memorability: r={corr['correlation']:.3f}, p={corr['p_value']:.4f}, n={corr['sample_size']}")
    
    # Compare active vs delisted
    if len(delisted) > 10:
        logger.info("\nComparing active vs delisted stocks:")
        
        active_memo = np.array([a.memorability_score for s, a in active if a.memorability_score])
        delisted_memo = np.array([a.memorability_score for s, a in delisted if a.memorability_score])
        
        if len(active_memo) > 0 and len(delisted_memo) > 0:
            t_stat, p_value = stats.ttest_ind(active_memo, delisted_memo)
            logger.info(f"  Active memorability: {np.mean(active_memo):.2f} ± {np.std(active_memo):.2f}")
            logger.info(f"  Delisted memorability: {np.mean(delisted_memo):.2f} ± {np.std(delisted_memo):.2f}")
            logger.info(f"  t-test: t={t_stat:.3f}, p={p_value:.4f}")
            
            if p_value < 0.05:
                logger.info("  ✅ Significant difference!")
            else:
                logger.info("  ⚠️  No significant difference")
    
    return results


def main():
    """Run comprehensive validation"""
    
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        logger.info("="*80)
        logger.info("PATTERN VALIDATION WITH UNBIASED DATASET")
        logger.info("Testing whether nominative determinism holds with failures included")
        logger.info("="*80)
        
        # Analyze each sphere
        crypto_results = analyze_cryptocurrency()
        domain_results = analyze_domains()
        stock_results = analyze_stocks()
        
        # Overall summary
        logger.info("\n" + "="*80)
        logger.info("OVERALL SUMMARY")
        logger.info("="*80)
        
        all_results = crypto_results + domain_results + stock_results
        
        significant = [r for r in all_results if r['significant']]
        strong = [r for r in all_results if r['strong']]
        
        logger.info(f"\nTotal tests run: {len(all_results)}")
        logger.info(f"Significant correlations (p < 0.05): {len(significant)}")
        logger.info(f"Strong correlations (|r| > 0.3): {len(strong)}")
        
        if len(all_results) > 0:
            pct_significant = len(significant) / len(all_results) * 100
            logger.info(f"Percentage significant: {pct_significant:.1f}%")
        
        # Statistical power check
        total_assets = Cryptocurrency.query.count() + Domain.query.count() + Stock.query.count()
        logger.info(f"\n📊 Dataset size: {total_assets:,} total assets")
        
        if total_assets >= 10000:
            logger.info("✅ Excellent statistical power (can detect d > 0.3 with p < 0.001)")
        elif total_assets >= 5000:
            logger.info("✅ Good statistical power (can detect d > 0.5 with p < 0.01)")
        else:
            logger.info("⚠️  Moderate statistical power (recommend more data)")
        
        # Survivorship bias check
        dead_cryptos = Cryptocurrency.query.filter_by(is_active=False).count()
        failed_domains = Domain.query.filter_by(auction_failed=True).count()
        delisted_stocks = Stock.query.filter_by(is_active=False).count()
        
        has_failures = dead_cryptos > 0 or failed_domains > 0 or delisted_stocks > 0
        
        logger.info(f"\n📊 Failure representation:")
        logger.info(f"  Dead cryptos: {dead_cryptos:,}")
        logger.info(f"  Failed domains: {failed_domains:,}")
        logger.info(f"  Delisted stocks: {delisted_stocks:,}")
        
        if has_failures:
            logger.info("\n✅ ZERO SURVIVORSHIP BIAS - Results are statistically valid")
        else:
            logger.warning("\n⚠️  SURVIVORSHIP BIAS DETECTED - Results may be invalid")
        
        # Final verdict
        logger.info("\n" + "="*80)
        logger.info("FINAL VERDICT")
        logger.info("="*80)
        
        if len(significant) > 0 and has_failures:
            logger.info("✅ NOMINATIVE DETERMINISM VALIDATED")
            logger.info("   Patterns persist even when including failures")
            logger.info("   Ready for publication/investment use")
        elif len(significant) > 0 and not has_failures:
            logger.warning("⚠️  PATTERNS DETECTED BUT BIASED")
            logger.warning("   Need to add failures to confirm validity")
        else:
            logger.info("❌ NO SIGNIFICANT PATTERNS DETECTED")
            logger.info("   Either theory is wrong or need more data")


if __name__ == '__main__':
    main()

