#!/usr/bin/env python3
"""
Analyze 3,514 coins to find:
1. Most undervalued (strong narrative, low market cap)
2. Most absent names (what patterns are missing)
"""

import json
import numpy as np
from collections import Counter
from analyzers.investment_opportunity_predictor import InvestmentOpportunityPredictor

print("="*80)
print("CRYPTO OPPORTUNITY ANALYSIS - 3,514 COINS")
print("="*80)
print()

# Load data
with open('data/crypto_with_competitive_context.json', 'r') as f:
    coins = json.load(f)

print(f"✅ Loaded {len(coins)} coins")
print()

# Initialize predictor
predictor = InvestmentOpportunityPredictor()

# Analyze all coins
print("Analyzing narrative scores...")
scored_coins = []

for coin in coins[:500]:  # Analyze top 500 for speed
    try:
        prediction = predictor.predict_opportunity(coin)
        scored_coins.append({
            'name': coin['name'],
            'symbol': coin.get('symbol', ''),
            'market_cap': coin.get('market_cap', 0),
            'rank': coin.get('rank', 999),
            'opportunity_score': prediction['opportunity_score'],
            'narrative_strength': prediction['narrative_strength'],
            'position': prediction['competitive_position'],
            'gaps': len(prediction['narrative_gaps'])
        })
    except:
        continue

print(f"✅ Scored {len(scored_coins)} coins")
print()

# PART 1: MOST UNDERVALUED
print("="*80)
print("MOST UNDERVALUED: Strong Narrative + Low Market Cap")
print("="*80)
print()

# Find high narrative score but low market cap (rank > 100)
undervalued = [c for c in scored_coins if c['rank'] > 100 and c['opportunity_score'] > 55]
undervalued.sort(key=lambda x: x['opportunity_score'], reverse=True)

print("Top 10 Hidden Gems (Rank >100, Strong Narrative):")
print("-"*80)
for i, coin in enumerate(undervalued[:10], 1):
    print(f"{i:2}. {coin['name']:30} Score: {coin['opportunity_score']:5.1f}  "
          f"Rank: #{coin['rank']:4}  MCap: ${coin['market_cap']/1e6:>8.1f}M")
print()

# PART 2: MOST OVERVALUED
print("="*80)
print("MOST OVERVALUED: Weak Narrative + High Market Cap")
print("="*80)
print()

overvalued = [c for c in scored_coins if c['rank'] <= 50 and c['opportunity_score'] < 45]
overvalued.sort(key=lambda x: x['opportunity_score'])

print("Top 10 Overvalued (Top 50 Rank, Weak Narrative):")
print("-"*80)
for i, coin in enumerate(overvalued[:10], 1):
    print(f"{i:2}. {coin['name']:30} Score: {coin['opportunity_score']:5.1f}  "
          f"Rank: #{coin['rank']:4}  MCap: ${coin['market_cap']/1e9:>7.1f}B")
print()

# PART 3: NAME PATTERN ANALYSIS
print("="*80)
print("EXISTING NAME PATTERNS (What's Present)")
print("="*80)
print()

all_names = [c['name'] for c in coins]

# Extract morphemes
morphemes = []
for name in all_names:
    name_lower = name.lower()
    # Tech morphemes
    if 'bit' in name_lower: morphemes.append('Bit-')
    if 'crypto' in name_lower: morphemes.append('Crypto-')
    if 'coin' in name_lower: morphemes.append('-coin')
    if 'chain' in name_lower: morphemes.append('-chain')
    if 'protocol' in name_lower: morphemes.append('-protocol')
    if 'network' in name_lower: morphemes.append('-network')
    if 'finance' in name_lower: morphemes.append('-finance')
    # Meme morphemes
    if 'doge' in name_lower: morphemes.append('Doge-')
    if 'shib' in name_lower: morphemes.append('Shib-')
    if 'pepe' in name_lower: morphemes.append('Pepe-')
    if 'inu' in name_lower: morphemes.append('-inu')
    if 'moon' in name_lower: morphemes.append('-moon')
    if 'safe' in name_lower: morphemes.append('Safe-')

morpheme_counts = Counter(morphemes)

print("Most Common Morphemes (Saturated Patterns):")
for morpheme, count in morpheme_counts.most_common(15):
    saturation = count / len(coins) * 100
    print(f"  {morpheme:15} {count:4} coins ({saturation:4.1f}% saturation)")
print()

# PART 4: ABSENT NAME PATTERNS
print("="*80)
print("ABSENT/RARE NAME PATTERNS (Opportunities)")
print("="*80)
print()

# Check for rare but potentially valuable patterns
rare_patterns = {
    'Nexus-': 'chain connection hub',
    'Apex-': 'maximum performance',
    '-vault': 'security and storage',
    'Prime-': 'highest quality',
    '-bridge': 'cross-chain connection',
    'Quantum-': 'next-gen tech',
    'Zenith-': 'peak achievement',
    'Core-': 'fundamental layer',
    '-forge': 'creation and building',
    'Axis-': 'pivot point'
}

print("Rare Patterns with High Potential:")
print("-"*80)

for pattern, value_prop in rare_patterns.items():
    # Check if pattern exists
    pattern_clean = pattern.replace('-', '')
    count = sum(1 for name in all_names if pattern_clean.lower() in name.lower())
    
    if count < 20:  # Rare
        saturation = count / len(coins) * 100
        opportunity = "HIGH" if count < 5 else "MEDIUM" if count < 15 else "LOW"
        print(f"  {pattern:15} Only {count:2} coins ({saturation:4.1f}%) - {opportunity} opportunity")
        print(f"                  Signals: {value_prop}")
print()

# PART 5: OPTIMAL MISSING NAMES
print("="*80)
print("OPTIMAL NAMES THAT DON'T EXIST YET")
print("="*80)
print()

# Generate high-scoring names that aren't taken
test_names = [
    'NexusProtocol',
    'ApexChain',
    'VaultNetwork',
    'PrimeFinance',
    'QuantumBridge',
    'ZenithProtocol',
    'CoreNetwork',
    'AxisChain',
    'ForgeProtocol',
    'PrimeBit'
]

print("Proposed Names (High Predicted Scores):")
print("-"*80)

name_scores = []
for name in test_names:
    # Check if exists
    exists = any(name.lower() == c.lower() for c in all_names)
    
    if not exists:
        # Predict score
        result = predictor.predict_opportunity({'name': name})
        name_scores.append((name, result['opportunity_score'], exists))

name_scores.sort(key=lambda x: x[1], reverse=True)

for name, score, exists in name_scores:
    status = "❌ TAKEN" if exists else "✅ AVAILABLE"
    print(f"  {name:20} Score: {score:5.1f}  {status}")

print()
print("="*80)
print("SUMMARY")
print("="*80)
print()
print(f"📊 Total coins analyzed: {len(scored_coins)}")
print(f"💎 Hidden gems found: {len(undervalued)} (rank >100, score >55)")
print(f"⚠️  Overvalued found: {len(overvalued)} (top 50 rank, score <45)")
print(f"🎯 Rare patterns identified: {len(rare_patterns)}")
print(f"✨ Optimal available names: {len([x for x in name_scores if not x[2]])}")
print()

