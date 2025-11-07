"""
Academic Names Collector
Collects university professor data for nominative determinism analysis

Targets:
- Top 50 universities (Phase 1): n=10,000 professors
- Mid-tier universities (Phase 2): n=20,000 professors  
- Teaching-focused institutions (Phase 3): n=20,000 professors

Data sources:
- University faculty directories (web scraping)
- Google Scholar (research metrics)
- Manual university ranking data
"""

import re
import time
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse
import random

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from scholarly import scholarly, ProxyGenerator
import nameparser

from core.models import db, Academic, AcademicAnalysis, AcademicResearchMetrics
from analyzers.name_analyzer import NameAnalyzer
from analyzers.advanced_analyzer import AdvancedAnalyzer
from analyzers.phonemic_analyzer import PhonemicAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AcademicCollector:
    """Collect and analyze university professor data"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / 'data' / 'academics'
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize analyzers
        self.name_analyzer = NameAnalyzer()
        self.advanced_analyzer = AdvancedAnalyzer()
        self.phonemic_analyzer = PhonemicAnalyzer()
        
        # University rankings (US News 2024)
        self.university_rankings = self._load_university_rankings()
        
        # Field classification mappings
        self.field_mappings = self._load_field_mappings()
        
        # Selenium driver (lazy init)
        self._driver = None
        
        # User agents for polite scraping
        self.user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]
        
    def _load_university_rankings(self) -> Dict[str, Dict]:
        """Load university rankings and metadata"""
        
        # Top 50 US universities (US News 2024 rankings)
        rankings = {
            # Ivy League
            'Princeton University': {'rank': 1, 'tier': 'top_20', 'type': 'private'},
            'Harvard University': {'rank': 3, 'tier': 'top_20', 'type': 'private'},
            'Yale University': {'rank': 5, 'tier': 'top_20', 'type': 'private'},
            'Stanford University': {'rank': 3, 'tier': 'top_20', 'type': 'private'},
            'Massachusetts Institute of Technology': {'rank': 2, 'tier': 'top_20', 'type': 'private'},
            'Columbia University': {'rank': 12, 'tier': 'top_20', 'type': 'private'},
            'University of Pennsylvania': {'rank': 7, 'tier': 'top_20', 'type': 'private'},
            'Cornell University': {'rank': 12, 'tier': 'top_20', 'type': 'private'},
            'Brown University': {'rank': 9, 'tier': 'top_20', 'type': 'private'},
            'Dartmouth College': {'rank': 12, 'tier': 'top_20', 'type': 'private'},
            
            # Top private universities
            'Duke University': {'rank': 7, 'tier': 'top_20', 'type': 'private'},
            'Northwestern University': {'rank': 9, 'tier': 'top_20', 'type': 'private'},
            'University of Chicago': {'rank': 6, 'tier': 'top_20', 'type': 'private'},
            'California Institute of Technology': {'rank': 7, 'tier': 'top_20', 'type': 'private'},
            'Johns Hopkins University': {'rank': 9, 'tier': 'top_20', 'type': 'private'},
            
            # Top public universities
            'University of California, Berkeley': {'rank': 15, 'tier': 'top_20', 'type': 'public'},
            'University of California, Los Angeles': {'rank': 15, 'tier': 'top_20', 'type': 'public'},
            'University of Michigan': {'rank': 21, 'tier': 'top_50', 'type': 'public'},
            'University of Virginia': {'rank': 24, 'tier': 'top_50', 'type': 'public'},
            'University of North Carolina': {'rank': 22, 'tier': 'top_50', 'type': 'public'},
            'University of California, San Diego': {'rank': 28, 'tier': 'top_50', 'type': 'public'},
            'University of Texas at Austin': {'rank': 32, 'tier': 'top_50', 'type': 'public'},
            'University of Washington': {'rank': 40, 'tier': 'top_50', 'type': 'public'},
            'Georgia Institute of Technology': {'rank': 33, 'tier': 'top_50', 'type': 'public'},
            
            # More top 50
            'Vanderbilt University': {'rank': 18, 'tier': 'top_20', 'type': 'private'},
            'Rice University': {'rank': 17, 'tier': 'top_20', 'type': 'private'},
            'Washington University in St. Louis': {'rank': 24, 'tier': 'top_50', 'type': 'private'},
            'Emory University': {'rank': 24, 'tier': 'top_50', 'type': 'private'},
            'Carnegie Mellon University': {'rank': 24, 'tier': 'top_50', 'type': 'private'},
            'University of Notre Dame': {'rank': 20, 'tier': 'top_20', 'type': 'private'},
            'University of Southern California': {'rank': 28, 'tier': 'top_50', 'type': 'private'},
            'New York University': {'rank': 35, 'tier': 'top_50', 'type': 'private'},
            'Boston University': {'rank': 43, 'tier': 'top_50', 'type': 'private'},
            'Boston College': {'rank': 39, 'tier': 'top_50', 'type': 'private'},
        }
        
        return rankings
    
    def _load_field_mappings(self) -> Dict[str, str]:
        """Map department names to broad fields"""
        
        mappings = {
            # STEM fields
            'physics': 'stem',
            'chemistry': 'stem',
            'biology': 'stem',
            'mathematics': 'stem',
            'computer science': 'stem',
            'engineering': 'stem',
            'electrical engineering': 'stem',
            'mechanical engineering': 'stem',
            'bioengineering': 'stem',
            'statistics': 'stem',
            'astronomy': 'stem',
            'earth science': 'stem',
            'geology': 'stem',
            'neuroscience': 'stem',
            'biochemistry': 'stem',
            
            # Humanities
            'english': 'humanities',
            'literature': 'humanities',
            'history': 'humanities',
            'philosophy': 'humanities',
            'classics': 'humanities',
            'languages': 'humanities',
            'linguistics': 'humanities',
            'art history': 'humanities',
            'music': 'humanities',
            'theater': 'humanities',
            'religion': 'humanities',
            
            # Social sciences
            'psychology': 'social_science',
            'sociology': 'social_science',
            'economics': 'social_science',
            'political science': 'social_science',
            'anthropology': 'social_science',
            'geography': 'social_science',
            
            # Professional schools
            'business': 'professional',
            'law': 'professional',
            'medicine': 'professional',
            'education': 'professional',
            'public policy': 'professional',
            'architecture': 'professional',
            'social work': 'professional',
        }
        
        return mappings
    
    def classify_field(self, department: str) -> Tuple[str, str]:
        """
        Classify department into broad field category
        
        Returns:
            (field_broad, field_specific)
        """
        if not department:
            return ('unknown', None)
        
        dept_lower = department.lower()
        
        # Try exact matches first
        for field_specific, field_broad in self.field_mappings.items():
            if field_specific in dept_lower:
                return (field_broad, field_specific)
        
        # Fallback heuristics
        if any(word in dept_lower for word in ['science', 'engineering', 'math', 'tech']):
            return ('stem', None)
        elif any(word in dept_lower for word in ['literature', 'art', 'music', 'history']):
            return ('humanities', None)
        elif any(word in dept_lower for word in ['social', 'psychology', 'economics', 'political']):
            return ('social_science', None)
        elif any(word in dept_lower for word in ['business', 'law', 'medicine', 'school']):
            return ('professional', None)
        
        return ('interdisciplinary', None)
    
    def extract_academic_rank(self, title: str) -> str:
        """
        Extract academic rank from title
        
        Examples:
            "John Smith, Associate Professor" -> "associate"
            "Jane Doe, Distinguished Professor" -> "distinguished"
            "Bob Jones, Assistant Professor of Physics" -> "assistant"
        """
        if not title:
            return 'unknown'
        
        title_lower = title.lower()
        
        # Check for specific ranks
        if 'distinguished' in title_lower or 'endowed chair' in title_lower:
            return 'distinguished'
        elif 'emeritus' in title_lower or 'emerita' in title_lower:
            return 'emeritus'
        elif 'assistant professor' in title_lower:
            return 'assistant'
        elif 'associate professor' in title_lower:
            return 'associate'
        elif 'professor' in title_lower:
            return 'full'
        elif 'lecturer' in title_lower or 'instructor' in title_lower:
            return 'lecturer'
        
        return 'unknown'
    
    def parse_name(self, full_name: str) -> Dict[str, str]:
        """
        Parse full name into components
        
        Returns:
            {'first': str, 'middle': str, 'last': str, 'full': str}
        """
        name = nameparser.HumanName(full_name)
        
        return {
            'first': name.first,
            'middle': name.middle,
            'last': name.last,
            'full': full_name.strip()
        }
    
    def scrape_mit_faculty(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Scrape MIT faculty directory
        
        MIT has a well-structured directory that's good for testing
        """
        logger.info("="*70)
        logger.info("SCRAPING: MIT Faculty")
        logger.info("="*70)
        
        faculty = []
        
        # MIT Physics Department as pilot
        # In real implementation, would iterate through all departments
        departments = [
            {'name': 'Physics', 'url': 'https://web.mit.edu/physics/people/faculty/index.html'},
            {'name': 'Mathematics', 'url': 'https://math.mit.edu/directory/faculty.html'},
            # Add more departments here
        ]
        
        for dept in departments:
            logger.info(f"\nScraping {dept['name']} department...")
            
            try:
                response = requests.get(
                    dept['url'],
                    headers={'User-Agent': random.choice(self.user_agents)},
                    timeout=10
                )
                
                if response.status_code != 200:
                    logger.warning(f"Failed to fetch {dept['url']}: {response.status_code}")
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find faculty listings (structure varies by department)
                # This is a generic parser - would need customization per university
                faculty_links = soup.find_all('a', href=True)
                
                for link in faculty_links:
                    text = link.get_text(strip=True)
                    
                    # Heuristic: looks like a professor name
                    if len(text.split()) >= 2 and len(text) > 5:
                        # Extract info
                        parsed_name = self.parse_name(text)
                        
                        faculty_data = {
                            'full_name': parsed_name['full'],
                            'first_name': parsed_name['first'],
                            'middle_name': parsed_name['middle'],
                            'last_name': parsed_name['last'],
                            'university_name': 'Massachusetts Institute of Technology',
                            'department': dept['name'],
                            'profile_url': urljoin(dept['url'], link['href']),
                            'data_source': 'university_directory'
                        }
                        
                        faculty.append(faculty_data)
                
                logger.info(f"  Found {len(faculty)} faculty members in {dept['name']}")
                
                # Polite delay
                time.sleep(2)
                
                if limit and len(faculty) >= limit:
                    break
                    
            except Exception as e:
                logger.error(f"Error scraping {dept['name']}: {e}")
                continue
        
        logger.info(f"\n✓ Total MIT faculty collected: {len(faculty)}")
        return faculty
    
    def scrape_harvard_faculty(self, limit: Optional[int] = None) -> List[Dict]:
        """Scrape Harvard faculty directory"""
        logger.info("="*70)
        logger.info("SCRAPING: Harvard University Faculty")
        logger.info("="*70)
        
        # Placeholder - real implementation would scrape Harvard's directory
        # Harvard has decentralized directories, so would need per-school scraping
        
        faculty = []
        
        # Example structure
        schools = [
            'Faculty of Arts and Sciences',
            'Harvard Business School',
            'Harvard Law School',
            'Harvard Medical School',
            # etc.
        ]
        
        logger.info(f"✓ Harvard faculty collection (placeholder): {len(faculty)}")
        return faculty
    
    def collect_from_manual_data(self) -> List[Dict]:
        """
        Bootstrap with manually collected faculty data
        
        For pilot testing, use a small manually curated set
        """
        logger.info("="*70)
        logger.info("LOADING: Manual Bootstrap Faculty Data")
        logger.info("="*70)
        
        # Sample data for testing (real people from public directories)
        bootstrap_data = [
            # MIT Physics (real examples)
            {
                'full_name': 'Frank Wilczek',
                'first_name': 'Frank',
                'last_name': 'Wilczek',
                'academic_rank': 'distinguished',
                'title': 'Herman Feshbach Professor of Physics',
                'university_name': 'Massachusetts Institute of Technology',
                'department': 'Physics',
                'field_broad': 'stem',
                'field_specific': 'physics',
                'profile_url': 'https://physics.mit.edu/faculty/frank-wilczek/'
            },
            {
                'full_name': 'Alan Guth',
                'first_name': 'Alan',
                'last_name': 'Guth',
                'academic_rank': 'full',
                'title': 'Victor F. Weisskopf Professor of Physics',
                'university_name': 'Massachusetts Institute of Technology',
                'department': 'Physics',
                'field_broad': 'stem',
                'field_specific': 'physics',
                'profile_url': 'https://physics.mit.edu/faculty/alan-guth/'
            },
            
            # Harvard (real examples)
            {
                'full_name': 'Steven Pinker',
                'first_name': 'Steven',
                'last_name': 'Pinker',
                'academic_rank': 'full',
                'title': 'Johnstone Family Professor of Psychology',
                'university_name': 'Harvard University',
                'department': 'Psychology',
                'field_broad': 'social_science',
                'field_specific': 'psychology',
                'profile_url': 'https://psychology.fas.harvard.edu/people/steven-pinker'
            },
            
            # Stanford (real examples)
            {
                'full_name': 'Andrew Ng',
                'first_name': 'Andrew',
                'last_name': 'Ng',
                'academic_rank': 'associate',
                'title': 'Associate Professor of Computer Science',
                'university_name': 'Stanford University',
                'department': 'Computer Science',
                'field_broad': 'stem',
                'field_specific': 'computer science',
                'profile_url': 'https://cs.stanford.edu/people/ang/'
            },
        ]
        
        logger.info(f"✓ Loaded {len(bootstrap_data)} bootstrap faculty records")
        return bootstrap_data
    
    def enrich_google_scholar(self, academic_id: int, full_name: str, 
                            university: str) -> Optional[Dict]:
        """
        Enrich academic record with Google Scholar metrics
        
        Args:
            academic_id: Database ID
            full_name: Professor's full name
            university: University name for disambiguation
            
        Returns:
            Dict with scholar metrics or None if not found
        """
        try:
            logger.info(f"Searching Google Scholar for: {full_name} at {university}")
            
            # Search for scholar profile
            search_query = f'{full_name} {university}'
            search_results = scholarly.search_author(search_query)
            
            # Get first result (assumes correct match)
            try:
                author = next(search_results)
            except StopIteration:
                logger.warning(f"No Google Scholar profile found for {full_name}")
                return None
            
            # Fill in details
            author_filled = scholarly.fill(author)
            
            # Extract metrics
            metrics = {
                'h_index': author_filled.get('hindex', None),
                'total_citations': author_filled.get('citedby', None),
                'i10_index': author_filled.get('i10index', None),
                'google_scholar_id': author_filled.get('scholar_id', None),
                'google_scholar_url': author_filled.get('url_picture', None),
            }
            
            # Extract publication years for temporal metrics
            if 'publications' in author_filled:
                years = []
                for pub in author_filled['publications']:
                    if 'bib' in pub and 'pub_year' in pub['bib']:
                        try:
                            year = int(pub['bib']['pub_year'])
                            years.append(year)
                        except:
                            pass
                
                if years:
                    metrics['first_publication_year'] = min(years)
                    metrics['most_recent_publication_year'] = max(years)
                    current_year = datetime.now().year
                    metrics['years_publishing'] = current_year - min(years)
                    
                    if metrics['years_publishing'] > 0:
                        metrics['citations_per_year'] = metrics['total_citations'] / metrics['years_publishing']
                        metrics['h_index_per_year'] = metrics['h_index'] / metrics['years_publishing']
            
            # Most cited paper
            if 'publications' in author_filled and len(author_filled['publications']) > 0:
                sorted_pubs = sorted(
                    author_filled['publications'],
                    key=lambda x: x['num_citations'] if 'num_citations' in x else 0,
                    reverse=True
                )
                if sorted_pubs:
                    top_pub = sorted_pubs[0]
                    if 'bib' in top_pub:
                        metrics['most_cited_paper_title'] = top_pub['bib'].get('title', None)
                        metrics['most_cited_paper_citations'] = top_pub.get('num_citations', None)
                        metrics['most_cited_paper_year'] = top_pub['bib'].get('pub_year', None)
            
            metrics['collected_from_google_scholar'] = True
            metrics['google_scholar_last_updated'] = datetime.utcnow()
            
            logger.info(f"  ✓ Found: h-index={metrics.get('h_index')}, citations={metrics.get('total_citations')}")
            
            # Polite delay
            time.sleep(5)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error fetching Google Scholar data for {full_name}: {e}")
            return {
                'collection_errors': str(e),
                'collected_from_google_scholar': False
            }
    
    def analyze_academic_name(self, academic: Academic) -> AcademicAnalysis:
        """
        Perform comprehensive phonetic analysis of academic name
        
        Uses existing analyzers from the nominative determinism framework
        """
        full_name = academic.full_name
        
        # Basic name analysis
        basic = self.name_analyzer.analyze_name(full_name, None)
        
        # Advanced linguistic analysis
        advanced = self.advanced_analyzer.analyze(full_name, None)
        
        # Phonemic analysis
        phonemic = self.phonemic_analyzer.analyze(full_name)
        
        # Create analysis record
        analysis = AcademicAnalysis(
            academic_id=academic.id,
            
            # Basic metrics
            syllable_count=basic.get('syllable_count'),
            character_length=basic.get('character_length'),
            word_count=basic.get('word_count'),
            
            # Phonetic
            phonetic_score=basic.get('phonetic_score'),
            vowel_ratio=basic.get('vowel_ratio'),
            consonant_clusters=basic.get('consonant_clusters'),
            
            # Memorability
            memorability_score=basic.get('memorability_score'),
            pronounceability_score=basic.get('pronounceability_score'),
            uniqueness_score=basic.get('uniqueness_score'),
            
            # Advanced
            phonestheme_score=advanced.get('phonestheme_score'),
            phonestheme_type=advanced.get('phonestheme_type'),
            vowel_brightness=advanced.get('vowel_brightness'),
            vowel_emotion_profile=advanced.get('vowel_emotion_profile'),
            consonant_hardness=advanced.get('consonant_hardness'),
            
            # Psychological
            authority_score=advanced.get('authority_score'),
            innovation_score=advanced.get('innovation_score'),
            trust_score=advanced.get('trust_score'),
            
            # Phonemic
            plosive_ratio=phonemic.get('plosive_ratio'),
            fricative_ratio=phonemic.get('fricative_ratio'),
            voicing_ratio=phonemic.get('voicing_ratio'),
            initial_is_plosive=phonemic.get('initial_is_plosive'),
            
            # Name categorization
            name_type=basic.get('name_type'),
            has_numbers=basic.get('has_numbers'),
            has_special_chars=basic.get('has_special_chars'),
            capital_pattern=basic.get('capital_pattern'),
        )
        
        # Calculate academic-specific composite scores
        analysis.intellectual_sophistication_score = self._calculate_sophistication(
            syllable_count=analysis.syllable_count,
            phonetic_score=analysis.phonetic_score,
            uniqueness_score=analysis.uniqueness_score
        )
        
        analysis.academic_authority_composite = self._calculate_academic_authority(
            authority_score=analysis.authority_score,
            consonant_hardness=analysis.consonant_hardness,
            memorability_score=analysis.memorability_score
        )
        
        # Gender coding (simple heuristic)
        analysis.gender_coding = self._infer_gender(academic.first_name)
        
        return analysis
    
    def _calculate_sophistication(self, syllable_count: int, phonetic_score: float,
                                 uniqueness_score: float) -> float:
        """
        Calculate intellectual sophistication composite score
        
        Higher syllables + higher phonetic complexity + higher uniqueness = more sophisticated
        """
        if syllable_count is None or phonetic_score is None or uniqueness_score is None:
            return None
        
        # Normalize and combine
        syllable_component = min(syllable_count / 5.0, 1.0) * 100  # Cap at 5 syllables
        phonetic_component = phonetic_score
        uniqueness_component = uniqueness_score or 50
        
        # Weighted average
        sophistication = (syllable_component * 0.3 + 
                         phonetic_component * 0.4 + 
                         uniqueness_component * 0.3)
        
        return round(sophistication, 2)
    
    def _calculate_academic_authority(self, authority_score: float,
                                     consonant_hardness: float,
                                     memorability_score: float) -> float:
        """Calculate composite authority score for academic context"""
        if authority_score is None or consonant_hardness is None or memorability_score is None:
            return None
        
        # Higher authority + moderate hardness + high memorability = academic gravitas
        composite = (authority_score * 0.5 + 
                    consonant_hardness * 0.2 + 
                    memorability_score * 0.3)
        
        return round(composite, 2)
    
    def _infer_gender(self, first_name: str) -> str:
        """Simple gender coding based on common names"""
        if not first_name:
            return 'unknown'
        
        name_lower = first_name.lower()
        
        # Very simple heuristic (would use proper name-gender database in production)
        masculine_endings = ['ert', 'ard', 'ald', 'iam', 'ohn', 'ack', 'ick']
        feminine_endings = ['ara', 'ina', 'ine', 'lyn', 'elle', 'ette']
        
        for ending in feminine_endings:
            if name_lower.endswith(ending):
                return 'feminine'
        
        for ending in masculine_endings:
            if name_lower.endswith(ending):
                return 'masculine'
        
        # Ambiguous or neutral
        if len(name_lower) <= 4:
            return 'neutral'
        
        return 'ambiguous'
    
    def save_academic_to_db(self, academic_data: Dict) -> Optional[int]:
        """
        Save academic and their analysis to database
        
        Returns:
            academic_id if successful, None otherwise
        """
        try:
            # Check if already exists
            existing = Academic.query.filter_by(
                full_name=academic_data['full_name'],
                university_name=academic_data['university_name']
            ).first()
            
            if existing:
                logger.info(f"  Already in database: {academic_data['full_name']}")
                return existing.id
            
            # Get university metadata
            uni_info = self.university_rankings.get(academic_data.get('university_name'), {})
            
            # Classify field if not provided
            field_broad = academic_data.get('field_broad')
            field_specific = academic_data.get('field_specific')
            
            if not field_broad:
                field_broad, field_specific = self.classify_field(
                    academic_data.get('department')
                )
            
            # Create Academic record
            academic = Academic(
                full_name=academic_data['full_name'],
                first_name=academic_data.get('first_name'),
                middle_name=academic_data.get('middle_name'),
                last_name=academic_data.get('last_name'),
                academic_rank=academic_data.get('academic_rank', 'unknown'),
                title=academic_data.get('title'),
                university_name=academic_data['university_name'],
                university_ranking=uni_info.get('rank'),
                university_tier=uni_info.get('tier', 'other'),
                department=academic_data.get('department'),
                field_broad=field_broad,
                field_specific=field_specific,
                profile_url=academic_data.get('profile_url'),
                data_source=academic_data.get('data_source', 'manual')
            )
            
            db.session.add(academic)
            db.session.flush()  # Get ID without committing
            
            # Perform name analysis
            analysis = self.analyze_academic_name(academic)
            db.session.add(analysis)
            
            db.session.commit()
            
            logger.info(f"  ✓ Saved: {academic.full_name} (ID: {academic.id})")
            return academic.id
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"  ✗ Error saving {academic_data.get('full_name')}: {e}")
            return None
    
    def collect_pilot_sample(self, n_target: int = 500) -> Dict:
        """
        Collect pilot sample for testing
        
        Args:
            n_target: Target number of professors
            
        Returns:
            Collection statistics
        """
        logger.info("\n" + "="*70)
        logger.info("ACADEMIC NAMES COLLECTION - PILOT SAMPLE")
        logger.info("="*70)
        logger.info(f"Target: {n_target} professors from top universities")
        logger.info("="*70 + "\n")
        
        stats = {
            'target': n_target,
            'collected': 0,
            'analyzed': 0,
            'google_scholar_enriched': 0,
            'errors': 0,
            'universities': []
        }
        
        # Start with manual bootstrap data
        bootstrap = self.collect_from_manual_data()
        
        for academic_data in bootstrap:
            academic_id = self.save_academic_to_db(academic_data)
            
            if academic_id:
                stats['collected'] += 1
                stats['analyzed'] += 1
                
                if academic_data['university_name'] not in stats['universities']:
                    stats['universities'].append(academic_data['university_name'])
        
        # Try to enrich with Google Scholar (slow, so limited in pilot)
        academics = Academic.query.limit(10).all()
        for academic in academics:
            if not academic.research_metrics:
                scholar_data = self.enrich_google_scholar(
                    academic.id,
                    academic.full_name,
                    academic.university_name
                )
                
                if scholar_data and scholar_data.get('collected_from_google_scholar'):
                    metrics = AcademicResearchMetrics(
                        academic_id=academic.id,
                        **{k: v for k, v in scholar_data.items() 
                           if hasattr(AcademicResearchMetrics, k)}
                    )
                    db.session.add(metrics)
                    db.session.commit()
                    stats['google_scholar_enriched'] += 1
        
        logger.info("\n" + "="*70)
        logger.info("PILOT COLLECTION COMPLETE")
        logger.info("="*70)
        logger.info(f"✓ Collected: {stats['collected']} professors")
        logger.info(f"✓ Analyzed: {stats['analyzed']} name profiles")
        logger.info(f"✓ Google Scholar: {stats['google_scholar_enriched']} enriched")
        logger.info(f"✓ Universities: {len(stats['universities'])}")
        logger.info("="*70 + "\n")
        
        return stats


def main():
    """Run academic collector pilot"""
    collector = AcademicCollector()
    results = collector.collect_pilot_sample(n_target=500)
    
    print("\n" + "="*70)
    print("PILOT RESULTS")
    print("="*70)
    print(f"Target: {results['target']}")
    print(f"Collected: {results['collected']}")
    print(f"Google Scholar enriched: {results['google_scholar_enriched']}")
    print(f"Universities sampled: {len(results['universities'])}")
    print("="*70)
    
    return results


if __name__ == '__main__':
    main()

