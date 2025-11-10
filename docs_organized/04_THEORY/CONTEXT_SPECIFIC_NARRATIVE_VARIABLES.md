# Context-Specific Narrative Variables by Domain

## Purpose

Beyond universal phonetic features (harshness, syllables, memorability), each domain has **context-specific story elements** that matter for narrative construction. This document identifies 5-10 unique narrative variables per domain.

---

## Universal Baseline Features (All Domains)

Before domain-specific variables, these apply everywhere:

1. **Phonetic Harshness**: Presence of harsh consonants (k, g, p, t, b, d, x, z)
2. **Syllable Count**: Number of syllables (brevity = memorability)
3. **Vowel Ratio**: Proportion of vowels to consonants
4. **Length**: Total character count
5. **Memorability**: Combination of brevity and distinctiveness

**Now add context-specific variables:**

---

## Hurricanes: Danger Narrative Variables

### Core Mechanism
Names signal pre-landfall danger when actual ground-level impact is uncertain. Story variables amplify or diminish perceived threat.

### Specific Variables

**1. Name Familiarity** (0-100%)
- Is this a common person name?
- **Theory**: Familiar names feel more "real" → Higher personal connection
- **Example**: "Katrina" (common) vs "Zephyr" (rare)
- **Measurement**: Frequency in SSA baby name database
- **Expected Effect**: +0.08 to r for highly familiar names

**2. Gender Associations** (Male/Female/Neutral)
- Historical gender of name
- **Theory**: Gender stereotypes affect risk perception (bias: male storms seem more dangerous)
- **Example**: "Andrew" (male) vs "Katrina" (female)
- **Measurement**: 90%+ usage in one gender = gendered
- **Expected Effect**: Interaction with severity (female names underestimated)

**3. Cultural Connotations** (Positive/Neutral/Negative)
- What stories does this name evoke culturally?
- **Theory**: Names with negative associations amplify danger narrative
- **Example**: "Hades" (mythology death) vs "Grace" (religious peace)
- **Measurement**: Sentiment analysis of name in cultural texts
- **Expected Effect**: Negative connotations +0.10 to danger perception

**4. Historical Hurricane Context** (Yes/No/Major)
- Has this name been used for previous deadly storms?
- **Theory**: Reused names carry baggage from past disasters
- **Example**: Second "Andrew" vs first-time name
- **Measurement**: Deaths from previous storms with same name
- **Expected Effect**: Major historical hurricane +0.15 to evacuation

**5. Pronunciation Difficulty** (Easy/Medium/Hard)
- How hard is it for newscasters to say?
- **Theory**: Easily pronounced names get more airtime → more salient
- **Example**: "Ian" (easy) vs "Hermione" (harder)
- **Measurement**: Phonetic complexity score
- **Expected Effect**: Easy pronunciation +0.05 to salience

**6. Length in Syllables** (1-4)
- Single vs multi-syllable names
- **Theory**: Shorter names in headlines → more media presence
- **Example**: "Ike" (1) vs "Alejandro" (4)
- **Measurement**: Direct syllable count
- **Expected Effect**: Each syllable -0.03 to headline usage

**7. Religious/Mythological Associations** (Yes/No)
- Does name reference religious or mythological figures?
- **Theory**: Sacred or mythological names amplify apocalyptic framing
- **Example**: "Hades," "Zeus" vs "Bob," "Alice"
- **Measurement**: Dictionary lookup of religious/myth references
- **Expected Effect**: Mythological association +0.12 to apocalyptic framing

---

## Cryptocurrencies: Technology Sophistication Signals

### Core Mechanism
Investors cannot evaluate blockchain technology, so construct quality narratives from name signals.

### Specific Variables

**1. Technical Morpheme Presence** (0-3 count)
- Contains "bit-," "crypto-," "-coin," "-chain," "block-"
- **Theory**: Technical morphemes signal serious technology project
- **Example**: "Bitcoin" (2: bit, coin) vs "Doge" (0)
- **Measurement**: Regex count of tech morphemes
- **Expected Effect**: Each morpheme +0.10 to institutional interest

**2. Seriousness vs Humor Framing** (Serious/Mixed/Joke)
- Does name signal joke or serious project?
- **Theory**: Serious names attract institutional money, jokes attract retail
- **Example**: "Ethereum" (serious) vs "DogeCoin" (joke)
- **Measurement**: Presence of humor words (Doge, Meme, Joke, Fun)
- **Expected Effect**: Joke framing -0.20 to institutional adoption (but +0.15 to retail)

**3. Ecosystem Reference** (Bitcoin/Ethereum/Other/None)
- Does name reference existing ecosystem?
- **Theory**: Ecosystem fit signals integration potential
- **Example**: "BitcoinCash" references Bitcoin, "Polkadot" independent
- **Measurement**: String matching to major ecosystems
- **Expected Effect**: Ecosystem reference +0.08 to perceived compatibility

**4. Length Complexity** (Short/Medium/Long)
- Character count as barrier to adoption
- **Theory**: Short names are easier to discuss, trade, remember
- **Example**: "BTC" vs "VeChainThor"
- **Measurement**: Character count (short <6, long >12)
- **Expected Effect**: Each 5 characters -0.04 to retail adoption

**5. Pronounceability** (Easy/Medium/Hard)
- Can average person say it?
- **Theory**: Easily pronounced names spread via word-of-mouth
- **Example**: "Tron" (easy) vs "Zilliqa" (medium)
- **Measurement**: Phonotactic probability
- **Expected Effect**: Hard pronunciation -0.07 to social sharing

**6. Real Word vs Invented** (Real/Hybrid/Invented)
- Is it a dictionary word or neologism?
- **Theory**: Real words easier to remember, invented seem more novel/technical
- **Example**: "Stellar" (real) vs "Ethereum" (invented)
- **Measurement**: Dictionary lookup
- **Expected Effect**: Real word +0.05 to memorability, invented +0.05 to tech perception

**7. Whitepaper Name Coherence** (0-100%)
- Does technical description match name's implications?
- **Theory**: Coherent name-tech match signals legitimate project
- **Example**: "Bitcoin" (digital + money) vs "FluffyCoin" (incoherent for serious project)
- **Measurement**: Semantic similarity (name morphemes ↔ whitepaper keywords)
- **Expected Effect**: Each 20% coherence +0.04 to perceived legitimacy

**8. Previous Scam Association** (Yes/No)
- Has similar name been used in previous crypto scams?
- **Theory**: Name patterns associated with scams reduce trust
- **Example**: "SafeMoon" pattern (Safe- prefix often scams)
- **Measurement**: Lookup in scam database
- **Expected Effect**: Scam pattern association -0.25 to trust

---

## Sports (NBA/NFL/MLB): Persona Construction Variables

### Core Mechanism
Names contribute to athlete persona narratives that affect brand value, endorsements, and legacy voting.

### Specific Variables

**1. Position Congruence** (Fits/Neutral/Clashes)
- Does name fit expected position archetype?
- **Theory**: Position stereotypes create expected personas
- **Example**: "Tank" for defensive lineman (fits) vs quarterback (clashes)
- **Measurement**: Position-specific name pattern analysis
- **Expected Effect**: Position fit +0.12 to draft perception

**2. Nickname Potential** (High/Medium/Low)
- Does name generate good nicknames?
- **Theory**: Nicknames amplify brand and fan connection
- **Example**: "LeBron" → "King James" vs "Bob Smith" → "Bob"
- **Measurement**: Linguistic analysis of nickname-able components
- **Expected Effect**: High nickname potential +0.08 to brand value

**3. Cultural Heritage Signal** (Strong/Moderate/Weak)
- Does name clearly signal cultural background?
- **Theory**: Authenticity narratives matter for persona
- **Example**: "Giannis Antetokounmpo" (clearly Greek) vs "John Smith" (generic)
- **Measurement**: Name origin classification confidence
- **Expected Effect**: Strong heritage signal +0.06 to authenticity narrative

**4. Marketability Score** (0-100)
- Combined measure of memorability, uniqueness, pronounceability
- **Theory**: Marketable names generate better brand opportunities
- **Example**: "Kobe Bryant" (95) vs "DeAndre Jordan" (70)
- **Measurement**: Composite of length, uniqueness, ease
- **Expected Effect**: Each 10 points +0.03 to endorsement potential

**5. All-Time Great Name Similarity** (0-100%)
- How similar to legendary player names?
- **Theory**: Names reminiscent of legends carry positive associations
- **Example**: "Jordan" similarity to Michael Jordan
- **Measurement**: String similarity + phonetic similarity to HOF names
- **Expected Effect**: High similarity +0.05 to fan expectations

**6. Toughness Phonetics** (for Contact Positions) (0-100)
- Harsh sounds appropriate for physical positions
- **Theory**: Contact positions benefit from tough-sounding names
- **Example**: "Lynch" for running back vs "Lynch" for kicker
- **Measurement**: Harshness score × position contact level
- **Expected Effect**: Interaction: +0.15 for contact positions, -0.05 for skill positions

---

## Bands/Music: Genre Signaling Variables

### Core Mechanism
Name sets genre expectations that frame how first listen is perceived.

### Specific Variables

**1. Genre Congruence Score** (0-100%)
- How well does name match genre conventions?
- **Theory**: Genre-appropriate names set correct expectations
- **Example**: "Metallica" for metal (95%) vs "Metallica" for folk (5%)
- **Measurement**: Name features × genre typical features correlation
- **Expected Effect**: Each 20% congruence +0.05 to initial positive reception

**2. Mythos Potential** (High/Medium/Low)
- Does name suggest an interesting backstory?
- **Theory**: Names that imply stories generate fan curiosity
- **Example**: "Radiohead" (intriguing) vs "The Band" (bland)
- **Measurement**: Semantic richness and cultural reference count
- **Expected Effect**: High mythos +0.08 to fan engagement

**3. Searchability Score** (0-100)
- How easy to find online?
- **Theory**: Unique but not obscure names facilitate discovery
- **Example**: "The Beatles" (unique enough) vs "The Band" (too generic)
- **Measurement**: Google search result precision
- **Expected Effect**: Each 20 points +0.04 to online discovery

**4. Length Appropriateness** (Short/Medium/Long)
- Does length match genre conventions?
- **Theory**: Some genres prefer brevity (punk), others wordiness (progressive)
- **Example**: "Ramones" (punk, short) vs "Godspeed You! Black Emperor" (post-rock, long)
- **Measurement**: Character count relative to genre median
- **Expected Effect**: Genre-appropriate length +0.06 to perceived authenticity

**5. Reference Density** (0-5 count)
- Number of cultural/literary/artistic references in name
- **Theory**: References signal artistic sophistication
- **Example**: "Vampire Weekend" (2 references) vs "The Band" (0)
- **Measurement**: Count of identifiable cultural references
- **Expected Effect**: Each reference +0.03 to perceived artistic depth

**6. Seriousness Signal** (Serious/Ironic/Joke)
- Does name signal artistic intent?
- **Theory**: Genre expectations about artistic seriousness
- **Example**: "Pink Floyd" (serious) vs "Butthole Surfers" (provocative)
- **Measurement**: Presence of humor/shock words vs poetic words
- **Expected Effect**: Genre-appropriate seriousness +0.07 to critical reception

---

## Mental Health: Stigma Construction Variables

### Core Mechanism
Diagnostic labels construct illness identities that affect stigma and treatment-seeking behavior.

### Specific Variables

**1. Character Judgment Implication** (Yes/Somewhat/No)
- Does term sound like character flaw vs medical condition?
- **Theory**: Character-implying terms increase stigma
- **Example**: "Personality Disorder" (character) vs "Syndrome" (medical)
- **Measurement**: Presence of character words (personality, antisocial, etc.)
- **Expected Effect**: Character implication +0.15 to stigma

**2. Severity Phonetics** (Mild/Moderate/Severe-sounding)
- Do harsh phonetics make condition sound worse?
- **Theory**: Harsh sounds amplify perceived severity
- **Example**: "Schizophrenia" (harsh) vs "Depression" (softer)
- **Measurement**: Harshness score applied to medical context
- **Expected Effect**: Harsh phonetics +0.10 to perceived severity

**3. Medical vs Colloquial Framing** (Medical/Mixed/Colloquial)
- Technical medical terminology vs everyday language
- **Theory**: Medical framing reduces stigma (it's clinical, not personal)
- **Example**: "Major Depressive Disorder" (medical) vs "the blues" (colloquial)
- **Measurement**: Presence of Latin/Greek morphemes vs common words
- **Expected Effect**: Medical framing -0.12 to stigma

**4. Historical Baggage** (High/Medium/Low)
- Was term used historically in stigmatizing ways?
- **Theory**: Historical misuse creates lasting negative associations
- **Example**: "Hysteria" (high baggage) vs "Anxiety" (lower)
- **Measurement**: Historical text analysis for stigmatizing usage
- **Expected Effect**: High baggage +0.18 to current stigma

**5. Spectrum Language** (Spectrum/Discrete/Hybrid)
- Does terminology allow for variability?
- **Theory**: Spectrum language reduces binary sick/well framing
- **Example**: "Autism Spectrum" vs "Autistic" (discrete)
- **Measurement**: Presence of "spectrum," "continuum," "range" language
- **Expected Effect**: Spectrum framing -0.08 to stigma

**6. Functional Description** (Yes/No)
- Does name describe function vs personality?
- **Theory**: Functional descriptions less stigmatizing
- **Example**: "Attention Deficit" (function) vs "Borderline" (personality)
- **Measurement**: Presence of functional descriptors
- **Expected Effect**: Functional description -0.10 to character judgment

---

## Board Games: Shelf Appeal Variables

### Core Mechanism
Name must communicate game type in 5-second shelf exposure before purchase decision.

### Specific Variables

**1. Complexity Signaling** (Simple/Medium/Complex)
- Does name signal casual vs hardcore game?
- **Theory**: Target audience immediately identified by name complexity
- **Example**: "Ticket to Ride" (simple) vs "Twilight Imperium" (complex)
- **Measurement**: Syllable count + word rarity
- **Expected Effect**: Appropriate complexity for target +0.08 to target audience sales

**2. Theme Clarity** (Clear/Vague/Abstract)
- Is theme immediately obvious from name?
- **Theory**: Clear themes help with decision-making
- **Example**: "Pandemic" (clear: disease theme) vs "Azul" (vague)
- **Measurement**: Semantic specificity of theme words
- **Expected Effect**: Theme clarity +0.06 to purchase confidence

**3. Family-Friendliness Signal** (Family/Adult/Mature)
- Does name signal appropriate age range?
- **Theory**: Family game buyers need clear age-appropriate signals
- **Example**: "Candy Land" (family) vs "Cards Against Humanity" (adult)
- **Measurement**: Presence of child-associated vs adult-associated words
- **Expected Effect**: Clear age targeting +0.09 to appropriate audience

**4. Fantasy/Realism Balance** (Fantasy/Mixed/Realistic)
- Does name evoke fantastical vs realistic themes?
- **Theory**: Fantasy names attract hobby gamers, realistic attract casuals
- **Example**: "Dungeons & Dragons" (fantasy) vs "Monopoly" (realistic)
- **Measurement**: Fantasy word count vs realistic word count
- **Expected Effect**: Genre-appropriate fantasy level +0.05 to target audience

**5. Wordplay/Cleverness** (High/Medium/None)
- Does name demonstrate wit or wordplay?
- **Theory**: Clever names attract hobby enthusiasts
- **Example**: "Forbidden Island" (clever setup) vs "Chess" (direct)
- **Measurement**: Presence of puns, alliteration, double meanings
- **Expected Effect**: Wordplay +0.07 to hobby gamer appeal

---

## Ships: Historical Import Variables

### Core Mechanism
Names signal builder confidence and intended mission importance.

### Specific Variables

**1. Gravitas Score** (0-100)
- How "weighty" does the name sound?
- **Theory**: Important missions get important-sounding names
- **Example**: "HMS Victory" (100) vs "HMS Ferret" (20)
- **Measurement**: Semantic weight of component words
- **Expected Effect**: Gravitas correlates with resource allocation (not causal)

**2. Purpose Signaling** (Military/Commercial/Exploration/Ceremonial)
- Does name indicate intended use?
- **Theory**: Purpose-appropriate names reflect mission planning
- **Example**: "Destroyer" (military) vs "Titanic" (commercial grandeur)
- **Measurement**: Semantic class of name components
- **Expected Effect**: Purpose fit correlates with mission success

**3. National Pride Level** (High/Medium/Low)
- How much national identity is in name?
- **Theory**: Nationally important ships get patriotic names + resources
- **Example**: "USS Constitution" (high) vs "Generic Trader" (low)
- **Measurement**: Presence of national symbols, heroes, values
- **Expected Effect**: High pride = high resources = better outcomes

**4. Predecessor Legacy** (Yes/No)
- Named after successful previous ship?
- **Theory**: Legacy names carry expectations and traditions
- **Example**: "HMS Victory III" vs new name
- **Measurement**: Historical ship name database lookup
- **Expected Effect**: Positive legacy +0.10 to crew morale

**5. Mythological References** (Yes/No)
- References gods, myths, legends?
- **Theory**: Mythological names signal ambition and importance
- **Example**: "HMS Ajax" (Greek hero) vs "HMS Sparrow"
- **Measurement**: Mythology database lookup
- **Expected Effect**: Mythological reference correlates with flagship status

---

## Elections: Trustworthiness Signaling Variables

### Core Mechanism
Candidate names signal trustworthiness and electability in absence of governance track record.

### Specific Variables

**1. Traditional vs Modern** (Traditional/Mixed/Modern)
- Does name sound like "traditional leader"?
- **Theory**: Traditional names signal stability, modern names signal change
- **Example**: "John" (traditional) vs "Jayden" (modern)
- **Measurement**: Name popularity in previous generations
- **Expected Effect**: Traditional +0.08 for conservative electorate, Modern +0.06 for progressive

**2. Cultural Fit Score** (0-100%)
- How well does name match constituency demographics?
- **Theory**: Names that "fit" the electorate seem more relatable
- **Example**: Irish name in Boston (high fit) vs Irish name in Arizona (lower fit)
- **Measurement**: Name origin × constituency demographics correlation
- **Expected Effect**: Each 20% fit +0.04 to relatability

**3. Simplicity/Pronounceability** (Easy/Medium/Hard)
- Can average voter say and remember it?
- **Theory**: Simple names get repeated in word-of-mouth
- **Example**: "Bush" (easy) vs "Buttigieg" (hard)
- **Measurement**: Phonotactic probability + length
- **Expected Effect**: Easy pronunciation +0.06 to name recognition

**4. Political Dynasty Similarity** (0-100%)
- Similar to previous political families?
- **Theory**: Dynasty similarity creates positive (or negative) associations
- **Example**: "Clinton" similarity to Bill, "Bush" to George HW
- **Measurement**: String/phonetic similarity to known political families
- **Expected Effect**: Positive dynasty +0.09, negative dynasty -0.12

**5. Gender-Expected Leadership** (Expected/Neutral/Unexpected)
- Does name match gender leadership stereotypes?
- **Theory**: Gender-typical names face less bias
- **Example**: Traditional male name for male candidate vs ambiguous
- **Measurement**: Gender typicality score
- **Expected Effect**: Gender-expected +0.05 to perceived competence

---

## Summary Table: Variables by Domain

| Domain | # Variables | Highest Impact Variable | Effect Size |
|--------|-------------|------------------------|-------------|
| Hurricanes | 7 | Historical context | +0.15 |
| Crypto | 8 | Technical morphemes | +0.10 per morpheme |
| Sports | 6 | Position congruence | +0.12 |
| Bands | 6 | Genre congruence | +0.05 per 20% |
| Mental Health | 6 | Character judgment | +0.15 |
| Board Games | 5 | Complexity signaling | +0.08 |
| Ships | 5 | Gravitas (resource correlation) | Selection effect |
| Elections | 5 | Cultural fit | +0.04 per 20% |

---

## Implementation in Analysis

### For Each Domain Analyzer

Add domain-specific feature extraction:

```python
def extract_narrative_features(entity, domain):
    # Universal features
    features = extract_phonetic_features(entity.name)
    
    # Domain-specific
    if domain == 'hurricanes':
        features['name_familiarity'] = calculate_ssa_frequency(entity.name)
        features['gender_association'] = classify_gender(entity.name)
        features['historical_context'] = lookup_previous_hurricane(entity.name)
        # ... 4 more
    
    elif domain == 'crypto':
        features['technical_morphemes'] = count_tech_morphemes(entity.name)
        features['seriousness'] = classify_seriousness(entity.name)
        # ... 6 more
    
    return features
```

---

**Status**: Context-specific variables identified for all major domains ✅  
**Total Variables**: 48 domain-specific + 5 universal = 53 narrative features  
**Next**: Implement feature extraction functions  
**Last Updated**: November 2025

