#!/usr/bin/env python3
"""
Demo: Investment Opportunity Predictor & Narrative Gap Analyzer

Shows how to use the tools to:
1. Predict investment opportunity of any coin
2. Identify the most valuable missing narrative element
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from analyzers.investment_opportunity_predictor import (
    InvestmentOpportunityPredictor,
    NarrativeGapAnalyzer,
    predict_investment,
    find_missing_element
)
import json

def demo_single_coin_prediction():
    """Demo: Predict opportunity for a single coin"""
    print("="*80)
    print("DEMO 1: Single Coin Prediction")
    print("="*80)
    print()
    
    # Example 1: Bitcoin (strong narrative)
    print("Example 1: Bitcoin")
    print("-"*80)
    result = predict_investment('Bitcoin', market_cap=2_034_000_000_000)
    
    print(f"Opportunity Score: {result['opportunity_score']}/100")
    print(f"Confidence: {result['confidence']}/100")
    print(f"Narrative Strength: {result['narrative_strength']}/100")
    print(f"Competitive Position: {result['competitive_position']}")
    print(f"Recommendation: {result['recommendation']}")
    print()
    print("Key Strengths:")
    for strength in result['key_strengths']:
        print(f"  ✓ {strength}")
    print()
    
    # Example 2: FluffyCoin (weak narrative)
    print("Example 2: FluffyCoin (hypothetical)")
    print("-"*80)
    result2 = predict_investment('FluffyCoin', market_cap=1_000_000)
    
    print(f"Opportunity Score: {result2['opportunity_score']}/100")
    print(f"Confidence: {result2['confidence']}/100")
    print(f"Recommendation: {result2['recommendation']}")
    print()
    print("Narrative Gaps:")
    for gap in result2['narrative_gaps'][:3]:
        print(f"  ⚠️  {gap['element']}: {gap['issue']}")
        print(f"      Fix: {gap['fix']}")
        print()
    print()

def demo_gap_analysis():
    """Demo: Find most valuable missing element"""
    print("="*80)
    print("DEMO 2: Narrative Gap Analysis")
    print("="*80)
    print()
    
    test_coins = [
        'SuperTechBlockchainProtocol',  # Over-technical
        'Doge2',  # Unoriginal meme
        'XYZ',  # No meaning
        'Ethereum'  # Well-designed
    ]
    
    for coin_name in test_coins:
        print(f"Analyzing: {coin_name}")
        print("-"*80)
        
        analysis = find_missing_element(coin_name)
        
        print(f"Current Score: {analysis['current_score']:.1f}/100")
        
        if analysis.get('most_valuable_gap'):
            gap = analysis['most_valuable_gap']
            print(f"\n🎯 MOST VALUABLE MISSING ELEMENT:")
            print(f"   Element: {gap['element']}")
            print(f"   Issue: {gap['issue']}")
            print(f"   Fix: {gap['fix']}")
            print(f"   Expected Impact: +{gap['estimated_improvement']} points → {gap['new_score_if_fixed']:.1f}/100")
            print(f"   Example: {gap.get('example', 'N/A')}")
        else:
            print("✅ No major gaps - narrative is complete!")
        
        print()
    print()

def demo_competitive_comparison():
    """Demo: Compare coins within competitive cohort"""
    print("="*80)
    print("DEMO 3: Competitive Comparison")
    print("="*80)
    print()
    
    # Load real data if available
    try:
        with open('data/crypto_with_competitive_context.json', 'r') as f:
            crypto_data = json.load(f)
        
        print(f"Loaded {len(crypto_data)} coins with competitive context")
        print()
        
        # Analyze top 10
        predictor = InvestmentOpportunityPredictor()
        
        print("Top 10 coins by market cap - Opportunity Analysis:")
        print("-"*80)
        
        for i, coin in enumerate(crypto_data[:10], 1):
            result = predictor.predict_opportunity(coin)
            
            print(f"{i:2}. {coin['name']:20} "
                  f"Opportunity: {result['opportunity_score']:5.1f} "
                  f"Position: {result['competitive_position']:12} "
                  f"Gaps: {len(result['narrative_gaps'])}")
        
        print()
        
        # Find best opportunities (high score, lower market cap)
        mid_cap_coins = [c for c in crypto_data if 1e6 < c.get('market_cap', 0) < 1e9]
        if mid_cap_coins:
            print("Hidden Gems (mid-cap with strong narrative):")
            print("-"*80)
            
            opportunities = []
            for coin in mid_cap_coins[:100]:  # Sample
                result = predictor.predict_opportunity(coin)
                if result['opportunity_score'] > 65:
                    opportunities.append({
                        'name': coin['name'],
                        'score': result['opportunity_score'],
                        'market_cap': coin.get('market_cap', 0)
                    })
            
            opportunities.sort(key=lambda x: x['score'], reverse=True)
            
            for opp in opportunities[:5]:
                print(f"  • {opp['name']:30} Score: {opp['score']:.1f} "
                      f"MCap: ${opp['market_cap']/1e6:.1f}M")
        
        print()
        
    except FileNotFoundError:
        print("⚠️  Crypto data file not found")
        print("   Run: python3 collect_crypto_comprehensive.py")
        print()

def main():
    print()
    print("="*80)
    print("INVESTMENT OPPORTUNITY PREDICTOR & NARRATIVE GAP ANALYZER")
    print("="*80)
    print()
    print("These tools help you:")
    print("1. Predict investment opportunity based on narrative strength")
    print("2. Identify the most valuable missing story element")
    print("3. Compare coins within competitive cohorts")
    print()
    
    demo_single_coin_prediction()
    demo_gap_analysis()
    demo_competitive_comparison()
    
    print("="*80)
    print("USAGE IN YOUR CODE")
    print("="*80)
    print()
    print("# Predict single coin")
    print("from analyzers.investment_opportunity_predictor import predict_investment")
    print("result = predict_investment('YourCoinName')")
    print("print(f\"Score: {result['opportunity_score']}\")")
    print()
    print("# Find missing element")
    print("from analyzers.investment_opportunity_predictor import find_missing_element")
    print("gaps = find_missing_element('YourCoinName')")
    print("print(f\"Fix: {gaps['quick_fix']}\")")
    print()

if __name__ == '__main__':
    main()

