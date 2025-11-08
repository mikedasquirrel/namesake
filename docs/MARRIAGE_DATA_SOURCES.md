# Marriage & Divorce Data Sources Guide

## Ethical & Legal Considerations

**CRITICAL:** All data collection must comply with:
- IRB (Institutional Review Board) approval for human subjects research
- State and federal privacy laws
- HIPAA regulations (where applicable)
- GDPR (for international data)
- Informed consent requirements (where applicable)

**Principle:** Only use publicly available records. Never collect or publish personally identifiable information.

---

## Data Source Categories

### 1. Public Marriage & Divorce Records

#### Federal Sources

**1.1 National Center for Health Statistics (NCHS)**
- Website: https://www.cdc.gov/nchs/nvss/index.htm
- Data: Aggregate marriage/divorce statistics
- Availability: Public, aggregate only
- Coverage: U.S. national statistics, 1960-present
- **Access:** Public use files (de-identified)
- **Cost:** Free

**1.2 U.S. Census Bureau**
- Website: https://www.census.gov/topics/families/marriage-and-divorce.html
- Data: Marital status, marriage timing, demographics
- Availability: Public, aggregate and microdata
- Coverage: 1890-present (decennial), 2005-present (ACS)
- **Access:** Public Use Microdata Sample (PUMS)
- **Cost:** Free

#### State Sources (Examples)

**2.1 Texas Department of State Health Services**
- Website: https://www.dshs.texas.gov/vs/
- Data: Marriage and divorce records (1966-present)
- **Access:** Public records request
- **Cost:** $20-50 per certified copy
- **Research Access:** May require IRB approval

**2.2 Florida Department of Health**
- Website: http://www.floridahealth.gov/certificates/certificates/marriage/index.html
- Data: Marriage records (1927-present), divorce (1964-present)
- **Access:** Public records
- **Cost:** $5-20 per record
- **Bulk Access:** May require research agreement

**2.3 California Department of Public Health**
- Website: https://www.cdph.ca.gov/Programs/CHSI/Pages/Vital-Records.aspx
- Data: Marriage and divorce records
- **Access:** Restricted (some access for research)
- **Cost:** Varies
- **Note:** California restricts access more than other states

**2.4 Nevada**
- Website: Various county clerk offices
- Data: Marriage records (very high volume due to Las Vegas)
- **Access:** County clerk offices
- **Note:** Excellent source for diverse sample

**2.5 Arizona**
- Website: County-level vital statistics
- Data: Marriage and divorce records
- **Access:** Public records

### 2. Historical & Genealogical Databases

**3.1 FamilySearch (LDS Church)**
- Website: https://www.familysearch.org/
- Data: Billions of historical records, including marriages
- Availability: Free, mostly historical (pre-1950)
- Coverage: Global, emphasis on U.S. and Europe
- **Access:** Free account
- **Research Use:** Allowed for scholarly purposes

**3.2 Ancestry.com**
- Website: https://www.ancestry.com/
- Data: Marriage records, family trees, census data
- Availability: Subscription required
- Coverage: 1600s-present, global
- **Access:** Subscription ($25-50/month)
- **Research Use:** May require institutional agreement

**3.3 MyHeritage**
- Website: https://www.myheritage.com/
- Data: Historical records, family trees
- Availability: Subscription
- Coverage: Global, emphasis on Europe

**3.4 FindAGrave**
- Website: https://www.findagrave.com/
- Data: Death records, often include spouse names
- Availability: Free
- Coverage: Primarily U.S., growing international

### 3. Celebrity & Public Figure Marriages

**4.1 Wikipedia**
- Website: https://www.wikipedia.org/
- Data: Celebrity biographies, marriage history
- Availability: Public, structured data
- Coverage: Global, comprehensive for notable figures
- **Access:** Free, API available
- **Format:** Structured data (info boxes), easily parsable

**4.2 IMDb (Internet Movie Database)**
- Website: https://www.imdb.com/
- Data: Entertainment industry relationships
- Availability: Public (some data restricted)
- Coverage: Actors, directors, producers
- **Access:** Free browsing, API requires license

**4.3 Wikidata**
- Website: https://www.wikidata.org/
- Data: Structured data from Wikipedia
- Availability: Public, machine-readable
- Coverage: Global knowledge base
- **Access:** Free, SPARQL query interface

**4.4 DBpedia**
- Website: https://www.dbpedia.org/
- Data: Structured information from Wikipedia
- Availability: Public
- **Access:** Free, RDF format

**4.5 News Archives**
- Google News Archive
- ProQuest Historical Newspapers
- Nexis Uni (LexisNexis Academic)
- **Note:** Requires institutional access

### 4. Research Databases

**5.1 ICPSR (Inter-university Consortium for Political and Social Research)**
- Website: https://www.icpsr.umich.edu/
- Data: Survey data, longitudinal studies
- Availability: Restricted, requires membership
- Coverage: U.S. and international social science data
- **Access:** Institutional membership required

**5.2 Add Health (National Longitudinal Study of Adolescent to Adult Health)**
- Website: https://addhealth.cpc.unc.edu/
- Data: Longitudinal data including marriage/relationships
- Availability: Restricted, requires application
- Coverage: U.S., 1994-present

**5.3 NLSY (National Longitudinal Survey of Youth)**
- Website: https://www.nlsinfo.org/
- Data: Life course data including marriage
- Availability: Public with registration
- Coverage: U.S., 1979-present

**5.4 Panel Study of Income Dynamics (PSID)**
- Website: https://psidonline.isr.umich.edu/
- Data: Family dynamics, marriage, divorce
- Availability: Public with registration
- Coverage: U.S., 1968-present

### 5. International Sources

**6.1 Eurostat**
- Website: https://ec.europa.eu/eurostat
- Data: EU marriage/divorce statistics
- Availability: Public, aggregate
- Coverage: European Union

**6.2 ONS (UK Office for National Statistics)**
- Website: https://www.ons.gov.uk/
- Data: Marriage and divorce statistics
- Availability: Public
- Coverage: United Kingdom

**6.3 StatCan (Statistics Canada)**
- Website: https://www.statcan.gc.ca/
- Data: Canadian marriage/divorce data
- Availability: Public

---

## Recommended Collection Strategy

### Phase 1: Public Aggregate Data (Immediate)
1. Download NCHS aggregate statistics (baseline rates)
2. Access Census PUMS data (demographics)
3. Collect from FamilySearch (historical sample)

**Timeline:** 2-4 weeks  
**Cost:** Free  
**IRB:** May not be required (public aggregate data)

### Phase 2: Celebrity Sample (2-4 weeks)
1. Scrape Wikipedia via API
2. Cross-reference with IMDb
3. Validate through news archives

**Timeline:** 3-6 weeks  
**Cost:** $0-500 (news archive access)  
**IRB:** May not be required (public figures)

### Phase 3: State Records (if needed, 8-12 weeks)
1. File public records requests
2. Negotiate research agreements
3. Obtain IRB approval

**Timeline:** 3-6 months  
**Cost:** $2,000-10,000 (filing fees, research agreements)  
**IRB:** Required

---

## Sample Acquisition Plan

**Target:** 5,000 couples total

**Breakdown:**
- Historical records (FamilySearch): 2,000 couples (1900-1980)
- Celebrity marriages (Wikipedia/IMDb): 1,000 couples (1980-2024)
- Census PUMS: 1,000 couples (2000-2024)
- State records (if accessible): 1,000 couples (1990-2024)

**Stratification:**
- By era: 1980s (20%), 1990s (25%), 2000s (30%), 2010s (20%), 2020s (5%)
- By outcome: Target 50% divorced, 50% still married
- By geography: Diverse U.S. regions

---

## Data Quality Considerations

### Minimum Required Fields
**Essential:**
- Partner 1 first name
- Partner 2 first name
- Marriage year
- Relationship status (married/divorced)
- Marriage duration (years)

**Highly Desirable:**
- Full names (first, middle, last)
- Ages at marriage
- Marriage location
- Divorce year (if divorced)

**Nice to Have:**
- Children's names
- Surname choices
- Previous marriages

### Quality Thresholds
- Missing data: <15% per variable
- Completeness: >90% for essential fields
- Validation: Cross-check celebrity data with multiple sources

---

## Legal & Ethical Checklist

- [ ] IRB approval obtained (if required)
- [ ] Data use agreements signed
- [ ] Privacy policy created
- [ ] De-identification protocol established
- [ ] Data security measures implemented
- [ ] Informed consent (if collecting new data)
- [ ] Publication approval from data providers
- [ ] Compliance with state laws verified

---

## Cost Estimate

**Minimal Budget (Public Data Only):**
- Personnel time: $0 (self-collected)
- News archive access: $500
- **Total:** ~$500

**Moderate Budget (with State Records):**
- Personnel time: $5,000
- Records request fees: $2,000
- Legal review: $1,000
- Database licenses: $1,000
- **Total:** ~$9,000

**Full Budget (Comprehensive):**
- Personnel time: $15,000
- Data acquisition: $5,000
- Legal/IRB: $3,000
- Software/infrastructure: $2,000
- **Total:** ~$25,000

---

## Timeline

**Week 1-2:** IRB preparation and approval
**Week 3-6:** Public data collection (Census, NCHS)
**Week 7-10:** Historical data (FamilySearch)
**Week 11-14:** Celebrity data (Wikipedia/IMDb)
**Week 15-26:** State records (if pursuing)

**Total:** 6 months for complete dataset

---

## Contact Information

**For IRB Questions:**
- Your institution's IRB office
- OHRP (Office for Human Research Protections): https://www.hhs.gov/ohrp/

**For Data Access:**
- NCHS: nchs-data@cdc.gov
- Census: census.askdata@census.gov
- State vital statistics: (varies by state)

---

**Last Updated:** November 8, 2025  
**Next Review:** Before data collection begins

