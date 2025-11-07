"""Test Single NFL Player Collection

Tests collecting a single known player to verify everything works.
"""

import sys
import os
import time

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from collectors.nfl_collector import NFLCollector
from core.models import NFLPlayer, NFLPlayerAnalysis

print("\n" + "=" * 60)
print("NFL Single Player Test".center(60))
print("=" * 60 + "\n")

print("Waiting 10 seconds to respect rate limits...")
time.sleep(10)

with app.app_context():
    collector = NFLCollector()
    
    # Test with Patrick Mahomes (known player, good stats)
    player_id = "MahoPa00"
    player_url = "https://www.pro-football-reference.com/players/M/MahoPa00.htm"
    
    print(f"Collecting: Patrick Mahomes")
    print(f"URL: {player_url}\n")
    
    player = collector.collect_player(player_id, player_url)
    
    if player:
        print("\n✓ SUCCESS!")
        print(f"\nPlayer Data:")
        print(f"  Name: {player.name}")
        print(f"  Position: {player.position}")
        print(f"  Debut Year: {player.debut_year}")
        print(f"  Era: {player.era}s ({player.rule_era})")
        print(f"  Games: {player.games_played}")
        
        if player.passer_rating:
            print(f"\nQB Stats:")
            print(f"  Completion %: {player.completion_pct:.1f}%" if player.completion_pct else "  Completion %: N/A")
            print(f"  Passer Rating: {player.passer_rating:.1f}")
            if player.td_int_ratio:
                print(f"  TD/INT Ratio: {player.td_int_ratio:.2f}")
        elif player.completion_pct or player.passing_yards:
            print(f"\nQB Stats (Partial):")
            if player.completion_pct:
                print(f"  Completion %: {player.completion_pct:.1f}%")
            if player.passing_yards:
                print(f"  Passing Yards: {player.passing_yards:,}")
        
        # Check analysis
        analysis = NFLPlayerAnalysis.query.filter_by(player_id=player_id).first()
        if analysis:
            print(f"\nLinguistic Analysis:")
            print(f"  Syllables: {analysis.syllable_count}")
            print(f"  Memorability: {analysis.memorability_score:.1f}")
            print(f"  Harshness: {analysis.harshness_score:.1f}")
            print(f"  Toughness: {analysis.toughness_score:.1f}")
        else:
            print("\n⚠ No linguistic analysis found")
    else:
        print("\n✗ FAILED to collect player")

print("\n" + "=" * 60)
print("Test Complete".center(60))
print("=" * 60)

