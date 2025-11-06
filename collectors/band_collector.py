"""Band Collector

Collects band/artist data from MusicBrainz API (primary) and Last.fm API (popularity metrics).
Implements stratified sampling by decade (1950s-2020s) with focus on successful/influential bands.

Target: 4,000-5,000 bands total (~500-800 per decade)
Strategy: Prioritize chart success, critical acclaim, genre-defining acts
"""

import logging
import time
import json
import requests
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple
from collections import Counter

from core.models import db, Band, BandAnalysis
from analyzers.name_analyzer import NameAnalyzer
from analyzers.phonemic_analyzer import PhonemicAnalyzer
from analyzers.semantic_analyzer import SemanticAnalyzer
from analyzers.sound_symbolism_analyzer import SoundSymbolismAnalyzer
from analyzers.prosodic_analyzer import ProsodicAnalyzer

logger = logging.getLogger(__name__)


class BandCollector:
    """Collect band data from MusicBrainz and Last.fm APIs."""
    
    def __init__(self, lastfm_api_key: Optional[str] = None):
        """Initialize the collector with API credentials.
        
        Args:
            lastfm_api_key: Last.fm API key (optional, get from config if not provided)
        """
        self.musicbrainz_base_url = "https://musicbrainz.org/ws/2"
        self.lastfm_base_url = "http://ws.audioscrobbler.com/2.0/"
        
        # Get Last.fm API key from config or parameter
        if lastfm_api_key:
            self.lastfm_api_key = lastfm_api_key
        else:
            try:
                from core.config import Config
                self.lastfm_api_key = getattr(Config, 'LASTFM_API_KEY', None)
            except:
                self.lastfm_api_key = None
                logger.warning("Last.fm API key not found. Popularity metrics will be limited.")
        
        # Rate limiting
        self.musicbrainz_delay = 1.0  # 1 second between requests (MusicBrainz requirement)
        self.lastfm_delay = 0.2  # 5 req/sec (conservative, limit is higher)
        
        # Analyzers
        self.name_analyzer = NameAnalyzer()
        self.phonemic_analyzer = PhonemicAnalyzer()
        self.semantic_analyzer = SemanticAnalyzer()
        self.sound_symbolism_analyzer = SoundSymbolismAnalyzer()
        self.prosodic_analyzer = ProsodicAnalyzer()
        
        # User agent for MusicBrainz (required)
        self.headers = {
            'User-Agent': 'NominativeDeterminismResearch/1.0 (research@nominative-determinism.org)'
        }
        
        # Country code to name mapping
        self.country_names = {
            'US': 'United States',
            'GB': 'United Kingdom',
            'CA': 'Canada',
            'AU': 'Australia',
            'DE': 'Germany',
            'FR': 'France',
            'SE': 'Sweden',
            'NO': 'Norway',
            'FI': 'Finland',
            'IS': 'Iceland',
            'IE': 'Ireland',
            'IT': 'Italy',
            'ES': 'Spain',
            'NL': 'Netherlands',
            'BE': 'Belgium',
            'JP': 'Japan',
            'BR': 'Brazil',
            'MX': 'Mexico',
            'AR': 'Argentina',
            'NZ': 'New Zealand',
        }
    
    def collect_stratified_sample(self, target_per_decade: int = 600) -> Dict:
        """Collect stratified sample of bands across decades.
        
        Strategy:
        - Query MusicBrainz for bands formed in each decade
        - Prioritize by rating/score (indicator of significance)
        - Enrich with Last.fm popularity data
        - Save to database with comprehensive linguistic analysis
        
        Args:
            target_per_decade: Target number of bands per decade (default 600)
            
        Returns:
            Collection statistics
        """
        stats = {
            'decades_collected': {},
            'total_added': 0,
            'total_updated': 0,
            'total_analyzed': 0,
            'errors': 0
        }
        
        # Decades to collect (1950s-2020s)
        decades = [1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020]
        
        logger.info("Starting stratified band collection...")
        logger.info(f"Target: {target_per_decade} bands per decade")
        logger.info(f"Total target: {len(decades) * target_per_decade} bands")
        
        for decade in decades:
            logger.info(f"\n{'='*60}")
            logger.info(f"Collecting {decade}s bands...")
            logger.info(f"{'='*60}")
            
            decade_stats = self._collect_decade_bands(decade, target_per_decade)
            stats['decades_collected'][f"{decade}s"] = decade_stats
            stats['total_added'] += decade_stats['added']
            stats['total_updated'] += decade_stats['updated']
            stats['total_analyzed'] += decade_stats['analyzed']
            stats['errors'] += decade_stats['errors']
            
            logger.info(f"✓ {decade}s complete: {decade_stats['added']} added, {decade_stats['updated']} updated")
        
        logger.info(f"\n{'='*60}")
        logger.info("COLLECTION COMPLETE")
        logger.info(f"{'='*60}")
        logger.info(f"Total added: {stats['total_added']}")
        logger.info(f"Total updated: {stats['total_updated']}")
        logger.info(f"Total analyzed: {stats['total_analyzed']}")
        logger.info(f"Errors: {stats['errors']}")
        
        return stats
    
    def _collect_decade_bands(self, decade: int, target_count: int) -> Dict:
        """Collect bands from a specific decade.
        
        Args:
            decade: Starting year of decade (e.g., 1970 for 1970s)
            target_count: Number of bands to collect
            
        Returns:
            Decade collection statistics
        """
        stats = {
            'decade': decade,
            'target': target_count,
            'fetched': 0,
            'added': 0,
            'updated': 0,
            'analyzed': 0,
            'skipped': 0,
            'errors': 0
        }
        
        # Query MusicBrainz for bands formed in this decade
        begin_year = decade
        end_year = decade + 9
        
        offset = 0
        limit = 100  # MusicBrainz pagination limit
        collected = 0
        
        while collected < target_count:
            try:
                # Build query for bands/groups formed in this decade
                query = f'begin:[{begin_year} TO {end_year}] AND type:group'
                
                params = {
                    'query': query,
                    'limit': limit,
                    'offset': offset,
                    'fmt': 'json'
                }
                
                response = requests.get(
                    f"{self.musicbrainz_base_url}/artist",
                    params=params,
                    headers=self.headers
                )
                
                if response.status_code != 200:
                    logger.error(f"MusicBrainz API error: {response.status_code}")
                    stats['errors'] += 1
                    break
                
                data = response.json()
                artists = data.get('artists', [])
                
                if not artists:
                    logger.info(f"No more artists found for {decade}s at offset {offset}")
                    break
                
                stats['fetched'] += len(artists)
                
                # Process each artist
                for artist in artists:
                    if collected >= target_count:
                        break
                    
                    # Extract and save band data
                    result = self._process_artist(artist, decade)
                    
                    if result == 'added':
                        stats['added'] += 1
                        stats['analyzed'] += 1
                        collected += 1
                    elif result == 'updated':
                        stats['updated'] += 1
                        stats['analyzed'] += 1
                        collected += 1
                    elif result == 'skipped':
                        stats['skipped'] += 1
                    elif result == 'error':
                        stats['errors'] += 1
                    
                    # Rate limiting
                    time.sleep(self.musicbrainz_delay)
                
                offset += limit
                
                logger.info(f"  Progress: {collected}/{target_count} ({(collected/target_count)*100:.1f}%)")
                
            except Exception as e:
                logger.error(f"Error collecting {decade}s bands: {e}")
                stats['errors'] += 1
                break
        
        return stats
    
    def _process_artist(self, artist_data: Dict, decade: int) -> str:
        """Process a single artist from MusicBrainz.
        
        Args:
            artist_data: Artist data from MusicBrainz API
            decade: Decade of formation
            
        Returns:
            Status: 'added', 'updated', 'skipped', or 'error'
        """
        try:
            mbid = artist_data.get('id')
            name = artist_data.get('name')
            
            if not mbid or not name:
                return 'skipped'
            
            # Skip if name is too short or obviously invalid
            if len(name) < 2 or name.isdigit():
                return 'skipped'
            
            # Check if already exists
            existing_band = Band.query.get(mbid)
            
            # Parse formation year
            formation_year = None
            life_span = artist_data.get('life-span', {})
            begin = life_span.get('begin')
            if begin:
                try:
                    formation_year = int(begin.split('-')[0])
                except:
                    formation_year = decade  # Default to decade start
            else:
                formation_year = decade
            
            # Parse dissolution year
            dissolution_year = None
            end = life_span.get('end')
            if end:
                try:
                    dissolution_year = int(end.split('-')[0])
                except:
                    pass
            
            # Calculate years active
            current_year = datetime.now().year
            is_active = dissolution_year is None
            if is_active:
                years_active = current_year - formation_year
            else:
                years_active = dissolution_year - formation_year
            
            # Parse origin country
            origin_country = artist_data.get('country', 'Unknown')
            origin_country_name = self.country_names.get(origin_country, origin_country)
            
            # Parse area (city/region)
            origin_city = None
            area = artist_data.get('area', {})
            if area:
                origin_city = area.get('name')
            
            # Get genre/tags from artist data if available
            genres = []
            tags = artist_data.get('tags', [])
            for tag in tags:
                if isinstance(tag, dict):
                    genres.append(tag.get('name', ''))
            
            # Enrich with Last.fm data
            lastfm_data = self._get_lastfm_data(name)
            
            # Combine genres
            if lastfm_data and lastfm_data.get('genres'):
                genres.extend(lastfm_data['genres'])
            
            # Deduplicate genres
            genres = list(set([g.lower() for g in genres if g]))
            
            # Determine primary genre and cluster
            primary_genre = genres[0] if genres else 'Unknown'
            genre_cluster = self._classify_genre_cluster(genres)
            
            # Create or update Band record
            if existing_band:
                band = existing_band
                status = 'updated'
            else:
                band = Band(id=mbid)
                status = 'added'
            
            # Update fields
            band.name = name
            band.origin_country = origin_country
            band.origin_country_name = origin_country_name
            band.origin_city = origin_city
            band.formation_year = formation_year
            band.formation_decade = (formation_year // 10) * 10
            band.dissolution_year = dissolution_year
            band.is_active = is_active
            band.years_active = years_active
            band.genres = json.dumps(genres)
            band.primary_genre = primary_genre
            band.genre_cluster = genre_cluster
            band.musicbrainz_url = f"https://musicbrainz.org/artist/{mbid}"
            
            # Add Last.fm data if available
            if lastfm_data:
                band.listeners_count = lastfm_data.get('listeners', 0)
                band.play_count = lastfm_data.get('playcount', 0)
                band.popularity_score = self._calculate_popularity_score(lastfm_data)
                band.lastfm_url = lastfm_data.get('url')
            
            # Calculate longevity score
            band.longevity_score = self._calculate_longevity_score(band)
            
            # Determine cross-generational appeal (simplified)
            band.cross_generational_appeal = (
                band.years_active >= 20 and
                band.popularity_score and band.popularity_score > 50
            )
            
            # Save band
            if status == 'added':
                db.session.add(band)
            
            db.session.commit()
            
            # Perform linguistic analysis
            self._analyze_band_name(band)
            
            return status
            
        except Exception as e:
            logger.error(f"Error processing artist {artist_data.get('name', 'Unknown')}: {e}")
            db.session.rollback()
            return 'error'
    
    def _get_lastfm_data(self, band_name: str) -> Optional[Dict]:
        """Fetch additional data from Last.fm API.
        
        Args:
            band_name: Name of the band
            
        Returns:
            Dictionary with Last.fm data or None if not found
        """
        if not self.lastfm_api_key:
            return None
        
        try:
            params = {
                'method': 'artist.getinfo',
                'artist': band_name,
                'api_key': self.lastfm_api_key,
                'format': 'json'
            }
            
            response = requests.get(self.lastfm_base_url, params=params)
            time.sleep(self.lastfm_delay)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            artist = data.get('artist', {})
            
            if not artist:
                return None
            
            # Extract relevant data
            stats = artist.get('stats', {})
            tags = artist.get('tags', {}).get('tag', [])
            
            genres = []
            if isinstance(tags, list):
                genres = [tag.get('name', '') for tag in tags[:5]]  # Top 5 tags
            
            return {
                'listeners': int(stats.get('listeners', 0)),
                'playcount': int(stats.get('playcount', 0)),
                'genres': genres,
                'url': artist.get('url')
            }
            
        except Exception as e:
            logger.warning(f"Error fetching Last.fm data for {band_name}: {e}")
            return None
    
    def _calculate_popularity_score(self, lastfm_data: Dict) -> float:
        """Calculate normalized popularity score (0-100).
        
        Uses log scale for listeners and play count.
        
        Args:
            lastfm_data: Data from Last.fm
            
        Returns:
            Popularity score (0-100)
        """
        import math
        
        listeners = lastfm_data.get('listeners', 0)
        playcount = lastfm_data.get('playcount', 0)
        
        if listeners == 0:
            return 0.0
        
        # Log scale (1M listeners ≈ 90, 10K listeners ≈ 40)
        listener_score = min(100, (math.log10(listeners + 1) / 6.0) * 100)
        
        # Playcount as secondary factor
        playcount_score = 0
        if playcount > 0:
            playcount_score = min(100, (math.log10(playcount + 1) / 8.0) * 100)
        
        # Weighted average (listeners weighted more heavily)
        popularity = (listener_score * 0.7) + (playcount_score * 0.3)
        
        return round(popularity, 2)
    
    def _calculate_longevity_score(self, band: Band) -> float:
        """Calculate longevity score based on years active and current relevance.
        
        Args:
            band: Band object
            
        Returns:
            Longevity score (0-100)
        """
        if not band.years_active:
            return 0.0
        
        # Base score from years active (diminishing returns after 30 years)
        years_score = min(100, (band.years_active / 30.0) * 70)
        
        # Bonus for still being active
        active_bonus = 15 if band.is_active else 0
        
        # Bonus for having good popularity despite age
        popularity_bonus = 0
        if band.popularity_score and band.years_active > 20:
            popularity_bonus = min(15, band.popularity_score / 10.0)
        
        longevity = years_score + active_bonus + popularity_bonus
        
        return round(min(100, longevity), 2)
    
    def _classify_genre_cluster(self, genres: List[str]) -> str:
        """Classify genres into broader clusters.
        
        Args:
            genres: List of genre tags
            
        Returns:
            Genre cluster name
        """
        if not genres:
            return 'Unknown'
        
        genres_lower = [g.lower() for g in genres]
        
        # Define cluster keywords
        clusters = {
            'rock': ['rock', 'classic rock', 'alternative rock', 'indie rock', 'hard rock'],
            'metal': ['metal', 'heavy metal', 'death metal', 'black metal', 'doom metal', 'thrash'],
            'punk': ['punk', 'hardcore', 'post-punk', 'punk rock'],
            'pop': ['pop', 'pop rock', 'synth-pop', 'indie pop'],
            'electronic': ['electronic', 'techno', 'house', 'ambient', 'idm', 'edm'],
            'hip-hop': ['hip hop', 'hip-hop', 'rap'],
            'jazz': ['jazz', 'bebop', 'fusion'],
            'folk': ['folk', 'folk rock', 'americana'],
            'blues': ['blues', 'blues rock'],
            'progressive': ['progressive rock', 'prog rock', 'progressive metal', 'art rock'],
            'grunge': ['grunge', 'alternative'],
        }
        
        # Check each cluster
        for cluster, keywords in clusters.items():
            for genre in genres_lower:
                if any(keyword in genre for keyword in keywords):
                    return cluster
        
        return 'Other'
    
    def _analyze_band_name(self, band: Band) -> None:
        """Perform comprehensive linguistic analysis on band name.
        
        Args:
            band: Band object to analyze
        """
        try:
            name = band.name
            
            # Check if analysis already exists
            existing_analysis = BandAnalysis.query.filter_by(band_id=band.id).first()
            if existing_analysis:
                analysis = existing_analysis
            else:
                analysis = BandAnalysis(band_id=band.id)
            
            # Standard metrics from name analyzer
            name_metrics = self.name_analyzer.analyze_name(name)
            
            analysis.syllable_count = name_metrics.get('syllable_count', 0)
            analysis.character_length = name_metrics.get('character_length', 0)
            analysis.word_count = name_metrics.get('word_count', 0)
            analysis.phonetic_score = name_metrics.get('phonetic_score', 0)
            analysis.vowel_ratio = name_metrics.get('vowel_ratio', 0)
            analysis.memorability_score = name_metrics.get('memorability_score', 0)
            analysis.pronounceability_score = name_metrics.get('pronounceability_score', 0)
            analysis.uniqueness_score = name_metrics.get('uniqueness_score', 0)
            analysis.name_type = name_metrics.get('name_type', 'Unknown')
            
            # Phonosemantic analysis
            phonemic_results = self.phonemic_analyzer.analyze(name)
            analysis.harshness_score = phonemic_results.get('harshness_score', 0)
            analysis.softness_score = phonemic_results.get('softness_score', 0)
            analysis.phonosemantic_data = json.dumps(phonemic_results)
            
            # Semantic analysis
            semantic_results = self.semantic_analyzer.analyze(name)
            analysis.fantasy_score = semantic_results.get('fantasy_score', 0)
            analysis.power_connotation_score = semantic_results.get('power_score', 0)
            analysis.abstraction_score = semantic_results.get('abstraction_score', 0)
            analysis.literary_reference_score = semantic_results.get('literary_reference_score', 0)
            analysis.semantic_data = json.dumps(semantic_results)
            
            # Sound symbolism
            sound_symbolism_results = self.sound_symbolism_analyzer.analyze(name)
            analysis.sound_symbolism_data = json.dumps(sound_symbolism_results)
            
            # Prosodic analysis
            prosodic_results = self.prosodic_analyzer.analyze(name)
            analysis.prosodic_data = json.dumps(prosodic_results)
            
            # Temporal cohort
            if band.formation_decade:
                analysis.temporal_cohort = f"{band.formation_decade}s"
            
            # Geographic cluster (simplified for now)
            if band.origin_country:
                analysis.geographic_cluster = self._get_geographic_cluster(
                    band.origin_country,
                    band.origin_city
                )
            
            # Save analysis
            if not existing_analysis:
                db.session.add(analysis)
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error analyzing band name '{band.name}': {e}")
            db.session.rollback()
    
    def _get_geographic_cluster(self, country: str, city: Optional[str]) -> str:
        """Determine geographic cluster for a band.
        
        Args:
            country: Country code
            city: City name (optional)
            
        Returns:
            Geographic cluster identifier
        """
        # US regions
        if country == 'US':
            if city:
                city_lower = city.lower()
                # West Coast
                if any(c in city_lower for c in ['los angeles', 'san francisco', 'seattle', 'portland']):
                    return 'US_West'
                # NYC/Northeast
                elif any(c in city_lower for c in ['new york', 'boston', 'philadelphia']):
                    return 'US_Northeast'
                # South
                elif any(c in city_lower for c in ['nashville', 'austin', 'atlanta', 'miami']):
                    return 'US_South'
                # Midwest
                elif any(c in city_lower for c in ['chicago', 'detroit', 'cleveland']):
                    return 'US_Midwest'
            return 'US_Other'
        
        # UK regions
        elif country == 'GB':
            if city:
                city_lower = city.lower()
                if 'london' in city_lower:
                    return 'UK_London'
                elif 'manchester' in city_lower:
                    return 'UK_Manchester'
                elif 'liverpool' in city_lower:
                    return 'UK_Liverpool'
                elif 'birmingham' in city_lower:
                    return 'UK_Birmingham'
            return 'UK_Other'
        
        # Nordic countries
        elif country in ['SE', 'NO', 'FI', 'IS', 'DK']:
            return 'Nordic'
        
        # Other major regions
        elif country == 'CA':
            return 'Canada'
        elif country == 'AU':
            return 'Australia'
        elif country == 'DE':
            return 'Germany'
        elif country == 'FR':
            return 'France'
        elif country == 'IT':
            return 'Italy'
        elif country == 'JP':
            return 'Japan'
        elif country in ['MX', 'BR', 'AR']:
            return 'Latin_America'
        else:
            return 'Other'


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Note: Set Last.fm API key in core/config.py or pass as parameter
    collector = BandCollector()
    
    # Collect 100 bands per decade for testing (use 600+ for full collection)
    stats = collector.collect_stratified_sample(target_per_decade=100)
    
    print("\nCollection complete!")
    print(f"Total bands added: {stats['total_added']}")
    print(f"Total bands updated: {stats['total_updated']}")
    print(f"Total analyzed: {stats['total_analyzed']}")

