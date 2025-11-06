"""Darwin Correspondence Project Corpus Collector

Accesses the Darwin Correspondence Project to download:
1. Beagle voyage journals (1831-1836)
2. Letters mentioning the Beagle
3. Pre and post-voyage correspondence
4. Origin of Species drafts

Purpose: Test whether HMS Beagle name primed Darwin's adaptation thinking

Data source: https://www.darwinproject.ac.uk/
Free access, digitized corpus
"""

import requests
import json
import re
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DarwinCorpusCollector:
    """Collect and organize Darwin's writings for temporal analysis."""
    
    def __init__(self):
        self.base_url = "https://www.darwinproject.ac.uk"
        self.output_dir = Path(__file__).parent.parent / 'data' / 'darwin_corpus'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Temporal periods for analysis
        self.periods = {
            'pre_voyage': (1820, 1831),  # Before HMS Beagle
            'voyage': (1831, 1836),      # On HMS Beagle
            'post_voyage_early': (1836, 1844),  # Theory gestation
            'post_voyage_late': (1844, 1859),   # Origin of Species writing
            'post_publication': (1859, 1882)    # After publication
        }
        
    def collect_full_corpus(self) -> Dict[str, Any]:
        """Collect complete Darwin corpus organized by period."""
        
        logger.info("="*70)
        logger.info("DARWIN CORPUS COLLECTION")
        logger.info("="*70)
        logger.info("Collecting letters, journals, and manuscripts")
        logger.info("Source: Darwin Correspondence Project")
        logger.info("="*70)
        
        results = {
            'metadata': {
                'collected_date': datetime.now().isoformat(),
                'source': 'Darwin Correspondence Project',
                'purpose': 'HMS Beagle nominative synchronicity analysis'
            },
            'periods': {},
            'beagle_mentions': [],
            'adaptation_language': [],
            'corpus_statistics': {}
        }
        
        # Note: Darwin Correspondence Project doesn't have a full API
        # We'll create a structured dataset from known sources
        
        # 1. Create manual corpus from publicly available texts
        logger.info("\n[Phase 1] Creating corpus structure...")
        results['corpus_structure'] = self._create_corpus_structure()
        
        # 2. Manual data entry guide
        logger.info("\n[Phase 2] Creating data collection templates...")
        results['collection_templates'] = self._create_collection_templates()
        
        # 3. Search keywords
        logger.info("\n[Phase 3] Defining search strategy...")
        results['search_strategy'] = self._define_search_strategy()
        
        # Save results
        self._save_corpus_plan(results)
        
        return results
    
    def _create_corpus_structure(self) -> Dict[str, Any]:
        """Define corpus organization structure."""
        
        structure = {
            'voyage_journals': {
                'source': 'The Voyage of the Beagle (1839 publication)',
                'url': 'https://www.gutenberg.org/ebooks/944',
                'format': 'Plain text available via Project Gutenberg',
                'period': 'voyage',
                'estimated_word_count': 200000,
                'chapters': 21,
                'years_covered': '1831-1836',
                'key_for_analysis': 'Primary source for ship name mentions and adaptation language'
            },
            
            'correspondence': {
                'source': 'Darwin Correspondence Project',
                'url': 'https://www.darwinproject.ac.uk/letters',
                'total_letters': 15000,  # Digitized portion
                'searchable': True,
                'periods_covered': 'all',
                'key_for_analysis': 'Temporal tracking of concept emergence'
            },
            
            'notebooks': {
                'source': 'Darwin Online (http://darwin-online.org.uk/)',
                'types': [
                    'Red Notebook (1836-1837)',
                    'Transmutation Notebooks (1837-1839)',
                    'Zoology Notes',
                    'Geology Notes'
                ],
                'period': 'post_voyage_early',
                'key_for_analysis': 'Theory development after voyage'
            },
            
            'origin_of_species': {
                'source': 'Project Gutenberg + Darwin Online',
                'url': 'https://www.gutenberg.org/ebooks/1228',
                'publication_year': 1859,
                'estimated_word_count': 150000,
                'key_for_analysis': 'Final theory - count "adaptation" usage'
            },
            
            'autobiography': {
                'source': 'The Autobiography of Charles Darwin (1887)',
                'url': 'https://www.gutenberg.org/ebooks/2010',
                'period': 'post_publication',
                'key_for_analysis': 'Reflections on Beagle voyage, any ship name mentions'
            }
        }
        
        return structure
    
    def _create_collection_templates(self) -> Dict[str, Any]:
        """Create templates for manual data extraction."""
        
        # Since we can't auto-scrape everything, create structured templates
        
        templates = {
            'beagle_mention_template': {
                'fields': [
                    'document_id',
                    'document_type',  # letter, journal, notebook
                    'date',
                    'period',  # pre_voyage, voyage, post_voyage_early, etc.
                    'mention_text',  # Exact quote with "beagle"
                    'context_before',  # 100 words before
                    'context_after',  # 100 words after
                    'adaptation_language_present',  # Boolean
                    'adaptation_words',  # List of adaptation-related words in context
                    'sentiment',  # Positive/Neutral/Negative about ship
                    'topic',  # What is being discussed
                ],
                'example': {
                    'document_id': 'DCP-LETT-0123',
                    'document_type': 'letter',
                    'date': '1832-04-15',
                    'period': 'voyage',
                    'mention_text': 'The Beagle anchored in the bay...',
                    'context_before': 'We have observed remarkable variations in finch beaks...',
                    'context_after': 'These adaptations to different food sources are striking...',
                    'adaptation_language_present': True,
                    'adaptation_words': ['variations', 'adaptations'],
                    'sentiment': 'Neutral',
                    'topic': 'Natural history observations'
                }
            },
            
            'adaptation_language_template': {
                'fields': [
                    'document_id',
                    'date',
                    'period',
                    'word_used',  # adaptation, adapt, adaptive, etc.
                    'full_sentence',
                    'context',  # What adaptation is being discussed
                    'beagle_mentioned_nearby',  # Within 100 words
                    'biological_context',  # Is this about biology vs general use
                ],
                'search_terms': [
                    'adapt', 'adaptation', 'adaptive', 'adaptable',
                    'variation', 'vary', 'varied',
                    'modification', 'modify', 'modified',
                    'gradation', 'graduated',
                    'fitness', 'suited', 'fit for'
                ]
            }
        }
        
        return templates
    
    def _define_search_strategy(self) -> Dict[str, Any]:
        """Define search strategy for corpus analysis."""
        
        return {
            'primary_search_terms': {
                'ship_name': ['Beagle', 'beagle', 'H.M.S. Beagle', 'HMS Beagle'],
                'adaptation_family': [
                    'adapt', 'adaptation', 'adaptive', 'adaptable', 'adaptability',
                    'adapted', 'adapting', 'adaptations'
                ],
                'variation_family': [
                    'variation', 'vary', 'varied', 'varying', 'variety', 'varieties'
                ],
                'selection_family': [
                    'selection', 'select', 'selected', 'selecting',
                    'natural selection', 'artificial selection'
                ]
            },
            
            'temporal_analysis': {
                'bin_by_year': True,
                'cumulative_counts': True,
                'test_for_spikes': 'Around voyage years (1831-1836)',
                'co_occurrence_window': 100,  # Words
            },
            
            'semantic_network': {
                'when_beagle_mentioned': 'What concepts co-occur?',
                'topic_modeling': 'Identify themes in beagle-mentioning passages',
                'sentiment_analysis': 'Positive/negative around ship name'
            },
            
            'control_comparisons': {
                'other_ships': 'Compare to mentions of other ships (HMS Adventure, etc.)',
                'other_animals': 'Compare to dog breed mentions (terrier, hound)',
                'ship_operations': 'Distinguish name from operational discussions'
            },
            
            'data_sources_priority': {
                '1_highest': 'Voyage of the Beagle (1839) - Gutenberg #944',
                '2_high': 'Beagle voyage correspondence - Darwin Project search',
                '3_medium': 'Red Notebook & Transmutation notebooks - Darwin Online',
                '4_low': 'Autobiography - Gutenberg #2010'
            }
        }
    
    def _save_corpus_plan(self, results: Dict[str, Any]):
        """Save corpus collection plan."""
        
        output_file = self.output_dir / 'darwin_corpus_plan.json'
        
        with output_file.open('w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"\n{'='*70}")
        logger.info(f"✅ Corpus plan saved to: {output_file}")
        logger.info(f"{'='*70}")
    
    def download_gutenberg_text(self, book_id: int, title: str) -> Optional[str]:
        """Download text from Project Gutenberg."""
        
        url = f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt"
        
        try:
            logger.info(f"Downloading {title} from Project Gutenberg...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Save to file
            output_file = self.output_dir / f'gutenberg_{book_id}_{title.replace(" ", "_")}.txt'
            output_file.write_text(response.text, encoding='utf-8')
            
            logger.info(f"✅ Downloaded {title} ({len(response.text)} characters)")
            logger.info(f"   Saved to: {output_file}")
            
            return response.text
            
        except Exception as e:
            logger.error(f"Failed to download {title}: {e}")
            return None
    
    def collect_key_texts(self):
        """Download key Darwin texts from free sources."""
        
        logger.info("\n[DOWNLOADING KEY TEXTS FROM PROJECT GUTENBERG]")
        
        texts = {
            'voyage_of_beagle': (944, 'Voyage_of_the_Beagle'),
            'origin_of_species': (1228, 'Origin_of_Species'),
            'darwin_autobiography': (2010, 'Darwin_Autobiography')
        }
        
        downloaded = {}
        
        for key, (book_id, title) in texts.items():
            text = self.download_gutenberg_text(book_id, title)
            if text:
                downloaded[key] = {
                    'book_id': book_id,
                    'title': title,
                    'length': len(text),
                    'file': f'gutenberg_{book_id}_{title}.txt'
                }
            time.sleep(2)  # Be polite to Gutenberg servers
        
        # Save metadata
        metadata_file = self.output_dir / 'downloaded_texts_metadata.json'
        with metadata_file.open('w') as f:
            json.dump(downloaded, f, indent=2)
        
        logger.info(f"\n✅ Downloaded {len(downloaded)}/3 key texts")
        
        return downloaded


def main():
    """Run Darwin corpus collection."""
    
    collector = DarwinCorpusCollector()
    
    # Create collection plan
    results = collector.collect_full_corpus()
    
    # Download available texts
    downloaded = collector.collect_key_texts()
    
    logger.info("\n" + "="*70)
    logger.info("DARWIN CORPUS COLLECTION COMPLETE")
    logger.info("="*70)
    logger.info("Next steps:")
    logger.info("1. Review downloaded texts in data/darwin_corpus/")
    logger.info("2. Run temporal coding analysis")
    logger.info("3. Search for 'beagle' and 'adaptation' co-occurrences")
    logger.info("="*70)
    
    return results, downloaded


if __name__ == '__main__':
    main()

