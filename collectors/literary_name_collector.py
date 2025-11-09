"""Literary Name Collector

Collects texts from Project Gutenberg and extracts character names, place names,
and invented terminology for cross-category literary name composition analysis.

Categories: Fiction, Nonfiction, Synoptic Gospels (Matthew, Mark, Luke)

Author: Michael Smerconish
Date: November 2025
"""

import logging
import json
import re
import random
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    logging.warning("spacy not available, will use fallback extraction")

# gutenbergpy has Python 2 dependencies, using direct HTTP instead
GUTENBERG_AVAILABLE = False

import requests
from bs4 import BeautifulSoup

from core.models import db, LiteraryWork, LiteraryCharacter, LiteraryNameAnalysis
from data.common_american_names import COMMON_FIRST_NAMES, COMMON_SURNAMES, generate_population_names
from analyzers.phonetic_base import PhoneticBase

logger = logging.getLogger(__name__)


class LiteraryNameCollector:
    """
    Collects literary texts and extracts character/place names for analysis.
    
    Aggregates:
    - Fiction works from Project Gutenberg (mixed genres)
    - Nonfiction works from Project Gutenberg
    - Synoptic gospels (Matthew, Mark, Luke)
    - American baseline names for comparison
    """
    
    def __init__(self, baseline_sample_size: int = 10000):
        """
        Initialize collector.
        
        Args:
            baseline_sample_size: Number of baseline American names to generate
        """
        self.baseline_sample_size = baseline_sample_size
        self.phonetic_analyzer = PhoneticBase()
        
        # Load spaCy model if available
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_sm")
                logger.info("spaCy model loaded successfully")
            except OSError:
                logger.warning("spaCy model not found, using fallback extraction")
                self.nlp = None
        else:
            self.nlp = None
        
        # Gospel texts (canonical)
        self.gospel_texts_dir = Path("data/texts/gospels")
        
        # Common name database for detecting invented names
        self.common_first_names = set([n.lower() for n in COMMON_FIRST_NAMES])
        self.common_surnames = set([n.lower() for n in COMMON_SURNAMES])
        
        logger.info("LiteraryNameCollector initialized")
        logger.info(f"Baseline sample size: {baseline_sample_size:,}")
    
    def collect_full_dataset(self) -> Dict:
        """
        Collect all literary texts and extract names.
        
        Returns:
            Dictionary with works, characters, and baseline data
        """
        logger.info("="*80)
        logger.info("COLLECTING LITERARY DATA")
        logger.info("="*80)
        
        results = {
            'works': {},
            'characters': {},
            'baselines': {},
            'total_works': 0,
            'total_characters': 0,
        }
        
        # Collect fiction
        logger.info("\nCollecting fiction works...")
        fiction_works = self._collect_fiction_works(target_count=50)
        results['works']['fiction'] = fiction_works
        logger.info(f"  Fiction: {len(fiction_works)} works collected")
        
        # Collect nonfiction
        logger.info("\nCollecting nonfiction works...")
        nonfiction_works = self._collect_nonfiction_works(target_count=30)
        results['works']['nonfiction'] = nonfiction_works
        logger.info(f"  Nonfiction: {len(nonfiction_works)} works collected")
        
        # Collect gospels
        logger.info("\nCollecting synoptic gospels...")
        gospel_works = self._collect_gospel_works()
        results['works']['gospels'] = gospel_works
        logger.info(f"  Gospels: {len(gospel_works)} works collected")
        
        # Extract characters from all works
        logger.info("\nExtracting characters from all works...")
        all_characters = {}
        for category, works in results['works'].items():
            for work_id, work_data in works.items():
                chars = self._extract_characters_from_work(work_data, category)
                all_characters.update(chars)
                results['characters'][work_id] = chars
        
        logger.info(f"  Total characters extracted: {len(all_characters)}")
        
        # Generate baseline
        logger.info("\nGenerating baseline names...")
        baselines = self._generate_baselines()
        results['baselines'] = baselines
        logger.info(f"  Random baseline: {len(baselines['random'])} names")
        logger.info(f"  Stratified baseline: {len(baselines['stratified'])} names")
        
        # Calculate totals
        results['total_works'] = sum(len(works) for works in results['works'].values())
        results['total_characters'] = len(all_characters)
        
        logger.info("\n" + "="*80)
        logger.info(f"DATA COLLECTION COMPLETE")
        logger.info(f"  Total works: {results['total_works']}")
        logger.info(f"  Total characters: {results['total_characters']}")
        logger.info("="*80)
        
        return results
    
    def _collect_fiction_works(self, target_count: int = 50) -> Dict:
        """
        Collect fiction works from Project Gutenberg.
        
        Mixed genres: literary fiction, mystery, sci-fi, fantasy, romance
        """
        works = {}
        
        # Curated list of fiction work IDs from Project Gutenberg
        # Mix of genres and time periods (1900-present available in public domain)
        fiction_ids = self._get_fiction_gutenberg_ids(target_count)
        
        for work_id in fiction_ids[:target_count]:
            try:
                work_data = self._fetch_gutenberg_text(work_id, 'fiction')
                if work_data:
                    works[work_id] = work_data
                    logger.info(f"    Collected: {work_data['title']} by {work_data['author']}")
            except Exception as e:
                logger.error(f"    Error collecting fiction {work_id}: {e}")
        
        return works
    
    def _collect_nonfiction_works(self, target_count: int = 30) -> Dict:
        """
        Collect nonfiction works from Project Gutenberg.
        
        Biographies, memoirs, histories - real person names only
        """
        works = {}
        
        # Curated list of nonfiction work IDs
        nonfiction_ids = self._get_nonfiction_gutenberg_ids(target_count)
        
        for work_id in nonfiction_ids[:target_count]:
            try:
                work_data = self._fetch_gutenberg_text(work_id, 'nonfiction')
                if work_data:
                    works[work_id] = work_data
                    logger.info(f"    Collected: {work_data['title']} by {work_data['author']}")
            except Exception as e:
                logger.error(f"    Error collecting nonfiction {work_id}: {e}")
        
        return works
    
    def _collect_gospel_works(self) -> Dict:
        """
        Collect synoptic gospels (Matthew, Mark, Luke).
        
        Uses canonical texts from data/texts/gospels directory or fetches from Gutenberg.
        """
        works = {}
        
        # Gospel metadata
        gospels = {
            'matthew': {
                'title': 'Gospel of Matthew',
                'author': 'Matthew (canonical)',
                'gutenberg_id': 8001,  # King James Bible includes all gospels
            },
            'mark': {
                'title': 'Gospel of Mark',
                'author': 'Mark (canonical)',
                'gutenberg_id': 8001,
            },
            'luke': {
                'title': 'Gospel of Luke',
                'author': 'Luke (canonical)',
                'gutenberg_id': 8001,
            },
        }
        
        for gospel_key, gospel_info in gospels.items():
            try:
                # Try to load from local files first
                local_path = self.gospel_texts_dir / f"{gospel_key}.txt"
                if local_path.exists():
                    with open(local_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                    work_data = {
                        'work_id': gospel_key,
                        'title': gospel_info['title'],
                        'author': gospel_info['author'],
                        'category': 'gospels',
                        'genre': 'religious',
                        'publication_year': None,  # Ancient text
                        'source': 'canonical_text',
                        'source_id': gospel_key,
                        'text': text,
                        'word_count': len(text.split()),
                    }
                else:
                    # Extract specific gospel from King James Bible
                    work_data = self._extract_gospel_from_kjv(gospel_key, gospel_info)
                
                if work_data:
                    works[gospel_key] = work_data
                    logger.info(f"    Collected: {work_data['title']}")
            
            except Exception as e:
                logger.error(f"    Error collecting gospel {gospel_key}: {e}")
        
        return works
    
    def _get_fiction_gutenberg_ids(self, target_count: int) -> List:
        """
        Get curated list of fiction work IDs from Project Gutenberg.
        
        Returns mix of genres and periods.
        """
        # Curated fiction works (public domain, various genres)
        fiction_works = [
            # Classic literature
            1342,  # Pride and Prejudice (Austen)
            11,    # Alice's Adventures in Wonderland (Carroll)
            74,    # The Adventures of Tom Sawyer (Twain)
            76,    # Adventures of Huckleberry Finn (Twain)
            84,    # Frankenstein (Shelley)
            98,    # A Tale of Two Cities (Dickens)
            174,   # The Picture of Dorian Gray (Wilde)
            345,   # Dracula (Stoker)
            1661,  # The Adventures of Sherlock Holmes (Doyle)
            2701,  # Moby Dick (Melville)
            
            # Science Fiction
            35,    # The Time Machine (Wells)
            36,    # The War of the Worlds (Wells)
            64,    # A Princess of Mars (Burroughs)
            
            # Mystery
            863,   # The Mysterious Affair at Styles (Christie)
            244,   # A Study in Scarlet (Doyle)
            
            # Fantasy/Adventure
            33,    # The Scarlet Pimpernel (Orczy)
            140,   # The Jungle Book (Kipling)
            
            # Romance
            105,   # Persuasion (Austen)
            161,   # Sense and Sensibility (Austen)
            
            # Gothic
            46,    # A Christmas Carol (Dickens)
            
            # More classics
            1400,  # Great Expectations (Dickens)
            1232,  # The Prince and the Pauper (Twain)
            219,   # Heart of Darkness (Conrad)
            120,   # Treasure Island (Stevenson)
            43,    # The Strange Case of Dr. Jekyll and Mr. Hyde (Stevenson)
        ]
        
        # Extend with more IDs if needed
        if len(fiction_works) < target_count:
            # Add more well-known fiction IDs
            additional = [1260, 2554, 514, 205, 768, 1399, 16, 23, 27, 28, 41, 55]
            fiction_works.extend(additional[:target_count - len(fiction_works)])
        
        return fiction_works[:target_count]
    
    def _get_nonfiction_gutenberg_ids(self, target_count: int) -> List:
        """
        Get curated list of nonfiction work IDs from Project Gutenberg.
        
        Returns biographies, memoirs, historical works.
        """
        # Curated nonfiction works
        nonfiction_works = [
            # Biographies
            1232,  # Autobiography of Benjamin Franklin
            2680,  # Meditations (Marcus Aurelius)
            5200,  # Metamorphosis (Kafka) - autobiographical elements
            
            # Historical
            1250,  # Anthem (political)
            1497,  # The Republic (Plato)
            3600,  # Essays of Michel de Montaigne
            4300,  # Ulysses S. Grant: Personal Memoirs
            
            # Memoirs
            1998,  # The Autobiography of Charles Darwin
            6593,  # History of the Peloponnesian War (Thucydides)
            
            # Philosophy (with person references)
            4363,  # Beyond Good and Evil (Nietzsche)
            5827,  # Thus Spake Zarathustra (Nietzsche)
            
            # More historical/biographical
            10,    # The King James Bible (historical names)
            3207,  # Leviathan (Hobbes)
            4280,  # Discourse on Method (Descartes)
        ]
        
        # Extend with historical documents if needed
        if len(nonfiction_works) < target_count:
            additional = list(range(6000, 6000 + target_count - len(nonfiction_works)))
            nonfiction_works.extend(additional)
        
        return nonfiction_works[:target_count]
    
    def _fetch_gutenberg_text(self, work_id: int, category: str) -> Optional[Dict]:
        """
        Fetch text from Project Gutenberg via direct HTTP.
        
        Args:
            work_id: Gutenberg ID
            category: 'fiction' or 'nonfiction'
            
        Returns:
            Work data dictionary or None
        """
        try:
            # Try multiple URL patterns for Project Gutenberg
            urls = [
                f"https://www.gutenberg.org/files/{work_id}/{work_id}-0.txt",
                f"https://www.gutenberg.org/cache/epub/{work_id}/pg{work_id}.txt",
                f"https://www.gutenberg.org/ebooks/{work_id}.txt.utf-8",
            ]
            
            text = None
            for url in urls:
                try:
                    response = requests.get(url, timeout=30)
                    if response.status_code == 200:
                        text = response.text
                        logger.info(f"    Fetched from: {url}")
                        break
                except Exception as e:
                    logger.debug(f"    Failed URL {url}: {e}")
                    continue
            
            if not text:
                logger.warning(f"Could not fetch work {work_id} from any URL")
                return None
            
            # Strip Gutenberg headers/footers
            text = self._strip_gutenberg_headers(text)
            
            # Extract metadata
            metadata = self._extract_metadata_from_text(text, work_id)
            
            # Build work data
            work_data = {
                'work_id': str(work_id),
                'title': metadata.get('title', f'Work {work_id}'),
                'author': metadata.get('author', 'Unknown'),
                'category': category,
                'genre': metadata.get('genre', 'unknown'),
                'publication_year': metadata.get('year'),
                'source': 'Project Gutenberg',
                'source_id': str(work_id),
                'source_url': f'https://www.gutenberg.org/ebooks/{work_id}',
                'text': text,
                'word_count': len(text.split()),
            }
            
            return work_data
        
        except Exception as e:
            logger.error(f"Error fetching Gutenberg text {work_id}: {e}")
            return None
    
    def _strip_gutenberg_headers(self, text: str) -> str:
        """Strip Project Gutenberg headers and footers from text."""
        # Find start of actual text
        start_markers = [
            "*** START OF THE PROJECT GUTENBERG",
            "*** START OF THIS PROJECT GUTENBERG",
            "*END*THE SMALL PRINT",
        ]
        
        for marker in start_markers:
            if marker in text:
                parts = text.split(marker, 1)
                if len(parts) > 1:
                    text = parts[1]
                    # Skip to end of header line
                    if '\n' in text:
                        text = text.split('\n', 1)[1]
                    break
        
        # Find end of actual text
        end_markers = [
            "*** END OF THE PROJECT GUTENBERG",
            "*** END OF THIS PROJECT GUTENBERG",
            "End of the Project Gutenberg",
        ]
        
        for marker in end_markers:
            if marker in text:
                text = text.split(marker)[0]
                break
        
        return text.strip()
    
    def _extract_metadata_from_text(self, text: str, work_id: int) -> Dict:
        """Extract title, author, and other metadata from text."""
        metadata = {}
        
        # Look for title and author in first 2000 characters
        header = text[:2000]
        
        # Title patterns
        title_match = re.search(r'Title:\s*(.+?)(?:\r?\n|$)', header, re.IGNORECASE)
        if title_match:
            metadata['title'] = title_match.group(1).strip()
        
        # Author patterns
        author_match = re.search(r'Author:\s*(.+?)(?:\r?\n|$)', header, re.IGNORECASE)
        if author_match:
            metadata['author'] = author_match.group(1).strip()
        
        # Year patterns
        year_match = re.search(r'Release Date:.*?(\d{4})', header)
        if year_match:
            metadata['year'] = int(year_match.group(1))
        
        return metadata
    
    def _extract_gospel_from_kjv(self, gospel_key: str, gospel_info: Dict) -> Optional[Dict]:
        """Extract specific gospel from King James Bible."""
        # For now, return placeholder - would need to parse KJV properly
        # In practice, gospels would be loaded from separate files
        logger.warning(f"Gospel {gospel_key} not found locally, using placeholder")
        
        return {
            'work_id': gospel_key,
            'title': gospel_info['title'],
            'author': gospel_info['author'],
            'category': 'gospels',
            'genre': 'religious',
            'publication_year': None,
            'source': 'canonical_text',
            'source_id': gospel_key,
            'text': '',  # Would be filled with actual text
            'word_count': 0,
        }
    
    def _extract_characters_from_work(self, work_data: Dict, category: str) -> Dict:
        """
        Extract characters and their metadata from work text.
        
        Args:
            work_data: Work data dictionary
            category: 'fiction', 'nonfiction', or 'gospels'
            
        Returns:
            Dictionary of character data
        """
        text = work_data['text']
        work_id = work_data['work_id']
        
        characters = {}
        
        # Use NER if available, otherwise fallback to pattern matching
        if self.nlp:
            entities = self._extract_entities_with_ner(text)
        else:
            entities = self._extract_entities_with_patterns(text)
        
        # Filter and classify entities
        person_entities = [e for e in entities if e['type'] == 'PERSON']
        place_entities = [e for e in entities if e['type'] in ['GPE', 'LOC']]
        
        logger.info(f"    Extracted {len(person_entities)} person names from {work_data['title']}")
        
        # Count mentions to determine importance
        name_counts = Counter([e['text'] for e in person_entities])
        
        # Create character entries
        char_id = 0
        for name, count in name_counts.most_common():
            if count < 2:  # Skip characters mentioned only once
                continue
            
            char_id += 1
            character_id = f"{work_id}_char_{char_id}"
            
            # Parse name components
            first_name, last_name = self._parse_name(name)
            
            # Classify name type
            name_type = self._classify_name_type(first_name, last_name, category)
            is_invented = name_type in ['invented_plausible', 'invented_fantastical']
            
            # Determine importance based on mention count
            importance_score = min(100, (count / len(person_entities)) * 1000)
            if importance_score > 75:
                importance = 'major'
            elif importance_score > 25:
                importance = 'supporting'
            else:
                importance = 'minor'
            
            characters[character_id] = {
                'character_id': character_id,
                'work_id': work_id,
                'full_name': name,
                'first_name': first_name,
                'last_name': last_name,
                'mention_count': count,
                'importance_score': importance_score,
                'importance': importance,
                'name_type': name_type,
                'is_invented': is_invented,
                'is_place_name': False,
                'entity_type': 'PERSON',
                'extraction_confidence': 0.85,
                # Role and outcome would be filled by analyzer or manual tagging
                'character_role': None,
                'character_outcome': None,
            }
        
        return characters
    
    def _extract_entities_with_ner(self, text: str) -> List[Dict]:
        """Extract named entities using spaCy NER."""
        entities = []
        
        # Process text in chunks (spaCy has limits)
        chunk_size = 100000
        for i in range(0, len(text), chunk_size):
            chunk = text[i:i+chunk_size]
            doc = self.nlp(chunk)
            
            for ent in doc.ents:
                entities.append({
                    'text': ent.text,
                    'type': ent.label_,
                    'start': i + ent.start_char,
                    'end': i + ent.end_char,
                })
        
        return entities
    
    def _extract_entities_with_patterns(self, text: str) -> List[Dict]:
        """Extract named entities using pattern matching (fallback)."""
        entities = []
        
        # Simple capitalized word pattern for names
        # Pattern: Capitalized word(s) not at sentence start
        name_pattern = r'(?<=[.!?]\s)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        
        for match in re.finditer(name_pattern, text):
            name = match.group(1)
            # Filter out common false positives
            if len(name) > 2 and not name.lower() in ['the', 'and', 'but', 'or']:
                entities.append({
                    'text': name,
                    'type': 'PERSON',  # Assume person for now
                    'start': match.start(),
                    'end': match.end(),
                })
        
        return entities
    
    def _parse_name(self, full_name: str) -> Tuple[str, str]:
        """Parse full name into first and last components."""
        parts = full_name.strip().split()
        
        if len(parts) == 1:
            return parts[0], ''
        elif len(parts) == 2:
            return parts[0], parts[1]
        else:
            # Multiple parts: take first and last
            return parts[0], parts[-1]
    
    def _classify_name_type(self, first_name: str, last_name: str, category: str) -> str:
        """
        Classify name as real vs invented.
        
        Returns:
            'real_common', 'real_uncommon', 'historical', 'invented_plausible', 'invented_fantastical'
        """
        first_lower = first_name.lower()
        last_lower = last_name.lower() if last_name else ''
        
        # Check if in common names
        first_is_common = first_lower in self.common_first_names
        last_is_common = last_lower in self.common_surnames if last_name else False
        
        # Gospels: mostly historical
        if category == 'gospels':
            return 'historical'
        
        # Nonfiction: assume all real
        if category == 'nonfiction':
            if first_is_common or last_is_common:
                return 'real_common'
            else:
                return 'real_uncommon'
        
        # Fiction: classify as invented or real
        if first_is_common and (not last_name or last_is_common):
            return 'real_common'
        elif first_is_common or last_is_common:
            return 'real_uncommon'
        else:
            # Check if name has unusual phonetics (fantastical)
            if self._has_fantastical_phonetics(first_name):
                return 'invented_fantastical'
            else:
                return 'invented_plausible'
    
    def _has_fantastical_phonetics(self, name: str) -> bool:
        """Check if name has unusual/fantastical phonetic patterns."""
        name_lower = name.lower()
        
        # Fantastical markers
        fantastical_patterns = [
            r'[xzq]{2,}',  # Repeated exotic consonants
            r'[aeiou]{4,}',  # Long vowel sequences
            r"['-]{2,}",  # Multiple apostrophes/hyphens
            r'^[zxq]',  # Starts with exotic consonant
        ]
        
        for pattern in fantastical_patterns:
            if re.search(pattern, name_lower):
                return True
        
        return False
    
    def _generate_baselines(self) -> Dict:
        """
        Generate baseline American name samples for comparison.
        
        Returns:
            Dictionary with 'random' and 'stratified' baseline samples
        """
        baselines = {}
        
        # Random baseline: uniform sampling
        random_names = generate_population_names(self.baseline_sample_size)
        baselines['random'] = {
            'names': random_names,
            'sample_size': len(random_names),
        }
        
        # Stratified baseline: match literary category proportions
        stratified_names = []
        
        # 60% fiction-like (diverse), 30% nonfiction-like (common), 10% historical
        fiction_count = int(self.baseline_sample_size * 0.6)
        nonfiction_count = int(self.baseline_sample_size * 0.3)
        historical_count = self.baseline_sample_size - fiction_count - nonfiction_count
        
        # Fiction-like: more diverse combinations
        stratified_names.extend(generate_population_names(fiction_count))
        
        # Nonfiction-like: common names only
        for _ in range(nonfiction_count):
            first = random.choice(COMMON_FIRST_NAMES[:50])  # Top 50
            last = random.choice(COMMON_SURNAMES[:50])
            stratified_names.append(f"{first} {last}")
        
        # Historical: biblical/classical names
        historical_names = [
            "John", "Peter", "James", "Mary", "Matthew", "Mark", "Luke",
            "Paul", "Thomas", "Andrew", "Philip", "Simon", "Joseph"
        ]
        for _ in range(historical_count):
            name = random.choice(historical_names)
            last = random.choice(COMMON_SURNAMES)
            stratified_names.append(f"{name} {last}")
        
        baselines['stratified'] = {
            'names': stratified_names,
            'sample_size': len(stratified_names),
        }
        
        return baselines


if __name__ == '__main__':
    # Test collector
    logging.basicConfig(level=logging.INFO)
    
    collector = LiteraryNameCollector(baseline_sample_size=1000)
    dataset = collector.collect_full_dataset()
    
    print(f"\nDataset collected:")
    print(f"  Total works: {dataset['total_works']}")
    print(f"  Total characters: {dataset['total_characters']}")
    print(f"  Fiction works: {len(dataset['works']['fiction'])}")
    print(f"  Nonfiction works: {len(dataset['works']['nonfiction'])}")
    print(f"  Gospel works: {len(dataset['works']['gospels'])}")

