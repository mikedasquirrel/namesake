"""Mass Wikipedia Ship Collection

Scrapes Wikipedia ship categories to collect hundreds of ships with documented histories.

Strategy:
1. Start with major ship categories on Wikipedia
2. Extract ship data from infoboxes
3. Categorize names (geographic, saint, virtue, etc.)
4. Calculate achievement metrics
5. Target: 500-1000 ships

Usage:
    python scripts/collect_ships_wikipedia.py --target 500
"""

import sys
import os
import argparse
import logging
import time
import json
import requests
import re
from datetime import datetime
from typing import Dict, List, Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from core.config import Config
from core.models import db, Ship
from collectors.ship_collector import ShipCollector

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WikipediaShipScraper:
    """Scrape ships from Wikipedia categories."""
    
    def __init__(self):
        self.base_url = "https://en.wikipedia.org/w/api.php"
        self.collector = ShipCollector()
        self.ships_collected = 0
        self.target = 500
        
        # Proper headers for Wikipedia API
        self.headers = {
            'User-Agent': 'NominativeDeterminismResearch/1.0 (Educational Research; contact@example.com)'
        }
        
        # Wikipedia ship categories to scrape
        self.ship_categories = [
            "Category:Ships by name",
            "Category:Individual sailing vessels",
            "Category:Naval ships",
            "Category:Warships",
            "Category:Exploration ships",
            "Category:Age of Sail ships",
            "Category:Royal Navy ships",
            "Category:United States Navy ships",
            "Category:Spanish Navy ships",
            "Category:French Navy ships",
            "Category:Research vessels",
            "Category:Famous ships",
            "Category:Museum ships",
            "Category:Historic ships",
            "Category:World War II naval ships",
            "Category:Frigates",
            "Category:Ships of the line",
            "Category:Battleships",
            "Category:Aircraft carriers",
            "Category:Cruisers",
            "Category:Destroyers",
        ]
        
    def collect_ships(self, target: int = 500) -> Dict:
        """Collect ships from Wikipedia categories.
        
        Args:
            target: Target number of ships to collect
            
        Returns:
            Collection statistics
        """
        self.target = target
        logger.info("="*70)
        logger.info(f"WIKIPEDIA SHIP COLLECTION - TARGET: {target}")
        logger.info("="*70)
        
        stats = {
            'ships_added': 0,
            'ships_updated': 0,
            'ships_skipped': 0,
            'errors': 0,
            'categories_processed': 0
        }
        
        for category in self.ship_categories:
            if self.ships_collected >= target:
                logger.info(f"\n✓ Target reached: {self.ships_collected}/{target}")
                break
            
            logger.info(f"\n{'='*70}")
            logger.info(f"Processing: {category}")
            logger.info(f"{'='*70}")
            
            category_stats = self._process_category(category)
            
            stats['ships_added'] += category_stats['added']
            stats['ships_updated'] += category_stats['updated']
            stats['ships_skipped'] += category_stats['skipped']
            stats['errors'] += category_stats['errors']
            stats['categories_processed'] += 1
            
            logger.info(f"Category complete: +{category_stats['added']} ships "
                       f"(Total: {self.ships_collected}/{target})")
            
            # Rate limiting
            time.sleep(1)
        
        logger.info("\n" + "="*70)
        logger.info("COLLECTION COMPLETE")
        logger.info("="*70)
        logger.info(f"Ships added: {stats['ships_added']}")
        logger.info(f"Ships updated: {stats['ships_updated']}")
        logger.info(f"Ships skipped: {stats['ships_skipped']}")
        logger.info(f"Errors: {stats['errors']}")
        logger.info(f"Categories processed: {stats['categories_processed']}")
        
        return stats
    
    def _process_category(self, category: str) -> Dict:
        """Process a Wikipedia category to extract ships.
        
        Args:
            category: Wikipedia category name
            
        Returns:
            Category statistics
        """
        stats = {
            'added': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0
        }
        
        # Get pages in category
        pages = self._get_category_pages(category, limit=100)
        
        logger.info(f"Found {len(pages)} pages in {category}")
        
        for page in pages:
            if self.ships_collected >= self.target:
                break
            
            try:
                # Skip non-ship pages
                if not self._is_ship_page(page['title']):
                    stats['skipped'] += 1
                    continue
                
                # Get ship data from page
                ship_data = self._extract_ship_data(page['pageid'], page['title'])
                
                if not ship_data:
                    stats['skipped'] += 1
                    continue
                
                # Save to database
                result = self._save_ship(ship_data)
                
                if result == 'added':
                    stats['added'] += 1
                    self.ships_collected += 1
                    logger.info(f"  ✓ Added: {ship_data['name']} ({self.ships_collected}/{self.target})")
                elif result == 'updated':
                    stats['updated'] += 1
                elif result == 'skipped':
                    stats['skipped'] += 1
                
                # Rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error processing {page['title']}: {e}")
                stats['errors'] += 1
        
        return stats
    
    def _get_category_pages(self, category: str, limit: int = 100) -> List[Dict]:
        """Get pages in a Wikipedia category.
        
        Args:
            category: Category name
            limit: Maximum pages to retrieve
            
        Returns:
            List of page dictionaries
        """
        pages = []
        
        params = {
            'action': 'query',
            'list': 'categorymembers',
            'cmtitle': category,
            'cmlimit': min(limit, 50),  # Be more conservative
            'cmtype': 'page',
            'format': 'json'
        }
        
        try:
            response = requests.get(
                self.base_url, 
                params=params, 
                headers=self.headers,
                timeout=15
            )
            
            # Check response
            if response.status_code != 200:
                logger.error(f"HTTP {response.status_code} for {category}")
                return []
            
            # Check for content
            if not response.text:
                logger.error(f"Empty response for {category}")
                return []
            
            data = response.json()
            
            # Check for warnings (category might not exist)
            if 'warnings' in data:
                logger.warning(f"API warning for {category}: {data['warnings']}")
            
            if 'query' in data and 'categorymembers' in data['query']:
                pages = data['query']['categorymembers']
                logger.debug(f"Found {len(pages)} pages in {category}")
            else:
                logger.debug(f"No categorymembers in response for {category}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {category}: {e}")
        except ValueError as e:
            logger.error(f"JSON decode error for {category}: {e}")
        except Exception as e:
            logger.error(f"Error fetching category {category}: {e}")
        
        return pages
    
    def _is_ship_page(self, title: str) -> bool:
        """Check if page title represents a ship.
        
        Args:
            title: Page title
            
        Returns:
            True if ship page
        """
        # Skip disambiguation, lists, categories
        skip_terms = ['(disambiguation)', 'List of', 'Category:', 'Template:', 'ships of']
        if any(term in title for term in skip_terms):
            return False
        
        # Look for ship prefixes
        ship_prefixes = ['HMS', 'USS', 'RMS', 'SS', 'HMAS', 'HMCS', 'INS', 'SMS']
        if any(title.startswith(prefix) for prefix in ship_prefixes):
            return True
        
        # Check for parenthetical year/ship designation
        if re.search(r'\(ship\)|\(\d{4}\)|\(vessel\)', title, re.IGNORECASE):
            return True
        
        return False
    
    def _extract_ship_data(self, page_id: int, title: str) -> Optional[Dict]:
        """Extract ship data from Wikipedia page.
        
        Args:
            page_id: Wikipedia page ID
            title: Page title
            
        Returns:
            Ship data dictionary or None
        """
        try:
            # Get page content
            params = {
                'action': 'query',
                'pageids': page_id,
                'prop': 'revisions|categories',
                'rvprop': 'content',
                'rvslots': 'main',
                'format': 'json'
            }
            
            response = requests.get(
                self.base_url, 
                params=params, 
                headers=self.headers,
                timeout=15
            )
            
            if response.status_code != 200:
                return None
                
            data = response.json()
            
            if 'query' not in data or 'pages' not in data['query']:
                return None
            
            page_data = data['query']['pages'][str(page_id)]
            
            if 'revisions' not in page_data:
                return None
            
            content = page_data['revisions'][0]['slots']['main']['*']
            
            # Parse ship data from content
            ship_data = self._parse_infobox(content, title)
            
            if ship_data:
                ship_data['wikipedia_url'] = f"https://en.wikipedia.org/?curid={page_id}"
                
            return ship_data
            
        except Exception as e:
            logger.debug(f"Error extracting data for {title}: {e}")
            return None
    
    def _parse_infobox(self, content: str, title: str) -> Optional[Dict]:
        """Parse ship infobox from Wikipedia content.
        
        Args:
            content: Page content
            title: Page title
            
        Returns:
            Ship data dictionary or None
        """
        # Extract ship name from title
        name = self._extract_ship_name(title)
        
        if not name:
            return None
        
        # Parse launch year
        launch_year = None
        launch_match = re.search(r'launched.*?(\d{4})', content, re.IGNORECASE)
        if launch_match:
            launch_year = int(launch_match.group(1))
        
        # Try alternative patterns
        if not launch_year:
            year_match = re.search(r'\|\s*Ship launched\s*=\s*(\d{4})', content)
            if year_match:
                launch_year = int(year_match.group(1))
        
        # Parse nation
        nation = self._extract_nation(content, title)
        
        # Parse ship type
        ship_type = self._extract_ship_type(content, title)
        
        # Determine era
        era = self._determine_era(launch_year)
        
        # Calculate basic achievement score from page length and categories
        achievement_score = self._estimate_achievement(content, title)
        
        return {
            'name': name,
            'full_designation': title,
            'prefix': self._extract_prefix(title),
            'nation': nation,
            'ship_type': ship_type,
            'launch_year': launch_year,
            'era': era,
            'historical_significance_score': achievement_score,
            'primary_purpose': ship_type or 'Unknown',
            'primary_source': 'Wikipedia',
            'data_completeness_score': 60.0  # Medium completeness
        }
    
    def _extract_ship_name(self, title: str) -> Optional[str]:
        """Extract ship name from title.
        
        Args:
            title: Page title
            
        Returns:
            Ship name or None
        """
        # Remove prefix
        for prefix in ['HMS', 'USS', 'RMS', 'SS', 'HMAS', 'HMCS', 'INS', 'SMS']:
            if title.startswith(prefix + ' '):
                name = title[len(prefix)+1:]
                # Remove parenthetical suffixes
                name = re.sub(r'\s*\([^)]+\)\s*$', '', name)
                return name.strip()
        
        # No prefix, use title directly
        name = re.sub(r'\s*\([^)]+\)\s*$', '', title)
        return name.strip() if name else None
    
    def _extract_prefix(self, title: str) -> Optional[str]:
        """Extract ship prefix from title."""
        for prefix in ['HMS', 'USS', 'RMS', 'SS', 'HMAS', 'HMCS', 'INS', 'SMS']:
            if title.startswith(prefix + ' '):
                return prefix
        return None
    
    def _extract_nation(self, content: str, title: str) -> str:
        """Extract nation from content or title."""
        # Check title prefix
        prefix_nations = {
            'HMS': 'United Kingdom',
            'USS': 'United States',
            'RMS': 'United Kingdom',
            'HMAS': 'Australia',
            'HMCS': 'Canada',
            'INS': 'India',
            'SMS': 'Germany'
        }
        
        for prefix, nation in prefix_nations.items():
            if title.startswith(prefix + ' '):
                return nation
        
        # Search content for country
        nation_patterns = [
            (r'Royal Navy', 'United Kingdom'),
            (r'United States Navy', 'United States'),
            (r'US Navy', 'United States'),
            (r'British', 'United Kingdom'),
            (r'American', 'United States'),
            (r'Spanish', 'Spain'),
            (r'French', 'France'),
            (r'German', 'Germany'),
        ]
        
        for pattern, nation in nation_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return nation
        
        return 'Unknown'
    
    def _extract_ship_type(self, content: str, title: str) -> str:
        """Extract ship type from content."""
        # Check for keywords
        type_patterns = [
            (r'battleship', 'naval'),
            (r'aircraft carrier', 'naval'),
            (r'cruiser', 'naval'),
            (r'destroyer', 'naval'),
            (r'frigate', 'naval'),
            (r'submarine', 'naval'),
            (r'exploration', 'exploration'),
            (r'research vessel', 'exploration'),
            (r'survey ship', 'exploration'),
            (r'passenger', 'passenger'),
            (r'liner', 'passenger'),
            (r'merchant', 'commercial'),
            (r'cargo', 'commercial'),
        ]
        
        content_lower = content.lower()
        
        for pattern, ship_type in type_patterns:
            if pattern in content_lower:
                return ship_type
        
        return 'naval'  # Default
    
    def _determine_era(self, launch_year: Optional[int]) -> str:
        """Determine historical era from launch year."""
        if not launch_year:
            return 'unknown'
        
        if launch_year < 1650:
            return 'age_of_discovery'
        elif launch_year < 1850:
            return 'age_of_sail'
        elif launch_year < 1945:
            return 'steam_era'
        else:
            return 'modern'
    
    def _estimate_achievement(self, content: str, title: str) -> float:
        """Estimate achievement score based on content and title.
        
        Heuristics:
        - Longer articles = more notable
        - More references = better documented
        - Certain keywords = higher significance
        
        Args:
            content: Page content
            title: Page title
            
        Returns:
            Achievement score (0-100)
        """
        score = 50.0  # Base score
        
        # Content length bonus (longer = more notable)
        content_length = len(content)
        if content_length > 50000:
            score += 20
        elif content_length > 20000:
            score += 15
        elif content_length > 10000:
            score += 10
        elif content_length > 5000:
            score += 5
        
        # Keyword bonuses
        high_value_keywords = [
            'flagship', 'famous', 'historic', 'battle', 'victory', 'discovery',
            'exploration', 'museum ship', 'national historic', 'world war',
            'decisive', 'revolutionary', 'breakthrough'
        ]
        
        content_lower = content.lower()
        keyword_matches = sum(1 for kw in high_value_keywords if kw in content_lower)
        score += min(keyword_matches * 3, 20)
        
        # Cap at 100
        return min(score, 100.0)
    
    def _save_ship(self, ship_data: Dict) -> str:
        """Save ship to database.
        
        Args:
            ship_data: Ship data dictionary
            
        Returns:
            Status: 'added', 'updated', or 'skipped'
        """
        try:
            # Check if exists
            existing = Ship.query.filter_by(name=ship_data['name']).first()
            
            if existing:
                # Update if better data
                if ship_data.get('data_completeness_score', 0) > existing.data_completeness_score:
                    self.collector._populate_ship_from_dict(existing, ship_data)
                    db.session.commit()
                    return 'updated'
                return 'skipped'
            
            # Create new ship
            ship = Ship()
            self.collector._populate_ship_from_dict(ship, ship_data)
            db.session.add(ship)
            db.session.commit()
            
            # Analyze ship name
            self.collector._analyze_ship_name(ship)
            
            return 'added'
            
        except Exception as e:
            logger.error(f"Error saving ship {ship_data.get('name')}: {e}")
            db.session.rollback()
            return 'skipped'


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(description='Wikipedia ship mass collection')
    parser.add_argument('--target', type=int, default=500,
                       help='Target number of ships (default: 500)')
    
    args = parser.parse_args()
    
    # Initialize Flask app
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Run bootstrap first if empty
        current_count = Ship.query.count()
        
        if current_count == 0:
            logger.info("Database empty - running bootstrap first...")
            collector = ShipCollector()
            bootstrap_stats = collector.collect_bootstrap_ships()
            logger.info(f"Bootstrap: {bootstrap_stats['ships_added']} ships added\n")
            current_count = Ship.query.count()
        
        logger.info(f"Starting count: {current_count} ships")
        logger.info(f"Target: {args.target} ships")
        logger.info(f"Need: {args.target - current_count} more ships\n")
        
        if current_count >= args.target:
            logger.info(f"✓ Target already reached!")
            return
        
        # Run Wikipedia scraper
        scraper = WikipediaShipScraper()
        stats = scraper.collect_ships(target=args.target - current_count)
        
        # Final summary
        final_count = Ship.query.count()
        logger.info("\n" + "="*70)
        logger.info("FINAL SUMMARY")
        logger.info("="*70)
        logger.info(f"Total ships in database: {final_count}")
        logger.info(f"Target: {args.target}")
        logger.info(f"Progress: {final_count}/{args.target} ({final_count/args.target*100:.1f}%)")


if __name__ == "__main__":
    main()

