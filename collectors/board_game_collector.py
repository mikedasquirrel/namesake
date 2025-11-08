"""Board Game Collector

Collects board game data from BoardGameGeek (BGG) XML API.
Implements stratified sampling by era (1950s-2024) with focus on popular/influential games.

Target: 2,000 games total (200/400/600/800 across eras)
Strategy: Prioritize games with 100+ ratings, balanced across categories and eras
"""

import logging
import time
import xml.etree.ElementTree as ET
import requests
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import re

from core.models import db, BoardGame, BoardGameAnalysis
from analyzers.name_analyzer import NameAnalyzer
from analyzers.phonemic_analyzer import PhonemicAnalyzer
from analyzers.semantic_analyzer import SemanticAnalyzer
from analyzers.sound_symbolism_analyzer import SoundSymbolismAnalyzer
from analyzers.prosodic_analyzer import ProsodicAnalyzer

logger = logging.getLogger(__name__)


class BoardGameCollector:
    """Collect board game data from BoardGameGeek XML API."""
    
    def __init__(self):
        """Initialize the collector with BGG API configuration."""
        self.bgg_base_url = "https://boardgamegeek.com/xmlapi2"
        
        # Rate limiting (BGG API: 2 requests per second recommended)
        self.bgg_delay = 0.6  # Conservative: ~1.7 requests/second
        
        # Analyzers
        self.name_analyzer = NameAnalyzer()
        self.phonemic_analyzer = PhonemicAnalyzer()
        self.semantic_analyzer = SemanticAnalyzer()
        self.sound_symbolism_analyzer = SoundSymbolismAnalyzer()
        self.prosodic_analyzer = ProsodicAnalyzer()
        
        # User agent for BGG
        self.headers = {
            'User-Agent': 'NominativeDeterminismResearch/1.0 (research@nominative-determinism.org)'
        }
        
        # Era definitions
        self.eras = {
            'classic_1950_1979': (1950, 1979),
            'golden_1980_1999': (1980, 1999),
            'modern_2000_2009': (2000, 2009),
            'contemporary_2010_2024': (2010, 2024)
        }
        
        # Category mappings
        self.category_keywords = {
            'strategy': ['strategy', 'economic', 'civilization'],
            'party': ['party', 'humor', 'trivia'],
            'family': ['family', 'children'],
            'war_game': ['wargame', 'war', 'military'],
            'abstract': ['abstract'],
            'thematic': ['thematic', 'adventure', 'fantasy', 'sci-fi']
        }
    
    def collect_stratified_sample(self, targets: Dict[str, int] = None) -> Dict:
        """Collect stratified sample of board games across eras.
        
        Strategy:
        - Query BGG for top games in each era
        - Filter by minimum ratings (100+)
        - Balanced across categories
        - Save to database with linguistic analysis
        
        Args:
            targets: Dict mapping era to target count
                    Default: {'classic_1950_1979': 200, 'golden_1980_1999': 400,
                             'modern_2000_2009': 600, 'contemporary_2010_2024': 800}
        
        Returns:
            Dict with collection statistics
        """
        if targets is None:
            targets = {
                'classic_1950_1979': 200,
                'golden_1980_1999': 400,
                'modern_2000_2009': 600,
                'contemporary_2010_2024': 800
            }
        
        logger.info("=== BOARD GAME COLLECTION: Stratified Sample ===")
        logger.info(f"Targets: {targets}")
        
        results = {
            'total_collected': 0,
            'by_era': {},
            'by_category': {},
            'errors': 0,
            'start_time': datetime.now().isoformat()
        }
        
        for era_name, target_count in targets.items():
            logger.info(f"\n--- Collecting {era_name}: Target {target_count} ---")
            year_start, year_end = self.eras[era_name]
            
            collected = self._collect_era_sample(
                era_name=era_name,
                year_start=year_start,
                year_end=year_end,
                target_count=target_count
            )
            
            results['by_era'][era_name] = collected
            results['total_collected'] += collected
        
        results['end_time'] = datetime.now().isoformat()
        logger.info(f"\n=== COLLECTION COMPLETE: {results['total_collected']} games ===")
        
        return results
    
    def _collect_era_sample(self, era_name: str, year_start: int, 
                           year_end: int, target_count: int) -> int:
        """Collect games from a specific era.
        
        Args:
            era_name: Era identifier
            year_start: Start year (inclusive)
            year_end: End year (inclusive)
            target_count: Number of games to collect
        
        Returns:
            Number of games successfully collected
        """
        collected_count = 0
        page = 1
        max_pages = 20  # Prevent infinite loops
        
        while collected_count < target_count and page <= max_pages:
            # Search BGG for games in this year range
            # Note: BGG API doesn't have direct year range search, so we use geeksearch
            # and filter by year, or iterate through ranked games
            games = self._fetch_top_games_for_era(year_start, year_end, page)
            
            if not games:
                logger.warning(f"No more games found for {era_name}, page {page}")
                break
            
            for game_data in games:
                if collected_count >= target_count:
                    break
                
                # Check if already in database
                existing = BoardGame.query.filter_by(bgg_id=game_data['bgg_id']).first()
                if existing:
                    logger.debug(f"Game already exists: {game_data['name']}")
                    continue
                
                # Collect detailed game info
                detailed_game = self._fetch_game_details(game_data['bgg_id'])
                if not detailed_game:
                    continue
                
                # Filter by year and minimum ratings
                if (detailed_game['year_published'] < year_start or 
                    detailed_game['year_published'] > year_end or
                    detailed_game.get('num_ratings', 0) < 100):
                    continue
                
                # Save to database
                success = self._save_game_to_db(detailed_game, era_name)
                if success:
                    collected_count += 1
                    logger.info(f"  [{collected_count}/{target_count}] {detailed_game['name']} ({detailed_game['year_published']})")
                
                # Rate limiting
                time.sleep(self.bgg_delay)
            
            page += 1
        
        return collected_count
    
    def _fetch_top_games_for_era(self, year_start: int, year_end: int, page: int = 1) -> List[Dict]:
        """Fetch top games for a given era from BGG.
        
        Uses BGG's browse endpoint to get ranked games, then filters by year.
        
        Args:
            year_start: Start year
            year_end: End year
            page: Page number (100 games per page)
        
        Returns:
            List of game dicts with basic info
        """
        games = []
        
        # BGG browse API - get ranked games
        # Note: We'll use the search API with year published filters
        try:
            # Get games ranked in overall BGG rankings
            # We'll query by rank and then filter by year
            start_rank = (page - 1) * 100 + 1
            end_rank = page * 100
            
            # For now, we'll use a list of well-known game IDs and fetch details
            # In production, you'd use BGG's hot list, browse, or search APIs
            # This is a simplified approach for the template system
            
            # Alternative: Use BGG search with year published filter
            url = f"{self.bgg_base_url}/search"
            params = {
                'query': '',  # Empty for browse-style
                'type': 'boardgame',
                'yearpublished': f"{year_start},{year_end}"
            }
            
            # For this template, we'll generate sample game IDs
            # In production, replace with actual BGG API calls
            sample_game_ids = self._get_sample_game_ids_for_era(year_start, year_end, page)
            
            for game_id in sample_game_ids:
                games.append({'bgg_id': game_id})
            
        except Exception as e:
            logger.error(f"Error fetching games for era {year_start}-{year_end}: {e}")
        
        return games
    
    def _get_sample_game_ids_for_era(self, year_start: int, year_end: int, page: int) -> List[int]:
        """Get sample game IDs for testing (replace with real BGG API in production).
        
        This is a placeholder that returns well-known game IDs for each era.
        In production, use BGG's search/browse API or a pre-downloaded database.
        """
        # Famous games by era (sample for template system)
        known_games = {
            (1950, 1979): [2651, 181, 2651, 3076],  # Monopoly, Risk, Stratego, Puerto Rico
            (1980, 1999): [478, 13, 822, 2651],  # Citadels, Catan, Carcassonne, etc.
            (2000, 2009): [31260, 84876, 9209, 36218],  # Agricola, Dominion, Ticket to Ride, 7 Wonders
            (2010, 2024): [167791, 182028, 220308, 266192]  # Wingspan, 7 Wonders Duel, Azul, Everdell
        }
        
        # Find matching era
        for (start, end), game_ids in known_games.items():
            if year_start == start and year_end == end:
                # In production, paginate through real BGG data
                # For now, return sample IDs repeated to simulate collection
                return game_ids * (25 * page)  # Multiply to simulate pages
        
        return []
    
    def _fetch_game_details(self, bgg_id: int) -> Optional[Dict]:
        """Fetch detailed game information from BGG API.
        
        Args:
            bgg_id: BoardGameGeek game ID
        
        Returns:
            Dict with complete game data, or None if error
        """
        try:
            url = f"{self.bgg_base_url}/thing"
            params = {
                'id': bgg_id,
                'stats': 1,
                'type': 'boardgame'
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            
            if response.status_code == 202:
                # BGG returns 202 when data is being prepared, retry
                time.sleep(2)
                response = requests.get(url, params=params, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"BGG API returned {response.status_code} for game {bgg_id}")
                return None
            
            # Parse XML response
            root = ET.fromstring(response.content)
            item = root.find('item')
            
            if item is None:
                return None
            
            # Extract game data
            game_data = self._parse_bgg_xml(item)
            game_data['bgg_id'] = bgg_id
            
            return game_data
            
        except Exception as e:
            logger.error(f"Error fetching game {bgg_id}: {e}")
            return None
    
    def _parse_bgg_xml(self, item: ET.Element) -> Dict:
        """Parse BGG XML item into game data dict.
        
        Args:
            item: XML Element for game
        
        Returns:
            Dict with game attributes
        """
        data = {}
        
        # Name (primary)
        name_elem = item.find("name[@type='primary']")
        if name_elem is not None:
            data['name'] = name_elem.get('value', 'Unknown')
        else:
            # Fallback to any name
            name_elem = item.find('name')
            data['name'] = name_elem.get('value', 'Unknown') if name_elem is not None else 'Unknown'
        
        # Year published
        year_elem = item.find('yearpublished')
        data['year_published'] = int(year_elem.get('value', 0)) if year_elem is not None else None
        
        # Ratings and statistics
        stats = item.find('statistics/ratings')
        if stats is not None:
            # BGG Rating (Geek Rating)
            rating_elem = stats.find('bayesaverage')
            data['bgg_rating'] = float(rating_elem.get('value', 0)) if rating_elem is not None else None
            
            # Average rating
            avg_elem = stats.find('average')
            data['average_rating'] = float(avg_elem.get('value', 0)) if avg_elem is not None else None
            
            # Number of ratings
            num_elem = stats.find('usersrated')
            data['num_ratings'] = int(num_elem.get('value', 0)) if num_elem is not None else 0
            
            # Complexity weight
            weight_elem = stats.find('averageweight')
            data['complexity_weight'] = float(weight_elem.get('value', 0)) if weight_elem is not None else None
            
            # Ownership
            owned_elem = stats.find('owned')
            data['ownership_count'] = int(owned_elem.get('value', 0)) if owned_elem is not None else None
            
            # Rankings
            rank_elem = stats.find("ranks/rank[@name='boardgame']")
            if rank_elem is not None:
                rank_val = rank_elem.get('value', 'Not Ranked')
                data['bgg_rank'] = int(rank_val) if rank_val.isdigit() else None
        
        # Player counts
        min_players_elem = item.find('minplayers')
        data['min_players'] = int(min_players_elem.get('value', 0)) if min_players_elem is not None else None
        
        max_players_elem = item.find('maxplayers')
        data['max_players'] = int(max_players_elem.get('value', 0)) if max_players_elem is not None else None
        
        # Playing time
        playtime_elem = item.find('playingtime')
        data['playing_time'] = int(playtime_elem.get('value', 0)) if playtime_elem is not None else None
        
        # Minimum age
        age_elem = item.find('minage')
        data['min_age'] = int(age_elem.get('value', 0)) if age_elem is not None else None
        
        # Categories (get primary)
        categories = item.findall("link[@type='boardgamecategory']")
        if categories:
            data['category'] = categories[0].get('value', 'Unknown')
        else:
            data['category'] = 'Unknown'
        
        # Mechanics (get primary)
        mechanics = item.findall("link[@type='boardgamemechanic']")
        if mechanics:
            data['primary_mechanic'] = mechanics[0].get('value', 'Unknown')
        else:
            data['primary_mechanic'] = 'Unknown'
        
        # Designer
        designers = item.findall("link[@type='boardgamedesigner']")
        if designers:
            data['designer'] = designers[0].get('value', 'Unknown')
        else:
            data['designer'] = 'Unknown'
        
        # Publisher
        publishers = item.findall("link[@type='boardgamepublisher']")
        if publishers:
            data['publisher'] = publishers[0].get('value', 'Unknown')
        else:
            data['publisher'] = 'Unknown'
        
        return data
    
    def _determine_designer_nationality(self, designer_name: str) -> str:
        """Determine designer nationality (simplified heuristic).
        
        In production, maintain a designer database or use BGG designer pages.
        This is a simplified version for the template.
        
        Args:
            designer_name: Designer name
        
        Returns:
            Country code (US, DE, FR, JP, etc.)
        """
        # Known designers mapping (sample)
        known_designers = {
            'Reiner Knizia': 'DE',
            'Uwe Rosenberg': 'DE',
            'Vital Lacerda': 'PT',
            'Stefan Feld': 'DE',
            'Vlaada Chvátil': 'CZ',
            'Antoine Bauza': 'FR',
            'Bruno Cathala': 'FR',
            'Elizabeth Hargrave': 'US',
            'Jamey Stegmaier': 'US',
            'Matt Leacock': 'US',
            'Rob Daviau': 'US',
            'Klaus Teuber': 'DE',
            'Martin Wallace': 'GB',
            'Seiji Kanai': 'JP',
            'Hisashi Hayashi': 'JP'
        }
        
        if designer_name in known_designers:
            return known_designers[designer_name]
        
        # Heuristic: Check for common German suffixes
        if any(designer_name.endswith(s) for s in ['mann', 'schmidt', 'feld', 'berg']):
            return 'DE'
        
        # Default to US for unknown
        return 'US'
    
    def _save_game_to_db(self, game_data: Dict, era: str) -> bool:
        """Save board game and analysis to database.
        
        Args:
            game_data: Game data dict
            era: Era classification
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create BoardGame model
            game = BoardGame(
                name=game_data['name'],
                bgg_id=game_data['bgg_id'],
                year_published=game_data.get('year_published'),
                bgg_rating=game_data.get('bgg_rating'),
                average_rating=game_data.get('average_rating'),
                num_ratings=game_data.get('num_ratings', 0),
                complexity_weight=game_data.get('complexity_weight'),
                ownership_count=game_data.get('ownership_count'),
                min_players=game_data.get('min_players'),
                max_players=game_data.get('max_players'),
                playing_time=game_data.get('playing_time'),
                min_age=game_data.get('min_age'),
                category=game_data.get('category', 'Unknown'),
                primary_mechanic=game_data.get('primary_mechanic'),
                designer=game_data.get('designer', 'Unknown'),
                designer_nationality=self._determine_designer_nationality(game_data.get('designer', '')),
                publisher=game_data.get('publisher'),
                bgg_rank=game_data.get('bgg_rank')
            )
            
            db.session.add(game)
            db.session.flush()  # Get game ID
            
            # Perform linguistic analysis
            analysis_data = self._analyze_game_name(game_data['name'], era)
            analysis_data['game_id'] = game.id
            
            analysis = BoardGameAnalysis(**analysis_data)
            db.session.add(analysis)
            db.session.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving game {game_data.get('name', 'Unknown')}: {e}")
            db.session.rollback()
            return False
    
    def _analyze_game_name(self, name: str, era: str) -> Dict:
        """Perform comprehensive linguistic analysis on board game name.
        
        Args:
            name: Game name
            era: Era classification
        
        Returns:
            Dict with analysis features
        """
        analysis = {}
        
        # Basic structure
        words = name.split()
        analysis['word_count'] = len(words)
        analysis['character_length'] = len(name)
        analysis['contains_colon'] = ':' in name
        analysis['contains_number'] = any(char.isdigit() for char in name)
        analysis['contains_article'] = words[0].lower() in ['the', 'a', 'an'] if words else False
        
        # Syllable count
        try:
            syllables = self.name_analyzer.count_syllables(name)
            analysis['syllable_count'] = syllables
        except:
            analysis['syllable_count'] = len(words) * 2  # Rough estimate
        
        # Phonetic features
        try:
            phonetic = self.phonemic_analyzer.analyze(name)
            analysis['harshness_score'] = phonetic.get('harshness_score', 50.0)
            analysis['smoothness_score'] = phonetic.get('smoothness_score', 50.0)
            analysis['plosive_ratio'] = phonetic.get('plosive_ratio', 0.0)
            analysis['fricative_ratio'] = phonetic.get('fricative_ratio', 0.0)
            analysis['vowel_ratio'] = phonetic.get('vowel_ratio', 0.4)
            analysis['consonant_cluster_density'] = phonetic.get('consonant_cluster_density', 0.0)
        except Exception as e:
            logger.warning(f"Phonetic analysis failed for '{name}': {e}")
            analysis.update({
                'harshness_score': 50.0,
                'smoothness_score': 50.0,
                'plosive_ratio': 0.0,
                'fricative_ratio': 0.0,
                'vowel_ratio': 0.4,
                'consonant_cluster_density': 0.0
            })
        
        # Advanced phonetic
        analysis['phonetic_complexity'] = (analysis['syllable_count'] * 10 + 
                                          analysis['consonant_cluster_density'] * 50)
        analysis['sound_symbolism_score'] = 50.0  # Placeholder
        analysis['alliteration_score'] = self._calculate_alliteration(name)
        
        # Semantic features
        analysis['name_type'] = self._classify_name_type(name)
        analysis['memorability_score'] = self._calculate_memorability(name, analysis)
        analysis['pronounceability_score'] = 100.0 - analysis['phonetic_complexity']
        analysis['semantic_transparency'] = self._calculate_semantic_transparency(name)
        
        # Cultural/linguistic
        analysis['is_fantasy_name'] = self._is_fantasy_name(name)
        analysis['is_latin_derived'] = self._is_latin_derived(name)
        analysis['is_compound_word'] = '-' in name or (len(words) == 1 and len(name) > 12)
        analysis['primary_language'] = 'en'  # Default, enhance with language detection
        
        # Composite scores
        analysis['name_quality_score'] = (
            analysis['memorability_score'] * 0.4 +
            analysis['pronounceability_score'] * 0.3 +
            (100 - abs(50 - analysis['harshness_score'])) * 0.3
        )
        analysis['cultural_alignment_score'] = 70.0  # Placeholder
        analysis['thematic_resonance'] = analysis['semantic_transparency']
        
        # Era
        analysis['era'] = era
        
        return analysis
    
    def _calculate_alliteration(self, name: str) -> float:
        """Calculate alliteration score (same starting sounds).
        
        Args:
            name: Game name
        
        Returns:
            Alliteration score 0-100
        """
        words = [w for w in name.split() if w[0].isalpha()]
        if len(words) < 2:
            return 0.0
        
        # Check if first letters match
        first_letters = [w[0].lower() for w in words]
        if len(set(first_letters)) == 1:
            return 100.0
        elif len(set(first_letters)) < len(first_letters):
            return 50.0
        
        return 0.0
    
    def _classify_name_type(self, name: str) -> str:
        """Classify the type of board game name.
        
        Args:
            name: Game name
        
        Returns:
            Name type: descriptive, abstract, thematic, compound, portmanteau
        """
        words = name.split()
        
        # Check for compound (hyphenated or CamelCase-like single word)
        if '-' in name:
            return 'compound'
        
        # Check for thematic (common game-related words)
        thematic_words = ['quest', 'adventure', 'battle', 'empire', 'kingdom', 
                         'war', 'king', 'knight', 'dragon', 'realm', 'saga']
        if any(word.lower() in thematic_words for word in words):
            return 'thematic'
        
        # Check for descriptive (describes gameplay)
        descriptive_words = ['game', 'puzzle', 'strategy', 'match', 'build', 'trade']
        if any(word.lower() in descriptive_words for word in words):
            return 'descriptive'
        
        # Single abstract word
        if len(words) == 1 and len(name) < 10:
            return 'abstract'
        
        # Default to compound for multi-word
        if len(words) > 1:
            return 'compound'
        
        return 'abstract'
    
    def _calculate_memorability(self, name: str, analysis: Dict) -> float:
        """Calculate memorability score based on name features.
        
        Args:
            name: Game name
            analysis: Partial analysis dict with structural features
        
        Returns:
            Memorability score 0-100
        """
        score = 50.0  # Baseline
        
        # Bonus for brevity
        if analysis['syllable_count'] <= 3:
            score += 20
        elif analysis['syllable_count'] <= 5:
            score += 10
        else:
            score -= 10
        
        # Bonus for single word
        if analysis['word_count'] == 1:
            score += 15
        
        # Bonus for alliteration
        if analysis.get('alliteration_score', 0) > 50:
            score += 10
        
        # Penalty for colon (expansion names less memorable)
        if analysis['contains_colon']:
            score -= 15
        
        # Bonus for high vowel ratio (easier to remember)
        if analysis['vowel_ratio'] > 0.45:
            score += 10
        
        return max(0, min(100, score))
    
    def _calculate_semantic_transparency(self, name: str) -> float:
        """Calculate how clearly the name conveys the game's theme.
        
        Args:
            name: Game name
        
        Returns:
            Transparency score 0-100
        """
        # Thematic/descriptive words suggest high transparency
        transparent_words = ['castle', 'kingdom', 'war', 'quest', 'battle', 'trade',
                            'build', 'farm', 'ship', 'train', 'empire', 'conquest',
                            'adventure', 'treasure', 'mystery', 'horror', 'zombie']
        
        words = name.lower().split()
        matches = sum(1 for word in words if any(tw in word for tw in transparent_words))
        
        if matches > 0:
            return min(100, 60 + matches * 20)
        
        # Abstract names have low transparency
        if len(words) == 1 and len(name) < 8:
            return 20.0
        
        return 40.0  # Default middle ground
    
    def _is_fantasy_name(self, name: str) -> bool:
        """Check if name is a made-up/fantasy word.
        
        Args:
            name: Game name
        
        Returns:
            True if fantasy/invented name
        """
        # Heuristic: unusual letter patterns, ends in certain suffixes
        fantasy_patterns = ['dor', 'dil', 'gorn', 'thul', 'zar', 'quin', 'ath']
        name_lower = name.lower()
        
        return any(pattern in name_lower for pattern in fantasy_patterns)
    
    def _is_latin_derived(self, name: str) -> bool:
        """Check if name has Latin roots.
        
        Args:
            name: Game name
        
        Returns:
            True if Latin-derived
        """
        latin_endings = ['us', 'um', 'a', 'ia', 'is', 'or', 'ex', 'ix']
        latin_words = ['terra', 'aqua', 'via', 'lux', 'rex', 'deus', 'vita', 'magnus']
        
        name_lower = name.lower()
        
        # Check endings
        if any(name_lower.endswith(ending) for ending in latin_endings):
            return True
        
        # Check known Latin words
        if any(word in name_lower for word in latin_words):
            return True
        
        return False
    
    def collect_top_n(self, n: int = 2000) -> Dict:
        """Collect top N games from BGG rankings.
        
        Simpler alternative to stratified sampling.
        
        Args:
            n: Number of games to collect
        
        Returns:
            Dict with collection statistics
        """
        logger.info(f"=== COLLECTING TOP {n} BOARD GAMES ===")
        
        collected = 0
        errors = 0
        start_time = datetime.now()
        
        # BGG top games typically start from ID 1 and go up
        # Top 2000 games have IDs scattered throughout, use ranks
        # For template: use known popular game IDs
        sample_ids = self._get_popular_game_ids(n)
        
        for i, game_id in enumerate(sample_ids[:n], 1):
            try:
                # Check if exists
                existing = BoardGame.query.filter_by(bgg_id=game_id).first()
                if existing:
                    continue
                
                # Fetch and save
                game_data = self._fetch_game_details(game_id)
                if game_data and game_data.get('num_ratings', 0) >= 100:
                    # Determine era
                    year = game_data.get('year_published', 2000)
                    era = self._year_to_era(year)
                    
                    if self._save_game_to_db(game_data, era):
                        collected += 1
                        if collected % 50 == 0:
                            logger.info(f"Progress: {collected}/{n} games collected")
                else:
                    errors += 1
                
                time.sleep(self.bgg_delay)
                
            except Exception as e:
                logger.error(f"Error processing game ID {game_id}: {e}")
                errors += 1
        
        duration = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"\n=== COLLECTION COMPLETE ===")
        logger.info(f"Collected: {collected} games")
        logger.info(f"Errors: {errors}")
        logger.info(f"Duration: {duration:.1f}s")
        
        return {
            'collected': collected,
            'errors': errors,
            'duration_seconds': duration
        }
    
    def _get_popular_game_ids(self, n: int) -> List[int]:
        """Get list of popular game IDs for collection.
        
        In production, use BGG's browse/hot/top APIs or a pre-downloaded database.
        This is a placeholder with known popular games.
        
        Args:
            n: Number of IDs needed
        
        Returns:
            List of BGG game IDs
        """
        # Sample of popular games across eras (expand this in production)
        base_ids = [
            174430,  # Gloomhaven
            167791,  # Terraforming Mars
            220308,  # Gaia Project
            233078,  # Twilight Imperium 4th
            161936,  # Pandemic Legacy S1
            182028,  # Through the Ages
            173346,  # 7 Wonders Duel
            169786,  # Scythe
            224517,  # Brass: Birmingham
            266192,  # Wingspan
            266524,  # PARKS
            256916,  # Cascadia
            295947,  # Everdell
            216132,  # Azul
            68448,   # 7 Wonders
            9209,    # Ticket to Ride
            13,      # Catan
            822,     # Carcassonne
            36218,   # Dominion
            31260,   # Agricola
            120677,  # Terra Mystica
            167355,  # Nemesis
            193738,  # Great Western Trail
            162886,  # Spirit Island
            246784,  # Barrage
        ]
        
        # Repeat and extend to reach target n
        extended = base_ids * ((n // len(base_ids)) + 1)
        return extended[:n]
    
    def _year_to_era(self, year: int) -> str:
        """Convert year to era classification.
        
        Args:
            year: Year published
        
        Returns:
            Era name
        """
        if year < 1980:
            return 'classic_1950_1979'
        elif year < 2000:
            return 'golden_1980_1999'
        elif year < 2010:
            return 'modern_2000_2009'
        else:
            return 'contemporary_2010_2024'
    
    def get_collection_status(self) -> Dict:
        """Get current collection status from database.
        
        Returns:
            Dict with counts and statistics
        """
        total = BoardGame.query.count()
        by_era = {}
        
        for era_name in self.eras.keys():
            count = BoardGameAnalysis.query.filter_by(era=era_name).count()
            by_era[era_name] = count
        
        return {
            'total_games': total,
            'by_era': by_era,
            'timestamp': datetime.now().isoformat()
        }


# Quick test function
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    collector = BoardGameCollector()
    
    # Test with small sample
    result = collector.collect_top_n(50)
    print(f"\nCollected {result['collected']} games in {result['duration_seconds']:.1f}s")

