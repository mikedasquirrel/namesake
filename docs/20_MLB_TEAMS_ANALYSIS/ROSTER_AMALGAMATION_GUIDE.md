# Roster Amalgamation Methodology

## What is Roster Amalgamation?

**Roster amalgamation** is the process of aggregating individual player name features into team-level composite metrics.

---

## Calculation Method

### Step 1: Collect Player Features
For each player on the 25-man roster, extract:
- Syllable count
- Harshness score
- Memorability score
- Power connotation score
- Name origin (Anglo/Latino/Asian)

### Step 2: Calculate Aggregates
```python
roster_mean_syllables = mean([player.syllable_count for player in roster])
roster_mean_harshness = mean([player.harshness_score for player in roster])
roster_syllable_stddev = std([player.syllable_count for player in roster])
```

### Step 3: Calculate Harmony
```python
roster_harmony_score = 100 - (roster_syllable_stddev × 15)
```

**Interpretation:**
- High harmony (>80): Phonetically cohesive roster
- Medium harmony (65-80): Moderate diversity
- Low harmony (<65): High name diversity

### Step 4: Calculate International %
```python
latino_count = sum(1 for p in roster if p.name_origin == 'Latino')
asian_count = sum(1 for p in roster if p.name_origin == 'Asian')
international_pct = ((latino_count + asian_count) / 25) × 100
```

---

##  Example: New York Yankees

**Roster (hypothetical 5-player sample):**
1. Aaron Judge: 4 syl, 58 harshness, Anglo
2. Gerrit Cole: 4 syl, 62 harshness, Anglo
3. Giancarlo Stanton: 6 syl, 64 harshness, Anglo
4. Anthony Volpe: 5 syl, 56 harshness, Anglo
5. Juan Soto: 3 syl, 60 harshness, Latino

**Aggregates:**
- Mean syllables: 4.4
- Mean harshness: 60.0
- Syllable stddev: 1.14
- Harmony: 100 - (1.14 × 15) = 82.9 (high)
- International: 20%

**Interpretation:** Yankees have high roster harmony (82.9) with moderate international representation. Phonetically cohesive.

---

**Method Documentation:** Complete  
**Last Updated:** November 8, 2025

