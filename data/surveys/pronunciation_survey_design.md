# Pronunciation Survey Design - CHY-NAH vs CHAI-na Study

**Study Name:** "How Americans Say Foreign Country Names"  
**Primary Hypothesis:** Pronunciation of "China" predicts political ideology  
**Platform:** Prolific  
**Sample Size:** 500-1,000 U.S. adults  
**Cost:** $500-1,000 ($1-2 per participant)  
**Timeline:** 2-3 weeks (design 1 week, field 1 week, analysis 1 week)

---

## I. Research Questions

### Primary

**RQ1:** Does pronunciation of "China" correlate with political ideology?  
- H1a: "CHY-NAH" (harsh, Americanized) → Republican/Conservative
- H1b: "CHAI-na" (softer, closer to Mandarin) → Democrat/Liberal
- **Predicted correlation:** r = -0.52 (pronunciation harshness × liberalism)

### Secondary

**RQ2:** Do other politically-loaded country names show similar patterns?
- Iran: "eye-RAN" (Bush-era hawkish) vs "ih-RON" (closer to Farsi)
- Ukraine: "The Ukraine" (Soviet-era) vs "Ukraine" (independent nation)
- Israel: Pronunciation variants signal Israeli/Palestinian sympathies?

**RQ3:** What predicts pronunciation choices?
- Education level
- Foreign language experience
- News consumption patterns
- Foreign policy attitudes
- Travel experience

### Exploratory

**RQ4:** Cross-validation with policy attitudes
- Tariff support × China pronunciation
- Military intervention × Iran pronunciation
- Ukraine aid × "The Ukraine" usage

---

## II. Survey Design

### Section 1: Pronunciation Task (Audio Recording)

**Instructions:**
> "We're interested in how Americans pronounce foreign country names. Please say each country name OUT LOUD as you normally would in conversation. There are no right or wrong answers - we just want to hear how you naturally say these names."

**Technical Implementation:**
- Audio recording via browser (requires permission)
- Each participant records 15 country names
- 5-second recording window per name
- Can re-record if needed
- Audio saved as .mp3 or .wav files

**Country List (Randomized Order):**
1. China (PRIMARY)
2. Iran (POLITICAL)
3. Iraq (POLITICAL)
4. Ukraine (POLITICAL) 
5. Israel (POLITICAL)
6. Qatar (PRONUNCIATION CHALLENGE)
7. Vietnam (HISTORICAL EVOLUTION)
8. Korea (NORTH/SOUTH DISTINCTION)
9. Mexico (IMMIGRATION POLITICS)
10. Nicaragua (LATIN AMERICA)
11. France (EUROPEAN BASELINE)
12. Germany (EUROPEAN BASELINE)
13. Japan (ASIAN BASELINE)
14. India (ASIAN BASELINE)
15. Egypt (MIDDLE EAST BASELINE)

**Audio Analysis:**
- Phonetic transcription (automated via speech-to-text)
- Manual coding for pronunciation variants
- Harshness scoring (plosive count, stress patterns)
- Accuracy scoring (distance from native pronunciation)

### Section 2: Article Usage (The Ukraine Test)

**Instructions:**
> "Some country names are used with 'the' and some without. For each country below, how would you naturally refer to it?"

**Format:** Multiple choice for each country

Example:
> When discussing this country in conversation, I would say:
> - [ ] "The Ukraine is facing challenges"
> - [ ] "Ukraine is facing challenges"  
> - [ ] Both sound equally natural to me
> - [ ] I'm not sure

**Countries Tested:**
- Ukraine (key political marker)
- Netherlands (grammatically requires "the")
- Philippines (grammatically requires "the")
- United States (baseline)
- Congo (ambiguous)

### Section 3: Political Orientation

**Ideology (7-point scale):**
> How would you describe your political views?
> 1 = Very Liberal
> 2 = Liberal
> 3 = Somewhat Liberal
> 4 = Moderate
> 5 = Somewhat Conservative
> 6 = Conservative
> 7 = Very Conservative

**Party Identification:**
> Generally speaking, do you consider yourself a:
> - [ ] Strong Democrat
> - [ ] Democrat
> - [ ] Lean Democrat
> - [ ] Independent
> - [ ] Lean Republican
> - [ ] Republican
> - [ ] Strong Republican
> - [ ] Other party (specify)

**Foreign Policy Orientation:**
> Rate your agreement (1=Strongly Disagree, 7=Strongly Agree):
> 1. "The U.S. should focus on problems at home rather than overseas"
> 2. "The U.S. should promote democracy abroad"
> 3. "Military strength is the best way to ensure peace"
> 4. "The U.S. should cooperate with international organizations like the UN"
> 5. "Protecting American jobs should be the top priority in trade policy"

### Section 4: Policy Attitudes (China-Specific)

**China Policy Scale:**
> Rate your agreement (1=Strongly Disagree, 7=Strongly Agree):
> 1. "The U.S. should increase tariffs on Chinese goods"
> 2. "China is the greatest threat to U.S. national security"
> 3. "The U.S. should work with China on climate change"
> 4. "China engages in unfair trade practices"
> 5. "The U.S. should defend Taiwan militarily if China attacks"
> 6. "China's economic rise is a threat to American prosperity"

**Iran Policy Scale:**
> 1. "The U.S. should pursue diplomatic engagement with Iran"
> 2. "Military force may be necessary to stop Iran's nuclear program"
> 3. "Economic sanctions on Iran should be strengthened"

**Ukraine Policy Scale:**
> 1. "The U.S. should continue military aid to Ukraine"
> 2. "Ukraine should negotiate a peace settlement with Russia"
> 3. "Defending Ukraine is vital to U.S. interests"

### Section 5: Demographics & Background

**Education:**
> Highest level of education completed:
> - [ ] Less than high school
> - [ ] High school graduate
> - [ ] Some college
> - [ ] Associate's degree
> - [ ] Bachelor's degree
> - [ ] Master's degree
> - [ ] Doctoral or professional degree

**Foreign Language Experience:**
> Do you speak any languages other than English?
> - [ ] Yes, fluently
> - [ ] Yes, conversationally
> - [ ] Yes, basic knowledge
> - [ ] No

> If yes, which language(s)? [Free text]

**Travel Experience:**
> Have you traveled internationally?
> - [ ] Never
> - [ ] 1-2 countries
> - [ ] 3-5 countries
> - [ ] 6-10 countries
> - [ ] 11+ countries

> Specifically, have you visited: [Checkboxes]
> - [ ] China
> - [ ] Middle East countries
> - [ ] Europe
> - [ ] Asia (other than China)
> - [ ] Latin America

**News Consumption:**
> How often do you follow international news?
> - [ ] Daily
> - [ ] A few times a week
> - [ ] Weekly
> - [ ] Rarely
> - [ ] Never

> Primary news sources (check all that apply):
> - [ ] Cable TV (Fox News, CNN, MSNBC)
> - [ ] Network TV (ABC, CBS, NBC)
> - [ ] Newspapers (NYT, WSJ, local)
> - [ ] Online news sites
> - [ ] Social media
> - [ ] Radio (NPR, talk radio)
> - [ ] Other (specify)

**Demographics:**
- Age (open-ended number)
- Gender (Male/Female/Non-binary/Prefer not to say)
- Race/Ethnicity (standard categories)
- Household income (brackets)
- State of residence
- Urban/Suburban/Rural

### Section 6: Attention Checks

**Attention Check 1 (embedded in policy questions):**
> To ensure you're reading carefully, please select "Somewhat Agree" for this question.
> [1-7 scale]

**Attention Check 2 (embedded in demographics):**
> Have you lived in Antarctica for more than one year?
> - [ ] Yes
> - [ ] No

**Time Check:**
- Flag participants who complete in <5 minutes (minimum reasonable time)
- Flag participants who take >45 minutes (possible inattention)

---

## III. Technical Implementation

### Platform: Prolific

**Why Prolific:**
- High-quality U.S. participant pool
- Built-in demographic screening
- Fair pay rates ($10-12/hour equivalent)
- Good for audio recording studies
- API for data download

**Screening Criteria:**
- Country: United States only
- Age: 18-80
- Approval rate: >95%
- Native language: English
- No restrictions on political views (we need full spectrum)

**Compensation:**
- Estimated time: 15 minutes
- Pay rate: $2.50 (equivalent to $10/hour)
- Bonus for complete audio: $0.50
- Total per participant: $3.00

**Sample Composition:**
- Target: 500 complete responses
- Oversample by 20% (600 launched) for exclusions
- Expected cost: 600 × $3 = $1,800
- Prolific fee (33%): $600
- **Total: ~$2,400**
- (Reduce to 300 if budget constrained: $1,200 total)

### Survey Platform: Qualtrics or Gorilla

**Requirements:**
- Audio recording capability
- Integration with Prolific
- Data export to CSV
- Randomization of stimuli
- Skip logic

**Qualtrics Setup:**
1. Create survey following design above
2. Enable audio recording (requires license upgrade)
3. Set up Prolific integration (redirect URLs)
4. Test with pilot (n=10)
5. Launch full study

**Alternative (Budget):** Google Forms + JavaScript audio capture

---

## IV. Analysis Plan

### Primary Analysis: CHY-NAH Hypothesis

**Step 1: Pronunciation Coding**

Audio files coded for:
- **Variant type:**
  - Type 1: "CHY-NAH" (harsh, first syllable stress, Americanized)
  - Type 2: "CHAI-na" (softer, second syllable stress, closer to Mandarin)
  - Type 3: "Zhōngguó" (Mandarin endonym - extremely rare, signals exposure/education)
  - Type 4: Other/unclear

- **Harshness score (0-100):**
  - Plosive count
  - Stress intensity
  - Vowel openness
  - Overall perceived aggression

- **Accuracy score (0-100):**
  - Phonetic distance from Mandarin "Zhōngguó"
  - Tone attempt (if any)
  - Syllable structure

**Step 2: Correlation Analysis**

Primary test:
```
ideology_scale ~ china_harshness_score + controls
```

Controls:
- Education
- Foreign language experience
- News consumption
- Age, gender, race

**Predicted Results:**
- Correlation: r = -0.52 (harshness × liberalism)
- Effect size: d = 0.75 (liberal vs conservative mean difference)
- Significance: p < 0.001

**Robustness Checks:**
- Exclude non-native English speakers
- Exclude those who've been to China
- Exclude those with Mandarin knowledge
- Test linear vs categorical (Type 1 vs Type 2)

**Step 3: Policy Validation**

Cross-validation with policy attitudes:
```
china_tariff_support ~ china_pronunciation_harshness
```

**Predicted:**
- CHY-NAH users: 72% support tariffs
- CHAI-na users: 45% support tariffs
- **Difference: 27 points** (p < 0.001)

### Secondary Analyses

**Iran Pronunciation:**
- "eye-RAN" vs "ih-RON" 
- Predicted correlation with hawkishness

**Ukraine Article:**
- "The Ukraine" vs "Ukraine"
- Predicted correlation with Russia sympathy (or older age)

**Education Gradient:**
- Higher education → more accurate pronunciations
- But controlling for education, ideology effect persists

**News Source:**
- Fox News viewers → harsher pronunciations?
- NPR listeners → more accurate pronunciations?

### Exploratory

**Pronunciation Clusters:**
- K-means clustering on all 15 countries
- Do pronunciation styles cluster?
- Predict cluster membership from ideology

**Geographic Patterns:**
- Do pronunciation patterns vary by state?
- Border states vs inland?
- Liberal states (CA, NY) vs conservative (TX, AL)?

---

## V. Expected Outcomes

### Scenario 1: Strong Confirmation (Most Exciting)

**Findings:**
- r = -0.50 to -0.60 (ideology × harshness)
- Clear clustering: CHY-NAH = Republican, CHAI-na = Democrat
- Policy validation: 25-30 point gap in tariff support
- Robust to controls

**Implications:**
- **Nature/Science-level finding**
- Pronunciation is a political shibboleth
- First quantitative documentation
- Viral media potential

**Next Steps:**
- Submit to *Nature Human Behaviour*
- Write op-ed for NYT/Atlantic
- Pitch to NPR, major media
- Follow-up: Presidential speech corpus analysis

### Scenario 2: Moderate Confirmation (Still Publishable)

**Findings:**
- r = -0.25 to -0.35 (weaker but significant)
- Some clustering but overlap
- Policy validation moderate (10-15 point gap)
- Controls reduce but don't eliminate

**Implications:**
- Publishable in *Language in Society* or *Political Communication*
- Real effect but not as dramatic
- Still novel, still interesting
- More nuanced story

**Next Steps:**
- Submit to field-specific journal
- Frame as exploratory finding
- Call for follow-up research

### Scenario 3: Null Result (Informative)

**Findings:**
- r = -0.10 or weaker (non-significant)
- No clear clustering
- Policy attitudes don't correlate
- Effects disappear with controls

**Implications:**
- Prediction wrong, but still publishable
- Null results important (file drawer problem)
- Education/exposure drive pronunciation, not ideology
- Revise theory

**Next Steps:**
- Submit null result to appropriate journal
- Explore alternative explanations
- Check if other countries (Iran, Ukraine) work better

---

## VI. Pilot Study (n=50)

### Before Full Launch

**Pilot Objectives:**
1. Test audio recording functionality
2. Verify survey flow and timing
3. Check attention check effectiveness
4. Preliminary data check (are variants present?)
5. Refine coding scheme

**Pilot Sample:**
- n=50
- Prolific U.S. sample
- Cost: ~$200
- Timeline: 1-2 days

**Pilot Analysis:**
- Distribute across variants?
- Coding reliability?
- Survey completion rate?
- Average time?
- Technical issues?

**Revise Based on Pilot:**
- Adjust unclear questions
- Fix technical bugs
- Refine coding scheme
- Finalize before full launch

---

## VII. Timeline

**Week 1: Design & Setup**
- Day 1-2: Finalize survey design
- Day 3-4: Build Qualtrics survey
- Day 5-7: Test audio recording, Prolific integration

**Week 2: Pilot**
- Day 8: Launch pilot (n=50)
- Day 9-10: Collect pilot data
- Day 11-12: Analyze pilot, revise survey
- Day 13-14: Finalize for main study

**Week 3: Main Study**
- Day 15: Launch main study (n=500-1000)
- Day 16-18: Data collection (typically 2-3 days on Prolific)
- Day 19-21: Download and organize data

**Week 4: Analysis**
- Day 22-24: Code audio files
- Day 25-26: Run statistical analyses
- Day 27-28: Draft results summary

**Total: 4 weeks from start to preliminary findings**

---

## VIII. Budget

### Full Study (n=500)

- Participant payments: 500 × $3 = $1,500
- Prolific fees (33%): $500
- Qualtrics license (if needed): $0-500
- Audio transcription service (optional): $0-300
- **Total: $2,000-2,800**

### Reduced Study (n=300)

- Participant payments: 300 × $3 = $900
- Prolific fees: $300
- Other: $0-500
- **Total: $1,200-1,700**

### Pilot (n=50)

- Participant payments: 50 × $3 = $150
- Prolific fees: $50
- **Total: $200**

---

## IX. Ethical Considerations

**IRB Approval:**
- Low risk (pronunciation study)
- Informed consent required
- Audio recordings raise privacy (but no identifying info in recordings)
- Political views are sensitive (ensure confidentiality)
- Likely exempt or expedited review

**Participant Welfare:**
- Fair compensation ($10/hour equivalent)
- Right to withdraw
- Data confidentiality
- No deception

**Data Security:**
- Audio files stored securely
- No personally identifying information linked to audio
- Aggregate reporting only
- Delete raw audio after coding (or anonymize permanently)

---

## X. Contingency Plans

**If audio recording doesn't work:**
- Fall back to text-based: "How do you pronounce 'China'?" with options
- Less rich data but still testable

**If sample too homogeneous:**
- Oversample conservatives (Prolific leans liberal)
- Use demographic quotas
- Post to conservative forums (Reddit, Facebook) for balance

**If effect doesn't emerge:**
- Test whether other countries (Iran, Ukraine) show pattern
- Explore education/exposure effects instead
- Null result still publishable

---

## XI. Deliverables

### Immediate (Week 4)

1. **Dataset:**
   - Audio files (500-1,000)
   - Coded pronunciation data
   - Survey responses (all sections)
   - Full demographic data

2. **Analysis Report:**
   - Descriptive statistics
   - Primary hypothesis test results
   - Secondary analyses
   - Exploratory findings

3. **Visualizations:**
   - Pronunciation distribution by ideology
   - Policy attitude correlations
   - Geographic heat maps
   - Cluster analyses

### Medium-Term (Month 2-3)

4. **Academic Paper:**
   - Full manuscript for journal submission
   - Supplementary materials
   - Code and data (open science)

5. **Media Materials (if warranted):**
   - Press release
   - Explainer graphics
   - Audio samples (anonymous)

---

## XII. Success Criteria

**Minimum Success:**
- Survey completes successfully
- Audio recordings usable
- Data collected from 300+ participants
- Pronunciation variants documented

**Target Success:**
- CHY-NAH hypothesis supported (r > 0.35)
- Policy validation confirmed
- Publishable in good journal
- Novel contribution to literature

**Maximum Success:**
- Strong effect (r > 0.50)
- Multiple countries show pattern
- Nature-tier publication
- Media coverage
- Paradigm-shifting for political linguistics

---

**Document Status:** Ready for implementation  
**Next Step:** Pilot study design and launch  
**Contact:** Research team for Qualtrics setup and Prolific account

