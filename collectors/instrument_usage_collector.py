"""
Instrument Usage Frequency Data Collector

Combines multiple data sources to create comprehensive usage frequency metrics
for musical instruments across Romance language regions. Uses proxy-based estimates
informed by musicological knowledge, regional traditions, and cultural patterns.

Data Sources Combined:
A. Historical Composition Counts (proxy: composer nationality + typical instrumentation)
B. Modern Recording Frequency (proxy: genre popularity by region)
C. Sheet Music Corpus (proxy: educational emphasis by region)
D. Cultural Survey Prominence (proxy: ethnomusicological literature)
E. Ensemble Appearance Rate (proxy: standard ensemble configurations)

Note: This collector uses culturally-informed estimates. In production, these would
be replaced with actual data from musicological databases, streaming services,
sheet music catalogs, and cultural surveys.
"""

import logging
from typing import Dict, List
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class InstrumentUsageCollector:
    """
    Collects and normalizes usage frequency data for instruments by Romance regions.
    Uses proxy estimates based on musicological knowledge and cultural patterns.
    """
    
    def __init__(self):
        # Regional music genre emphases (inform usage patterns)
        self.regional_genre_profiles = {
            'spain': {
                'classical': 0.3,
                'flamenco': 0.4,
                'folk': 0.2,
                'popular': 0.1
            },
            'france': {
                'classical': 0.5,
                'chanson': 0.2,
                'folk': 0.1,
                'popular': 0.2
            },
            'italy': {
                'classical': 0.4,
                'opera': 0.3,
                'folk': 0.15,
                'popular': 0.15
            },
            'portugal': {
                'classical': 0.2,
                'fado': 0.3,
                'folk': 0.3,
                'popular': 0.2
            },
            'romania': {
                'classical': 0.3,
                'folk': 0.4,
                'popular': 0.3
            }
        }
        
        # Instrument-region affinities (cultural associations)
        self.cultural_affinities = self._build_cultural_affinities()
    
    def _build_cultural_affinities(self) -> Dict:
        """
        Build culturally-informed instrument-region affinity scores.
        Scale 0-100: How culturally central is this instrument to this region?
        """
        return {
            # STRING INSTRUMENTS
            'violin': {'spain': 75, 'france': 90, 'italy': 95, 'portugal': 70, 'romania': 80},
            'viola': {'spain': 70, 'france': 85, 'italy': 90, 'portugal': 65, 'romania': 75},
            'cello': {'spain': 72, 'france': 88, 'italy': 92, 'portugal': 68, 'romania': 78},
            'double bass': {'spain': 70, 'france': 85, 'italy': 88, 'portugal': 65, 'romania': 75},
            'guitar': {'spain': 98, 'france': 70, 'italy': 75, 'portugal': 95, 'romania': 65},
            'harp': {'spain': 55, 'france': 80, 'italy': 70, 'portugal': 60, 'romania': 50},
            'lute': {'spain': 60, 'france': 65, 'italy': 75, 'portugal': 55, 'romania': 45},
            'mandolin': {'spain': 65, 'france': 55, 'italy': 85, 'portugal': 60, 'romania': 50},
            
            # WOODWIND INSTRUMENTS
            'flute': {'spain': 75, 'france': 88, 'italy': 85, 'portugal': 70, 'romania': 75},
            'clarinet': {'spain': 70, 'france': 85, 'italy': 80, 'portugal': 68, 'romania': 75},
            'oboe': {'spain': 68, 'france': 92, 'italy': 82, 'portugal': 65, 'romania': 70},
            'bassoon': {'spain': 65, 'france': 85, 'italy': 78, 'portugal': 62, 'romania': 68},
            'saxophone': {'spain': 65, 'france': 88, 'italy': 70, 'portugal': 68, 'romania': 65},
            'recorder': {'spain': 60, 'france': 70, 'italy': 75, 'portugal': 65, 'romania': 60},
            'piccolo': {'spain': 65, 'france': 78, 'italy': 80, 'portugal': 63, 'romania': 68},
            
            # BRASS INSTRUMENTS
            'trumpet': {'spain': 75, 'france': 82, 'italy': 88, 'portugal': 72, 'romania': 75},
            'trombone': {'spain': 70, 'france': 78, 'italy': 82, 'portugal': 68, 'romania': 72},
            'French horn': {'spain': 65, 'france': 90, 'italy': 75, 'portugal': 63, 'romania': 68},
            'tuba': {'spain': 65, 'france': 75, 'italy': 72, 'portugal': 63, 'romania': 70},
            'cornet': {'spain': 68, 'france': 80, 'italy': 75, 'portugal': 65, 'romania': 70},
            
            # PERCUSSION INSTRUMENTS
            'drums': {'spain': 75, 'france': 80, 'italy': 82, 'portugal': 78, 'romania': 80},
            'timpani': {'spain': 70, 'france': 82, 'italy': 85, 'portugal': 68, 'romania': 75},
            'cymbals': {'spain': 68, 'france': 75, 'italy': 78, 'portugal': 70, 'romania': 75},
            'castanets': {'spain': 98, 'france': 45, 'italy': 50, 'portugal': 70, 'romania': 30},
            'xylophone': {'spain': 60, 'france': 70, 'italy': 68, 'portugal': 62, 'romania': 65},
            'maracas': {'spain': 75, 'france': 55, 'italy': 58, 'portugal': 72, 'romania': 45},
            
            # KEYBOARD INSTRUMENTS
            'piano': {'spain': 85, 'france': 92, 'italy': 95, 'portugal': 82, 'romania': 88},
            'organ': {'spain': 78, 'france': 88, 'italy': 92, 'portugal': 80, 'romania': 85},
            'harpsichord': {'spain': 65, 'france': 85, 'italy': 88, 'portugal': 63, 'romania': 68},
            'accordion': {'spain': 68, 'france': 88, 'italy': 92, 'portugal': 75, 'romania': 85},
            'celesta': {'spain': 55, 'france': 75, 'italy': 72, 'portugal': 53, 'romania': 60},
            
            # FOLK/REGIONAL INSTRUMENTS
            'bagpipes': {'spain': 75, 'france': 70, 'italy': 55, 'portugal': 68, 'romania': 50},
            'bandoneón': {'spain': 65, 'france': 45, 'italy': 48, 'portugal': 50, 'romania': 35},
        }
    
    def generate_usage_data(self, instrument_name: str, region: str) -> Dict:
        """
        Generate comprehensive usage data for an instrument in a region.
        
        Args:
            instrument_name: Base English name of instrument
            region: spain, france, italy, portugal, romania
            
        Returns:
            Dictionary with all usage metrics
        """
        # Get cultural affinity (baseline)
        affinity = self.cultural_affinities.get(instrument_name, {}).get(region, 50)
        
        # A. Historical Composition Count (proxy estimate)
        # Higher affinity → more compositions featuring this instrument
        historical_base = affinity * 10  # Scale to reasonable count
        historical_count = int(historical_base + (historical_base * 0.3 * (hash(instrument_name + region) % 100 / 100)))
        historical_score = min(100, (historical_count / 10))  # Normalize
        
        # B. Modern Recording Frequency (proxy based on genre mix)
        # Classical-heavy regions favor orchestral; folk-heavy favor regional
        genre_profile = self.regional_genre_profiles.get(region, {})
        
        # Determine if instrument fits regional genres
        is_orchestral = instrument_name in ['violin', 'viola', 'cello', 'double bass', 'flute', 'clarinet', 'oboe', 'bassoon', 'trumpet', 'trombone', 'French horn', 'tuba', 'timpani', 'piano']
        is_folk = instrument_name in ['guitar', 'accordion', 'bagpipes', 'castanets', 'mandolin']
        
        genre_fit = 0
        if is_orchestral:
            genre_fit = genre_profile.get('classical', 0.3) * 100
        if is_folk:
            genre_fit += genre_profile.get('folk', 0.2) * 100
        
        modern_recording_score = min(100, (affinity * 0.6 + genre_fit * 0.4))
        
        # C. Sheet Music Corpus Frequency (proxy: educational emphasis)
        # Common educational instruments score higher
        educational_instruments = {
            'piano': 95, 'violin': 90, 'guitar': 88, 'flute': 85, 'clarinet': 80,
            'trumpet': 75, 'cello': 75, 'recorder': 85, 'drums': 70
        }
        education_base = educational_instruments.get(instrument_name, 50)
        sheet_music_frequency = int(education_base * (affinity / 100) * 50)  # Scaled count
        sheet_music_score = min(100, education_base * (affinity / 100))
        
        # D. Cultural Survey Prominence (1-10 scale)
        # Direct mapping from affinity
        cultural_prominence = affinity / 10  # Scale to 1-10
        cultural_survey_score = affinity  # Already 0-100
        
        # E. Ensemble Appearance Rate (percentage)
        # Orchestral instruments appear in more ensembles
        standard_ensembles = {
            'violin': 0.95, 'viola': 0.90, 'cello': 0.92, 'double bass': 0.85,
            'flute': 0.88, 'oboe': 0.82, 'clarinet': 0.85, 'bassoon': 0.78,
            'trumpet': 0.80, 'trombone': 0.75, 'French horn': 0.82, 'tuba': 0.70,
            'piano': 0.90, 'timpani': 0.75, 'drums': 0.70
        }
        ensemble_rate = standard_ensembles.get(instrument_name, 0.40)
        ensemble_appearance_score = ensemble_rate * 100
        
        # Period Breakdown (medieval to contemporary)
        # Estimate based on instrument age and regional history
        period_breakdown = self._generate_period_breakdown(instrument_name, region, affinity)
        
        # Composite Normalized Usage Score (weighted average)
        weights = {
            'historical': 0.15,
            'modern': 0.30,
            'sheet_music': 0.20,
            'cultural': 0.20,
            'ensemble': 0.15
        }
        
        normalized_score = (
            historical_score * weights['historical'] +
            modern_recording_score * weights['modern'] +
            sheet_music_score * weights['sheet_music'] +
            cultural_survey_score * weights['cultural'] +
            ensemble_appearance_score * weights['ensemble']
        )
        
        # Data quality metrics
        # (In production, would reflect actual source availability)
        sources_available = []
        if historical_count > 0:
            sources_available.append('historical_compositions')
        if modern_recording_score > 30:
            sources_available.append('modern_recordings')
        if sheet_music_frequency > 10:
            sources_available.append('sheet_music')
        if cultural_prominence > 3:
            sources_available.append('cultural_surveys')
        if ensemble_rate > 0.3:
            sources_available.append('ensemble_data')
        
        data_completeness = (len(sources_available) / 5) * 100
        
        if data_completeness > 80:
            confidence = 'high'
        elif data_completeness > 50:
            confidence = 'medium'
        else:
            confidence = 'low'
        
        # Regional specialization score
        # How unique is this usage to this region vs. others?
        all_affinities = self.cultural_affinities.get(instrument_name, {})
        if all_affinities:
            mean_affinity = sum(all_affinities.values()) / len(all_affinities)
            regional_specialization = (affinity - mean_affinity) / mean_affinity * 100 if mean_affinity > 0 else 0
        else:
            regional_specialization = 0
        
        return {
            'historical_composition_count': historical_count,
            'historical_composition_score': historical_score,
            'modern_recording_frequency': modern_recording_score / 100,  # As float 0-1
            'modern_recording_score': modern_recording_score,
            'sheet_music_corpus_frequency': sheet_music_frequency,
            'sheet_music_corpus_score': sheet_music_score,
            'cultural_survey_prominence': cultural_prominence,
            'cultural_survey_score': cultural_survey_score,
            'ensemble_appearance_rate': ensemble_rate,
            'ensemble_appearance_score': ensemble_appearance_score,
            'period_breakdown': json.dumps(period_breakdown),
            'normalized_usage_score': normalized_score,
            'weights_used': json.dumps(weights),
            'data_completeness_score': data_completeness,
            'confidence_level': confidence,
            'sources_used': json.dumps(sources_available),
            'regional_specialization_score': regional_specialization,
            'usage_notes': self._generate_usage_notes(instrument_name, region, affinity)
        }
    
    def _generate_period_breakdown(self, instrument_name: str, region: str, affinity: float) -> Dict:
        """
        Generate usage frequency estimates across historical periods.
        
        Returns dict with keys: medieval, baroque, classical, romantic, modern, contemporary
        """
        # Instrument age affects historical presence
        ancient_instruments = ['harp', 'lute', 'recorder', 'bagpipes', 'drums', 'organ']
        baroque_instruments = ['violin', 'viola', 'cello', 'double bass', 'flute', 'oboe', 'bassoon', 'trumpet', 'harpsichord']
        modern_instruments = ['saxophone', 'accordion', 'bandoneón', 'xylophone', 'celesta']
        
        # Base pattern: 0 before invention, ramp up after
        breakdown = {
            'medieval': 0,
            'baroque': 0,
            'classical': 0,
            'romantic': 0,
            'modern': 0,
            'contemporary': 0
        }
        
        if instrument_name in ancient_instruments:
            breakdown['medieval'] = affinity * 0.3
            breakdown['baroque'] = affinity * 0.5
            breakdown['classical'] = affinity * 0.6
            breakdown['romantic'] = affinity * 0.7
            breakdown['modern'] = affinity * 0.8
            breakdown['contemporary'] = affinity * 0.9
        elif instrument_name in baroque_instruments:
            breakdown['medieval'] = 0
            breakdown['baroque'] = affinity * 0.6
            breakdown['classical'] = affinity * 0.9
            breakdown['romantic'] = affinity * 1.0
            breakdown['modern'] = affinity * 0.95
            breakdown['contemporary'] = affinity * 0.90
        elif instrument_name in modern_instruments:
            breakdown['medieval'] = 0
            breakdown['baroque'] = 0
            breakdown['classical'] = 0
            breakdown['romantic'] = affinity * 0.3
            breakdown['modern'] = affinity * 0.8
            breakdown['contemporary'] = affinity * 1.0
        else:
            # Default classical-era instruments
            breakdown['medieval'] = affinity * 0.1
            breakdown['baroque'] = affinity * 0.4
            breakdown['classical'] = affinity * 0.8
            breakdown['romantic'] = affinity * 1.0
            breakdown['modern'] = affinity * 0.9
            breakdown['contemporary'] = affinity * 0.85
        
        return breakdown
    
    def _generate_usage_notes(self, instrument_name: str, region: str, affinity: float) -> str:
        """Generate qualitative usage notes"""
        notes = []
        
        if affinity > 90:
            notes.append(f"{instrument_name.capitalize()} is central to {region.capitalize()}'s musical identity.")
        elif affinity > 75:
            notes.append(f"{instrument_name.capitalize()} has strong cultural presence in {region.capitalize()}.")
        elif affinity > 60:
            notes.append(f"{instrument_name.capitalize()} is commonly used in {region.capitalize()}'s music.")
        elif affinity > 40:
            notes.append(f"{instrument_name.capitalize()} has moderate presence in {region.capitalize()}.")
        else:
            notes.append(f"{instrument_name.capitalize()} is relatively uncommon in {region.capitalize()}'s tradition.")
        
        # Special cases
        if instrument_name == 'castanets' and region == 'spain':
            notes.append("Quintessentially Spanish, central to flamenco.")
        elif instrument_name == 'accordion' and region in ['france', 'italy']:
            notes.append("Strongly associated with folk music traditions.")
        elif instrument_name == 'guitar' and region in ['spain', 'portugal']:
            notes.append("National instrument, ubiquitous across musical genres.")
        elif instrument_name == 'oboe' and region == 'france':
            notes.append("French name 'hautbois' reflects historical importance.")
        
        return " ".join(notes)
    
    def get_all_usage_data(self, instruments_list: List[str]) -> Dict[str, Dict[str, Dict]]:
        """
        Generate usage data for all instruments across all regions.
        
        Args:
            instruments_list: List of instrument base names
            
        Returns:
            Nested dict: {instrument_name: {region: usage_data}}
        """
        all_data = {}
        regions = ['spain', 'france', 'italy', 'portugal', 'romania']
        
        for instrument in instruments_list:
            all_data[instrument] = {}
            for region in regions:
                all_data[instrument][region] = self.generate_usage_data(instrument, region)
        
        return all_data
    
    def get_regional_rankings(self, instruments_list: List[str], region: str) -> List[Dict]:
        """
        Get instruments ranked by usage frequency within a region.
        
        Returns:
            List of dicts with instrument name and usage score, sorted descending
        """
        rankings = []
        for instrument in instruments_list:
            usage_data = self.generate_usage_data(instrument, region)
            rankings.append({
                'instrument': instrument,
                'usage_score': usage_data['normalized_usage_score'],
                'affinity': self.cultural_affinities.get(instrument, {}).get(region, 50)
            })
        
        return sorted(rankings, key=lambda x: x['usage_score'], reverse=True)
    
    def get_stats(self, instruments_list: List[str]) -> Dict:
        """Get collection statistics"""
        total_instruments = len(instruments_list)
        total_regions = 5
        total_data_points = total_instruments * total_regions
        
        return {
            'total_instruments': total_instruments,
            'total_regions': total_regions,
            'total_data_points': total_data_points,
            'regions': ['spain', 'france', 'italy', 'portugal', 'romania'],
            'data_sources': [
                'historical_compositions',
                'modern_recordings',
                'sheet_music_corpus',
                'cultural_surveys',
                'ensemble_appearances'
            ],
            'methodology': 'Proxy estimates based on musicological knowledge and cultural patterns'
        }


if __name__ == '__main__':
    # Test collector
    collector = InstrumentUsageCollector()
    
    # Test with a few instruments
    test_instruments = ['violin', 'guitar', 'castanets', 'accordion']
    
    print("="*60)
    print("INSTRUMENT USAGE FREQUENCY DATA")
    print("="*60)
    
    for instrument in test_instruments:
        print(f"\n{instrument.upper()}:")
        for region in ['spain', 'france', 'italy']:
            data = collector.generate_usage_data(instrument, region)
            print(f"  {region.capitalize()}: {data['normalized_usage_score']:.1f}/100 (confidence: {data['confidence_level']})")
    
    print("\n" + "="*60)
    print("SPAIN RANKINGS (Top 5):")
    rankings = collector.get_regional_rankings(test_instruments, 'spain')
    for i, item in enumerate(rankings[:5], 1):
        print(f"  {i}. {item['instrument']}: {item['usage_score']:.1f}")
    
    print("="*60)

