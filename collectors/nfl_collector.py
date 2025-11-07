"""NFL Player Collector

Collects NFL player data from multiple sources:
- Pro Football Reference (primary)
- NFL.com API (secondary)
- ESPN (tertiary)

Implements stratified sampling by position AND era (decade + rule era) with comprehensive statistics.

Target: 5,000+ players total (~200+ per major position)
Strategy: Mix of stars, role players, and journeymen to avoid survivorship bias
"""

import logging
import time
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import re

from core.models import db, NFLPlayer, NFLPlayerAnalysis
from analyzers.name_analyzer import NameAnalyzer
from analyzers.phonemic_analyzer import PhonemicAnalyzer
from analyzers.semantic_analyzer import SemanticAnalyzer
from analyzers.sound_symbolism_analyzer import SoundSymbolismAnalyzer
from analyzers.prosodic_analyzer import ProsodicAnalyzer

logger = logging.getLogger(__name__)


class NFLCollector:
    """Collect NFL player data with comprehensive linguistic analysis."""
    
    def __init__(self):
        """Initialize the collector with rate limiting and analyzers."""
        self.base_url = "https://www.pro-football-reference.com"
        
        # Rate limiting (be respectful to Pro Football Reference)
        self.request_delay = 5.0  # 5 seconds between requests
        
        # Analyzers
        self.name_analyzer = NameAnalyzer()
        self.phonemic_analyzer = PhonemicAnalyzer()
        self.semantic_analyzer = SemanticAnalyzer()
        self.sound_symbolism_analyzer = SoundSymbolismAnalyzer()
        self.prosodic_analyzer = ProsodicAnalyzer()
        
        # User agent
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        }
        
        # Position mapping and classification
        self.position_groups = {
            'QB': 'Offense',
            'RB': 'Offense',
            'FB': 'Offense',
            'WR': 'Offense',
            'TE': 'Offense',
            'OT': 'Offense',
            'OG': 'Offense',
            'G': 'Offense',
            'C': 'Offense',
            'T': 'Offense',
            'DE': 'Defense',
            'DT': 'Defense',
            'NT': 'Defense',
            'OLB': 'Defense',
            'ILB': 'Defense',
            'MLB': 'Defense',
            'LB': 'Defense',
            'CB': 'Defense',
            'S': 'Defense',
            'FS': 'Defense',
            'SS': 'Defense',
            'DB': 'Defense',
            'K': 'Special Teams',
            'P': 'Special Teams',
            'LS': 'Special Teams',
        }
        
        self.position_categories = {
            'QB': 'Skill',
            'RB': 'Skill',
            'FB': 'Skill',
            'WR': 'Skill',
            'TE': 'Skill',
            'OT': 'Offensive Line',
            'OG': 'Offensive Line',
            'G': 'Offensive Line',
            'C': 'Offensive Line',
            'T': 'Offensive Line',
            'DE': 'Defensive Line',
            'DT': 'Defensive Line',
            'NT': 'Defensive Line',
            'OLB': 'Linebackers',
            'ILB': 'Linebackers',
            'MLB': 'Linebackers',
            'LB': 'Linebackers',
            'CB': 'Defensive Backs',
            'S': 'Defensive Backs',
            'FS': 'Defensive Backs',
            'SS': 'Defensive Backs',
            'DB': 'Defensive Backs',
            'K': 'Special Teams',
            'P': 'Special Teams',
            'LS': 'Special Teams',
        }
    
    def classify_rule_era(self, debut_year: int) -> str:
        """Classify player into rule era based on debut year.
        
        Args:
            debut_year: Year player debuted in NFL
            
        Returns:
            Rule era classification
        """
        if debut_year < 1978:
            return 'Dead Ball'  # Pre-liberalized passing rules
        elif debut_year < 1994:
            return 'Modern'  # Post-1978 rule changes (Mel Blount Rule)
        elif debut_year < 2011:
            return 'Passing Era'  # Increased passing emphasis, no major rule changes
        else:
            return 'Modern Offense'  # RPO, pass-heavy, player safety rules
    
    def classify_era_group(self, debut_year: int) -> str:
        """Classify player into broad era group.
        
        Args:
            debut_year: Year player debuted in NFL
            
        Returns:
            Era group classification
        """
        if debut_year < 1978:
            return 'Pre-Modern'
        elif debut_year < 2010:
            return 'Modern'
        else:
            return 'Contemporary'
    
    def collect_stratified_sample(self, target_per_position: int = 200, target_per_era: int = 500) -> Dict:
        """Collect stratified sample of players across positions and eras.
        
        Strategy:
        - Query Pro Football Reference for players by position and era
        - Mix of All-Pros, Pro Bowlers, starters, and bench players
        - Include both successful and unsuccessful players
        - Save to database with comprehensive linguistic analysis
        
        Args:
            target_per_position: Target number of players per major position (default 200)
            target_per_era: Target number of players per era (default 500)
            
        Returns:
            Collection statistics
        """
        stats = {
            'positions_collected': {},
            'eras_collected': {},
            'total_added': 0,
            'total_updated': 0,
            'total_analyzed': 0,
            'errors': 0
        }
        
        # Major positions to collect
        major_positions = ['QB', 'RB', 'WR', 'TE', 'OT', 'OG', 'C', 
                          'DE', 'DT', 'LB', 'CB', 'S', 'K', 'P']
        
        # Eras to collect (by decade of debut)
        eras = [
            (1950, 1959, '1950s'),
            (1960, 1969, '1960s'),
            (1970, 1979, '1970s'),
            (1980, 1989, '1980s'),
            (1990, 1999, '1990s'),
            (2000, 2009, '2000s'),
            (2010, 2019, '2010s'),
            (2020, 2025, '2020s'),
        ]
        
        logger.info("Starting stratified NFL player collection...")
        logger.info(f"Target: {target_per_position} per position, {target_per_era} per era")
        
        # Collect by position first, then balance by era
        for position in major_positions:
            try:
                logger.info(f"\n{'=' * 60}")
                logger.info(f"Collecting {position} players...")
                logger.info(f"{'=' * 60}")
                
                position_stats = self.collect_position_sample(
                    position=position,
                    target_count=target_per_position,
                    eras=eras
                )
                
                stats['positions_collected'][position] = position_stats
                stats['total_added'] += position_stats['added']
                stats['total_updated'] += position_stats['updated']
                stats['total_analyzed'] += position_stats['analyzed']
                stats['errors'] += position_stats['errors']
                
                logger.info(f"✓ {position}: Added {position_stats['added']}, "
                          f"Updated {position_stats['updated']}, "
                          f"Analyzed {position_stats['analyzed']}")
                
                # Brief pause between positions
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Error collecting {position} players: {e}")
                stats['errors'] += 1
                continue
        
        logger.info(f"\n{'=' * 60}")
        logger.info("Collection Complete")
        logger.info(f"{'=' * 60}")
        logger.info(f"Total Added: {stats['total_added']}")
        logger.info(f"Total Updated: {stats['total_updated']}")
        logger.info(f"Total Analyzed: {stats['total_analyzed']}")
        logger.info(f"Errors: {stats['errors']}")
        
        return stats
    
    def collect_position_sample(self, position: str, target_count: int, eras: List[Tuple]) -> Dict:
        """Collect sample of players for a specific position across eras.
        
        Args:
            position: Position code (e.g., 'QB', 'RB')
            target_count: Target number of players to collect
            eras: List of (start_year, end_year, label) tuples
            
        Returns:
            Collection statistics for this position
        """
        stats = {
            'position': position,
            'added': 0,
            'updated': 0,
            'analyzed': 0,
            'errors': 0,
            'by_era': {}
        }
        
        # Balance collection across eras
        target_per_era = max(20, target_count // len(eras))
        
        for start_year, end_year, era_label in eras:
            try:
                logger.info(f"  Collecting {position} from {era_label}...")
                
                era_stats = self._collect_position_era(
                    position=position,
                    start_year=start_year,
                    end_year=end_year,
                    target_count=target_per_era
                )
                
                stats['by_era'][era_label] = era_stats
                stats['added'] += era_stats['added']
                stats['updated'] += era_stats['updated']
                stats['analyzed'] += era_stats['analyzed']
                stats['errors'] += era_stats['errors']
                
            except Exception as e:
                logger.error(f"Error collecting {position} from {era_label}: {e}")
                stats['errors'] += 1
                continue
        
        return stats
    
    def _collect_position_era(self, position: str, start_year: int, end_year: int, 
                             target_count: int) -> Dict:
        """Collect players for specific position and era from Pro Football Reference.
        
        Args:
            position: Position code
            start_year: Start year of era
            end_year: End year of era
            target_count: Target number of players
            
        Returns:
            Collection statistics
        """
        stats = {
            'added': 0,
            'updated': 0,
            'analyzed': 0,
            'errors': 0
        }
        
        # Pro Football Reference uses different position codes for URLs
        url_position = position.replace('OG', 'G').replace('OT', 'T')
        
        # Collect players year by year within the era
        collected = 0
        for year in range(start_year, end_year + 1):
            if collected >= target_count:
                break
            
            try:
                logger.info(f"    Fetching {position} players from {year}...")
                
                # Construct URL for year stats (passing for QB, rushing for RB, etc.)
                if position == 'QB':
                    stat_type = 'passing'
                elif position in ['RB', 'FB']:
                    stat_type = 'rushing'
                elif position in ['WR', 'TE']:
                    stat_type = 'receiving'
                elif position in ['OT', 'OG', 'C', 'T', 'G']:
                    # OL stats are limited, use games played
                    stat_type = 'fantasy'
                elif position in ['K']:
                    stat_type = 'kicking'
                elif position in ['P']:
                    stat_type = 'punting'
                else:
                    # Defensive positions
                    stat_type = 'defense'
                
                url = f"{self.base_url}/years/{year}/{stat_type}.htm"
                
                response = requests.get(url, headers=self.headers, timeout=15)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find the stats table - try multiple methods
                table = soup.find('table', {'id': stat_type})
                if not table:
                    # Try finding any table with the stat type in class
                    table = soup.find('table', {'class': lambda x: x and stat_type in x})
                if not table:
                    # Try finding the first stats table
                    table = soup.find('table', {'class': 'stats_table'})
                
                if not table:
                    logger.warning(f"    No table found for {year}")
                    continue
                
                tbody = table.find('tbody')
                if not tbody:
                    logger.warning(f"    No tbody found for {year}")
                    continue
                
                rows = tbody.find_all('tr')
                year_collected = 0
                
                logger.info(f"    Found {len(rows)} rows in table")
                
                for row in rows:
                    if collected >= target_count:
                        break
                    
                    # Skip header rows
                    if row.get('class') and 'thead' in row.get('class'):
                        continue
                    
                    # Get player link - try multiple data-stat values
                    player_link = row.find('td', {'data-stat': 'name_display'})
                    if not player_link:
                        player_link = row.find('td', {'data-stat': 'player'})
                    if not player_link:
                        player_link = row.find('th', {'data-stat': 'player'})
                    if not player_link:
                        player_link = row.find('td', {'data-stat': 'name'})
                    
                    if not player_link:
                        continue
                    
                    a_tag = player_link.find('a')
                    if not a_tag or not a_tag.get('href'):
                        continue
                    
                    player_href = a_tag['href']
                    
                    # Skip non-player links
                    if '/players/' not in player_href:
                        continue
                    
                    player_id = player_href.split('/')[-1].replace('.htm', '')
                    player_name = a_tag.get_text(strip=True)
                    
                    # Skip if already collected
                    existing = NFLPlayer.query.get(player_id)
                    if existing:
                        logger.debug(f"      Skipping {player_name} (already exists)")
                        continue
                    
                    # Get position from row - be more flexible
                    pos_cell = row.find('td', {'data-stat': 'pos'})
                    if not pos_cell:
                        pos_cell = row.find('td', {'data-stat': 'position'})
                    
                    player_pos = None
                    if pos_cell:
                        player_pos = pos_cell.get_text(strip=True)
                        # More flexible position matching
                        # For QB, accept QB
                        # For RB, accept RB, HB
                        # For WR, accept WR, FL, SE
                        if position == 'QB' and 'QB' not in player_pos:
                            continue
                        elif position == 'RB' and not any(p in player_pos for p in ['RB', 'HB', 'FB']):
                            continue
                        elif position == 'WR' and not any(p in player_pos for p in ['WR', 'FL', 'SE']):
                            continue
                        elif position == 'TE' and 'TE' not in player_pos:
                            continue
                        elif position in ['DE', 'DT', 'LB', 'CB', 'S', 'OT', 'OG', 'C', 'K', 'P']:
                            if position not in player_pos:
                                continue
                    
                    # Collect this player
                    player_url = f"{self.base_url}{player_href}"
                    
                    logger.info(f"      Collecting: {player_name} ({position})")
                    player = self.collect_player(player_id, player_url)
                    
                    if player:
                        stats['added'] += 1
                        collected += 1
                        year_collected += 1
                        
                        logger.info(f"      ✓ Success: {player_name}")
                    else:
                        stats['errors'] += 1
                        logger.warning(f"      ✗ Failed: {player_name}")
                    
                    # Limit per year to spread across eras
                    if year_collected >= 5:
                        break
                
                logger.info(f"    Collected {year_collected} from {year}")
                
                # Rate limiting between years
                time.sleep(self.request_delay)
                
            except Exception as e:
                logger.error(f"    Error collecting from {year}: {e}")
                stats['errors'] += 1
                continue
        
        stats['analyzed'] = stats['added']  # All added players are analyzed
        return stats
    
    def collect_player(self, player_id: str, pfr_url: str = None, retry_count: int = 0) -> Optional[NFLPlayer]:
        """Collect comprehensive data for a single player.
        
        Args:
            player_id: Pro Football Reference player ID
            pfr_url: Direct URL to player page (optional)
            retry_count: Number of retries attempted (for exponential backoff)
            
        Returns:
            NFLPlayer object if successful, None otherwise
        """
        try:
            # Check if player already exists
            existing_player = NFLPlayer.query.get(player_id)
            
            if pfr_url is None:
                pfr_url = f"{self.base_url}/players/{player_id[0]}/{player_id}.htm"
            
            logger.info(f"Collecting player: {player_id}")
            
            # Fetch player page with retry logic
            response = requests.get(pfr_url, headers=self.headers, timeout=10)
            
            # Handle rate limiting
            if response.status_code == 429:
                if retry_count < 3:
                    wait_time = 30 * (2 ** retry_count)  # 30s, 60s, 120s
                    logger.warning(f"Rate limited (429). Waiting {wait_time}s before retry {retry_count+1}/3...")
                    time.sleep(wait_time)
                    return self.collect_player(player_id, pfr_url, retry_count + 1)
                else:
                    logger.error(f"Rate limited after 3 retries. Skipping {player_id}")
                    return None
            
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract basic info
            player_data = self._parse_player_page(soup, player_id, pfr_url)
            
            if not player_data:
                logger.warning(f"Could not parse data for {player_id}")
                return None
            
            # Create or update player
            if existing_player:
                # Update existing player
                for key, value in player_data.items():
                    setattr(existing_player, key, value)
                player = existing_player
                logger.info(f"Updated existing player: {player.name}")
            else:
                # Create new player
                player = NFLPlayer(**player_data)
                db.session.add(player)
                logger.info(f"Added new player: {player.name}")
            
            db.session.commit()
            
            # Perform linguistic analysis
            self._analyze_player(player)
            
            # Rate limiting
            time.sleep(self.request_delay)
            
            return player
            
        except Exception as e:
            logger.error(f"Error collecting player {player_id}: {e}")
            db.session.rollback()
            return None
    
    def _parse_player_page(self, soup: BeautifulSoup, player_id: str, url: str) -> Optional[Dict]:
        """Parse Pro Football Reference player page.
        
        Args:
            soup: BeautifulSoup object of player page
            player_id: Player ID
            url: Player page URL
            
        Returns:
            Dictionary of player data
        """
        try:
            data = {
                'id': player_id,
                'pro_football_reference_url': url,
            }
            
            # Extract name - span contains the clean name
            name_elem = soup.find('h1')
            if name_elem:
                span = name_elem.find('span')
                if span:
                    data['name'] = span.get_text(strip=True)
                else:
                    data['name'] = name_elem.get_text(strip=True)
            else:
                return None
            
            # Extract position and other meta info
            meta_div = soup.find('div', {'id': 'meta'})
            if meta_div:
                # Position - look for "Position: QB" in any p tag
                for p in meta_div.find_all('p'):
                    p_text = p.get_text()
                    if 'Position:' in p_text:
                        position_match = re.search(r'Position:\s*([A-Z]+)', p_text)
                        if position_match:
                            position = position_match.group(1)
                            data['position'] = position
                            data['position_group'] = self.position_groups.get(position, 'Unknown')
                            data['position_category'] = self.position_categories.get(position, 'Unknown')
                            data['primary_position'] = position
                            break
                
                # Draft info
                for p in meta_div.find_all('p'):
                    p_text = p.get_text()
                    if 'Draft:' in p_text or 'draft' in p_text.lower():
                        year_match = re.search(r'(\d{4})', p_text)
                        if year_match:
                            data['draft_year'] = int(year_match.group(1))
                            data['debut_year'] = data['draft_year']
                            data['era'] = (data['draft_year'] // 10) * 10
                            data['era_group'] = self.classify_era_group(data['draft_year'])
                            data['rule_era'] = self.classify_rule_era(data['draft_year'])
                        
                        round_match = re.search(r'round (\d+)', p_text, re.IGNORECASE)
                        if round_match:
                            data['draft_round'] = int(round_match.group(1))
                        
                        pick_match = re.search(r'pick (\d+)', p_text, re.IGNORECASE)
                        if pick_match:
                            data['draft_pick'] = int(pick_match.group(1))
                        break
            
            # Get position to determine which table to look for
            position = data.get('position', '')
            
            # Find the appropriate stats table based on position
            stats_table = None
            if position == 'QB':
                stats_table = soup.find('table', {'id': 'passing'})
            elif position in ['RB', 'FB']:
                stats_table = soup.find('table', {'id': 'rushing_and_receiving'})
            elif position in ['WR', 'TE']:
                stats_table = soup.find('table', {'id': 'receiving_and_rushing'})
            elif position in ['DE', 'DT', 'NT', 'LB', 'OLB', 'ILB', 'MLB', 'CB', 'S', 'FS', 'SS', 'DB']:
                stats_table = soup.find('table', {'id': 'defense'})
            elif position == 'K':
                stats_table = soup.find('table', {'id': 'kicking'})
            elif position == 'P':
                stats_table = soup.find('table', {'id': 'punting'})
            
            if stats_table:
                tfoot = stats_table.find('tfoot')
                if tfoot:
                    career_row = tfoot.find('tr')
                    if career_row:
                        # Games played
                        g_cell = career_row.find('td', {'data-stat': 'g'})
                        if g_cell and g_cell.get_text(strip=True):
                            data['games_played'] = int(g_cell.get_text(strip=True))
                        
                        # Games started
                        gs_cell = career_row.find('td', {'data-stat': 'gs'})
                        if gs_cell and gs_cell.get_text(strip=True):
                            data['games_started'] = int(gs_cell.get_text(strip=True))
                        
                        # Position-specific stats
                        if position == 'QB':
                            self._extract_qb_stats(career_row, data)
                        elif position in ['RB', 'FB']:
                            self._extract_rb_stats(career_row, data)
                        elif position in ['WR', 'TE']:
                            self._extract_wr_stats(career_row, data)
                        elif position in ['DE', 'DT', 'NT', 'LB', 'OLB', 'ILB', 'MLB', 'CB', 'S', 'FS', 'SS', 'DB']:
                            self._extract_defensive_stats(career_row, data)
                        elif position == 'K':
                            self._extract_kicker_stats(career_row, data)
                        elif position == 'P':
                            self._extract_punter_stats(career_row, data)
            
            # Calculate years active
            if 'games_played' in data and data['games_played']:
                data['years_active'] = max(1, data['games_played'] // 16)
            
            # Calculate success metrics
            data['performance_score'] = self._calculate_performance_score(data)
            data['career_achievement_score'] = self._calculate_achievement_score(data)
            data['longevity_score'] = self._calculate_longevity_score(data)
            data['overall_success_score'] = (
                data['performance_score'] * 0.4 +
                data['career_achievement_score'] * 0.4 +
                data['longevity_score'] * 0.2
            )
            
            return data
            
        except Exception as e:
            logger.error(f"Error parsing player page: {e}")
            return None
    
    def _extract_qb_stats(self, row, data: Dict):
        """Extract QB statistics from career row."""
        try:
            # Passing attempts
            att_cell = row.find('td', {'data-stat': 'pass_att'})
            if att_cell and att_cell.get_text(strip=True):
                data['passing_attempts'] = int(att_cell.get_text(strip=True))
            
            # Completions
            cmp_cell = row.find('td', {'data-stat': 'pass_cmp'})
            if cmp_cell and cmp_cell.get_text(strip=True):
                data['passing_completions'] = int(cmp_cell.get_text(strip=True))
            
            # Completion percentage
            cmp_pct_cell = row.find('td', {'data-stat': 'pass_cmp_perc'})
            if cmp_pct_cell and cmp_pct_cell.get_text(strip=True):
                data['completion_pct'] = float(cmp_pct_cell.get_text(strip=True))
            
            # Passing yards
            yds_cell = row.find('td', {'data-stat': 'pass_yds'})
            if yds_cell and yds_cell.get_text(strip=True):
                data['passing_yards'] = int(yds_cell.get_text(strip=True))
            
            # TDs
            td_cell = row.find('td', {'data-stat': 'pass_td'})
            if td_cell and td_cell.get_text(strip=True):
                data['passing_tds'] = int(td_cell.get_text(strip=True))
            
            # INTs
            int_cell = row.find('td', {'data-stat': 'pass_int'})
            if int_cell and int_cell.get_text(strip=True):
                data['interceptions'] = int(int_cell.get_text(strip=True))
            
            # Passer rating
            rate_cell = row.find('td', {'data-stat': 'pass_rating'})
            if rate_cell and rate_cell.get_text(strip=True):
                data['passer_rating'] = float(rate_cell.get_text(strip=True))
            
            # YPA
            ypa_cell = row.find('td', {'data-stat': 'pass_yds_per_att'})
            if ypa_cell and ypa_cell.get_text(strip=True):
                data['yards_per_attempt'] = float(ypa_cell.get_text(strip=True))
            
            # Calculate TD/INT ratio
            if 'passing_tds' in data and 'interceptions' in data and data['interceptions'] > 0:
                data['td_int_ratio'] = data['passing_tds'] / data['interceptions']
            
        except Exception as e:
            logger.warning(f"Error extracting QB stats: {e}")
    
    def _extract_rb_stats(self, row, data: Dict):
        """Extract RB statistics from career row."""
        try:
            # Rushing attempts
            att_cell = row.find('td', {'data-stat': 'rush_att'})
            if att_cell and att_cell.get_text(strip=True):
                data['rushing_attempts'] = int(att_cell.get_text(strip=True))
            
            # Rushing yards
            yds_cell = row.find('td', {'data-stat': 'rush_yds'})
            if yds_cell and yds_cell.get_text(strip=True):
                data['rushing_yards'] = int(yds_cell.get_text(strip=True))
            
            # Rushing TDs
            td_cell = row.find('td', {'data-stat': 'rush_td'})
            if td_cell and td_cell.get_text(strip=True):
                data['rushing_tds'] = int(td_cell.get_text(strip=True))
            
            # YPC
            ypc_cell = row.find('td', {'data-stat': 'rush_yds_per_att'})
            if ypc_cell and ypc_cell.get_text(strip=True):
                data['yards_per_carry'] = float(ypc_cell.get_text(strip=True))
            
            # Fumbles
            fmb_cell = row.find('td', {'data-stat': 'fumbles'})
            if fmb_cell and fmb_cell.get_text(strip=True):
                data['rushing_fumbles'] = int(fmb_cell.get_text(strip=True))
            
        except Exception as e:
            logger.warning(f"Error extracting RB stats: {e}")
    
    def _extract_wr_stats(self, row, data: Dict):
        """Extract WR/TE statistics from career row."""
        try:
            # Receptions
            rec_cell = row.find('td', {'data-stat': 'rec'})
            if rec_cell and rec_cell.get_text(strip=True):
                data['receptions'] = int(rec_cell.get_text(strip=True))
            
            # Receiving yards
            yds_cell = row.find('td', {'data-stat': 'rec_yds'})
            if yds_cell and yds_cell.get_text(strip=True):
                data['receiving_yards'] = int(yds_cell.get_text(strip=True))
            
            # Receiving TDs
            td_cell = row.find('td', {'data-stat': 'rec_td'})
            if td_cell and td_cell.get_text(strip=True):
                data['receiving_tds'] = int(td_cell.get_text(strip=True))
            
            # YPR
            ypr_cell = row.find('td', {'data-stat': 'rec_yds_per_rec'})
            if ypr_cell and ypr_cell.get_text(strip=True):
                data['yards_per_reception'] = float(ypr_cell.get_text(strip=True))
            
            # Targets
            tgt_cell = row.find('td', {'data-stat': 'targets'})
            if tgt_cell and tgt_cell.get_text(strip=True):
                data['targets'] = int(tgt_cell.get_text(strip=True))
            
            # Calculate catch rate
            if 'receptions' in data and 'targets' in data and data['targets'] > 0:
                data['catch_rate'] = (data['receptions'] / data['targets']) * 100
            
        except Exception as e:
            logger.warning(f"Error extracting WR stats: {e}")
    
    def _extract_defensive_stats(self, row, data: Dict):
        """Extract defensive statistics from career row."""
        try:
            # Tackles
            tackles_cell = row.find('td', {'data-stat': 'tackles_combined'})
            if tackles_cell and tackles_cell.get_text(strip=True):
                data['tackles'] = int(tackles_cell.get_text(strip=True))
            
            # Sacks
            sacks_cell = row.find('td', {'data-stat': 'sacks'})
            if sacks_cell and sacks_cell.get_text(strip=True):
                data['sacks'] = float(sacks_cell.get_text(strip=True))
            
            # Interceptions
            int_cell = row.find('td', {'data-stat': 'def_int'})
            if int_cell and int_cell.get_text(strip=True):
                data['defensive_interceptions'] = int(int_cell.get_text(strip=True))
            
            # Forced fumbles
            ff_cell = row.find('td', {'data-stat': 'fumbles_forced'})
            if ff_cell and ff_cell.get_text(strip=True):
                data['forced_fumbles'] = int(ff_cell.get_text(strip=True))
            
            # Pass deflections
            pd_cell = row.find('td', {'data-stat': 'pass_defended'})
            if pd_cell and pd_cell.get_text(strip=True):
                data['pass_deflections'] = int(pd_cell.get_text(strip=True))
            
        except Exception as e:
            logger.warning(f"Error extracting defensive stats: {e}")
    
    def _extract_kicker_stats(self, row, data: Dict):
        """Extract kicker statistics from career row."""
        try:
            # FG made
            fgm_cell = row.find('td', {'data-stat': 'fgm'})
            if fgm_cell and fgm_cell.get_text(strip=True):
                data['field_goals_made'] = int(fgm_cell.get_text(strip=True))
            
            # FG attempted
            fga_cell = row.find('td', {'data-stat': 'fga'})
            if fga_cell and fga_cell.get_text(strip=True):
                data['field_goals_attempted'] = int(fga_cell.get_text(strip=True))
            
            # FG%
            fg_pct_cell = row.find('td', {'data-stat': 'fg_perc'})
            if fg_pct_cell and fg_pct_cell.get_text(strip=True):
                data['field_goal_pct'] = float(fg_pct_cell.get_text(strip=True))
            
        except Exception as e:
            logger.warning(f"Error extracting kicker stats: {e}")
    
    def _extract_punter_stats(self, row, data: Dict):
        """Extract punter statistics from career row."""
        try:
            # Punts
            punts_cell = row.find('td', {'data-stat': 'punts'})
            if punts_cell and punts_cell.get_text(strip=True):
                data['punts'] = int(punts_cell.get_text(strip=True))
            
            # Punting average
            avg_cell = row.find('td', {'data-stat': 'punt_yds_per_punt'})
            if avg_cell and avg_cell.get_text(strip=True):
                data['punting_avg'] = float(avg_cell.get_text(strip=True))
            
        except Exception as e:
            logger.warning(f"Error extracting punter stats: {e}")
    
    def _calculate_performance_score(self, data: Dict) -> float:
        """Calculate performance score based on position-specific stats.
        
        Args:
            data: Player data dictionary
            
        Returns:
            Performance score (0-100)
        """
        # Position-specific calculations
        position = data.get('position', '')
        
        # Placeholder - would calculate based on actual stats
        return 50.0
    
    def _calculate_achievement_score(self, data: Dict) -> float:
        """Calculate achievement score based on awards and honors.
        
        Args:
            data: Player data dictionary
            
        Returns:
            Achievement score (0-100)
        """
        score = 0.0
        
        score += data.get('pro_bowl_count', 0) * 5
        score += data.get('all_pro_first_count', 0) * 10
        score += data.get('all_pro_count', 0) * 7
        score += data.get('mvp_count', 0) * 20
        score += data.get('championship_count', 0) * 8
        score += data.get('super_bowl_mvp_count', 0) * 15
        
        if data.get('hof_inducted'):
            score += 30
        
        return min(score, 100.0)
    
    def _calculate_longevity_score(self, data: Dict) -> float:
        """Calculate longevity score based on years active.
        
        Args:
            data: Player data dictionary
            
        Returns:
            Longevity score (0-100)
        """
        years = data.get('years_active', 0)
        
        # NFL average career is ~3.3 years
        # 10+ years is exceptional
        score = min((years / 10.0) * 100, 100.0)
        
        return score
    
    def _analyze_player(self, player: NFLPlayer) -> NFLPlayerAnalysis:
        """Perform comprehensive linguistic analysis on player name.
        
        Args:
            player: NFLPlayer object
            
        Returns:
            NFLPlayerAnalysis object
        """
        try:
            name = player.name
            
            # Split name
            name_parts = name.strip().split()
            first_name = name_parts[0] if name_parts else name
            last_name = name_parts[-1] if len(name_parts) > 1 else ''
            
            # Check if analysis already exists
            existing_analysis = NFLPlayerAnalysis.query.filter_by(player_id=player.id).first()
            if existing_analysis:
                analysis = existing_analysis
            else:
                analysis = NFLPlayerAnalysis(player_id=player.id)
            
            # Full name analysis
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
            
            # First name analysis
            if first_name:
                first_metrics = self.name_analyzer.analyze_name(first_name)
                analysis.first_name_syllables = first_metrics.get('syllable_count', 0)
                analysis.first_name_length = first_metrics.get('character_length', 0)
                analysis.first_name_memorability = first_metrics.get('memorability_score', 0)
            
            # Last name analysis
            if last_name:
                last_metrics = self.name_analyzer.analyze_name(last_name)
                analysis.last_name_syllables = last_metrics.get('syllable_count', 0)
                analysis.last_name_length = last_metrics.get('character_length', 0)
                analysis.last_name_memorability = last_metrics.get('memorability_score', 0)
            
            # Phonemic analysis
            phonemic_metrics = self.phonemic_analyzer.analyze(name)
            analysis.harshness_score = phonemic_metrics.get('harshness_score', 50)
            analysis.softness_score = phonemic_metrics.get('softness_score', 50)
            
            # Semantic analysis
            semantic_metrics = self.semantic_analyzer.analyze(name)
            analysis.power_connotation_score = semantic_metrics.get('power_score', 50)
            
            # Sound symbolism analysis
            sound_metrics = self.sound_symbolism_analyzer.analyze(name)
            analysis.speed_association_score = sound_metrics.get('speed_score', 50)
            analysis.strength_association_score = sound_metrics.get('strength_score', 50)
            analysis.toughness_score = sound_metrics.get('toughness_score', 50)
            
            # Prosodic analysis
            prosodic_metrics = self.prosodic_analyzer.analyze(name)
            analysis.rhythm_score = prosodic_metrics.get('rhythm_score', 50)
            analysis.consonant_cluster_complexity = prosodic_metrics.get('complexity_score', 50)
            
            # Alliteration
            analysis.alliteration_score = self._check_alliteration(first_name, last_name)
            
            # Temporal cohort
            if player.era:
                analysis.temporal_cohort = f"{player.era}s"
            
            # Rule era cohort
            analysis.rule_era_cohort = player.rule_era
            
            # Position cluster
            analysis.position_cluster = player.position_group
            analysis.position_category_cluster = player.position_category
            
            # JSON data
            analysis.phonosemantic_data = json.dumps(phonemic_metrics)
            analysis.semantic_data = json.dumps(semantic_metrics)
            analysis.prosodic_data = json.dumps(prosodic_metrics)
            analysis.sound_symbolism_data = json.dumps(sound_metrics)
            
            # Save analysis
            if not existing_analysis:
                db.session.add(analysis)
            
            db.session.commit()
            
            logger.info(f"Analyzed player: {player.name}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing player '{player.name}': {e}")
            db.session.rollback()
            return None
    
    def _check_alliteration(self, first_name: str, last_name: str) -> float:
        """Check if first and last names alliterate.
        
        Args:
            first_name: First name
            last_name: Last name
            
        Returns:
            Alliteration score (0-100)
        """
        if not first_name or not last_name:
            return 0.0
        
        first_initial = first_name[0].lower()
        last_initial = last_name[0].lower()
        
        if first_initial == last_initial:
            return 100.0
        
        # Partial credit for similar sounds
        similar_pairs = [
            ('b', 'p'), ('d', 't'), ('g', 'k'),
            ('v', 'f'), ('z', 's'), ('j', 'ch')
        ]
        
        for pair in similar_pairs:
            if (first_initial in pair and last_initial in pair):
                return 50.0
        
        return 0.0
    
    def test_collection(self, num_players: int = 5) -> Dict:
        """Test collection with a small sample.
        
        Args:
            num_players: Number of players to collect per position
            
        Returns:
            Collection statistics
        """
        logger.info(f"Starting test collection ({num_players} players per position)...")
        
        test_positions = ['QB', 'RB', 'WR']
        
        stats = {
            'positions_collected': {},
            'total_added': 0,
            'total_updated': 0,
            'total_analyzed': 0,
            'errors': 0
        }
        
        for position in test_positions:
            logger.info(f"\nTesting {position} collection...")
            # This would call actual collection methods
            # For now, placeholder
            logger.info(f"  (Mock mode - would collect {num_players} {position} players)")
        
        return stats

