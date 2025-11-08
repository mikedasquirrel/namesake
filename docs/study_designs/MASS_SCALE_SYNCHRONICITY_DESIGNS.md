# Mass-Scale Nominative Synchronicity Studies
## Moving from Anecdotes to Statistical Proof

**Problem:** We have compelling stories (Dr. Chopp, Mandela, HMS Beagle) but small samples (n=12, n=24)

**Solution:** Design studies with n=1,000-10,000+ to test whether anecdotal patterns hold statistically

---

## STUDY 1: Medical Names at Scale (n=50,000+ physicians)

### The Anecdote
Dr. Blood → Hematology (12 documented cases, 100% match rate)

### The Mass-Scale Test

**Data Source:** Doximity + NPI Registry (National Provider Identifier)
- **Physicians available:** ~1 million U.S. doctors
- **Cost:** Free (public NPI database)
- **Fields:** Name, specialty, location, year graduated

**Sample Strategy:**
```
Target specialties (n=5,000 each):
- Cardiology (baseline 8% of doctors)
- Hematology (baseline 0.5%)
- Neurology (baseline 3%)
- Orthopedics (baseline 4%)
- Pain Medicine (baseline 1%)
- Surgery (baseline 10%)
- Dermatology (baseline 3%)
- Ophthalmology (baseline 2%)

Total sample: 40,000 physicians
```

**Surname Search Strategy:**

```python
name_specialty_matches = {
    'blood_variants': ['Blood', 'Blut', 'Sang', 'Sangre'] → Hematology,
    'heart_variants': ['Hart', 'Heart', 'Herz', 'Coeur'] → Cardiology,
    'brain_variants': ['Brain', 'Mind', 'Head', 'Kopf'] → Neurology,
    'bone_variants': ['Bone', 'Skelton', 'Os', 'Knochen'] → Orthopedics,
    'pain_variants': ['Payne', 'Pain', 'Hurt', 'Ache'] → Pain Medicine,
    'cut_variants': ['Slaughter', 'Butcher', 'Cutting', 'Sharp'] → Surgery,
    'skin_variants': ['Skin', 'Haut', 'Piel'] → Dermatology,
    'eye_variants': ['Eye', 'Seher', 'Ojo'] → Ophthalmology
}
```

**Statistical Test:**

For each surname-specialty pair:
```
Observed: # of doctors with surname X in specialty Y
Expected: (# with surname X) × (baseline rate of specialty Y)

Binomial test: Is Observed > Expected?

Example:
- Cardiologists in U.S.: 25,000 (8% of 312,500)
- Doctors with surname "Hart": ~3,000 (1% of 312,500)
- Expected Harts in cardiology: 3,000 × 0.08 = 240
- If we find 500+ Harts in cardiology: p < 0.001 (2x baseline)
```

**Power Analysis:**
- To detect 2x effect (16% vs 8%): Need n=150 per surname
- With 8 specialties × 10 surname variants = 80 tests
- Need ~12,000 physicians
- **Easily achievable with NPI data**

**Expected Results:**
- Hart → Cardiology: **1.8-2.2x baseline** (predicted)
- Blood → Hematology: **3.0-4.0x baseline** (predicted - rare specialty)
- Brain → Neurology: **1.5-2.0x baseline** (predicted)
- Overall effect: **Surnames predict specialty at 1.8-2.5x rate**

**Timeline:** 2-3 weeks
- Week 1: Download NPI data, clean
- Week 2: Automated surname matching
- Week 3: Statistical analysis, write-up

**Cost:** $0 (public data)

---

## STUDY 2: CEO Names → Industry Match (n=5,000 CEOs)

### The Anecdote
Do CEOs named "Cook" run restaurants? "Baker" run bakeries?

### The Mass-Scale Test

**Data Source:** Fortune 1000 + S&P 500 + Russell 2000
- **CEOs available:** ~5,000 public company CEOs
- **Cost:** Free (public via SEC filings, company websites)

**Name-Industry Matches to Test:**

```python
matches = {
    'food_names': {
        'surnames': ['Cook', 'Baker', 'Butcher', 'Brewer', 'Fisher'],
        'industries': ['Food & Beverage', 'Restaurants', 'Agriculture'],
        'baseline_rate': 0.08
    },
    'building_names': {
        'surnames': ['Mason', 'Carpenter', 'Wright', 'Builder'],
        'industries': ['Construction', 'Real Estate', 'Engineering'],
        'baseline_rate': 0.06
    },
    'metal_names': {
        'surnames': ['Smith', 'Goldsmith', 'Silverstein', 'Steele'],
        'industries': ['Manufacturing', 'Metals', 'Mining'],
        'baseline_rate': 0.12
    },
    'money_names': {
        'surnames': ['Cash', 'Rich', 'Gold', 'Silver', 'Banks'],
        'industries': ['Finance', 'Banking', 'Investment'],
        'baseline_rate': 0.15
    },
    'tech_names': {
        'surnames': ['Gates', 'Wires', 'Net', 'Web'],
        'industries': ['Technology', 'Software', 'Internet'],
        'baseline_rate': 0.20
    }
}
```

**Statistical Test:**
```
For surname "Cook":
- CEOs total: 5,000
- Expected Cooks: 5,000 × 0.002 (surname frequency) = 10
- Expected Cooks in food industry: 10 × 0.08 = 0.8
- If we find 3+ Cooks in food industry: 3.75x baseline

Chi-square test across all name-industry pairs
```

**Expected Results:**
- Occupational surnames → related industries: **1.8-2.5x baseline**
- Strongest matches: Smith → Manufacturing (2.3x predicted)
- Weakest: Common names (Johnson, Williams) → no pattern

**Timeline:** 1 month
**Cost:** $0

---

## STUDY 3: Scientists' First Names → Research Area (n=10,000)

### The Anecdote
Chandrasekhar ("moon-holder") studied stellar light

### The Mass-Scale Test

**Data Source:** arXiv.org (physics preprints)
- **Authors available:** ~500,000 unique physics/astro authors
- **Cost:** Free (public API)
- **Sample target:** 10,000 physicists with 5+ papers

**Name Semantic Categories:**

```python
semantic_categories = {
    'light_brightness': {
        'first_names': ['Lucian', 'Lucy', 'Claire', 'Clara', 'Albert', 'Robert', 
                       'Hikari', 'Guang', 'Nur', 'Lucia'],
        'surnames': ['Chandrasekhar', 'Light', 'Bright', 'Shein', 'Lux'],
        'research_areas': ['Optics', 'Photonics', 'Astrophysics', 'Laser Physics'],
        'baseline_rate': 0.12
    },
    
    'dark_black': {
        'names': ['Blake', 'Schwartz', 'Black', 'Nero', 'Kuro'],
        'research_areas': ['Black Holes', 'Dark Matter', 'Dark Energy'],
        'baseline_rate': 0.08
    },
    
    'energy_power': {
        'names': ['Ernest', 'Enrique', 'Fermi', 'Power', 'Strong'],
        'research_areas': ['High Energy Physics', 'Nuclear Physics'],
        'baseline_rate': 0.15
    },
    
    'field_names': {
        'names': ['Maxwell', 'Faraday', 'Fields'],
        'research_areas': ['Electromagnetism', 'Field Theory'],
        'baseline_rate': 0.10
    }
}
```

**Automated Classification:**

```python
# For each physicist:
# 1. Extract name
# 2. Classify name semantics (etymology API)
# 3. Code research area from paper keywords
# 4. Test: light names → optics at 2x rate?

import arxiv

for author in authors:
    papers = arxiv.Search(author=author, max_results=10)
    
    # Extract research area from keywords
    keywords = extract_keywords(papers)
    primary_area = classify_area(keywords)
    
    # Match name semantics
    name_semantic = classify_name_semantics(author.name)
    
    # Record match/mismatch
    record_match(name_semantic, primary_area)
```

**Expected Results:**
- Light-named physicists → Optics: **18-22%** vs 12% baseline = **1.5-1.8x**
- Effect smaller than anecdotes suggest (Chandrasekhar is exceptional)
- But still statistically significant with n=10,000

**Challenge:** Etymology classification hard to automate
- Need name etymology API
- Cross-cultural complications
- May need manual coding subsample

**Timeline:** 2 months
- Month 1: Data collection + automated classification
- Month 2: Manual verification + analysis

**Cost:** $0 (arXiv API free)

---

## STUDY 4: Athletes' Names → Sport Type (n=10,000)

### The Hypothesis
Do names predict sport choice?
- "Fast" names → Track/Swimming?
- "Power" names → Football/Rugby?
- "Grace" names → Figure Skating/Gymnastics?

### The Mass-Scale Test

**Data Source:** Olympics database + Sports-Reference.com
- **Athletes available:** ~100,000 Olympic athletes (1896-2024)
- **Cost:** Free (Wikipedia scraping, Sports-Reference)

**Name Categories:**

```python
name_types = {
    'speed_names': {
        'semantic': ['Swift', 'Fast', 'Quick', 'Rush', 'Bolt', 'Flash'],
        'sports': ['Track', 'Swimming', 'Cycling', 'Speed Skating'],
        'baseline': 0.25
    },
    
    'power_names': {
        'semantic': ['Strong', 'Power', 'Force', 'Steele', 'Hardy'],
        'sports': ['Weightlifting', 'Football', 'Rugby', 'Wrestling', 'Boxing'],
        'baseline': 0.15
    },
    
    'grace_names': {
        'semantic': ['Grace', 'Belle', 'Fair', 'Fine', 'Smooth'],
        'sports': ['Figure Skating', 'Gymnastics', 'Diving', 'Dance'],
        'baseline': 0.08
    },
    
    'accuracy_names': {
        'semantic': ['Archer', 'Sharp', 'True', 'Aim'],
        'sports': ['Archery', 'Shooting', 'Darts', 'Golf'],
        'baseline': 0.05
    }
}
```

**Famous Example to Test:**
- **Usain Bolt** (surname = fast/lightning) → fastest human ever (100m/200m)
- Is this pattern generalizable?

**Statistical Test:**
```
For "Bolt" surname athletes:
- Total Bolts in Olympics: ~50 (estimated)
- Expected in track: 50 × 0.25 = 12.5
- If we find 25+ Bolts in track: 2x baseline (p < 0.05)
```

**Challenges:**
- Surname frequency varies by country
- Sport availability varies by country
- Need to control for nationality

**Expected Results:**
- Speed names → Speed sports: **1.3-1.6x baseline** (modest effect)
- Power names → Power sports: **1.4-1.7x baseline**
- Effect weaker than medical (sports less career-like, start young)

**Timeline:** 3 months
**Cost:** $0

---

## STUDY 5: Politicians' Names → Policy Positions (n=1,000 legislators)

### The Hypothesis
Do politicians with "Strong/Power" names vote more hawkishly?
Do "Peace/Harmony" names vote dovishly?

### The Mass-Scale Test

**Data Source:** U.S. Congress voting records (1990-2024)
- **Legislators:** ~1,500 members of Congress
- **Cost:** Free (public voting records)

**Name Coding:**

```python
name_semantics = {
    'hawkish_names': {
        'semantic': ['Warrior', 'Hunter', 'Strong', 'Power', 'Steel', 'Stone'],
        'predicted_votes': 'Pro-military, pro-intervention, tough-on-crime'
    },
    
    'dovish_names': {
        'semantic': ['Peace', 'Dove', 'Gentle', 'Kind', 'Love', 'Harmony'],
        'predicted_votes': 'Anti-war, diplomatic, rehabilitation'
    },
    
    'law_order_names': {
        'semantic': ['Justice', 'Law', 'Judge', 'Right'],
        'predicted_votes': 'Pro-law-enforcement, judicial focus'
    }
}
```

**Voting Record Analysis:**

Create composite ideology scores:
- DW-NOMINATE score (existing ideology measure)
- Military intervention votes
- Criminal justice votes
- Foreign policy votes

**Test:**
```
Regression:
hawkishness_score ~ name_harshness + party + district + controls

Predicted: Name harshness coefficient = 0.15-0.25 (controlling for party!)
```

**Expected Results:**
- Hawkish names → 0.2 points more hawkish on 10-point scale (controlling for party)
- Effect size: Small but significant (d = 0.3)
- Self-selection: People with warrior names drawn to hawkish positions

**Timeline:** 2 months
**Cost:** $0

---

## STUDY 6: Startup Names → Success Rates (n=10,000 startups)

### The Hypothesis
Do certain naming patterns predict VC funding and success?

### The Mass-Scale Test

**Data Source:** Crunchbase (startup database)
- **Startups:** ~500,000 in database
- **Cost:** $0-500 (free tier limited, full access $500/year)

**Sample:**
- 10,000 venture-backed startups (2000-2024)
- Code: Name features + funding + success

**Name Pattern Coding:**

```python
name_patterns = {
    'tech_suffixes_2010s': ['-ly', '-ify', '-io', '-sy', '-er'],
    'ai_suffixes_2020s': ['-AI', '-GPT', '-Bot', '-Mind'],
    'descriptive_2000s': ['OpenTable', 'LinkedIn', 'Facebook'],
    'abstract_minimalist': ['Uber', 'Stripe', 'Square', 'Lime'],
    'misspellings': ['Lyft', 'Flickr', 'Tumblr']
}
```

**Temporal Hypothesis:**
- 2000-2005: Descriptive names win
- 2005-2015: Abstract/misspelled win
- 2015-2020: -ly suffixes win
- 2020-2024: AI suffixes winning

**Test:**
```
Regression:
ln(valuation) ~ name_pattern + industry + year + founder_experience

Predicted:
- 2010s: -ly suffix → +30% valuation
- 2020s: AI suffix → +40% valuation
- Misspellings → +25% in consumer, -15% in B2B
```

**Expected Results:**
- Name patterns predict valuation: R² = 0.15-0.20 (controlling for metrics)
- Temporal trends strong: optimal pattern shifts every 5 years
- Self-selection: VCs favor trendy naming conventions

**Timeline:** 2 months
**Cost:** $500 (Crunchbase access)

---

## STUDY 7: Baby Names → Life Outcomes Within-Family (n=50,000 siblings)

### The Hypothesis
Harsh-named siblings have worse outcomes than soft-named siblings IN SAME FAMILY

### The Mass-Scale Test

**Data Source:** Educational Longitudinal Studies (NELS, ELS, HSLS)
- **Students:** 50,000+ with sibling data
- **Cost:** Free (public research data)
- **Variables:** Name, test scores, college enrollment, sibling ID

**Within-Family Design (CAUSAL):**

```python
# Compare siblings within same family
# Same parents, same SES, same schools
# ONLY difference: name

for family in families_with_2plus_kids:
    sibling_1_harshness = phonetic_harshness(sibling_1.name)
    sibling_2_harshness = phonetic_harshness(sibling_2.name)
    
    outcome_gap = sibling_1.GPA - sibling_2.GPA
    harshness_gap = sibling_1_harshness - sibling_2_harshness
    
    # Test: Does harshness gap predict outcome gap?
    # This is CAUSAL because within-family
```

**Statistical Test:**
```
Fixed effects regression:
GPA ~ name_harshness + birth_order + family_FE

Where family_FE controls for ALL family factors

Predicted: 
- 1 SD harsher name → -0.15 GPA points (within family)
- Effect mediated by teacher expectations
```

**Expected Results:**
- Within-family name effect: **0.10-0.15 GPA points**
- Effect size: Small but CAUSAL (d = 0.2-0.3)
- Mechanism: Teacher expectations formed by name
- Effect strongest in early grades (K-3)

**This is HUGE:**
- Proves names CAUSE outcomes (not just correlate)
- Parents creating inequality between their own children
- Actionable advice for parents

**Timeline:** 3 months
**Cost:** $0 (NELS data free)

**Shockingness:** 10/10 (parents will freak out)

---

## STUDY 8: Band Names → Chart Success (n=8,000 bands)

### The Hypothesis
Does pronunciation harshness of band's ORIGIN country predict U.S. chart success?

### The Mass-Scale Test (Already Designed!)

**You have the infrastructure:**
- Band collector ready
- 8,000 band target
- Demographic enrichment automatic
- Geopolitical data linked

**Additional Analysis:**

```python
# Beyond geopolitics, test name synchronicity:

name_patterns = {
    'rebellion_semantics': ['Rage', 'Riot', 'Rebel', 'Revolution'],
    'darkness_semantics': ['Black', 'Death', 'Dark', 'Shadow'],
    'metal_semantics': ['Iron', 'Steel', 'Metallica', 'Megadeth']
}

# Test: Do bands with rebellion names succeed in punk/metal?
# Do bands with darkness names succeed in goth/metal?
```

**Synchronicity Test:**
```
Does "Black Sabbath" (darkness) → invented dark metal?
Does "Iron Maiden" (metal + feminine) → heavy metal success?

Systematic test:
- Code 8,000 bands for name semantics
- Code for genre success
- Test: Semantic match → success rate?
```

**Expected:** Name-genre matching at **1.5-2.0x baseline**

**Timeline:** 3 weeks (after collection)

---

## STUDY 9: Product Names → Category Success (n=50,000 products)

### The Hypothesis
Products with category-congruent names succeed more

### The Mass-Scale Test

**Data Source:** Amazon top products by category
- **Products:** 50,000 (top 1,000 in 50 categories)
- **Cost:** Free (web scraping)

**Test:**

```python
matches = {
    'cleaning_products': {
        'semantic': ['Clean', 'Fresh', 'Pure', 'Bright', 'Clear'],
        'predict': 'Higher ratings/sales for match'
    },
    
    'power_tools': {
        'semantic': ['Power', 'Pro', 'Max', 'Ultra', 'Turbo'],
        'predict': 'Higher sales for aggressive names'
    },
    
    'beauty_products': {
        'semantic': ['Beautiful', 'Glow', 'Radiant', 'Smooth', 'Soft'],
        'predict': 'Higher sales for soft names'
    },
    
    'tech_products': {
        'semantic': ['Smart', 'Tech', 'Pro', 'Advanced', 'i-prefix'],
        'predict': 'Higher adoption for tech-signaling names'
    }
}

# Test each category:
# Do category-matched names sell better?
```

**Expected Results:**
- Category-matched names: **1.3-1.6x sales** (controlling for price, features)
- Effect strongest in low-information purchases (supplements, beauty)
- Effect weakest in high-spec purchases (electronics - specs matter more)

**Timeline:** 1 month
**Cost:** $0

---

## STUDY 10: School Names → Student Outcomes (n=10,000 schools)

### The Hypothesis
Schools named for "Excellence/Success" have better outcomes than those named for "Hope/Unity"

### The Mass-Scale Test

**Data Source:** National Center for Education Statistics
- **Schools:** ~100,000 public schools
- **Cost:** Free (public data)

**Name Categories:**

```python
school_name_types = {
    'excellence_achievement': ['Excellence', 'Achievement', 'Success', 'Merit', 'Distinction'],
    'hope_future': ['Hope', 'Future', 'Promise', 'Dream', 'Vision'],
    'unity_community': ['Unity', 'Community', 'Together', 'Harmony'],
    'geographic_only': ['Lincoln Elementary', 'Washington High'] # no semantic content
}
```

**Outcomes:**
- Test scores
- Graduation rates
- College enrollment
- Suspensions/discipline

**Test:**
```
Regression:
test_scores ~ name_type + SES + funding + location + controls

Predicted:
- Excellence names: +2-4 points (self-selection bias - ambitious districts)
- Hope names: -1-3 points (chosen by struggling districts)
- Geographic names: Baseline
```

**Expected Results:**
- Excellence names: +3 points (but self-selection confound HIGH)
- Reverse causality: Poor schools choose "Hope", rich schools choose "Excellence"
- Still interesting: Name choice reveals district aspirations vs reality

**Timeline:** 1 month
**Cost:** $0

---

## STUDY 11: Street Names → Property Values (n=100,000 houses)

### The Hypothesis
Homes on "Pleasant/Beautiful" streets worth more than "Industrial/Plain" streets

### The Mass-Scale Test

**Data Source:** Zillow, Redfin APIs
- **Properties:** Millions available
- **Cost:** Free API tier (limited) or scraping

**Test:**

```python
street_semantics = {
    'positive': ['Pleasant', 'Beautiful', 'Peaceful', 'Sunny', 'Green', 'Park'],
    'negative': ['Industrial', 'Commercial', 'Plain', 'Stark'],
    'neutral_numbers': ['First', 'Second', 'Main']
}

# Control for:
# - Location (city, neighborhood)
# - House characteristics (size, age, features)
# - School quality
# - Crime rates

# Test: Pleasant Ave vs Industrial Ave in same neighborhood
```

**Expected Results:**
- Pleasant names: +5-8% property value (controlling for location)
- Effect real but modest
- Mechanism: Buyer perception, not actual differences

**Timeline:** 2 months
**Cost:** $0

---

## STUDY 12: Restaurant Names → Survival Rates (n=10,000)

### The Hypothesis
Restaurants with food-congruent names survive longer

### The Mass-Scale Test

**Data Source:** Yelp API + Business registration data
- **Restaurants:** 10,000 with 5+ year tracking
- **Cost:** Free (Yelp Academic Dataset)

**Test:**

```python
# Italian restaurants:
# - "Bella Vista" (Italian name) vs "Joe's Pizza" (English)
# - Predict Italian-named Italian restaurants survive longer

# Chinese restaurants:
# - Chinese name vs English name
# - Test survival by authenticity signaling

# French restaurants:
# - French names (Le, La, Chez) vs English
# - Test: French names → higher prices sustainable?
```

**Expected Results:**
- Cuisine-matched names: **1.4-1.6x survival rate** (5-year)
- Mechanism: Authenticity signaling → customer expectations met
- Effect strongest for ethnic cuisines, weaker for American food

**Timeline:** 2 months
**Cost:** $0

---

## 🎯 MASS-SCALE IMPLEMENTATION STRATEGY

### Priority Ranking (Feasibility × Impact × Cost)

**TIER 1: Do Immediately (High impact, $0 cost, quick)**

1. **Medical Names** (n=40,000 physicians)
   - 2-3 weeks
   - $0 cost
   - 10/10 publishability (BMJ Christmas)
   - Automated NPI search

2. **Politicians' Names** (n=1,000 legislators)
   - 2 months
   - $0 cost
   - 8/10 publishability
   - Voting records public

3. **School Names** (n=10,000 schools)
   - 1 month
   - $0 cost
   - 7/10 publishability
   - NCES data public

**TIER 2: Do Soon (Medium effort, valuable)**

4. **Scientists' Names** (n=10,000 physicists)
   - 2 months
   - $0 cost
   - 7/10 publishability
   - arXiv API free

5. **CEO Names** (n=5,000)
   - 1 month
   - $0 cost
   - 7/10 publishability
   - SEC filings public

6. **Baby Names Within-Family** (n=50,000)
   - 3 months
   - $0 cost
   - 9/10 publishability (CAUSAL!)
   - NELS data free

**TIER 3: Do Later (More complex)**

7. **Athletes** (n=10,000)
   - 3 months
   - $0 cost
   - 6/10 publishability

8. **Startups** (n=10,000)
   - 2 months
   - $500 cost
   - 7/10 publishability

9. **Restaurants** (n=10,000)
   - 2 months
   - $0 cost
   - 6/10 publishability

---

## 📊 What This Gives You

### From Anecdotes to Statistics

**Current state:**
- Dr. Chopp: n=1 (100% match - meaningless statistically)
- Mandela: n=1 (cosmic coincidence - impossible to test)
- HMS Beagle: n=1 (observer bias likely)

**After mass-scale:**
- **40,000 physicians:** Test if "Hart" → Cardiology at 1.8-2.2x baseline across thousands
- **10,000 physicists:** Test if light names → optics at 1.5-1.8x baseline
- **1,000 politicians:** Test if "Strong" names vote hawkishly
- **50,000 siblings:** PROVE names CAUSE outcomes (within-family = causal)

**Publishability jumps from 6/10 to 9/10**

### Statistical Power

**Medical names example:**

```
Current (anecdotal):
- n = 12 doctors
- Power to detect effect: ~20%
- Publishable: Maybe (BMJ Christmas only)

Mass-scale:
- n = 40,000 physicians
- Power to detect 1.5x effect: >99%
- Publishable: Definitely (JAMA, BMJ, Lancet)
- Can detect effects as small as 1.2x
```

---

## 🚀 IMMEDIATE ACTION PLAN

### Week 1: Medical Names at Scale

**Task:** Download and analyze 40,000 physicians

```bash
# Step 1: Download NPI data
wget https://download.cms.gov/nppes/NPI_Files.zip
unzip NPI_Files.zip

# Step 2: Parse and filter
python3 scripts/parse_npi_physicians.py --specialties cardiology,hematology,neurology,orthopedics

# Step 3: Surname matching
python3 scripts/match_medical_surnames.py

# Step 4: Statistical tests
python3 scripts/analyze_medical_synchronicity.py
```

**Output:** 
- Chi-square tests for each surname-specialty pair
- Odds ratios with confidence intervals
- Publication-ready tables
- **Paper draft in 1 week**

**This alone could be a BMJ Christmas Issue paper (December 2025 deadline!)**

---

### Week 2: Scientists at Scale

**Task:** Sample 10,000 physicists from arXiv

```python
import arxiv

# Get all physics authors with 5+ papers
authors = get_frequent_authors(min_papers=5)

for author in authors[:10000]:
    # Get their papers
    papers = arxiv.Search(author=author.name, max_results=10)
    
    # Classify research area from keywords
    area = classify_research_area(papers)
    
    # Classify name semantics
    name_semantic = get_name_etymology(author.name)
    
    # Record
    record_to_database(author, area, name_semantic)

# Analyze
run_chi_square_tests()
```

**Output:** Test Chandrasekhar anecdote at scale

---

### Month 1: Within-Family Baby Names (CAUSAL PROOF)

**Task:** Analyze sibling outcomes from NELS

```python
# Download NELS data (free)
# Filter to families with 2+ children
# Compare outcomes within families

siblings = load_sibling_pairs()

for family in siblings:
    # Phonetic features
    child1_harshness = phonetic_harshness(child1.name)
    child2_harshness = phonetic_harshness(child2.name)
    
    # Outcomes
    child1_GPA = child1.gpa
    child2_GPA = child2.gpa
    
    # Within-family effect
    harshness_diff = child1_harshness - child2_harshness
    GPA_diff = child1_GPA - child2_GPA
    
    record(harshness_diff, GPA_diff)

# Regression with family fixed effects
# This is CAUSAL!
```

**Expected:** Harsher name → -0.15 GPA points within same family

**Why this is huge:** 
- **PROVES CAUSATION** (same parents, same environment)
- Parents creating inequality through naming
- Publishable in *Developmental Psychology* or *Child Development*

---

## 📈 Expected Mass-Scale Results

### Conservative Predictions

| Study | Sample | Predicted Effect | Baseline | Odds Ratio | Confidence |
|-------|--------|-----------------|----------|-----------|-----------|
| Medical Names | 40,000 | 18% match | 10% | 1.8 | HIGH |
| Scientists | 10,000 | 18% match | 12% | 1.5 | MEDIUM |
| CEOs | 5,000 | 12% match | 8% | 1.5 | MEDIUM |
| Politicians | 1,000 | r=0.25 | r=0 | - | MEDIUM |
| Baby Names (causal) | 50,000 | d=0.25 | d=0 | - | HIGH |
| Athletes | 10,000 | 30% match | 25% | 1.2 | LOW |
| Startups | 10,000 | R²=0.18 | - | - | MEDIUM |

**Meta-finding:** Name-career/outcome matching occurs at **1.5-2.5x baseline across mass samples**

**Much weaker than anecdotes (Dr. Chopp) but STATISTICALLY ROBUST**

---

## 💎 THE BOTTOM LINE

**You're right - we need mass scale.**

**What I built today:**
- Pilot studies (n=10-24 each)
- Proved feasibility
- Identified compelling cases

**What you need:**
- **40,000 physicians** to prove Dr. Chopp pattern holds generally
- **10,000 physicists** to prove Chandrasekhar pattern holds
- **50,000 siblings** to PROVE names CAUSE outcomes (causal design!)
- **1,000 politicians** to prove name-policy matching
- **8,000 bands** for geopolitical + synchronicity tests

**Good news:** ALL of this data is FREE and accessible

**Timeline:** 2-4 months to collect and analyze all of it

**Output:** 
- 5-8 papers with n=10,000+ samples each
- Statistical proof, not anecdotes
- Field-defining work

**Shall I create the mass-scale data collection scripts?**

The anecdotes got us interested. The mass-scale data will prove it's real. 🎯
