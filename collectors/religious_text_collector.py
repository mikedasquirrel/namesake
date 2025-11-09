"""
Religious Text Collector
========================

Collects and processes religious texts (gospels, sutras, etc.) with success metrics.
Gathers adherent data, geographic spread, cultural influence metrics.
"""

import logging
import json
from typing import Dict, List, Optional
from pathlib import Path
import re

from core.models import db, ReligiousText, ReligiousTextSuccessMetrics, RegionalAdoptionAnalysis
from analyzers.gospel_success_analyzer import gospel_success_analyzer

logger = logging.getLogger(__name__)


class ReligiousTextCollector:
    """Collect and process religious texts with success metrics."""
    
    # Pre-defined religious texts with metadata
    CANONICAL_TEXTS = {
        'matthew': {
            'text_name': 'Gospel of Matthew',
            'text_type': 'gospel',
            'religious_tradition': 'christianity',
            'sub_tradition': 'canonical',
            'author_attributed': 'Matthew',
            'composition_year': 85,
            'composition_location': 'Antioch (traditional)',
            'original_language': 'Greek',
            'character_names': ['Jesus', 'Peter', 'John', 'James', 'Mary', 'Joseph', 'Judas', 'Pilate', 'Herod'],
            'place_names': ['Jerusalem', 'Galilee', 'Bethlehem', 'Nazareth', 'Capernaum']
        },
        'mark': {
            'text_name': 'Gospel of Mark',
            'text_type': 'gospel',
            'religious_tradition': 'christianity',
            'sub_tradition': 'canonical',
            'author_attributed': 'Mark',
            'composition_year': 70,
            'composition_location': 'Rome (traditional)',
            'original_language': 'Greek',
            'character_names': ['Jesus', 'Peter', 'John', 'James', 'Mary', 'Joseph', 'Judas', 'Pilate'],
            'place_names': ['Jerusalem', 'Galilee', 'Capernaum', 'Bethsaida']
        },
        'luke': {
            'text_name': 'Gospel of Luke',
            'text_type': 'gospel',
            'religious_tradition': 'christianity',
            'sub_tradition': 'canonical',
            'author_attributed': 'Luke',
            'composition_year': 85,
            'composition_location': 'Achaia (traditional)',
            'original_language': 'Greek',
            'character_names': ['Jesus', 'Peter', 'John', 'James', 'Mary', 'Joseph', 'Judas', 'Pilate', 'Elizabeth', 'Zechariah'],
            'place_names': ['Jerusalem', 'Galilee', 'Bethlehem', 'Nazareth', 'Emmaus']
        },
        'john': {
            'text_name': 'Gospel of John',
            'text_type': 'gospel',
            'religious_tradition': 'christianity',
            'sub_tradition': 'canonical',
            'author_attributed': 'John',
            'composition_year': 95,
            'composition_location': 'Ephesus (traditional)',
            'original_language': 'Greek',
            'character_names': ['Jesus', 'Peter', 'John', 'Thomas', 'Mary', 'Martha', 'Lazarus', 'Judas', 'Pilate'],
            'place_names': ['Jerusalem', 'Galilee', 'Bethany', 'Cana', 'Samaria']
        }
    }
    
    # Historical adherent data (estimated millions by region/century)
    CHRISTIANITY_ADHERENT_DATA = [
        # Format: (century, region, adherents_millions, percentage_of_population)
        (1, 'Middle East', 0.1, 0.5),
        (2, 'Middle East', 0.5, 2.0),
        (3, 'Roman Empire', 5.0, 10.0),
        (4, 'Roman Empire', 20.0, 40.0),
        (5, 'Europe', 25.0, 50.0),
        (10, 'Europe', 50.0, 85.0),
        (15, 'Europe', 70.0, 95.0),
        (16, 'Americas', 5.0, 20.0),
        (18, 'Global', 200.0, 25.0),
        (20, 'Global', 2000.0, 33.0),
        (21, 'Global', 2400.0, 31.0),
    ]
    
    def __init__(self):
        """Initialize collector."""
        self.logger = logging.getLogger(__name__)
        self.logger.info("ReligiousTextCollector initialized")
    
    def collect_gospel(self, gospel_key: str) -> Optional[ReligiousText]:
        """
        Collect and process a gospel/religious text.
        
        Args:
            gospel_key: Key identifier (e.g., 'matthew', 'mark')
        
        Returns:
            ReligiousText object
        """
        if gospel_key not in self.CANONICAL_TEXTS:
            self.logger.error(f"Unknown gospel: {gospel_key}")
            return None
        
        metadata = self.CANONICAL_TEXTS[gospel_key]
        
        # Check if already exists
        existing = ReligiousText.query.filter_by(text_name=metadata['text_name']).first()
        if existing:
            self.logger.info(f"Gospel {metadata['text_name']} already exists")
            return existing
        
        # Create mock text for analysis (in production, load actual text)
        mock_text = self._generate_mock_gospel_text(metadata)
        
        # Analyze composition
        composition = gospel_success_analyzer.analyze_text_composition(
            metadata['text_name'],
            mock_text,
            metadata['character_names']
        )
        
        # Create religious text entry
        text = ReligiousText(
            text_name=metadata['text_name'],
            text_type=metadata['text_type'],
            religious_tradition=metadata['religious_tradition'],
            sub_tradition=metadata['sub_tradition'],
            author_attributed=metadata['author_attributed'],
            composition_year=metadata['composition_year'],
            composition_location=metadata['composition_location'],
            original_language=metadata['original_language'],
            total_words=composition['text_stats']['total_words'],
            total_characters=composition['text_stats']['total_characters'],
            unique_character_names=composition['text_stats']['unique_names'],
            unique_place_names=len(metadata['place_names']),
            lexical_diversity=composition['linguistic']['lexical_diversity'],
            mean_word_length=composition['linguistic']['mean_word_length'],
            mean_sentence_length=composition['linguistic']['mean_sentence_length'],
            reading_level=composition['linguistic']['reading_level'],
            mean_name_syllables=composition['name_patterns']['mean_syllables'],
            mean_name_length=composition['name_patterns']['mean_length'],
            name_melodiousness=composition['name_patterns']['melodiousness'],
            name_complexity=composition['name_patterns']['complexity'],
            translation_count=100,  # Estimated
            first_translation_year=200,  # Approximate
            narrative_style='chronological',
            key_themes=json.dumps(['faith', 'redemption', 'ministry', 'resurrection']),
            miracle_count=20,  # Approximate
            parable_count=15,  # Approximate
        )
        
        try:
            db.session.add(text)
            db.session.commit()
            self.logger.info(f"Saved {metadata['text_name']} to database")
            
            # Add success metrics
            self._add_success_metrics(text.id, metadata['religious_tradition'])
            
            return text
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error saving religious text: {e}")
            return None
    
    def _generate_mock_gospel_text(self, metadata: Dict) -> str:
        """Generate mock gospel text for analysis."""
        # Simple mock text with character names
        names = ' '.join(metadata['character_names'])
        places = ' '.join(metadata['place_names'])
        
        mock = f"""
        In the beginning, {names} traveled through {places}.
        They spoke of faith and taught the people.
        Many miracles were performed, and parables were told.
        The story spread across nations and changed the world.
        """ * 50  # Repeat for sufficient word count
        
        return mock
    
    def _add_success_metrics(self, religious_text_id: int, tradition: str):
        """Add historical success metrics for text."""
        if tradition != 'christianity':
            return  # Only have Christian data currently
        
        for century, region, adherents_millions, percentage in self.CHRISTIANITY_ADHERENT_DATA:
            year = century * 100  # Convert century to approximate year
            
            metric = ReligiousTextSuccessMetrics(
                religious_text_id=religious_text_id,
                region=region,
                continent='Multiple' if region == 'Global' else 'Europe/Middle East',
                year=year,
                century=century,
                adherent_population=int(adherents_millions * 1_000_000),
                percentage_of_population=percentage,
                growth_rate_annual=0.5,  # Simplified
                geographic_area_km2=10_000_000.0 if region == 'Global' else 5_000_000.0,
                number_of_countries=50 if region == 'Global' else 20,
                overall_cultural_influence=0.8 if century >= 10 else 0.5,
                biblical_names_popularity=0.7 if century >= 5 else 0.3,
                places_of_worship=100000 if region == 'Global' else 10000,
                data_source='Historical estimates',
                data_quality='medium',
                confidence_score=0.6
            )
            
            try:
                db.session.add(metric)
            except Exception as e:
                self.logger.error(f"Error adding success metric: {e}")
        
        try:
            db.session.commit()
            self.logger.info(f"Added success metrics for text {religious_text_id}")
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error committing success metrics: {e}")
    
    def collect_all_gospels(self) -> List[ReligiousText]:
        """Collect all canonical gospels."""
        texts = []
        for gospel_key in ['matthew', 'mark', 'luke', 'john']:
            text = self.collect_gospel(gospel_key)
            if text:
                texts.append(text)
        return texts


# Singleton
religious_text_collector = ReligiousTextCollector()

