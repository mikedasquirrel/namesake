"""
Adult Film Video Collector with Competitive Context
Collects videos with ALL publicly visible nominal features:
- Title, categories, tags, performer names, views

Enables competitive analysis and story coherence measurement
"""

import requests
import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class AdultFilmVideoCollector:
    """
    Collect adult film videos with complete nominal feature set
    and competitive cohort context
    """
    
    def __init__(self):
        """Initialize collector"""
        self.api_base = None  # Would use actual API
        self.rate_limit_delay = 1.0  # Seconds between requests
    
    def collect_performer_videos(self, 
                                 performer_name: str, 
                                 limit: int = 10) -> List[Dict]:
        """
        Collect top videos for a specific performer
        
        Args:
            performer_name: Performer's stage name
            limit: Number of videos to collect
        
        Returns:
            List of video dicts with complete nominal features
        """
        logger.info(f"Collecting videos for {performer_name} (limit={limit})")
        
        videos = []
        
        # In production: actual API call
        # For now: return structure showing what we need
        
        return videos
    
    def collect_monthly_cohort(self, 
                               year: int, 
                               month: int,
                               limit: int = 1000) -> List[Dict]:
        """
        Collect ALL videos from specific month (competitive cohort)
        
        Args:
            year: Year (e.g., 2023)
            month: Month (1-12)
            limit: Maximum videos to collect
        
        Returns:
            List of all videos in that competitive window
        """
        logger.info(f"Collecting monthly cohort: {year}-{month:02d}")
        
        cohort = []
        
        # In production: API call with date filters
        # This would be the actual data collection
        
        logger.info(f"Collected {len(cohort)} videos from {year}-{month:02d}")
        return cohort
    
    def extract_nominal_features(self, video: Dict) -> Dict:
        """
        Extract ALL publicly visible nominal/linguistic features
        
        Input video dict should have:
        - title: str
        - categories: List[str]
        - tags: List[str]  
        - performers: List[str]
        - views: int
        - upload_date: datetime
        
        Returns:
            Complete feature dictionary for analysis
        """
        features = {
            'video_id': video.get('id'),
            'upload_date': video.get('upload_date'),
            'views': video.get('views', 0)
        }
        
        # Extract from TITLE
        title = video.get('title', '')
        features['title'] = title
        features['title_length'] = len(title)
        features['title_word_count'] = len(title.split())
        features['title_harshness'] = self._count_harsh_consonants(title)
        features['title_syllables'] = self._estimate_syllables(title)
        features['title_explicitness'] = self._measure_explicitness(title)
        features['title_quality_words'] = self._count_quality_adjectives(title)
        
        # Extract from CATEGORIES
        categories = video.get('categories', [])
        features['categories'] = categories
        features['n_categories'] = len(categories)
        features['category_specificity'] = self._measure_category_specificity(categories)
        features['mainstream_vs_niche'] = self._classify_mainstream(categories)
        
        # Extract from TAGS
        tags = video.get('tags', [])
        features['tags'] = tags
        features['n_tags'] = len(tags)
        features['tag_specificity'] = self._measure_tag_specificity(tags)
        
        # Extract from PERFORMER NAMES
        performers = video.get('performers', [])
        features['performers'] = performers
        features['n_performers'] = len(performers)
        if performers:
            # Average across performers
            features['performer_harshness'] = sum(self._count_harsh_consonants(p) for p in performers) / len(performers)
            features['performer_memorability'] = sum(self._calculate_memorability(p) for p in performers) / len(performers)
        
        # STORY COHERENCE (across all elements)
        features['title_category_coherence'] = self._measure_coherence(title, categories)
        features['title_tag_coherence'] = self._measure_coherence(title, tags)
        features['overall_story_coherence'] = self._calculate_overall_coherence(features)
        
        return features
    
    def _count_harsh_consonants(self, text: str) -> int:
        """Count harsh consonants in text"""
        harsh = 'kgptbdxz'
        return sum(1 for char in text.lower() if char in harsh)
    
    def _estimate_syllables(self, text: str) -> int:
        """Estimate syllables in text (simple heuristic)"""
        vowels = 'aeiouy'
        text = text.lower()
        count = 0
        prev_vowel = False
        
        for char in text:
            is_vowel = char in vowels
            if is_vowel and not prev_vowel:
                count += 1
            prev_vowel = is_vowel
        
        return max(1, count)
    
    def _measure_explicitness(self, text: str) -> float:
        """
        Measure explicitness of language (0-1)
        Higher = more explicit terminology
        """
        explicit_words = ['hardcore', 'intense', 'rough', 'extreme', 'wild']
        soft_words = ['passionate', 'sensual', 'intimate', 'romantic', 'gentle']
        
        text_lower = text.lower()
        explicit_count = sum(1 for word in explicit_words if word in text_lower)
        soft_count = sum(1 for word in soft_words if word in text_lower)
        
        if explicit_count + soft_count == 0:
            return 0.5  # Neutral
        
        return explicit_count / (explicit_count + soft_count)
    
    def _count_quality_adjectives(self, text: str) -> int:
        """Count quality-signaling adjectives"""
        quality_words = ['best', 'top', 'amazing', 'incredible', 'ultimate', 'perfect', 'premium']
        text_lower = text.lower()
        return sum(1 for word in quality_words if word in text_lower)
    
    def _measure_category_specificity(self, categories: List[str]) -> float:
        """
        Measure how specific vs generic categories are (0-1)
        Higher = more specific/niche
        """
        if not categories:
            return 0.5
        
        generic_categories = ['amateur', 'professional', 'hd', 'verified']
        specific_count = sum(1 for cat in categories if cat.lower() not in generic_categories)
        
        return specific_count / len(categories)
    
    def _classify_mainstream(self, categories: List[str]) -> str:
        """Classify as mainstream, mixed, or niche"""
        if not categories:
            return 'unknown'
        
        mainstream_cats = ['amateur', 'blowjob', 'hardcore', 'milf', 'teen', 'anal']
        mainstream_count = sum(1 for cat in categories if cat.lower() in mainstream_cats)
        
        ratio = mainstream_count / len(categories)
        
        if ratio > 0.6:
            return 'mainstream'
        elif ratio < 0.3:
            return 'niche'
        else:
            return 'mixed'
    
    def _measure_tag_specificity(self, tags: List[str]) -> float:
        """Measure tag specificity (0-1)"""
        if not tags:
            return 0.5
        
        # Longer tags tend to be more specific
        avg_length = sum(len(tag) for tag in tags) / len(tags)
        
        if avg_length < 5:
            return 0.3  # Short, generic tags
        elif avg_length < 10:
            return 0.6  # Medium specificity
        else:
            return 0.9  # Highly specific tags
    
    def _measure_coherence(self, text: str, elements: List[str]) -> float:
        """
        Measure coherence between text and list of elements
        Do they tell the same story?
        """
        if not elements:
            return 0.5
        
        text_lower = text.lower()
        text_words = set(text_lower.split())
        
        # Count how many elements have word overlap with text
        matches = 0
        for element in elements:
            element_words = set(element.lower().split())
            if text_words & element_words:  # Intersection
                matches += 1
        
        return matches / len(elements) if elements else 0.5
    
    def _calculate_memorability(self, name: str) -> float:
        """Calculate name memorability (0-1)"""
        # Simple heuristic: shorter + unique = memorable
        length_score = max(0, 1 - (len(name) - 4) / 10)
        syllable_score = max(0, 1 - (self._estimate_syllables(name) - 2) / 4)
        return (length_score + syllable_score) / 2
    
    def _calculate_overall_coherence(self, features: Dict) -> float:
        """
        Calculate story coherence across ALL nominal elements
        Do title, categories, tags, and names tell a coherent story?
        """
        coherence_scores = [
            features.get('title_category_coherence', 0.5),
            features.get('title_tag_coherence', 0.5)
        ]
        
        return sum(coherence_scores) / len(coherence_scores)
    
    def save_cohort_data(self, cohort: List[Dict], domain: str, cohort_id: str):
        """Save collected cohort data"""
        filename = f"data/cohorts/{domain}_{cohort_id}.json"
        
        import os
        os.makedirs('data/cohorts', exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump(cohort, f, indent=2, default=str)
        
        logger.info(f"Saved cohort data to {filename}")


# =============================================================================
# Example Usage
# =============================================================================

def example_collection():
    """Example of how to use competitive context collection"""
    
    collector = AdultFilmVideoCollector()
    
    # Collect a monthly cohort
    cohort_2023_01 = collector.collect_monthly_cohort(2023, 1, limit=500)
    
    # Extract features for each video
    enhanced_videos = []
    for video in cohort_2023_01:
        features = collector.extract_nominal_features(video)
        enhanced_videos.append(features)
    
    # Save for analysis
    collector.save_cohort_data(enhanced_videos, 'adult_film', '2023-01')
    
    return enhanced_videos


if __name__ == '__main__':
    # Would run actual collection
    print("Adult Film Video Collector - Ready for data collection")
    print("Use: collector = AdultFilmVideoCollector()")
    print("Then: cohort = collector.collect_monthly_cohort(2023, 1)")

