"""Monitor Background Data Enhancement Jobs

Checks progress of all running data collection/analysis jobs.

Usage:
    python scripts/monitor_background_jobs.py
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from core.models import db, Stock, StockAnalysis, Ship, ShipAnalysis, Domain, DomainAnalysis
from core.models import MentalHealthTerm, MentalHealthAnalysis, NBAPlayer, NBAPlayerAnalysis
from core.models import Band, BandAnalysis


def main():
    """Monitor all data enhancement progress."""
    print("\n" + "=" * 80)
    print("BACKGROUND DATA ENHANCEMENT - LIVE STATUS".center(80))
    print("=" * 80 + "\n")
    
    with app.app_context():
        # Phase 1: Analysis Completion
        print("PHASE 1: Complete Partial Analyses")
        print("-" * 80)
        
        stock_total = Stock.query.count()
        stock_analyzed = StockAnalysis.query.count()
        stock_pct = (stock_analyzed / stock_total * 100) if stock_total else 0
        print(f"Stocks:  {stock_analyzed:5d} / {stock_total:5d} ({stock_pct:5.1f}%) {'✓ COMPLETE' if stock_pct >= 99 else '⏳ Running'}")
        
        ship_total = Ship.query.count()
        ship_analyzed = ShipAnalysis.query.count()
        ship_pct = (ship_analyzed / ship_total * 100) if ship_total else 0
        print(f"Ships:   {ship_analyzed:5d} / {ship_total:5d} ({ship_pct:5.1f}%) {'✓ COMPLETE' if ship_pct >= 99 else '⏳ Running'}")
        
        domain_total = Domain.query.count()
        domain_analyzed = DomainAnalysis.query.count()
        domain_pct = (domain_analyzed / domain_total * 100) if domain_total else 0
        print(f"Domains: {domain_analyzed:5d} / {domain_total:5d} ({domain_pct:5.1f}%) {'✓ COMPLETE' if domain_pct >= 99 else '⏳ Running'}")
        
        phase1_complete = stock_pct >= 99 and ship_pct >= 99 and domain_pct >= 99
        
        # Phase 2: New Data Collection
        print(f"\nPHASE 2: High-Value New Data Collection")
        print("-" * 80)
        
        mh_terms = MentalHealthTerm.query.count()
        mh_analyzed = MentalHealthAnalysis.query.count()
        mh_status = "✓ COMPLETE" if mh_terms >= 500 else ("⏳ Running" if mh_terms > 0 else "⏸ Pending")
        print(f"Mental Health:  {mh_terms:5d} terms, {mh_analyzed:5d} analyzed  {mh_status}")
        
        nba_players = NBAPlayer.query.count()
        nba_analyzed = NBAPlayerAnalysis.query.count()
        nba_status = "✓ COMPLETE" if nba_players >= 1000 else ("⏳ Running" if nba_players > 0 else "⏸ Pending")
        print(f"NBA Players:    {nba_players:5d} players, {nba_analyzed:5d} analyzed  {nba_status}")
        
        try:
            bands = Band.query.count()
            band_analyzed = BandAnalysis.query.count()
            band_status = "✓ COMPLETE" if bands >= 500 else ("⏳ Running" if bands > 0 else "⏸ Pending")
            print(f"Bands:          {bands:5d} bands, {band_analyzed:5d} analyzed  {band_status}")
        except Exception as e:
            bands = 0
            band_analyzed = 0
            print(f"Bands:          ERROR (schema issue - {str(e)[:30]})")
        
        # Overall Summary
        print(f"\nOVERALL PLATFORM STATUS")
        print("=" * 80)
        
        total_entities = stock_total + ship_total + domain_total + mh_terms + nba_players + bands
        total_analyzed = stock_analyzed + ship_analyzed + domain_analyzed + mh_analyzed + nba_analyzed + band_analyzed
        
        print(f"Total Entities:  {total_entities:6d}")
        print(f"Total Analyzed:  {total_analyzed:6d} ({total_analyzed/total_entities*100 if total_entities else 0:.1f}%)")
        
        # Recommendations
        print(f"\nNEXT ACTIONS")
        print("-" * 80)
        
        if not phase1_complete:
            print("⏳ Phase 1 analysis still running (should complete in minutes)")
        else:
            print("✓ Phase 1 complete!")
        
        if mh_terms < 500:
            print("⏳ Mental health collection running...")
        else:
            print("✓ Mental health complete!")
        
        if nba_players < 1000:
            print("⏳ NBA collection running (will take 2-4 hours with rate limiting)")
        else:
            print("✓ NBA complete!")
        
        if bands < 500:
            print("⏳ Band collection running...")
        else:
            print("✓ Bands complete!")
        
        print(f"\n💡 Rerun this script anytime to check progress: python scripts/monitor_background_jobs.py")
        print("=" * 80 + "\n")


if __name__ == "__main__":
    main()

